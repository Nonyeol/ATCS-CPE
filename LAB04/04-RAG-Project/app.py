"""
app.py
------
Flask web server for LAB04 RAG Project.
Exposes the RAGPipeline via web API and renders an interactive web interface.

Usage:
    python app.py
    Then open http://127.0.0.1:5000 in your browser.
"""

import os
from flask import Flask, jsonify, render_template, request

import config
from src.document_loader import load_qa_file
from src.rag_pipeline import RAGPipeline

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

# Initialize RAG Pipeline at server start so models/index stay cached in RAM
print("[web] Loading RAG Pipeline and FAISS Index into memory...")
rag_pipeline = RAGPipeline()
print("[web] RAG Pipeline loaded successfully!")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "กรุณาพิมพ์คำถาม"}), 400

    try:
        # Call LAB04 RAGPipeline directly
        result = rag_pipeline.ask(question)

        return jsonify({
            "question": question,
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "queries_used": result.get("queries_used", [question]),
            "timings": result.get("timings", {}),
            "no_context": result.get("no_context", False),
        })
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/documents")
def api_documents():
    """List all Q&A records in the dataset for knowledge base browsing."""
    try:
        records = load_qa_file(config.SOURCE_FILE)
        return jsonify(records)
    except Exception as error:
        return jsonify({"error": str(error)}), 500

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print(" 🚀 LAB04 RAG Web Server starting at http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
