# tools — Curriculum Tool + Skill Assessment Tool

| | |
|---|---|
| เจ้าของ | **P5** |
| แผนงาน | [`05_CURRICULUM_SKILL_TOOLS.md`](../../../../IMPLEMENTATION_PLANS/05_CURRICULUM_SKILL_TOOLS.md) |
| Branch prefix | ดู `IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md` §2 |

## หน้าที่

ข้อมูลหลักสูตรแบบมีโครงสร้าง (`data/curriculum/`) และแบบประเมิน skill + สูตรคะแนน (`data/assessment/`) — ข้อมูลพวกนี้ห้ามให้ LLM เดา

## โครงไฟล์ที่จะสร้าง

```text
tools/
├─ __init__.py       # re-export ทั้งสอง tool
├─ curriculum/       # loader.py, service.py, validate.py (python -m app.modules.tools.curriculum.validate)
├─ skill/            # loader.py, service.py
└─ tests/
```

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

`get_courses`, `get_course_detail`, `get_total_credits`, `get_curriculum_overview`, `get_assessment`, `calculate_skill`, `top_skills`

## ใช้ของ module อื่นได้จาก

`app.core`, `app.schemas.contract`
