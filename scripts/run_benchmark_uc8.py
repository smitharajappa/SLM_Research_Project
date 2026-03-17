# -*- coding: utf-8 -*-
"""
run_benchmark_uc8.py
====================
S3 Research Project -- UC8 Benchmark Runner
Use Case  : Financial Report Drafting
S3 Score  : 3.80  (Hybrid tier predicted)
Category  : Cat 3 -- Multi-step Reasoning / Generation

Inference config (locked 2026-03-02):
  Models     : 6 local SLMs via Ollama + Llama-3.3-70B via Groq
  Temp       : 0.0  |  Seeds : 42, 43, 44  |  Max tokens : 512
  Test items : 30   |  Total inferences: 630

Groq rate-limit handling:
  - 2s delay between every Groq call (stays under 30 RPM)
  - Automatic retry: waits 15s / 45s / 90s on consecutive 429s
  - Use --resume to continue from last checkpoint
"""

import csv
import json
import os
import sys
import time
import argparse
from datetime import datetime

import requests

# ---------------------------------------------------------------------------
# INFERENCE CONFIG (locked 2026-03-02)
# ---------------------------------------------------------------------------
SEEDS = [42, 43, 44]
MAX_TOKENS = 512
TEMPERATURE = 0.0
GOLD_SET_PATH = "data/gold_sets/uc8_financial_report_drafting.csv"

MODELS = [
    {"name": "Llama-3.2-3B",  "tier": "SLM", "params": "3B",   "provider": "ollama", "model_tag": "llama3.2:3b"},
    {"name": "Phi4-Mini",     "tier": "SLM", "params": "3.8B", "provider": "ollama", "model_tag": "phi4-mini"},
    {"name": "Gemma3-4B",     "tier": "SLM", "params": "4B",   "provider": "ollama", "model_tag": "gemma3:4b"},
    {"name": "Qwen2.5-7B",    "tier": "SLM", "params": "7B",   "provider": "ollama", "model_tag": "qwen2.5:7b"},
    {"name": "Mistral-7B",    "tier": "SLM", "params": "7B",   "provider": "ollama", "model_tag": "mistral:latest"},
    {"name": "Llama-3.1-8B",  "tier": "SLM", "params": "8B",   "provider": "ollama", "model_tag": "llama3.1:8b"},
    {"name": "Llama-3.3-70B", "tier": "LLM", "params": "70B",  "provider": "groq",   "model_tag": "llama-3.3-70b-versatile"},
]

OLLAMA_BASE_URL = "http://localhost:11434"
GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL   = "https://api.groq.com/openai/v1"

# Groq rate-limit config
GROQ_INTER_CALL_DELAY = 2.0          # seconds between every Groq call (~30 RPM)
GROQ_RETRY_WAITS      = [15, 45, 90] # wait on consecutive 429s

RAW_OUTPUT_DIR = "data/raw_outputs"
os.makedirs(RAW_OUTPUT_DIR, exist_ok=True)

FIELDNAMES = [
    "timestamp", "model_name", "model_tier", "model_params", "provider",
    "item_id", "company_name", "period", "sector", "difficulty",
    "seed", "run_number", "raw_output", "is_valid", "latency_ms", "error"
]

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def call_ollama(model_tag: str, prompt: str, seed: int, timeout: int = 180) -> tuple:
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model_tag, "prompt": prompt, "stream": False,
        "options": {"temperature": TEMPERATURE, "seed": seed, "num_predict": MAX_TOKENS}
    }
    t0 = time.time()
    resp = requests.post(url, json=payload, timeout=timeout)
    latency_ms = (time.time() - t0) * 1000
    resp.raise_for_status()
    return resp.json().get("response", "").strip(), latency_ms


