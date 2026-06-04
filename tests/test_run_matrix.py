from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

import eval as bench
import run_matrix


class FakeAdapter:
    name = "fake"

    def query(self, image_path: str, prompt: str) -> str:
        return '{"answer":"one","confidence":"certain"}'


def test_free_openrouter_vision_models_filters_expected_variants(monkeypatch):
    monkeypatch.setattr(
        run_matrix,
        "fetch_openrouter_models",
        lambda: [
            {
                "id": "google/lyria-2",
                "pricing": {"prompt": "0", "completion": "0"},
                "architecture": {"input_modalities": ["image"], "output_modalities": ["text"]},
            },
            {
                "id": "openai/gpt-4.1-mini",
                "pricing": {"prompt": "0", "completion": "0"},
                "architecture": {"input_modalities": ["image", "text"], "output_modalities": ["text"]},
            },
            {
                "id": "anthropic/claude-paid",
                "pricing": {"prompt": "1", "completion": "0"},
                "architecture": {"input_modalities": ["image"], "output_modalities": ["text"]},
            },
            {
                "id": "text/only",
                "pricing": {"prompt": "0", "completion": "0"},
                "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]},
            },
        ],
    )

    assert run_matrix.free_openrouter_vision_models() == ["openai/gpt-4.1-mini"]


def test_run_for_model_returns_structured_error_on_adapter_failure(monkeypatch):
    item = bench.Item(id="SB-001", category="count", image_path="dataset/images/two-hat-logo.png", prompt="How many?", expected="one")
    args = SimpleNamespace(ollama_host="http://localhost:11434", ollama_think="default", timeout_s=30)
    monkeypatch.setattr(run_matrix.bench, "build_adapter", lambda *a, **k: (_ for _ in ()).throw(ValueError("boom")))

    payload = run_matrix.run_for_model("openrouter/bad-model", args, [item])

    assert payload["model"] == "openrouter/bad-model"
    assert payload["total_items"] == 1
    assert payload["incorrect"] == 1
    assert payload["error"] == "boom"


def test_main_dedupes_models_and_writes_stable_json(monkeypatch, tmp_path: Path):
    dataset = tmp_path / "items.jsonl"
    dataset.write_text(
        '{"id":"SB-001","category":"count","image_path":"dataset/images/two-hat-logo.png","prompt":"How many?","expected":"one"}\n',
        encoding="utf-8",
    )
    output = tmp_path / "result.json"
    items = [bench.Item(id="SB-001", category="count", image_path="dataset/images/two-hat-logo.png", prompt="How many?", expected="one")]
    captured_models: list[str] = []

    def fake_run_for_model(model: str, args, loaded_items):
        captured_models.append(model)
        assert loaded_items == items
        return {
            "model": model,
            "model_ref": model,
            "total_items": len(loaded_items),
            "correct": 1,
            "partial": 0,
            "incorrect": 0,
            "accuracy": 1.0,
            "partial_credit_score": 1.0,
            "latency_mean_ms": 5.0,
            "latency_p50_ms": 5.0,
            "items": [],
        }

    monkeypatch.setattr(run_matrix.bench, "load_items", lambda path: items)
    monkeypatch.setattr(run_matrix.bench, "dataset_sha256", lambda path: "deadbeef")
    monkeypatch.setattr(run_matrix.bench, "display_path", lambda path: "dataset/items.jsonl")
    monkeypatch.setattr(run_matrix, "free_openrouter_vision_models", lambda: ["vendor/free-vision", "vendor/free-vision"])
    monkeypatch.setattr(run_matrix, "run_for_model", fake_run_for_model)
    monkeypatch.setattr(
        run_matrix.sys,
        "argv",
        [
            "run_matrix.py",
            "--dataset",
            str(dataset),
            "--free-openrouter-vision",
            "--model",
            "openai/gpt-4.1",
            "--model",
            "openai/gpt-4.1",
            "--output",
            str(output),
        ],
    )

    rc = run_matrix.main()

    assert rc == 0
    assert captured_models == ["openai/gpt-4.1", "openrouter/vendor/free-vision"]
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["dataset"] == "dataset/items.jsonl"
    assert payload["dataset_sha256"] == "deadbeef"
    assert payload["prompt_protocol"] == "structured-json-v1"
    assert [row["model_ref"] for row in payload["results"]] == captured_models
