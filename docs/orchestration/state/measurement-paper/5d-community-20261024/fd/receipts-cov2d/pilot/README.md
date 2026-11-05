# COV2D: the pilot PASSes ((2b) and section 9.12 reproduce part B; no REPRICE class)

**By** the `cov2d` session, 2026-11-05. Binding 2 rulings 2.2 and 2.3. The director gave GO for each connect after
checking its sha256: `connect-pilot.sh` (`4beedd40…`) and `connect-pilot-readout.sh` (`714781b5…`). The director read
`pilot_readout.json` and accepted it before this commit.

**MEASURES:** the pilot's controls (2b) and section 9.12, its walls against REPRICE, and the DVS read, at M.
**CANNOT AUTHORIZE:** any bulk job. Each bulk connect's sha goes to the director first.

`pilot_readout.json` is the record `cov2d_jobs.order` reads from origin/main (`PILOT_RECORD`). It is byte for byte the
readout's file, sha256 `b59ffa2d7363b7de1c702d037868d9794491e9433907cafe743784133b6bf99d`, the digest taken on the
node and logged in `connect-readout.log.txt`. With `cov2d_jobs.py` at M, `order("pseudo", "AR23", …)` returns `[]` on
this record and G18's. Every unfold is still refused until AR23's pseudo-data PASS.

## The submission (14:44:04Z)

- **The connect:** DIGEST_MATCH, then launched on login02 (`connect-pilot.log.txt`).
- **The deploy:** `/pscratch/sd/j/josephrb/cov2d-deploy-cb31611c`, at **M = `cb31611ca8b96ed2d1eeb809fda7236e56645863`**.
  Porcelain was plain 0 and `--ignored` 0, before and after.
- **origin/main** was at `f7a63b8e`. Its G18 record has sha256 `230f6918…`.
- **gate** (`logs/gate-pilot-*.gate.json`): spent 2.41 node-h (pseudo_G18), held 0, want 1.68, total 4.09 of 165.8. PASS.
- **order:** `blocked_by` was empty.
- **submissions.log:** `… job=pilot id=60857636 limit=01:41:00`.
- **scontrol:** TimeLimit 01:41:00, Account m3246, QOS regular_1. The QOS note is in `../pseudo/G18/README.md`.

## The job

| | |
|---|---|
| sacct | `60857636 cov2d-pilot COMPLETED 0:0`, Elapsed 00:45:02 (2,702 s), 1 node: **0.75 node-h** of the 1.68 reserved |
| window | 14:53:20Z to 15:38:22Z, nid007037; the runs 14:54:49Z to 15:38:20Z |
| check (`logs/check-pilot-60857636.json`) | 8 runs; the staged CV and lateral, `$UNI`'s stat, the MC and flux-universe files, (2a)'s kept file `7eb39088` and G18's two data files, each at its record; `problems: []` |
| runs | all 8 srun steps COMPLETED 0:0; `walls.pilot.*.tsv` rc 0 for each; `SHA256SUMS.pilot.*` holds all 8 digests |
| deploy after | porcelain plain 0, `--ignored` 0 |

## The readout (15:45:10Z to 15:45:33Z, login02, 0 node-h)

**Setup:** root_6_28 + the pinned MAT environment, with run_check_mat_setup reporting 6 scripts and 0 mismatches. The
readout ran from the deploy, so `"M"` is the deploy's HEAD. Part B's references were copied through O_NOATIME at their
pins. The output was `COV2D-PILOT PASS reprice=[] invalid=0`, rc 0. The deploy was still 0/0 afterwards.

**The controls.** The rule is `re2_k1`'s: relative difference ≤ 1e-8 on E_R's 205 cells, with the same cell set.
Bitwise equality is reported but does not decide.

| control | pilot run vs part B | max_rel | median_rel | same cells | bitwise | |
|---|---|---:|---:|---|---|---|
| (2b) | P2b_ER vs ER | 4.55e-15 | 1.11e-15 | yes | no | PASS |
| 9.12 lateral | P912_L_BeamAngleX_0 vs S3_BeamAngleX0 | 1.04e-11 | 3.73e-13 | yes | no | PASS |
| 9.12 universe | P912_U_MaRES_0 vs U_MaRES_0 | 2.88e-12 | 5.93e-14 | yes | no | PASS |

**REPRICE.** The pilot's run-only wall per run is compared with part B's like for like, at 1.25×. **No class reprices.**

| class | pilot (s) | part B (s) | ratio |
|---|---:|---:|---:|
| central | 585.0 | 610.0 | 0.959 |
| toy | 585.0 | 610.0 | 0.959 |
| lateral | 930.0 | 1,174.8 | 0.792 |
| replica | 569.0 | 691.7 | 0.823 |
| universe (128 CPUs) | 751.0 | 864.9 | 0.868 |

U_G18_Flux_0 (685 s) ran at 64 CPUs. It is a route test, not priced.

**DVS** (descriptive, with the record's cache note): 4 GiB read from each, with equal prefixes.

| source | MB/s |
|---|---:|
| CFS original | 588.4 |
| staged copy | 919.7 (may be cached) |

The verdict is PASS, with `reprice_classes`, `invalid` and `stop` all empty. **This is not the second STOP**; the STOP
count stays at one.

## Files

- `pilot_readout.json`: the record, verbatim.
- `connect-pilot.sh`, `connect-pilot.log.txt`: the submission connect and its log.
- `connect-pilot-readout.sh`, `connect-readout.log.txt`: the readout connect and its log, with the rootmap warnings
  ROOT prints under MAT.
- `walls.pilot.{1,2,3}.tsv`, `SHA256SUMS.pilot.{1,2,3}`, `submissions.log.txt`: the job namespace's records.
- `logs/`: the job log, check, dvs-rate, the MAT record, the gate files and the eight per-run logs.
- `remote_sha256.txt`: digests taken on the node. Every file here equals its digest.
- `removal.log.txt`: both connects' `/dev/shm` files were removed, rc 0 each, and `/dev/shm` was left empty.
- `.log` and `.out` files carry a `.txt` suffix, because those patterns are gitignored. Their bytes are unchanged.
