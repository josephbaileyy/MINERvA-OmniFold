# 2D closeout Stage D preparation: the independent inputs, where they could come from, and their price

**CITABLE FOR:**
- the inventory of the three independent inputs that
  [`PLAN-20261011-2d-closeout.md`](../../../PLAN-20261011-2d-closeout.md) §4 Stage D items 1–3 requires, with
  each input's availability, source, production law, price basis and dependencies, as measured on 2026-10-14;
- the event-identity key of the MC AnaTuples, and its measured uniqueness and reco → `Truth` join on four real
  files (§4.2);
- the measured reuse of overlaid data gates between MC events (§4.4), a dependence channel for any split of
  the one MC production;
- the measured unit costs that a Stage D price can be built from (§3), and the projections built from them;
- the per-input outcomes (PRICED, UNPRICED or UNAVAILABLE) and the overall outcome in §1;
- the questions recorded for Joseph in §10.

**NOT CITABLE FOR:**
- any cross section, uncertainty, covariance, coverage, calibration or bias result. A construction or a
  conditional-width result is not coverage evidence, and nothing here is a pass;
- a fit judgement. Whether a price fits the delegation ceiling is the director's call (scope amendment 1);
- a compute grant, a request for authorization, a recipe change or a KI-85 lift;
- a statement that a projection is a price. Every projection in §3 and §8 is labelled, and its unmeasured
  parts are named;
- any message to MINERvA, to an external author or to a coauthor. §10 records questions only;
- the Stage C pilot's results. The pilot is running; its own REPORT governs it.

| field | content |
|---|---|
| `Owner` | Stage D preparation lane (read-only): a Claude Opus 5.5 (`claude-opus-5-5`) subagent of Claude Code session `minerva-omnifold-ed` did the inventory and wrote this text; that session committed it |
| `Authority` | Joseph, in session `minerva-omnifold-ed` on 2026-10-14, answering that session's offer of a read-only Stage D inventory lane: *"yes you can start it"*. That instruction is the only authority, and it covers a read-only inventory. The director (paper-tighten lane) accepted the lane as scoped and sent six scope amendments, which this report follows (§0). This report grants nothing |
| `Branch` / `Base` | `prep/stage-d-inputs-20261014` / `origin/main` `4c742f35f8905f4fd2ef883d772cbe675b14e3ce` (re-fetched 2026-10-14T07:1xZ; unchanged) |
| `Decision` | For each required Stage D input: does it exist or can it be obtained, from whom, by what production law, at what measured or projected cost, and with what dependencies? |
| `Terminal outcomes` | Per input and overall: **PRICED** (with basis), **UNPRICED** (with the measurement that would price it), **UNAVAILABLE** (with the acquisition route). Amended from the brief's A/B/C by the director |
| `Compute` | **No Slurm job; 0 charged node-h.** Login-node reads on Perlmutter `login29` only (ROOT 6.28/12 under `root_6_28`, Python 3.11.14). Nothing was written on the cluster outside `/tmp` of the ssh session (no files; the probes print to stdout) |
| `Reviewer` | One fresh read-only verifier (a Claude Opus 5.5 subagent in a separate detached worktree at `d534b7ea`): **PASS WITH CHANGES**, with 2 MATERIAL, 12 MINOR and 5 COSMETIC findings. All of them are applied in this revision, each re-checked against its source before applying ([`verification/VERIFICATION.md`](verification/VERIFICATION.md)). A focused re-review of the repair follows. The director reviews before merge |
| `Interference` | None with the director or the 2d closer: no Stage C file, pilot path or job was read for writing, and nothing was submitted, cancelled or modified |

`E` = [`evidence/`](evidence/) (the probe scripts, their raw outputs, the `sacct` snapshot and the remote-read log).
Repository citations are `path:line` at `4c742f35` unless stated.

## 0. Scope amendments applied

The director's amendments, received during the work, override the matching parts of the brief:

1. **Price, not a fit verdict.** Measured jobs are priced as `ElapsedRaw × billing / 256 / 3600` with their JobIDs;
   reservations as cap × billing; anything resting on unmeasured parts is a **PROJECTION**. Outcomes are
   PRICED / UNPRICED / UNAVAILABLE. No fit is computed.
2. **Measure, don't inherit.** "No feasible route with current inputs" is tested against files and sources in §9,
   not quoted.
3. **Event identity** is defined as a key and tested on real AnaTuples (§4.1–4.2).
4. **Custodians** are named per assessment sample (§7). Where a person or the collaboration must hold a sample, it
   is a question for Joseph (§10), with no draft message.
5. **Independent generators** are located by `ls -d`, CFS first (§6.1).
6. **Mechanics.** This report gets a `CATALOG.md` row, a `MANIFEST-overrides.tsv` LIVE row and a regenerated
   `MANIFEST.tsv`. No `sbatch` or `salloc`. A probe that needs compute is a priced request, not a run.

## 1. Answer

**Overall: UNAVAILABLE.** Two of the three inputs cannot be produced inside this project with the samples that
exist. The third (the nuisance generator) is unbuilt and unpriced, and its physical-adequacy evidence is
unavailable. The decision therefore goes to Joseph as the plan's §6 two-outcome decision: keep the full endpoint
open while the inputs below are acquired, or separately adopt narrower conditional or convention claims.

