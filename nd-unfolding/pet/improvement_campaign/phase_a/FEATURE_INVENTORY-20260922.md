# Phase A2, Part 3 — feature inventory for Phases C and D

What exists, in which produced file, under which exact field name, in which units, over which
population, and whether it is row-aligned with the G2 inventory. Everything below was measured by
`a2_feature_inventory.py` (this branch) running under `nd-unfolding/mnv_guarded_run.py` from a clean
checkout; the machine-readable form is `receipts/feature_inventory.json`. Column meanings are taken
from the code that WROTE each array, cited `file:line`; every cited file is byte-identical between
this branch and the comparison's pinned commit `68cf9d29` (`git rev-parse <commit>:<path>` compared
for each).

Read `DATA_AND_SCORING_RECOVERY-20260922.md` for the identity, split and selection facts this
document assumes.

## 0. The two facts that should shape Phase C before any feature is added

1. **The 12-token cap bites on 85.1 % of reco-passing events, and it throws away 39.9 % of the
   event's cluster energy on average** (mean over reco-passing events of
   `1 − sum(top-12 cluster E)/sum(all cluster E)`; 47.3 % averaged over the over-cap events alone;
   median 44.3 %, p90 74.0 %). MEASURED, from the untruncated `part_reco_E` vectors in the G2
   omnifile joined by event identity to the inventory (232,965 reco-passing rows compared;
   row alignment confirmed on 99.9966 % of them by exact top-12 energy-sum equality).
   On the truth side the same cap costs almost nothing: 1.4 % of truth-passing events exceed 12
   hadrons and 0.099 % of hadron energy is lost.
2. **Reconstructed `E_avail` is already in the inventory and is bit-identical to the 3D pipeline's
   own reconstructed `E_avail`** — so a step-1 "reco E_avail" feature does not need a new
   definition, an extraction, or a re-derivation (§2.1).

Together these say the detector-side representation is missing ~40 % of the calorimetric energy
that the analysis's own `E_avail` definition integrates over, while the summary that recovers it
is one column away. That is a Phase C hypothesis with a measured magnitude, not a guess.

## 1. Produced files inspected

| File | What it is | Rows / entries | sha256 or size |
|---|---|---|---|
| `/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz` | the G2 inventory the comparison trained on | 49,152,885 signal rows | `fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625` |
| `/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz` | identity sidecar, row-bound to the above | 49,152,885 | `01e07412b253ff496c30025cc71a9185b166a00892b1e1b4c8bce714ddd5f95c` |
| `…/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1L.root` | one G2 playlist omnifile, **untruncated** clouds | 583,219 | 1,329,986,521 B |
| `…/nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root` | the merged G2 omnifile | `mc_truth_denom` 49,906,108 | 113,496,440,965 B |
| `…/3d-unfolding/runEventLoopOmniFold_MEFHC_3D.root` | the 3D `E_avail` pipeline's own tuple | `mc_signal_reco` 32,849,103 | 2,840,567,529 B |
| `/pscratch/sd/j/josephrb/r4slim/1A_MC/*.slim.root` | `extract_r4_slim.py` output (their-arm source) | 186,439 / file, 65 branches | 138,592,663 B (sample file) |
| `/pscratch/sd/j/josephrb/theirs_inputs/1A_MC/*.theirs.npz` | `build_theirs_inputs.py` output | 186,439 / file | see §4 |
| `/pscratch/sd/j/josephrb/campaign-20260920/cache/theirs-final.npz` | the theirs-arm cache the final tasks actually read | 600,143 prior rows | see §4 |
| `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1A/MasterAnaDev_mc_AnaTuple_run00110000_Playlist.root` | a real MasterAnaDev AnaTuple, opened to READ its branch list | 186,439, 4,102 branches | 17,318,473,069 B |

The AnaTuple is the first file of `2d-unfolding/playlist_manifests/1A_MC.txt`
(41 files, sha256 `4100dca453de1beef0213a0feac1fe4faa77d769f2dd5f36f4e11c6cea4894f8`). Every branch name
in §5 was read out of that file's `MasterAnaDev` tree, not guessed.

