let currentDataset = null;
let datasetsInfo = [];

async function init() {
  const res = await fetch("/api/datasets");
  datasetsInfo = await res.json();

  if (datasetsInfo.length === 0) return;

  const switchEl = document.getElementById("dataset-switch");
  switchEl.innerHTML = "";

  if (datasetsInfo.length <= 1) {
    switchEl.style.display = "none";
  } else {
    switchEl.style.display = "flex";
  }

  datasetsInfo.forEach((ds, i) => {
    const btn = document.createElement("button");
    btn.className = "dataset-tab" + (i === 0 ? " active" : "");
    btn.textContent = ds.label;
    btn.dataset.key = ds.key;
    btn.addEventListener("click", () => selectDataset(ds.key));
    switchEl.appendChild(btn);
  });

  selectDataset(datasetsInfo[0].key);
}

async function selectDataset(key) {
  currentDataset = key;

  document.querySelectorAll(".dataset-tab").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.key === key);
  });

  document.getElementById("result-area").innerHTML = "";
  loadDocuments(key);
  loadSampleChips(key);
}

async function loadDocuments(key) {
  const listEl = document.getElementById("doc-list");
  listEl.innerHTML = '<p class="loading">กำลังโหลด...</p>';

  try {
    const res = await fetch(`/api/documents?dataset=${encodeURIComponent(key)}`);
    const docs = await res.json();

    if (!Array.isArray(docs) || docs.length === 0) {
      listEl.innerHTML = '<p class="loading">ไม่มีเอกสารในชุดข้อมูลนี้</p>';
      return;
    }

    listEl.innerHTML = "";
    docs.forEach(doc => {
      const card = document.createElement("div");
      card.className = "doc-card";
      card.innerHTML = `
        <span class="doc-cat">${escapeHtml(doc.category)}</span>
        <p class="doc-q">${escapeHtml(doc.question)}</p>
        <p class="doc-a">${escapeHtml(truncate(doc.answer, 140))}</p>
      `;
      listEl.appendChild(card);
    });
  } catch (err) {
    listEl.innerHTML = `<div class="error-box"><span class="error-label">Error</span>โหลดเอกสารไม่สำเร็จ: ${escapeHtml(String(err))}</div>`;
  }
}

function loadSampleChips(key) {
  const ds = datasetsInfo.find(d => d.key === key);
  const chipsEl = document.getElementById("sample-chips");
  chipsEl.innerHTML = "";

  (ds?.sample_questions || []).forEach(q => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.textContent = q;
    chip.addEventListener("click", () => {
      document.getElementById("question-input").value = q;
      askQuestion(q);
    });
    chipsEl.appendChild(chip);
  });
}

async function askQuestion(question) {
  const resultArea = document.getElementById("result-area");
  const askButton = document.getElementById("ask-button");

  askButton.disabled = true;
  resultArea.innerHTML = '<p class="loading">กำลังค้นคำตอบ...</p>';

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, dataset: currentDataset }),
    });

    const data = await res.json();

    if (!res.ok) {
      resultArea.innerHTML = `<div class="error-box"><span class="error-label">Error</span>${escapeHtml(data.error || "เชื่อมต่อเซิร์ฟเวอร์ไม่ได้")}</div>`;
      return;
    }

    if (!data.answer) {
      resultArea.innerHTML = `<div class="error-box"><span class="error-label">ไม่พบคำตอบ</span>ลองถามคำถามอื่น หรือใช้คำที่ตรงกับหัวข้อในคลังเอกสารมากขึ้น</div>`;
      return;
    }

    const sourcesHtml = (data.sources || [])
      .map(s => `
        <div class="source-item">
          <strong>${escapeHtml(s.category)}</strong> — ${escapeHtml(s.question)}
          <div style="color:var(--text-dim)">คะแนนความใกล้เคียง: ${s.score.toFixed(3)}</div>
        </div>
      `)
      .join("");

    resultArea.innerHTML = `
      <div class="result-card">
        <p class="result-q">Q: ${escapeHtml(data.question)}</p>
        <p class="result-a">${escapeHtml(data.answer)}</p>
        <div class="result-meta">
          <span>หมวด: ${escapeHtml(data.category)}</span>
          <span>คะแนนความใกล้เคียง: ${data.score.toFixed(3)}</span>
        </div>
        <details class="sources">
          <summary>ดูแหล่งอ้างอิงทั้งหมด (top ${data.sources.length})</summary>
          ${sourcesHtml}
        </details>
      </div>
    `;
  } catch (err) {
    resultArea.innerHTML = `<div class="error-box"><span class="error-label">Error</span>เชื่อมต่อเซิร์ฟเวอร์ไม่ได้: ${escapeHtml(String(err))}</div>`;
  } finally {
    askButton.disabled = false;
  }
}

function truncate(text, n) {
  if (!text) return "";
  return text.length > n ? text.slice(0, n) + "…" : text;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

document.getElementById("ask-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const input = document.getElementById("question-input");
  const q = input.value.trim();
  if (q) askQuestion(q);
});

init();
