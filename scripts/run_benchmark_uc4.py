"""
run_benchmark_uc4.py
Runs all 7 models against UC4 test set.
30 test items × 7 models × 3 runs = 630 inferences

Key difference from UC1:
  - 3-class output: POSITIVE / NEGATIVE / NEUTRAL
  - System prompt updated for 3-class task
  - clean_response handles all three labels
"""

import os, csv, json, time, re, httpx
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from benchmark_utils import log_memory_state, check_memory, unload_ollama_model, warm_up_inference

load_dotenv()

GOLD_SET_PATH  = "data/gold_sets/uc4_product_review_sentiment.csv"
RAW_OUTPUT_DIR = "data/raw_outputs"
RESULTS_DIR    = "data/results"
os.makedirs(RAW_OUTPUT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR,    exist_ok=True)

TIMESTAMP    = datetime.now().strftime("%Y%m%d_%H%M%S")
RAW_FILE     = os.path.join(RAW_OUTPUT_DIR, f"uc4_raw_{TIMESTAMP}.csv")
SUMMARY_FILE = os.path.join(RESULTS_DIR,    f"uc4_summary_{TIMESTAMP}.csv")

TEMPERATURE = 0.0
MAX_TOKENS  = 128
SEEDS       = [42, 43, 44]
RUNS        = len(SEEDS)

MODELS = [
    { "name": "Llama-3.2-3B",  "model_id": "llama3.2:3b",               "provider": "ollama", "base_url": "http://localhost:11434/v1", "api_key": "ollama", "tier": "SLM", "params": "3B",   "delay": 1.0, "timeout": 300.0 },
    { "name": "Phi4-Mini",     "model_id": "phi4-mini:latest",           "provider": "ollama", "base_url": "http://localhost:11434/v1", "api_key": "ollama", "tier": "SLM", "params": "3.8B", "delay": 1.0, "timeout": 300.0 },
    { "name": "Gemma3-4B",     "model_id": "gemma3:4b",                  "provider": "ollama", "base_url": "http://localhost:11434/v1", "api_key": "ollama", "tier": "SLM", "params": "4B",   "delay": 1.0, "timeout": 300.0 },
    { "name": "Qwen2.5-7B",    "model_id": "qwen2.5:7b",                 "provider": "ollama", "base_url": "http://localhost:11434/v1", "api_key": "ollama", "tier": "SLM", "params": "7B",   "delay": 1.0, "timeout": 300.0 },
    { "name": "Mistral-7B",    "model_id": "mistral:latest",             "provider": "ollama", "base_url": "http://localhost:11434/v1", "api_key": "ollama", "tier": "SLM", "params": "7B",   "delay": 1.0, "timeout": 300.0 },
    { "name": "Llama-3.1-8B",  "model_id": "llama3.1:8b",               "provider": "ollama", "base_url": "http://localhost:11434/v1", "api_key": "ollama", "tier": "SLM", "params": "8B",   "delay": 1.0, "timeout": 300.0 },
    { "name": "Llama-3.3-70B", "model_id": "llama-3.3-70b-versatile",   "provider": "groq",   "base_url": "https://api.groq.com/openai/v1", "api_key": os.getenv("GROQ_API_KEY"), "tier": "LLM", "params": "70B", "delay": 2.0, "timeout": 30.0 },
]

SYSTEM_PROMPT = (
    "You are a sentiment classification system. "
    "Classify the product review as POSITIVE, NEGATIVE, or NEUTRAL. "
    "POSITIVE = overall satisfied, recommends the product. "
    "NEGATIVE = overall dissatisfied, does not recommend. "
    "NEUTRAL = mixed feelings, neither clearly positive nor negative. "
    "Reply with exactly ONE word: POSITIVE, NEGATIVE, or NEUTRAL. "
    "No explanation. No punctuation. Just one word."
)

VALID_LABELS = {"POSITIVE", "NEGATIVE", "NEUTRAL"}

