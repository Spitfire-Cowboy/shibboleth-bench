# shibboleth-bench

A small benchmark for one narrow question: how do multimodal models answer this dataset of visual anomaly items?

[![CI](https://github.com/Spitfire-Cowboy/shibboleth-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/Spitfire-Cowboy/shibboleth-bench/actions/workflows/ci.yml)
[![Pages](https://img.shields.io/badge/pages-live-7d3f1d)](https://spitfire-cowboy.github.io/shibboleth-bench/)

<p>
  <a href="https://spitfire-cowboy.github.io/shibboleth-bench/">
    <img src="dataset/images/two-hat-logo.png" alt="Two-hat cowboy benchmark image" width="420">
  </a>
</p>

## What it is

- **Repo:** https://github.com/Spitfire-Cowboy/shibboleth-bench
- **Benchmark site:** https://spitfire-cowboy.github.io/shibboleth-bench/
- **Dataset:** 14 benchmark items in `dataset/items.jsonl`
- **Purpose:** compare checked-in model results on a small visual anomaly dataset

## Current snapshots

### Harness snapshot — 14 items

| Model | Score | Misses |
| --- | ---: | --- |
| `openai/gpt-4.1` | 12 / 14 | `SB-012`, `SB-013` |
| `openai/gpt-4o` | 12 / 14 | `SB-012`, `SB-013` |
| `openai/gpt-4o-mini` | 12 / 14 | `SB-012`, `SB-013` |
| `xai/grok-4.3` | 11 / 14 | `SB-001`, `SB-013`, `SB-014` |
| `openai/gpt-5` | 7 / 14 | `SB-001`, `SB-004`, `SB-005`, `SB-011`, `SB-012`, `SB-013`, `SB-014` |

Artifacts:
- `results/livefire-may-2026.json`
- `results/livefire-may-2026.md`
- `results/livefire-may-2026.csv`
- `results/livefire-may-2026.json.ots`

### OpenAI frontier snapshot — 14 items

| Model | Score |
| --- | ---: |
| `openai/gpt-5.4` | 14 / 14 |
| `openai/gpt-5.2` | 13 / 14 |
| `openai/gpt-5.5` | 11 / 14 |
| `openai/gpt-5.1` | 10 / 14 |

Artifacts:
- `results/livefire-openai-gpt5x-2026-05-26.json`
- `results/livefire-openai-gpt5x-2026-05-26.md`
- `results/livefire-openai-gpt5x-2026-05-26.csv`
- `results/livefire-openai-gpt5x-2026-05-26.json.ots`

### Claude compatibility snapshot — 10 items

| Model | Score | Misses |
| --- | ---: | --- |
| `anthropic/claude-opus-4-6` | 10 / 10 | none |
| `anthropic/claude-sonnet-4-6` | 10 / 10 | none |
| `anthropic/claude-haiku-4-5` | 9 / 10 | `SB-001` |

Artifacts:
- `results/claude-may-2026.json`
- `results/claude-may-2026.md`
- `results/claude-may-2026.json.ots`

## Quick start

```bash
python3 eval.py --dry-run
```

```bash
export OPENAI_API_KEY=...
export XAI_API_KEY=...
python3 run_matrix.py \
  --may-2026-openai \
  --may-2026-xai \
  --output results/livefire-may-2026.json
```

## Dataset and method

- dataset manifest: `dataset/items.jsonl`
- images: `dataset/images/`
- provenance: `dataset/PROVENANCE.md`
- harness: `eval.py`
- matrix runner: `run_matrix.py`
- tests: `tests/`

The harness records the model ref, dataset SHA, timestamp, prompt protocol, raw response, parsed answer, and grading label.

## Limits

- 14 items is still a small benchmark
- most items are synthetic probes
- model behavior changes over time
- these snapshots apply to this dataset only

## License

Apache 2.0.
