# -*- coding: utf-8 -*-
"""
main.py
-------
สคริปต์เมนูหลักสำหรับการรันและจำลอง 9 ปัญหาสำคัญของระบบ RAG (เปรียบเทียบข้อผิดพลาดของ LAB04 และแนวทางแก้ไข)
ใช้ชุดข้อมูลจริง ai_models_qa.txt (คลังความรู้โมเดล AI)

การใช้งาน:
    python main.py          # เปิดเมนู Interactive ให้เลือกหมายเลขปัญหา [0-9]
    python main.py 4        # รันเจาะจงปัญหาที่ 4 ทันที
    python main.py 0        # รันจำลองครบทั้ง 9 ปัญหาต่อเนื่อง
"""

import sys

# รองรับภาษาไทยบน Windows Terminal
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")

from problem01_hallucination import run as problem01
from problem02_transformer import run as problem02
from problem03_data_quality import run as problem03
from problem04_chunking import run as problem04
from problem05_metadata import run as problem05
from problem06_reranking import run as problem06
from problem07_generation import run as problem07
from problem08_config import run as problem08
from problem09_evaluation import run as problem09

PROBLEMS = {
    1: ("Hallucination & Context Deficiency (ภาพหลอนและการขาด Context)", problem01),
    2: ("Vocabulary Mismatch & Token Position (ศัพท์ไม่ตรงกัน + Lost in Middle)", problem02),
    3: ("Data Quality, Noise & Redundancy (คุณภาพข้อมูลดิบ + ข้อความซ้ำ)", problem03),
    4: ("Chunking Strategy - Size & Overlap (การหั่นข้อความ + คำขาดครึ่ง)", problem04),
    5: ("Metadata Filtering (การคัดกรองข้อมูลด้วยหมวดหมู่)", problem05),
    6: ("Top-K Selection & Cross-Encoder Re-ranking (การจัดอันดับซ้ำ)", problem06),
    7: ("Generation Failure despite Correct Retrieval (ค้นหาถูกแต่สร้างคำตอบผิด)", problem07),
    8: ("RAG Configuration & Hyperparameters (การปรับแต่งคอนฟิกและ Index Drift)", problem08),
    9: ("RAG Evaluation Suite - Hit Rate & MRR (การประเมินและวัดผลระบบ RAG)", problem09),
}


def show_menu():
    print("*" * 75)
    print("   ⚡ LAB05: RAG System Failure Modes Analysis & Solutions (LAB04 vs Fixed)")
    print("   ชุดข้อมูลคลังความรู้จริง: ai_models_qa.txt (โมเดลภาษา AI)")
    print("*" * 75)
    print("  0. รันจำลองครบทุกปัญหา (Run All 1-9)")
    for no, (name, _) in PROBLEMS.items():
        print(f"  {no}. {name}")
    print("*" * 75)


def execute(number):
    if number == 0:
        for no, (name, func) in PROBLEMS.items():
            print("\n" + "=" * 75)
            print(f" [PROBLEM {no}]: {name}")
            print("=" * 75)
            func()
        return

    if number not in PROBLEMS:
        print(f"⚠️ กรุณาเลือกตัวเลขระหว่าง 0 ถึง {len(PROBLEMS)}")
        return

    name, func = PROBLEMS[number]
    print("\n" + "=" * 75)
    print(f" [PROBLEM {number}]: {name}")
    print("=" * 75)
    func()


def main_loop():
    while True:
        show_menu()
        choice = input(f"กรุณาเลือกหมายเลขปัญหาที่ต้องการทดสอบ [0-{len(PROBLEMS)}] หรือพิมพ์ Q เพื่อออก: ").strip()

        if choice.upper() == "Q":
            print("ปิดโปรแกรมเรียบร้อยแล้ว ขอบคุณครับ!")
            break

        try:
            number = int(choice)
        except ValueError:
            print(f"⚠️ กรุณาระบุตัวเลข 0 ถึง {len(PROBLEMS)} หรือ Q เท่านั้น\n")
            continue

        if number < 0 or (number not in PROBLEMS and number != 0):
            print(f"⚠️ ไม่มีหมายเลขปัญหาที่เลือก กรุณาระบุ 0 ถึง {len(PROBLEMS)}\n")
            continue

        execute(number)
        print("\n" + "#" * 75 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        if arg.upper() == "Q":
            sys.exit(0)
        try:
            execute(int(arg))
        except ValueError:
            print(f"⚠️ กรุณาระบุตัวเลข 0 ถึง {len(PROBLEMS)} หรือ Q เท่านั้น")
    else:
        main_loop()
