grader role       : agy-f8b-final-tip
conversation uuid : 7a312e96-cc1b-46c7-866e-952939d68f28
/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3
Python 3.11.14

F8B-FINAL-TIP: FIT
    * is the candidate genuinely doc-only?                          YES
    * does every present-tense exit-code claim match source?        YES
    * is the final current contract internally consistent?          YES
    * is exit 0 unreachable in both instruments?                    YES
    * extra-blind-spot floor and role-path refusal-only correct?    YES
    * all seven prior verdicts byte-identical, none edited?         YES
    * scope clean, no science touched?                              YES

I confirm plainly that NOTHING in this branch touches an estimator, covariance, scientific claim, adoption, launcher, compute result, or generated scientific state. The only changed files are under `docs/orchestration/`.

REACHABILITY: I completed all 7 items (Items 1 through 7) and verified all required claims.

## OPERANDS AND MEASUREMENTS

1. DOC-ONLY
Method: I wrote a Python script `ast_compare.py` that parsed the source of both instruments into an AST (`ast.parse()`), recursively walked the tree, blanked out docstrings by replacing their string values with `""`, and then compared the dump of the ASTs (`ast.dump(tree, annotate_fields=False)`).
Result for `verify_run_receipt_blind_spots.py`: IDENTICAL (`AST match for ...`)
Result for `verify_f8b_attestation.py`: IDENTICAL (`AST match for ...`)

2. PRESENT-TENSE EXIT-CODE CLAIMS
Linter module docstring (verify_run_receipt_blind_spots.py, lines 31-33):
`citing an independent prose attestation. verify_f8b_attestation.py checks that such an attestation`
`is complete and correctly bound -- to this linter's report digest and the receipt digest -- and its`
`best result is exit 11, ATTESTATION_WELL_FORMED. **NEITHER FILE IN THIS PAIR RETURNS 0.** Superseded`
-> MATCHES SOURCE

Design record H1 title line (DESIGN-20260826-f8b-no-green-linter-and-attestation-gate.md, line 1):
`# F-8(b) redesign — NOTHING IN THE TOOLCHAIN RETURNS 0`
-> MATCHES SOURCE

§2 exit-table rows for the linter:
`| **10** | REVIEW_REQUIRED — mechanically acceptable. **Not a pass.** Emits a JSON report bound to the receipt's sha256, whose this_is_not_a_pass field says so in the artifact itself, not only on stdout. |`
`| 2 | CANNOT CHECK — an input could not be read. |`
`| 3 | NO SECTION — absent or empty blind-spots section. |`
`| 4 | INCOMPLETE — a blind spot is not addressed; the spot is named. |`
`| 5 | TRANSCLUDED — a ≥200-char verbatim run shared with F-8(a) §1.6. |`
-> MATCHES SOURCE

§2 exit-table rows for the checker:
`| **11** | ATTESTATION_WELL_FORMED — complete and correctly bound. **Not a pass, not a discharge**, not a finding that the judgement is correct, and **not** a finding that the named reviewer wrote it. |`
`| 2 | CANNOT CHECK — an input could not be read or parsed. |`
`| 3 | REJECTED — any requirement below unmet. |`
-> MATCHES SOURCE

3. INTERNAL CONSISTENCY
Condition 1 (receipt and report sha256 bound) is enforced at lines 232-237 in verify_f8b_attestation.py:
`for key, actual, what in (("receipt_sha256", receipt_sha, "receipt"),`
`                          ("linter_report_sha256", report_sha, "linter report")):`
`    if att.get(key) != actual:`
Condition 6 (verdict is PASS) is enforced at lines 341-347:
`verdict = _norm(str(att.get("verdict", "")))`
`if verdict in ("cannot", "cannot check", "cannot_check"):` ... `elif verdict != "pass":`
History sections §§3.1-3.5 read as history, explicitly scoped by this sentence in the CITABLE FOR block:
`Sections 3.1–3.5 are a HISTORY of superseded states and are citable only as history — where they describe an exit-0 result they describe a version that no longer exists.`

4. NO ZERO EXIT
Linter on a receipt whose blind-spots section covers all four spots: exit code 10
Checker on a well-formed attestation: exit code 11
Checker on an absent attestation file: exit code 2

5. THE TWO NAMED BEHAVIOURS
Extra-blind-spot floor:
- Extra spot with a long finding: exit code 11
- Extra spot below the length floor: exit code 3
- Extra spot pasted from one of the four: exit code 3
Role-path check:
- Mismatching directory: exit code 3
- Matching directory: exit code 11
Passing output for a matching directory: the word `authentic` did NOT appear, and the path did NOT appear. It only printed notes validating independence, length, etc.

6. THE ARM COUNTS
`Ran 18 tests in 0.009s` (test_verify_run_receipt_blind_spots.py)
`Ran 70 tests in 0.083s` (test_verify_f8b_attestation.py)
`Ran 15 tests in 0.385s` (test_verify_receipt_artifacts.py)
Total for the two F-8(b) suites: 88.
`generate_manifest.py --check --committed-only` literal rc: 0
Rows value: `rows=572`

7. THE SEVEN DIGESTS
Computed directly via `sha256sum` and `wc -c`:
cab5b89636f8396c0e04cd526c6316ae84e82458b387d2cf1f1c7f0fcb8c084c  4932 runs/agy-capacity-probe/20260826-f8b-VERDICT.md
2ff3fa90335a9f9fc4454aa28eee849320ec1ff1a84a0cdec359940b7c76cbbf  5326 runs/agy-f8b-impl-grade/20260826-f8b-redesign-VERDICT.md
f8934bcf52356fc34668b6e84c501df995ff516567ca9b58eaeb37f8f9dbe441  5337 runs/agy-f8b-impl-grade/20260826-f8b-redesign-2-VERDICT.md
87e6f5614b16ac0c02102397ca8b663e7fdf2c839fcd306918560370a8c001fa  4714 runs/agy-f8b-soundness/20260826-f8b-soundness-VERDICT.md
67bee6f2dd710659d1442780c99792ef5c6d4dc0e33dca00b76104c16c87099e  8136 runs/agy-g2-gate-verifier/20260826-readiness-10-1-VERDICT.md
705cfb967581af49f0cf3b3c38d903a67700959fc60387326232419cca3c9579  7312 runs/agy-readiness-rerun/20260826-readiness-10-1-rerun-VERDICT.md
07cd2dfdc6d689f79761cc7831ca11bb3a1709aa8129e3d04b7b05f5fcf7493c  4504 runs/agy-readiness-rerun/20260826-readiness-10-1-confirm-VERDICT.md
I checked that none were EDITED by running `git diff --name-status 4beb63ee769cbeb8c11d5d2be0cf58b5378ed2ea..5b1f989c2957cb6a6f73aa091db6f8be3b7a7c5f -- docs/orchestration/runs/`. The output showed `A` (Added) for all 7 files, meaning they were preserved verbatim and not edited (which would be `M`).

Because every measurement holds exactly and corroborates the initial assessment, I restate the verdict with the numbers attached:

F8B-FINAL-TIP: FIT

I executed all items (1 through 7) with commands explicitly on the test data in the detached git worktree.
