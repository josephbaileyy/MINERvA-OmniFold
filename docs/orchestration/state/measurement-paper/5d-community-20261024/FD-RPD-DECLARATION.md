# DECLARATION RPD, part 1 (design): the run-period diagnosis, with its readouts and their reading fixed before any number is read (2026-11-02)

**By** the `limitation-resolver` lane, for the director to bind after a fresh Sonnet audit.

**Under:**
- [`DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md`](../../../DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md)
  (#690) item 3(b): "12 per-playlist unfolds from the CFS-preserved event loops (#646), to look for the cause of the p∥
  step and test the block's size", "declared, priced, audited and bound before anything runs";
- the director's rulings of 2026-11-02, given in messages:
  1. the inputs are MP-1's zero per-playlist loops, with the CFS bkgaware copy as the fallback;
  2. a stage 0 at 0 node-h on 5B's existing period unfolds, with each branch naming the paper sentence it can move;
  3. a between-period against within-period test, with a simulated null, fixed before any playlist number is read;
  4. the paper wording each outcome licenses, decided here.

**After:** [`FD-CT-5B-REPORT.md`](FD-CT-5B-REPORT.md) and its declaration, whose chain this campaign reuses, and the
2026-11-01 limitation inventory's Q17 and Q18 rows
(`2d-closeout/stageF/methods/secondary-results/referee-and-qualifications-20261101/inventory-answer.txt:73-74, 133-134`).

**Declares (this part):** the question, the inputs, the stages, the controls, the readouts with their reading rules and
outcomes, the wording each outcome licenses, the price and the stops.

**Part 2** declares the code, its tests, the exact commands and the pinned bytes. It cites this part by sha256, changes
none of its rules, and goes to its own audit before the director binds both. This split puts the readouts under review
before any code is written to produce them.

**MEASURES:** nothing. This part read records only, plus `ls -l` of two cluster directories on login23 on 2026-11-02
(metadata only; §1). It read no unfold, no event loop and no readout of any period or playlist.

**CANNOT AUTHORIZE:**
- any run, which needs part 2 and the director's binding of both parts;
- a covariance component, or any change to the reported matrix C_total + C_resp + C_PL,5D. Any 12-playlist block is
  printed beside it, never in it. Adopting one is a covariance change, which goes to Joseph;
- a paper or note edit. §6 fixes which wording each outcome licenses; the paper lane drafts it, the director reviews it,
  and Joseph reads it;
- the cause of a period difference, or which period is right.

**CITABLE FOR:** what the campaign will compute, from which inputs, at what price, how each readout will be read, and
which sentence each outcome may move.

**NOT CITABLE FOR:** any result. Once run, also not for:
- a cause. §6.1 says why no outcome here can supply one;
- a validated coverage: a block built from the observed differences contains them by construction
  (`2d-closeout/playlist-term/REPORT.md:20`).

**Paths:** as in 5B's declaration. A bare `.md` name is in this directory. Paths beginning `docs/` or `nd-unfolding/` are
from the repository root; other paths are relative to `docs/orchestration/state/`. `$P` = `/pscratch/sd/j/josephrb`.

## 0. Summary

**The question.** The paper states two run-period limitations:
- `docs/analysis-note/paper_body.tex:112` (the 2D result): one period group's unfolded p∥ distribution, relative to its
  own simulation, "differs from that of the earliest periods by a step of about 7% near 8 GeV/c. The cause is not
  known";
- `paper_body.tex:81` (the 5D result): C_PL,5D "accounts for differences among the three run-period groups … The cause
  is not known … with three groups its size is poorly determined: the 68% interval on the ratio of its true to its
  estimated size is 0.73–2.56".

The campaign asks three things:
1. Is the step carried by every playlist of its period group, or by some of them?
2. Do the playlist offsets cluster by period group, or scatter like twelve exchangeable draws?
3. Only if they scatter: what is the size estimate from twelve playlists, and its interval?

**The stages:**

| stage | where | what | node-h |
|---|---|---|---|
| 0 | login | the dr_PB/PA p∥ step from 5B's existing period unfolds, with its bootstrap distribution (§3) | 0 |
| S | login | O_NOATIME staging copies, with sha256 checks, of every pre-existing input; 12 per-playlist flux files (§2) | 0 |
| A | 1 node | the 12 per-playlist inputs (dump, lateral form, check, MC truth), and one re-unfold of a 5B product (§2, K2′) | about 0.25 |
| C | login | the partition and flux controls (§4) | 0 |
| B | 1 node | 12 × 31 unfolds: seed 42 and 30 bootstrap replicas per playlist (§2) | about 1.0 |
| R | login | readouts R1–R3 and the simulated null (§5) | 0 |
| H | login | the HPSS copy, after maintenance ends 2026-11-06 17:00 (§8) | 0 |

**Price: about 1.3 node-h expected, at most 3.0** (§7). Every job is under 12 h, on CPU, at QOS regular.

## 1. Inputs, and why the zero loops

**MP-1's 12 zero per-playlist loops**, `$P/measurement-paper/phase1/mp1/s1/evloop/zero/runEventLoopOmniFold_5D_<PL>_zero.root`,
are pinned at `fd_ct_period_inputs.ZERO_LOOPS` (sha256 measured on login37, 2026-10-30). `ls -l` on login23 on 2026-11-02
listed all 12, totalling 4.84 GB.

**The evidence that they are the right CV inputs:**
- **5B's bound chain read them, and reproduced MP-1's zero chain bitwise.** The ALL merge's npz is byte-identical to
  `lat_zero.npz`, its background arrays are key-for-key `lat_zero_bkg.npz`'s (K1), and its unfold's `xsec_flat` is
  bitwise `mp1s1_zero` (K2, maximum relative difference 0.0) (`FD-CT-5B-REPORT.md:100-103`).
- **Their CV columns equal the bkgaware loops' for 1A.** For 1A, the production bkgaware file's CV-pass rows (1,736,833)
  and `mc_background` rows (52,626) equal MP-1 S0's `base_cv` and W2b's `rrzero_1A`, in file order and as a multiset
  over all 15 CV columns. They differ only by the bkgaware file's 454 per-universe branches (`FD-CT-5B-INPUTS.md:32-36`,
  citing `measurement-paper/phase1/mp1/S0-REPORT.md:58-76`). Each zero loop equals W2b's rrzero pass of its playlist
  under W2's `equal` rule (`FD-CT-5B-INPUTS.md:37-39`).
