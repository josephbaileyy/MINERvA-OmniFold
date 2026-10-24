# RE-2 J0 report: the pilot's controls, its measured units, and the part-B request (2026-10-24, re-1 lane)

**Status.** Both J0 jobs ran once and COMPLETED: all 34 runs, 30 of 30 checks and 21 of 21 refinement-health rows
PASS. The production rule (RE2-DECLARATION.md §5.3, fixed before J0) returns **WITHIN GRANT: core + J7**. J0
was bound by `RE2-BINDING-J0.md` and ran from a clean deploy at `668e9b44e41e6eae7b2d0727b0a924bc311d063d`.

**MEASURES:**
- J0's controls against Stage C, the period unfolds, the July sweep, `driver_p1.py` and RE-1's D2;
- the refined 2D unit times;
- J0's charge.

**CANNOT AUTHORIZE:**
- a production job: the director binds part B (RE2-DECLARATION.md §5.4);
- a claim: no product here is a result, and `D_cv` is a control product compared with D2 only.

The records are in [`run/j0_readout/`](run/j0_readout/), copied from
`/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/j0/`. The two files below are re-hashed from the copies here, and
they match the hashes printed by `re2_j0_readout.sh` on the cluster:

| record | sha256 |
|---|---|
| `k1.json` (`re2_k1.py`) | `1f066704b5f2457f4df4b214a121dda7fa2c8d2c535226af86cc62678b18ff4b` |
| `units.json` (`re2_units.py`) | `2e3a633125c4eb869a3895739aa03d569fbff4e07f9c3a2439e4b2c4b992aa81` |
| `steps.psv` (`sacct`) | `77e6063b3d702cadaef316bb6797c2535d7942534e585bfad213ec7ddb34b733` |
| `j0_ledger.tsv` (`re2_ledger.sh`) | `e68cd0b16505f888812c791866e26e8a294bcd37b8b31bf93e9c4e8b698d34bd` |
| `SHA256SUMS.J0a` (12 outputs) | `28ff13406b5323f66885a64da3d38d6efb437e1c1d5609e79f0f0eb30004228e` |
| `SHA256SUMS.J0b` (22 outputs) | `7cb99a0ab2610dec5c06b925c67952fb037af83ae6fccbd6a0c8a5e927ea9205` |

## 1. The jobs and the ledger

| job | Slurm id | QOS | state | start (local) | elapsed | limit | billing | charge, node-h |
|---|---|---|---|---|---|---|---|---|
| J0a `re2-j0a` | 60173037 | regular_1 | COMPLETED, rc=0 | 2026-10-23T16:43:21 | 4:02:19 (14,539 s) | 5:55 | 256 | 4.0386 |
| J0b `re2-j0b` | 60173038 | regular_1 | COMPLETED, rc=0 | 2026-10-23T16:43:21 | 1:26:13 (5,173 s) | 4:15 | 256 | 1.4369 |
| **J0** | | | | | | | | **5.4755** |

**The charge against the bounds:**
- the bound cap is ≤ 10.5 node-h;
- the declared projection was 8.1 node-h, worst case 10.2 (RE2-DECLARATION.md §4).

**Wall time against the 1.25× stop rule:**
- J0a ran 0.86× of its 4.72 h projection and J0b 0.42× of its 3.40 h projection.
- Neither job was past 1.25× at any check.

**Submission and provenance:**
- One submission each (`submissions.log`), `--no-requeue`.
- All 34 run logs' OI-136 inventory names one checkout root, the deploy, and nothing else.

**Booking:**
- J0's 5.4755 node-h is booked against the 90 node-h RE-2 grant, which sits under the 700 node-h ceiling.
- The ledger rows are in `j0_ledger.tsv`.

## 2. Deviations

**D1. J0a's preflight took 5,057 s; the declaration projected about 900 s (RE2-DECLARATION.md:174).**
- **The timeline:**
  - The job started at 2026-10-23T23:43:21Z, and its runs started at "[re2] start 2026-10-24T01:07:38Z".
  - Almost all of the gap was the `sha256sum` of the 53.8 GB lateral BAX0 input on CFS.
- **The read rate,** measured on the node from `/proc/<pid>/io`:
  - `rchar` went from 50,555,360,208 to 50,899,751,888 bytes in 60 s at about 01:02Z, which is 5.7 MB/s;
  - the average over the hash was about 12 MB/s.
- **The digest:** the hash matched the declared `38b9fc30…`. `re2_check` exits 4 on a mismatch, and the job went
  on to its runs.
