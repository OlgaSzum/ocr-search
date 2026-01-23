"""
Batch runner for OCR.

Odpowiedzialność (docelowo):
- listowanie obrazów w Google Cloud Storage
- wywołanie ocr.vision_ocr.run_ocr dla każdego obrazu
- zapis wyników do jednego pliku CSV

Na tym etapie:
- tylko interfejs CLI (argparse)
- bez logiki OCR
- bez dostępu do GCS
"""

import argparse
import sys


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run OCR on images stored in Google Cloud Storage."
    )

    parser.add_argument(
        "--bucket",
        required=True,
        help="Nazwa bucketu GCS, np. ocr-2026",
    )

    parser.add_argument(
        "--prefix",
        default="",
        help="Prefix w bucket (np. 'photos/1946/'). Domyślnie: cały bucket.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Ścieżka do pliku wyjściowego CSV (lokalnie).",
    )

    parser.add_argument(
        "--ocr-language",
        default="pl",
        help="Preferowany język OCR (language hint), domyślnie: pl.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Nie wykonuje OCR. Tylko wypisuje, co by zostało zrobione.",
    )

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # Na tym etapie: tylko echo parametrów
    print("OCR batch runner (CLI stub)")
    print("--------------------------")
    print(f"Bucket:        {args.bucket}")
    print(f"Prefix:        {args.prefix}")
    print(f"Output CSV:    {args.output}")
    print(f"OCR language:  {args.ocr_language}")
    print(f"Dry run:       {args.dry_run}")

    print("\n[INFO] Logika OCR nie jest jeszcze zaimplementowana.")
    print("[INFO] Ten krok definiuje wyłącznie interfejs uruchomieniowy.")


if __name__ == "__main__":
    sys.exit(main())