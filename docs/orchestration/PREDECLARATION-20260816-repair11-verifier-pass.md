# PREDECLARATION — the repair-11 standard-P4 verifier pass

**Written 2026-08-16, BEFORE `N3` lands and before any repair is reviewed.** Author: the lane that
issued repair-10 (`758f069`), acting as `standard-p4-verifier`. **No verdict is issued here and no
token is set.**

**Why this exists as a committed document rather than a message.** `BEN-361` records that a
predeclared *limitation* is the least-checked claim in a predeclaration. A predeclared **bar** is its
paired object, and it is worth less the moment it can be reconstructed after seeing the repair. So it
is timestamped, in the tree, before the thing it judges exists.

---

## 1. The execution surface, recorded

Derived as the gate computes it — `p4_lib.standard_p4_execution_surface()`, the union repair-9 built
from the import graph plus the scripts the shell drivers invoke. **20 paths at HEAD:**

```
2d-unfolding/unfold_2d_omnifold_unbinned.py     nd-unfolding/p4_lib.py
2d-unfolding/uq/hadd_universes_full.py          nd-unfolding/p4_project_4d.py
nd-unfolding/flux_universe.py                   nd-unfolding/p4_validate_active_lateral.py
nd-unfolding/omnifold_nn_core.py                nd-unfolding/project_cov_nd.py
nd-unfolding/p3s_manifest_summary.py            nd-unfolding/run_p4_merge_audit_std.sh
nd-unfolding/p4_build_components.py             nd-unfolding/run_p4_standard.sh
nd-unfolding/p4_check_receipt.py                nd-unfolding/run_p4_unfold_std.sh
nd-unfolding/p4_check_verifier_token.py         nd-unfolding/unfold_nd_omnifold_unbinned.py
nd-unfolding/p4_evidence.py                     nd-unfolding/uq_math.py
                                                nd-unfolding/xsec_nd.py
                                                unbinned_unfolding/python/omnifold.py
```

**UNCHANGED since repair-10's `code_rev 0e83b54`** — derived independently in a throwaway worktree at
that commit and in the main checkout, both 20 paths, byte-identical lists. *The comparison was
performed twice: the first attempt ran both derivations inside the worktree and compared the old
surface with itself, and the second produced an empty file from a wrong cwd. Both were caught by
checking the two outputs' shas and by requiring the diff to detect an injected line before believing
its silence. Recorded because a self-comparison that reports "identical" is exactly `BEN-344`'s
shape, and it happened here minutes after accepting `BEN-344`.*

`p4_adopt_standard.py` remains **off** the surface — correct for an *execution* surface (it is
unwired; grep finds it only in comments) and noted in repair-10 as converging with `OI-128`.

## 2. `code_rev` discipline

* **A literal 40-hex `git rev-parse HEAD` of the reviewed tree.** Never `HEAD`, `main`, `HEAD~n`, a
  ref name, or an abbreviation — repair-9 measured all of those passing 4a/4b **vacuously**, and
  repair-10 re-measured 13 such values reaching `code_rev_in_history=False`. A verdict of mine that
  broke this rule would be rejected by the gate it certifies, which is the sharpest available test
  that the rule works, and repair-10 self-tested against it.
* **Rule 4c requires the working tree clean on every in-scope path**, not merely the commit. This is a
  shared checkout and other lanes commit into it hourly, so the pass will:
  1. record `git status --short -- <surface>` immediately before reading anything;
  2. re-check it immediately before stamping, and **re-derive, not re-run** — a check repeated after
    a rebase re-runs the check without re-deriving its numbers (`BEN-228`);
  3. **if 4c fires on another lane's uncommitted work, STOP and report.** Not stash, not revert, not
    commit. That is coordination, not a defect, and it is not the verifier's to clear.
* **HEAD moving mid-review is expected, not exceptional** — it happened to repair-8 and to repair-10.
  The response is to measure the drift over the surface and stamp the tree actually reviewed, never
  to re-run from scratch.

## 3. THE BAR — what returns PASS

`authorizes_covariance_stages_4_6: true` **iff all four hold:**

**B1. Every defect bearing on projection validity is closed, and closed by measurement.** At
repair-10 that is **`N3` alone** — `check_projection_validity`'s second leg must compute `C_low` by a
route that does **not** reuse `M @ C_high`. **Not sufficient: that the code changed.** Required: a
test that FAILS on the pre-fix form and on a *wrong `M`*, which the current form cannot detect. If A's
repair lands without such a test, that is a BLOCK and the repair is not the question.

**B2. The self-guard items do not gate this bar, and the verdict must say so explicitly.**
`self_guards_adequate` may remain `NO` on `#7`/`#8` while stages 4–6 are authorized. Repair-10 already
declined to conflate them; this restates it in advance so it is not read as a concession made after
seeing the count.

