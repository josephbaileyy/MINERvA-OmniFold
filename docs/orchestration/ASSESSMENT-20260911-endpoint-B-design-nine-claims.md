# ASSESSMENT 2026-09-11 — the endpoint-B generator-comparison design, nine load-bearing claims
# checked pre-implementation

**CITABLE FOR:** the nine verdicts in §1 and the measurements behind them in §2–§10, each with its
site or command.
**NOT CITABLE FOR:** any authorization, any implementation, any compute, any grade, any adoption, any
gate movement, or any publication claim. **Endpoint B remains DEFERRED, NOT PASSED. Gate 2 remains
FAIL. `cause3_corr` remains WITHHELD. `R4`'s suspension of the cause-3 seed scan stands.** Nothing was
launched; every cluster action was a read.

**Subject:** `DESIGN-20260911-endpoint-B-generator-comparison-test.md` at commit `8a42f8ea`,
`lane/z-criteria-recommendation-20260910`. **Routed by** a peer coordinator with the **designer
recused** from assessing it, and the designer also declining to write endpoint B's terminal adoption
rule. **This lane did not author the design** and is not its implementer.

**What this assessment is not.** It does not review the design's physics taste, does not write the
adoption rule, and **does not supply remedies** — naming a requirement and handing over a fix are
different acts, and the second would disqualify this lane from reviewing the fix
(`offering-a-remedy-spends-my-next-verdict`).

## 1. The nine verdicts

| # | claim | verdict |
|---|---|---|
| 1 | samples present; *"what is missing is an ND histogrammer"* | **SAMPLES CONFIRMED; BLOCK on the gap statement** — an `(E_avail,W)` histogrammer already exists and is generator-agnostic (§2) |
| 2 | the existing instrument aims at the **opposite end** of the axis | **CONFIRMED**, decisively, on four sites vs the subsection title (§3) |
| 3 | the catch bin makes the two best models **swap** | **CONFIRMED**, including the row the requester had not verified — the derivation is exact (§4) |
| 4 | an arithmetic inconsistency in the catch fractions | **BLOCK** — the four values are a *function of the withdrawn input*, and show no inconsistency (§5) |
| 5 | only GENIE+MEC is **nested**; `mec==0` on the base | **CONFIRMED**, and already measured in-tree (§6) |
| 6 | target asymmetry C vs CH is not absorbed per-nucleon | **CONFIRMED**, with the mechanism documented (§7) |
| 7 | Tune v1 is the unfolding prior and **no assembly term covers it** | **CONFIRMED**, decisively (§8) |
| 8 | three inherited defects in the old instrument | **CONFIRMED**, all three, with one reclassified as a **label-only** defect (§9) |
| 9 | multiplicity: 120 candidates, *"at worst 1.09"* | **BLOCK on the direction** — independence is **not** the worst case (§10) |

## 2. Claim 1 — the samples are there; the gap statement is overstated

**Present, measured on pscratch** (`3d-unfolding/genie/`), sizes given in **both** units because the
reported figures are decimal MB and `stat`/`du` report MiB — the apparent mismatch is entirely that:

| artifact | reported | measured |
|---|---|---|
| `genie_mefhc_cv_ALL.gst.root` | 999 MB | **953.2 MiB = 999.5 MB** ✓ |
| `genie_mefhc_mec_ALL.gst.root` | 997 MB | **951.4 MiB = 997.6 MB** ✓ |
| `work_nuwro_p{1..8}` | 8 × 304 MB | **8 dirs** ✓; `nuwro_pN.root` **309.9–310.9 MB**, not 304 (~2% high, immaterial) |
| `work_gibuu_arr` | 2.0 GB | **2020 MiB, 80 files** ✓ |

**So the premise correction holds: no fresh generator production is needed.** Also worth recording,
because the design's inventory omits it: each `work_nuwro_pN` additionally holds **`nuwro_flat.root`
(7.3 MiB)**, and that — not `nuwro_pN.root` — is the file `build_fps_prior_nuwro_5d.py` reads.

**BLOCK on *"what is missing is an ND histogrammer."*** Measured on `main`:

