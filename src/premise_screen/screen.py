from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class Criterion:
    field: str
    name: str
    rejection_category: str


CRITERIA = (
    Criterion(
        "specific_pain_underserved",
        "real_specific_pain_in_underserved_niche",
        "generic_shell",
    ),
    Criterion(
        "delivery_fit",
        "genuinely_fits_chosen_delivery_form",
        "better_as_phone_app",
    ),
    Criterion(
        "local_first_deliverable",
        "deliverable_without_backend_accounts_or_third_party_api",
        "not_deliverable_local_first",
    ),
    Criterion(
        "concrete_single_workflow",
        "one_clear_purpose_with_concrete_core_workflow",
        "generic_shell",
    ),
)


@dataclass(frozen=True)
class CandidateResult:
    candidate_id: str
    result: str
    failing_criterion: str | None
    rejection_category: str | None

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


def screen_candidate(candidate: Mapping[str, object]) -> CandidateResult:
    candidate_id = str(candidate["id"])
    for criterion in CRITERIA:
        if candidate[criterion.field] is not True:
            return CandidateResult(
                candidate_id=candidate_id,
                result="reject",
                failing_criterion=criterion.name,
                rejection_category=criterion.rejection_category,
            )
    return CandidateResult(
        candidate_id=candidate_id,
        result="pass",
        failing_criterion=None,
        rejection_category=None,
    )


def screen_candidates(candidates: Iterable[Mapping[str, object]]) -> list[CandidateResult]:
    return [screen_candidate(candidate) for candidate in candidates]
