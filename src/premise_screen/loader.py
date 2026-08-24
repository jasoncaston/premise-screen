from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .screen import CRITERIA


class CandidateInputError(ValueError):
    pass


def load_candidates(path: str | Path) -> list[dict[str, object]]:
    source = Path(path)
    try:
        text = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise CandidateInputError(f"cannot read candidate file: {exc}") from exc

    suffix = source.suffix.lower()
    if suffix == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise CandidateInputError(f"invalid JSON: {exc}") from exc
    elif suffix in {".yaml", ".yml"}:
        data = _parse_flat_yaml(text)
    else:
        raise CandidateInputError("candidate file must end in .json, .yaml, or .yml")
    return _validate_candidates(data)


def _parse_flat_yaml(text: str) -> dict[str, list[dict[str, object]]]:
    """Parse the documented YAML subset without a runtime dependency.

    Supported YAML is a top-level ``candidates`` list containing flat mappings
    with string IDs and boolean criterion values.
    """
    candidates: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    saw_root = False

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.strip() == "candidates:":
            saw_root = True
            continue
        if not saw_root:
            raise CandidateInputError(f"invalid YAML at line {line_number}: expected candidates:")

        stripped = raw_line.strip()
        if stripped.startswith("-"):
            if current is not None:
                candidates.append(current)
            current = {}
            remainder = stripped[1:].strip()
            if remainder:
                key, value = _parse_yaml_pair(remainder, line_number)
                current[key] = value
            continue
        if current is None:
            raise CandidateInputError(f"invalid YAML at line {line_number}: expected list item")
        key, value = _parse_yaml_pair(stripped, line_number)
        current[key] = value

    if current is not None:
        candidates.append(current)
    if not saw_root:
        raise CandidateInputError("invalid YAML: expected candidates:")
    return {"candidates": candidates}


def _parse_yaml_pair(text: str, line_number: int) -> tuple[str, object]:
    match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*):\s*(.*)", text)
    if not match or not match.group(2):
        raise CandidateInputError(f"invalid YAML mapping at line {line_number}")
    key, raw_value = match.groups()
    lowered = raw_value.lower()
    if lowered == "true":
        return key, True
    if lowered == "false":
        return key, False
    if (raw_value.startswith('"') and raw_value.endswith('"')) or (
        raw_value.startswith("'") and raw_value.endswith("'")
    ):
        return key, raw_value[1:-1]
    return key, raw_value


def _validate_candidates(data: Any) -> list[dict[str, object]]:
    if isinstance(data, dict):
        data = data.get("candidates")
    if not isinstance(data, list):
        raise CandidateInputError("input must contain a candidates list")

    required_fields = [criterion.field for criterion in CRITERIA]
    validated: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    for index, candidate in enumerate(data, start=1):
        if not isinstance(candidate, dict):
            raise CandidateInputError(f"candidate {index} must be an object")
        candidate_id = candidate.get("id")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            raise CandidateInputError(f"candidate {index} requires a non-empty string id")
        if candidate_id in seen_ids:
            raise CandidateInputError(f"duplicate candidate id: {candidate_id}")
        seen_ids.add(candidate_id)
        normalized: dict[str, object] = {"id": candidate_id}
        for field in required_fields:
            value = candidate.get(field)
            if not isinstance(value, bool):
                raise CandidateInputError(f"candidate {candidate_id} requires boolean field {field}")
            normalized[field] = value
        validated.append(normalized)
    return validated
