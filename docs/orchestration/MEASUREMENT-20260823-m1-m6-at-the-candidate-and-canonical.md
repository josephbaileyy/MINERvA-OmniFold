# M-1…M-6 RE-MEASURED — on the CANDIDATE and on the CANONICAL CHECKOUT, reported separately

**CITABLE FOR:** the state of the six measurements the review contract rests on, taken 2026-08-23 on
two named trees, by a committed instrument whose output is reproducible.

**NOT CITABLE FOR:** a Gate-1 pass. Gate 1 does **not** pass; `F-2(a)` and `F-17(a)` failed at round 6
and this document is part of the `F-17(a)` repair, not a verdict on it.

**Closes the `F-17(a)` filing defect** the round-6 grader identified: the previous filing
(`MEASUREMENT-20260822-m1-m6-at-pinned-sha.md`) dropped `unified_throw_cov.py` — one of the six B-1
files — from M-1, and said *"the three that remain"* where there are four.

## THE TWO TREES ARE DIFFERENT SUBJECTS AND SHARE NO COLUMN

| | path | sha | state |
|---|---|---|---|
| **CANDIDATE** | `/pscratch/sd/j/josephrb/k0r2/clean` | `60cf728d…` (see §5 for the final sha) | `git status --porcelain` empty, A-2(g) applied, 0 writable files |
| **CANONICAL** | `/pscratch/sd/j/josephrb/MINERvA-OmniFold` | `b2d7d4ca24707344cf12f99c0aa51381b81dd445` | 722 dirty = 718 `??` + 4 ` M`; behind `github/main` by 1 |

**Conflating them is the specific error this document was rewritten to stop.** While preparing this
repair the builder measured `unified_throw_cov.py` on **`main`**, found an active hardcoded `_REPO`
feeding a `sys.path.insert(0, …)`, and reported it as *the candidate's* state. That was wrong. Joseph
caught it and re-measured `git show fabeedc2:nd-unfolding/unified_throw_cov.py` directly. On the
candidate that file carries the B-1 repair — `_REPO = str(Path(__file__).resolve().parents[1])` — and
its only absolute canonical literal is `_DATA_ROOT`. The hardcoded `_REPO` is real, and it is on the
**canonical checkout**, where it is one of five. Both statements are true of different trees; only one
of them is true of the thing that executes.

## THE INSTRUMENT

`docs/orchestration/measure_m1_m6.py`. The tree is a **mandatory argument with no default** — every
number here is tree-dependent. It **refuses on CPython < 3.10** rather than degrading: on the
pre-conda 3.6.15 a string literal parses to `ast.Str`, not `ast.Constant`, so the M-1 scan would print
a clean, silent, wrong **zero**. Refusal verified on saul (`rc=1`).

```
source /pscratch/sd/j/josephrb/k0env/setup_salloc_env.sh     # MNV_ENV_ROOT + MNV_CONDA_PREFIX set first
python3 docs/orchestration/measure_m1_m6.py --tree <TREE> --label <WHAT IT IS>
```
Interpreter for every number below: **CPython 3.11.14**, `…/.conda/envs/root_6_28/bin/python3`.

---

## M-1 — root literals and imports after a rooted insert. **TEN ROWS.**

### CANDIDATE

| entrypoint | literal | first insert | repo modules after |
|---|---|---|---|
| `bootstrap_nd.py` | — | :28 | 3 |
| `seedscan_split.py` | — | :37 | 3 |
| **`unified_throw_cov.py`** | **`_DATA_ROOT` @:69** | :61 | 5 |
| `unified_throw_cov_5d.py` | — | :42 | 3 |
| `unfold_nd_omnifold_unbinned.py` | `_DATA_ROOT` @:73 | :77 | 4 |
| `sweep_bank_5d.py` | `_DATA_ROOT` @:59 | :51 | 6 |
| `combine_cov_nd.py` | — | none | 0 |
| `analyze_universes_5d.py` | — | none | 0 |
| `mii_adopt_unified_5d_stamped.py` | — | :149 | 2 |
| `adopt_unified_5d.py` | `_REPO` @:35 | :38 | **0** |

