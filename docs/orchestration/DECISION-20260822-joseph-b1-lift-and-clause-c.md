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

### Ruling 11 amendment — AUTHORIZED AND EXECUTED 2026-08-22, superseding "no note edit is made"

Joseph authorized the narrow clarification on 2026-08-22: *"connect the quoted combined chi-square
explicitly to the external rank-205 near-diagonal StatOnlyCov floor... Do not use trace share alone as
the safety argument and do not change any quoted result."* **Done**, on branch
`note-statonlycov-floor-clarification`, as one new `\paragraph{}` in `app_statmethods.tex` (now at
`:679`, immediately after the declaration-(v) paragraph and before the `chi2_with_cov` implementation
note, i.e. in the same subsection as the quoted headline). It states that the headline inverts the
paper+ours **sum**, that the sum carries the paper's rank-205 near-diagonal `StatOnlyCov`, that a
finite-`N` debiasing factor would act on small-eigenvalue directions an external published block
supplies, and — explicitly — that this is *not* a trace-share argument, because a trace weights
eigenvalues by `lambda` and a precision matrix by `1/lambda`. No quoted result changed; note, primer
and paper rebuilt (`build_all.sh` exit 0).

**The paper needs no counterpart, and this is the measured reason rather than a judgement.**
`paper_body.tex` quotes `\chiPaper` (`3.66`, paper-covariance-only) at `:71` and `:74` and **never**
`\chiCombined`; it contains no occurrence of `StatOnly`, `Hartlap`, or any finite-ensemble statement.
`primer_body.tex` quotes no chi-square at all. The sentence protects the *combined* number, so the
distillation has nothing for it to attach to; adding it would import a discussion of an object the
paper does not quote.

**THE TRACE RATIO IS 6.5, NOT 6.41 — the `6.41` above is an asymmetric-rounding artefact.**
Re-derived 2026-08-22 from the note's own operands, and reported rather than adopted:

| route | operands | sqrt-trace ratio | trace ratio |
|---|---|---|---|
| note's displayed values, both 2 s.f. | `4.6e-40 / 1.8e-40` | 2.556 | **6.53** |
| this document / the brief, mixed precision | `4.6e-40 / 1.817e-40` | 2.532 | **6.41** |
| **the note's own recorded ratio** (`app_statmethods.tex:927`) | `C^boot/StatOnly = 0.392 = 1/2.55` | **2.551** | **6.51** |

The middle row divides a **2-significant-figure** numerator by a **4-significant-figure** denominator.
It is refuted by the note itself: `1.817/4.6 = 0.395`, not the recorded `0.392`, so `4.6e-40` is the
rounded form of `4.635e-40` and the honest ratio is `2.55`. Propagating the last recorded digit
(`0.392 +/- 0.0005`) gives a sqrt-trace ratio of `2.548-2.554` and a trace ratio of **`6.49-6.52`** —
an interval that contains 6.5 and **excludes 6.41**. The note therefore says `2.55^2 ~ 6.5`, written
as the square so the derivation is visible inline. Joseph's `~6.4` is the one figure in the
authorization not adopted; the deviation is deliberate and is flagged for him to overrule.

The prose mislabel that produced the trap is also corrected at `app_statmethods.tex:899`: *"smaller by
trace"* now reads *"smaller in square-root trace"*, which is what its own displayed operands measure.
No number changed on that line. Left alone deliberately, because fixing it would change a claim rather
than a label: the same sentence's *"regularizes the small systematic modes 2.5x less"* is a
variance-scale statement, and in variance the factor is 6.5, not 2.5. That is a substantive edit, is
outside this authorization, and is recorded here for its owner.

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


---

# THIRD SET OF RULINGS, 2026-08-22 — the trace ratio, durability, and the k=0 integrity package

## Ruling 15 — the trace ratio is 6.5, and the adjacent wording is repaired rather than patched

Joseph re-measured over the 205 reported bins: `sqrt(Tr StatOnlyCov) = 4.63860e-40`,
`sqrt(Tr C_boot) = 1.817e-40`, **sqrt-trace 2.5529, trace 6.5172.** Independently reproduced here;
it falls inside the `[6.49, 6.52]` interval derived earlier from the note's own recorded `0.392`.

**The 6.41 I supplied was an asymmetric-rounding artifact** — a 2-significant-figure numerator over a
4-significant-figure denominator. It reached this ruling because I relayed it without checking the
precision of its operands.

**AND THE OLD SENTENCE IS REPLACED, NOT RENUMBERED, ON A POINT OF PHYSICS THAT IS JOSEPH'S NOT MINE.**
I had proposed changing *"regularizes the small systematic modes 2.5x less"* to `6.5`. That is wrong:
**a global trace ratio is not a uniform per-eigendirection factor.** The replacement states the global
scale, gives both powers, and explicitly refuses the per-mode reading:

