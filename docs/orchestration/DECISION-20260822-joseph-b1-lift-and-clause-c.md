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

### Which document supports which half of "measured, not argued"

**Added 2026-08-22 to correct an overclaim of mine.** My merge commit `63cbf995` described
`FINDING-20260822-clause-c-adopt-is-unreachable-under-its-own-pause.md` as *"the only one that RAN
the launcher rather than reading it"* and pointed the sentence above at it. **Its author objected and
is right on both counts**, in the direction this whole thread has been correcting — over-claiming
scope. The commit message cannot be edited after pushing, so the correction lives here, where a reader
chasing the evidence for ruling 1 will actually arrive.

| claim | cite | why |
|---|---|---|
| **the adopt semantics were measured** | `33c0e0fa` / `81905bba` | the real extracted segment under `srun`, **real ROOT at production dimension** *n* = 10694, 22 arms, 16 refusals firing |
| **no configuration reaches `:347`/`:352`** | the reachability finding | a control-flow harness plus a covering enumeration of the environment |

**What that finding actually ran, in its own words and in its own scope section:** a **copy** of the
launcher with line 15's hardcoded `REPO` repointed at a sandbox (verified by diff as the sole hunk); a
**stub `python3`** recording argv and touching output paths, so **not one ROOT byte was read** and the
two 892 MB products were never built; a stubbed `setup_salloc_env.sh`; bash 3.2.57 locally, **never
under `sbatch` or Slurm**; and in the single arm that reached adopt, **a fabricated `.done` marker** —
on the real tree that marker is absent, which is the point of its own §4. So the resolver block at
`:18-100`, the `BASH_SOURCE`/spool behaviour and the `${REPO}` hardcode's real effect are all
**untested by it**.

That makes it the right instrument for the **branch** question and **weaker**, not stronger, evidence
about anything downstream of the branch. Its value is real and specific: the launcher takes **no
positional arguments**, so behaviour is a pure function of the environment, and a covering enumeration
of every `${VAR}` on an uncommented line leaves `MNV_EST_SEED_OFFSET` as the only lever on `:256`.
That is a structural claim, and structural is what ruling 1 needs.

**On "third independent method", which I also wrote:** its author declines to certify the count,
noting it can only attest that neither of the other two routes is its own — it has not audited whether
the runbook's route and `33c0e0fa`'s are independent **of each other**. They are not fully: the runbook
reads the same control flow the verdict does. **Two methods are demonstrably independent — the stubbed
harness and the real-ROOT `srun` arms. The runbook is a third reading, not a third measurement.**

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


---

# SECOND SET OF RULINGS, 2026-08-22 — rulings 9–14

Recorded on the same basis as rulings 1–8: verbatim from Joseph in session, committed because a
relayed result is not quotable.

## Ruling 9 — the two pinned Gate-5 records stay; erratum elsewhere

> "Preserve the two pinned Gate-5 records byte-for-byte; do not rerun Gate 5 or reissue their receipts
> for this prose error. Add a concise erratum to the live, non-pinned Gate-5 specification stating that
> the noisy sample-covariance inverse is biased upward: for a fixed residual, χ² is inflated and
> tension is overstated. Point from there to the corrected OI-93/OI-137 record."

**EXECUTED, WITH ONE SUBSTITUTION THAT THE RULING'S OWN PREMISE REQUIRES.** *"The live, non-pinned
Gate-5 specification"* **does not exist.** Measured 2026-08-22:
`state/gate5-cstat-spec-measurements-20260814.json` pins **both** records —
`SPEC-20260814-gate5-cstat-construction-v1.md` at `4fed4e2b…` under `"SPEC (markdown)"` **and**
`pet/gate5_cstat_contract.json` at `ef5fe362…` under `"machine contract"`. The SPEC's live sha256 is
exactly `4fed4e2b…`, `verify_hash_bindings.py` reports ALL BINDINGS INTACT, and that same digest is
the mutation anchor at `tests/test_hash_bindings.py:41`. Editing the SPEC breaks a live binding and
fails pre-commit, which is the same cost the ruling declines to pay for the contract.

**The erratum therefore landed in `nd-unfolding/PET_UQ_REMEDIATION_STATUS.md`** — unpinned, `LIVE`, and
already citing both Gate-5 records at `:579`. This is not a workaround: that file **already contains a
paragraph explaining that the pin makes amendment impossible**, ending *"This paragraph exists because
a contract reader has no other way to learn the ruling exists"*, with precedent at `BEN-238` / `OI-123`
where an additive amendment was **reverted rather than repinned**. The ruling's intent — an erratum a
Gate-5 reader will reach, pointing at the corrected record — is satisfied at the established channel.

