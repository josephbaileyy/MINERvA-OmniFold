# Endpoint B — design for the generator-comparison test

**Owner:** `z-criteria-owner` lane. **Base:** `258bddc2` (lane), `6f24fb00` (`origin/main`).
**Requested by:** `minerva-omnifold-7f`, routing the design away from whoever will review it.

> **CITABLE FOR:** a proposed design for the non-2D generator-significance test — hypotheses,
> observables, regions, normalization treatment, statistic, and terminal outcomes.
> **NOT CITABLE FOR:** any significance, any adopted criterion, any grade. **Nothing here is
> adopted, run, or authorized.** Endpoint B remains **DEFERRED, NOT PASSED**. Gate 2 remains
> **FAIL**, `cause3_corr` remains **WITHHELD**, and no value from `nd-unfolding/mii/member_k000000/`
> is quoted anywhere in this document.
>
> ⚠ **I AM THIS DESIGN'S AUTHOR AND THEREFORE CANNOT BE ITS ASSESSOR.** Supplying a design spends
> my verdict on it. Route it to the independent assessor **before** any part is implemented, not
> after. I also do not write endpoint B's terminal adoption rule, for the same reason I declined
> endpoint A's.

---

## 0. The brief's premise, corrected: no fresh generator production is needed

The brief says Joseph *"is willing to fund fresh production."* **Measured on the cluster today, the
truth event samples for every candidate survive.** `ls -la` /`du -sh` on
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie/`:

| prediction | surviving sample | size |
|---|---|---:|
| GENIE 2.12 CV | `genie_mefhc_cv_ALL.gst.root` (+ `work_seed1..10/`) | 999 MB (+ 10 × 268 MB) |
| **GENIE CV + Valencia 2p2h** | `genie_mefhc_mec_ALL.gst.root` (+ `work_mecseed1001..1008/`) | 997 MB (+ 8 × 334 MB) |
| NuWro 21.09 | `work_nuwro_p1..p8/nuwro_pN.root` + `nuwro_flat.root` | 8 × 304 MB |
| GiBUU 2019 | `work_gibuu_arr/task1..~80/` | 2.0 GB |
| MINERvA Tune v1 | not a generator sample — the analysis MC truth with `w_truth` | — |

**So the funding question is narrower than the brief assumes.** What is missing is not events but a
**histogrammer for the ND grid**: `genie_to_xsec3d.py` does `(pT,p‖,E_avail)`, and
`gen_to_xsec_eavailW.py` does `(E_avail,W)` on edges it states are *identical* to the 5D axes.
Neither produces a 4- or 5-axis prediction, and the three generators sit on **three parallel
scripts** (`genie_to_xsec3d.py`, `nuwro_to_xsec_eavailW.py`, `gibuu_to_xsec_eavailW.py`) rather than
behind `gst_reader.READERS`, which still contains **only** `{"genie": read_gst}` despite its own
docstring inviting the other two. Re-histogramming ~2 M events per generator is a per-event loop,
not a generation campaign.

**Where fresh production WOULD be needed is stated in §4.3** — and it is not for the four
candidates.

---

## 1. What the manuscript claims, and why the existing instrument tests the wrong end of the axis

The claim is a subsection title: **"The low-available-energy excess recovers the known low-recoil
2p2h deficit"** (`docs/analysis-note/sec_3d.tex:268`). Its load-bearing parts:

| # | component of the claim | note line | needs a covariance? |
|---|---|---|---|
| a | data sit **above** all four models at low `E_avail` | `:201-202` | yes — and the treatment of §5 decides it |
| b | the gap is **localized** in the QE–Δ dip `[0.10,0.20)`, `[0.20,0.40)` | `:303-306` | yes — this is the discriminating, shape-level part |
| c | its **shape and size match 2p2h** (≈43% of the QE rate) | `:307-310` | yes |
| d | enabling Valencia 2p2h **moves GENIE toward the data** (46% of the dip gap, 27% integrated) | `:319-320` | yes |
| e | it is the established MINERvA low-recoil feature | `:273-277` | no — interpretive |
| f | FSI does **not** explain it (sub-percent dials) | `:280-292` | no — already closed at central value |

**⚠ The existing instrument tests the opposite end of the axis.**
`nd-unfolding/eavail_generator_significance.py` is, by its own docstring, *"the high-E_avail excess
(open question 6)"* (`:2`), *"the high-E_avail / high-W corner"* (`:6`), with the sub-block taken at
*`E_avail >= 0.8 GeV`, the DIS tail* (`:15`, `:106`). The manuscript's stated conclusion is about
**the lowest `E_avail` bins**. Both excesses may be real — all four models under-predict everywhere —
but **an instrument aimed at the DIS tail cannot deliver evidence for a dip-localized claim.**
Inheriting it because its code exists would test a different proposition than the one asserted.

---

## 2. The catch bin is not inert — it changes which generator is closest

The brief says the `[3,100]` GeV catch bin *"carries 43–46% of integrated rate and nothing
discriminating."* The first half is relayed; **the second half is wrong, and the note's own numbers
show it.** Transcribing only published values — the flux-averaged totals at `:194-197` (full range)
and the integrated `E_avail` deficits at `:219-221` (catch bin **dropped**):

| prediction | deficit, FULL range (derived from `:194-197`) | deficit, catch DROPPED (`:219-221`) |
|---|---:|---:|
| MINERvA Tune v1 | **12.0%** ← closest | 9.5% |
| GENIE 2.12 CV | 18.2% | **7.2%** ← closest |
| NuWro 21.09 | 24.0% | 15.3% |
| GiBUU 2019 | 27.9% | 21.9% |

**The left column is derived, so here is its check:** my derived full-range deficits span
**12.0–27.9%**, and the note itself states *"all four models under-predict the rate, by 12 to 28%"*
(`:197-198`). The derivation reproduces the note's own published range, so the arithmetic is checked
against the source rather than merely asserted.

**⚠ THE LEADING MODEL CHANGES IDENTITY.** Full range: `Tune v1 < GENIE CV < NuWro < GiBUU`. Catch
dropped: `GENIE CV < Tune v1 < NuWro < GiBUU`. Including or excluding one bin **swaps the two best
models**. The catch bin therefore does not merely *dilute* — it **reverses the conclusion about
which prediction the data prefer.** Whether it is in the test is a declared scientific choice that
must carry a stated reason; it cannot be inherited from a figure's axis range.

Two further facts about that bin, both structural:

- **Width.** On edges `[0, .1, .2, .4, .8, 1.5, 3, 100]` the catch bin is **97 GeV** against **3.0
  GeV for the entire rest of the axis — 32.3×.** Any *width-weighted* rate functional is
  catch-bin-dominated. Any *equal-weight* χ² over 7 density values gives it **1/7** of the test.
  Neither is neutral, and they differ by a factor of ~200 in effective weight. The dip — the two
  bins that carry claim (b) — is **0.30% of the axis but 28.6% of an equal-weight 7-bin χ².**
- **⚠ An unresolved inconsistency in the inputs I was given, flagged rather than resolved.** If the
  two note quantities integrate the same phase space and differ *only* by the catch bin, then the
  implied catch fraction of each prediction's own total is Tune v1 43.4%, **GENIE CV 37.6%, NuWro
  38.7%, GiBUU 40.4%** — three of four outside the relayed 43–46%. Either the two note quantities
  are over different phase spaces, or the 43–46% range describes the data only. **This is one
  arithmetic check on the producing scripts (`overlay_generators_band.py`, `model_tune_xsec3d.py`),
  and the answer changes §2's table, so it should be settled before the table is used.** I have not
  settled it: I transcribed, and the disagreement is between two published numbers, not with a
  measurement of mine.

---

## 3. Three independent constraints all cap the test's dimension — this is the design's spine

### 3.1 Rank. A proven bound, not an estimate.

The relayed band inventory makes the covariance's low rank a **consequence of construction**:
42 of 44 bands are two-point `±1σ` finite differences, and **a `±1σ` pair spans exactly one
direction**, so each contributes rank exactly 1 — under CV-centering and mean-centering alike, since
the pair is `{+d, −d}`.

| centering | bound on `rank(C_syst)` | |
|---|---|---|
| mean-centred (`≤ N−1` per band) | `42 + 99 + 2 + 1` | **144** |
| CV-centred (`≤ N`) | `42 + 100 + 3 + 1` | **146** |

Measured `[TOTAL syst 5D] rank = 141` sits inside both, 3–5 below. **So `rank = 141` is explained by
the ensemble sizes, not by ill-conditioning** — these are linear-response derivatives, and the
systematic model carries no information outside a 141-dimensional subspace.

**The relayed inventory reconciles against the Z contract exactly, which is worth recording because
it had not been cross-checked.** `z_contract.py:66-71` fixes `|V| = 13`, `|A| = 5`,
`N_BANDS_TOTAL = 45`, `|R| = 27` derived. Against the relay:

| cell | from the relay | contract | |
|---|---|---|---|
| all bands | 44 file-backed **+ 1 analytic** | **45** | ✓ exact |
| two-point split | `V 11 + A 5 + R 26 = 42` | — | ✓ consistent (`2p2h`, `Flux` are the two non-two-point, both in `V`; `p4_lib.ENDPOINTS = (0,1)` makes all of `A` two-point) |
| `R` | 26 two-point + 1 analytic | **27** | ✓ exact |
| **files** | **188** | implied `22 + 100 + 3 + 10 + 52 =` **187** | ⚠ **one over** |

**All three band cells reconcile exactly; only the file total is one over.** That is a one-line check
in the producer's own log, and it does not move the rank bound either way.

**The relevant `rank(C)` must be named with its population, because two numbers are in play and they
belong to different objects.** `[COMBINED 5D] rank = 263/10694` is **measured on the existing
combined 5D covariance — the predecessor, not Z.** Z's own figure is a **bound, `rank(C_Z) ≤ 265`**,
and Z has not been built. So the cap below is `rank(C)` for whichever object the test actually
consumes, and it is of order `263–265` either way — which is why the design conclusion does not
depend on resolving it, but the *receipt* must record which object was used.

For a test on `y = M x` with `d` rows, `rank(M C Mᵀ) ≤ min(d, rank(C))`:

- **`d > rank(C)`:** `C_y` is **necessarily** singular, `pinv` is mandatory, and the χ² lives in a
  subspace **whose dimension depends on `rcond`**. The significance then becomes a function of a
  numerical tolerance — **which is exactly the object the note already quarantined**
  (Fig. `compare_3d_fullcov`, *"χ²/ndf versus eigenvalue tolerance"*, `sec_3d.tex:231-236`). A design
  that lands here recreates the retired figure.
- **`d ≤ rank(C)`:** full rank is *possible* but **not guaranteed** — `M`'s rows can align with the null
  space. **It must be measured, never assumed.**

### 3.2 Generator MC statistics. An empirical estimate, and it is optimistic.

The prediction is itself a Monte Carlo estimate. With `N_CC = 1.48e6` (`:297`) — an **upper** bound,
since the note does not state the phase-space-surviving count — a uniform split gives:

| `d` | events/cell | generator MC stat error |
|---:|---:|---:|
| 6 | 246,667 | **0.20%** |
| 7 | 211,429 | 0.22% |
| 42 | 35,238 | 0.53% |
| 1,431 | 1,034 | 3.11% |
| **10,694** | **138** | **8.50%** |

Against deficits of **7.2–27.9%**, generator MC error is negligible at `d ≈ 6–7`, marginal at
`d ≈ 42`, and at full grid resolution **comparable to the smallest deficit under test.** Uniform is
optimistic: the dip bins hold well under `1/d` of the rate, so the realised error in the bins that
carry claim (b) is larger than the table shows.

### 3.3 The uthrow inflation. The strongest of the three, and it was nearly mis-stated.

The relayed inflation `g` multiplies `√trace` by **1.333 (mean-centred) / 1.431 (CV-centred)**.
Since `g` scales every σ, `χ² → χ²/g²`. **`Z ∝ 1/g` is exact only at `ndf = 1`** and is wrong in the
optimistic direction as `ndf` grows — a multi-bin test loses **more** to the inflation, not less.
Recomputing exactly through `chi2.sf` at the stated `ndf`:

| `ndf` | nominal `Z = 3.00` becomes (mean-centred) | (CV-centred) | the `1/g` shortcut would have said |
|---:|---:|---:|---:|
| 1 | 2.25 | 2.10 | 2.25 ✓ |
| 6 | **1.75** | **1.50** | 2.25 ✗ (+0.50) |
| 36 | **0.73** | **0.40** | 2.25 ✗ (+1.52) |
| 42 | **0.62** | **0.30** | 2.25 ✗ (+1.63) |

**⚠ A 33% uncertainty inflation destroys a 3σ result at `ndf = 36` (→ 0.73σ) but leaves 1.75σ at
`ndf = 6` and 2.25σ at `ndf = 1`.** All three constraints therefore point the same way, and the
third points hardest: **the test must be low-dimensional, and a 1-dof test is worth substantially
more than a 42-bin one.**

Two caveats I will not paper over. First, **the centering convention alone moves the answer by
0.25–0.33σ** and must be declared as part of the contract, not chosen at analysis time. Second,
**`D_Z^c` in `z_assembly.py:4` multiplies only `Σ_V C_b`**, not `C_stat + C_ML + Σ_A L_b`, so the
effective inflation on the *combined* object is smaller than 1.333 by however much stat+ML
contribute — **and I do not know whether the relayed `√trace` was of the systematic sum or of the
combined object.** The table above is therefore an **upper bound on the damage**, and which it is
is one line to measure (§6.1).

---

## 4. Hypotheses and the candidate set

### 4.1 Four point nulls are not one test, and ranking them is not a significance

Each prediction is a **fixed, parameter-free** curve. So `H_g: data = prediction g` is a legitimate
point null with a well-defined goodness-of-fit p-value. But the four are **not nested and not
exhaustive**, so:

- **Reporting all four goodness-of-fit values, each as its own pre-declared statement, is
  legitimate** and incurs no selection penalty.
- **Ranking them is not a significance statement.** The note already retired exactly this — *"The
  historical truncated-spectral scan ranked Tune v1 closest and GiBUU farthest, but its covariance
  is superseded"* (`:222-225`). The ranking must not return through a new covariance.

### 4.2 Keep all four — and add the fifth, which is the only one that can carry the conclusion

**Yes, keep all four.** They span the model space in the way the claim requires: bare GENIE CV has
**no 2p2h and no RPA** (`mec = 0` for all `1.48e6` CC events, `:296-298`); Tune v1 layers MINERvA's
empirical low-recoil enhancement and RPA on stock Valencia; NuWro and GiBUU carry **native,
un-enhanced** 2p2h from independent codes, one of them transport-theoretic. Four is the minimum that
distinguishes *"the MINERvA tune is doing something special"* from *"every model is short."*

**But the fifth prediction is not optional.** `genie_mefhc_mec_ALL.gst.root` — GENIE CV with
`--event-generator-list Default+CCMEC` — **already exists**, and it is the **only prediction nested
with a candidate**: the note's own construction adds MEC on top of an MEC-free base
(*"Any 2p2h is therefore added, not reweighted"*, `:299`). **Nesting is what makes a significance
possible.** Without it there is no legitimate test of claim (c)/(d), only non-nested goodness-of-fit
numbers that cannot say *"the shape and size match 2p2h."*

### 4.3 Two asymmetries in the candidate set that the covariance does not cover

**⚠ (i) NuWro and GiBUU are on a C target; GENIE and Tune v1 are on CH** (`:175`, `:182-183`, `:184-185`).
Per-nucleon normalization absorbs the bulk of this but **not the nuclear-model part, and 2p2h scales
with the initial-state n–p pair content** — so the residual target mismatch lands **precisely in the
dip region that carries claim (b)**. This is not a covariance defect and no covariance treatment
fixes it. **Consequence for the design: the primary dip test must run on the GENIE CV / GENIE+MEC
nested pair, where the target is common by construction.** NuWro and GiBUU enter as pre-declared
secondary context. **This — and only this — is where fresh production would buy something: a CH
NuWro or GiBUU sample.** It is a real ask and it is *not* needed for the primary test.

**⚠ (ii) Tune v1 is the unfolding prior, and nothing in the assembly covers the pull toward it.**
`build_fps_prior_nuwro_5d.py:11` states the nominal shape as
`[NuWro truth shape] / [MnvTune-weighted GENIE truth shape]` — **the denominator is the prior.**

**I first argued this from the band registries, and that argument does not cover its own claim.**
The authoritative partition is `z_contract.py:66-71`: `V = 13` (`adopt_unified_5d.VERT_BANDS`),
`A = 5` (`p4_lib.BANDS` — the kinematic lateral shifts, **not** the 9-entry
`assemble_gbdt5d_adopted.LAT_BANDS` I first cited, which adds the four `MinosEfficiency`/`GEANT_*`
weight bands), and `N_BANDS_TOTAL = 45` with **`R = 27` DERIVED AS THE REMAINDER AND, in the
contract's own words, "never listed."** So **27 of 45 band names are unavailable from the contract by
construction**, and an absence claim resting on the registries I grepped covers **22 of 45** band
names — 13 in `V`, 5 in `A`, 4 falling in `R` — leaving **23 uncovered**. That is inference
from absence over a non-covering population, and I withdraw it as stated.

**The architectural argument does cover, and it is the stronger one.** `z_assembly.py:4` is SPEC
§1.3a's identity with **five terms** — `D_Z^c(Σ_V C_b)D_Z^c`, `Σ_R C_b`, `Σ_A L_b`, `C_stat`, `C_ML`
— and gate **G1** checks closure against *"its declared parts,"* so the term list is complete rather
than indicative. **None of the five is a prior or re-unfold term.** A band is a reweight or a
kinematic shift applied to a **fixed** estimator; changing the prior **re-runs OmniFold** and yields
a different central value, which is why the tree carries a *separate* construction for it
(`fps_3prior_envelope_5d.py`, `sbatch_fps_reunfold_5d.sh`) that produces an **envelope appearing in
none of the five terms.** `C_ML` is a **training-seed** variation of one estimator, not a prior
variation.

**The covering search, if the enumeration is wanted anyway:** the 44 file-backed band names are
printed in the producer log the brief already cites, `fin5dBKG_55912230.out`. **And that count
reconciles exactly** — 44 file-backed bands **+ the analytic `__Normalization_flat` = the contract's
45** — which disposes of the BAND half of one of my residues below, though not its file half.

So **the candidate the unfolded result was seeded from is the one the covariance is least equipped
to penalise.** The note's central values are consistent with that: both GENIE-family predictions are
closest and both independent generators are farthest, on both ranges of §2. **I cannot separate
"prior pull" from "the tune was built to fit MINERvA data" from central values alone** — which is
exactly why it must be measured rather than argued (§6.2). A design that quoted a Tune v1
significance without that measurement would be quoting the prior's own agreement with itself.

---

## 5. Normalization treatment — the choice that decides whether the test discriminates

All four models under-predict the rate by 12–28%, coherently. **Each verdict below is written to
survive being read alone and apart from the others.**

| treatment | mechanics | **VERDICT** |
|---|---|---|
| **(N1) Absolute** — no normalization freedom | `χ² = Δᵀ C⁻¹ Δ` on the cross section as measured | **REJECT as the primary test; REPORT as secondary.** It is dominated by a coherent rate offset that is *the same statement in every region*, so it cannot localize anything. Its likely output — "all four excluded" — is true, uninformative, and **does not support claim (b) or (c)**, which are about *where* and *what shape*. Rejected for lack of discrimination, **not** because it is wrong. |
| **(N2) Area-normalized** — rescale each prediction to the data integral over the test region | one scale per prediction, fixed by construction; `ndf → ndf − 1` | **ACCEPT as the primary treatment.** It asks "is the *shape* wrong", which is the note's actual claim. Conditions: the rescaling applies to the **prediction only** — never to the data and never to `C` — and the region over which the area is matched is **part of the declared test**, since matching over the full support and over the displayed range are different tests with different answers. |
| **(N3) Profiled** — one free scale with a Gaussian nuisance penalty | minimize over `α`, penalty `σ_α` | **ACCEPT only with the penalty width DERIVED, not chosen** — otherwise `σ_α` is a free dial that sets the answer. ⚠ **The existing `__Normalization_flat` at `σ = 0.014` cannot serve:** 1.4% is far too tight to absorb a 12–28% deficit and would convert the whole offset into χ². The defensible width is the **coherent flux normalization uncertainty**, which must be measured (§6.1). Until it is, N3 is not executable. |

**Reuse, with one trap.** `gen_to_xsec_eavailW.py:70` already exposes
`--norm {splines,shape}` with `--shape-total`, which is N2's mechanics. ⚠ **But `--shape-total`
defaults to `1.0`** — normalizing to unity, not to the data integral. Reused unchanged for this
purpose it silently implements a *different* test. The default must be overridden explicitly and the
value recorded in the receipt.

---

## 6. The smallest measurements needed — none of them run here

Each is specified so that whoever holds the product can execute it; **I have launched nothing.**

**6.1 The coherent rate uncertainty, per band.** `√(uᵀCu)/uᵀx` for the **width-weighted** rate
functional `u`, computed **per band and then summed**. The per-band split is the point: it separates
the coherent part (flux, normalization) from the incoherent part, and that separation decides
whether an absolute test can say anything and supplies N3's penalty width. It also settles whether
the relayed `√trace × 1.333` was of `Σ_V C_b` or of the combined object (§3.3).
**Instrument exists — `z_build_path.full_support_rate_functional` / `destination_widths`; zero new
code.** ⚠ **Width-weighting is mandatory: the stored values are differential densities per unit
bin-volume, so unit weights are simply wrong** — on this axis they would give the 97 GeV catch bin
the same weight as the 0.1 GeV first bin, a **970×** volume error (§2).
⚠ **I did not run it.** The only covariance available today is the historical 4D/3D object the note
explicitly quarantines (`:239-247`, *"all covariance-dependent 3D comparisons are gated on that
product"*), and producing a number from it — even to size a design — is the gated act.

**6.2 Prior dependence, and it is nearly free.** Re-unfold with the NuWro-shaped prior and measure
the shift **in the test region**, not globally. **There is no analytic argument for prior
independence; it has to be measured.** Instruments exist: `build_fps_prior_nuwro_5d.py`,
`fps_3prior_envelope_5d.py`, `fps_gbdt_prior_reunfold_5d.py`, launcher
`sbatch_fps_reunfold_5d.sh`. Declared wall `--time=06:00:00`, one task, 32 CPU, 120 G →
**≤ 6 task-hours per prior, ≤ 18 for three.**
⚠ **A `--time` REQUEST, not a measurement** — an upper bound from the launcher; `sacct ElapsedRaw`
not queried. **Against the endpoint-A pilot's 1,284–2,028 task-hours, endpoint B's most important
precondition costs 0.9–1.4% of it** — 18 against 2,028 and against 1,284 respectively — **or 0.47%
for a single prior.**

**6.3 Full rank of the projected covariance.** `λ_min/λ_max` of `M C Mᵀ` with its `rcond`, recorded
as a named field. Required by §3.1 and **not assumable at any `d`**.

**6.4 The systematic-subspace support fraction of the residual — and it is free.**
`f_in = ‖P_syst Δ‖² / ‖Δ‖²`, where `P_syst` projects onto the span of the band directions. §3.1
proves the systematic model spans only 141 of 10,694 directions. **If the data−model difference lies
largely outside that span, a large χ² states that the systematic model has no direction in which to
absorb the difference** — which may be a real discovery or a missing systematic, and the χ² alone
cannot tell them apart. **`f_in` is the measurement that distinguishes them, and it is a by-product
of the eigendecomposition that endpoint A's clause-(iii) scan is already obliged to produce** — a
genuine synergy at zero marginal cost.
I propose `f_in` be **reported unconditionally beside every significance**. **I do not propose a
threshold on it** — that is a scientific judgement, and inventing a number here would be exactly the
unapproved-default failure.

**6.5 The generator MC covariance.** The per-cell event counts, a histogramming by-product. Required
in `C` whenever `d` is large enough for §3.2 to matter.

**6.6 `g`'s distribution over the test's own support.** The global median `1.000` does not describe a
sub-region, and the relayed **max is 22.45** — if the test support contains that bin it dominates.
Report min/median/max restricted to the test's support, not the global summary.

---

## 7. The proposed tests

> **On the label.** `GB-*` is a **new namespace** and deliberately does not reuse `B-n`. Endpoint B
> already has `B-2`/`B-3`/`B-4` outstanding, and **I did not re-read their content this session** —
> so nothing here renumbers, supersedes, or discharges them. Whoever composes the endpoint-B
> requirement set should reconcile the two namespaces rather than assume I did.

**Primary — GB-P1, and it is the only test that carries the physics conclusion.**
A **one-parameter nested fit** of the 2p2h strength `α`, on the pre-declared dip region
`E_avail ∈ [0.10, 0.40)`, treatment N2, prediction family `GENIE CV + α · (GENIE+MEC − GENIE CV)`.
`α = 1` is stock Valencia. Output: `α̂ ± σ_α` at **1 dof**, plus the post-fit goodness of fit.

Why this and not a four-way comparison: it is the **only** available test that is nested (§4.2),
target-matched (§4.3 i), prior-neutral in the sense that both members share the prior's generator
family, and at **`ndf = 1` where §3.3 shows the inflation costs least.** It answers claims (b), (c)
and (d) together — a fixed-shape template absorbing the residual at the empirical magnitude *is* the
statement "the shape and size match 2p2h, localized in the dip."

**Secondary, pre-declared, each reported as its own statement and none as "the" significance:**
per-prediction goodness of fit for all five predictions on (i) the displayed `E_avail` range
(catch dropped) and (ii) the full support, treatment N2 primary and N1 reported beside it.

**Global or region-specific? Both, and the distinction is not a display convention.** §2 shows the
range choice **reverses which model is closest**, so both must be reported and neither may be
selected after seeing the other. Joseph's ruling that the catch bin is a **display** exclusion and
not an exclusion from declared support is what makes this coherent: the bin stays in the declared
support and in the covariance, while the test functional gives it zero weight. Those are different
acts and the receipt must show both. `check_rate_closure`, `full_support_rate_functional` and
`displayed_range_rate_functional` in `z_build_path.py` already express exactly this pair.

**⚠ Why the primary set must be this small: multiplicity.** The design's own axes of choice — 5
predictions × 4 regions × 3 normalizations × 2 observables — span **120 candidate significances.**
If one is quoted having been selected as the most significant, then under independence a nominal
**3.00σ degrades to 1.09σ, and even a 5σ to 3.98σ**. Independence is the **worst case** here, since
tests sharing data and covariance are strongly correlated, so the true inflation is smaller — it is
a bound in the conservative direction. For a nominal 3σ to survive as ≥2.5σ the pre-declared set
must be **at most four**. Hence: **one primary, declared before it is run, with the secondaries
carrying their secondary status on them.**

---

## 8. Three defects in the instrument that would be inherited

Both in `nd-unfolding/eavail_generator_significance.py`, measured at `258bddc2`:

**8.1 `ndf` is the bin count while the inverse is a pseudo-inverse.** `:132` computes
`Δ @ pinv(C_y) @ Δ` and passes `ndf = n_ea = 7`; `:133` does the same on the sub-block with
`ndf = hi.sum()`. **`pinv` drops directions and does not report how many it kept**, so if `C_y` is
rank-deficient the χ² and its `ndf` disagree silently. The script *prints* a condition number
(`:104`) and then never uses it to set `ndf`. Both errors here happen to point toward
**understating** significance — but neither is a bound, and with a near-singular `C_y` the
amplification of retained small-eigenvalue modes can reverse the direction.

**8.2 The significance convention is mislabelled, in the direction of the larger number.**
`:111-113` computes `p = chi2.sf(χ², ndf)` then `z = norm.isf(p/2.0)` under the comment
*"one-sided Gaussian-equivalent significance"*. **`isf(p/2)` is the two-sided equivalent and is the
larger of the two:** at `p = 0.01` it returns **2.576** where one-sided is **2.326**; at `p = 0.05`,
**1.960** vs **1.645**. Not a rounding difference, and the mislabelling favours the bigger number.
**The convention must be declared in the contract and asserted in the receipt.**

**8.3 The map, as the brief says, must not be inherited.** `:85-88` builds the 4D→1D map inline over
the legacy 7-bin binning with **no both-direction support check and no refusal**. One thing it does
get right and a replacement must preserve: the weight is `dpt·dpz·dq3` and **deliberately excludes
`dea`** (`:69`, `_dea` unused), which is the correct density treatment for `dσ/dE_avail`. A
replacement should route through the `project_cov_nd` + both-support-arms repair already specified
for endpoint A rather than re-deriving a map — that repair is **code not yet written**, and it is the
same gap in both endpoints.

---

## 9. What the test must show — the anti-laundering clause, stated as terminal outcomes

Joseph's instruction is that **no significance may enter the manuscript merely because covariance
construction or numerical stability passes.** Stated mechanically:

> **A-1…A-7 passing licenses the uncertainty. It does not license the test.** Construction
> correctness and numerical stability are preconditions for the *denominator*; they say nothing about
> whether the *numerator* — the data−model difference — means what the manuscript says it means.
> **§3.1 is why this is not a formality:** a covariance can be correctly constructed, numerically
> pristine, and still span only 141 of 10,694 directions. **`f_in` (§6.4) is the measurement that
> detects that, and it is not implied by any endpoint-A criterion.**

For **GB-P1**, the terminal outcomes, all four of which must be stated before it runs:

| outcome | condition | what may be written |
|---|---|---|
| **SUPPORTS the claim** | `α̂` significantly `> 0`, **and** `α̂` consistent with the empirical/Valencia magnitude the note cites, **and** post-fit goodness of fit not rejecting, **and** `f_in` reported | the note's claim (b)+(c)+(d) may be stated with `α̂ ± σ_α` |
| **PARTIALLY supports** | `α̂ > 0` significantly but the required magnitude is far from the known value | *"the data require a component in the dip"* — **but calling it 2p2h is then unsupported** |
| **REFUTES** | `α̂` consistent with 0, **or** post-fit goodness of fit rejects the template | the dip deficit is **not** 2p2h-shaped; the claim must be withdrawn or narrowed |
| **INCONCLUSIVE, and it must be reported as such rather than retried** | `C_y` not full rank at declared `rcond`, **or** prior shift (§6.2) comparable to `α̂`'s effect, **or** `f_in` small | **no significance may be quoted**, and the remedy is the missing measurement — **not a different region, normalization, or tolerance** |

That last row is the one that matters. **The failure mode this design is built against is not a
wrong number; it is a correct number obtained by trying regions until one is significant.**

---

## 10. Residues — what I did not settle

1. **The §2 catch-fraction inconsistency is open** (three of four implied fractions outside the
   relayed range). One arithmetic check; it changes §2's table.
2. **One file, not one band.** §3.1 now reconciles the relayed inventory against
   `z_contract.py:66-71` and **all three band cells match exactly** (45 total, `R = 27`). The
   remaining gap is the **file** total: implied 187 against the relayed 188. Possibly a CV file, but
   that is a guess. **A one-line check in `fin5dBKG_55912230.out`, not a defect claim** — the
   inventory is the peer's measurement from a log I did not open.
3. **`Getq3True()`'s Q² convention is not established here.** `CVUniverse.h:207` defers to
   `PlotUtils/TruthFunctions.h`, **not vendored in this checkout**. Meanwhile `RecoQ3` uses the exact
   `Q² = 2E_ν(E_μ − p_μcosθ) − m_μ²` (`:215`) and `CalcTrueExperimentersQ2` uses the **massless**
   `4E_νE_μsin²(θ/2)` (`:392`). So **two Q² conventions coexist in the analysis**, and the generator
   side replicates only the second. **`W` is exactly replicable** — `gen_to_xsec_eavailW.py:49-61`
   reproduces `GetTrueExperimentersW` formula-for-formula, with the `M_n`-vs-`M_p` choice a declared
   1.3 MeV approximation against ~0.3 GeV bins. **`q3` is not verified replicable.** Independently,
   `build_fps_prior_nuwro_5d.py:8-9` **excludes `q3` on purpose** — *"the plan specifies
   (pT,p‖,Eavail,W), and adding q3 would only thin the per-cell statistics."* **So the generator-test
   axes should be `(pT, p‖, E_avail, W)`, reusing a choice already made in the tree for a reason that
   holds here too** — not a new proposal.
4. **I have proposed no numerical thresholds**: not `f_in`'s floor, not `α̂`'s acceptance window, not
   `rcond`, not the region boundaries beyond the note's own dip definition. Each is either a
   scientific judgement or awaits a §6 measurement. **`[0.10, 0.40)` is the note's own dip, cited,
   not chosen by me.**
5. **The `g` centering convention is undeclared** and worth 0.25–0.33σ (§3.3). It belongs in the
   contract.
6. **The three generator scripts are not behind `READERS`**, so any ND extension must touch three
   files or unify them first. I have not written either, and **I should not** — I would then be
   reviewing my own implementation of my own design.
7. ⚠ **One argument in this document was withdrawn during its own review, and the withdrawal is
   recorded in place rather than quietly repaired** (§4.3 ii). I first argued "no prior systematic
   exists" from the band registries. Those registries name **22 distinct bands of 45** — 13 in `V`,
   5 in `A`, and 4 that fall in `R` — **leaving 23 uncovered**, because `R = 27` is derived and never
   listed. (The contract's own two imports name only 18.) **An absence claim over a non-covering
   population is void, not weak.** The
   replacement is architectural and does cover. I note it because the first version read as fully
   sourced — it cited two files and a line range — and **citing files is not the same as covering the
   population.**
8. **"Lateral" names two different sets in this tree, and a reader who equates them mis-assigns four
   bands.** The Z contract's `A` is `p4_lib.BANDS` — **5** kinematic shift bands; the assembler's
   `assemble_gbdt5d_adopted.LAT_BANDS` is **9**, adding `MinosEfficiency` and three `GEANT_*`, which
   `pet_lateral_band.py:65-67` separates as `WEIGHT_BANDS`. Those four are absent from `VERT_BANDS`,
   so they fall in `R`. **Not a defect** — a naming collision — and it does not change the inflation,
   since `D_Z^c` applies to `Σ_V` alone and both `A` and `R` sit outside it. Flagged because I
   tripped on it above.
