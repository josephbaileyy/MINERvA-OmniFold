# AUTHORIZATION 2026-10-15 — 2D closeout: binding addendum to the Stage C production grant

**Issued by** the paper-tighten lane, as director. This is step 2 of the two-step activation in
[`AUTHORIZATION-20261015-2d-closeout-stageC-production.md`](AUTHORIZATION-20261015-2d-closeout-stageC-production.md)
§1. With this record on `origin/main`, the 2d closer may deploy the package and submit G0.

**CITABLE FOR:**
- the production package, manifest and digests that every Stage C production job runs under;
- the enforced worst-case charge per job and in total;
- the director's explicit rulings on the six items the package DESIGN §3.6 asks the binding to accept;
- the operating conditions in §4.

**NOT CITABLE FOR:**
- anything the production grant excludes: G2 wording, a G2 repair, Stage D/E work, adoption, claims, the KI-85 lift,
  publication changes, or a playlist-consistency term;
- any result. No job had run when this record was written; the namespace
  `/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015/` did not exist (`ls`, 2026-10-15);
- a higher ceiling. It stays at 100.0 node-h, and committed grant ceilings under the delegation stay at 132.0 of 700.

## 1. Binding

| item | value |
|---|---|
| package commit | `4139548b3920c1c7944e700c08649493167bc45d` on `closeout/stagec-production-20261015` (PR #131). Its base is `8fbcae96`, the grant's merge. The director merged it as `e96c20e8`; the merge tree equals the package commit's (`git diff 4139548b e96c20e8` is empty) |
| manifest | `docs/orchestration/state/2d-closeout/stageC/production/manifest.json`, sha256 `3962cb4d57c2986e7182b56fbdc45f3a876f3a9c24331b31e1dd82a6247e0b3e` |
| job table | `jobs.tsv`, sha256 `c4f1b7082fac3635be78622cb9b9a5f71103789337bbc29e7dd29684e9b4d3a4`, pinned as `JOBS_SHA` in `sbatch_prod.sh` |
| gate | `launch.py`, sha256 `ea9f06d7cfebe34e6792b800902b8e55f5d9c1eba5b4309af1a71dc4223f40c6` (`CEILING = 100.0`, `PREFIX = "2dc_P_"`) |
| dispatcher | `sbatch_prod.sh`, sha256 `1dc95ad32b442e54713b58d08724f9112fa6b4183caa8c9c306f9e94c21576d5` |
| analysis | `analyze_prod.py` `f9e0d8f271f28bee1ef264de62cf7b924d18d4086e8fbe896abff4adb79320a4`; `s5_rollup.py` `6c437004fb439201c173a2857fb95bda2cb3045285ba61c1bef8f8c215b39d15` |
| drivers | production driver `74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56` (grant §1); `driver_p1.py` `3056e625a22f2ee79621e515aa5a76a4685662ac6fc10ee7e832680dde087578`, from `state/2d-closeout/stageC/pilot/p1/` on `main` (ruling 1 below) |
| helper | `omnifold.py` `e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a` |

## 2. Enforced worst-case charge

Charge per job = billing × cap ÷ 256, QOS `shared`, billing = CPUs, memory 1,905 MB per CPU.

| family | jobs | cap | CPUs | per job (node-h) | family total |
|---|---:|---|---:|---:|---:|
| CV unfolds: C0 (2), S4(ii) CV (4), S1 (300), S2 (100), S4(i) (80) | 486 | 00:51:00 | 64 | 0.2125 | 103.2750 |
| S4(ii) universe unfolds | 35 | 00:30:00 | 128 | 0.2500 | 8.7500 |
| S3 laterals | 10 | 01:10:00 | 128 | 0.58333 | 5.8333 |
| **all 531 jobs** | | | | | **117.8583** |

This exceeds the 100.0 ceiling. That is acceptable, because the gate counts terminal charges at their measured
values and only queued and running jobs at their caps. Batches are therefore admitted as charges settle. The
expected charge is 44.9 node-h at the pilot's mean units and 57.0 at its p84/max units. Only if every job ran to
its cap would the gate first refuse, at S2b.

## 3. Director's review, and rulings on DESIGN §3.6

**What the director re-measured** at `4139548b`, in a detached worktree:
- **Digests.** All six digests the closer reported, plus `driver_p1.py` on `main` (`3056e625…`).
- **`jobs.tsv`.**
  - It has 531 unique names: C0 2, S3 10, S4(ii) 39, S1 300, S2 100, S4(i) 80.
  - Every row is QOS `shared`, with billing equal to CPUs, memory 1,905 MB per CPU, and a cap under 12 h.
  - Every `enforced_nh` recomputes from billing × time ÷ 256, to 6e-5.
  - The total is 117.8583, and the batch totals match DESIGN §6.
  - The S1 and S2 bootstrap seeds are 1–300 and 1–100.
  - S4(i) covers seeds {45, 48, 51, 54} × bootstrap seeds 1–20.
  - S4(ii) covers seeds {42, 45, 48, 51, 54}.
- **Seed triplets.** The driver pins (step 1, step 2, regressor) = (s, s+1, s+2) at
  `unfold_2d_omnifold_unbinned.py:2080-2083` (`4139548b`). So the five triplets share no seed.
- **`launch.py simulate`** prints:

  | mode | result |
  |---|---|
  | `mean` | 44.9004 |
  | `p84` | 57.0448 |
  | `cap` | first refusal at S2b (100.8583) |

- **`evidence/smoke/test_launch.py`**, run locally: 15 PASS, 0 other lines, exit 0.
- **The gate code** (`launch.py` `ledger()`, `gate()`, `owed()`, `preconditions()`, `deadline_arg()`):
  - it refuses on an unreadable `sacct` or `squeue`;
  - it counts in-flight jobs at the larger of the table billing and Slurm's billing;
  - it skips never-started `DEADLINE` rows as attempts;
  - it allows a retry only after exactly one TIMEOUT;
  - it submits with `--no-requeue`;
  - it refuses everything after G0 unless `results/c0.json` says PASS, computed from `$NS/out`.
- **The dispatcher** (`sbatch_prod.sh`) re-checks:
  - `jobs.tsv`, and that the job's name is one row of it;
  - the granted QOS, CPUs, billing and TimeLimit;
  - the driver, helper, MC and flux digests;
  - the input digest, or the universe omnifile's preflight stat.

  It refuses on a non-empty output directory.
- **The independent reviews** are recorded in DESIGN §13:
  - first review at `647a78ca`: APPROVE WITH CHANGES, 1 MATERIAL and 12 MINOR, all disposed;
  - re-review at `51615e0d`: APPROVE, 0 MATERIAL and 2 MINOR, fixed at `4139548b`.

  The verifiers' own reports are not committed separately; DESIGN §13 is the record.

**Rulings on the six items DESIGN §3.6 asks the binding to accept:**

1. **`driver_p1.py` for 481 of 531 jobs: ACCEPTED.**
   - These are C0_unit, S1, S2 and S4(i). The production driver offers no three-stream, bkg-only or b ≡ 1 mode
     (`:1448`). The grant names the b ≡ 1 control as the first job, and only `driver_p1.py` can run it.
   - `driver_p1.py` is the production driver plus `p1/patch.diff`. With the new options off it is bitwise the
     production path (pilot test C1), and its b ≡ 1 control passed twice in the pilot.
   - In production, `2dc_P_C0_unit` must reproduce XR-L0 at 1e-8 before anything else runs.
   - It is deployed as a pinned copy, and no driver on `main` is edited.
   - **Carried to Stage F:** `driver_p1.py` reaches `2d-unfolding/` on `main` through its own reviewed PR before any
     production product is adopted.
2. **The run-count departures: ACCEPTED.**
   - S3 runs 10 laterals (+2). The two pilot laterals become reproduction checks.
   - S4(i) has 80 jobs (−20), because S1's replicas 1–20 are the seed-42 column. The seed and bootstrap-seed
     arguments are identical, so this is the same run, not a substitute.
   - S4(ii) gets +4 CV references.
   - There is one production-driver CV control.
   - The net count is 531, against 544 for Stage B §7's 543 runs plus the control. All of it is inside the grant's price.
3. **The §3.5 choices: ACCEPTED as frozen.**
   - Seeds 42/45/48/51/54.
   - The seven S4(ii) universes. `NormDISCC:0` is the null and the path control. At each seed it must reproduce that
     seed's CV at 1e-8, so it also checks that the universe file's derived read equals the CV file's.
   - Bootstrap seeds 1–300 and 1–100.
   - The R4 closure, read per cell from each lateral's `hOFCompleteness2D` at 1e-9, with the guard against the
     driver's c ≡ 1 fallback.

   They were fixed before any production job and are not tuned to any result.
4. **The gate-refusal reading: ACCEPTED.** The grant's gate row (§3) requires batching because queued caps count in
   full. A `launch.py gate` pre-check that does not admit a batch while `2dc_P_` jobs are in flight is that batching
   rule working, so the executor waits and re-checks. **A stop** is any of:
   - a pre-check refusal with nothing in flight;
   - any refusal by `submit`;
   - any refusal for a reason other than the ceiling.
5. **Storage: amended.** The S5 ROOT rollup `uq_production_covariance.root` **is copied to CFS** with the other
   products and listed in `SHA256SUMS.pscratch`. The grant's "xsec.root/JSON/NPZ only" was there to keep the inputs
   off CFS. This rollup is a product of order 14 MB (VL175's is 14,112,829 B), and leaving it on `pscratch` would
   expose it to the purge. The pilot's 74 outputs total 256 MB, so all production products should be about 2 GB.
6. **Input checks: ACCEPTED.**
   - The 171 GB universe omnifile is hashed once on a DTN by `preflight_uomni.sh`, and each job checks its size,
     mtime and inode against that record, as in the pilot.
   - The 24 per-playlist flux and POT files are checked against VL175's `build.json`, which the manifest pins at
     `dcc1331e…`.

## 4. Operating conditions

- **Deploy** as DESIGN §10.1 says:
  - `git archive 4139548b3920c1c7944e700c08649493167bc45d` into the new namespace;
  - `driver_p1.py` copied from `stageC/pilot/p1/`;
  - every file checked against `manifest.json`;
  - `.deployed_commit` recorded.

  The period-unfold test's `pu_*` jobs may be in the queue. They do not interact with this gate, because of the
  prefix.
- **Check that `--deadline` was applied.** `sbatch --test-only` tested the syntax only. After the first submission
  of G0, the executor reads `scontrol show job <id>` and checks that its `Deadline=` field is
  `2026-10-20T23:00:00`, the window's start in the login node's zone. If the field is absent or different, cancel
  what is pending, submit nothing more before the window, and report.
- **Maintenance.** If any production job is RUNNING at a time when its start plus TimeLimit would pass 2026-10-21
  06:00 UTC, that is a stop (DESIGN §6). Report it; do not cancel it unless the director says so.
- **Purge exposure.** These inputs are on `pscratch`, not CFS:
  - the universe omnifile;
  - the MC and flux files;
  - `E_U`;
  - the July and May sweeps;
  - the VL175 build;
  - the pilot outputs.

  A purged or changed input fails its check, which is a stop. Recovery from the CFS Stage C copy needs a director
  ruling. It is not a retry.
- **Window.** Production must end by 2026-11-15. Running past that date needs a director record before it, not a
  late note.
- **Report.** `state/2d-closeout/stageC/production/REPORT.md`, as grant §3 says, including:
  - the `Deadline=` check;
  - every `DEADLINE` row and its `redo`;
  - the CFS copy's `sha256sum -c` result.

## 5. Committed ceilings

This record changes no ceiling:
- production stays at 100.0 node-h;
- committed grant ceilings under the delegation stay at **132.0 of 700**.