- **No per-playlist (e) unfold reads a universe branch.** The chain is 5B's: dump, lateral form, check, unfold.
- **Size:** 4.5 GiB, against the bkgaware loops' 159.4 GiB.

**The fallback.** If a later step needs universe branches, it reads the CFS copy
`/global/cfs/cdirs/m3246/josephrb/eventloop-5d-bkgaware-preservation-20261101/` (#646). That needs its own declaration,
with a login-node O_NOATIME staging step. No job reads CFS.

**Every other input:**

| input | where | pin |
|---|---|---|
| the baseline flux files, one per playlist | `$P/MINERvA-OmniFold/2d-unfolding/baseline_flux/` | part 2 records each sha256; F1 (§4) ties their combination to 5B's committed period flux files and to production `d40aea69…` |
| 5B's period unfolds and MC truths (stage 0) | `$P/fd-ct-5b-20261030/unf/{PA,PB}/`, `truth/truth_{PA,PB}.npz` | `fd/receipts-ct/5b/run/preserve/INVENTORY.sha256` (51 rows, committed) |
| 5B's PC lateral npz and background dump (K2′) | `$P/fd-ct-5b-20261030/dumps/` | part 2 records each sha256, and K2′ checks them against 5B's PC check receipt (`fd/receipts-ct/5b/run/inputs/check_PC.json`) |
| S1, C_resp, 5B's period readout, the 16-cell definition | as 5B's readout | 5B's pins (`FD-CT-5B-DECLARATION.md` §1, §8) |
| per-playlist data POT | each zero loop's `dataPOTUsed`; checked against its flux file | `check` refuses beyond 10⁻¹², as in 5B |

**Reads.** Every pre-existing pscratch file is read exactly once, by a login-node staging copy into `$R/staged/`. The
copy opens with O_NOATIME and checks the copy's sha256 against its pin. Every later step reads only the staged copies.
So no purge clock moves, and the jobs never read a file this campaign did not make.

**The pscratch-only exposure.**
- The zero loops have no HPSS or CFS copy and are exposed from 2026-12-15 (`FD-CT-RETENTION.md:63`). 5B's PC dumps are on
  pscratch only (`FD-CT-5B-REPORT.md:235`).
- Both go on the post-maintenance HPSS catch-up list, as the director ruled, with the 12 per-playlist flux files and
  this campaign's products (§8).
- The campaign must finish its jobs, or hold the staged copies on HPSS, before 2026-12-15.

## 2. The chain

**Per playlist X ∈ {1A, …, 1P}**, by 5B's tools with a single-playlist group in place of a period:

| step | tool | what it makes |
|---|---|---|
| flux (login) | 2D's `build_flux.py` arithmetic, on one playlist | Φ_X with `DataPOTUsedForFluxWeighting` = X's data POT |
| input | the staged zero loop (part 2 settles whether 5B's `merge` runs on one file or is bypassed; either way `check` ties the dump to the pinned loop) | — |
| dump | `nn_dump_inputs.py --axes eavail,q3,W --mcfile <Φ_X>` | X's npz |
| lateral form | `s5p_input_dumps.py lateral --cv-npz <that npz> --mcfile <Φ_X>` | the npz in MP-1's lateral form, and its background dump |
| check | `fd_ct_period_inputs.py check` → `s5p_mc_truth_pred.py` | X's receipt and MC truth T_X |
| unfold | `fd_ct_period_inputs.py unfold` → `s5p_numerics.py` | (e): config R, 5 iterations, real data |

**Unfolds:** for each X, seed 42 and 30 bootstrap replicas, 372 in all.
- The seeds are 4000 + 100·i + k, where i = 1…12 is X's production-order index and k = 1…30. They are disjoint across
  playlists, so the playlists' replicas share no Poisson draws (5B's review M1).
- **Why 30 and not 5B's 10:** R2's simulated null needs each playlist's 16 × 16 noise covariance at full rank, which 10
  replicas (rank ≤ 9) cannot give. With 30 the rank is up to 16. The unfold is cheap per playlist (§7).
- `s5p_numerics.py` must be byte-identical to 5B's bound copy. Part 2 pins it, so 5B's K2 carries over to the code.
  K2′ (§4) checks the deploy.

**Job geometry:** 5B's. One exclusive CPU node, 8 lanes of 32 CPUs and 56 GB, `--no-requeue`, account m3246, QOS
regular, no GPU. Every step refuses to overwrite, and there is no resume (5B's stop rule, `FD-CT-5B-DECLARATION.md:120-123`).

## 3. Stage 0: does the 5D chain see the step? (login, 0 node-h, before any job)

**The statistic.** For a period or playlist Y, with unfold X_Y and its own MC truth T_Y on the fine grid, and a p∥
region R, let D_Y(R) = Σ_{c∈R} X_Y(c) / Σ_{c∈R} T_Y(c).
- The sums run over fine cells that map to a reporting cell (`fine_map` ≥ 0). So the unreported boxes are excluded, as in
  every 16-cell readout.
- The sums are of cell-integrated values. Part 2 asserts which `xsec_flat` holds, against `s1_assemble`.
- The regions are L = p∥ ∈ [1.5, 8) GeV/c and H = [8, 15) GeV/c. Both are unions of fine p∥ bins: the fine grid has edges
  at 8 and 15 (`nd-unfolding/s5p_stage1_inspect.py`, `FINE["pz"]`). They are the 2D test's regions
  (`2d-closeout/period-unfold-20261014/REPORT.md:52`, "r[8,15) / r[1.5,8) − 1").

The step of Y against a reference Z is s_{Y/Z} = [D_Y(H) / D_Z(H)] / [D_Y(L) / D_Z(L)] − 1. It is a double ratio, so each
group's MC truth divides out.

**Stage 0 reads** s₀ = s_{PB/PA} on 5B's seed-42 period unfolds. Its noise is σ₀, the SD of s over the 10 replica pairs:
5B's replica k of PB with replica k of PA, k = 1…10, from disjoint seed blocks. (e)'s seed term is zero by construction
(`FD-CT-5B-REPORT.md:127`). The reference is 2D's dr_PB/PA step, +6.94 ± 0.41% (`period-unfold-20261014/REPORT.md:57`).

**The reading, fixed here:**

| branch | rule | what it gates |
|---|---|---|
| **SEES** | s₀ ≥ +3.47% (half of 2D's +6.94%) and s₀ / σ₀ ≥ 5 | R1 is read as a localization of the 5D analogue of line 112's step. §6.1's wordings may move **line 112** (and `sec_fived16.tex:125`'s 5D sentence) |
| **ABSENT** | s₀ / σ₀ < 3 | the 5D chain does not show 2D's step on its phase space. R1 is printed descriptively, and nothing from it moves line 112. R2 and R3 may move only **line 81**. Localizing line 112's step needs 2D per-playlist unfolds (§9) |
| **OTHER** | neither | as ABSENT for line 112. The value is reported beside 2D's, unread |

- With 10 replicas, an SD is uncertain by about ±22%, as the 2D report notes for its P_C step
  (`period-unfold-20261014/REPORT.md:72`). The SEES threshold of 5σ leaves room for that.
- **Stage 0 runs before job A,** so an ABSENT or OTHER branch reaches the director at 0 node-h. The director may then
  re-scope before anything is charged. Stage 0 is a gate on scope, not on running: unless the director says otherwise,
  the jobs still run, because R2 and R3 address line 81 in every branch.

## 4. Controls (each a stop, reported unrepaired)

- **F1, the flux** (login, stage S). For each period P, the data-POT-weighted combination of its playlists' Φ_X must equal
  5B's committed period flux file bin by bin to 10⁻¹², with its POTs (`FLUX` pins, `fd_ct_period_inputs.py`). For ALL
  it must equal production `d40aea69…`, as 2D's `verify_inputs.py` required of ALL.
- **C1, the partition** (login, after job A). Concatenate the 12 per-playlist lateral npz files' per-event arrays in
  production order, and compare them key by key with MP-1's `lat_zero.npz`. Each key falls in one of three classes:
  - **kinematic and pass keys** (coordinates, pass flags): equal bitwise;
  - **weight keys:** a per-playlist dump normalizes its MC to that playlist's own exposure, not to ALL's. So within each
    playlist's slice, the weights must equal `lat_zero`'s times one constant, to 10⁻¹² relative. That constant must
    equal the ratio the two dumps' recorded POT and flux normalizations imply;
  - **global keys** (flux, POT, edges): checked by F1 and by each receipt, not concatenated.

  The background dumps are compared with `lat_zero_bkg.npz` in the same way. Part 2 assigns every key in `NPZ_KEYS` and
  `BKG_KEYS` to its class, and derives the expected constant, from the code of `nn_dump_inputs.py` and
  `s5p_input_dumps.py`. A key it cannot assign is a stop in part 2's review, not at run time. If C1 passes, the
  per-playlist inputs are a partition of the inputs whose unfold is `mp1s1_zero`, renormalized per playlist and
  otherwise unchanged.
- **K2′, the deploy** (job A, one lane). This deploy's unfold of 5B's own PC inputs at seed 42 must be bitwise 5B's
  `ct5b_unfold_PC_s42` (its INVENTORY digest). That ties this deploy's environment to 5B's bound one, at about 140 s of
  one lane (`lanes-periods/line1-60549044.log`).
- **Gates.** Job B is submitted only after C1 and K2′ pass on this deploy's records, by a gate in the submit stage, as
  in 5B. The readout refuses unless all 372 unfolds exist with their receipts.
- **Q3** (in the readout): every unfold and MC-truth integral is positive and finite on L, H and each reporting cell.
- **The leak guard.** Every output passes F0's `LeakGuard`, as in 5B: ratios, steps and decompositions only.

## 5. The readouts (login, after job B), fixed before any playlist number is read

**Notation.**
- r_X is X's double ratio X_X / T_X, on the 16 reporting cells (as 5B's readout forms it) and on L and H (§3).
- e_X is X's exposure share, computed as 5B computes e for a period, with X in place of the period: POT_X Φ_X(p_T) / Σ_Y.
  - **Arithmetic, as an approximation:** splitting 5B's period shares (0.5334, 0.2945, 0.1721) within each period by
    data POT (`2d-closeout/playlist-spread-20261014/outputs/potcheck.json`) gives e from 0.0127 (1L) to 0.1575 (1F).
  - If e varies by cell beyond 10⁻¹², the block takes that design's diag(√k) form (`2d-closeout/playlist-term/DESIGN.md` §2), and the rank assertion becomes ≤ 11.
- Replica k of any combination uses replica k of every member.

### R1, where the step is (fine p∥; read under stage 0's branch)

**For each playlist X,** t_X = s_{X/A*}, with the stage-0 step formula.
- The reference A* is the exposure-weighted combination of the 1A–1F playlists' D values (with X left out when X is in
  1A–1F). It matches 2D's reference, "the earliest periods" (line 112).
