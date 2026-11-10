# RPL DECLARATION: locating the run-period step, three referee checks (2026-11-10, DRAFT for the director's binding)

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
| (i) the band's size | the lateral muon-energy bands' ±1σ shifted reco kinematics in the per-playlist universe files `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_<PL>_universes_full.root` (`sim_pz` and its `Muon_Energy_MINOS_<i>`, `Muon_Energy_MINERvA_<i>` shifted branches; first 500k `mc_signal_reco` rows per playlist, as the coverage study read them); and the MAT-MINERvA source of those shifts, quoted by file:line@sha from the cluster checkout | login connect | 0 node-h |
| **(ii-a) MINOS method** | step 1, an inventory: the branch lists of MP-1's 12 per-playlist zero loops `$P/measurement-paper/phase1/mp1/s1/evloop/zero/runEventLoopOmniFold_5D_<PL>_zero.root` (pinned in `nd-unfolding/fd_ct_period_inputs.py` `ZERO_LOOPS`). Do they carry `ev_run`/`ev_subrun`/`ev_gate` (data) and `mc_run`/`mc_subrun`/`mc_nthEvtInFile` (MC)? Each file is staged by an O_NOATIME copy to /dev/shm (about 400 MB each, one at a time) and opened there | login connect | 0 node-h |
| (ii-a) the join | only if the inventory finds the keys: the AnaTuples' `MasterAnaDev_minos_used_range` / `_used_curvature` (present in the release's MasterAnaDev tree, `data-survey-20261022/outputs/followup/branches_fhc_data_1B.json`), read for the selected events' keys only. Data: 1,818 files, 0.994 TB; MC: 489 files, 10.706 TB (`data-survey-20261022/SURVEY.md:28`); a few branches each | one CPU job, after a one-file-per-tier dry run measures the read rate | estimated 0.5–1.5 node-h, priced by the dry run before any go |
| (ii-a) without the keys | a new event-loop pass carrying the flag | jobs | several node-h; **not in this declaration**, which would then report (ii-a) as not made |
| **(ii-b) configuration** | RPD-RECO's per-playlist step s_obs,X and σ_X (d2's data-side statistics), and the conditions table above | local, once RPD-RECO's record lands | 0 |
| **(iii) published analysis** | Ruterbories et al., Phys. Rev. D 104, 092007 (2021), arXiv:2106.16210 (`docs/analysis-note/technote.bib`, `MINERvA:2021owq`), with its supplemental material and the release's public pages already copied under `data-survey-20261022/outputs/pages/` | local document read | 0 |

