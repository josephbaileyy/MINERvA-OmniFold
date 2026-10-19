# M4: truth θ axis, truth-W residual and generator W convention (record)

**Run by** a Claude agent for the director, 2026-10-19, on Perlmutter login nodes, about 3 CPU-minutes, no batch job. Scripts, results and input hashes are in [`m4-w/`](m4-w/). The agent could not write this file, so the director saved its final report verbatim below.

**Summary for the paper.**
- **Truth angle.** The truth muon angle is measured from a fixed beam axis tilted −58.87 mrad about x (MAT `TruthFunctions.h:21-27`). It is not measured from the true neutrino direction.
- **Truth W.** Because of that tilt, truth W is not an exact function of (pT, p∥, q3, M). The residual is within ±2 MeV for 68% of events and within −49/+67 MeV for 99.9%. 0.25% of events (weighted) change J W bin, and 0.15% have no real solution.
- **Reco W.** Reco W² = (M̄+q0)² − q3² holds exactly, apart from the W² clamp, which fires for 1.5% of events.
- **Generator W convention.** The predictions use a fixed M_n and set W = 0 when W² ≤ 0; the analysis does not. Switching them to the analysis convention moves J-cell predictions by 0.13% (GENIE CV) and 0.087% (NuWro) at the median, 1.6% and 2.2% at most. Those shifts are at or below each prediction's per-cell MC statistical error.
- **New point.** The analysis truth pT (beam axis) and the generators' pT (neutrino axis) differ per event by ±4 MeV (68%), and 3.1% of events change fine pT bin. The net effect on cell contents is not measured.
- **Correction.** This replaces the unmeasured "fixed to within tens of MeV" wording used in the triage and in the director's messages.

**CITABLE FOR:** these measurements.
**NOT CITABLE FOR:** the net J-cell effect of the axis convention, a comparison with the data covariance, or GiBUU's W convention effect (inferred, not measured).

---

## M4 W measurement: truth θ axis, truth-W residual, generator W convention

All three questions are answered with numbers. The main finding: **at truth level, W is not an exact function of (pT, p∥, q3)**. The truth muon angle is measured from a fixed beam axis, not the true neutrino direction, and that is the only thing that breaks the relation. The leftover differences are a few MeV for most events, with tails up to hundreds of MeV. At reco level the relation is exact. The generator W convention moves the 109 J-cell predictions by about 0.1% typically and at most about 2%.

Everything ran on login16 on login nodes, with no Slurm and roughly 3 minutes of CPU in total. I made no git edits anywhere and wrote nothing outside `/pscratch/sd/j/josephrb/methods-paper/m4-w-20261019/`.

### Q1: truth θ is measured from a fixed tilted beam axis
**Source checkout.** Two cluster checkouts exist, and both are at the cited shas with clean git status:
- `~/MINERvA101/{MAT,MAT-MINERvA}`
- `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/{MAT,MAT-MINERvA}`

| Item | Value |
|---|---|
| MAT sha | `35097b65ab16…` |
| MAT-MINERvA sha | `50d7631416d1…` |
| `MAT-MINERvA/calculators/TruthFunctions.h` sha256 | `e6df3503…66f27d` |
| `MAT-MINERvA/utilities/PlotUtilsPhysicalConstants.h` sha256 | `386979d5…eb098` |
| `MAT/PlotUtils/BaseUniverse.cxx` sha256 | `60e5f2de…c2d5b` |

The installed `opt/include/{PlotUtils,calculators}/TruthFunctions.h` copies are byte-identical to the source in both trees. CVU includes it at `CVUniverse.h:25`.

**`TruthFunctions.h`:**
- `GetElepTrue` (:10-12) = `mc_primFSLepton[3]`
- `GetPlepTrue` (:14-19) = |`mc_primFSLepton` 3-vector|
- `GetQ2True` (:37-39) = `mc_Q2`
- `Getq3True` (:45-47) = `calcq3(GetQ2True(), GetEnuTrue(), GetElepTrue())`, with `calcq3 = sqrt(Q2+(Enu-Elep)^2)` at `BaseUniverse.cxx:81-82`
- `GetThetalepTrue` (:21-27):
```
double GetThetalepTrue() const { /* radians w.r.t. incident nu dirn */
  TVector3 p3lep(GetVecElem("mc_primFSLepton", 0), ..., 2));
  p3lep.RotateX(MinervaUnits::numi_beam_angle_rad);
  return p3lep.Theta();
```
The constant is `static const double numi_beam_angle_rad = -0.05887;` (`PlotUtilsPhysicalConstants.h:44`).

**Answer.** θ is measured from the beam axis with a fixed tilt of −58.87 mrad about x. It does not use `mc_incomingPartVec` and it is not detector z. The comment "w.r.t. incident nu dirn" is only an approximation.