| Stage D input | outcome | one-line reason |
|---|---|---|
| **1. Fresh identity-carrying MC banks** (or a validated generative law) | **UNAVAILABLE** at production size | The project holds one ME-FHC MC production (489 AnaTuples), and all 489 feed the 2D production. The AnaTuples do carry an event key, measured unique and joinable (§4.2). So an identity-carrying rebuild (R0) needs no new events. But no identity-only event-loop mode exists (§4.3), so R0 is **UNPRICED**, and so are the disjoint **sub-production** folds that would follow it (§4.5). Those folds are at most half size, and they share overlaid data gates (inferred from the branch values, §4.4). A second production must come from MINERvA (§10 Q1), or possibly from the current open-data release, whose relation to ours is unknown (Q2). A generative law is UNPRICED |
| **2. Validated continuous nuisance generator** | **UNPRICED** (generator); **UNAVAILABLE** (physical adequacy) | No code draws a continuous lateral shift. The event loop can only re-run an existing ±1σ universe (`runEventLoopOmniFold.cpp:1764-1844`). Background, flux and correlation laws exist only as the MAT discrete universes. Building a generator is method development. Its adequacy cannot come from pseudo-data drawn from the same law; that evidence would be external (Q5) |
| **3. Untouched truth/response departures, with independent-generator evidence** | **UNAVAILABLE** (independent response); **UNPRICED** (explicitly limited alternative) | Every independent-generator sample is truth-only. NuWro and GiBUU are on C12, not CH, and all four samples have already been inspected against our unfolded results. No detector-simulated alternative-generator sample exists (MINERvA, Q4). The limited alternative is a fresh GENIE v3 configuration on CH as a truth reweight under the nominal response. It is partial evidence, and GENIE v3 generation throughput is unmeasured |
| Independent custodian | **UNAVAILABLE** inside the lanes | Every lane runs as the one cluster account `josephrb`, so no lane can hold a sample the others cannot read. A person or the collaboration must hold it (Q3) |
| Affordable interval-validation method | **UNPRICED** | No cheaper interval method has equivalence evidence. Repriced with today's measured unit costs, the nested design still projects to about 1.8–2.6 × 10⁵ node-h at 5,000 experiments (§8). The fixed-band test's unfolds are cheap, but its populations are missing and it answers a narrower question |

## 2. Ceiling and charges, as measured (no fit is computed)

| quantity | value | basis |
|---|---|---|
| delegation ceiling | ≤ 700 charged CPU node-h on m3246, all stage grants together | [`AUTHORIZATION-20261012-2d-closeout-delegation.md`](../../../AUTHORIZATION-20261012-2d-closeout-delegation.md) §3.2 |
| committed grant ceilings | **26.0**: Stages A–B 2.0, flux repair 1.0, Stage B diagnostics 3.0 (the P4 retry record leaves it unchanged), Stage C pilot 20.0 | re-read from the committed grants: `AUTHORIZATION-20261012-2d-closeout-stageAB.md:26`, `…-fluxrepair.md:45`, `…-stageB-diagnostics.md:27`, `…-stageB-p4-retry.md:67`, `AUTHORIZATION-20261013-2d-closeout-stageC-pilot-recap.md:70-74`. The exit record and both binding addenda raise no ceiling. **This agrees with the director's 26.0/700.** Uncommitted headroom: 700 − 26.0 = 674.0, before Stage C production, which is unpriced |
| charged to date, `2dc_*` | **3.6267 node-h**: `2dc_B4` 0.5290 (20 rows), `2dc_B5` 0.7233 (6 rows), `2dc_C` 2.3743 (74 rows: 23 COMPLETED, 1 TIMEOUT, **50 PENDING**) | MEASURED: `sacct -u josephrb -X -S 2026-10-10T00:00:00` at 2026-10-14T07:21:20Z, exit 0, 119 job rows (plus a header and a timestamp line); [`E/sacct_josephrb_since_20261010.txt`](evidence/sacct_josephrb_since_20261010.txt). No `2dc_AB_*` or `2dc_C04_*` row exists. The pilot is in flight, so this figure is moving |
| m3246 CPU pool (context only, not a ceiling or a reservation) | 17,193.7 of 20,000 charged: **2,806.3 node-h left for all users**; `josephrb` 2,043.0 of a 10,000 user allocation | MEASURED: `iris`, 2026-10-14T07:28:47Z ([`E/remote_reads_20261014.txt`](evidence/remote_reads_20261014.txt)). Lane B's 2026-10-09 reading was 16,959.4 charged |
| CFS m3246 (context for any new bank) | 83,496 of 102,400 GB used (81 %) | MEASURED: `prjquota m3246`, same log. Our own CFS usage was 2,512 GiB on 2026-10-09 against a 3 TB rule (`docs/publication/corrections-20261008/RECORD-20261009-anatuple-data-cfs-copy.md:58-60`); not re-measured |

## 3. Per-unfold and per-event-loop cost basis

All MEASURED rows are `ElapsedRaw × billing / 921,600`. The pilot rows are committed on `main` only where the
recap record quotes them. The P1 replica rows come from this lane's own `sacct` read. The pilot is not terminal,
and its REPORT is not on `origin/main`.

