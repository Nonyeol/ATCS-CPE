# -*- coding: utf-8 -*-
"""
problem02_transformer.py
------------------------
ปัญหาที่ 2: Vocabulary Mismatch (คำศัพท์ไม่ตรงกัน) และ Token Position (Lost in the Middle)

[ข้อผิดพลาดที่พบในโค้ด LAB04]
1. Vocabulary Mismatch: ใน config.py ตั้งค่า `USE_QUERY_TRANSFORM = False` เป็นค่าเริ่มต้น
   เมื่อผู้ใช้ใช้คำพูดภาษาปากหรือคำพ้องความหมาย (เช่น "เขียนโปรแกรม", "ตัวไหนไวสุด", "ประหยัดงบ")
   ระบบ BM25 ใน hybrid_retriever.py จะตัดคำแล้วไม่ตรงกับศัพท์ใน ai_models_qa.txt
   (ซึ่งใช้คำว่า "เขียนโค้ด", "เร็วและประหยัดที่สุด", "งบประมาณจำกัด") ทำให้หาเอกสารไม่เจอ
2. Lost in the Middle: ใน prompt_templates.py ฟังก์ชัน format_context() เรียง Chunk ต่อกันเป็น [1], [2], [3]
   หากข้อมูลสำคัญหลุดไปอยู่ตรงกลางของ Prompt โมเดล Transformer มักจะละเลยเนื้อหาตรงกลาง (U-shaped Attention curve)

[แนวทางการแก้ไขสำหรับ LAB04]
1. เปิด `USE_QUERY_TRANSFORM = True` ใน config.py เพื่อทำ Query Expansion / Rewrite
2. ปรับการจัดเรียง Context ใหม่ (Re-ordering) วาง Chunk สำคัญที่สุดไว้ที่ขอบบนหรือล่างติดกับคำถาม
"""

import sys
from data_loader import load_qa

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")


def tokenize_simple(text):
    """ตัดคำภาษาไทย/อังกฤษอย่างง่าย"""
    import re
    tokens = re.findall(r"[a-zA-Z0-9]+|[ก-๙]+", text.lower())
    return [t for t in tokens if len(t) > 1]


def bow(text):
    tokens = tokenize_simple(text)
    counts = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    return counts


def run():
    print("=" * 70)
    print(" 🔤 Problem 02: Vocabulary Mismatch & Token Position (Transformer)")
    print("=" * 70)

    data = load_qa()
    # หา Q&A ที่เกี่ยวกับโมเดลความเร็ว/ประหยัด (Haiku)
    target_doc = next(d for d in data if "Haiku" in d["answer"])

    # กรณีที่ 1: Vocabulary Mismatch
    user_query_slang = "แนะนำ ai ตัวไหนไวและถูกสุด สำหรับเขียนโปรแกรม"
    doc_text = f"{target_doc['question']} {target_doc['answer']}"

    query_bow = bow(user_query_slang)
    doc_bow = bow(doc_text)

    overlap = set(query_bow.keys()) & set(doc_bow.keys())

    print("\n[ส่วนที่ 1: ปัญหา Vocabulary Mismatch (คำศัพท์ไม่ตรงกัน)]")
    print(" คำถามของผู้ใช้ (ภาษาพูด) :", user_query_slang)
    print(" คำสำคัญในฐานข้อมูล (เอกสาร) : 'Haiku (เร็วและประหยัดที่สุด)', 'เขียนโค้ด'")
    print(" Tokens คำถามผู้ใช้        :", list(query_bow.keys()))
    print(" คำที่ตรงกันเป๊ะ (Exact Token Overlap):", list(overlap) or "ไม่พบเลย (0 คำ)")
    print(" ⚠️ ผลกระทบใน LAB04: BM25 ให้คะแนน = 0 หากปิด USE_QUERY_TRANSFORM จะค้นหาพลาดทันที")

    # วิธีแก้ด้วย Query Expansion / Rewrite
    expanded_query = "AI สำหรับงานเขียนโค้ด โมเดลที่เร็วและประหยัดที่สุด Haiku Sonnet"
    exp_overlap = set(tokenize_simple(expanded_query)) & set(doc_bow.keys())
    print("\n ✅ วิธีแก้ (เปิด USE_QUERY_TRANSFORM):")
    print(" คำถามหลัง Rewrite/Expand :", expanded_query)
    print(" คำที่ตรงกันหลังปรับปรุง   :", list(exp_overlap))

    # กรณีที่ 2: Token Position (Lost in the Middle)
    print("\n" + "-" * 70)
    print("[ส่วนที่ 2: ปัญหา Token Position / Lost in the Middle]")
    print("ใน prompt_templates.py ของ LAB04 เรียง Context ดังนี้:")
    print("  [1] Chunk สำคัญปานกลาง (คะแนน 0.75)   <- ต้น Prompt (โมเดลจำได้ดี)")
    print("  [2] Chunk ที่มีคำตอบสำคัญที่สุด (คะแนน 0.95) <- กลาง Prompt (⚠️ โมเดลมองข้าม!)")
    print("  [3] Chunk ข้อมูลเสริม (คะแนน 0.60)      <- ท้าย Prompt (ใกล้คำถาม)")

    print("\n ⚠️ ปรากฏการณ์ Lost in the Middle:")
    print(" สถาปัตยกรรม Attention ของ Transformer มี Attention Weight สูงสุดที่ 'หัว' และ 'ท้าย'")
    print(" ทำให้ Chunk [2] ที่อยู่ตรงกลางถูกละเลย หรือได้รับความสนใจต่ำที่สุด")

    print("\n ✅ วิธีแก้ใน LAB04 (Context Re-ordering):")
    print(" จัดเรียงลำดับใหม่ให้ Chunk สำคัญที่สุดอยู่ที่ตำแหน่ง [1] (บนสุด) หรือ [3] (ติดกับคำถาม)")
    print("  -> ตำแหน่งใหม่: [Chunk 0.75] -> [Chunk 0.60] -> [⭐ Chunk 0.95 (สำคัญที่สุดติดคำถาม)]")

    print("\n" + "-" * 70)
    print("💡 สรุปสาเหตุและการแก้ไขสำหรับโค้ด LAB04:")
    print("1. เปิด `USE_QUERY_TRANSFORM = True` ใน config.py เพื่อแก้คำศัพท์ไม่ตรงกัน")
    print("2. แก้ไข format_context() ใน prompt_templates.py ให้จัดเรียงเอกสารสำคัญไว้ชิดขอบคำถาม")
    print("-" * 70)


if __name__ == "__main__":
    run()
