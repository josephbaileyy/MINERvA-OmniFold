# MP1-A step S0: report

The agent wrote this report; the coordinating session reviewed it before commit (2026-10-20).

**By** the measurement session, under [`BINDING-PHASE1-ADDENDUM-2.md`](../../BINDING-PHASE1-ADDENDUM-2.md) (R1–R5,
origin/main `46d1ec5a`).

## G0, recorded 2026-10-19 22:25 UTC, before any ±1σ pass was submitted

**G0: PASS.** Receipts: `receipts/G0_1A.json`, `receipts/F_1A.txt`, `receipts/s0_g0_run.txt`.

- **The table.** F was tabulated by `measurement-paper/phase1/mp1/s0_g0_ftable.py` from the training file
  (1A MC `run00110000`). It used all 42,436 selected-like events with pc, q0 > 0.
  - The result is a monotone polyline with 12 segments and 13 knots, covering pc from 0 to 54,483 MeV.
  - Each segment's points lie on its fitted line to ≤ 1.7e-14 relative.
  - The segment slopes are 1.499557, 1.60678, 1.614205, 1.540229, 1.520889, 1.530447, 1.530537, 1.51581,
    1.486447, 1.504665, 1.516825 and 1.51324.
  - The first knot is (0, 3.9e-14).
  - Table sha256 `61f4dd82…`; on the cluster it is `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s0/g0/F_1A.txt`.
- **Held-out check.** On the held-out file, 1A MC `run00110001`, there are 42,298 selected-like events with
  pc, q0 > 0.
  - max |F(pc) − q0|/q0 = 2.1e-14 (p99 1.5e-15), and no event exceeds 1e-4.
  - No held-out event lies beyond the training range.
- **Descriptive, not part of the gate.** On all held-out events with pc, q0 > 0 (131,860, with no selection),
  8,305 (6.3%) are off F by more than 1e-4, with a maximum of 0.26. Only the selected-like population is on F.
- **Convention, therefore.** The ±1σ passes use R1's F-propagation in the form q0' = q0 + F(pc + k·pc_s) − F(pc).
  - On G0's population, q0 = F(pc) to 2e-14, so this equals R1's q0' = F(pc + k·pc_s).
  - Off that population, the form applies F's local response and leaves q0's own offset unchanged.
  - The fractional fallback is not needed.

## G1, evaluated 2026-10-20 07:53 UTC: **PASS**, primary and secondary (`receipts/checks/g1_*.json`)

**Jobs.**
- 60017651 `mp1s0_base_cv`: the unmodified binary, md5 `a6b85ec3…`.
- 60017653 `mp1s0_zero`: the species binary, md5 `15b4789f…`, with `SpeciesResponse_zero:0`, `fprop`, `prorata`,
  and F table `61f4dd82…`.
- Both are COMPLETED 0:0, full 1A (41 MC and 253 data files), built from the same source and libraries.
- The zero pass loaded the 13-knot table and built every band; its migration census was 0 entrants and 0 exits.

**Primary, `equal base_cv zero`: PASS.** Every scalar branch of every tree is identical: `mc_signal_reco`
2,682,267, `mc_truth_denom` 2,682,267, `mc_background` 52,626 and `data` 360,123 entries. This holds with both
readers (below).

**Secondary, `equal` W2b `rrzero_1A` vs zero: PASS**, with the same entry counts.

**A reader defect in `publication/w2/compare_omnifiles.py`** (found here).
- The long 1A outputs carry a stale autosave cycle next to the final one: `mc_signal_reco;9` (2,682,267 entries) and
  `;8` (2,489,136); `mc_truth_denom;5` (2,682,267) and `;4` (2,217,328).
- The W2 reader walks `GetListOfKeys()` and keeps the last key per name, which is the lower, stale cycle (verified
  with ROOT on `rrzero_1A`).
- So its PASS (`g1_*_w2comparer.json`) covers only the stale cycles: 2,489,136 and 2,217,328 entries.
- `measurement-paper/phase1/mp1/omnifile_io.py` applies the same W2 `equal` rule to each tree's highest cycle
  (`g1_*_latest.json`), and G1 is decided on that.
- W2's earlier passing-row checks are unaffected in count: the stale cycle already held all 1,736,833 passing signal
  rows, as the W2a report shows.
