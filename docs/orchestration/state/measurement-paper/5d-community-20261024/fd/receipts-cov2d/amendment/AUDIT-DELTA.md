# COV2D amendment, final delta audit (045364a8; code at 0d43c9a3), the director's ruling on it, and the director's F3

**Auditor:** the `coverage-5b-audit` session, 2026-11-04, read-only. Its two reports and its verdict on the F1/F2 fixes, received by SendMessage, are
copied verbatim below, with the director's ruling and the director's F3, also received by SendMessage and copied verbatim. The answers
and fixes are in `ANSWERS.md` (this directory), under "Final delta audit" and "The director's F3".

---

## The delta audit

COV2D amendment, final delta audit (045364a8; code at 0d43c9a3): parts 1–4's fixes hold, with one medium finding (F1) that blocks the route as written, and one lower one (F2).

How I checked:
- A fresh detached worktree.
- Locally: 102 tests OK, 23 skipped (no PyROOT here; your 112 is from your ROOT env).
- My former survivors re-run against the final code, only the survivors (your 51-mutant receipt covers the rest). The runs are slow: the CLI test alone is about 10 minutes per suite run.
  - **KILLED (3 of 3 so far):** "(i) background tree skipped", "(i) product without r_T" and "(i) AR23 on G18's draws", all by the rewritten CLI hand-histogram test.
  - **Re-anchored by your rewrite,** so my old text didn't match: "the outlier read at the wrong position" and "(i) unit F, not sqrt(F)". Your receipt kills both by name ("S3 outlier read at position 0", "R1 z over F not sqrt F").
  - **Still running:** the two coherent-offset mutants (on the identity; without x_true), the outlier max as median, missing R_c as 0, and the two MEC ones. Your receipt names the last four but has no coherent-offset mutant, so those two are the ones to watch. I'll send them when they finish.
- The harness restores each file after its mutant. I'll confirm 0 .pyc and a clean status when the run ends.

**F1 (medium; RUN): order() requires an "M" key that no record writer emits.**
- order() admits a record only if `r.get("verdict") == "PASS" and r.get("M") == M`.
- The real records don't carry M:
  - cov2d_pseudo_write.py builds pseudo_b.json from truth, host, root, stop, pins_checked, inputs, files, atime_moved, verdict and seconds (:214–259);
  - cov2d_pilot.py's readout record starts as {"stop": [], "invalid": []} and never sets M.
- Your order tests pass because the fixture hand-writes {"verdict": …, "M": M} (test_cov2d_jobs.py:262).
- Run: order("pilot", "pilot", {G18 record: {"verdict": "PASS", "files": [], "stop": []}}, set(), M) is blocked: "the G18 pseudo-data PASS record … is not on main for M". The same record with M added gives [].
- So, as written, the pilot and every later job are refused. It fails closed, but the quick workaround under deadline, hand-adding M to a committed record, would forge exactly the provenance the gate exists to check.
- What would close it:
  - each writer records the deploy's HEAD, which the job has already verified equals M, as "M";
  - a test that feeds order() the record each writer actually writes.

**F2 (low-medium; reading): a pilot that needs repricing still reads PASS.**
- The verdict is STOP, then INVALID, then PASS; reprice_classes never enters it.
- order() admits AR23's pseudo-data job and every unfold after a PASS, so a pilot with reprice_classes ≠ [] opens the bulk route automatically.
- §8 makes REPRICE an amendment ("decided after the pilot"). The director's merge of the record is the human gate, but the code doesn't help them.
- What would close it: order() also requires reprice_classes == [], or a "REPRICE" verdict that it refuses.

**Your five questions**

**1. The J1 order.** The sequence is right against §10 steps 5–6:
- G18's pseudo-data job first, then the pilot after G18's PASS;
- AR23's pseudo-data job and every unfold after the pilot's PASS;
- the universe jobs after both pseudo-data PASSes, and the rest after all 8 universe jobs are submitted.

The records come from origin/main via a fetch that leaves the deploy's tree at M. The gate now sees every cov2d-* job of the user and refuses an unknown name. Except F1 and F2.

