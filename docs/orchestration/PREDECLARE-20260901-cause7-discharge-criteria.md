# PREDECLARATION 2026-09-01 — quarantine cause 7 discharge criteria

**Status: DRAFT CRITERIA ONLY. Every leg below is OPEN.** This document grades no leg, discharges no
cause, adopts no artifact, changes no quarantine count, and moves no gate. The 2026-09-01 authorizing
turn — *"I authorize you spend the hours and drafting to investigate and fix the causes"* — authorizes
this drafting only. It does not authorize construction, compute, grading, discharge, adoption, or a
change to the publication state. Those decisions remain outside this document.

The vocabulary and the four-leg rule come from
`CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md` §0: discharge is a property of a
**(cause × artifact)** pair; all of **C** (code), **P** (provenance), **M** (magnitude), and **T**
(test) must hold; and any leg that does not hold leaves the cause OPEN. In particular, **M is “the leg
everyone skips” and “the one that makes discharge falsifiable.”** This file adds criteria that the
earlier document did not contain. It does not apply them.

## 0. Artifact scope — four names, no substitution

Joseph's 2026-08-31 ruling fixes the grading subject as:

> **G = `nd-unfolding/uq_5d/readopt_20260811_footing/`**
> **`stamped_bkgaware_meancentered_20260812.root`**, sha256
> `4f168e83eaeb4bc7191a4e13e219c7ff06556e5ad30b9df4fcc249e6720c7ec2`, job `56720356`,
> 10,694 reported bins on the 65,856-bin scalar-5D grid.

That is the subject of **every C/P/M/T criterion below**. The other objects are named to make an
accidental scope transfer visible:

| name | artifact | relation to these criteria |
|---|---|---|
| **G** | `stamped_bkgaware_meancentered_20260812.root` (`4f168e83…`) | The ruled `(cause 7 × artifact)` subject. |
| **J** | the July `uq_universe_5d_covariance_combined_bkgaware_uthrow{,_cvcentered}.root` pair quoted by `values.tex` | Retained historical/quoted object; **not** the grading subject under `DECISION-20260831` and cannot supply a leg for G. |
| **F** | `uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root`, 266 reported bins, job `56431823` | The artifact for which cause 7 already has a recorded discharge; **not G**. `docs/OPEN_ITEMS.md` `OI-5` explicitly resolves that discharge as FPS-only. |
| **S** | `active_universe_5d/standard/candidate/std_final5_candidate.root` and its standard-P4 packet | A later selection-complete scalar-5D construction that may provide counterfactual lateral components. It is **not G**, and its existence, validation, or eventual adoption cannot by itself prove anything about G's bytes. |

The FPS discharge cannot be imported: 266 ≠ 10,694, exactly the finding in `CRITERIA-20260811` §4.1
and stable ledger row `VL68`. The July object cannot be substituted either: `DECISION-20260831` §1
rules that the seven causes are graded against G, not J.

### Is the defect on G's path?

**Yes.** G's committed readback names
`uq_universe_5d_covariance_combined_bkgaware.root` as its `combined_source`
(`nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json:28-34`). The adopter says that the detector/lateral
bands already inside that combined source are left untouched
(`nd-unfolding/adopt_unified_5d.py:17-20`). G therefore inherits the support-limited lateral block; no
selection-complete lateral replacement was composed into G.

The later standard-P4 path describes a different operation: remove exactly five named support-limited
lateral bands and add five selection-complete active-universe MAT blocks
(`nd-unfolding/p4_build_components.py:11-18`). It produced S, not G. **The lateral replacement does not
exist inside, or as a provenance-bound replacement of, G.** This is stronger than saying merely that an
adoption command has not run.

There is an unavoidable artifact-identity consequence. G is identified by an immutable digest; changing
its lateral block produces new bytes and therefore a new artifact, called **Y** below. No future receipt
can make the existing G bytes have been produced by a path they did not traverse. These criteria specify
what a cause-7-only successor **Y derived from G** would have to prove. Whether Joseph's ruling permits
the cause-7 grade to follow that successor, or instead requires an explicit new grading-subject ruling,
is left OPEN. This document does not take that decision.

