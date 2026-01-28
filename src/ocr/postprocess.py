"""
Postprocessing OCR: group WORD-level records into LINE-level records.
"""

from typing import List, Dict, Tuple


def _bbox_from_str(bbox: str) -> Tuple[float, float, float, float]:
    x1, y1, x2, y2 = bbox.split(",")
    return float(x1), float(y1), float(x2), float(y2)


def _bbox_union(bboxes: List[Tuple[float, float, float, float]]) -> str:
    xs1 = [b[0] for b in bboxes]
    ys1 = [b[1] for b in bboxes]
    xs2 = [b[2] for b in bboxes]
    ys2 = [b[3] for b in bboxes]
    return f"{min(xs1)},{min(ys1)},{max(xs2)},{max(ys2)}"


def _y_center(bbox: Tuple[float, float, float, float]) -> float:
    return (bbox[1] + bbox[3]) / 2.0


def words_to_lines(
    word_records: List[Dict],
    *,
    y_threshold_px: float = 20.0,
) -> List[Dict]:
    """
    Grupuje rekordy WORD w rekordy LINE na podstawie położenia w osi Y.

    y_threshold_px — maksymalna różnica środków Y (w pikselach),
    aby uznać słowa za należące do tej samej linii.
    """

    # Grupujemy per obraz
    by_file: Dict[str, List[Dict]] = {}
    for r in word_records:
        by_file.setdefault(r["file_id"], []).append(r)

    line_records: List[Dict] = []

    for file_id, words in by_file.items():
        # Parsuj bboxy i sortuj po Y
        enriched = []
        for w in words:
            bbox = _bbox_from_str(w["bbox_norm"])
            enriched.append((w, bbox, _y_center(bbox)))

        enriched.sort(key=lambda x: x[2])  # po y_center

        lines: List[List[Tuple[Dict, Tuple[float, float, float, float]]]] = []

        for w, bbox, yc in enriched:
            placed = False
            for line in lines:
                _, _, line_yc = line[0][0], line[0][1], _y_center(line[0][1])
                if abs(yc - line_yc) <= y_threshold_px:
                    line.append((w, bbox))
                    placed = True
                    break
            if not placed:
                lines.append([(w, bbox)])

        # Dla każdej linii: sortuj po X i sklej tekst
        for line_idx, line in enumerate(lines):
            line_sorted = sorted(line, key=lambda x: x[1][0])  # po x1
            texts = [w["text"] for (w, _) in line_sorted]
            bboxes = [bbox for (_, bbox) in line_sorted]

            line_text = " ".join(texts)
            line_bbox = _bbox_union(bboxes)

            base = line_sorted[0][0]
            rec = {
                "text": line_text,
                "file_name": base["file_name"],
                "file_id": base["file_id"],
                "gcs_path": base["gcs_path"],
                "line_id": line_idx,
                "bbox_norm": line_bbox,
                "source": "gcv_ocr_line",
            }
            line_records.append(rec)

    return line_records
