async function loadManifest() {
  const res = await fetch("../out/manifest.json");
  if (!res.ok) throw new Error("Brak demo/out/manifest.json (uruchom ocr_batch.py)");
  return await res.json();
}

function getIgnoreList() {
  const raw = document.getElementById("ignorePhrases").value || "";
  return raw
    .split("\n")
    .map(s => s.trim())
    .filter(Boolean)
    .map(s => s.toLowerCase());
}

function isIgnoredWord(wordText, ignoreList) {
  const t = (wordText || "").toLowerCase();
  if (!t) return false;
  // prosta heurystyka: jeśli słowo jest częścią którejś frazy lub fraza częścią słowa
  return ignoreList.some(p => t.includes(p) || p.includes(t));
}

function snippet(text, n=80) {
  const t = (text || "").trim();
  return t.length <= n ? t : t.slice(0, n) + "…";
}

function drawOverlay(imgEl, canvas, words, ignoreList, hideIgnored) {
  const ctx = canvas.getContext("2d");

  // Rozmiar wyświetlany (CSS px)
  const dispW = imgEl.clientWidth;
  const dispH = imgEl.clientHeight;

  // Rozmiar naturalny (piksele obrazu)
  const natW = imgEl.naturalWidth;
  const natH = imgEl.naturalHeight;

  // Canvas w CSS px (żeby nakładka idealnie pasowała)
  canvas.style.width = dispW + "px";
  canvas.style.height = dispH + "px";

  // Canvas w pikselach urządzenia dla ostrości
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.round(dispW * dpr);
  canvas.height = Math.round(dispH * dpr);

  // Skalowanie z naturalnych px -> wyświetlane px
  const sx = dispW / natW;
  const sy = dispH / natH;

  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, dispW, dispH);

  for (const wd of words) {
    const ignored = isIgnoredWord(wd.text, ignoreList);
    if (hideIgnored && ignored) continue;

    const x = wd.left * sx;
    const y = wd.top * sy;
    const w = wd.width * sx;
    const h = wd.height * sy;

    ctx.lineWidth = 2;
    ctx.strokeStyle = ignored ? "rgba(180,180,180,0.9)" : "rgba(0,160,0,0.9)";
    ctx.fillStyle = ignored ? "rgba(180,180,180,0.15)" : "rgba(0,160,0,0.10)";

    ctx.strokeRect(x, y, w, h);
    ctx.fillRect(x, y, w, h);
  }
}

function renderTable(items) {
  const tbody = document.querySelector("#resultsTable tbody");
  tbody.innerHTML = "";
  for (const it of items) {
    const tr = document.createElement("tr");
    tr.dataset.itemId = it.id;

    const td1 = document.createElement("td");
    td1.textContent = it.file_name;

    const td2 = document.createElement("td");
    td2.textContent = snippet(it.full_text);

    tr.appendChild(td1);
    tr.appendChild(td2);

    tbody.appendChild(tr);
  }
}

function setupInteractions(manifest) {
  const items = manifest.items || [];
  const imgEl = document.getElementById("previewImg");
  const canvas = document.getElementById("overlay");
  const fullTextEl = document.getElementById("fullText");
  const hideIgnoredEl = document.getElementById("hideIgnored");
  const ignoreEl = document.getElementById("ignorePhrases");

  let current = null;

  function updateView(it) {
    current = it;
    imgEl.src = it.image_rel_path;
    fullTextEl.textContent = it.full_text || "";

    imgEl.onload = () => {
      const ignoreList = getIgnoreList();
      drawOverlay(imgEl, canvas, it.words || [], ignoreList, hideIgnoredEl.checked);
    };
  }

  document.querySelector("#resultsTable tbody").addEventListener("click", (e) => {
    const tr = e.target.closest("tr");
    if (!tr) return;
    const it = items.find(x => x.id === tr.dataset.itemId);
    if (it) updateView(it);
  });

  function redraw() {
    if (!current) return;
    const ignoreList = getIgnoreList();
    drawOverlay(imgEl, canvas, current.words || [], ignoreList, hideIgnoredEl.checked);
  }

  hideIgnoredEl.addEventListener("change", redraw);
  ignoreEl.addEventListener("input", redraw);

  if (items.length) updateView(items[0]);
}

function renderGallery(items) {
  const gallery = document.getElementById("gallery");
  const hideIgnoredEl = document.getElementById("galleryHideIgnored");
  const ignoreEl = document.getElementById("ignorePhrases");

  gallery.innerHTML = "";

  function buildCard(it) {
    const card = document.createElement("div");
    card.className = "card";

    const title = document.createElement("div");
    title.className = "cardTitle";
    title.textContent = it.file_name;

    const wrap = document.createElement("div");
    wrap.className = "thumbWrap";

    const row = document.createElement("div");
    row.className = "cardRow";

    const textBox = document.createElement("div");
    textBox.className = "cardText";

    let expanded = false;
    const full = it.full_text || "(brak tekstu)";
    const short = snippet(full, 220) || "(brak tekstu)";

    function renderText() {
      textBox.innerHTML = `<div class="muted">OCR:</div>${expanded ? full : short}`;
    }

    renderText();

    card.addEventListener("click", (e) => {
      // nie przełączaj, jeśli użytkownik zaznacza tekst
      if (window.getSelection && String(window.getSelection())) return;
      expanded = !expanded;
      renderText();
    });
    
    row.appendChild(wrap);
    row.appendChild(textBox);

    card.appendChild(title);
    card.appendChild(row);
    
    const img = document.createElement("img");
    img.className = "thumbImg";
    img.alt = it.file_name;
    img.src = it.image_rel_path;

    const canvas = document.createElement("canvas");
    canvas.className = "thumbCanvas";

    wrap.appendChild(img);
    wrap.appendChild(canvas);

    function redraw() {
      const ignoreList = getIgnoreList();

      requestAnimationFrame(() => {
        if (!img.clientWidth || !img.clientHeight) return;
        drawOverlay(img, canvas, it.words || [], ignoreList, hideIgnoredEl.checked);
      });
    }

    img.onload = redraw;
    hideIgnoredEl.addEventListener("change", redraw);
    ignoreEl.addEventListener("input", redraw);

    return card;
  }

  for (const it of items) {
    gallery.appendChild(buildCard(it));
  }
}

(async function main() {
  const manifest = await loadManifest();
  const items = manifest.items || [];
  renderTable(items);
  setupInteractions(manifest);
  renderGallery(items);
})();