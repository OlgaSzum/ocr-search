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


def run_ocr(
    gcs_uri: str,
    *,
    file_id: Optional[str] = None,
    detect_script: bool = True,
) -> List[Dict]:
    """
    Wykonuje OCR na pojedynczym obrazie z Google Cloud Storage.

    Parametry:
    ----------
    gcs_uri : str
        Pełna ścieżka do obrazu, np. 'gs://bucket/path/image.jpg'

    file_id : Optional[str]
        Stabilny identyfikator obrazu. Jeśli None, będzie generowany
        deterministycznie w kolejnym etapie implementacji.

    detect_script : bool
        Czy wykrywać pismo (latin / cyrillic / hebrew) na podstawie Unicode.

    Zwraca:
    -------
    List[Dict]
        Lista rekordów zgodnych z kontraktem CSV.

    Na tym etapie:
    - funkcja nie wywołuje jeszcze Google Vision API
    - zwraca pustą listę
    """
    # TODO: implementacja OCR (Google Vision API)
    return []