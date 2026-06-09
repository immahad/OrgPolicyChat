"""ChromaDB vector index for the policy RAG app."""

from __future__ import annotations
import os
import shutil
from pathlib import Path
import chromadb
from langchain_core.documents import Document

COLLECTION_NAME = "policy_docs"


class _PolicyEmbedFn:
    """
    Thin wrapper that makes PolicyEmbeddings look like a chromadb
    EmbeddingFunction.  We pass this to get_or_create_collection /
    get_collection so chromadb NEVER tries to load its built-in
    DefaultEmbeddingFunction (which requires onnxruntime).

    Note: since we always supply query_embeddings / embeddings
    explicitly in .add() and .query() calls, chromadb will never
    actually *call* this function — it's just stored as metadata.
    """

    def __init__(self, policy_embeddings):
        self._pe = policy_embeddings

    def __call__(self, input):          # noqa: A002
        return self._pe.embed_documents(list(input))


def _get_client(persist_directory: str):
    return chromadb.PersistentClient(path=persist_directory)


def save_index(chunks, embeddings, persist_directory: str, reset: bool = False) -> int:
    if reset and os.path.isdir(persist_directory):
        shutil.rmtree(persist_directory)

    client = _get_client(persist_directory)
    ef = _PolicyEmbedFn(embeddings)

    # Delete existing collection if it exists
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
        embedding_function=ef,          # ← our EF, not chromadb's DefaultEF
    )

    # Embed in batches of 50 to avoid memory issues
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c.page_content for c in batch]
        vectors = embeddings.embed_documents(texts)
        ids = [f"chunk_{i + j}" for j in range(len(batch))]
        metadatas = [dict(c.metadata) for c in batch]

        collection.add(
            ids=ids,
            embeddings=vectors,
            documents=texts,
            metadatas=metadatas,
        )

    return collection.count()


def search_index(question: str, embeddings, persist_directory: str, k: int = 5):
    client = _get_client(persist_directory)
    ef = _PolicyEmbedFn(embeddings)

    collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,          # ← our EF, not chromadb's DefaultEF
    )

    query_vector = embeddings.embed_query(question)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    docs_and_scores = []
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for text, meta, distance in zip(documents, metadatas, distances):
        # ChromaDB cosine distance → similarity score (1 - distance)
        score = 1.0 - distance
        doc = Document(page_content=text, metadata=meta)
        docs_and_scores.append((doc, score))

    return docs_and_scores