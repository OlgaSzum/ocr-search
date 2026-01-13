#!/usr/bin/env python3
"""
Batch OCR demo (Tesseract TSV) -> manifest.json do UI.

Uruchomienie (VS Code Terminal, lokalny Mac):
python3 demo/scripts/ocr_batch.py

Wymagania:
- zainstalowany tesseract + język pol (brew)
- obrazy w demo/images/
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
IMAGES_DIR = ROOT / "demo" / "images"
TSV_DIR = ROOT / "demo" / "ocr_tsv"
OUT_DIR = ROOT / "demo" / "out"
MANIFEST_PATH = OUT_DIR / "manifest.json"

LANG = "pol"


@dataclass
class WordBox:
    text: str
    conf: int
    left: int
    top: int
    width: int
    height: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "conf": self.conf,
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
        }


def run_tesseract_tsv(img_path: Path, out_base: Path) -> Path:
    """
    Uruchamia Tesseract i generuje plik TSV.
    out_base to ścieżka bez rozszerzenia (tesseract dopisze .tsv).
    """
    cmd = [
        "tesseract",
        str(img_path),
        str(out_base),
        "-l",
        LANG,
        "tsv",
    ]
    subprocess.run(cmd, check=True)
    tsv_path = out_base.with_suffix(".tsv")
    if not tsv_path.exists():
        raise FileNotFoundError(f"Brak pliku TSV: {tsv_path}")
    return tsv_path


def parse_tsv_words(tsv_path: Path) -> list[WordBox]:
    """
    Parsuje TSV i wyciąga bboxy na poziomie słów.
    """
    words: list[WordBox] = []
    with tsv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            # Tesseract TSV: level 5 = word
            try:
                level = int(row.get("level", "") or 0)
            except ValueError:
                continue
            if level != 5:
                continue

            text = (row.get("text") or "").strip()
            if not text:
                continue

            conf = int(float(row.get("conf") or "-1"))
            left = int(row.get("left") or 0)
            top = int(row.get("top") or 0)
            width = int(row.get("width") or 0)
            height = int(row.get("height") or 0)

            # Prosty filtr demo: usuń śmieci
            if conf < 40:
                continue
            if len(text) == 1 and not text.isdigit():
                continue

            words.append(WordBox(text=text, conf=conf, left=left, top=top, width=width, height=height))
    return words


def build_full_text(words: list[WordBox]) -> str:
    """
    Skleja tekst ze słów (prosto). Do demo wystarczy.
    """
    return " ".join(w.text for w in words)


def main() -> None:
    if not IMAGES_DIR.exists():
        raise SystemExit(f"Brak katalogu: {IMAGES_DIR}")

    TSV_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    image_paths = sorted([p for p in IMAGES_DIR.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}])
    if not image_paths:
        raise SystemExit(f"Brak obrazów w: {IMAGES_DIR}")

    items: list[dict[str, Any]] = []
    for img_path in image_paths:
        stem = img_path.stem
        out_base = TSV_DIR / stem

        print(f"OCR: {img_path.name}")
        tsv_path = run_tesseract_tsv(img_path, out_base)
        words = parse_tsv_words(tsv_path)
        full_text = build_full_text(words)

        items.append(
            {
                "id": stem,
                "file_name": img_path.name,
                "image_rel_path": f"../images/{img_path.name}",
                "tsv_rel_path": f"../ocr_tsv/{tsv_path.name}",
                "full_text": full_text,
                "words": [w.to_dict() for w in words],
            }
        )

    manifest = {
        "version": "demo-1",
        "lang": LANG,
        "items": items,
    }

    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK -> {MANIFEST_PATH}")


if __name__ == "__main__":
    main()