- σ_X is the SD of t_X over the 30 replicas.

**Each playlist gets one class.** t* = s₀ is the stage-0 step:
- **UNRESOLVED** if σ_X > t*/4. Then 0 and t* are less than 4σ apart, and the playlist is not classified;
- **CARRIES** if |t_X − t*| ≤ 2σ_X;
- **FREE** if |t_X| ≤ 2σ_X;
- **PARTIAL** otherwise.

For a resolved playlist, CARRIES and FREE cannot both hold.

**The pattern:**
- **PERIOD-WIDE:** at least two of 1G, 1L and 1M are resolved, every resolved one CARRIES, and every resolved 1A–1F
  playlist is FREE.
- **SUBSET:** at least one resolved 1G/1L/1M playlist CARRIES, and at least one is FREE.
- **OTHER:** anything else, including a 1A–1F playlist that CARRIES, or a PARTIAL in 1G/1L/1M.

By the arithmetic shares, 1L (e ≈ 0.013) may well be UNRESOLVED; this is stated before reading. 1N–1P are printed with
their classes, but they enter no pattern.

**Beside it, descriptive:** the per-playlist recombination of 1G/1L/1M against A*. Its step is compared with s₀, the
pooled period unfold's. The difference is the pooling's (J36-like) mix effect, with its replica σ.

