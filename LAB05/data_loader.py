# -*- coding: utf-8 -*-
"""
data_loader.py
--------------
โหลดและแปลงชุดข้อมูล ai_models_qa.txt เป็นรายการของ dict
สำหรับใช้ร่วมกันใน problem01 - problem09 เพื่อจำลองและวิเคราะห์ปัญหาในระบบ RAG (LAB04 -> LAB05)

รูปแบบข้อมูลใน ai_models_qa.txt:
    [หมวด: <category>]
    Q: <question>
    A: <answer>
"""

import os
import re
import sys

# รองรับภาษาไทยบน Windows Terminal
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_models_qa.txt")
_HEADER_RE = re.compile(r"\[หมวด:\s*(.+?)\]")


def load_qa(path=DATA_PATH):
    """
    คืนค่ารายการของ dict:
    [
        {
            "id": 0,
            "category": "ภาพรวมค่าย AI หลัก",
            "question": "ตอนนี้มีค่ายโมเดล AI หลักอะไรบ้าง...",
            "answer": "ในกลางปี 2569 มีหลายค่าย...",
            "text": "ตอนนี้มีค่าย... ในกลางปี 2569..."
        },
        ...
    ]
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"ไม่พบไฟล์ชุดข้อมูล: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    entries = []
    current_category = "ทั่วไป"
    question = None

    for line in raw.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        header_match = _HEADER_RE.match(line)
        if header_match:
            current_category = header_match.group(1).strip()
            continue

        if line.startswith("Q:"):
            question = line[2:].strip()
        elif line.startswith("A:") and question:
            answer = line[2:].strip()
            entries.append({
                "id": len(entries),
                "category": current_category,
                "question": question,
                "answer": answer,
                "text": f"{question} {answer}",
            })
            question = None

    return entries


def get_categories(entries=None):
    """ดึงรายชื่อหมวดหมู่ทั้งหมดในชุดข้อมูล"""
    entries = entries if entries is not None else load_qa()
    return sorted(list(set(e["category"] for e in entries)))


if __name__ == "__main__":
    data = load_qa()
    print("=" * 60)
    print(f" โหลดชุดข้อมูลสำเร็จ: {len(data)} รายการ Q&A")
    print(f" หมวดหมู่ทั้งหมด ({len(get_categories(data))} หมวด):")
    for cat in get_categories(data):
        print(f"   - {cat}")
    print("=" * 60)
    print("ตัวอย่างข้อมูลรายการแรก:")
    print(" หมวด    :", data[0]["category"])
    print(" คำถาม   :", data[0]["question"])
    print(" คำตอบ   :", data[0]["answer"][:120] + "...")