- The species checker and the J-cell readout use the latest cycle.

## R4 event-level check (report only): CV-selected subsets **identical** (`receipts/checks/r4_*.json`)

- **Comparison.** `s0_r4_event_check.py` compares the full-universe production file
  `nd-unfolding/runEventLoopOmniFold_5D_1A_universes_full_bkgaware.root` (latest cycles) with this S0's `base_cv`,
  and with W2b's `rrzero_1A`.
  - `mc_signal_reco`: 2,682,267 entries each.
  - CV-pass rows: 1,736,833 each, identical in file order and as a multiset over all 15 CV columns.
  - Non-pass rows: 945,434 each.
  - `mc_background`: 52,626 pass rows each, identical.
  - `mc_truth_denom`: 2,682,267 each.
- **Correction of S0-PREP §6 and of what was reported to the director.** The entry-count difference (2,679,264 /
  39,870 against 2,489,136 / 52,626) was this session's error. It came from reading stale, lower TTree cycles
  (production `mc_signal_reco;224`, `mc_background;2`), not the final ones.
  - The W2a review's "entry counts are equal in all four trees" (`REVIEW-20261006-w2a-independent.md:16-19`) is
    **correct**.
  - R4's proposed sentence, that the review "compared another pair", therefore does **not** apply.
  - R4's premise, that the named G1 reference has a different event set, is withdrawn. The production file's CV
    columns equal the lateral-only pass. Under `equal` it would differ only by its extra per-universe branches (454
    in `mc_signal_reco`); that comparison was not run.

## W2-STALE-CYCLE-RECHECK (director's grant; report only, 0 node-h, login node, existing files)

**The defect.** `publication/w2/compare_omnifiles.py:40-55` iterates `GetListOfKeys()` and keeps the last key per
name. ROOT lists the higher cycle first, so on a file with an autosave cycle the comparer reads the stale lower one
(verified with ROOT on `rrzero_1A`).

**Re-check.** `omnifile_io.py` applies the same `equal` and `shifted` rules, reusing `cmd_equal` and `cmd_shifted`
unchanged, to each tree's highest cycle. Results are in `receipts/checks/w2recheck/`.

| W2 check (receipt) | pair | cycles W2 read → latest (entries) | latest-cycle verdict |
|---|---|---|---|
| W2a no-op (`checks/noop.json`) | smoke `base_cv` vs `mod_cv` | single cycle ;1 in every tree (131,346 / 131,346 / 2,616 / 15,055) | **PASS** (same as W2) |
| W2a identity lateral, δ = 0 (`checks/rrzero.json`) | smoke `base_cv` vs `mod_rrzero` | single cycle ;1 | **PASS** (same) |
| W2a negative control (`NEG_equal_shift.json`) | smoke `base_cv` vs `mod_rr1`, `equal` | single cycle ;1 | **FAIL**, as required (same) |
| W2a ±4% (`rr0.json`, `rr1.json`), `shifted` | smoke | single cycle ;1 | **PASS**: 85,166 signal and 2,616 background rows; q0 rows 83,873 / 83,911 (same) |
| W2a wrong scale (`NEG_wrongscale.json`) | smoke, s = 1.0 | single cycle ;1 | **FAIL**, as required (same) |
| W2a full 1A (`full1A_rr1_vs_rr0.json`), `shifted` s = 1.0833 | cost1A `mod_rr0` vs `mod_rr1` | W2 read `mc_signal_reco;8` (2,489,136) and `mc_truth_denom;4` (2,217,328) → latest `;9` (2,682,267) and `;5` (2,682,267); `mc_background;1` (52,626) and `data;1` (360,123) single | **PASS** with identical statistics: 1,736,833 passing signal rows (1,710,436 q0-checked), 52,626 background rows (50,913) |
| W2b δ = 0 | — | W2b ran **no** omnifile `equal`; its δ = 0 control is at the unfolded-product level (`W2B-REPORT:71-75`) and is not a cycle reader | — |
| W2b `rrzero_1A` vs this S0's `base_cv` (new; also G1 secondary) | `equal` | W2's reader would see ;8/;4 (2,489,136 / 2,217,328) → latest ;9/;5 (2,682,267) | **PASS** |

