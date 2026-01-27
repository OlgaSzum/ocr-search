"""
Eksport wyników OCR po edycji.

Funkcje:
- join_unique_lines: łączenie unikalnych niepustych linii w jeden słupek
- export_reviewed_lines: zapis pełnego df (audit)
- export_per_image: zapis 1 wiersz / zdjęcie (po filtrze excluded=True)
"""

from __future__ import annotations

import os
import pandas as pd


def join_unique_lines(lines: pd.Series) -> str:
    """Łączy unikalne, niepuste linie tekstu w jeden słupek (jedna linia na wpis)."""
    seen: set[str] = set()
    out: list[str] = []
    for x in lines.astype(str).tolist():
        t = x.strip()
        if not t:
            continue
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return "\n".join(out)


def export_reviewed_lines(df: pd.DataFrame, output_csv: str) -> None:
    """Zapisuje pełny DF do CSV (audit / powrót do edycji)."""
    out_dir = os.path.dirname(output_csv)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    df.to_csv(output_csv, index=False, encoding="utf-8")


def export_per_image(
    df: pd.DataFrame,
    output_csv: str,
    *,
    text_col_prefer: str = "text_edited",
    excluded_col: str = "excluded",
) -> str:
    """
    Zapisuje 1 wiersz / zdjęcie do pliku output_csv__per_image.csv.
    Zwraca ścieżkę per_image_csv.

    - usuwa linie excluded==True (watermark)
    - agreguje po file_name
    """
    base, _ = os.path.splitext(output_csv)
    per_image_csv = base + "__per_image.csv"

    dff = df.copy()
    if excluded_col in dff.columns:
        dff = dff[~dff[excluded_col].eq(True)].copy()

    text_col = text_col_prefer if text_col_prefer in dff.columns else "text"
    if text_col not in dff.columns:
        raise KeyError(f"Brak kolumny tekstu: {text_col}")

    agg = (
        dff.groupby("file_name", as_index=False)
        .agg(
            gcs_path=("gcs_path", "first") if "gcs_path" in dff.columns else ("file_name", "first"),
            text_joined=(text_col, join_unique_lines),
            lines_n=(text_col, lambda s: int((s.astype(str).str.strip() != "").sum())),
        )
    )

    out_dir = os.path.dirname(per_image_csv)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    agg.to_csv(per_image_csv, index=False, encoding="utf-8")
    return per_image_csv
