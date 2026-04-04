# Two-Hat OpenRouter Matrix — 2026-04-04

Prompt:

> How many hats is the person wearing?

Image:

- `dataset/images/two-hat-logo.png`

Raw machine-readable results:

- `results/two-hat-openrouter-2026-04-04.json`

## Human-Adjudicated Summary

| Model | Raw outcome | Human read | Notes |
|---|---:|---:|---|
| `openrouter/google/gemma-3-12b-it:free` | rate-limited | n/a | `429 Too Many Requests` |
| `openrouter/google/gemma-3-27b-it:free` | rate-limited | n/a | `429 Too Many Requests` |
| `openrouter/google/gemma-3-4b-it:free` | pass | pass | Answered `two` clearly |
| `openrouter/nvidia/nemotron-nano-12b-v2-vl:free` | fail | fail | Said one hat worn, one held |
| `openrouter/openrouter/free` | fail | fail | Said one hat worn |
| `openrouter/qwen/qwen3.6-plus:free` | fail/partial | fail | Said one hat; long latency |
| `openrouter/openai/gpt-4o` | fail | fail | Said one worn, one held |
| `openrouter/anthropic/claude-sonnet-4.6` | pass | fail | Auto-scorer marked pass because response mentioned `2 hats` total, but the model explicitly said the person is wearing `1 hat` |
| `openrouter/anthropic/claude-opus-4.6` | pass | pass | Counted two hats worn |
| `openrouter/google/gemini-2.5-pro` | fail | fail | Response truncated but clearly started with `wearing one` |

## Caveat

The current automatic scorer is substring-based. It can overcount contradictory
answers as passes when the expected answer appears anywhere in the response.

Concrete example:

- `claude-sonnet-4.6` was auto-scored as correct because it mentioned `2 hats`
  in total, but it explicitly answered that the person is wearing `1 hat`.

Use the raw responses, not just the auto score, for publication-quality claims.
