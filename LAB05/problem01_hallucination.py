# -*- coding: utf-8 -*-
"""
problem01_hallucination.py
--------------------------
ปัญหาที่ 1: การเกิดภาพหลอน (Hallucination) และการขาด Context ที่สนับสนุน

[ข้อผิดพลาดที่พบในโค้ด LAB04]
1. ใน generator.py ฟังก์ชัน generate() มีการตรวจสอบเฉพาะ `if not chunks:` เท่านั้น
   หากคำถามอยู่นอกขอบเขต (Out-of-domain) แต่มีคีย์เวิร์ดบังเอิญตรงกัน 1 คำ (เช่น คำว่า 'ราคา')
   Retriever ดึง Chunk ที่มีคะแนนต่ำมากแต่ไม่เกี่ยวกับเรื่องที่ถามติดมา
   ระบบ LAB04 เดิมจะส่ง Chunks นั้นเข้า Prompt ส่งผลให้ LLM พยายามผสมข้อมูลและแถตอบ (Hallucination)
2. ในกรณีฉุกเฉิน (LLM API Error หรือ USE_LLM=False) โค้ด LAB04 เขียน Fallback ไว้ว่า:
   `answer = chunks[0]["answer"]` ซึ่งจะส่งคำตอบเรื่องค่าบริการ AI ไปตอบคำถามเรื่องตั๋วเครื่องบินทันที!

[แนวทางการแก้ไขสำหรับ LAB04]
1. กำหนด SIMILARITY_THRESHOLD (เช่น cutoff score = 0.40) หากคะแนนสูงสุดไม่ถึงเกณฑ์
   ให้ถือว่าค้นหาไม่พบ (No Evidence) ทันที
2. เสริม System Prompt กฎ Guardrails เข้มงวด และตอบปฏิเสธด้วย NO_CONTEXT_MESSAGE
"""

import sys
from data_loader import load_qa

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")

DOCS = load_qa()
NO_CONTEXT_MESSAGE = "ขออภัย ไม่พบข้อมูลที่เกี่ยวข้องในฐานข้อมูลโมเดล AI"
SIMILARITY_THRESHOLD = 0.40  # เกณฑ์คะแนนขั้นต่ำสำหรับตัดข้อมูลที่ไม่เกี่ยวข้องออก


def naive_retrieve(question, top_k=3):
    """จำลองการค้นหาแบบเดิมของ LAB04 (คืนค่าเอกสารเสมอ แม้คะแนนจะต่ำมากเพียงเพราะตรงกันแค่คำเดียว)"""
    keywords = ["ราคา", "โมเดล", "ai", "anthropic", "claude", "gpt", "context", "token"]
    words = [w.lower() for w in keywords if w in question.lower()]
    if not words:
        words = question.lower().split()

    scored = []
    for d in DOCS:
        matched = sum(1 for w in words if w in d["text"].lower())
        score = matched / max(1, len(words) + 2)
        if matched > 0:
            scored.append((score, d))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]


def lab04_bad_generate(question, retrieved_items):
    """
    จำลองพฤติกรรมเดิมของ LAB04:
    - ดึง Chunk แรกมาตอบทันที หรือส่งให้ LLM ทั้งๆ ที่คะแนนต่ำมากจนเกิดการมโน/หลอน
    """
    if not retrieved_items:
        return NO_CONTEXT_MESSAGE

    best_score, top_doc = retrieved_items[0]
    if best_score < SIMILARITY_THRESHOLD:
        # จำลองการหลอนของ LLM ที่นำบริบทราคา AI ไปมั่วตอบคำถามตั๋วเครื่องบิน
        return f"[Hallucination / Wrong Fallback]: ตั๋วเครื่องบินราคาประมาณเดือนละ 20 ดอลลาร์สหรัฐ (อ้างอิงผิดจาก Chunk: '{top_doc['question']}')"

    return top_doc["answer"]


def lab04_fixed_generate(question, retrieved_items):
    """
    การแก้ไขที่ถูกต้อง:
    - ตรวจสอบทั้งการมีอยู่ของ Chunk และ Confidence Score Threshold
    - ปฏิเสธการตอบอย่างปลอดภัยหากไม่มีหลักฐานสนับสนุนที่หนักแน่นพอ
    """
    if not retrieved_items:
        return NO_CONTEXT_MESSAGE

    best_score, top_doc = retrieved_items[0]
    if best_score < SIMILARITY_THRESHOLD:
        return f"[Grounded Guardrail]: {NO_CONTEXT_MESSAGE} (คะแนนสูงสุด {best_score:.2f} ต่ำกว่าเกณฑ์ {SIMILARITY_THRESHOLD})"

    return top_doc["answer"]


def run():
    print("=" * 70)
    print(" 🛑 Problem 01: Hallucination & Context Deficiency")
    print("=" * 70)

    test_queries = [
        ("คำถามตรงตามฐานความรู้ (In-KB)", "Anthropic มีโมเดลระดับไหนบ้าง"),
        ("คำถามนอกฐานความรู้แต่มีคีย์เวิร์ดหลงมา (Out-of-KB)", "ตั๋วเครื่องบินไปเชียงใหม่ราคาเท่าไหร่"),
    ]

    for label, query in test_queries:
        print(f"\n▶ [{label}] คำถาม: '{query}'")
        retrieved = naive_retrieve(query)

        if retrieved:
            print(f"  ผลการค้นหา Top-1 (คะแนน: {retrieved[0][0]:.2f}): '{retrieved[0][1]['question']}'")
        else:
            print("  ผลการค้นหา: ไม่พบเอกสารใดๆ")

        bad_ans = lab04_bad_generate(query, retrieved)
        fixed_ans = lab04_fixed_generate(query, retrieved)

        print(f"  ❌ คำตอบแบบ LAB04 เดิม : {bad_ans}")
        print(f"  ✅ คำตอบหลังแก้ไข (Fixed) : {fixed_ans}")

    print("\n" + "-" * 70)
    print("💡 สรุปสาเหตุและการแก้ไขสำหรับโค้ด LAB04:")
    print("1. สาเหตุ: LAB04 ใน generator.py เช็คแค่ 'if not chunks:' แต่ไม่ตรวจคะแนน Similarity Score")
    print("   เมื่อถามเรื่อง 'ตั๋วเครื่องบิน...ราคาเท่าไหร่' มีคำว่า 'ราคา' ไปตรงกับคลัง AI")
    print("   ทำให้ระบบดึง Chunk ค่าบริการ AI มาตอบ ส่งผลให้ LLM มั่วว่าตั๋วราคา $20")
    print("2. วิธีแก้: เพิ่ม SIMILARITY_THRESHOLD ใน config.py และคัดกรองคะแนนก่อนส่ง Context ให้ LLM")
    print("-" * 70)


if __name__ == "__main__":
    run()
