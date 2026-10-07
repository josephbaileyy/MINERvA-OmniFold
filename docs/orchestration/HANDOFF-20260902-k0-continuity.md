# Handoff — k=0 redeploy continuity: the far-end filing, blocked on a NERSC filesystem outage

Written for a cold start. Everything here is durable: repository paths, real commit ids, and cluster
paths. Nothing points at a previous session's own filesystem.

## 1. What this is

`MINERvA-OmniFold` develops MINERvA ME-FHC inclusive charged-current cross sections with unbinned
OmniFold. **Read `AGENTS.md` first** — the shared front door, which routes every task to its governing
evidence. It is a view, never evidence or authorization. Domain, environment and scheduler rules are
task-specific; follow the route rather than inferring them.

Repository state at handoff: `main` at **`462d68be`**, pushed, working tree clean apart from
untracked drafts belonging to other lanes.

## 2. The state in one chain

Joseph authorized advancing the deployed execution tree
`/pscratch/sd/j/josephrb/k0r2/clean` from `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` to **one named
sha** on canonical `main`. **It has not moved.** Three links, in order:

1. **`FREEZE-20260830-k0-deployment-7ac0edec.md` §1 is LIVE.** It expires on exactly one condition,
   verbatim: *"when that rehearsal's F-1(b) producer filing is committed — not when its jobs merely
   look terminal."* No such filing exists. The only F-1(b) receipt in the repository,
   `RECEIPT-20260830-k0-f1b-producer-filing.md`, is scoped by its own box to the **previous**
   rehearsal at `aa67c426`.
2. **The filing needs `A-2(b)`**, which is `dirty_count` from `git status --porcelain` — the precedent
   filing named that instrument explicitly.
3. **That command does not return** on either cluster checkout.

Governing records: `DECISION-20260901-joseph-authorizes-k0r2-redeploy.md` (the authorization, its
scope, and the ordering constraint in its §3) and
`FINDING-20260901-pscratch-read-stalls-block-a2b.md` (the stall, its signature, and its complete
file list).

## 3. THE BLOCKER IS A NERSC SITE INCIDENT, NOT OURS

`https://api.nersc.gov/api/v1.2/status` reports **`perlmutter` = `degraded`** since
**`2026-09-01T05:58`**: *"Some jobs using Perlmutter's Scratch File System may hang or fail. Jobs with
a scratch file system license won't start."* `container_runtimes` is degraded *"until Perlmutter's
Scratch File System is recovered."* Global homes and CFS are `active`.

**The incident predates every probe in the finding.** There is nothing to report to NERSC and no
diagnostic left worth running; the only remaining variable is site recovery. Check the status API —
it costs nothing and touches no filesystem. **Do not infer recovery from a monitor's silence**: a
watch that fires only on change is indistinguishable, when quiet, from a watch that died.

**This also corrects the finding's §4 aside** that a fresh checkout "would very likely dissolve this."
The fault is under the filesystem, not under this tree, so a fresh checkout on the same scratch is not
a fix.

## 4. FIRST ACTIONS, in order

**While scratch is still degraded: do nothing on the cluster.** No sweep, no probe, no submission.

**When `perlmutter` clears:**

1. **Re-take `A-2(b)` and the rest of the far end.** A working script exists on the cluster at
   `/pscratch/sd/j/josephrb/k0r2/f1b_v4.sh`. **pscratch is purgeable — if it is gone, re-create it
   from this spec**, which is the shape the precedent filing used:
   - instrument: the **in-tree** `nd-unfolding/mnv_source_manifest.py` inside the deploy tree at
     `/pscratch/sd/j/josephrb/k0r2/clean` — **not** a wrapper that re-implements the measurement, and
     not `docs/orchestration/measure_k0_farend_f1b_f17b.sh`
   - interpreter: `/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3`
   - one invocation with all five fail-closed flags — `--require-clean --require-checkout
     --require-no-nested-checkout --require-not-nested --require-readonly` — plus `--compare` against
     `/pscratch/sd/j/josephrb/k0r2/declarations/7ac0edec/source-manifest.json`, and `--write` to a
     destination **outside** the deploy tree
   - record the instrument's `sha256` before and after
   - log every attempt **before** the operation, and write a terminal marker at the end
   - run it **`setsid`-detached**, output to a file on the cluster
   - **put the heartbeat on `$HOME`, not on scratch**, so a scratch stall cannot silence it
   - **nothing inside the deploy tree is edited to take this measurement**
2. **File the receipt.** It must name the instrument *and* the interpreter that produced its seven
   `A-2` values, as the precedent filing did. If a wrapper called the in-tree measurer, say so.
3. **Let the freeze expire on its own terms** at that commit. Do not cut it short.
4. **Redeploy per `DECISION-20260901-joseph-authorizes-k0r2-redeploy.md` §4**, which enumerates six
   obligations: re-verify the outgoing bundle including recovery from the bundle **alone**; confirm
   the freeze ref in **both** repositories first; do not repoint the old ref or destroy the old pin;
   file a superseding pin row per `OI-123`; instantiate a new declaration and freeze under that
   decision; and record the precondition delta for the other eight launchers.

## 5. Already measured — do not redo

- **`A-2(a)` is taken.** `.git/HEAD` holds the raw sha `7ac0edec…`, not a `ref:` — therefore
  **DETACHED**.
- **Bundle-alone recovery passes all six declared checks**, including the recovered clone
  independently measuring **820 files / `8d036d94…`**.
- **Preservation prerequisites re-measured** 2026-09-01: freeze ref present in both repositories at
  the pin; bundle **82,761,577 B** / `514bd46e…` exactly as declared; `git bundle list-heads`
  **exact-row** match, count 1.
