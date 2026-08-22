# Orchestration router

This is a pointer-only active-tree router. It contains no scientific evidence or authorization.

## Current work

- Live snapshot: [`LIVE-STATE.md`](LIVE-STATE.md); run its freshness check before use.
- Bounded queue: [`../CURRENT_WORK.md`](../CURRENT_WORK.md); sources live in
  [`control-plane/`](control-plane/).
- Queue overflow: [`../CURRENT_WORK_OVERFLOW.md`](../CURRENT_WORK_OVERFLOW.md).
- Unpromoted active records: [`../CURRENT_WORK_BACKLOG.md`](../CURRENT_WORK_BACKLOG.md).
- Active process rules: [`PLAYBOOK.md`](PLAYBOOK.md).
- Open/deferred source records: [`../OPEN_ITEMS.md`](../OPEN_ITEMS.md).
- Joseph-only decisions: [`USER-DECISIONS.md`](USER-DECISIONS.md).

## Evidence and claims

- Verified numbers: [`../../VALIDATION_LEDGER.md`](../../VALIDATION_LEDGER.md).
- Physics claims: [`CLAIMS.md`](CLAIMS.md).
- Active BEN identifiers: [`FINDINGS.md`](FINDINGS.md); full evidence is at the frozen tag.
- Bugs and traps: [`../../KNOWN_ISSUES.md`](../../KNOWN_ISSUES.md).
- Retracted values: [`INDEX-retracted-and-superseded-values.md`](INDEX-retracted-and-superseded-values.md).
- Why the B1 pause's clause (c) cannot be met through the launcher:
  [`FINDING-20260822-clause-c-adopt-is-unreachable-under-its-own-pause.md`](FINDING-20260822-clause-c-adopt-is-unreachable-under-its-own-pause.md)
  — measured: `sbatch_finalize_5d_bkgaware_gpu.sh:347/:352` is unreachable in both regimes, so the
  condition is circular as written and the disposition is a forced choice, not a judgement call.

### Documents that open items route to but this router did not list

Added 2026-08-20. `live_doc_indexed.py --check` reports **19 LIVE docs absent from this
catalog and does NOT enforce it**, so an item's own governing document could be
unreachable from the router. These five are the subset that `docs/OPEN_ITEMS.md` rows
actually cite; the other fourteen are not routed to by any open item and are left out
deliberately, because this file is a pointer-only router and not an exhaustive index.

- [`PROVENANCE-DEBT-20260810-standard-p4.md`](PROVENANCE-DEBT-20260810-standard-p4.md) — **`OI-7`'s
  own blocker**: its §3e is the sentence that row is open on. Cited 4× in `OPEN_ITEMS.md` and
  reachable from no router until now.
- [`SPEC-20260814-gate5-cstat-construction-v1.md`](SPEC-20260814-gate5-cstat-construction-v1.md) —
  the ruled `C_stat` construction spec; cited 6×, including by `OI-93`, whose row is stale against
  it.
- [`RANK-AND-INVERSION-20260810.md`](RANK-AND-INVERSION-20260810.md) — the rank and pseudo-inverse
  measurements behind the N-D χ² protocol; routed to by `OI-137`.
- [`RECONCILIATION-20260817-gbdtfive-macros-vs-rebuilt-candidate.md`](RECONCILIATION-20260817-gbdtfive-macros-vs-rebuilt-candidate.md)
  — traces the `\gbdtFive*` note macros to their artifacts; one of them had been destroyed.
- [`DETERMINATION-20260811-cause5-binding-half.md`](DETERMINATION-20260811-cause5-binding-half.md),
  [`CONVENTION-verifying-a-check-is-deployed.md`](CONVENTION-verifying-a-check-is-deployed.md) —
  each cited once.

## Task routes

| Task | Route |
|---|---|
| Change code | `KNOWN_ISSUES.md`, relevant status/reference, callers, tests, and hash bindings |
| Quote a result | `VALIDATION_LEDGER.md`, then the exact product or live receipt |
| Run or monitor compute | fresh `LIVE-STATE.md`, direct scheduler observation, then the exact launcher receipt |
| Work on 2D/3D/N-D/PET | relevant workstream status; PET also `PET_UQ_REMEDIATION_STATUS.md` |
| Maintain queue/playbook | [`control-plane/policy.json`](control-plane/policy.json), [`control-plane/source-record-inventory.tsv`](control-plane/source-record-inventory.tsv), then `control_plane_lint.py` |
| Maintain classifications | `MANIFEST-overrides.tsv`, then `generate_manifest.py` |
| Operate continuation | `WAKER.md`, `wakerctl.py`, `waker-config.json`, and `profiles.json` |
| Build deliverables | `docs/analysis-note/build_all.sh` for note, primer, and paper |

## Frozen pre-compaction evidence

Complete history, terminal receipts, long-form findings, audits, determinations, prompts, and old paths
live at:

`evidence/prepublication-2026-08-20-0b329e8a`