**FOUR surviving absolute canonical literals, not three: three `_DATA_ROOT` and one `_REPO`.**

- The three `_DATA_ROOT` cases are the canonical checkout **in its data role**, which the two-root
  design explicitly permits: *"acceptable in THIS ROLE ONLY. Nothing is executed or imported from it."*
- The one `_REPO` — `adopt_unified_5d.py:35` — is the **inert** case, and inert is a measurement here,
  not an assertion: it feeds the insert at `:38` and the file imports **zero** repository modules
  afterwards. The count is in the table and moves if the file changes.
- `unified_throw_cov.py` is the **tenth row and the one that was missing.** Its literal is at `:69`,
  *after* the insert at `:61`, so it does not feed it — the B-1 repair derives the import root from
  `__file__`. It is a `_DATA_ROOT` case, not a `_REPO` case.

### CANONICAL CHECKOUT

**FIVE surviving literals, all `_REPO`, none `_DATA_ROOT`** — the unrepaired world:
`unified_throw_cov.py:42`, `unified_throw_cov_5d.py:24`, `unfold_nd_omnifold_unbinned.py:47`,
`sweep_bank_5d.py:32`, `adopt_unified_5d.py:35`.

**`unified_throw_cov.py:42` on this tree is the hazardous one and is NOT inert.** `_REPO` at `:42`
feeds `sys.path.insert(0, …)` at `:45`, and **five** repository modules are imported after it
(`flux_universe` :47, `seed_offset_policy` :48, `compare_unified_throw` :49, `uq_math` :50,
`unfold_2d_omnifold_unbinned` :196). That is OI-136's measured mechanism — an absolute `insert(0, …)`
executes *that* tree's modules whichever checkout launched the entrypoint, and `PYTHONPATH` cannot
outrank position 0. **Nothing may be executed or imported from this tree.**

## M-2 — could an insert shadow a non-repository name?

| | importable top-level names | stdlib collisions |
|---|---|---|
| CANDIDATE | 127 | **0** |
| CANONICAL | 125 | **0** |

Zero in both directions on both trees. The 127/125 difference is the candidate's two new
`lib_mnv_env_*` modules' neighbours, not a hazard.

## M-3 — hash-bound files

- **CANDIDATE: `rc=0`, `ALL BINDINGS INTACT`.** Status read directly, never through a pipe.
- **CANONICAL: `rc=1`, `ALL BINDINGS INTACT` is FALSE.** It takes roughly **30 minutes** on that
  tree, which is why an earlier draft of this document recorded it as "did not complete in 26
  minutes." **That draft was wrong, and wrong in the safe-sounding direction** — a slow check reads
  as an inconvenience, whereas the actual answer is that the canonical checkout's hash bindings are
  **not intact**. The correction is recorded here rather than silently applied, because "the
  instrument was still running" and "the instrument returned a failure" are different claims and
  only the second is a finding.

  The itemized list of which bindings break is **not yet captured** — it needs another ~30-minute
  run and is recorded as owed, not as absent. What is established is the verdict, not the inventory.
  **Do not read the candidate's `rc=0` as covering the canonical tree**, and do not read this `rc=1`
  as touching the candidate: nothing is executed or imported from the canonical checkout, so this is
  a finding about the data-role tree, not about what runs.

## M-4 — tree identity

| | HEAD | dirty | behind | ahead |
|---|---|---|---|---|
| CANDIDATE | `60cf728d…` | **0** | 0 | — |
| CANONICAL | `b2d7d4ca…` | **722** = 718 `??` + 4 ` M` | 1 (vs `github/main`) | 0 |

