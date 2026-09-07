# -*- coding: utf-8 -*-
"""
problem07_generation.py
-----------------------
ปัญหาที่ 7: ค้นหาเอกสารเจอถูกต้อง แต่ LLM สร้างคำตอบผิดพลาด (Generation Failure / Faithfulness)

[ข้อผิดพลาดที่พบในโค้ด LAB04]
1. ใน config.py ของ LAB04 ตั้งค่า `USE_LLM = False` เป็นค่าเริ่มต้น ซึ่งจะผ่านคลาส NoLLM()
   โดย NoLLM() จะทำเพียงแค่หยิบข้อความก้อนแรกออกมาตัดแสดง โดยไม่สังเคราะห์หรือตอบตรงตามคำถาม
2. เมื่อเปิด `USE_LLM = True`:
   - แม้ระบบจะค้นหา Context ที่ถูกต้องมาได้ แต่ LLM อาจบิดเบือนตัวเลข สเปก หรือเงื่อนไขสำคัญ (Faithfulness Failure)
   - เช่น ตัวเลข Context window "1 ล้านโทเคน" ถูกบิดเบือนเป็น "1 แสนโทเคน"
   - หรือค่าบริการ "20 ดอลลาร์สหรัฐ" ถูกบิดเบือนเป็นตัวเลขอื่น
3. ใน generator.py ของ LAB04 หาก LLM มีปัญหา จะ Fallback อัตโนมัติเป็น `answer = chunks[0]["answer"]`
   ซึ่งไม่ได้ตอบเจาะจงตามคำถามของผู้ใช้

[แนวทางการแก้ไขสำหรับ LAB04]
1. ปรับ `LLM_TEMPERATURE = 0.0` ใน config.py สำหรับงานถาม-ตอบเชิงข้อเท็จจริง
2. ปรับ System Prompt ให้เน้นย้ำความเที่ยงตรง (Strict Grounding) และประเมินค่า Faithfulness ก่อนส่งมอบคำตอบ
"""

import sys
from data_loader import load_qa

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")


def find_target_doc(data):
    """หาเอกสารเกี่ยวกับ context window และราคา"""
    return next(d for d in data if "1 ล้านโทเคน" in d["answer"])


def lab04_bad_generation(context):
    """
    จำลองการสร้างคำตอบที่ผิดพลาด (บิดเบือนตัวเลขและข้อเท็จจริงสำคัญ):
    - เปลี่ยน 1 ล้านโทเคน เป็น 1 แสนโทเคน
    - เปลี่ยนเงื่อนไขโหมดทดลองเป็นเปิดใช้งานทั่วไป
    """
    bad_text = (
        context.replace("1 ล้านโทเคน", "100,000 โทเคน (บิดเบือนตัวเลข)")
        .replace("ในโหมดทดลอง", "สำหรับผู้ใช้งานทุกคนทั่วไป (บิดเบือนเงื่อนไข)")
    )
    return f"[Bad Generation / Low Faithfulness]: {bad_text}"


def grounded_generation(context):
    """การสร้างคำตอบที่เที่ยงตรงและยึดโยงกับบริบทจริง 100% (High Faithfulness)"""
    return f"[Grounded Generation]: ตามข้อมูลอ้างอิง {context} [1]"


def run():
    print("=" * 70)
    print(" ⚠️ Problem 07: Generation Failure despite Correct Retrieval")
    print("=" * 70)

    data = load_qa()
    target_doc = find_target_doc(data)

    print("คำถามของผู้ใช้ :", target_doc["question"])
    print("\n[Retrieved Context ที่ค้นหามาได้ถูกต้อง (Ground Truth)]:")
    print(f"  \"{target_doc['answer']}\"")

    # 1. แสดงผลการสร้างคำตอบที่บิดเบือน (Bad Generation)
    print("\n❌ กรณีสร้างคำตอบผิดพลาด (LLM เพี้ยน/บิดเบือนตัวเลขสเปก):")
    bad_result = lab04_bad_generation(target_doc["answer"])
    print(f"  {bad_result}")
    print("  ⚠️ อันตราย: ผู้ใช้ได้รับข้อมูลตัวเลขสเปกที่ผิดพลาด ทั้งที่เอกสารที่ค้นหาได้ถูกต้องแล้ว!")

    # 2. แสดงผลการสร้างคำตอบที่ถูกต้องตามหลัก Grounding
    print("\n✅ กรณีสร้างคำตอบที่ถูกต้อง (Strictly Grounded & Temperature=0.0):")
    good_result = grounded_generation(target_doc["answer"])
    print(f"  {good_result}")

    print("\n" + "-" * 70)
    print("💡 สรุปสาเหตุและการแก้ไขสำหรับโค้ด LAB04:")
    print("1. สาเหตุ: อุณหภูมิ LLM_TEMPERATURE สูงเกินไป หรือ System Prompt หละหลวมจนโมเดลแต่งเติมข้อมูลเอง")
    print("2. วิธีแก้: ตั้งค่า LLM_TEMPERATURE = 0.0 ใน config.py และใส่กฎเกณฑ์ห้ามดัดแปลงตัวเลขใน prompt_templates.py")
    print("-" * 70)


if __name__ == "__main__":
    run()
