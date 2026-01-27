# ### 10. Galeria: duże miniatury z bboxami (delegowane do src/viz/gallery.py)

from src.viz.gallery import load_image_bytes, thumb_with_bboxes, pil_to_data_uri

MAX_SIDE = 720
LIMIT_GALLERY = 50  # zwiększ, jeśli chcesz; 0/None = bez limitu

files = sorted(df["file_name"].dropna().astype(str).unique().tolist())

if len(files) == 0:
    print("[WARN] df nie zawiera żadnych file_name (lista plików pusta).")
else:
    if LIMIT_GALLERY and len(files) > LIMIT_GALLERY:
        print(f"[INFO] Galeria: pokazuję {LIMIT_GALLERY}/{len(files)} plików (LIMIT_GALLERY).")
        files = files[:LIMIT_GALLERY]

    cards = []
    ok = 0
    missing = 0

    for fn in files:
        rows = df[df["file_name"] == fn]
        try:
            img_bytes = load_image_bytes(fn, gcs_photos_prefix=GCS_PHOTOS_PREFIX, photos_dir=PHOTOS_DIR)
            thumb = thumb_with_bboxes(img_bytes, rows, max_side=MAX_SIDE)
            uri = pil_to_data_uri(thumb)
            ok += 1
            cards.append(f"""
            <div style="width:{MAX_SIDE+40}px; margin:10px;">
                <div style="font-size:12px; margin-bottom:6px;">{fn}</div>
                <img src="{uri}" style="max-width:{MAX_SIDE}px; border:1px solid #ddd;" />
            </div>
            """)
        except Exception as e:
            missing += 1
            cards.append(f"""
              <div style="width:520px; margin:10px; border:1px solid #f2f2f2; padding:10px;">
                <div style="font-size:12px; margin-bottom:6px;">{fn}</div>
                <div style="font-size:12px; color:#a00;">Brak obrazu / błąd odczytu</div>
                <div style="font-size:11px; white-space:pre-wrap;">{str(e)[:350]}</div>
              </div>
            """)

    print(f"[DONE] Galeria: OK={ok}, błędy={missing}, razem={ok+missing}")

    html = "<div style='display:flex; flex-wrap:wrap; align-items:flex-start;'>" + "\n".join(cards) + "</div>"
    display(HTML(html))
