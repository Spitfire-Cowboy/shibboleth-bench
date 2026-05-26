# shibboleth-bench

A small Apache 2.0 benchmark for **visual anomaly screening** in multimodal models.

[![CI](https://github.com/Spitfire-Cowboy/shibboleth-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/Spitfire-Cowboy/shibboleth-bench/actions/workflows/ci.yml)
[![Pages](https://img.shields.io/badge/pages-live-7d3f1d)](https://spitfire-cowboy.github.io/shibboleth-bench/)

## 🔎 What it asks

> Does this model miss obvious image-generation mistakes or discrete-object anomalies?

Shibboleth is a **screening benchmark**, not a full evaluation stack.
It is meant to cheaply filter out weak multimodal candidates before deeper testing.

## 🌐 Public surface

- **Repo:** https://github.com/Spitfire-Cowboy/shibboleth-bench
- **Benchmark site:** https://spitfire-cowboy.github.io/shibboleth-bench/
- **Latest JSON snapshot:** `results/livefire-may-2026.json`
- **Latest CSV snapshot:** `results/livefire-may-2026.csv`

## ✅ Current status

- **public-ready benchmark harness:** yes
- **checked-in dataset:** 10 items
- **structured-answer grading:** yes
- **direct vendor livefire support:** yes
  - Ollama
  - OpenRouter
  - OpenAI
  - xAI
- **public benchmark site:** live
- **scope:** narrow anomaly screening, not a broad leaderboard

## 🧪 Current May 2026 snapshot

| Model | Score | Misses |
| --- | ---: | --- |
| `openai/gpt-4o` | 10 / 10 | none |
| `openai/gpt-4.1` | 9 / 10 | `SB-001` |
| `openai/gpt-4o-mini` | 9 / 10 | `SB-001` |
| `xai/grok-4.3` | 9 / 10 | `SB-001` |
| `openai/gpt-5` | 7 / 10 | `SB-001`, `SB-005`, `SB-008` |

Artifacts:
- `results/livefire-may-2026.json`
- `results/livefire-may-2026.md`
- `results/livefire-may-2026.csv`

## 🖼️ Current dataset

The benchmark currently includes ten high-signal probes:

- `SB-001` — two-hat count
- `SB-002` — mirror mismatch
- `SB-003` — water reflection mismatch
- `SB-004` — six-finger hand
- `SB-005` — garbled sign text
- `SB-006` — detached glasses arm
- `SB-007` — shadow direction mismatch
- `SB-008` — repeated chair count
- `SB-009` — detached mug handle
- `SB-010` — transparent glasses count

Most of these are **self-authored synthetic probe images** designed to be simple, legible, and easy to score.

See:
- `dataset/items.jsonl`
- `dataset/PROVENANCE.md`
- `scripts/generate_synthetic_assets.py`

## ⚡ Quick start

### Dry run

```bash
python3 eval.py --dry-run
```

### Run against a local Ollama model

```bash
python3 eval.py \
  --model ollama/llava:13b \
  --ollama-host http://127.0.0.1:11434
```

### Run against OpenAI

```bash
export OPENAI_API_KEY=...
python3 eval.py --model openai/gpt-4.1
```

### Run against xAI

```bash
export XAI_API_KEY=...
python3 eval.py --model xai/grok-4.3
```

### Run the May 2026 vendor snapshot

```bash
export OPENAI_API_KEY=...
export XAI_API_KEY=...
python3 run_matrix.py \
  --may-2026-openai \
  --may-2026-xai \
  --output results/livefire-may-2026.json
```

### Run against OpenRouter free vision models

```bash
export OPENROUTER_API_KEY=...
python3 run_matrix.py \
  --free-openrouter-vision \
  --output results/openrouter-free-vision.json
```

## 🧱 Output contract

Each run records:
- exact model ref
- dataset path
- dataset SHA-256
- run timestamp
- prompt protocol version
- raw model response
- parsed answer
- grading label
- latency stats

This keeps results reproducible and auditable.

## 🧮 Grading model

The harness asks models to return strict JSON:

```json
{"answer":"two","confidence":"certain","notes":"..."}
```

Why this shape:
- freeform answers are fragile to grade
- substring matching creates false positives
- contradictory answers should not accidentally pass

The grader still falls back to freeform parsing when needed, but structured output is the preferred path.

## 📁 Repo layout

- `dataset/items.jsonl` — benchmark item manifest
- `dataset/images/` — benchmark images
- `dataset/PROVENANCE.md` — asset provenance notes
- `scripts/generate_synthetic_assets.py` — reproducible synthetic asset generator
- `scripts/build_pages.py` — static benchmark site builder
- `eval.py` — single-model runner and grading harness
- `run_matrix.py` — multi-model batch runner
- `results/` — checked-in benchmark snapshots
- `site/` — generated static site output
- `tests/` — harness tests
- `docs/edge-cases.md` — researched expansion targets

## 📉 Limitations

This repo is intentionally small, which means the current results have real limits:

- ten items is still a small benchmark
- most items are synthetic probes, not naturalistic photographs
- live model behavior changes over time
- passing Shibboleth does **not** imply general multimodal competence

Treat it as a **cheap screen**, not a final verdict.

## 🛣️ Next steps

High-value future additions include:
- more naturalistic mirror and glossy-surface probes
- more hand and anatomy edge cases
- signage and label reading variants
- accessory symmetry and attachment failures
- repeated-object counting scenes with more visual noise
- lighting contradictions in more realistic scenes

See `docs/edge-cases.md` for the fuller research list.

## 📄 License

Apache 2.0.
