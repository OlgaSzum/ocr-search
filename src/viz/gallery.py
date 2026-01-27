"""
Galeria miniatur z bboxami OCR.

- Czyta obrazy z PHOTOS_DIR (jeśli podane) lub z GCS przez: gcloud storage cat gs://.../file_name
- Rysuje bboxy z kolumny bbox_norm (px lub [0..1])
- Renderuje HTML w notebooku
"""

from __future__ import annotations

import os
import io
import base64
import subprocess
from typing import Optional

import pandas as pd
from PIL import Image, ImageDraw
from IPython.display import display, HTML


def load_image_bytes(file_name: str, gcs_photos_prefix: str, photos_dir: str = "") -> bytes:
    """Ładuje bajty obrazu lokalnie (photos_dir) albo z GCS (gcloud storage cat)."""
    if photos_dir:
        p = os.path.join(photos_dir, file_name)
        if os.path.exists(p):
            with open(p, "rb") as f:
                return f.read()

    gs_path = f"{gcs_photos_prefix.rstrip('/')}/{file_name}"
    r = subprocess.run(["gcloud", "storage", "cat", gs_path], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise FileNotFoundError(r.stderr.decode("utf-8", errors="ignore")[:400])
    return r.stdout


def _parse_bbox(s: str) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = map(float, str(s).split(","))
    return x1, y1, x2, y2


def thumb_with_bboxes(img_bytes: bytes, rows: pd.DataFrame, max_side: int = 720) -> Image.Image:
    """Zwraca miniaturę PIL z dorysowanymi bboxami."""
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    W, H = img.size

    scale = min(max_side / W, max_side / H, 1.0)
    nw, nh = int(W * scale), int(H * scale)
    thumb = img.resize((nw, nh))

    draw = ImageDraw.Draw(thumb)

    if "bbox_norm" in rows.columns:
        for _, r in rows.iterrows():
            bn = r.get("bbox_norm", None)
            if pd.isna(bn) or not str(bn).strip():
                continue

            x1, y1, x2, y2 = _parse_bbox(str(bn))

            # jeśli <= 1.5 => [0..1], inaczej piksele
            if max(x1, y1, x2, y2) <= 1.5:
                x1, y1, x2, y2 = x1 * W, y1 * H, x2 * W, y2 * H

            draw.rectangle(
                [int(x1 * scale), int(y1 * scale), int(x2 * scale), int(y2 * scale)],
                outline="red",
                width=2,
            )

    return thumb


def pil_to_data_uri(pil_img: Image.Image) -> str:
    """Konwertuje PIL → data URI (JPEG) do wstawienia w HTML."""
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def render_gallery(
    df: pd.DataFrame,
    gcs_photos_prefix: str,
    photos_dir: str = "",
    max_side: int = 720,
    limit_gallery: Optional[int] = 50,
) -> None:
    """
    Renderuje galerię miniatur dla plików z df['file_name'].
    limit_gallery: None/0 = bez limitu.
    """
    if "file_name" not in df.columns:
        raise KeyError("Brak kolumny 'file_name' w df.")

    files = sorted(df["file_name"].dropna().astype(str).unique().tolist())

    if len(files) == 0:
        print("[WARN] df nie zawiera żadnych file_name (lista plików pusta).")
        return

    if limit_gallery and len(files) > int(limit_gallery):
        print(f"[INFO] Galeria: pokazuję {int(limit_gallery)}/{len(files)} plików (limit_gallery).")
        files = files[: int(limit_gallery)]

    cards = []
    ok = 0
    missing = 0

    for fn in files:
        rows = df[df["file_name"] == fn]
        try:
            img_bytes = load_image_bytes(fn, gcs_photos_prefix=gcs_photos_prefix, photos_dir=photos_dir)
            thumb = thumb_with_bboxes(img_bytes, rows, max_side=max_side)
            uri = pil_to_data_uri(thumb)
            ok += 1
            cards.append(f"""
            <div style="width:{max_side+40}px; margin:10px;">
                <div style="font-size:12px; margin-bottom:6px;">{fn}</div>
                <img src="{uri}" style="max-width:{max_side}px; border:1px solid #ddd;" />
            </div>
            """)
        except Exception as e:
            missing += 1
            cards.append(f"""
              <div style="width:520px; margin:10px; border:1px solid #f2f2f2; padding:10px;">
                <div style="font-size:12px; margin-bottom:6px;">{fn}</div>
                <div style="font-size:12px; color:#a00;">Brak obrazu / błąd odczytu</div>
                <div style="font-size:11px; white-space:pre-wrap;">{str(e)[:350]}</div>
              </div>
            """)

    print(f"[DONE] Galeria: OK={ok}, błędy={missing}, razem={ok+missing}")
    html = "<div style='display:flex; flex-wrap:wrap; align-items:flex-start;'>" + "\n".join(cards) + "</div>"
    display(HTML(html))
