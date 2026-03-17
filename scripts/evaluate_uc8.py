# -*- coding: utf-8 -*-
"""
evaluate_uc8.py
===============
S3 Research Project -- UC8 Evaluator
Use Case  : Financial Report Drafting
S3 Score  : 3.80  |  Predicted tier: Hybrid

Evaluation: LLM-as-Judge (Llama-3.3-70B via Groq)
Each output scored on D1 Accuracy / D2 Depth / D3 Tone / D4 Completeness (1-5 each).
Composite = mean(D1-D4) normalised 0-100%.
Parity threshold: SLM composite >= 95% of LLM composite.

Rate-limit handling:
  - 3s delay between every judge call  (~20 RPM, well under Groq free limit)
  - Retry on 429: waits 20s / 60s / 120s before giving up
  - Corrupted judge responses fall back to score=3 (not 0)

Pre-registered hypotheses:
  H8.1 -- >= 4/6 SLMs reach >= 95% of LLM composite score
  H8.2 -- >= 4/6 SLMs have P95 latency < LLM P95
  H8.3 -- hard items score lower than easy items for all SLMs
  H8.4 -- Financial sector produces lowest relative SLM scores
"""

import csv, json, os, sys, time, argparse, statistics
from datetime import datetime
from collections import defaultdict
import requests

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
GOLD_SET_PATH   = "data/gold_sets/uc8_financial_report_drafting.csv"
RAW_OUTPUT_DIR  = "data/raw_outputs"
EVAL_OUTPUT_DIR = "evaluation"
os.makedirs(EVAL_OUTPUT_DIR, exist_ok=True)

GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
JUDGE_MODEL   = "llama-3.3-70b-versatile"

JUDGE_INTER_CALL_DELAY = 3.0          # seconds between every judge call
JUDGE_RETRY_WAITS      = [20, 60, 120]  # wait on consecutive 429s

PARITY_THRESHOLD  = 0.95
PARITY_MIN_MODELS = 4

LLM_NAME  = "Llama-3.3-70B"
SLM_NAMES = ["Llama-3.2-3B", "Phi4-Mini", "Gemma3-4B",
             "Qwen2.5-7B", "Mistral-7B", "Llama-3.1-8B"]

EVAL_FIELDNAMES = [
    "model_name", "tier", "params",
    "item_id", "sector", "difficulty", "seed",
    "d1_accuracy", "d2_depth", "d3_tone", "d4_completeness",
    "composite_raw", "composite_pct", "latency_ms", "judge_rationale"
]

# ---------------------------------------------------------------------------
# JUDGE PROMPT
# ---------------------------------------------------------------------------
JUDGE_SYSTEM = (
    "You are an expert financial analyst evaluating AI-generated financial report summaries.\n\n"
    "Score on four dimensions (1-5 each):\n\n"
    "D1 Numerical Accuracy\n"
    "  5=All key figures correct with context | 4=Minor omissions, no errors\n"
    "  3=Some correct, some omitted | 2=Several incorrect | 1=Wrong/fabricated\n\n"
    "D2 Analytical Depth\n"
    "  5=Identifies trends and drivers | 4=Some interpretation\n"
    "  3=Mostly restates numbers | 2=Pure regurgitation | 1=Less than input\n\n"
    "D3 Professional Tone\n"
    "  5=Polished earnings-report register | 4=Professional, minor issues\n"
    "  3=Acceptable but inconsistent | 2=Informal/verbose | 1=Incoherent\n\n"
    "D4 Completeness\n"
    "  5=>80% gold criteria covered | 4=60-80% | 3=40-60% | 2=20-40% | 1=<20%\n\n"
    "Respond ONLY with valid JSON — no prose, no markdown fences:\n"
    '{"d1_accuracy":<1-5>,"d2_depth":<1-5>,"d3_tone":<1-5>,"d4_completeness":<1-5>,'
    '"rationale":"<one sentence>"}'
)


def build_judge_prompt(item: dict, model_output: str) -> str:
    fd = json.loads(item["financial_data_json"])
    return (
        f"COMPANY: {item['company_name']}  PERIOD: {item['period']}  "
        f"SECTOR: {item['sector']}  DIFFICULTY: {item['difficulty']}\n\n"
        f"FINANCIAL DATA:\n{json.dumps(fd, indent=2)}\n\n"
        f"GOLD CHECKLIST (key points a good summary must cover):\n"
        + "\n".join(f"  - {c.strip()}" for c in item["gold_criteria"].split("|"))
        + f"\n\nAI SUMMARY TO EVALUATE:\n{model_output}\n\n"
        "Return JSON scores only."
    )


