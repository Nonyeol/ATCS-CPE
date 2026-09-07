# -*- coding: utf-8 -*-
"""
problem08_config.py
-------------------
ปัญหาที่ 8: การปรับแต่งค่าคอนฟิกและการตั้งค่าระบบ (RAG Configuration Impact)

[ข้อผิดพลาดที่พบในโค้ด LAB04]
1. ใน config.py ของ LAB04 สวิตช์การทำงานถูกปิดไว้หลายตัว (`USE_RERANK = False`, `USE_QUERY_TRANSFORM = False`, `USE_LLM = False`)
   เพื่อเน้นความเร็วระดับมิลลิวินาที (0.18s) แต่แลกมาด้วยความฉลาดและความแม่นยำที่ลดลงอย่างมาก
2. ปัญหา Index Desynchronization: เมื่อมีการแก้ไขค่า `CHUNK_SIZE`, `CHUNK_OVERLAP` หรือ `EMBEDDING_MODEL_NAME`
   ใน config.py ระบบ LAB04 จะไม่มีการแจ้งเตือนว่า Index ใน vector_db/ ล้าสมัยแล้ว
   หากผู้ใช้ลืมรัน `python build_index.py` ใหม่ ระบบจะทำงานด้วยเวกเตอร์ผิดขนาดหรือแมป Chunk ไม่ตรงทันที

[แนวทางการแก้ไขสำหรับ LAB04]
1. สร้าง Profile การตั้งค่าที่ชัดเจน เช่น Fast Profile vs High-Accuracy Profile
2. เพิ่มระบบตรวจสอบความสอดคล้องของ Index (Index Metadata Validation) เมื่อเปิดระบบ
"""

import sys
from data_loader import load_qa

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")

# คอนฟิกค่าตั้งต้นตามไฟล์ config.py ของ LAB04
LAB04_CONFIG = {
    "USE_HYBRID": True,
    "USE_RERANK": False,
    "USE_QUERY_TRANSFORM": False,
    "USE_MEMORY": True,
    "USE_LLM": False,
    "CHUNK_SIZE": 400,
    "CHUNK_OVERLAP": 50,
    "TOP_K": 3,
    "CANDIDATE_K": 20,
    "RRF_K": 60,
    "EMBEDDING_MODEL": "BAAI/bge-m3",
}

PROFILES = {
    "1. Fast / Lightweight (LAB04 Default)": {
        "USE_HYBRID": True,
        "USE_RERANK": False,
        "USE_QUERY_TRANSFORM": False,
        "USE_LLM": False,
        "ESTIMATED_LATENCY": "0.18 วินาที",
        "ACCURACY_LEVEL": "ปานกลาง (เน้นเร็ว แสดงข้อความดิบ)",
    },
    "2. High-Accuracy Enterprise RAG": {
        "USE_HYBRID": True,
        "USE_RERANK": True,
        "USE_QUERY_TRANSFORM": True,
        "USE_LLM": True,
        "ESTIMATED_LATENCY": "1.2 - 2.5 วินาที",
        "ACCURACY_LEVEL": "สูงมาก (จัดอันดับลึก + ขยายคำค้น + LLM สรุป)",
    },
    "3. Cost-Saving (Dense Only)": {
        "USE_HYBRID": False,
        "USE_RERANK": False,
        "USE_QUERY_TRANSFORM": False,
        "USE_LLM": True,
        "ESTIMATED_LATENCY": "0.65 วินาที",
        "ACCURACY_LEVEL": "ปานกลาง (ประหยัด RAM จาก BM25)",
    },
}


def run():
    print("=" * 70)
    print(" ⚙️ Problem 08: RAG Configuration & Hyperparameters")
    print("=" * 70)

    data = load_qa()
    print(f"ฐานความรู้: ai_models_qa.txt ({len(data)} รายการ Q&A)")
    print("\n[ค่าคอนฟิกปัจจุบันใน config.py ของ LAB04]:")
    for k, v in LAB04_CONFIG.items():
        print(f"  {k:22}: {v}")

    print("\n" + "-" * 70)
    print("[การเปรียบเทียบผลกระทบของ Profile การตั้งค่าระบบ (Trade-offs)]:")
    for name, p in PROFILES.items():
        print(f"\n▶ {name}:")
        print(f"  - สวิตช์: HYBRID={p['USE_HYBRID']} | RERANK={p['USE_RERANK']} | TRANSFORM={p['USE_QUERY_TRANSFORM']} | LLM={p['USE_LLM']}")
        print(f"  - ความเร็วเฉลี่ย : {p['ESTIMATED_LATENCY']}")
        print(f"  - ระดับความแม่นยำ: {p['ACCURACY_LEVEL']}")

    print("\n" + "-" * 70)
    print("[⚠️ ปัญหา Index Desynchronization ใน LAB04]:")
    print("  หากคุณแก้ CHUNK_SIZE = 400 -> 250 ใน config.py แต่ไม่ได้รัน 'python build_index.py'")
    print("  ไฟล์ vector_db/document.index และ chunk_store.json จะยังคงเป็นค่าเดิม (400 chars)")
    print("  ทำให้ตำแหน่ง Chunk ที่ค้นหาได้ไม่ตรงกับเนื้อหาจริง (Index Drift)")

    print("\n" + "-" * 70)
    print("💡 สรุปสาเหตุและการแก้ไขสำหรับโค้ด LAB04:")
    print("1. เลือก Profile ให้เหมาะกับ Use Case (เช่น งาน Web Real-time vs งานวิจัยที่ต้องการความแม่นยำสูง)")
    print("2. เพิ่มฟังก์ชันเช็ค Timestamp หรือ Hash ของ config.py เทียบกับ index_meta.json ใน build_index.py")
    print("-" * 70)


if __name__ == "__main__":
    run()