| workload | node-h per unit | n | JobIDs / source | class |
|---|---:|---:|---|---|
| CV central unfold, current producer, 64 CPUs shared | 0.0649 | 1 | `59733771` `P0_default`, 935 s × 64 (recap record `:24`) | MEASURED, committed |
| CV unfold, derived (selective-I/O) path, 64 CPUs | 0.1007 | 1 | `59733772`, 1,450 s × 64 (recap `:25`; the director reads the 1.55× as node contention) | MEASURED, committed |
| universe unfold, derived path, 128 CPUs | 0.1189–0.1619 | 4 | `59734955`, `59734956`, `59734957`, `59734959` (recap `:26-29`) | MEASURED, committed |
| universe unfold, default path, 128 CPUs | 0.3468 | 1 | `59734961` (recap `:30`) | MEASURED, committed |
| three-stream statistical replica, seed 42, 64 CPUs | **0.0464–0.0688**, mean 0.0571 | 12 | `59753253`–`59753261`, `59753263`–`59753265` (668–991 s, billing 64) | MEASURED by this lane; **pilot not terminal**, not on `origin/main` |
| unit-factor replica (b ≡ 1) | 0.0497 | 1 | `59740518`, 715 s × 64 | MEASURED by this lane, same caveat |
| VL170 bootstrap replica, 64 CPUs | 0.0591 | 300 | ki84 `59410433` (`ASSESSMENT-20261008-2d-total-uncertainty-feasibility.md:258-263`) | MEASURED, historical |
| **12-playlist CV event loop** (production CV configuration, census-patched binary; outputs identical to the May per-playlist files on common branches) | **0.4302** for all 12 playlists; longest job 18,227 s (1M) | 12 | P4: `59717845_0`, `59713345_1`, `59713348_2`, `59717848_3`, `59717850_4`, `59717852_5`, `59717855_6`, `59713360_7`, `59717856_8`, `59717858_9`, `59713364_10`, `59713365_11` (99,108 s × billing 4); [`../stageB/diagnostics/REPORT.md`](../stageB/diagnostics/REPORT.md) §2, §5 | MEASURED, committed |
| exact-GBT central | about 19 h on a full node | — | `ASSESSMENT-20261008-…:274` | DOCUMENTED, not a receipt |
| GENIE v2.12 truth generation | 2M events, 8 parallel gevgen × 250k, "~9 min on a 256-core node" | — | `3d-unfolding/genie/README.md:97-98` | DOCUMENTED, not a receipt |
| NuWro 21.09 truth generation (C12) | 2M events, 8 × 250k in parallel, "~5 min" | — | `3d-unfolding/genie/README.md:129` | DOCUMENTED, not a receipt |
| GENIE v2 / NuWro, single process on a login node | gevgen 4 min per 100k events; NuWro 2 min | — | `state/s5p/gen5d/README-gen5d-fluxfix.md:189-190` | DOCUMENTED, not a receipt |

The P4 row is the first measured price for a full CV event loop over the 2D input set. It ran without the identity
or point-cloud dump, so the dump I/O is not in it.

## 4. Input 1: fresh MC banks that carry event identity

### 4.1 What "carries event identity" means here

A bank carries event identity when every row of every MC tree it contributes (signal reco rows, truth-only miss
rows, the efficiency denominator and the background template) carries the key

`K = (mc_run, mc_subrun, mc_nthEvtInFile)`,

with these properties:
- `K` is unique per generated event after the known exact double-fill is removed. That double-fill is MC playlist
  1E, `run00111353`, which the event loop already de-duplicates;
- every reco row's `K` is found in the `Truth` tree (a reco → truth injection);
- the signal and denominator trees of a derived omnifile are a bijection on `K`.

`source` (the playlist) is informative, not required, because MC run ranges are disjoint between playlists
(`nd-unfolding/pet/EVENT_IDENTITY_JOIN_CONTRACT.md:254-266`). `mc_nthEvtInFile` alone is not a key: it is an
index within one generator subrun.

**Data are different.** `(ev_run, ev_subrun, ev_gate)` is a DAQ gate key, not an event key. In the G2 data tree,
212,677 gate keys repeat with differing kinematics (`EVENT_IDENTITY_JOIN_CONTRACT.md:268-275`). Data enter no
role in this report.

### 4.2 Measured on real AnaTuples (read-only, 2026-10-14, `login29`)

Script [`E/identity_probe.py`](evidence/identity_probe.py) reads only the integer identity branches of both trees.
Outputs: [`E/identity_probe_1A-110001.out`](evidence/identity_probe_1A-110001.out) and
[`E/identity_probe_1E-1M-1P.out`](evidence/identity_probe_1E-1M-1P.out); both runs exit 0.

| file (`MC/StandardMC/…`) | reco rows (`MasterAnaDev`) | `Truth` rows | duplicate `K`, reco / truth | reco `K` found in `Truth` | subruns | truth `K` with no reco row |
|---|---:|---:|---|---:|---:|---:|
| `Playlist1A/…run00110001…` | 186,557 | 544,499 | 0 / 0 | 186,557 of 186,557 | 500 | 357,942 |
| `Playlist1E/…run00111353…` | 184,992 | 549,196 | **111 / 1,102**, max multiplicity 2 | 184,881 of 184,881 unique | 496 | 363,213 |
| `Playlist1M/…run00113020…` | 175,721 | 547,846 | 0 / 0 | 175,721 of 175,721 | 487 | 372,125 |
| `Playlist1P/…run00112000…` | 169,086 | 549,315 | 0 / 0 | 169,086 of 169,086 | 481 | 380,229 |

- **The 1E duplicates are one double-filled subrun.** [`E/dup_probe.py`](evidence/dup_probe.py) →
  [`E/dup_probe_1E-111353.out`](evidence/dup_probe_1E-111353.out): every duplicate is in subrun 489. All 1,102
  `Truth` pairs and all 111 reco pairs are identical on 11 branches (`mc_incomingE`, `mc_Q2`, `mc_w`,
  `mc_intType`, `mc_current`, `mc_incoming`, `mc_targetZ`, `mc_nthEvtInSpill`, `ev_gate`, `ev_subrun`,
  `ev_run`). So the remedy is the existing de-duplication, not more identity.
- In 1,963 of the 1,964 subruns, the truth `K` set is contiguous from 0. The exception is the double-filled 1E subrun.
- **Scope.** Four of 489 files, in four of 12 playlists. The G2 audit measured the same key unique on all 12
  playlists of a *derived* full-phase-space omnifile (49,906,108 rows), with the signal ↔ denominator bijection on
  12/12 playlists (`EVENT_IDENTITY_JOIN_CONTRACT.md:254-266, 285-293`). The verifier re-measured the key with its
  own probe on three further playlists: 1L `run00113003`, 1N `run00113275` and 1B `run00111005`. Each had 0 duplicates,
  and every reco key was found in `Truth` ([`verification/VERIFICATION.md`](verification/VERIFICATION.md)). A census of all 489 source files has not been run (§11).

### 4.3 The production 2D omnifile carries no identity (re-measured)