def load_test_items():
    items = []
    with open(GOLD_SET_PATH, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["split"] == "test":
                items.append(row)
    return items

def clean_response(raw):
    cleaned = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip().upper()
    for label in VALID_LABELS:
        if label in cleaned:
            return label
    return "INVALID"

def run_inference(model_cfg, item, run_idx):
    try:
        client = OpenAI(
            api_key=model_cfg["api_key"],
            base_url=model_cfg["base_url"],
            timeout=httpx.Timeout(model_cfg["timeout"], connect=10.0)
        )
        start    = time.time()
        response = client.chat.completions.create(
            model=model_cfg["model_id"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Classify this product review: {item['text']}"}
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

def run_model_benchmark(model_cfg, test_items):
    print(f"\n  ── {model_cfg['name']} ({model_cfg['tier']} · {model_cfg['params']}) ──")
    print(f"     {len(test_items)} items × {RUNS} runs = {len(test_items)*RUNS} inferences")

    rows      = []
    latencies = []

    for item in test_items:
        for run_idx in range(RUNS):
            result, latency, raw, error = run_inference(model_cfg, item, run_idx)
            correct = (result == item["label"]) if result not in ["ERROR","INVALID"] else False
            rows.append({
                "timestamp":    datetime.now().isoformat(),
                "model_name":   model_cfg["name"],
                "model_tier":   model_cfg["tier"],
                "model_params": model_cfg["params"],
                "provider":     model_cfg["provider"],
                "item_id":      item["id"],
                "item_text":    item["text"][:80] + "..." if len(item["text"]) > 80 else item["text"],
                "gold_label":   item["label"],
                "category":     item["category"],
                "difficulty":   item["difficulty"],
                "run_number":   run_idx + 1,
                "prediction":   result,
                "correct":      correct,
                "latency_ms":   latency,
                "raw_output":   raw[:200] if raw else "",
                "error":        error or "",
            })
            latencies.append(latency)
            icon = "✓" if correct else "✗" if result != "ERROR" else "E"
            print(f"     [{item['id']}] run{run_idx+1}: {result:<10} {icon}  ({latency}ms)", end="\r")
        time.sleep(model_cfg["delay"])

    total_inf   = len(test_items) * RUNS
    total_cor   = sum(1 for r in rows if r["correct"])
    # NOTE: quick-run accuracy only — includes INVALID in denominator.
    # For paper figures always use evaluate_uc4.py output, not this summary CSV.
    accuracy    = round(total_cor / total_inf * 100, 1)
    valid_lats  = sorted([l for l in latencies if l > 0])
    p50 = valid_lats[len(valid_lats)//2]          if valid_lats else 0
    p95 = valid_lats[int(len(valid_lats)*0.95)]   if valid_lats else 0
    print(f"\n     ✅ Done — Accuracy: {accuracy}%  |  P50: {p50}ms  |  P95: {p95}ms")
    return rows, accuracy, p50, p95

def save_csv(path, rows):
    if not rows: return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    print()
    print("=" * 65)
    print("  UC4 BENCHMARK — Product Review Sentiment")
    print("  7 models × 30 test items × 3 runs = 630 inferences")
    print("  3-class output: POSITIVE / NEGATIVE / NEUTRAL")
    print(f"  S³ Score: 2.1  →  Pure SLM predicted")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    test_items = load_test_items()
    print(f"\n  Loaded {len(test_items)} test items")

    all_rows     = []
    summary_rows = []
    llm_accuracy = None

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
        all_rows.extend(raw_rows)

        log_memory_state(f"After {model_cfg['name']}")

        summary_rows.append({
            "model_name":       model_cfg["name"],
            "tier":             model_cfg["tier"],
            "params":           model_cfg["params"],
            "provider":         model_cfg["provider"],
            "accuracy_pct":     accuracy,
            "latency_p50":      p50,
            "latency_p95":      p95,
            "total_inferences": len(test_items) * RUNS,
        })
        if model_cfg["tier"] == "LLM":
            llm_accuracy = accuracy
        save_csv(RAW_FILE, all_rows)
        save_csv(SUMMARY_FILE, summary_rows)

        # Infrastructure: unload Ollama model to free RAM before next model
        if model_cfg["provider"] == "ollama":
            unload_ollama_model(model_cfg["model_id"])

    # ── Results table ──────────────────────────────────────────
    print()
    print("=" * 65)
    print("  UC4 BENCHMARK RESULTS — Product Review Sentiment")
    print("=" * 65)
    print(f"  {'Model':<20} {'Tier':<5} {'Params':<6} {'Accuracy':>9} {'P50(ms)':>9} {'P95(ms)':>9}")
    print(f"  {'-'*20} {'-'*5} {'-'*6} {'-'*9} {'-'*9} {'-'*9}")

    for row in summary_rows:
        flag = ""
        if row["tier"] == "SLM" and llm_accuracy:
            ratio = row["accuracy_pct"] / llm_accuracy * 100 if llm_accuracy > 0 else 0
            if ratio >= 95:   flag = " ✅ Pure SLM confirmed"
            elif ratio >= 90: flag = " ⭐ Strong SLM"
        if row["tier"] == "LLM":
            flag = " ← baseline"
        print(f"  {row['model_name']:<20} {row['tier']:<5} {row['params']:<6} "
              f"{row['accuracy_pct']:>8.1f}% {row['latency_p50']:>9} {row['latency_p95']:>9}{flag}")

    print()
    if llm_accuracy:
        slm_rows   = [r for r in summary_rows if r["tier"] == "SLM"]
        pure_slm   = [r for r in slm_rows if r["accuracy_pct"] / llm_accuracy >= 0.95]
        print(f"  LLM baseline accuracy  : {llm_accuracy}%")
        print(f"  SLMs at >= 95% parity  : {len(pure_slm)}/{len(slm_rows)}")
        print(f"  S³ prediction          : Pure SLM (score 2.1)")
        if pure_slm:
            print()
            print("  ✅ H4.3 SUPPORTED: UC4 GRADUATES TO PURE SLM")
            print("     SLMs achieve >= 95% LLM parity on sentiment classification")
        else:
            print()
            print("  ⚠️  H4.3 NOT SUPPORTED — review results")

    print()
    print("  Files saved:")
    print(f"    {RAW_FILE}")
    print(f"    {SUMMARY_FILE}")
    print()
    print("  NEXT STEP:")
    print("  → python3 scripts/evaluate_uc4.py")
    print("=" * 65)
    print()