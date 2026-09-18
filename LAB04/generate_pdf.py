import os
import re
import subprocess
import markdown

base_dir = os.path.dirname(os.path.abspath(__file__))
md_path = os.path.join(base_dir, "LAB04_SUMMARY_GUIDE.md")
html_path = os.path.join(base_dir, "LAB04_SUMMARY_GUIDE.html")
pdf_path = os.path.join(base_dir, "LAB04_SUMMARY_GUIDE.pdf")

with open(md_path, "r", encoding="utf-8") as f:
    md_text = f.read()

# Render mermaid diagram into a structured visual HTML block
def render_flowchart_html():
    return """
    <div class="flowchart-container">
      <div class="flow-step user-query">
        <span class="step-badge">INPUT</span>
        <strong>คำถามของผู้ใช้ (User Query)</strong>
      </div>
      <div class="arrow-down">↓</div>
      <div class="flow-step step-transform">
        <span class="step-badge">STEP 1</span>
        <strong>Query Transform & Normalize</strong> (<code>src/query_transform.py</code>)
        <div class="sub-desc">ตัดคำลงท้าย (ครับ/ค่ะ), ปรับคำสแลง, หรือขยายคำถามด้วย LLM (Rewrite/Multi-query)</div>
      </div>
      <div class="arrow-down">↓</div>
      <div class="retrieval-box">
        <div class="retrieval-title">STEP 2: HYBRID RETRIEVAL (<code>src/hybrid_retriever.py</code>)</div>
        <div class="retrieval-branches">
          <div class="branch branch-dense">
            <strong>Dense Vector Search</strong><br/>
            FAISS (<code>IndexFlatIP</code>)<br/>
            Embedding Model: <code>bge-m3</code> (1024 dims)
          </div>
          <div class="branch branch-rrf">
            <strong>Reciprocal Rank Fusion (RRF)</strong><br/>
            รวมอันดับด้วยสูตร:<br/>
            <code>Score = 1 / (60 + rank)</code>
          </div>
          <div class="branch branch-sparse">
            <strong>Sparse Keyword Search</strong><br/>
            BM25 (<code>BM25Okapi</code>)<br/>
            Tokenize ไทยด้วย PyThaiNLP (<code>newmm</code>)
          </div>
        </div>
      </div>
      <div class="arrow-down">↓ <em>ดึงผู้เข้ารอบ Top-20 Candidates</em></div>
      <div class="flow-step step-rerank">
        <span class="step-badge">STEP 3</span>
        <strong>Cross-Encoder Reranker</strong> (<code>src/rerankers.py</code>)<br/>
        โมเดล <code>BAAI/bge-reranker-v2-m3</code> ประเมินคู่ (Query, Document) คัดเหลือ <strong>Top-3 Chunks</strong>
      </div>
      <div class="arrow-down">↓</div>
      <div class="flow-step step-llm">
        <span class="step-badge">STEP 4</span>
        <strong>Generator & LLM</strong> (<code>src/generator.py</code> & <code>src/prompt_templates.py</code>)<br/>
        ประกอบ Prompt ร่วมกับ Context และประวัติเก่า ส่งให้ LLM (Ollama / OpenAI / Gemini) สร้างคำตอบพร้อมเลขอ้างอิง <code>[n]</code>
      </div>
      <div class="arrow-down">↓</div>
      <div class="flow-step step-memory">
        <span class="step-badge">STEP 5</span>
        <strong>Conversation Memory</strong> (<code>src/memory.py</code>)<br/>
        จดจำบริบทคำถาม-คำตอบ เพื่อรองรับบทสนทนาต่อเนื่อง (Multi-turn Context)
      </div>
    </div>
    """

# Replace markdown mermaid block with the rendered visual flowchart
md_text = re.sub(r'```mermaid\s+flowchart TD.*?```', render_flowchart_html(), md_text, flags=re.DOTALL)

# Convert markdown to HTML
html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'nl2br'])

