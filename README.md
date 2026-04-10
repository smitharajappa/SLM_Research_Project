# Suitability Framework: Decision Framework for Small Language Model Deployment

**Suitability Score for SLM Selection (S3) and SDDF Runtime Routing**

A complete two-stage deployment decision architecture for enterprise Small Language Model (SLM) systems. This project benchmarks SLMs (3B-8B parameters) against LLMs (70B) across eight pre-registered enterprise use cases to validate whether task type — not model scale — governs SLM deployment suitability.

> **Paper**: *Decision Framework and Industrial Deployment Protocol for Small Language Models in Agentic AI Systems*
> **Authors**: Smitha Rajappa, Riddhima Ramasahayam Reddy, Rohit Savant, Yashraj Saxena, Smita Sengupta 
> **Professor**: Dr. Ashim Bose
> **Institution**: University of Texas at Dallas

---

## Table of Contents

- [Overview](#overview)
- [The S3 Formula](#the-s3-formula)
  - [Dynamic Denominator WSM](#dynamic-denominator-wsm)
  - [Scoring Dimensions](#scoring-dimensions)
  - [Weight Assignment](#weight-assignment)
  - [Tier Boundaries](#tier-boundaries)
  - [Pre-Screening Gate](#pre-screening-gate)
  - [Worked Example](#worked-example)
- [Use Cases](#use-cases)
- [Project Structure](#project-structure)
- [Hardware Requirements](#hardware-requirements)
- [Installation Guide](#installation-guide)
  - [1. System Prerequisites](#1-system-prerequisites)
  - [2. Install Ollama](#2-install-ollama)
  - [3. Download Models](#3-download-models)
  - [4. Python Environment](#4-python-environment)
  - [5. API Keys](#5-api-keys)
- [Running Benchmarks](#running-benchmarks)
  - [Step 1: Verify Infrastructure](#step-1-verify-infrastructure)
  - [Step 2: Build Gold Sets](#step-2-build-gold-sets)
  - [Step 3: Run Benchmarks](#step-3-run-benchmarks)
  - [Step 4: Evaluate Results](#step-4-evaluate-results)
- [Model Registry](#model-registry)
- [Inference Configuration](#inference-configuration)
- [Key Results](#key-results)
- [Known Limitations](#known-limitations)
- [Citation](#citation)
- [License](#license)

---

## Overview

Enterprise adoption of LLMs faces a fundamental scaling constraint: API cost differentials across model tiers reach two orders of magnitude. This project asks: **for which tasks can a 3-8B parameter SLM replace a 70B LLM without meaningful quality loss?**

The S3 framework provides a **pre-deployment scoring instrument** that predicts the answer before running any inference. The SDDF framework provides **runtime query-level routing** that operationalises the prediction in production.

**Core finding**: Task type accounts for the majority of SLM performance variance. The same 3B model moves 36.6 percentage points between two use cases; the 70B LLM moves only 6.7pp across the same two tasks. S3 predicts this variance before any model is run.

---

## The S3 Formula

### Dynamic Denominator WSM

S3 uses a Weighted Sum Model (WSM) with a dynamic denominator:

```
S3 = [ Sum(Score_i * w_i) ] / [ Sum(5 * w_i) ] * 5
```

Where:
- `Score_i` is the raw score (1-5) assigned to dimension `i`
- `w_i` is the organisational weight (integer 1-5) for dimension `i`
- `Sum(5 * w_i)` is the dynamic denominator (the exact maximum possible weighted sum)

**Key property**: The dynamic denominator guarantees `S3 in [1, 5]` under **any** valid weight configuration:
- When all scores = 1: S3 = 1 exactly
- When all scores = 5: S3 = 5 exactly
- The output range is identical regardless of the specific weight values chosen

This enables **threshold portability** across organisations with different risk profiles.

### Scoring Dimensions

Each task is scored on six dimensions. Score 1 = SLM optimal; Score 5 = LLM likely required.

| Dimension | Score 1 | Score 2 | Score 3 | Score 4 | Score 5 | What It Measures |
|-----------|---------|---------|---------|---------|---------|------------------|
| **Task Complexity (TC)** | Binary classification | Multi-class classification | Multi-step extraction | Reasoning with context | Expert-level judgment under ambiguity | Cognitive demand on the model at inference time |
| **Output Structure (OS)** | Free-form text | Loose paragraph | One-of-N labels | Strict JSON schema | Exact single value/code token | Degree of output format constraint |
| **Stakes (SK)** | No consequence | Minor inconvenience | Business impact, rework required | Significant harm, affects persons | Severe, irreversible, legally consequential | Maximum consequence of incorrect output |
| **Data Sensitivity (DS)** | Fully public | Semi-public/internal | Personal data, not regulated | Regulated PII/PHI | Classified/ITAR-controlled | Governs deployment location |
| **Latency Requirement (LT)** | Batch (hours) | Background (minutes) | Interactive (P95 < 2s) | Near real-time (P95 < 500ms) | Real-time (P95 < 100ms) | P95 SLA compliance |
| **Volume (VL)** | Dozens/day | Hundreds/day | Thousands/day | Tens of thousands/day | Millions/day | Throughput scale |

**Scoring rule**: Score dimensions for the specific inference the model performs in production. Score the hardest representative item type appearing in more than 5% of production volume.

### Weight Assignment

Weights are integers 1-5, assigned via SMART direct-rating (Edwards and Barron, 1994). Each weight reflects how much that dimension influences deployment tier decisions in your organisation.

| Weight | Label | Meaning |
|--------|-------|---------|
| 1 | Negligible | Minimal influence on tier decision |
| 2 | Low | Considered but rarely drives escalation |
| 3 | Moderate | Important, regularly influences the score |
| 4 | High | Frequently determines the tier outcome |
| 5 | Dominant | Almost always determines the deployment tier |

**Hard constraint**: `w_SK >= w_TC` must hold for any valid weight profile. The swing from SK=1 (no consequence) to SK=5 (irreversible harm) is at least as consequential as TC=1 to TC=5 for any rational enterprise decision-maker.

**Default weight profile used in this study**:

| Dimension | TC | OS | SK | DS | LT | VL |
|-----------|----|----|----|----|----|----|
| Weight | 3 | 2 | 4 | 2 | 3 | 1 |

Dynamic denominator = 5 x (3 + 2 + 4 + 2 + 3 + 1) = **75**

### Tier Boundaries

S3 maps to three deployment tiers:

```
S3 <= 3.2          -->  Pure SLM     (SLM handles task autonomously)
3.2 < S3 <= 4.0    -->  Hybrid       (SLM primary + LLM fallback)
S3 > 4.0           -->  LLM Only     (LLM required for quality/safety)
```

These thresholds are initialised from scoring scale geometry (55th and 75th percentiles of [1,5]) and validated for internal stability via sensitivity analysis. They are **provisional** — full empirical calibration via UTADIS linear programming is planned at N >= 50 confirmed deployment outcomes.

### Pre-Screening Gate

Before computing S3, a non-compensatory gate is applied. This prevents the weighted average from masking disqualifying conditions:

| Stakes (SK) | Task Complexity (TC) | Gate Decision |
|-------------|---------------------|---------------|
| 5 | Any | **DISQUALIFY** — Hard Rule 1. No autonomous deployment. |
| >= 4 | 5 | **DISQUALIFY** — Hard Rule 2. Expert reasoning under severe consequences. |
| >= 4 | <= 4 | **PASS WITH FLAG** — Minimum tier = Hybrid regardless of S3 score. |
| <= 3 | Any | **PASS** — Proceed to S3 weighted scoring. |

**Why the gate exists**: WSM is a fully compensatory model — a high latency score could mathematically offset a catastrophic stakes score. The gate makes S3 non-compensatory where it matters most (safety) and compensatory everywhere else.

### Worked Example

**UC4 — Product Review Sentiment** vs **UC1 — SMS Threat Detection**

Both use the same weight profile. The only major difference is Stakes (1 vs 4):

| Dimension | UC4 Score | UC1 Score | Weight | UC4 Score x Weight | UC1 Score x Weight |
|-----------|-----------|-----------|--------|--------------------|--------------------|
| TC | 1 | 2 | 3 | 3 | 6 |
| OS | 3 | 3 | 2 | 6 | 6 |
| SK | 1 | 4 | 4 | 4 | 16 |
| DS | 1 | 2 | 2 | 2 | 4 |
| LT | 3 | 2 | 3 | 9 | 6 |
| VL | 3 | 1 | 1 | 3 | 1 |
| **Sum** | | | | **27** | **39** |

```
UC4: S3 = 27/75 x 5 = 1.80  -->  Pure SLM (confirmed: 100% parity)
UC1: S3 = 39/75 x 5 = 2.60  -->  Formula says Pure SLM, but SK=4 triggers
                                   Flag Rule --> Hybrid (confirmed: Mistral-7B
                                   100% threat recall, but LLM fallback needed
                                   for edge cases)
```

The 12-point numerator difference comes **entirely from Stakes**. This demonstrates why Stakes carries the highest weight and why the Flag Rule exists.

---

## Use Cases

Eight pre-registered enterprise use cases spanning all three deployment tiers:

| UC | Domain | Task Type | S3 Score | Predicted Tier | Gate Rule | Status |
|----|--------|-----------|----------|----------------|-----------|--------|
| UC1 | SMS Threat Detection | Binary classification | 3.10 | Hybrid | SK=4 Flag Rule | Confirmed |
| UC2 | Invoice Field Extraction | Structured JSON extraction | 2.56 | Pure SLM | None | Confirmed |
| UC3 | Support Ticket Routing | 6-way classification | 2.67 | Pure SLM | None | Confirmed |
| UC4 | Product Review Sentiment | 3-way classification | 2.10 | Pure SLM | None | Confirmed |
| UC5 | Automated Code Review | 5-way classification | 3.33 | Hybrid | None (formula only) | Pending |
| UC6 | Healthcare Clinical Triage | 4-way classification | 4.44 | LLM Only | SK=5 Hard Rule 1 | Confirmed |
| UC7 | Legal Contract Analysis | 4-way risk classification | 3.60 | Hybrid | SK=4 Flag Rule | Pending |
| UC8 | Financial Report Drafting | Free-form generation | 3.80 | Hybrid | None (formula only) | Confirmed |

**Pre-registration date**: 2 March 2026 (ID: S3-UTD-2026-03-02). All hypotheses, metrics, and gold sets were locked before any inference, following Gelman and Loken (2014).

---

## Project Structure

```
SLM_Research_Project/
|
|-- configs/
|   |-- models.json               # Model registry (SLM + LLM tiers)
|   |-- inference_config.json      # Locked inference parameters
|
|-- scripts/
|   |-- verify_apis.py             # Health check for all models
|   |-- build_gold_set_uc[N].py    # Generate gold sets (100 items each)
|   |-- run_benchmark_uc[N].py     # Run inference benchmarks
|   |-- evaluate_uc[N].py          # Compute evaluation metrics
|
|-- data/
|   |-- gold_sets/                 # Pre-registered test sets (CSV + metadata JSON)
|   |   |-- uc[N]_*.csv            # 100-item gold sets
|   |   |-- uc[N]_metadata.json    # S3 scores, hypotheses, dimensions
|   |-- raw_outputs/               # Raw inference results per benchmark run
|   |-- results/                   # Aggregated per-model summary metrics
|
|-- evaluation/                    # Evaluation reports (TXT + CSV)
|
|-- README.md                      # This file
```

**Workflow for each use case**:
```
build_gold_set_ucN.py  -->  run_benchmark_ucN.py  -->  evaluate_ucN.py
   (creates gold set)      (runs 630 inferences)     (computes metrics + report)
```

---

## Hardware Requirements

### Minimum Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **RAM** | 16 GB | 32 GB | 16 GB causes memory pressure with 7-8B models |
| **CPU** | 8 cores | 10+ cores | Apple Silicon or modern x86_64 |
| **Disk** | 30 GB free | 50 GB free | For Ollama model files |
| **OS** | macOS 13+ / Ubuntu 22.04+ | Latest | Ollama requires modern OS |
| **GPU** | Not required | NVIDIA 8GB+ VRAM | Dramatically reduces latency |

### Hardware Used in This Study

```
Machine:    MacBook Pro (Model 14,9)
Chip:       Apple M2 Pro
Cores:      10 (6 Performance + 4 Efficiency)
RAM:        16 GB unified memory
GPU:        Integrated (Apple Neural Engine) — no discrete GPU
OS:         macOS (arm64)
Inference:  CPU-only via Ollama (no GPU acceleration)
```

### Memory Budget per Model

Ollama uses quantised models (typically Q4_K_M). Approximate memory requirements:

| Model | Parameters | Quantised Size | RAM Needed (weights + KV cache) |
|-------|-----------|---------------|--------------------------------|
| Llama-3.2-3B | 3B | ~2.0 GB | ~3-4 GB |
| Phi4-Mini | 3.8B | ~2.5 GB | ~4-5 GB |
| Gemma3-4B | 4B | ~2.8 GB | ~4-5 GB |
| Qwen2.5-7B | 7B | ~4.5 GB | ~6-8 GB |
| Mistral-7B | 7B | ~4.5 GB | ~6-8 GB |
| Llama-3.1-8B | 8B | ~5.0 GB | ~7-9 GB |

**Important**: On a 16 GB machine, 7-8B models leave minimal headroom for the OS and KV cache, causing memory pressure and swap. This affects **latency** (not accuracy). See [Known Limitations](#known-limitations).

### Latency Expectations

All latency numbers below are from CPU-only inference on M2 Pro 16GB. GPU deployments are expected to be 10-50x faster.

| Model | UC1 (128 tok) P50/P95 | UC8 (1024 tok) P50/P95 |
|-------|----------------------|----------------------|
| Llama-3.2-3B | 210 / 978ms | 9,055 / 11,802ms |
| Mistral-7B | 155 / 418ms | 17,045 / 20,654ms |
| Llama-3.1-8B | 331 / 2,413ms | 19,793 / 25,680ms |
| Llama-3.3-70B (Groq) | 319 / 2,428ms | 1,332 / 1,540ms |

---

## Installation Guide

### 1. System Prerequisites

```bash
# Verify system
uname -m          # Should show arm64 (Apple Silicon) or x86_64
python3 --version # Requires Python 3.8+
```

### 2. Install Ollama

Ollama runs LLMs locally. It manages model downloads, quantisation, and serving.

**macOS**:
```bash
# Download and install from https://ollama.com/download
# Or via Homebrew:
brew install ollama
```

**Linux**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Verify installation**:
```bash
ollama --version
# Expected: ollama version 0.6.x or later
```

**Start the Ollama server**:
```bash
# Start in background (required before running benchmarks)
ollama serve

# In a separate terminal, verify it's running:
curl http://localhost:11434
# Expected: "Ollama is running"
```

### 3. Download Models

Download all six SLM models and verify each one responds correctly:

```bash
# Small models (3-4B) — fast download, fits easily in 16GB RAM
ollama pull llama3.2:3b
ollama pull phi4-mini:latest
ollama pull gemma3:4b

# Medium models (7-8B) — larger download, needs 8GB+ free RAM
ollama pull qwen2.5:7b
ollama pull mistral:latest
ollama pull llama3.1:8b
```

**Verify each model works**:
```bash
# Quick test — should return a classification
ollama run llama3.2:3b "Classify as THREAT or BENIGN: You won a free iPhone! Click here."

# Check model sizes
ollama list
```

**Expected output from `ollama list`**:
```
NAME                 SIZE
llama3.2:3b          2.0 GB
phi4-mini:latest     2.5 GB
gemma3:4b            3.3 GB
qwen2.5:7b           4.7 GB
mistral:latest       4.1 GB
llama3.1:8b          4.9 GB
```

**Total disk space**: ~21.5 GB for all six models.

### 4. Python Environment

```bash
# Clone the repository
git clone https://github.com/<your-org>/SLM_Research_Project.git
cd SLM_Research_Project

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install openai httpx python-dotenv psutil
```

**Required packages**:

| Package | Version | Purpose |
|---------|---------|---------|
| `openai` | >= 1.0 | OpenAI-compatible API client (works with Ollama and Groq) |
| `httpx` | >= 0.24 | HTTP client with timeout support |
| `python-dotenv` | >= 1.0 | Load API keys from .env file |
| `psutil` | >= 5.9 | Memory monitoring (optional but recommended) |

### 5. API Keys

The LLM baseline (Llama-3.3-70B) runs on Groq's cloud API. You need a free API key:

1. Go to [console.groq.com](https://console.groq.com)
2. Create a free account
3. Generate an API key
4. Create a `.env` file in the project root:

```bash
echo "GROQ_API_KEY=gsk_your_key_here" > .env
```

**Free tier limits**: 14,400 requests/day — sufficient for all benchmarks.

**Running without Groq**: If you only want to benchmark local SLMs (without the LLM baseline), the scripts will skip the Groq model and log errors for it. All local SLM results remain valid.

---

## Running Benchmarks

### Step 1: Verify Infrastructure

```bash
# Ensure Ollama is running
ollama serve &

# Run the verification script
python3 scripts/verify_apis.py
```

**Expected output**:
```
=== LOCAL MODELS (Ollama) ===
  Llama-3.2-3B    ✓  (latency: 210ms)
  Phi4-Mini       ✓  (latency: 222ms)
  Gemma3-4B       ✓  (latency: 311ms)
  Qwen2.5-7B      ✓  (latency: 221ms)
  Mistral-7B      ✓  (latency: 155ms)
  Llama-3.1-8B    ✓  (latency: 331ms)

=== CLOUD MODELS (Groq) ===
  Llama-3.3-70B   ✓  (latency: 319ms)
```

**Troubleshooting**:
- `Connection refused`: Ollama server not running. Start with `ollama serve`.
- `Model not found`: Model not downloaded. Run `ollama pull <model_name>`.
- `Groq 401`: Invalid API key. Check `.env` file.
- `Groq 429`: Rate limit hit. Wait 60 seconds and retry.

### Step 2: Build Gold Sets

Gold sets are pre-registered test datasets. They only need to be built once:

```bash
# Build all gold sets (creates CSV + metadata JSON files)
python3 scripts/build_gold_set_uc1.py
python3 scripts/build_gold_set_uc2.py
python3 scripts/build_gold_set_uc3.py
python3 scripts/build_gold_set_uc4.py
python3 scripts/build_gold_set_uc5.py
python3 scripts/build_gold_set_uc6.py
python3 scripts/build_gold_set_uc7.py
python3 scripts/build_gold_set_uc8.py
```

Each script creates:
- `data/gold_sets/uc[N]_*.csv` — 100-item gold set
- `data/gold_sets/uc[N]_metadata.json` — S3 scores, hypotheses, dimensions

### Step 3: Run Benchmarks

Each benchmark runs **7 models x 30 test items x 3 seeds = 630 inferences**:

```bash
# Classification tasks (Category 1, max_tokens=128) — ~15-30 min each
python3 scripts/run_benchmark_uc1.py    # SMS Threat Detection
python3 scripts/run_benchmark_uc3.py    # Support Ticket Routing
python3 scripts/run_benchmark_uc4.py    # Product Review Sentiment
python3 scripts/run_benchmark_uc5.py    # Code Review
python3 scripts/run_benchmark_uc6.py    # Healthcare Clinical Triage
python3 scripts/run_benchmark_uc7.py    # Legal Contract Analysis

# Structured extraction (Category 2, max_tokens=512) — ~30-60 min
python3 scripts/run_benchmark_uc2.py    # Invoice Field Extraction

# Long-form generation (Category 3, max_tokens=1024) — ~60-120 min
python3 scripts/run_benchmark_uc8.py    # Financial Report Drafting
```

**Important notes**:
- Run benchmarks **one at a time** to avoid memory contention between models.
- Close other memory-intensive applications before running.
- On 16GB RAM, 7-8B models will cause memory pressure. This affects latency, not accuracy.
- Results are saved incrementally after each model completes (crash-safe).
- The `--resume` flag (UC6, UC8) allows continuing interrupted runs.

**Output files**:
- `data/raw_outputs/uc[N]_raw_[TIMESTAMP].csv` — every inference result
- `data/results/uc[N]_summary_[TIMESTAMP].csv` — per-model aggregated metrics

### Step 4: Evaluate Results

```bash
# Generate evaluation reports
python3 scripts/evaluate_uc1.py
python3 scripts/evaluate_uc2.py
python3 scripts/evaluate_uc3.py
python3 scripts/evaluate_uc4.py
python3 scripts/evaluate_uc5.py
python3 scripts/evaluate_uc6.py
python3 scripts/evaluate_uc7.py
python3 scripts/evaluate_uc8.py
```

Each evaluation script:
1. Loads the most recent raw results file
2. Computes per-model metrics (accuracy, F1, precision, recall, latency percentiles)
3. Computes per-difficulty and per-category breakdowns
4. Validates pre-registered hypotheses
5. Generates evaluation report (TXT) and metrics (CSV)

**Output files**:
- `evaluation/uc[N]_report_[TIMESTAMP].txt` — human-readable report
- `evaluation/uc[N]_evaluation_[TIMESTAMP].csv` — machine-readable metrics

---

## Model Registry

### Local SLMs (Ollama)

| Model | Parameters | Architecture | Quantisation | Strengths |
|-------|-----------|--------------|-------------|-----------|
| Llama-3.2-3B | 3B | Decoder-only | Q4_K_M | Lowest parameter boundary; demonstrates task-type dominance over scale |
| Phi4-Mini | 3.8B | Decoder-only | Q4_K_M | Microsoft instruction-tuned; strong structured output |
| Gemma3-4B | 4B | Decoder-only | Q4_K_M | Google efficient architecture; consistent mid-tier |
| Qwen2.5-7B | 7B | Decoder-only | Q4_K_M | Alibaba multilingual; strong structured extraction |
| Mistral-7B | 7B | Decoder-only | Q4_K_M | Best SLM across 5 confirmed UCs; UC3 parity 104% |
| Llama-3.1-8B | 8B | Decoder-only | Q4_K_M | Largest local SLM; UC4 exact parity with LLM |

### Cloud LLM (Groq)

| Model | Parameters | Backend | Role |
|-------|-----------|---------|------|
| Llama-3.3-70B | 70B | Groq LPU Cloud | Performance ceiling for parity computation |

---

## Inference Configuration

All parameters are **locked** as of 2 March 2026 (pre-registration date):

```json
{
  "temperature": 0.0,
  "top_p": 1.0,
  "seeds": [42, 43, 44],
  "runs_per_item": 3,
  "max_tokens_by_category": {
    "C1": 128,
    "C2": 512,
    "C3": 1024
  }
}
```

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Temperature | 0.0 | Deterministic output for reproducibility |
| Seeds | [42, 43, 44] | Three runs per item for variance estimation |
| Runs per item | 3 | Statistical reliability without excessive cost |
| Test items | 30 per UC | From 100-item gold set (70 train / 30 test) |
| Total inferences | 630 per UC | 7 models x 30 items x 3 runs |

**Acceptance criteria** (pre-registered):
- Accuracy >= 95% of LLM baseline on valid outputs
- P95 latency <= task-specific SLA
- Valid output rate >= 95%

---

## Key Results

### S3 Tier Prediction: 100% Accuracy on 5 Confirmed Cases

| UC | S3 Score | Predicted | Best SLM | LLM Baseline | Parity | Confirmed? |
|----|----------|-----------|----------|-------------|--------|-----------|
| UC4 | 2.10 | Pure SLM | Llama-3.1-8B: 96.7% | 96.7% | 100% | Yes |
| UC2 | 2.56 | Pure SLM | Mistral-7B: 96.7% | 96.7% | 100% | Yes |
| UC3 | 2.67 | Pure SLM | Mistral-7B: 86.7% | 83.3% | 104% | Yes |
| UC1 | 3.10 | Hybrid | Mistral-7B: 90.0% | 90.0% | 100% | Yes |
| UC6 | 4.44 | LLM Only | Mistral-7B: 63.6% recall | 81.8% recall | 77.8% | Yes |

### Cross-Task Finding

**Task type dominates model scale**: Llama-3.2-3B achieves 93.3% on UC4 (S3=2.10) and 56.7% on UC1 (S3=3.10) — a 36.6pp swing from the same model, same hardware, same prompt structure. The 70B LLM moves only 6.7pp across the same two tasks. S3 score predicts this variance before any inference is run.

---

## Known Limitations

### Memory Pressure on 16GB Systems

With 16GB RAM and CPU-only inference, 7-8B models cause memory pressure (swap). Evidence from benchmark data:

- **Periodic latency spikes**: Every 3rd inference shows 3-5x latency increase due to memory decompression after inter-item sleep
- **Catastrophic swap events**: Occasional 10-50x latency spikes (e.g., 13,591ms vs typical 331ms for Llama-3.1-8B)
- **UC8 latency explosion**: Local models show 40-110x slowdown on 1024-token generation vs 128-token classification, far exceeding the expected 8x from token count alone

**Impact**: Latency metrics (P50, P95) are contaminated by swap. Accuracy metrics are unaffected.

**Mitigation**: For reliable latency measurement, use 32GB+ RAM or GPU-accelerated inference. All SDDF latency metrics require GPU recalibration before use in production SLA decisions.

### Groq API Reliability

The Groq cloud API (Llama-3.3-70B baseline) experienced cascading failures during UC8 benchmarking:
- Rate limit errors (HTTP 429) after sustained high-volume requests
- DNS resolution failures following rate limit exhaustion
- ~18 out of 630 UC8 inferences failed (97.1% success rate)

UC1-UC6 benchmarks completed without Groq failures.

### Threshold Calibration

Tier boundaries (3.2 and 4.0) are geometrically initialised and validated for internal stability with N=5 confirmed cases. Full empirical calibration via UTADIS linear programming requires N >= 50 confirmed deployment outcomes. See paper Section 9 for details.

### Dimensional Independence

The WSM additive formula assumes preferential independence between dimensions. Correlations likely exist in practice (e.g., high-Stakes tasks tend to involve regulated data). This is documented as a known limitation with conservative impact (double-counting risk factors errs toward escalation, which is the safe direction).

---

## Citation

```bibtex
@article{rajappa2026s3framework,
  title     = {Decision Framework and Industrial Deployment Protocol
               for Small Language Models in Agentic AI Systems},
  author    = {Rajappa, Smitha and Ramasahayam Reddy, Riddhima and
               Savant, Rohit and Saxena, Yashraj and Sengupta, Smita},
  year      = {2026},
  institution = {University of Texas at Dallas},
  keywords  = {small language models, enterprise AI deployment,
               model selection framework, dynamic denominator WSM,
               hybrid routing, SDDF, threshold calibration, agentic AI}
}
```

---

## License

This project is part of academic research at the University of Texas at Dallas under the guidance of Professor Ashim Bose. Please cite the paper if you use this framework or data in your work.
