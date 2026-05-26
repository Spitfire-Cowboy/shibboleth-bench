#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import re
import statistics
import sys
import time
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
class ParsedResponse:
    answer: str
    confidence: str | None = None
    notes: str | None = None
    parse_mode: str = "freeform"


@dataclass
class ItemResult:
    item_id: str
    response: str
    parsed_answer: str
    parse_mode: str
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


PROMPT_SUFFIX = (
    'Return strict JSON with keys "answer", "confidence", and optional "notes". '
    'Use "answer" for the direct final answer only. '
    'Set "confidence" to "certain" or "uncertain". '
    'Do not include markdown fences.'
)


def dataset_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_items(path: Path) -> list[Item]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(Item(**json.loads(line)))
    return rows


def normalize_answer(value: str) -> str:
    text = (value or "").strip().lower()
    text = re.sub(r"[`*_#]", "", text)
    text = re.sub(r"\b(hats?|people|person|wearing|is|are|there|visible|total)\b", " ", text)
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def matches_expected(response: str, expected: str) -> bool:
    response_norm = normalize_answer(response)
    expected_norm = normalize_answer(expected)
    if not response_norm or not expected_norm:
        return False
    if expected_norm == response_norm:
        return True
    if re.search(rf"\b{re.escape(expected_norm)}\b", response_norm):
        return True
    alias = NUMBER_ALIASES.get(expected_norm)
    if alias and re.search(rf"\b{re.escape(alias)}\b", response_norm):
        return True
    return False


def extract_json_object(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def extract_candidate_answer(text: str) -> str:
    lowered = text.lower()
    patterns = [
        r"wearing\s+([a-z0-9-]+)\s+hat",
        r"wearing\s+([a-z0-9-]+)\s+hats",
        r"is\s+([a-z0-9-]+)\s+hat",
        r"is\s+wearing\s+([a-z0-9-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, lowered)
        if match:
            return match.group(1)
    generic = re.search(r"(zero|one|two|three|four|five|six|seven|eight|nine|ten|[0-9]+)", lowered)
    if generic:
        return generic.group(1)
    return text.strip()


def parse_model_response(response: str) -> ParsedResponse:
    if response.startswith("[ERROR:"):
        return ParsedResponse(answer="", parse_mode="error")
    obj = extract_json_object(response)
    if obj is not None:
        answer = str(obj.get("answer", "")).strip()
        confidence = str(obj.get("confidence", "")).strip().lower() or None
        notes = str(obj.get("notes", "")).strip() or None
        return ParsedResponse(answer=answer, confidence=confidence, notes=notes, parse_mode="json")
    return ParsedResponse(answer=extract_candidate_answer(response), parse_mode="freeform")


def score_response(response: str, expected: str) -> tuple[float, str, ParsedResponse]:
    parsed = parse_model_response(response)
    if parsed.parse_mode == "error":
        return 0.0, "incorrect", parsed
    answer_text = parsed.answer
    response_lower = response.lower()
    correct = matches_expected(answer_text, expected)
    hedged = (
        (parsed.confidence == "uncertain")
        or any(keyword in response_lower for keyword in PARTIAL_KEYWORDS)
    )
    if correct and hedged:
        return 0.5, "partial", parsed
    if correct:
        return 1.0, "correct", parsed
    return 0.0, "incorrect", parsed


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


class OpenAIResponsesAdapter:
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
            "input": [{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": data_url, "detail": "high"},
                ],
            }],
            "max_output_tokens": 256,
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            return f"[ERROR: {exc}]"
        text = data.get("output_text")
        if text:
            return text
        output = data.get("output") or []
        for item in output:
            for content in item.get("content") or []:
                if content.get("type") == "output_text" and content.get("text"):
                    return content["text"]
        return "[ERROR: empty output in response]"


class XAIChatAdapter:
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
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}},
                    {"type": "text", "text": prompt},
                ],
            }],
            "stream": False,
            "max_tokens": 256,
        }
        req = urllib.request.Request(
            "https://api.x.ai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
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
    if model.startswith("openai/"):
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for openai/<model>")
        return OpenAIResponsesAdapter(model[len("openai/"):], api_key, timeout_s)
    if model.startswith("xai/"):
        api_key = os.environ.get("XAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("XAI_API_KEY is required for xai/<model>")
        return XAIChatAdapter(model[len("xai/"):], api_key, timeout_s)
    raise ValueError("Supported prefixes: dry-run, ollama/, openrouter/, openai/, xai/")


def build_prompt(item: Item) -> str:
    return f"{item.prompt}\n\n{PROMPT_SUFFIX}"


def evaluate(items: list[Item], adapter) -> RunResult:
    results: list[ItemResult] = []
    for item in items:
        image_path = str((ROOT / item.image_path).resolve()) if not Path(item.image_path).is_absolute() else item.image_path
        t0 = time.monotonic()
        response = adapter.query(image_path, build_prompt(item))
        latency_ms = int((time.monotonic() - t0) * 1000)
        score, label, parsed = score_response(response, item.expected)
        results.append(
            ItemResult(
                item_id=item.id,
                response=response[:2000],
                parsed_answer=parsed.answer,
                parse_mode=parsed.parse_mode,
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

    if args.dry_run:
        args.model = "dry-run"

    items = load_items(args.dataset)
    if not items:
        print(f"No items found in {args.dataset}", file=sys.stderr)
        return 1

    try:
        adapter = build_adapter(args.model, args.ollama_host, args.ollama_think, args.ollama_timeout_s)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    result = evaluate(items, adapter)
    payload = {
        **asdict(result),
        "dataset": display_path(args.dataset),
        "dataset_sha256": dataset_sha256(args.dataset),
        "run_at": datetime.now(timezone.utc).isoformat(),
        "prompt_protocol": "structured-json-v1",
    }
    text = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
