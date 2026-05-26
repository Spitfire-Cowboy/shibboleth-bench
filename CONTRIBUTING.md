# Contributing

Thanks for helping improve Shibboleth.

## Scope

This repo is intentionally narrow. Good contributions usually improve one of:
- benchmark item quality
- grading rigor
- result reproducibility
- dataset provenance
- backend support for running existing benchmark items

Please avoid turning the repo into a general multimodal eval framework unless there is a strong reason.

## Development

Run the tests:

```bash
python3 -m pytest -q tests/test_eval.py tests/test_dataset.py
```

Regenerate the synthetic benchmark assets:

```bash
python3 scripts/generate_synthetic_assets.py
```

Build the static site:

```bash
python3 scripts/build_pages.py
```

Dry-run the harness:

```bash
python3 eval.py --dry-run
```

Render Markdown and CSV summaries from a JSON snapshot:

```bash
python3 scripts/render_results.py \
  --input results/livefire-may-2026.json \
  --markdown-out results/livefire-may-2026.md \
  --csv-out results/livefire-may-2026.csv \
  --title "Shibboleth livefire — May 2026"
```

Runtime note:
- the benchmark harness itself is stdlib-only
- `pytest` is only needed for running tests

## Contribution guidelines

- Keep benchmark items small, legible, and easy to score.
- Prefer owned or clearly licensed images.
- Add provenance notes for any new assets.
- Keep grading changes explainable and auditable.
- Do not add opaque scoring heuristics.
- Submit contributions as a pull request against `main`.
