#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import statistics
import sys
import time
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

PARTIAL_KEYWORDS = ("maybe", "possibly", "might", "could be", "not sure", "uncertain")
NUMBER_ALIASES = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}
ROOT = Path(__file__).resolve().parent


@dataclass
class Item:
    id: str
    category: str
    image_path: str
    prompt: str
    expected: str
    notes: str = ""


@dataclass
class ItemResult:
    item_id: str
    response: str
    score: float
    score_label: str
    latency_ms: int


@dataclass
class RunResult:
    model: str
    total_items: int
    correct: int
    partial: int
    incorrect: int
    accuracy: float
    partial_credit_score: float
    latency_mean_ms: float
    latency_p50_ms: float
    items: list[ItemResult]


def load_items(path: Path) -> list[Item]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(Item(**json.loads(line)))
    return rows


def matches_expected(response: str, expected: str) -> bool:
    response_lower = response.lower()
    expected_lower = expected.lower()
    if expected_lower in response_lower:
        return True
    alias = NUMBER_ALIASES.get(expected_lower)
    if alias and re.search(rf"\b{re.escape(alias)}\b", response_lower):
        return True
    return False


def score_response(response: str, expected: str) -> tuple[float, str]:
    if response.startswith("[ERROR:"):
        return 0.0, "incorrect"
    response_lower = response.lower()
    correct = matches_expected(response, expected)
    hedged = any(keyword in response_lower for keyword in PARTIAL_KEYWORDS)
    if correct and hedged:
        return 0.5, "partial"
    if correct:
        return 1.0, "correct"
    return 0.0, "incorrect"


class DryRunAdapter:
    name = "dry-run"

    def query(self, image_path: str, prompt: str) -> str:
        return ""


class OllamaAdapter:
    def __init__(self, model: str, host: str, think: bool | None, timeout_s: int):
        self.name = model
        self.host = host.rstrip("/")
        self.think = think
        self.timeout_s = timeout_s

    def query(self, image_path: str, prompt: str) -> str:
        try:
            img_bytes = Path(image_path).read_bytes()
        except OSError as exc:
            return f"[ERROR: cannot read image {image_path}: {exc}]"

        payload = {
            "model": self.name,
            "prompt": prompt,
            "images": [base64.b64encode(img_bytes).decode("utf-8")],
            "stream": False,
        }
        if self.think is not None:
            payload["think"] = self.think

        req = urllib.request.Request(
            f"{self.host}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            return f"[ERROR: {exc}]"
        return data.get("response", "")


class OpenRouterAdapter:
    def __init__(self, model: str, api_key: str, timeout_s: int):
        self.name = model
        self.api_key = api_key
        self.timeout_s = timeout_s

    def query(self, image_path: str, prompt: str) -> str:
        try:
            img_bytes = Path(image_path).read_bytes()
        except OSError as exc:
            return f"[ERROR: cannot read image {image_path}: {exc}]"

        mime = mimetypes.guess_type(image_path)[0] or "image/png"
        data_url = f"data:{mime};base64,{base64.b64encode(img_bytes).decode('utf-8')}"
        payload = {
            "model": self.name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            "max_tokens": 256,
        }
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/Spitfire-Cowboy/shibboleth-bench",
                "X-Title": "shibboleth-bench",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            return f"[ERROR: {exc}]"

        choices = data.get("choices") or []
        if not choices:
            return "[ERROR: empty choices in response]"
        return ((choices[0].get("message") or {}).get("content")) or ""


def build_adapter(model: str, host: str, think: str, timeout_s: int):
    if model == "dry-run":
        return DryRunAdapter()
    if model.startswith("ollama/"):
        think_value = None
        if think == "true":
            think_value = True
        elif think == "false":
            think_value = False
        return OllamaAdapter(model[len("ollama/"):], host, think_value, timeout_s)
    if model.startswith("openrouter/"):
        api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is required for openrouter/<model>")
        return OpenRouterAdapter(model[len("openrouter/"):], api_key, timeout_s)
    raise ValueError("Only dry-run, ollama/<model>, and openrouter/<model> are supported")


def evaluate(items: list[Item], adapter) -> RunResult:
    results: list[ItemResult] = []
    for item in items:
        image_path = str((ROOT / item.image_path).resolve()) if not Path(item.image_path).is_absolute() else item.image_path
        t0 = time.monotonic()
        response = adapter.query(image_path, item.prompt)
        latency_ms = int((time.monotonic() - t0) * 1000)
        score, label = score_response(response, item.expected)
        results.append(
            ItemResult(
                item_id=item.id,
                response=response[:500],
                score=score,
                score_label=label,
                latency_ms=latency_ms,
            )
        )

    correct = sum(1 for result in results if result.score_label == "correct")
    partial = sum(1 for result in results if result.score_label == "partial")
    incorrect = sum(1 for result in results if result.score_label == "incorrect")
    latencies = [result.latency_ms for result in results]
    total = len(results)
    accuracy = correct / total if total else 0.0
    partial_credit = (correct + 0.5 * partial) / total if total else 0.0
    return RunResult(
        model=adapter.name,
        total_items=total,
        correct=correct,
        partial=partial,
        incorrect=incorrect,
        accuracy=round(accuracy, 4),
        partial_credit_score=round(partial_credit, 4),
        latency_mean_ms=round(statistics.mean(latencies), 1) if latencies else 0.0,
        latency_p50_ms=round(statistics.median(latencies), 1) if latencies else 0.0,
        items=results,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Shibboleth benchmark.")
    parser.add_argument("--dataset", type=Path, default=ROOT / "dataset" / "items.jsonl")
    parser.add_argument("--model", default="dry-run")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ollama-host", default="http://127.0.0.1:11434")
    parser.add_argument("--ollama-think", choices=("default", "true", "false"), default="default")
    parser.add_argument("--ollama-timeout-s", type=int, default=60)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    model = "dry-run" if args.dry_run else args.model
    items = load_items(args.dataset)
    if not items:
        print(f"No items found in {args.dataset}", file=sys.stderr)
        return 1

    adapter = build_adapter(model, args.ollama_host, args.ollama_think, args.ollama_timeout_s)
    result = evaluate(items, adapter)
    payload = json.dumps(asdict(result), indent=2) + "\n"
    output = args.output
    if output:
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