## 1. Cause 7 — CV-support-limited lateral selection

**The defect.** Detector shifts can move events into or out of the selected/reported sample. A lateral
covariance built only on the nominal CV support omits that selection migration. The corrected object must
be built from selection-complete shifted endpoint samples, not from a CV-supported projection that can
only move already-selected events among bins.

### C — CODE — OPEN

**Scoped artifact: G, through an explicitly named cause-7-only successor Y whose parent digest is G's
`4f168e83…`.**

The pinned code path that writes Y must implement the algebra

`C_Y = C_G - L_support(G.combined_source) + L_active(selection-complete endpoints)`

and must prove, rather than assume, all of the following:

1. `L_support` is exactly the sum of the five named support-limited lateral bands embedded in G's
   committed `combined_source`; `L_active` is exactly the corresponding five selection-complete,
   mean-centered MAT endpoint covariances on G's 10,694-bin mask and row order.
2. The five-band sets are exact: a missing band, an extra band, a duplicate, a one-sided endpoint, a
   wrong grid, or a wrong mask/order aborts. Selection-migration censuses and declared policies must be
   checked for every endpoint; presence alone is not evidence.
3. Every non-lateral contribution is bit-identical or identity-verified against G. In particular, the
   unified-throw vertical inflation already carried by G, plus its statistical and ML blocks, must not be
   replaced by S's full block-sum total. S may supply bound active lateral components; it may not be
   substituted wholesale for G.
4. The writer and validator recompute `C_Y - C_G = L_active - L_support`, symmetry, PSD, the exact
   five-band sum, and the full component identity. The identity tolerance may use the existing standard-P4
   relative tolerance `1e-9` (`p4_build_components.py:140-171`); that is a numerical closure tolerance,
   not the M-leg materiality threshold.
5. The complete producing/import closure is pinned. A clean implementation at an unpinned revision is
   not C for Y.

No existing implementation or artifact is declared to satisfy this leg here.

### P — PROVENANCE — OPEN

**Scoped artifact: Y, with G as its required and digest-bound parent. It is not scoped to J, F, or S.**

A committed receipt must be written last and must identify the exact Y it describes. At minimum it must
record:

- Y's path, byte size, sha256, reported-bin count, mask digest, row-order digest, and producing job/run;
- G's exact path and full sha256 as `parent_candidate`, plus G's committed `combined_source` and the
  digest of the support-family ROOT actually read;
- the exact five removed support-band keys and content digests, the exact ten active endpoint inputs and
  digests, their selection-migration censuses/policies, the five constructed active-band content digests,
  and the endpoint/merged/component manifest digests;
- the pinned producing revision and executable import-closure digests, with the code identity bound to the
  run rather than inferred from a nearby checkout;
- measured closure operands and residuals for `C_Y - C_G = L_active - L_support`, the unchanged
  non-lateral block, exact band inventories, symmetry, PSD, and the full-total identity; and
- an explicit statement that F's 266-bin receipt and S's whole-file PASS are not evidence that Y was
  produced. If S supplies lateral components, their digests must be rebound into Y's receipt.

A receipt about S alone proves S; a receipt about F alone proves F. Neither is P for Y or retroactive P
for G. If the ruled subject must remain the exact bytes of G, then this leg is unsatisfiable for a
corrected construction and must remain OPEN pending Joseph's artifact-subject ruling.

### M — MAGNITUDE — OPEN; ACCEPTANCE THRESHOLD LEFT OPEN

**Scoped artifact: the matched pair (G, Y), on G's own inputs, mask, ordering, non-lateral blocks, and
central value.** A comparison of S with G is not sufficient because S also embodies a different full
construction.

The primary number is

`delta_full = sqrt(Tr(C_Y)) / sqrt(Tr(C_G)) - 1`,

