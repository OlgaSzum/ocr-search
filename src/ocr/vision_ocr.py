"""
OCR module (Google Cloud Vision).

Odpowiedzialność:
- wykonanie OCR dla JEDNEGO obrazu z Google Cloud Storage
- zwrot bloków tekstowych jako rekordów do zapisu w CSV

Ten moduł:
- nie zapisuje plików
- nie robi batch processing
- nie łączy się z innymi modułami
- nie implementuje jeszcze wywołania Vision API

Kontrakt danych (1 rekord = 1 wiersz CSV):

file_id       : str
file_name     : str
gcs_path      : str
page          : int        # zawsze 1
block_id      : int        # kolejność bloku w obrazie
text          : str        # surowy tekst OCR
bbox_norm     : str        # "x1,y1,x2,y2" w zakresie [0–1]
confidence    : float | None
script        : str | None # latin | cyrillic | hebrew | mixed | unknown
source        : str        # zawsze "gcv_ocr"
"""

from typing import List, Dict, Optional
from google.cloud import vision
import os
import hashlib


def detect_script_from_text(text: str) -> str:
    """
    Wykrywa pismo (script) na podstawie zakresów Unicode.

    Zwraca jedną z wartości:
    - 'latin'
    - 'cyrillic'
    - 'hebrew'
    - 'mixed'
    - 'unknown'
    """
    if not text:
        return "unknown"

    has_latin = False
    has_cyrillic = False
    has_hebrew = False

    for ch in text:
        code = ord(ch)

        # Hebrew: U+0590–U+05FF
        if 0x0590 <= code <= 0x05FF:
            has_hebrew = True

        # Cyrillic: U+0400–U+04FF
        elif 0x0400 <= code <= 0x04FF:
            has_cyrillic = True

        # Latin (basic + extended): U+0041–U+024F
        elif 0x0041 <= code <= 0x024F:
            has_latin = True

    count = sum([has_latin, has_cyrillic, has_hebrew])

    if count > 1:
        return "mixed"
    if has_hebrew:
        return "hebrew"
    if has_cyrillic:
        return "cyrillic"
    if has_latin:
        return "latin"

    return "unknown"

def _stable_file_id(gcs_uri: str) -> str:
    """
    Generuje stabilny identyfikator pliku na podstawie gcs_uri.
    """
    return hashlib.sha256(gcs_uri.encode("utf-8")).hexdigest()

def run_ocr(
    gcs_uri: str,
    *,
    file_id: Optional[str] = None,
    detect_script: bool = True,
    ocr_language_hint: str = "pl",
) -> List[Dict]:
    """
    Wykonuje OCR na pojedynczym obrazie z Google Cloud Storage.
    """
    client = vision.ImageAnnotatorClient()

    image = vision.Image(source=vision.ImageSource(image_uri=gcs_uri))

    response = client.text_detection(
        image=image,
        image_context=vision.ImageContext(
            language_hints=[ocr_language_hint]
        ),
    )

    if response.error.message:
        raise RuntimeError(response.error.message)

    annotations = response.text_annotations
    if not annotations:
        return []

    if file_id is None:
        file_id = _stable_file_id(gcs_uri)

    file_name = os.path.basename(gcs_uri)

    records: List[Dict] = []

    # annotations[0] = cały tekst; pomijamy
    for idx, ann in enumerate(annotations[1:], start=0):
        text = ann.description.strip()
        if not text:
            continue

        vertices = ann.bounding_poly.vertices
        if len(vertices) < 4:
            continue

        xs = [v.x for v in vertices if v.x is not None]
        ys = [v.y for v in vertices if v.y is not None]
        if not xs or not ys:
            continue

        # Normalizacja bbox do [0–1] NIE jest tu robiona (brak width/height).
        # Na tym etapie zapisujemy surowe wartości pikselowe jako string.
        bbox_norm = f"{min(xs)},{min(ys)},{max(xs)},{max(ys)}"

        script = None
        if detect_script:
            script = detect_script_from_text(text)

        record = {
            "file_id": file_id,
            "file_name": file_name,
            "gcs_path": gcs_uri,
            "page": 1,
            "block_id": idx,
            "text": text,
            "bbox_norm": bbox_norm,
            "confidence": None,
            "script": script,
            "source": "gcv_ocr",
        }

        records.append(record)

    return records