# shibboleth-bench

A focused benchmark for one narrow question: do multimodal models catch obvious visual anomalies that a human would notice immediately?

[![CI](https://github.com/Spitfire-Cowboy/shibboleth-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/Spitfire-Cowboy/shibboleth-bench/actions/workflows/ci.yml)
[![Pages](https://img.shields.io/badge/pages-live-7d3f1d)](https://spitfire-cowboy.github.io/shibboleth-bench/)

[![Two-hat cowboy benchmark image](dataset/images/two-hat-logo.png)](https://spitfire-cowboy.github.io/shibboleth-bench/)

## 🔎 What it asks

> Does this model miss obvious image-generation mistakes or discrete-object anomalies?

Shibboleth is a narrow benchmark, not a full evaluation stack. It compares models on a small set of crisp, high-signal probes before deeper testing.

## 🌐 Public surface

- **Repo:** https://github.com/Spitfire-Cowboy/shibboleth-bench
- **Benchmark site:** https://spitfire-cowboy.github.io/shibboleth-bench/
- **Latest JSON snapshot:** `results/livefire-may-2026.json`
- **Latest CSV snapshot:** `results/livefire-may-2026.csv`

## 🧪 Latest May 2026 snapshot

| Model | Score | Misses |
| --- | ---: | --- |
| `openai/gpt-4.1` | 12 / 14 | `SB-012`, `SB-013` |
| `openai/gpt-4o` | 12 / 14 | `SB-012`, `SB-013` |
| `openai/gpt-4o-mini` | 12 / 14 | `SB-012`, `SB-013` |
| `xai/grok-4.3` | 11 / 14 | `SB-001`, `SB-013`, `SB-014` |
| `openai/gpt-5` | 7 / 14 | `SB-001`, `SB-004`, `SB-005`, `SB-011`, `SB-012`, `SB-013`, `SB-014` |

Additional OpenAI frontier snapshot:
- `results/livefire-openai-gpt5x-2026-05-26.json`
- `results/livefire-openai-gpt5x-2026-05-26.md`
- `results/livefire-openai-gpt5x-2026-05-26.csv`

Artifacts:
- `results/livefire-may-2026.json`
- `results/livefire-may-2026.md`
- `results/livefire-may-2026.csv`

## 🖼️ Current dataset

The benchmark currently includes fourteen high-signal probes:

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
- `SB-011` — photographic garbled sign text
- `SB-012` — photographic duplicated hat portrait
- `SB-013` — photographic five-chair table
- `SB-014` — photographic three-wheel bicycle

Nine of the fourteen current items are **self-authored synthetic probe images** designed to be simple, legible, and easy to score. The remaining five are photographic derivatives built from public-domain or clearly licensed source photos.

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

This keeps results easier to reproduce and audit.

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
- `scripts/build_pages.py` — static site builder
- `eval.py` — single-model runner and grading harness
- `run_matrix.py` — multi-model batch runner
- `results/` — checked-in benchmark snapshots
- `site/` — generated site output
- `tests/` — harness tests
- `docs/edge-cases.md` — researched expansion targets

## 📉 Limitations

This repo is intentionally small, which means the current results have real limits:

- ten items is still a small benchmark
- most items are synthetic probes, not naturalistic photographs
- live model behavior changes over time
- passing Shibboleth does **not** imply general multimodal competence

Treat it as a small benchmark, not a final verdict on overall model quality.

## 🛣️ Next steps

High-value future additions include:
- more naturalistic mirror and glossy-surface probes
- more hand and anatomy edge cases
- signage and label reading variants
- accessory symmetry and attachment failures
- repeated-object counting scenes with more visual noise
- lighting contradictions in more realistic scenes

See `docs/edge-cases.md` for the fuller list of candidate additions.

## 📄 License

Apache 2.0.
