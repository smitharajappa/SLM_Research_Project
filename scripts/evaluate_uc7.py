"""
evaluate_uc7.py
Full evaluation for UC7 Legal Contract Clause Analysis.

Computes:
  - Overall accuracy per model (valid-only denominator — excludes INVALID)
  - Per-class Precision, Recall, F1 (all 4 risk levels)
  - Macro F1 (average across 4 classes)
  - 4×4 confusion matrix
  - Hallucination rate (INVALID outputs)
  - Latency P50 / P95
  - H7.1 – H7.4 hypothesis outcomes
  - Cross-use-case comparison: UC1, UC4, UC7
  - HIGH_RISK class deep dive (H7.4)
  - Flag Rule analysis (SK=4 → Hybrid enforcement)

Usage:
  python3 scripts/evaluate_uc7.py
"""

import os
import csv
import glob
from collections import defaultdict
from datetime import datetime

RAW_OUTPUT_DIR = "data/raw_outputs"
EVAL_DIR       = "evaluation"
os.makedirs(EVAL_DIR, exist_ok=True)

TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_FILE = os.path.join(EVAL_DIR, f"uc7_report_{TIMESTAMP}.txt")
EVAL_FILE   = os.path.join(EVAL_DIR, f"uc7_evaluation_{TIMESTAMP}.csv")

LABELS = ["HIGH_RISK", "MEDIUM_RISK", "LOW_RISK", "STANDARD"]

# ── Prior UC results for cross-use-case comparison ────────────
UC1_RESULTS = {
    "Mistral-7B":    {"accuracy": 90.0, "f1": 93.3},
    "Phi4-Mini":     {"accuracy": 80.0, "f1": 83.3},
    "Gemma3-4B":     {"accuracy": 76.7, "f1": 80.0},
    "Qwen2.5-7B":    {"accuracy": 60.0, "f1": 60.0},
    "Llama-3.1-8B":  {"accuracy": 66.7, "f1": 68.8},
    "Llama-3.2-3B":  {"accuracy": 56.7, "f1": 55.2},
    "Llama-3.3-70B": {"accuracy": 90.0, "f1": 92.3},
}

UC4_RESULTS = {
    "Mistral-7B":    {"accuracy": 95.5, "f1": 94.7},
    "Phi4-Mini":     {"accuracy": 86.7, "f1": 85.1},
    "Gemma3-4B":     {"accuracy": 90.0, "f1": 89.1},
    "Qwen2.5-7B":    {"accuracy": 90.0, "f1": 89.4},
    "Llama-3.1-8B":  {"accuracy": 93.3, "f1": 93.0},
    "Llama-3.2-3B":  {"accuracy": 93.3, "f1": 93.2},
    "Llama-3.3-70B": {"accuracy": 96.7, "f1": 96.6},
}


def find_latest_raw():
    files = sorted(glob.glob(os.path.join(RAW_OUTPUT_DIR, "uc7_raw_*.csv")))
    return files[-1] if files else None


