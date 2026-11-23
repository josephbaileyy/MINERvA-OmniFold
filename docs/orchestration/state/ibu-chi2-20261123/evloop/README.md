# ibuchi event-loop diagnostic: the code on record before it runs (2026-11-23)

**By** the `ibu-chi-squared-issue` session (Claude Opus 5.5). This follows the test chain in [`../README.md`](../README.md).
Joseph authorized running these jobs. The director's GO named three conditions: this record, one agy read, and no
`squeue` in any script. This directory satisfies them before the first submission. The results will follow in a
separate records PR.

**What it tests** ([`DECLARATION.txt`](DECLARATION.txt), sha256 `f3a8064f7f073381916d6fdba862f2a0b7ef5775b0cb341d6b4be623265796ec`,
written before running). It asks which tested change to our chain makes the published result fit our reco data at
reco p‖ 40–60 GeV/c and reco pT 0–0.07 GeV/c. The changes are:
- SEL: the official MINOS cuts we omit;
- MAD: MasterAnaDev's `muon_P` in place of MAT's `GetPmu`;
- CURV/RANGE: a data-only MINOS momentum offset;
- ANG: a data-only thetaX/Y offset.

It is not a statement about MINERvA's code or calibration, a cause, or note wording.

## The code

| file | sha256 | role |
|---|---|---|
| `runEventLoopOmniFold.cpp` | `a417a212668574ac7fd038b8bdce7c7ee598a3b365279352fd5af043fe9a2768` | the event loop as built for this run |
| `runEventLoopOmniFold.cpp.diff` | (see SHA256SUMS) | its diff against the canonical file at `83dd3bd8f` |
| `build.sh` | `4a6362b3f7f4774c710b7d9748fa79cb35b4e2514c50587b0f375ac5dcbd1117` | login-node build into the run root |
| `evl.sbatch` | `df799fef2a6dc88abd72640033688b4625139f9b3904437d38309afc9be32ce0` | the `ibuchi_evl` array, 12 playlists |
| `ana.sbatch` | `90e1dbfc6f32135a458bc982e05949d669db7c4e55da1f0272c3830a273a3b19` | `ibuchi_ana`: hadd, then `ana.py` |
| `ana.py` | `7f9417dc3410ce039dba66c17c7a3a1554517205b5bbcd3bb176d40b5e803048` | binned products per variant, plus C-KIN and C-ANG |
| `smoke.sh` | `8918dd15e7dcd7c5ee947d20f29ed11063884a46b95a899ad8b49e429d5d2760` | login-node smoke on 1A (2 MC + 8 data files), functional checks |
| `staged.sha256` | | everything staged on Perlmutter (5 uploads, 24 manifests) |

The canonical diff is `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp`, sha256 `57792e42…`. The receipt
copy here adds one opt-in flag, `MNV101_DUMP_MUONQ`. It books 14 `mu_*` branches on `mc_signal_reco`, `mc_background`
and `data`: `GetPmu`, `GetPmuMinos`, the MINOS track p and its range and curvature values, used_range/used_curvature,
trk_quality, qp, eqp_qp, MasterAnaDev `muon_P`, thetaX/Y and theta. The branches hold -9999 on rows without a reco muon.
With the flag unset, no branch is booked and no value is read.

The canonical file is not changed in the repo. The pre-commit hook reports `BINDINGS BROKEN` when it changes, because
receipts pin its bytes. So the modified source lives only here.

**Build.** It ran on login02 into `/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/` from a copy of the cluster source
tree. That copy matched canonical `57792e42` before the receipt copy replaced it. The build links against the installed
MAT, MAT-MINERvA and UnfoldUtils, read-only.
- Binary sha256: `10bf7fd9b6a4442d4955b51a2d336874d2f865cb5be17b2dc8ca0aa377abb8fd`.
- The build log had no warning or error lines.
- `MAT/PlotUtils/BaseUniverse.h:66` declares `GetAnaToolName()` public, so the receipt copy may call it from outside
  the class.

**Fix after the smoke, before `ibuchi_ana` ran.** The smoke showed that `mc_signal_reco` keeps `sim_pass` set on truth-only miss rows, whose `mu_*` fields are -9999. In the MAD variant, -9999 MeV at a -9999 rad angle could land inside the grid, so `ana.py` now requires `mu_mad_p > 0` on all three trees for MAD. BASE and SEL were already safe, because `sim` is itself -9999 on those rows and `mu_trk_quality` is -9999. The agy read did not catch this. The fix was committed before `ibuchi_ana` was submitted. The event-loop array (job 61885471) does not run `ana.py`.

