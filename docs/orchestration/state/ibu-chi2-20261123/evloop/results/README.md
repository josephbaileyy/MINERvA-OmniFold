# ibuchi event-loop diagnostic: results (2026-11-24)

**By** the `ibu-chi-squared-issue` session (Claude Opus 5.5). The code, the declaration and the checks before running are in
[`../README.md`](../README.md). This directory holds what the run produced and how it was scored. Nothing here changes
a script on record.

**Reading: none of the tested changes accounts for the excess at reco p‖ 40–60 GeV/c (COL) or the deficit at reco
pT 0–0.07 GeV/c (ROW).** All controls passed, so this is a READ, not a STOP. It is a statement about these four changes
to our chain, not about MINERvA's code or calibration, a cause, or note wording.

## The run

- `ibuchi_evl` array 61885471: 12 of 12 tasks COMPLETED, none failed. Every task logged binary `10bf7fd9b6a4442d`.
  The longest was 1M at 5:02:26 and the shortest 1L at 0:11:16 ([`run_record.txt`](run_record.txt),
  [`watch_evl.log`](watch_evl.log)).
- `ibuchi_ana` job 61908135: COMPLETED in 0:10:31, peak RSS 13.4 GB ([`ana_61908135.log`](ana_61908135.log)).
  `ana.py` and `ana.sbatch` were re-hashed on the cluster just before submission and matched the recorded values.
- The products were fetched to the Mac by `cat` over ssh. Their local sha256 equals the cluster's (table below).
- The scorer `score_evloop.py` v2 (sha in `../README.md`) was run locally on them, unchanged: rc 0
  ([`score.out`](score.out); [`score.err`](score.err) holds two numpy divide warnings from empty cells, which the scorer
  masks).

## Controls

| control | value | threshold | |
|---|---|---|---|
| C-REPRO M (BASE response vs `signed_data.npz`) | 1.5e-14 | ≤ 1e-9 | pass |
| C-REPRO T (BASE truth vs `signed_data.npz`) | 3.4e-14 | ≤ 1e-9 | pass |
| C-REPRO B (vs `hBkgReco2D`) | 7.6e-15 | ≤ 1e-9 | pass |
| C-REPRO N (vs `hDataReco2D`) | 0.0 | ≤ 1e-9 | pass |
| counts n_sig 32,849,103 / n_bkg 658,227 | equal | equal | pass |
| C-KIN sig/bkg/data | 0 / 0 / 0 | declared | pass |
| C-ANG sig/bkg/data | 3.9e-12 / 1.6e-12 / 2.6e-12 | declared | pass |

So BASE rebuilt from the new event loop reproduces the inputs of the earlier tests exactly, and the dumped muon
branches reproduce the kinematics the canonical loop bins.

## Readings

`S_COL` is the shape-only statistic over the 40–60 column; `S_ROW` over the 0–0.07 row (definitions in the declaration).
D10 is χ²/ndf of the 10-iteration IBU against the published result.

| variant | S_COL | S_ROW | χ² of fold | D10 | data total | class |
|---|---|---|---|---|---|---|
| BASE | +0.1000 | −0.0638 | 425.1 | 0.961 | 4,091,707 | — |
| SEL (official MINOS cuts) | +0.1288 | −0.0761 | 717.8 | 3.461 | 3,116,992 | NONE / NONE |
| MAD (`muon_P` for `GetPmu`) | +0.1000 | −0.0638 | 425.1 | 0.961 | 4,091,707 | NONE / NONE |
| CURV at d̂ = −0.2 % | +0.0918 | −0.0624 | 395.2 | 0.967 | — | NONE / NONE |
| RANGE at d̂ = 0.0 % | +0.1000 | −0.0638 | 425.1 | 0.961 | — | NONE / NONE |
| ANG at (dx, dy) = (+0.75, −1.75) mrad | +0.0999 | −0.0589 | 413.7 | 1.076 | — | ROW NONE |

**What each line says.**
- **SEL.** The official MINOS cuts remove 24 % of the data and make both regions worse: COL from +0.100 to +0.129 and
  D10 from 0.96 to 3.46. Omitting them is not what separates us from the published result.