## 2. Step-1 candidates (detector side — NO truth quantity may enter here)

### 2.1 Reconstructed `E_avail` — EXISTS, row-aligned, and is the analysis definition

| | |
|---|---|
| Field | `reco_scalars[:, 2]` in `G2_FPS_MEFHC_P12.npz` |
| Shape / dtype | `(49152885, 4)` float32; column 2 |
| Units | **GeV** |
| Population | MC signal inventory; valid on `pass_reco` rows, `-9999.0` sentinel on `!pass_reco` |
| Row-aligned | yes, with every other MC-signal member of the npz |
| Written by | `nd-unfolding/pet/dump_pointcloud_inputs.py:78` (`SIG_SCALAR_BRANCHES`), `:147-154`, `:335` |
| Source branch | `sim_eavail`, filled at `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp:1178` |

**The analysis definition, read from the source:**
`sim_eavail = CVUniverse::NewEavail()/1000` GeV, and
`NewEavail() = 1.17 × [(blob_recoil_E_tracker − tracker muon fuzz) + (blob_recoil_E_ecal − ECAL
muon fuzz)]` MeV
(`MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:185-193`, with the fuzz sum at `:168-183`;
the header states it is copied verbatim from MAT `LowRecoilPionFunctions.h`, tracker+ECAL × 1.17).

