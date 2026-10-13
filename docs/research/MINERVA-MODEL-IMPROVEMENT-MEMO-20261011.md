# Interaction model improvements motivated by the MINERvA ME FHC comparison

Research memo for Joseph Bailey · 11 October 2026

**Conclusion.** The evidence motivates testing an existing, more consistent nuclear-current calculation. It does not presently justify inventing a new interaction model, identifying one cause for all discrepancies, or fitting an extension with the adopted scalar covariance. The most promising bounded question is whether the revised Valencia multinucleon calculation, with its associated exclusive nucleon kinematics, improves the low-available-energy distribution while satisfying independent lepton and nucleon constraints. This is an implementation and validation proposal for published physics, not a novelty claim. The high-energy normalization and shape questions need separate treatment.

The particularly useful target is the residual at **0.1–0.4 GeV available energy**. The lowest bin is already approximately filled by the tested meson-exchange-current (MEC) addition. A uniform increase of that addition is therefore a poor starting hypothesis. Even the residual's attribution to the interaction remains conditional on energy definitions, response, and estimator dependence.

**Ownership and bounds.** Joseph owns the scientific decision. This session owns this memo and its analytical deductions. The investigation considers three candidates and ends with one synthesis; production-compute budget is zero. The owner performs one source-and-algebra review; this is not independent verification. Subsequent validation should have an independent nuclear-theory reviewer and a generator implementation reviewer. No analysis replacement, new simulation campaign, publication adoption, or collaborator contact is implied.

## Evidence baseline and definitions

### Repository baseline

The starting checkout was `f6dc46e6afef9efa8722d01b43c3f2b379b41314`, **187 commits behind** remote `main`. The evidence reviewed here is pinned to `3892e769043cddebfd58ec19e1ab1a567eb01784`, fetched and inspected in a clean, detached worktree. A second remote query returned the same head. The user's checkout was not updated. All repository links below use that evidence commit, so this memo remains intelligible when `main` moves.

The starting routes were [AGENTS.md][agents], [CURRENT_WORK][current], and the [campaign review][campaign]. Scientific statements follow the [claim-to-evidence matrix, including superseding sections D–H][claims], the current [article body][paper], the [validation ledger][ledger], and the original receipts identified below. The October 9 pairing correction and October 10–11 follow-up matter: the 2D covariance transfer remains unresolved. Successful central-value reproduction does not establish a matched, publication-ready uncertainty construction. The latest integration record reports no successful XR scientific fit; its scope is operational disposition, not a new cross-section result. [Pairing assessment][pairing]; [follow-up, sections A1, A4 and E][followup]; [integration, sections 1 and 10][integration].

A local copy of the article's figure arrays was checked against the committed manifest: SHA-256 `72394a2b4eff9f14b01903ff97525bcb690c2adee58ccaf573a8d95139b415b8`. The existing `fig_numbers.py` check passed against `values.tex`. This reproduces arithmetic on existing artifacts; it does not reconstruct events, independently validate the measurement, or authorize otherwise restricted significances. The generator input products are bound by their full digests in the [original generator-context receipt][context]. [Figure manifest][figmanifest].

### Common experimental comparison

The repository analysis uses twelve ME-FHC playlists, about $1.0574\times10^{21}$ POT, and a flux peaking near 6 GeV. The truth signal is inclusive $\nu_\mu$ CC in the tracker fiducial region, $\theta_\mu<20^\circ$, $1.5<p_\parallel<60$ GeV, and $p_T<4.5$ GeV. There is no hadron veto. The reconstruction requires a negatively charged, MINOS-matched muon and the associated fiducial and quality cuts. The analysis fiducial limits are $5980<z<8422$ mm and hexagonal apothem 850 mm. Thus CC0π and multinucleon samples discussed later are diagnostic subsets, not this measurement's signal definition. [Selection producer][selection]; [article][paper].

The corrected prediction flux is the data-POT-weighted, neutrino-electron-constrained PPFX CV flux, integrated over 0–100 GeV: $\Phi=6.243343\times10^{-4}\ {\rm m}^{-2}/{\rm POT}$. The correction repairs both flux shape and a variable-width histogram sampling problem; earlier generator comparisons cannot be carried forward unchanged. GENIE and NuWro now include separately produced 50–100 GeV contributions. GiBUU remains limited to 20 GeV. The flux-fix README retains an early “uncommitted” status line; the later committed receipts and VL156–VL161 establish the quotable products used here. [Flux construction and supplements][fluxfix]; [ledger][ledger].

The physical tracker is not exactly CH or pure carbon. The reference experiment gives mass fractions C 88.51%, H 8.18%, O 2.50%, Ti 0.47%, Cl 0.20%, Al 0.07%, Si 0.07%. These are the reference detector composition, not evidence that every external prediction implemented that mixture. Its quoted POT and flux integral also differ slightly from this repository's analysis-specific normalization. Use the latter for this comparison. [Ruterbories et al., section IV][inclusivepaper].

| Prediction label used below | Version and actual configuration | Target and energy support | What is and is not pinned |
|---|---|---|---|
| **Tune v1** | Nominal detector MC: GENIE 2.12.6, MINERvA Tune v1; RPA, empirically enhanced Valencia 2p2h, reduced nonresonant pion production | Tracker detector MC; analysis flux and signal | This is the unfolding prior and the comparator in the descriptive excess map. It is not external GENIE CV. |
| **GENIE CV** | UPS `v2_12_10c`; cross-section tables `v2_12_10`, `DefaultPlusValenciaMEC`; actual CV `gevgen` event list is default and contains **zero MEC events** | C12/H1 mass weights 0.9225/0.0775; corrected 0–100 GeV flux | A spline/configuration name containing “MEC” does not mean the CV events contain MEC. The mode census resolves this ambiguity. |
| **GENIE+MEC** | Same GENIE installation, `Default+CCMEC` event list, original Valencia MEC implementation; no MINERvA empirical enhancement | Same CH mixture and corrected energy coverage | Tests adding this particular implementation, not all two-body currents. |
| **NuWro** | 21.09, installed as `v21_09_1`; launcher enables CC QEL, RES, DIS, COH, MEC | C12; initial 0.5–50 GeV plus 50–100 supplement, corrected flux | The launcher leaves underlying physics options at installation defaults. A complete resolved runtime model/tune dump is not established by this evidence; do not invent one from a version label. |
| **GiBUU** | 2019, committed ME-FHC jobcard; QE, Δ, other resonances, 1π, DIS, 2p2hQE enabled; `ME_Version=4`, BBBA07 QE vectors, MAID resonance option; medium-width switches false | C12; corrected sampled flux, **no events above 20 GeV** | The jobcard is the configuration, not a universal statement about GiBUU. Its omitted energy tail prevents an unrestricted normalization comparison. |

Configuration sources: [GENIE launcher][genielaunch], [MEC launcher][meclaunch], [NuWro launcher][nuwrolaunch], [GiBUU jobcard][gibuucard], [flux receipt route][fluxfix], [mode census][modes]. Tune v1's underlying model uses a dipole QE axial form factor, resonance production and Bodek–Yang inelastic scattering, with intranuclear hA transport; the reference description specifies a roughly 50% integrated empirical 2p2h enhancement and 43% nonresonant-pion reduction. Those are tune history, not independent evidence for our preferred mechanism. [Ruterbories et al., section III][inclusivepaper].

For ideal CH, per-nucleon rates obey approximately

$$
 \sigma_{\rm CH}/N=(12\sigma_{C}/N_C+\sigma_H)/13.
$$

For neutrino QE, free hydrogen supplies no neutron target, so a C-only per-nucleon QE prediction can exceed ideal CH by $13/12$, even before other nuclear effects. Inelastic hydrogen contributes. Consequently a single constant “carbon-to-CH correction” is insufficient across channels. The actual assay requires a species-weighted prediction. This is an algebraic consequence of target counting, not a measured correction to the quoted curves.

### What the three hadronic axes mean

Write $A\equiv E_{\rm avail}$ to distinguish available energy from nuclear mass number. The repository's truth definition, after nuclear FSI, is

$$
 A=\sum_p(E_p-0.93827)
   +\sum_{\pi^\pm}(E_\pi-0.135)
   +\sum_{\pi^0,\gamma}E,
 \qquad \text{energies in GeV}. \tag{1}
$$

