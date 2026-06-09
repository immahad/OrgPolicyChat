# RAG Evaluation Results

## Summary

| Metric | Score |
|--------|-------|
| **Groundedness** | 100.0% |
| **Citation Accuracy** | 100.0% |
| **Partial Match (Gold)** | 96.7% |
| **Latency p50** | 2.228s |
| **Latency p95** | 3.168s |
| **Latency avg** | 3.037s |
| **Questions evaluated** | 30 |

## Per-Question Results

| ID | Category | Grounded | Citation | Partial Match | Latency | Sources |
|----|----------|----------|----------|---------------|---------|---------|
| Q01 | PTO | ✅ | ✅ | ✅ | 23.596s | pto-policy.md, health-benefits-policy.md, onboarding-policy.md |
| Q02 | PTO | ✅ | ✅ | ✅ | 3.02s | pto-policy.md |
| Q03 | PTO | ✅ | ✅ | ✅ | 2.811s | remote-work-policy.md, pto-policy.md, onboarding-policy.md, health-benefits-policy.md |
| Q04 | PTO | ✅ | ✅ | ✅ | 2.611s | pto-policy.md, training-policy.md, onboarding-policy.md |
| Q05 | PTO | ✅ | ✅ | ✅ | 2.188s | pto-policy.md, performance-policy.md, remote-work-policy.md, expense-policy.md |
| Q06 | RemoteWork | ✅ | ✅ | ✅ | 2.206s | remote-work-policy.md, health-benefits-policy.md |
| Q07 | RemoteWork | ✅ | ✅ | ✅ | 1.433s | remote-work-policy.md, it-policy.md |
| Q08 | RemoteWork | ✅ | ✅ | ✅ | 3.168s | expense-policy.md, remote-work-policy.md, health-benefits-policy.md |
| Q09 | RemoteWork | ✅ | ✅ | ✅ | 2.251s | remote-work-policy.md, health-benefits-policy.md, training-policy.md |
| Q10 | Expense | ✅ | ✅ | ✅ | 2.1s | expense-policy.md, performance-policy.md |
| Q11 | Expense | ✅ | ✅ | ✅ | 2.185s | expense-policy.md |
| Q12 | Expense | ✅ | ✅ | ✅ | 2.075s | expense-policy.md, training-policy.md, health-benefits-policy.md |
| Q13 | Expense | ✅ | ✅ | ✅ | 2.333s | expense-policy.md, training-policy.md |
| Q14 | Security | ✅ | ✅ | ✅ | 2.461s | security-policy.md, remote-work-policy.md |
| Q15 | Security | ✅ | ✅ | ✅ | 2.926s | security-policy.md, remote-work-policy.md, it-policy.md, health-benefits-policy.md |
| Q16 | Security | ✅ | ✅ | ✅ | 2.379s | security-policy.md, it-policy.md, remote-work-policy.md, pto-policy.md |
| Q17 | CodeOfConduct | ✅ | ✅ | ✅ | 2.426s | code-of-conduct.md, expense-policy.md |
| Q18 | Performance | ✅ | ✅ | ❌ | 2.575s | performance-policy.md, code-of-conduct.md |
| Q19 | Performance | ✅ | ✅ | ✅ | 1.977s | performance-policy.md |
| Q20 | Onboarding | ✅ | ✅ | ✅ | 2.023s | onboarding-policy.md, pto-policy.md, performance-policy.md |
| Q21 | Onboarding | ✅ | ✅ | ✅ | 2.427s | onboarding-policy.md, health-benefits-policy.md |
| Q22 | Training | ✅ | ✅ | ✅ | 2.171s | training-policy.md, expense-policy.md |
| Q23 | Training | ✅ | ✅ | ✅ | 2.089s | training-policy.md |
| Q24 | Benefits | ✅ | ✅ | ✅ | 2.199s | health-benefits-policy.md, performance-policy.md |
| Q25 | Benefits | ✅ | ✅ | ✅ | 2.092s | health-benefits-policy.md, expense-policy.md, training-policy.md |
| Q26 | Benefits | ✅ | ✅ | ✅ | 2.088s | health-benefits-policy.md, training-policy.md |
| Q27 | IT | ✅ | ✅ | ✅ | 2.526s | it-policy.md, remote-work-policy.md, security-policy.md, onboarding-policy.md |
| Q28 | IT | ✅ | ✅ | ✅ | 2.205s | remote-work-policy.md, it-policy.md, security-policy.md |
| Q29 | CodeOfConduct | ✅ | ✅ | ✅ | 2.144s | code-of-conduct.md, security-policy.md |
| Q30 | OutOfScope | ✅ | ✅ | ✅ | 2.426s | expense-policy.md |

## Methodology

- **Groundedness**: Verified by checking that at least one source document was retrieved and cited.
- **Citation Accuracy**: Verified by confirming the retrieved sources match the expected policy document category for each question.
- **Partial Match**: Key terms from the gold answer checked against the generated answer.
- **Latency**: Measured end-to-end from request receipt to answer delivery using `time.perf_counter()`.
- Evaluation set: 30 questions covering PTO, remote work, expenses, security, conduct, performance, onboarding, training, benefits, IT, and out-of-scope detection.
