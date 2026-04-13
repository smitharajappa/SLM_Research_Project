"""
run_benchmark_uc5.py
Runs all models against UC5 test set (30 items × 7 models × 3 runs = 630 inferences)
Saves raw outputs to: data/raw_outputs/uc5_raw_results.csv
Saves summary to:     data/results/uc5_results_summary.csv

Pre-registered config:
  temperature = 0.0
  seeds       = [42, 43, 44]
  max_tokens  = 128 (Category 1)
  test split  = 30 items only
"""

import os
import csv
import json
import time
import re
import httpx
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from benchmark_utils import log_memory_state, check_memory, unload_ollama_model, warm_up_inference

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────
GOLD_SET_PATH  = "data/gold_sets/uc5_code_review.csv"
RAW_OUTPUT_DIR = "data/raw_outputs"
RESULTS_DIR    = "data/results"
os.makedirs(RAW_OUTPUT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

TIMESTAMP      = datetime.now().strftime("%Y%m%d_%H%M%S")
RAW_FILE       = os.path.join(RAW_OUTPUT_DIR, f"uc5_raw_{TIMESTAMP}.csv")
SUMMARY_FILE   = os.path.join(RESULTS_DIR,    f"uc5_summary_{TIMESTAMP}.csv")

# ── Locked inference config ────────────────────────────────────
TEMPERATURE  = 0.0
MAX_TOKENS   = 128
SEEDS        = [42, 43, 44]
RUNS         = len(SEEDS)

# ── Model registry ─────────────────────────────────────────────
MODELS = [
    # LOCAL SLMs — Ollama
    {
        "name":     "Llama-3.2-3B",
        "model_id": "llama3.2:3b",
        "provider": "ollama",
        "base_url": "http://localhost:11434/v1",
        "api_key":  "ollama",
        "tier":     "SLM",
        "params":   "3B",
        "delay":    1.0,
        "timeout":  300.0,
    },
    {
        "name":     "Phi4-Mini",
        "model_id": "phi4-mini:latest",
        "provider": "ollama",
        "base_url": "http://localhost:11434/v1",
        "api_key":  "ollama",
        "tier":     "SLM",
        "params":   "3.8B",
        "delay":    1.0,
        "timeout":  300.0,
    },
    {
        "name":     "Gemma3-4B",
        "model_id": "gemma3:4b",
        "provider": "ollama",
        "base_url": "http://localhost:11434/v1",
        "api_key":  "ollama",
        "tier":     "SLM",
        "params":   "4B",
        "delay":    1.0,
        "timeout":  300.0,
    },
    {
        "name":     "Qwen2.5-7B",
        "model_id": "qwen2.5:7b",
        "provider": "ollama",
        "base_url": "http://localhost:11434/v1",
        "api_key":  "ollama",
        "tier":     "SLM",
        "params":   "7B",
        "delay":    1.0,
        "timeout":  300.0,
    },
    {
        "name":     "Mistral-7B",
        "model_id": "mistral:latest",
        "provider": "ollama",
        "base_url": "http://localhost:11434/v1",
        "api_key":  "ollama",
        "tier":     "SLM",
        "params":   "7B",
        "delay":    1.0,
        "timeout":  300.0,
    },
    {
        "name":     "Llama-3.1-8B",
        "model_id": "llama3.1:8b",
        "provider": "ollama",
        "base_url": "http://localhost:11434/v1",
        "api_key":  "ollama",
        "tier":     "SLM",
        "params":   "8B",
        "delay":    1.0,
        "timeout":  300.0,
    },
    # CLOUD LLM — Groq
    {
        "name":     "Llama-3.3-70B",
        "model_id": "llama-3.3-70b-versatile",
        "provider": "groq",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key":  os.getenv("GROQ_API_KEY"),
        "tier":     "LLM",
        "params":   "70B",
        "delay":    2.0,
        "timeout":  30.0,
    },
]

SYSTEM_PROMPT = (
    "You are a code review classifier. "
    "Classify the code snippet into exactly ONE category: "
    "SECURITY, LOGIC_ERROR, PERFORMANCE, BEST_PRACTICE, or CLEAN. "
    "Reply with exactly ONE word from that list. "
    "No explanation. No punctuation."
)


def load_test_items():
    """Load only test split items from gold set."""
    items = []
    with open(GOLD_SET_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["split"] == "test":
                items.append(row)
    return items


def clean_response(raw: str) -> str:
    """Normalize model output to one of 5 valid labels."""
    cleaned = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
    cleaned = cleaned.strip().upper()
    if "BEST_PRACTICE" in cleaned or "BEST PRACTICE" in cleaned:
        return "BEST_PRACTICE"
    if "LOGIC_ERROR" in cleaned or "LOGIC ERROR" in cleaned:
        return "LOGIC_ERROR"
    if "SECURITY" in cleaned:
        return "SECURITY"
    if "PERFORMANCE" in cleaned:
        return "PERFORMANCE"
    if "CLEAN" in cleaned:
        return "CLEAN"
    # Partial matches
    if "LOGIC" in cleaned:
        return "LOGIC_ERROR"
    if "BEST" in cleaned:
        return "BEST_PRACTICE"
    return "INVALID"


def run_inference(model_cfg, item, run_idx):
    """Run single inference. Returns (result, latency_ms, raw_output, error)."""
    try:
        client = OpenAI(
            api_key=model_cfg["api_key"],
            base_url=model_cfg["base_url"],
            timeout=httpx.Timeout(model_cfg["timeout"], connect=10.0)
        )
        user_msg = f"Classify this code snippet: {item['text']}"

        start = time.time()
        response = client.chat.completions.create(
            model=model_cfg["model_id"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            seed=SEEDS[run_idx] if model_cfg["provider"] == "groq" else None,
        )
        latency = round((time.time() - start) * 1000)
        raw     = response.choices[0].message.content
        result  = clean_response(raw)
        return result, latency, raw, None

    except Exception as e:
        return "ERROR", 0, "", str(e)[:120]


def is_correct(predicted, gold_label):
    return predicted == gold_label


def run_model_benchmark(model_cfg, test_items):
    """Run a model against all test items × 3 runs. Returns list of raw result rows."""
    print(f"\n  ── {model_cfg['name']} ({model_cfg['tier']} · {model_cfg['params']}) ──")
    print(f"     {len(test_items)} items × {RUNS} runs = {len(test_items)*RUNS} inferences")

    rows = []
    correct_counts = []
    latencies = []

    for item_idx, item in enumerate(test_items):
        run_results = []

        for run_idx in range(RUNS):
            result, latency, raw, error = run_inference(model_cfg, item, run_idx)

            correct = is_correct(result, item["label"]) if result not in ["ERROR", "INVALID"] else False

            row = {
                "timestamp":     datetime.now().isoformat(),
                "model_name":    model_cfg["name"],
                "model_tier":    model_cfg["tier"],
                "model_params":  model_cfg["params"],
                "provider":      model_cfg["provider"],
                "item_id":       item["id"],
                "item_text":     item["text"][:80] + "..." if len(item["text"]) > 80 else item["text"],
                "gold_label":    item["label"],
                "category":      item["category"],
                "difficulty":    item["difficulty"],
                "run_number":    run_idx + 1,
                "prediction":    result,
                "correct":       correct,
                "latency_ms":    latency,
                "raw_output":    raw[:200] if raw else "",
                "error":         error or "",
            }
            rows.append(row)
            run_results.append(correct)
            latencies.append(latency)

            # Progress dot
            icon = "✓" if correct else "✗" if result != "ERROR" else "E"
            print(f"     [{item['id']}] run{run_idx+1}: {result:<15} {icon}  ({latency}ms)", end="\r")

        correct_counts.append(all(run_results))
        time.sleep(model_cfg["delay"])

    # Per-model summary
    total_inferences = len(test_items) * RUNS
    total_correct    = sum(1 for r in rows if r["correct"])
    # NOTE: quick-run accuracy only — includes INVALID in denominator.
    # For paper figures always use evaluate_uc5.py output, not this summary CSV.
    accuracy         = round(total_correct / total_inferences * 100, 1)
    valid_latencies  = [r["latency_ms"] for r in rows if r["latency_ms"] > 0]
    p50              = sorted(valid_latencies)[len(valid_latencies)//2] if valid_latencies else 0
    p95              = sorted(valid_latencies)[int(len(valid_latencies)*0.95)] if valid_latencies else 0

    print(f"\n     ✅ Done — Accuracy: {accuracy}%  |  P50: {p50}ms  |  P95: {p95}ms")
    return rows, accuracy, p50, p95


def save_raw_results(all_rows):
    """Save all raw inference results to CSV."""
    if not all_rows:
        return
    fieldnames = list(all_rows[0].keys())
    with open(RAW_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)


def save_summary(summary_rows):
    """Save per-model summary to CSV."""
    if not summary_rows:
        return
    fieldnames = list(summary_rows[0].keys())
    with open(SUMMARY_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)


if __name__ == "__main__":
    print()
    print("=" * 65)
    print("  UC5 BENCHMARK — Automated Code Review")
    print("  7 models × 30 test items × 3 runs = 630 inferences")
    print(f"  Config: temp={TEMPERATURE}, max_tokens={MAX_TOKENS}")
    print(f"  S³ prediction: Hybrid (formula-only, S³=3.33)")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    # Load test items
    test_items = load_test_items()
    print(f"\n  Loaded {len(test_items)} test items from gold set")

    if len(test_items) == 0:
        print("  ❌ No test items found. Check gold set path.")
        exit(1)

    # Run all models
    all_raw_rows   = []
    summary_rows   = []
    llm_accuracy   = None

    for model_idx, model_cfg in enumerate(MODELS):
        # Infrastructure: memory check before loading model
        check_memory(min_available_mb=2048)
        log_memory_state(f"Before {model_cfg['name']}")

        # Infrastructure: warm-up inference (discarded)
        if model_cfg["provider"] == "ollama":
            print(f"     Warming up {model_cfg['name']}...")
            warmup_client = OpenAI(
                api_key=model_cfg["api_key"],
                base_url=model_cfg["base_url"],
                timeout=httpx.Timeout(model_cfg["timeout"], connect=10.0)
            )
            warm_up_inference(warmup_client, model_cfg["model_id"], SYSTEM_PROMPT, None)

        raw_rows, accuracy, p50, p95 = run_model_benchmark(model_cfg, test_items)
        all_raw_rows.extend(raw_rows)

        log_memory_state(f"After {model_cfg['name']}")

        summary_rows.append({
            "model_name":   model_cfg["name"],
            "tier":         model_cfg["tier"],
            "params":       model_cfg["params"],
            "provider":     model_cfg["provider"],
            "accuracy_pct": accuracy,
            "latency_p50":  p50,
            "latency_p95":  p95,
            "total_inferences": len(test_items) * RUNS,
        })

        # Track LLM baseline for S³ validation
        if model_cfg["tier"] == "LLM":
            llm_accuracy = accuracy

        # Save after each model — never lose data
        save_raw_results(all_raw_rows)
        save_summary(summary_rows)

        # Infrastructure: unload Ollama model to free RAM before next model
        if model_cfg["provider"] == "ollama":
            unload_ollama_model(model_cfg["model_id"])

    # ── Final results table ────────────────────────────────────
    print()
    print("=" * 65)
    print("  UC5 BENCHMARK RESULTS")
    print("=" * 65)
    print(f"  {'Model':<20} {'Tier':<5} {'Params':<6} {'Accuracy':>9} {'P50(ms)':>9} {'P95(ms)':>9}")
    print(f"  {'-'*20} {'-'*5} {'-'*6} {'-'*9} {'-'*9} {'-'*9}")

    for row in summary_rows:
        # Flag if SLM matches LLM baseline
        flag = ""
        if row["tier"] == "SLM" and llm_accuracy:
            ratio = row["accuracy_pct"] / llm_accuracy if llm_accuracy > 0 else 0
            if ratio >= 0.85:
                flag = " ⭐ Hybrid candidate"
            elif ratio >= 0.80:
                flag = " ⚡ Approaching parity"
        if row["tier"] == "LLM":
            flag = " ← baseline"

        print(f"  {row['model_name']:<20} {row['tier']:<5} {row['params']:<6} "
              f"{row['accuracy_pct']:>8.1f}% {row['latency_p50']:>9} {row['latency_p95']:>9}"
              f"{flag}")

    print()
    if llm_accuracy:
        slm_rows = [r for r in summary_rows if r["tier"] == "SLM"]
        hybrid_slm = [r for r in slm_rows if r["accuracy_pct"] / llm_accuracy >= 0.85]
        pure_slm   = [r for r in slm_rows if r["accuracy_pct"] / llm_accuracy >= 0.95]
        print(f"  LLM baseline accuracy : {llm_accuracy}%")
        print(f"  SLMs at >= 85% parity : {len(hybrid_slm)}/{len(slm_rows)}")
        print(f"  SLMs at >= 95% parity : {len(pure_slm)}/{len(slm_rows)}")
        print()
        if pure_slm:
            print("  ⚠️  S³ PREDICTION MISMATCH:")
            print("     Some SLMs achieve Pure SLM parity (>= 95%)")
            print("     S³ predicted Hybrid — review whether fallback is needed")
        elif hybrid_slm:
            print("  ✅ S³ HYPOTHESIS SUPPORTED:")
            print("     SLMs approach but do not reach full parity with LLM")
            print("     → Hybrid assignment validated (SLMs need LLM fallback)")
        else:
            print("  ❌ S³ CONCERN:")
            print("     No SLMs reach even 85% parity with LLM")
            print("     → Task may require full LLM delegation")

    print()
    print("  Files saved:")
    print(f"    {RAW_FILE}")
    print(f"    {SUMMARY_FILE}")
    print()
    print("  NEXT STEP:")
    print("  → python3 scripts/evaluate_uc5.py")
    print("  → Computes F1, precision, recall, hallucination rate")
    print("=" * 65)
    print()
