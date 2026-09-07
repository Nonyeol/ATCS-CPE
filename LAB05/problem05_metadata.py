# -*- coding: utf-8 -*-
"""
problem05_metadata.py
---------------------
ปัญหาที่ 5: การคัดกรองด้วยข้อมูลกำกับ (Metadata Filtering)

[ข้อผิดพลาดที่พบในโค้ด LAB04]
1. ใน document_loader.py ของ LAB04 ดึงค่า `category` มาเก็บไว้ใน chunk_store.json ก็จริง
2. แต่ใน hybrid_retriever.py ฟังก์ชัน retrieve(), dense_search() และ bm25_search()
   "ไม่มี Parameter สำหรับรับค่า Metadata Filter" เลย
3. เมื่อผู้ใช้ต้องการคำตอบเฉพาะหมวด (เช่น ต้องการเฉพาะหมวด 'ราคาและ context window')
   ผลการค้นหาแบบไม่กรองจะดึงข้อความจากหมวดอื่น (เช่น 'ภาพรวมค่าย AI หลัก' หรือ 'คำศัพท์พื้นฐาน')
   ที่บังเอิญมีคำว่า 'โมเดล', 'AI', 'ราคา' ปนเปื้อนเข้ามาแทน

[แนวทางการแก้ไขสำหรับ LAB04]
1. เพิ่ม Parameter `category_filter=None` ในฟังก์ชัน retrieve() ของ hybrid_retriever.py
2. ทำ Pre-filtering หรือ Post-filtering คัดเลือกเฉพาะ Chunk ที่มี category ตรงตามเงื่อนไข
"""

import sys
from data_loader import get_categories, load_qa

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")


def score_text(query, text):
    """คำนวณคะแนนความคล้ายคลึงจากคีย์เวิร์ดอย่างง่าย"""
    q_words = [w.lower() for w in query.split() if len(w) > 1]
    return sum(1 for w in q_words if w in text.lower())


def lab04_search_without_filter(data, query, top_k=3):
    """จำลองการค้นหาของ LAB04 (ค้นหาแบบไม่สน Metadata Category)"""
    scored = []
    for d in data:
        s = score_text(query, d["question"] + " " + d["answer"])
        scored.append((s, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]


def fixed_search_with_filter(data, query, category_filter=None, top_k=3):
    """การค้นหาที่รองรับการกรอง Metadata (Pre-filtering)"""
    candidate_docs = data
    if category_filter:
        candidate_docs = [d for d in data if d["category"] == category_filter]

    scored = []
    for d in candidate_docs:
        s = score_text(query, d["question"] + " " + d["answer"])
        scored.append((s, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]


def run():
    print("=" * 70)
    print(" 🏷️ Problem 05: Metadata Filtering")
    print("=" * 70)

    data = load_qa()
    all_cats = get_categories(data)
    print("หมวดหมู่ที่มีในระบบ:", all_cats)

    query = "โมเดล AI ราคา ค่าบริการต่อโทเคน"
    target_category = "ราคาและ context window"

    print(f"\nคำถามของผู้ใช้: '{query}'")
    print(f"เจตนาของผู้ใช้: ต้องการข้อมูลเฉพาะหมวด '{target_category}'")

    # แบบเดิมของ LAB04: ไม่มี Metadata Filter
    results_no_filter = lab04_search_without_filter(data, query, top_k=3)
    print("\n❌ ผลการค้นหาแบบ LAB04 เดิม (ไม่มี Metadata Filter):")
    for i, (score, doc) in enumerate(results_no_filter, start=1):
        is_target = "✅" if doc["category"] == target_category else "⚠️ ผิดหมวด"
        print(f"  อันดับ {i} [คะแนน {score}] หมวด: '{doc['category']}' {is_target}")
        print(f"       คำถาม: {doc['question']}")

    # แบบแก้ไข: มี Metadata Pre-filtering
    results_filtered = fixed_search_with_filter(data, query, category_filter=target_category, top_k=3)
    print(f"\n✅ ผลการค้นหาหลังแก้ไข (กรองเฉพาะหมวด '{target_category}'):")
    for i, (score, doc) in enumerate(results_filtered, start=1):
        print(f"  อันดับ {i} [คะแนน {score}] หมวด: '{doc['category']}' ✅")
        print(f"       คำถาม: {doc['question']}")

    print("\n" + "-" * 70)
    print("💡 สรุปสาเหตุและการแก้ไขสำหรับโค้ด LAB04:")
    print("1. สาเหตุ: แม้ LAB04 จะเก็บ category ไว้ใน chunk_store แต่ hybrid_retriever.py ไม่รองรับการกรอง")
    print("2. วิธีแก้: เพิ่ม category_filter ใน HybridRetriever.retrieve() เพื่อคัดกรองเฉพาะหมวดที่ตรงเจตนา")
    print("-" * 70)


if __name__ == "__main__":
    run()
