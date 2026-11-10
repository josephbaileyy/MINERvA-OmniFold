# RPL DECLARATION: locating the run-period step, three referee checks (2026-11-10, revision 2, DRAFT for the director's binding)

**By** the valid-region lane (director-helper-2), for the director, on Joseph's go relayed by the director
(2026-11-10). This is a draft: nothing here runs before a binding and each connect's go.

**Nothing has been computed.** No ratio, fit, split or reading in this declaration's sense exists yet.
<!-- absence-ok: a statement about this draft's own status before binding, not a claim that a result does not exist -->

## The question

**The paper's step.** The paper reports a reconstruction-level step between playlist groups near p_∥ ≈ 8 GeV/c:
- 1G–1M against 1A–1E, +6.10 % (`2d-closeout/period-unfold-20261014/REPORT.md:63`, from
  `2d-closeout/playlist-spread-20261014/outputs/ref_shape.json` `1G-1M_vs_1A-1E.by_pz`);
- after per-period unfolding, the double ratio is +(6.94 ± 0.41) % (`period-unfold-20261014/REPORT.md:57,64`), and the
  Supplement quotes +(6.89 ± 0.46) % (`supplement-confirm.blind.txt@879b9501:1231`);
- its cause is stated as unknown.

**The referee's request.** The blind Claude referee of the confirming round (`referee-methods-confirm-20261110/claude.txt@879b9501`
M6, :116-123) asks for basic localization:
1. fit the step as an effective muon-momentum scale shift per period, and compare it with the lateral muon-energy
   band's size;
2. split it by the muon-momentum measurement method (range or curvature in MINOS), and by any recorded beam or
   detector configuration;
3. say whether the published analysis saw or treated it.

## What already exists (read, not recomputed)

- **The bands at the unfolded level** (`playlist-spread-20261014/coverage/REPORT.md` §3.1):
  - `Muon_Energy_MINOS`'s step sd is 3.03 %, but its universes tilt the p_∥ marginal rather than step at 8 GeV/c;
    the best cos² with the 1G–1M shape is 0.25;
  - the Flux band carries no p_∥ step (sd 0.17 %).
- **The bands at reco level** (§3.2): every band acts alike in all playlists. As 1G–1M-against-1A–1E differences, the
  bands' step sd in quadrature is 0.40 %, against the observed +6.10 %.
- **The recorded playlist conditions** (`data-survey-20261022/outputs/pages/minerva-playlists.txt`, the MINERvA
  playlists page as read 2026-10-22):

  | playlists | beam comment | water target | helium target | slip stacking |
  |---|---|---|---|---|
  | 1A–1E | none | empty | empty → filling → full (1A empty, 1B filling, 1C–1E full) | 6+0 |
  | 1F | none | empty | full | 6+2 |
  | 1G | **tilted horn** | empty | empty | 6+4 |
  | 1L, 1M | **tilted horn** | full | empty | 6+4 |
  | 1N | none | full | empty | 6+4 |
  | 1O, 1P | none | full | filling (1O), full (1P) | 6+4 |

  - **The step group 1G–1M is exactly the tilted-horn set.** No split of the data can separate "tilted horn" from
    "that period".
  - The helium target empties at 1G, the start of the same set, and stays empty through 1N. The water target fills
    at 1L, inside it.
  - The flux files the code applies follow the same grouping: 1D, 1M and 1N
    (`playlist-spread-20261014/REPORT.md` §3.1).
- **RPD-RECO** (`FD-RPD-RECO-DECLARATION.md`, OI-204, owner limitation-resolver; design bound, code next). It will
  compute, from 24 pinned per-playlist dumps:
  - the per-playlist reco data/MC offsets on the p_∥, p_μ, θ_μ and p_T axes (d1);
  - the per-playlist step s_obs,X;
  - a flux-swap test of the tilted-horn flux file (d2: TRACKS / PARTIAL / DOES-NOT-TRACK).
- **RPD-RECO's limits.** It is frozen before any data/MC comparison is read from those dumps. The dumps hold no MINOS
  category or curvature (`FD-RPD-RECO-DECLARATION.md` §1).

## Scope, inputs and price (step 1)

