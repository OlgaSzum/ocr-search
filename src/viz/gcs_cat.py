import subprocess

def gcs_cat_bytes(gs_path: str) -> bytes:
    """
    Pobiera plik z GCS przez `gcloud storage cat` i zwraca bytes.

    gs_path – pełna ścieżka, np. "gs://ocr-2026/photos/0002.jpg"
    """
    r = subprocess.run(
        ["gcloud", "storage", "cat", gs_path],
        capture_output=True,
    )
    if r.returncode != 0 or not r.stdout:
        err = (r.stderr or b"").decode("utf-8", errors="ignore")[:800]
        raise RuntimeError(f"gcloud storage cat failed for {gs_path}\n{err}")
    return r.stdout
