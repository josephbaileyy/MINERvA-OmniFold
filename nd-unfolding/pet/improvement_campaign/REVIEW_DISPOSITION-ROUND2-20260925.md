# Independent review round 2 — dispositions (FINAL)

**Reviewer:** one codex-school lane (a different model family from every implementer), read-only sandbox, detached
worktree at `8282a6eb`. **Dispatch approved by Joseph for round 2 on 2026-09-24** (asked in the orchestrating
session; the approval covers FINAL now and STRESS/coverage when they land). The worktree was unchanged afterwards.
**This file is the orchestrator's restatement and disposition; no reviewer wording is committed.** Each finding was
checked against the code or data before being accepted. Scope: the code changed since round 1 (`24f4f455`), FINAL
provenance, and the scientific scope of report §11, `confirm/CONFIRM_RESULTS.md` and the deck's FINAL slide. STRESS
is out of scope for this round.

| # | severity | finding (restated) | verified? | disposition |
|---|---|---|---|---|
| 1 | MAJOR | The analyzer's FINAL gate treats an absent audit, or an audit that does not cover every row, as clean; the default audit file covered 23 of the 36 rows; receipts are not checked by the gate. | yes (the gate only intersected rows with the audit's suspect set) | **Fixed** (`c61660f6`): the gate requires a named audit (`--audit`, no default) in which every manifest row is present with verdict CLEAN, and each row's committed receipt `complete` with the manifest's configuration hash; otherwise FINAL stays interim and the reasons are printed. Tests in both directions (`confirm/test_audit_and_gate.py`). The FINAL numbers were never affected: the explicitly named 23:20Z audit covered all 36 rows. |
| 2 | MAJOR | The lock audit's verdict ignores missing scheduler intervals, executing jobs without a segment, missing fits and a COMPLETE run that stops early; it cannot say "unverifiable". | yes (`suspect = overlaps or dup or seg_problems` only) | **Fixed** (`c61660f6`): verdict CLEAN / SUSPECT / UNVERIFIABLE; a COMPLETE run must carry exactly the expected `(iteration, step)` fits and a terminal segment; an unfinished run both steps of every completed iteration; a job without a scheduler interval or segment makes the run UNVERIFIABLE; driver intervals are recorded. **Re-audit** at 2026-09-25 00:19Z with the committed code (`confirm/results/audit_locks-20260925T0019Z.json`): PILOT 9, FINAL 36, STRESS 8 (in progress) — **all CLEAN**. |
| 3 | MAJOR | §11 attributes B's gain to the reco energy summaries alone, but B's frozen configuration also changes the truth-side PDG encoding; and "the only change that reaches the events that fail reconstruction" is wrong, since carry-misses also applies the step-2 classifier to every generated event. | yes (`b2e5-C2-H-s1.json` → `reco_summaries_pdg_onehot`; `omnifold.py:218-220`) | **Fixed** in §11: B − A is the combined effect of both input changes (the DEV arms, all on the one-hot truth side, are what isolate the reco summaries); C is described as training step 2 on the reconstructed events and extrapolating that ratio to the misses. The measured ordering and sizes are unchanged. |
| 4 | MINOR | Scoring of completed runs happens outside the run lock; two chains can score one run at once through the scorer's fixed temporary file. | yes — **and it happened**: `final-B-F11` and `final-CTL-F11` were each scored by jobs 58838064 and 58839336 within seconds of each other | **Fixed** for new submissions (`c61660f6`: `flock` per run around scoring, completion rechecked inside). The running STRESS chains use the pinned `6b18e09d` checkout and are not redeployed mid-stage; instead every run scored more than once is re-scored in isolation (`confirm/jobs/sbatch_rescore.sh`) and compared with its committed `scores.json`. FINAL: see "Rescore" below. STRESS: the same check runs when STRESS is harvested. |

## Rescore of the two concurrently scored FINAL runs

CPU job 58843833 (script `confirm/jobs/sbatch_rescore.sh` from `c61660f6`, scorer from the `6b18e09d` checkout that
produced the originals, same population target) re-scored both runs into a separate directory and compared every
field except wall time: **`final-B-F11` IDENTICAL, `final-CTL-F11` IDENTICAL**
(`confirm/results/rescore-final-20260925/rescore.txt`). No other PILOT or FINAL run was scored by more than one job
(count of `score-<job>.log` per run directory, 2026-09-25). The FINAL result stands as committed.

## Checked and found correct by the reviewer (not re-litigated here)

An independent recomputation of every FINAL paired mean, standard error, one-sided bound, t probability, fixed-family
Holm decision and adequacy decision matches `confirm_results.json`; the historical floors and margins are unchanged;
the corrected sizing reproduces 306/432 (partial pilot) and 259/298 (complete pilot), n = 12 either way; all 36
receipts match the manifest, frozen sha256s, miss rules, seed policy, pool-F selection, row digests and iteration
hashes, and their code commits exist with the relevant training/resume/scoring code unchanged across them; the 23:20Z
audit covers exactly the 36 FINAL rows and excludes the quarantined `final-C-F1`, whose replacement starts at
iteration 0; the sizing commit `e61ba86c` (01:32:57Z) precedes the first FINAL submission (01:33:24Z); the flock is
held for the job lifetime; resume restarts at `completed_iteration + 1` with contiguous histories; `iter02` is k = 3
and `iter09` is k = 10; the positive control's resumed pulls/pushes are identical; the FINAL slide's 73 registered
numbers match the committed sources; PILOT stays separate; the scoped "recoverable within this closure" is supported.

## Not verifiable by the reviewer

Cluster-side checkpoint bytes, original scheduler intervals, cross-node Lustre locking and first physical pool reads
(no cluster access in its sandbox); GPU bit-exact resume beyond the committed positive control (no TensorFlow). The
re-audit above ran on the cluster with scheduler intervals.