- **Terminality**: `sacct -X` over the seven round-2 ids returns **374 distinct identities, 374
  COMPLETED, zero otherwise**, reconciling with 374 declared and with a second lane's independent
  count by a different method.
- **The stalled-file set is known** — ten files, listed in
  `FINDING-20260901-pscratch-read-stalls-block-a2b.md` §3, from a sweep that ran to completion
  (1803 attempts, terminal marker written). **Do not re-run that sweep**; the list already exists and
  probing adds load to the thing that is failing.
- **Wedged, not killed**, established by a detached run whose `$HOME` heartbeat ticked 41 times
  unbroken across 20 minutes while its output stayed at 0 bytes and `ps` showed the process alive in
  `futex_wait_queue`.

## 6. Prohibitions

- **Do not improvise a substitute for `A-2(b)`.** The precedent filing named its instrument; swapping
  the instrument to get past a refusal is the failure this campaign keeps recording. If a substitute
  is ever needed it is declared as one, in a record, with the reason.
- **Do not launch anything from the deploy tree**, freeze or no freeze. Three of the ten stalled files
  are executable science inputs — `nd-unfolding/pet_lateral_band.py`,
  `nd-unfolding/tests/test_fps_cli_integration.py`,
  `nd-unfolding/active_universe_5d/fps/covariance/fps_reported_mask.json`. A job that reads a stalled
  file stalls the same way and burns walltime in uninterruptible sleep without failing loudly.
- **Do not cut the live freeze short**, and do not cite the authorization as doing so. Its §2
  supersession route via `OI-123` sits at `DECISION-20260830` level — **Joseph's authority**.
- The redeploy target is **a sha, not a branch name**. `main` moved twice inside a single peer session;
  a definite description re-points the moment a second object satisfies it.

## 7. Working on a shared checkout

Several lanes commit to this repository concurrently — a `[pet]` lane pushed five commits during the
last session without either active lane knowing. Consequences:

- **`git add` with explicit pathspecs**, and diff your own hunks before committing. Never `git add -A`.
- **Regenerate the manifest with `--committed-only`**:
  `python3 docs/orchestration/generate_manifest.py --committed-only`. Default mode sweeps in
  *untracked* paths as `tracking=intended`, which will inventory another lane's uncommitted draft.
  This is the `OI-70` shared-checkout case and the flag exists for it.
- **Gates before committing**, and read their exit codes **unpiped**:
  `generate_manifest.py --check --committed-only`, then `control_plane_lint.py`. A `pre-commit` hook
  runs 12 checks.
- Adding a record needs a `MANIFEST-overrides.tsv` row **and** a `CATALOG.md` pointer — a record
  declared LIVE with no CATALOG pointer is born unreachable and the hook refuses it. Note
  `MANIFEST-overrides.tsv` **re-sorts on write**, so its diff stat looks alarming for a one-row
  addition; verify with a sorted diff before assuming a clobber.
- Check `ListAgents` before dispatching work; message a live peer rather than spawning a cold session.

## 8. Roadmap, in priority order

1. **Blocked on NERSC**: everything in §4. Poll the status API, not the filesystem.
2. **Unblocked, free, on paper**: the permanence-scope question — see
   `HANDOFF-20260902-clean-lane-permanence-scope.md`. **That work is not yours if you take any
   measurement bearing on cause 4's `M` leg**; it requires a lane with no such measurement, per
   `BEN-381`.
3. **Unblocked, and a real defect**: `SCOREBOARD-20260817-quarantine-seven-causes.md:73` asserts a
   value *"CANNOT be recorded on the dominant arm"*. Measured **false at HEAD** — four write sites
   exist. A live board asserting an untrue impossibility, load-bearing for what cause 3's `P-ii`
   remedy costs. Routed, unowned, and not yet repaired.
4. **Standing schedule constraint**: a seven-day maintenance is reserved **16–23 September**. Compute
   either lands before the 16th or waits for the 23rd. The `M(ii)` family remains the long pole.

## 9. Deliberately left alone

- **Cause 4's `M` cell is settled and should not be reopened.** Its referent was re-issued to the
  stamped candidate, and the leg is annotated at `SCOREBOARD:78` as unable to become `MET`. Cause 4 is
  therefore permanently undischargeable and the CAND ceiling is six, not seven — ruled with that cost
  stated. See `DECISION-20260902-joseph-applies-oi173-cause4-m.md`.
- **`CRITERIA-20260811` §0's grade vocabulary stands.** No fourth token; the *permanently unmeetable*
  state lives in cell prose. Decided on a census of 46 graded cells, not on preference. See
  `DECISION-20260902-joseph-rules-no-fourth-grade-token.md` — **do not re-propose a fourth token
  without new evidence.**
- **The historical-ratio reading of cause 4's `M` is undisposed by choice**, not by oversight.
  Disposing it decides `MET` vs not, which is the grade wearing a specification costume.
- **`DECISION-20260831` §2(b)'s stated 36.5-hour mechanism** is flagged, not filed: its conclusion
  stands, its `git log -S` reasoning is refuted by `VALIDATION_LEDGER.md:484` (VL40). Cite the
  conclusion, not the reason. Nobody has swept for other consumers of that step.
- Untracked files belonging to other lanes are theirs. Leave them.

## 10. Counts and gates, unchanged

**Gate 2 remains FAIL.** Quarantine counts hold at **CAND `1 of 7`, QUOTED `0 of 7`**. No scalar-5D
covariance is adopted; `values.tex` quotes none. A completed run is not a passed gate, and a
deployment is a position change that authorizes no science.
