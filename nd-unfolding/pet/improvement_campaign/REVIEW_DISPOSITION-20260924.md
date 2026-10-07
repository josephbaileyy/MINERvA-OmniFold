# Independent review round 1 — dispositions

**Reviewer:** one codex-school lane (a different model family from every implementer), read-only sandbox, detached
worktree at `24f4f455`; dispatch approved by Joseph for this purpose on 2026-09-23. The worktree was unchanged
afterwards. **This file is the orchestrator's restatement and disposition; no reviewer wording is committed.** Each
finding was checked against the code or data before being accepted.

| # | severity | finding (restated) | verified? | disposition |
|---|---|---|---|---|
| 1 | BLOCK | The confirmatory launcher's run lock (`confirm/jobs/confirm_lib.sh` `claim()`) is not atomic: a competing copy can see the lock directory before its owner record exists, treat it as stale and take it too, so a debug chain and its shared-queue race copy could both write one run. | yes (by reading the function; the reviewer reproduced it in a temp dir) | **In progress (V1):** atomic ownership held for the job's lifetime, redeployed to live chains; every PILOT/FINAL/STRESS run audited for overlapping writers; suspect runs quarantined and rerun. Result recorded in `confirm/CONFIRM_RESULTS.md`. |
| 2 | MAJOR | The analyzer emits FINAL decisions from partial data and shrinks the Holm family when a candidate has too few pairs. | yes | **In progress (V1):** inferential output gated on the complete frozen manifest; Holm m fixed at the frozen family size (3); interim output descriptive only. |
| 3 | MAJOR | The committed Phase F ablation driver could not run (tuple-unpacking a single-return function), so the cited numbers lacked code provenance. | yes | **Fixed** (`b5e2dd40`), rerun from clean committed code (`4346af0d`): every cited value reproduces exactly. |
| 4 | MAJOR | D5 normalizes each generator histogram before forming the ratio and clips afterwards — not amendment 1's operation order. | yes | **Recorded** as protocol amendment 4 (erratum); all D5 numbers labelled "implemented variant" in the report. |
| 5 | MAJOR | "Real data is never read by any stage" is false for the DEV path: the historical loader loads and discards the inventory's measured arrays. | yes | **Recorded** in amendment 4; corrected statement: never used by any stage, not read at all on the confirmatory path (`SignalOnlyNpz`). |
| 6 | MAJOR | The pilot sizing labels the search cap (200) as the "uncapped" requirement; true requirements for C are ≈ 306 (k = 10) and ≈ 432 (k = 3). | yes (the function returns the cap when power is never reached) | **In progress (V1):** returns an explicit lower bound; sizing record's wording corrected in a new commit. FINAL's n = 12 (pool cap) is unchanged. |
| 7 | MAJOR | The report said no scalar estimator reaches the floor at k = 3; efficiency-corrected IBU does (0.880). | yes | **Fixed** in the report (`5c663a30`): restricted to carry-misses estimators, counterexample stated with its caveats. |
| 8 | MAJOR | "Not the bottleneck" overstates two capability measurements (the truth-only test supplies the exact tilt; marginal reco closure is not joint-ratio accuracy). | yes | **Fixed** (`5c663a30`): the measured capabilities are stated as such; attribution rests on the matched miss-rule intervention. |
| 9 | MAJOR | "At least 96 % definitional" is a causal claim the 1×/8× comparison cannot make. | yes | **Fixed** (`5c663a30`): "96.6 % of the gap remains at 8× the events"; no asymptotic decomposition claimed. |
| 10 | MAJOR | Phase D repetitions change both subset seed and estimator seed, and the full-size point has no subsampling, so its spread is seed-only. | yes | **Fixed** in the report and `phase_d/SCALAR_SCALING-20260922.md` (`a78630c7`): spreads labelled; the confirmatory Phase D should cross the two factors. |

**Checked and found correct by the reviewer (not re-litigated here):** the efficiency-corrected step 2 trains on
reco-passing events only and applies the ratio to all truth events; carry-misses delegates to the engine; no truth
quantity reaches step 1; the scorer is the historical seven-bin score with `iter02` = k = 3 and `iter09` = k = 10;
historical floors and margins imported unchanged; paired-t, SD bound and Holm arithmetic correct for complete input;
pool/draw exclusion and disjointness; frozen configurations and pilot receipts pass provenance checks; the sizing
record precedes the FINAL launch in history; 92 tests pass, 6 skip.

**Not verifiable by the reviewer** (no cluster access in its sandbox): cluster-side checkpoint integrity, the first
physical read of pool F, and bit-exact resume under TensorFlow. The lock audit (#1) addresses the first.

A second review round covers the FINAL and STRESS results once they land.
