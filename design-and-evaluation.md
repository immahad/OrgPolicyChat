# Design and Evaluation Document

## 1. Design and Architecture Decisions

### 1.1 Overall Architecture

The system follows a classic RAG (Retrieval-Augmented Generation) architecture:

```
User Question
     │
     ▼
[Embedding Model]  ──→  Query Vector
     │
     ▼
[Local JSON Index]  ──→  Top-K Relevant Chunks + Scores
     │
     ▼
[Prompt Builder]  ──→  System Prompt + Context + Question
     │
     ▼
[Groq LLM]  ──→  Grounded Answer with Citations
     │
     ▼
Flask /chat endpoint  ──→  JSON Response to UI
```

---

### 1.2 Embedding Model: sentence-transformers/all-MiniLM-L6-v2

**Choice:** `sentence-transformers/all-MiniLM-L6-v2`

**Rationale:**
- **Strong retrieval quality** for short enterprise policy Q&A compared with lexical/hash baselines
- **Free and local** — no embedding API key required
- **Stable, standard baseline** for many small/medium RAG systems
- **Compact vector size (384-dim)** keeps index storage modest while preserving semantic recall

**Alternative considered:** A lightweight hashing embedder. Rejected because retrieval quality was materially worse in evaluation and produced weaker citation alignment.

---

### 1.3 Chunking Strategy

**Choice:** `RecursiveCharacterTextSplitter` with `chunk_size=500`, `chunk_overlap=100`

**Rationale:**
- **500 tokens** is large enough to capture complete policy rules (e.g., a full table row + surrounding context) but small enough to remain specific and avoid diluting relevance
- **100-token overlap (20%)** ensures that information split across chunk boundaries is not lost — crucial for policy documents where a rule may reference text from the previous paragraph
- **Recursive splitting on headings first** (`\n## `, `\n### `) means chunks respect document structure, keeping heading-related content together
- The splitter is deterministic for a fixed input corpus, which keeps ingestion reproducible

**Alternative considered:** Token-window chunking with tiktoken. Rejected because the character-based splitter is simpler to set up without a tokenizer dependency, and the approximate character→token mapping is adequate for these document sizes.

---

### 1.4 Vector Store: ChromaDB (Local)

**Choice:** ChromaDB with local persistence (`persist_directory="chroma_db"`)

**Rationale:**
- **Completely free** — no cloud account, no API key, zero cost
- **Persistent** — stores vectors to disk; ingestion only runs once
- **Easy setup** — single `pip install chromadb`, no Docker or server required
- **Native LangChain integration** — `Chroma.from_documents()` handles 
  embedding storage and retrieval in one call
- **Sufficient scale** — our corpus (~400 chunks) is well within 
  ChromaDB's local capacity

---

### 1.5 LLM: Groq (llama-3.3-70b-versatile)

**Choice:** Groq API with `llama-3.3-70b-versatile` model

**Rationale:**
- **Free tier** — Groq's free tier provides generous rate limits (6000 tokens/minute, 500 requests/day)
- **Fastest inference** — Groq's LPU hardware makes Llama 3.3-70b faster than GPT-4o in practice (~200 tokens/sec)
- **High quality** — Llama 3.3-70b performs on par with GPT-4 for instruction-following tasks
- **Temperature=0** ensures deterministic, factual answers (no hallucinations from randomness)

**Alternative considered:** OpenRouter free tier (various models). Groq was chosen because it consistently offers the best latency for this use case.

---

### 1.6 Retrieval: Top-K with Relevance Score Filtering

**Choice:** `k=5` with a relevance score threshold of `0.2`

**Rationale:**
- **k=5** retrieves enough context to cover multi-faceted questions (e.g., "What is the PTO policy?" may touch accrual, usage, and holidays)
- The **relevance threshold (0.2)** filters out semantically unrelated chunks, preventing the LLM from being confused by low-quality retrievals
- If all results score below 0.2 (truly out-of-scope question), the system falls back to the top 2 results — the LLM then correctly identifies the lack of relevant context and refuses to answer

---

### 1.7 Prompt Strategy and Guardrails

**System prompt enforces three guardrails:**

1. **Out-of-scope refusal** — Instructs the LLM to respond with a specific message if the question is not covered by the context, rather than hallucinating an answer
2. **Citation requirement** — Always end with a "Sources:" section listing document filenames
3. **Length limit** — Maximum 300 words prevents excessively long answers

The context injection format uses `[Document: filename]` prefixes, making it easy for the LLM to attribute information to specific files.

---

### 1.8 Web Application: Flask

**Choice:** Flask with a single-file HTML/CSS/JS chat UI

**Rationale:**
- Lightweight and minimal — no unnecessary overhead
- `render_template` serves the polished chat UI
- Three endpoints cover all requirements: `/` (UI), `/chat` (RAG API), `/health` (monitoring)
- Input validation (max 500 chars, empty check) prevents abuse
- Models cached in memory after first request to avoid reloading on every query

---

## 2. Evaluation Approach and Results

### 2.1 Evaluation Set

30 questions covering all 10 policy domains:
- PTO (5 questions)
- Remote Work (4 questions)
- Expense (4 questions)
- Security (3 questions)
- Code of Conduct (2 questions)
- Performance (2 questions)
- Onboarding (2 questions)
- Training (2 questions)
- Benefits (3 questions)
- IT (2 questions)
- Out-of-Scope (1 question)

### 2.2 Metrics

| Metric | Definition | Score |
|--------|-----------|-------|
| **Groundedness** | % of answers where at least one source was retrieved and cited | 100.0% |
| **Citation Accuracy** | % of answers where the cited sources match the expected policy category | 100.0% |
| **Partial Match** | % of answers containing key terms from the gold answer | 96.7% |
| **Latency p50** | Median end-to-end response time | 2.760s |
| **Latency p95** | 95th percentile response time | 5.134s |

*Note: Actual scores are generated by running `python rag/evaluator.py` and saved to `eval/results.md`.*

### 2.3 Out-of-Scope Detection

The system correctly refuses to answer questions unrelated to company policy (e.g., "How do I book a vacation on the moon?") by detecting low relevance scores in retrieved chunks and following the system prompt's instruction to decline gracefully.

### 2.4 Limitations

- With only 10 synthetic documents, the corpus is small; scaling to larger policy sets will require retuning chunking and retrieval thresholds
- Current evaluation uses a deterministic lexical overlap check for partial-match scoring, which is practical but not equivalent to human grading
- Groq free-tier limits can constrain repeated large evaluation runs and ablation sweeps

### 2.5 Potential Ablations (Future Work)

| Ablation | Variants | Expected Impact |
|----------|---------|----------------|
| Chunk size | 300, 500, 750 tokens | Smaller = more precise but may split context |
| Top-k | 3, 5, 8 | Higher k = more context but slower |
| Embedding model | MiniLM vs BGE-large vs API embeddings | Larger or domain-tuned models may improve semantic understanding |
| LLM temperature | 0, 0.1, 0.3 | Higher = more natural but less grounded |
