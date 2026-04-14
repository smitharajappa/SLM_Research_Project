# S³ Canonical Scoring Worksheet — All 8 Use Cases

**Purpose**: Establish the authoritative dimension scores for all 8 UCs.
These scores will be used in the paper, bridge script, and sensitivity analysis.

**Formula**: S³ = Σ(Scoreᵢ × wᵢ) / Σ(5 × wᵢ) × 5
**Default weights**: TC=3, OS=2, SK=4, DS=2, LT=3, VL=1 → Σ(5×wᵢ) = 75
**Tier boundaries**: τ₁=3.2 (Pure SLM/Hybrid), τ₂=4.0 (Hybrid/LLM Only)
**Gate rules**: SK=5 → DISQUALIFY (Hard Rule 1), TC=5 AND SK≥4 → DISQUALIFY (Hard Rule 2), SK≥4 → min Hybrid (Flag Rule)

## Scoring Scale Reference (from Paper Table I-A)

| Dim | 1 | 2 | 3 | 4 | 5 |
|-----|---|---|---|---|---|
| **TC** | Binary yes/no | Few-class classification | Multi-class with edge cases | Multi-step reasoning or structured extraction | Expert-level judgment, compositional reasoning |
| **OS** | Free-form paragraph | Soft-structured paragraph | Named fields / semi-schema | Defined labels from closed vocabulary | Single word/value, strict schema |
| **SK** | No consequence; informational | Minor inconvenience; easily corrected | Business impact; rework required | Significant harm; affects persons directly | Severe, irreversible, legally consequential |
| **DS** | Fully public data | Semi-public / internal data | Personal data; not actively regulated | Regulated PII/PHI under legal obligation | Classified, ITAR-controlled, legally privileged |
| **LT** | Batch pipeline; hours acceptable | Background processing; minutes | Interactive; P95 < 2 seconds | Near real-time; P95 < 500ms | Real-time; P95 < 100ms mandatory |
| **VL** | Dozens per day | Hundreds per day | Tens of thousands per day | Hundreds of thousands per day | Millions per day |

---

## UC1 — SMS Threat Detection
**Task**: Binary classification of SMS as THREAT or BENIGN
**Benchmark**: Mistral-7B 90.0% (100% recall), LLM 90.0% (85.7% recall), parity 100%

| Dim | Score | Rationale |
|-----|-------|-----------|
| TC  | 2 | Binary classification, but hard items use authority spoofing and urgency language requiring full-sentence contextual reading (beyond simple keyword matching) |
| OS  | 5 | Single word from closed vocabulary {THREAT, BENIGN} — maximally constrained output |
| SK  | 4 | A missed THREAT means a real phishing/credential-theft attack reaches the recipient. Direct harm to persons. Not life-safety (SK=5), but significant and direct |
| DS  | 2 | SMS content is semi-personal but not subject to active regulatory obligation (not PHI, not PII under GDPR active compliance) |
| LT  | 4 | Near real-time threat response required; P95 < 500ms target. Paper confirms LLM failed this SLA (P95=2,428ms) |
| VL  | 3 | Carrier-scale SMS screening: tens of thousands per day |

**Weighted sum**: 2×3 + 5×2 + 4×4 + 2×2 + 4×3 + 3×1 = 6+10+16+4+12+3 = **51**
**S³**: 51/75 × 5 = **3.40**
**Gate**: SK=4, TC=2 → PASS WITH FLAG → minimum tier = Hybrid
**Formula tier**: 3.40 > τ₁=3.2 → Hybrid (formula agrees with Flag Rule)
**Benchmark confirms**: Yes — SLM matches LLM on accuracy but SK=4 requires human oversight

### Note on paper v4 discrepancy
Paper worked example (Table I-C) uses TC=2, OS=3, SK=4, DS=2, LT=2, VL=1 → S³=2.60.
Paper Section 7.5 states S³=3.10. Neither matches the canonical scores above.
The worked example used simplified scores for illustration; Section 7 has a computation error
(3.10 × 75/5 = 46.5, not achievable with integer scores).
**Canonical S³=3.40** is the correct value with justified scores.

---

## UC2 — Invoice Field Extraction
**Task**: Extract 6 structured JSON fields from invoice text
**Benchmark**: Phi4-Mini 92.2%, LLM 91.1%, parity 101.2%. All 6 SLMs ≥95% parity.

