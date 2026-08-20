# Publication close-out orchestrator prompt — authored 2026-08-20

**How to use this.** Start a fresh Claude school session in
`/pscratch/sd/j/josephrb/MINERvA-OmniFold` and say:

> Read `docs/orchestration/PROMPTS-20260820-publication-closeout-orchestrator.md` and execute it.

**Reasoning effort: run the orchestrator at `high`.** Its work is almost entirely judgment —
deciding whether a lane's "verified" is verification or a mechanical check, noticing when two
lanes agree because they read the same source, refusing to treat a generated view as evidence.
That is exactly where this campaign's expensive failures came from: the `5 of 5 CURRENT` parity
banner that was true and useless, the retracted *"deterministic same cause"*, the ~39 GPU-h
scheduling constraint built on a stale `ACTIVE` row. `max` mainly duplicates lane work; anything
at or below `medium` rubber-stamps lane reports, and in this repo a rubber-stamped report becomes
next month's true-when-written claim. Per-lane efforts are stated in each lane below.

**Why this file exists.** The state as of `38e876bf` is a large scope *reduction* that has not
propagated: Joseph's `OI-126` ruling took PET off the publication critical path, and most of what
`LIVE-STATE.md` still presents as blockers is no longer publication-blocking. A session that reads
the blocker list top-to-bottom will work the wrong queue.

---

## Standing authorizations — stated once, and none of them is a blanket

Carried forward from `PROMPTS-20260811-four-session-closeout.md` and **re-confirmed live on
2026-08-20** by `RECEIPT-20260820-oi50-hashverify.md`, which launched job `57287380` *"inside the
standing under-12 h approval; launched, not asked."*

- Any single Slurm job **under 12 h walltime is pre-approved.** Launch it; do not ask.
- **Commit and push are permitted, including to `main`.** Never force-push, never rewrite pushed
  history, never `git stash` bare — the stash stack is shared across worktrees.
- **THE STANDING GRANT IS ABOUT WALLTIME AND NOTHING ELSE.** It does not touch an explicit hold.
  Independently NOT authorized regardless of how short the job is: the 151 A100-h M(ii) family,
  `C_ML` construction, lifting the B1 steps 4-5 pause, and anything that moves a central
  estimator, an uncertainty model, or a published claim. If a job is short AND under an explicit
  hold, the hold wins and you ask.

---

## Orient first — do not skip, and do not trust memory

1. Read `AGENTS.md`. It routes every task. It is a **view**, never evidence or authorization.
2. Read `docs/orchestration/LIVE-STATE.md`, then verify it:
   `/usr/bin/python3.11 docs/orchestration/generate_live_state.py --check-freshness`
   **Regenerating fixes the sha and the timestamp and revalidates nothing.** The prose fields
   (`state`, `blockers`, `next_authorized_action`) are AUTHORED and carried forward verbatim, so
   they can assert false things while the file reads `FRESH`. Their source is
   `docs/orchestration/state/live-state.json` — edit **that**, never the generated `.md`.
3. Read `docs/CURRENT_WORK.md`, then the exact cited row in `docs/OPEN_ITEMS.md`. A generated
   view is never the authority for a number or a gate.
4. `git fetch github` — **the remote is `github`, not `origin`** — and check whether `HEAD` is
   behind. A pull aborts on other lanes' untracked files; there are ~717 of them. Never stash.

## What you are inheriting — verify each before acting on it

- **`OI-126` was RULED by Joseph on 2026-08-20 (`2e210468`).** The PET central/statistical pairing
  is DECLINED and PET is diagnostic/method-development. This removes Gate 5, Gate 6, `C_stat` and
  `C_ML` from the publication critical path. Reconsideration needs estimator-equivalence **plus
  coverage**, and coverage is a DIFFERENT OBJECT from verifying the construction — so
  `OI-121`-style blind-builder verification does not satisfy it. `"bootstrap-centering"` is
  explicitly **not** part of the ruling and may not be quoted as Joseph's.
- **The critical path is the ADOPTED SCALAR-5D COVARIANCE.** Every non-2D uncertainty projects
  from it and no candidate is adoptable. 2D is complete on central value *and* uncertainty; 3D,
  4D and 5D central values are validated with their covariances quarantined pending that trunk.
- **`OI-136` is MITIGATED, not closed (`38e876bf`).** `nd-unfolding/mnv_guarded_run.py` makes the
  `sys.path` hijack fail closed, wired into the two data-only launchers only.

---

## Lanes

Spawn one subagent per lane, in parallel. Each owns **disjoint files**. **No subagent commits** —
they return diffs and verdicts, and you serialize every commit yourself. Never stage another
session's changes.

