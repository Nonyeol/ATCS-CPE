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
├── app.py                     # 🌐 Web Server (Flask) สำหรับรันหน้าเว็บ http://localhost:5000
├── build_index.py             # 🛠️ สคริปต์สำหรับสร้าง FAISS Vector Index และ BM25 Index
├── main.py                    # 💻 สคริปต์สำหรับรันระบบตอบคำถามบน Terminal (CLI)
├── config.py                  # ⚙️ ไฟล์ตั้งค่ากลางของระบบ (โมเดล, พารามิเตอร์, ปิด/เปิดฟีเจอร์)
├── Dockerfile                 # 🐳 ขั้นตอนสำหรับสร้าง Docker Image
├── requirements.txt           # 📦 รายการ Python dependencies
├── .dockerignore              # 🚫 ไฟล์ที่ไม่ต้องส่งเข้า Docker build context
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

## 🐳 Quick Start ด้วย Docker (แนะนำ)

Docker จะจัดเตรียม Python และ Dependencies ให้ภายใน Container ผู้ใช้งานจึงไม่ต้องติดตั้งแพ็กเกจ Python ของโปรเจกต์ลงในเครื่องโดยตรง

### สิ่งที่ต้องมีก่อนเริ่ม

- [Git](https://git-scm.com/downloads)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) หรือ Docker Engine
- อินเทอร์เน็ตสำหรับดาวน์โหลด Docker Image, Python packages และโมเดล Embedding ในการรันครั้งแรก

ตรวจสอบว่า Docker พร้อมใช้งาน:

```powershell
docker --version
docker info
```

หาก `docker info` เชื่อมต่อไม่ได้ ให้เปิด Docker Desktop และรอจน Docker Engine เริ่มทำงานก่อน

### 1. Clone Repository และเข้าโฟลเดอร์ LAB04

```powershell
git clone https://github.com/Nonyeol/ATCS-CPE.git
cd ATCS-CPE/LAB04/04-RAG-Project
```

หาก Clone Repository ไว้แล้ว ให้เข้าโฟลเดอร์ `LAB04/04-RAG-Project` โดยตรงก่อนรันคำสั่ง Docker ทุกครั้ง

### 2. สร้าง Docker Image

```powershell
docker build -t atcs-lab04-rag:latest .
```

- `-t atcs-lab04-rag:latest` กำหนดชื่อและ Tag ของ Image
- จุด `.` หมายถึงใช้ `Dockerfile` และไฟล์ในโฟลเดอร์ปัจจุบันเป็น Build context
- การ Build ครั้งแรกอาจใช้เวลาหลายนาที เพราะต้องติดตั้ง `sentence-transformers`, PyTorch, FAISS และ Dependencies อื่น

ตรวจสอบว่า Image ถูกสร้างแล้ว:

```powershell
docker image ls
```

### 3. สร้างและรัน Container

```powershell
docker run -d `
  --name atcs-lab04-rag `
  -p 5000:5000 `
  -v lab04-huggingface-cache:/root/.cache/huggingface `
  atcs-lab04-rag:latest
```

สำหรับ Command Prompt, macOS หรือ Linux สามารถใช้คำสั่งบรรทัดเดียว:

```bash
docker run -d --name atcs-lab04-rag -p 5000:5000 -v lab04-huggingface-cache:/root/.cache/huggingface atcs-lab04-rag:latest
```

คำสั่งข้างต้นทำงานดังนี้:

| Option | ความหมาย |
| :--- | :--- |
| `-d` | รัน Container เบื้องหลัง |
| `--name atcs-lab04-rag` | ตั้งชื่อ Container เพื่อใช้อ้างอิงในคำสั่งอื่น |
| `-p 5000:5000` | เชื่อมพอร์ต 5000 ของเครื่องเข้ากับ Flask ใน Container |
| `-v lab04-huggingface-cache:...` | เก็บโมเดล Hugging Face ใน Docker Volume เพื่อไม่ต้องดาวน์โหลดใหม่ทุกครั้ง |

> การรันครั้งแรกจะดาวน์โหลดโมเดล `BAAI/bge-m3` จึงอาจใช้เวลาสักครู่และต้องเชื่อมต่ออินเทอร์เน็ต

### 4. ตรวจสอบสถานะและ Log

```powershell
docker ps
docker logs -f atcs-lab04-rag
```

รอจนพบข้อความว่า RAG Pipeline โหลดสำเร็จ จากนั้นเปิด Web UI ที่:

**[http://localhost:5000](http://localhost:5000)**

กด `Ctrl+C` เพื่อออกจากหน้าติดตาม Log ได้ โดย Container จะยังทำงานอยู่เบื้องหลัง

### 5. หยุดและเปิด Container อีกครั้ง

```powershell
# หยุดชั่วคราว
docker stop atcs-lab04-rag

# เปิด Container เดิม
docker start atcs-lab04-rag

# Restart
docker restart atcs-lab04-rag
```

### 6. หลังแก้ Source Code หรือ Dependencies

Source code ถูก Copy เข้า Docker Image ระหว่าง Build ดังนั้นหลังแก้โค้ด, `requirements.txt` หรือ `Dockerfile` ให้สร้าง Image และ Container ใหม่:

```powershell
docker stop atcs-lab04-rag
docker rm atcs-lab04-rag
docker build -t atcs-lab04-rag:latest .
docker run -d `
  --name atcs-lab04-rag `
  -p 5000:5000 `
  -v lab04-huggingface-cache:/root/.cache/huggingface `
  atcs-lab04-rag:latest
```

Docker Volume `lab04-huggingface-cache` จะยังคงอยู่หลังลบ Container จึงไม่ต้องดาวน์โหลดโมเดลใหม่

### 7. การแก้ปัญหาเบื้องต้น

ดู Container ทั้งหมด รวมตัวที่หยุดไปแล้ว:

```powershell
docker ps -a
```

ดู Log 100 บรรทัดล่าสุด:

```powershell
docker logs --tail 100 atcs-lab04-rag
```

เข้า Shell ภายใน Container:

```powershell
docker exec -it atcs-lab04-rag sh
```

หากพอร์ต 5000 ถูกใช้งานอยู่ ให้เปลี่ยนเฉพาะพอร์ตด้านซ้าย เช่น:

```powershell
docker run -d `
  --name atcs-lab04-rag `
  -p 8080:5000 `
  -v lab04-huggingface-cache:/root/.cache/huggingface `
  atcs-lab04-rag:latest
```

แล้วเปิด `http://localhost:8080`

หากต้องการลบ Container หลังเลิกใช้งาน:

```powershell
docker stop atcs-lab04-rag
docker rm atcs-lab04-rag
```

> ไม่จำเป็นต้องลบ Volume `lab04-huggingface-cache` เว้นแต่ต้องการล้างโมเดลที่ดาวน์โหลดไว้จริง ๆ

---

## 🐍 การรันด้วย Python โดยไม่ใช้ Docker

วิธีนี้เหมาะสำหรับผู้ที่ต้องการแก้โค้ดและทดลองจาก Python environment โดยตรง

### 1. สร้างและเปิด Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. ติดตั้ง Dependencies

```powershell
pip install -r requirements.txt
```

### 3. สร้าง Search Index เมื่อจำเป็น

Repository มี Search Index ที่สร้างไว้แล้วใน `vector_db/` หากแก้ไข `data/ai_models_qa.txt`, `EMBEDDING_MODEL_NAME`, `CHUNK_SIZE` หรือ `CHUNK_OVERLAP` ให้สร้าง Index ใหม่:

```powershell
python build_index.py
```

### 4. เปิด Web UI

```powershell
python app.py
```

จากนั้นเปิด **[http://localhost:5000](http://localhost:5000)**

### 5. รันผ่าน Terminal (CLI)

```powershell
python main.py
```

พิมพ์คำถามในช่อง `Q:` และพิมพ์ `exit` หรือ `q` เพื่อออกจากโปรแกรม

---

## 🧪 การรันประเมินผลระบบ (Evaluation Suite)

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

คุณสามารถปรับแต่งการทำงานของระบบ RAG ได้ในไฟล์ [`config.py`](config.py):

| พารามิเตอร์ | ค่าตั้งต้น | คำอธิบาย |
| :--- | :--- | :--- |
| `USE_HYBRID` | `True` | เปิด/ปิดการค้นหาแบบผสม (BM25 + Vector Search) |
| `USE_RERANK` | `False` | เปิด/ปิดการ Re-rank จัดอันดับด้วย Cross-Encoder (ปิดเพื่อความเร็วในการค้นหา) |
| `USE_LLM` | `False` | `False` = แสดงผลข้อความจากคลังข้อมูลดิบๆ โดยไม่ใช้ LLM / `True` = ใช้ LLM สรุปคำตอบ |
| `EMBEDDING_MODEL_NAME` | `"BAAI/bge-m3"` | เปลี่ยนโมเดลสร้าง Vector Embedding (เช่น `BAAI/bge-m3` หรือ `intfloat/multilingual-e5-small`) |
| `LLM_PROVIDER` | `"ollama"` | เลือกระบบ LLM ที่จะใช้งาน (`ollama`, `openai`, `gemini`, `typhoon`) |

---

## 📝 หมายเหตุ
* หากมีการแก้ไขค่า `EMBEDDING_MODEL_NAME`, `CHUNK_SIZE`, `CHUNK_OVERLAP` หรือข้อมูลใน `ai_models_qa.txt` จะต้องรัน `python build_index.py` ใหม่เพื่อให้ Index อัปเดตล่าสุด
* ค่าเริ่มต้น `USE_LLM=False` ทำให้ระบบตอบจากข้อมูลที่ค้นคืนมาโดยไม่ต้องใช้ API Key หรือ Ollama
* หากเปิด `USE_LLM=True` ต้องตั้งค่า Provider และ Credential ที่เกี่ยวข้องเพิ่มเติมใน `config.py`
