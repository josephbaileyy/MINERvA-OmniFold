# RULING — a RECONSTRUCTED cell assignment is admissible, but **not as a substitute**, because the thing my own ruling specified **does not exist and could not**; the phrase is WRONG and is amended here

**By:** lane C (PET), on the mediator's dispatch, 2026-08-19, at `448fe5ec`. **The defect is in my own
lane's `RULING-20260817-lanec-oi126-branch-set-not-exhaustive.md:217`.** Lane B is right that this is a
method choice and not a detail, and right to have escalated rather than improvised silently.

| | | authority |
|---|---|---|
| **§1 does the specified mechanism exist?** | **NO — and its absence is a DESIGN PROPERTY, not an omission.** | **MEASURED.** |
| **§2 is B's reconstruction admissible?** | **YES, as a CONSTRUCTION. "Substitute" is the wrong frame — there is nothing to substitute FOR.** | **RULED.** |
| **§3 faithful, or merely consistent?** | **FAITHFUL about the grid; NOVEL about the assignment.** The split is the ruling. | **RULED.** |
| **§4 the no-clip choice** | **REQUIRED, not permitted.** Clipping would contaminate the two bins the comparison reads. | **RULED.** |
| **§5 must `-1` cells be reported?** | **YES, and a number that omits them is NOT quotable.** | **RULED.** |
| **§6 should my ruling's phrase be amended?** | **YES. It is wrong, and it has ALREADY PROPAGATED into an artifact I may not touch.** | **RULED + ROUTED.** |

> **THE ONE-LINE FORM:** *the loader owns the GRID and does not own the ASSIGNMENT; production never assigns
> cells at all, because production refinement is unbinned by design — so Test 2's assignment is a new
> construction that must be labelled as one, and the sentence in my ruling that called it "the loader's own"
> names a capability whose absence is deliberate.*

**Everything below was measured this turn at `448fe5ec` after `fetch` + `rebase`, by reading the pinned
loader (read-only; I did not modify it) and by importing its constants in a throwaway process.**

---

## 1. THE FINDING IS CONFIRMED, AND IT IS STRONGER THAN "THE PRIMITIVE IS MISSING"

Lane B's three measurements reproduce exactly:

- `grep -cE 'digitize|searchsorted|ravel_multi_index'` over `fullevent_fps_dataloader.py` → **`0`**. The
  loader contains no binning primitive.
- `build_reco_cloud` returns the literal `(1, 2)` at **`:161`** and **`:175`**, and its docstring
  (`:142`) says *"coord_idx is (1,2) either way => the KNN"* — the point cloud's **(pos, z) neighbourhood
  columns**. **This is the concrete way the next reader gets misled:** `coord_idx` is the only
  index-shaped thing the loader hands back, and a reader told the loader has "its own per-event assignment"
  will find it and use it. It is not a bin index and using it as one would produce a number.
- `stay_positive_refine_binned(signed_w, cell, n_cells)` at **`:628`** RECEIVES `cell` (`:633`
  `cell = np.asarray(cell)`) and `bincount`s over it; it never derives it.

**AND THE DECISIVE FACT, WHICH IS THE LOADER'S OWN COMMENT — `:659-666`:**

> *"The binned `stay_positive_refine_binned` above is **FIXTURE-ONLY** (needs a **pre-assigned cell index**;
> it backs the coherence/independent cross-check tests). **PRODUCTION refinement is the LEARNED UNBINNED
> classifier** `unfold_2d_omnifold_unbinned.refine_stay_positive` on **CONTINUOUS reco features** (the
> locked ND/PET method, arXiv:2505.03724)."*

**So the absence is not an oversight to be worked around — it is the method.** The production estimator is
unbinned; there is no per-event cell index anywhere in the production path, and there never was one to
reference. `refine_signed_measured` (`:667`) and `learned_stay_positive_refiner` (`:708`) are the production
route, exactly as B reported.

