"""
retriever.py - RAG pipeline: retrieve + generate
"""

import os
import time
import logging
from pathlib import Path

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma_db")
TOP_K       = int(os.getenv("TOP_K", 5))
GROQ_MODEL  = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are PolicyBot, a helpful assistant for Acme Corporation employees.
Your ONLY job is to answer questions about Acme Corporation's internal company policies and procedures.

STRICT RULES you must follow:
1. Answer ONLY using the provided policy context below. Do not use any outside knowledge.
2. If the question is not covered by the provided context, respond EXACTLY with:
   "I can only answer questions about Acme Corporation's policies, and this topic is not covered in our policy documents. Please contact HR at hr@acmecorp.com for further assistance."
3. Always end your answer with a "Sources:" section listing the document filenames you used.
4. Keep answers clear, concise, and professional. Maximum 300 words.
5. If citing specific numbers, rules, or dates, be precise and accurate to the source.
6. Do NOT speculate, guess, or add information not present in the context.

POLICY CONTEXT:
{context}
"""

# Module-level cache
_embeddings = None


def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        logger.info("Loading embedding model (once)...")
        from rag.embeddings import PolicyEmbeddings
        _embeddings = PolicyEmbeddings()
        logger.info("Embedding model loaded.")
    return _embeddings


def retrieve(question: str, k: int = TOP_K):
    """Retrieve top-k relevant chunks with similarity scores."""
    if not os.path.exists(CHROMA_PATH):
        raise RuntimeError(
            f"Vector store not found at '{CHROMA_PATH}'. "
            "Please run: python rag/ingest.py"
        )

    from rag.vector_index import search_index
    results = search_index(question, _get_embeddings(), CHROMA_PATH, k=k)

    filtered = [(doc, score) for doc, score in results if score > 0.2]
    return filtered if filtered else results[:2]


def build_context(results):
    """Build context string and source list from retrieved chunks."""
    context_parts = []
    sources  = []
    snippets = []

    for doc, score in results:
        source_file = doc.metadata.get("source_file", "unknown")
        doc_id      = doc.metadata.get("doc_id", source_file)
        text        = doc.page_content.strip()

        context_parts.append(f"[Document: {source_file}]\n{text}")

        if source_file not in sources:
            sources.append(source_file)

        snippets.append({
            "source": source_file,
            "doc_id": doc_id,
            "text":   text[:300] + ("..." if len(text) > 300 else ""),
            "score":  round(float(score), 3),
        })

    return "\n\n---\n\n".join(context_parts), sources, snippets


def generate(question: str, context: str) -> str:
    """Call Groq LLM with the retrieved context."""
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or api_key.strip() == "your_groq_api_key_here":
        return (
            "Demo mode: No GROQ_API_KEY set. "
            "Add your free Groq API key to the .env file.\n\n"
            "Sources: (demo mode)"
        )

    from langchain_groq import ChatGroq
    from langchain.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    llm = ChatGroq(
        model=GROQ_MODEL,
        temperature=0,
        max_tokens=600,
        api_key=api_key,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ])

    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": context, "question": question})


def get_rag_response(question: str, k: int = TOP_K) -> dict:
    """Full RAG pipeline: retrieve -> build context -> generate."""
    start = time.perf_counter()

    try:
        results                    = retrieve(question, k=k)
        context, sources, snippets = build_context(results)
        answer                     = generate(question, context)
        latency                    = round(time.perf_counter() - start, 3)

        return {
            "answer":   answer,
            "sources":  sources,
            "snippets": snippets,
            "latency":  latency,
            "status":   "ok",
        }

    except RuntimeError as e:
        logger.error(f"RuntimeError: {e}")
        return {
            "answer":   str(e),
            "sources":  [],
            "snippets": [],
            "latency":  round(time.perf_counter() - start, 3),
            "status":   "error",
        }
    except Exception as e:
        logger.exception("Unexpected error in RAG pipeline")
        return {
            "answer":   f"An error occurred: {str(e)}",
            "sources":  [],
            "snippets": [],
            "latency":  round(time.perf_counter() - start, 3),
            "status":   "error",
        }