- **`3d-unfolding/genie/gen_to_xsec_eavailW.py` already exists** and histograms
  `d²σ/(dE_avail dW)` *"on the analysis binning"*. It is **generator-agnostic** — `:67`
  `--gst required=True` takes an arbitrary truth-event file and `:68` `--generator` selects a reader
  from `READERS` — and its docstring states the binning is *"**identical to the 5D OmniFold W axis**
  (`unfold_nd_omnifold_unbinned.py` "W"/"eavail")"*, which is precisely the destination space an
  endpoint-B comparison needs.
- **`nuwro_to_xsec_eavailW.py`** and **`gibuu_to_xsec_eavailW.py`** mirror it, the former explicitly
  *"identical to `gen_to_xsec_eavailW.py` (GENIE) so the generator overlay is shared"*.
- `overlay_eavailW_band.py` exists for the band itself.

Because `--gst` is arbitrary, the **MEC sample — the fifth prediction, and the only nested one — is
already histogrammable by an existing tool.** The plausible residual gap is **Tune v1**, whose weights
are applied by `model_tune_xsec3d.py` in 3D only; whether `gen_to_xsec_eavailW.py`'s `--graphs`/`--norm`
path carries MnvTune weights is **not established here**.

**This verdict runs in the permissive direction, so its limits are stated.** I verified these modules
**exist**, are generator-agnostic, and **declare** matching binning. I did **not** run them, did not
verify their output against the unfolded result, and did not establish Tune v1 coverage. **The finding
is that the gap must be re-scoped, not that no work is required** — and the re-scoping matters, because
"build an ND histogrammer" and "extend one weighting path" are different authorizations.

## 3. Claim 2 — CONFIRMED: the instrument is aimed at the other end of the axis

`nd-unfolding/eavail_generator_significance.py`:

- `:2` — *"Per-generator significance of the **high-E_avail excess** (open question 6)"*
- `:6` — *"the unfolded data sits **above** every generator in the **high-E_avail / high-W corner**"*
- `:15` — *"the **high-E_avail sub-block** (E_avail >= 0.8 GeV, **the DIS tail**)"*
- `:106` — `hi = ea_e[:-1] >= 0.8   # DIS-tail sub-block`
- `:118` — the printed column is literally `chi2/ndf(DIS>=0.8)`

`docs/analysis-note/sec_3d.tex`:

- `:268` — `\subsection{The **low**-available-energy excess recovers the known low-recoil 2p2h deficit}`
- `:270` — *"The **low**-$\Eavail$ excess is the most physically interesting feature the third axis
  exposes"*

**The only region-specific block the instrument computes is the high end.** So the existing code cannot
evidence the claim the note actually makes. **Two precisions:**

1. The instrument **also** computes a **full-range** 7-bin χ² (`:132`, `chi2_to_sigma(chi2, n_ea)`).
   That is direction-agnostic rather than wrong — but it is a global goodness-of-fit and **does not
   isolate the low-E_avail region either**, so it is not a substitute.
2. **The sign convention must be pinned before anything is pre-declared.** The note says the data shows
   a low-E_avail **excess** which *recovers a generator **deficit***; the routing message called it
   *"the low-E_avail dip"*. Those name the same feature from opposite sides. A pre-declared
   one-directional test inherits whichever side it was written from, and a one-directional check waves
   the other direction through (`a-filter-needs-a-test-in-the-direction-it-acts`).

## 4. Claim 3 — CONFIRMED, including the row that had not been verified

**The catch-dropped row is transcribed correctly.** `sec_3d.tex:220-222`: *"the integrated $\Eavail$
rate (catch bin dropped) places GENIE CV, Tune~v1, NuWro and GiBUU respectively 7.2%, 9.5%, 15.3% and
21.9% below the data."*

**The full-range row does NOT appear in `sec_3d.tex`** — a covering search for `12.0`/`18.2`/`24.0`/
`27.9` in generator context returns nothing there. **That is not a defect: the design discloses at
`:86` that the left column is derived**, and the derivation reproduces **exactly** from the
flux-averaged totals at `sec_3d.tex:194-197` (GiBUU `2.22`, NuWro `2.34`, GENIE CV `2.52`, Tune v1
`2.71`, data `3.08`, all `e-38 cm²/nucleon`):

