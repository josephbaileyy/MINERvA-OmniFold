# DECISION 2026-08-22 — Joseph's eight rulings: clause (c), the verdict merge, and the B1 lift

**Recorded by the publication close-out lane on 2026-08-22, from Joseph directly in session.**

**Why this file exists.** These rulings arrived as a chat message. `AGENTS.md` states that a merely
relayed result is not quotable, and the campaign has already been burned by an authorization that
lived only in a socket — see
[`FINDING-20260822-a-hold-that-instructed-its-own-deletion.md`](FINDING-20260822-a-hold-that-instructed-its-own-deletion.md),
where a hold binding two lanes existed nowhere a lane could reach. **A lift of the B1 pause cannot
rest on a message.** This document is the citable record. Cite this path; do not cite a relay of it.

**This document records rulings. It does not interpret them into new scope.** Where I disagree or see
a residual, that is marked as mine and separated from his words.

---

## Ruling 1 — clause (c) is satisfied by the `srun` execution

> "The srun execution of the launcher's exact steps 4–5 segment satisfies clause (c). The clause
> excludes a wrapper-only invocation; it does not require submitting the complete launcher through
> sbatch. Requiring that would make the expiry circular because the declared launcher exits at the
> pause before reaching those steps. Do not reword the clause."

**The clause text is UNCHANGED and must stay unchanged.** It remains at
`nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh`, anchored on content (the block has moved
repeatedly; it sat at `:285-291` at `00be534f`). This ruling is recorded *beside* it, not *in* it.

The circularity is real and was measured, not argued: `mr_declared()`
(`nd-unfolding/lib_member_resume.sh:230`) is true exactly when `MNV_EST_SEED_OFFSET` is set — that is,
for a **declared present-seed member**, which is the case clause (c) requires. That branch is entered
at `:256` and exits at `:330`, **before both adopt calls at `:347` and `:352`**. So while the pause
holds, the present-seed path cannot reach steps (4)/(5) through a real `sbatch`, and a clause
demanding it would be its own precondition.

## Ruling 2 — merge both verdict branches

> "Integrate both verdict branches into main, including the full correction chain through 81905bba.
> Preserve the first verdict as historical evidence and identify the production-dimension rerun as
> the operative verdict. The inventory cost is accepted. Regenerate and verify MANIFEST.tsv from the
> tree containing all evidence."

**Executed** at `2d8ec657` (first verdict) and `c7f27ec0` (operative rerun), pushed to `origin/main`.
Ancestry verified separately for each: `33c0e0fa` and `81905bba` are both ancestors of remote `main`.

| document | class | event_status | successor |
|---|---|---|---|
| `VERDICT-20260821-clausec-rerun-production-dimension.md` | `ARCHIVAL` | `terminal` | — **OPERATIVE** |
| `VERDICT-20260821-expiry-c-real-path-present-seed.md` | `ARCHIVAL` | `superseded` | the rerun |

Manifest verified from the tree containing all evidence: rows `377 → 414`, **zero dropped** by path-set
difference, 36 added and all 36 are the merged paths; `generate_manifest.py --check` exits 0.

**MY QUALIFIER ON THE WORD "SUPERSEDED", which is coarser than the truth.** The first verdict is not
wrong and is not retracted. It scopes itself explicitly to the upstream-seed **identity axis** and
says in its own words that it "verifies nothing about the payload at production dimension." The rerun
is what covers production dimension — 22 arms at *n* = 10694 with real ROOT. So the first is
**narrower**, not superseded in the ordinary sense. The manifest has no vocabulary for "extended by";
`canonical_successor` is the field that carries Joseph's operative designation. Both files are
preserved in full.

## Ruling 3 — the pause is lifted, conditionally

> "Once those verdict records are integrated and the manifest checks pass, I rule all three expiry
> conditions satisfied and lift the B1 steps 4–5 pause."

**Both conditions are met as of `c7f27ec0`** (integration in ruling 2 above; `--check` exits 0).
Therefore, on Joseph's authority and not on any lane's: **the B1 steps 4–5 pause is LIFTED.**

The three clauses, with where each was discharged:

| clause | requirement | discharged at |
|---|---|---|
| (a) | `OI-141` — gate verdict from structured data, not parsed prose | `3cb46337` |
| (b) | `OI-140` — upstream-seed identity **recomputed**, not declared | `3cb46337` |
| (c) | fresh non-builder verifies the real steps (4)/(5) path, present-seed, with a negative control | `81905bba`, ruled satisfied by ruling 1 |

**The launcher's own text is not edited by this and still says what it says**, including *"NOTHING
ABOUT (c) IS SATISFIED BY THIS SCRIPT RUNNING SUCCESSFULLY. Only Joseph lifts the pause."* That
remains true; this document is Joseph lifting it.

## Ruling 4 — the preflight runbook gates the first submission

> "Before the first real submission, land the preflight runbook with the exact sbatch command and
> environment, executing-tree/digest checks, expected output at every gate, abort conditions, and the
> disposition rule for the 41.44 GB intermediate. Do not delete that intermediate until MVFINAL_j
> exists and validates."

See [`RUNBOOK-20260822-b1-lift-preflight.md`](RUNBOOK-20260822-b1-lift-preflight.md).
**No production submission before that document is on `main`.**

The deletion prohibition is not new and is not only Joseph's: §11g of the launcher gates deletion on
`MVFINAL_j`, which is produced by steps (4)/(5) — so deleting the intermediate before then would
destroy **the only input** to the steps that have not run.

## Ruling 5 — preserve the hold; file the composition as a finding