| check | inputs (path, pin) | where | price |
|---|---|---|---|
| **(i) scale fit** | RPD-RECO's 24 pinned dumps `/pscratch/sd/j/josephrb/fd-rpd-20261103/dumps/lat_<PL>{,_bkg}.npz` (`fd/rpd-reco/INPUTS.sha256`): `measured`, `MCreco`, `w_reco`, `pass_reco`, `bkg_reco`, `bkg_w`, `data_pot` | login connect, O_NOATIME | 0 node-h |
| (i) the band's size | the lateral muon-energy bands' ±1σ shifted reco kinematics in the per-playlist universe files `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_<PL>_universes_full.root` (`sim_pz` and its `Muon_Energy_MINOS_<i>`, `Muon_Energy_MINERvA_<i>` shifted branches). It reads the first 500k `mc_signal_reco` rows per playlist in **file order**, as the coverage study did; that is not a random draw. MAT-MINERvA's source of the shifts is quoted by file:line@sha from the cluster checkout | login connect | 0 node-h |
| **(ii-a) MINOS method**, the inventory | the branch lists of MP-1's 12 per-playlist zero loops `$P/measurement-paper/phase1/mp1/s1/evloop/zero/runEventLoopOmniFold_5D_<PL>_zero.root` (pinned in `nd-unfolding/fd_ct_period_inputs.py` `ZERO_LOOPS`), and of one data and one MC AnaTuple. It asks whether the zero loops carry `ev_run`/`ev_subrun`/`ev_gate` (data) and `mc_run`/`mc_subrun`/`mc_nthEvtInFile` (MC), **and** whether either side carries a slice or physics-event index (`n_slices`, `slice_numbers`, `physEvtNum` in the AnaTuple). One gate can hold more than one entry (audit M6), so **the key includes the slice or physics-event index if one exists on both sides**; if not, the key's uniqueness is measured in the inventory itself. Each file is staged by an O_NOATIME copy to /dev/shm, one at a time | login connect | 0 node-h |
| (ii-a) the join | only if the inventory finds a unique key: the AnaTuples' `MasterAnaDev_minos_used_range` / `_used_curvature` (`data-survey-20261022/outputs/followup/branches_fhc_data_1B.json`), read for the selected events' keys only. Data: 1,818 files, 0.994 TB; MC: 489 files, 10.706 TB (`data-survey-20261022/SURVEY.md:28`); a few branches each | one CPU job, after a one-file-per-tier dry run measures the read rate | estimated 0.5–1.5 node-h, priced by the dry run before any go |
| (ii-a) without a unique key | a new event-loop pass carrying the flag | jobs | several node-h; **not in this declaration**, which then reports (ii-a) as not made |
| **(ii-b) configuration** | RPD-RECO's pinned dumps (as (i)), and its record's per-playlist s_obs,X for the reproduction control | local or login, after P-RPD | 0 |
| **(iii) published analysis** | Ruterbories et al., Phys. Rev. D 104, 092007 (2021), arXiv:2106.16210 (`docs/analysis-note/technote.bib`, `MINERvA:2021owq`), and its arXiv ancillary files' README. "Supplemental material" here means the arXiv ancillary set (`https://arxiv.org/src/2106.16210v4/anc/`), not the journal's. The MINERvA web pages under `data-survey-20261022/outputs/pages/` are **not** inputs of (iii) (audit m5) | local document read | 0 |

**Sequencing** (the director's rulings, 2026-11-10, and audit B1).

**Precondition P-RPD.** RPD-RECO's d1/d2 record is committed on main, and is named here by its sha256. Until then this
line reads "not yet". P-RPD gates every statistic below that forms a data/MC quantity on RPD's events:
- (i)'s fit;
- (ii-a)'s method-split statistic s^m and Δ, and any data/MC histogram of the joined rows. These read a data/MC p_∥
  step on the zero-loop events that RPD's dumps were made from (`FD-RPD-DECLARATION.md:186-187`), so they wait for
  RPD-RECO's record too (audit B1; the director's ruling);
- (ii-b).

RPL stays its own declaration; it is not folded into RPD-RECO.

**What can go first,** because none of it forms a data/MC comparison from RPD's events (limitation-resolver's answer,
2026-11-10):
- **RPD-RECO's pins.** RPD-RECO reads only its 24 dumps (`fd/rpd-reco/INPUTS.sha256`) and, for d2, MAT's flux files.
  No RPD-RECO gate checks the zero loops, the per-playlist universe files or the May CV files.
