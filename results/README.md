# Results snapshots

This directory holds checked-in benchmark snapshots.

## Naming

Preferred naming pattern:

- `livefire-<label>-<YYYY-MM>.json`
- matching summary files:
  - `.md`
  - `.csv`

Examples:

- `livefire-may-2026.json`
- `livefire-openai-gpt5x-2026-05-26.json`
- `claude-may-2026.json`

## Notes

- The JSON file is the source of truth.
- The Markdown and CSV files are rendered summaries.
- Older snapshots may target smaller datasets than the current `main` branch corpus. Check the embedded `dataset_sha256` before comparing runs.
- Some snapshots may come from non-harness execution paths (for example, agent-run Claude tests). Those should be labeled clearly in the summary file.
- `.ots` sidecars are OpenTimestamps proofs for the JSON snapshots when available.
