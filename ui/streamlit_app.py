"""
Streamlit MVP: OCR Review
- Czyta: gs://ocr-2026/ui/images.csv, lines.csv, edits.csv + thumbs_overlay/
- Edytuje: text_edited, keep, excluded, watermark_flag, note
- Zapisuje: edits.csv z powrotem do GCS
"""

import os
import subprocess
import pandas as pd
import streamlit as st

GCS_UI_PREFIX = os.environ.get("GCS_UI_PREFIX", "gs://ocr-2026/ui")
CACHE_DIR = os.environ.get("UI_CACHE_DIR", "outputs/_ui_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

LOCAL_IMAGES = f"{CACHE_DIR}/images.csv"
LOCAL_LINES  = f"{CACHE_DIR}/lines.csv"
LOCAL_EDITS  = f"{CACHE_DIR}/edits.csv"

def gcs_cp(src: str, dst: str):
    subprocess.run(["gcloud", "storage", "cp", src, dst], check=True)

def gcs_exists(gs_path: str) -> bool:
    r = subprocess.run(["gcloud", "storage", "ls", gs_path], capture_output=True, text=True)
    return r.returncode == 0

def refresh_cache():
    gcs_cp(f"{GCS_UI_PREFIX}/images.csv", LOCAL_IMAGES)
    gcs_cp(f"{GCS_UI_PREFIX}/lines.csv",  LOCAL_LINES)
    if gcs_exists(f"{GCS_UI_PREFIX}/edits.csv"):
        gcs_cp(f"{GCS_UI_PREFIX}/edits.csv", LOCAL_EDITS)
    else:
        pd.DataFrame(columns=["image_id","line_id","text_edited","keep","excluded","watermark_flag","note"]).to_csv(
            LOCAL_EDITS, index=False, encoding="utf-8"
        )
        gcs_cp(LOCAL_EDITS, f"{GCS_UI_PREFIX}/edits.csv")

@st.cache_data(show_spinner=False)
def load_data():
    images = pd.read_csv(LOCAL_IMAGES)
    lines  = pd.read_csv(LOCAL_LINES)
    edits  = pd.read_csv(LOCAL_EDITS)
    return images, lines, edits

def save_edits(edits: pd.DataFrame):
    edits.to_csv(LOCAL_EDITS, index=False, encoding="utf-8")
    gcs_cp(LOCAL_EDITS, f"{GCS_UI_PREFIX}/edits.csv")

st.set_page_config(page_title="OCR Review", layout="wide")

with st.sidebar:
    st.write("Źródło:", GCS_UI_PREFIX)
    if st.button("Odśwież z GCS"):
        refresh_cache()
        st.cache_data.clear()

# init cache
if not (os.path.exists(LOCAL_IMAGES) and os.path.exists(LOCAL_LINES) and os.path.exists(LOCAL_EDITS)):
    refresh_cache()

images, lines, edits = load_data()

if "file_name" not in images.columns:
    # fallback: jeśli nie ma file_name, użyj image_id
    images["file_name"] = images["image_id"]

# wybór obrazu
label_map = dict(zip(images["file_name"], images["image_id"]))
file_name = st.selectbox("Wybierz obraz", images["file_name"].tolist())
image_id = label_map[file_name]

colA, colB = st.columns([1, 2], gap="large")

with colA:
    if "thumb_overlay_path" in images.columns:
        ovl = images.loc[images["image_id"] == image_id, "thumb_overlay_path"].iloc[0]
    else:
        ovl = ""

    if isinstance(ovl, str) and ovl.strip():
        local_img = f"{CACHE_DIR}/{image_id}_overlay.jpg"
        try:
            gcs_cp(ovl, local_img)
            st.image(local_img, caption=file_name, use_container_width=True)
        except Exception as e:
            st.warning(f"Nie mogę pobrać miniatury overlay: {e}")
    else:
        st.info("Brak thumb_overlay_path w images.csv. Najpierw wygeneruj thumbs_overlay w notatniku.")

# dane do edycji
dff = lines[lines["image_id"] == image_id].copy()
dff = dff.merge(edits, on=["image_id","line_id"], how="left")

# domyślne wartości
for col, default in {
    "text_edited": "",
    "keep": True,
    "excluded": False,
    "watermark_flag": False,
    "note": "",
}.items():
    if col not in dff.columns:
        dff[col] = default
    else:
        dff[col] = dff[col].fillna(default)

with colB:
    st.write("Edycja linii OCR (dla wybranego obrazu)")

    edited = st.data_editor(
        dff[["line_id","text","text_edited","keep","excluded","watermark_flag","note"]],
        use_container_width=True,
        num_rows="fixed",
        hide_index=True
    )

    if st.button("Zapisz edits.csv do GCS"):
        keep_cols = ["image_id","line_id","text_edited","keep","excluded","watermark_flag","note"]
        new_edits = edited.copy()
        new_edits["image_id"] = image_id
        new_edits = new_edits[keep_cols]

        edits2 = edits[edits["image_id"] != image_id].copy()
        edits2 = pd.concat([edits2, new_edits], ignore_index=True)

        save_edits(edits2)
        st.success("Zapisano edits.csv w GCS.")
        st.cache_data.clear()