> The bootstrap block is smaller in *global scale* by a factor 2.55 in square-root trace
> (`1.817e-40` vs `4.639e-40`), equivalently about 6.5 in trace. The paper's full-rank, near-diagonal
> `StatOnlyCov` supplies a variance floor in every reported eigendirection; because the covariance
> structures differ, this should *not* be read as a uniform 6.5-fold per-mode effect.

**One change beyond the ruling's text, disclosed:** the displayed operands move from `1.8`/`4.6` to
`1.817`/`4.639`. Necessary, not cosmetic — leaving 2-significant-figure operands beside a `2.55` claim
would reproduce the exact rounding defect this ruling exists to correct. No quoted *result* moved:
`252`, `3.66` and the headline are untouched.

Rebuilt after the edit, not before: `build_all.sh` exit 0 read unpiped, 4 engine starts, 4
`Output written on`, all three PDFs newer than a marker stamped before the run, and the new prose
present in `main_note.pdf` and absent from primer and paper — which is correct, since the paper
quotes only `\chiPaper` and never the combined number.

## Ruling 16 — durability copy authorized

Copy the six quarantined files to a dedicated directory under `/global/homes/j/josephrb/evidence/`,
verify all six sha256 at both locations, **retain the pscratch originals**, and amend the existing
receipt with the destination and the verification results. Home over HPSS for a 278,611-byte object.
**Copying and receipt amendment only — no deletion, no regeneration, no submission.**

## Ruling 17 (3a) — the two-root design is approved

`MNV_CODE_ROOT` (immutable, clean, named-commit execution tree) and `MNV_DATA_ROOT` (inputs and
outputs; the canonical checkout may serve **only** in this role). Both mandatory, no default. Every
executed or imported repository file resolves under the code root; every data product under the data
root. Grounds, in Joseph's words: *"A clean checkout cannot simultaneously host 47.7 GB of gitignored
products and remain clean."*

## Ruling 18 (3b) — the bounded source and launcher repair is approved

Authorized **exactly**: the six Python repairs **including `unified_throw_cov.py`** — excluding that
imported module *"would leave the transitive rooted-import defect open"*; the **eight launchers' shell-root
repairs**, because otherwise *"the wrong root is selected before Python or the guard starts"*; and the
necessary guard, tests, OI-136 positive-control replacement, ratchet update, runbook and plan
couplings. **New ratchet values must come from the probe/test output.** Not authorized: the
repository-wide 59-file migration, or any scientific-model change.

## Ruling 19 (3c) — N-2 is REJECTED as written, and child-boundary testing is NOT waived

Joseph's reason is a defect neither the reviewer nor I saw, and it is internal to the contract:
**a copied writer placed outside `MNV_CODE_ROOT` would be refused by the contract's own planned
script-containment rule (B-4) BEFORE its injected import ever executes.** The control would pass for
the wrong reason — proving containment, not child-boundary import guarding. Second defect: *"the
proposed third checkout is not actually on the adopter's hardcoded import path."*

Replacement, authorized:

- a **minimal purpose-built fixture writer INSIDE a disposable expected checkout** — so it passes
  script containment;
- accepting the real child argument shape;
- deliberately importing an **existing repository-local module from a second checkout** — so the
  resolution guard is what fires;
- invoked through the actual `build_child_argv(..., writer=fixture)` path;
- **unguarded: prove the wrong module loads. Guarded: exit 3 before any output is opened.**
- **No copy or edit of the pinned science writer, and no `--allow`.**

This tests the child-wrapper plumbing directly while the production writer stays untouched. It is
strictly better than both my proposal and the reviewer's.

## Scope, restated because a package this size reads as broader than it is

> "None of these rulings authorizes a Slurm submission, the full family, `C_ML`, or a scientific
> adoption."


---

# FOURTH SET OF RULINGS, 2026-08-22 — F-9 restated, the guarding boundary, and A-2 enforcement

## Ruling 20 — B-4 is preserved and F-9 is RESTATED, not exempted

> "Do not disable or exempt B-4. F-9 is restated because its original import-specific expectation is
> incompatible with the earlier script-containment protection. F-9 now passes when the real
> canonical-checkout wrapper is run with the clean tree as `--expect-root` and: exits 3 through B-4;
> records `refused:script-outside-expect-root`, never an empty/green verdict; names the script,
> canonical root and expected clean root; records `checked=0` as expected; satisfies O-1 through O-4,
> with no child marker or output. It must not name `seed_offset_policy`, because the import guard is
> intentionally never reached. N-2 and N-3 remain the import-resolution negative controls. The U/U'
> arm may remain as evidence that the canonical module would load without containment, but it is not
> the mechanism of the F-9 refusal. Update F-12 consistently. No B-4 bypass flag or production
> exception is authorized."

