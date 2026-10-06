# LAB06 — COPIE: Curriculum Tool และ Skill Assessment Tool (P5)

**ผู้จัดทำ:** นายรัชชานนท์ ศรีไชย (Ratchanon Srichai) • `116730462005-3` • [@Nonyeol](https://github.com/Nonyeol)

งานนี้เป็นส่วนที่ผมรับผิดชอบในบทบาท **P5** ของโครงงาน [COPIE AI — Computer Engineering RMUTT Knowledge](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage) โดยพัฒนาเครื่องมือ 2 ส่วน ได้แก่ **Curriculum Tool** สำหรับข้อมูลหลักสูตร และ **Skill Assessment Tool** สำหรับแบบประเมินและคำนวณคะแนนทักษะ เพื่อให้ระบบ AI เรียกใช้ข้อมูลและสูตรที่ตรวจสอบได้

## สรุปหน้าที่และสิ่งที่ทำ

| ส่วนงาน | หน้าที่ที่ผมทำ | ไฟล์หลัก |
|---|---|---|
| ข้อมูลหลักสูตร | จัดทำข้อมูลหลักสูตรวิศวกรรมคอมพิวเตอร์ฉบับปรับปรุง พ.ศ. 2568 ครบปี 1–4 และ 8 ภาคการศึกษา รวม 51 รายการตามแผนการเรียนและ 141 หน่วยกิต พร้อมแหล่งอ้างอิงและเลขหน้า | [curriculum.json](data/curriculum/curriculum.json), [SOURCE.md](data/curriculum/SOURCE.md) |
| โหลดและตรวจข้อมูล | โหลด JSON แบบ cache ตรวจรูปแบบข้อมูลด้วย Pydantic และตรวจรหัสวิชาซ้ำ ช่วงปี/ภาค และยอดหน่วยกิต | [loader.py](backend/app/modules/tools/curriculum/loader.py), [validate.py](backend/app/modules/tools/curriculum/validate.py) |
| Curriculum Tool | พัฒนาฟังก์ชันดึงรายวิชาตามปี/ภาค ค้นรหัสหรือชื่อไทย/อังกฤษ รวมหน่วยกิต และสรุปภาพรวม 4 ปี | [service.py](backend/app/modules/tools/curriculum/service.py) |
| ปรับการค้นวิชา | ใช้ RapidFuzz WRatio พร้อมปรับข้อความก่อนค้น รองรับชื่อย่อ ชื่อใกล้เคียง และตัวพิมพ์ใหญ่/เล็ก เช่น `Data Structure` | [service.py](backend/app/modules/tools/curriculum/service.py), [ชุดทดสอบ](backend/app/modules/tools/tests/test_curriculum_service.py) |
| แบบประเมินทักษะ | จัดทำคำถามประเมินประสบการณ์ตนเอง 12 ข้อ ครอบคลุม 6 ด้าน ด้านละ 2 ข้อ พร้อมตัวเลือก 0–4 และน้ำหนักคะแนน | [skill_v1.json](data/assessment/skill_v1.json) |
| Skill Assessment Tool | โหลดและตรวจแบบประเมิน ส่งแบบฟอร์มโดยไม่เปิดเผยน้ำหนัก คำนวณคะแนน 0–100 ด้วยสูตรแน่นอน และเรียงทักษะเด่น | [loader.py](backend/app/modules/tools/skill/loader.py), [service.py](backend/app/modules/tools/skill/service.py) |
| ทดสอบ | เขียนชุดทดสอบข้อมูลหลักสูตร การค้นวิชา หน่วยกิต แบบประเมิน สูตรคะแนน คำตอบผิด/ซ้ำ และการเรียงคะแนนเสมอ | [tests/](backend/app/modules/tools/tests/) |
| เอกสารและส่งต่องาน | จัดทำสรุปหลักสูตรสำหรับทีม RAG (P4) และรายงานส่งมอบฟังก์ชัน/ข้อมูลให้ทีม Agent (P3) พร้อมหลักฐานตรวจข้อมูลและตัวอย่างคำนวณ | [study-plan-overview.md](data/knowledge/study-plan-overview.md), [รายงาน P5](docs/handoffs/P5-curriculum-skill.md) |

ไฟล์ `backend/app/schemas/contract.py` เป็น **contract กลางของทีม** ที่นำมาด้วยเพื่อให้ทดสอบเครื่องมือได้ ไม่ใช่งานที่อ้างว่าผมพัฒนาคนเดียว การเชื่อมต่อ Agent/API เป็นงานร่วมกับ P3 และการนำเอกสารเข้า RAG เป็นหน้าที่ร่วมกับ P4

## โครงสร้าง Directory และหน้าที่แต่ละส่วน

```text
LAB06/
├── README.md                              # สรุปหน้าที่ P5 และวิธีทดสอบ
├── requirements.txt                       # dependency สำหรับทดสอบเครื่องมือ
├── SOURCE_MANIFEST.json                    # commit ต้นทางและ SHA-256 ของไฟล์ที่นำมา
├── backend/app/
│   ├── schemas/contract.py                # contract กลางของทีม (dependency)
│   └── modules/tools/
│       ├── __init__.py                     # public API ของเครื่องมือทั้งสอง
│       ├── README.md                       # ขอบเขตโมดูล P5 จากต้นทาง
│       ├── curriculum/
│       │   ├── loader.py                   # โหลด/cache และ validate รายวิชา
│       │   ├── service.py                  # ค้นวิชา ดึงตาราง รวมหน่วยกิต ภาพรวม
│       │   └── validate.py                 # ตรวจข้อมูลและพิมพ์หน่วยกิตรายเทอม
│       ├── skill/
│       │   ├── loader.py                   # ตรวจ 12 ข้อ 6 ด้าน สเกลและน้ำหนัก
│       │   └── service.py                  # แบบฟอร์ม สูตรคะแนน และ top skills
│       └── tests/
│           ├── test_curriculum_data.py     # ข้อมูล 8 เทอม รหัสซ้ำ และยอดรวม
│           ├── test_curriculum_service.py  # query ค้นวิชา หน่วยกิต และภาพรวม
│           └── test_skill.py               # แบบฟอร์ม คะแนน 0/100 และข้อมูลผิด
├── data/
│   ├── curriculum/
│   │   ├── curriculum.json                # แผนการเรียนปี 1–4
│   │   ├── SOURCE.md                      # เอกสารอ้างอิงและเลขหน้า
│   │   └── README.md                      # คำอธิบายชุดข้อมูล
│   ├── assessment/
│   │   ├── skill_v1.json                  # คำถาม สเกล 0–4 และ weights
│   │   └── README.md                      # คำอธิบายแบบประเมิน
│   └── knowledge/study-plan-overview.md    # สรุปหลักสูตรส่งต่อทีม RAG
├── docs/handoffs/P5-curriculum-skill.md     # รายงานส่งมอบและหลักฐานจากต้นทาง
└── IMPLEMENTATION_PLANS/
    └── 05_CURRICULUM_SKILL_TOOLS.md        # แผนงาน P5 จากโครงงานต้นทาง
```

มีไฟล์ `__init__.py` ใน Python packages ด้วย โครงสร้าง `backend/` และ `data/` คงตำแหน่งสัมพัทธ์จากต้นทาง เพื่อให้ loader อ่านข้อมูลได้ตามเดิม เอกสารต้นทางที่คัดลอกมาบางลิงก์อ้างถึงส่วนอื่นของ COPIE; ดูเอกสารโครงงานเต็มผ่านลิงก์ต้นทางด้านล่าง

## ฟังก์ชันที่พัฒนา

| ฟังก์ชัน | การทำงาน |
|---|---|
| `get_courses(year, semester)` | คืนรายวิชาและหน่วยกิตของปี/ภาคที่เลือก; ไม่มีข้อมูลคืน `None` |
| `get_course_detail(query)` | ค้นรหัสก่อน แล้วค้นชื่อไทย/อังกฤษด้วย fuzzy matching ที่คะแนนอย่างน้อย 80 |
| `get_total_credits(year=None, semester=None)` | รวมหน่วยกิตตาม filter หรือคืนยอดหลักสูตร 141 หน่วยกิต |
| `get_curriculum_overview()` | สรุปการ์ดปี 1–4 พร้อมหน่วยกิต วิชาเด่น และหมวดวิชา |
| `get_assessment()` | คืนแบบประเมิน 12 ข้อและตัวเลือก โดยไม่ส่ง weights |
| `calculate_skill(answers)` | คำนวณคะแนน 6 ด้าน ตรวจ question ID ที่ไม่รู้จัก/ซ้ำ และคิดข้อที่ไม่ตอบเป็น 0 |
| `top_skills(scores, n=2)` | เรียงทักษะเด่นตามคะแนน; เมื่อคะแนนเสมอใช้ลำดับใน contract |

ทักษะ 6 ด้านคือ `frontend`, `backend`, `network`, `embedded`, `ai_data` และ `cybersecurity` แบบประเมินนี้สะท้อนประสบการณ์ที่ผู้ใช้ประเมินตนเอง

สูตรต่อด้าน: `round(sum(answer_value × weight) / sum(4 × weight) × 100)` ตัวอย่าง `q1=1`, `q2=3` ได้ frontend = `round((1+3)/8×100)` = **50** คะแนน คำตอบเดิมให้ผลเดิมโดยไม่ใช้ LLM ให้คะแนน

## วิธีติดตั้งและทดสอบเฉพาะงาน P5

ใช้ Python 3.11 ขึ้นไป จาก root ของ ATCS-CPE:

```powershell
cd LAB06
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd backend
..\.venv\Scripts\python.exe -m pytest -q app/modules/tools/tests
..\.venv\Scripts\python.exe -m app.modules.tools.curriculum.validate
```

ชุดไฟล์นี้ใช้ทดสอบเครื่องมือ P5 โดยตรง การเปิดเว็บหรือเรียก `/api/chat` ต้องใช้ระบบ COPIE เต็มพร้อมโมดูลของทีม

## หลักฐานและสถานะงาน

- ข้อมูลรายภาค: ปี 1 = 19/21, ปี 2 = 20/21, ปี 3 = 20/19, ปี 4 = 6/15 หน่วยกิต รวม **141**
- รายงานส่งมอบต้นทางบันทึกการสุ่มตรวจรายวิชา **20/20 ตรง** และชุดทดสอบ **12 passed** ณ วันที่ตรวจ 25 กันยายน 2569; เป็นหลักฐานเดิมของโครงงาน
- รายงานต้นทางยังระบุว่ารอการยืนยัน integration ผ่าน API ด้วยข้อมูลจริงครบกรณี การ review ถ้อยคำแบบประเมิน และการ review/ingest เอกสารโดย P4 จึงแยกสถานะเหล่านี้จากงานเครื่องมือที่ส่งมอบแล้ว
- ผลตรวจชุดไฟล์ที่คัดลอกสำหรับ Lab นี้จะบันทึกใน [VERIFICATION.md](VERIFICATION.md)

## ที่มาของงาน

คัดลอกเฉพาะงาน P5 และ contract ที่จำเป็นจาก COPIE commit [`51a2be3`](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/tree/51a2be32663a54b2ae0ed256efa964609a644899) เมื่อ 7 ตุลาคม 2569 มีรายละเอียด checksum ใน [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json)

ประวัติ commit ในขอบเขตนี้ระบุผู้เขียน `Racharnon Srichai` เช่น `412195f` (curriculum queries), `06d4d92` (skill scoring), `2fcfc6c` (audit และเอกสาร), `244b8a4` (RapidFuzz) และ `2c7d8ee` (หลักฐาน review) ดู [แผนงาน P5 ต้นทาง](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/blob/51a2be32663a54b2ae0ed256efa964609a644899/IMPLEMENTATION_PLANS/05_CURRICULUM_SKILL_TOOLS.md) และ [รายงานส่งมอบต้นทาง](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/blob/51a2be32663a54b2ae0ed256efa964609a644899/docs/handoffs/P5-curriculum-skill.md)