**What it means for W2.**
- The stale cycles hold every CV-passing row (1,736,833: the same count is found in both cycles). The rows they lack
  are the last 193,131 signal-tree rows and 464,939 truth-tree rows; the signal-tree ones are all non-passing rows.
- So every W2 passing-row check stands. The W2a full-1A PASS did not cover the tail rows. On the latest cycles it
  still PASSes.
- The independent W2a review's "entry counts are equal in all four trees" used another reader. It agrees with the
  latest cycles.

**Other readers in the repository.** A read-only audit by a subagent covered all tracked
.py/.C/.cxx/.cpp/.h/.sh files, excluding vendored MAT. Bare-name `uproot.open(p)[name]` and ROOT `Get(name)` are
safe: both return the highest cycle.

| file:line | reads | rule | could read a stale cycle? |
|---|---|---|---|
| `publication/w2/compare_omnifiles.py:40-55` | omnifile TTrees | last key per name | **YES**, measured above; outcome unchanged |
| `docs/orchestration/state/2d-closeout/stageD-inputs/evidence/omni_branches.py:6-9` | production 2D omnifile `2d-unfolding/runEventLoopOmniFold_MEFHC.root` | last key per name (`entries`) | in principle; **not in fact**, because that file has one cycle per tree (`receipts/checks/w2recheck/flagged_files_cycles.txt`), so the committed 32,849,103 is right |
| `nd-unfolding/pet/improvement_campaign/phase_a/a2_feature_inventory.py:151` (called at :409, :431, :432) | G2 merged omnifile, anatuple, R4 slim file | uproot `{k.split(";")[0]: f[k]}`, last wins | in principle; **not in fact for the G2 merged file** (single cycle; the committed 49,906,108 is right). The anatuple and slim-file rows were not checked |
| `docs/orchestration/state/2d-closeout/stageB/evidence/b-flux/ls_branches.py:3-5` | omnifile | prints every cycle | diagnostic; no committed output |
| `reproduction/s5p/repro_s5p.py:1246`; `nd-unfolding/mii_anchor_comparator.py:399`; `next-preparation-20261009/sb1-prep/sb1_verify.py:200`, `tests/test_sb1_guarded.py:93`; `next-preparation-20261009/structure/checks/equivalence.py:165`; `2d-closeout/stageB/evidence/b-genie-truth/read_sweeps.py:52`, `read_adopted_cov.py:9`; `2d-unfolding/tests/test_selective_io.py:590` | histogram and covariance files | last key per name | low risk (files written once). Not checked file by file |
| `docs/orchestration/runs/clausec-rerun-20260821/harness/mutate.py:69-104` | copies keys in list order | — | low risk; on a two-cycle source it would make the stale copy the output's highest cycle |
| `2d-unfolding/uq/plot_uncertainty_fig6_7_style.py:148`; `docs/sep-09-presentation/ai-research-talk/plot_uncertainty_sources.py:84`; `nd-unfolding/adopt_active_lateral_fps.py:94`; `2d-closeout/stageB/evidence/verify-c04/verify_c04.py:238-247` | covariance rollups | sum inside a per-key loop | low risk; a double count on a two-cycle file, not a stale read |
| `MINERvA-101-Cross-Section/runEventLoop*.cpp` (e.g. `runEventLoopOmniFold.cpp:1640`) and roughly 40 other scripts | tree names, or data via bare-name `Get`/`TChain` | — | safe or names-only |

- The audit also notes that `docs/orchestration/state/uncertainty-preparation-20261008/e/review.md:229` cleared
  `compare_omnifiles.py:40` on reasoning that does not hold for two cycles.
- No W2 file, KNOWN_ISSUES row or reader was edited. This session's S0 tools read the latest cycle.
- This session's own S0-PREP §6 error came from the same pattern, in an ad hoc uproot dict built from
  `classnames()`.

## ±1σ passes: reco-level J-cell shifts (`receipts/checks/jcell_shifts_6pass.json`, `jcell_shifts_xtalk.json`)

