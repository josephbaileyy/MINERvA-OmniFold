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

---

# Round 2, part 2 — STRESS, coverage decision and conclusion

Same lane and approval, detached worktree at `f6f8764d`, unchanged afterwards. **No BLOCK: the reviewer
independently recomputed all 360 stress recoveries against both targets, every moves-away flag and the table, and
they match; the decision not to run coverage at K* stands.**

| # | severity | finding (restated) | verified? | disposition |
|---|---|---|---|---|
| 5 | MAJOR | §12 "no PET configuration tested is both adequate and robust" is too broad: C at k = 3 is adequate by the mean rule and has no moves-away in any stress cell. | yes (C@3 0.570, `adequate: true`; 12/12 cells positive, minimum +0.014) | **Fixed** in §11.3, §11.4, §12, `CONFIRM_RESULTS.md`, the deck, RUN_LOG and STATUS: "no frozen candidate **at K* = 10**"; C@3 is reported with its lower bound below the floor, two replicates per case, and as a **prospective** candidate needing a new predeclared amendment — coverage is not run for it retroactively. |
| 6 | MAJOR | "All six cases identifiable" is unsupported for R1 × 1.05 + D1 +0.35: E1 measured only a standalone R1 that also recomputes reco q3. | yes (`identifiability.json` has `R1_x1.05`, "reco q3 recomputed"; no combined entry) | **Fixed**: the five truth cases are identifiable (same definitions, 600,111 events); the combined case is "identifiability unmeasured". The deck now computes identifiability from E1 instead of assuming it. The coverage decision rests on D4c/D4d, which are measured. |
| 7 | MAJOR | C's PET failure is attributed to acceptance extrapolation, but the D4 weights are functions of the stored truth PDG codes that PET's truth cloud receives, so the scalar explanation does not transfer. | yes (`distortions.py` D4 = f^N over truth PDGs; `fullevent_fps_dataloader.py` keeps the PDG column) | **Fixed**: mechanism "not established" on the PET path for C and B; acceptance extrapolation stated as a hypothesis; "hidden from E_avail, not from PET's inputs". |
| 8 | MAJOR | "The response error moves recovery up" (C 0.956 under R1 + D1) has no matching unscaled control on the same replicates. | yes (`stress.tsv` has D1 −0.35 and R1+D1 +0.35, no D1 +0.35 alone) | **Fixed**: reported as measured; the R1 effect is "not isolated" on the PET path. |
| 9 | MINOR | The STRESS slide does not state two replicates per case. | yes | **Fixed** on the slide and in the limitations bullet. |
| 10 | MINOR | D5 is shown without its "implemented variant" label in `CONFIRM_RESULTS.md` and on the slide. | yes | **Fixed** (amendment 4 label on both). |

**Checked and found correct (part 2):** 36 STRESS receipts match the manifest, frozen hashes, miss rules, pool and
distortion identities; all 360 iteration-file hashes match the score provenance; code `6b18e09d` with the relevant
files unchanged at HEAD; the strict audit covers all 36 STRESS rows CLEAN; D1, D2, D4c/D4d and the PET R1 follow
their declarations and D5 the documented implemented variant; targets use the distorted truth (R1 leaves it
unchanged); "moves away" is exactly `residual_l1 > injected_l1`; the part-1 fixes behave as described; all 684 deck
values recompute from their sources.

**Not verifiable by the reviewer:** cluster-side bytes and scheduler observations; "no STRESS run scored twice"
(the committed audit covers driver logs, not scorer logs — the count was taken on the cluster, 2026-09-25 12:44Z,
by listing `score-<job>.log` per STRESS run directory: none had more than one).
