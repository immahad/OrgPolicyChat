# AI Tooling Documentation

## Tools Used

### 1. Claude (Anthropic) — Primary Development Assistant

**How it was used:**
- Generated all 10 synthetic company policy documents (PTO, remote work, expense, security, code of conduct, performance, IT, onboarding, training, benefits)
- Wrote the core RAG pipeline code (`ingest.py`, `retriever.py`)
- Designed and generated the Flask application (`app.py`)
- Built the full chat UI (`templates/index.html`) with CSS animations and JavaScript
- Wrote the evaluation framework (`evaluator.py`)
- Generated all 30 evaluation questions with gold answers
- Wrote all documentation (README.md, design-and-evaluation.md, this file)
- Helped debug LangChain API changes between versions

**What worked well:**
- Extremely fast at generating complete, well-structured policy documents with realistic detail
- Generated production-quality Python code with proper error handling, logging, and environment variable management
- Understood the project rubric requirements and produced code that specifically addressed each grading criterion
- Helped reason through architecture decisions (embedding model choice, chunking strategy, prompt design)

**What didn't work as well:**
- LangChain's API changes frequently between minor versions; some generated import paths required manual correction (e.g., `langchain_community` vs `langchain` imports)
- Initial prompt template syntax needed adjustments for the specific LangChain version in use

---

### 2. GitHub Copilot — In-Editor Autocomplete

**How it was used:**
- Autocompleted repetitive boilerplate (e.g., Flask route patterns, pytest fixture setup)
- Suggested error handling patterns for API calls
- Helped fill in type hints and docstrings

**What worked well:**
- Fast inline suggestions for standard patterns (Flask test client setup, JSON handling)
- Reduced time spent on repetitive code

**What didn't work as well:**
- Suggestions for LangChain RAG patterns were sometimes outdated due to the library's rapid evolution
- Required manual review for all security-sensitive code (API key handling, input validation)

---

### 3. Groq Console — LLM Testing

**How it was used:**
- Tested prompt templates interactively before embedding them in code
- Verified that the system prompt guardrails (out-of-scope refusal, citation requirement) worked correctly
- Benchmarked latency of different Groq models to select the best free-tier option

**What worked well:**
- Playground made it easy to iterate on the system prompt quickly
- Confirmed that `llama-3.3-70b-versatile` outperformed smaller models for policy Q&A accuracy

---

## Summary

AI tools accelerated the project significantly — particularly for generating the policy corpus (which would have taken hours manually) and for scaffolding the RAG pipeline. All AI-generated code was reviewed, tested, and refined manually. The architecture decisions, evaluation design, and integration work were done with human judgment guided by AI suggestions.
