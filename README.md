# shibboleth-bench

A small Apache 2.0 benchmark harness for **visual anomaly screening** in multimodal models.

Shibboleth is meant to answer a narrow question quickly:

> Does this model miss obvious image-generation mistakes or discrete-object counting failures?

It is a **screening benchmark**, not a full model evaluation stack.

## Why this exists

Many multimodal models look impressive in broad demos while still failing on narrow, high-signal visual anomalies:
- counting discrete objects incorrectly
- misreading reflections or mirrored scenes
- hallucinating text, hands, or accessories
- giving confident answers to obviously wrong interpretations

The goal here is to filter out weak candidates before spending time on deeper evals.

## Current status

- public benchmark harness: **yes**
- structured-answer grading: **yes**
- direct vendor livefire support: **yes**
  - Ollama
  - OpenRouter
  - OpenAI
  - xAI
- checked-in benchmark dataset: **still tiny**
- current benchmark scope: **prototype / screening**, not a broad leaderboard

## Canonical benchmark item

Current dataset includes:
- `SB-001` — the canonical **two-hat** image

Source image:
- `dataset/images/two-hat-logo.png`

Prompt:
- `How many hats is the person wearing?`

Expected answer:
- `two`

This is intentionally simple and high-signal.

## Quick start

Dry run:

```bash
python3 eval.py --dry-run
```

Run against a local Ollama multimodal model:

```bash
python3 eval.py \
  --model ollama/llava:13b \
  --ollama-host http://127.0.0.1:11434
```

Run against OpenAI:

```bash
export OPENAI_API_KEY=...
python3 eval.py --model openai/gpt-4.1
```

Run against xAI:

```bash
export XAI_API_KEY=...
python3 eval.py --model xai/grok-4.3
```

Run a May 2026 vendor snapshot:

```bash
export OPENAI_API_KEY=...
export XAI_API_KEY=...
python3 run_matrix.py \
  --may-2026-openai \
  --may-2026-xai \
  --output results/livefire-may-2026.json
```

Run against OpenRouter free vision models:

```bash
export OPENROUTER_API_KEY=...
python3 run_matrix.py \
  --free-openrouter-vision \
  --output results/openrouter-free-vision.json
```

## Output contract

Each run now records:
- exact model ref
- dataset path
- dataset SHA-256
- run timestamp
- prompt protocol version
- raw model response
- parsed answer
- grading label
- latency stats

This makes results more reproducible and easier to audit.

## Grading model

The harness now asks models to return strict JSON:

```json
{"answer":"two","confidence":"certain","notes":"..."}
```

Why:
- freeform answers are fragile to grade
- substring matching creates false positives
- contradictory answers should not accidentally pass

The grader still falls back to freeform parsing when needed, but the preferred path is structured output.

## Current repo layout

- `dataset/items.jsonl` — benchmark item manifest
- `dataset/images/` — local benchmark images
- `eval.py` — single-model runner and grading harness
- `run_matrix.py` — multi-model batch runner
- `results/` — checked-in benchmark snapshots
- `tests/` — harness tests
- `docs/edge-cases.md` — researched expansion targets for future benchmark items

## Latest livefire snapshot

See:
- `results/livefire-may-2026.json`
- `results/livefire-may-2026.md`

That snapshot reflects direct vendor runs in May 2026 rather than older OpenRouter-only results.

## Benchmark limitations

This repo is intentionally small, and that means the current results have real limits:

- one benchmark item is not enough for strong claims
- model answers can still fail in ways the parser does not perfectly normalize
- live model catalogs change over time
- passing this benchmark does **not** imply general multimodal competence

Treat Shibboleth as a **cheap screen**, not a final verdict.

## Expansion plan

The next important step is **dataset breadth**, not framework complexity.

High-value future items include:
- mirror/reflection anomalies
- water/glass reflection anomalies
- extra fingers / merged fingers / impossible hand poses
- malformed text on signs, labels, and logos
- asymmetrical jewelry or eyewear
- impossible object duplication in repeated patterns
- shadow / lighting contradictions

See `docs/edge-cases.md` for the researched list.

## License

Apache 2.0.