### R2, do the offsets cluster by period group? (16 cells; read in every branch)

**The offsets.** g_X = r_X / m − 1 per cell, with m = Σ_X e_X r_X over all 12, so Σ_X e_X g_X = 0. For a partition π of
the 12 playlists into groups of sizes 6, 3 and 3, with group shares E_g = Σ_{X∈g} e_X and group offsets
G_g = Σ_{X∈g} e_X g_X / E_g:
- Q_b(π) = Σ_g E_g G_gᵀ M⁻¹ G_g;
- Q_tot = Σ_X e_X g_Xᵀ M⁻¹ g_X, the same for every π;
- F(π) = Q_b(π) / Q_tot.

M = (C_total + C_resp)/(f fᵀ), 5B's metric.

**The test: exact permutation.** p_clust is the fraction of the 9,240 distinct partitions with F(π) ≥ F(π_obs), where
π_obs is the flux-file grouping {1A–1F}, {1G, 1L, 1M}, {1N, 1O, 1P}.
- The grouping follows the flux files, not the data (`2d-closeout/period-unfold-20261014/scripts/periods.py:1-4`).
- (18,480 ordered partitions give 9,240 distinct values of F, because swapping the two size-3 groups leaves F
  unchanged.)
- Under exchangeable playlist offsets, the labels are arbitrary, so this p needs no noise model. The shared-flux
  clustering of 1G/1L/1M is therefore tested, not assumed.

