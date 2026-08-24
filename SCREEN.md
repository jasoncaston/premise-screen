# The Premise Screen

The screen exists to kill weak product ideas before design and implementation make them expensive to abandon. A candidate passes only when all four criteria are true. Evaluation stops at the first failure and returns the criterion name plus a categorical rejection code.

## 1. Real, specific pain in an underserved niche

The premise must solve an observable, repeated problem for a clearly bounded group that is not already well served. A broad aspiration, invented inconvenience, or audience label without a concrete pain does not pass.

**Required field:** `specific_pain_underserved`

**Failure criterion:** `real_specific_pain_in_underserved_niche`

**Rejection category:** `generic_shell`

## 2. Genuine fit for the chosen delivery form

The core work must belong in the proposed form. A desktop utility, command-line tool, browser extension, static document, or other chosen form must provide the right interaction at the moment the work occurs; the form cannot be an arbitrary wrapper around a workflow better served elsewhere.

**Required field:** `delivery_fit`

**Failure criterion:** `genuinely_fits_chosen_delivery_form`

**Rejection category:** `better_as_phone_app`

## 3. Deliverable local-first

The complete useful workflow must run without a backend, user accounts, or a third-party API. Local files, browser storage, and deterministic computation are acceptable. A premise that depends on remote state, paid data, hosted coordination, or an external account does not pass.

**Required field:** `local_first_deliverable`

**Failure criterion:** `deliverable_without_backend_accounts_or_third_party_api`

**Rejection category:** `not_deliverable_local_first`

## 4. One clear purpose and concrete core workflow

The premise must perform one recognizable job through a specific sequence of inputs, decisions, and outputs. A generic tracker, dashboard, form builder, or record list with only a niche label changed does not pass.

**Required field:** `concrete_single_workflow`

**Failure criterion:** `one_clear_purpose_with_concrete_core_workflow`

**Rejection category:** `generic_shell`

## Decision contract

- All four values `true`: `pass`.
- First `false` value in screen order: `reject` with that criterion and its categorical rejection code.
- Missing, non-boolean, or duplicate input: invalid input, not a screened result.
- A rejection reason is always a stable category, never generated prose.
