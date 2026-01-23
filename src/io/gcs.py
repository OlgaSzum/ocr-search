"""
GCS I/O helpers.
"""

from google.cloud import storage
from typing import List


def list_images(bucket: str, prefix: str = "") -> List[str]:
    """
    Zwraca listę gs://... URI dla obrazów w buckecie pod danym prefixem.
    Filtruje podstawowe formaty rastrowe.
    """
    client = storage.Client()
    bkt = client.bucket(bucket)

    exts = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp")
    uris: List[str] = []

    for blob in client.list_blobs(bkt, prefix=prefix):
        name = blob.name.lower()
        if name.endswith(exts):
            uris.append(f"gs://{bucket}/{blob.name}")

    return uris