**The simulated null, and the power** (2,000 simulated datasets each, NumPy seed 20261102, fixed here):
- **Calibration (null S0).** Each simulated dataset draws g_X = δ_X + ε_X:
  - δ_X iid N(0, Σ_δ), where Σ_δ is the exchangeable model's per-playlist offset covariance:
    Σ_X e_X g_X g_Xᵀ / (1 − V2), less the same statistic averaged over the replica-noise draws, then projected onto
    the PSD cone;
  - ε_X ~ N(0, Σ_X), X's 16 × 16 noise covariance from its 30 replicas (deviations about their mean, scaled by
    30/29). Each simulated dataset is re-centred so that Σ e_X g_X = 0.
  - α̂ is the share of datasets with p_clust < 0.05. **The test is calibrated if α̂ ≤ 0.0646**, which is
    0.05 + 3 √(0.05 · 0.95 / 2000).
- **Power (alternative S1, period-clustered).**
  - δ_X = G_{P(X)}. The three period offsets are drawn from N(0, Σ_P), with Σ_P the same estimator applied to the
    per-playlist-recombined period offsets with the three period shares, less its replica-noise expectation and
    projected onto the PSD cone. There are no within-period offsets.
  - The noise is as in S0.
  - The power β̂ is the share with p_clust < 0.05.