**A. 5D covariance — write, effort `high`.** The B1 steps 4-5 pause holds because remedy (A) is
verified as SOURCE CODE ONLY and its ROOT write path *has never executed anywhere*. Note that
`sbatch_finalize_5d_bkgaware_gpu.sh`'s `mr_declared` gate exits 0 for declared members, so an
**undeclared** member reaches the adopt calls at `:181,186` — that is the route to a first real
ROOT execution without lifting the pause. Expect defects; the wrapper carries CLUSTER-UNVERIFIED
markers in four places. Deliver a launch proposal naming the exact output target and what it must
not overwrite. The walltime grant covers the run; **it does not cover the pause**, so the proposal
comes to Joseph.

**B. Provenance — READ-ONLY, isolated worktree, effort `high`.** `OI-7` and `OI-130`: enumerate
quoted values to artifacts and preservation status, then remediate by evidence class. Read-only
means read-only — run `git status` in the worktree when done and report it. Never freeze an
auditor's silent edit into a receipt.

**C. `OI-136` remainder — write, effort `high`.** The other 57 fail-open `.py` files, the 284
other `.sh` launchers, and whether `sbatch_finalize_5d_bkgaware_gpu.sh` should route through the
guard. **Re-run** `docs/orchestration/state/probe-oi136-sys-path-hijack-20260820.py`; do not quote
its numbers from the row. **Do NOT re-point a receipt-bound file to make a check pass** —
`OI-123` forbids it and `verify_hash_bindings.py` correctly refuses it. Landing the resolution
helper across the 59 is a frozen-provenance change: propose it per-site, do not sweep. Read the
row's `MITIGATED` note first — it records what the guard does *not* do.

**D. Deliverables — write, effort `high`.** The ruling requires PET to read as diagnostic in note,
primer **and** paper. **The paper is a distillation, not an extract, so a note-side edit does not
propagate** — it needs its own pass. `build_all.sh` must build all three cleanly.

**E. Re-triage — read-only, effort `medium`.** `OI-58` and `OI-93` are filed as PET/Gate-5 quoting
blockers. If PET is diagnostic, are they still *publication* blockers or method-development notes?
Report; do not rule.

**F. Infrastructure — write, effort `medium`.** `OI-70`, `OI-73`, `OI-127`, `OI-128`. Also:
`MANIFEST.tsv` is stale, but `generate_manifest.py` wants to add ~49 untracked files as `intended`
inventory and change `inbound_count` on ~74 rows. Report the split; do not assert other lanes'
files as intended inventory.

---

## Traps that have already cost this project real time

- **A passing check on the FILES AT PATHS says nothing about the MODULES IMPORTED.** That cost
  3 h 08 m of A100 on `57266000_0` while deployment parity reported `5 of 5 CURRENT`, honestly.
- **Tests here pin launcher LINE NUMBERS and file hashes.** Inserting one line can break a test in
  a different directory. Run the suites before and after and compare **symmetrically** — comparing
  your 7 failures to someone else's 5 is this campaign's signature error.
- **No `pytest` exists under any interpreter here.** Suites are `unittest` (run
  `python -m unittest <mod>` from the file's own directory) or are run directly as scripts.
  Default `python3` is 3.6 — use `/usr/bin/python3.11`, or
  `/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python` when numpy or ROOT is needed.
- **`sacct`/`scontrol` print PACIFIC.** A UTC read manufactures a 7-hour phantom offset.
- **One job id can show two rows with opposite answers.** Read the row with a real elapsed time;
  `Reason=BeginTime` is normal scron idle, not a hold.
- **Worker agreement is not independence.** Trace agreeing statements to their first measurement
  and count shared origins once.
- **A result is live only when its evidence, ledger, RUN_LOG and STATUS records land in a commit.**
  Uncommitted or merely relayed results are not quotable.
- **A guard whose fixture does not reproduce the defect passes vacuously.** Assert the failure
  first, then the fix.

## Do not redo

The 2D Phase-18.2 campaigns; the 3D framework, central unfold, marginal anchor, injected-shape
closure and generator comparison; the 4D/5D central anchors and closures; and any `OI-126`
containment, tail-geometry, target-factor, extraction or signal-MC occupancy probe. Their
surviving conclusions **and their retractions** are already recorded.

## Reserved for Joseph — collect, do not decide

`OI-71`, `OI-31`, `OI-75`, `OI-131(a)`. `OI-29` needs the collaboration, not a lane. Plus: lifting
the B1 pause, any change to the central estimator, uncertainty model or published claims, and any
compute under an explicit hold regardless of walltime.

## Capacity

Codex school **17.0%** weekly remaining (resets 2026-08-25), Codex personal 46.0% (resets
2026-08-27), **0 Full resets available or protected**. Claude school and school-legacy are ONE
quota — never sum the aliases. Budget delegation accordingly and re-measure before dispatch.

## Deliver

A decision list for Joseph; a per-lane verdict with witnesses (commit shas, `file:line`, job ids);
and an explicit list of what you did **not** do and why.
