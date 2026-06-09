"""
ingest.py - Document ingestion and indexing pipeline

Loads policy documents from the policies/ directory,
chunks them with overlap, embeds with a lightweight local model,
and stores in a local JSON vector index.
"""

import os
import shutil
import logging
import re
from html import unescape
from pathlib import Path

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from rag.embeddings import PolicyEmbeddings
from rag.vector_index import save_index

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Config
CHROMA_PATH   = os.getenv("CHROMA_PATH", "chroma_db")
POLICIES_PATH = os.getenv("POLICIES_PATH", "policies")
CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))


def load_documents(policies_path: str):
    """Load all .md and .txt files from the policies directory."""
    logger.info(f"Loading documents from: {policies_path}")
    docs = []

    for ext in ["**/*.md", "**/*.txt"]:
        loader = DirectoryLoader(
            policies_path,
            glob=ext,
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            show_progress=True,
        )
        loaded = loader.load()
        docs.extend(loaded)
        logger.info(f"  Loaded {len(loaded)} files matching {ext}")

    # Load HTML if any
    html_files = list(Path(policies_path).glob("**/*.html")) + list(
        Path(policies_path).glob("**/*.htm")
    )
    for html_path in html_files:
        raw_html = html_path.read_text(encoding="utf-8", errors="ignore")
        text = unescape(re.sub(r"<[^>]+>", " ", raw_html))
        text = re.sub(r"\s+", " ", text).strip()
        docs.append(Document(page_content=text, metadata={"source": str(html_path)}))
    if html_files:
        logger.info(f"  Loaded {len(html_files)} HTML files")

    # Load PDFs if any
    pdf_files = list(Path(policies_path).glob("**/*.pdf"))
    if pdf_files:
        from langchain_community.document_loaders import PyPDFLoader
        for pdf_path in pdf_files:
            loader = PyPDFLoader(str(pdf_path))
            pdf_docs = loader.load()
            docs.extend(pdf_docs)
            logger.info(f"  Loaded PDF: {pdf_path.name} ({len(pdf_docs)} pages)")

    logger.info(f"Total documents loaded: {len(docs)}")
    return docs


def chunk_documents(docs):
    """Split documents into overlapping chunks for better retrieval."""
    logger.info(f"Chunking with size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", ". ", " "],
        length_function=len,
    )

    chunks = splitter.split_documents(docs)

    for chunk in chunks:
        raw_source = chunk.metadata.get("source", "unknown")
        chunk.metadata["source_file"] = Path(raw_source).name
        chunk.metadata["doc_id"] = Path(raw_source).stem

    logger.info(f"Total chunks created: {len(chunks)}")
    return chunks


def build_vectorstore(chunks, reset: bool = False):
    """Embed chunks and store in a local JSON index."""
    if reset and os.path.exists(CHROMA_PATH):
        logger.info(f"Resetting existing vector store at: {CHROMA_PATH}")
        shutil.rmtree(CHROMA_PATH)

    os.makedirs(CHROMA_PATH, exist_ok=True)

    logger.info("Loading embedding model: sentence-transformers/all-MiniLM-L6-v2")
    embeddings = PolicyEmbeddings()

    logger.info("Building local vector index...")
    vector_count = save_index(
        chunks=chunks,
        embeddings=embeddings,
        persist_directory=CHROMA_PATH,
        reset=False,
    )

    logger.info(f"Vector store saved to: {CHROMA_PATH}")
    logger.info(f"Total vectors stored: {vector_count}")
    return vector_count


def ingest(reset: bool = True):
    """Full ingestion pipeline: load -> chunk -> embed -> store."""
    logger.info("=" * 55)
    logger.info("  Starting Policy Document Ingestion Pipeline")
    logger.info("=" * 55)

    docs   = load_documents(POLICIES_PATH)
    chunks = chunk_documents(docs)
    store  = build_vectorstore(chunks, reset=reset)

    logger.info("=" * 55)
    logger.info("  Ingestion complete!")
    logger.info(f"  Documents : {len(docs)}")
    logger.info(f"  Chunks    : {len(chunks)}")
    logger.info(f"  Vectors   : {store}")
    logger.info("=" * 55)
    return store


if __name__ == "__main__":
    ingest(reset=True)