# ---------------------------------------------------------------------------
# JUDGE CALL
# ---------------------------------------------------------------------------

def call_judge(item: dict, model_output: str) -> dict:
    """Call Llama-3.3-70B via Groq as judge with retry on 429."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set.")
    url = f"{GROQ_BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": JUDGE_MODEL,
        "messages": [
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user",   "content": build_judge_prompt(item, model_output)}
        ],
        "temperature": 0.0,
        "max_tokens": 200,
    }
    for attempt, wait in enumerate(JUDGE_RETRY_WAITS):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 429:
                print(f"      [429] Rate limit — waiting {wait}s (attempt {attempt+1}/{len(JUDGE_RETRY_WAITS)})...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            text = resp.json()["choices"][0]["message"]["content"].strip()
            # Strip any accidental markdown fences
            if "```" in text:
                text = text.split("```")[1].lstrip("json").strip()
            parsed = json.loads(text)
            return {
                "d1_accuracy":     max(1, min(5, int(parsed.get("d1_accuracy", 3)))),
                "d2_depth":        max(1, min(5, int(parsed.get("d2_depth", 3)))),
                "d3_tone":         max(1, min(5, int(parsed.get("d3_tone", 3)))),
                "d4_completeness": max(1, min(5, int(parsed.get("d4_completeness", 3)))),
                "rationale":       str(parsed.get("rationale", ""))[:200]
            }
        except json.JSONDecodeError:
            # Judge returned non-JSON — fall back gracefully
            print(f"      [WARN] Judge returned non-JSON — using score=3 fallback")
            return {"d1_accuracy": 3, "d2_depth": 3, "d3_tone": 3,
                    "d4_completeness": 3, "rationale": "PARSE_ERROR"}
        except Exception as e:
            if attempt < len(JUDGE_RETRY_WAITS) - 1:
                print(f"      [ERR] {e} — waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"      [FAIL] Judge failed after all retries: {e}")
                return {"d1_accuracy": 3, "d2_depth": 3, "d3_tone": 3,
                        "d4_completeness": 3, "rationale": f"JUDGE_ERROR: {str(e)[:80]}"}
    return {"d1_accuracy": 3, "d2_depth": 3, "d3_tone": 3,
            "d4_completeness": 3, "rationale": "JUDGE_ERROR: exhausted retries"}


def composite_pct(d1, d2, d3, d4) -> float:
    return round((((d1+d2+d3+d4)/4.0) - 1) / 4.0 * 100, 2)  # 1->0%, 5->100%


# ---------------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------------

def load_gold_set() -> dict:
    gold = {}
    with open(GOLD_SET_PATH, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["split"] == "test":
                gold[row["item_id"]] = row
    return gold


def latest_raw_file() -> str:
    files = sorted([f for f in os.listdir(RAW_OUTPUT_DIR)
                    if f.startswith("uc8_raw_") and f.endswith(".csv")])
    if not files:
        print("ERROR: No UC8 raw output file found. Run run_benchmark_uc8.py first.")
        sys.exit(1)
    return os.path.join(RAW_OUTPUT_DIR, files[-1])


def load_raw(raw_path: str) -> list:
    rows = []
    with open(raw_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("error") and row.get("is_valid", "").lower() == "true":
                rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# EVALUATE
# ---------------------------------------------------------------------------

def majority_output(runs: list) -> str:
    """For generation tasks, use seed=42 as canonical output."""
    for r in runs:
        if int(r["seed"]) == 42:
            return r["raw_output"]
    return runs[0]["raw_output"] if runs else ""


def evaluate(raw_path: str, use_judge: bool = True):
    gold     = load_gold_set()
    raw_rows = load_raw(raw_path)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    eval_csv = os.path.join(EVAL_OUTPUT_DIR, f"uc8_evaluation_{ts}.csv")
    sum_csv  = os.path.join(EVAL_OUTPUT_DIR, f"uc8_summary_{ts}.csv")
    rpt_path = os.path.join(EVAL_OUTPUT_DIR, f"uc8_report_{ts}.txt")

    # Group: {model: {item_id: [rows]}}
    grouped   = defaultdict(lambda: defaultdict(list))
    latencies = defaultdict(list)
    for row in raw_rows:
        grouped[row["model_name"]][row["item_id"]].append(row)
        latencies[row["model_name"]].append(float(row["latency_ms"]))

    MODEL_PARAMS = {"Llama-3.2-3B":"3B","Phi4-Mini":"3.8B","Gemma3-4B":"4B",
                    "Qwen2.5-7B":"7B","Mistral-7B":"7B","Llama-3.1-8B":"8B","Llama-3.3-70B":"70B"}
    MODEL_TIER  = {m:"SLM" for m in SLM_NAMES}
    MODEL_TIER[LLM_NAME] = "LLM"

    print()
    print("=" * 68)
    print("  UC8 Evaluator — Financial Report Drafting")
    print(f"  Raw   : {raw_path}")
    print(f"  Judge : {JUDGE_MODEL} ({'LIVE' if use_judge else 'MOCK'})")
    print(f"  Delay : {JUDGE_INTER_CALL_DELAY}s between calls | 429 waits: {JUDGE_RETRY_WAITS}s")
    print("=" * 68)

    eval_rows       = []
    scores_by_model = defaultdict(list)
    model_order     = [LLM_NAME] + SLM_NAMES

    for model_name in model_order:
        if model_name not in grouped:
            print(f"  SKIP: no rows for {model_name}")
            continue
        print(f"\n  Judging {model_name} ...")
        for item_id in sorted(grouped[model_name].keys()):
            if item_id not in gold:
                continue
            runs      = grouped[model_name][item_id]
            item      = gold[item_id]
            canonical = majority_output(runs)
            avg_lat   = statistics.mean(float(r["latency_ms"]) for r in runs)

            if use_judge:
                scores = call_judge(item, canonical)
                time.sleep(JUDGE_INTER_CALL_DELAY)   # paced delay every call
            else:
                scores = {"d1_accuracy":3,"d2_depth":3,"d3_tone":3,
                          "d4_completeness":3,"rationale":"MOCK"}

            comp = composite_pct(scores["d1_accuracy"], scores["d2_depth"],
                                 scores["d3_tone"], scores["d4_completeness"])
            scores_by_model[model_name].append(comp)
            raw_mean = (scores["d1_accuracy"]+scores["d2_depth"]+
                        scores["d3_tone"]+scores["d4_completeness"])/4.0

            eval_rows.append({
                "model_name": model_name,
                "tier": MODEL_TIER.get(model_name,"SLM"),
                "params": MODEL_PARAMS.get(model_name,"?"),
                "item_id": item_id, "sector": item["sector"],
                "difficulty": item["difficulty"], "seed": 42,
                "d1_accuracy": scores["d1_accuracy"], "d2_depth": scores["d2_depth"],
                "d3_tone": scores["d3_tone"], "d4_completeness": scores["d4_completeness"],
                "composite_raw": f"{raw_mean:.2f}", "composite_pct": f"{comp:.1f}",
                "latency_ms": f"{avg_lat:.0f}", "judge_rationale": scores["rationale"]
            })
            print(f"    {item_id}  D1={scores['d1_accuracy']} D2={scores['d2_depth']} "
                  f"D3={scores['d3_tone']} D4={scores['d4_completeness']}  comp={comp:.1f}%")

    # Write eval CSV
    with open(eval_csv, "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=EVAL_FIELDNAMES).writeheader()
        csv.DictWriter(f, fieldnames=EVAL_FIELDNAMES).writerows(eval_rows)

    # -----------------------------------------------------------------------
    # AGGREGATES
    # -----------------------------------------------------------------------
    model_avg = {m: statistics.mean(v) for m,v in scores_by_model.items() if v}
    llm_avg   = model_avg.get(LLM_NAME, 0.0)

    lat_p50, lat_p95 = {}, {}
    for m, lats in latencies.items():
        s = sorted(lats)
        lat_p50[m] = s[int(len(s)*0.50)]
        lat_p95[m] = s[min(int(len(s)*0.95), len(s)-1)]
    llm_p95 = lat_p95.get(LLM_NAME, 9999)

    sector_scores = defaultdict(lambda: defaultdict(list))
    diff_scores   = defaultdict(lambda: defaultdict(list))
    dim_scores    = defaultdict(lambda: defaultdict(list))
    for row in eval_rows:
        sector_scores[row["model_name"]][row["sector"]].append(float(row["composite_pct"]))
        diff_scores[row["model_name"]][row["difficulty"]].append(float(row["composite_pct"]))
        for d in ["d1_accuracy","d2_depth","d3_tone","d4_completeness"]:
            dim_scores[row["model_name"]][d].append(float(row[d]))

    # H8.1
    slm_parity = sum(1 for m in SLM_NAMES
                     if m in model_avg and llm_avg > 0 and model_avg[m]/llm_avg >= PARITY_THRESHOLD)
    h81 = slm_parity >= PARITY_MIN_MODELS

    # H8.2
    lat_below = sum(1 for m in SLM_NAMES if lat_p95.get(m,9999) < llm_p95)
    h82 = lat_below >= PARITY_MIN_MODELS

    # H8.3
    h83 = all(
        statistics.mean(diff_scores[m].get("easy",[0])) > statistics.mean(diff_scores[m].get("hard",[0]))
        for m in SLM_NAMES if m in diff_scores
    )

    # H8.4 — which sector has lowest relative SLM score vs LLM
    sector_rel = defaultdict(list)
    for row in eval_rows:
        if row["model_name"] == LLM_NAME:
            continue
        llm_row = next((r for r in eval_rows
                        if r["model_name"]==LLM_NAME and r["item_id"]==row["item_id"]), None)
        if llm_row and float(llm_row["composite_pct"]) > 0:
            sector_rel[row["sector"]].append(float(row["composite_pct"])/float(llm_row["composite_pct"]))
    avg_rel = {s: statistics.mean(v) for s,v in sector_rel.items() if v}
    lowest_sector = min(avg_rel, key=avg_rel.get) if avg_rel else "N/A"
    h84 = lowest_sector == "Financial"

    tier_verdict = (
        "HYBRID CONFIRMED" if h81 and not all(model_avg.get(m,0)/llm_avg >= 0.99 for m in SLM_NAMES if m in model_avg)
        else "PURE SLM (exceeds prediction)" if h81
        else "LLM ONLY or further review"
    )

    # -----------------------------------------------------------------------
    # REPORT
    # -----------------------------------------------------------------------
    SEP = "=" * 72
    LIN = "-" * 72
    SECTORS = ["Technology","Retail","Healthcare","Manufacturing","Financial"]

    with open(rpt_path, "w", encoding="utf-8") as rpt:
        def w(s=""): rpt.write(s + "\n")

        w(SEP)
        w("  UC8 EVALUATION REPORT — Financial Report Drafting")
        w(f"  Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        w(f"  Pre-reg   : 2026-03-11  |  S3 Score: 3.80  |  Prediction: Hybrid")
        w(f"  Judge     : {JUDGE_MODEL}")
        w(SEP)

        w()
        w("  TABLE 1 — Overall Composite Scores")
        w(LIN)
        w(f"  {'Model':<18} {'Tier':<5} {'Avg%':>7} {'Ratio':>7} {'P50ms':>7} {'P95ms':>7} {'<LLM_P95':>9}")
        w(LIN)
        for m in model_order:
            if m not in model_avg: continue
            avg = model_avg[m]
            rat = avg/llm_avg if llm_avg > 0 else 0
            bl  = "YES" if lat_p95.get(m,9999) < llm_p95 else "NO "
            tag = " <- LLM baseline" if m == LLM_NAME else ""
            w(f"  {m:<18} {MODEL_TIER.get(m,'SLM'):<5} {avg:>6.1f}% {rat:>6.3f} "
              f"{lat_p50.get(m,0):>6.0f} {lat_p95.get(m,0):>6.0f}  {bl:>8}{tag}")
        w(LIN)

        w()
        w("  TABLE 2 — Scores by Sector")
        w(LIN)
        w(f"  {'Model':<18}" + "".join(f"{s[:6]:>10}" for s in SECTORS))
        w(LIN)
        for m in model_order:
            if m not in sector_scores: continue
            row_str = f"  {m:<18}"
            for s in SECTORS:
                v = statistics.mean(sector_scores[m].get(s,[0]))
                row_str += f"{v:>9.1f}%"
            w(row_str)
        w(LIN)
        w("  SLM/LLM relative: " + " | ".join(f"{s[:6]}={avg_rel.get(s,0):.3f}" for s in SECTORS))

        w()
        w("  TABLE 3 — Scores by Difficulty")
        w(LIN)
        w(f"  {'Model':<18} {'Easy':>9} {'Medium':>9} {'Hard':>9} {'Gap(E-H)':>10}")
        w(LIN)
        for m in model_order:
            if m not in diff_scores: continue
            e = statistics.mean(diff_scores[m].get("easy",[0]))
            md= statistics.mean(diff_scores[m].get("medium",[0]))
            h = statistics.mean(diff_scores[m].get("hard",[0]))
            w(f"  {m:<18} {e:>8.1f}% {md:>8.1f}% {h:>8.1f}% {(e-h):>9.1f}pp")
        w(LIN)

        w()
        w("  TABLE 4 — Dimension Averages (1-5 scale)")
        w(LIN)
        w(f"  {'Model':<18} {'D1 Acc':>8} {'D2 Dpth':>8} {'D3 Tone':>8} {'D4 Comp':>8}")
        w(LIN)
        for m in model_order:
            if m not in dim_scores: continue
            w(f"  {m:<18} "
              f"{statistics.mean(dim_scores[m]['d1_accuracy']):>7.2f}  "
              f"{statistics.mean(dim_scores[m]['d2_depth']):>7.2f}  "
              f"{statistics.mean(dim_scores[m]['d3_tone']):>7.2f}  "
              f"{statistics.mean(dim_scores[m]['d4_completeness']):>7.2f}")
        w(LIN)

        w()
        w(SEP)
        w("  HYPOTHESIS OUTCOMES")
        w(SEP)
        w()
        w(f"  H8.1 Accuracy parity (>={PARITY_MIN_MODELS}/6 SLMs >= {PARITY_THRESHOLD*100:.0f}% of LLM):")
        w(f"       {slm_parity}/6 models achieved parity  ->  {'SUPPORTED' if h81 else 'NOT SUPPORTED'}")
        for m in SLM_NAMES:
            if m in model_avg and llm_avg > 0:
                r = model_avg[m]/llm_avg
                w(f"       {m:<18} {model_avg[m]:>5.1f}% / {llm_avg:.1f}% = {r:.3f}  "
                  f"{'PARITY' if r >= PARITY_THRESHOLD else 'BELOW'}")
        w()
        w(f"  H8.2 Latency ({PARITY_MIN_MODELS}/6 SLMs P95 < LLM P95 of {llm_p95:.0f}ms):")
        w(f"       {lat_below}/6 faster  ->  {'SUPPORTED' if h82 else 'NOT SUPPORTED'}")
        for m in SLM_NAMES:
            if m in lat_p95:
                w(f"       {m:<18} P95={lat_p95[m]:.0f}ms  "
                  f"{'FASTER' if lat_p95[m]<llm_p95 else 'SLOWER'}")
        w()
        w(f"  H8.3 Difficulty gradient (hard < easy for all SLMs):")
        w(f"       ->  {'SUPPORTED' if h83 else 'NOT SUPPORTED'}")
        w()
        w(f"  H8.4 Financial sector lowest relative SLM scores:")
        w(f"       Lowest: {lowest_sector}  ->  {'SUPPORTED' if h84 else f'NOT SUPPORTED (lowest={lowest_sector})'}")
        for s in sorted(avg_rel, key=avg_rel.get):
            w(f"       {s:<14} rel={avg_rel[s]:.3f}")
        w()
        w(SEP)
        n_supported = sum([h81, h82, h83, h84])
        w(f"  HYPOTHESES SUPPORTED : {n_supported}/4")
        w(f"  TIER VERDICT         : {tier_verdict}")
        w(f"  S3 PREDICTION        : Hybrid")
        w(f"  OUTCOME              : {'CONFIRMED' if 'HYBRID' in tier_verdict else 'DISCONFIRMED'}")
        w(SEP)
        w()
        w("  OUTPUT FILES")
        w(f"  Eval CSV  : {eval_csv}")
        w(f"  Report    : {rpt_path}")
        w(SEP)

    with open(rpt_path) as f:
        print(f.read())

    return eval_csv, rpt_path


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default=None, help="Path to raw CSV (default: latest)")
    parser.add_argument("--mock-judge", action="store_true", help="Use score=3 mock (no API)")
    args = parser.parse_args()

    if not args.mock_judge and not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not set.")
        print("  export GROQ_API_KEY=your_key  OR  run with --mock-judge to test")
        sys.exit(1)

    raw_path = args.raw or latest_raw_file()
    evaluate(raw_path=raw_path, use_judge=not args.mock_judge)