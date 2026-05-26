# Shibboleth Claude snapshot — May 2026

Dataset: `dataset/items.jsonl` (10 items, SB-001 – SB-010)
Run method: parallel Claude subagents via Cowork / Claude Agent SDK (not via `eval.py` harness)
Run date: 2026-05-26
Prompt protocol: structured-json-v1

## Results

| Model | Score | Misses |
| --- | ---: | --- |
| `anthropic/claude-opus-4-6` | **10 / 10** | none |
| `anthropic/claude-sonnet-4-6` | **10 / 10** | none |
| `anthropic/claude-haiku-4-5` | **9 / 10** | `SB-001` |

## Per-item detail

### claude-opus-4-6

| Item | Category | Answer | Expected | Correct | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| SB-001 | counting | two | two | ✓ | certain | Cowboy wears one hat on his head and holds a second hat in his raised hand. |
| SB-002 | mirror | no | no | ✓ | certain | Real stick figure wears one hat; the mirror shows two stacked hats. |
| SB-003 | reflection | no | no | ✓ | certain | Three buoys above the waterline, only two reflections shown below. |
| SB-004 | hands | six | six | ✓ | certain | Five raised digits plus one thumb on the side equals six fingers. |
| SB-005 | text | no | no | ✓ | certain | Sign displays "P1Z7A?" which is not an English word. |
| SB-006 | accessories | no | no | ✓ | certain | Right side temple arm floats above the face, detached from the frame. |
| SB-007 | lighting | no | no | ✓ | certain | The two posts cast shadows pointing inward toward each other, opposite directions. |
| SB-008 | counting | five | five | ✓ | certain | Five chairs visible around the oval table (one top, two upper sides, two lower). |
| SB-009 | continuity | no | no | ✓ | certain | The C-shaped handle floats to the right, not touching the mug body. |
| SB-010 | transparency | three | three | ✓ | certain | Three transparent drinking glasses lined up on the shelf. |

### claude-sonnet-4-6

| Item | Category | Answer | Expected | Correct | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| SB-001 | counting | two | two | ✓ | certain | One hat worn on head, one held raised in the hand. |
| SB-002 | mirror | no | no | ✓ | certain | Real figure wears one hat; mirror shows two stacked. |
| SB-003 | reflection | no | no | ✓ | certain | Three buoys above water, only two reflected below. |
| SB-004 | hands | six | six | ✓ | certain | Five fingers plus thumb = six visible fingers. |
| SB-005 | text | no | no | ✓ | certain | Sign reads "P1Z7A?" — digits mixed with letters, not English. |
| SB-006 | accessories | no | no | ✓ | certain | Left arm attached normally; right arm floats disconnected. |
| SB-007 | lighting | no | no | ✓ | certain | Left post shadow goes right, right post shadow goes left — opposite directions. |
| SB-008 | counting | five | five | ✓ | certain | 1 top-center, 1 upper-left, 1 upper-right, 1 lower-left, 1 lower-right. |
| SB-009 | continuity | no | no | ✓ | certain | Mug handle (C-shape) floats to the right, clearly detached from mug body. |
| SB-010 | transparency | three | three | ✓ | certain | Three transparent drinking glasses visible on shelf. |

### claude-haiku-4-5

| Item | Category | Answer | Expected | Correct | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| SB-001 | counting | **one** | two | ✗ | certain | Saw one hat on person's head; missed the second hat held in hand. |
| SB-002 | mirror | no | no | ✓ | certain | Real figure has 1 hat, mirror shows 2 — mismatch detected. |
| SB-003 | reflection | no | no | ✓ | certain | 3 buoys above, 2 reflected below — mismatch detected. |
| SB-004 | hands | six | six | ✓ | certain | Counted 6 distinct finger shapes. |
| SB-005 | text | no | no | ✓ | certain | Sign reads "P1Z7A?" — not readable English. |
| SB-006 | accessories | no | no | ✓ | certain | One glasses arm detached/floating above the face. |
| SB-007 | lighting | no | no | ✓ | certain | Two posts cast shadows in opposite directions. |
| SB-008 | counting | five | five | ✓ | certain | 5 chairs visible around the table. |
| SB-009 | continuity | no | no | ✓ | certain | Mug handle floating separately, not attached. |
| SB-010 | transparency | three | three | ✓ | certain | 3 transparent glasses visible. |

## Analysis

**Opus and Sonnet scored a clean 10/10.** Both answered with `"confidence": "certain"` on every item. Neither hedged on the harder probes (shadow contradiction, transparent glass counting, or the SB-001 two-hat count). Response reasoning was correct and specific.

**Haiku scored 9/10, missing SB-001.** The miss is interpretive rather than perceptual: Haiku saw the figure correctly (one hat on the head, one hat held in the raised hand) but decided the held hat was "not worn" and answered `"one"`. This reflects a reasonable ambiguity in the prompt — "how many hats is the person wearing?" could legitimately exclude a held hat — but the other models and the canonical benchmark answer count the held hat. The prompt for SB-001 may benefit from rewording if Haiku's interpretation keeps recurring.

**Haiku over-read the dataset.** Haiku continued reading image files beyond the 10-item `items.jsonl` manifest, encountering files outside the official dataset and scoring them as if they were benchmark items. The `eval.py` harness would prevent this (it only iterates over loaded `Item` objects), but it is useful behaviour to know about when running models via agent tooling rather than the harness.

**All three models returned structured JSON on every item.** No freeform fallback parsing was needed. All confidence values were `"certain"` across all three models.

## Notes on dataset scope

The existing `results/livefire-may-2026.json` was run against 14 items (SB-001 – SB-014), not the 10-item set currently in `dataset/items.jsonl`. This Claude snapshot covers only the 10-item set. If the extended 14-item dataset is restored to `items.jsonl`, re-run this snapshot for a comparable score.

## Comparison with existing May 2026 snapshot (10-item subset)

Cross-referencing the livefire JSON for SB-001 – SB-010 only:

| Model | Score (10-item) |
| --- | ---: |
| `openai/gpt-4o` | 10 / 10 |
| `anthropic/claude-opus-4-6` | 10 / 10 |
| `anthropic/claude-sonnet-4-6` | 10 / 10 |
| `openai/gpt-4.1` | 9 / 10 |
| `openai/gpt-4o-mini` | 9 / 10 |
| `xai/grok-4.3` | 9 / 10 |
| `anthropic/claude-haiku-4-5` | 9 / 10 |
| `openai/gpt-5` | 7 / 10 |

This snapshot should not be read as a broad multimodal ranking. Shibboleth is a narrow anomaly-focused benchmark with a small synthetic dataset.
