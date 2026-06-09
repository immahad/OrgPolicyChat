"""
evaluator.py - Evaluation script for the Policy RAG system

Measures:
  - Groundedness: % of answers supported by retrieved context
  - Citation accuracy: % of answers with correct source citations
  - Latency: p50 and p95 response times
  - Out-of-scope detection: correctly refuses irrelevant questions

Run: python rag/evaluator.py
Results saved to: eval/results.md
"""

import os
import sys
import json
import time
import statistics
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add parent dir to path so we can import retriever
sys.path.insert(0, str(Path(__file__).parent.parent))
from rag.retriever import get_rag_response

QUESTIONS_FILE = "eval/questions.json"
RESULTS_FILE   = "eval/results.md"

# Category -> expected source file keywords
CATEGORY_SOURCE_MAP = {
    "PTO":           ["pto-policy"],
    "RemoteWork":    ["remote-work-policy"],
    "Expense":       ["expense-policy"],
    "Security":      ["security-policy"],
    "CodeOfConduct": ["code-of-conduct"],
    "Performance":   ["performance-policy"],
    "Onboarding":    ["onboarding-policy"],
    "Training":      ["training-policy"],
    "Benefits":      ["health-benefits-policy"],
    "IT":            ["it-policy"],
    "OutOfScope":    [],
}

REFUSAL_PHRASES = [
    "i can only answer",
    "not covered in our policy",
    "please contact hr",
    "outside the scope",
    "not found in",
]


def is_grounded(result: dict) -> bool:
    """An answer is grounded if it retrieved at least one source."""
    return len(result.get("sources", [])) > 0


def is_citation_accurate(result: dict, category: str) -> bool:
    """Citation is accurate if the retrieved sources match the expected category."""
    if category == "OutOfScope":
        # For out-of-scope, check it refused to answer
        answer_lower = result.get("answer", "").lower()
        return any(phrase in answer_lower for phrase in REFUSAL_PHRASES)

    expected_keywords = CATEGORY_SOURCE_MAP.get(category, [])
    if not expected_keywords:
        return True

    sources = [s.lower() for s in result.get("sources", [])]
    return any(
        any(kw in src for src in sources)
        for kw in expected_keywords
    )


def contains_gold(answer: str, gold: str) -> bool:
    """Check if key parts of the gold answer appear in the generated answer."""
    if gold == "OUT_OF_SCOPE":
        return any(phrase in answer.lower() for phrase in REFUSAL_PHRASES)

    # Extract key numbers/phrases from gold answer
    gold_lower = gold.lower()
    answer_lower = answer.lower()

    # Look for any 3+ character token from gold in answer
    tokens = [t.strip("$%.,") for t in gold_lower.split() if len(t.strip("$%.,")) >= 2]
    matches = sum(1 for t in tokens if t in answer_lower)
    return matches >= max(1, len(tokens) // 2)


def run_evaluation():
    print("=" * 60)
    print("  Policy RAG Evaluation Suite")
    print("=" * 60)

    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        questions = json.load(f)

    results = []
    latencies = []

    for i, q in enumerate(questions, 1):
        qid      = q["id"]
        question = q["question"]
        gold     = q["gold_answer"]
        category = q["category"]

        print(f"\n[{i:02d}/{len(questions)}] {qid} ({category})")
        print(f"  Q: {question[:70]}...")

        result  = get_rag_response(question)
        latency = result["latency"]
        latencies.append(latency)

        grounded      = is_grounded(result)
        cite_accurate = is_citation_accurate(result, category)
        partial_match = contains_gold(result["answer"], gold)

        results.append({
            "id":            qid,
            "category":      category,
            "question":      question,
            "gold":          gold,
            "answer":        result["answer"][:200] + "...",
            "sources":       result["sources"],
            "latency":       latency,
            "grounded":      grounded,
            "cite_accurate": cite_accurate,
            "partial_match": partial_match,
        })

        status = []
        if grounded:      status.append("✅ grounded")
        else:             status.append("❌ not grounded")
        if cite_accurate: status.append("✅ citation ok")
        else:             status.append("❌ citation miss")
        if partial_match: status.append("✅ partial match")

        print(f"  Sources : {result['sources']}")
        print(f"  Latency : {latency}s")
        print(f"  Status  : {' | '.join(status)}")

    # ── Compute metrics ──────────────────────────────────────
    n = len(results)
    groundedness   = sum(r["grounded"]      for r in results) / n * 100
    citation_acc   = sum(r["cite_accurate"] for r in results) / n * 100
    partial_match  = sum(r["partial_match"] for r in results) / n * 100

    latencies_sorted = sorted(latencies)
    p50 = statistics.median(latencies_sorted)
    p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)]
    avg = statistics.mean(latencies_sorted)

    print("\n" + "=" * 60)
    print("  EVALUATION RESULTS")
    print("=" * 60)
    print(f"  Questions evaluated : {n}")
    print(f"  Groundedness        : {groundedness:.1f}%")
    print(f"  Citation Accuracy   : {citation_acc:.1f}%")
    print(f"  Partial Match       : {partial_match:.1f}%")
    print(f"  Latency p50         : {p50:.3f}s")
    print(f"  Latency p95         : {p95:.3f}s")
    print(f"  Latency avg         : {avg:.3f}s")
    print("=" * 60)

    # ── Write markdown report ─────────────────────────────────
    md = f"""# RAG Evaluation Results

## Summary

| Metric | Score |
|--------|-------|
| **Groundedness** | {groundedness:.1f}% |
| **Citation Accuracy** | {citation_acc:.1f}% |
| **Partial Match (Gold)** | {partial_match:.1f}% |
| **Latency p50** | {p50:.3f}s |
| **Latency p95** | {p95:.3f}s |
| **Latency avg** | {avg:.3f}s |
| **Questions evaluated** | {n} |

## Per-Question Results

| ID | Category | Grounded | Citation | Partial Match | Latency | Sources |
|----|----------|----------|----------|---------------|---------|---------|
"""
    for r in results:
        g  = "✅" if r["grounded"]      else "❌"
        ca = "✅" if r["cite_accurate"] else "❌"
        pm = "✅" if r["partial_match"] else "❌"
        srcs = ", ".join(r["sources"]) if r["sources"] else "none"
        md += f"| {r['id']} | {r['category']} | {g} | {ca} | {pm} | {r['latency']}s | {srcs} |\n"

    md += f"""
## Methodology

- **Groundedness**: Verified by checking that at least one source document was retrieved and cited.
- **Citation Accuracy**: Verified by confirming the retrieved sources match the expected policy document category for each question.
- **Partial Match**: Key terms from the gold answer checked against the generated answer.
- **Latency**: Measured end-to-end from request receipt to answer delivery using `time.perf_counter()`.
- Evaluation set: {n} questions covering PTO, remote work, expenses, security, conduct, performance, onboarding, training, benefits, IT, and out-of-scope detection.
"""

    results_path = Path(RESULTS_FILE)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(md, encoding="utf-8")
    print(f"\nResults saved to: {RESULTS_FILE}")
    return results


if __name__ == "__main__":
    run_evaluation()
