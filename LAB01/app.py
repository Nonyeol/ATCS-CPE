"""
app.py
------
Small Flask web server that exposes the existing RAG pipeline (src/retriever.py)
as a demo website with a dataset switcher, matching the "RAG Lab" style demo.

Before running this, build the index for each dataset once:
    python build_dataset.py all

Then run the server:
    python app.py
and open http://127.0.0.1:5000
"""

import os

from flask import Flask, jsonify, request, render_template

import config
from src.document_loader import load_qa_file
from src.retriever import Retriever

app = Flask(__name__)

# Retrievers are loaded lazily and cached here, keyed by dataset key.
# Loading a Retriever loads the embedding model + FAISS index, which is
# somewhat slow, so we only do it once per dataset per server run.
_retrievers = {}


def get_retriever(dataset_key):
    if dataset_key not in config.DATASETS:
        raise ValueError(f"Unknown dataset: {dataset_key}")

    if dataset_key not in _retrievers:
        cfg = config.DATASETS[dataset_key]
        if not os.path.exists(cfg["index_file"]):
            raise FileNotFoundError(
                f"Index for '{dataset_key}' not found. Run: python build_dataset.py {dataset_key}"
            )
        _retrievers[dataset_key] = Retriever(
            model_name=config.EMBEDDING_MODEL_NAME,
            index_path=cfg["index_file"],
            chunk_store_path=cfg["chunk_store_file"],
        )
    return _retrievers[dataset_key]


@app.route("/")
def index():
    return render_template("index.html", datasets=config.DATASETS)


@app.route("/api/datasets")
def api_datasets():
    """List available datasets (for the switcher tabs + sample question chips)."""
    out = []
    for key, cfg in config.DATASETS.items():
        out.append({
            "key": key,
            "label": cfg["label"],
            "sample_questions": cfg.get("sample_questions", []),
        })
    return jsonify(out)


@app.route("/api/documents")
def api_documents():
    """List every Q&A record in a dataset (for the 'คลังเอกสาร' panel)."""   
    dataset_key = request.args.get("dataset", "ai_models")
    if dataset_key not in config.DATASETS:
        return jsonify({"error": f"Unknown dataset: {dataset_key}"}), 400

    cfg = config.DATASETS[dataset_key]
    records = load_qa_file(cfg["source_file"])
    return jsonify([
        {
            "id": r["id"],
            "category": r["category"],
            "question": r["question"],
            "answer": r["answer"],
        }
        for r in records
    ])


@app.route("/api/ask", methods=["POST"])
def api_ask():
    """Answer a question by retrieving the most relevant chunk(s) from the dataset."""
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    dataset_key = data.get("dataset", "ai_models")

    if not question:
        return jsonify({"error": "กรุณาพิมพ์คำถาม"}), 400
    if dataset_key not in config.DATASETS:
        return jsonify({"error": f"Unknown dataset: {dataset_key}"}), 400

    try:
        retriever = get_retriever(dataset_key)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503

    results = retriever.retrieve(question, top_k=config.TOP_K)
    if not results:
        return jsonify({"question": question, "answer": None, "sources": []})

    best = results[0]
    return jsonify({
        "question": question,
        "answer": best["answer"],
        "category": best["category"],
        "score": best["score"],
        "sources": [
            {
                "category": r["category"],
                "question": r["question"],
                "answer": r["answer"],
                "score": r["score"],
            }
            for r in results
        ],
    })


if __name__ == "__main__":
    app.run(debug=True)