- **(ii-a)'s inventory, its dry run, and the join itself.** The inventory reads branch names. The dry run, which prices
  the join, reads AnaTuple flags for one file per tier. The join only attaches flags to keys. Each comes to the director
  with its sha256 before it runs. If no unique key exists, (ii-a) is reported as not made; a new event-loop pass needs
  its own decision.
  - The MP-1 zero loops were noted with purge exposure around 2026-12-15. That is re-checked by stat first, and
    O_NOATIME reads do not refresh it.
- **(i)'s band-size measurement** is MC only. limitation-resolver's condition is kept: the band sizes are not printed
  beside, or compared with, any per-playlist data step until P-RPD holds.
  - **Before that read,** the per-playlist `_universes_full.root` files are checked against the cov2d session's
    protected list, and `cov2d_fence.sh` runs. That is the committed
    `fd/tier2-20261110/t2a/code/cov2d_fence.sh`, sha256
    `16a2a5cd5e36f0a3d48577afd3c4b1d4adebe6baf72fcf228d7c85275739754a` (audit m6).
  - RPD-RECO's policy lists the pooled `runEventLoopOmniFold_MEFHC_universes_full.root` and the CFS
    `runEventLoopOmniFold_MEFHC.root` as COV2D-protected (`fd/rpd-reco/prologue5-20261108/policy-config.json`). The
    per-playlist files sit in the same directory, so the cov2d session is asked first.
  - Every read is an O_NOATIME copy.
- **(iii)** reads a published paper and depends on nothing else. It has run: see `iii/README.md`.

## (i) The scale fit, fixed