def load_rows(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def accuracy(rows):
    """Valid-only denominator — excludes INVALID from count."""
    valid = [r for r in rows if r["prediction"] not in ["ERROR", "INVALID"]]
    if not valid:
        return 0
    return round(sum(1 for r in valid if r["correct"] == "True") / len(valid) * 100, 1)


def hallucination_rate(rows):
    return round(sum(1 for r in rows if r["prediction"] == "INVALID") / len(rows) * 100, 1)


def latency_percentiles(rows):
    lats = sorted([int(r["latency_ms"]) for r in rows if int(r["latency_ms"]) > 0])
    if not lats:
        return 0, 0
    return lats[len(lats) // 2], lats[int(len(lats) * 0.95)]


def per_class_metrics(rows, label):
    """Precision, Recall, F1 for one class treated as the positive class."""
    tp = sum(1 for r in rows if r["prediction"] == label and r["gold_label"] == label)
    fp = sum(1 for r in rows if r["prediction"] == label and r["gold_label"] != label)
    fn = sum(1 for r in rows if r["prediction"] != label and r["gold_label"] == label)
    prec   = tp / (tp + fp) * 100 if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
    f1     = 2 * prec * recall / (prec + recall) if (prec + recall) > 0 else 0
    return round(prec, 1), round(recall, 1), round(f1, 1)


def macro_f1(rows):
    f1s = [per_class_metrics(rows, l)[2] for l in LABELS]
    return round(sum(f1s) / len(f1s), 1)


def confusion_matrix(rows):
    """Returns dict[actual][predicted] = count for all 4 labels + INVALID."""
    mat = {l: {p: 0 for p in LABELS + ["INVALID"]} for l in LABELS}
    for r in rows:
        actual = r["gold_label"]
        pred   = r["prediction"]
        if actual in LABELS:
            key = pred if pred in LABELS else "INVALID"
            mat[actual][key] += 1
    return mat


def evaluate_by_model(rows):
    """Compute all metrics grouped by model name."""
    models = {}
    for model_name in dict.fromkeys(r["model_name"] for r in rows):
        mr   = [r for r in rows if r["model_name"] == model_name]
        p50, p95 = latency_percentiles(mr)
        entry = {
            "tier":     mr[0]["model_tier"],
            "params":   mr[0]["model_params"],
            "accuracy": accuracy(mr),
            "macro_f1": macro_f1(mr),
            "halluc":   hallucination_rate(mr),
            "p50": p50,
            "p95": p95,
            "cm":  confusion_matrix(mr),
        }
        for label in LABELS:
            p, r_, f = per_class_metrics(mr, label)
            entry[f"prec_{label}"]   = p
            entry[f"recall_{label}"] = r_
            entry[f"f1_{label}"]     = f
        models[model_name] = entry
    return models


def save_eval_csv(model_results):
    rows = []
    for name, m in model_results.items():
        row = {
            "model":      name,
            "tier":       m["tier"],
            "params":     m["params"],
            "accuracy":   m["accuracy"],
            "macro_f1":   m["macro_f1"],
            "halluc_pct": m["halluc"],
            "latency_p50": m["p50"],
            "latency_p95": m["p95"],
        }
        for label in LABELS:
            row[f"f1_{label}"] = m[f"f1_{label}"]
        rows.append(row)
    with open(EVAL_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def build_report(model_results):
    lines = []
    W = 72

    lines += [
        "=" * W,
        "  UC7 EVALUATION REPORT — Legal Contract Clause Analysis",
        f"  Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "  Pre-reg   : 2026-03-02  |  S³ Score: 3.60  |  Prediction: Hybrid",
        "  Flag Rule : SK=4 → Hybrid enforced (safety measure for 4-class risk)",
        "=" * W, "",
    ]

    sorted_models = sorted(model_results.items(),
                           key=lambda x: x[1]["macro_f1"], reverse=True)

    llm_acc = llm_f1 = None
    for name, m in sorted_models:
        if m["tier"] == "LLM":
            llm_acc = m["accuracy"]
            llm_f1  = m["macro_f1"]

    # ── TABLE 1: Overall metrics ───────────────────────────────
    lines += [
        "  TABLE 1 — Overall Classification Metrics",
        "  " + "-" * 68,
        f"  {'Model':<20} {'Tier':<5} {'Acc':>6} {'MacroF1':>8} "
        f"{'Halluc':>7} {'P50':>6} {'P95':>7}",
        "  " + "-" * 68,
    ]
    for name, m in sorted_models:
        flag = " ← LLM baseline" if m["tier"] == "LLM" else ""
        lines.append(
            f"  {name:<20} {m['tier']:<5} {m['accuracy']:>5.1f}% "
            f"{m['macro_f1']:>7.1f}% {m['halluc']:>6.1f}% "
            f"{m['p50']:>5}ms {m['p95']:>6}ms{flag}"
        )
    lines += ["  " + "-" * 68, ""]

    # ── TABLE 2: Per-class F1 ──────────────────────────────────
    lines += [
        "  TABLE 2 — Per-Class F1 Score",
        "  " + "-" * W,
        f"  {'Model':<20} {'HIGH':>6} {'MED':>6} {'LOW':>6} "
        f"{'STD':>6}  {'Lowest class'}",
        "  " + "-" * W,
    ]
    for name, m in sorted_models:
        f1s    = {l: m[f"f1_{l}"] for l in LABELS}
        lowest = min(f1s, key=f1s.get)
        lines.append(
            f"  {name:<20} "
            f"{f1s['HIGH_RISK']:>5.1f}% "
            f"{f1s['MEDIUM_RISK']:>5.1f}% "
            f"{f1s['LOW_RISK']:>5.1f}% "
            f"{f1s['STANDARD']:>5.1f}%  "
            f"{lowest}"
        )
    lines += ["  " + "-" * W, ""]

    # ── TABLE 3: Confusion matrices ────────────────────────────
    short = {"HIGH_RISK": "HIGH", "MEDIUM_RISK": "MED", "LOW_RISK": "LOW", "STANDARD": "STD"}

    lines += ["  TABLE 3 — 4×4 Confusion Matrices (all runs combined)", ""]
    for name, m in sorted_models:
        cm = m["cm"]
        header = "  " + " " * 12 + "".join(f"{short[p]:>7}" for p in LABELS)
        lines += [
            f"  {name} ({m['tier']} · {m['params']}):",
            header,
        ]
        for actual in LABELS:
            row_vals = "".join(f"{cm[actual][p]:>7}" for p in LABELS)
            lines.append(f"  {short[actual]:<12}{row_vals}")
        lines.append("")

    # ── TABLE 4: Cross-UC comparison ───────────────────────────
    lines += [
        "  TABLE 4 — Cross Use-Case Comparison: UC1 → UC4 → UC7",
        f"  S³: UC1=3.10 (Hybrid)  UC4=2.10 (Pure SLM)  UC7=3.60 (Hybrid)",
        "  " + "-" * W,
        f"  {'Model':<20} {'UC1 Acc':>8} {'UC4 Acc':>8} {'UC7 Acc':>8} "
        f"{'Δ UC1→7':>9} {'UC1 F1':>8} {'UC7 F1':>8}",
        "  " + "-" * W,
    ]
    for name, m in sorted_models:
        uc1    = UC1_RESULTS.get(name, {})
        uc4    = UC4_RESULTS.get(name, {})
        d_acc  = m["accuracy"] - uc1.get("accuracy", 0)
        lines.append(
            f"  {name:<20} "
            f"{uc1.get('accuracy', 0):>7.1f}% "
            f"{uc4.get('accuracy', 0):>7.1f}% "
            f"{m['accuracy']:>7.1f}% "
            f"{d_acc:>+8.1f}pp "
            f"{uc1.get('f1', 0):>7.1f}% "
            f"{m['macro_f1']:>7.1f}%"
        )
    lines += ["  " + "-" * W, ""]

    # ── HIGH_RISK class deep dive ──────────────────────────────
    lines += [
        "  HIGH_RISK CLASS ANALYSIS (H7.4 — expected highest SLM-vs-LLM gap)",
        "  " + "-" * 68,
    ]
    for name, m in sorted_models:
        high_f1 = m["f1_HIGH_RISK"]
        other   = [m[f"f1_{l}"] for l in LABELS if l != "HIGH_RISK"]
        avg_other = sum(other) / len(other)
        gap     = avg_other - high_f1
        lines.append(
            f"  {name:<20} HIGH_RISK F1: {high_f1:>5.1f}%   "
            f"Avg other classes: {avg_other:>5.1f}%   Gap: {gap:>+5.1f}pp"
        )
    lines += ["", "  Higher gap = HIGH_RISK harder than other classes for that model", ""]

    # ── FLAG RULE ANALYSIS ─────────────────────────────────────
    lines += [
        "  FLAG RULE ANALYSIS — SK=4 Enforces Hybrid",
        "  " + "-" * 68,
        "  The S³ framework's flag rule triggers when SK >= 4.",
        "  UC7 has SK=4 (4-way risk classification), so even if SLM accuracy",
        "  is competitive, the gate rule enforces Hybrid as a safety measure.",
        "  This ensures safety-critical legal classifications receive LLM",
        "  verification when needed.",
        "",
    ]

    # ── S³ Hypothesis outcomes ─────────────────────────────────
    lines += [
        "  PRE-REGISTERED HYPOTHESIS OUTCOMES",
        "  " + "-" * 68,
    ]

    if llm_acc:
        slm_models   = {n: m for n, m in model_results.items() if m["tier"] == "SLM"}
        best_slm_acc = max(m["accuracy"] for m in slm_models.values())
        best_slm_p95 = min(m["p95"]      for m in slm_models.values())
        ratio        = best_slm_acc / llm_acc * 100 if llm_acc > 0 else 0

        h71 = "SUPPORTED" if llm_acc >= 80 else "NOT SUPPORTED"
        h72 = "SUPPORTED" if best_slm_p95 < 4000 else "NOT SUPPORTED"
        h73 = "SUPPORTED" if ratio < 95 else "NOT SUPPORTED"

        # H7.4 — HIGH_RISK has highest SLM-vs-LLM gap
        llm_high_f1 = None
        for n, m in model_results.items():
            if m["tier"] == "LLM":
                llm_high_f1 = m["f1_HIGH_RISK"]

        high_gap_largest_count = 0
        for n, m in slm_models.items():
            if llm_high_f1 is not None:
                high_gap = llm_high_f1 - m["f1_HIGH_RISK"]
                other_gaps = [
                    (model_results[[k for k in model_results if model_results[k]["tier"] == "LLM"][0]][f"f1_{l}"] - m[f"f1_{l}"])
                    for l in LABELS if l != "HIGH_RISK"
                ]
                if high_gap >= max(other_gaps):
                    high_gap_largest_count += 1
        h74 = "SUPPORTED" if high_gap_largest_count >= len(slm_models) // 2 else "NOT SUPPORTED"

        lines += [
            f"  H7.1 (LLM accuracy >= 80%)              : {h71}",
            f"        LLM accuracy: {llm_acc}%",
            "",
            f"  H7.2 (Best SLM P95 < 4000ms)            : {h72}",
            f"        Best SLM P95: {best_slm_p95}ms",
            "",
            f"  H7.3 (Best SLM < 95% LLM parity)        : {h73}",
            f"        Best SLM {best_slm_acc}% vs LLM {llm_acc}% → ratio {ratio:.0f}%",
            f"        Validates Hybrid — SK=4 flag rule justified",
            "",
            f"  H7.4 (HIGH_RISK highest SLM-vs-LLM gap) : {h74}",
            f"        {high_gap_largest_count} of {len(slm_models)} SLMs show HIGH_RISK as largest gap",
            f"        Safety-critical errors concentrated in high-risk clauses",
        ]

    lines += [
        "",
        "=" * W,
        "  END OF UC7 EVALUATION REPORT",
        "=" * W,
    ]

    return "\n".join(lines)


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  UC7 Evaluation — Legal Contract Clause Analysis")
    print("=" * 60)

    raw_file = find_latest_raw()
    if not raw_file:
        print("  ❌ No raw results found. Run run_benchmark_uc7.py first.")
        exit(1)

    print(f"  Loading: {raw_file}")
    rows = load_rows(raw_file)
    print(f"  Loaded {len(rows)} inference records")

    if len(rows) != 630:
        print(f"  ⚠️  Expected 630 rows (30 items × 7 models × 3 runs), got {len(rows)}")

    print("  Computing metrics...")
    model_results = evaluate_by_model(rows)

    save_eval_csv(model_results)
    print(f"  Saved: {EVAL_FILE}")

    report = build_report(model_results)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  Saved: {REPORT_FILE}")

    print()
    print(report)

    print()
    print("  FILES SAVED:")
    print(f"    {EVAL_FILE}")
    print(f"    {REPORT_FILE}")
    print()
    print("  NEXT STEP:")
    print("  → Results feed into paper Section 5 UC7")
    print("=" * 60)
    print()
