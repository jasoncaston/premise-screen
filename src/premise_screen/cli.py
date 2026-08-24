from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .loader import CandidateInputError, load_candidates
from .screen import CandidateResult, screen_candidates


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="premise-screen",
        description="Reject product premises that fail a four-criterion screen.",
    )
    parser.add_argument("candidate_file", help="JSON or supported YAML candidate file")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        results = screen_candidates(load_candidates(args.candidate_file))
    except CandidateInputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps([result.to_dict() for result in results], indent=2, sort_keys=True))
    else:
        print(render_table(results))
    if not results:
        return 2
    return 1 if any(result.result == "reject" for result in results) else 0


def render_table(results: list[CandidateResult]) -> str:
    if not results:
        return "No candidates found."
    headers = ("CANDIDATE", "RESULT", "FAILING CRITERION", "CATEGORY")
    rows = [
        (
            result.candidate_id,
            result.result,
            result.failing_criterion or "—",
            result.rejection_category or "—",
        )
        for result in results
    ]
    widths = [max(len(headers[index]), *(len(row[index]) for row in rows)) for index in range(len(headers))]
    header = "  ".join(value.ljust(widths[index]) for index, value in enumerate(headers))
    divider = "  ".join("-" * width for width in widths)
    body = ["  ".join(value.ljust(widths[index]) for index, value in enumerate(row)) for row in rows]
    return "\n".join([header, divider, *body])


if __name__ == "__main__":
    raise SystemExit(main())