## Ruling 10 — declaration (v) assigned to the standard-P4 lane

> "Assign the remaining declaration-(v) work to the standard-P4 lane, acting as the scalar-5D
> adoption/statistics owner. Its scope is to record, for each 5D sample-covariance block, ensemble
> size, normalization convention, effective inversion dimension, and finite-ensemble treatment. This
> assignment authorizes record/provenance completion only—not adoption or an uncertainty-model change.
> Do not route it back to the measurement lane or the PET C_stat lane."

**Recorded on `OI-137`'s owner cell**, superseding `UNOWNED`, with the scope limit and the
do-not-reroute instruction stated in the cell so they travel with the assignment.

## Ruling 11 — disclose, do not correct

> "I accept the recommendation to disclose and not correct. Apply no blanket Hartlap factor to the
> summed covariance and make no covariance change. The disclosure must use the mixed-block/
> data-dependent-truncation rationale. Do not justify this using the finite-N blocks' trace share. For
> the quoted 2D headline, the relevant protection is that the paper's external rank-205 StatOnlyCov
> sets the small-eigenvalue floor; the result remains explicitly non-calibrated as a goodness-of-fit
> statistic."

**LARGELY ALREADY SATISFIED IN THE NOTE — measured before writing anything, so that no redundant prose
is added to a publication artifact.**

| requirement | status |
|---|---|
| mixed-block / data-dependent-truncation rationale | **present**, `app_statmethods.tex:673-675` — *"a sum of that kind has no single debiasing factor; the standard factor also assumes independent Gaussian realizations and a truncation dimension chosen independently of the data, neither of which is established for a data-dependent rank cut"* |
| explicitly non-calibrated as a GoF statistic | **present**, `sec_results.tex:63` |
| no blanket Hartlap factor, no covariance change | **holds** — nothing implements one; `app_statmethods.tex:672` says *"No generic correction is mandated here, deliberately"* |
| StatOnlyCov as the small-eigenvalue floor **for the quoted headline** | **partially present and framed differently** — see below |

**The gap, and it is narrow.** `app_statmethods.tex:874-884` states the StatOnlyCov comparison, but as
an argument about why an **ours-only** χ² is out of reach, not as the protection for the **quoted**
headline. Those are adjacent, not identical. **No note edit is made on my own reading** — the note is a
publication artifact and the ruling does not in terms require new text. Flagged for Joseph.

**A NUMBER TRAP TO CARRY, because both values are correct at different scopes.** The brief says our
bootstrap is **6.41×** smaller than `StatOnlyCov`; the note says **2.5×**
(`sqrt(Tr C^boot) = 1.8e-40` vs `sqrt(Tr StatOnlyCov) = 4.6e-40`). **2.5 is the sqrt-trace ratio and
6.4 is the trace ratio** — 2.56² = 6.53 from the note's rounded operands. Neither is wrong; quoting
either at the other's scope is. **Say which power you mean.**

## Ruling 12 — the target is option (a), the M(ii) member scan

> "The scientific target is option (a), the M(ii) member scan—not stamped re-adoption of the archive
> products. Marker backfill remains unauthorized. This selects the target but does not authorize the
> 151 A100-hour family, C_ML production, or a full member scan."

**Selection only.** A staged one-member plan is required before production authorization is sought,
covering: exact jobs and per-leg resource estimates; scratch quota and output disposition below the
runbook threshold; the exact member/offset for the first submission; terminal success and abort
conditions; **what a one-member pass cannot authorize**; and the remaining cost and storage for the
full family.

## Ruling 13 — pause-branch removal deferred

> "Defer removal of the launcher's pause branch until a member is actually runnable. Preserve the
> clause text and existing pins in the meantime."

No action. Matches the disposition already recorded under ruling 1.

## Ruling 14 — the first complete member IS the Slurm rehearsal

> "For option (a), the first complete member should also serve as the real Slurm rehearsal. That
> rehearsal is a production submission, not a stub test, and therefore must wait for explicit approval
> of the one-member plan. It should exercise the real launcher, executing-tree/digest checks, Slurm
> resolver behavior, gates, and abort conditions. A successful rehearsal does not authorize the
> remaining family."

This closes the open item the reachability lane left: its harness ran a patched copy with stubbed
producers, never under Slurm, so `BASH_SOURCE`/spool behaviour, the resolver block and the `${REPO}`
hardcode's real effect are untested. Ruling 14 makes the first real member the test of exactly those.