def call_groq(model_tag: str, prompt: str, seed: int, timeout: int = 60) -> tuple:
    """Call Groq with automatic retry on 429 rate-limit errors."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set.")
    url = f"{GROQ_BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": model_tag,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "seed": seed
    }
    for attempt, wait in enumerate(GROQ_RETRY_WAITS):
        t0 = time.time()
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            latency_ms = (time.time() - t0) * 1000
            if resp.status_code == 429:
                print(f"      [429] Rate limit — waiting {wait}s (attempt {attempt+1}/{len(GROQ_RETRY_WAITS)})...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip(), latency_ms
        except requests.exceptions.HTTPError as e:
            if attempt < len(GROQ_RETRY_WAITS) - 1:
                print(f"      [ERR] {e} — waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Groq call failed after all retries.")


def validate_output(text: str) -> bool:
    if not text or len(text.strip()) < 100:
        return False
    return "$" in text or "%" in text or any(c.isdigit() for c in text)


def load_gold_set(split: str = "test") -> list:
    if not os.path.exists(GOLD_SET_PATH):
        print(f"ERROR: Gold set not found at {GOLD_SET_PATH}")
        sys.exit(1)
    items = []
    with open(GOLD_SET_PATH, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["split"] == split:
                items.append(row)
    return items


def load_checkpoint(output_path: str) -> set:
    done = set()
    if not os.path.exists(output_path):
        return done
    with open(output_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("error") == "" and row.get("is_valid", "").lower() == "true":
                done.add((row["model_name"], row["item_id"], int(row["seed"])))
    return done


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def run_benchmark(resume: bool = False):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(RAW_OUTPUT_DIR, f"uc8_raw_{timestamp}.csv")

    if resume:
        existing = sorted([f for f in os.listdir(RAW_OUTPUT_DIR)
                           if f.startswith("uc8_raw_") and f.endswith(".csv")])
        if existing:
            output_path = os.path.join(RAW_OUTPUT_DIR, existing[-1])
            print(f"Resuming from: {output_path}")
        else:
            resume = False
            print("No existing UC8 file found — starting fresh.")

    checkpoint  = load_checkpoint(output_path) if resume else set()
    test_items  = load_gold_set(split="test")
    total_inferences = len(test_items) * len(MODELS) * len(SEEDS)
    completed = len(checkpoint)

    print("=" * 68)
    print("  UC8 Benchmark Runner — Financial Report Drafting")
    print(f"  S3 Score: 3.80  |  Predicted tier: Hybrid")
    print(f"  Test items: {len(test_items)}  |  Models: {len(MODELS)}  |  Seeds: {len(SEEDS)}")
    print(f"  Total inferences: {total_inferences}  |  Already done: {completed}")
    print(f"  Groq inter-call delay: {GROQ_INTER_CALL_DELAY}s  |  429 waits: {GROQ_RETRY_WAITS}s")
    print(f"  Output: {output_path}")
    print("=" * 68)

    write_header = not os.path.exists(output_path)
    run_number = 0

    with open(output_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()

        for model_cfg in MODELS:
            model_name = model_cfg["name"]
            print(f"\n  Model: {model_name} ({model_cfg['tier']} · {model_cfg['params']})")
            print(f"  {'─' * 50}")

            for item in test_items:
                for seed in SEEDS:
                    key = (model_name, item["item_id"], seed)
                    if key in checkpoint:
                        run_number += 1
                        continue

                    run_number += 1
                    prompt     = item["prompt_text"]
                    raw_output = ""
                    is_valid   = False
                    latency_ms = 0.0
                    error_msg  = ""

                    try:
                        if model_cfg["provider"] == "ollama":
                            raw_output, latency_ms = call_ollama(model_cfg["model_tag"], prompt, seed)
                        else:
                            raw_output, latency_ms = call_groq(model_cfg["model_tag"], prompt, seed)
                        is_valid = validate_output(raw_output)
                        status = "OK " if is_valid else "INV"
                    except Exception as e:
                        error_msg = str(e)[:200]
                        status = "ERR"

                    row = {
                        "timestamp": datetime.now().isoformat(),
                        "model_name": model_name, "model_tier": model_cfg["tier"],
                        "model_params": model_cfg["params"], "provider": model_cfg["provider"],
                        "item_id": item["item_id"], "company_name": item["company_name"],
                        "period": item["period"], "sector": item["sector"],
                        "difficulty": item["difficulty"], "seed": seed,
                        "run_number": run_number, "raw_output": raw_output,
                        "is_valid": is_valid, "latency_ms": f"{latency_ms:.0f}",
                        "error": error_msg,
                    }
                    writer.writerow(row)
                    f.flush()

                    pct = run_number / total_inferences * 100
                    print(f"    [{status}] {item['item_id']} seed={seed} "
                          f"{latency_ms:.0f}ms  ({pct:.1f}%)")

                    # Paced delay after every Groq call
                    if model_cfg["provider"] == "groq":
                        time.sleep(GROQ_INTER_CALL_DELAY)

    # Summary
    valid_count = error_count = invalid_count = 0
    with open(output_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("error"):
                error_count += 1
            elif row.get("is_valid", "").lower() == "true":
                valid_count += 1
            else:
                invalid_count += 1

    print()
    print("=" * 68)
    print("  BENCHMARK COMPLETE")
    print(f"  Valid: {valid_count}  |  Invalid: {invalid_count}  |  Errors: {error_count}")
    if error_count > 0:
        print(f"  Re-run with --resume to retry {error_count} failed calls.")
    else:
        print("  All 630 inferences valid. Ready for evaluate_uc8.py")
    print(f"  Output: {output_path}")
    print("=" * 68)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run_benchmark(resume=args.resume)