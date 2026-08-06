# ⚡ LAB04: AI Models Question Answering System (RAG Pipeline)

ระบบตอบคำถามและค้นหาข้อมูลด้านโมเดลภาษา AI ด้วยสถาปัตยกรรม **RAG (Retrieval-Augmented Generation)** ที่ผสมผสานการค้นหาแบบความหมาย (**Vector Search - FAISS**) ร่วมกับการค้นหาด้วยคำตรงตัว (**Keyword Search - BM25**) พร้อมอินเทอร์เฟซรองรับทั้ง **CLI Terminal** และ **Web UI App**

---

สมาชิกผู้จัดทำ (Author)
ชื่อ-นามสกุล (Name): นายรัชชานนท์ ศรีไชย
รหัสนักศึกษา (Student ID): 116730462005-3


## 🌟 จุดเด่นของระบบ (Features)

* ** Hybrid Search (BM25 + FAISS Vector Search)**: ค้นหาคำตอบได้ครอบคลุมทั้งคำตรงตัวและคำที่มีความหมายใกล้เคียงกันด้วยสูตร **RRF (Reciprocal Rank Fusion)**
* ** High-Accuracy Thai Embedding (`BAAI/bge-m3`)**: ใช้โมเดล Embedding ระดับท็อป รองรับภาษาไทยและศัพท์เทคนิค AI ได้อย่างลึกซึ้ง
* ** PyThaiNLP Tokenizer**: ตัดคำภาษาไทยเพื่อสร้าง BM25 Index ได้อย่างแม่นยำ
* ** 0.18s Instant Web Response**: ค้นหาและส่งคืนคำตอบอย่างรวดเร็วในระดับมิลลิวินาทีผ่าน Web UI
* ** Multi-Interface Support**:
  * **CLI Mode**: รันแบบ interactive terminal สะดวกต่อการทดสอบ
  * **Web UI Mode**: หน้าเว็บแชทโต้ตอบสไตล์ Glassmorphic Dark Mode แสดงความเร็วและแหล่งอ้างอิง

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

```text
04-RAG-Project/
├── app.py                     # 🌐 Web Server (Flask) สำหรับรันหน้าเว็บ http://127.0.0.1:5000
├── build_index.py             # 🛠️ สคริปต์สำหรับสร้าง FAISS Vector Index และ BM25 Index
├── main.py                    # 💻 สคริปต์สำหรับรันระบบตอบคำถามบน Terminal (CLI)
├── config.py                  # ⚙️ ไฟล์ตั้งค่ากลางของระบบ (โมเดล, พารามิเตอร์, ปิด/เปิดฟีเจอร์)
│
├── data/
│   └── ai_models_qa.txt       # 📚 ชุดข้อมูลฐานความรู้ Q&A ด้านโมเดล AI
│
├── src/                       # 🧩 โค้ดโมดูลหลักของระบบ RAG
│   ├── document_loader.py     # ตัวอ่านและดึงข้อมูลจากไฟล์ Q&A
│   ├── text_splitter.py       # ตัวหั่นข้อความออกเป็น Chunk พร้อมแปะ Metadata
│   ├── embedding_model.py     # ตัวแปลงข้อความให้เป็น Vector Embedding (SentenceTransformers)
│   ├── vector_store.py        # ตัวจัดการ FAISS Index (IndexFlatIP)
│   ├── hybrid_retriever.py    # ตัวค้นหาแบบผสม (BM25 + Dense RRF)
│   ├── rerankers.py           # ตัวคัดกรองจัดอันดับใหม่ (CrossEncoder Reranker)
│   ├── query_transform.py     # ตัวปรับแต่ง/ขยายคำถามก่อนนำไปค้นหา
│   ├── generator.py           # ตัวประกอบ Prompt และสร้างคำตอบ (OpenAI/Ollama/Gemini/NoLLM)
│   └── memory.py              # ตัวจำประวัติบทสนทนา (Multi-turn Context)
│
├── templates/
│   └── index.html             # 🎨 หน้าต่างอินเทอร์เฟซผู้ใช้แบบ Web UI
│
└── vector_db/                 # 💾 โฟลเดอร์เก็บ Index ฐานข้อมูลที่สร้างแล้ว
    ├── document.index         # ไฟล์ FAISS Vector Index
    ├── chunk_store.json       # ไฟล์คลังข้อความและ Metadata
    └── bm25_index.pkl         # ไฟล์ BM25 Index
```

