# Replaying the charge control

`measure.cpp` reads the production `MasterAnaDev` trees before the inclusive analysis charge requirement. The archived MAT release, CVUniverse, environment, upstream manifest paths and scan commands are given in `build.sh` and `run.sh`. The exact input lists, CVUniverse header and scanner binary are identified in `input-manifest-checksums.txt`. The cluster scan directory is `/pscratch/sd/j/josephrb/precharge-101kGc`. The 1L pilot used the same executable and cuts as the 11-playlist array.

The prefilter is total muon momentum ≥20 GeV/c. The reported measurement additionally requires reconstructed longitudinal momentum ≥20 GeV/c and transverse momentum in [0,4.5) GeV/c. The surviving cuts are the production fiducial z, hexagonal apothem, beam-frame muon angle, MINOS match and deadtime predicates. Only the sign predicate is removed. The MC uses the production CV weights. The ME flux reweighter uses the incoming neutrino PDG code. The MINOS efficiency correction uses horn mode, MINOS momentum and batch POT for both reconstructed signs. In-domain fiducial muon-neutrino CC events of either reconstructed sign receive the same true-cell conversion to the published cross section with the all-selected efficiency convention. All other origins retain their nominal weights. The antineutrino and neutrino labels in the origin tables refer to the interacting neutrino and current. The matched track's true particle need not be the primary lepton in either category.

The full-sample comparison uses the ratio of summed data and simulation POT. The training and validation calculations use the data-to-simulation POT ratio separately for each playlist. Consequently their partitioned predictions need not sum to the quoted full-sample prediction. Row indices 0 through 3 correspond to [20,40), [40,60), [60,80) and [80,infinity) GeV/c. The last two are diagnostic subdivisions of the published upper overflow. All finite q/p bins in the CSV include their left edge and exclude their right edge. `tune_weight` is the event count for data and the CV weight sum for MC. `fold` is the all-selected prediction. The two sum-of-squares columns propagate finite simulation statistics.

On a system with the 24 extracted event files, Python, NumPy, pandas and Matplotlib, run in this directory

```sh
export PRECHARGE_EVENTS=/path/to/extracted/event/files
python score.py
python threshold.py
python verify.py "$PRECHARGE_EVENTS"
python display.py
```

The `inputs/replay` files freeze the published-grid conversion, playlist exposures and archived negative counts. The `inputs/control` files hold the previous charge-selected control and its negative-only fit. Both variations change the composition in a given reconstructed bin while retaining its source's simulated sign distribution. They test specific transfers, and do not implement a physical flux variation or rerun track reconstruction. The threshold test changes only the sign assignment relative to data at fixed reconstructed momentum. All three comparisons use observed negative-sign counts for training. Positive-sign data never enter any fit.

`verify.py` independently recounts the extracted rows and CV weights with a scalar reader. `score.py` checks closure to the previously archived data, nominal weighted yield, all-selected fold and true-tail feed-in per playlist. It also checks the held-out negative-sign predictions against the earlier template fit. These checks share the input event files. The positive-sign sample was excluded by the archived cut.

The held-out playlists are independent of the fitted amplitudes. Both predictions share the nominal detector simulation, the published cross-section anchor and its all-selected conversion. Their positive-sign predictions transfer the simulated charge mixture. Correlated flux, detector, background and published-spectrum uncertainties were not propagated. A discrepancy in a positive-sign count is therefore a composition or response diagnostic, with no calibrated model significance.
