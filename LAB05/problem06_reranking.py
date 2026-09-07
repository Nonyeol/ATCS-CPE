# -*- coding: utf-8 -*-
"""
problem06_reranking.py
----------------------
ปัญหาที่ 6: การเลือก Top-K และการจัดอันดับใหม่ (First-Stage vs Re-ranking)

[ข้อผิดพลาดที่พบในโค้ด LAB04]
1. ใน config.py ของ LAB04 ตั้งค่า `USE_RERANK = False` เป็นค่าเริ่มต้นเพื่อเน้นความเร็ว
2. การค้นหาขั้นแรก (First-stage) ด้วย Bi-encoder (Vector Search) และ BM25 จะให้คะแนนคำกว้างๆ
   (เช่น 'โมเดล', 'AI', 'ค่าย', 'ความปลอดภัย') พอๆ กัน
3. ส่งผลให้เอกสารที่มีคำตอบเจาะจงและตรงประเด็นที่สุด ถูกดันไปอยู่อันดับท้ายๆ (เช่น อันดับ 5-7)
   เมื่อระบบตัดเอาเฉพาะ `TOP_K = 3` เอกสารคำตอบจริงจึงหลุดโผ ไม่ถูกส่งไปให้ LLM

[แนวทางการแก้ไขสำหรับ LAB04]
1. เปิด `USE_RERANK = True` ใน config.py
2. ดึง Candidate_K ออกมาจำนวนมากก่อน (เช่น 15-20 chunks) แล้วใช้ Cross-Encoder (BAAI/bge-reranker-v2-m3)
   มาคำนวณ Attention ร่วมกันระหว่างคำถามและเอกสารเพื่อจัดอันดับใหม่
"""

import sys
from data_loader import load_qa

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")

# ศัพท์ทั่วไป (Generic) vs ศัพท์เฉพาะเจาะจง (Specific)
GENERIC_TERMS = ["โมเดล", "ai", "ความปลอดภัย", "ค่าย"]
SPECIFIC_TERMS = ["fable", "mythos", "ชีววิทยา", "ไซเบอร์", "สูงกว่า opus"]


def first_stage_score(doc):
    """จำลองการค้นหาขั้นแรก (Bi-encoder / BM25) ที่คำนวณแยกคำกว้างๆ"""
    text = (doc["question"] + " " + doc["answer"]).lower()
    return sum(1 for t in GENERIC_TERMS if t in text)


def cross_encoder_rerank_score(doc):
    """จำลอง Cross-Encoder Reranking ที่จับคู่ความสัมพันธ์เชิงลึก (Semantic Interaction)"""
    base = first_stage_score(doc)
    text = (doc["question"] + " " + doc["answer"]).lower()
    # Cross-Encoder ให้ค่าน้ำหนักสูงมากกับคำเฉพาะทางและเจตนารมณ์ที่แท้จริง
    specific_bonus = sum(5 for t in SPECIFIC_TERMS if t in text)
    return base + specific_bonus


def run():
    print("=" * 70)
    print(" 🎯 Problem 06: Top-K Selection & Cross-Encoder Re-ranking")
    print("=" * 70)

    data = load_qa()
    query = "โมเดลตัวไหนของ Anthropic ที่สูงกว่า Opus และเพิ่มมาตรการความปลอดภัยไซเบอร์และชีววิทยา"

    print(f"คำถามเจาะจง: '{query}'\n")

    # ขั้นที่ 1: First-stage Retrieval (แบบที่ LAB04 ใช้เมื่อ USE_RERANK = False)
    first_stage_results = sorted(data, key=first_stage_score, reverse=True)[:6]

    print("❌ อันดับก่อน Re-ranking (First-Stage: BM25 + Vector Search):")
    for rank, d in enumerate(first_stage_results, start=1):
        score = first_stage_score(d)
        is_target = "⭐ (คำตอบที่ถูกต้องตรงประเด็น!)" if "Fable" in d["answer"] else ""
        topk_status = "[ติด Top-3]" if rank <= 3 else "[⚠️ หลุด Top-3!]"
        print(f"  อันดับ {rank} {topk_status} (คะแนน: {score}) {is_target}")
        print(f"       คำถาม: {d['question']}")

    print("\n⚠️ ปัญหาใน LAB04: เนื่องจากปิด USE_RERANK และตั้ง TOP_K = 3")
    print("   เอกสารที่มีคำตอบสำคัญที่สุด (Fable & Mythos) หลุดไปอยู่อันดับ 5-6 ทำให้ LLM ไม่มีข้อมูลตอบ!")

    # ขั้นที่ 2: Second-stage Reranking (เมื่อเปิด USE_RERANK = True)
    reranked_results = sorted(first_stage_results, key=cross_encoder_rerank_score, reverse=True)

    print("\n" + "-" * 70)
    print("✅ อันดับหลังทำ Cross-Encoder Re-ranking (Two-Stage Retrieval):")
    for rank, d in enumerate(reranked_results[:3], start=1):
        score = cross_encoder_rerank_score(d)
        is_target = "⭐ (คำตอบถูกต้องถูกดันขึ้นอันดับ 1 สำเร็จ!)" if "Fable" in d["answer"] else ""
        print(f"  อันดับ {rank} [ติด Top-3] (คะแนน Rerank: {score}) {is_target}")
        print(f"       คำถาม: {d['question']}")

    print("\n" + "-" * 70)
    print("💡 สรุปสาเหตุและการแก้ไขสำหรับโค้ด LAB04:")
    print("1. สาเหตุ: LAB04 ตั้ง USE_RERANK = False ทำให้เอกสารที่ตรงประเด็นลึกๆ แพ้เอกสารที่มีคำกว้างๆ")
    print("2. วิธีแก้: เปิด `USE_RERANK = True` ใน config.py และใช้ BAAI/bge-reranker-v2-m3")
    print("-" * 70)


if __name__ == "__main__":
    run()
