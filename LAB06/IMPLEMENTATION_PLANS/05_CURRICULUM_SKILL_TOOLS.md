# P5 — Curriculum Tool + Skill Assessment Tool

## Mission

สร้าง Tool ที่ใช้ **ข้อมูลแบบมีโครงสร้าง** 2 ตัว:
1. **Curriculum Tool** — ข้อมูลรายวิชาทุกปี/ทุกเทอมของหลักสูตร วศ.บ. วิศวกรรมคอมพิวเตอร์ RMUTT ที่ **ตรงเล่มหลักสูตร 100%**
2. **Skill Assessment Tool** — แบบประเมิน 12 ข้อ + สูตรคำนวณคะแนน 6 ด้านที่ deterministic และอธิบายได้

**ความสำคัญ:** ข้อมูลประเภทนี้ห้ามให้ LLM เดา ถ้าตาราง/หน่วยกิตผิด อาจารย์จะเห็นทันที Demo 3 (ตาราง) และ Demo 4 (Radar) ขึ้นกับงานนี้โดยตรง

## Ownership

แก้ได้โดยตรง
- `data/curriculum/**`, `data/assessment/**`
- `backend/app/modules/tools/**` (curriculum, skill, tests)

ต้องขอ review เพิ่ม
- `requirements.txt` (เพิ่ม `rapidfuzz`) — P3

Dependency

| รับจาก | อะไร |
|---|---|
| เล่มหลักสูตรจริง | รหัส ชื่อ หน่วยกิต แผนการเรียนรายเทอม |
| P3 | การเรียก function ผ่าน Agent (ทดสอบร่วม Day 4) |

ส่งให้: **P3** functions ตาม `00_API_AND_DATA_CONTRACTS.md` §4 (stub D1 17:00) · **P4** ข้อความสรุปหลักสูตร (Day 4) · **P6** ตัวอย่างข้อมูลจริงสำหรับ mock

## Stack

- Python + Pydantic (`Course`, `CourseTableData`, `AssessmentFormData`, `SkillScores` จาก contract)
- `rapidfuzz` สำหรับค้นชื่อวิชา
- โหลด JSON ครั้งเดียวด้วย `functools.lru_cache`

## Target folder structure

```text
data/curriculum/
├─ curriculum.json
└─ SOURCE.md                 # เล่มหลักสูตรฉบับไหน ปีไหน URL/หน้า
data/assessment/
└─ skill_v1.json

backend/app/modules/tools/   # 👤 P5
├─ __init__.py               # public: re-export ทุก function ของทั้งสอง tool
├─ curriculum/
│  ├─ loader.py              # load_curriculum() -> list[Course] (cached, validate)
│  ├─ service.py             # get_courses, get_course_detail, get_total_credits, get_curriculum_overview
│  └─ validate.py            # python -m app.modules.tools.curriculum.validate
├─ skill/
│  ├─ loader.py              # load_assessment() (cached)
│  └─ service.py             # get_assessment, calculate_skill, top_skills
└─ tests/                    # test_curriculum.py, test_skill.py
```

## Design details

### Curriculum functions

| Function | พฤติกรรม |
|---|---|
| `get_courses(year, semester)` | กรองตาม year/semester, เรียงตามรหัส, `total_credits = Σ credits`; ไม่มีข้อมูล → `None` |
| `get_course_detail(query)` | 1) ตรงรหัส (ตัด `-`/ช่องว่าง) 2) fuzzy `WRatio` กับ `name_th`/`name_en` ≥ 80 → คืนตัวที่ดีที่สุด, ไม่งั้น `None` |
| `get_total_credits(year=None, semester=None)` | รวมหน่วยกิตตาม filter |
| `get_curriculum_overview()` | `CardsData` 4 การ์ด (ปี 1–4): หน่วยกิตรวม + วิชาเด่น 3–4 วิชา + tags หมวดวิชา |

- วิชาเลือก / วิชาเลือกเสรีที่เล่มระบุเป็น "เลือกเรียน X หน่วยกิต" ให้ใส่เป็น course พิเศษ เช่น `code: "ELECTIVE-1"`, `name_th: "วิชาเลือกเฉพาะสาขา 1"` เพื่อให้หน่วยกิตรวมตรงเล่ม

### `validate.py` (รันก่อนทุก PR ข้อมูล)

- ทุก course ผ่าน Pydantic `Course`
- รหัสไม่ซ้ำ (ยกเว้น ELECTIVE)
- `year` 1–4, `semester` 1–2 (ถ้ามีภาคฤดูร้อน ใช้ 3 และแจ้ง P3/P6)
- หน่วยกิตรวมทั้งหลักสูตรตรงกับ `total_credits` ในไฟล์ (ที่คัดจากเล่ม)
- พิมพ์ตารางสรุปหน่วยกิตรายเทอมให้เทียบกับเล่มด้วยตา

### Skill Assessment

- 6 skill × 2 ข้อ = 12 ข้อ · คำถามเป็นประสบการณ์ที่วัดได้ ("เคยต่อ Arduino/ESP32 อ่านค่าเซนเซอร์")
- ตัวเลือก 5 ระดับ value 0–4 (label ใน `scale`)
- `weights` อนุญาตข้ามหมวดเล็กน้อย (≤ 0.3) เช่น REST API ให้ backend 1.0 + frontend 0.2
- **สูตร:** `score[s] = round( Σ(value_q × w_q,s) / Σ(4 × w_q,s) × 100 )` เฉพาะข้อที่มี weight ของ s
- ข้อที่ไม่ได้ตอบ → ถือว่า 0 (frontend บังคับตอบครบอยู่แล้ว)
- `top_skills(scores, n=2)` เรียงคะแนนมาก→น้อย, เสมอกันเรียงตามลำดับ `SKILL_KEYS`
- `get_assessment()` **ไม่ส่ง weights** ออกไป (คืนเฉพาะ `id`, `text`, `options`)