**Outcomes, fixed here:**

| outcome | rule | meaning |
|---|---|---|
| **CLUSTERED** | calibrated, and p_clust < 0.05 | the offsets cluster by flux-file group. The block's size rests on three period-level draws, as now |
| **EXCHANGEABLE-COMPATIBLE** | calibrated, p_clust ≥ 0.05, and β̂ ≥ 0.80 | clustering of the size the 3-group block implies would have been detected 80% of the time, and was not |
| **INCONCLUSIVE** | anything else (miscalibrated, or β̂ < 0.80) | no reading |

### R3, the size from twelve playlists (16 cells; always printed, read only under EXCHANGEABLE-COMPATIBLE)

- **The 12-playlist block:** C_PL,12 = Σ_X k₁₂ e_X (f ∘ g_X)(f ∘ g_X)ᵀ, with k₁₂ = V2₁₂ / (1 − V2₁₂), by the estimator of
  `2d-closeout/playlist-term/DESIGN.md` §2. It is printed in relative form through the leak guard: as σ/f per cell and as ratios to C_PL,5D.
- **Its noise expectation** is the same estimator on the replica-noise draws, scaled by 30/29. The block is printed
  raw and debiased. The debiased form is projected onto the PSD cone, and the projection's discarded trace is printed.
- **Its Satterthwaite dof:** ν₁₂ = (1 − V2)² / (V2 − 2Σe³ + V2²), with the 68% interval of σ_true/σ_hat from χ²_ν,
  exactly the formula of the 5D label (`nd-unfolding/fd_ct_5b_audit.py:94`). That formula with 5B's three shares
  reproduces the label's ν = 1.824 and 0.73–2.56.
  - With the approximate twelve shares above, ν₁₂ ≈ 7.98 and the interval is about 0.82–1.38 **(arithmetic; the readout
    recomputes it from the actual e)**.
