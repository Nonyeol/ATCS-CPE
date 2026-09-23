"""
build_dataset.py
-----------------
Build (or rebuild) the chunk store + FAISS index for one dataset defined in
config.DATASETS. This is the same pipeline as labs 01-04 (extract -> chunk
-> embed -> build index), just parameterized so it can run for either
dataset used by the web demo (app.py).

Usage:
    python build_dataset.py ai_models
    python build_dataset.py scam_callcenter
    python build_dataset.py all          # builds every dataset in config.DATASETS
"""

import sys
import json

import numpy as np

import config
from src.document_loader import load_qa_file
from src.text_splitter import build_chunks
from src.embedding_model import EmbeddingModel
from src.vector_store import VectorStore, save_chunk_store


def build_one(dataset_key):
    if dataset_key not in config.DATASETS:
        raise ValueError(f"Unknown dataset '{dataset_key}'. Options: {list(config.DATASETS)}")

    cfg = config.DATASETS[dataset_key]
    print(f"\n=== Building dataset: {dataset_key} ({cfg['label']}) ===")

    # 1) load Q&A records from the .txt file
    records = load_qa_file(cfg["source_file"])
    print(f"[1/4] Loaded {len(records)} Q&A records from {cfg['source_file']}")

    # 2) split into chunks (same logic as lab02)
    chunks = build_chunks(records, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    with open(cfg["chunks_file"], "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"[2/4] Built {len(chunks)} chunks -> {cfg['chunks_file']}")

    # 3) embed each chunk (same logic as lab03)
    model = EmbeddingModel(config.EMBEDDING_MODEL_NAME)
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts)
    np.save(cfg["embeddings_file"], embeddings)
    print(f"[3/4] Created embeddings, shape={embeddings.shape} -> {cfg['embeddings_file']}")

    # 4) build + save the FAISS index and chunk store (same logic as lab04)
    store = VectorStore()
    store.build_index(embeddings)
    store.save(cfg["index_file"])
    save_chunk_store(chunks, cfg["chunk_store_file"])
    print(f"[4/4] Saved FAISS index -> {cfg['index_file']}")
    print(f"Done: {dataset_key}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    target = sys.argv[1]
    if target == "all":
        for key in config.DATASETS:
            build_one(key)
    else:
        build_one(target)