**B3. The suite is executable and its baseline is unchanged except by the repair.** TMPDIR established
**by writing**, never by reading an env var (repair-7 verdicted on a read-only-tmpdir suite: `120
failed, 57 errors`). Baseline of record: **`3 failed, 1410 passed, 1 skipped`** at repair-10. Any new
failure is a BLOCK until attributed.

**B4. Rules 4a/4b/4c pass over the 20-path surface at the stamped `code_rev`,** verified by running
them, and the receipt self-tests against them.

**Anything else outstanding — `#7`, `#8`, `#9`, `N4`, `N6`, the sweep snapshot — does not gate B1–B4.**
None bears on whether the projection is valid. **This is the whole bar. If I return PASS on a
different basis, this document is the falsifier.**

## 4. Evidence standard, adopted in advance

Lane B audited repair-10's *evidence* rather than its defects and found one citation vacuous
(`#8`) and one measuring the wrong property (`#7`). **Both accepted — see §5.** From repair-11:

> **Every defect must cite a measurement with a reachable other outcome, and the receipt must state
> what that other outcome would have been.**

Operationally, each defect row carries a `falsified_by` field: the observation that would have shown
the defect absent. **A row whose `falsified_by` cannot be written is not a defect row; it is a
suspicion**, and will be reported as one. This is the generalisation of `P-USED` from `OI-124`'s own
guard — *an absence-based check that also passes when the thing is absent proves nothing* — applied to
the verdict format rather than to a probe.

**AMENDED 2026-08-16, still before `N3` lands and before any repair is reviewed, on lane B's stress
test of this field against its own `#7`** (`d2c01ed`). B observed that `#7`'s `falsified_by` would
naturally be written *"a commit to `test_p4_guard_mutations.py` after `c308a9c`"* — falsifiable, and
useless.

**The wording above already rejects that** — it requires an observation showing *the defect* absent,
and `#7`'s defect is **inadequacy**, not untouchedness; a commit existing shows neither. But the near
miss names the field's real failure mode, so it is stated rather than left to be inferred:

> **`falsified_by` must be able to falsify the claim's PREDICATE, not merely some fact about its
> SUBJECT.** A falsifier aimed at the subject is the form that will pass review, because it *is*
> checkable — it simply checks the wrong proposition.

**Applied honestly, this is uncomfortable for `#7` and that is the point**, not a reason to soften it:
under this field, repair-10's `#7` is **a well-evidenced claim about neglect wearing the label of a
claim about inadequacy**. B owns `#7` and is measuring adequacy directly; whichever way that lands,
the label and the evidence must agree in repair-11. The field did not create that mismatch — it made
it visible before the verdict rather than after, which is the whole reason it is predeclared.

## 5. Acceptance of the audit of repair-10

**`#8` — ACCEPTED, my evidence was vacuous.** Verified at my own `code_rev 0e83b54`: `grep -c`
returned `0` for `p4_lib`, `p4_evidence`, `p4_adopt_standard`, `run_p4_standard`, `p4_project_4d` and
`p4_build_components` — **every module, swept or not** — because the snapshot records the sweep's
*output* (`files_with_candidates`, `n_candidates`, `fields`, `gates`) and never its *scope*. No input
could have made that grep non-zero. **The defect may still be real** — repair-7 and repair-8 both
asserted it and B closed it at `86fe270` — **but repair-10 did not establish it.** This is the defect
class this lane retired the `OI-120(c)` `P4` arm for the same morning, reproduced in its own receipt.

**`#7` — ACCEPTED as stated.** *"Unchanged since `c308a9c`"* is true and was correctly derived, but
**unchanged is evidence of neglect, not of inadequacy**; a suite can be untouched and correct. The
adequacy claim rested on the author's self-declaration, which repair-10 cited but did not distinguish
from measurement. **If B's direct examination finds the mutation suite adequate, `#7` should be struck
and the count changes** — and B pre-committing to report that refutation is the right shape.

**Not accepted as systemic**, consistent with B: five of seven were properly evidenced, and `#9` — the
block's own command returning six "Repair-4 defect" commits — is self-refuting on re-execution, which
is the standard §4 now generalises.

## 6. Scope

* No verdict, no token, no `P4_VERIFIER_PASS`, nothing launched, `p4_lib.py` untouched (lane A is
  inside it).
* The bar is stated against the defect list **as of repair-10 plus B's `86fe270`**. If `#7` is struck
  or new defects land, B1–B4 are unchanged in form; only the membership of B1 can move, and only
  toward *more* being required.
* This document does not bind lane A's repair, only how it will be judged.