```
Tune v1   (3.08-2.71)/3.08 = 12.01%   design 12.0
GENIE CV  (3.08-2.52)/3.08 = 18.18%   design 18.2
NuWro     (3.08-2.34)/3.08 = 24.03%   design 24.0
GiBUU     (3.08-2.22)/3.08 = 27.92%   design 27.9
```

and the note's own `:197` *"all four models under-predict the rate, by 12 to 28%"* corroborates the
span independently.

**So the swap is real:** full range **Tune v1 12.0 < GENIE CV 18.2**; catch dropped **GENIE CV 7.2 <
Tune v1 9.5**. The two best predictions exchange places on a choice of integration region.
**Global-vs-region-specific is therefore a scientific choice, not a display choice**, and pre-declaring
both is the right response.

## 5. Claim 4 — BLOCK: the four catch fractions are a function of the withdrawn input

The design flags, as *"an unresolved inconsistency in the inputs I was given"*, that the implied catch
fractions are **Tune v1 43.4%, GENIE CV 37.6%, NuWro 38.7%, GiBUU 40.4%** — *"three of four outside the
relayed 43–46%."*

**Reconstructed.** With `d_full`, `d_catch` and a single **assumed data catch fraction** `f_d`,
`f_g = 1 − (1−d_catch)(1−f_d)/(1−d_full)`. Solving `f_d` from the Tune v1 row alone gives
**`f_d = 44.96%`**, and that one value then reproduces **all four** published figures:

```
Tune v1  43.40  (design 43.4)      NuWro  38.66  (design 38.7)
GENIE CV 37.56  (design 37.6)      GiBUU  40.38  (design 40.4)
```

**Two consequences, and they dissolve the flagged item.**

1. **The four values are a deterministic function of ≈45%, which is the withdrawn 43–46% band itself.**
   The requester has withdrawn that range as unsourced and fabricated. **The derived fractions inherit
   the withdrawal** — they are not independent evidence about the note, and should be withdrawn with
   their input rather than carried as an open inconsistency. The design's self-description as having
   *"transcribed"* is also imprecise: this quantity was **derived**, using a fabricated input.
2. **Even granting `f_d`, it shows no inconsistency.** *"Generator catch fractions (37.6–43.4%) differ
   from the data's (45%)"* is the arithmetic restatement of *"the full-range and catch-dropped deficits
   differ"*, which is the design's own claim 3. Two predictions that under-predict the catch bin and the
   rest of the axis by different amounts **must** yield different catch fractions. The design's second
   stated escape — *"or the 43–46% range describes the data only"* — is **not an alternative**: it is
   what the arithmetic already assumed.

**What follows.** The flagged work item — *"one arithmetic check on the producing scripts
(`overlay_generators_band.py`, `model_tune_xsec3d.py`) … should be settled before the table is used"* —
**has no premise left**, and the claim that *"the answer changes §2's table"* is **false**: both columns
of that table are independently sourced (right from `:221-222`, left from `:194-197`), so **the table
stands and does not depend on any catch fraction.** This removes a blocker rather than adding one.

## 6. Claim 5 — CONFIRMED, and it was already measured in-tree

The nesting premise is not a new measurement; it is recorded:

- `3d-unfolding/genie/README.md:201` — *"(`mec==0` for all 1.48M CC events; modes are QE 11%, RES 22%,
  DIS 66%, COH …)"*
- `3d-unfolding/genie/mode_decomp_eavail.py:4` — *"absent from this CV: `mec==0` for …"*
- `genie_fsi_*_xsec3d_summary.txt:3` gives the exact count — **`total CC=1484896`**

**So 2p2h is added by the MEC sample, not reweighted, and GENIE+MEC is nested with the GENIE CV base.**
The consequence the design draws — that ranking four **non-nested** predictions is not a significance,
so the fifth prediction is **not optional** — follows.

**One population note.** The same summary line reads `total CC=1484896, **in-PS=938600**`. The design
says *"all 1.48e6 CC events"*, which is the **full** sample; the in-phase-space subset is **938,600**.
The nesting conclusion is unaffected (`mec==0` on the superset implies it on any subset), but the two
populations should be named wherever the count is quoted
(`my-recurring-failure-is-asymmetric-comparison`).