It excludes neutrons, electrons/positrons, kaons and other strange particles. Charged pions use **135 MeV**, not their physical charged-pion mass. Final-state records must avoid counting both a decayed π0 and its photons. This operational definition must be reproduced literally for comparison; it should not be silently “corrected” while keeping the data product fixed. [Definition audit][eavail]; [CVUniverse implementation][cvuniverse].

The reconstructed available-energy input instead uses $1.17$ times tracker-plus-ECAL blob recoil energy after muon-fuzz subtraction. The reconstructed energy transfer $\omega_r$ used for $q_3$ and $W$ is the separate full calibrated recoil branch, not that available-energy expression. With $a=E_\mu-p_\mu\cos\theta_\mu$, the implementation uses

$$
 Q_r^2=2(E_\mu+\omega_r)a-m_\mu^2,\quad
 q_{3,r}=\sqrt{Q_r^2+\omega_r^2},\quad
 W_r=\sqrt{M^2+2M\omega_r-Q_r^2}, \tag{2}
$$

with the implementation's nonnegative clamps and average nucleon mass. Away from clamps, differentiation gives

$$
 \frac{\partial Q_r^2}{\partial\omega_r}=2a,\qquad
 \frac{\partial q_{3,r}}{\partial\omega_r}=\frac{\omega_r+a}{q_{3,r}},\qquad
 \frac{\partial W_r}{\partial\omega_r}=\frac{M-a}{W_r}. \tag{3}
$$

These are memo derivations from the committed definitions. They show why a recoil-response error produces structured, correlated motion in the hadronic axes. Available energy and recoil are also correlated through shared deposits. Five analysis coordinates are not five independent measurements of the hard interaction.

At truth level, $\omega=E_\nu-E_\mu$ and $q_3=|\mathbf k-\mathbf k'|$ are actual lepton energy and momentum transfers. But the analysis's truth $W$ is an **experimenter's estimator**, using a stationary nucleon and $\widetilde Q^2=4E_\nu E_\mu\sin^2(\theta_\mu/2)$. Native MC chooses the struck proton/neutron mass where available; external conversion uses a fixed neutron mass. The massless-lepton approximation differs from the exact lepton expression by

$$
 Q^2-\widetilde Q^2=2E_\nu(E_\mu-p_\mu)\cos\theta_\mu-m_\mu^2. \tag{4}
$$

For a moving, off-shell struck nucleon, the corresponding subprocess invariant is $(p+q)^2$; the entire nuclear final state's invariant is $(P_A+q)^2$. Neither is generally the plotted $W^2$. A 2p2h interaction need not even have a unique struck-nucleon interpretation. The fixed-mass and finite-muon-mass differences require a matched-convention check before fine resonance attribution. [Native definitions][cvuniverse]; [external 5D converter][converter].

Equation (1) also is not $\omega$: energy can go to neutrons, separation energy, residual excitation and recoil, rest masses, or excluded species. Low $A$ therefore does not uniquely mean low transfer, QE, or multinucleon scattering. In the tested GENIE CV, even the lowest $A$ bin contains a substantial generator-labelled DIS contribution, about 21%; that is a model decomposition, not a data classification. [Mode census][modes].

The definition mismatch with published available-energy measurements is consequential. The committed audit finds that using the broader Ascencio definition changes the mean truth energy by 212.18 MeV/event and moves 4.837% of events between its checked truth bins; 10.99% leave the lowest $A<0.1$ bin. These are MC convention diagnostics, not data corrections. Correcting just the charged-pion mass changes the mean by 4.827 MeV/event and moves 0.666% of events. The broader definition also includes species our definition omits. Neither effect licenses borrowing another measurement's unfolded bins as if identical. [Definition audit, OI-30/56/59 routes][eavail]; [Ascencio et al., observable definition, Eq. (1)][ascencio].

Workstream routes for the validated central results and their qualifications are the [2D status][status2d], [3D status][status3d], and [scalar N-D status][statusnd]. The newer pairing and inference records above control where they supersede older summaries.

## Exactly what needs explaining

### Evidence table

All comparisons below use the inclusive muon selection and operational definitions above. Ratios are data/prediction unless explicitly stated otherwise. Central differences are not significances.

| Evidence class | Committed observation | Estimator and prediction scope | Available uncertainty support and inference limit |
|---|---|---|---|
| **(a) Low available energy** | Adding original Valencia MEC fills approximately 106.5%, 31.8%, and 59.8% of the CV gap in 0–0.1, 0.1–0.2, and 0.2–0.4 GeV respectively. It fills 52% of the gap below 0.4 and 63% of the net deficit below 3 GeV. | Production 3D OmniFold $(p_T,p_\parallel,A)$, five iterations, nominal Tune v1 detector MC; external GENIE CV versus GENIE+MEC as configured above. | Central value, marginal anchor and injected-shape closure validated. Historical standalone 3D block-sum covariance significances remain quarantined. The diagnostic producer prints old pulls; this memo does not use them. [VL159–160; original log][meclog]. |
| **(b) Overall normalization** | Scalar-5D integral $3.06993\times10^{-38}$ cm²/nucleon. Ratios: CV 1.1105; +MEC 1.0676; NuWro 1.1529; GiBUU 1.3859. | Production scalar 5D central result, not the s5p refit. Corrected flux and full scalar grid; GiBUU's missing >20 GeV component persists. | Descriptive integrals. The adopted covariance is byte-scoped and non-passing under its own criteria; no unrestricted normalization likelihood. C-only targets differ from the detector. [VL156–158; receipt][context]. |
| **(c) Shape and descriptive $(A,W)$ map** | For $A\geq0.8, W\geq1.8$ GeV: ratios 1.1421, 1.1386, 1.1601, 1.6070 in the same order. Against **Tune v1**, 67.215% of positive cell-integrated differences occur at $A\geq0.8$; 83.172% of that share has $W\geq1.8$. One catch cell contributes 21.947% of the positive difference. | 42-cell projection of production scalar 5D. The map's comparator is Tune v1, whereas its external-generator overlays use the four configurations above. | The projection is paired by digest with adopted trunk `3d7465f6…`, projected digest `835828bf…`. Adoption does not establish local significance, identify a mode, or remove response and estimator qualifications. [Article/figure manifest][figmanifest]; [adoption, section 4][adoption]. |
| **(d) Conditional joint-generator tests** | All ten simple hypotheses—Tune v1 and four external predictions, each total and shape—rejected at familywise $\alpha=0.05$. | s5p estimator R: deterministic LightGBM, five iterations, negative-weight refinement, 400 trees/31 leaves; 109 supported coarse joint cells, GiBUU 72 with $p_\parallel<6$. Fine-grid generator null retains Tune v1 subcell structure. This differs from the nominal 100-tree/8-leaf scalar estimator. | Monte Carlo calibrated finite p-values and Holm correction, with all six conditions below. Independent recomputation agrees with the calculation, not calibration adequacy. No new measured cross section or reportable uncertainty; global rejection neither localizes a failure nor selects its cause. [Result record][s5p]; [terminal delivery][delivery]. |

The low-energy densities make the candidate's challenge concrete:

| $A$ bin, GeV | Data | GENIE CV | GENIE+MEC |
|---|---:|---:|---:|
| 0–0.1 | 2.19 | 2.02 | 2.20 |
| 0.1–0.2 | 2.04 | 1.51 | 1.68 |
| 0.2–0.4 | 1.84 | 1.56 | 1.73 |
| 0.4–0.8 | 1.20 | 1.21 | 1.29 |
| 0.8–1.5 | 0.745 | 0.750 | 0.760 |
| 1.5–3 | 0.416 | 0.381 | 0.383 |
| 3–100 catch interval | 0.00681 | 0.00536 | 0.00537 |

Units are $10^{-38}\ {\rm cm}^2/({\rm GeV\ nucleon})$, **bin-averaged densities**, rounded as in the [original log][meclog]. Below 3 GeV the integrated values are 2.418, 2.245, and 2.355 in $10^{-38}\ {\rm cm}^2/{\rm nucleon}$. Density height alone cannot establish where the integrated deficit resides.

### Overflow and normalization change the interpretation

For a density $D_{ij}=d^2\sigma/(dA\,dW)$, the contribution to a region is $D_{ij}\Delta A_i\Delta W_j$. The scalar projection uses edges

$$
 A:[0,.1,.2,.4,.8,1.5,3,100],\quad
 W:[0,1.1,1.4,1.8,2.2,3,100]\quad{\rm GeV}.
$$

