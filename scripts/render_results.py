#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def ordered_results(payload: dict) -> list[dict]:
    return sorted(
        payload.get("results", []),
        key=lambda result: (
            -(result.get("correct", 0) / max(result.get("total_items", 1), 1)),
            result.get("model_ref", ""),
        ),
    )


def misses_for(result: dict) -> str:
    misses = [item["item_id"] for item in result.get("items", []) if item.get("score_label") != "correct"]
    return ", ".join(misses) if misses else "none"


def render_markdown(payload: dict, title: str) -> str:
    lines = [
        f"# {title}",
        "",
        f"Dataset SHA-256: `{payload['dataset_sha256'][:12]}…` (full hash in the JSON snapshot)",
        "",
        "## Results",
        "",
    ]
    for result in ordered_results(payload):
        lines.append(
            f"- `{result['model_ref']}` — **{result['correct']}/{result['total_items']}** "
            f"(misses: {misses_for(result)})"
        )
    lines.extend(
        [
            "",
            "This snapshot covers a small anomaly-focused benchmark. It should not be read as a broad multimodal ranking.",
            "",
        ]
    )
    return "\n".join(lines)


def render_csv(payload: dict) -> str:
    rows = [["model_ref", "correct", "total_items", "accuracy", "misses"]]
    for result in ordered_results(payload):
        rows.append(
            [
                result["model_ref"],
                str(result["correct"]),
                str(result["total_items"]),
                f"{result['accuracy']:.4f}",
                misses_for(result),
            ]
        )

    out: list[str] = []
    for row in rows:
        out.append(",".join(f'"{value}"' for value in row))
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render markdown and CSV summaries from a benchmark JSON snapshot.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    parser.add_argument("--csv-out", type=Path, required=True)
    parser.add_argument("--title", default="Shibboleth livefire")
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.markdown_out.write_text(render_markdown(payload, args.title), encoding="utf-8")
    args.csv_out.write_text(render_csv(payload), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