html_template = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<title>LAB04 Summary Guide - RAG Pipeline</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sarabun:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Prompt:wght@400;500;600;700&family=Fira+Code:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
<style>
  @page {{
    size: A4;
    margin: 18mm 14mm 18mm 14mm;
  }}
  * {{
    box-sizing: border-box;
  }}
  body {{
    font-family: 'Sarabun', 'Segoe UI', Tahoma, sans-serif;
    font-size: 13px;
    line-height: 1.6;
    color: #1e293b;
    background: #ffffff;
    margin: 0;
    padding: 0;
  }}
  h1, h2, h3, h4 {{
    font-family: 'Prompt', 'Sarabun', sans-serif;
    color: #0f172a;
    page-break-after: avoid;
    break-after: avoid;
  }}
  h1 {{
    font-size: 22px;
    border-bottom: 2.5px solid #2563eb;
    padding-bottom: 8px;
    margin-top: 0;
    margin-bottom: 14px;
    color: #1d4ed8;
  }}
  h2 {{
    font-size: 16px;
    border-bottom: 1.5px solid #e2e8f0;
    padding-bottom: 6px;
    margin-top: 24px;
    margin-bottom: 12px;
    color: #0f172a;
  }}
  h3 {{
    font-size: 14px;
    margin-top: 16px;
    margin-bottom: 8px;
    color: #1e40af;
  }}
  p, li {{
    text-align: justify;
  }}
  ul, ol {{
    margin-top: 4px;
    margin-bottom: 10px;
    padding-left: 20px;
  }}
  li {{
    margin-bottom: 4px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 12px;
    page-break-inside: avoid;
    break-inside: avoid;
  }}
  th, td {{
    border: 1px solid #cbd5e1;
    padding: 7px 9px;
    text-align: left;
    vertical-align: top;
  }}
  th {{
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 600;
  }}
  tr:nth-child(even) {{
    background-color: #f8fafc;
  }}
  code {{
    font-family: 'Fira Code', 'Consolas', monospace;
    font-size: 11.5px;
    background: #f1f5f9;
    color: #0369a1;
    padding: 1.5px 4.5px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
  }}
  pre {{
    background: #0f172a;
    color: #f8fafc;
    padding: 10px 14px;
    border-radius: 6px;
    overflow-x: auto;
    font-family: 'Fira Code', monospace;
    font-size: 11.5px;
    page-break-inside: avoid;
    break-inside: avoid;
    white-space: pre-wrap;
    word-break: break-word;
    line-height: 1.45;
  }}
  pre code {{
    background: transparent;
    color: inherit;
    padding: 0;
    border: none;
  }}
  blockquote {{
    border-left: 4px solid #3b82f6;
    margin: 10px 0;
    padding: 8px 12px;
    background: #eff6ff;
    color: #1e40af;
    border-radius: 0 6px 6px 0;
    page-break-inside: avoid;
    break-inside: avoid;
  }}
  hr {{
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 16px 0;
  }}
  
  /* Flowchart Styling */
  .flowchart-container {{
    display: flex;
    flex-direction: column;
    align-items: center;
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px;
    margin: 14px 0;
    page-break-inside: avoid;
    break-inside: avoid;
  }}
  .flow-step {{
    background: #ffffff;
    border: 1.5px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 14px;
    width: 90%;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}
  .step-badge {{
    display: inline-block;
    background: #2563eb;
    color: #ffffff;
    font-size: 10px;
    font-weight: 700;
    padding: 1px 6px;
    border-radius: 4px;
    margin-right: 6px;
  }}
  .sub-desc {{
    font-size: 11px;
    color: #64748b;
    margin-top: 2px;
  }}
  .arrow-down {{
    color: #3b82f6;
    font-weight: bold;
    font-size: 13px;
    margin: 4px 0;
  }}
  .retrieval-box {{
    border: 1.5px dashed #3b82f6;
    background: #eff6ff;
    border-radius: 6px;
    padding: 10px;
    width: 95%;
    text-align: center;
  }}
  .retrieval-title {{
    font-weight: 700;
    color: #1d4ed8;
    font-size: 11.5px;
    margin-bottom: 8px;
  }}
  .retrieval-branches {{
    display: flex;
    justify-content: space-between;
    gap: 8px;
  }}
  .branch {{
    flex: 1;
    background: #ffffff;
    border: 1px solid #bfdbfe;
    border-radius: 5px;
    padding: 6px 8px;
    font-size: 11px;
    color: #1e293b;
  }}
  .branch-rrf {{
    background: #fef3c7;
    border-color: #fde68a;
    color: #92400e;
  }}
  .step-rerank {{
    border-color: #8b5cf6;
    background: #faf5ff;
  }}
  .step-rerank .step-badge {{
    background: #7c3aed;
  }}
  .step-llm {{
    border-color: #10b981;
    background: #ecfdf5;
  }}
  .step-llm .step-badge {{
    background: #059669;
  }}
  .step-memory {{
    border-color: #f59e0b;
    background: #fffbeb;
  }}
  .step-memory .step-badge {{
    background: #d97706;
  }}
</style>
<script>
  document.addEventListener("DOMContentLoaded", function() {{
    if (typeof renderMathInElement !== 'undefined') {{
      renderMathInElement(document.body, {{
        delimiters: [
          {{left: "$$", right: "$$", display: true}},
          {{left: "$", right: "$", display: false}}
        ]
      }});
    }}
  }});
</script>
</head>
<body>
{html_body}
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"Generated HTML at: {html_path}")

# Run Edge Headless to print PDF
edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge):
    edge = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

cmd = [
    edge,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    "--run-all-compositor-stages-before-draw",
    "--virtual-time-budget=3000",
    f"--print-to-pdf={pdf_path}",
    html_path
]

print("Converting to PDF using browser engine...")
subprocess.run(cmd, check=True)

if os.path.exists(pdf_path):
    size_kb = os.path.getsize(pdf_path) / 1024
    print(f"SUCCESS: PDF created at {pdf_path} ({size_kb:.1f} KB)")
else:
    print("FAILED to create PDF.")