- **The decision:** the lane reported the overrun to the director while it ran. The director ruled: continue, re-project after the
  first runs, and stop if the projection or the elapsed time passes 5:55. The re-projection at 2:36 elapsed was
  about 4.2 h, and J0a ended at 4:02:19.
- **The effect:** none on the results. The charge rose by about 1.2 node-h of idle node time, already included in
  §1.

**D2. Four diagnostic `srun --overlap` steps**, all from the lane while it diagnosed D1:
- J0a steps .0 `ps`, .1 `bash` and .2 `bash`, and J0b step .22 `bash`;
- 1 CPU each, at most 60 s;
- they read `ps`, `/proc/<pid>/io` and `stat`, and changed nothing;
- they are in `steps.psv`, and `re2_units.py` skips them because their names are not labels in `j0_runs.tsv`.

## 3. Controls (`k1.json`)

**How to read the table:**
- Equality checks (`le`) pass at max rel. diff. ≤ 1e-8 on E_U's 205 cells, with the same reported cell set.
  Bitwise equality is reported but does not decide, because configuration (a) is LightGBM's non-deterministic mode.
- Power checks (`differs`) pass above 1e-6.
- All 34 outputs match the jobs' `SHA256SUMS` (`sums.mismatched` is empty, `n_listed` = 34).
- Every reference given with a sha256 re-hashed to it.

| check | kind | test | reference | hist | max rel. diff. | bitwise | verdict |
|---|---|---|---|---|---|---|---|
| K1-C1 | le | `C_cv` | `…/out/2dc_P_C0_cv/xsec.root` | hXSec2D | 1.45e-11 | False | PASS |
| K1-C2 | le | `C_cv` | `…/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` | hXSec2D | 1.43e-11 | False | PASS |
| K1-C3 | le | `C_unit` | `…/out/2dc_P_C0_unit/xsec.root` | hXSec2D | 5.74e-13 | False | PASS |
| K1-B1 | le | `B_S1_001` | `…/out/2dc_P_S1_001/xsec.root` | hXSec2D | 4.44e-13 | False | PASS |
| K1-B2 | le | `B_S2_001` | `…/out/2dc_P_S2_001/xsec.root` | hXSec2D | 3.86e-12 | False | PASS |
| K1-U1 | le | `U_MaCCQE0` | `…/out/2dc_P_S4U_MaCCQE0_s42/xsec.root` | hXSec2D | 5.85e-12 | False | PASS |
| K1-U2 | le | `U_Flux23` | `…/out/2dc_P_S4U_Flux23_s42/xsec.root` | hXSec2D | 1.2e-12 | False | PASS |
| K1-U3 | le | `U_NormDISCC0` | `…/out/2dc_P_S4U_NormDISCC0_s42/xsec.root` | hXSec2D | 2.86e-13 | False | PASS |
| K1-U4 | le | `U_MaCCQE0` | `…/uq/purity_newomni/2d_xsec_MEFHC_5iter_lgbm_pn_uni_MaCCQE_0.root` | hXSec2D | 4.97e-12 | False | PASS |
| K1-U5 | le | `U_Flux23` | `…/uq/purity_newomni/2d_xsec_MEFHC_5iter_lgbm_pn_uni_Flux_23.root` | hXSec2D | 9.9e-13 | False | PASS |
| K1-U6 | le | `U_NormDISCC0` | `…/uq/purity_newomni/2d_xsec_MEFHC_5iter_lgbm_pn_uni_NormDISCC_0.root` | hXSec2D | 1.37e-11 | False | PASS |
| K1-L1 | le | `L_BAX0` | `…/out/2dc_P_S3_BeamAngleX0/xsec.root` | hXSec2D | 4.55e-13 | False | PASS |
| K1-P1 | le | `P_ctrl` | `…/out/pu_CTRL_s42/xsec.root` | hXSec2D | 1.37e-11 | False | PASS |
| K1-P2 | le | `P_PA` | `…/out/pu_PA_s42/xsec.root` | hXSec2D | 1.05e-11 | False | PASS |
| K1-P3 | le | `P_PA_b01` | `…/out/pu_PA_b01/xsec.root` | hXSec2D | 1.59e-13 | False | PASS |
| K1-R1 | le | `R_re2_MaCCQE0` | `run:R_p1_MaCCQE0` | hXSec2D | 8.64e-13 | False | PASS |
| K1-R2 | le | `RP_re2_PA` | `run:RP_p1_PA` | hXSec2D | 3.63e-13 | False | PASS |
| K1-D1 | le | `D_cv` | `…/out/2d/d2_data_refined.npz` | hXSec2D | 5.14e-12 | False | PASS |
| CHK-unit | le | `D_unit` | `run:D_cv` | hXSec2D | 1.81e-12 | False | PASS |
| CHK-det1 | le | `RB_001_rep` | `run:RB_001` | hXSec2D | 1.88e-14 | False | PASS |
| CHK-det2 | le | `FL_BAX0_rep` | `run:FL_BAX0` | hXSec2D | 6.36e-13 | False | PASS |
| CHK-null-r | le | `F_NormDISCC0` | `run:D_cv` | hXSec2D | 5.07e-12 | False | PASS |
| CHK-null-p | le | `U_NormDISCC0` | `run:C_cv` | hXSec2D | 1.44e-11 | False | PASS |
| CHK-eff | le | `D_cv` | `run:C_cv` | hEff2D | 0 | True | PASS |
| STREAM-1 | stream | `RB_001` | `run:B_S1_001` | — | 3.33e-16 | — | PASS |
| POW-1 | differs | `D_cv` | `run:C_cv` | hXSec2D | 0.101 | False | PASS |
| POW-2 | differs | `RB_001` | `run:D_cv` | hXSec2D | 0.182 | False | PASS |
| POW-3 | differs | `F_MaCCQE0` | `run:F_NormDISCC0` | hXSec2D | 0.0296 | False | PASS |
| POW-4 | differs | `FL_BAX0` | `run:F_NormDISCC0` | hXSec2D | 0.0105 | False | PASS |
| POW-5 | differs | `RPR_PA_b01` | `run:RF_PA` | hXSec2D | 0.216 | False | PASS |