**2. R2/R3.**
- **The texts:** the three are 1B's verbatim (fd_1b_mc.py:803–808), with flat indices for R<cc>.
- **The cells:** every cell flagged under C_T⁻ is listed, which is 1B's `hit`. When C_T covers, that equals "newly flagged", so the departure changes nothing. I agree with it.
- **The null:** C_T⁻'s null is built in null_at_T at NULL_SEED with C_model⁻ in the Gaussian, before any toy error, as 1B builds both (fd_1b_mc.py:740).

**3. The P3 arithmetic.** I recomputed it from the raw ledger.tsv and partb_jobs.tsv, independently of partb_wall_per_run:
- central/toy 762.5 s, universe 1,081.1, lateral 1,468.5 and replica 864.6, equal to the module.
- Your two looseness sources are right, and every trigger is below the bulk's per-run estimate.

**4. The J6 waves.** I recomputed them from the real tables:
- limits 179.95 node-h in total (pilot 01:41:00);
- steps 1–4 come to 78.88, and the rest to 101.07;
- the projected wall is 144.95.

The at-limit argument is right: at each submission, spent + held + new ≤ cap, and the sum can only fall afterwards. One caveat: "Slurm enforces the limit" holds only up to KillWait. A job that hits its limit is killed after the grace period, and is charged its elapsed time, slightly past the limit. Across 24 jobs that's tenths of a node-h at most, worth a margin or a sentence.

**5. The new refusals:**
- **300 toys:** a correct run has exactly the declared set.
- **The outlier cell:** 216 is in C2's committed cells205 (c2-clip2.json efficiency/cells205).
- **The seed order:** cells.npz `seeds` holds the CV nature plus the 300 toys, so a caller passing the toys' rows passes.

None refuses a correct run.

**Also verified:**
- **J2:** uni-stat runs before step A.
- **J3:** the per-run rc goes to walls.
- **J4:** the resets and mkdir happen before step A.
- **J5:** the tables are regenerated and compared at every submission.
- **J7:** the pseudo job checks its QOS and TimeLimit, and check closes its files.
- **P1:** P912_U is at 128 CPUs, the pilot limit is 01:41:00 as I priced it, and U_G18_Flux_0 at 64 is excluded from REPRICE.
- **P2:** every run has rc 0 plus a digest, and every class has a wall.
- **P4:** dvs-rate runs before check, with the cache note.
- **The flux check:** PASS. Both logs' PROBE lines hold a TH1D with 14 equal bins, and the log digests equal FLUX-CHECK.md's.
- **P5:** not run, as you said. It's still the one 0 node-h check I'd do before the pilot, because a mismatch there is a STOP.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---

## The auditor's follow-up (the survivor re-run)

Follow-up to my cov2d final audit: my survivor re-run is done. Every former survivor whose anchor still matches 0d43c9a3 is KILLED.

- **KILLED by test_runs_over_600_draws_and_matches_a_hand_first_order_histogram:**
  - (i) background tree skipped;
  - product without r_T;
  - AR23 on G18's draws;
  - product composition = first order.
- **KILLED by test_clipping_residual_on_varying_inputs_against_a_hand_computation:**
  - (ii) coherent offset on the identity;
  - coherent offset without x_true;
  - outlier max as median;
  - missing R_c as 0 in the medians.

  The two coherent-offset mutants, the ones I flagged, are therefore closed by a named test.
- **NOMATCH because the code was rewritten:**
  - "MEC newly ignores C_T's flags": removed by design (R2).
  - "unit F", "outlier at position", and "MEC null seed", now in null_at_T: your receipt kills each by name.
- Afterwards there were 0 .pyc and a clean status.

F1 and F2 stand as reported, and the director has upheld both. I'll check that delta when it's pushed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---

## The director's ruling

director, on coverage-5b-audit's cov2d final audit (045364a8): F1 and F2 are both upheld. Fix them in the amendment before binding 2.

**F1, the M key** (order() requires "M", and no writer emits it).
- cov2d_pseudo_write (pseudo_b.json) and cov2d_pilot (readout) each record M as the deploy HEAD. Read it from `git rev-parse HEAD` of the deployed checkout at write time. The writer refuses if that checkout is dirty.
- **The test must use a record produced by calling the real writer,** not a hand-written fixture. Assert three things:
  - order() admits that record;
  - it refuses the same record with M deleted;
  - it refuses the record with M set to a different sha.
