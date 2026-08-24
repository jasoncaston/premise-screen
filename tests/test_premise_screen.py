from __future__ import annotations

import json
from pathlib import Path

import pytest

from premise_screen.cli import main, render_table
from premise_screen.loader import load_candidates
from premise_screen.screen import screen_candidate, screen_candidates


def candidate(**overrides: bool) -> dict[str, object]:
    value: dict[str, object] = {
        "id": "candidate-test",
        "specific_pain_underserved": True,
        "delivery_fit": True,
        "local_first_deliverable": True,
        "concrete_single_workflow": True,
    }
    value.update(overrides)
    return value


@pytest.fixture
def yaml_candidates(tmp_path: Path) -> Path:
    source = tmp_path / "candidates.yaml"
    source.write_text(
        """candidates:
  - id: candidate-pass
    specific_pain_underserved: true
    delivery_fit: true
    local_first_deliverable: true
    concrete_single_workflow: true
  - id: candidate-reject
    specific_pain_underserved: true
    delivery_fit: false
    local_first_deliverable: true
    concrete_single_workflow: true
""",
        encoding="utf-8",
    )
    return source


def test_rejects_missing_specific_pain_as_generic_shell() -> None:
    result = screen_candidate(candidate(specific_pain_underserved=False))
    assert result.result == "reject"
    assert result.failing_criterion == "real_specific_pain_in_underserved_niche"
    assert result.rejection_category == "generic_shell"


def test_rejects_delivery_mismatch_as_better_phone_app() -> None:
    result = screen_candidate(candidate(delivery_fit=False))
    assert result.result == "reject"
    assert result.failing_criterion == "genuinely_fits_chosen_delivery_form"
    assert result.rejection_category == "better_as_phone_app"


def test_rejects_backend_dependency_as_not_local_first() -> None:
    result = screen_candidate(candidate(local_first_deliverable=False))
    assert result.result == "reject"
    assert result.failing_criterion == "deliverable_without_backend_accounts_or_third_party_api"
    assert result.rejection_category == "not_deliverable_local_first"


def test_rejects_generic_workflow_as_generic_shell() -> None:
    result = screen_candidate(candidate(concrete_single_workflow=False))
    assert result.result == "reject"
    assert result.failing_criterion == "one_clear_purpose_with_concrete_core_workflow"
    assert result.rejection_category == "generic_shell"


def test_clean_candidate_passes_without_failure_fields() -> None:
    result = screen_candidate(candidate())
    assert result.result == "pass"
    assert result.failing_criterion is None
    assert result.rejection_category is None


def test_yaml_loader_and_json_cli_return_real_results(yaml_candidates: Path, capsys: pytest.CaptureFixture[str]) -> None:
    loaded = load_candidates(yaml_candidates)
    assert loaded[0]["id"] == "candidate-pass"
    assert loaded[1]["delivery_fit"] is False

    exit_code = main([str(yaml_candidates), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert payload[0] == {
        "candidate_id": "candidate-pass",
        "failing_criterion": None,
        "rejection_category": None,
        "result": "pass",
    }
    assert payload[1] == {
        "candidate_id": "candidate-reject",
        "failing_criterion": "genuinely_fits_chosen_delivery_form",
        "rejection_category": "better_as_phone_app",
        "result": "reject",
    }


def test_json_input_is_supported(tmp_path: Path) -> None:
    source = tmp_path / "candidates.json"
    source.write_text(json.dumps({"candidates": [candidate()]}), encoding="utf-8")
    loaded = load_candidates(source)
    result = screen_candidate(loaded[0])
    assert loaded[0]["concrete_single_workflow"] is True
    assert result.result == "pass"
    assert result.candidate_id == "candidate-test"


def test_default_table_renderer_contains_real_results() -> None:
    passed = candidate()
    passed["id"] = "candidate-pass"
    rejected = candidate(delivery_fit=False)
    rejected["id"] = "candidate-reject"
    table = render_table(screen_candidates([passed, rejected]))

    assert "CANDIDATE" in table
    assert "candidate-pass" in table
    assert "candidate-reject" in table
    assert "genuinely_fits_chosen_delivery_form" in table
    assert "better_as_phone_app" in table


def test_empty_candidate_list_has_defined_non_rejection_exit(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = tmp_path / "empty.json"
    source.write_text('{"candidates": []}\n', encoding="utf-8")

    exit_code = main([str(source)])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == "No candidates found.\n"
    assert captured.err == ""
    assert render_table([]) == "No candidates found."


def test_invalid_input_returns_exit_two_with_specific_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = tmp_path / "invalid.json"
    incomplete = candidate()
    del incomplete["concrete_single_workflow"]
    source.write_text(json.dumps({"candidates": [incomplete]}), encoding="utf-8")

    exit_code = main([str(source)])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert captured.err == (
        "ERROR: candidate candidate-test requires boolean field concrete_single_workflow\n"
    )