The upper catch cell has area $97^2=9409\ {\rm GeV}^2$. Its 21.947% share is of the **sum of positive differences against Tune v1**, not of the total cross section, net difference, or a narrow localized peak. Do not interpret its plotted colour as a resonance structure. [Figure producer inputs][figmanifest]; [paper][paper].

For comparison, the 3D $A=3–100$ bin contains approximately $0.661\times10^{-38}\ {\rm cm}^2/{\rm nucleon}$, about 21% of the 3D total. Its data-minus-CV difference is approximately $0.141\times10^{-38}$, roughly 45% of the full 3D net gap. These are **memo arithmetic from rounded densities**, not new ledger measurements, and they have a different denominator and comparator from the 21.947% map share.

Dividing a corner data/prediction ratio by the corresponding total ratio isolates its normalization-independent fraction:

| Prediction | Corner/total ratio of ratios |
|---|---:|
| GENIE CV | 1.0285 |
| GENIE+MEC | 1.0665 |
| NuWro | 1.0062 |
| GiBUU | 1.1595 |

Thus the high corner is only approximately 0.6–6.7% more discrepant than overall normalization for the first three predictions. Conversely GENIE CV and +MEC **exceed** data by 9.39% and 11.79% in $1.4<W<1.8$ GeV. An all-positive enhancement is not a general shape remedy. These calculations follow the [committed figure inputs][figmanifest] and [VL156–158][ledger].

The other generators place approximately 14–15% of the corner and 7% of the total above $E_\nu=20$ GeV. Substituting their tail fractions as a GiBUU proxy reduces the apparent GiBUU corner ratio to about 1.37–1.38 and total ratio to 1.28–1.29. This is a **conditional proxy**, not the absent GiBUU prediction or a correction we may adopt. Flux coverage is material even after the flux-shape repair. [VL161 and original cap-share receipt][capshare].

### Uncertainty and inference conditions that travel with the evidence

The adopted 5D covariance is specifically the CV-centred 890,500,272-byte product with SHA-256 `3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5`. Its four associated measurements are:

1. Estimator-seed sensitivity $s_{\rm proj}=6.145\%$, exceeding the declared 5% bound, measured with the companion seed comparison.
2. Values 6.02%, 6.02%, 6.145% at nested $N=40,80,160$ in one ensemble and one seed pair; the same-seed resampling floor falls from 20.91% to 7.57% between 40 and 80. This establishes neither an infinite-ensemble limit nor the distribution over seed pairs.
3. Five of 45 bands use seed 42 only; their 26% share in square-root trace, or 6.75% in trace, is unprobed in either direction. “Lower bound” was withdrawn.
4. Companion seed changes move projected centrals by median 0.104%, maximum 0.761%—median 1.06%, maximum 6.02% of quoted uncertainty. Individual 5D cells are more sensitive: median 3.77%, 90th percentile 13.6%, maximum 49.8% of quoted uncertainty.

These are part of the adoption, not optional caveats. The product's own `NON-PASSING` and `adoptable: false` remain; the exception is byte-scoped, Cause 3 is not discharged, and no declared boundary was evaluated in production. Neither mean-centred alternatives nor other corrected candidates inherit adoption. [Adoption, section 4][adoption]; [operative sheet][operative]; [ledger VL142–144][ledger].

The 2D 6.87% median budget is a construction for LightGBM seed 42; against the quoted exact-split central denominator it is 6.83%. The quoted central uses scikit-learn gradient boosting with unpinned seed, whereas the statistical, universe, and training-seed blocks use LightGBM. The median central difference is 0.97% per cell, about 1.3 statistical standard deviations, without a measured transfer allowance. VL170 statistical coverage remains untested; the earlier VL162 band failed its coverage test. The latest committed follow-up additionally documents different truth inputs for the May universe path and its CV and a common offset; this does not itself provide a corrected covariance or coverage result. **The 2D agreement with the published total, approximately 1.1%, is useful central-value reproduction, not an independently calibrated fitting likelihood.** [Claims section H][claims]; [pairing assessment][pairing]; [follow-up section A4][followup]; [KNOWN_ISSUES 85, 88–90][issues].

Every s5p rejection carries these six conditions, condensed from its governing record:

1. Fine-grid convergence was not demonstrated; the last change was 50–86% of the full construction change in relative L2. The unmeasured remainder is represented by a declared sensitivity direction, not bounded by a convergence proof.
2. Covered detector bands include MINOS efficiency, Geant hadron interactions, and five muon/beam lateral variations. There is **no calorimetric recoil-response band establishing completeness**.
3. Thirty-four interaction-model bands enter each draw, including the declared treatment of two clipped bands.
4. Half-MC calibration versus full-MC data evaluation requires its stated finite-MC shift allowance and rounding treatment.
5. GiBUU lacks >20 GeV, including migration from outside its admitted region; all predictions lack >100 GeV support.
6. Finite generator MC enters both the comparison metric and the simulated draws.

The missing calibration and power draws were subsequently recovered; the frozen decisions survived. P-values use ((k+1)/(B+1)), not zero or a Gaussian “sigma”: nine tests have $k=0$, NuWro shape has $k=1$; $B$ is approximately 1,343–1,751 depending on generator. The metric is the campaign's calibrated construction, not an unrestricted inverse of the adopted covariance. [Result record, sections 1–4][s5p]; [delivery, section 1][delivery].

Later sensitivity scans do not remove condition 1. The October 8 scan remains determinate through the declared range to κ=5.25 for the frozen procedure, with its first loss of determinacy bracketed above that; this explores one prescribed direction. Nor is response completeness established by the exploratory ±4% coherent data-side recoil rescaling: it did not vary the null response, species dependence, resolution, or pre-calibration response. The matched muon-only projection does not reject GENIE CV, and no general claim of extra discrimination from five dimensions is established. [Claims sections E–G][claims].

## What can be attributed to interaction physics

| Competing explanation | Assessment from existing evidence | Missing discriminator |
|---|---|---|
| Observable definitions | A demonstrated issue for comparisons to other published $A$ measurements; inherited particle list, pion mass, and $W$ conventions affect migrations. Internally matched generator conversion reduces this problem but does not convert $A$ into energy transfer. | Common stable-particle specification and identical analysis functions, including residual nuclei and decays; response mapping for any changed definition. |
| Flux and energy coverage | The repaired sampling/PPFX correction materially raised predictions. GiBUU's high-energy truncation still affects total and corner. Overall flux normalization remains degenerate with an inclusive rate change. | Matched complete energy support, flux covariance shared between relevant data samples, and externally constrained normalization. |
| Target composition | Pure C, ideal CH and the actual tracker differ; channel fractions determine the effect. | Explicit target-mixture predictions, with hydrogen treated separately rather than absorbed into a nuclear knob. |
| Background treatment | Signal reweighting closure is not background closure. The committed purity stress finds high-$W$ bias about −3.5 to −4.1%; nominal changes on real data are much smaller but are not estimates of the actual bias. | Background-enriched constraints and tests of subtraction under independently specified interaction/response changes. [VL149/151/152][ledger]. |
| Unfolding regularization and prior | Finite-capacity estimators and priors affect hadronic structure. The committed studies include large stress-closure deviations and reduced, still nonzero residuals for estimator R. Stress truths derived from old generator deformations are tests of the procedure, not measurements of real-model bias. | Matched-estimator uncertainty, untouched truth tests with adequate support, and bias/coverage evidence for the intended comparison. [VL149–155][ledger]; [s5p][s5p]. |
| Hadronic detector response | Shared inputs can create correlated $A,q_3,W$ discrepancies by Eq. (3). ±4% tests one coherent direction. Charged-particle test-beam constraints do not span neutron response, all energies, or species-dependent fluctuations. | Full response nuisance family propagated in data extraction **and** null predictions, including neutron and secondary-hadron effects. [Claims I7 and E][claims]. |
| Interaction physics | Original MEC improves a specific low-energy gap, and the old generators give different patterns. That makes the underlying current and final-state partition plausible research targets. | A physically constrained change that predicts complementary observables and survives the preceding alternatives. |

The limited `FrAbs_pi` and `FrInel_pi` ±1σ tests move their checked distributions by less than about 0.82% and 0.75%. They concern two knobs in a particular older event sample, not nucleon transport, all pion amplitudes, correlated transport changes, or the complete detector response. **They do not exclude an FSI explanation.** [Original absorption result][fsiabs]; [inelastic result][fsiinel].