ตัวอย่างข้อคำถาม (ปรับได้)

| id | skill | ข้อความ |
|---|---|---|
| q1 | frontend | สร้างหน้าเว็บด้วย HTML/CSS/JavaScript |
| q2 | frontend | ใช้ React/Vue/Next.js ทำเว็บที่มีหลายหน้า |
| q3 | backend | เขียน REST API และเชื่อมฐานข้อมูล |
| q4 | backend | ออกแบบตารางฐานข้อมูลและเขียน SQL |
| q5 | network | ตั้งค่า IP / subnet / router / switch |
| q6 | network | ใช้ Wireshark หรือวิเคราะห์ปัญหาเครือข่าย |
| q7 | embedded | เขียนโปรแกรม Arduino/ESP32 อ่านเซนเซอร์ |
| q8 | embedded | ออกแบบวงจรดิจิทัลหรือใช้ FPGA |
| q9 | ai_data | ใช้ Python (pandas/numpy) วิเคราะห์ข้อมูล |
| q10 | ai_data | เทรนโมเดล Machine Learning |
| q11 | cybersecurity | เข้าใจช่องโหว่เว็บ (SQL injection, XSS) |
| q12 | cybersecurity | เคยเล่น CTF หรือใช้เครื่องมือ security |

## Implementation steps

### Phase 0 — หาข้อมูล (Day 1 AM)
1. หาเล่มหลักสูตรฉบับล่าสุด + แผนการเรียน, บันทึกใน `SOURCE.md` (ฉบับปี, URL, เลขหน้า)

### Phase 1 — ปี 1–2 + stubs (Day 1 PM)
1. กรอก `curriculum.json` ปี 1–2
2. stub ทุก function คืนข้อมูลตาม type

Exit: **M1** — P3 เรียกได้ทุก function

### Phase 2 — ข้อมูลครบ + Curriculum service (Day 2)
1. AM: ปี 3–4 + description, `validate.py`
2. PM: `service.py` ครบ 4 functions + `test_curriculum.py`

Exit: **M2** — `validate.py` ผ่าน, หน่วยกิตตรงเล่ม

### Phase 3 — Skill (Day 3)
1. AM: `skill_v1.json` 12 ข้อ + weights + review กับทีม 10 นาทีใน stand-up
2. PM: `calculate_skill`, `top_skills`, `get_assessment` + `test_skill.py`

Exit: **M3**

### Phase 4 — Integration (Day 4)
1. ทดสอบผ่าน `/api/chat` กับ P3: "ปี 1 เทอม 2", "วิชา Data Structure เรียนอะไร", "หลักสูตรมีกี่หน่วยกิต", "ประเมิน skill"
2. เขียน `data/knowledge/study-plan-overview.md` ส่ง P4 (PR แยก ให้ P4 review)

Exit: **M4**

### Phase 5 — ตรวจข้อมูล (Day 5)
- สุ่ม 20 วิชาเทียบเล่ม, แก้ข้อมูล, ตรวจคำถาม skill ที่เพื่อนบอกว่ากำกวม

## Required tests

| ประเภท | Cases |
|---|---|
| Curriculum | ทุก (ปี,เทอม) มีข้อมูล, total_credits ถูก, ปี 5 → None, ค้นรหัสแบบมี/ไม่มีขีด, ค้นชื่อสะกดใกล้เคียง |
| Skill | ตอบ 0 หมด → ทุกด้าน 0, ตอบ 4 หมด → ทุกด้าน 100, คำตอบผสม → ค่าที่คำนวณมือไว้, deterministic |
| Contract | ผลลัพธ์ผ่าน Pydantic model จาก `contract.py` |
| Data | `python -m app.modules.tools.curriculum.validate` ผ่าน |

## Acceptance checklist

- [ ] `curriculum.json` ครบ 4 ปี ตรงเล่มหลักสูตร (มี `SOURCE.md`)
- [ ] "ปี X เทอม Y" คืนตาราง + หน่วยกิตรวมถูกต้อง
- [ ] ค้นรายละเอียดวิชาด้วยรหัส/ชื่อได้
- [ ] แบบประเมิน 12 ข้อ + สูตรที่อธิบายได้ + ไม่มีการสุ่ม
- [ ] ผลลัพธ์ทุก function ตรง Contract
- [ ] ส่งข้อความสรุปหลักสูตรให้ RAG แล้ว

## Branch / PR breakdown

1. `tools/curriculum-data-v1` — ปี 1–2 + SOURCE.md + stubs
2. `tools/curriculum-data-v2` — ปี 3–4 + validate
3. `tools/curriculum-service` — functions + tests
4. `tools/skill-assessment` — skill_v1.json
5. `tools/skill-scoring` — scoring + tests
6. `tools/integration-fix`, `tools/data-fix`

## Completion report requirements

สร้าง `docs/handoffs/P5-curriculum-skill.md` ระบุเพิ่ม: เล่มหลักสูตรที่ใช้, ตารางหน่วยกิตรายเทอมเทียบเล่ม, คำถาม 12 ข้อ + weights, ตัวอย่างคำนวณคะแนน 1 ชุดแบบแสดงวิธีทำ, ผลสุ่มตรวจ 20 วิชา