**HOW THIS AROSE, because the shape recurs.** The round-2 builder performed N-1 and found F-9
**unsatisfiable by its own B-4's success**: containment runs before `install()`
(`mnv_guarded_run.py:464`), N-1 runs the real wrapper from the canonical checkout, so the script is
outside `MNV_CODE_ROOT` and is refused *first* — `checked=0`, and `seed_offset_policy` is never
named. Verified here in the source, not taken on report.

**This is the identical shape ruling 19 found in N-2, arriving in N-1.** Neither the contract nor the
round-1 verdict caught it: §7.0.2 uses F-9 as its *worked pre-submission example* and the verdict
recorded only "not performed". **A protection can invalidate the control written to test a different
protection**, and the control then reads as merely unperformed.

**One inversion a grader will get wrong:** `checked=0` is now the EXPECTED value for F-9, where in
every other criterion an empty inspection set is the vacuity trap. It must additionally require
`refused:script-outside-expect-root` **positively** — the builder found a real bug where a B-4
refusal raised no violation and fell through to `EMPTY-REPOSITORY-ORIGIN-SET — THE GUARD REFUSED
NOTHING BECAUSE IT SAW NOTHING`, both clauses false.

## Ruling 21 — the 14/30 guarding boundary is ACCEPTED

> "I accept the guarding boundary: guard all 14 launcher-level science invocations and the
> pinned-writer child. The 16 calls to the two preflight integrity tools are excluded from the guard
> and from P-4 because guarding the tools before they validate the guard creates a trust-order
> inversion, and their intentionally empty import sets would weaken P-4 with standing exceptions.
> Both preflight tools must remain covered by the source manifest and executing-file parity set and
> must run before any science invocation."

**Fourteen, not eight** — enumerated by the builder and counted independently here: finalize 5,
detector 2, uthrow-block 2, one each elsewhere. "Eight one-line edits" was my figure and it was wrong;
Joseph's "every production Python invocation" was the right phrasing.

The ordering clause is now a **criterion, not a convention**: if a launcher can reach a science
invocation without the preflight having run, that is a finding.

## Ruling 22 — A-2(d), (e), (g) must be enforced before Gate 1

> "A-2(d), (e), and (g) may not remain merely documented. Before Gate 1, add fail-closed checks
> rejecting a nested checkout, a code root nested inside another checkout, and a writable code root;
> apply and verify write protection. Production P-4 pins are correctly a post-rehearsal artifact, but
> the mechanism and its fail-closed behavior remain Gate-1 requirements."

(d) and (e) are the two directions of one nesting hazard, and `checkout_root_of` returning the
**innermost** match is why a nested checkout inside the code root resolves to itself — the same
mechanism that made the OI-136 ratchet read 369 instead of 58.

**The pin is post-rehearsal; the mechanism is Gate-1.** What must be provable now is that an
undeclared or mismatched import set is refused, not that the real pins exist.

## Ruling 23 — the verdict is held

> "Hold the Gate-1 verdict until those changes and the F-9/F-12 amendment are independently verified.
> No merge or submission is authorized by this ruling."

The grading lane must be neither the builder nor the verifier who amended the rubric.

## Ruling 24 — cause 3 is scoped to `X` per (cause × artifact × covariance role), and 2D is NOT reopened

> "Cause 3 is assessed per cause × artifact and per covariance role. It remains applicable to `X`'s
> construction. It is N/A to an intentionally isolated training-seed covariance, including the
> validated 2D ML block, because seed variation is that block's declared estimand rather than
> contamination of another uncertainty component."

**This closes `PR-X3`, and it closes it NARROWLY: the carve-out names the 2D ML BLOCK, not the 2D
artifact.** Nothing here reopens 2D and nothing here clears it beyond that block. In particular the
question of whether 2D's own 187-universe systematic sweep is single-seeded is **neither asked nor
answered**, and "per covariance role" must not be read as having settled it.

**The factual basis is verified, not relayed** — `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md:94`:

| Component | N | √tr(C) |
|---|---|---|
| ML noise (lgbm seedscan) | 10 | 5.061e-41 |
| Statistical (Poisson bootstrap, **pinned ML seed**) | 300 | 1.817e-40 |

Separately constructed, separately reported, and the bootstrap pins the seed so the two cannot
double-count. The earlier contaminated bootstrap family was replaced with negligible movement.

### The criterion as stated does not describe `X`, and this record repairs it rather than inheriting it

