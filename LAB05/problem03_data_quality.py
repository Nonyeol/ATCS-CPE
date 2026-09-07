# -*- coding: utf-8 -*-
"""
problem03_data_quality.py
-------------------------
ปัญหาที่ 3: คุณภาพข้อมูลดิบ ความซ้ำซ้อน และสัญญาณรบกวน (Data Quality & Normalization)

[ข้อผิดพลาดที่พบในโค้ด LAB04]
1. ใน document_loader.py ของ LAB04 ทำเพียงแค่ `line = raw.strip()` เท่านั้น
   ไม่มีกระบวนการ Text Normalization เพื่อจัดการสระลอย, วรรณยุกต์ซ้ำ, อักขระพิเศษ หรือ Zero-width space
   ทำให้เวกเตอร์ Embedding จากโมเดล BAAI/bge-m3 คลาดเคลื่อน
2. ขาดการตัดข้อมูลซ้ำซ้อน (Deduplication): หากคลังข้อมูลมีข้อความซ้ำหรือใกล้เคียงกันมาก
   จะถูกดึงเข้ามาติดใน Top-K พร้อมกัน ทำให้แย่งโควตา Context Window ของ LLM ไปโดยเปล่าประโยชน์

[แนวทางการแก้ไขสำหรับ LAB04]
1. ใช้ฟังก์ชัน Normalization (เช่น pythainlp.util.normalize หรือ regex cleaning) ใน document_loader.py
2. ทำ Deduplication ด้วย Text Hash ก่อนนำไปสร้าง Index ใน build_index.py
"""

import re
import sys
from data_loader import load_qa

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")


def simulate_noisy_samples(data, n=2):
    """จำลองข้อความที่มีสัญญาณรบกวน (Noise) และข้อความซ้ำ (Duplicate)"""
    samples = []
    for d in data[:n]:
        q = d["question"]
        samples.append(q)                                 # ข้อความต้นฉบับ
        samples.append(q)                                 # ข้อความซ้ำกันเป๊ะ (Duplicate)
        samples.append("   " + q + "   \t")               # ปัญหาวรรคตอนส่วนเกิน
        samples.append(q.replace(" ", "___") + "!!?*")    # อักขระพิเศษปนเปื้อน
    return samples


def clean_and_normalize(text):
    """ฟังก์ชันทำความสะอาดและจัดมาตรฐานข้อความภาษาไทย"""
    try:
        from pythainlp.util import normalize as thai_normalize
        text = thai_normalize(text)
    except ImportError:
        pass

    # ลบอักขระพิเศษขยะและวรรคตอนซ้ำซ้อน
    text = re.sub(r"[_!*?@#]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def run():
    print("=" * 70)
    print(" 🧹 Problem 03: Data Quality, Noise & Redundancy")
    print("=" * 70)

    data = load_qa()
    raw_samples = simulate_noisy_samples(data, n=2)

    print("\n[1. ข้อมูลดิบก่อนทำความสะอาด (มีทั้ง Noise และ Duplicate)]")
    for i, s in enumerate(raw_samples, start=1):
        print(f"  {i}. {repr(s)}")

    # ขั้นตอนทำความสะอาด + ตัดข้อมูลซ้ำ
    cleaned = [clean_and_normalize(s) for s in raw_samples]
    unique_cleaned = list(dict.fromkeys(cleaned))

    print("\n[2. ข้อมูลหลังทำ Normalization + Deduplication]")
    for i, s in enumerate(unique_cleaned, start=1):
        print(f"  {i}. {repr(s)}")

    print(f"\n📊 สถิติ: จำนวนข้อมูลลดลงจาก {len(raw_samples)} รายการ เหลือเพียง {len(unique_cleaned)} รายการที่ไม่ซ้ำกัน")

    # ผลกระทบต่อ Top-K ใน LAB04
    print("\n" + "-" * 70)
    print("[3. ผลกระทบต่อ Top-K ใน LAB04 เมื่อมีข้อมูลซ้ำซ้อน]")
    print("  กรณี LAB04 เดิม (ไม่มี Deduplication):")
    print("    - Top-1: 'ตอนนี้มีค่ายโมเดล AI หลักอะไรบ้าง... (ฉบับที่ 1)'")
    print("    - Top-2: 'ตอนนี้มีค่ายโมเดล AI หลักอะไรบ้าง... (ฉบับที่ 2 - ซ้ำ!)'")
    print("    - Top-3: 'ตอนนี้มีค่ายโมเดล AI หลักอะไรบ้าง... (ฉบับที่ 3 - ซ้ำ!)'")
    print("    ⚠️ ผลลัพธ์: LLM ได้รับข้อมูลเดิม 3 รอบ เสียโควตา Context Window ไปฟรีๆ 66%")

    print("\n  กรณีหลังแก้ไขใน LAB04 (มี Deduplication):")
    print("    - Top-1: 'ตอนนี้มีค่ายโมเดล AI หลักอะไรบ้าง... (ค่ายหลัก)'")
    print("    - Top-2: 'Anthropic มีโมเดลระดับไหนบ้าง... (ระดับโมเดล)'")
    print("    - Top-3: 'จุดเด่นของแต่ละค่ายต่างกันอย่างไร... (การเปรียบเทียบ)'")
    print("    ✅ ผลลัพธ์: LLM ได้รับมุมมองข้อมูลที่หลากหลายและครบถ้วน 100%")

    print("\n" + "-" * 70)
    print("💡 สรุปสาเหตุและการแก้ไขสำหรับโค้ด LAB04:")
    print("1. เพิ่ม clean_and_normalize() ใน document_loader.py ก่อนนำไปตัดแบ่ง Chunk")
    print("2. เพิ่มระบบตัดข้อความซ้ำ (Deduplication) ใน build_index.py ก่อนสร้าง Index")
    print("-" * 70)


if __name__ == "__main__":
    run()
