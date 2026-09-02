# DECISION 2026-09-02 — Joseph rules `OI-173`: cause 4's `M` referent is the STAMPED CANDIDATE

**CITABLE FOR:** the ruling in §2, and the consequence in §5 **as a routed consequence, not as an
applied grade**.
**NOT CITABLE FOR** grading cause 4's `M` cell, discharging cause 4 or any cause, adopting any
covariance, moving any gate, changing the quarantine counts, or altering `values.tex`. Gate 2 remains
**FAIL**. Counts hold at CAND `1 of 7`, QUOTED `0 of 7`. **The `M` cell stays `OPEN` and this lane does
not move it — see §6.**

## 1. Authority, and the full sequence, because a superseded authorization is part of the record

Joseph, 2026-09-02, in his own turn, directly to this lane — **not relayed, not inferred**:

> *"okay do c"*

**He had authorized a DIFFERENT branch first, and that matters.** Earlier in the same session he
answered *"Can you do (a)?"*. This lane began implementing `(a)`, then halted before filing when the
`5d` lane objected that `(a)` names the wrong object. `docs/OPEN_ITEMS.md` was reverted and the draft
was parked outside the tree, so **nothing under `(a)` was ever committed**. The `(a)` authorization is
recorded here rather than omitted: he gave it, this lane accepted it, and it was superseded by his own
later ruling once the third object was on the table. A reader who finds `(a)` in the transcript should
find its disposal here.

## 2. THE RULING

`(c)` was put to him in the `5d` lane's words, and is reproduced verbatim rather than summarised:

> **`M` is specified against the reported ratio of the STAMPED CANDIDATE.**

## 3. Why `(a)` was wrong: there are three objects, and the choice offered him had two

1. **The 2026-07-01 occupant** of `uq_5d/unified_throw_cov_5d.root` — overwritten 2026-07-13, no longer
   exists. **`1.539` describes this**, which is what `FINDING-20260901-cause4-jitter-floor-recovered.md`
   established and what made a re-issue necessary at all.
2. **X, the adopted July artifact** — raw ratio `1.3107364286763725` from its own committed operands
   (VL44, `VALIDATION_LEDGER.md:488`). **`(a)` aimed here.**
3. **`stamped_bkgaware_meancentered_20260812.root`** — sha256 `4f168e83…`, job `56720356`. **The graded
   subject**, per `DECISION-20260831-joseph-quarantine-graded-against-the-candidate.md` §1, verbatim:
   *"The seven quarantine causes are graded against `stamped_bkgaware_meancentered_20260812.root` …
   NOT against the adopted July artifact X."* — a ruling he confirmed directly with *"yes its my
   ruling"*.

**This is two correct rulings composing into a defect.** The 2026-08-31 ruling fixes the *subject*;
Ruling 2 of 2026-09-01 fixes the *referent class*. Neither is wrong in its own scope, and the pair
leaves `M` pointed at an object the framework does not grade. Naming the composition is the point of
this record; the error in offering him a two-object choice was this lane's.

## 4. The supporting analysis is the `5d` lane's, and is adopted rather than rewritten

`PROPOSAL-20260902-oi173-reissue-cause4-M-referent.md` is filed alongside this decision **unchanged and
under its own lane's authorship.** It reached the third-object problem independently and first. Writing
a competing record would have cost the campaign the drafting history it carries, which is the more
useful artifact: §3a retracts that lane's stamp-based argument on this lane's counterexample, §3b
restores the conclusion on this lane's flux-fix route with that lane's same-file strengthening, and its
chain paragraph retracts a universal on this lane's near-miss. **Three corrections across two lanes,
each retracted in place rather than deleted.**

**The one measurement this lane contributes, re-verified by `5d` independently:**

- `git log --all -S "jitter floor" -- nd-unfolding/unified_throw_cov.py` returns **exactly two**
  commits — `a0cdc019` (2026-06-08) introduces the print, `07c18aee` (2026-07-14) removes it. It never
  returns on any ref; `grep -c` at HEAD is `0`. Two hits are the search's own positive control.
- The candidate's unified-throw **input** is `unified_throw_cov_5d_fluxfix_20260806_full160.root`
  (sha256 `4cb02ae7…`), named in `STAMPED_HASH_RECEIPT.slurm-56720356.json` and restated at
  `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md:365-369`.
- `081ae4ac` (2026-07-31, the J28 flux fix) modifies **`unified_throw_cov.py` itself** — 81 insertions
  across `_flux_universe`, `do_throws`, `do_blockunits`, `do_combine` — and
  `git show 081ae4ac:nd-unfolding/unified_throw_cov.py | grep -c "jitter floor"` is `0`.
  `git merge-base --is-ancestor 07c18aee 081ae4ac` returns **true**.

