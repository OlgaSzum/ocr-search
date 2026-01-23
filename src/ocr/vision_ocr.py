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
        Lista rekordów zgodnych z kontraktem CSV (patrz docstring modułu).

    Na tym etapie:
    - funkcja nie wywołuje jeszcze Google Vision API
    - zwraca pustą listę
    """
    # TODO: implementacja OCR (Google Vision API)
    return []