from __future__ import annotations

from pathlib import Path

import eval as bench


class StubAdapter:
    def __init__(self, responses: dict[str, str]):
        self.name = "stub"
        self._responses = responses
        self.calls: list[tuple[str, str]] = []

    def query(self, image_path: str, prompt: str) -> str:
        item_id = Path(image_path).stem
        self.calls.append((image_path, prompt))
        return self._responses[item_id]


def test_load_items_reads_jsonl_rows(tmp_path: Path):
    dataset = tmp_path / "items.jsonl"
    dataset.write_text(
        '{"id":"SB-001","category":"count","image_path":"dataset/images/one.png","prompt":"How many?","expected":"one"}\n\n'
        '{"id":"SB-002","category":"count","image_path":"dataset/images/two.png","prompt":"How many?","expected":"two","notes":"second"}\n',
        encoding="utf-8",
    )

    items = bench.load_items(dataset)

    assert [item.id for item in items] == ["SB-001", "SB-002"]
    assert items[1].notes == "second"


def test_matches_expected_handles_word_and_numeric_aliases():
    assert bench.matches_expected("two", "two")
    assert bench.matches_expected("2", "two")
    assert bench.matches_expected('{"answer":"two"}', "two")


def test_parse_model_response_prefers_json_answer():
    parsed = bench.parse_model_response('{"answer":"two","confidence":"certain"}')
    assert parsed.answer == "two"
    assert parsed.confidence == "certain"
    assert parsed.parse_mode == "json"


def test_score_response_rejects_contradictory_freeform_count():
    score, label, parsed = bench.score_response(
        "The person is wearing 1 hat, but there are 2 hats visible in total.",
        "two",
    )
    assert parsed.answer == "1"
    assert score == 0.0
    assert label == "incorrect"


def test_score_response_allows_partial_when_json_answer_is_uncertain_but_correct():
    score, label, parsed = bench.score_response(
        '{"answer":"two","confidence":"uncertain","notes":"might be two"}',
        "two",
    )
    assert parsed.parse_mode == "json"
    assert score == 0.5
    assert label == "partial"


def test_score_response_marks_error_payload_incorrect():
    score, label, parsed = bench.score_response("[ERROR: timeout]", "two")

    assert parsed.parse_mode == "error"
    assert score == 0.0
    assert label == "incorrect"


def test_build_adapter_supports_and_rejects_expected_prefixes(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
    monkeypatch.setenv("OPENAI_API_KEY", "oa-key")
    monkeypatch.setenv("XAI_API_KEY", "xai-key")

    dry = bench.build_adapter("dry-run", "http://localhost:11434", "default", 30)
    ollama = bench.build_adapter("ollama/llava", "http://localhost:11434", "true", 30)
    openrouter = bench.build_adapter("openrouter/google/gemma", "http://localhost:11434", "default", 30)
    openai = bench.build_adapter("openai/gpt-4.1", "http://localhost:11434", "default", 30)
    xai = bench.build_adapter("xai/grok-4.3", "http://localhost:11434", "default", 30)

    assert isinstance(dry, bench.DryRunAdapter)
    assert isinstance(ollama, bench.OllamaAdapter)
    assert ollama.think is True
    assert isinstance(openrouter, bench.OpenRouterAdapter)
    assert isinstance(openai, bench.OpenAIResponsesAdapter)
    assert isinstance(xai, bench.XAIChatAdapter)

    try:
        bench.build_adapter("anthropic/claude", "http://localhost:11434", "default", 30)
    except ValueError as exc:
        assert "Supported prefixes" in str(exc)
    else:
        raise AssertionError("expected ValueError for unsupported adapter prefix")


def test_evaluate_computes_summary_metrics(monkeypatch):
    items = [
        bench.Item(id="one", category="count", image_path="/tmp/one.png", prompt="How many?", expected="one"),
        bench.Item(id="two", category="count", image_path="/tmp/two.png", prompt="How many?", expected="two"),
        bench.Item(id="three", category="count", image_path="/tmp/three.png", prompt="How many?", expected="three"),
    ]
    adapter = StubAdapter(
        {
            "one": '{"answer":"one","confidence":"certain"}',
            "two": '{"answer":"two","confidence":"uncertain"}',
            "three": "zero",
        }
    )
    ticks = iter([0.0, 0.01, 0.01, 0.03, 0.03, 0.06])
    monkeypatch.setattr(bench.time, "monotonic", lambda: next(ticks))

    result = bench.evaluate(items, adapter)

    assert result.model == "stub"
    assert result.total_items == 3
    assert result.correct == 1
    assert result.partial == 1
    assert result.incorrect == 1
    assert result.accuracy == 0.3333
    assert result.partial_credit_score == 0.5
    assert result.latency_mean_ms == 19.7
    assert result.latency_p50_ms == 19
    assert [item.score_label for item in result.items] == ["correct", "partial", "incorrect"]
    assert all(bench.PROMPT_SUFFIX in prompt for _, prompt in adapter.calls)
