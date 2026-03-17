"""
run_benchmark_uc6.py — UC6 Healthcare Clinical Triage Benchmark
S³ Research Project | UT Dallas | March 2026

Usage:
  python3 scripts/run_benchmark_uc6.py               # fresh run
  python3 scripts/run_benchmark_uc6.py --resume FILE  # resume from existing CSV

Pre-requisites: ollama serve (in separate terminal), GROQ_API_KEY in .env
"""

import argparse
import csv
import os
import re
import time
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SEEDS       = [42, 43, 44]
TEMPERATURE = 0.0
MAX_TOKENS  = 10
OLLAMA_BASE = "http://localhost:11434/v1"
GROQ_BASE   = "https://api.groq.com/openai/v1"
GROQ_KEY    = os.getenv("GROQ_API_KEY", "")
MAX_RETRIES = 5

VALID_LABELS = {"CRITICAL", "URGENT", "SEMIURGENT", "NONURGENT"}

SYSTEM_PROMPT = """You are a clinical triage nurse assigning emergency priority levels.

Read the triage note and respond with EXACTLY ONE of these labels:
  CRITICAL    — Immediate life threat; patient may die without intervention in < 10 minutes
  URGENT      — Potentially life-threatening; needs clinical assessment within 30 minutes
  SEMIURGENT  — Significant but currently stable; can wait up to 2 hours
  NONURGENT   — Minor complaint; routine care, no immediate risk

Rules:
- Output EXACTLY ONE WORD from the list above
- No explanation, no punctuation, no additional text
- Base your decision on chief complaint, vital signs, and history together
- When in doubt about CRITICAL vs URGENT, choose CRITICAL (under-triage is the more dangerous error)"""

USER_TEMPLATE = "Triage this patient:\n\n{presentation}"

MODELS = [
    {"name": "Llama-3.2-3B",  "model": "llama3.2:3b",            "provider": "ollama", "tier": "SLM", "params": "3B"},
    {"name": "Phi4-Mini",      "model": "phi4-mini:latest",        "provider": "ollama", "tier": "SLM", "params": "3.8B"},
    {"name": "Gemma3-4B",      "model": "gemma3:4b",               "provider": "ollama", "tier": "SLM", "params": "4B"},
    {"name": "Qwen2.5-7B",     "model": "qwen2.5:7b",              "provider": "ollama", "tier": "SLM", "params": "7B"},
    {"name": "Mistral-7B",     "model": "mistral:latest",          "provider": "ollama", "tier": "SLM", "params": "7B"},
    {"name": "Llama-3.1-8B",   "model": "llama3.1:8b",             "provider": "ollama", "tier": "SLM", "params": "8B"},
    {"name": "Llama-3.3-70B",  "model": "llama-3.3-70b-versatile", "provider": "groq",   "tier": "LLM", "params": "70B"},
]


def get_client(provider):
    if provider == "ollama":
        return OpenAI(base_url=OLLAMA_BASE, api_key="ollama",
                      http_client=httpx.Client(timeout=120.0))
    return OpenAI(base_url=GROQ_BASE, api_key=GROQ_KEY,
                  http_client=httpx.Client(timeout=60.0))


def parse_label(raw_text):
    clean = raw_text.strip().upper()
    if clean in VALID_LABELS:
        return clean, True
    for ch in ".,!?:;":
        clean = clean.replace(ch, "")
    clean = clean.strip()
    if clean in VALID_LABELS:
        return clean, True
    for label in VALID_LABELS:
        if label in clean:
            return label, True
    return clean[:20], False


def parse_retry_wait(error_str):
    """Extract suggested wait seconds from a Groq 429 error message."""
    match = re.search(r"try again in\s+(?:(\d+)m)?(\d+(?:\.\d+)?)s", str(error_str))
    if match:
        minutes = int(match.group(1) or 0)
        seconds = float(match.group(2) or 0)
        return int(minutes * 60 + seconds) + 5  # 5s buffer
    return 30  # fallback