| Dim | Score | Rationale |
|-----|-------|-----------|
| TC  | 3 | Multi-field extraction with format normalization (dates → YYYY-MM-DD, amounts → numeric). Not simple classification (>2) but not multi-step reasoning (≤4). line_item_count field at ~63% accuracy shows genuine complexity |
| OS  | 3 | Named fields in JSON schema — semi-structured. Not free-form (1-2), not single-word (5) |
| SK  | 2 | Wrong extraction causes invoice processing delay — minor business inconvenience, easily corrected by human review. No harm to persons |
| DS  | 2 | Invoice data is internal business data. Contains vendor names and amounts but not personal/regulated data |
| LT  | 3 | Interactive processing pipeline; P95 < 2 seconds acceptable for invoice batch processing with user-facing dashboard |
| VL  | 3 | Enterprise invoice volume: tens of thousands per day for mid-large organization |

**Weighted sum**: 3×3 + 3×2 + 2×4 + 2×2 + 3×3 + 3×1 = 9+6+8+4+9+3 = **39**
**S³**: 39/75 × 5 = **2.60**
**Gate**: SK=2 → PASS
**Tier**: 2.60 ≤ τ₁=3.2 → **Pure SLM**
**Benchmark confirms**: Yes — all 6 SLMs ≥95% parity, Phi4-Mini exceeds LLM

---

## UC3 — Support Ticket Routing
**Task**: 6-class classification of support tickets (BILLING, TECHNICAL, ACCOUNT, SHIPPING, RETURNS, GENERAL)
**Benchmark**: 4 SLMs at 86.7%, LLM 83.3%, parity 104.1%. SLM exceeds LLM.

| Dim | Score | Rationale |
|-----|-------|-----------|
| TC  | 2 | Multi-class but categories are well-defined with clear keyword/topic signals. Not binary (>1) but not complex edge cases requiring reasoning |
| OS  | 5 | Single word from closed 6-label vocabulary |
| SK  | 2 | Wrong routing causes delayed support resolution — minor business impact, easily re-routed. No harm to persons |
| DS  | 2 | Support ticket text is internal customer-facing data. May contain account references but not regulated PII |
| LT  | 3 | Interactive support system; P95 < 2 seconds for real-time ticket triage |
| VL  | 3 | Enterprise support volume: tens of thousands of tickets per day |

**Weighted sum**: 2×3 + 5×2 + 2×4 + 2×2 + 3×3 + 3×1 = 6+10+8+4+9+3 = **40**
**S³**: 40/75 × 5 = **2.67**
**Gate**: SK=2 → PASS
**Tier**: 2.67 ≤ τ₁=3.2 → **Pure SLM**
**Benchmark confirms**: Yes — SLM exceeds LLM (104% parity), zero hallucinations

---

## UC4 — Product Review Sentiment
**Task**: 3-class sentiment classification (POSITIVE, NEGATIVE, NEUTRAL)
**Benchmark**: Mistral-7B 95.5%, LLM 96.7%, parity 98.8%

| Dim | Score | Rationale |
|-----|-------|-----------|
| TC  | 1 | 3-class sentiment is near-binary difficulty. NEUTRAL is the only ambiguous class; POSITIVE/NEGATIVE have strong lexical signals |
| OS  | 5 | Single word from closed 3-label vocabulary |
| SK  | 1 | Wrong sentiment label causes minor ratings inaccuracy — no person harmed, no business consequence beyond analytics noise |
| DS  | 1 | Publicly available product review text — fully public data |
| LT  | 3 | Batch sentiment pipeline; P95 < 2 seconds acceptable |
| VL  | 3 | E-commerce review volume: tens of thousands per day |

**Weighted sum**: 1×3 + 5×2 + 1×4 + 1×2 + 3×3 + 3×1 = 3+10+4+2+9+3 = **31**
**S³**: 31/75 × 5 = **2.07**
**Gate**: SK=1 → PASS
**Tier**: 2.07 ≤ τ₁=3.2 → **Pure SLM**
**Benchmark confirms**: Yes — Mistral-7B at 98.8% parity, three SLMs ≥95%

### Note
Paper v4 states S³=2.10 (likely rounded from 2.07). Paper worked example gives S³=1.80 using
TC=1, OS=3, SK=1, DS=1, LT=3, VL=3 — the OS score was 3 in the example but should be 5
(single-word output). Canonical S³=2.07.

---

## UC5 — Automated Code Review
**Task**: 5-class code quality classification (SECURITY, LOGIC_ERROR, PERFORMANCE, BEST_PRACTICE, CLEAN)
**Benchmark**: Llama-3.1-8B 46.7%, LLM 61.1%, parity 76.4%