**What the controls establish:**
- **The purity path is unchanged.**
  - `re2_driver.py` with purity subtraction reproduces Stage C's central unfold, unit-weight unfold, replicas,
    universes and lateral (K1-C*, B*, U1–U3, L1).
  - It also reproduces the July sweep's universes (K1-U4–U6) and the period unfolds (K1-P*).
  - All of these agree to ≤ 1.45e-11.
- **The copy changes nothing else.** `re2_driver.py` agrees with frozen `driver_p1.py` on the same helper
  (K1-R1, R2).
- **The refined central unfold matches RE-1's D2** to 5.1e-12 (K1-D1).
- **The checks have power.** Each power check moves hXSec2D by 1.0e-2 to 2.2e-1, against run-to-run noise of
  ≤ 6.4e-13 at the same CPU count (CHK-det1, det2).
- **The refined background stream enters the data correctly:** STREAM-1 agrees to 3.3e-16.

**Refinement health,** 21 rows: every `re2_driver.py --bkg-mode negweight-refined` run.
- Every row records `random_state` 45. The 19 rows that set a size also record 400 trees and 31 leaves; the other
  two, `R_re2_MaCCQE0` and `RP_re2_PA`, are the K1-R controls. They run without a size so they can be compared
  with `driver_p1.py` (RE2-DECLARATION.md:186, :190).
- The clipped fraction is at most 9.4e-5; the allowed maximum is 0.01.
- Refined/signed lies in [0.9999978, 0.9999999]; the allowed band is [0.99, 1.01].

## 4. Measured units and the rule (`units.json`)

The unit is a run's srun step: ElapsedRaw × AllocCPUS / 256 / 3600. Each class takes the **maximum** over its J0
runs. Counts are RE2-PLAN §4.2's.

| class | job | J0 runs (n) | unit, node-h (max) | count | projected node-h |
|---|---|---|---|---|---|
| central | J1 | 1 | 0.0601 | 3 | 0.18 |
| universe | J2 | 4 | 0.1597 | 175 | 27.95 |
| lateral | J3 | 2 | 0.2331 | 10 | 2.33 |
| replica (S1) | J4 | 10 | 0.0639 | 300 | 19.17 |
| replica_seed (S4(i)) | J6 | 8 | 0.0639 | 80 | 5.11 |
| period | J8 | 2 | 0.0408 | 37 | 1.51 |
| seed_panel (S4(ii)), diagnostic | J7 | 4 | 0.1597 | 39 | 6.23 |
| bkg_only (S2), diagnostic | J5 | 8 | 0.0639 | 100 | 6.39 |

**The rule's numbers:**
- room = 90 − 5.4755 = **84.5245** node-h.
- Core (J1, J2, J3, J4, J6, J8) projected **56.25**; 1.25 × core = **70.31** ≤ room.
- J7 is added: projected 62.48, worst **78.10** ≤ room.
- J5 is not added: 1.25 × (62.48 + 6.39) = 86.09 > room.
- **Verdict: WITHIN GRANT: core + J7.**