**The statistic.**
- The fit is for **PB = {1G, 1L, 1M} only**, against PA = 1A–1F (RPD-RECO's groups), on RPD-RECO's p_∥ bins (1.5, 2,
  3, 4, 5, 6, 8, 10, 15, 20, 60 GeV/c) and its overflow bins (audit M1).
  - The double ratio is D_PB(b) = r_PB(b) / r_PA(b), with r = N/P as RPD-RECO §2 defines it.
  - α̂ for PC (1N–1P) and the per-playlist α̂_X are reported as descriptions, with no outcome.
- **The model:** PB's data muon momentum is scaled, p_μ → p_μ/(1 + α), with p_T and p_∥ scaled together so θ_μ is
  unchanged.
  - **The whole measured set is rescaled, overflow included, and re-binned** (audit m3). The event loop applies no reco
    p_∥ or p_T cut; its reco cuts are the fiducial volume, θ < 20°, the MINOS match, dead time and
    the neutrino (charge) requirement (`runEventLoopOmniFold.cpp:1710-1715`), and 1.5/60/4.5 GeV/c are truth phase space (:1737-1740). So rescaled rows
    move between the window and the overflow bins, and that is kept.
  - A free normalization k is profiled.
- **The fit:** α runs over [−10 %, +10 %].
  - It is a coarse scan in 0.5 % steps, then a fine scan in 0.01 % steps over ±0.5 % around the coarse minimum, then a
    parabola through the three fine points nearest the minimum. α̂ is the parabola's vertex, and the fine-grid minimum
    is reported beside it (audit m1).
  - χ²(α, k) = Σ_b (k·D_PB,α(b) − 1)² / σ_b². **σ_b is RPD-RECO's paired-bootstrap σ of D_PB(b) evaluated at α = 0,
    and held fixed over α** (audit m1). Its change with α is second order in α, and α̂'s σ below does not use it.
- **The errors:** σ_α is the SD of α̂ refitted on each of RPD-RECO's 200 paired-bootstrap replicas (its seeds), with
  the same scans.
- **Reported:** α̂ ± σ_α; χ²_0 (α = 0) and χ²(α̂), each with ndf; α̂_PC and α̂_X (descriptive); and the published
  analysis's 1 % muon energy scale (`iii/README.md`, quote 3b) beside σ_band.

**The comparator, the band's size.**
- σ_band is the ±1σ fractional p_μ shift of `Muon_Energy_MINOS`: the **`w_reco`-weighted** median of
  |p_μ,shifted / p_μ − 1| over `pass_reco` rows, overall and in the p_∥ < 8 and ≥ 8 strata (audit m2).
- `Muon_Energy_MINERvA`'s shift is measured the same way and **is descriptive only**; only MINOS's enters the outcomes
  (audit m2).
- **What the band is** (audit M3): the band shifts every playlist alike (`playlist-spread-20261014/coverage/REPORT.md`
  §3.2), so it cannot represent a scale of PB relative to PA. **The comparison is one of magnitudes only:** is a
  per-period scale of α̂'s size within the size of the muon-energy uncertainty? It is not a statement that the band
  covers the step.

**Outcomes, evaluated in this order; exactly one applies** (audit M1):

| # | outcome | condition |
|---|---|---|
| 1 | **NO-STEP** | RPD-RECO's R-d1.0 reads NOT-SEEN-AT-3σ for PB. No fit is read |
| 2 | **AT-SCAN-EDGE** | α̂ (or the coarse minimum) is at −10 % or +10 %. No further reading |
| 3 | **NOT-A-SCALE** | P(χ²_ndf(α̂) > χ²(α̂)) < 0.01. A per-period momentum scale does not reproduce the step's shape |
| 4 | **SCALE-BEYOND-BAND** | |α̂| − 2σ_α > σ_band |
| 5 | **SCALE-WITHIN-BAND** | |α̂| + 2σ_α ≤ σ_band |
| 6 | **SCALE-UNRESOLVED-AGAINST-BAND** | otherwise: α̂ is compatible with both sides of σ_band at 2σ_α |

Outcomes 4–6 are read with the band's nature stated beside them: a magnitude comparison with an uncertainty that is
common to all playlists.

## (ii) The splits, fixed

**(ii-a) MINOS method** (its statistic after P-RPD).
- **The method partition** (audit M7). Every selected event is counted as range-only, curvature-only, both flags or
  neither flag, in data and MC.
  - If range ∪ curvature covers less than 99.9 % of the selected weight on either side, or "both" exceeds 0.1 %, that
    is a STOP: (ii-a) is not made.
  - The counts are reported.
- **The reproduction control** (audit M7). On the joined zero-loop rows, unrestricted by method, the R-d1.0 statistic
  must reproduce RPD-RECO's recorded s_PB within 0.1 σ_s, where σ_s is RPD-RECO's.
  - It is not to 10⁻¹², because the dumps are not the zero loops row for row. The dumps dropped 33–511 rows per
    playlist for non-finite truth support (about 10⁻⁴ of the weight), and their MC weights are scaled to each
    playlist's own data POT; the control applies the same POT scaling.
  - A failure is a STOP.
- **The statistic.** For m ∈ {range, curvature}, s^m is R-d1.0's s_PB with both data and MC restricted to events whose
  MINOS momentum used method m. The difference is Δ = s^range − s^curv, with σ_Δ from the paired bootstrap on the same
  rows.
- **The method fraction** in each p_∥ bin is reported. Range-measured muons are the stopping ones, so method and
  momentum are correlated; the fraction shows that confound.

**Outcomes, in order:**
1. **NOT-TESTABLE (method m):** m holds under 5 % of the weight on either side of 8 GeV/c.
2. **METHOD-DEPENDENT:** |Δ| ≥ 3σ_Δ, naming the method that carries the larger step.
3. **NOT-METHOD-DEPENDENT-AT-THIS-SENSITIVITY:** otherwise, with σ_Δ stated.

**(ii-b) Configuration** (after P-RPD).

**The statistic** (audit M5).
- RPL computes, from RPD-RECO's pinned dumps with RPD-RECO's R-d1.0 recipe and its paired bootstrap (B = 200, its
  seeds), each step against the PA pool:
  - s_1G;
  - s_1LM, for 1L and 1M **pooled** as one group (R = ΣN / ΣP over both, as RPD-RECO's R_G; 1L holds 0.13 and 1M
    2.1 × 10²⁰ POT);
  - s_1N and s_PC;
  - s_PB.
- **Every difference's σ comes from the same replicas,** so the shared PA reference is carried.
- **The control:** RPL's per-playlist steps equal RPD-RECO's recorded s_obs,X to 10⁻¹² relative. A failure is a STOP.
- limitation-resolver is told that RPL recomputes the replicas itself, so RPD-RECO need not store them.

**Readings, each with the magnitudes printed beside it** (audit M4, m4).
- **The tilted-horn set:**
  - **ALIGNED-WITH-1G–1M:** each of 1G, 1L and 1M has s_obs,X ≥ 3σ_X, and every other playlist has |s_obs,X| < 3σ_X;
  - otherwise **NOT-ALIGNED**, with the playlists that break it.
  - The per-playlist s_obs,X and σ_X are printed beside the reading, because at these statistics a 1 % step elsewhere
    breaks a significance-only rule.
  - The step group is exactly the tilted-horn set, so horn and period cannot be separated.
- **1G against 1L+1M** (water empty against water full, inside the tilted-horn set). With d = s_1G − s_1LM and σ_d
  from the replicas:
  - **1G-DIFFERS-FROM-1L+1M** if |d| ≥ 3σ_d;
  - **1G-CONSISTENT-WITH-1L+1M** if |d| < 2σ_d **and** σ_d ≤ s_PB / 3, so that a difference of a third of the full
    step would have been seen at 3σ;
  - **UNRESOLVED** otherwise.
  - The names describe playlists, not a cause: 1G and 1L+1M also differ in exposure.
- **1N** (helium empty, no tilted horn) and **1N–1P** (6+4, no tilted horn). For X ∈ {1N, PC}, with s_X and
  e_X = s_X − s_PB, both σ from the replicas:
  - **X-SHOWS-NO-STEP-OF-1G–1M's-SIZE** if |s_X| < 2σ(s_X) **and** |e_X| ≥ 3σ(e_X). It is consistent with 0 and
    inconsistent with the full step;
  - **X-SHOWS-A-STEP-OF-1G–1M's-SIZE** if |s_X| ≥ 3σ(s_X) **and** |e_X| < 2σ(e_X);
  - **UNRESOLVED** otherwise, including when s_X is consistent with both 0 and s_PB.
  - **These names describe the playlists, not a condition** (audit M4). 1N and 1N–1P differ from PA in water,
    helium, slip stacking and flux file at once (the conditions table; flux files 1D, 1M and 1N).

## (iii) The published analysis, fixed

**What is read:** the paper and its arXiv ancillary README (see the table above). The search terms are:
- playlist, run period, "1G", "1M", "tilted", "horn", "slip";
- MINOS range, curvature, muon energy scale;
- pile-up and intensity;
- "per-playlist" and "playlist-dependent".

Each hit is quoted verbatim with its section.

**There are two readings** (audit B2; the director's ruling).

**(iii-a) This step, a difference between run periods in the data.** Exactly one applies:
- **STEP-TREATED:** a stated correction or uncertainty for a difference between run periods, or between playlists, in
  the data, quoted.
- **STEP-SEEN-NOT-TREATED:** such a difference in the data is stated, with no treatment.
- **STEP-NOT-MENTIONED:** no hit states a difference between run periods or playlists in the data. The outcome carries
  its search line, and says nothing about what the analysis did internally.

**(iii-b) Time- or intensity-dependent modelling of conditions in general.**
- This reading is descriptive: the hits that state any time- or intensity-dependent modelling (calibration, overlay,
  efficiency) are quoted verbatim, with their sections.
- It has no outcome name, and it is not read as a treatment of the step.

The committed search output is re-read under this rule; no new search is run (the director's ruling).

## Controls

**Each is a STOP that reports the check as not made; nothing is repaired.**
- the input pins (RPD-RECO's `INPUTS.sha256`; `ZERO_LOOPS`);
- O_NOATIME on every pinned read;
- **The environment for every reproduction to 10⁻¹²:**
  - (i), (ii-a) and (ii-b) run in RPD-RECO's pinned environment (`FD-RPD-RECO-DECLARATION.md:247`): its numpy, thread
    caps of 1 (OMP, OPENBLAS, MKL, NUMEXPR) and nice 19, on a login node;
  - the reason is limitation-resolver's caution (2026-11-10): RPD-RECO's record keeps full float64
    (`fd_rpd_reco.py:344-350` at `9634aadf`), but a different BLAS threading or numpy can change the summation order
    of large sums beyond 10⁻¹².
  - If the environment cannot be matched, the run returns to the director before it starts, with a tolerance and its
    reason; it is not widened after a failure.
- (i): at α = 0 the code reproduces RPD-RECO's R-d1.0 s_PB to 10⁻¹² relative;
- (i): **the planted scale** (audit M2). The pseudo-data are built as the data are:
  - RPD-RECO's own C-0 recipe splits PB's pooled MC rows at random into a pseudo-data half and a prediction half, with
    seed `SeedSequence([20261110, 17, 1])`, and the same for PA;
  - the pseudo-data half's momentum is scaled by a planted α_true = +1.0 % **before binning**, over the whole set,
    overflow included, so rows move in and out of the window as the selection would;
  - the fit runs with its bootstrap on those rows.
  - **The tolerance:** |α̂ − α_true| ≤ 3.5 σ_α. The derivation of the false-STOP rate:
    - α̂ − α_true is close to Gaussian with SD σ_α;
    - σ_α is estimated from 200 replicas, so its relative standard error is about 1/√398 ≈ 5 %;
    - the rate is P(|Z| > 3.5 · σ̂_α/σ_α);
    - at σ̂_α/σ_α = 1 it is 4.7 × 10⁻⁴;
    - at 0.9, two standard errors low, it is 1.6 × 10⁻³;
    - at 0.8, a 20 % underestimate (four standard errors), it is 5.1 × 10⁻³.
    - So it is under 1 % even at a 20 % underestimate of σ_α, against about 32 % for the first draft's 1σ.
- (ii-a): the key is unique on both sides. The unmatched selected weight is reported, and above 0.1 % it is a STOP. The
  method partition and the reproduction control are as above;
- (ii-b): RPL's per-playlist steps equal RPD-RECO's recorded s_obs,X.

## Licence

**CITABLE FOR (once a binding's record lands):** each check's outcome, as defined above, and its numbers, as
descriptions of the reconstruction-level step.

**NOT CITABLE FOR:**
- **The cause of the step.** SCALE-BEYOND-BAND, METHOD-DEPENDENT, ALIGNED-WITH-1G–1M and the 1N or 1N–1P readings each
  describe where the step sits, not why.
- **That the muon-energy band covers, accounts for or absorbs the step** (audit M3). The band is common to all
  playlists, and (i) compares magnitudes only.
- **Which period is right.**
- **Any change to C_PL,5D,** to any covariance, or to any result.
- **Coverage.**
- **A statement about the published analysis beyond what its text says,** including **that the published analysis did
  not consider time or intensity dependence** (audit m7). (iii-b) quotes the modelling it states.

**A finding enters the paper only by Joseph's decision,** through the paper lane and a PRD-referee read.

## Revision 2 (2026-11-10): the audit and the director's rulings

coverage-5b-audit's audit of revision 1 (`a63dabb2…`) found 2 blocking, 7 major and 7 minor issues. All are folded in.

**Blocking:**
- **B1:** (ii-a)'s statistic is under P-RPD.
- **B2:** (iii) has two readings, and its record is re-read under them.

**Major:**
- **M1:** (i) has an ordered outcome table, fits PB only, has a scan-edge outcome, and uses σ_α against the band.
- **M2:** the planted scale is built as the data, with a 3.5σ tolerance whose false-STOP rate is under 1 %.
- **M3:** the band's nature is stated, and "covers" is excluded.
- **M4:** the absence readings need incompatibility with the full step, and the names describe playlists.
- **M5:** the combination is pooled, and σ comes from the replicas.
- **M6:** the slice and physics-event index enter the key.
- **M7:** (ii-a) has a reproduction control and a method partition.

**Minor:**
- **m1:** σ_b is fixed at α = 0, the grid is refined with interpolation, and 10⁻¹² is relative.
- **m2:** the median is `w_reco`-weighted, the rows are read in file order, and MINERvA's band is descriptive.
- **m3:** the whole set is rescaled, overflow included.
- **m4:** magnitudes are printed beside the readings.
- **m5:** (iii)'s inputs are aligned.
- **m6:** the fence's path and sha are named.
- **m7:** the licence line is added.

Nothing is submitted, deposited or tagged.
