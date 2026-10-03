# GiBUU E_ν cap in the (E_avail, W) corner — share measured in the other generators (2026-10-03)

**Question.** The GiBUU 2019 sample stops at E_ν ≈ 20 GeV (`KNOWN_ISSUES.md` 82). How much of GiBUU's larger
corner shortfall (data/GiBUU 1.607 in the corner against 1.386 integrated, `VL156`/`VL157`) does that cap explain?

**Method.** `cap_share.py` (sha256 `d96b64b4…`) imports the s5p flux-fix code unchanged and rebuilds the
flux-repaired GENIE-CV, GENIE+MEC and NuWro < 50 GeV 5D products from their events, once with the full
per-event flux weight r and once with r · [E_ν < 20 GeV]. The E_ν ≥ 20 GeV share is 1 − σ(E_ν < 20) / σ(full
product), where the full product adds the 50–100 GeV supplement. Corner = E_avail ≥ 0.8 GeV and W ≥ 1.8 GeV
(3 × 3 cells of the 5D grid), projected over p_T, p_∥ and q_3 with the bin volumes. Central values only.
Run on Perlmutter login33, 2026-10-03, `root_6_28` conda env (python 3.11.14), 59 s; written only to
`/pscratch/sd/j/josephrb/note-capgap-20261003/`.

**Inputs (sha256).** Code: `gen5d_flux_reweight.py` `89863318…`, `gen5d_flux_supplement.py` `ff7a2d0e…`,
`gen_to_xsec5d.py` (gen5d tree) `1608acd5…`. Products in `/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/`:
`genie_cv_xsec5d.npz` `59b41776…`, `genie_mec_xsec5d.npz` `fda2eb86…`, `nuwro_cv_xsec5d.npz` `f5231637…`,
`genie_cv_xsec5d_full.npz` `cfa42210…`, `genie_mec_xsec5d_full.npz` `c179855d…`, `nuwro_cv_xsec5d_full.npz`
`475a2871…`, `gibuu_cv_xsec5d_fluxfix.npz` `48917692…` (the full-product and GiBUU digests are the inputs named
in `state/s5p/stage7/generator-context/*_xsec_eavailW.json`). Output `cap_share.json` `1e4f3f66…`.

**Controls (all pass).**
- The per-event rebuild with the full r reproduces each committed < 50 GeV product **bitwise** (all three).
- The full products give corner data/generator 1.142 / 1.139 / 1.160 and GiBUU 1.607, and integrated
  σ 2.7645 / 2.8756 / 2.6628 / 2.2152e-38 cm²/nucleon: `VL156` and `VL157` exactly (data corner 1.3497e-38,
  data integrated 3.0699e-38).
- The integrated E_ν ≥ 20 GeV shares, 6.96 / 6.79 / 7.43%, reproduce the flux-fix README's "6.8–7.4% of the
  in-grid σ".

**Result.**

| | E_ν ≥ 20 share, corner | E_ν ≥ 20 share, integrated | corner / integrated (full) | same, E_ν < 20 only |
|---|---:|---:|---:|---:|
| GENIE-CV | 14.30% | 6.96% | 1.028 | 1.117 |
| GENIE+MEC | 14.46% | 6.79% | 1.067 | 1.162 |
| NuWro | 14.82% | 7.43% | 1.006 | 1.094 |
| GiBUU (sample < 20 GeV) | — | — | 1.160 | — |

- Restricted to the common E_ν < 20 GeV domain, the other generators' corner-to-integrated contrast is
  1.09–1.16, bracketing GiBUU's 1.16.
- Supplying GiBUU the others' E_ν ≥ 20 GeV shares instead gives data/GiBUU ≈ 1.37–1.38 in the corner and
  1.28–1.29 integrated, a contrast of 1.06–1.07, inside the others' 1.01–1.07. This assumes GiBUU's high-energy
  share resembles theirs (they agree with each other to 0.5 points).
- **Reading:** GiBUU's extra corner shortfall is its E_ν cap, not a corner-specific generator difference. GiBUU
  stays the most deficient generator overall and in the corner.

Statistics: 3,245 / 3,181 / 4,444 raw in-phase-space events with E_ν ≥ 20 GeV fall in the corner of the < 50 GeV
samples (plus the 50–100 GeV supplements). Single-lane measurement, not independently reviewed.
