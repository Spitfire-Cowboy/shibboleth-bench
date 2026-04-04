# shibboleth-bench

Private home for the Shibboleth visual anomaly benchmark.

## What It Is

Shibboleth is a narrow visual anomaly benchmark for multimodal models. It is meant
to quickly filter out models that miss obvious AI-generation artifacts or
discrete-object mistakes before spending time on broader evaluations.

It is a screening benchmark, not a full model evaluation.

## Canonical Image

- `dataset/images/two-hat-logo.png` — the original two-hat Spitfire Cowboy logo used for `SB-001`

## Quick Start

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

Run against a remote Ollama host:

```bash
python3 eval.py \
  --model ollama/gemma4:26b \
  --ollama-host http://YOUR-HOST:11434 \
  --ollama-think false \
  --ollama-timeout-s 180
```

Run the two-hat matrix across OpenRouter free vision models:

```bash
export OPENROUTER_API_KEY=...
python3 run_matrix.py \
  --free-openrouter-vision \
  --output results/openrouter-free-vision.json
```

Add frontier models explicitly:

```bash
export OPENROUTER_API_KEY=...
python3 run_matrix.py \
  --free-openrouter-vision \
  --model openrouter/openai/gpt-4o \
  --model openrouter/anthropic/claude-sonnet-4 \
  --model openrouter/google/gemini-2.5-pro \
  --output results/two-hat-matrix.json
```

## Repo Layout

- `dataset/items.jsonl` — benchmark item manifest
- `dataset/images/` — local benchmark images
- `eval.py` — evaluation harness
- `run_matrix.py` — batch runner for free and selected frontier models

## License

Code in this repo is Apache 2.0. Data and image provenance should be tracked
per asset before any public release.
