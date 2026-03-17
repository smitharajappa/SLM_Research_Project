"""
run_benchmark_uc2.py — UC2 Invoice Field Extraction Benchmark
S³ Research Project | UT Dallas | March 2026

CRITICAL DIFFERENCE FROM UC1/UC4:
  UC1, UC4 → single-word classification (THREAT/BENIGN, POS/NEG/NEUTRAL)
  UC2      → structured JSON extraction (6 fields from invoice text)

This requires:
  • JSON-prompting: model must return valid JSON, not a single word
  • JSON parsing with graceful fallback (regex extraction if raw parse fails)
  • Field-level scoring (each field right/wrong independently)
  • Hallucination detection: fields with values not in the invoice text

Usage: python3 scripts/run_benchmark_uc2.py
Pre-requisites: ollama serve (in separate terminal), GROQ_API_KEY in .env
"""

import csv
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────────
SEEDS       = [42, 43, 44]
TEMPERATURE = 0.0
MAX_TOKENS  = 300
OLLAMA_BASE = "http://localhost:11434/v1"
GROQ_BASE   = "https://api.groq.com/openai/v1"
GROQ_KEY    = os.getenv("GROQ_API_KEY", "")

OUTPUT_FIELDS = ["vendor_name", "invoice_date", "invoice_number",
                 "total_amount", "tax_amount", "line_item_count"]

SYSTEM_PROMPT = """You are a precise invoice data extraction assistant.
Extract exactly these 6 fields from the invoice and return ONLY a valid JSON object — no explanation, no markdown, no extra text:
{
  "vendor_name": "string — exact company/vendor name",
  "invoice_date": "YYYY-MM-DD or null if not found",
  "invoice_number": "string — exact invoice reference number",
  "total_amount": float — total due as a number,
  "tax_amount": float or null — tax/GST/VAT amount if stated, else null,
  "line_item_count": integer — number of distinct line items billed
}
Rules:
- Return ONLY the JSON object, starting with { and ending with }
- Use null (not "null") for missing optional fields
- total_amount and line_item_count are always required — never null
- Dates must be in YYYY-MM-DD format"""

USER_TEMPLATE = "Extract the invoice fields from this invoice:\n\n{invoice_text}"

MODELS = [
    {"name": "Llama-3.2-3B",  "model": "llama3.2:3b",             "provider": "ollama", "tier": "SLM", "params": "3B"},
    {"name": "Phi4-Mini",      "model": "phi4-mini:latest",         "provider": "ollama", "tier": "SLM", "params": "3.8B"},
    {"name": "Gemma3-4B",      "model": "gemma3:4b",                "provider": "ollama", "tier": "SLM", "params": "4B"},
    {"name": "Qwen2.5-7B",     "model": "qwen2.5:7b",               "provider": "ollama", "tier": "SLM", "params": "7B"},
    {"name": "Mistral-7B",     "model": "mistral:latest",           "provider": "ollama", "tier": "SLM", "params": "7B"},
    {"name": "Llama-3.1-8B",  "model": "llama3.1:8b",              "provider": "ollama", "tier": "SLM", "params": "8B"},
    {"name": "Llama-3.3-70B", "model": "llama-3.3-70b-versatile",  "provider": "groq",   "tier": "LLM", "params": "70B"},
]


def parse_json_output(raw_text):
    clean = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()
    clean = re.sub(r"```(?:json)?", "", clean).strip().replace("```", "").strip()
    try:
        return json.loads(clean), True, None
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*?\}", clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group()), True, "regex_extracted"
        except json.JSONDecodeError:
            pass
    return {}, False, "parse_failed"


def normalize_field(field_name, predicted, gold):
    if predicted is None and gold is None:
        return True
    if predicted is None or gold is None:
        return False
    if field_name == "vendor_name":
        norm = lambda s: re.sub(r"[^\w\s]", "", str(s)).lower().strip()
        return norm(predicted) == norm(gold)
    elif field_name == "invoice_date":
        norm = lambda s: str(s).strip().replace("/", "-")[:10]
        return norm(predicted) == norm(gold)
    elif field_name == "invoice_number":
        return str(predicted).strip().upper() == str(gold).strip().upper()
    elif field_name in ("total_amount", "tax_amount"):
        try:
            return abs(float(str(predicted).replace(",", "")) - float(gold)) <= 0.50
        except (ValueError, TypeError):
            return False
    elif field_name == "line_item_count":
        try:
            return int(predicted) == int(gold)
        except (ValueError, TypeError):
            return False
    return str(predicted).strip() == str(gold).strip()


def call_model(client, model_id, invoice_text, seed):
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": USER_TEMPLATE.format(invoice_text=invoice_text)},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            seed=seed,
        )
        latency_ms = round((time.time() - start) * 1000)
        return response.choices[0].message.content or "", latency_ms, None
    except Exception as e:
        return "", round((time.time() - start) * 1000), str(e)[:120]


