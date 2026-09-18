# ⚡ LAB04: AI Models Question Answering System (RAG Pipeline)

ระบบตอบคำถามและค้นหาข้อมูลด้านโมเดลภาษา AI ด้วยสถาปัตยกรรม **RAG (Retrieval-Augmented Generation)** ที่ผสมผสานการค้นหาแบบความหมาย (**Vector Search - FAISS**) ร่วมกับการค้นหาด้วยคำตรงตัว (**Keyword Search - BM25**) พร้อมอินเทอร์เฟซรองรับทั้ง **CLI Terminal** และ **Web UI App**

---

### สมาชิกผู้จัดทำ (Author)
* **ชื่อ-นามสกุล**: นายรัชชานนท์ ศรีไชย
* **รหัสนักศึกษา**: 116730462005-3

---

คู่มือและคำอธิบายโดยละเอียดสามารถอ่านได้ที่:
👉 **[04-RAG-Project/README.md](04-RAG-Project/README.md)**

## 🐳 Quick Start ด้วย Docker (แนะนำ)

ต้องติดตั้งและเปิด Docker Desktop ก่อน จากนั้นรัน:

```powershell
cd 04-RAG-Project
docker build -t atcs-lab04-rag:latest .
docker run -d `
  --name atcs-lab04-rag `
  -p 5000:5000 `
  -v lab04-huggingface-cache:/root/.cache/huggingface `
  atcs-lab04-rag:latest
```

ติดตามการดาวน์โหลดโมเดลและการเริ่มระบบ:

```powershell
docker logs -f atcs-lab04-rag
```

เปิดใช้งาน Web UI ที่: **[http://localhost:5000](http://localhost:5000)**

การรันครั้งแรกอาจใช้เวลาสักครู่ เนื่องจากระบบต้องดาวน์โหลดโมเดล `BAAI/bge-m3` ส่วนขั้นตอนโดยละเอียด การแก้ปัญหา และวิธีรันโดยไม่ใช้ Docker อยู่ใน [คู่มือโปรเจกต์](04-RAG-Project/README.md)
