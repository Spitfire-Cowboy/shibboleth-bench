#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from dataclasses import asdict
from pathlib import Path

import eval as bench

ROOT = Path(__file__).resolve().parent


def fetch_openrouter_models() -> list[dict]:
    with urllib.request.urlopen("https://openrouter.ai/api/v1/models", timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload.get("data") or []


def free_openrouter_vision_models() -> list[str]:
    selected: list[str] = []
    for model in fetch_openrouter_models():
        pricing = model.get("pricing") or {}
        modalities = (model.get("architecture") or {}).get("input_modalities") or []
        outputs = (model.get("architecture") or {}).get("output_modalities") or []
        if pricing.get("prompt") != "0" or pricing.get("completion") != "0":
            continue
        if "image" not in modalities or "text" not in outputs:
            continue
        model_id = model.get("id", "")
        if model_id.startswith("google/lyria-"):
            continue
        selected.append(model_id)
    return sorted(selected)


def run_for_model(model: str, args, items: list[bench.Item]) -> dict:
    try:
        adapter = bench.build_adapter(model, args.ollama_host, args.ollama_think, args.timeout_s)
        result = bench.evaluate(items, adapter)
        payload = asdict(result)
        payload["model_ref"] = model
        return payload
    except Exception as exc:  # noqa: BLE001
        return {
            "model": model,
            "model_ref": model,
            "total_items": len(items),
            "correct": 0,
            "partial": 0,
            "incorrect": len(items),
            "accuracy": 0.0,
            "partial_credit_score": 0.0,
            "latency_mean_ms": 0.0,
            "latency_p50_ms": 0.0,
            "items": [],
            "error": str(exc),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the two-hat matrix across multiple models.")
    parser.add_argument("--dataset", type=Path, default=ROOT / "dataset" / "items.jsonl")
    parser.add_argument("--ollama-host", default="http://127.0.0.1:11434")
    parser.add_argument("--ollama-think", choices=("default", "true", "false"), default="default")
    parser.add_argument("--timeout-s", type=int, default=120)
    parser.add_argument("--free-openrouter-vision", action="store_true")
    parser.add_argument("--model", action="append", default=[], help="Model ref, e.g. openrouter/google/gemma-3-27b-it:free")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    items = bench.load_items(args.dataset)
    if not items:
        print(f"No items found in {args.dataset}", file=sys.stderr)
        return 1

    models = list(args.model)
    if args.free_openrouter_vision:
        models.extend(f"openrouter/{model}" for model in free_openrouter_vision_models())
    deduped_models = []
    seen = set()
    for model in models:
        if model not in seen:
            deduped_models.append(model)
            seen.add(model)
    if not deduped_models:
        print("No models selected", file=sys.stderr)
        return 2

    results = [run_for_model(model, args, items) for model in deduped_models]
    payload = json.dumps({"dataset": str(args.dataset), "results": results}, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