The credible theoretical targets are therefore (i) the low-$A$ shape left after the specific MEC addition, (ii) the partition of transferred energy among protons, neutrons, pions and the residual nucleus, and (iii) separate inclusive inelastic normalization/shape questions after energy coverage and mixture are matched. The map is a guide for designing diagnostics, not a measurement of which microscopic amplitude failed. Global rejection of a composite prediction leaves all its shared interaction, response and inference assumptions in play.

## Literature assessment and three candidates

The comparison versions predate substantial relevant work. Official GENIE documentation lists production 3.6.2, and its modern model families include SuSAv2 and later tunes. Rejecting GENIE 2.12 configurations is not rejecting present-day generator theory. [Official releases][geniereleases]; [official model/tune list][genietunes]. The assessment below distinguishes published results, recent preprints, and deductions about our data.

### Candidate 1 Consistent quasielastic and multinucleon currents

**Physical content.** Quasielastic (QE) scattering converts a bound neutron into a proton without creating a meson at the primary vertex. A zero-pion final state is broader: it can also contain an interaction that produced a pion which was absorbed. The Δ(1232) is a spin-3/2, isospin-3/2 baryon resonance; in a nucleus its excitation can feed pion emission or energy transfer to other nucleons. Nuclear correlations alter the initial state and propagators; two-body electroweak currents add amplitudes in which the probe couples to an interacting pair. The same final state can receive both contributions and their interference. “Two-body current” and “two emitted nucleons” are not interchangeable. A 2026 calculation explicitly examines two-body-current contributions to 1p1h as well as modern axial form factors; its comparisons do not establish one preferred form-factor choice across experiments. [Franco-Muñoz et al., sections II–IV, Eq. (1), preprint][sf2026].

**What already exists.** Sobczyk and Nieves' published 2025 revision corrects a nucleon mean-field inconsistency. The cited arXiv v1 reports a 20–40% strength increase; the final journal abstract describes an increase around 40%. These statements concern the calculation's studied domain, **not our flux-integrated bins**. [Sections II B–C, III, Fig. 8 and footnote 12][valencia2025]; [final journal record][valencia2025journal].

Exclusive extensions are also available. The 2020 calculation distinguishes 2p2h and 3p3h and compares its nucleon distributions with phase-space prescriptions. NuWro work published in 2025 implements that **2020** model with improved sampling; its introduction, footnote 1, explicitly excludes the later self-energy revision. [Sobczyk et al., sections II–IV][valencia2020]; [Prasad et al., sections I, III–IV][nuwro2025]. A study submitted in March 2026 and published on 13 July 2026 as *Physical Review D* **114**, 012002 studies the updated exclusive Valencia calculation at fixed 450, 650 and 1,000 MeV: asymmetric sharing and harder leading nucleons survive the tested NEUT cascade. Its detector study uses thresholds, not a full response simulation. [Kasturi et al., sections II–VI][exclusive2026]; [journal issue record][exclusive2026journal].

SuSAv2-MEC already supplies a different, electron-constrained QE plus two-body framework, with a GENIE implementation and explicit scrutiny of inclusive-to-exclusive factorization. It is an established benchmark, not a fourth candidate proposed here. [Dolan, Megias and Bolognesi, sections II–V and Appendix C][susa]. Spectral-function approaches describe a distribution of removal energy and initial momentum, rather than one Fermi-gas shell; a 2026 exclusive two-nucleon calculation gives a further independently formulated benchmark. [Rocco and Steinberg, section II, Eqs. (4)–(5), section III][exclusiveSF].

**Expected effect and constraints.** Increasing physically allowed pair-current strength can add CC0π events between QE and resonance energy transfers. But its sign in a particular $A$ bin also depends on pair charge, sharing, and transport. Increasing the magnitude of $F_A(Q^2)$ enhances the axial-squared QE contribution and alters vector–axial interference; it generally changes muon kinematics and many QE-like bins, not just our dip. Vector form factors are constrained by electron scattering and CVC; axial factors need weak probes, lattice calculations and elementary-target data. Recent hydrogen/deuterium work uses a constrained $z$-expansion and finds data tensions, so “raise the axial mass” is neither unique nor unconstrained. [Meyer et al., sections II, III.4.2 and IV.1, Eqs. (11)–(12), (31), preprint][axial2025].

Electron scattering constrains the vector response, spectral distributions and aspects of FSI, but not the axial response or the vector–axial interference separately. Existing e-GENIE comparisons show that improving QE/MEC does not automatically fix the resonance region. [Papadopoulou et al., sections II–III][egenie]. A pure form-factor rescaling is consequently less identifiable here than a correction whose medium consistency and exclusive consequences can be tested separately.

### Candidate 2 Nuclear energy balance and hadron transport

**Physical content.** Removal energy, recoil of the residual nucleus, nucleon rescattering, charge exchange and pion absorption redistribute energy and final-state identities. Greater transfer to neutrons or residual excitation generally lowers visible $A$ at fixed lepton kinematics; pion charge exchange can move energy between total-energy-counted π0 and kinetic-energy-counted π±. Pion absorption can replace a pion by several nucleons, with a sign depending on their charges and energies. There is no universal FSI sign for all $A$ bins. These signs follow Eq. (1) and conservation laws.

**What already exists.** The published MINERvA low-recoil study tested an existing combination of SuSA 2p2h, a QE high-momentum-tail change, and a 25 MeV resonance removal-energy adjustment. The latter was selected using that study's data and moved events in available energy while preserving the resonance rate. This is not an independently predicted new mechanism. [Ascencio et al., sections IV B–C and discussion of MnvTune-v3][ascencio]. In the microscopic 2020 pair calculation, final-state interactions smear the visible-energy structures and shift strength downward; proton–neutron final states are especially sensitive to which nucleon receives the energy. [Section IV B, Fig. 7][valencia2020].

A September 2026 preprint makes the transport alternative more concrete: comparisons of GENIE hA2018/hN2018, INCL++ and Geant4 Bertini against hadron data find different nucleon spectra and de-excitation treatments, including carbon proton-to-neutron data. Matching total reaction rates does not ensure correct nucleon energy distributions. Its visible-energy definition counts meson total energy and is not Eq. (1), so its energy shifts cannot be imported numerically. These are existing transport developments, not a new mechanism inferred here. [Diurba et al., section II, Figs. 3–7; sections IV–V][fsi2026].

**Discriminator.** A normalized post-vertex transport kernel cannot change the fully inclusive muon cross section at fixed primary interaction. It changes topology and visible energy, and can change a reconstructed selected sample through detector response. This statement is about a generator cascade; quantum FSI already incorporated in an inclusive hadronic tensor can change the differential inclusive response and must not be removed by this argument. Hadron–nucleus scattering, proton transparency and electron-induced knockout constrain transport independently of neutrino flux. The limited two-pion-knob test leaves this candidate open. Its weakness is strong degeneracy with hadronic detector response and removal-energy conventions.

### Candidate 3 Resonance and nonresonant inelastic matching with hadronization

**Physical content.** The transition region combines resonance amplitudes, nonresonant pion production and inclusive quark-level descriptions. Changing axial transition form factors or nonresonant amplitudes can alter low-$Q^2$ pion strength and interference; changing matching and multiplicity probabilities redistributes low-multiplicity versus many-hadron events. Vector transition information comes from electroproduction, while axial transitions need weak pion data and PCAC constraints. Higher-$W$ hadronization changes charged/neutral energy fractions even at fixed inclusive rate. These are plausible ingredients, not deductions that the plotted high-$W$ cells isolate them.

**What already exists.** GENIE v3 bare-nucleon tuning treats the resonance/shallow-inelastic (SIS)/deep-inelastic (DIS) partition and fits inclusive and exclusive elementary-target data together. Its Eqs. (1)–(3) show explicitly how multiplicity weights participate in avoiding double counting. AGKY tuning uses bubble-chamber hadron multiplicities and documents tensions between hydrogen and deuterium constraints. [Tena-Vidal et al., section II and sections IV–VI][baregenie]; [AGKY paper, sections II and VI–VII][agky]. A 2025 MINERvA SIS measurement selects $1.5<W<2$ GeV and studies a $Q^2\geq1\ {\rm GeV}^2$ variant, providing a useful dedicated comparison rather than equating an experimenter's $W$ corner with DIS. [Sections I A and IV B][sis2025].

