"""
Batch runner for OCR.
"""

import argparse
import csv
import sys
from typing import List, Dict

from src.io.gcs import list_images
from src.ocr.vision_ocr import run_ocr


CSV_FIELDS = [
    "text",
    "file_name",
    "file_id",
    "gcs_path",
    "page",
    "block_id",
    "bbox_norm",
    "confidence",
    "script",
    "source",
]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run batch OCR on images stored in Google Cloud Storage."
    )

    parser.add_argument("--bucket", required=True)
    parser.add_argument("--prefix", default="")
    parser.add_argument("--output", required=True)
    parser.add_argument("--ocr-language", default="pl")
    parser.add_argument("--dry-run", action="store_true")

    return parser.parse_args(argv)


def write_csv(path: str, rows: List[Dict]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main(argv=None):
    args = parse_args(argv)

    images = list_images(args.bucket, args.prefix)

    print(f"[INFO] Found {len(images)} images under gs://{args.bucket}/{args.prefix}")

    if args.dry_run:
        for uri in images[:10]:
            print(f"[DRY-RUN] {uri}")
        print("[INFO] Dry-run only. Exiting.")
        return 0

    all_rows: List[Dict] = []

    for idx, uri in enumerate(images, start=1):
        print(f"[INFO] OCR {idx}/{len(images)}: {uri}")
        records = run_ocr(uri, ocr_language_hint=args.ocr_language)

        for rec in records:
            # Upewnij się, że kolejność/klucze są zgodne z CSV_FIELDS
            row = {k: rec.get(k) for k in CSV_FIELDS}
            all_rows.append(row)

    write_csv(args.output, all_rows)
    print(f"[DONE] Wrote {len(all_rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())