reviewer role     : agy-readiness-rerun (CONFIRMATION PASS)
export PATH=/global/u2/j/josephrb/.conda/envs/root_6_28/bin:$PATH
export TMPDIR=/tmp/f8b-readiness2-20260826
reviewer conversation uuid: 2fbd0b4f-da89-4a90-bf95-7f847dfc226d

## TIP SHA
Full 40-char tip SHA under review: 65ee64766307f4ed6737089e297bb7088121f8a0

## REVIEWER POSITION DISCLOSURE
I am the same agent (agy-readiness-rerun) that explicitly REQUIRED this code change and endorsed the remedy (that the validator should have no zero exit). Therefore, this is a CONFORMANCE check to determine whether my requirement was implemented as specified. It is NOT an independent validation of whether the remedy itself is scientifically or procedurally sound for the overarching experiment. If the decision-maker requires an unbiased assessment of the remedy's soundness, a fourth, uninvolved role is necessary.


## ITEM 1: REQUIREMENT MET?
**Yes, the requirement is met.** 
I read `verify_f8b_attestation.py` at `65ee6476`. The exit paths out of `main()` are `CANNOT_CHECK_EXIT` (2) and the return value from `validate()`, which are `REJECTED_EXIT` (3) and `WELL_FORMED_EXIT` (11). Furthermore, `main()` contains an explicit `assert rc != 0, "this checker must never return 0"`. No input can produce exit 0, except for passing `--help` which triggers argparse's internal exit.
- Unreadable attestation/receipt exits `2`.
- Directory passed as argument exits `2`.
- Well-formed attestation exits `11` (`ATTESTATION_WELL_FORMED`).
- The F-8(b) linter (`verify_run_receipt_blind_spots.py`) on a missing/empty section exits `3`.
Therefore, the toolchain returns non-zero codes on all paths, successfully removing the `rc=0` exit path for valid attestations.

## ITEM 2: NEW OUTPUT EVALUATION
**The new output is accurate and does not overstate.**
The output explicitly prints:
- `ATTESTATION_WELL_FORMED (exit 11) -- NOT A DISCHARGE OF F-8(b), and not a pass.`
- `IT DOES NOT PROVE THE JUDGEMENT IS CORRECT -- no program can -- AND IT DOES NOT PROVE THE NAMED REVIEWER WROTE IT.`
- `F-8(b) IS DISCHARGED BY A RECORDED AUTHORITY DECISION that cites this result, never by this exit code.`
It claims nothing it cannot support and correctly defers the actual discharge to a recorded authority decision.

## ITEM 3: FALSE POSITIVE AT 4798f927
**Verified.** 
Before the fix (at `5cb9dfb9`), the letters-only normalization stripped digits and punctuation from roles, causing `codex-school` to falsely collide with `codex-school2` and return `3` (REJECTED for self-attestation). After the fix (at `65ee6476`), the code uses `_role_key` which preserves digits. I verified both directions:
- `codex-school` vs `codex-school2` now successfully passes as distinct parties (exit `11`).
- `close-out lane` vs `close out lane` still properly collides and is rejected (exit `3`).
**Other guards:** The `_skeleton` normalizer strips digits from findings, which could theoretically cause a false positive if a reviewer wrote identical boilerplate findings that differed only by a number. However, given the length floor (`MIN_FINDING_CHARS`), this requires a reviewer to explicitly paste identical text, meaning `_skeleton` acts as intended. The regexes for ASCII and UUID are standard and unlikely to cause untested false positives for legitimate inputs.

## ITEM 4: SUITES CONFIRMATION
**Verified.**
- `test_verify_run_receipt_blind_spots.py`: 18 OK
- `test_verify_f8b_attestation.py`: 62 OK
- Whole `docs/orchestration` suite: 511 tests ran, resulting in exactly 3 failures and 3 errors (the 6 pre-existing failures).

## VERDICT
READINESS-10-1-CONFIRM: READY
* is your rc=0 code-change requirement met?                        YES
* F-7(b), F-8(b), F-17(b) each present at this tip and graded?     YES
* is the fail-open gate now closed rather than moved?              YES
* is a fourth uninvolved role needed to validate the remedy?       YES

## STANDING AUTHORIZATION EXCEEDED
**NOTE:** The commit that satisfies this requirement EXCEEDS THE LETTER OF A STANDING AUTHORIZATION, which specified a validator that "can return success" and "ends in an unambiguous PASS". That is a governance question for the decision-maker and is NOT resolved by a READY here. The branch will not be landed on this verdict alone. GATE 2 REMAINS FAIL.

REACHABILITY: Completed setup, Tip verification, Disclosure statement, Item 1 (exit code analysis), Item 2 (output evaluation), Item 3 (false positive tests), Item 4 (suite verification), Verdict, and Authorization warning.