## 7. Claim 6 — CONFIRMED, with the mechanism and why per-nucleon cannot absorb it

- `3d-unfolding/genie/README.md:32` — *"Target: **CH** (C12 0.9225 / H1 0.0775 by mass); **per-nucleon
  = /13**."*
- `run_gevgen.sh:9` — *"**CH target** by mass fraction (C12 0.9225, H1 0.0775)"*
- `run_nuwro.sh:6` — *"Target: **C12** (`target_type=0`). NuWro's composite `target_content` crashed;
  C12 is …"*, with `:32-34` `target_type = 0`, `nucleus_p = 6`, `nucleus_n = 6`
- `sec_3d.tex:175` *"on a CH target"* vs `:183` and `:185` *"(C target)"*

**So NuWro and GiBUU are on C and GENIE/Tune v1 on CH, as claimed.** The design's reasoning that
per-nucleon normalization does not absorb the nuclear-model part is **sound and stronger than stated**:
CH carries **one free proton per 13 nucleons**, and on a free proton 2p2h **cannot occur at all** while
RPA and nuclear FSI do not apply. Dividing by 13 rather than 12 rescales a total; it cannot remove a
component that exists in one target and not the other — **and the missing component is exactly the
low-recoil multi-nucleon physics that claim (b) is about.** Restricting the primary to the GENIE pair
follows.

## 8. Claim 7 — CONFIRMED, decisively; this is the design's strongest precondition

- **Tune v1 is the prior.** `build_fps_prior_nuwro_5d.py:11` —
  `ratio(pT,p||,Eavail,W) = [NuWro truth shape] / [**MnvTune-weighted GENIE truth shape**]`, i.e. the
  nominal shape's denominator.
- **Nothing in the assembly covers it.** `z_assembly.py:4` —
  `C_Z^c = D_Z^c (sum_V C_b) D_Z^c + sum_R C_b + sum_A L_b + C_stat + C_ML`, five terms; and a search of
  that module for `prior|unfold|reunfold` returns **nothing**.

**The stated reason is correct and is the load-bearing part:** a band **reweights a fixed estimator**,
whereas a prior change **re-runs OmniFold**. A quantity that changes the estimator cannot appear as a
term in a covariance assembled over a fixed estimator, so **no amount of band work can cover it** —
this is not an omission in the assembly, it is outside the assembly's form. Calling it endpoint B's most
important precondition is justified.

**Two limits recorded.** The `<= 6` task-h figure is explicitly a `--time` **request**, not a `sacct`
measurement — **correctly labelled**, and it must stay labelled that way. And a prior re-unfold is a
**compute act requiring its own authorization**; nothing here authorizes it.

## 9. Claim 8 — all three CONFIRMED, one of them reclassified

**(a) ndf is the bin count while the inverse is a pseudo-inverse — CONFIRMED.** `:107-108`
`Cinv = np.linalg.pinv(C_y)` and `Cinv_hi = np.linalg.pinv(...)`; `:132` passes **`n_ea`** (7) as `ndf`
and `:133` passes **`int(hi.sum())`**. `pinv` discards modes below its `rcond`, so the effective degrees
of freedom are the **retained rank**, not the bin count, and **χ² and ndf disagree with no diagnostic
printed**. Same failure family as the ρ-bound finding already recorded on this lane
(`a-proof-about-the-inverse-is-not-about-pinv`): a result stated for `C^-1` does not transfer to
`pinv(C)`. The module's own `:98` comment already warns the covariance is correlation-dominated, which
is the regime where this bites hardest.

**(b) The *"one-sided"* label — CONFIRMED, but it is a LABEL defect only, and that reclassification
matters.** `:111-113`:

```python
p = stats.chi2.sf(chi2, ndf)
# one-sided Gaussian-equivalent significance
z = stats.norm.isf(p / 2.0) if p > 0 else float("inf")
```

Measured: at `p = 0.01`, `isf(p/2) = 2.5758` against `isf(p) = 2.3263` — the cited `2.576` vs `2.326`,
confirmed. **But for a χ² upper-tail `p`, `isf(p/2)` IS the conventional HEP Gaussian-equivalent**
(the convention on which 5σ ↔ `p = 5.7e-7`). So the **printed number is standard and correct**; only
the comment is wrong, and **fixing the comment changes no output**. Reported this way deliberately: if
it is carried as a numerical defect, the next reader recomputes `2.326`, concludes the code is wrong,
and **changes a correct number**. The defect is the word *"one-sided"*, nothing else.