**Against the declaration's expectation:**
- RE2-DECLARATION.md §5.3 expected the second branch.
  - At today's packed 1.81× it put the core at about 98 node-h, worst case about 122.
  - On J0's own basis it put the core at about 83, worst case about 104.
- J0 measured the refined 2D unit well below the 5D figure, so the first branch applies. Ruling 2's ≤ 165 is not
  needed.
- The units were measured at one-quarter and one-half node: 64 and 128 CPUs.

## 5. Findings for part B

**F1. The rule projects step node-h; Slurm charges the exclusive node.** J0's steps took up this share of each job's
charge:

| job | steps' node-h | charge, node-h | steps / charge |
|---|---|---|---|
| J0b | 1.1855 | 1.4369 | 0.825 |
| J0a, whole job | 2.0103 | 4.0386 | 0.498 |
| J0a, after the preflight (2.634 node-h) | 2.0103 | 2.634 | 0.763 |

- **Why the share is below 1:** J0a's lanes were imbalanced (a2 ended about 1.2 h before a1), and every job ends
  in a lane tail.
- **What packing does to the margin:** at 0.76–0.83 packing, the core's charge is about 68–74 node-h. Core + J7 is
  about 75–82 node-h.
- **What that means:** these still fit room (84.52), but packing alone takes up most of the 1.25 factor. That leaves
  little margin for a slowdown.
- **What part B must do:**
  - pack lanes so each job's steps keep its node busy, for example with equal-length lanes;
  - project each job's charge from its own packing, not from step node-h;
  - check the ledger's cumulative charge against room before J7's job starts.

**F2. The lateral input check: re-hashing 54 GB over CFS cost about 1.3 h of J0a's preflight (D1).** That is
5,057 s, less J0b's 506 s preflight of the other inputs. The director ruled it
(preliminary, to be bound with part B):
- **The check:** part B checks `stat -c '%s %Y %i'` (size, mtime, inode) against the stat recorded with the J0a
  sha256. This is the universe-omnifile pattern in `re2_env.sh`.
- **On a mismatch:**
  - any stat mismatch forces a full re-hash;
  - a hash mismatch refuses the run.
- **Its test runs in both directions:**
  - a touched mtime, a changed size or a changed inode each forces the re-hash;
  - an unchanged stat skips it.
- **The recorded pair:**
  - sha256 `38b9fc307eabd864cd0fd663679b51fb2e6d064672410af6b3cf8b0a7e161ed5` (matched in J0a's preflight);
  - stat `53845911012 1784361874 759636316`, taken at 2026-10-24T01:03Z, while J0a's hash was reading the
    file.
- **Why the device number is excluded:** at the same moment the file's device number was
  - 124 on login12, where CFS is mounted as gpfs;
  - 105 on nid005117 and nid005118, where CFS is mounted through DVS (filesystem type 0x3e3f).
  
  Size, mtime and inode agreed on all three. A recorded device would miss on the other mount type and force the
  ~1.3 h re-hash on correct runs.

**F3. The universe omnifile and pscratch.**
- The universe omnifile is on pscratch, not CFS: `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/`.
- Its stat is still `171117087867 1783523295 882725391507234642` at 2026-10-24, as declared.
- J2 needs a full hash of it before it starts (RE2-DECLARATION.md §3). That hash reads from Lustre, not the slow CFS
  path.
- `df -h /pscratch` now reports 68%; the declaration recorded 85%.
- The purge risk (RE2-DECLARATION.md §8) still argues for part B promptly.

## 6. The part-B request

**The request.** Bind part B for J1–J4, J6, J8 and J7 within the 90 node-h grant. That leaves 84.5245 node-h after
J0. J5 stays out, as the rule says.

**The lane will write part B's declaration** to the plan and the deferred items (RE2-DECLARATION.md §1). Before any
production job it will contain:

1. **Job layout and limits:**
   - lanes packed per F1;
   - each job's projected charge from its own packing × 1.25;
   - each limit under 12 h;
   - a cumulative-charge check before J7's job.
2. **The lateral check of F2,** with its two-direction test, and the full universe-omnifile hash before J2.
3. **The deferred items:**
   - `re2/inventory.tsv`;
   - the R7 producer search;
   - the replaced-identity list for the rollup, C_PL, combination and Fig. 1 copies;
   - the code that writes the step weights the C2ST re-evaluation needs.
4. **RO-FPS** (§6 of the declaration), printed either way.
5. **HPSS:** the copies of the final products, each with a recorded `hsi` hash verification (R9).

**The lane asks the director** to confirm the request's scope (core + J7) before it writes the declaration.