**Expected effect and weakness.** Increasing missing inelastic strength could raise high-energy totals, whereas multiplicity changes could alter $A$ at fixed total. Either could damage the intermediate-$W$ region where our GENIE predictions already exceed data. Since the corner/total ratio is near unity for several models, flux normalization and energy coverage currently compete strongly with a proposed new inelastic mechanism. A free high-$W$ scale would be an empirical tune. No minimal, independently constrained new matching law is identified by this evidence.

### Ranking

| Rank | Candidate | Explanatory reach | Independent constraints | Identifiability and consistency | Feasibility for a QFT-trained investigator |
|---|---|---|---|---|---|
| **1** | Consistent QE/multinucleon current, focusing on revised Valencia | Specific low-transfer hypothesis and correlated nucleon predictions; not a full high-energy explanation | Electron responses, elementary weak amplitudes, pion/photon medium effects, external CC0π/nucleon data | Physically motivated correction; exclusive response still essential; overlap bookkeeping must be reviewed | Good entry through currents, propagators and cuts; use an existing nuclear calculation with expert review |
| **2** | Energy balance and transport | Directly addresses visible/missing energy and topology; cascade alone does not repair inclusive normalization | Nuclear masses, electron knockout, hadron–nucleus data | Strong response degeneracy; conservation is testable; many correlated transport parameters | Good diagnostic project, less minimal as a new theory |
| **3** | Resonance/SIS/DIS and hadronization | Relevant to separate inelastic shape and normalization | Electroproduction, weak H/D pion and multiplicity data | Current corner evidence insufficient to isolate matching; double counting and multi-parameter freedom | Substantially broader phenomenology; defer until modern baseline and support are matched |

Selection is based on a constrained physical defect and testable consequences, not on claiming candidate 1 maximizes agreement with all our data. The immediate comparison should be the published corrected model versus its predecessor. There is no supported claim that this memo creates a new theoretical model.

## Worked formulation of the preferred extension

### From the weak amplitude to a nuclear response

At these momentum transfers the charged-current interaction can be written