**So the exclusion holds inside a single file: no committed revision of `unified_throw_cov.py` contains
both the jitter print and the flux fix.** A tree old enough to print the jitter floor cannot produce
the candidate's input. This replaces the stamp-based argument, which was **refuted** — `git log -S`
dates the oldest *commit*, not the oldest *existence*, and `VALIDATION_LEDGER.md:484` records
`fixed_seed_null_norm` present on a ROOT written 36.5 h before that key was committed.

**Two residual limits, kept:** `--all` scopes to committed refs, and the 2026-07-13 case proves
uncommitted trees are run here; and the adopt step **does** print and persist a sqrt-trace ratio
(`adopt_unified_5d.py:158-160`, `:177-178`) — a different quantity, adopted-combined across inflation
rather than unified against block-sum, with no `jit_trace` in its path.

## 5. THE CONSEQUENCE THAT FOLLOWS, STATED AS A CHAIN RATHER THAN ASSERTED

Neither step is new; both are his.

1. **Ruling 2, 2026-09-01, retained in force:** *"if the printed `jit_trace` is not recoverable from
   committed bytes, `M` is `NOT MET` — unmeasured — rather than `N/A`."* The `N/A`-on-the-merits
   shortcut stays **explicitly REFUSED**.
2. **This ruling:** the subject is the stamped candidate.
3. **§4:** no committed revision could have printed a unified/block ratio for that subject.

**⇒ `M` for cause 4 against the candidate is `NOT MET (unmeasured)`, and §4's mutual exclusion means it
is unmeasurable for this subject rather than awaiting work.**

**AND THIS IS NOT THE SHORTCUT HE REFUSED.** His refusal targeted *"the subtraction never touched X, so
cause 4 is `N/A` for X on the merits"* — an argument whose premise was a claim about how the artifact
was **built**, which is what made it circular. This is a dated fact about which code revisions can
produce an artifact class, and it lands on `NOT MET (unmeasured)`, the branch his own ruling
**prescribed** for the unrecoverable case, rather than on a discharge. The distinction is real; it is
also convenient, and under his own rule — *do not let measurability choose the specification* — the
convenience is a reason for suspicion rather than comfort. **Recorded so he can weigh it, not banked.**

**A COVERING LOG SWEEP MUST NOT BE LAUNCHED FOR THIS.** It would be the weaker foundation —
`FINDING-20260901-pscratch-read-stalls-block-a2b.md` §6, *"an empty result from a sweep is not a
negative result"* — and Perlmutter's scratch is degraded, so its silence would be indistinguishable
from a null. The five sweeps attempted 2026-09-01 returned no data at all; they were terminated by the
CLI harness, which is a fact about this workstation and carries no information about the filesystem.

## 6. THE GRADE IS ROUTED, NOT TAKEN

**This lane measured §4, so this lane does not grade the cell.** That is `BEN-381`'s convention,
recorded at `VALIDATION_LEDGER.md:753` and already applied to this very row — `OI-173`'s owner field
reads *"filed 2026-08-30 by the stale blocker sweep lane, which measured it and therefore does not
grade it (`BEN-381`)"*. The row's owner is **Joseph / the delegated authority**, and it stays there.

So: `M` is now **SPECIFIED against the right object**, the consequence in §5 is **derived and routed**,
and the cell change itself needs one more act by him or by a lane he delegates. **A reader must not
treat §5 as an applied grade.** Also unapplied, and deliberately: the alternative reading in
`PROPOSAL-20260902…` §5 Reading B — that `M` is a property of the *defect* rather than of an artifact,
under which `M` is MET at `1.541 → 1.539`, −0.11% — which this lane could not refute and which his
choice of `(c)` narrows but does not formally dispose of.

## 7. What this decision does not do

It discharges nothing. Cause 4 does not close. No covariance is adopted, no gate moves, `values.tex` is
untouched, the CAND/QUOTED counts are unchanged, and `DECISION-20260831` is not re-opened. It does not
depend on the k=0 redeploy or on `FREEZE-20260830-k0-deployment-7ac0edec.md`, and it is not blocked by
the scratch outage.

**ONE FLAG IT RAISES AND DOES NOT SETTLE:** `DECISION-20260831` §2(b) reaches *"no stamp for X can ever
be produced … permanent for X"* through the same `git log -S` step refuted in §4. Its **substance
survives** on VL3–VL8, where the propagated `*_checked` / `upstream_*` keys are a different key family
from VL40's raw stamp — but its **stated mechanism does not**. Cite that conclusion, not its
36.5-hour reason. Neither lane has swept for other consumers of that step, and it sits inside a ruling
he confirmed directly, so it is surfaced here rather than filed.
