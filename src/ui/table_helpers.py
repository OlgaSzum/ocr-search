"""
Helpery do tabeli edycyjnej (ipywidgets).

Cel: wynieść logikę danych z notebooka, zostawiając konstrukcję widgetów w notatniku.
"""

from __future__ import annotations

import pandas as pd


def ensure_edit_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Zapewnia text_edited i excluded w df (bez modyfikowania oryginału)."""
    out = df.copy()
    if "text" not in out.columns:
        raise KeyError("Brak kolumny 'text'.")
    if "text_edited" not in out.columns:
        out["text_edited"] = out["text"].astype(str)
    if "excluded" not in out.columns:
        out["excluded"] = False
    return out


def filter_df_for_table(df: pd.DataFrame, file_name: str, query: str) -> pd.DataFrame:
    """
    Filtruje df pod tabelę:
    - opcjonalnie ogranicza do file_name (jeśli nie '(wszystkie)'),
    - filtruje substring po text_edited/text,
    - NIE usuwa excluded (to robimy per plik, bo status liczymy na całości).
    """
    dff = df.copy()

    if file_name and file_name != "(wszystkie)":
        dff = dff[dff["file_name"] == file_name]

    q = (query or "").strip().lower()
    if q:
        base_col = "text_edited" if "text_edited" in dff.columns else "text"
        dff = dff[dff[base_col].astype(str).str.lower().str.contains(q, na=False)]

    return dff


def list_files(dff: pd.DataFrame) -> list[str]:
    return sorted(dff["file_name"].dropna().astype(str).unique().tolist())


def rows_to_lines(s: pd.Series) -> list[str]:
    return [str(x) if pd.notna(x) else "" for x in s.tolist()]


def calc_height_px(n_lines: int, min_px: int = 80, max_px: int = 520, per_line: int = 18, pad: int = 28) -> str:
    h = pad + int(n_lines) * int(per_line)
    h = max(min_px, min(max_px, h))
    return f"{h}px"


def normalize_edited_lines(edited_lines: list[str], n: int) -> list[str]:
    """Dopasowuje listę edytowanych linii do długości n (padding/truncation)."""
    if len(edited_lines) < n:
        edited_lines = edited_lines + [""] * (n - len(edited_lines))
    if len(edited_lines) > n:
        edited_lines = edited_lines[:n]
    return [str(x) for x in edited_lines]