---

## 🚀 ขั้นตอนการติดตั้งและการใช้งาน (Quick Start)

### 1. ติดตั้ง Dependencies ที่จำเป็น
เปิด Terminal ในโฟลเดอร์โครงการ แล้วรันคำสั่ง:
```powershell
pip install flask pythainlp sentence-transformers faiss-cpu rank-bm25 openai
```

### 2. สร้าง Search Index (Build Index)
ก่อนเริ่มใช้งานระบบครั้งแรก หรือเมื่อมีการแก้ไขไฟล์ข้อมูล `data/ai_models_qa.txt` ให้รันคำสั่งสร้าง Index ใหม่:
```powershell
python build_index.py
```
*(ระบบจะสร้างไฟล์ Index ทั้งหมดเก็บไว้ในโฟลเดอร์ `vector_db/`)*

---

### 3. การรันใช้งานระบบ

#### 🅰️ แบบที่ 1: รันผ่าน Web UI (แนะนำ ⭐)
สั่งรันเว็บเซิร์ฟเวอร์:
```powershell
python app.py
```
จากนั้นเปิดบราวเซอร์ไปที่: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**
* สามารถพิมพ์คำถาม หรือคลิกเลือกตัวอย่างคำถามเพื่อดูคำตอบ ความเร็วในการค้นหา และแหล่งอ้างอิงได้ทันที

#### 🅱️ แบบที่ 2: รันผ่าน Terminal (CLI)
สั่งรันผ่านบรรทัดคำสั่ง:
```powershell
python main.py
```
* พิมพ์คำถามลงในช่อง `Q:` และพิมพ์ `exit` หรือ `q` เพื่อให้ออกจากโปรแกรม

---

### 4. การรันประเมินผลระบบ (Evaluation Suite)

หากต้องการรันวัดผลคะแนนและสร้างไฟล์รายงานใน `outputs/`:
```powershell
# 1. สร้างชุดข้อสอบประเมิน (golden_set.json)
python evaluation/build_golden_set.py

# 2. วัดผลความแม่นยำของการค้นหา (eval_retrieval.json)
python evaluation/eval_retrieval.py

# 3. วัดผลคุณภาพคำตอบของ LLM (eval_generation.json)
python evaluation/eval_generation.py
```

---

## ⚙️ การปรับแต่งค่าใน `config.py`

คุณสามารถปรับแต่งการทำงานของระบบ RAG ได้ในไฟล์ [config.py](file:///h:/Advance%20LLM/ATCS-CPE/LAB04/04-RAG-Project/config.py):

| พารามิเตอร์ | ค่าตั้งต้น | คำอธิบาย |
| :--- | :--- | :--- |
| `USE_HYBRID` | `True` | เปิด/ปิดการค้นหาแบบผสม (BM25 + Vector Search) |
| `USE_RERANK` | `False` | เปิด/ปิดการ Re-rank จัดอันดับด้วย Cross-Encoder (ปิดเพื่อความเร็วในการค้นหา) |
| `USE_LLM` | `False` | `False` = แสดงผลข้อความจากคลังข้อมูลดิบๆ โดยไม่ใช้ LLM / `True` = ใช้ LLM สรุปคำตอบ |
| `EMBEDDING_MODEL_NAME` | `"BAAI/bge-m3"` | เปลี่ยนโมเดลสร้าง Vector Embedding (เช่น `BAAI/bge-m3` หรือ `intfloat/multilingual-e5-small`) |
| `LLM_PROVIDER` | `"ollama"` | เลือกระบบ LLM ที่จะใช้งาน (`ollama`, `openai`, `gemini`, `typhoon`) |

---

## 📝 หมายเหตุ
* หากมีการแก้ไขค่า `EMBEDDING_MODEL_NAME`, `CHUNK_SIZE` หรือแก้ไขข้อมูลใน `ai_models_qa.txt` จะต้องรัน `python build_index.py` ใหม่เสมอเพื่อให้ Index อัปเดตล่าสุด
