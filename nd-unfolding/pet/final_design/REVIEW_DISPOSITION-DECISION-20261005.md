# Review disposition — independent review of the terminal decision (cycle 1 of at most 2)

**Review:** under `REVIEW_BRIEF-DECISION-20261001.md`, by a fresh read-only Codex session (model `gpt-6-astra`,
reasoning effort high; session `01a10c41-5115-7541-999b-e2bbb0da8693`) in a detached, clean worktree at
`f27d92d0da7cd3985780af3f6e2627f0c71929ad`; it wrote nothing and contacted no cluster. The reviewer's output is
restated here by the owner (the orchestrator); quotations are exact where marked.

**Verdict of the review:** *"`NO_ELIGIBLE_DESIGN` reproduces numerically, but provenance-gate, scope, and reporting
defects require disposition."* Checks (a) PASS, (b) PASS, (c) FAIL, (d) FAIL, (e) FAIL, (f) PASS, (g) PASS for the
committed chronology, (h) PASS, (i) FAIL on provenance enforcement. The reviewer independently recomputed B2 for both
finalists, C1 (pooled 68 % 753/840 = 0.896429, 95 % 832/840 = 0.990476) and C4 (width/limit 0.828, 1.569, 1.716,
1.704, 1.323, 1.450, 1.535) and re-evaluated the look-1, provisional and terminal decisions with the committed functions:
**no numerical discrepancy**.

## Findings and dispositions

| # | finding (operand at `f27d92d0`) | impact (reviewer) | disposition | evidence of the repair |
|---|---|---|---|---|
| 1 | `analysis/build_evidence.py:95` set `"provenance_complete": True` unconditionally; `decide.py` checked only `receipt.complete`, so `P(section 10)` could PASS with the receipt, configuration and row bindings removed (reproduced in memory) | defective gate; no corruption of the committed scores (all 1,664 receipt digests match their completeness records) | **Repaired.** `decide.binding_problems` checks every scored run: receipt complete, receipt config hash = run-identity config hash, code commit present, both row digests, receipt and replicate-array digests recorded. `build_evidence.provenance` adds, for every final-bank run, equality of the score's receipt digest with its committed completeness record (a run in no record fails closed); `coverage_spec.py` applies the same to every coverage member. `run_look1.sh` / `run_final.sh` pass `freeze/COMPLETENESS-*.tsv` | `analysis/test_pfd_provenance_gate.py` (the reviewer's counterexample is now INCOMPLETE; wrong digest and missing record refused; the committed evidence binds); with the binding check disabled the counterexample control fails. All 1,680 scored files bind (16 seed, 944 look-1, 720 coverage). Regenerated `decision_look1.json`, `decision_look1_provisional.json` and `coverage_dev/decision_final.json` are **identical in every verdict and number** to the committed ones; `P(section 10)` now PASSes on verified bindings for all four designs |
| 2 | `analysis/coverage.py:258–266` computed `vs_population` for the aggregate only; `regions.*.vs_population` absent | missing report-only evidence; no verdict change | **Repaired** from the committed member histograms (no new compute): `coverage.py` writes `vs_population` per region (and for D4c when present). Regenerated `coverage_dev/coverage_H2S1T24K5.json`; rules identical | regions, own / population target, 68 % and 95 %: low acceptance 0.257 / 0.250 and 0.789 / 0.787; moderate 0.701 / 0.706 and 0.964 / 0.964; good 0.929 / 0.929 and 0.998 / 0.999 (the reviewer's independent values) |
| 3 | Decision record and report: "the other 17 library cases have no population comparison" (also the brief's check (c)) | incorrect count and scope statement | **Corrected:** 19 of the 21 final-library cases lack a population comparison (all but D4c up and D3 +0.35; the library's own D1 +0.35 is a different distortion from FINAL's historical tilt). **Erratum to the brief:** check (c)'s "17" is wrong; the brief itself is left as fixed and this row records the correction | decision record (population row), report §6 |
| 4 | Report §7 and deck: "over-conservative, not anti-conservative" unqualified, while the low-acceptance region under-covers (68 % 0.257, 95 % 0.789) | scope/interpretation; no additional frozen-rule failure (C3 gates only moderate and good) | **Corrected:** the aggregate E_avail intervals over-cover and fail C1/C4; the good region over-covers, the moderate region is near nominal at 68 %, and the low-acceptance region under-covers (ungated). "Mechanism not established" kept | decision record (coverage and terminal rows), report §7–8, deck coverage and terminal slides, RUN_LOG, STATUS, handoff, PR #4 body |
| 5 | Report §6 and deck: "D4c n down"; deck placed C1's FAIL on the 95 % row | labels; numbers reproduce | **Corrected:** "D4d n down" (report, deck, RUN_LOG, handoff); the deck now marks the 95 % ceiling comparison "unresolved", the 68 % ceiling "decisive", and C1 FAIL on a combined row | deck slide 13; `CLAIM_INDEX-deck.md` |
| 6 | Decision record: the `PROVISIONAL_SELECTED H2S1T24 K5` sentence carried no scope (check (d)) | scope statement only | **Corrected:** stated as an ordering label for the coverage stage, not a selection, with the estimator, bank-conditioning, signal-only, fixed-response and diagnostic/no-adoption scope attached | decision record (provisional row) |
| 7 | Independent numerical reproduction | none | **Accepted**: the numerical verdicts stand | — |

**Could not verify (reviewer), recorded as limits:** cluster-side submit/start times of the scoring jobs and the absence
of uncommitted earlier scoring; original receipt bytes, training guard inventories, raw arrays and bit-exact resumes;
end-to-end regeneration of scores and population targets from the cluster inputs; the scheduler inputs behind the cost
receipt (its arithmetic reproduces: medians 1.767919 / 1.517087 A100-h); PR #4's body at the reviewed commit.

## Outcome of cycle 1

No verdict changed; the terminal outcome **NO_ELIGIBLE_DESIGN** stands. One defective gate was repaired and re-verified
on the committed evidence; five reporting/scope statements were corrected. Per the brief, a repair that changes no
verdict is dispositioned without restarting the review; because finding 1 touched check (i)'s gate, a narrow cycle-2
check of findings 1–6 on the repaired commit is requested (the brief's budget: at most two cycles).