- **MAD.** Identical to BASE in every number. That is a fact about the files, not a bug:
  [`mad_vs_getpmu.out`](mad_vs_getpmu.out) ([`mad_vs_getpmu.sh`](mad_vs_getpmu.sh), run read-only on the merged output)
  shows `MasterAnaDev_muon_P` equal to `GetPmu()` within 5e-13 MeV on all 4,119,797 data, 658,227 background and
  20,498,013 signal-reco rows, with no sentinel on any reco row. In this processing the two momenta are the same number,
  so the choice between them cannot be the difference. The concern noted before the run, that MAD might drop real
  events with `muon_P` = −9999, does not arise here: it drops none. (The counts in `mad_vs_getpmu.out` were copied
  from the command's printed output.)
- **CURV.** The fitted data-only curvature offset is d̂ = −0.2 %. Its Δχ² ≤ 1 interval is that one grid point.
  At d̂, COL falls by 8 %, short of the declared 30 % for PARTIAL. Of the two descriptive readings the scorer prints,
  "within the fitted interval" gives 8 % (also short of 30 %). "Any d in range" gives 99 %, but only at d ≈ −2.7 %,
  where the fold χ² is 4,522 against 395 at d̂ ([`curv_scan.txt`](curv_scan.txt), made by
  [`curv_desc.py`](curv_desc.py), which reuses the scorer's own functions). A curvature scale that removes the column
  excess wrecks the rest of the fit by a factor of 11. COL moves linearly with d across the whole range while χ² is a
  parabola centred near zero, so the excess is not a MINOS curvature scale.
- **RANGE.** No effect: d̂ = 0, best reduction anywhere 0.3 %. Range-measured muons stop in MINOS, so few of them reach the 40–60 column.
- **ANG.** The best data-only beam-angle offset is under 2 mrad. It moves ROW from −0.064 to −0.059, about 8 %, and
  leaves COL unchanged. D10 gets slightly worse.

## What this leaves

From the chain in [`../../README.md`](../../README.md), these are now excluded as the source of the COL excess:
the prior route, overflow fakes, a uniform scale, resolution, beam angle, the event weights (descriptively), and now
the MINOS selection cuts, MasterAnaDev's momentum, and a MINOS curvature or range scale. The excess is a reco effect
confined to high-momentum, curvature-measured muons. A momentum-dependent (not uniform) curvature correction, or a
selection at high p that is not among the official MINOS cuts tested here, remain untested. The ROW deficit is still
open.
<!-- absence-ok: scoped to this lane's test chain; it says which changes these tests did not cover, not that no such study exists elsewhere -->

## Custody

- **Writes:** only under `/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/`. CPU only, nothing to CFS. The one
  `/dev/shm` file used to measure atimes was removed in the same command.
- **Reads:** as declared in `../README.md`, plus the merged output above for the MAD check.
- **Atimes, measured 2026-11-24 after `ibuchi_ana`:** all 2,307 AnaTuples in the 24 manifests now have atime at or after
  2026-11-23T21:49Z, the first task's start. The flux files under `minerva_large_files/MATFluxAndReweightFiles/flux/` and
  `MINERvA101/opt/lib/data/flux/` show atimes from 2026-11-23, inside the run window. These moves were
  expected and disclosed before the run.
- **Protected roots:** none of the roots the director listed as protected for the other lanes was opened.
- **Scheduler:** job state was read only with `sacct`, plus the one `scontrol show job` the director allowed (in
  `../README.md`). `squeue` was never run.
  <!-- absence-ok: a statement about this lane's own scheduler commands, from its scripts and command history -->

## Files

See [`SHA256SUMS`](SHA256SUMS). The two products fetched from the cluster:

| file | sha256 (local, equal to the cluster's) |
|---|---|
| `ana.json` | `11a18ea314b36f8f196c25d4c48cfc24b44ceb670a12e5d14a90e725a5fc4e73` |
| `ibuchi_products.npz` | `f66c0e1bf6285ea51425704f31eefd09994e0dd169e9d2a80a1d461eb107c49b` |