Recover a known path without changing the current checkout:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:<old-path>
```

Search the complete frozen tree:

```bash
git grep '<identifier>' evidence/prepublication-2026-08-20-0b329e8a --
```

The independently stored bundle and recovery proof are recorded in
[`../POST_PUBLICATION_REORG_PLAN.md`](../POST_PUBLICATION_REORG_PLAN.md).

### Anchored-but-unreachable commits — `git fetch github` will NEVER bring these down

Several commits cited in the record are reachable from **no branch**; that is exactly why they were
anchored by `evidence/*` tags. **Git only auto-follows tags that point at objects it is already
downloading**, and `remote.github.fetch` is branches-only
(`+refs/heads/*:refs/remotes/github/*`) with `remote.github.tagOpt` unset — so a tag on a commit
unreachable from `refs/heads/*` can never arrive from an ordinary fetch. **Measured 2026-08-20: six
of the ten `evidence/*` tags on the remote were absent from the main checkout, and `git cat-file -t`
failed outright on all six anchored commits — including `ecee9ff1`, the one carrying
`array_equal True across all 114,361,636 elements`.** Preservation had succeeded; discovery had not,
and a session here would reasonably have concluded the evidence was lost.

Fetch them explicitly — once per checkout:

```bash
git fetch github 'refs/tags/evidence/*:refs/tags/evidence/*'
```

Or make an ordinary `git fetch github` do it permanently, per checkout:

```bash
git config --add remote.github.fetch '+refs/tags/evidence/*:refs/tags/evidence/*'
```

**THE REMOTE NAME IS CHECKOUT-LOCAL — do not hardcode it, and do not trust either name from this
file.** This paragraph read *"The remote is `github`. There is no remote named `origin` —
`git rev-parse origin/main` is fatal"* until 2026-08-21. That is true on the Perlmutter checkout and
**exactly inverted in the local clone**, where `git remote -v` lists only `origin`,
`git rev-parse origin/main` resolves, and `git rev-parse github/main` is the fatal one. A witness
phrased against *either* name is unfollowable in the other tree. Resolve it first and substitute:

```bash
# NAME the remote. Do NOT use `git remote | head -1`.
git remote -v                       # look, then substitute the right name below
git fetch github 'refs/tags/evidence/*:refs/tags/evidence/*'   # on Perlmutter
git fetch origin 'refs/tags/evidence/*:refs/tags/evidence/*'   # in the local clone
```

**`git remote | head -1` IS ITSELF A DEFINITE DESCRIPTION AND IT IS WRONG HERE.** This file recommended
it until 2026-08-21, and it failed the same day it was written: the Perlmutter checkout has TWO
remotes, `analysis-note` and `github`, and `head -1` returns **`analysis-note`** on alphabetical
order. Every downstream number was then computed against the wrong repository -- it reported the
checkout as *"9 behind"* only once the remote was named, having first reported *"behind 94, ahead
2069"*, which was a true measurement of the distance to the ANALYSIS-NOTE repo and meaningless as an
answer to the question asked. **A command that silently answers about a different subject is the
failure mode this campaign keeps paying for; substituting one guess for another is not a fix.**

**The generalisation, and it has now cost this campaign four separate errors:** a remote name, an
interpreter version, a hook's liveness and a file's dirtiness are **properties of a checkout, not of
`main`**. `HANDOFF-20260820-2154Z-publication-closeout.md` §2.1 (a dirty `state/sessions.json` at
51,542 B blocking `MANIFEST.tsv`), §2.2 (`build_all.sh` cannot exit 0) and §2.12 (the pre-commit hook
is inert, 7 of 12 checks `SyntaxError`) are all `login19` facts. Measured in the local clone at
`80eeb441`: `sessions.json` is **clean at its committed 46,746 B**, `core.hooksPath` **is** set, and
the hook reports **12 checks passed** under python 3.12.2. Re-measure with an explicit `-C <path>`
and say which tree you are in.

**Test reachability with `git for-each-ref --contains <sha>`, never `git branch -a --contains`,**
which cannot see tags and will declare an anchored commit disposable.

### The four removed artifacts with no routed citation

`84607aa3` removed 734 tracked files, all under `docs/orchestration`. Most are covered by the generic
route above. **These four were cited by nothing live**, so a reader had no way to learn they exist;
`HANDOFF-20260820-2154Z-publication-closeout.md` §2.11 identified them. They are **recoverable, and
were never lost** — this section is the missing *route*, not a recovery. Restoring the paths into the
live tree is a separate freeze-scope question and is **not** what this section does.

All four resolve at `evidence/prepublication-2026-08-20-0b329e8a`, verified 2026-08-21:

| artifact (under `docs/orchestration/`) | why it matters |
|---|---|
| `runs/standard-p4-verifier/20260811T132822Z-packetB-final-pass.md` | `OI-7`'s PB3/PB4 evidence |
| `runs/standard-p4-verifier/20260817T045149Z-repair12-verdict.json` | supersedes repair-11, which *is* on `main` |
| `AUDIT-20260819-analysis-note-vs-record.md` (1,375 lines) | the only prior enumeration of the 70; bears on `OI-130`, which is 22% enumerated |
| `state/hpss-residency-inventory-20260812.json` | preservation state behind `OI-131` |

```bash
git fetch github 'refs/tags/evidence/*:refs/tags/evidence/*'   # `origin` in the local clone; NAME it
git show evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/<path-above>
```

**Note the self-contamination, because it recurs in this campaign:** before this section existed, the
`AUDIT` file's *only* live citation was the document reporting that it had none. A write moves the
population it measures — so "cited nowhere" needs a timestamp and a tree, like any other measurement.

**Resolve citations by SHA, not by path.** A path can resolve at HEAD and read a *different* file
with no error. Measured: `nd-unfolding/mii_anchor_comparator.py` is blob `a7cb2d9b…` at both
`ecee9ff1` and `f7ab02ff`, and `cbeac61d…` at HEAD.

## Regenerate

```bash
python3 docs/orchestration/control_plane_lint.py
python3 docs/orchestration/generate_manifest.py
python3 docs/orchestration/generate_manifest.py --check
```
