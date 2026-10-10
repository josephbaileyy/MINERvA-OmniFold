# Review round 2 — focused re-review of the single repair batch, fixed commit `31517ad7`

Recorded by the lane owner. This is the same fresh reviewer's one permitted focused re-review, of
`df0923aa..31517ad726c671195e752ce9239c14e981c17dd2` in a clean detached worktree. The worktree was
checked clean (`status --porcelain --ignored` empty) afterwards. The reviewer's final message is
reproduced with its formatting condensed; statuses, numbers and verdicts are unchanged. The review
budget is now exhausted. The owner's post-review edits are listed in `REPORT.md` §11 and are
**unreviewed**.

---

**Checked:** the diff touches only `gbdt/`; in `results.json` only `diagnostic_cost` changed.
`test_comparator.py`: 10 passed. Re-derived with the reviewer's own code: the `diagnostic_cost`
arithmetic from `synthetic_timing.json` (0.0534 + 2.004 + 0.664 + 0.1 = 2.822, admitted 4.78–8.30;
matches); |r|/|s| 0.753–0.980 and reverse slopes 1.11–1.27 (J); |bias|/SD medians 11.7–23.5; pool
ratios 237×/83×/14×/25×; λ_5D 1031.0→174.4. `branch_outcome` and `missed_concentration` were probed
with the reviewer's own fixtures. `synthetic_timing.py` was not run.

| # | status | reason |
|---|---|---|
| 1 | RESOLVED | branch population GiBUU/W1/W3/q3 plus W2 at K = 5 via its ensemble mean; P1r–P3r σ_c/r_IBU only; missing-comparator rule added |
| 2 | RESOLVED | branch B coded and tested; r_IBU(∞) enters a rule; `missed_concentration` coded with a frozen 2/3 threshold and tested both ways; E4 GiBUU/W1 in rank-1 "against". The branches are disjoint, so nothing double-counts. A C = A = 50% tie resolves to C by code order (undocumented) |
| 3 | RESOLVED | primary same-sample against asimov_same; split-half never labels; confounds declared; 1e-8 control restricted to same-sample |
| 4 | RESOLVED | branch C scoped to binned estimators at this reco binning and T2, in §4 and §6 |
| 5 | RESOLVED | the q3 claim rests on λ_5D; J/H2 −14%/−3% quoted; I1's motivation restated |
| 6 | RESOLVED | "about 14–240×"; ratios match |
| 7 | PARTIAL | the price is derived and agrees with `results.json`, but: (a) the computations header ("for each weight set × grid × sample role × response weighting … Fisher at T1 and T2") literally implies 36 T2 Fishers while the price counts 18, and the code labels the 18 as roles × weight sets when the labelling Fishers are same-sample × 2 weightings; (b) the T1 departure-weighted convergence runs for the exactness control are unpriced (≈ 0.2 core-h); (c) read literally, admitted would be 5.85–10.46. Repair: say Fisher is same-sample only for both weightings, and add the T1 exactness runs |
| 8 | RESOLVED | exactness at T1 within 0.01 σ_c; T2 non-convergence flagged and excluded from B. Small gap: the cap rule declares a branch once stages 1–3 are done, but B needs stage 4; if the cap hits during stage 4, B-eligible functionals fall silently into "mixed". Repair: report B as undeclarable in that case |
| 9 | RESOLVED | "overstates"; numbers match |
| 10 | RESOLVED | 11.7–23.5 quoted in §5 and §13 |
| 11 | RESOLVED | "only partly reduce" (GiBUU/W1), "not at all" (W3/q3); matches 27.5→29.4% and 11.4→11.4% |
| 12 | RESOLVED | partial-trace pairing labelled as routed |
| 13 | RESOLVED | branch and resolution-sensitivity rules coded and tested; tautological tests labelled. Minor: the 2/3 concentration rule has no null calibration; the reviewer's heavy-tailed unrelated fixtures give ≈ 5–7% false positives at n = 27–109, tolerable because it is reported beside the branch, not as one |
| 14 | RESOLVED | second paper example added; "answer exactly" softened |

**New MATERIAL — N1.** §6 "Interpretation: Branch B" and §14 route branch B to "the noise-free
convergence study already costed in the s5e next design (item 3, ≈ 4–6 node-hours)". That study was
already executed as s5p study K (`RECORD-20260927-s5p-stage2-exit.md`: nominal/W3 complete to
K = 200, GiBUU/W1/q3 partial, capacity to K = 10), and s5p is terminal. Branch B therefore presents an
executed terminal study as the new experiment, which conflicts with "completed s5p remains terminal".
D-ID's IBU to K = 200, matched-K against the existing traces, already answers the B question for W3
(whose GBDT residual worsens to K = 200) and up to K = 40/30/40 for GiBUU/q3/W1. The 4–6 node-hour
figure is an old forecast, while a measured timing exists: 31,954 s per 200-iteration trace × 5 truths
/ 8 per node × 1.25 / 0.8 ≈ 8.7 node-hours admitted. Repair: branch B is first read from D-ID's
matched-K comparison against the existing s5p study-K traces; extending the partial traces is a re-run
of terminal s5p study K that needs its own authorization; price it from the measured timing and label
the 4–6 figure as an old forecast.

**Verdicts:** D1 ACCEPT-WITH-REPAIRS (N1 is a text-level repair to §6 branch B and §14; #7 and #8
partials are minor clarifications; the design is otherwise complete and each branch is reachable as
coded). D2 ACCEPT. D3 ACCEPT.

**Resources:** ≈ 0.15 CPU core-minutes this round (≈ 1.5 over both rounds), ≤ 1 thread; the prescribed
pytest created a gitignored `gbdt/__pycache__/`, which the reviewer removed; the worktree was clean.
