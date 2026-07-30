# RAG Lab — วิธีการรัน

โปรเจกต์ระบบ RAG (Retrieval-Augmented Generation) ที่ดึงคำตอบจากฐานความรู้ Q&A
ผ่าน Embedding + FAISS แล้วโชว์ผลผ่านหน้าเว็บ

---

## 1. ติดตั้งครั้งแรก

```bash
cd LAB01
pip install -r requirements.txt
```

การติดตั้งครั้งแรกจะโหลดโมเดล embedding (`paraphrase-multilingual-MiniLM-L12-v2`)
มาเก็บไว้ในเครื่องด้วย ต้องต่อเน็ตตอนติดตั้ง ใช้เวลาสักพัก

---

## 2. สร้างฐานความรู้ (ต้องทำก่อนรันเว็บเสมอ)

มี 2 วิธี เลือกอย่างใดอย่างหนึ่ง

### วิธีที่ 1 — รันทีเดียวจบ (แนะนำ)
```bash
python build_dataset.py ai_models
```
คำสั่งนี้ทำหน้าที่แทน Lab 1–4 ทั้งหมด (extract → chunk → embed → build index)
ในคำสั่งเดียว จะได้ไฟล์ output ครบ:
- `outputs/extracted_text.json`, `outputs/chunks.json`, `outputs/embeddings.npy`
- `vector_db/document.index`, `vector_db/chunk_store.json`

### วิธีที่ 2 — รันทีละ Lab (ไว้ดูขั้นตอนแบบละเอียด/เก็บส่งงาน)
```bash
python labs/lab01_extract_text.py
python labs/lab02_chunking.py
python labs/lab03_create_embeddings.py
python labs/lab04_create_vector_db.py
```
รันตามลำดับนี้เท่านั้น เพราะแต่ละไฟล์ใช้ output ของไฟล์ก่อนหน้าต่อกัน

> ทั้งสองวิธีอ่านไฟล์ต้นทางจาก `config.SOURCE_FILE` (ตอนนี้ตั้งเป็น `data/ai_models_qa.txt`)
> ถ้าเปลี่ยน dataset ใหม่ ต้องแก้ `config.py` แล้วรันขั้นตอนนี้ซ้ำทุกครั้ง

---

## 3. ทดสอบระบบค้นหาแบบ CLI (ไม่บังคับ)

ใช้ดูผลลัพธ์ในเทอร์มินัลก่อนขึ้นเว็บ

```bash
python labs/lab05_query_embedding.py     # ทดสอบแปลงคำถามเป็นเวกเตอร์
python labs/lab06_similarity_search.py   # ทดสอบค้นหา top-k
python labs/lab07_complete_retrieval.py  # รันครบ pipeline หลายคำถาม เซฟผลเป็น outputs/retrieval_results.json
```

---

## 4. รันหน้าเว็บ

```bash
python app.py
```

รอจนเห็นบรรทัดประมาณนี้ในเทอร์มินัล:
```
* Running on http://127.0.0.1:5000
```

เปิดเบราว์เซอร์ไปที่ **http://127.0.0.1:5000** พิมพ์คำถามแล้วกด "ถาม →"
กด `Ctrl+C` ในเทอร์มินัลเพื่อปิดเซิร์ฟเวอร์

---

## โครงสร้างโปรเจกต์

```
RAG-Project/
├── data/                     ไฟล์ dataset ต้นฉบับ (.txt)
├── outputs/                  ไฟล์ผลลัพธ์ระหว่างทาง (json, npy)
├── vector_db/                FAISS index + chunk store
├── src/                      โค้ดหลัก (document_loader, text_splitter, embedding_model, vector_store, retriever)
├── labs/                     ไฟล์ lab01–lab07 (การบ้าน ทำทีละขั้น)
├── templates/, static/       หน้าเว็บ (HTML/CSS/JS)
├── config.py                 ค่าคงที่และ path ทั้งหมด
├── build_dataset.py          สคริปต์รันทั้ง pipeline ทีเดียว
└── app.py                    Flask server สำหรับหน้าเว็บ
```

---

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ / วิธีแก้ |
|---|---|
| `python app.py` แล้วเปิดเว็บไม่มีคำตอบ / error 503 | ยังไม่ได้รันขั้นตอนที่ 2 (สร้างฐานความรู้) หรือรันไม่ครบ ให้รัน `python build_dataset.py ai_models` ก่อน |
| เห็น warning สีเหลือง/แดงเต็มเทอร์มินัลตอนรัน (`oneDNN`, `tf.losses...`) | เป็น log ปกติจาก TensorFlow ไม่ใช่ error ไม่กระทบการทำงาน เพิกเฉยได้ |
| เปลี่ยน `data/*.txt` แล้วเว็บยังตอบข้อมูลเก่า | ต้องรัน `python build_dataset.py ai_models` ใหม่ทุกครั้งที่แก้ dataset เพราะ index เก่าไม่อัปเดตอัตโนมัติ |
| อยากเปลี่ยนคำถามตัวอย่าง (chip) บนเว็บ | แก้ `sample_questions` ใน `config.py` ใต้ `DATASETS["ai_models"]` |