**Readout.** `s0_jcell_shifts.py` uses the s5p fine grid and the partition-J map, imported from
`nd-unfolding/s5p_stage1_inspect.py` with the s5c contract's 109 supported cells.
- It takes reco (pT, p∥, E_avail, q3, W) on passing rows, and weights signal by `w_reco` and background by `w_bkg`.
- Per cell it reports rel = N_pass/N_zero − 1. The control is `zero.root`.
- This is a reco-level description before any unfolding, **not** an unfolded J-cell number.
- Control rows: 1,789,459 passing, of which 10,887 fall outside the grid (including the 20 with E_avail < 0) and
  7,167 fall in unreported cells.
- The total reported yield moves by +0.003% to +0.005% (migration only). `base_cv` against `zero` gives 0 in every
  cell.

| pass (q0 F-prop) | median \|rel\| | max \|rel\| (cell) | range | cells > 1% / > 5% | L2 over 109 |
|---|---:|---:|---|---:|---:|
| **proton +1σ, pro-rata (primary)** | 1.03% | 5.22% (72) | −5.22% … +3.09% | 57 / 1 | 0.175 |
| proton, fuzz none (R2) | 1.21% | 5.30% (72) | −5.30% … +3.29% | 65 / 2 | |
| proton, fuzz all (R2) | 0.98% | 5.15% (72) | −5.15% … +3.00% | 54 / 1 | |
| **meson +1σ, pro-rata (primary)** | 1.35% | 5.15% (83) | −5.15% … +5.12% | 72 / 2 | 0.198 |
| meson, fuzz none (R2) | 1.54% | 8.98% (10) | −5.60% … +8.98% | 80 / 4 | |
| meson, fuzz all (R2) | 1.37% | 4.90% (83) | −4.90% … +3.66% | 73 / 0 | |
| cross-talk +1σ (20%), pro-rata (R3 variant) | 0.37% | 1.98% (96) | −1.86% … +1.98% | 11 / 0 | 0.064 |

- **R2 extremes against the primary.**
  - Proton: none − primary has max 1.67% and median 0.20% (L2 0.044); all − primary has max 3.63% and median 0.24%
    (L2 0.061).
  - Meson: none − primary has max 3.86% and median 0.37% (L2 0.087); all − primary has max 4.77% and median 0.37%
    (L2 0.082).
  - The primary lies between the two extremes in 108 of 109 cells, for each species.
  - The fuzz's species split is **not known**. The extremes bound it descriptively; they are not a band.
- **R3.** Cross-talk is **out** of the primary band, per MAT's "DO NOT USE". With it at 20%, its shift is about a third
  of the proton or meson shifts in L2.
- The proton and meson cell patterns are partly correlated (r = 0.52).
- G3 (linearity) needs the −1σ passes and the unfolds of S1. No −1σ pass was run at S0.

**Species-pass checks** (`check_species_pass.py` against zero; `receipts/checks/species_*.json`).
- In all seven passes, every unshifted branch and the whole data tree are identical, and the pass flags are
  identical.
- The q0 shift never has the wrong sign.
- Under F-propagation, |Δq0| reaches 1.067·δ_s·q0 (proton) and 1.066 (meson). That is F's local slope over the
  secant: 9,087 and 5,600 signal rows. It is reported only; the bound is enforced only for fractional.
- Fraction of passing signal rows whose E_avail moved: proton 0.78 (0.65 under fuzz all), meson 0.62 (0.55),
  cross-talk 0.99.
- The pro-rata passes, including cross-talk, return FAIL only on the sign rule: 9+2, 5+2 and 14+4 rows. Every such
  row has NewEavail < 0. There are 16 signal and 4 background passing rows with E_avail < 0, where the fuzz exceeds
  the blob energy.
  - R2's formula E·(1 + δ·E_s/raw) moves them away from zero. That is the formula as ruled, and the checker's sign
    rule assumed E ≥ 0.
  - Those rows lie outside the J grid (E_avail < 0), so they do not enter the J-cell readout.
  - Under fuzz none or all, |ΔE| exceeds δ·E on 88,142 (proton) and 90,122 (meson) signal rows under none, as
    expected when E_s·1.17 exceeds the fuzz-subtracted sum. Under all it never does.

## Timing, memory, charge (`receipts/s0_w2_1A_sacct.txt`; sacct below)

