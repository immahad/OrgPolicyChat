"""
app.py - Flask web application for the Policy RAG chatbot

Endpoints:
  GET  /        - Chat UI
  POST /chat    - RAG query endpoint
  GET  /health  - Health check
  GET  /debug   - Diagnostic endpoint (step-by-step component test)
"""

import os
import sys
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def _vector_store_ready() -> bool:
    chroma_path = Path(os.getenv("CHROMA_PATH", "chroma_db"))
    # ChromaDB 0.6.x uses chroma.sqlite3 (not index.json)
    return chroma_path.is_dir() and (
        (chroma_path / "chroma.sqlite3").is_file()
        or any(chroma_path.iterdir())
    )


app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# ── Pre-warm: actually load the SentenceTransformer model into memory ─────────
# Without this, the first request triggers model loading (~15-30s) and
# gunicorn's default 30s worker timeout can kill it → 500.
try:
    from rag.retriever import _get_embeddings
    _emb = _get_embeddings()
    _emb.embed_query("warm up")           # ← this is what actually loads the model
    logger.info("Embedding model pre-warmed successfully.")
except Exception as _e:
    logger.warning(f"Could not pre-warm embedding model: {type(_e).__name__}: {_e}")
# ─────────────────────────────────────────────────────────────────────────────


@app.route("/")
def index():
    """Serve the chat UI."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    POST /chat
    Body:    { "question": "What is the PTO policy?" }
    Returns: { "answer": "...", "sources": [...], "snippets": [...], "latency": 0.5 }
    """
    data = request.get_json(silent=True)
    if not data or not data.get("question", "").strip():
        return jsonify({"error": "Missing or empty 'question' field"}), 400

    question = data["question"].strip()

    if len(question) > 500:
        return jsonify({"error": "Question too long (max 500 characters)"}), 400

    logger.info(f"Question: {question[:80]}")

    try:
        from rag.retriever import get_rag_response
        result = get_rag_response(question)
        logger.info(f"Answered in {result['latency']}s | sources: {result['sources']}")
        return jsonify(result)

    except Exception as e:
        logger.exception("Error in /chat endpoint")
        return jsonify({
            "answer":   f"Server error [{type(e).__name__}]: {str(e)}",
            "sources":  [],
            "snippets": [],
            "latency":  0,
            "status":   "error",
        }), 500


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status":       "ok",
        "service":      "Policy RAG",
        "version":      "1.0.0",
        "vector_store": _vector_store_ready(),
    })


@app.route("/debug")
def debug():
    """
    Diagnostic endpoint — tests every component step-by-step.
    Hit this on Render to find out exactly where the pipeline breaks:
      https://rag-policybot.onrender.com/debug
    """
    chroma_path = os.getenv("CHROMA_PATH", "chroma_db")
    groq_key    = os.getenv("GROQ_API_KEY", "")

    report = {
        "python_version":   sys.version,
        "working_dir":      os.getcwd(),
        "chroma_path":      chroma_path,
        "chroma_dir_exists": os.path.isdir(chroma_path),
        "groq_key_present": bool(groq_key),
        "groq_key_is_placeholder": groq_key.strip() == "your_groq_api_key_here",
        "steps": {},
    }

    # ── Step 1: Import chromadb ───────────────────────────────────────────────
    try:
        import chromadb
        report["steps"]["1_chromadb_import"] = f"OK  (chromadb {chromadb.__version__})"
    except Exception as exc:
        report["steps"]["1_chromadb_import"] = f"FAIL  {type(exc).__name__}: {exc}"
        return jsonify(report)

    # ── Step 2: Open PersistentClient ────────────────────────────────────────
    try:
        client = chromadb.PersistentClient(path=chroma_path)
        report["steps"]["2_chroma_client"] = "OK"
    except Exception as exc:
        report["steps"]["2_chroma_client"] = f"FAIL  {type(exc).__name__}: {exc}"
        return jsonify(report)

    # ── Step 3: List collections ──────────────────────────────────────────────
    try:
        cols = [c.name for c in client.list_collections()]
        report["steps"]["3_list_collections"] = f"OK  {cols}"
    except Exception as exc:
        report["steps"]["3_list_collections"] = f"FAIL  {type(exc).__name__}: {exc}"
        return jsonify(report)

    # ── Step 4: Import & load embedding model ────────────────────────────────
    try:
        from rag.retriever import _get_embeddings
        emb = _get_embeddings()
        vec = emb.embed_query("test")
        report["steps"]["4_embed_query"] = f"OK  (dim={len(vec)})"
    except Exception as exc:
        report["steps"]["4_embed_query"] = f"FAIL  {type(exc).__name__}: {exc}"
        return jsonify(report)

    # ── Step 5: Get collection ────────────────────────────────────────────────
    try:
        from rag.vector_index import _PolicyEmbedFn, COLLECTION_NAME
        ef = _PolicyEmbedFn(emb)
        col = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
        report["steps"]["5_get_collection"] = f"OK  (count={col.count()})"
    except Exception as exc:
        report["steps"]["5_get_collection"] = f"FAIL  {type(exc).__name__}: {exc}"
        return jsonify(report)

    # ── Step 6: Vector search ─────────────────────────────────────────────────
    try:
        from rag.vector_index import search_index
        hits = search_index("performance rating", emb, chroma_path, k=2)
        report["steps"]["6_search_index"] = f"OK  (hits={len(hits)}, top_score={round(hits[0][1], 3) if hits else 'n/a'})"
    except Exception as exc:
        report["steps"]["6_search_index"] = f"FAIL  {type(exc).__name__}: {exc}"
        return jsonify(report)

    # ── Step 7: Groq API call ────────────────────────────────────────────────
    if not groq_key or groq_key.strip() == "your_groq_api_key_here":
        report["steps"]["7_groq_api"] = "SKIP  (no GROQ_API_KEY set)"
    else:
        try:
            from langchain_groq import ChatGroq
            llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0,
                           max_tokens=20, api_key=groq_key)
            resp = llm.invoke("Say OK")
            report["steps"]["7_groq_api"] = f"OK  (reply: {resp.content[:40]})"
        except Exception as exc:
            report["steps"]["7_groq_api"] = f"FAIL  {type(exc).__name__}: {exc}"

    report["overall"] = "ALL_OK" if all(
        v.startswith("OK") or v.startswith("SKIP")
        for v in report["steps"].values()
    ) else "SOME_STEPS_FAILED"

    return jsonify(report)


if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "production") == "development"
    logger.info(f"Starting PolicyBot on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