**Agreement with the 3D pipeline: MEASURED, exact.** Joining the G2 inventory's `pass_truth &
pass_reco` rows to `mc_signal_reco` in `runEventLoopOmniFold_MEFHC_3D.root` on exact float32
equality of (reco `pT`, reco `p∥`, true `pT`, true `p∥`), keeping only keys unique on both sides:
20,481,532 of 20,571,564 rows matched, and on **every** matched row the reco `E_avail` values are
bit-equal in float32 (`max_abs_difference_gev = 0.0`). The 3D pipeline reads the same `sim_eavail`
branch (`3d-unfolding/unfold_3d_omnifold_unbinned.py:228`, `:476`).

**So step 1 should use `reco_scalars[:, 2]` and nothing else needs defining.** Note it is a
*calorimetric* quantity, not the cluster-cloud sum: on the same events the whole-event cluster
energy sum correlates with it but is a different object (§2.3).

Reco `q3` is also present as `reco_scalars[:, 3]` (GeV, same population, same sentinel), from
`recoCV->RecoQ3()/1000` at `runEventLoopOmniFold.cpp:1179`.

Relation to truth, measured on the 20,571,564 `pass_truth & pass_reco` rows: Pearson
`r = 0.8666`; median `E_avail_reco / E_avail_true = 0.826` where true > 0.1 GeV; 0.0103 % of rows
have reco exactly zero and 0.0012 % negative. Quantiles (5/25/50/75/95, GeV) are
reco `[0.066, 0.316, …]` vs true `[0.040, 0.309, …]` — the full vectors are in the receipt.

### 2.2 Muon kinematics — EXISTS, row-aligned

| | |
|---|---|
| Field | `reco_muon` |
| Shape / dtype | `(49152885, 7)` float32 |
| Columns | `(px, py, pz, E, phi, q/p, minos_ok)` |
| Units | px/py/pz/E in **MeV**; `phi` rad; `q/p` 1/MeV; `minos_ok` 0/1 |
| Population | MC signal; `-9999.0` on `!pass_reco` (with `minos_ok = 0.0`) |
| Written by | `dump_pointcloud_inputs.py:73-74`, `:156-161`, `:176` (`reco_muon_row`); source `runEventLoopOmniFold.cpp:1014-1020` |

Reco muon `pT` and `p∥` are separately in `reco_scalars[:, 0]` and `[:, 1]` in **GeV** — these are
the two the loader already exposes as truth-side globals, so adding muon kinematics at step 1 means
adding the `reco_muon` block (energy scale MeV) beside them, and the unit mismatch is real: the
existing globals are GeV, `reco_muon` is MeV.

`reco_vertex` `(49152885, 3)` float32, mm, same sentinel (`dump_pointcloud_inputs.py:75`, `:163-168`).

### 2.3 Pre-truncation whole-event energy sums and multiplicities — NOT in the inventory; derivable from the G2 omnifiles

The inventory stores only the **kept** tokens:

| Field | Shape | Meaning | Units |
|---|---|---|---|
| `part_reco` | `(49152885, 12, 3)` f32 | per non-muon cluster `(E, pos, z)`, **top 12 by E, surplus DROPPED**, zero-padded | E MeV, pos mm, z mm |
| `reco_view` | `(49152885, 12)` f32 | view code 1=X 2=U 3=V, same token permutation | code |
| `reco_time` | `(49152885, 12)` f32 | cluster time, same permutation | ns |

Written by `dump_pointcloud_inputs.py:90-112` (`_pad_tokens` / `pad_reco_cloud_tokens`), `:270-285`;
clusters come from `CVUniverse.h:340-352` `GetRecoClusters` (`cluster_energy/pos/z`, filtered by
`cluster_isMuontrack == 0`) via `runEventLoopOmniFold.cpp:1007-1011`.

`_pad_tokens` sorts by energy descending (stable) and keeps `k = min(n, 12)` — **no overflow
summary of any kind is written**. Measured consequences on the inventory:

* reco tokens per event on `pass_reco` rows (20,573,521): histogram
  `[39334, 223526, 308241, 318366, 305129, 289449, 278818, 270184, 265218, 260351, 257090, 253427,
  17504388]` for 0…12 tokens → **fraction at cap 0.8508**;
* gen tokens per event on `pass_truth` rows (49,150,928): fraction at cap **0.0250**.

**Where the untruncated vectors live: the G2 omnifiles.** `part_reco_E` and `part_gen_E` in the
`mc_signal_reco` tree are the full per-event vectors that the dump truncates. Measured on one
playlist omnifile (583,219 entries; 574,504 found in the inventory by
`(mc_run, mc_subrun, mc_nthEvtInFile)`; 232,965 reco-passing rows compared):

| Quantity | Value |
|---|---|
| reco clusters per event, quantiles 50/90/99/max | 54 / 210 / … (full vector in the receipt) |
| fraction of reco-passing events over the 12-token cap | 0.8433 |
| mean fraction of cluster energy beyond the cap | **0.3992** |
| same, quantiles 50/90/99 | 0.4434 / 0.7397 / … |
| mean over over-cap events only | 0.4734 |
| gen hadrons per event, quantiles 50/90/99/max | 4 / 8 / … |
| fraction of truth events over cap | 0.0142 |
| mean fraction of hadron energy beyond cap | 0.000995 |
| row alignment: omnifile top-12 energy sum == inventory kept energy | 0.999966 |
| omnifile `sim_eavail` == inventory `reco_scalars[:,2]` | 1.000000 |

So for Phase C, **pre-truncation sums, multiplicities, overflow energy and overflow count are all
derivable for every inventory row from an already-produced file** — the G2 omnifiles, joined by
`(mc_run, mc_subrun, mc_nthEvtInFile)` — with no AnaTuple re-extraction. The merged omnifile
`runEventLoopOmniFold_G2_FPS_MEFHC.root` covers the whole inventory (`mc_truth_denom` 49,906,108
entries against 49,152,885 inventory rows; the merged file also carries `mc_signal_reco`,
`mc_background` and `data` trees). What does **not** exist is a produced *summary* array: the
derivation is a scan of the omnifile's jagged branches, which is a CPU extraction job, not a read.

Calorimetric recoil is a different, cheaper route to the same information and is *not* in the
inventory either — see §4 (the theirs-arm globals already carry `MasterAnaDev_hadron_recoil`) and
§5 (the AnaTuple branches).

## 3. Step-2 candidates (truth side — true `E_avail` is legitimate here)

| Field | Shape | Columns | Units | Population |
|---|---|---|---|---|
| `truth_scalars` | `(49152885, 4)` f32 | `(MC, MC_pz, MC_eavail, MC_q3)` = true muon `pT`, true muon `p∥`, **true `E_avail`**, true `q3` | GeV | truth denominator; valid where `pass_truth` |
| `part_gen` | `(49152885, 12, 5)` f32 | truth FS hadrons `(E, px, py, pz, pdg)`, muon and neutrinos removed, top-12 by E, surplus dropped | E/p MeV, raw PDG | `pass_truth` |

`truth_scalars` written by `dump_pointcloud_inputs.py:79`, `:339`; sources
`runEventLoopOmniFold.cpp:589-590` (`GetEAvailableTrue` at `CVUniverse.h:361-374`, `Getq3True`).
`part_gen` written by `dump_pointcloud_inputs.py:114-116`, `:336-338`; hadrons from
`CVUniverse.h:289-304` `GetTruthFSHadrons` (`mc_FSPart*`).

**True `E_avail` (`truth_scalars[:, 2]`) and true `q3` (`truth_scalars[:, 3]`) therefore need no
extraction at all** — they are already row-aligned in the inventory, and the loader deliberately
leaves them unused (the scope document's §Phase C names this as a design choice to test). Note
that `truth_scalars[:, 2]` is *also* the quantity the closure injects the tilt into, so a step-2
feature arm that adds true `E_avail` is adding the injected coordinate itself: that is legitimate
for the simulation-truth classifier, but it makes the step-2 arm's learnability trivially higher
and must not be read as a detector-level recovery result.

## 4. The theirs-arm products (already-produced, and what they carry that we do not)

`build_theirs_inputs.py` shards, one per AnaTuple file
(`/pscratch/sd/j/josephrb/theirs_inputs/1A_MC/*.theirs.npz`):

| Member | Shape (per shard) | dtype |
|---|---|---|
| `tokens` | `(186439, 33, 5)` | float32 |
| `add_info` | `(186439, 33, 5)` | float32 |
| `globals` | `(186439, 16)` | float32 |
| `identity` | `(186439, 3)` | int64 — `(mc_run, mc_subrun, mc_nthEvtInFile)` |

`join_theirs_to_inventory.py` produces `campaign-20260920/join/join_sig.npz`
(`row_index`, `origin`) mapping every inventory row to a shard row by identity; the final tasks
read the gathered cache `campaign-20260920/cache/theirs-final.npz`.

The 16 `globals` columns, measured on the cache's 251,109 reco-passing half-B rows, with each
column's Pearson correlation against the inventory's reco `E_avail` on the same rows:

| # | Column | Pearson vs reco `E_avail` | median |
|---:|---|---:|---:|
| 0 | `log muon_fuzz_energy` | 0.329 | 2.837 |
| 1 | `log muon_iso_blobs_energy` | −0.015 | −11.513 |
| 2 | `log hadron_recoil` | 0.637 | 7.483 |
| 3 | `log passive_id` | 0.687 | −2.678 |
| 4 | `log passive_od` | 0.274 | −5.863 |
| 5 | `log passive_sum` | 0.640 | −2.461 |
| 6 | `improved_nmichel` | 0.215 | 0.0 |
| 7 | `muon_present` | undefined (constant 1.0 on these rows) | 1.0 |
| 8 | `diphoton_mass` | 0.477 | 0.0 |
| 9 | `charged_pion_prongs` | 0.166 | 1.0 |
| 10 | `log sumE pid2 blob` | 0.379 | 5.119 |
| 11 | `log sumE pid3 prong3` | −0.257 | 8.514 |
| 12 | `log sumE pid4 prong8` | 0.007 | 7.000 |
| 13 | `log sumE pid5 prong13` | undefined (constant) | −6.908 |
| 14 | `log sumE pid6 agg-blob` | 0.671 | −6.908 |
| 15 | `log sumE pid7 agg-prong` | 0.560 | −6.908 |

Two "undefined" entries are constant columns on this population, not failures to compute.

On the **raw** (pre-log) scale, `MasterAnaDev_hadron_recoil` correlates with reco `E_avail` at
`r = 0.8558`, with median ratio 2242.8 MeV per GeV of `E_avail`. **`hadron_recoil` is NOT the
analysis's `E_avail` definition** — it is the calorimetric recoil, a different MAT quantity — so a
Phase C step-1 arm should use `reco_scalars[:, 2]`, and may use `hadron_recoil` as an *additional*
feature, never as a substitute.

His columns 14/15 are the **energy-preserving overflow treatment we lack**: when his per-event
object count exceeds his cap, the surplus is summed into aggregate tokens with PID codes 6 (blob)
and 7 (prong) and their energies also appear in these two globals. Our dump drops the surplus
outright. That is a concrete, already-implemented reference design for the "energy-preserving
overflow treatment" ablation.

These globals exist for **every joined signal row** via `join_sig.npz`, not only the cache's rows.

## 5. What would need a new extraction, and the branches that would supply it

Read out of a real MasterAnaDev AnaTuple (`…run00110000_Playlist.root`, `MasterAnaDev` tree,
186,439 entries, 4,102 branches). Present = the branch name was found in that tree's branch list.

Inputs to the analysis `E_avail` definition — all present:

| Branch | Type | Present |
|---|---|---|
| `blob_recoil_E_tracker` | double | yes |
| `blob_recoil_E_ecal` | double | yes |
| `muon_fuzz_per_plane_r80_planeIDs` | int32_t[] | yes |
| `muon_fuzz_per_plane_r80_energies` | double[] | yes |
| `muon_fuzz_per_plane_r80_planeIDs_sz` | int32_t | yes |

Pre-truncation clusters, calorimetric recoil and truth final state — all present:

| Branch | Type | Present |
|---|---|---|
| `cluster_energy`, `cluster_pos`, `cluster_z`, `cluster_view`, `cluster_time` | jagged | yes |
| `cluster_isMuontrack` | jagged | yes |
| `MasterAnaDev_recoil_E` | double | yes |
| `MasterAnaDev_hadron_recoil` | double | yes |
| `mc_nFSPart`, `mc_FSPartE`, `mc_FSPartPDG` | int32_t / double[] / int32_t[] | yes |

The same 13 names are present in the Data AnaTuple
(`…/Data/Playlist1A/MasterAnaDev_data_AnaTuple_run00006038_Playlist.root`, `MasterAnaDev` tree) —
**branch names only were read there; no data value was read and no data statistic is recorded
anywhere in this task.**

**The R4 slim extraction does not carry them.** `extract_r4_slim.py`'s output has 65 branches and
its `clusters_pre_truncation` and `analysis_reco_eavail_inputs` families are **empty**: it kept
blobs (`MasterAnaDev_Blob*`), prongs (`prong_part_*`, `prong_dEdXMean`), michel
(`improved_nmichel`), muon fuzz / iso / passive totals and `MasterAnaDev_hadron_recoil`, but no
`cluster_*` and no `blob_recoil_E_tracker` / `blob_recoil_E_ecal`. So any Phase C arm that wants
cluster-level pre-truncation information from the AnaTuples needs a **new** extraction manifest —
and per the authorization, that manifest must be committed before the extraction runs.

Ranking the three routes to pre-truncation reco energy, cheapest first:

1. **G2 omnifiles** (`part_reco_E` etc.) — already produced, covers the whole inventory, joins by
   identity, needs only a scan. Gives exact sums/multiplicities/overflow for the tokens the dump
   truncated. **Recommended.**
2. **theirs-arm globals** — already produced and already joined, gives calorimetric recoil and
   per-PID energy sums including the overflow aggregates, but on his object vocabulary, not ours.
3. **New AnaTuple extraction** — needed only for cluster-level quantities the omnifiles do not
   already carry, or for the `E_avail` ingredients separately (tracker vs ECAL vs fuzz), which the
   inventory already gives combined.

## 6. Phase D event budget

| Population | Rows |
|---|---|
| G2 signal inventory rows (= distinct events, see §7) | 49,152,885 |
| truth denominator, `pass_truth` | 49,150,928 |
| reco-selected, `pass_reco` | 20,573,521 |
| both | 20,571,564 |
| merged G2 omnifile `mc_truth_denom` entries | 49,906,108 |

What the comparison used:

| | Rows |
|---|---|
| loader subsample (`default_rng(0).choice(N, 2e6)`) | 2,000,000 — **4.069 %** of the inventory |
| final stage of that subsample | 1,200,286 |
| each half | 600,143 |
| half A, truth-passing (the score's target) | 600,130 |
| half B, truth-passing (the score's prior/unfolded) | 600,111 |
| step-1 pseudodata rows (half A, `pass_reco & pass_truth`) | 250,501 |

The stage hash is per event, so applying the committed `stage_splits.assign` to the **whole**
inventory leaves the historical membership of the 2 M subsampled rows unchanged and extends it:

| Stage | Rows (whole inventory) | of which `pass_truth` |
|---|---:|---:|
| tuning | 9,829,737 | 9,829,376 |
| pilot | 9,829,681 | 9,829,272 |
| final | 29,493,467 | 29,492,280 |

Final-stage rows outside the historical 2 M subsample: **28,293,181**.

Fully independent, identity-disjoint draws of *pairs of halves* (a draw needs 2 × size, one half A
and one half B), by floor division:

| Half size | Pairs, whole inventory | Pairs inside the `final` partition | Pairs inside `final`, excluding the historical subsample |
|---:|---:|---:|---:|
| 100,000 | 245 | 147 | 141 |
| 300,000 | 81 | 49 | 47 |
| **600,143** (the historical size) | **40** | **24** | **23** |
| 1,000,000 | 24 | 14 | 14 |
| 2,000,000 | 12 | 7 | 7 |
| 5,000,000 | 4 | 2 | 2 |

The right column is the one Phase D should size against if it wants draws that are both disjoint
from each other *and* untouched by the historical campaign: **23 independent 600 k-per-half draws,
or 7 at 2 M per half.** The middle column is the one to use if only the tuning/pilot/final
separation must be respected.

Caveats on these counts, both of which matter:

* they are *row*-disjointness counts, which equal identity-disjointness only because inventory rows
  are unique events — measured, see `DATA_AND_SCORING_RECOVERY-20260922.md` §2.2;
* they count the truth-denominator population. A draw's usable step-1 pseudodata is smaller by the
  reco acceptance: the historical draw turned 600,143 half-A rows into 250,501 step-1 rows
  (41.7 %). Size Phase D on whichever leg binds.

## 7. Population and alignment summary

Every MC-signal member listed above is row-aligned with every other over the 49,152,885 inventory
rows: `part_reco`, `reco_scalars`, `reco_muon`, `reco_vertex`, `reco_view`, `reco_time`,
`part_gen`, `truth_scalars`, `pass_reco`, `pass_truth`, `w_truth`, `w_reco`, and the identity
sidecar's `sig_event_id` / `sig_event_source` / `sig_event_occurrence` / `sig_event_key`.

Separate, NOT row-aligned with the signal block: the MC background block
(`bkg_part_reco`, `bkg_reco_scalars`, `bkg_muon`, `bkg_vertex`, `bkg_view`, `bkg_time`, `w_bkg`,
`bkg_indices`, `bkg_nuPDG`, `bkg_current`, `bkg_inttype`), 564,591 rows.

Real-data members (`measured_pc`, `measured_scalars`, `data_muon`, `data_vertex`, `data_view`,
`data_time`, `data_pot`, `data_identity_hash`) exist in the npz. **They were not read and no
statistic of them is recorded in this task or its receipts.** The comparison ran `bkg_mode`
`mc-only` with `measured_leg_is_real_data: false`.

Scalars: `edges_0`, `edges_1` (the 15 × 19 = 285 reporting cells), `petSchemaVersion`,
`hasFullEventSchema`, `fullPhaseSpace`, `estimator_fingerprint`, `mc_pot`, `pot_scale`,
`num_part` (= 12), `sig_identity_hash`, `bkg_identity_hash`.