| job | pass | ElapsedRaw s | TotalCPU | MaxRSS (batch) | node-h |
|---|---|---:|---:|---:|---:|
| 60017651 | base_cv | 1,598 | 20:50 | 16,749,132K | 0.01734 |
| 60017653 | zero | 1,609 | 22:17 | 16,749,120K | 0.01746 |
| 60017710 | proton +1σ pro-rata | 4,450 | 51:38 | 16,749,140K | 0.04829 |
| 60017711 | meson +1σ pro-rata | 6,366 | 68:18 | 16,749,136K | 0.06908 |
| 60017712 | proton +1σ none | 5,547 | 63:09 | 16,749,112K | 0.06019 |
| 60017713 | proton +1σ all | 3,203 | 38:15 | 16,749,128K | 0.03475 |
| 60017715 | meson +1σ none | 5,562 | 58:50 | 16,749,148K | 0.06035 |
| 60017716 | meson +1σ all | 4,673 | 47:11 | 16,749,100K | 0.05071 |
| 60017717 | cross-talk +1σ pro-rata | 6,686 | 77:31 | 16,749,104K | 0.07255 |
| **total** | 9 passes | 39,694 | | | **0.4307** |

- All jobs: QOS shared, `-A m3246`, billing 10, AllocTRES `billing=10,cpu=10,mem=16G,node=1`, COMPLETED 0:0.
- **W2's 1A passes** (same loop, same input, no point clouds) took 2,247–4,842 s, with TotalCPU 30–50 min and
  MaxRSS 16,746,024–16,749,400K.
- The δ = 0 pair ran faster than any W2 pass: 1,598 and 1,609 s.
- The species passes took 3,203–6,686 s, which is 2.0–4.2× the δ = 0 pair and up to 1.4× W2's longest.
  - The likely cause is the ~25 extra tuple branches read per event at k ≠ 0 (`part_response_*`, `blob_*`,
    fuzz). At k = 0 these reads are short-circuited.
  - This is not separated from node contention: the passes ran concurrently on shared.
- The cross-talk pass finished 214 s inside its 6,900 s limit. **For S1, give 1A species passes at least 2.5 h.**
  Other playlists scale by input bytes (W2A §4).
- MaxRSS sits at the 16G cap in every pass, W2's included. It counts page cache (W2 review F8), so it does not
  measure headroom; every pass completed inside its 16G cgroup.
- **Charge:** 0.4307 CPU node-h, 0 GPU node-h, against the 1.5 node-h S0 budget and the phase-1 ceiling.
  - Ledger rows are in `LEDGER-rows-mp1-s0.tsv`, in `phase1/LEDGER.tsv` columns, for the director to merge.
  - Storage: 9 omnifiles of about 0.40 GB each, under `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s0/`.
    Nothing was written to CFS.

## Builds and files

- **Build.** `build_mp1_s0.sh` ran on login04 at 2026-10-19 22:19 UTC from deploy `DEPLOY.sha256` `28098176…`. The
  files are not committed, so their digests stand in for a commit.
  - Canonical inputs were pinned.
  - Base md5 `a6b85ec3…`; mod md5 `15b4789f…`.
  - Base equals canonical; mod differs only by the header and the patch.
  - The manifest is `s0/build/MANIFEST.sha256` (108 lines).
- **Analysis tools.** They are deployed under `s0/tools`, `TOOLS.sha256` `ed1f7748…`.
- **Launcher.** The fixed launcher (a work directory per process) is in `s0/tools` only. The queued jobs ran the
  build-deploy copy, and each had its own job id.

## UNCONFIRMED

1. **G0** covers 1A, one training file and one held-out file, on selected-like events: tuple θ and qp stand in for
   MAT's getters. 6.3% of unselected events are off F. The universe's difference form applies F's local response
   there, and its use on rows outside G0's population is not validated.
2. **The fuzz species split is unknown.** The R2 extremes are descriptive bounds only.
3. **Speed.** The species-pass slowdown is attributed to the extra branch reads without a measurement separating it
   from contention.
4. **Linearity (G3)** and the −1σ endpoints are untested at S0.
5. **Reco level only.** The readout is reco-level: no unfold, no null calibration and no J-cell number.
6. **The stale-cycle audit** is by pattern. The flagged readers' other input files (the anatuple and the R4 slim file
   in `a2_feature_inventory.py`) were not checked for multiple cycles.