The ruling's general clause — cause 3 applies where seed variation *"leaks into a covariance intended
to measure something else and is consequently misclassified"* — **is not what cause 3 is about on
`X`.** `SCOREBOARD-20260817` §2b, on `X`: *"**NO NUMBER MOVES.** Every leg is internally
single-seeded, so nothing is mis-computed. What fails is a **verification claim**."* Nothing leaks.
Read literally the stated criterion would make cause 3 `N/A` for `X` too, contradicting the ruling's
own next sentence.

**Nor can "has an isolated training-seed block" be the discriminator: `X` has one.**
`sbatch_finalize_5d_bkgaware_gpu.sh:280` builds `C_ML` from `seedscan_split`. Both artifacts have a
seedscan block.

**The discriminator that yields both of the ruling's answers is the DOMINANT block.** `X`'s dominant
term is the 188-universe systematic sweep, computed at a **hardcoded seed 42** —
`sweep_bank_5d.py:252`, the only occurrence of `seed` in that file. Cause 3 on `X` is three separate
defects with three separate remedies:

| leg | defect | remedy | needs compute? |
|---|---|---|---|
| **P-i** | no product or receipt records the seed **value**, anywhere | add a stamp | **no** |
| **P-ii** | the dominant arm has **nowhere to put one** — `analyze_universes_5d.py` contains `seed` zero times. **Survives P-i's fix** | a new write site | **no** |
| **M(ii)** | the magnitude is unmeasured | the member scan | **yes** |

**So the operative form of the ruling is:** *cause 3 asks whether an artifact's **dominant** block's
estimator-seed dependence is **recorded** and **measured**.* `N/A` for the 2D ML block — its estimand
*is* seed variation and it is not a dominant block. **APPLICABLE** to `X`. No contradiction, and both
halves are falsifiable from named files.

**Consequence worth acting on: two of cause 3's three legs cost nothing.** `P-i` and `P-ii` are
dispatchable independently of the family and of `M(ii)`.

## Ruling 25 — PR-J5: no binding-after-use for Gate 1; verify before source

> "A file sourced before the parity check can be bound afterward as historical provenance … But that
> cannot establish the stronger claim needed here: 'unverified bytes were prevented from executing.'
> … resolve frozen code root → verify `setup_salloc_env.sh` and `resume_guard.sh` → source them → run
> remaining preflight checks → invoke science. … do not redefine an after-the-fact check as preflight."

**Implemented in `PR-02`, `6113a34d` on `build-k0-execution-integrity`.** The ordering was cheap:
`CODE_ROOT` is already resolved before the first `source` in all eight launchers.

### The ruling's feasibility note is FALSIFIED, and the ruling's own fallback is what was used

> "The current verifier is deliberately lightweight — standard library plus git — so an earlier
> invocation appears practical."

The imports are indeed stdlib. **The interpreter is not.** Measured on `saul.nersc.gov`:

```
$ command -v python3; python3 -V          # bare login shell, nothing sourced
/usr/bin/python3
Python 3.6.15
$ /usr/bin/python3 -m py_compile nd-unfolding/pet/verify_executing_copy_is_committed.py
  File ".../verify_executing_copy_is_committed.py", line 54
    from __future__ import annotations
SyntaxError: future feature annotations is not defined
```

And **`setup_salloc_env.sh` is itself what activates the conda env that provides a modern Python**, so
no Python checker can precede it. The ruling anticipated this branch — *"use a minimal bootstrap
checker"* — and the checker used is **pure git** (`rev-parse HEAD:<f>` vs `hash-object <f>`; git is
2.51.0 pre-conda), which **removes** the toolchain dependency rather than relocating it.

## THE TRANSITIVE ENVIRONMENT TRUST BOUNDARY — Joseph's instruction, and it is a GATE-1 BLOCKER

> "Do not call Gate 1 closed until the transitive environment trust boundary is explicitly settled and
> a fresh non-builder passes it."

**`setup_salloc_env.sh` is 24 committed lines that source two files which are NOT tracked by git:**

```
18: source "${SCRIPT_DIR}/unbinned_unfolding/build/setup.sh"
21: source "${SCRIPT_DIR}/MINERvA101/opt/bin/setup.sh"
$ git ls-files -- unbinned_unfolding/build/setup.sh MINERvA101/opt/bin/setup.sh   -> (empty)
```

They are build-tree artifacts, and they are **what activates conda and sets up ROOT/MINERvA101** — the
executing environment. **A git-based check cannot bind them, structurally.** `PR-02` therefore moves
the boundary one hop and does not close it. `lib/resume_guard.sh` sources nothing (311 lines) and **is**
fully bound.

**Standing consequence:** `F-2(a)` may be recorded as *repaired in its first hop*, never as *closed*,
until this is settled and a **fresh non-builder** passes it. The disclosure is pinned by a test in all
eight launchers, plus a second arm that re-checks the two scripts really are untracked, so a future
`git add` fails the test rather than leaving a stale slogan in eight files.