---

## 2. RULED — ADMISSIBLE, BUT THE FRAME "SUBSTITUTE" MUST BE REJECTED

**A substitute presupposes a referent.** Because production performs no cell assignment, B's `digitize` is
not standing in for a canonical assignment that was inconvenient to reach — **it is the only cell assignment
that has ever existed for this quantity.** Calling it a substitute would imply a canonical one exists to be
compared against, and a later reader would go looking for it, fail, and reach for `coord_idx`.

**RULED: it is admissible as a CONSTRUCTION, on the conditions in §3–§5, and it must be described as one.**
Every artifact reporting a Test 2 number must say that the binning is introduced by the probe and is not
part of the estimator. **A binned diagnostic of an unbinned estimator is legitimate; silently presenting it
as the estimator's own view is not.**

---

## 3. FAITHFUL vs MERELY CONSISTENT — THE ANSWER SPLITS BY OBJECT, AND THAT SPLIT IS THE RULING

The mediator asked whether importing the loader's edge constants makes the reconstruction *faithful* or
merely *consistent*. **Neither answer is right for the whole object, because the reconstruction has two
parts with different referents.**

**THE GRID — FAITHFUL, and about as strongly as this repo can manage.** B imports
`CANONICAL_PT_EDGES` (`:64`), `CANONICAL_PPARALLEL_EDGES` (`:67`), `SCALAR_COLS` (`:76`) and
`assert_extended_fps_edges` (`:102`) rather than restating any of them, so **no second copy exists to
diverge** — `BEN-227`/`BEN-228` satisfied by construction rather than by discipline. Verified in-process:
**16 pT edges → 15 bins, 20 p_parallel edges → 19 bins, `15 × 19 = 285` cells**, matching B's report.

**THE ASSIGNMENT — NOVEL, and cannot be faithful, because faithfulness requires a referent and there is
none.** It is *consistent with* the grid the estimator's domain guard enforces. That is the strongest
available property and it is weaker than faithfulness. **Say "consistent with the canonical grid", never
"the loader's assignment".**

### 3a. ON THE DRIFT ASSERTIONS — I NEARLY FILED A GAP HERE AND IT DISSOLVED ON READING THE GUARD

B's spot assertions are `edges[10] == 6.0` and `edges[16] == 20.0`. **Both are on the p_parallel axis** —
verified: `CANONICAL_PPARALLEL_EDGES[10] == 6.0`, `[16] == 20.0`, while `CANONICAL_PT_EDGES[10] == 1.0` and
`6.0` does not occur in the pT edges at all. I began to file this as an **asymmetric guard** — pT unpinned,
and pT is where the `[4.5, 30]` catch bin lives.

**It is not a gap.** `assert_extended_fps_edges` (`:102-125`) pins **both** axes exhaustively: shape plus
`allclose` against the full canonical array for pT *and* p_parallel, plus an explicit paper-grid rejection on
each (`pt[-1] == 4.5` and `ppar[0] == 1.5` both raise). Since the probe imports and calls it, **the whole
grid is pinned and the two spot assertions are redundant belt-and-braces.** Recorded because the near-miss
is the useful part: *a spot check that covers one axis, sitting next to an exhaustive guard, reads like the
guard.*

**RULED, as a maintenance condition rather than a defect:** the spot assertions are permitted and must
**not** be treated as the drift guard. **If `assert_extended_fps_edges` is ever removed from the probe on the
grounds that the spot checks cover it, pT becomes unpinned** — including the top edge that distinguishes the
extended grid from the paper grid, which is the difference between measuring this domain and silently
measuring a restricted one.

---

## 4. RULED — THE NO-CLIP CHOICE IS **REQUIRED**, NOT MERELY PERMITTED

`np.digitize` without clipping sends out-of-grid events to a sentinel; clipping folds them into the edge
bins. **Verified geometry:** the pT top bin is `[4.5, 30]` and the p_parallel top bins run above `20`
(`… 15, 20, 40, 60, 120`).

