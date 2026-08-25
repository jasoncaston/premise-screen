# premise-screen

`premise-screen` is a small rejection engine for product premises. It does not generate ideas, improve pitches, or reward a long candidate list. Its useful output is a high, explainable rejection rate that prevents weak premises from consuming build time.

On 2026-07-03, a source report recorded a read-only screening run in which 22 parallel readers evaluated 110 candidate specifications against the four criteria. The report recorded 35 qualified premises and 75 rejections. It described rejection categories as overlapping estimates rather than an exclusive split, so no categorical counts are claimed here. The per-candidate data is not published.

## The four criteria

A candidate passes only if every answer is `true`:

1. It addresses real, specific pain in an underserved niche.
2. It genuinely fits the delivery form chosen.
3. It can be delivered without a backend, accounts, or a third-party API.
4. It has one clear purpose and a concrete core workflow rather than a generic tracker with a niche label.

See `SCREEN.md` for the complete decision contract and categorical rejection mapping. See `RESULTS.md` for aggregate results only.

## Install

Python 3.11 or newer is required. Runtime code uses only the standard library.

```console
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

Tests use pytest, which is an optional development dependency:

```console
python -m pip install -e '.[test]'
pytest
```

## Run the screen

Input may be JSON or the documented flat YAML form:

```console
premise-screen examples/candidates.yaml
premise-screen examples/candidates.yaml --json
python -m premise_screen examples/candidates.yaml
```

Each candidate has a non-empty `id` and four boolean fields:

```yaml
candidates:
  - id: candidate-001
    specific_pain_underserved: true
    delivery_fit: true
    local_first_deliverable: true
    concrete_single_workflow: true
```

The default table and JSON output return `pass` or `reject` for every candidate. A rejection includes the exact failing criterion and one categorical reason: `generic_shell`, `better_as_phone_app`, or `not_deliverable_local_first`.

## Exit codes

Exit `0` means every candidate passed. Exit `1` means at least one candidate was rejected. Exit `2` means the input was invalid or contained no candidates.

## Aggregate result

| Outcome | Count |
|---|---:|
| Screened | 110 |
| Qualified | 35 |
| Rejected | 75 |

The reported 68.2% rejection rate is the useful output. It sharply reduces the premises allowed to become builds without pretending the missing per-candidate record exists.

## License

Released under the MIT License. See `LICENSE`.
