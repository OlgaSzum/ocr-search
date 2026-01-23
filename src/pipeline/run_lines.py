import csv
import argparse
from typing import List, Dict

from src.ocr.postprocess import words_to_lines

LINE_FIELDS = [
    "text",
    "file_name",
    "file_id",
    "gcs_path",
    "page",
    "line_id",
    "bbox_norm",
    "script",
    "source",
]


def read_words(path: str) -> List[Dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_lines(path: str, rows: List[Dict]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LINE_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in LINE_FIELDS})


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="ocr_blocks.csv")
    p.add_argument("--output", required=True, help="ocr_lines.csv")
    p.add_argument("--y-threshold", type=float, default=20.0)
    args = p.parse_args()

    words = read_words(args.input)
    lines = words_to_lines(words, y_threshold_px=args.y_threshold)
    write_lines(args.output, lines)
    print(f"[DONE] Wrote {len(lines)} lines to {args.output}")


if __name__ == "__main__":
    main()