the fractional change in the full scalar-5D candidate when only the five lateral bands are replaced.
The receipt must also report the diagnostic that localizes it,
`delta_lateral = sqrt(Tr(L_active)) / sqrt(Tr(L_support)) - 1`, and a distribution rather than a maximum
alone for the reported-bin uncertainty ratio
`sqrt(diag(C_Y)) / sqrt(diag(C_G))` (at least min, median, p05, p95, and max, with zero/invalid counts).
Because a trace can stay fixed while correlations move, it must additionally report
`||C_Y - C_G||_F / ||C_G||_F` and the largest absolute correlation-matrix change, with their operands.

**No numerical materiality threshold is set in this draft.** The existing standard-P4 validator records
the active/support trace ratio but explicitly labels it diagnostic and unbounded
(`p4_validate_active_lateral.py:240-248`; the committed receipt carries
`support_ratio_is_diagnostic_not_bounded`). The four-leg framework also states that a large and a small
measured difference can both satisfy M; size does not repair or excuse a construction defect. There is
therefore no inherited principled cutoff that this drafting lane can honestly apply.

This is deliberately not tuned to make today's already-visible answer come out right. In the form of
`nd-unfolding/uq_math.py:128-137`: the threshold is **LEFT OPEN**; it is left there because no
pre-observation rule connects a particular `delta_full`, `delta_lateral`, or shape-change value to
cause-7 discharge; and choosing a boundary after the standard-P4 comparison is visible would be a
threshold placed to obtain today's preferred verdict, not a criterion. Joseph must either rule a
principled materiality threshold before M is graded or rule explicitly that M is measurement-only under
§0 and carries no smallness requirement. Until then M is OPEN regardless of the measured value.

### T — TEST — OPEN

**Scoped artifact: the G→Y cause-7 replacement path and its receipt contract. Existing FPS tests are
tests of F, not tests of this pair.**

A regression test must exercise the real replacement predicate with synthetic matrices and endpoint
metadata and must be power-tested in both framework-required directions:

1. **Defect reintroduced:** replace the selection-complete active endpoints/blocks with the
   CV-support-limited bands while leaving all other inputs valid. The test must fail specifically because
   selection migration was lost, even if dimensions, PSD, total trace, and internal sums still pass.
   Fixtures must include events migrating both into and out of nominal support so a one-sign guard cannot
   pass accidentally.
2. **Guarded object disappears:** delete or rename one active endpoint, one active-band object, the
   selection-migration census/policy, G's parent digest, or the cause-7 closure identity. Each mutation
   must fail rather than skip, reduce the band count, or interpret absence as zero migration.

The positive control must pass with exactly five ± endpoint pairs, the exact G parent digest, the exact
10,694-bin mask/order, unchanged non-lateral content, and the replacement identity within its declared
closure tolerance. Artifact-confusion controls must show that supplying F (wrong 266-bin grid), J (wrong
parent digest), or a whole S total (changes more than the lateral block) fails. A source-string assertion
or a test of `check_support_comparison` alone is insufficient: that helper only records a finite trace
ratio and deliberately imposes no bound (`p4_lib.py:1309-1318`).

No existing test is declared to satisfy this leg here.

## 2. What remains open by construction

- **C, P, M, and T are all OPEN on delivery.** Nothing in this file is a grade.
- Joseph must rule whether a cause-7-corrected successor Y can inherit G's role as the grading subject;
  exact G cannot be changed without changing its digest.
- Joseph must rule the M-leg threshold or explicitly rule that M is measurement-only with no smallness
  requirement. No threshold has been inferred from the visible standard-P4 result.
- The exact Y output path, receipt schema/version, and producing revision do not exist in this draft.
- No claim is made that S is adoptable, adopted, or suitable as Y; no claim is made that its present
  packet supplies any leg.
- This document does not alter `CRITERIA`, `SCOREBOARD`, `MAP`, `OPEN_ITEMS`, `VALIDATION_LEDGER`, or any
  gate/adoption record.
