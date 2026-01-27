"""
    OCR z cache dla obrazów w Google Cloud Storage.

    run_ocr_cache():
    - listuje obrazy w GCS (stan "teraz"),
    - wczytuje out_csv jako cache,
    - uruchamia OCR tylko dla brakujących plików,
    - dopisuje wyniki, deduplikuje,
    - zapisuje out_csv i zwraca df_out.

    Uwaga: dla obrazów (nie PDF) nie zapisujemy kolumny `page`.
"""

from __future__ import annotations

import os
import subprocess
import hashlib
from typing import Iterable

import pandas as pd
from google.cloud import vision


DEFAULT_IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp")


def file_id_from_gcs_path(gs_path: str) -> str:
    """Stabilny identyfikator pliku na podstawie pełnej ścieżki gs://..."""
    return hashlib.sha1(gs_path.encode("utf-8")).hexdigest()


def list_gcs_images(prefix: str, image_exts: tuple[str, ...] = DEFAULT_IMAGE_EXTS) -> list[str]:
    """Listuje obrazy pod prefix/** w GCS przez CLI (gcloud storage ls)."""
    r = subprocess.run(
        ["gcloud", "storage", "ls", f"{prefix.rstrip('/')}/**"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:2000])

    paths: list[str] = []
    for line in r.stdout.splitlines():
        p = line.strip()
        if not p or p.endswith("/"):
            continue
        if p.lower().endswith(image_exts):
            paths.append(p)

    return sorted(paths)


def ocr_lines_from_gcs(
    gs_path: str,
    client: vision.ImageAnnotatorClient,
    source: str = "gcv_ocr_line",
) -> list[dict]:
    """
    Uruchamia Google Vision OCR (document_text_detection) i zwraca linie tekstu.

    Zwracane pola: text, file_name, file_id, gcs_path, line_id, bbox_norm, source
    (bez `page`).
    """
    image = vision.Image(source=vision.ImageSource(gcs_image_uri=gs_path))
    resp = client.document_text_detection(image=image)
    if resp.error.message:
        raise RuntimeError(resp.error.message)

    out: list[dict] = []
    fid = file_id_from_gcs_path(gs_path)
    file_name = gs_path.split("/")[-1]

    fta = resp.full_text_annotation
    if (not fta) or (not fta.pages):
        return out

    # Dla obrazów traktujemy wynik jako jeden "ciąg linii" (bez numerowania stron)
    line_id = 0

    for page in fta.pages:
        line_text: list[str] = []
        xs: list[int] = []
        ys: list[int] = []

        def flush_line():
            nonlocal line_id, line_text, xs, ys
            text = "".join(line_text).strip()
            if text and xs and ys:
                x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
                out.append(
                    {
                        "text": text,
                        "file_name": file_name,
                        "file_id": fid,
                        "gcs_path": gs_path,
                        "line_id": line_id,
                        "bbox_norm": f"{float(x1)},{float(y1)},{float(x2)},{float(y2)}",
                        "source": source,
                    }
                )
                line_id += 1
            line_text, xs, ys = [], [], []

        for block in page.blocks:
            for para in block.paragraphs:
                for word in para.words:
                    wb = word.bounding_box.vertices
                    xs.extend([v.x for v in wb])
                    ys.extend([v.y for v in wb])

                    for sym in word.symbols:
                        line_text.append(sym.text)

                        sb = sym.bounding_box.vertices
                        xs.extend([v.x for v in sb])
                        ys.extend([v.y for v in sb])

                        br = None
                        if sym.property and sym.property.detected_break:
                            br = sym.property.detected_break.type

                        # defensywnie: 1=SPACE, 3=EOL_SURE_SPACE, 5=LINE_BREAK
                        br_val = int(br) if br is not None else 0
                        if br_val in (1, 3):
                            line_text.append(" ")
                        if br_val == 5:
                            flush_line()

        flush_line()

    return out


