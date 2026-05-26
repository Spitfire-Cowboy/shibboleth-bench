from __future__ import annotations

import eval as bench


def test_matches_expected_handles_word_and_numeric_aliases():
    assert bench.matches_expected('two', 'two')
    assert bench.matches_expected('2', 'two')
    assert bench.matches_expected('{"answer":"two"}', 'two')


def test_parse_model_response_prefers_json_answer():
    parsed = bench.parse_model_response('{"answer":"two","confidence":"certain"}')
    assert parsed.answer == 'two'
    assert parsed.confidence == 'certain'
    assert parsed.parse_mode == 'json'


def test_score_response_rejects_contradictory_freeform_count():
    score, label, parsed = bench.score_response(
        'The person is wearing 1 hat, but there are 2 hats visible in total.',
        'two',
    )
    assert parsed.answer == '1'
    assert score == 0.0
    assert label == 'incorrect'


def test_score_response_allows_partial_when_json_answer_is_uncertain_but_correct():
    score, label, parsed = bench.score_response(
        '{"answer":"two","confidence":"uncertain","notes":"might be two"}',
        'two',
    )
    assert parsed.parse_mode == 'json'
    assert score == 0.5
    assert label == 'partial'