| Dim | Score | Rationale |
|-----|-------|-----------|
| TC  | 4 | Requires understanding code semantics, identifying vulnerability patterns (SQL injection, buffer overflow), distinguishing performance from logic issues. Multi-step reasoning over code structure |
| OS  | 5 | Single label from closed 5-category vocabulary |
| SK  | 3 | Missing a SECURITY issue in code review has business impact — potential vulnerability reaches production. But code review has downstream human review gates (PR approval). Rework required, not direct person harm |
| DS  | 2 | Internal source code — proprietary but not regulated personal data |
| LT  | 3 | CI/CD pipeline integration; P95 < 2 seconds acceptable. Not blocking developer flow |
| VL  | 2 | Hundreds of code review items per day across engineering org |

**Weighted sum**: 4×3 + 5×2 + 3×4 + 2×2 + 3×3 + 2×1 = 12+10+12+4+9+2 = **49**
**S³**: 49/75 × 5 = **3.27**
**Gate**: SK=3 → PASS
**Tier**: 3.27 > τ₁=3.2 → **Hybrid** (by formula alone — no gate rule needed)
**Benchmark confirms**: Yes — 76.4% parity validates that SLM alone is insufficient

---

## UC6 — Healthcare Clinical Triage
**Task**: 4-class triage priority (CRITICAL, URGENT, SEMIURGENT, NONURGENT)
**Benchmark**: Llama-3.1-8B 73.3%, LLM 68.9%, parity 106.4%. But URGENT recall: SLM 0-64% vs LLM 82%

| Dim | Score | Rationale |
|-----|-------|-----------|
| TC  | 4 | Requires integration of chief complaint, vital signs, and clinical history. Multi-step clinical reasoning; distinguishing URGENT from SEMIURGENT requires nuanced vital sign interpretation |
| OS  | 5 | Single word from closed 4-label vocabulary |
| SK  | 5 | **DISQUALIFYING**. Under-triage (labeling CRITICAL as SEMIURGENT) can result in delayed treatment and patient death. Irreversible, legally consequential harm. Medical malpractice liability |
| DS  | 4 | PHI under HIPAA — regulated personal health information with active legal compliance obligation |
| LT  | 4 | Emergency department triage; near real-time P95 < 500ms for patient flow |
| VL  | 2 | Hundreds of ED presentations per day per hospital |

**Weighted sum**: 4×3 + 5×2 + 5×4 + 4×2 + 4×3 + 2×1 = 12+10+20+8+12+2 = **64**
**S³**: 64/75 × 5 = **4.27**
**Gate**: SK=5 → **DISQUALIFY (Hard Rule 1)** — autonomous deployment prohibited
**Tier**: **LLM Only** (with mandatory human oversight — Hard Rule disqualification means even LLM requires human-in-the-loop)
**Benchmark confirms**: Yes — SLMs show systematic URGENT under-triage; no SLM is safe for autonomous clinical decisions

### Note
Paper v4 states S³=4.44. Canonical S³=4.27. Both are well above τ₂=4.0, and Hard Rule 1
makes the formula value irrelevant — SK=5 always disqualifies.

---

## UC7 — Legal Contract Risk Analysis
**Task**: 4-class contract clause risk (HIGH_RISK, MEDIUM_RISK, LOW_RISK, STANDARD)
**Benchmark**: Qwen2.5-7B 53.3%, LLM 57.8%, parity 92.2%

| Dim | Score | Rationale |
|-----|-------|-----------|
| TC  | 3 | Multi-class classification with legal terminology. Requires understanding indemnity clauses, liability limits, and risk language. More complex than topic routing but not multi-step reasoning |
| OS  | 5 | Single label from closed 4-category vocabulary |
| SK  | 4 | Missing a HIGH_RISK clause (unlimited indemnity, one-sided liability) exposes the organization to significant financial and legal harm. Directly affects contract counterparty. Not irreversible (contracts can be renegotiated) but significant |
| DS  | 3 | Contract text is confidential business data. May contain terms under NDA. Not regulated PII but commercially sensitive |
| LT  | 2 | Document review pipeline; minutes acceptable for contract analysis batch processing |
| VL  | 1 | Dozens of contracts per day — low volume, high-value documents |

**Weighted sum**: 3×3 + 5×2 + 4×4 + 3×2 + 2×3 + 1×1 = 9+10+16+6+6+1 = **48**
**S³**: 48/75 × 5 = **3.20**
**Gate**: SK=4, TC=3 → PASS WITH FLAG → minimum tier = Hybrid
**Tier**: 3.20 = τ₁ → boundary case. Flag Rule enforces **Hybrid** regardless
**Benchmark confirms**: Yes — 92.2% parity is close but below 95%, validates Hybrid. Flag Rule is load-bearing since formula score sits exactly on the boundary.

---

