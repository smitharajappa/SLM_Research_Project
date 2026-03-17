"""
verify_apis.py — FINAL VERSION
Local : 7 SLM models via Ollama (unlimited, free)
Cloud : 2 models via Groq (14,400 req/day, free)
Total : 9 models across full 3B-70B parameter range

Usage:
  python3 scripts/verify_apis.py
"""

import os
import re
import time
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TEST_PROMPT = (
    "Classify this SMS as THREAT or BENIGN.\n"
    "Reply with ONE WORD ONLY — no explanation.\n"
    "SMS: 'Your bank account suspended. Click now: bit.ly/3xR9k'"
)

OLLAMA_BASE = "http://localhost:11434/v1"
GROQ_BASE   = "https://api.groq.com/openai/v1"
GROQ_KEY    = os.getenv("GROQ_API_KEY")

# ── 7 local models — full 3B to 8B parameter spectrum ─────────
LOCAL_MODELS = [
    {
        "name":  "Llama-3.2-3B",
        "model": "llama3.2:3b",
        "role":  "Pure SLM demo — 3B ⭐",
        "params": "3B"
    },
    {
        "name":  "Phi4-Mini",
        "model": "phi4-mini:latest",
        "role":  "Microsoft SLM — 3.8B",
        "params": "3.8B"
    },
    {
        "name":  "Gemma3-4B",
        "model": "gemma3:4b",
        "role":  "Google SLM — 4B",
        "params": "4B"
    },
    {
        "name":  "Qwen2.5-7B",
        "model": "qwen2.5:7b",
        "role":  "Alibaba SLM — 7B",
        "params": "7B"
    },
    {
        "name":  "Mistral-7B",
        "model": "mistral:latest",
        "role":  "Speed baseline — 7B",
        "params": "7B"
    },
    {
        "name":  "Llama-3.1-8B",
        "model": "llama3.1:8b",
        "role":  "SLM killer pair ⭐ — 8B",
        "params": "8B"
    },
    {
        "name":  "DeepSeek-R1-8B",
        "model": "deepseek-r1:8b",
        "role":  "Reasoning LLM local — 8B",
        "params": "8B"
    },
]

# ── 2 cloud models — LLM comparison baseline ──────────────────
CLOUD_MODELS = [
    {
        "name":  "Llama-3.1-8B (Groq)",
        "model": "llama-3.1-8b-instant",
        "role":  "Local vs cloud cross-check",
        "params": "8B"
    },
    {
        "name":  "Llama-3.3-70B (Groq)",
        "model": "llama-3.3-70b-versatile",
        "role":  "LLM killer pair ⭐ — 70B",
        "params": "70B"
    },
]


def clean_response(raw: str) -> str:
    """Strip think blocks and normalize to THREAT / BENIGN."""
    cleaned = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
    cleaned = cleaned.strip().upper()
    if "THREAT" in cleaned:
        return "THREAT"
    if "BENIGN" in cleaned:
        return "BENIGN"
    first = re.sub(r'[^A-Z]', '', cleaned.split()[0]) if cleaned.split() else ""
    return f"?{first[:12]}" if first else "?EMPTY"


def test_local(config):
    print(f"\n  [{config['params']:<4}] Loading {config['name']}  —  {config['role']}")
    print(f"         ⏳ Please wait up to 90s for first load...")
    try:
        client = OpenAI(
            api_key="ollama",
            base_url=OLLAMA_BASE,
            timeout=httpx.Timeout(300.0, connect=10.0)
        )
        start = time.time()
        response = client.chat.completions.create(
            model=config["model"],
            messages=[
                {"role": "system",
                 "content": "You are a binary SMS classifier. Reply ONE word: THREAT or BENIGN."},
                {"role": "user", "content": TEST_PROMPT}
            ],
            temperature=0.0,
            max_tokens=80,
        )
        latency = round((time.time() - start) * 1000)
        result  = clean_response(response.choices[0].message.content)
        correct = result in ["THREAT", "BENIGN"]
        icon    = "✅" if correct else "⚠️ "
        print(f"         {icon} {config['name']:<18} → {result:<8}  ({latency}ms)")
        return correct, latency

    except Exception as e:
        print(f"         ❌ {config['name']:<18} → FAILED")
        print(f"            └─ {str(e)[:75]}")
        if "11434" in str(e) or "Connection" in str(e):
            print(f"            💡 Check: curl http://localhost:11434")
        return False, 0