- **The size comparison:** ρ = √(tr M⁻¹ C_PL,12,deb / tr M⁻¹ C_PL,5D), with the per-cell σ ratios (median, minimum,
  maximum) and the replica-noise reference of ρ, as the P^(k) draws of 5B's audit.

## 6. What the paper may say, decided now

The paper lane drafts, the director reviews and Joseph reads (#690 item 2). This table fixes the **only** changes each
outcome licenses. Everything not listed stays.

### 6.1 "The cause is not known" (lines 81 and 112, `sec_fived16.tex:125`)

**No outcome of this campaign licenses dropping it.**
- A localization says where a difference is, not why. Dropping the clause needs a named mechanism whose predicted
  effect matches the localization and the size, tested by its own declared step.
- Two routes to such a mechanism exist on record. Both are outside this campaign:
  - an answer from MINERvA. The prepared question (`QUESTION-20260920-hadronic-response-coverage-for-eavail-w.md:8`)
    is "PREPARED, NOT SENT", it concerns hadronic response, and sending anything is Joseph's act;
  - a declared test of a mechanism that a SUBSET or PERIOD-WIDE outcome points to.

**What each R1 pattern licenses (only under stage-0 SEES).** The bracketed lists are filled from the readout:

| R1 pattern | line 112 (2D step) | line 81 / `sec_fived16.tex:125` |
|---|---|---|
| **PERIOD-WIDE** | append: "The step appears in each playlist of that group that the data resolve ([1G, 1M]), and those playlists share one simulated flux; the cause is not known." | the same sentence, of the 5D double ratios |
| **SUBSET** | append: "The step is confined to playlist(s) [list]; the group's other resolved playlist(s) [list], which share its simulated flux, do not show it. The cause is not known." | the same |
| **OTHER** | no change | no change |

Under ABSENT or OTHER at stage 0, no R1 wording is licensed for line 112. R1 is not read for line 81 either: the 16
cells dilute the step (`FD-CT-5B-REPORT.md:128`).

### 6.2 "With three groups its size is poorly determined" (line 81; `sec_fived16.tex:125`)

| R2 outcome | licensed |
|---|---|
| **CLUSTERED** | the clause stays. One may be added: "The differences are shared by the playlists within each period group, so the block's size rests on three period-level estimates." |
| **EXCHANGEABLE-COMPATIBLE** | **(i)** If Joseph adopts C_PL,12 as the reported block (a covariance change, his), the clause becomes: "Estimated from the twelve playlists, the 68% interval on the ratio of its true to its estimated size is [a]–[b]." **(ii)** If C_PL,5D stays the reported block, the clause stays, because it describes that block's own estimator. One may be added: "An estimate from the twelve playlists is [ρ] times the block's size (68% interval of that estimate [a]–[b])." |
| **INCONCLUSIVE** | no change |

**Joseph's choice in (i) is open, and nothing here recommends it.** Whether to adopt a block chosen after seeing its
size is exactly the post-hoc question the block's audit faced (line 81: "added after these differences were seen").

### 6.3 What no outcome licenses

- "validated", "covers" or "coverage" of either block;
- "which period is correct";
- line 81's "is not corrected for the bootstrap noise it contains" changes only if the reported block changes. R3's
  debiased form is printed beside it.

## 7. Price

From 5B's measured units:
- **Unfolds** (`lanes-periods/line{1,2,3}-60549044.log`): a PA unfold (e ≈ 0.53) took about 400 s, a PB one (0.29) about
  236 s and a PC one (0.17) about 136–141 s on a 32-CPU lane. That is nearly linear, at about 780 s × e plus about 10 s.
  So one round of 12 playlists takes about 900 lane-seconds **(arithmetic)**.
- **Inputs:** 5B's ALL lane (100% of the data) took merge 3:00, dump 7:12, lateral 7:06 and check 3:14
  (`FD-CT-5B-REPORT.md:87`).

| job | geometry | projected | limit, so at most |
|---|---|---|---|
| A: 12 input lanes, plus K2′ | one node, 8 lanes, longest first | about 15 min, so 0.25 node-h **(estimate: per-step start-up unpriced)** | 1:00:00, so 1.0 |
| B: 372 unfolds | one node, 8 lanes, longest first | 31 × 900 / 8 ≈ 3,500 s, so about 1.0 node-h **(estimate)** | 2:00:00, so 2.0 |

**About 1.3 node-h expected, at most 3.0.** The login stages charge nothing. The standing approval covers jobs under
12 h. For comparison, the inventory's guess was "about 3–4 for 12 playlists" (`inventory-answer.txt:133`).

**Stops:** any refusal, any non-zero exit, a lane without its products, a job past its limit, or a control FAIL is
reported unrepaired. A FAIL of F1, C1 or K2′ stops the campaign before job B. A rerun needs the director and a new `$R`.

## 8. Ledger, storage and HPSS

- **`$R`** = `$P/fd-rpd-<date>/`, which must not exist beforehand.
- **HPSS is deferred** under `RECORD-20261102-director-hpss-deferral.md` (#685) until 2026-11-06 17:00. The catch-up
  archive gains:
  - the 12 zero loops (4.84 GB);
  - 5B's PC lateral npz and background dump;
  - the 12 flux files;
  - the 372 unfolds and the 12 MC truths;
  - the control records and the readout.

  The procedure is the bound one: hpssquota, an explicit list, htar -Hcrc -Hverify=1, hashcreate/hashverify, and
  retrieval compared by sha256.
- **Committed in the report's PR:** the readouts, the logs, `sacct`, receipts, the products' sha256 list and ledger
  rows. The per-playlist dumps (about 9 GB **(estimate)**) stay on pscratch, rebuilt from the loops by job A.
- `$R` goes on the pscratch retention list.

## 9. Scoped separately: 2D per-playlist unfolds (if stage 0 is ABSENT or OTHER)

**The case for them.** Line 112's step is a 2D result. If the 5D chain does not show it, localizing it needs the 2D
chain itself: RE-2's estimator on 12 per-playlist 2D inputs.

**Price, from RE-2's measured period runs:** J8, 37 period unfolds, charged 1.1358 node-h (job 60195845), which is about
0.0307 node-h per run. Its steps' mean was 0.0274 (0.0196–0.0553) (`2d-closeout/stageF/methods/re2/RE2-PARTB-REPORT.md:52-64`;
per-run figures derived from its `steps.psv`).
- 12 × (1 + 30) = 372 per-playlist runs would cost about 7–11 node-h. With 10 replicas, it would be 132 runs, about
  3–4 node-h **(arithmetic; a per-playlist run is smaller than a period run, so this is an upper estimate)**.
- **Needs:** per-playlist 2D inputs and flux, and a check that the 2D per-playlist CV omnifiles still exist (not checked
  here).
- **Its own declaration and audit.** This part declares none of it.

## 10. For the director

1. **Two audits:** this design part now, and part 2 (the code) before binding. The alternative is one audit after the
   code is written.
2. **Thirty replicas,** against 5B's ten, for R2's full-rank noise covariance (§2), at about +0.7 node-h.
3. **Stage 0's thresholds,** SEES at ≥ half of 2D's step and ≥ 5σ, are a choice. They were set before any 5D step was
   read.
4. **R2's 0.05 and 0.80** are conventional, and fixed here.

## 11. Not changed

The paper, the note, every covariance and block, 5B's records, the CFS copy and the retention list. No run is
authorized.
