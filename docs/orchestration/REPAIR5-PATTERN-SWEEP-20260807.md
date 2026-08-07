# Repair-5 — the four defects, their self-guards, and a sweep of the two recurring patterns

Repair-5 closes the four defects the verifier left open on repair-4
(`runs/standard-p4-verifier/20260807T134623Z-repair4-verdict.json`) and, on Joseph's
instruction, treats them as **instances of two patterns** rather than four sites.

---

## 1. Self-guards — the assertion that fails if each defect returns

Joseph's rule: *if you can't name one, the defect isn't closed.* Each row names a test that is
a live computation against the repaired behaviour, not a restatement of the fix.

| Defect | Reintroducing it looks like | Assertion that then FAILS |
|---|---|---|
| **D2** receipt source identity | accept a receipt whose `code_rev` disagrees with HEAD | `test_stale_code_rev_rejected_with_reason` — asserts rc=1 **and** the phrase `different revision`; a bare rc≠0 would not distinguish it from any other error |
| **D2** (source blob) | accept an endpoint produced by a changed unfold driver | `test_stale_unfold_blob_rejected_with_reason` — asserts `unfold driver changed` |
| **D2** (shape) | go back to a receipt with no source identity at all | `test_receipt_without_source_identity_rejected` — the pre-repair-5 shape must fail `missing required keys` |
| **D3** fail-open on deletion | restore the `_w is None or` disjunct | `test_deleted_bound_source_is_a_blocker_not_a_pass` — asserts the disjunct is **absent** and `need(_c == _w,` is present, plus the `ABSENT from the working tree` branch exists |
| **D4a** containment | revert to `normpath`/substring containment | `test_absolute_path_outside_the_repo_is_rejected` (the verifier's exact `/evil/...` bypass) and `test_symlink_escape_is_rejected`, which **creates a real symlink** out of the candidate dir and requires rejection — `normpath` cannot see it, `realpath` can |
| **D4a** (not over-tightened) | a guard that cannot pass | `test_legitimate_candidate_paths_still_accepted` — both the ND-relative and repo-relative real forms must PASS |
| **D4b** identity overclaim | go back to PSD-only | `test_psd_residual_that_is_not_stat_plus_ml_fails` — constructs a residual that **is** symmetric PSD (so the repair-4 check passes, asserted explicitly on the same object) and **is not** stat+ML, then requires the real gate to raise |
| **D4b** (substitution) | compare against the wrong blocks | `test_full_total_identity_catches_a_swapped_stat_block`; and the validator re-verifies the stat/ML `sha256` the manifest recorded before loading them, so the identity cannot be satisfied by swapping files |
| **D6** strong-name-over-weak-check | re-add a test named for a stronger claim than it makes | `test_validator_proves_full_total_against_the_bound_stat_and_ml_blocks` asserts the retired gate name `combined_minus_syst_is_psd` is **absent** from the validator |
| **D6** (real execution) | assert on source text only | the whole `ReceiptGateIntegration` class runs `p4_check_receipt.py` as a subprocess, incl. a happy path — a gate that has never returned OK on real input is unverified in the direction that matters |

---

## 2. Pattern A — "assert presence, never compare"

**Instances found. Three were live; two are now fixed; two remain and are named below.**

| # | Site | State |
|---|---|---|
| A1 | `P4_VERIFIER_PASS` non-emptiness (`run_p4_standard.sh:41`) | **OPEN** — `KNOWN_ISSUES.md` #21, the original instance. Deliberately not fixed here: the gate is Joseph's human checkpoint and changing it mid-round would alter the thing being used to authorise the round. |
| A2 | `code_rev` presence in the receipt gate | **FIXED** (D2) — compared to HEAD, and a source blob added and compared |
| A3 | **`identities` written as literal `True`** (`p4_build_components.py`) — four flags asserting equalities, with two consumers (`p4_validate_active_lateral.py`, `p4_adopt_standard.py`) reading them as evidence | **FIXED** — now four MEASURED relative errors plus `identity_rtol`; both consumers reject the retired `pure_addition` key and check the measurements against the tolerance; the validator additionally **recomputes** the full-total identity rather than reading any of them |
| A4 | **`migration_policy`** (`p4_lib.check_merged_metadata`) — required truthy, compared to nothing; a merged file could declare any policy string, or the wrong one, and pass | **FIXED** — `check_declared_migration_policy` compares the declaration against the observed census in both directions |
| A5 | `nTruthOnlyMisses` / `hasTruthOnlyMisses` (`p4_lib.py`, `p4_evidence.py`) — required non-`None`, never compared to anything | **OPEN, reported not fixed.** There is no independent expected value to compare against without re-deriving the native-miss count from the merged tree, which is a physics read this round should not add. Recorded so it is not mistaken for a check. |

**Structural fix, not just site fixes:** the migration-band sets were **duplicated** in
`p4_evidence.py` and `p4_validate_active_lateral.py` — two private copies of a policy, one edit
from disagreeing. They are now single-sourced as `p4_lib.NONZERO_MIGRATION_BANDS` /
`ZERO_MIGRATION_BANDS`, with a test asserting both consumers use them and that the two sets
partition the five bands exactly.

## 3. Pattern B — "strong name over weak check"

| # | Site | State |
|---|---|---|
| B1 | `test_project_rejects_protected_out_path` passing `--proj` so argparse fired before the guard | **FIXED in repair-4** (verifier defect 6b) — now asserts the specific guard message and explicitly rejects `unrecognized arguments` |
| B2 | `combined_minus_syst_is_psd` presented as the **full-total identity** — in the gate name, the receipt field, the test name and the commit message | **FIXED** — replaced by `check_full_total_identity`, which compares the residual to the bound stat+ML blocks; the gate, the receipt field and the test are all renamed to what they now do |
| B3 | `identities` key names (`C_syst_eq_sum_bands`, `pure_addition`, …) naming equalities whose values were literals | **FIXED** with A3 — the names now end in `_relerr` and carry measurements |
| B4 | `check_support_comparison` — named a "comparison", returns a ratio, and the validator records it without a pass/fail bound | **OPEN, reported not fixed.** It is genuinely diagnostic today (there is no declared tolerance for the support ratio, and inventing one would be a physics decision, not a repair). Flagged so nobody later reads its presence in the PASS receipt as a gate. |

---

## 4. What is deliberately NOT repaired

- **A1 / `KNOWN_ISSUES.md` #21** — the verifier-token gate itself. Joseph's checkpoint.
- **`4d`** — `p4_adopt_standard.py` still performs no promotion. Adoption is out of scope; the
  chain stops at CANDIDATE. Its *gates* were tightened here only because A3 changed the
  manifest shape underneath it, and leaving it reading a now-absent key would have made
  adoption fail for the wrong reason.
- **A5, B4** — named above with the reason each needs a decision rather than a patch.