The canonical's dirty count has moved `721 → 722` since 2026-08-22 (one more untracked file); the
`717/4` split is now `718/4`. **The behind-count is a drifting quantity and is never quotable without
its timestamp** — it moves every time `main` moves.

## M-5 — the `.sh` half

| | `REPO=` assignments | activator from `CODE_ROOT` | activator from `ENV_ROOT` |
|---|---|---|---|
| CANDIDATE | **0 of 8** | **0 of 8** | **8 of 8** |
| CANONICAL | **8 of 8** | 0 of 8 | 0 of 8 |

The review contract's *"all eight assign `REPO=…` unconditionally"* is **false on the candidate and
still true on the canonical checkout.** The 2026-08-22 filing reported only the repaired half, which
is what made it stale in the builder's favour; both halves are now stated side by side.

## M-6 — does the guard emit evidence that it looked?

| | file | counts resolutions | inventory write | verdict |
|---|---|---|---|---|
| CANDIDATE | 557 lines | yes | `:369` | **WRITTEN BUT DEFAULTED** — `"checked": (guard.checked if guard is not None else 0)`, so a containment-path zero is a *default*, not a measurement. The vacuity hole is **open**. |
| CANONICAL | 281 lines | yes | **none** | **NO INVENTORY WRITE** — the guard counts and emits nothing. The vacuity question cannot even be asked of this tree. |

**A defect in this document's own instrument was found and fixed while writing it.** `m6`'s first
version tested for the `else 0` substring and returned `vacuity_hole_open: False` for the canonical
tree — reading *"the whole feature is absent"* as *"the hole is closed"*, exactly backwards. A
substring search fails in both directions. It now reports three distinct states and names which one
it found.

---

## THE DIFFERENCES, AS FINDINGS

| # | measurement | difference | direction |
|---|---|---|---|
| 1 | **M-1** | the filing had **nine** rows and said "three"; there are **ten** and **four** | **against the builder** — an entrypoint was missing from the filing entirely |
| 2 | **M-1** | candidate 3 `_DATA_ROOT` + 1 inert `_REPO`; canonical **5 `_REPO`**, one of them active with 5 repo imports after it | the trees disagree; only the candidate executes |
| 3 | **M-3** | candidate `rc=0`; canonical **`rc=1`, bindings NOT intact** | **against the builder** — the previous filing recorded M-3 as simply "UNCHANGED", and an earlier draft of *this* filing recorded the canonical run as merely slow |
| 4 | **M-4** | canonical dirty `721 → 722` | neither; a drifting quantity |
| 5 | **M-5** | candidate `0 of 8`; canonical `8 of 8` | reported both ways this time |
| 6 | **M-6** | canonical has **no inventory write at all**, which the previous instrument would have scored as clean | **against the builder** |

**M-2 is unchanged on both trees.**

## SUITE, ON MATCHED TREES

Both runs are **fresh writable clones from the same bare repo, same host, same interpreter**
(Linux, CPython 3.13.15, pytest 9.1.1). The first attempt compared the *read-only deployed* candidate
against a *writable* baseline clone and produced 39-vs-13 — a difference in tree protection, not in
the change. That comparison was discarded rather than reported.

| tree | result |
|---|---|
| candidate `e93364d1` | **13 failed, 2531 passed, 17 skipped, 643 subtests passed** |
| baseline `fabeedc2` | **13 failed, 2521 passed, 17 skipped, 581 subtests passed** |

**Failure sets identical — zero regressions and zero accidental fixes** (`comm` both directions
empty). The `+10 passed` are the new parity arms; the `+62 subtests` are their per-launcher and
per-library loops. The 13 are pre-existing at `fabeedc2` and are not touched by this change.

## EXPIRY

Every number above is falsified by a commit to either tree. **Re-run the instrument; do not inherit a
number from this table.** `M-4`'s behind-count is falsified by any push to `main`, and `M-2` rests on
718 untracked files in a tree nobody controls.