**Measured on a MasterAnaDev truth tuple** (Playlist1A run 110000, sha256 `172a0087…e82460b`; 65,911 signal events, which matches the `EAVAIL_DEFINITION` count). The angle between the true ν and the MAT axis is:
- median 1.03 mrad
- 68% range [0.51, 1.92] mrad
- 95% range [0.19, 3.29] mrad
- max 6.1 mrad

Against detector z the same angle is 58.6 mrad, so the sign of the rotation is right.

**Control.** If θ is instead measured from the true ν direction, W_true − W_pred has max |·| = 7e-9 MeV. **The fixed-axis tilt is the only thing breaking the truth relation** apart from the choice of M.

### Q2: truth W residual
**Input.** `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_MEFHC.root`, sha256 `b6d2651c…98dd5175a`. This is the `cv_omnifile` in `s5c/contract.json`.

I used the full `mc_truth_denom` tree, 32,849,103 rows, with no subsampling. I applied the `und:333-358` gate (finite values, 0 ≤ w < 1e4, the inclusive Python phase space).
- 1,474 in-phase-space rows have NaN W (a 4.9e-5 weight fraction). Removing them leaves 32,846,302 rows.
- The omnifile has no struck-nucleon id, so the headline uses **M̄ = 939.048 MeV**.
- Root choice: Eν = p∥ + sqrt(q3² − pT²); the other root is unphysical.
- q3² < pT² for **49,754 events (0.15%, a 0.086% weight fraction)**, so W_pred is undefined for them. This happens only because of the tilt: about the ν axis q3 ≥ pT always holds.

**W_true − W_pred (MeV):**

| Sample | median | 68% | 95% | 99.9% | max abs |
|---|---|---|---|---|---|
| Omnifile, M̄ | +0.23 | [−2.20, +2.08] | [−10.0, +11.3] | [−48.9, +66.6] | 544 |
| Omnifile, best-of-{M_n, M_p, M̄} (lower envelope for the M part) | +0.04 | [−0.87, +1.18] | [−9.1, +10.6] | [−48.0, +66.0] | 541 |
| MAD tuple, per-event M | 0.00 | [−1.61, +1.70] | [−10.3, +11.1] | [−50.0, +67.3] | 197 |
| MAD tuple, M̄ | +0.26 | [−2.19, +2.10] | [−10.1, +11.5] | [−49.5, +67.9] | 195 |

The MAD-tuple M̄ row reproduces the omnifile distribution. That supports reading the omnifile residual as tilt plus M.

**Fraction of events whose W bin changes** (with M̄; undefined W_pred counted as a change):

| Binning | unweighted | weighted |
|---|---|---|
| fine W bins | 0.57% | 0.58% |
| J W bins | 0.32% | 0.25% |

With per-event M on the MAD tuple these drop to 0.41% (fine) and 0.17% (J).

**Where the residual sits:**
- By true W, the 68% range is ±5.4 MeV below 1.4 GeV, ±1.6 MeV in 1.4–2.2 GeV, and ±1.6 MeV above 2.2 GeV. The largest values are all in the low-W bin.
- By tilt (MAD quartiles of α), the RMS rises steadily: 2.2 / 4.2 / 6.1 / 9.1 / 12.3 MeV for α up to 0.65 / 1.03 / 1.57 / 2.79 / 6.1 mrad. That is roughly 4–6 MeV of RMS per mrad.
- The predicted Eν is off from the true Eν by 68% ±3 MeV, 99.9% [−66, +54] MeV.

**The tilt also moves pT** (MAD tuple):
- pT(beam axis) − pT(ν axis): 68% ±4.3 MeV, 99.9% ±52 MeV.
- 3.1% of signal events change fine pT bin; 0.07% change p∥ bin; 89 of 65,911 change the phase-space decision.
- The generators measure pT about their own ν axis (+z), so their pT differs from the analysis truth pT by this smearing. These are per-event migrations only; I did not compute the net effect on cell contents.

**Reco check.** The omnifile does not store q0. I recovered it by inverting reco q3 (Eμ = sqrt(p² + M_mu²) with M_mu = 105.6583, as in `GetEmu`; Q² clamp handled), then compared sim_W with sqrt(max(0, (M̄+q0)² − q3²)).

| Tree | events | max abs residual (MeV) | Q² clamp fired | W² clamp fired (W = 0) |
|---|---|---|---|---|
| sim (20,498,013 passing) | 20,498,013 | 3.2e-7 | 0 | 316,227 (1.5%) |
| data | 4,119,797 | 4.4e-8 | 0 | 67,737 (1.6%) |

**Reco W is an exact function of (pT, p∥, q3)**, apart from the W² clamp.

### Q3: generator W convention in the J cells
The struck-nucleon id is in both files (`hitnuc`), so I did not need the M-spread bound for these two:
- GENIE CV: 2112 = 574,948, 2212 = 350,715, 0 = 12,478 (COH, which gets M̄).
- NuWro: 2112 / 2212 / 0 = 810,435 / 437,237 / 14,325.

