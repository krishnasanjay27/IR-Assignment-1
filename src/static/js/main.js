// src/static/js/main.js  (replace your existing file with this)

const input = document.getElementById("queryInput");
const btn = document.getElementById("searchBtn");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

async function doSearch(q) {
  statusEl.textContent = "Searching…";
  resultsEl.innerHTML = "";

  try {
    const resp = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q })
    });
    const data = await resp.json();
    if (!resp.ok) {
      statusEl.textContent = "Error: " + (data.error || resp.statusText);
      return;
    }

    const rows = data.results || [];
    statusEl.textContent = `Found ${rows.length} result(s).`;

    if (rows.length === 0) {
      resultsEl.innerHTML = `<div class="text-slate-500">No documents matched your query.</div>`;
      return;
    }

    // render rows
    rows.forEach((r, idx) => {
      const card = document.createElement("div");
      card.className = "p-4 bg-slate-50 border rounded-lg";

      const title = document.createElement("div");
      title.className = "flex justify-between items-start gap-4";
      title.innerHTML = `<div class="font-medium">${idx+1}. ${r.filename}</div>
                         <div class="text-sm text-slate-500">${r.score.toFixed(4)}</div>`;

      const previewDiv = document.createElement("div");
      previewDiv.className = "mt-2 text-sm text-slate-600";
      previewDiv.textContent = "";           // initially empty
      previewDiv.style.display = "none";     // hidden by default
      previewDiv.dataset.loaded = "false";   // track if fetched
      previewDiv.dataset.open = "false";     // track visible state

      card.appendChild(title);
      card.appendChild(previewDiv);

      // Preview / Close button
      const previewBtn = document.createElement("button");
      previewBtn.className = "mt-2 inline-block px-3 py-1 text-sm bg-white border rounded hover:bg-slate-100";
      previewBtn.textContent = "Preview";

      previewBtn.addEventListener("click", async () => {
        const isOpen = previewDiv.dataset.open === "true";

        if (isOpen) {
          // currently open -> close it
          previewDiv.style.display = "none";
          previewDiv.dataset.open = "false";
          previewBtn.textContent = "Preview";
          return;
        }

        // Not open -> open it
        previewDiv.style.display = ""; // show while loading / or after load
        previewDiv.dataset.open = "true";
        previewBtn.textContent = "Loading preview...";

        // If already loaded, just show content and update button
        if (previewDiv.dataset.loaded === "true") {
          previewBtn.textContent = "Close preview";
          return;
        }

        // fetch snippet from server
        try {
          const p = await fetch(`/api/preview?file=${encodeURIComponent(r.filename)}`);
          const pj = await p.json();
          if (p.ok && pj.snippet) {
            previewDiv.textContent = pj.snippet;
            previewDiv.dataset.loaded = "true";
            previewBtn.textContent = "Close preview";
          } else {
            previewDiv.textContent = pj.error || "Could not load preview";
            previewDiv.dataset.loaded = "true";
            previewBtn.textContent = "Close preview";
          }
        } catch (err) {
          previewDiv.textContent = "Preview failed";
          previewDiv.dataset.loaded = "true";
          previewBtn.textContent = "Close preview";
        }
      });

      card.appendChild(previewBtn);
      resultsEl.appendChild(card);
    });

  } catch (err) {
    statusEl.textContent = "Search failed";
  }
}

btn.addEventListener("click", () => {
  const q = input.value.trim();
  if (q) doSearch(q);
});

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    const q = input.value.trim();
    if (q) doSearch(q);
  }
});

// focus input on load
input.focus();