[`E/omni_branches.py`](evidence/omni_branches.py) →
[`E/omni_branches_production_2d.out`](evidence/omni_branches_production_2d.out):
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC.root` (2,144,008,221 B, mtime
2026-05-18) has `mc_truth_denom` {MC, MC_pz, w_truth}, `mc_signal_reco` {sim, sim_pz, sim_pass, w_reco, MC, MC_pz,
w_truth}, `mc_background` {sim_background, sim_background_pz, sim_background_pass, w_bkg} and `data` {measured,
measured_pz, measured_pass}. No tree has an identity branch. This reproduces lane B's 2026-10-09 reading
(`state/uncertainty-preparation-20261008/b/populations.tsv`). The event loop writes `mc_run`, `mc_subrun` and
`mc_nthEvtInFile` only under `MNV101_DUMP_POINTCLOUD`, at all four write sites (`runEventLoopOmniFold.cpp`):
`:450, 460-474` (truth denominator), `:753, 787-789` (misses), `:985, 1001-1035` (signal, which also writes
`part_*`, `mu_*` and `vtx_*`) and `:1346, 1390-1392` (background). `EVENT_IDENTITY_JOIN_CONTRACT.md` §6 says the same.

**So identity is lost in our omnifile; it is present in the source.** An identity-carrying rebuild (R0) needs
no new information from the source. **But no identity-only mode exists at `4c742f35`.** R0 therefore needs one of two things:
- a producer change that adds an identity-only flag. That is a new producer revision, so it needs the plan's
  equivalence bridge;
- the point-cloud mode. The repository's one identity-carrying omnifile written in that mode,
  `nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root`
  (`state/uncertainty-preparation-20261008/b/populations.tsv:10`), is 113,496,440,965 B, about 53× the production file
  ([`E/remote_reads_repair_20261014.txt`](evidence/remote_reads_repair_20261014.txt)). Its selection also differs.

### 4.4 Overlaid data gates are shared between MC events (new measurement; the reading is inferred from values)

In MC, `(ev_run, ev_subrun, ev_gate)` takes data-run values. In 1A, `ev_run` spans 6,038–10,066, the 1A data run
range ([`E/overlay_probe_1A-110001.out`](evidence/overlay_probe_1A-110001.out)). This is consistent with the
identity of the data gate overlaid for pile-up. The reading rests on the values only; MINERvA's documentation of
these branches was not checked. The reco tree also carries overlay-fraction branches (`fracOverlay`,
`overlayEnergyInfo`, …). The verifier found three supporting observations, none of them documentation:
- the MC `ev_run` ranges match the data manifests: 1A data `run00006038`–`run00010066` and 1E data
  `run00016003`–`run00016522` (`2d-unfolding/playlist_manifests/1A_Data.txt`, `1E_Data.txt`);
- all 37,277 shared gates in 1A `run00110001` link events from distinct MC subruns, with `mc_nthEvtInSpill` = 0
  throughout, which is reuse across generator jobs, not same-spill multiplicity;
- the official MAD tuple documentation has no `ev_*` or overlay rows, so documentation cannot settle the reading
  ([`verification/VERIFICATION.md`](verification/VERIFICATION.md)).

[`E/overlay_reuse.py`](evidence/overlay_reuse.py) → [`E/overlay_reuse.out`](evidence/overlay_reuse.out) (after the
1E de-duplication):

| file | MC events | distinct overlay gates | events on a gate shared with another MC event | gates shared across different MC subruns | max events per gate |
|---|---:|---:|---:|---:|---:|
| 1A `run00110001` | 544,499 | 505,173 | 76,603 (14.1 %) | 37,277 | 5 |
| 1A `run00110002` | 544,097 | 507,222 | 71,962 (13.2 %) | 35,087 | 5 |
| 1E `run00111353` | 548,094 | 512,457 | 69,936 (12.8 %) | 34,299 | 5 |

The two 1A files share **66,657** overlay gates. 1A and 1E share **0**, because their data run ranges are
disjoint. Lane B recorded overlay dependence as "untestable here" because our omnifile holds no overlay identity
(`DESIGN-20261008-2d-independent-statistical-validation.md:216-219`). The AnaTuples hold it, so it can now be
tested:
- **Within a playlist, any split by event, subrun or file shares overlaid readouts between folds.** Its effect on
  muon kinematics is unmeasured.
- An overlay-disjoint split needs connected components of the (MC event, overlay gate) graph within each playlist.
  Whether those components percolate into one per playlist is unmeasured. If they do, the only overlay-disjoint
  unit is the playlist, and playlists are not exchangeable: they have different beam and detector periods.

### 4.5 Routes, laws, prices and dependencies

| sub-input | exists? | source / holder | production law | price | outcome | dependencies |
|---|---|---|---|---|---|---|
| **R0**: identity-carrying CV rebuild of the 12-playlist 2D omnifile | can be made | this project, from the 489 AnaTuples on `/pscratch` | same binary, inputs and environment, plus the identity branches; the R0 equality test of lane B §4 (every shared column equal row by row to `43f8cc16…`) | **UNPRICED.** Reference projection only: the MEASURED P4 CV unit 0.4302 node-h (§3), run with no identity or point-cloud I/O. It is **not a lower bound**: P4 used a census-patched binary on shared nodes, and the pilot records a 1.55× contention spread. Measurement that would price it: one 1L run in the chosen identity mode under `sacct`, against `59713360_7` (856 s) | **UNPRICED** | the AnaTuples' durability (§4.6). **No identity-only mode exists** (§4.3), so R0 needs either a producer change, with the plan's equivalence bridge, or the point-cloud mode, whose output is about 53× larger and so is constrained by the CFS 3 TB rule. P4's census patch is not in production |
| R0 with universe columns | can be made | same | as above, under `MNV101_DUMP_UNIVERSES` | FORECAST 2.8–27.0 node-h, billing ASSUMED (`ASSESSMENT-20261008-…:313`) | **UNPRICED** | measurement: one playlist in universe-dump mode with identity, under `sacct` |
| Disjoint sub-production folds (development / calibration / assessment) | can be made after R0 | this project | hash fold of `K` (lane B §4), with overlay-aware grouping (§4.4) | split manifest: no Slurm. Overlay-component census over 489 `Truth` trees: login-node reads only. PROJECTION ≈ 15–45 login-minutes, from the verifier's measured 2.1–5.5 s per file for the integer branches (1B, 1L, 1N; [`verification/VERIFICATION.md`](verification/VERIFICATION.md)); no Slurm | **UNPRICED** (it depends on R0) | **Explicitly limited.** A fold of fraction f trains at MC/data 4.708 f (2.35 at f = ½; `DESIGN-20261008-…:240-246`). The production-size bin-mapper and row-sample variability is not reached without an independently established scaling (plan §4 Stage D). The folds share overlaid gates within a playlist |
| **Fresh production-size identity-carrying bank(s)** | **no** | not held. 489 of 489 MC AnaTuples are in the 2D manifest (`2d-unfolding/playlist_manifests/MEFHC_MC.txt`, 489 lines; cluster count 489, [`E/remote_reads_20261014.txt`](evidence/remote_reads_20261014.txt)). No other production-size ME-FHC MC AnaTuple set exists on our `/pscratch` or at the top level of m3246 CFS ([`E/remote_reads_repair_20261014.txt`](evidence/remote_reads_repair_20261014.txt)). A top-level scan cannot see inside member directories. `gregork/Minerva/20260326/{1A,1B}/` holds 41 + 11 per-file `.pb` conversions of ME-FHC MC AnaTuples with our 1A and 1B filenames (15 G + 4.0 G, group `m3246`), of unknown release. They are derived files covering 2 of 12 playlists, so they are not a fresh bank, but they bear on Q2 | MINERvA GENIE + Geant4 + overlay + reconstruction production; or a re-generated open-data release | not priceable by this project | **UNAVAILABLE** | Q1 (MINERvA) and Q2 (whether the current open-data release is a new generation). A bank larger than ours is also constrained by the CFS 3 TB rule (§2) |
| Generative law (route G): truth from a generator plus a validated smearing/efficiency law | no | — | undeveloped (`DESIGN-20261008-…:494`) | no unit cost exists | **UNPRICED** | method development; a validity criterion independent of the bank it is fitted on |
| Reference-truth error | — | — | for a reservoir fold of fraction ρ, the reference offset τ² ≤ 1/(4.708 ρ) in data-stream variance units (`DESIGN-20261008-…:258-280`) | arithmetic | — | the per-bin ESS and smearing share are unmeasured (lane B §18) |
| Calibration bank | no | — | would be a further fold, or a second production | — | **UNAVAILABLE** at production size | as above |

### 4.6 A dependency of every route above: the MC AnaTuples are only on `/pscratch`

The 489 MC AnaTuples (9.6 TiB by `du -sh` today, [`E/remote_reads_repair_20261014.txt`](evidence/remote_reads_repair_20261014.txt), the same quantity as the 10.53 TB of the 2026-10-08
inventory in decimal units) exist only under
`/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/`. The CFS preservation copy holds data, flux and
parameter files only. Its `MC/` path does not exist ([`E/remote_reads_20261014.txt`](evidence/remote_reads_20261014.txt)). The 2026-10-09 record leaves the simulation copy
to Joseph's unsent drafts A and B (`RECORD-20261009-anatuple-data-cfs-copy.md` §3). They are an *earlier*
open-data production: current public files of the same names are 1.243–1.244 × larger, so a re-download does not
reproduce our inputs (`docs/OPEN_ITEMS.md:185`, OI-55).

## 5. Input 2: a validated continuous nuisance generator

| component | what exists (measured or cited) | missing | outcome |
|---|---|---|---|
| Selection-changing laterals (muon energy scale MINOS/MINERvA, resolution, beam angle X/Y) | 10 discrete ±1σ active-mode universes, merged files on CFS (`/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-inputs-20261012/active_universe_5d_standard_merged/`, 21 entries). `MNV101_ACTIVE_UNIVERSE` resolves an existing `band:idx` and refuses anything else (`runEventLoopOmniFold.cpp:1764-1844`). The universes come from `GetStandardSystematics` (`:1785`) | a draw at an arbitrary shift. Two routes: (a) one event loop per draw, PROJECTION ≈ 0.43 node-h per draw at the P4 unit, before the code exists; (b) an analysis-level generator from a per-event dump. Stage B finds that the muon enters the cuts only through `MaxMuonAngle(20°)` (`stageB/REPORT.md` §2.7), so energy-scale and resolution shifts change selection only through the reco window, and beam-angle shifts through the angle cut. Route (b) needs code and a closure against the 10 active universes | **UNPRICED** (method development; first measurement: closure of a per-event re-selection against the 10 existing active universes) |
| Varied backgrounds | the July sweep varies the background in 185 of 187 universes (`stageB/REPORT.md` §2.6), as ±1σ (or 2p2h 3-point) per-event weights | a continuous law between and beyond the stored points (interpolation is an assumption, not a law) | **UNPRICED** |
| Coherent flux normalization | 100 PPFX universes with MAT ν-e+IMD constraint weights, n_eff 19.1 (`stageB/REPORT.md` §3, C04; KI 95) | none for a discrete-resampling law; a continuous law would need PPFX itself | discrete law **exists**; continuous **UNPRICED** |
| Dependence structure | flux × muon energy enters in-band, through the MINOS universes' correlated flux (KI 96; `stageB/REPORT.md` §2.3) | joint draws across bands, beyond the per-band universe pairing | **UNPRICED** |
| **Physical adequacy of the law** | none. Pseudo-data drawn from the MAT universe law cannot establish that law (plan §4 Stage D item 2) | external evidence: MINERvA's own validation of its systematic prescriptions, or an independent constraint | **UNAVAILABLE** inside the project (Q5) |

**Overall input 2: UNPRICED** for the generator, **UNAVAILABLE** for its adequacy. Its dependencies are R0 (the
generator's draws need event-level identity to be paired with a fold) and the 10 active-mode files.

## 6. Input 3: untouched truth/response departures and independent-generator evidence

### 6.1 Independent-generator samples that physically exist (`ls -d`, CFS first, 2026-10-14)

- **CFS:** `/global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006/gen5d` and `…/gen5d_fluxfix` exist: binned 5D
  products, which include each prediction's own `sumw2`. Per `state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt`
  the event files there are the 50–100 GeV supplements for GENIE CV, GENIE+MEC and NuWro
  (`gen5d_fluxfix/supp/{genie_cv,genie_mec,nuwro}/`, including `supp/nuwro/nuwro_supp.root` and
  `nuwro_supp_flat5d.root`) and the `supp/timing/{genie,nuwro}/` timing samples.
  The top level of `/global/cfs/cdirs/m3246/` holds 99 directories and 7 other entries. None of them is a
  neutrino-generator or AnaTuple directory. The generator-like names are Herwig7, Sherpa and Geant4 builds, and
  none of those is a neutrino generator ([`E/remote_reads_repair_20261014.txt`](evidence/remote_reads_repair_20261014.txt)). Member directories were searched only at their second level, for MINERvA-named
  directories. That search found `gregork/Minerva` (§4.5).
- **`/pscratch` only** (`/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie/`; 12 G in all, [`E/remote_reads_repair_20261014.txt`](evidence/remote_reads_repair_20261014.txt)):

| sample | generator, version, configuration | target | flux | file(s) present | form | inspected already? |
|---|---|---|---|---|---|---|
| GENIE CV | GENIE `v2_12_10c`, splines `DefaultPlusValenciaMEC`; the CV event list contains zero MEC events (`docs/research/MINERVA-MODEL-IMPROVEMENT-MEMO-20261011.md:31`) | CH (C12/H1 0.9225/0.0775) | ME FHC νμ, reweighted per event to the analysis flux | `genie_mefhc_cv_ALL.gst.root` (999,514,329 B) + `work_seed1..10/` | truth gst | **yes**: 3D χ² and 5D s5p tests |
| GENIE + MEC | same install, `Default+CCMEC` (Valencia 2011, no MINERvA enhancement) | CH | same | `genie_mefhc_mec_ALL.gst.root` (997,606,940 B) + `work_mecseed1001..1008/` | truth gst | **yes** |
| NuWro | 21.09 (`v21_09_1`), CC QEL/RES/DIS/COH/MEC, defaults otherwise | **C12** | 0.5–50 GeV + 50–100 supplement | `work_nuwro_p1..p8/nuwro_pN.root` (8 × ≈ 310 MB) | truth | **yes** |
| GiBUU | 2019, ME-FHC jobcard | **C12** | **no events above 20 GeV** (KI 82) | `work_gibuu_arr/task1..80/FinalEvents.dat` (80 of 80; 2.0 GB) | truth | **yes** |

Effective sample sizes in the 5D grid are 281,530 (GENIE CV), 286,981 (MEC) and 345,893 (NuWro)
(`state/s5p/gen5d/README-gen5d-fluxfix.md:158-159`). The 2D paper ancillary in the repository carries only the
MINERvA Tune v1 prediction (`2d-unfolding/minerva_paper_anc/`; `2d-unfolding/compare_to_models.py:5`). Tune v1 is
our prior, not an independent generator. NEUT is "not openly available" (`3d-unfolding/genie/README.md:234-235`).

**None of these is fresh.** All four were compared with our 3D and 5D results (`3d-unfolding/genie/README.md:144-198`;
`docs/analysis-note/paper_body.tex:410-460`). The 2D measurement is the E_avail marginal of the 3D result, so a 2D
projection of these samples is a projection of an inspected sample.

### 6.2 Routes, laws, prices and dependencies

| sub-input | exists? | source | production law | price | outcome | dependencies |
|---|---|---|---|---|---|---|
| **Independent generator with MINERvA detector response** (a reco-level alternative truth) | **no** | MINERvA only: "MINERvA simulation not available in this environment" (`state/valencia-feasibility-20261011/REPORT.md:268`) | generator + MINERvA Geant4 + overlay + reconstruction + AnaTuple | not priceable here | **UNAVAILABLE** | Q4 |
| **Explicitly limited alternative**: a fresh, uninspected truth-level configuration on CH, applied as a truth reweight of the existing MC (nominal response) | software exists: GENIE v3 builds on CVMFS (`/cvmfs/larsoft.opensciencegrid.org/products/genie/`, up to `v3_06_02_sbn4`, built `Linux64bit+3.10-2.17`). Splines exist for G18_10a_02_11b and AR23_20i (`state/inelastic-high-region-20261011/REPORT.md:1034`). NuWro `v21_09_1` is also on CVMFS | this project (generation); configuration chosen by the custodian (§7) | GENIE v3 on CH with the analysis flux, as in the 3D samples; reweight on a declared truth-variable set | generation: FORECAST 1.5–15 core-h per 1M + 0.1M configuration at an **assumed** 5–50 ms/event (`inelastic-high-region-20261011/REPORT.md:754`). GENIE v3 throughput is unmeasured, and so is whether the v3 builds run here. The SL7 UPS workaround is documented to run the CVMFS GENIE v2 and NuWro `v21_09_1` builds on Perlmutter (`3d-unfolding/genie/README.md:116-118`). GENIE v2 gevgen took 4 min per 100k events on a login node (`state/s5p/gen5d/README-gen5d-fluxfix.md:189-190`). Neither result establishes anything about v3. Measurement: a 10⁴-event pilot (≤ 0.2 core-h). The reweight unfolds are ≈ 0.065 node-h each at the P0 unit, but the departure design that fixes their number is not frozen | **UNPRICED** | partial evidence only: one response (plan §4 Stage D item 3). Truth-variable set for the reweight; finite-sample error of the prediction (`sumw2`, as the s5p products record); matched target (CH), phase space and flux; Q3 (custodian) |
| CH NuWro or GiBUU | NuWro software exists and is documented to run here (`3d-unfolding/genie/README.md:116-118`); no CH sample | this project | NuWro on CH; GiBUU needs a build (not on CVMFS: `products/gibuu` absent, [`E/remote_reads_repair_20261014.txt`](evidence/remote_reads_repair_20261014.txt)) | PROJECTION basis only: NuWro took 2 min per 100k events single-process on a login node on C12 (`README-gen5d-fluxfix.md:189-190`, documented, not a receipt). A CH run is unmeasured | **UNPRICED** | The design record names a CH NuWro or GiBUU sample as "where fresh production would buy something", for the C-versus-CH target asymmetry (`DESIGN-20260911-endpoint-B-generator-comparison-test.md:243-250`). The inspected C12 NuWro sample uses the same generator physics. Whether a CH run of an inspected generator counts as fresh for Stage D is not established here |
| Truth warps of the current bank | can be made | this project | pre-registered warps, never used in development | ≈ 1 unfold per case at the measured unit; the design is not frozen | **UNPRICED** | same-generator-family; partial evidence only |

## 7. Independent custodians

| assessment sample | who would hold it | why independent | outcome |
|---|---|---|---|
| Assessment fold(s) of an R0 split, and the fold salt | **not any lane.** Every lane runs as Unix user `josephrb`. Every file on `/pscratch` and CFS under that account is readable by every lane, and the CFS preservation copies are group `josephrb` (`RECORD-20261009-anatuple-data-cfs-copy.md:66-69`). The project records the one-account practice at `FINDINGS.md:158` (BEN-533), `PLAYBOOK.md:26` (PB-18) and `REVIEW-CONTRACT-20260822-k0-execution-integrity.md:1017` ("every leg runs as the same user"). The other lanes' `sb1`, `xr` and `xrl` jobs appear in the same `sacct -u josephrb`. A code-enforced seal binds only cooperating code (the PET campaign's `refuse_sealed_pool`, `nd-unfolding/pet/improvement_campaign/confirm/replicate_inputs.py:86-100`) | a holder outside the account: Joseph personally, Ben, another m3246 member under their own account, or MINERvA. A salt-commitment scheme (the holder commits sha256 of the salt; lanes cannot form folds until it is revealed) needs only that holder to keep the salt. Caveat: `josephrb` is in group `m3246` and can read group-readable member directories (the verifier read `gregork`'s), so a member-held sample must withhold group permissions | **UNAVAILABLE** inside the lanes (Q3) |
| A fresh second production (if MINERvA supplies one) | MINERvA, or a holder Joseph names | the producer is outside the analysis | follows Q1 and Q3 |
| A fresh independent-generator truth sample (§6.2) | the person who chooses its configuration, seeds and amplitude must not be a lane that tunes the recipe | the outcome stays uninspected until the recipe is frozen (`PROPOSAL-20261005-scalar-measurement-successor.md:308-316`) | Q3 |

## 8. Interval-validation method and cost, repriced from today's units

- **No affordable validated interval method exists.** The two cheaper constructions on record are S1 (transfer the
  systematic and ML blocks) and S2 (50 inner replicas with a corrected multiplier). Both are unvalidated method
  development, with zero admitted savings (`ASSESSMENT-20261008-…` §7). No linearized interval procedure has
  equivalence evidence. **UNPRICED**: the measurement that would price one is an equivalence study on development
  folds. It needs R0 and folds, and its size is not designed.
- **PROJECTIONS, from the measured units of §3.** These are not prices. They exclude populations (unavailable),
  nuisance pseudo-data construction, retries, verification and reserve.

| design | per experiment | at 4 cases × 1,250 = 5,000 experiments |
|---|---|---|
| P1 nested: central + 300 replicas + 10 seeds + 187 universes, all recomputed | 0.0649 + 300 × (0.0464–0.0688) + 10 × 0.0649 + 187 × (0.1189–0.1619) = **36.9–51.6 node-h** | **≈ 1.84–2.58 × 10⁵ node-h** |
| P2 fixed band: one unfold of nuisance-drawn pseudo-data | 0.0464–0.0688 node-h | **232–344 node-h** of unfolds. If each selection-changing draw needs its own event loop (§5 route a), add 5,000 × 0.4302 = **2,151 node-h** |
| N2 held-out data-stream variance (KI-85 question only; lane B §16.1) | 100 unfolds | **4.6–6.9 node-h** + R0 (UNPRICED, §4.5) |

- **Comparison with the forecasts.** The feasibility assessment's P1 forecast was 0.29–1.21 million admitted
  node-h (§6; per experiment 43.2–160.9 node-h at §5 `:249`, before its 20 % reserve and overheads). The measured
  units lower the per-experiment cost. The nested design remains **NO-GO** under delegation §3.4, which this report
  does not re-decide. P2 answers a narrower question (calibration of a frozen band) than validation
  of data-dependent interval reconstruction (plan §4 Stage D). Its unfolds are cheap, but it is blocked on inputs
  1–2 and §7, not on compute.

## 9. Is "no feasible route to the full objective under current inputs" confirmed?

**CONFIRMED by inventory, with one refinement.** The basis is the files themselves, not the earlier reports:

| premise | measured here | verdict |
|---|---|---|
| one MC production, all of it in production | 489 MC AnaTuples on the cluster; the 2D manifest lists 489 | confirmed |
| no event identity | **refined:** the production omnifile has none (§4.3). The source AnaTuples carry a unique, joinable key, measured on 4 of 489 files at source plus 3 more by the verifier; the rest is supported by the G2 derived-file audit (§4.2). Identity needs an R0 rebuild (UNPRICED; no identity-only mode exists, §4.3), not a new production | refined: the identity obstacle needs no new events but is not yet priced; the freshness obstacle cannot be removed inside the project |
| no independent production-size bank | none production-size on our `/pscratch` or at the top level of m3246 CFS. `gregork/Minerva` holds derived 1A/1B conversions of unknown release (§4.5). The current open-data release is a different production whose relation to ours is unmeasured (§4.6) | confirmed, with one open route (Q2) |
| independent-generator evidence is truth-only and inspected | every sample's form, target and history checked (§6.1) | confirmed |
| no continuous nuisance generator | the event loop accepts only an existing `band:idx` (§5) | confirmed |
| new dependence channel | overlaid data gates are shared within a playlist (inferred from values, §4.4) | **new**: it constrains any split of the existing production |

## 10. Questions for Joseph (recorded only; no draft message exists, and none is sent)

Contacting MINERvA, an external author or a coauthor is Joseph's act or Ben's.

- **Q1 (input 1).** Should MINERvA be asked whether a second ME-FHC MC production is available, or whether MC
  held back from the open-data release exists? Ideally it would be production-size (≥ 4.98 × 10²¹ POT), with
  AnaTuples carrying `mc_run/mc_subrun/mc_nthEvtInFile` and the overlay gate. Without one, input 1 stays
  UNAVAILABLE at production size.
- **Q2 (input 1).** The current open-data MC files have our filenames but are 1.243–1.244 × larger (OI-55). Should we
  establish whether they are a re-generation (new events, so a candidate fresh bank) or a reprocessing of the same
  events? Two ways: ask MINERvA (Q1), or let a lane read one remote file from a DTN and compare the truth kinematics
  of shared `K` against ours. That read needs a write of about 20 GB to a new scratch path, which this read-only
  lane may not do. A full copy (≈ 13 TB) would exceed the CFS 3 TB rule. A third, internal route:
  `gregork/Minerva/20260326/{1A,1B}` holds `.pb` conversions with our 1A and 1B filenames (§4.5). Which release
  they came from could settle Q2 without a scratch write. Asking the member, or reading their data for this purpose,
  is Joseph's call.
- **Q3 (custodian).** Who holds the assessment samples and the fold salt: Joseph, Ben, another m3246 member under
  their own account, or MINERvA? No lane can, because every lane runs as `josephrb` (§7).
- **Q4 (input 3).** Should MINERvA be asked for detector-simulated samples from an alternative generator (for example
  GENIE v3 G18_10a_02_11b or AR23_20i, or NuWro, on the tracker)? Or should Stage D accept the explicitly limited
  alternative of §6.2, a fresh truth-level configuration reweighting the nominal response, as partial evidence?
- **Q5 (input 2).** For the nuisance law, should Stage D declare the MAT universe law as a convention, with no
  physical-adequacy claim? Or should external validation evidence for MINERvA's systematic prescriptions be sought
  from the collaboration?
- **Q6 (dependency, already open).** The 10.5 TB of MC AnaTuples are only on `/pscratch` (§4.6). Every Stage D route
  through R0 depends on them. Drafts A and B of 2026-10-09 remain unsent.
- **Q7 (plan §6).** Given §1, the two-outcome decision: keep the full endpoint open while Q1–Q5 are pursued, or
  separately adopt narrower conditional or convention claims, which is a different publication endpoint.

## 11. Not measured, and how each would be measured

- **The identity census over all 489 MC files.** Four were read (§4.2). Measurement: the same probe over every
  file. It needs login-node reads only: the verifier measured 2.1–5.5 s per file for the integer branches, so the
  census is ≈ 15–45 login-minutes (PROJECTION).
- **Overlay-gate connected components per playlist** (§4.4), and their effect on muon kinematics.
- **The cost of R0 in either identity route** (§4.3). One 1L run, against `59713360_7`. Alternatively, the
  historical `sacct` cost of the point-cloud-mode event loops (G2), if a committed receipt exists; none was found.
- **The relation of the current open-data MC to ours** (Q2).
- **GENIE v3 throughput,** and whether the CVMFS v3 builds run on Perlmutter. GENIE v2 and NuWro are documented to
  run (§6.2). CH NuWro throughput is also unmeasured.
- **Per-bin ESS and the smearing share,** on an R0 file (lane B §5, §18).
- **The final charge of the Stage C pilot,** with 50 jobs pending at 07:21Z. Stage C production is unpriced.
- **CFS usage of `/global/cfs/cdirs/m3246/josephrb`** today. The 2,512 GiB figure is from 2026-10-09.
- **Which release `gregork`'s `.pb` conversions come from** (Q2).

## 12. Reproduction

On Perlmutter, read-only:

    eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
    conda activate $HOME/.conda/envs/root_6_28        # do not set -u before this (ADDR2LINE)
    B=/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC
    python -I identity_probe.py $B/Playlist1A/MasterAnaDev_mc_AnaTuple_run00110001_Playlist.root
    python -I dup_probe.py      $B/Playlist1E/MasterAnaDev_mc_AnaTuple_run00111353_Playlist.root
    python -I overlay_reuse.py  $B/Playlist1A/…run00110001… $B/Playlist1A/…run00110002… $B/Playlist1E/…run00111353…
    python -I omni_branches.py  /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC.root
    sacct -u josephrb -X -S 2026-10-10T00:00:00 -E now --parsable2 \
      --format=JobID,JobName%60,Account,QOS,State,ElapsedRaw,AllocTRES%120,Submit,Start,End

The probes were run by piping the script to `python -I -` over ssh. Charges are summed with billing parsed from
`AllocTRES`.

## 13. Limits

- Four AnaTuples are a sample of 489. The key's uniqueness on the rest is supported by the G2 derived-file audit,
  not measured here at source.
- The reading of the MC `ev_*` branches as the overlaid data gate rests on their values, not on MINERvA
  documentation.
- The pilot timings are mid-campaign `sacct` readings. The pilot's own REPORT may classify them differently.
- One independent verifier ran (PASS WITH CHANGES, repaired here; [`verification/VERIFICATION.md`](verification/VERIFICATION.md)). It did not re-run the 1E double-fill
  probe or the 66,657 shared-gate figure; those rest on this lane's evidence outputs.
