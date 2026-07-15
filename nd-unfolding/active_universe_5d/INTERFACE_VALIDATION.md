# P2 — #16 active-universe event-loop interface validation

Validation record for the `MNV101_ACTIVE_UNIVERSE=BAND:IDX` selection-complete
event-loop mode. This is the gate before any P3 active-universe production family
is launched. A smoke pass is **not** evidence that any production endpoint exists.

- **Date:** 2026-07-15 (UTC 12:49–12:59)
- **Source commit gated with this record.** Prior HEAD `01660fa`.
- **Binary (rebuilt + installed from current source):**
  `MINERvA101/opt/bin/runEventLoopOmniFold`, md5 `e63c74961d699313ef155065fc790ff1`,
  383448 bytes, 9 `ACTIVE_UNIVERSE` strings. Rebuilt via
  `2d-unfolding/sbatch_build.sh` recipe (cmake `--target runEventLoopOmniFold`
  + `cmake --install .`). Downstream P3 tasks re-print this md5 per task.
- **Compute:** `gpu_interactive` salloc 55933725 (nid001017), CPU-only via
  `srun --gres=none`; env `setup_salloc_env.sh` with `HOME=/global/homes/j/josephrb`.
- **Smoke inputs:** `interface_smoke/1A_{MC,Data}_smoke.txt` (4 MC + 8 Data
  files derived from the canonical 1A manifests). Smoke ROOTs are disposable
  (`*.root` gitignored) and are **not** production inputs.
- **Readback validator:** `interface_smoke/p2_validate.py`.

## Interface source (owned by Agent A: `runEventLoopOmniFold.cpp`)
Adds a selection-complete promotion mode distinct from the CV-support-limited
`MNV101_DUMP_UNIVERSES` shadow-branch dump:
- `ParseActiveUniverse(BAND:IDX)` with strict format/index/range parsing.
- The requested `(band, idx)` reco+truth universe objects are promoted to the
  ordinary event-loop universe, so truth/reco selection, kinematics, weights,
  backgrounds, truth-authoritative IDs, bilateral dedupe, and native misses are
  all rebuilt in that universe.
- A per-event migration census vs CV (unique-key, counted once regardless of
  selection) is written as `TParameter<long>`
  `activeUniverse{Truth,Reco}{Entrants,Exits}`.
- Metadata: `TNamed activeUniverseBand`, `TParameter<int>`
  `activeUniverseIndex`, `hasActiveUniverse`, `activeUniverseIsLateral`.
- `MNV101_ACTIVE_UNIVERSE` is rejected with `MNV101_SKIP_SYST` (universe maps
  would not be built). CV-mode output is preserved bit-for-identical: the
  `if(!isSignalTruth) continue;` is only relocated past the reco computation so
  the census sees all events; the signal-reco tree still fills signal-truth rows
  only, and the CV comparison universe is null when inactive.
- `MNV101_DUMP_POINTCLOUD=1` now also dumps `part_reco_{E,pos,z}` on the
  background tree (mirrors data/signal), so P5 shifted-cloud processing has
  selection-complete background clouds.

## Gate results — ALL PASS
| Gate | Result |
|---|---|
| Unit/remediation tests (`tests/test_uq_remediation.py`) | 20/20 OK |
| Compile + install | OK (binary fingerprint above) |
| Invalid band/index fail-closed | `nocolon`→rc1, `NotARealBand:0`→rc1, `BeamAngleX:999`→rc1 |
| CV smoke (`hasActiveUniverse=0`, band `cv`) | PASS |
| CV census counters all zero (no comparison run) | PASS (0/0/0/0) |
| Endpoint `BeamAngleX:0` metadata (band/idx/lateral) | PASS (band=BeamAngleX idx=0 isLateral=1) |
| Endpoint selection migration vs CV (lateral) | reco entrants=21 exits=21, truth 0/0 (reco-level beam shift — expected) |
| Truth-authoritative completeness signal_reco/truth_denom | 1.000000 (CV and endpoint) |
| Native misses present | nTruthOnlyMisses=66989 (endpoint), hasTruthOnlyMisses=1 |
| Point-cloud branches complete (signal `part_gen_*`+`part_reco_*`; bkg+data `part_reco_*`) | PASS all 4 trees, clouds 99.7–99.9% populated |
| Standard vs FPS distinct behaviour | FPS truth_denom 399015 vs standard 263111 (×1.52; muon truth cuts dropped) |

## Scope note
This validates the interface only. P3S standard production
(`MNV101_ACTIVE_UNIVERSE=BAND:IDX` + `MNV101_DUMP_POINTCLOUD=1`, no
full-phase-space) writes to `active_universe_5d/standard/`; P3F FPS
(Agent C) adds `MNV101_FULL_PHASE_SPACE=1` and writes to
`active_universe_5d/fps/`. Launcher: `sbatch_evloop_array_5d_active_laterals.sh`
(committed with P3 per the campaign commit gate).
