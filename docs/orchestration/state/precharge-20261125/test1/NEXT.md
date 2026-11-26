# Proposed next tests (not run)

This is a proposal only. Joseph decides what runs. Test 1 found two features. In every reco p∥ band, Data/fold rises with E_avail at fixed p∥. Separately, at E_avail < 1 GeV the excess grows with p∥: held-out Data/fold is 0.85, 1.23 and 1.51 at 40–50, 50–60 and 60–80 (`README.md`). Each test below targets one feature and says what a terminal result can and cannot settle. A and B are local, read the same saved event tables as Test 1 and use 0 node-hours. Only C needs NERSC.

## A. Does one recoil function describe all bands? (the rise with E_avail)

- **Compute.** Fit Data/fold = a(p∥ band) · b(E_avail) on good negative tracks in the training playlists, then score the held-out six. As a second fit, apply a single data E_avail scale factor s, scanned from 0.90 to 1.20, to the data histogram in every band.
- **Discriminates.** A common b(E_avail), or one scale s, that fits all five bands points to a recoil response or a hadronic-model shape that is independent of the muon. If the E_avail slope steepens with p∥, it tracks the neutrino energy at fixed muon momentum. That would support a rate change at high inelasticity and Eν.
- **Cannot settle.** The ≥60 total. Test 1 showed that w(E_avail) leaves band totals within 3.5% of the fold.
- **Cost.** One local script, a few minutes of CPU, 0 node-h. About an hour of work including the README.

## B. Momentum-dependent curvature bias against a rate excess (E_avail < 1 GeV)

- **Compute.** Apply a constant curvature offset to the simulation: (q/p)_reco → (q/p)_reco + ε. Recompute p∥ at fixed direction, as `../curvature_scale.py` does for the 3.6% scale, and reapply acceptance. Fit ε to the shape of low-E_avail negative tracks at reco 20–60 in the training playlists. Then predict, with no further freedom:
  - negative tracks at ≥60;
  - positive tracks in every band;
  - the good/poor split.
- **Discriminates.** A constant Δ(q/p) grows in effect with momentum, as the low-recoil excess does. It also moves the two signs in opposite directions. A rate excess at Eν ≈ p∥ (low recoil) moves both signs the same way. The positive sample is therefore the independent check. Full-sample positive Data/fold is 1.27, 1.18 and 1.28 at 40–60, 60–80 and ≥80; negative is 1.05, 1.67 and 1.19 (`../README.md`). The Gemini read raised this bias in its section A.3.2. The existing scale and width controls excluded only the uniform cases.
- **Cannot settle.** A physical calibration bias in data. That needs an independent momentum reference, such as MINOS range for stopping tracks, and is not in the saved tables.
- **Cost.** Local, about 10 minutes of CPU, 0 node-h. Two to three hours of work, because the acceptance reapplication must reuse the transverse cut exactly.

## C. Truth-Eν reweight (needs the AnaTuples, so NERSC)

- **Compute.** Add the MC true neutrino energy to `../measure.cpp`. The CVUniverse branch is expected to be `mc_incomingE`; verify it on the tree before submitting. Rerun the MC side only. Locally, fit a smooth w(Eν_true) on reco 20–40, as Test 1 did. Inside the published grid, renormalize w per true (p_T, p∥) cell so that the published anchor is unchanged. Apply w freely to true ≥60. Then predict the same held-out quantities as Test 1.
- **Approximation.** Renormalizing with selected events assumes the efficiency is flat in Eν within a cell. The exact version also needs Eν from the `Truth` tree for the generated denominators. That is a second, similar scan.
- **Cost.** NERSC is required. The earlier scan (`../batch.sh`) ran 11 one-core `shared` array tasks with a 45-minute limit each, covering both Data and MC, plus the 1L pilot. An MC-only rerun is at most that request. In NERSC charging that is under 0.1 CPU node-hours, an estimate from the requested resources, not a measured `sacct` value. Adding the `Truth`-tree pass for the exact denominators likely doubles it. Wall time is about an hour once queued.
- **Needs.** Joseph's NERSC certificate (24-hour `sshproxy`), authorization for the cluster act, and a rebuild of `measure` in the archived MAT environment (`../build.sh`).
- **Recommendation.** Run C only if B fails to describe the low-recoil and positive-sign pattern. If B succeeds, a truth reweight would be fitting a detector effect.

## Recommended order

Run A and B together first, in about half a day locally. Run C only on B's outcome.