**The `−1.828` limb of the structure Test 2 is asked to reproduce is the `> 20 GeV` p_parallel region, and
the pT catch bin is `[4.5, 30]`. Clipping would pile every overflow event into exactly the two bins the
comparison reads.** A clipped Test 2 would therefore produce a number, and the number would be
contaminated in the one place the test is looking — **the failure mode where the instrument is wrong
precisely where it is being read.**

**RULED: no-clip is required. A Test 2 result computed with clipping is not admissible, and this is not a
matter of analyst preference.** B's choice is correct and its stated reason is the correct reason.

---

## 5. RULED — `-1` CELLS MUST BE REPORTED, AND OMITTING THEM MAKES THE NUMBER UNQUOTABLE

Given §4, out-of-grid events exist as `-1` and must go somewhere. **Dropping them silently changes the
denominator while still producing a number** — the same shape as §4 and the shape this campaign keeps
filing.

**RULED, as the quotability condition:**
1. **Report the `-1` count AND its weight share**, per arm (nominal and each of the 50 replicas), in every
   JSON the probe writes. A count alone is insufficient: the comparison is over weighted mass, so a small
   count carrying large weight is the case that matters.
2. **Report them per arm, not pooled.** If the nominal and the replicas have materially different `-1`
   shares, the target-level gap is partly an out-of-grid-fraction difference and **not** the spatial
   structure being tested. That would be a confound, not a result.
3. **A Test 2 number is quotable only alongside those shares.** If they are non-negligible and differ across
   arms, the number is **not** quotable as evidence about the `−0.128 / +3.555 / −1.828` structure.

---

## 6. THE AMENDMENT — AND THE PART I CANNOT FIX

**My ruling's `:217` reads:**

> *"**Test 2 — spatial, still no jobs.** Histogram both into the reco grid using the loader's own per-event
> assignment and ask whether the **target-level** gap reproduces the `−0.128 / +3.555 / −1.828` structure."*

**It is WRONG, not imprecise**, and the mediator is right about its family: it is a committed ruling
specifying a **nonexistent mechanism**, alongside this campaign's guard-citing-a-nonexistent-authority and
constant-derived-from-syntax findings. **The aggravating feature, relative to those:** it does not name a
mechanism that was removed or misremembered — it names one whose absence is a **deliberate design property**
of an unbinned estimator, so no version of the loader ever had it.

**Amended text, which I have applied in place at `:217` in the same commit as this ruling:** the phrase
"using the loader's own per-event assignment" becomes an assignment **reconstructed by the consumer** from
the loader's imported canonical edges and guard, with the note that the loader performs no binning and
production refinement is unbinned.

### 6a. ⚠ THE PHRASE HAS ALREADY PROPAGATED, AND ONE COPY IS OUTSIDE MY REACH

`docs/orchestration/state/live-state.json:56` restates it **verbatim** — *"into the reco grid using the
loader's own per-event assignment"* — inside `next_authorized_action`, whence it renders into the generated
`LIVE-STATE.md`. **Both are control-plane sources on my do-not-touch list, so I have not touched them, and
amending only my ruling leaves the defective phrase live in the file that answers "what is happening right
now".**

**ROUTED, with the exact string so it needs no re-derivation:** whoever owns `live-state.json` should replace
*"using the loader's own per-event assignment"* with *"using a consumer-reconstructed assignment over the
loader's canonical edges (the loader performs no binning; production refinement is unbinned)"*. The probe's
own header carries the corrected framing already, per the mediator's report.

*This is the mechanism from `a-claim-about-code-is-dated` in a worse form: that entry is about a claim true
when written and later copied; **this one was never true, and was copied anyway** — by me into a ruling,
thence into a generated control-plane artifact. **A ruling's prose is a specification, and this campaign
propagates specifications faster than it checks them.***