**agy confirm on that diff** (director's condition; [`agy-confirm/`](agy-confirm/); Gemini 3.8 Flash (High), sandboxed, hashed copies unchanged afterwards): **VERDICT: GO**.
- The guard is correct and complete.
- No other variant, tree or control admits a sentinel: BASE needs `sim >= 0`; SEL's quality cut fails on -9999; the scans are data-only; the controls require `mu_p_total > 0`.
- The diff changes only that line.

One point is noted against agy's Q1 claim that "no valid reco muon is excluded". In the older 1A processing, `MasterAnaDev_muon_P` is -9999 on some real reco events (`stageD-inputs/q2-opendata-20261014/REPORT.md` §3). The MAD variant therefore drops those rows, in data and in MC. The MAD readout reports MAD's total counts beside BASE's, so the size of that selection change is visible.

**Local scorer** `score_evloop.py` (sha256 `72d3f89cd95e5d2964a0058bd2652089474498c8be1e2f6f3757cb3573d87c5d`). It was committed before any product existed. It implements C-REPRO, the C-KIN and C-ANG thresholds, and the declared readings. **One interpretation is fixed here, before any number was read.** The declaration's CURV/RANGE "PARTIAL if reduction >= 30 % within \|d\| <= 3 %" is evaluated at the fitted d̂, not at the best d in the range, so that no point is picked after the fact. The best reduction over the whole range is printed as a descriptive number, read by no rule.

**agy read of the scorer** (the director's request; [`agy-score/`](agy-score/); Gemini 3.8 Flash (High), sandboxed, hashed copies unchanged afterwards), against `DECLARATION.txt`: **VERDICT: GO**.
- Every control and reading is implemented as declared.
- The weights and cell sets are fixed from BASE.
- No path picks a variant, a d, a (dx, dy), a region or a weight after seeing data, beyond the declared fits.
- On the PARTIAL clause it names two other readings the text allows: "any d in range" and "within the fitted interval". It judges the fitted-d̂ choice the more conservative one.

**Scorer v2** (`72d3f89cd95e5d2964a0058bd2652089474498c8be1e2f6f3757cb3573d87c5d`, replacing v1 `a1a4a0461bbc28f565fed06f9ff4ed141ef0d7ce4057ac9856f76b1bf2e730a1`), at the director's request, before any product exists. It adds, DESCRIPTIVE ONLY, the two other readings of the PARTIAL clause, each with a "would meet 30 %" flag:
- the best reduction of \|S_COL\| over the whole d range;
- the best reduction over the d values inside the fitted Δχ² ≤ 1 interval.

The declared classification at d̂ is unchanged. The agy confirm on the diff ([`agy-score2/`](agy-score2/)) gives **VERDICT: GO**: no change to the classification, the controls or any existing output value, and the two numbers are computed correctly.

## The checks before running

- **agy read** (Gemini 3.8 Flash (High), sandboxed, on hashed copies; [`agy-read/`](agy-read/)): **VERDICT: GO**, no
  fixes. The copies were byte-identical afterwards (`agy-read/files.sha256`). It found:
  - with the flag unset, the code path is the production path, since every added call is guarded;
  - no write outside the run root, and nothing to CFS;
  - no `squeue`;
  - `set -eo pipefail` in each shell script;
  - `ana.py` matches the declaration.

  Its quotes were spot-checked against the files.
- **`squeue`:** `grep -c squeue` over the four scripts gives 0.

## Custody

- **Writes:** only under `/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/`. CPU only, nothing to CFS.
- **Reads:**
  - the 24 playlist manifests (identical to `origin/main`);
  - 2,307 AnaTuples under `/pscratch/sd/j/josephrb/minerva/minerva_large_files/{Data,MC/StandardMC}/Playlist1?/`;
  - `MINERvA-OmniFold/setup_salloc_env.sh` and `MINERvA101/opt`, including the flux and reweight files under
    `minerva_large_files/MATFluxAndReweightFiles/flux`, which MAT's FluxReweighter reads.
- **Atimes:** these reads will move the AnaTuple and flux-file atimes.
- **Protected roots:** none of the roots the director listed as protected for the other lanes is opened.