def run_ocr_cache(
    gcs_photos_prefix: str,
    out_csv: str,
    limit_images: int | None = None,
    image_exts: tuple[str, ...] = DEFAULT_IMAGE_EXTS,
) -> pd.DataFrame:
    """
    OCR z cache:
    - listuje obrazy w GCS (stan teraz),
    - wczytuje out_csv jako cache,
    - uruchamia OCR tylko dla brakujących plików,
    - dopisuje i deduplikuje,
    - zapisuje out_csv,
    - zwraca df_out.

    Uwaga (legacy): starsze cache mogły zawierać kolumny z poprzednich iteracji (np. 'page', 'script').
    W tym workflow dla obrazów ich nie utrzymujemy.
    """
    client = vision.ImageAnnotatorClient()

    # kolumny, których nie chcemy w tym workflow (obrazy, bez PDF/page, bez script)
    DROP_LEGACY_COLS = ("page", "script")

    # 1) lista plików w GCS
    gcs_files_all = list_gcs_images(gcs_photos_prefix, image_exts=image_exts)
    if limit_images is not None:
        gcs_files_all = gcs_files_all[: int(limit_images)]

    # 2) wczytaj cache
    df_cache = pd.read_csv(out_csv) if os.path.exists(out_csv) else pd.DataFrame()

    # usuń legacy kolumny z cache (w pamięci)
    if len(df_cache):
        cols_to_drop = [c for c in DROP_LEGACY_COLS if c in df_cache.columns]
        if cols_to_drop:
            df_cache = df_cache.drop(columns=cols_to_drop)

    cached_paths = (
        set(df_cache["gcs_path"].dropna().astype(str).unique().tolist())
        if "gcs_path" in df_cache.columns
        else set()
    )

    # 3) brakujące
    gcs_files_missing = [p for p in gcs_files_all if p not in cached_paths]

    print("GCS files:", len(gcs_files_all))
    print("Cached OCR files:", len(cached_paths))
    print("Missing (to OCR now):", len(gcs_files_missing))

    # 4) OCR tylko brakujących + zapis cache
    if len(gcs_files_missing) == 0:
        print("[SKIP] Brak nowych plików – OCR nie został uruchomiony (0 kosztów).")
        df_out = df_cache.copy()

        # KLUCZOWE: zapisz „oczyszczony” cache także w tym wariancie,
        # żeby stary CSV z kolumną 'page' zniknął z dysku
        out_dir = os.path.dirname(out_csv)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        df_out.to_csv(out_csv, index=False, encoding="utf-8")
        print("[DONE] Cache odświeżony (bez legacy kolumn):", out_csv)

    else:
        rows_new: list[dict] = []
        for i, gs_path in enumerate(gcs_files_missing, start=1):
            fn = gs_path.split("/")[-1]
            try:
                rows = ocr_lines_from_gcs(gs_path, client=client)  # bez 'page' i bez 'script'
                rows_new.extend(rows)
                print(f"[{i}/{len(gcs_files_missing)}] OK: {fn} -> {len(rows)} linii")
            except Exception as e:
                print(f"[{i}/{len(gcs_files_missing)}] ERROR: {fn}: {e}")

        df_new = pd.DataFrame(rows_new)

        # defensywnie: jeśli skądkolwiek przyszły legacy kolumny -> usuń
        if len(df_new):
            cols_to_drop = [c for c in DROP_LEGACY_COLS if c in df_new.columns]
            if cols_to_drop:
                df_new = df_new.drop(columns=cols_to_drop)

        df_out = pd.concat([df_cache, df_new], ignore_index=True) if len(df_cache) else df_new

        # defensywnie: usuń legacy po concat
        if len(df_out):
            cols_to_drop = [c for c in DROP_LEGACY_COLS if c in df_out.columns]
            if cols_to_drop:
                df_out = df_out.drop(columns=cols_to_drop)

        if len(df_out) > 0:
            key_cols = [c for c in ["gcs_path", "line_id", "text"] if c in df_out.columns]
            if key_cols:
                df_out = df_out.drop_duplicates(subset=key_cols, keep="first")

        out_dir = os.path.dirname(out_csv)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        df_out.to_csv(out_csv, index=False, encoding="utf-8")
        print("[DONE] Cache zaktualizowany:", out_csv)

    print("CSV rows:", len(df_out))
    print(
        "CSV unique files:",
        df_out["file_name"].nunique() if "file_name" in df_out.columns and len(df_out) else 0,
    )
    return df_out