---

## 7. THE TWO SMALLER ITEMS — BOTH REAL, ONE CHEAPER THAN THE REPORT IMPLIES

**(a) `n_data` / `n_bkg` — the values ALREADY EXIST at runtime; only the PERSISTENCE is missing.**
`build_signed_measured_inventory` **returns them individually** (`:680` docstring, unpacked at `:1447`), and
`:1495` already checks `w_refined.shape[0] != n_data + n_bkg`. **So the fix is to persist two integers that
are already in hand, not to derive or infer a split** — materially cheaper than "unrecorded" suggests.
**And it matters more than alignment:** `coherent_bootstrap_factors(n_data, n_sig, n_bkg, seed)` (`:614`)
draws Poisson factors **per leg** (`:621`, `:624`), so a wrong split changes **which draws are produced**,
not merely how they are laid out. **RULED: B's decision to assert the sum and fail closed rather than assume
a split is correct.** A receipt naming both is endorsed; it is not mine to write.

**(b) Row order — CONFIRMED: data first, then aligned background.** `build_signed_measured_inventory`
(`:675`) returns `feat = np.vstack([fd, fb])` at **`:702`**. **RULED: the probe must assert this rather than
rely on it.** Reversed, every number stays finite and plausible and every one is wrong — there is no
exception, no shape mismatch, and nothing fails. **A property that only breaks the answer and never the run
must be asserted at the point of use.**

---

## 8. WHAT THIS RULING DOES AND DOES NOT AUTHORISE

**It authorises no execution.** Joseph authorised the runnability fact-finding in his own words and
explicitly **not** the measurement. **Test 2 has not been run, and this ruling does not license running it.**
It rules on admissibility *if and when* it is authorised.

Not authorised, and each standing before this ruling: any compute; any resubmit; the `M(ii)` family; any
repin; any rename or deletion of the 115 load-bearing `sbatch_*.sh` names; any deletion or top-level reorg.
**This is a ruling, not a receipt.**

**Independently noted, not relied upon:** the mediator reports Test 2 is unrunnable from this machine (all 51
arrays absent, `/pscratch/sd/j/josephrb` not a directory here, the certified Gate-2 nominal not git-tracked),
that the probe fails closed with exit 1 writing nothing, and that `verify_hash_bindings.py` reports ALL
BINDINGS INTACT either side. **I did not re-verify those and this ruling does not depend on them** — §1–§7
are properties of the source, not of any run. **I did confirm the cluster is unreachable from here
(`ssh` → rc=255, unpiped) in an earlier turn today.**

**And the scope shrink is acknowledged rather than buried:** with `(c)` refuted by lane D, Test 2 no longer
adjudicates it. **Its remaining value is localisation above the target layer, which nothing else on the
record probes — that is a real but smaller claim, and any Test 2 artifact must state it** rather than inherit
my 2026-08-17 framing, in which Test 2 was the discriminator for `(c)`.

## 9. WHY THIS SHOULD NOT RECUR IN THIS FORM

The disqualifying test for the next ruling that specifies a mechanism is one command:

```
grep -nE 'digitize|searchsorted|ravel_multi_index' nd-unfolding/pet/fullevent_fps_dataloader.py   # 0
```

**Before a ruling attributes a capability to a named module, grep the module for the capability.** I did not,
and the sentence survived commit, review, a quorum framing, and propagation into the control plane — because
prose that *sounds* like it describes code is not checked the way code is. **Prefer the executable form:
"histogram using edges imported from X and asserted by X's own guard" is checkable; "using X's own
assignment" is not.**

*Filed by lane C. §1, §3, §3a, §4 and §7 are measurements taken this turn at `448fe5ec`; §6a's propagation
is a `grep` over the committed control-plane source. I modified my own 2026-08-17 ruling and nothing else in
the code tree; I did not touch the loader, the probe, the runnability document, or any control-plane source.*