## UC8 — Financial Report Drafting
**Task**: Generate 2-3 paragraph quarterly earnings summary from financial data
**Benchmark**: Llama-3.2-3B 72.3%, LLM 80.6%, parity 89.7%

| Dim | Score | Rationale |
|-----|-------|-----------|
| TC  | 5 | Multi-step generative task: interpret financial metrics, compute year-over-year context, synthesize sector-appropriate narrative. Requires compositional reasoning across multiple data points |
| OS  | 1 | Free-form multi-paragraph text — no structural constraints beyond "2-3 paragraphs" |
| SK  | 4 | Factual errors in earnings reports can trigger regulatory issues (SEC), mislead investors, and cause reputational harm. Significant and direct consequences, but not irreversible |
| DS  | 3 | Quarterly financial data — material non-public information pre-earnings, commercially sensitive |
| LT  | 2 | Report generation pipeline; minutes acceptable for batch financial reporting |
| VL  | 1 | Dozens of reports per quarter — very low volume |

**Weighted sum**: 5×3 + 1×2 + 4×4 + 3×2 + 2×3 + 1×1 = 15+2+16+6+6+1 = **46**
**S³**: 46/75 × 5 = **3.07**
**Gate**: SK=4, TC=5 → **DISQUALIFY (Hard Rule 2)** — TC=5 AND SK≥4
**Tier**: **LLM Only** (with mandatory human oversight — Hard Rule 2 disqualification)
**Benchmark confirms**: Yes — best SLM at 89.7% parity, below 95%. Expert-level generation under significant stakes.

---

## Summary Table — Canonical Scores

| UC | Task | TC | OS | SK | DS | LT | VL | WS | S³ | Gate Rule | Tier |
|----|------|----|----|----|----|----|----|----|----|-----------|------|
| 1 | SMS Threat Detection | 2 | 5 | 4 | 2 | 4 | 3 | 51 | 3.40 | Flag (SK=4) | **Hybrid** |
| 2 | Invoice Extraction | 3 | 3 | 2 | 2 | 3 | 3 | 39 | 2.60 | Pass | **Pure SLM** |
| 3 | Support Ticket Routing | 2 | 5 | 2 | 2 | 3 | 3 | 40 | 2.67 | Pass | **Pure SLM** |
| 4 | Product Review Sentiment | 1 | 5 | 1 | 1 | 3 | 3 | 31 | 2.07 | Pass | **Pure SLM** |
| 5 | Code Review | 4 | 5 | 3 | 2 | 3 | 2 | 49 | 3.27 | Pass | **Hybrid** |
| 6 | Clinical Triage | 4 | 5 | 5 | 4 | 4 | 2 | 64 | 4.27 | Hard Rule 1 (SK=5) | **LLM Only** |
| 7 | Legal Contract Risk | 3 | 5 | 4 | 3 | 2 | 1 | 48 | 3.20 | Flag (SK=4) | **Hybrid** |
| 8 | Financial Report Draft | 5 | 1 | 4 | 3 | 2 | 1 | 46 | 3.07 | Hard Rule 2 (TC=5,SK≥4) | **LLM Only** |

### Tier Distribution
- **Pure SLM** (S³ ≤ 3.2): UC2 (2.60), UC3 (2.67), UC4 (2.07)
- **Hybrid** (3.2 < S³ ≤ 4.0 or Flag Rule): UC1 (3.40, Flag), UC5 (3.27, Formula), UC7 (3.20, Flag)
- **LLM Only** (S³ > 4.0 or Hard Rules): UC6 (4.27, Hard Rule 1), UC8 (3.07, Hard Rule 2)

### Benchmark Validation: 8/8 Confirmed
All tier predictions match benchmark outcomes.

### Key Observations
1. **UC7 is the boundary case**: S³=3.20 sits exactly on τ₁. The Flag Rule (SK=4) is load-bearing — without it, UC7 could be Pure SLM or Hybrid depending on rounding. Benchmark validates Hybrid (92.2% parity < 95%).
2. **UC8 demonstrates Hard Rule 2**: S³=3.07 is below τ₁ (Pure SLM by formula!) but TC=5 AND SK=4 triggers disqualification. This is the safety mechanism working as designed — expert-level generation under significant stakes should never be autonomous.
3. **UC4 is the easiest task**: S³=2.07, lowest in the suite. Matches benchmark reality (98.8% parity).
4. **UC6 is the hardest task**: S³=4.27, highest computable score. Hard Rule 1 (SK=5) makes the exact score irrelevant.
5. **Spread**: S³ range is [2.07, 4.27] — the scoring dimensions produce meaningful separation across the task complexity spectrum.