def test_cloud(config):
    try:
        client = OpenAI(
            api_key=GROQ_KEY,
            base_url=GROQ_BASE,
            timeout=httpx.Timeout(30.0)
        )
        start = time.time()
        response = client.chat.completions.create(
            model=config["model"],
            messages=[
                {"role": "system",
                 "content": "Reply ONE word only: THREAT or BENIGN."},
                {"role": "user", "content": TEST_PROMPT}
            ],
            temperature=0.0,
            max_tokens=10,
        )
        latency = round((time.time() - start) * 1000)
        result  = clean_response(response.choices[0].message.content)
        correct = result in ["THREAT", "BENIGN"]
        icon    = "✅" if correct else "⚠️ "
        print(f"  {icon} [{config['params']:<4}] {config['name']:<28} → {result:<8}  ({latency}ms)")
        return correct, latency

    except Exception as e:
        print(f"  ❌ [{config['params']:<4}] {config['name']:<28} → FAILED")
        print(f"     └─ {str(e)[:75]}")
        if "401" in str(e):
            print(f"     💡 Check GROQ_API_KEY in .env")
        if "429" in str(e):
            print(f"     💡 Rate limit — wait 60s and retry")
        return False, 0


if __name__ == "__main__":

    print()
    print("=" * 65)
    print("  SLM Research — FINAL API Verification")
    print("  Local : 7 models via Ollama  (3B → 8B, unlimited)")
    print("  Cloud : 2 models via Groq    (70B, 14,400 req/day)")
    print("  Time  : ~8-12 minutes")
    print("=" * 65)

    # ── Local models ───────────────────────────────────────────
    print()
    print("  ══ LOCAL MODELS — Ollama (3B → 8B spectrum) ══════")
    local_results = []
    local_latencies = []
    for i, m in enumerate(LOCAL_MODELS):
        ok, lat = test_local(m)
        local_results.append(ok)
        local_latencies.append(lat)
        if i < len(LOCAL_MODELS) - 1:
            print(f"         ⏸  8s pause — freeing RAM...")
            time.sleep(8)

    # ── Cloud models ───────────────────────────────────────────
    print()
    print("  ══ CLOUD MODELS — Groq (LLM baseline) ════════════")
    cloud_results = []
    cloud_latencies = []
    for m in CLOUD_MODELS:
        ok, lat = test_cloud(m)
        cloud_results.append(ok)
        cloud_latencies.append(lat)
        time.sleep(2)

    # ── Summary ────────────────────────────────────────────────
    lp = sum(local_results)
    cp = sum(cloud_results)
    tp = lp + cp
    lt = len(local_results)
    ct = len(cloud_results)

    # Latency comparison — the first finding
    llama_local = local_latencies[5] if local_latencies[5] > 0 else None
    llama_cloud = cloud_latencies[0] if cloud_latencies[0] > 0 else None

    print()
    print("=" * 65)
    print(f"  Local  (Ollama) : {lp}/{lt} passed")
    print(f"  Cloud  (Groq)   : {cp}/{ct} passed")
    print(f"  Total           : {tp}/{lt+ct} passed")

    if llama_local and llama_cloud:
        ratio = round(llama_local / llama_cloud)
        print()
        print(f"  ── FIRST RESEARCH FINDING ─────────────────────────")
        print(f"  Llama-3.1-8B local  : {llama_local}ms")
        print(f"  Llama-3.1-8B cloud  : {llama_cloud}ms")
        print(f"  Latency ratio       : {ratio}× slower local vs cloud")
        print(f"  → Cloud SLM wins on latency for real-time tasks")
        print(f"  → Local SLM wins on cost for batch tasks ($0/call)")

    print()
    if tp == lt + ct:
        print("  ✅  ALL SYSTEMS GO — benchmark infrastructure ready")
        print()
        print("  YOUR CONFIRMED RESEARCH STACK:")
        print("  ┌────────────────────────────────────────────────┐")
        print("  │  SLMs (local)  3B → 8B  · Ollama · Free       │")
        print("  │  LLM  (cloud)  70B      · Groq   · Free       │")
        print("  │  Killer pair:  Llama-3.1-8B vs Llama-3.3-70B  │")
        print("  │  Pure SLM:     Llama-3.2-3B  ⭐               │")
        print("  │  Total cost:   $0                              │")
        print("  └────────────────────────────────────────────────┘")
        print()
        print("  NEXT STEP:")
        print("  → python3 scripts/build_gold_set_uc1.py")
        print("  → Build 100-item SMS Threat Detection gold set")
    elif tp >= 7:
        print("  ✅  BENCHMARK READY — fix remaining model separately")
    else:
        print("  ⚠️   Check failed models above before proceeding")

    print("=" * 65)
    print()
