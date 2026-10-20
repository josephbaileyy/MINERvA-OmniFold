# MP-2 S0 and S1: the aligned final-state dump and the descriptive separability probe

**By** the measurement session, 2026-10-20, under BINDING-PHASE1-20261019 §2, which grants S0 and S1 only. The
director accepted both by message on 2026-10-20. The coordinating session wrote this file from the agent's report.

**CITABLE FOR:**
- S1's bitwise admission: final-state particles aligned to the s5p MCgen rows;
- S0's descriptive separability numbers.

**NOT CITABLE FOR:**
- any reweighter, any Δ_hyb, or anything in J cells, none of which was computed;
- any claim.

S2 and S3 wait for the feature contract ([`FEATURE-CONTRACT-DRAFT.md`](FEATURE-CONTRACT-DRAFT.md)), which the director
reviews.

## S1: aligned dump, ADMITTED bitwise

- **First attempt, and the fix.** Job 60034379 failed on a script bug. `of_inputs_5d.npz` (2026-06-27) was written by
  an older producer (21f2a003) that stores non-finite truth as −9999.0. The dump's cast now applies that same
  NaN → −9999.0 mapping before the float32 cast; 2,801 rows are affected (1,327 NaN q3, 1,474 NaN W).
  - The comparison stays bitwise against MCgen; nothing was relaxed. The director ruled it fine.
  - The first attempt is kept in `attempt1/`.
- **C1, admission.** The G2 `mc_signal_reco` rows inside the kinematic truth phase space, in playlist order 1A…1P,
  equal MCgen **bitwise for all 32,849,103 rows and all 5 columns**. w_truth is bitwise too, and every row is
  truth-passing. The source tree is `mc_signal_reco`, not `mc_truth_denom`.
- **C2, join.** Every row joins to its MasterAnaDev Truth entry. The 133 duplicate keys, all in 1E, are identical. The
  truth muon equals the rotated MAD lepton to 1.5e-11 MeV.
- **C3, particle content.** E_avail recomputed from the dumped `mc_FSPart` list with MAT's `GetEAvailableTrue` equals
  the stored `MC_eavail` bitwise on every row.
- **Targets.** C 30,028,386, H 1,632,529, others (O, N, Al, Si, Cl, Ti) 1,188,188 including 174 with Z = 0.
- **Output.** 12 per-playlist npz files, 13 GB, at `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp2/s1/`. They
  hold 178,060,474 particles, ragged by offsets, in MCgen order. Receipt `s1_receipt.json` (sha256 `d240b41a…`);
  per-file sha256 in `s1_npz_sha256.txt`.

## S0: descriptive probe (Tune v1 truth against NuWro C12 truth)

- **Samples.**
  - Tune v1: a seeded 2M-row subsample of the S1 rows, in-grid, 0.5 ≤ Eν ≤ 50 GeV, with hydrogen excluded on the Tune
    side only.
  - NuWro: all 1,261,997 in-grid C12 events, weighted e.weight × r(Eν). Control N0 rebuilds the frozen NuWro product
    bitwise; N1 confirms row alignment.
- **Model.** LightGBM, settings declared in `measurement-paper/phase1/mp2/mp2_s0_declaration.json` (sha256 `6ded06da…`).
  The declaration was amended after a smoke test and before any real fit (patience 50 → 200; class weights to mean 1),
  and the director accepted it.

| fit | AUC test | AUC gap vs NuWro split | ESS / ESS(w_truth) | ESS / N | max w / ⟨w⟩ | Var log w, total (share within fine cells) |
|---|---:|---:|---:|---:|---:|---:|
| Tune vs NuWro, 5 scalars | 0.649 | +0.151 | 0.63 | 0.54 | 311 | 0.292 (64%) |
| Tune vs NuWro, full features | 0.777 | **+0.275** | **0.116** | 0.10 | **1700** | 1.43 (**82%**) |
| NuWro vs NuWro split, scalars / full | 0.498 / 0.502 | — | 1.00 | 0.26 | 1.05 | ≈ 0 |
| Tune vs Tune split, scalars / full | 0.500 / 0.500 | — | 1.00 | 0.85 | 1.1–1.25 | ≈ 0 |

**Reading (descriptive).**
- The full final state carries substantially more Tune-vs-NuWro information than the five scalars, and most of the
  log-weight variance lies within fine 5D cells. That is structure the fine-grid hybrid cannot carry.
- The raw full-feature weights are heavy-tailed. Against the drafted V4 (ESS ≥ 0.3 N, max weight ≤ 50) they would fail
  both bounds, and the 5-scalar weights would fail the maximum-weight bound. The director ruled that V4 is not loosened
  because of this.

**Caveats.**
- Other nuclei remain on the Tune side (3.8% of the rows).
- The 5-scalar fit mixes W conventions (MP-5 (b)).
- The split controls stop after 1–19 iterations.
- The NuWro 50–100 GeV supplement is not used.
- Particle harmonization is untested.

## Jobs and charge

| job | QOS | State | Exit | ElapsedRaw | billing | CPU node-h |
|---|---|---|---|---:|---:|---:|
| 60034379 | shared | FAILED (script bug) | 3:0 | 74 | 32 | 0.002569 |
| 60045652 (S1) | debug | COMPLETED | 0:0 | 230 | 256 | 0.063889 |
| 60045657 (S0) | debug | COMPLETED | 0:0 | 129 | 256 | 0.035833 |

Total 0.102 CPU node-h; 0 GPU; nothing written to CFS.

**Held out of git:** the S0 receipts `s0_features.json` (sha256 `d070e12c02127800fc28084afcbde3e449a387539aa1dab2871250156bfabb41`) and `s0_fit.json` (sha256 `618823cb125155f928ebf23b5e293255b34601e3a21d701da86b7b43c1659791`).
They cite the 570 MB cluster-only feature arrays `s0_tune.npz` and `s0_nuwro.npz`
(`/pscratch/sd/j/josephrb/measurement-paper/phase1/mp2/s0/features/`) by bare name, and `verify_receipt_artifacts.py`
classifies those as MISSING before it consults off-area directories (the same question as MP-5's two receipts). Both receipts
are kept on pscratch and in the session worktree, and the table above restates their numbers.

**Code:** `measurement-paper/phase1/mp2/` (`mp2_s1_dump.py`, `mp2_s0_features.py`, `mp2_s0_fit.py`,
`mp2_s0_declaration.json`, `mp2_job.sh`).
