# Stage D Q2: is the current open-data ME-FHC MC new events or a reprocessing of ours? (2026-10-14)

**CITABLE FOR:**
- the 12-playlist size survey of our MC AnaTuples against the current public release;
- the event-key join and reco comparison on four MC files;
- the size comparison of the Data files for 1A, 1B and 1P;
- the answer to Q2;
- the correction this makes to OI-55's reach.

**NOT CITABLE FOR:**
- any effect on the 2D cross section. That is a separate triage, and it is open;
- a remedy or a re-download;
- any statement about files that were not compared (see §4).

| field | content |
|---|---|
| `Authority` | Joseph, 2026-10-14, answering Stage D Q2: "sure try this" ([`DECISION-20261014-joseph-stage-d-input-answers.md`](../../../../DECISION-20261014-joseph-stage-d-input-answers.md)) |
| `Who` | Measured by a Claude Opus 5.5 subagent of the paper-tighten lane (director). The director re-measured the 1A and 1P sizes and remote mtimes with `xrdfs stat`, recomputed the survey from the committed listings, and ran the Data size comparison |
| `Compute` | No Slurm job; 0 node-h. Perlmutter login-node reads, with the current release read over `root://fndca1.fnal.gov:1095` (the path is in `2d-unfolding/download_playlist.sh`); no full-file copy |
| `Evidence` | [`scripts/`](scripts/) (the probes) and [`outputs/`](outputs/) (raw listings, joins, diffs, checksums) |

## 1. Answer

**Q2: REPROCESSING, not new events. So the current release is not an independent MC bank.**

**New finding: our inputs mix two MINERvA processings.**
- **1A** is the older processing, for both MC and Data. We downloaded it on 2025-12-18, and the public files were
  replaced on 2026-01-06/11.
- **1B–1P** were downloaded on 2026-04-18/19, after the re-release. They match the current release.

## 2. Size survey (MC: `outputs/remote_ls_*`, `local_stat_*`; `scripts/survey_compare.py outputs`)

| MC playlists | files | same size as current | remote/local | our download | current public mtime |
|---|---:|---:|---|---|---|
| 1A | 41 | **0** | 1.2384–1.2492 | 2025-12-18 | 2026-01-06 |
| 1B–1P (11) | 448 | **448** | 1 | 2026-04-18/19 | 2026-01-06 … 2026-01-11 (1N: 2025-12-18) |

Two files in that group, 1P `run00112000` and 1D `run00111100`, have matching adler32 checksums (`outputs/adler.txt`).
The other 446 are matched by size only.

**Data** (director, `xrdfs ls -l` against `stat`, 2026-10-14):

| Data playlist | files | same size | mean remote/local |
|---|---:|---:|---|
| 1A | 253 | **0** | 1.052 |
| 1B | 47 | 47 | 1 |
| 1P | 40 | 40 | 1 |

The other nine Data playlists were not compared.

## 3. 1A MC: same events, different reconstruction (`outputs/join_*`, `meta_diff_*`, `reco_*`)

The key is `K = (mc_run, mc_subrun, mc_nthEvtInFile)`, read over every entry, with no duplicates.

**`Truth` tree:**
- `run00110000`: identical key sets (544,343). `mc_incomingE`, `mc_Q2`, `mc_w`, `mc_intType` and `mc_targetZ` are
  bit-identical, and so is the overlay gate.
- `run00110001`: all 544,499 of our keys are present, plus 29 new events, all in `mc_subrun` 112. The kinematics and
  gates are bit-identical, and row order is preserved.

**Reco tree `MasterAnaDev`, `run00110001`.** 186,535 keys are shared, 22 are only in ours and 35 only in the
current release. On shared keys the truth fields are identical, but the reconstruction is not:

| quantity | ours (older) | current |
|---|---:|---:|
| `muon_P` = −9999 | 54,685 | 0 |
| `MasterAnaDev_minos_trk_is_ok` true | 90,738 | 131,723 |
| `MasterAnaDev_minos_trk_quality` 1 / 2 | 69,860 / 20,878 | 100,802 / 30,921 |
| `muon_is_minos_match_track` | −1 in every event | branch removed; `truth_reco_isMinosMatchTrack` added |
| `muon_P` bit-identical, where both are real | 97.6 % | |

`run00110000` shows the same pattern. The current processing finds a MINOS-matched track in about 45% more MC
events.

**Why the files are larger** (`run00110001`, about +4.22 GB):
- about 81% is `mc_wgt_ppfx1_Total` and `mc_wgt_Flux_BeamFocus`. These go from 100 universes stored as doubles to
  1000 stored as integers ×10⁷. A spot check of 6 universes × 3 entries agrees to the 10⁻⁷ step;
- the reco tree gains 98 branches and loses 10;
- the `Truth` tree gains 53 branches and loses 8.

The Stage D REPORT's independent identity probe had already recorded 4,102 reco branches in 1A and 4,190 in 1E, 1M
and 1P (`../evidence/identity_probe_*.out`).

## 4. Not measured

- The 1A Data content: only sizes were compared.
- The other 39 1A MC files beyond those two.
- Reco variables beyond the four above.
- Nine Data playlists.
- The effect on the 2D result. A read-only impact triage (event-loop branch use, old 1A Data against new,
  per-playlist yields) was started on 2026-10-14. Its result will be recorded separately.

## 5. Corrections this makes

- **OI-55 ("valid older production, inputs COMPLETE").** Completeness stands. "Older production" holds for 1A
  only. The 1.243–1.244 ratios came from 1A files. 1B–1P are the current processing.
- **Stage D REPORT §4.6 and Q2** read OI-55 as covering all 489 MC files. Only the 41 1A files differ from the current
  release.
- **Drafts A and B** (`docs/publication/corrections-20261008/DRAFT-20261008-anatuple-preservation-requests.md`).
  Their statement that "a fresh download would not reproduce the analysis inputs" holds for 1A only. Re-measure
  before sending.
