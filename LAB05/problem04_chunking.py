# -*- coding: utf-8 -*-
"""
problem04_chunking.py
---------------------
ปัญหาที่ 4: การหั่นข้อความ (Chunking Strategy - Size & Overlap)

[ข้อผิดพลาดที่พบในโค้ด LAB04]
1. ใน text_splitter.py ของ LAB04 ฟังก์ชัน split_text() ใช้การหั่นตามจำนวนตัวอักษรดิบๆ:
   `text[start:start + chunk_size]`
   เนื่องจากภาษาไทยไม่มีการเว้นวรรคระหว่างคำ การหั่นแบบ Character Slicing จะทำให้ "คำศัพท์ถูกตัดขาดครึ่งคำ"
   เช่น 'ปัญ|ญาประดิษฐ์', 'ประสิทธิ|ภาพ' ส่งผลให้ Tokenizer และ Embedding เสียความหมาย
2. การเลือกขนาด Chunk ไม่สมดุล:
   - เล็กเกินไป (Too small): ใจความขาดตอน ขาดบริบทแวดล้อม
   - ใหญ่เกินไป (Too large): มี Noise ปะปนมากเกินไป และ Embedding เจือจาง (Dilution)
   - ไม่มี Overlap: รอยต่อระหว่างประโยคขาดออกจากกัน

[แนวทางการแก้ไขสำหรับ LAB04]
1. ใช้ Word-aware หรือ Sentence-aware Chunking แทนการตัดตามความยาวตัวอักษรทื่อๆ
2. กำหนด Chunk Size ให้สัมพันธ์กับโครงสร้างข้อมูล (เช่น 300-500 ตัวอักษร) พร้อม Overlap 10-15%
"""

import sys
from data_loader import load_qa

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")


def lab04_naive_split(text, chunk_size=100, overlap=20):
    """จำลองการตัดคำแบบเดิมของ LAB04 (Character slicing)"""
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        if start + chunk_size >= len(text):
            break
        start += chunk_size - overlap
    return chunks


def fixed_word_aware_split(text, target_size=100, overlap=20):
    """การตัดคำที่คำนึงถึงขอบเขตของคำและวรรคตอน (Word-aware)"""
    try:
        from pythainlp.tokenize import word_tokenize
        words = word_tokenize(text, engine="newmm")
    except ImportError:
        words = text.split()

    chunks = []
    current_chunk = []
    current_len = 0

    for w in words:
        current_chunk.append(w)
        current_len += len(w)
        if current_len >= target_size:
            chunks.append("".join(current_chunk))
            # คำนวณ overlap จากคำท้ายๆ
            overlap_words = []
            overlap_len = 0
            for ow in reversed(current_chunk):
                if overlap_len + len(ow) <= overlap:
                    overlap_words.insert(0, ow)
                    overlap_len += len(ow)
                else:
                    break
            current_chunk = overlap_words
            current_len = overlap_len

    if current_chunk:
        chunks.append("".join(current_chunk))
    return chunks


def run():
    print("=" * 70)
    print(" ✂️ Problem 04: Chunking Strategy (Size & Overlap)")
    print("=" * 70)

    data = load_qa()
    # ดึงคำตอบตัวอย่างที่มีศัพท์ทางเทคนิค
    sample_text = next(d["answer"] for d in data if "Mythos" in d["answer"])

    print("\n[ข้อความตัวอย่างสำหรับทดสอบ]:")
    print(sample_text[:180] + "...")

    # ทดสอบ 1: Naive character slicing ของ LAB04
    naive_chunks = lab04_naive_split(sample_text, chunk_size=80, overlap=15)
    print("\n❌ ผลลัพธ์จากการตัดแบบ Character Slicing ของ LAB04 เดิม (chunk_size=80):")
    for i, c in enumerate(naive_chunks[:3], start=1):
        print(f"  Chunk {i} [{len(c)} chars]: '{c}'")
    print("  ⚠️ สังเกตตรงรอยต่อ: คำศัพท์จะถูกหั่นกลางคำ ทำให้ BM25 Tokenizer และ Embedding เพี้ยน")

    # ทดสอบ 2: Word-aware chunking หลังแก้ไข
    fixed_chunks = fixed_word_aware_split(sample_text, target_size=80, overlap=15)
    print("\n✅ ผลลัพธ์หลังแก้ไขด้วย Word-aware Chunking (Fixed):")
    for i, c in enumerate(fixed_chunks[:3], start=1):
        print(f"  Chunk {i} [{len(c)} chars]: '{c}'")
    print("  ✨ สังเกตตรงรอยต่อ: คำศัพท์ทุกคำคงรูปสมบูรณ์ ไม่มีการขาดครึ่งคำ")

    # วิเคราะห์ผลกระทบของขนาด Chunk
    print("\n" + "-" * 70)
    print("[เปรียบเทียบผลกระทบของขนาด Chunk (Trade-offs)]:")
    print("  1. Chunk เล็กเกินไป (< 100 chars):")
    print("     - ปัญหา: ข้อความขาดตอน เช่น เหลือแค่ 'และ Fable ซึ่งเป็นรุ่นที่...' ขาดบริบทว่าเป็นของค่ายใด")
    print("  2. Chunk ใหญ่เกินไป (> 1000 chars):")
    print("     - ปัญหา: รวมหลายหัวข้อปนกัน (Noise สูง) Cosine Similarity เฉลี่ยเจือจาง และเปลือง Token")
    print("  3. Chunk ที่เหมาะสม (300-500 chars พร้อม Overlap 10-15%):")
    print("     - ข้อดี: ครบ 1 ใจความสมบูรณ์ และมี Overlap เชื่อมประโยคข้าม Chunk ได้อย่างต่อเนื่อง")

    print("\n" + "-" * 70)
    print("💡 สรุปสาเหตุและการแก้ไขสำหรับโค้ด LAB04:")
    print("1. แก้ไข split_text() ใน text_splitter.py ให้ใช้การตัดคำตามขอบเขตคำภาษาไทย (Word-aware)")
    print("2. ปรับค่า CHUNK_SIZE = 400 และ CHUNK_OVERLAP = 50 ใน config.py ให้เหมาะสมกับลักษณะข้อมูล")
    print("-" * 70)


if __name__ == "__main__":
    run()