**Sequencing** (the director's rulings, 2026-11-10).

**Precondition P-RPD, for (i)'s fit and for (ii-b).** RPD-RECO's d1/d2 record is committed on main, and is named here
by its sha256 before either runs. Until then this line reads "not yet". RPL stays its own declaration; it is not
folded into RPD-RECO.

**What can go first,** because none of it reads RPD-RECO's inputs or forms a data/MC comparison from them
(limitation-resolver's answer, 2026-11-10):
- **RPD-RECO's pins.** RPD-RECO reads only its 24 dumps (`fd/rpd-reco/INPUTS.sha256`) and, for d2, MAT's flux files.
  No RPD-RECO gate checks the zero loops, the per-playlist universe files or the May CV files.
- **(ii-a)'s inventory** reads branch names only. Its dry run, which prices the join, reads AnaTuple flags for one
  file per tier. Each comes to the director with its sha256 before it runs. If the keys are absent, (ii-a) is reported
  as not made; a new event-loop pass needs its own decision.
  - The MP-1 zero loops were noted with purge exposure around 2026-12-15. That is re-checked by stat first, and
    O_NOATIME reads do not refresh it.
- **(i)'s band-size measurement** is MC only. limitation-resolver's condition is kept: the band sizes are not printed
  beside, or compared with, any per-playlist data step until P-RPD holds.
  - **Before that read,** the per-playlist `_universes_full.root` files are checked against the cov2d session's
    protected list, and `cov2d_fence.sh` runs. RPD-RECO's policy lists the pooled
    `runEventLoopOmniFold_MEFHC_universes_full.root` and the CFS `runEventLoopOmniFold_MEFHC.root` as COV2D-protected
    (`fd/rpd-reco/prologue5-20261108/policy-config.json`). The per-playlist files sit in the same directory, so the
    cov2d session is asked first.
  - Every read is an O_NOATIME copy.
- **(iii)** reads a published paper and depends on nothing else. It has run: see `iii/README.md`.

## (i) The scale fit, fixed

**The statistic.**
- For group G ∈ {PB = 1G, 1L, 1M; PC = 1N–1P}, against PA = 1A–1F (RPD-RECO's groups), on RPD-RECO's p_∥ bins (1.5,
  2, 3, 4, 5, 6, 8, 10, 15, 20, 60 GeV/c):
  - the double ratio D_G(b) = r_G(b) / r_PA(b), with r = N/P as RPD-RECO §2 defines it.
- **The model:** G's data muon momentum is scaled, p_μ → p_μ/(1 + α), with p_T and p_∥ scaled together so θ_μ is
  unchanged, and the data rows re-binned. A free normalization k is allowed.
- **The fit:** α is scanned over [−10 %, +10 %] in steps of 0.05 %. At each α, χ²(α, k) = Σ_b (k·D_G,α(b) − 1)² / σ_b²,
  with k profiled. α̂ is the minimum.
- **The errors:** σ_α and every σ_b come from RPD-RECO's paired bootstrap (B = 200, its seeds), applied to the same
  rows.
- **Reported:** α̂ ± σ_α; χ²_0 (α = 0) and χ²(α̂), each with ndf; and per-playlist α̂_X, as a description.

**The comparator, the band's size.** The band's size is σ_band, the ±1σ fractional p_μ shift of `Muon_Energy_MINOS`,
and separately of `Muon_Energy_MINERvA`.
- It is measured as the weighted median of |p_μ,shifted / p_μ − 1| over `pass_reco` rows, overall and in the p_∥ < 8
  and ≥ 8 strata, from the universe files.
- It is quoted beside MAT-MINERvA's source constants.

**Outcomes, exactly one:**
- **SCALE-WITHIN-BAND:** P(χ²(α̂)) ≥ 0.01 and |α̂| ≤ σ_band (MINOS).
- **SCALE-BEYOND-BAND:** P(χ²(α̂)) ≥ 0.01 and |α̂| > σ_band. Reported in band σ.
- **NOT-A-SCALE:** P(χ²(α̂)) < 0.01. A momentum scale does not reproduce the step's shape.
- **NO-STEP:** RPD-RECO's R-d1.0 reads NOT-SEEN-AT-3σ. No fit is read.

## (ii) The splits, fixed

**(ii-a) MINOS method.**
- **The statistic.** For m ∈ {range, curvature}, the step statistic s^m is RPD-RECO's R-d1.0 s_PB, restricted on both
  data and MC to events whose MINOS momentum used method m. The difference is Δ = s^range − s^curv, with σ_Δ from the
  paired bootstrap.
- **The method fraction** in each p_∥ bin is reported. Range-measured muons are the stopping ones, so method and
  momentum are correlated; the fraction lets the reader see that confound.

**Outcomes:**
- **NOT-TESTABLE (method m):** m holds under 5 % of the weight on either side of 8 GeV/c.
- **METHOD-DEPENDENT:** |Δ| ≥ 3σ_Δ, naming the method that carries the larger step.
- **NOT-METHOD-DEPENDENT-AT-THIS-SENSITIVITY:** otherwise, with σ_Δ stated.

**(ii-b) Configuration.** This reads RPD-RECO's per-playlist steps s_obs,X ± σ_X, without recomputing them.
- **TILTED-HORN-ALIGNED:** each of 1G, 1L and 1M has s_obs,X ≥ 3σ_X, and every other playlist has |s_obs,X| < 3σ_X.
  Otherwise the mapping is reported as **NOT-ALIGNED**, with the playlists that break it. Either way, horn and period
  cannot be separated.
- **Water target, inside the tilted-horn set:** this compares 1G (water empty) with 1L and 1M combined (water full).
  - **WATER-DEPENDENT** if |s_1G − s_1L+1M| ≥ 3σ;
  - **NOT-WATER-DEPENDENT-AT-THIS-SENSITIVITY** if < 2σ;
  - **UNRESOLVED** between those.
- **Slip stacking:** 1N–1P shares 6+4 with 1G–1M but has no tilted horn. If PC's step is under 3σ, it is reported as
  **NOT-6+4-ALONE**; otherwise as **6+4-ALSO**.
- **Helium target:** it is empty from 1G through 1N and full in 1C–1F, so its emptying begins with the step group.
  1N is the one helium-empty playlist outside the tilted-horn set. If 1N's step is under 3σ_1N, it is reported as
  **NOT-HELIUM-ALONE**; otherwise as **HELIUM-ALSO**. 1N's σ is the single-playlist one, which is stated.

## (iii) The published analysis, fixed

**What is read:** the paper, its supplemental material, and the release pages already copied, for any statement on
run periods or playlists. The search terms are:
- playlist, run period, "1G", "1M", "tilted", "horn", "slip";
- MINOS range, curvature, muon energy scale;
- pile-up and intensity;
- "per-playlist" and "playlist-dependent".

Each hit is quoted verbatim with its section.

**Outcomes:**
- **TREATED:** a stated correction or uncertainty for run-period differences, quoted.
- **SEEN-NOT-TREATED:** the difference is stated with no treatment.
- **NOT-MENTIONED:** none of the terms gives a relevant hit. The outcome carries its search line, and says nothing
  about what the analysis did internally.

## Controls

**Each is a STOP that reports the check as not made; nothing is repaired.**
- the input pins (RPD-RECO's `INPUTS.sha256`; `ZERO_LOOPS`);
- O_NOATIME on every pinned read;
- (i): at α = 0 the code reproduces RPD-RECO's R-d1.0 s_PB to 10⁻¹²;
- (i): a planted scale on MC-only pseudo-data is recovered within 1σ_α;
- (ii-a): the join keys are unique, and the unmatched fraction is reported. Above 0.1 % of selected weight unmatched
  is a STOP.

## Licence

**CITABLE FOR (once a binding's record lands):** each check's outcome, as defined above, and its numbers, as
descriptions of the reconstruction-level step.

**NOT CITABLE FOR:**
- **The cause of the step.** SCALE-BEYOND-BAND, METHOD-DEPENDENT or TILTED-HORN-ALIGNED each describe where the step
  sits, not why.
- **Which period is right.**
- **Any change to C_PL,5D,** to any covariance, or to any result.
- **Coverage.**
- **A statement about the published analysis beyond what its text says.**

**A finding enters the paper only by Joseph's decision,** through the paper lane and a PRD-referee read.

Nothing is submitted, deposited or tagged.