- Change the existing hand-written-M fixture so it can't stand in for the writer test.
- **Never hand-edit M into a committed record,** not even under deadline. That would forge the provenance the gate checks. If a record without M ever exists, it is rewritten by the fixed writer, or the step is rerun.

**F2, REPRICE.** A pilot with any REPRICE class must not open the bulk. order() admits the bulk only on pilot PASS **and** zero REPRICE classes. REPRICE routes to an amendment, as §8 says. Add a mutant that drops the REPRICE condition, and make it required.

**Next:**
1. Push the fixes on the amendment branch, and send me the new head and the delta range.
2. coverage-5b-audit checks the delta, including its last 6 former survivors, the 2 coherent-offset mutants among them. Name a killing test for those two, or the audit reports them open.
3. Then binding 2.

The calendar holds: bulk submitted by 2026-12-01, $UNI exposed 2026-12-19. Thank you for the speed so far.

---

## The auditor's verdict on the F1/F2 delta (fd8d68bb; range ba10123c..1d566f0f)

Your F1/F2 delta (fd8d68bb) is checked: both are closed, and nothing blocks binding 2. My verdict has gone to the director.

- **What I verified:**
  - the real-writer tests (admit, refuse with M deleted, refuse with M wrong);
  - the dirty-deploy refusal before output;
  - the move-during-step-B STOP;
  - order()'s reprice_classes == [] check.
- **Four REQUIRED mutants re-run locally, all KILLED by assertion failures in named tests:**
  - F1 order ignores M;
  - both F2 mutants;
  - F1 dirty deploy admitted.
- The suite scoping keeps the writer-M mutants on their own suites.
- KillWait is a disclosure, not a blocker, and your §5 argument is right.

Your questions:
1. **Porcelain scope:** yes. deploy_head and cov2d_preflight both use plain `git status --porcelain`, which counts untracked files and excludes ignored ones. `*.pyc` and `__pycache__/` are gitignored, so stray bytecode won't trip it.
2. **Refusing a missing reprice_classes:** yes, that's the reading I'd want. It fails closed, and the real pilot writer always writes the key, so only a record not made by the writer could lack it.

Not re-run by me: the two writer-M mutants, which need PyROOT. I rely on your 60/60 receipt for those.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---

## The director's F3 (found while drafting binding 2)

director: I'm holding binding 2. I found a blocking defect in cov2d_submit.sh (blob 03ad296e) while drafting it. I'm merging #773 (your amendment branch) in the meantime, since code on main runs nothing.

**F3 (blocking): the binding check is a fixed point.**
- Lines 9–12 require the deploy checkout's HEAD to equal M, and then grep the deploy's own COV2D-BINDING-2.md for M.
- A commit cannot contain a file naming its own hash. If the deploy is at the code commit, binding 2 doesn't exist in it yet. If it's at the binding commit or later, the binding names an earlier commit, not HEAD.
- So every submission refuses, and no test reaches it: no test in 2d-unfolding/cov2d/tests mentions BINDING-2. It fails safe, but it would block the G18 job at the first connect.

**The fix: read the binding from origin/main, as order() reads records.**
- In the submit script, fetch origin, then `git -C "$C" show origin/main:<path to COV2D-BINDING-2.md>`, and require that it names M, the deploy's HEAD.
- The deploy stays at M, the code commit. The binding lives on main after it.
- Fail closed if the fetch fails or the file is absent on origin/main.
- **Tests on a real-shaped fixture** (a one-commit deploy plus an "origin" repo whose main carries a binding):
  - the fixed script admits when origin/main's binding names M;
  - it refuses when the binding names another sha, when it is absent, and when the fetch fails;
  - it refuses a dirty deploy or a HEAD ≠ M, as now;
  - the old blob 03ad296e refuses even the correct setup. Assert that, to show the test reaches the defect.
- **Mutants, REQUIRED:** one that reads the deploy's own copy, and one that skips the name check.
- **Amendment §5:** update the sentence "refuses unless COV2D-BINDING-2.md names the deploy's commit" to say where the binding is read from.

**Also check order()** for the same shape. It reads PASS records from origin/main naming M, which is fine, but confirm that it fetches before reading and refuses a failed fetch.

**Next:** push on a new branch from main after #773, then a delta to coverage-5b-audit (just this), then I bind 2 at the fix commit. The schedule has room: the bulk deadline is 12-01.
