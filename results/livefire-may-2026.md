# Livefire snapshot — May 26, 2026

Dataset:
- `dataset/items.jsonl`
- current scope: **1 item** (`SB-001`, the two-hat image)

Prompt protocol:
- `structured-json-v1`

## Models run

- `openai/gpt-4.1`
- `openai/gpt-4o`
- `openai/gpt-4o-mini`
- `openai/gpt-5`
- `xai/grok-4.3`

## Summary

All directly tested vendor models in this snapshot **failed** the canonical two-hat task.

### Human read

| Model | Outcome | Parsed answer | Notes |
|---|---:|---:|---|
| `openai/gpt-4.1` | fail | `one` | Clearly answered that one hat is worn |
| `openai/gpt-4o` | fail | `1` | Clearly answered one hat worn |
| `openai/gpt-4o-mini` | fail | `1` | Same failure pattern |
| `openai/gpt-5` | infra error | n/a | Direct retries returned empty-output / upstream-error behavior during this snapshot |
| `xai/grok-4.3` | fail | `1` | Clearly answered one hat worn |

## Important caveats

- This is still a **tiny screening benchmark**, not a broad capability ranking.
- A single-item failure is interesting, but not sufficient for sweeping claims.
- `gpt-5` did not produce a valid scored answer in this run because of an upstream API error, so this result should be treated as an infrastructure failure, not a benchmark verdict.

## Raw results

See:
- `results/livefire-may-2026.json`