def run_model(model_cfg, test_items):
    print(f"\n  ── {model_cfg['name']} ({model_cfg['tier']} · {model_cfg['params']}) ──")
    print(f"     {len(test_items)} items × {len(SEEDS)} runs = {len(test_items) * len(SEEDS)} inferences")

    client = OpenAI(
        api_key="ollama" if model_cfg["provider"] == "ollama" else GROQ_KEY,
        base_url=OLLAMA_BASE if model_cfg["provider"] == "ollama" else GROQ_BASE,
        timeout=httpx.Timeout(300.0, connect=10.0),
    )

    results, latencies = [], []
    field_correct = {f: 0 for f in OUTPUT_FIELDS}
    field_total   = {f: 0 for f in OUTPUT_FIELDS}
    json_valid, total_inf = 0, 0

    for item in test_items:
        for run_idx, seed in enumerate(SEEDS):
            raw, latency_ms, error = call_model(client, model_cfg["model"], item["invoice_text"], seed)

            row = {
                "item_id": item["item_id"], "category": item["category"],
                "difficulty": item["difficulty"], "seed": seed,
                "raw_output": raw[:400], "latency_ms": latency_ms,
            }

            if error:
                row.update({"json_valid": False, "parse_note": "api_error", "fields_correct": 0})
                for f in OUTPUT_FIELDS:
                    row[f"pred_{f}"] = None
                    row[f"correct_{f}"] = False
                results.append(row)
                continue

            parsed, is_valid, parse_note = parse_json_output(raw)
            row["json_valid"] = is_valid
            row["parse_note"] = parse_note or "clean"
            if is_valid:
                json_valid += 1

            n_correct = 0
            for f in OUTPUT_FIELDS:
                gold_val = item.get(f)
                pred_val = parsed.get(f) if is_valid else None
                if f in ("tax_amount", "invoice_date") and gold_val is None:
                    is_correct = (pred_val is None)
                else:
                    is_correct = normalize_field(f, pred_val, gold_val)
                row[f"pred_{f}"]    = pred_val
                row[f"correct_{f}"] = is_correct
                if is_correct:
                    n_correct += 1
                    field_correct[f] += 1
                field_total[f] += 1

            row["fields_correct"] = n_correct
            latencies.append(latency_ms)
            total_inf += 1
            results.append(row)

            if run_idx == len(SEEDS) - 1:
                status = "✓" if n_correct >= 4 else "△" if n_correct >= 2 else "✗"
                print(f"     [{item['item_id']}] run3: {n_correct}/6 fields  ({latency_ms}ms)  {status}")

        if model_cfg["provider"] == "groq":
            time.sleep(0.4)

    lats = sorted(latencies)
    p50 = lats[len(lats)//2] if lats else 0
    p95 = lats[int(len(lats)*0.95)] if lats else 0
    per_field_acc = {f: round(field_correct[f]/field_total[f]*100, 1) for f in OUTPUT_FIELDS if field_total[f]}
    # NOTE: quick-run field accuracy only — for paper figures always use evaluate_uc2.py output, not this summary CSV.
    overall = round(sum(per_field_acc.values())/len(per_field_acc), 1) if per_field_acc else 0
    jv_pct = round(json_valid/total_inf*100, 1) if total_inf else 0
    print(f"     ✅ Done — Field acc: {overall}%  |  JSON valid: {jv_pct}%  |  P50: {p50}ms  |  P95: {p95}ms")

    return results, overall, json_valid, total_inf


def main():
    if not os.path.exists("data/gold_sets/uc2_invoice_extraction.csv"):
        print("❌ Gold set not found. Run build_gold_set_uc2.py first.")
        return

    with open("data/gold_sets/uc2_invoice_extraction.csv", newline="", encoding="utf-8") as f:
        all_items = list(csv.DictReader(f))

    test_items = [x for x in all_items if x["split"] == "test"]
    for item in test_items:
        item["total_amount"]    = float(item["total_amount"]) if item["total_amount"] else None
        item["tax_amount"]      = float(item["tax_amount"]) if item["tax_amount"] else None
        item["line_item_count"] = int(item["line_item_count"]) if item["line_item_count"] else None
        item["invoice_date"]    = item["invoice_date"] or None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("=" * 65)
    print("  UC2 BENCHMARK — Invoice Field Extraction")
    print(f"  {len(MODELS)} models × {len(test_items)} test items × {len(SEEDS)} runs = "
          f"{len(test_items)*len(SEEDS)*len(MODELS)} inferences")
    print("  JSON extraction — 6 fields per inference")
    print("  S³ Score: 2.75 (corrected: 2.56)  →  Pure SLM predicted")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)
    print(f"  Loaded {len(test_items)} test items")

    all_raw, summaries = [], []

    for model_cfg in MODELS:
        rows, overall_acc, json_valid, total_run = run_model(model_cfg, test_items)
        for r in rows:
            r.update({"model": model_cfg["name"], "tier": model_cfg["tier"], "params": model_cfg["params"]})
        all_raw.extend(rows)

        per_field = {}
        for f in OUTPUT_FIELDS:
            correct = sum(1 for r in rows if r.get(f"correct_{f}"))
            total   = sum(1 for r in rows if f"correct_{f}" in r)
            per_field[f] = round(correct/total*100, 1) if total else 0

        lats = sorted([r["latency_ms"] for r in rows if isinstance(r.get("latency_ms"), int)])
        p50 = lats[len(lats)//2] if lats else 0
        p95 = lats[int(len(lats)*0.95)] if lats else 0

        summaries.append({
            "model": model_cfg["name"], "tier": model_cfg["tier"], "params": model_cfg["params"],
            "overall_acc": overall_acc,
            "json_valid_pct": round(json_valid/total_run*100, 1) if total_run else 0,
            "p50_ms": p50, "p95_ms": p95,
            **{f"acc_{f}": per_field[f] for f in OUTPUT_FIELDS},
        })

        if model_cfg["provider"] == "ollama":
            time.sleep(8)

    os.makedirs("data/raw_outputs", exist_ok=True)
    os.makedirs("data/results", exist_ok=True)
    raw_path = f"data/raw_outputs/uc2_raw_{timestamp}.csv"
    sum_path = f"data/results/uc2_summary_{timestamp}.csv"

    if all_raw:
        with open(raw_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_raw[0].keys())
            writer.writeheader()
            writer.writerows(all_raw)

    if summaries:
        with open(sum_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=summaries[0].keys())
            writer.writeheader()
            writer.writerows(summaries)

    llm_acc = next((s["overall_acc"] for s in summaries if s["tier"] == "LLM"), 0)
    n_pure  = sum(1 for s in summaries if s["tier"] == "SLM" and s["overall_acc"] >= llm_acc * 0.95)

    print("\n" + "=" * 65)
    print("  UC2 BENCHMARK RESULTS — Invoice Field Extraction")
    print("=" * 65)
    print(f"  {'Model':<20} {'Tier':<5} {'Params':<6} {'FieldAcc%':>9} {'JSON%':>6} {'P50':>6} {'P95':>7}")
    print(f"  {'-'*20} {'-'*5} {'-'*6} {'-'*9} {'-'*6} {'-'*6} {'-'*7}")
    for s in summaries:
        tag = "← baseline" if s["tier"]=="LLM" else ("✅ Pure SLM confirmed" if s["overall_acc"]>=llm_acc*0.95 else ("⭐ Strong SLM" if s["overall_acc"]>=llm_acc*0.90 else ""))
        print(f"  {s['model']:<20} {s['tier']:<5} {s['params']:<6} {s['overall_acc']:>8.1f}% "
              f"{s['json_valid_pct']:>5.1f}% {s['p50_ms']:>5} {s['p95_ms']:>6}  {tag}")

    best_slm = max((s for s in summaries if s["tier"]=="SLM"), key=lambda x: x["overall_acc"], default=None)
    llm_row  = next((s for s in summaries if s["tier"]=="LLM"), None)
    if best_slm and llm_row:
        print()
        print(f"  LLM baseline field accuracy : {llm_acc}%")
        print(f"  SLMs at ≥95% parity         : {n_pure}/{sum(1 for s in summaries if s['tier']=='SLM')}")
        print()
        print("  Per-field accuracy (best SLM vs LLM):")
        print(f"  {'Field':<22} {'Best SLM':>10} {'LLM':>8} {'Gap':>8}")
        print(f"  {'-'*22} {'-'*10} {'-'*8} {'-'*8}")
        gaps = {}
        for f in OUTPUT_FIELDS:
            sv, lv = best_slm[f"acc_{f}"], llm_row[f"acc_{f}"]
            gap = lv - sv
            gaps[f] = gap
            marker = " ⚠️" if gap > 10 else ""
            print(f"  {f:<22} {sv:>9.1f}% {lv:>7.1f}% {gap:>+7.1f}pp{marker}")
        hardest = max(gaps, key=gaps.get)
        h21 = best_slm["overall_acc"] >= llm_acc * 0.90
        h22 = best_slm["p95_ms"] < 4000
        h23 = n_pure >= 1
        h24 = hardest in ("tax_amount", "line_item_count")
        print()
        print(f"  H2.1 Best SLM ≥90% LLM acc    {'✅ SUPPORTED' if h21 else '❌ NOT SUPPORTED'}")
        print(f"  H2.2 Best SLM P95 < 4000ms    {'✅ SUPPORTED' if h22 else '❌ NOT SUPPORTED'}")
        print(f"  H2.3 UC2 graduates Pure SLM   {'✅ SUPPORTED' if h23 else '❌ NOT SUPPORTED'}")
        print(f"  H2.4 tax/count hardest fields  {'✅ SUPPORTED' if h24 else '⚠️  CHECK'} (hardest: {hardest})")
        if h23:
            print()
            print("  ✅ S³ PREDICTION CONFIRMED: UC2 → Pure SLM")
        else:
            print()
            print("  ⚠️  Prediction not yet confirmed — review per-field table")

    print()
    print(f"  Files saved:\n    {raw_path}\n    {sum_path}")
    print()
    print("  NEXT STEP:\n  → python3 scripts/evaluate_uc2.py")
    print("=" * 65)


if __name__ == "__main__":
    main()