**(c) The weight correctly excludes `dea` — CONFIRMED, and a replacement must preserve it.** `:69`
`dpt, dpz, _dea, dq3 = (np.diff(pt_e), np.diff(pz_e), np.diff(ea_e), np.diff(q3_e))` — `_dea` is
underscore-prefixed and deliberately unused. That is the **correct density treatment for
dσ/dE_avail**: the marginalization integrates `pt`, `pz`, `q3` and must **not** integrate the
differential variable. This is the one thing the old instrument gets right that is easy to "fix" into a
bug.

## 10. Claim 9 — BLOCK on the direction; the magnitude is small but the word *"worst"* is wrong

`N = 5 × 4 × 3 × 2 = 120` ✓. At a nominal `z = 3.00` (two-sided `p = 0.0027`, matching the code's own
`isf(p/2)` convention):

| dependence assumption | family-wise `p` | corrected `z` |
|---|---|---|
| perfect positive dependence | `0.00270` | **3.000** (no penalty) |
| **independence (Šidák)** | `0.27705` | **1.087** ← the design's `1.09` |
| **union / Bonferroni bound** | `0.32398` | **0.986** |

**The design's arithmetic reproduces exactly — `1.0870 ≈ 1.09`.** But **independence is not the worst
case.** The union bound is `0.986`, **more conservative by `0.101σ`**, and it is *attainable* under a
dependence structure with disjoint rejection regions. The attainable range over dependence structures
is therefore **`[0.99, 3.00]`**, and independence sits **near, not at**, the conservative end.

**So *"at worst 1.09"* is false as written** and should read *"1.09 under independence; 0.99 on the
union bound."* The practical consequence is `0.1σ` and changes no conclusion — **the reason to fix it is
that a claimed bound invites exactly one question from a referee, and the honest answer is that it is
not a bound.** Note also the direction: positive correlation between these 120 statistics — which is
certain, since they share a covariance, a data vector and overlapping regions — makes the penalty
*smaller*, so **independence understates the nominal significance's survival, not its risk**.

**The *"at most four"* cap is consistent** with a `≥ 2.5σ` floor: `N=4 → 2.551`, `N=5 → 2.472`. The
floor itself is a scientific choice this lane does not adjudicate.

## 11. The two self-disclosures, and the 187/188 item

**Both disclosures are the right disposition and are recorded rather than absorbed.** (i) Withdrawing
the *"no prior systematic exists"* argument because the cited registries name only **22 of 45** bands
is correct in kind, not merely in degree: an absence claim over a **non-covering population is void,
not weak** (`a-criterions-declared-population-can-be-empty`,
`inference-from-absence-needs-a-covering-search`) — and `z_contract.py:71` deriving `R = 27` without
ever listing it is exactly the *derived population* case that is no safer than a listed one.
(ii) Catching its own use of `263` as Z's rank when `263` is the **predecessor's** measured value is
the `a-claim-about-code-is-dated` shape.

**On the 187/188 gap, one datum this lane can contribute:** the live cluster count of
`nd-unfolding/uq_5d/universe_sweep_bkgaware` is **188 files**, and `PROVENANCE-20260822:230` records
`n_universes` as *"a whole-sweep **file count**, 188"*. **So the `188` printed in
`fin5dBKG_55912230.out` is corroborated twice independently, and the `187` side is the one to
re-derive.** Flagged, not chased; it is not this lane's item.

## 12. What this assessment did not do

It authorized nothing, launched nothing, implemented nothing, graded no leg, adopted nothing, moved no
gate, and wrote no adoption rule. It read `main` at `6f24fb00`, the design at `8a42f8ea`, and the
cluster read-only. **Endpoint B remains DEFERRED and NOT PASSED; `R4` stands suspended; Gate 2 remains
FAIL.** The histogrammer and the prior re-unfolds are **separate acts requiring their own
authorization**, and none is authorized. **The decisions are Joseph's.**