$$
 {\cal M}_{X}=\frac{G_F V_{ud}}{\sqrt2}
 \bar u_\mu(k')\gamma_\alpha(1-\gamma_5)u_\nu(k)
 \langle X|J_+^\alpha(q)|A\rangle,
 \qquad J_+=V_+-A_+. \tag{5}
$$

With relativistically normalized states, define the inclusive tensor by summing the products of nuclear matrix elements over complete final-state phase space and including $(2\pi)^4\delta^4(P_A+q-P_X)$. Then

$$
 d\sigma=\frac{1}{4E_\nu M_A}\frac{G_F^2|V_{ud}|^2}{2}
 L_{\alpha\beta}W^{\alpha\beta}
 \frac{d^3k'}{(2\pi)^3\,2E_\mu}. \tag{6}
$$

Here $L_{\alpha\beta}$ is the spin-summed product of the lepton currents in Eq. (5); factors of 2 and $2\pi$ are sometimes absorbed into $W$. For a concrete alternative convention see [Sobczyk et al., Eqs. (1)–(3)][valencia2020]. Equations (5)–(6) make clear that “extra events” require a changed current, nuclear states or their dynamics, not a multiplier justified solely by bin residuals.

For example, a one-nucleon current has vector Dirac/Pauli and axial/pseudoscalar structures,

$$
 \Gamma^\alpha=F_1^V\gamma^\alpha
 +F_2^V\frac{i\sigma^{\alpha\beta}q_\beta}{2M}
 -\left[F_A\gamma^\alpha+F_P\frac{q^\alpha}{2M}\right]\gamma_5, \tag{7}
$$

with the sign convention fixed by $J=V-A$. A nucleus requires $J=\sum_iJ_i+\sum_{i<j}J_{ij}+\cdots$. A hole is a removed occupied nucleon state; a particle is an excited state above the occupied sea. In a local Fermi-gas representation, the schematic two-particle/two-hole tensor is

$$
 W^{\alpha\beta}_{2p2h}=\int d^3r\,d\Pi_{h_1h_2p_1p_2}
 n(h_1)n(h_2)[1-n(p_1)][1-n(p_2)]
 \delta^{(3)}(\mathbf h_1+\mathbf h_2+\mathbf q-\mathbf p_1-\mathbf p_2)
 \delta(\omega+E_{h_1}+E_{h_2}-E_{p_1}-E_{p_2}-E_{\rm rem})
 \overline{j^{\alpha *}j^\beta}. \tag{8}
$$

The measure includes conventional normalization, symmetry factors and isospin sums; $j$ is antisymmetrized. Equation (8) is explanatory, not executable replacement code. The residual energy convention must be specified once, consistently with the nuclear masses. A spectral function replaces the sharp occupation/removal prescription by a joint momentum–removal-energy distribution; this is how correlations enter beyond simply “more Fermi motion.” [Exclusive spectral-function formulation, Eq. (4)][exclusiveSF].

The microscopic Valencia construction includes pion/ρ exchange, correlated medium propagation, and weak pion-production vertices. The latter require a coherent set of pole and contact contributions; isolated graph rescaling can spoil the cancellations in the full current. RPA is the resummation of repeated particle–hole interactions in this response, not a new elementary vertex. The familiar geometric-series structure $\Pi=\Pi_0+\Pi_0V\Pi=(1-\Pi_0V)^{-1}\Pi_0$, understood as a channel-space expression, connects the nuclear calculation to dressed propagators. [Valencia 2020, section II A–B][valencia2020]; [exclusive Valencia 2026, section II][exclusive2026].

### A consistency correction and one physical nuisance parameter

The following denominator argument is this memo's pedagogical derivation. Suppose an external hole and intermediate nucleon move in the same constant potential $U$, with kinetic-plus-rest energy $\epsilon_p=\sqrt{M^2+\mathbf p^2}$. Their time-ordered denominator contains

$$
 D_N=(\epsilon_h+U)+\omega-(\epsilon_p+U)+i0
     =\omega+\epsilon_h-\epsilon_p+i0. \tag{9}
$$

If $U$ is retained on the external line but omitted on the intermediate line, an artificial $+U$ remains. This shifts amplitude denominators even though a common potential cancels in the external energy balance. For a Δ intermediate state, a genuine **relative** medium potential remains:

$$
 D_\Delta=\omega+\epsilon_h-\epsilon_\Delta
          -u_\Delta\rho(r)/\rho_0+i\Gamma_\Delta^*/2. \tag{10}
$$

The lesson is not that binding disappears. Physical separation energy, momentum-dependent potentials, residual excitation, and collisional widths remain. It is that a common energy-zero convention must not act like a fitted interaction. The proposed extension uses the published corrected current and its coherent diagram set; Eqs. (9)–(10) illustrate the issue, not the full relativistic spin-3/2 propagator. [Corrected prescription, section II B(c), Eq. (10)][valencia2025].

| Input | Proposed treatment | Independent motivation |
|---|---|---|
| Relative effective Δ shift $u_\Delta$ | One exploratory nuisance; nominal 0, envelope −50 to +30 MeV at $\rho_0$, proportional to density | Published range reflecting different longitudinal and transverse medium shifts; **not** a Gaussian 1σ constraint or a newly fitted prior |
| Two-nucleon separation energy $S_{NN}$ | Fixed by residual nuclear masses for the charge channel; published illustrative averages ≈27 MeV C, ≈22 MeV O | Energy conservation, not a second freely fitted energy shift |
| Form factors, density, exchange couplings, widths | Published baseline and independent constraints; record their uncertainties, freeze them in this bounded diagnostic | Avoid absorbing every discrepancy into the one scanned parameter |
| Overall MEC multiplier or $A,W$ bin weights | None | No independent justification for an extra normalization freedom |

The first two rows follow [section II B(a–b), Eqs. (6)–(9)][valencia2025]. One effective $u_\Delta$ is a pragmatic envelope over tensor channels, not a claim that all channels have the same microscopic self-energy. Its parameters and fixed ingredients must be supplied as a complete model version.

An elementary line-shape derivation explains why this can be more informative than a strength scale. For a fixed-width isolated contribution let

$$
 R(\omega,u)=\frac{C}{x^2+a^2},\quad
 x=\omega-\omega_{\Delta,0}-u\rho/\rho_0,\quad a=\Gamma^*/2.
$$

Then

$$
 \frac{\partial R}{\partial u}
 =\frac{2C(\rho/\rho_0)x}{(x^2+a^2)^2}. \tag{11}
$$

A negative shift moves the peak downward: locally it raises the lower flank and lowers the upper flank. If $C,\Gamma$ are fixed and the full real line is integrated, the area is unchanged. Thresholds, interference, density averaging and energy-dependent widths invalidate a universal area or sign claim for the full nuclear response. Equation (11) therefore predicts a useful **shape diagnostic at fixed true transfer**, not guaranteed signs in our broad $A$ bins.

The comparison must remain in the calculation's supported low-transfer domain. The published total-response comparison imposes $\lvert\mathbf q\rvert<1.2$ GeV, and its displayed T2K calculation omits flux above 3 GeV. Access to low $q$ at a 6 GeV beam energy does not, by itself, validate a numerical implementation at that beam energy. Establish tensor and phase-space support before flux folding. No extrapolation to the entire ME-FHC inclusive or DIS domain is proposed. [Fig. 8 and footnote 12][valencia2025].

### Symmetry, positivity and double counting

For a usable implementation:

- **Vector current:** enforce CVC in the isospin-symmetric limit, with current vertices and medium propagators treated consistently. In operator form the charge continuity relation involves the nuclear Hamiltonian, so changing a potential without its associated current can break it.
- **Axial current:** respect PCAC and the pion-pole structure, with form factors fixed by the chosen convention. Do not impose $q_\alpha A^\alpha=0$; the axial current is not conserved at finite pion mass.
- **Statistics and conserved quantities:** antisymmetrize identical nucleons; impose Pauli blocking and charge, baryon-number, four-momentum and residual-mass conservation event by event. An effective $q^0-S_{NN}$ is bookkeeping for the residual system, not permission to lose energy.
- **Positivity:** the complete spectral tensor has $c_\alpha^*W^{\alpha\beta}c_\beta\geq0$. Interference pieces need not be separately positive; replacing them by independently positive event classes can change the physics.
- **Limits:** multinucleon contributions vanish for a free single nucleon and in the dilute-density limit; phase space closes below threshold. Neither a nonzero hydrogen 2p2h rate nor strength beyond the admitted kinematic domain is acceptable.

These are theoretical requirements, not claims that a one-parameter propagator ansatz proves all Ward identities. The selected framework is a hadronic many-body model; it is not a systematically convergent low-order chiral EFT for all ME-FHC transfers. An independent reviewer must check the actual implementation against its full current.

Replacement must be defined at the response level. Use the updated multinucleon component **instead of** its predecessor, remove the empirical Tune v1 enhancement for that replaced component, and retain a documented, compatible QE/RPA prescription. Do not simply add an updated MEC table on top of an enhanced old table.

Three overlaps need explicit accounting. First, an imaginary nucleon self-energy describes rescattering cuts that can overlap correlation diagrams counted as 2p2h. Second, Δ absorption contributing to a pionless primary response must be distinguished from an on-shell pion produced at the vertex and subsequently absorbed in the cascade. Third, 3p3h cuts are not an extra unlabelled contribution to a two-nucleon event sample. The 2025 paper discusses the first overlap in section II C; the 2020 formalism explicitly separates the third. A spectral-function swap, current swap and cascade swap performed independently would not establish this accounting. [Valencia 2025, section II C][valencia2025]; [Valencia 2020, section II][valencia2020].

### Why an inclusive tensor is not yet an available-energy prediction

Let $X$ be a primary nuclear final state, $f$ the state leaving the nucleus, and $y$ reconstructed detector quantities. A generator realization requires

$$
 \frac{d\bar\sigma}{dA}=
 \int dE_\nu\frac{\phi(E_\nu)}{\Phi}
 \int d\xi_\mu\frac{d\sigma_{\rm inc}}{d\xi_\mu}
 \sum_X P(X\mid E_\nu,\xi_\mu)
 \sum_f K(f\mid X)\,\delta[A-A(f)]. \tag{12}
$$

The sums include continuous phase-space integrals. $P$ is the exclusive distribution consistent with the lepton-contracted current, not a universal phase-space guess; $K$ is the nuclear transport kernel. For reconstructed predictions, replace the delta function by $\int dy\,R(y\mid f,\xi_\mu)$ with selection and bin indicators. The detector response includes lost events. This factorization is a generator approximation requiring a defined boundary between quantum primary dynamics and transport. The published implementation comparisons expose its limitations. [Dolan et al., sections II and IV, Appendix C][susa]; [Kasturi et al., sections III–V][exclusive2026].

Consider pionless two-nucleon emission before rescattering. At fixed transfer and residual energy,

$$
 A_{pp}\simeq T_{p1}+T_{p2}\simeq\omega-E_{\rm rem},
 \qquad A_{pn}\simeq T_p.
$$

Pair sharing scarcely changes the first sum but directly changes the second observable. If the neutron takes more energy, $A_{pn}$ falls; if the proton takes more, it rises. This elementary bookkeeping explains why inclusive agreement does not determine $A$, and why neutron/proton measurements are decisive. Nuclear rescattering then mixes these simple identities.

An inclusive ratio weight $w(q)=\sigma_{\rm new}(q)/\sigma_{\rm old}(q)$ is adequate only for inclusive observables when support is complete and the remaining conditional distributions are intentionally unchanged. A semi-inclusive weight would require the ratio of the **full differential** primary probabilities, and possibly transport probabilities, on common support. It cannot create a missing channel, new nucleon multiplicity, or unsampled kinematic domain. The actual CV sample has no MEC events. A faithful replacement of primary sharing or addition of 3p3h will generally require new event generation, after separate authorization. [GENIE Valencia implementation, sections 3.2–3.3][genievalencia]; [new NuWro sampling, sections III–IV][nuwro2025].

There is a useful scale warning. If the tested MEC component were merely multiplied by 1.2–1.4, its quoted 52% fill below 0.4 GeV would become about 62–73% of the original gap, while worsening a lowest bin already filled at 106.5%. This is illustrative arithmetic, **not** the updated model's prediction; it shows why neither the published enhancement nor an inclusive reweight alone establishes the explanation.

## Falsifiable predictions and a bounded future validation

### Predictions that distinguish mechanisms

| Observable or comparison | Preferred-current prediction or diagnostic | What would challenge the explanation |
|---|---|---|
| True $(\omega,\lvert\mathbf q\rvert)$ at fixed lepton kinematics | Consistent denominators change multinucleon strength; varying a negative relative Δ shift moves its local response peak downward as in Eq. (11). | The implementation gives only arbitrary $A$-bin weights, violates the reference tensor, or needs unsupported high-transfer strength. |
| Our $A=0.1–0.4$ GeV residual | Improvement is a **hypothesis to calculate**, with 0–0.1 and 0.4–0.8 as overshoot controls. No definite cell-level sign follows without Eq. (12). | The physically allowed family cannot reduce the middle-bin residual without damaging adjacent bins once uncertainties and response are controlled. |
| Leading and subleading nucleon spectra; two-proton energy asymmetry | The exclusive-current calculation predicts different, generally more asymmetric sharing than isotropic pair decay in its tested domain. This must accompany any use of that kernel. | A fit to available energy requires the opposite sharing pattern in independent nucleon data. [Exclusive study, section IV][exclusive2026]. |
| Proton versus neutron energy and multiplicity | Pair charge and sharing correlate visible energy with missing neutron energy. A neutron-driven downward migration must have a complementary neutron signature. | The required invisible energy lacks the corresponding neutron/remnant distribution, or a neutron detector nuisance alone explains the change. |
| Neutrino versus antineutrino | The antisymmetric leptonic tensor reverses the VA-interference contribution; the same nuclear current must describe both without separate arbitrary normalization knobs. | A neutrino improvement produces an excluded antineutrino pattern after matching flux, target and selection. |
| Electron vector response and elementary-target weak data | The chosen vector/current inputs retain their independently constrained response; the nuclear pair correction is absent on free hydrogen. | Fixing neutrino data damages an accepted vector response or requires a new nuclear contribution on H. |
| High true-transfer inelastic region | The bounded low-transfer replacement is not intended to repair this region; it supplies a control against an indiscriminate all-event scale. | Apparent improvement requires the low-transfer model to extrapolate into the high-$Q^2$, high-invariant-mass region. |

Transverse imbalance adds information complementary to $A$: define $\delta\mathbf p_T=\mathbf p_T^\mu+\mathbf p_T^p$, and compare its magnitude, the muon–proton transverse opening angle and the angle of $\delta\mathbf p_T$ relative to the inferred transfer. Initial momentum, two-body currents and rescattering affect these differently. None is a pure mechanism tag. Their utility is that a single specified model must predict their **joint pattern**, including proton thresholds, without a second fit to each distribution.

### External constraints and validation samples

| Data | Role and independence |
|---|---|
| Carbon/oxygen inclusive electron response and electron knockout | Constrain vector response, energy balance and transport. Use kinematics matched in true transfer; electron agreement alone leaves axial freedom. e-GENIE comparisons provide a practical starting map. [Sections II–III][egenie]. |
| MiniBooNE and T2K CC0π distributions already shown in the revised Valencia paper | Reproduce published benchmarks and establish implementation fidelity. They are **not** fresh independent validation of that model. |
| Original MINERvA low-recoil neutrino sample | Tune v1 development input, hence not independent validation of its empirical enhancement. [Rodrigues et al., discussion of the low-$q_3$ excess and model comparison][lowrecoil]. |
| MINERvA antineutrino multi-neutron, low-available-energy cross section | Particularly useful withheld topology and beam polarity: at least two neutrons with $T_n>10$ MeV and available energy <100 MeV. Match its broader particle definition and neutron response. It shares experiment-level systematics but not the FHC event sample. The published comparison finds tension in low-energy neutron candidates, so detector uncertainty is central. [Sections II, IV–V][multineutron]. |
| MicroBooNE CC two-proton final state on argon | Different detector, flux and nucleus; directly probes sharing and topology. A carbon calculation needs an independently justified argon extension and exact published cuts. Use only if not part of model development. [Measurement][microboone]. |
| MINERvA 2026 LE/ME triple-differential QE-like comparison | Tests energy dependence and recoil conditional on muon variables. Useful new literature beyond the original comparison versions, but ME data may overlap this analysis and flux/response correlations remain. [Sections V–VI, preprint][leme2026]. |
| Dedicated pion, SIS and elementary H/D measurements | Constrain candidate 3 and pion-absorption alternatives, rather than allowing them to compensate an arbitrary pair-current fit. [SIS selection][sis2025]; [bare-nucleon tuning inputs][baregenie]. |

Our lowest and adjacent $A$ bins and selected muon slices can be excluded from a future development fit, but they have already been inspected. Call them **withheld from fitting**, not blind discovery data. The 42-cell map and s5p tests are also already observed. Independence requires auditing event overlap, flux and detector correlations, shared theory inputs, and which data were used to tune each baseline.

### A finite proposal for a later authorization

The future question should be: **Does the published current replacement, with its constrained Δ envelope and exclusive final states, improve the low-transfer distribution and predict complementary nucleon data without compensating detector or normalization shifts?** It should not be “can a flexible model fit our entire map?”

1. **Definition and implementation gate.** Produce one complete configuration for the predecessor and one for the corrected model: versions, current inputs, channel bookkeeping, target mixture, energy support, stable-particle convention and transport boundary. Reproduce published inclusive and exclusive benchmarks. Stop if the required tensor/primary-event support cannot be established. No fitting our data at this stage.
2. **Bound the development family.** Use the published nominal model and the two declared $u_\Delta$ endpoints, with the published exclusive prescription. Do not introduce per-bin weights, an extra MEC normalization, or free form-factor changes. If external data justify interpolation of $u_\Delta$, fit it only in a declared development set and freeze the result. Electron constraints and elementary-current inputs must remain satisfied. This is one candidate family, not an open model search.
3. **Make detector-level and analysis-level predictions.** A separately authorized simulation stage would generate adequate final-state support, apply matched response and backgrounds, and propagate through the exact intended analysis. Include species/energy-dependent hadronic response, neutron response, migration, efficiency, flux and target uncertainties. Vary the null and the extraction consistently. Check estimator bias and coverage for the comparison being claimed; do not take the adopted scalar covariance as a complete likelihood. Report low-$A$, adjacent-bin, muon and nucleon predictions together.
4. **One independent validation round.** Freeze a small family of primary comparisons before evaluating withheld data: one neutrino nucleon-sharing observable, one antineutrino neutron observable, and the designated available-energy/adjacent-bin control. An independent reviewer should approve the observable definitions, dependence structure and calibration. Predeclare a 5% familywise rejection rule if calibrated hypothesis tests are used; define power/precision requirements from the predicted model separation, not from a desired outcome. Do not recycle the old s5p p-values as this model's test.
5. **Terminal decision.** One synthesis and one independent review, with at most one focused correction/review of implementation defects. No repeated parameter expansion after seeing validation failures. Joseph decides whether evidence warrants an implementation project or whether the hypothesis is rejected or remains unresolved. Event counts and computing resources belong in that later authorization; this memo requests and consumes no production budget.

**Failure** would be a conserved-current or channel-accounting defect; conflict with independent vector/weak constraints; a required parameter outside the declared envelope; controlled adjacent-bin overshoot; or an independently excluded proton/neutron pattern accompanying a purported $A$ improvement. A calibrated failure is stronger than the absence of a best fit.

**Inconclusive** would mean inadequate kinematic support, detector/model degeneracy, insufficient precision, uncalibrated estimator bias, or absent data correlations. For example, a pair-current increase and a neutron-response shift that produce indistinguishable selected distributions cannot be distinguished by choosing the smaller residual.

**Sufficient evidence to justify implementation** would combine reproduction of the theoretical calculation, clean overlap bookkeeping, improvement in the specified low-transfer distribution, and successful frozen predictions for complementary neutrino and antineutrino topologies with useful sensitivity. Fitting our discrepancy alone is insufficient. Implementation would still not constitute analysis or publication adoption.

For independent review, invite **Noemi Rocco**, or another theorist outside the selected Valencia calculation, to assess currents, spectral overlap and exclusive consequences; her recent exclusive spectral-function work is directly relevant. A separate experienced generator developer, for example **Stephen Dolan**, could review tensor-to-event consistency and response-facing assumptions. These are suggested expertise matches, not claims of availability or guaranteed independence; check collaboration and development involvement before appointment. The preferred model's authors are valuable technical consultants but should not be its sole independent validators. [Rocco and Steinberg][exclusiveSF]; [Dolan et al.][susa]. No contact has been made.

## Follow-up: computing cost and experimental use

This estimate answers Joseph's follow-up and grants no computing authority. No throughput benchmark for the corrected exclusive calculation has been run in this session. CPU core-hours below are conditional arithmetic, not a measured budget or wall-time guarantee.

| Stage | Work and cost basis |
|---|---|
| Inclusive benchmark | With validated response tables in hand, contract the hadronic tensor with the lepton tensor and integrate over the flux and cuts. This is suitable for a CPU workstation. It does not predict the exclusive hadronic distribution required for available energy. The cost of producing new response tables is not established. |
| Exclusive truth-level comparison | Illustrative scope: one million generated events at each of the nominal and two declared Δ-shift endpoints, three million total. At an **assumed**, unmeasured 0.1–1 CPU-second per generated event this costs 83–833 CPU core-hours, or ideally 2.6–26 hours on 32 fully utilized cores. Table production, integration setup, implementation work and a newly generated matched predecessor are additional. A microscopic exclusive sampler could be substantially slower. |
| Detector and analysis validation | Budget from measured detector/reconstruction time and the number of analysis repetitions. For three million events, every 10 CPU-seconds per event adds about 8,333 CPU core-hours. This scaling is not a claim about MINERvA throughput. Reuse of existing detector simulation requires valid exclusive reweighting and phase-space support; otherwise new simulation is needed. |

For approximately independent, positively weighted events, a bin's relative MC precision scales as $1/\sqrt{N_{\rm eff}}$, where $N_{\rm eff}=(\sum w)^2/\sum w^2$. Roughly 2,500–10,000 effective events per bin give 2–1% statistical precision. Generated counts must allow for selection efficiency, rare topologies and weight dispersion; three million events alone do not guarantee adequate precision. A small, separately authorized 1,000–10,000-event pilot would measure throughput, acceptance and effective statistics before fixing a larger allocation. CPU generation has no inherent GPU requirement; a new learned exclusive sampler would be a separate development and benchmarking task.

The main unresolved cost is access to a correct exclusive implementation. Kasturi et al. explicitly warn that naive high-dimensional tabulation is impractical and discuss on-the-fly sampling or surrogate models. Therefore an inclusive-table swap should not be priced as a finished available-energy model. [Section VI][exclusive2026].

**Experimental contact exists, with three distinct levels of evidence.**

1. **The exact correction has been compared with real data.** Sobczyk and Nieves' 2025 paper compares its revised predictions with previously published MiniBooNE carbon and T2K carbon/oxygen CC0π lepton distributions, reporting good agreement. These are theory-to-data comparisons, not a new experimental extraction adopting the corrected model. They are already model benchmarks and should not be labeled fresh independent validation. [Journal abstract][valencia2025journal]; [section III][valencia2025].
2. **Related exclusive implementations appear in new experimental comparisons.** T2K's July 2026 carbon/oxygen kinematic-imbalance measurement compares with NuWro 25.03.1 and cites both the NuWro implementation and the 2025 revision. However, the NuWro implementation paper explicitly excludes that revision, and the release author's description identifies Valencia 2020. The T2K citation alone does not establish which corrected tensors were actually used; verify the precise configuration before counting this as a test of the self-energy correction. Its overall generator comparison also cannot isolate that correction from the ground state and transport. [T2K, “Comparison to generator predictions” and “Discussion of the results”][t2k2026imbalance]; [NuWro introduction, footnote 1][nuwro2025]; [release author's description][nuwro2503description].
3. **Full experimental validation of the corrected exclusive prediction remains unestablished by these sources.** The 2026 exclusive paper includes a NEUT cascade and SuperFGD threshold study, explicitly leaving full detector simulation and experimental constraints to further work. MicroBooNE's 2026 electron-neutrino CC0π measurement describes inclusion of the revised self-energy model in generators as ongoing and its data comparison as future work. Neither establishes that it explains our MINERvA available-energy discrepancy. [Exclusive study, sections V–VI][exclusive2026]; [MicroBooNE, discussion immediately before section IV][microboone2026electron].

## Focused learning plan

The aim is to turn QFT fluency into the ability to audit one nuclear-response calculation, rather than first survey every generator model.

1. **Translate a tensor into the actual measurement.** Work through Eqs. (5)–(8), separate VV, AA and VA terms, and derive the neutrino/antineutrino interference change. Then derive Eqs. (3)–(4) from the repository definitions. Deliverable: one page distinguishing $\omega$, $A$, $q_3$, experimenter's $W$ and actual invariant mass. Read [Valencia 2020, section II][valencia2020] and [EAVAIL_DEFINITION][eavail].
2. **Learn nuclear states and their energy bookkeeping.** Study occupations, holes, Pauli blocking, separation energy and spectral functions. Derive the common-$U$ cancellation and identify what remains for momentum-dependent self-energies. Deliverable: an energy-conserving pp and pn example with an explicit residual nucleus. Read [Valencia 2025, section II B–C][valencia2025] and [exclusive spectral-function paper, section II][exclusiveSF].
3. **Connect diagrams, cuts and responses.** Trace pion/ρ exchange, Δ-hole excitations and RPA into a hadronic tensor; identify which cuts produce 1p1h, 2p2h, 3p3h and real pions. Deliverable: a channel-overlap diagram explaining why adding a spectral function, MEC and cascade independently can double count. Read [Valencia 2020, section II][valencia2020] and [Valencia 2025, section II C][valencia2025].
4. **Learn how generators lose exclusive information.** Contrast a tensor table followed by isotropic pair decay with a differential current. Derive the pp/pn visible-energy identities and Eq. (12). Deliverable: a list of the event-level quantities needed for a valid reweight. Read [SuSAv2 implementation, section II and Appendix C][susa], [GENIE Valencia, section 3][genievalencia], and [exclusive Valencia 2026, sections III–V][exclusive2026].
5. **Design the external test before adjusting parameters.** Read the neutron and two-proton measurements, write their exact particle/threshold definitions, and classify their shared inputs with our analysis. Deliverable: the three-observable frozen validation specification, including failure and inconclusive outcomes. Read [multi-neutron sections II–V][multineutron], [MicroBooNE two-proton measurement][microboone], and [MINERvA LE/ME comparison, sections V–VI][leme2026].

The scientific decision supported now is narrow: investigate a known consistency correction with complementary final-state tests. A new minimal theory explaining the whole MINERvA discrepancy is not established by the present evidence.

## Source index

Repository references resolve to remote-main commit `3892e769043cddebfd58ec19e1ab1a567eb01784`. The evidence table uses the ledger and original receipts, rather than treating front-door summaries as measurements. Literature dates refer to actual publication/submission records; dynamically generated HTML masthead dates are not publication dates. The 2026 and late-2025 sources marked preprint are used as research developments, not as experimentally validated resolutions.

[agents]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/AGENTS.md
[current]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/CURRENT_WORK.md
[campaign]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/CAMPAIGN-REVIEW-20260929.md
[claims]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/publication/CLAIMS-20261005-claim-to-evidence.md
[paper]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/analysis-note/paper_body.tex
[ledger]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/VALIDATION_LEDGER.md
[issues]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/KNOWN_ISSUES.md
[pairing]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md
[followup]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/next-preparation-20261009/two-d-followup/REPORT.md
[integration]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/next-preparation-20261009/xr-sb1-integration/REPORT.md
[figmanifest]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/publication/release/figs/_data/fig_arrays.npz.manifest.json
[context]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/s5p/stage7/generator-context/generator-context-receipt.json
[selection]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp
[cvuniverse]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h
[converter]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/3d-unfolding/genie/gen_to_xsec5d.py
[eavail]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/EAVAIL_DEFINITION.md
[fluxfix]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/s5p/gen5d/README-gen5d-fluxfix.md
[genielaunch]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/3d-unfolding/genie/run_gevgen.sh
[meclaunch]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/3d-unfolding/genie/sbatch_gevgen_mec.sh
[nuwrolaunch]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/3d-unfolding/genie/run_nuwro.sh
[gibuucard]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/3d-unfolding/genie/work_gibuu/gibuu_mefhc_numu.job
[modes]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/s5p/stage7/generator-context/mode_decomp_eavail-log.txt
[meclog]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/s5p/stage7/generator-context/compare_mec_eavail-log.txt
[capshare]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/state/note-capgap-20261003/cap_share.json
[adoption]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md
[operative]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/OPERATIVE-SHEET-scalar5d.md
[s5p]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md
[delivery]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md
[fsiabs]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/3d-unfolding/genie/genie_fsi_FrAbs_pi_xsec3d_summary.txt
[fsiinel]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/3d-unfolding/genie/genie_fsi_FrInel_pi_xsec3d_summary.txt
[inclusivepaper]: https://arxiv.org/html/2106.16210v4
[ascencio]: https://arxiv.org/pdf/2110.13372
[geniereleases]: https://genie-mc.github.io/releases.html
[genietunes]: https://genie-mc.github.io/tunes.html
[valencia2025]: https://arxiv.org/html/2407.21587v1
[valencia2025journal]: https://journals.aps.org/prc/abstract/10.1103/PhysRevC.111.025502
[valencia2020]: https://arxiv.org/html/2002.08302
[nuwro2025]: https://arxiv.org/html/2411.11523v1
[exclusive2026]: https://arxiv.org/html/2603.28314v1
[exclusive2026journal]: https://journals.aps.org/prd/issues/114/1
[t2k2026imbalance]: https://arxiv.org/html/2607.10638v2
[nuwro2503description]: https://indico.cern.ch/event/1528564/contributions/6613509/
[microboone2026electron]: https://lss.fnal.gov/archive/2026/pub/fermilab-pub-26-0054-csaid-ppd.pdf
[exclusiveSF]: https://arxiv.org/html/2602.02231v1
[sf2026]: https://arxiv.org/html/2605.00756v1
[susa]: https://arxiv.org/html/1905.08556v3
[axial2025]: https://arxiv.org/html/2512.14097v1
[egenie]: https://arxiv.org/html/2009.07228
[baregenie]: https://arxiv.org/html/2104.09179
[agky]: https://arxiv.org/html/2106.05884
[sis2025]: https://arxiv.org/html/2503.20043v1
[genievalencia]: https://arxiv.org/html/1601.02038
[lowrecoil]: https://arxiv.org/abs/1511.05944
[multineutron]: https://arxiv.org/html/2310.17014
[microboone]: https://arxiv.org/abs/2211.03734
[leme2026]: https://arxiv.org/html/2606.00745

[fsi2026]: https://arxiv.org/html/2609.22662
[status2d]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md
[status3d]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/3d-unfolding/3D_OMNIFOLD_STATUS.md
[statusnd]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/3892e769043cddebfd58ec19e1ab1a567eb01784/nd-unfolding/ND_OMNIFOLD_STATUS.md
