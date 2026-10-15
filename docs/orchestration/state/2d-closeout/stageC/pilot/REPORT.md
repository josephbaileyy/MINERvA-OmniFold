# 2D closeout Stage C pilot: REPORT (P0, P1, P2/K1, P2-G2/K2, P3)

**CITABLE FOR:**
- the pilot's terminal outcomes: P0, the P1 checks and σ ratios, **K1**, **K2**, P3;
- every pilot job's `sacct` row, each gate's printed arithmetic, the measured unit costs and peak memory;
- the S1–S5 production budget repriced from the pilot, with a ≥ 20% reserve (an estimate for the director's
  production grant, not a grant), under the stated node-type assumption (§7).

**NOT CITABLE FOR:**
- production authority, a G2 repair, a July rebuild, adoption, claims or publication. Production needs its own
  grant (pilot grant, "Production needs its own grant");
- any quoted cross-section product. Every pilot output is diagnostic and lives only in the pilot namespace and its
  CFS copy;
- σ_ML or σ_band re-measurement (pinned, not re-measured here).

| field | content |
|---|---|
| `Owner` | 2D closeout executor (2d closer), directed by the paper-tighten lane under [`AUTHORIZATION-20261012-2d-closeout-delegation.md`](../../../../AUTHORIZATION-20261012-2d-closeout-delegation.md) |
| `Grant` | [`AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md`](../../../../AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md); ceiling raised 12.9 → 20.0 by [`…-recap.md`](../../../../AUTHORIZATION-20261013-2d-closeout-stageC-pilot-recap.md) (PR #111, merge `9b30356c`) |
| `Bindings` | v1 [`…-binding.md`](../../../../AUTHORIZATION-20261013-2d-closeout-stageC-pilot-binding.md) (PR #110): package `92b0b466b4c94421446f7c751725365e8176793b`; v2 [`…-binding-v2.md`](../../../../AUTHORIZATION-20261013-2d-closeout-stageC-pilot-binding-v2.md) (PR #112, merge `f0926ccf`): package `a2ea0d6a50cc644f5898a2983f953172b2b3904b`, manifest `bd67d23a…`, `jobs.tsv` `1c30a50b…`, `launch.py` `fa0b0167…`, `sbatch_pilot.sh` `507ff6a1…` |
| `Branch` | `closeout/stagec-pilot-20261013` (package commits plus this REPORT) |
| `Namespace` | `/pscratch/sd/j/josephrb/2d-closeout-stageC-pilot-20261013/` (`$NS`) |
| `Durable copy` | `/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-pilot-20261013/`: 270 checksummed files (of 274; §10), sha256 re-measured on CFS against the pscratch source, 0 mismatches |
| `Charged` | **7.2479 node-h** of the 20.0 ceiling (every row in §5; retries and timeouts included) |

## 1. Answer

| item | terminal outcome | evidence (`$NS/results/`, sha256) |
|---|---|---|
| P0 producer bridge | **PASS** (default vs L0: max rel 9.35e-14, 0/205 over 1e-8; derived vs default: max rel 1.36e-11, 0/205) | `p0.json` `851a8a82…` |
| P1 b ≡ 1 control | **PASS** (unit run vs `XR-L0.root`: max rel 1.38e-11, 0/205 over 1e-8, provenance holds) | `p1_unit.json` `c6f53f20…`; repeated in `p1.json` |
| P1 σ ratios (20 + 20 + 20, paired by bootstrap seed) | **MEASURED**: median σ_joint/σ_fixed **1.032 ± 0.015**; median σ_bkg/σ_fixed **0.264 ± 0.021** (jackknife SE) | `p1.json` `381091ff…` |
| **K1** (P2, five comparisons) | **PASS** on all five; max rel ≤ 1.38e-11, max shift 2.09e-8 σ_ML | `p2.json` `8139a710…` |
| P2-EQ (derived vs default, real file) | **PASS** (max rel 1.57e-12) | `p2.json` |
| **K2** (P2-G2 on `Flux:23`, seeds 42 and 43) | **NOT RESOLVED ABOVE TRAINER NOISE**; seed-43 confirmation **NOT CONFIRMED** | `g2_s42.json` `0ad9da32…`, `g2_s43.json` `0915959b…` |
| P3 laterals from the active files | **MEASURED** for both (`BeamAngleX_0`, `Muon_Energy_MINOS_0`); provenance holds, no pin failed | `p3.json` `e5a02b1c…` |

**Production eligibility.** The pilot grant routes production only if K1 PASSES and K2 routes NOT MATERIAL or NOT
RESOLVED. **Both conditions hold.** No stop condition fired: P0 PASSED; the b ≡ 1 no-op control PASSED; the
identity (P2-EQ) PASSED; K1 PASSED; no gate refused. The one stop during the run (the B1 headroom stop, §3) was
ruled on by the director before any later batch. Production still needs its own grant; §7 prices it.

## 2. Terminal outcomes in detail

**P0** (`P0_default`, `P0_derived`, jobs 59733771/59733772): the current production driver at `74a4ed69…`
reproduces L0 under the frozen 1e-8 criterion (max rel 9.35e-14, 3 cells exactly equal); the derived path
reproduces the default on the CV (max rel 1.36e-11). Provenance holds; no pin failed.

**P1** (60 replicas, jobs 59753253–59753360; control `P1_unit` 59740518): each arm has 20/20 replicas with
matching provenance (none missing).

| arm | n | median rel σ over cells | replica mean relative to `E_U` (median over cells) |
|---|---|---|---|
| `fixed` (production driver, VL170 law at seed 42) | 20 | 0.00608 | 1.00036 |
| `joint` (data + signal MC + background streams) | 20 | 0.00643 | 1.00042 |
| `bkg` (background stream only) | 20 | 0.00175 | 0.99993 |

| ratio (per reported cell, ddof 1) | median | jackknife SE of median | q16–q84 over cells | mean |
|---|---|---|---|---|
| σ_joint / σ_fixed | 1.0316 | 0.0153 | 0.959–1.125 | 1.047 |
| σ_bkg / σ_fixed | 0.2642 | 0.0206 | 0.185–0.429 | 0.299 |

Reading, with no pass/fail (DESIGN §8). The median over cells of the per-cell paired ratio σ_joint/σ_fixed is
1.032 ± 0.015, about the ≈ 3% the Stage B report expected. That is 2.1 jackknife SE from 1. A jackknife SE of a
median is itself rough, so this is an indication, not a resolved effect. The ratio of the arms' median relative σ
(0.00643 / 0.00608 = 1.057) is a different statistic and is not the paired measure. The median per-cell
σ_bkg/σ_fixed is 0.264. The packaging-time checks (no-op
C1–C4, bkg variance = Σw² of B) PASSED before the pilot (DESIGN §8).

**K1** (`P2_NormDISCC0`, `P2_MaRES0`, `P2_Flux23`, `P2_MINOS0` on the derived path, `P2_MINOS0def` on the default
path; jobs 59734955–59734961): every comparison PASSES under E1 (1e-8) inside envelope E2.

| universe | path | max rel diff | cells over 1e-8 | max shift / σ_ML |
|---|---|---|---|---|
| `NormDISCC:0` (no-op) | derived | 1.38e-11 | 0/205 | 2.09e-8 |
| `MaRES:0` | derived | 2.43e-13 | 0/205 | 2.21e-10 |
| `Flux:23` | derived | 9.37e-13 | 0/205 | 1.29e-10 |
| `Muon_Energy_MINOS:0` | derived | 7.54e-12 | 0/205 | 1.06e-9 |
| `Muon_Energy_MINOS:0` | default (`--branch-select all`) | 7.89e-12 | 0/205 | 1.10e-9 |

P2-EQ, the first real-file equality of the selective read, `P2_MINOS0` vs `P2_MINOS0def`: max rel 1.57e-12, 0/205,
**PASS**. Null check, `P2_NormDISCC0` vs the July CV: max rel 1.43e-11, max shift 2.09e-8 σ_ML (MEASURED).

**K2** (`G2_on` 59747065 with `P2_Flux23` as its off run; seed-43 pair `G2_off_s43` 59753246, `G2_on_s43`
59753248). Every G gate is true at both seeds (seed 43: G-b max |c_on − 1| 2.72e-14, G-c 0.0).

| seed | r1 median / max (floored cells) | r3 = \|d\|/σ_ML median / p84 / max | integral rel change | outcome / routing |
|---|---|---|---|---|
| 42 | 0.040 / 0.927 | 0.912 / 2.15 / 9.27 | 8.96e-5 | MEASURED / NOT RESOLVED ABOVE TRAINER NOISE |
| 43 | 0.042 / 0.568 | 0.853 / 2.25 / 12.5 | 5.31e-5 | MEASURED / NOT RESOLVED ABOVE TRAINER NOISE |

Confirmation (`--confirm`, z = d/σ_ML over 205 cells): Pearson z43 vs z42 −0.295, Spearman −0.118; the seed-mean
r1 has median 0.026 and floored max 0.376 (rule holds). **Verdict NOT CONFIRMED; final routing NOT RESOLVED ABOVE
TRAINER NOISE.** The seed-42 pattern does not repeat at seed 43, so the miss-row weighting effect on `Flux:23` is
not resolved above the trainer's seed noise. This is a passing route for the exit condition, not a measurement of
zero.

**Resolution.**
- **Median r3:** 0.91 and 0.85 measured, against the pre-declared noise-only value of ≈ 0.95 (DESIGN line 289).
  K2 can exclude only a median effect large enough to raise r3 above its 2 σ_ML routing bound. It does not bound
  an effect below that.
- **Cell patterns:** the two seeds' per-cell z patterns are weakly anti-correlated (Pearson −0.295, Spearman
  −0.118). They do not reproduce each other, which is what the NOT CONFIRMED verdict tests.

**P3** (`P3_BeamAngleX0` retry 59802592, `P3_MINOS0` 59753421): the production driver on the CFS active files
(each hashed in the job against `SHA256SUMS`), seed 42, no `--universe`, `--branch-select all`. Both MEASURED.
Comparisons, with no pass/fail (DESIGN §7), over the 205 reported cells:

| comparison | \|d\|/σ_ML median / p84 / max | \|d\|/ref median / max | \|d\|/σ_band median / p84 |
|---|---|---|---|
| `P3_BeamAngleX0` vs July `BeamAngleX_0` (dump mode) | 1.01 / 2.39 / 5.27 | 0.18% / 1.44% | 1.04 / 2.95 |
| `P3_MINOS0` vs `P2_MINOS0def` (same driver and path, dump input) | 0.74 / 1.68 / 5.02 | 0.13% / 1.45% | 0.067 / 0.259 |
| `P3_MINOS0` vs July `Muon_Energy_MINOS_0` | identical to the row above to ≈ 1e-11 (`P2_MINOS0def` reproduces July, §2 K1) | | |

σ_band here is the per-cell, unfloored July pair half-difference |X_0 − X_1|/2 (`analyze_pilot.py` `p3()`), so its
max (1,424 and 244) is a ratio over cells where the July pair nearly coincides and is not read.

The active-file runs differ from the dump-mode runs at a median 0.7–1.0 σ_ML. That is the trainer-noise scale: a
trainer-path change moves cells by O(σ_ML) (DESIGN line 209), and the noise-only median r3 is ≈ 0.95 (DESIGN line
289). A single-seed comparison therefore cannot separate the active-vs-dump input difference from trainer noise.
That input difference is the 8,525,527 reco-failing rows whose truth weights differ (DESIGN §7). **No part of the
difference is attributed to the input.**

`P3_BeamAngleX0` is the first unfold of the beam-angle lateral on a selection-complete input (DESIGN §7). It is one
seed and diagnostic only. Its shift from the CV is not computed here, so it is not a measurement of the beam-angle
uncertainty.

## 3. Run record

Times are PDT (`sacct`'s clock). Gates act at submission, so batches are listed by their `sacct` Submit time.

| when (PDT) | event |
|---|---|
| 2026-10-13 05:51 | B0 (P0) submitted under v1 `92b0b466`; P0 PASS |
| 06:45–06:46 | B1 (P2 × 5, `P1_unit`) submitted |
| 08:50 | `P1_unit` 59734962 TIMEOUT at 1,930 s, past its 1,920 s cap. Iteration 4 of 0–4 had started at 1,756 s. On node `nid004107`, `sacct -a -N nid004107` lists jobs of 17 other users overlapping the attempt's window (not necessarily simultaneous). A headroom condition failed: pre-B4, elapsed × 1.3 ≤ 1,920 s. The director set it in a relayed message after P0, not in a committed record. I also held B2: `G2_on`'s 3,000 s cap failed a proportional check against the P5 pair. The recap record later ruled an off run's time "not a like-for-like check" (§3(c)). **Stop, reported** |
| 09:09:53 | The director's ruling arrives by message: `P1_unit` retry at 00:58:00 under the v1 binding; ceiling 20.0 and v2 caps to follow in a recap record |
| 09:10:19 | `P1_unit` retry 59740518 submitted under that ruling and the grant's committed "attempts" row: one walltime retry at 1.5 × a re-projection, 2,295 × 1.5 = 3,443 s → 00:58:00. `out/2dc_C_P1_unit/` was empty (`launch.py` refuses otherwise) |
| 09:12:19 / 09:13:13 | Recap record committed (`6382a70e`) and merged (PR #111, `9b30356c`). Its §3(a) records the same ruling, so it confirmed the retry about three minutes after submission |
| 10:16 | Retry (started 10:04) COMPLETED in 715 s; b ≡ 1 PASS; headroom 715 × 1.3 = 930 ≤ 3,480 s. Co-tenancy recorded once, as §3(a) asks, at 17:04:53Z: `nid004072` held josephrb 64 + rul048 64 + rul048 128 CPUs |
| 2026-10-13 | v2 binding (PR #112); v2 deployed to `$NS/repo` after `squeue` showed no pilot job (§6) |
| 11:57 | B2 (`G2_on`) submitted; seed-42 analysis after it ended |
| 14:27–14:31 | B3 (seed-43 pair), then B4–B8 submitted through the gate in turn |
| 2026-10-14 15:48 | Last pilot job before the outage ends (`P1_fixed_13`) |
| 2026-10-14 17:03–21:08 | Perlmutter-wide outage. Nodes reported "Not responding" from 17:03. Every partition was `DOWN` when observed at 20:34, with 29 pilot jobs `PartitionDown`. Pilot jobs started again at 21:08 (`P1_fixed_14`, `_15`). No job was killed |
| 2026-10-15 00:56 | `P3_BeamAngleX0` 59753370 TIMEOUT at 2,727 s (cap 2,700 s), after all five iterations |
| 00:59 | Walltime retry 59802592 submitted, cap 01:10:00 (§8) |
| 02:42 | Retry COMPLETED in 2,085 s. Every pilot job is terminal (73 jobs + 2 retries); P1 and P3 analyses run |

Two operational incidents changed no job: the NERSC sshproxy key expired twice during the run and was renewed by
Joseph (monitoring only; jobs unaffected), and the first v2 deploy pipe dropped mid-extract (redone from a local
`git archive`, §6).

## 4. Gates (each as printed by `launch.py`, `$NS/gatelog/*_submit.txt`)

Every gate and submit ran as `USER=josephrb python3 launch.py …`. Each gate ran only after every earlier
`2dc_C_*` submission appeared in its printed ledger (the ledger column counts them). Charged = `sacct`
ElapsedRaw × billing / 256 / 3600; in-flight jobs count at their full enforced cap.

| gate | completed | + in flight at cap | + batch | = total | ceiling | ledger rows | submitted |
|---|---|---|---|---|---|---|---|
| B0 | 0.0000 | 0.0000 | 0.2083 | 0.2083 | 12.9 | 0 | 2 |
| B1 | 0.1656 | 0.0000 | 1.7167 | 1.8823 | 12.9 | 2 | 6 |
| P1_unit_retry | 1.2151 | 0.0000 | 0.2417 | 1.4567 | 12.9 | 8 | 1 |
| B2 | 1.2647 | 0.0000 | 0.6250 | 1.8897 | 20.0 | 9 | 1 |
| B3 | 1.4879 | 0.0000 | 0.9583 | 2.4463 | 20.0 | 10 | 2 |
| B4 | 1.4879 | 0.9583 | 3.6250 | 6.0713 | 20.0 | 12 | 15 |
| B5 | 1.4879 | 4.5833 | 3.6250 | 9.6962 | 20.0 | 27 | 15 |
| B6 | 1.4879 | 8.2083 | 3.6250 | 13.3212 | 20.0 | 42 | 15 |
| B7 | 1.4879 | 11.8333 | 3.6250 | 16.9462 | 20.0 | 57 | 15 |
| B8 | 1.4879 | 15.4583 | 0.7500 | 17.6963 | 20.0 | 72 | 2 |
| P3_BeamAngleX0_retry | 6.9583 | 0.0000 | 0.5833 | 7.5417 | 20.0 | 74 | 1 |

The gate's first possible refusal was at B8 (DESIGN §4); no gate refused.

## 5. Every `sacct` row

`sacct -u josephrb -S 2026-10-13T00:00:00`, allocation rows, with MaxRSS from each job's `batch` step (the
allocation row's MaxRSS is empty). Billing = allocated CPUs on the shared QOS.

| job id | name | state | elapsed (s) | cap | CPUs | node | start (PDT) | MaxRSS (GiB) | charged node-h |
|---|---|---|---|---|---|---|---|---|---|
| 59733771 | `2dc_C_P0_default` | COMPLETED | 935 | 00:25:00 | 64 | `nid004141` | 2026-10-13 06:15:18 | 13.70 | 0.0649 |
| 59733772 | `2dc_C_P0_derived` | COMPLETED | 1,450 | 00:25:00 | 64 | `nid004130` | 2026-10-13 06:19:37 | 13.69 | 0.1007 |
| 59734955 | `2dc_C_P2_NormDISCC0` | COMPLETED | 1,003 | 00:30:00 | 128 | `nid004091` | 2026-10-13 07:19:43 | 15.38 | 0.1393 |
| 59734956 | `2dc_C_P2_MaRES0` | COMPLETED | 1,069 | 00:30:00 | 128 | `nid004091` | 2026-10-13 07:19:43 | 14.54 | 0.1485 |
| 59734957 | `2dc_C_P2_Flux23` | COMPLETED | 1,166 | 00:30:00 | 128 | `nid004093` | 2026-10-13 07:57:57 | 13.68 | 0.1619 |
| 59734959 | `2dc_C_P2_MINOS0` | COMPLETED | 856 | 00:30:00 | 128 | `nid004132` | 2026-10-13 07:57:57 | 15.96 | 0.1189 |
| 59734961 | `2dc_C_P2_MINOS0def` | COMPLETED | 2,497 | 01:10:00 | 128 | `nid004076` | 2026-10-13 08:18:38 | 65.94 | 0.3468 |
| 59734962 | `2dc_C_P1_unit` | TIMEOUT | 1,930 | 00:32:00 | 64 | `nid004107` | 2026-10-13 08:18:38 | 14.15 | 0.1340 |
| 59740518 | `2dc_C_P1_unit` | COMPLETED | 715 | 00:58:00 | 64 | `nid004072` | 2026-10-13 10:04:19 | 14.29 | 0.0497 |
| 59747065 | `2dc_C_G2_on` | COMPLETED | 1,607 | 01:15:00 | 128 | `nid004078` | 2026-10-13 13:27:19 | 16.64 | 0.2232 |
| 59753246 | `2dc_C_G2_off_s43` | COMPLETED | 695 | 00:40:00 | 128 | `nid004095` | 2026-10-13 14:35:03 | 15.98 | 0.0965 |
| 59753248 | `2dc_C_G2_on_s43` | COMPLETED | 752 | 01:15:00 | 128 | `nid004137` | 2026-10-13 14:35:04 | 16.55 | 0.1044 |
| 59753253 | `2dc_C_P1_fixed_01` | COMPLETED | 894 | 00:58:00 | 64 | `nid004114` | 2026-10-13 15:15:32 | 14.16 | 0.0621 |
| 59753254 | `2dc_C_P1_fixed_02` | COMPLETED | 691 | 00:58:00 | 64 | `nid004141` | 2026-10-13 15:15:32 | 13.49 | 0.0480 |
| 59753255 | `2dc_C_P1_fixed_03` | COMPLETED | 668 | 00:58:00 | 64 | `nid004141` | 2026-10-13 15:51:43 | 13.44 | 0.0464 |
| 59753256 | `2dc_C_P1_fixed_04` | COMPLETED | 745 | 00:58:00 | 64 | `nid004141` | 2026-10-13 16:09:38 | 13.47 | 0.0517 |
| 59753257 | `2dc_C_P1_fixed_05` | COMPLETED | 934 | 00:58:00 | 64 | `nid004104` | 2026-10-13 17:03:40 | 14.20 | 0.0649 |
| 59753258 | `2dc_C_P1_joint_01` | COMPLETED | 983 | 00:58:00 | 64 | `nid004092` | 2026-10-13 17:05:10 | 14.24 | 0.0683 |
| 59753259 | `2dc_C_P1_joint_02` | COMPLETED | 674 | 00:58:00 | 64 | `nid004137` | 2026-10-13 18:31:39 | 13.56 | 0.0468 |
| 59753260 | `2dc_C_P1_joint_03` | COMPLETED | 786 | 00:58:00 | 64 | `nid004122` | 2026-10-13 18:32:44 | 14.29 | 0.0546 |
| 59753261 | `2dc_C_P1_joint_04` | COMPLETED | 825 | 00:58:00 | 64 | `nid004100` | 2026-10-13 19:59:59 | 14.29 | 0.0573 |
| 59753263 | `2dc_C_P1_joint_05` | COMPLETED | 991 | 00:58:00 | 64 | `nid004111` | 2026-10-13 20:11:18 | 14.28 | 0.0688 |
| 59753264 | `2dc_C_P1_bkg_01` | COMPLETED | 898 | 00:58:00 | 64 | `nid004119` | 2026-10-13 22:28:53 | 14.24 | 0.0624 |
| 59753265 | `2dc_C_P1_bkg_02` | COMPLETED | 781 | 00:58:00 | 64 | `nid004109` | 2026-10-13 22:43:26 | 14.23 | 0.0542 |
| 59753267 | `2dc_C_P1_bkg_03` | COMPLETED | 833 | 00:58:00 | 64 | `nid004108` | 2026-10-14 00:52:32 | 14.25 | 0.0578 |
| 59753268 | `2dc_C_P1_bkg_04` | COMPLETED | 800 | 00:58:00 | 64 | `nid004106` | 2026-10-14 01:00:55 | 14.23 | 0.0556 |
| 59753269 | `2dc_C_P1_bkg_05` | COMPLETED | 1,225 | 00:58:00 | 64 | `nid004094` | 2026-10-14 03:13:31 | 14.28 | 0.0851 |
| 59753274 | `2dc_C_P1_fixed_06` | COMPLETED | 979 | 00:58:00 | 64 | `nid004097` | 2026-10-14 05:33:25 | 14.14 | 0.0680 |
| 59753276 | `2dc_C_P1_fixed_07` | COMPLETED | 728 | 00:58:00 | 64 | `nid004106` | 2026-10-14 07:09:26 | 13.49 | 0.0506 |
| 59753278 | `2dc_C_P1_fixed_08` | COMPLETED | 1,301 | 00:58:00 | 64 | `nid004105` | 2026-10-14 07:14:50 | 14.05 | 0.0903 |
| 59753280 | `2dc_C_P1_fixed_09` | COMPLETED | 1,206 | 00:58:00 | 64 | `nid004105` | 2026-10-14 07:36:56 | 13.51 | 0.0838 |
| 59753281 | `2dc_C_P1_fixed_10` | COMPLETED | 1,334 | 00:58:00 | 64 | `nid004104` | 2026-10-14 07:42:02 | 13.49 | 0.0926 |
| 59753282 | `2dc_C_P1_joint_06` | COMPLETED | 1,299 | 00:58:00 | 64 | `nid004116` | 2026-10-14 08:41:25 | 14.25 | 0.0902 |
| 59753283 | `2dc_C_P1_joint_07` | COMPLETED | 962 | 00:58:00 | 64 | `nid004128` | 2026-10-14 08:48:55 | 14.17 | 0.0668 |
| 59753284 | `2dc_C_P1_joint_08` | COMPLETED | 1,159 | 00:58:00 | 64 | `nid004116` | 2026-10-14 09:12:39 | 13.53 | 0.0805 |
| 59753285 | `2dc_C_P1_joint_09` | COMPLETED | 923 | 00:58:00 | 64 | `nid004100` | 2026-10-14 09:19:39 | 13.53 | 0.0641 |
| 59753287 | `2dc_C_P1_joint_10` | COMPLETED | 1,996 | 00:58:00 | 64 | `nid004092` | 2026-10-14 09:48:17 | 14.26 | 0.1386 |
| 59753290 | `2dc_C_P1_bkg_06` | COMPLETED | 850 | 00:58:00 | 64 | `nid004137` | 2026-10-14 10:32:30 | 13.57 | 0.0590 |
| 59753291 | `2dc_C_P1_bkg_07` | COMPLETED | 649 | 00:58:00 | 64 | `nid004137` | 2026-10-14 10:46:53 | 13.54 | 0.0451 |
| 59753292 | `2dc_C_P1_bkg_08` | COMPLETED | 1,125 | 00:58:00 | 64 | `nid004097` | 2026-10-14 12:08:07 | 13.80 | 0.0781 |
| 59753293 | `2dc_C_P1_bkg_09` | COMPLETED | 1,126 | 00:58:00 | 64 | `nid004140` | 2026-10-14 12:21:32 | 14.28 | 0.0782 |
| 59753294 | `2dc_C_P1_bkg_10` | COMPLETED | 1,005 | 00:58:00 | 64 | `nid004119` | 2026-10-14 14:25:53 | 13.69 | 0.0698 |
| 59753300 | `2dc_C_P1_fixed_11` | COMPLETED | 825 | 00:58:00 | 64 | `nid004137` | 2026-10-14 14:25:53 | 13.47 | 0.0573 |
| 59753302 | `2dc_C_P1_fixed_12` | COMPLETED | 969 | 00:58:00 | 64 | `nid004094` | 2026-10-14 15:14:05 | 13.53 | 0.0673 |
| 59753304 | `2dc_C_P1_fixed_13` | COMPLETED | 2,003 | 00:58:00 | 64 | `nid004117` | 2026-10-14 15:15:26 | 14.13 | 0.1391 |
| 59753305 | `2dc_C_P1_fixed_14` | COMPLETED | 1,118 | 00:58:00 | 64 | `nid004095` | 2026-10-14 21:08:40 | 13.84 | 0.0776 |
| 59753306 | `2dc_C_P1_fixed_15` | COMPLETED | 1,030 | 00:58:00 | 64 | `nid004095` | 2026-10-14 21:08:40 | 13.87 | 0.0715 |
| 59753308 | `2dc_C_P1_joint_11` | COMPLETED | 1,088 | 00:58:00 | 64 | `nid004140` | 2026-10-14 22:32:20 | 14.24 | 0.0756 |
| 59753309 | `2dc_C_P1_joint_12` | COMPLETED | 1,419 | 00:58:00 | 64 | `nid004076` | 2026-10-14 22:35:11 | 14.27 | 0.0985 |
| 59753311 | `2dc_C_P1_joint_13` | COMPLETED | 794 | 00:58:00 | 64 | `nid004086` | 2026-10-14 23:05:38 | 14.28 | 0.0551 |
| 59753312 | `2dc_C_P1_joint_14` | COMPLETED | 1,327 | 00:58:00 | 64 | `nid004139` | 2026-10-14 23:05:38 | 14.28 | 0.0922 |
| 59753313 | `2dc_C_P1_joint_15` | COMPLETED | 1,038 | 00:58:00 | 64 | `nid004137` | 2026-10-14 23:30:26 | 14.22 | 0.0721 |
| 59753314 | `2dc_C_P1_bkg_11` | COMPLETED | 1,056 | 00:58:00 | 64 | `nid004107` | 2026-10-14 23:30:30 | 14.30 | 0.0733 |
| 59753315 | `2dc_C_P1_bkg_12` | COMPLETED | 1,225 | 00:58:00 | 64 | `nid004122` | 2026-10-14 23:47:20 | 13.91 | 0.0851 |
| 59753317 | `2dc_C_P1_bkg_13` | COMPLETED | 1,060 | 00:58:00 | 64 | `nid004122` | 2026-10-14 23:47:20 | 13.87 | 0.0736 |
| 59753319 | `2dc_C_P1_bkg_14` | COMPLETED | 758 | 00:58:00 | 64 | `nid004133` | 2026-10-14 23:50:04 | 14.29 | 0.0526 |
| 59753321 | `2dc_C_P1_bkg_15` | COMPLETED | 1,343 | 00:58:00 | 64 | `nid004072` | 2026-10-14 23:50:04 | 13.80 | 0.0933 |
| 59753334 | `2dc_C_P1_fixed_16` | COMPLETED | 1,365 | 00:58:00 | 64 | `nid004072` | 2026-10-14 23:50:04 | 13.72 | 0.0948 |
| 59753338 | `2dc_C_P1_fixed_17` | COMPLETED | 1,252 | 00:58:00 | 64 | `nid004072` | 2026-10-14 23:50:04 | 13.74 | 0.0869 |
| 59753340 | `2dc_C_P1_fixed_18` | COMPLETED | 1,652 | 00:58:00 | 64 | `nid004097` | 2026-10-14 23:50:04 | 13.68 | 0.1147 |
| 59753342 | `2dc_C_P1_fixed_19` | COMPLETED | 1,808 | 00:58:00 | 64 | `nid004097` | 2026-10-14 23:50:04 | 13.65 | 0.1256 |
| 59753344 | `2dc_C_P1_fixed_20` | COMPLETED | 1,566 | 00:58:00 | 64 | `nid004097` | 2026-10-14 23:50:04 | 13.83 | 0.1087 |
| 59753347 | `2dc_C_P1_joint_16` | COMPLETED | 1,343 | 00:58:00 | 64 | `nid004099` | 2026-10-14 23:50:04 | 13.74 | 0.0933 |
| 59753350 | `2dc_C_P1_joint_17` | COMPLETED | 1,328 | 00:58:00 | 64 | `nid004099` | 2026-10-14 23:50:04 | 13.79 | 0.0922 |
| 59753351 | `2dc_C_P1_joint_18` | COMPLETED | 1,427 | 00:58:00 | 64 | `nid004099` | 2026-10-14 23:50:04 | 13.81 | 0.0991 |
| 59753352 | `2dc_C_P1_joint_19` | COMPLETED | 720 | 00:58:00 | 64 | `nid004133` | 2026-10-15 00:05:18 | 13.51 | 0.0500 |
| 59753353 | `2dc_C_P1_joint_20` | COMPLETED | 896 | 00:58:00 | 64 | `nid004073` | 2026-10-15 00:11:31 | 14.27 | 0.0622 |
| 59753354 | `2dc_C_P1_bkg_16` | COMPLETED | 915 | 00:58:00 | 64 | `nid004102` | 2026-10-15 00:11:31 | 14.28 | 0.0635 |
| 59753356 | `2dc_C_P1_bkg_17` | COMPLETED | 1,237 | 00:58:00 | 64 | `nid004122` | 2026-10-15 00:11:31 | 13.51 | 0.0859 |
| 59753357 | `2dc_C_P1_bkg_18` | COMPLETED | 1,062 | 00:58:00 | 64 | `nid004122` | 2026-10-15 00:11:31 | 13.55 | 0.0737 |
| 59753358 | `2dc_C_P1_bkg_19` | COMPLETED | 1,137 | 00:58:00 | 64 | `nid004115` | 2026-10-15 00:11:31 | 13.95 | 0.0790 |
| 59753360 | `2dc_C_P1_bkg_20` | COMPLETED | 981 | 00:58:00 | 64 | `nid004115` | 2026-10-15 00:11:31 | 13.83 | 0.0681 |
| 59753370 | `2dc_C_P3_BeamAngleX0` | TIMEOUT | 2,727 | 00:45:00 | 128 | `nid004115` | 2026-10-15 00:11:31 | 13.21 | 0.3787 |
| 59753421 | `2dc_C_P3_MINOS0` | COMPLETED | 2,657 | 00:45:00 | 128 | `nid004112` | 2026-10-15 00:11:31 | 14.06 | 0.3690 |
| 59802592 | `2dc_C_P3_BeamAngleX0` | COMPLETED | 2,085 | 01:10:00 | 128 | `nid004117` | 2026-10-15 02:07:24 | 13.94 | 0.2896 |
| | **75 jobs** | | | | | | | | **7.2479** |

## 6. Deployment

- **v1** `92b0b466b4c94421446f7c751725365e8176793b`: `git archive` to `$NS/repo`, every file checked against
  `manifest.json`. B0, B1 and the `P1_unit` retry ran on it. The tree is kept as `$NS/repo-v1-92b0b466/`.
- **v2** `a2ea0d6a50cc644f5898a2983f953172b2b3904b`, deployed after the v2 binding was on `origin/main` and `squeue`
  showed no pilot job. The first deploy pipe died (ssh 255) after `repo` had been moved aside, leaving a partial
  extract. It was redone from a local `git archive -o` file (sha256 `6da3f591…`, 448,440,320 B), copied with `scp`,
  sha-checked on the cluster, extracted into a fresh `repo/`, and the driver copies placed. `verify_deploy_v2.py`
  checked the four bound digests and all 41 manifest files: 0 mismatches. `.deployed_commit` = `a2ea0d6a…`. B2–B8
  and the P3 retry ran on v2.
- No code changed after either deployment.

## 7. Unit costs, peak memory, and S1–S5 repriced

**Measured unit costs** (charge per job from §5):

| unit | pilot jobs | elapsed (s) | charge (node-h) | MaxRSS (GiB, max) | Stage B estimate |
|---|---|---|---|---|---|
| u_CV: 64-CPU shared CV unfold (P1 replicas) | 60 | 649–2,003 (median 1,034, p84 1,343) | mean **0.0754**, p84 **0.0933** (range 0.0451–0.1391; sum 4.5217) | 14.30 | 0.058–0.066 |
| u_CV, other 64-CPU runs (`P0_default`, `P0_derived`, `P1_unit` retry) | 3 | 935, 1,450, 715 | 0.0649, 0.1007, 0.0497 | 14.29 | (same) |
| u_U,sel: 128-CPU universe unfold, derived (selective) read (`P2_*` derived, `G2_*`) | 7 | 695–1,607 | mean **0.1418**, max 0.2232 | 16.64 | ≈ 0.25 |
| u_U: 128-CPU universe unfold, all branches (`P2_MINOS0def`) | 1 | 2,497 | **0.3468** | 65.94 | 0.65–0.76 (full regular node) |
| u_A: 128-CPU active-file lateral (`P3_*`, completed) | 2 | 2,085, 2,657 | mean **0.3293** (0.2896, 0.3690); high edge 0.3889 (the timed-out attempt's 2,800 s re-projection) | 14.06 | 0.25–0.72 (unmeasured) |
| timed-out attempts (charged, not units) | 2 | `P1_unit` 1,930; `P3_BeamAngleX0` 2,727 | 0.1340; 0.3787 | — | — |

Peak memory never approached the 243,840M (128-CPU) or 121,920M (64-CPU) allocations: the largest was
`P2_MINOS0def`, the full-branch default read, at 65.94 GiB. No job was killed for memory.

**S1–S5** (Stage B REPORT §7 run counts, unchanged; units repriced from the pilot).

**Basis: the universe and lateral units were measured on 128 shared CPUs.** That is billed at 128/256 = 0.5 node.
Stage B's u_U and u_U,sel assumed a full regular node. The pilot's runs were not faster:
- `P2_MINOS0def` took 2,497 s, against a July median of 2,530 s;
- P2 derived took 856–1,166 s, against Stage B's 888 s.

So the drop in S3 and S4 against Stage B comes from billing, not speed. The table assumes production runs these
unfolds on shared QOS at 128 CPUs, as the pilot did. On regular nodes their terms double (second table).

**Edges.** For each unit, the left figure is the measured mean (the expected cost, not a lower bound). The right
figure is a conservative per-job value:
- **u_CV:** p84 over the 60 replicas. They spread 649–2,003 s, cause not diagnosed.
- **u_U,sel → u_U** for S4(ii), as in Stage B.
- **u_A:** mean of the two completed P3 runs, 0.3293. Including the timed-out attempt's 2,800 s re-projection, the
  mean is 0.3491. The high edge is that re-projection, 0.3889.
- **u_U and u_A carry no measured spread.** u_U rests on one run and u_A on two runs plus one re-projection.

| item | runs | repriced node-h (low–high) | Stage B estimate |
|---|---|---|---|
| S1 statistical ensemble, 300 replicas, three streams | 300 × u_CV | 22.6–28.0 | 17.4–19.8 |
| S2 bkg-only separable arm, 100 replicas | 100 × u_CV | 7.5–9.3 | 5.8–6.6 |
| S3 remaining 8 laterals from active files | 8 × u_A | 2.6–3.1 | 2.0–5.8 |
| S4 `C_ML` factorial: (i) 20 bootstrap × 5 seed triplets; (ii) 7 universe settings × 5 seeds | 100 × u_CV + 35 × (u_U,sel … u_U) | 12.5–21.5 | 14.6–33.2 |
| S5 rollups, C04/X01/KI-92 repairs, matrices | login node | 0 | 0 |
| **subtotal** | | **45.3–61.9** | 39.8–65.4 |
| **≥ 20% reserve** (admitted − subtotal) | | **11.3–15.5** | |
| **admitted total** (subtotal / 0.8) | | **56.6–77.4** | 49.8–81.8 |

Units used: u_CV 0.0754–0.0933; u_U,sel 0.1418; u_U 0.3468; u_A 0.3293–0.3889. S4(ii)'s high edge prices all 35
runs at u_U (the full-branch read), as Stage B did; at u_U,sel's measured max (0.2232) S4 would be 17.1.

**Alternatives** (same run counts):

| assumption | S3 | S4 | subtotal | admitted (/ 0.8) |
|---|---|---|---|---|
| as above: shared QOS, 128 CPUs | 2.6–3.1 | 12.5–21.5 | 45.3–61.9 | 56.6–77.4 |
| universe and lateral unfolds on regular nodes (billing 256: u_U,sel, u_U, u_A × 2) | 5.3–6.2 | 17.5–33.6 | 52.9–77.1 | 66.1–96.4 |
| shared QOS, u_U and u_A high edges × 1.85 (u_CV's measured max/mean spread) | 2.6–4.9 | 12.5–31.7 | 45.3–73.9 | 56.6–92.4 |
| regular nodes and the × 1.85 spread | 5.3–9.7 | 17.5–54.1 | 52.9–101.2 | 66.1–126.5 |

S1 and S2 are the same in every row: 22.6–28.0 and 7.5–9.3.

The ≥ 20% reserve follows the repository's cost model: admitted = subtotal / 0.8, so the reserve is 20% of the
admitted total (Stage B review M6).

**Gate sizing for production (not a cost):** the gate holds every in-flight job at its full cap. At the v2 P1 cap
(00:58:00, 0.2417 node-h per 64-CPU replica), 300 S1 replicas reserve 72.5 node-h of caps while queued even though
they charge about 22.6 node-h. A production grant sized at the admitted total therefore needs batching, or a cap
re-based on the 60 replicas measured here (their max, 2,003 s, × 1.5 = 3,005 s → 00:51:00, 0.2125 node-h).

## 8. Cap headroom

Caps against measured elapsed, per job family (enforced cap from `jobs.tsv`, or the retry's re-projected cap):

| family | cap | max elapsed | max / cap | note |
|---|---|---|---|---|
| P0 | 00:25:00 (1,500 s) | 1,450 s | 0.97 | `P0_derived` |
| P2 derived | 00:30:00 (1,800 s) | 1,166 s | 0.65 | |
| P2 default | 01:10:00 (4,200 s) | 2,497 s | 0.59 | |
| `P1_unit` v1 | 00:32:00 (1,920 s) | 1,930 s | TIMEOUT | the B1 stop |
| `P1_unit` retry, P1 replicas (v2) | 00:58:00 (3,480 s) | 2,003 s | 0.58 | retry 715 s; pre-B4 condition 715 × 1.3 = 930 ≤ 3,480 s held |
| `G2_on` / `G2_on_s43` (v2) | 01:15:00 (4,500 s) | 1,607 s | 0.36 | the director replaced the B2 headroom check with this ordinary retry trigger |
| `G2_off_s43` (v2) | 00:40:00 (2,400 s) | 695 s | 0.29 | |
| P3 | 00:45:00 (2,700 s) | 2,727 s | TIMEOUT | `P3_MINOS0` 2,657 s (0.98); P3's composite basis (1,704 s, DESIGN §9) was at least 1.56× low |
| `P3_BeamAngleX0` retry | 01:10:00 (4,200 s) | 2,085 s | 0.50 | |

**Retries.** Two jobs used their one walltime retry, both for walltime, neither after a scientific result.

- **`P1_unit`.** Submitted at 09:10:19 PDT under two authorities:
  - the grant's committed "attempts" row: one walltime retry at 1.5 × a re-projection from the job's own progress;
  - the director's ruling, relayed by message at 09:09:53.

  The recap record committing that ruling (§3(a)) landed at 09:12:19 and merged at 09:13:13, about three minutes
  after submission (§3). Re-projection: 2,295 s × 1.5 = 3,443 s → 00:58:00. `out/2dc_C_P1_unit/` was empty.
- **`P3_BeamAngleX0`.** Submitted under the DESIGN §9 rule, with no further ruling needed. At the kill its log
  showed all five iterations finished and the first four post-unfold `[CHECK]` lines printed. The fourth `[CHECK]`
  line was written at `.out` mtime 00:56:52, 2,721 s into the job. The verifier measured 73–79 s of finalization after
  that line in the sibling jobs, which gives the re-projection: ≈ 2,800 s × 1.5 = 4,200 s → 01:10:00 (< 12 h).
  - `out/` was empty, so nothing was moved aside.
  - Gate: 6.9583 + 0 + 0.5833 = 7.5417 ≤ 20.0.
  - MaxRSS 13.2 GiB, so not an out-of-memory kill.

Neither retry failed again, so no line is INCONCLUSIVE.

**Ceiling headroom.** Charged **7.2479** of 20.0 node-h (**12.7521** unused). The largest committed
worst case at any gate was B8's 17.6963 (2.3037 below the ceiling).

## 9. Correction on record

When I first requested the v1 binding, I sent the package commit as `92b0b466d4b2dce5…`, a hand-expanded short sha.
The true commit is **`92b0b466b4c94421446f7c751725365e8176793b`**. The director caught the error with `git rev-parse`
before binding, and the v1 binding cites the true value. Every sha in this REPORT was pasted from a tool result.

## 10. Evidence and durable copies

- **CFS (durable):** `/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-pilot-20261013/` holds `results/`,
  `gatelog/`, `retries/`, `logs/` (every job's `.out`/`.err`), `out/` (every job's `xsec.root` and the G2 override),
  `preflight/`, `tmp/verify_deploy_v2.py` and `repo-meta/` (both `.deployed_commit` values). `SHA256SUMS.pscratch`
  (sha256 `b82a0e085fab914693291ddc2468a197315987e9c111b8c05491ef4bd3c7f33f`, 270 entries) was computed on the
  pscratch originals, and `sha256sum -c` on the CFS copies returned 0.
  - The directory holds 274 files. The four outside that list are `SHA256SUMS.pscratch` itself, `.filelist`
    (its input list), and the two `repo-meta/` files.
  - The `repo-meta/` files are copies of `.deployed_commit` (v1 `92b0b466…`, v2 `a2ea0d6a…`). The verifier checked
    their contents by hand. The v2 deploy tarball (428 MB, reproducible by
  `git archive a2ea0d6a`) was not copied.
- **In this repository:** [`evidence/results/`](evidence/results/) (every analysis JSON and its stdout),
  [`evidence/gatelog/`](evidence/gatelog/) (every gate pre-check and submit printout) and
  [`evidence/SHA256SUMS.pscratch`](evidence/SHA256SUMS.pscratch). The 39 copied files check against it
  (`shasum -a 256 -c`, 0 failures).
- **Result digests** (sha256): `p0.json` `851a8a82e00fd82b802f8145f58482b893d602d971eb9f07b67e613ab2ce61e4`;
  `p1_unit.json` `c6f53f20f0ee9cbe3599b24ac7d0c2fd7809620ad968ba0907aa509891e5234b`; `p1.json`
  `381091ff538000659ffe7140325409899bfb961c6b97d32d87ad4ddac36d43bb`; `p2.json`
  `8139a710d7af4f47dac00213432ed9a845c8a868c3ea1cda6b6dfb102af2ce4a`; `g2_s42.json`
  `0ad9da3253b1848a1148298269f66db3f0372a6f7b38153d7c2065b2e4fa14c5`; `g2_s43.json`
  `0915959be53b819d680a75ab051a5fefa793ed23c6bc617726b872e6b7c94501`; `p3.json`
  `e5a02b1c88b3d06da39277e25283c3285680f853ce42c9a95821f0050baa11a6`.
- **Manifest.** `manifest.json` stays the v2-bound `bd67d23a…`: it describes the package as deployed. This REPORT
  and `evidence/results/`, `evidence/gatelog/` and `evidence/SHA256SUMS.pscratch` were added after the jobs and are
  not package files, so `make_manifest.py --check` now lists them as additions. That is expected and not regenerated.

## 11. Limits

- K1 tests five universes; the other 182 July universes are qualified by inference from the same producer.
- K2 measures one Flux universe at two seeds. NOT RESOLVED means the effect is not resolved above trainer noise,
  not that it is zero.
- P1 has 20 replicas per arm: the median ratios carry the jackknife SE above; per-cell ratios carry ≈ 9% SE each
  (median per-cell jackknife SE 0.094 and 0.068).
- P3's comparisons have no written criterion (DESIGN §7); its cost is the measured outcome.
- Unit costs come from one 2.5-day window on shared nodes. No cause is diagnosed for their spread. Other users'
  jobs overlapped some of the nodes; that is a candidate cause, not a measured one.
  - The P1 replicas spread 3× (649–2,003 s).
  - `P1_unit` ran 1,930 s (timed out), then 715 s.
- Only u_CV's high edge carries a measured spread. u_U (one run) and u_A (two runs) do not; §7's alternatives table
  shows the effect of adding one.
- σ_ML is the pinned LightGBM seed-scan σ and is not re-measured.
- **Same-model caveat:** the executor, the director, the P1 builder and the verifier are all Claude Opus 5.5.

## 12. Independent review

One fresh read-only verifier (Claude Opus 5.5) reviewed this REPORT at `c740a9a9` in its own detached worktree
(`git-dir` ≠ `git-common-dir`), re-measuring from `sacct`, the cluster namespace, the CFS copy and git. **Verdict:
APPROVE WITH CHANGES, 3 MATERIAL, 10 MINOR.**

It confirmed the following:
- all 75 `sacct` rows, with 0 field mismatches, and the 7.2479 total;
- every gate's arithmetic and its ledger count; the repo gate logs are byte-identical to the cluster's;
- every number, verdict and sha256 in §1–§2, on the repo, pscratch and CFS copies, and the routing;
- both retries against the rule;
- the four bound digests, the deployed v1 and v2 trees against the manifest (no change after deployment), and the
  reproducible deploy tarball;
- `sha256sum -c` of the CFS copy;
- every item the grant's record row requires, including the sha correction (`git rev-parse 92b0b466`).

| finding | disposition |
|---|---|
| M1 the `P1_unit` retry (submitted 09:10:19) predates the recap record it cited (committed 09:12:19, merged 09:13:13) | §3 and §8 now give the order with times. The authorities at submission were the grant's committed "attempts" row and the director's ruling relayed at 09:09:53; the recap record confirmed the retry afterwards |
| M2 the S1–S5 basis was unstated: u_U, u_U,sel and u_A were measured at 128 shared CPUs (0.5 node billing), not on a full node; and "high edges carry the spread" overclaimed | §7 states the shared-QOS assumption and that the runs were not faster. It adds a table for regular nodes and for a × 1.85 spread on u_U and u_A. §11 limits the spread claim to u_CV |
| M3 P3's active-vs-dump difference was attributed to the input without evidence | §2 now says the 0.7–1.0 σ_ML median is the trainer-noise scale and attributes none of it to the input |
| m1 the outage window conflicted with `sacct` (jobs started at 21:08) | §3: outage 17:03–21:08; 15:48 is the last job's end |
| m2 the timeline mixed start and submit times | §3 lists submit times and says so |
| m3 "like-for-like" mislabel; uncited pre-B4 condition | §3 uses the recap record's wording and names the source (a relayed message, not a committed record) |
| m4 co-tenancy record missing; `nid004107` claim uncited | §3 gives the retry node's recorded co-tenancy and the `sacct -a -N nid004107` count |
| m5 "low edge = mean" was mislabelled; u_A's mean left out the slowest attempt | §7: the mean is called the expected cost, and u_A's mean with the re-projection (0.3491) is stated |
| m6 P1 wording ("raises σ by 3.2%", "resolved") | §2 names the statistic, calls the 2.1 SE an indication, and contrasts it with the 1.057 ratio of arm medians |
| m7 K2's resolution was not stated | §2 adds a resolution paragraph: r3 against the noise-only ≈ 0.95, and the anti-correlated seed patterns |
| m8 "first unfolded measurement" overclaimed | §2: one seed, diagnostic, no CV shift computed |
| m9 durable-copy coverage (274 files vs 270 checksummed) | header and §10 state the coverage |
| m10 the P3 re-projection basis was not shown; `P1_unit` `out/` state was not stated | §8 gives the 2,721 s `[CHECK]` mtime and the verifier's 73–79 s finalization; §3 and §8 state that `out/` was empty |

The verifier is the same model as the executor and the director, so its blind spots may be correlated with
theirs.
