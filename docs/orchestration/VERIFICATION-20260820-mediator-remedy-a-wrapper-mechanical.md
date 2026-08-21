# 2026-08-20 — MECHANICAL verification of remedy (A)'s wrapper. **THIS IS NOT C's VERIFICATION.**

**Read this heading literally.** `HANDOFF-20260819-lane-b-member-axis.md:64` makes B1 steps 4-5's expiry
**"remedy (A) VERIFIED BY C, not merely landed"**. This document records that the wrapper LANDED and that its
mechanical claims were checked **by a party that did not build it** (the mediator). It is **not** C's
verification, it does **not** expire the B1 pause, and it does **not** license releasing the 41.44 GB
intermediate. `BEN-485`(b)'s composition stands exactly as filed.

## What landed

`nd-unfolding/mii_adopt_unified_5d_stamped.py` (lane B, `e94ef110` + `11ab9f82` on `main`, cherry-picked from
`worktree-agent-a26a858ce260f3238`), implementing the wrapper of
`RULING-20260820-lanec-stamp-coverage-is-a-file-claim-the-class-table-is-an-artifact-claim.md` and
`DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md` §25: `adopt_unified_5d.py` invoked as a
**subprocess**, its output reopened `UPDATE`, 7 keys written and **read back**.

## Checked by the mediator, each with its expected value named BEFORE the run

| check | predicted | measured |
|---|---|---|
| pinned files in the diff | none | **none** — `adopt_unified_5d.py`, `fullevent_fps_dataloader.py`, `train_fullevent_nominal.py` all absent from `git diff --name-only` |
| `docs/orchestration/verify_hash_bindings.py` | intact | **`ALL BINDINGS INTACT`**, exit 0 |
| `tests/test_remedy_a_adopt_wrapper.py` | pass | **34 passed** |
| `tests/test_uq_remediation.py` | pass | **233 passed, 2 skipped** |
| full `nd-unfolding/tests` failure SET | unchanged | **identical by name**; `diff` of the sorted `FAILED` lists is EMPTY |
| full-suite counts | more tests, same failures | baseline `8602a694`: **5 failed / 1879 passed**; with B: **5 failed / 1914 passed** (**+35**, 0 regressions) |
| any failure in B's files | none | **none** |

**The comparison was made symmetric on purpose.** Lane B reported `7 failed / 1878` vs `7 failed / 1911`; the
mediator measured 5. **That is the invocation, not a regression** — B ran with random test ordering (and itself
flagged one failure as session-order-dependent), the mediator ran `-p no:randomly` on **both** sides from a
detached worktree at `8602a694`. Comparing B's 7 against the mediator's 5 would have been exactly the
asymmetric comparison this campaign keeps filing; the two sides here differ in nothing but the commit.

## WHAT IS NOT ESTABLISHED, and it is most of the ROOT behaviour

`import ROOT` → `ModuleNotFoundError` on this host, so **`_read_scalars`, `_read_diagonal`, `_stamp_output`, and
`main` from the child launch onward have never executed.** The subprocess has never been launched: its argv is
proved, its behaviour is not. **No ROOT test double was built, deliberately** — a stub that cannot do what ROOT
does is evidence about the stub. B marked this in four places (module docstring, a banner over the ROOT
section, each function's docstring, and `ROOT WRITE PATH CLUSTER-UNVERIFIED as of 2026-08-20` in the
`STAMP_COVERAGE` row) **with a test asserting the markers are present**, because the likeliest damage is a
later reader taking a green suite as evidence that the writes work. Per the ruling's §5(d) this does **not**
bar the table row: `stamps` is a capability claim, and the four existing `True` rows include two that landed
source-only and unexecuted at `5afb7947`.

## Four places lane B contradicted its own specification, all of which the mediator asked it to report

- **(a) The line number was inverted in the brief.** The preserved patch's `:128` for `diag_comb` is RIGHT; the
  README's `:135` is WRONG. Confirmed independently: `adopt_unified_5d.py:128`. Now pinned by a test.
- **(b) §11g's justification does NOT survive the move to a wrapper, and the mediator's brief repeated it.**
  *"a WRITE, not a computation, and NOT an extra read of the 41 GB file"* is true of the in-file edit and
  **false** of the wrapper: the child has exited and `diag_comb` is gone, so the combined intermediate **must be
  re-read** (one 10694² TH2D, ~0.915 GB resident — not 41 GB, but a real extra read). B charged it rather than
  hiding it, and the re-read opens a TOCTOU window the in-file edit did not have, closed by requiring the
  re-read trace to reproduce the `sqrt_tr_old` the child stamped from *its* read.
- **(c) The patch's second refusal is ASYMMETRIC** — it compares only the combined leg's offset against the
  process, so with the combined leg unstamped and the throw leg carrying another member's offset it never
  fires. Both legs are checked now, and the mutation reverting to the spec's form is caught.
- **(d) The gate would have RED-ED on the wrapper's first real product**, exactly as the ruling's §8(3)
  predicted: `upstream_estimator_seed_g1/_g2` (+ `_checked`, + `hDiagCombinedOld`) were in **no**
  `ARCHIVE_KEY_MAP` row and **no** test. Five rows added. Also corrected: `RECOMPUTABILITY["sqrt_tr_old"]`'s
  stated size **0.527 MB was the 65,856 GRID**, not the 10,694 `cv>0` support — 0.0856 MB. *A grid is not an
  artifact size, and that is the second time this campaign that a number was quoted against the wrong support.*

## B's own instrument bug, recorded rather than quietly fixed (`11ab9f82`)

`assertNotIn("ROOT", sys.modules)` measured the **whole pytest session**, not the module: it passed on the file
alone and failed in the full run because a sibling suite installs a ROOT stub. Replaced with a fresh
interpreter. **Same family as `BEN-474`** — an instrument's conditions are part of the measurement.

## Deliberately NOT done, and flagged

- `RECOMPUTABILITY["sqrt_tr_old"]` stays `NOT_RECOMPUTABLE/WRITER_GAP` (reason text corrected only). The flip to
  `IN_FILE` is coupled twice — a `RECOMPUTE` implementation is required for any `IN_FILE` key, and the flip
  shrinks `declared_unrecomputable()`, which every `--acknowledge-unrecomputable` call site must equal exactly.
  **No product carries `hDiagCombinedOld` yet**, so the flip would be a claim about an artifact that does not exist.
- `adopt_unified_5d.py:35` hardcodes `_REPO = "/pscratch/..."` and prepends it to `sys.path`, so a child launched
  from any other tree still imports from pscratch **if it exists**. Receipt-bound, untouched, flagged only —
  and it is the *"a hardcoded `${REPO}` means the tree you read is not the tree that runs"* trap again.

## What remains, in order

1. **Lane C verifies remedy (A).** Not the mediator, not lane B. Only that expires B1 steps 4-5.
2. The ROOT write path executes for the first time **on the cluster**, which is down.
3. Only then does the 41.44 GB question become live, and `BEN-485`(b) still governs the ordering.