I used the flux-fix weights r(E) from `gen5d_flux_reweight.flux_weights`, with `phi_t.npz` sha256 `bbcbade3…`; NuWro uses weight × r. **The 50–100 GeV supplement samples are not included.** The 109 J cells come from local `contract.json` at `c5aa0e90` (sha256 `d54fd7c9…`). Because every J edge is a fine edge, each event's coarse bin is its J cell.

Inputs:
- GENIE: `…/3d-unfolding/genie/genie_mefhc_cv_ALL.gst.root` (`bafb698c…`), flux `flux_mefhc_numu.root` (`91b5b899…`)
- NuWro: `gen5d/nuwro_flat5d/nuwro_flat5d_p{1..8}.root` (hashes in `probe_gen.json`), flux `flux_mefhc_numu_nuwro.root` (`1d016921…`)

**Cross-checks reproduce the build record.**
- Fine-W-bin changes: 1,438 (GENIE) and 1,757 (NuWro).
- NaN W under the analysis convention: 29 and 37, the same events that are W = 0 under the fixed convention.
- NuWro's stored W matches a recomputation with fixed M_n to 3.6e-5 GeV.

**μ_c(analysis W)/μ_c(fixed M_n) − 1 over the 109 cells, flux-fix weighted:**

| | median abs | max abs (cell) | cells above 1e-3 | supported total | shift ÷ per-cell MC stat, median / max |
|---|---|---|---|---|---|
| GENIE CV | 0.13% | 1.57% (J240) | 66 | −7.9e-5 | 0.08 / 0.88 |
| NuWro | 0.087% | 2.19% (J91) | 51 | −5.7e-5 | 0.05 / 1.13 |

- Unweighted counts give nearly the same picture: medians 0.14% and 0.10%, maxima 1.51% and 2.19%.
- The largest moves are at the W = 1.4 GeV J boundary, in mid-E_avail and mid-q3 cells, and go one way: 40–85 events move in or out.
- The cause is the 1.3 MeV M_p/M_n difference, which moves W by about (M+q0)/W × ΔM, plus the W = 0 versus NaN handling.
- GiBUU cannot be evaluated because it has no nucleon id. By analogy with GENIE and NuWro its effect would be at the same 1e-3 typical, about 2% maximum scale, but that is inferred, not measured.

### What this means for the paper text
1. **Truth W is not redundant in exact form.** The paper should say the truth θ (and so pT, p∥) is measured from a fixed beam axis tilted 58.87 mrad from detector z, while q3 uses the true neutrino four-vector. W is then fixed by (pT, p∥, q3, M) up to the event-by-event ν-direction spread of about 1 mrad: residual 68% within about ±2 MeV, 99.9% within −49/+67 MeV, 0.25% (weighted) of events change J W bin, and 0.15% have no real solution.
   - This replaces the unmeasured "tens of MeV" wording, and settles Inconsistencies 3 and 8.
   - Reco W² = (M̄+q0)² − q3² can be stated as exact.
2. **Generator W convention (Inconsistency 1).** The paper should say the predictions use a fixed M_n and W = 0 when W² ≤ 0. Switching to the analysis convention changes the J-cell predictions by about 0.1% median and at most 2.2%, which is at or below each prediction's own per-cell MC statistical error and well inside the claimed agreement. So the difference is disclosure-level, not result-changing. One caveat: I did not compare these shifts to the data covariance.
3. **New point.** The analysis truth pT (beam axis) and the generators' pT (ν axis) differ per event by 68% ±4 MeV, and 3.1% of events change fine pT bin. This is worth one sentence next to the axis statement; its net effect on cell contents is unmeasured.

### Commands
Each probe was run as `source env.sh` (`module load python; conda activate root_6_28`) followed by:
- `python probe_mad.py <MAD tuple> $PWD probe_mad.json` (16 s)
- `python probe_omni.py <omnifile> $PWD probe_omni.json` (1:46, 6.9 GB peak memory)
- `python probe_gen.py $PWD probe_gen.json` (40 s)

### Files in /pscratch/sd/j/josephrb/methods-paper/m4-w-20261019/
- **Scripts:** `common.py` (`93719de7…`), `probe_mad.py` (`f6a80440…`), `probe_omni.py` (`a5708789…`), `probe_gen.py` (`49800935…`), `env.sh`, `jcells.json` (`a9b387c9…`)
- **Results:** `probe_mad.json` (`5e7573b3…`), `probe_omni.json` (`d1231bc9…`), `probe_gen.json` (`ce4d7a7d…`, includes the per-cell values for all 109 cells)
- **Logs:** `probe_{mad,omni,gen}.{log,err}`
- **Hashes:** `MANIFEST.sha256`, `mad_input.sha256`, `omni_input.sha256`

Local copies of the scripts are in `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/m4w/`. None of this is committed, so it cannot be cited as evidence yet.