def run_inference(client, model_id, presentation, seed):
    """Run a single inference with retry on 429 rate limit errors."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": USER_TEMPLATE.format(presentation=presentation)},
    ]
    for attempt in range(MAX_RETRIES):
        try:
            start = time.time()
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                seed=seed,
            )
            latency_ms = int((time.time() - start) * 1000)
            raw = response.choices[0].message.content or ""
            return raw.strip(), latency_ms
        except Exception as e:
            err_str = str(e)
            if "429" in err_str and attempt < MAX_RETRIES - 1:
                wait_s = parse_retry_wait(err_str)
                print(f"      ⏳ Rate limit — waiting {wait_s}s "
                      f"(attempt {attempt + 1}/{MAX_RETRIES})...")
                time.sleep(wait_s)
                continue
            raise


def load_test_items():
    path = "data/gold_sets/uc6_clinical_triage.csv"
    if not os.path.exists(path):
        raise FileNotFoundError("Gold set not found. Run build_gold_set_uc6.py first.")
    with open(path, newline="", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row["split"] == "test"]


def load_completed(resume_path):
    """Return set of (model, item_id, seed) already completed successfully."""
    done = set()
    if not resume_path or not os.path.exists(resume_path):
        return done
    with open(resume_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("pred_label", "") != "ERROR":
                done.add((row["model"], row["item_id"], row["seed"]))
    return done

def save_summary(summary_rows):
    """Save per-model summary to CSV."""
    if not summary_rows:
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("data/results", exist_ok=True)
    out_path = f"data/results/uc6_summary_{ts}.csv"
    fieldnames = list(summary_rows[0].keys())
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"  Summary saved → {out_path}")
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", metavar="FILE",
                        help="Resume from an existing raw CSV (skips completed rows)")
    args = parser.parse_args()

    print("=" * 72)
    print("  UC6 BENCHMARK — Healthcare Clinical Triage")
    print("  S³ Research Project | UT Dallas | March 2026")
    print("=" * 72)

    test_items    = load_test_items()
    n_items       = len(test_items)
    n_total       = n_items * len(MODELS) * len(SEEDS)
    completed_set = load_completed(args.resume)

    if completed_set:
        print(f"  RESUME MODE — {len(completed_set)} already done, "
              f"{n_total - len(completed_set)} remaining")
        print(f"  File: {args.resume}")
    print(f"  Test items       : {n_items}")
    print(f"  Total inferences : {n_total}")
    print()

    out_dir   = Path("data/raw_outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    if completed_set and args.resume:
        out_path  = Path(args.resume)
        file_mode = "a"
    else:
        ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path  = out_dir / f"uc6_raw_{ts}.csv"
        file_mode = "w"

    fieldnames = [
        "model", "tier", "params", "item_id", "category", "difficulty",
        "gold_label", "seed", "raw_output", "pred_label", "is_valid",
        "is_correct", "latency_ms",
    ]

    completed = len(completed_set)
    with open(out_path, file_mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if file_mode == "w":
            writer.writeheader()

        for m in MODELS:
            model_printed = False
            client = get_client(m["provider"])

            for item in test_items:
                for seed in SEEDS:
                    key = (m["name"], item["item_id"], str(seed))
                    if key in completed_set:
                        continue

                    if not model_printed:
                        print(f"  ── {m['name']} ({m['tier']}, {m['params']}) ──")
                        model_printed = True

                    try:
                        raw, latency = run_inference(
                            client, m["model"], item["presentation"], seed)
                        pred, valid  = parse_label(raw)
                        correct      = valid and (pred == item["triage_label"])
                        writer.writerow({
                            "model":      m["name"],
                            "tier":       m["tier"],
                            "params":     m["params"],
                            "item_id":    item["item_id"],
                            "category":   item["category"],
                            "difficulty": item["difficulty"],
                            "gold_label": item["triage_label"],
                            "seed":       seed,
                            "raw_output": raw,
                            "pred_label": pred,
                            "is_valid":   valid,
                            "is_correct": correct,
                            "latency_ms": latency,
                        })
                        f.flush()
                        completed += 1
                        pct = completed / n_total * 100
                        mark = "✓" if correct else ("?" if not valid else "✗")
                        print(f"    {mark} {item['item_id']} seed={seed} "
                              f"gold={item['triage_label']:<12} pred={pred:<12} "
                              f"{latency}ms  [{pct:.0f}%]")
                    except Exception as e:
                        print(f"    ❌ {item['item_id']} seed={seed} ERROR: {e}")
                        writer.writerow({
                            "model": m["name"], "tier": m["tier"], "params": m["params"],
                            "item_id": item["item_id"], "category": item["category"],
                            "difficulty": item["difficulty"], "gold_label": item["triage_label"],
                            "seed": seed, "raw_output": f"ERROR: {e}",
                            "pred_label": "ERROR", "is_valid": False,
                            "is_correct": False, "latency_ms": 0,
                        })
            if model_printed:
                print()

    print(f"  Results saved → {out_path}")
    print()
    print("  Run evaluate_uc6.py next.")
    print()


if __name__ == "__main__":
    main()