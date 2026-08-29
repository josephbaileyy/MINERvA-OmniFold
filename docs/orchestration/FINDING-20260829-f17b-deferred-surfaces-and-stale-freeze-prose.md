# FINDING 2026-08-29 — deferred F-17(b) surfaces, and three sentences the freeze's expiry stranded

**CITABLE FOR:** what the 2026-08-29 test-hardening pass deliberately did NOT change, and why.
**NOT CITABLE FOR** any gate movement, authorization, or claim that `OI-162` is closed. Gate 2
remains **FAIL**, the F-17(b) grade remains **NOT FIT** on finding `N1`, and no scalar-5D covariance
is adopted.

## Why anything is deferred at all

`measure_k0_farend_f1b_f17b.sh` is pin-bound. Its content sha256 was superseded once already at
`46691bbc` (`DECISION-20260828…` §"Dated pin supersessions"), and it is a `MANIFEST.tsv` row, so
F-14 / §7.0.7 coupling applies and `OI-123` forbids silent repointing. **Every further edit costs a
new dated supersession and another independent full-chain grade.** The corrected `OI-162` prefers
folding the real fix into the new forward-only rehearsal's fresh deployment rather than re-editing
this file now. So the items below are **recorded, not edited** — the same discipline §13.1 of
`DECISION-20260825…` applied to `test_compare_m1_m6.py`, and for the same reason: recording moves
no digest.

**They are MANDATORY ON NEXT TOUCH** — the next commit that moves this script for a behavioural
reason must carry them.

## 1. Deferred: `N1`, the defect the grade actually failed on

`:46` hardcodes `CODE_ROOT=/pscratch/sd/j/josephrb/k0r2/clean` with no environment override, `:128`
takes `MEASURER` from it, and the loop at `:169-171` runs that one measurer for **both** trees. The
frozen blob predates the repair and emits neither required key, so the comparator refuses with
exit 4, outside the `0|10|20` gate at `:213`. **Not fixed here by design:** an `MNV_MEASURER`
override would put a bypass on the code root, which is the one input whose identity this measurement
exists to establish. Deploying at a sha that carries the repaired measurer dissolves it with no
bypass and no edit. See the corrected `OI-162`.

## 2. Deferred: `N7`, an empty-vs-empty digest comparison

`:221,224` take `sha256sum … 2>/dev/null | awk '{print $1}'`. If `sha256sum` were unavailable both
sides are empty, `empty != empty` is false, and the bracket passes silently while the log prints
`pre=   post=`. It applies equally to the three pre-existing brackets at `:167,181,192,197,198`. Not
independently sufficient — `sha256sum` is coreutils-standard on the target and used at `:66,68`, and
the deletion direction is caught by the `prc` arm — but a bracket that cannot distinguish *no
movement* from *no measurement* should say so.

## 3. Three sentences the 2026-08-25 expiry stranded

None is a defect in behaviour. All three read as live conditions that are not live, which is the
failure mode `OI-160`/`OI-161` were filed for and which this same week produced a mis-diagnosed
deadlock.

| where | what it still says | why it is stranded |
|---|---|---|
| `measure_k0_farend_f1b_f17b.sh:71` | prints `ON BRANCH -- would violate the 7.0.19 freeze` | §7.0.19 expired 2026-08-25 when F-1(b) was taken and passed. The *check* is still worth keeping — the deployment's position still matters — but the reason it prints is no longer that freeze. |
| `measure_k0_farend_f1b_f17b.sh:126-127` | asserts the deploy and canonical copies of the measurer are byte-identical, closing *"'identical today' is a measurement and not a property"* | `46691bbc` made that false. The commit edited `:171-183` and `:218-234` of this same file and left `:125-128` untouched, so **the sentence warning the identity could lapse survived the commit that lapsed it.** This is `N1` seen from the other side. |
| `SPEC-20260825-f17b-tree-comparison-instrument.md:173` | *"The deployment is frozen at `aa67c426` until F-1(b) is filed (§7.0.19). Do not touch the frozen tree."* | F-1(b) was filed the same day the SPEC was written. The surrounding paragraph's substantive point — that A-2(f) is scoped to `--repo`, so work on `main` cannot perturb F-1(b) — is unaffected and still correct. |

## What WAS fixed on 2026-08-29, and verified by mutation

Seven mutations the 2026-08-28 grade measured as surviving with 100 tests green now each fail at
least one arm. Both instruments were restored to their pinned hashes after every mutation and
re-verified: `measure_m1_m6.py` = `ce52ff77…`, `compare_m1_m6.py` = `28490539…`,
`measure_k0_farend_f1b_f17b.sh` = `ad1a8b64…` — **no pinned digest moved.**

| gap | mutation that used to survive | now killed by |
|---|---|---|
| `N2` | the preserver-drift branch downgraded from `exit 13` to a warning | `test_the_preserver_drift_branch_REFUSES_rather_than_merely_warning` |
| `N3` | `completed_utc = started_utc`, collapsing the interval | `test_the_interval_is_TWO_clock_reads_and_not_ONE_STAMP_EMITTED_TWICE`, which drives the clock rather than racing it |
| `N4` | schema and instrument version reverted `2 → 1` | `test_the_MANDATED_schema_and_instrument_version_are_TWO_not_ONE` |
| `N5` M4 | the `branch/detached/not-a-git-checkout` state enum neutered | `test_every_SUB_GUARD_on_the_producer_identity_has_a_firing_arm` |
| `N5` M10 | the exactly-`{state,name}` shape guard neutered | same arm, three sub-cases |
| `N5` M11 | the "a branch must carry a non-empty string name" half dropped | same arm, two sub-cases |
| `N5` M13 | `not-a-git-checkout` never produced by any test | `test_a_NON_CHECKOUT_is_reported_as_such_and_carries_no_name` |

`N6`'s stale pin in `m1m6_expected_differences.json` — a **live instrument input**, unlike the
historical `5dc92487` references in the grades and CATALOG, which correctly identify the bytes they
graded — is superseded in place by a dated row: old `5dc92487`, new `28490539`, with the reason and
an explicit statement that the transcription below it is unchanged and still accurate.

**This does not make the chain FIT.** `N1` is untouched and remains independently sufficient.