> "Preserve HOLD-20260821-clause-c-verification.md unchanged. Add an explicit ARCHIVAL / terminal
> override and file the delete-versus-retention composition as a finding. Record honestly that the
> committed hold file was router-inert and that the live coordination came through socket traffic; do
> not delete, rename, or retroactively claim the file bound the lanes."

**Executed** at `d78858c6`. The hold's bytes are byte-identical to their committed form — I had
already appended a correction block to that file before this ruling arrived and reverted it in full.

**RESIDUAL, DISCLOSED AND NOT CLOSED:** the hold still ends with *"delete it"*, and preserving the
bytes means that instruction stays live and reachable. `MANIFEST.tsv` gives the file
`read_policy=exact-path-only`, so a lane arrives by opening that exact path. The disarm is the finding
plus the [`CATALOG.md`](CATALOG.md) route, and it works **only if the reader arrives there first**.
This cannot be closed without editing bytes ruling 5 preserves. Joseph's to weigh.

## Ruling 6 — the two hook changes, in order

> "I authorize the two hook changes in this order: first wire the seven-column checker onto an
> executed path, then add field-count validation to control_plane_lint. Include negative controls
> demonstrating malformed rows are refused."

The seven-column checker itself was **already built** by the `worktree-oi148-sevencol-check` lane at
`814556f6` — extraction only, hook untouched, ratchet excluded by an executable test rather than by a
comment, 27 cases including five mutation tests. Wiring cost measured at ~0.31 s against a 1.797 s
hook, about 17%.

**A RESIDUAL, AND IT IS SMALLER THAN I FIRST CLAIMED — MY OWN OBJECTION WAS REFUTED BY MEASUREMENT.**
That checker reads the **index** (`git show :docs/OPEN_ITEMS.md`), chosen so one lane's uncommitted
edit cannot block another's commit. I objected that this only narrows the hole from "any lane's
unsaved edit" to "any lane's staged edit," and predicted that a pathspec commit
(`git commit -- other.txt`) would be refused over a peer's staged row the commit does not contain.

**That prediction is false, and the reason is a measurement error of mine that this campaign keeps
filing.** I ran my probe *alongside* the commit rather than *inside the hook*, and those are different
subjects. Re-run from inside a real installed `pre-commit` on git 2.39.3 (Apple Git-146):

| commit form | `GIT_INDEX_FILE` seen by the hook | `git show :docs/OPEN_ITEMS.md` | `git diff --cached --name-only` | commit contains |
|---|---|---|---|---|
| `git commit -- other.txt` | `.git/next-index-<pid>.lock` | **GOOD** | `other.txt` | GOOD |
| `git commit` (plain) | `.git/index` | MALFORMED | `docs/OPEN_ITEMS.md` | **MALFORMED** |

Git builds a **separate temporary index for a partial commit** and exports it to the hook via
`GIT_INDEX_FILE`; `git show` honours it. So the set of paths the commit will create **is** derivable
from inside the hook — through the environment, not through a git query — and the pathspec case is not
a false block. Credit for that goes to the checker's own lane, which measured it correctly first.

**What survives is genuine but different:** on a plain `git commit`, the hook does see a peer's staged
row — and the commit **does contain it**, so refusing is correct rather than spurious. "Blocked over
someone else's row" stays true; "blocked over a defect the commit does not contain" does not.

**The fragile part is that the fix is invisible in the source.** Nothing in the checker reads
`GIT_INDEX_FILE`; it works because the module shells out without scrubbing the environment. Scrubbing
it for hygiene would silently restore the false block with nothing going red. That lane has added a
negative-control arm pinning exactly this, which is the arm that makes the other two mean anything.

## Ruling 7 — `OI-137`, scoped

> "For OI-137, declaration (v) has already landed. Assign the remaining candidate-specific work to
> the scalar-5D adoption/statistics owner. Do not apply a blanket Hartlap correction to the summed
> covariance. Require each sample-covariance block to declare its ensemble size, normalization
> convention, effective inversion dimension, and finite-ensemble treatment, and return a
> recommendation before any uncertainty-model change."

**No uncertainty-model change is authorized by this ruling** — a recommendation is required first.
The four required per-block declarations are: **ensemble size**, **normalization convention**,
**effective inversion dimension**, **finite-ensemble treatment**.

**VERIFIED 2026-08-22, having first recorded it as unchecked.** Declaration (v) landed at
`4fb0e3d4` on 2026-08-21 in `docs/analysis-note/app_statmethods.tex`, and it requires precisely the
four operands Joseph names. Joseph's ruling matches the landed text exactly.

**Verifying it falsified two claims in `OI-137`'s own row**, both true when written on 2026-08-20 and
overtaken by `4fb0e3d4` the next day. The row says the protocol "mandates exactly four declarations"
and that searching for `hartlap` / `N-p-2` / `(N - p` returns **zero** hits; it is five, and the
search now returns two. And the row says the bias runs "in the direction that flatters the fit" —
**the landed note says the opposite in as many words**, because an over-tight precision matrix
*inflates* a chi-square on a fixed residual. Tension is **overstated**, not hidden; what is
over-optimistic is any confidence region drawn from the same covariance. That is a materially
different hazard, and the row has been corrected.

## Ruling 8 — leave the strays; keep deferred items deferred

> "Leave the two untracked files alone unless ownership is established. Keep the off-critical-path
> WAITING-USER items deferred."

`PROJECT_STATE_PILOT_PROPOSAL.tmp.md` and `log_test.txt` remain untracked at the repository root,
untouched.
