# DECLARATION RPD, part 1 (design), revision 3: the run-period diagnosis, with its readouts and their reading fixed before any number is read (2026-11-02)

**By** the `limitation-resolver` lane, for the director to bind after a fresh Sonnet audit.

**Revision 3** answers the second audit, `FD-RPD-AUDIT-2-SONNET-ANSWER.txt` (of revision 2, sha256 `9fc61f3e…`). It
found 0 BLOCKING, 8 MAJOR, 12 MINOR and 3 NIT, and judged 12 of the first audit's 18 findings resolved and 6 partly
resolved. §13 gives each disposition. The main changes:
- R2's power alternative is now the observed period structure, held fixed, not a rank-2 Gaussian draw. That draw made
  EXCHANGEABLE-COMPATIBLE unreachable by construction;
- pre-job-B decision rules use the design-time simulations of R1 and R2;
- N0 has 10 partitions, t thresholds, a ratio-preserving `denom_nd`, a partition control, and stated power. Its two
  triggers act separately;
- C1 reads mc_pot from the staged loops and checks the npz `flux` key, and no default path is opened;
- the wording keeps the flux clause to 1G/1L/1M, says "no step larger than half", and carries the equal-variance
  condition;
- three departures from the decision's wording are listed for Joseph.

**Revision 2** answered the first audit, `FD-RPD-AUDIT-1-SONNET-ANSWER.txt` (of revision 1, sha256 `b9b32656…`). That
audit found 3 BLOCKING, 8 MAJOR, 5 MINOR and 1 NIT. §12 gives each disposition. Its main changes:
- every C1 key now has its exact predicate;
- K2′ compares arrays, not file bytes;
- R1's patterns form a partition, and t* is the recombined step with a correlated tolerance;
- an estimator-size null (N0) is added;
- the R2 test is called approximate, with its null run over a grid and a second alternative;
- a joint wording table, and wording that names no cause;
- stage 0's centre, sign and dilution are stated, and what was already read of 5B is disclosed;
- staging comes first, so every pre-existing read is O_NOATIME.

**Under:**
- [`DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md`](../../../DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md)
  (#690) item 3(b): "12 per-playlist unfolds from the CFS-preserved event loops (#646), to look for the cause of the p∥
  step and test the block's size", "declared, priced, audited and bound before anything runs";
- the director's rulings of 2026-11-02. They are verbatim in `FD-RPD-RULINGS-20261102.txt` beside this file:
  1. the inputs are MP-1's zero per-playlist loops, with the CFS bkgaware copy as the fallback;
  2. a stage 0 at 0 node-h on 5B's existing period unfolds;
  3. a between-period against within-period test, with a simulated null, fixed before any playlist number is read;
  4. the paper wording each outcome licenses, decided here.

**Three departures from the decision's and the director's wording, for the director to put to Joseph:**
- the input substitution (ruling 1);
- §6.1's reading that no outcome here can supply a cause. The decision says "to look for the cause". The campaign does
  look, by localizing the step, but a localization is not a cause;
- §6.2's reading that no outcome by itself drops "poorly determined". The director asked what result would drop it.
  The clause describes C_PL,5D's own three-group estimator. So it goes only if Joseph adopts a 12-playlist block after
  EXCHANGEABLE-COMPATIBLE, which re-opens that part of the section. Otherwise a sentence giving the 12-playlist estimate
  is added beside it.

**After:**
- [`FD-CT-5B-REPORT.md`](FD-CT-5B-REPORT.md) and its declaration, whose chain this campaign reuses;
- the 2026-11-01 inventory's Q17 and Q18 rows
  (`2d-closeout/stageF/methods/secondary-results/referee-and-qualifications-20261101/inventory-answer.txt:73-74, 133-134`).

**Declares (this part):** the question, the inputs, the stages, the controls, the readouts with their reading rules and
outcomes, the wording each outcome licenses, the price and the stops.

**Part 2** declares the code, its tests, the exact commands and the pinned bytes. It cites this part by sha256, changes
none of its rules, and goes to its own audit before the director binds both parts.

**MEASURES:** nothing. This part read records and code only, plus `ls -l` of two cluster directories on login23 on
2026-11-02 (metadata only). It read no unfold, event loop or readout of any period or playlist. §3 lists what this lane
had already read of 5B's published report.

**CANNOT AUTHORIZE:**
- any run, which needs part 2 and the director's binding of both parts;
- a covariance component, or any change to the reported matrix C_total + C_resp + C_PL,5D. Any 12-playlist block is
  printed beside it, never in it. Adopting one is a covariance change, which is Joseph's;
- a paper or note edit. §6 fixes which wording each outcome licenses; the paper lane drafts it, the director reviews
  it, and Joseph reads it;
- the cause of a period difference, or which period is right.

**CITABLE FOR:** what the campaign will compute, from which inputs, at what price, how each readout will be read, and
which sentence each outcome may move.

**NOT CITABLE FOR:** any result. Once run, also not for:
- a cause (§6.1);
- a validated coverage. A block built from the observed differences contains them by construction
  (`2d-closeout/playlist-term/REPORT.md:20`);
- an independent check of C_PL,5D. Every 12-playlist quantity uses the same events as the three-group block.

**Paths.**
- A bare `.md` or `.txt` name, and any path beginning `fd/`, is in `docs/orchestration/state/measurement-paper/5d-community-20261024/`.
- Paths beginning `docs/`, `nd-unfolding/` or `2d-unfolding/` are from the repository root.
- Paths beginning `2d-closeout/` or `measurement-paper/` are relative to `docs/orchestration/state/`.
- `DECISION-`, `QUESTION-`, `RECORD-` and `OUTCOME-` records are in `docs/orchestration/`.
- `$P` = `/pscratch/sd/j/josephrb`.
- `5B-run/` = `fd/receipts-ct/5b/run/`.

## 0. Summary

**The question.** The paper states two run-period limitations:
- `docs/analysis-note/paper_body.tex:112`, for the 2D result: one period group's unfolded p∥ distribution, relative to
  its own simulation, "differs from that of the earliest periods by a step of about 7% near 8 GeV/c. The cause is not
  known";
- `paper_body.tex:81`, for the 5D result, together with `docs/analysis-note/sec_fived16.tex:125`: C_PL,5D accounts for
  differences among the three run-period groups; "The cause is not known"; "with three groups its size is poorly
  determined: the 68% interval on the ratio of its true to its estimated size is 0.73–2.56".

**The campaign asks:**
1. Is the step carried by every resolved playlist of its period group, or by some of them?
2. Do the 16-cell playlist offsets differ between the period groups by more than playlist-to-playlist scatter would
   give?
3. If not, what size does the 12-playlist estimator give, and with what interval?

| stage | where | what | node-h |
|---|---|---|---|
| S | login | O_NOATIME staging copies, sha256-checked, of every pre-existing input (§1); the 12 per-playlist flux files built from the copies; F1 (§4) | 0 |
| 0 | login, after S | the dr_PB/PA p∥ step from 5B's existing period unfolds, with its bootstrap distribution (§3) | 0 |
| D | login, after 0 | the design-time simulations of R1 and R2 and their pre-job-B rules (§5) | 0 |
| A | 1 node | the 12 per-playlist inputs; K2′'s two unfolds; N0's 10 pseudo-playlist partitions built (§2, §4) | about 0.25 |
| C | login | C1, K2′, N0-P (§4); F1 ran at stage S | 0 |
| B | 1 node | 12 × 31 playlist unfolds, plus N0's 120 unfolds (§2, §4) | about 1.3 |
| R | login | N0's reading, then R1–R3 with the simulated nulls (§4, §5) | 0 |
| H | login | the HPSS copy, after maintenance ends 2026-11-06 17:00 (§8) | 0 |

**Price: about 1.55 node-h expected, at most 3.0** (§7). Every job is under 12 h, on CPU, at QOS regular.

## 1. Inputs, and why the zero loops

**MP-1's 12 zero per-playlist loops,** `$P/measurement-paper/phase1/mp1/s1/evloop/zero/runEventLoopOmniFold_5D_<PL>_zero.root`,
are pinned at `nd-unfolding/fd_ct_period_inputs.py` `ZERO_LOOPS` (sha256, login37, 2026-10-30). Their 4.84 GB in all is
`FD-CT-5B-DECLARATION.md:131`'s figure. `ls -l` on login23 on 2026-11-02 listed all 12.

**The evidence that they are the right CV inputs:**
- **5B's bound chain read them and reproduced MP-1's zero chain bitwise.** The ALL npz is byte-identical to
  `lat_zero.npz`, its background arrays are key-for-key `lat_zero_bkg.npz`'s (K1), and its unfold's `xsec_flat` is
  bitwise `mp1s1_zero`'s (K2) (`FD-CT-5B-REPORT.md:100-103`).
- **Their CV columns equal the bkgaware loops' for 1A.** The production bkgaware file's CV-pass rows (1,736,833) and
  `mc_background` rows (52,626) equal MP-1 S0's `base_cv` and W2b's `rrzero_1A`, in file order and as a multiset over
  all 15 CV columns. The two differ only by 454 per-universe branches (`FD-CT-5B-INPUTS.md:32-36`, citing
  `measurement-paper/phase1/mp1/S0-REPORT.md:58-76`).
- **Each zero loop equals W2b's rrzero pass of its playlist** under W2's `equal` rule (`FD-CT-5B-INPUTS.md:37-39`).
- **No per-playlist (e) unfold reads a universe branch.**
- **Size:** 4.5 GiB, against 159.4 GiB (`docs/orchestration/DECISION-20261101-joseph-eventloops-copy-to-cfs.md:8`).

**The fallback** is the CFS copy (#646), if a later step needs universe branches. It needs its own declaration. No
job reads CFS.

**Every input, all staged by stage S** (copies into `$R/staged/`, each opened with O_NOATIME and checked against its
pin):

| input | source | pin |
|---|---|---|
| 12 zero loops | as above | `ZERO_LOOPS` |
| 12 per-playlist baseline flux files | `$P/MINERvA-OmniFold/2d-unfolding/baseline_flux/` | part 2 records each sha256 |
| production flux | `$P/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root` | `d40aea69…` (`2d-closeout/period-unfold-20261014/scripts/periods.py` `PINS`) |
| 5B's period flux files | committed, `fd/receipts-ct/5b/flux/` | `FLUX` in `fd_ct_period_inputs.py` |
| 5B's period unfolds and MC truths, for PA, PB and PC (stage 0, K2′) | `$P/fd-ct-5b-20261030/unf/{PA,PB,PC}/`, `truth/truth_{PA,PB,PC}.npz` | `5B-run/preserve/INVENTORY.sha256` (51 rows) |
| 5B's PC lateral npz and background dump (K2′) | `$P/fd-ct-5b-20261030/dumps/` | the digests in `5B-run/inputs/check_PC.json` |
| MP-1's `lat_zero.npz` and `lat_zero_bkg.npz` (C1, N0), 1.55 GB (`FD-CT-5B-DECLARATION.md:258`) | `$P/measurement-paper/phase1/mp1/s1/lateral/` | `MP1_ZERO` (`6ca02c3d…`, `f09727d0…`) |
| S1's assembly | `$P/s1-20261024/s1_assembly.npz` | `db000707…` (`FD-CT-5B-DECLARATION.md:135`) |
| C_resp | `$P/cresp-20261026/out/cresp.npz` | `4d8b5797…` (same) |
| the 16-cell definition; 5B's period readout; 5A's readout | committed (`nd-unfolding/pv-ladder/readouts/h2_definition.json`; `fd/readout/fd_ct_5b_periods.json`; `fd/readout/fd_ct_period.json`) | git |

**The per-playlist flux files** are built on the login node from the staged copies, with the pinned combiner's reader
and arithmetic (2D's `build_flux.py`, `Φ_eff = Σ_p Φ_p POT_p / Σ_p POT_p` over one playlist).
- `build_flux.py` asserts the pinned combiner's fixed `BASE_FLUX` path. Part 2 must therefore point the reader at
  `$R/staged/`, without editing the pinned combiner, and test that. No pre-existing flux file is opened in place.
- **The reads.** After stage S, every step reads only staged copies or files this campaign made. No purge clock moves.
  No file is touched to reset its atime.
- **No default path is ever opened.** `nn_dump_inputs.py` and `s5p_input_dumps.py lateral` default `--mcfile` to a
  production-flux path: the deploy's own copy, and pscratch, respectively (`nd-unfolding/nn_dump_inputs.py:33`,
  `nd-unfolding/s5p_input_dumps.py:202`). Every step passes `--mcfile` explicitly. Part 2's submit stage
  refuses any step whose argv lacks it, or names a path outside `$R`, and a test covers that refusal.
- **The pscratch-only exposure.**
  - The zero loops have no HPSS or CFS copy and are exposed from 2026-12-15 (`FD-CT-RETENTION.md:63`). 5B's PC dumps and
    `lat_zero*` are on pscratch only.
  - All of them go on the post-maintenance HPSS catch-up list, with the flux files and this campaign's products (§8).
  - The jobs must run before 2026-12-15.

## 2. The chain

**Per playlist X ∈ {1A, …, 1P},** by 5B's tools with a single-playlist group in place of a period:

| step | tool | product |
|---|---|---|
| flux (login) | the reader above | Φ_X, with `DataPOTUsedForFluxWeighting` = X's data POT |
| dump | `nn_dump_inputs.py --axes eavail,q3,W --mcfile <Φ_X>` on X's staged zero loop | X's npz |
| lateral form | `s5p_input_dumps.py lateral --cv-npz <that npz> --mcfile <Φ_X>` | the npz in MP-1's lateral form, and its background dump |
| check | `fd_ct_period_inputs.py check` → `s5p_mc_truth_pred.py` | X's receipt and MC truth T_X |
| unfold | `fd_ct_period_inputs.py unfold` → `s5p_numerics.py` | (e): config R, 5 iterations, real data |

Part 2 settles whether 5B's `merge` runs on the single staged loop or is bypassed. Either way, `check` ties each dump to
its pinned loop, and the data POT to Φ_X's at 10⁻¹² relative.

**What the (e) unfold reads.** Config R replaces the npz's floor-at-zero `measured_weights` with the refinement's
weights (`nd-unfolding/s5p_numerics.py:112-116`, `nd-unfolding/s5e_trace.py:438-442`). So the per-bin max(0, data −
bkg)/data floor does not reach the unfold. Size-dependence through the refinement and the training is still possible,
and N0 measures it (§4).

**Unfolds:** per playlist, seed 42 and 30 bootstrap replicas (372).
- The replica seeds are 4000 + 100·i + k, with i = 1…12 the production-order index and k = 1…30. They are disjoint
  across playlists, so the replicas share no Poisson draws (5B's review M1, `FD-CT-5B-DECLARATION.md:644`).
- **Thirty replicas, not 10:** R2's null needs the per-playlist noise at more than 16 dimensions. Even at 30, a 16 × 16
  covariance from 29 dof is poorly conditioned. So R2 draws noise by resampling the replica deviations themselves,
  not from a fitted Gaussian (§5).
- **T_X is not resampled per replica,** as in 5B. Its MC-statistical variance per cell and per region (Σw² of the
  truth-selected weights) is computed from the npz. It is added to every noise σ and, on the diagonal, to every noise
  covariance, so the small playlists' finite MC is in the noise.
- `s5p_numerics.py` must be byte-identical to 5B's bound copy (part 2 pins it).

**Job geometry:** 5B's. One exclusive CPU node, 8 lanes of 32 CPUs and 56 GB, `--no-requeue`, account m3246, QOS
regular, no GPU. Steps refuse to overwrite, and there is no resume (`FD-CT-5B-DECLARATION.md:120-123`).

## 3. Stage 0: does the 5D chain see the step? (login, after S, before any job)

**What this lane had already read of 5B's published report:**
- its 16-cell tables. Their p∥ contrasts across 4.5 GeV/c are: dr_PB/PA +0.023% (z +0.06), dr_PC/PA +1.925% (z
  +6.05) and dr_PC/PB +1.902% (z +4.77); raw_PB/PA +3.329% (z +9.16) and raw_PC/PA +2.291% (z +7.17)
  (`FD-CT-5B-REPORT.md:149-154`);
- its per-cell double ratios (`FD-CT-5B-REPORT.md:147-178`).

The contrast across 4.5 GeV/c is not the step at 8 GeV/c: the 16 cells dilute a step inside [4.5, 60)
(`FD-CT-5B-REPORT.md:128`). No 5D quantity with an edge at 8 GeV/c has been computed. Since dr_PB/PA's 4.5 contrast is near zero, while the raw
PB/PA contrast is not, this lane's prior favours ABSENT or OTHER for the double ratio. It says so here.

**The statistic.** For a group Y, with unfold X_Y and MC truth T_Y on the fine grid, and a p∥ region R:
D_Y(R) = Σ_{c∈R} X_Y(c) / Σ_{c∈R} T_Y(c).
- The sums run over fine cells that map to a reporting cell (`fine_map` ≥ 0), as 5B's `contrast` sums cell integrals
  (`nd-unfolding/fd_ct_periods.py:310`, `contrast`).
- L = p∥ ∈ [1.5, 8) GeV/c and H = [8, 15) GeV/c, both unions of fine bins. The fine grid has edges at 8 and 15
  (`nd-unfolding/s5p_stage1_inspect.py` `FINE["pz"]`).
- The step is s_{Y/Z} = [D_Y(H)/D_Z(H)] / [D_Y(L)/D_Z(L)] − 1, the 2D test's form
  (`2d-closeout/period-unfold-20261014/REPORT.md:52`).

**How it differs from 2D's +6.94 ± 0.41%** (`2d-closeout/period-unfold-20261014/REPORT.md:57`):
- 5D sums over E_avail, q3 and W within the reporting cells, and excludes the 4 unreported H2 boxes
  (`nd-unfolding/pv-ladder/readouts/h2_definition.json` `unreported_boxes`);
- the estimator is 5D's config R, not 2D's;
- the p_T range is 5D's.

Each of these may dilute or change the step. **The SEES threshold of half of 2D's step allows up to 50% dilution;
this is a choice, made here.**

**Stage 0 reads** s₀ = s_{PB/PA} on 5B's seed-42 period unfolds.
- **σ₀** is the RMS about s₀ of the 10 replica-pair steps, 5B's replica k of PB with replica k of PA (k = 1…10), over 10
  with no ddof. That is 5B's convention, RMS about the base value (`nd-unfolding/fd_ct_periods.py:344-349`).
- (e)'s seed term is zero by construction (`FD-CT-5B-REPORT.md:127`).
- With 10 replicas, an SD is uncertain by about ±22% (`2d-closeout/period-unfold-20261014/REPORT.md:72`).

**The reading, fixed here:**

<!-- absence-ok: decision rules fixed in advance (what each branch computes and licenses), not claims that a result does not exist -->
| branch | rule | lines it may move |
|---|---|---|
| **SEES** | s₀ ≥ +3.47% and s₀/σ₀ ≥ 5 | R1 is read (§5). §6.1's R1 sentences may move **line 112**, and their 5D form may move **`sec_fived16.tex:125`**. R2 and R3 may move line 81 and `sec_fived16.tex:125`'s size clause, as in every branch |
| **ABSENT** | \|s₀\|/σ₀ < 3 | R1 is not computed. Nothing moves line 112 from this campaign. R2 and R3 may move only **line 81** and `sec_fived16.tex:125`'s size clause. Localizing line 112's step needs 2D per-playlist unfolds (§9) |
| **OTHER** | neither, including a significant negative step (s₀/σ₀ ≤ −3), which is reported with its sign | as ABSENT |

<!-- absence-ok: what the declared rule does in that band (a decision rule fixed in advance), not a claim that a result does not exist -->
- **OTHER includes a band that this rule accepts losing:** a significant positive step that is diluted below half of
  2D's (s₀/σ₀ ≥ 3 and s₀ < 3.47%), or one that is large but at 3 ≤ s₀/σ₀ < 5. In that band the 5D chain sees something,
  but R1 is not computed and line 112 is not moved. The value is reported with its sign and z.
- **Stage 0 runs before job A,** so an ABSENT or OTHER branch reaches the director at 0 node-h.
- **The jobs still run in every branch** unless the director says otherwise, because R2 and R3 address line 81.

## 4. Controls (each a stop, reported unrepaired, unless marked)

**F1, the flux** (login, stage S).
- For each period, the data-POT-weighted combination of its playlists' Φ_X must equal 5B's committed period flux file,
  bin by bin, to 10⁻¹² relative, with its POTs.
- For ALL it must equal the staged production flux `d40aea69…` the same way.
- F1 shows the per-playlist files combine to the period files. It does not show that playlists sharing a flux file
  have equal per-playlist baseline fluxes. §6 therefore says only "reweighted to the same flux file", never "the same
  simulated flux".

**C1, the partition** (login, after job A). The 12 per-playlist lateral npz files and background dumps are compared
with MP-1's `lat_zero.npz` and `lat_zero_bkg.npz`.
- s_X = data_pot_X / mc_pot_X is X's own POT scale. Both POTs are read from X's staged zero loop (`dataPOTUsed`,
  `mcPOTUsed`; `2d-unfolding/unfold_2d_omnifold_unbinned.py:117-126` reads them the same way) and recorded in
  X's receipt.
- s_ALL = Σ_X data_pot_X / Σ_X mc_pot_X over the 12 staged loops. `lat_zero`'s weights were scaled by the merged ALL
  file's POTs, so the weight predicate below also tests that hadd adds `mcPOTUsed`. If it did not, the predicate
  fails. Additivity is tested here, not assumed.
- All weights are float64 products w × pot_scale (`nd-unfolding/unfold_nd_omnifold_unbinned.py:338, 438, 567`).

| key (from `NPZ_KEYS`, `BKG_KEYS`) | predicate |
|---|---|
| `MCgen`, `MCreco`, `measured`, `pass_reco`, `pass_truth`, `bkg_reco` | concatenated in production order: **bitwise equal** |
| `w_truth`, `w_reco`, `bkg_w` | concatenated: within X's slice, **equal to `lat_zero`'s × (s_X / s_ALL)** to 10⁻¹² relative per event, and exactly equal where `lat_zero`'s weight is 0 |
| `denom_nd`, `bkg_nd` (histograms) | **Σ_X (s_ALL / s_X) · H_X equals H_ALL** to 10⁻⁹ relative per non-empty bin. 10⁻⁹ allows the summation order; empty bins equal exactly |
| `data_pot` | Σ_X data_pot_X = ALL's, to 10⁻¹² relative |
| `axes`, `edges_*`, `nedges`, `n_nucleons` | **equal** in every file |
| `flux` | **equal bin by bin to the staged Φ_X's** integrated flux, to 10⁻¹² relative. This catches a dump that took a default `--mcfile` |
| `measured_weights` | **differs by construction.** It is a per-bin function of X's own data and background histograms (`unfold_nd_omnifold_unbinned.py:581-602`), and the (e) unfold does not read it (§2). C1 instead recomputes it from X's own arrays and requires equality to 10⁻¹² (self-consistency). Its difference from ALL's is printed, not graded |

A key outside this table stops part 2's review. If C1 passes, the per-playlist inputs are a partition of the inputs
whose unfold is `mp1s1_zero`, with the weights and histograms renormalized per playlist as stated. Nothing more is
claimed.

**K2′, the deploy** (job A, one lane; graded at stage C).
- This deploy unfolds 5B's staged PC inputs at seed 42.
- **Its `xsec_flat` must be `np.array_equal` to that of 5B's `unf/PC/5b_PC_b-_j-.npz`** (INVENTORY row `e0594420…`).
  This is an array comparison, as 5B's K2 (`nd-unfolding/fd_ct_periods.py:255`). File bytes differ by design: the
  product's metadata carries the job and timings.
- **And for one replica:** this deploy's unfold of the same inputs at 5B's replica seed 3001 must be `np.array_equal` to
  5B's `unf/PC/5b_PC_b3001_j-.npz` (its INVENTORY row). This grades the bootstrap path that 360 of
  the 492 unfolds take.
- Cost: about 2 × 140 s of one lane (`5B-run/lanes-periods/line1-60549044.log`).

**N0, the estimator-size null** (built in job A, unfolded in job B, read first in stage R; this answers audit 1's
finding 6 and audit 2's M2, M3 and m4).

**What it builds:** from the staged `lat_zero` inputs, **10** random partitions of ALL into 12 pseudo-playlists at the
real shares e_X.
- Data rows, signal-MC rows and background rows are each assigned by a multinomial draw at e, with seeds 20261102 + p
  for partition p = 1…10. MC is split in the same proportion, so per-event weights are unchanged.
- Each pseudo-playlist's `data_pot` is e_X × ALL's. Its `flux` is ALL's: the true offsets are zero, and the true flux
  is common.
- **`denom_nd` keeps the completeness exactly.** The unfold forms comp = O / `denom_nd` per cell, where O is the binned
  truth-weight sum of the signal rows (`nd-unfolding/s5e_trace.py:287-290`). A scaled `denom_nd` against a randomly
  split O would let comp exceed 1 in sparse cells. So each pseudo-playlist k takes
  `denom_nd`_k = `denom_nd`_ALL × O_k / O_ALL where O_ALL > 0, and e_k × `denom_nd`_ALL elsewhere. Its completeness then
  equals ALL's in every cell.
  - **The consequence:** N0 carries no finite-MC completeness noise. A real playlist does carry it, through T_X's MC
    variance (§2).
- `bkg_nd` is the background histogram of each pseudo-playlist's own background rows. Each background dump's
  `meta.npz_sha256` names its own pseudo-npz, as `s5p_numerics.py` requires (`nd-unfolding/s5p_numerics.py:160-172`).
  The unfold is given the expected digests from N0's receipt.
- Each pseudo-playlist is unfolded once at seed 42: **120 unfolds**.

**N0-P, the partition control** (login, stage C; it is in job B's gate). In each partition:
- the 12 pseudo-npz files' per-event rows, put back in their original order, equal `lat_zero`'s bitwise in every
  per-event key;
- the row counts per tree sum to ALL's;
- Σ_k `data_pot`_k equals ALL's to 10⁻¹² relative;
- Σ_k `denom_nd`_k and Σ_k `bkg_nd`_k equal ALL's to 10⁻⁹ relative per non-empty bin;
- each pseudo-playlist's realized data share is within 5 multinomial σ of e_k;
- each background dump's meta names its pseudo-npz.

**The reading, fixed here.** Take the three smallest-share pseudo-playlists (the analogues of 1L, 1B and 1O, all with
e < 0.03) over the 10 partitions: 30 draws.
- b̄ is their mean 16-cell offset g (each against its own partition's m), with SE = SD(ddof 1)/√30.
- b̄_t is their mean R1 step t (each against its own partition's pseudo-A*), with its SE.
- **SIZE-BIAS-g** fires if any cell has |b̄_c| / SE > **3.835**, the t₂₉ two-sided quantile at 0.01/16.
- **SIZE-BIAS-t** fires if |b̄_t| / SE > **2.756**, the t₂₉ two-sided quantile at 0.01.
- The family false-fire level is about 0.02 if the cells are independent **(arithmetic)**.
- **Power:** treating the 30 draws as independent, a cell bias of 0.75 or 1.0 single-draw σ is caught with
  probability about 0.61 or 0.93, and a step bias of 0.5 or 0.75 σ with about 0.50 or 0.90 **(arithmetic, noncentral
  t)**. The single-draw σ of a small playlist's cell offset is printed. The detectable bias is printed in that σ and in
  % of the cell offset.
- **Not firing is not a clearance.** It means no bias at those sizes was seen.
- The slopes of g and t against e over all 120 pseudo-playlists are printed.

**The consequence, by trigger:**
- **SIZE-BIAS-g:** R2 and R3 are **INCONCLUSIVE**, because size and offset cannot be separated on the 16 cells. Every
  playlist with e < 0.03 is also **UNRESOLVED** in R1.
- **SIZE-BIAS-t** alone: every playlist with e < 0.03 is **UNRESOLVED** in R1. It does not touch R2 or R3.
- **Neither:** N0's 10 values of F (§5) are printed beside R2's null. That is descriptive.
- UNRESOLVED playlists still enter A* and t̄ at their exposure weights, which are each below 0.03.

**The limit.** Each real playlist has its own MC sample and MC/data ratio, while N0 splits ALL's MC in proportion. So
N0 measures size-dependence at proportional MC only.

**Gates:** job B is submitted only after F1 (stage S), and C1, K2′ and N0-P (stage C), pass on this deploy's records,
through a gate in the submit stage, as in 5B. The pre-job-B decision rules of §5 are applied and reported to the
director at stage D, before job A.

**Q3** (readout): every unfold and MC-truth integral is positive and finite on L, on H and on each reporting cell.

**The leak guard:** every output passes F0's `LeakGuard`, as in 5B.

## 5. The readouts (login, after job B and N0), fixed before any playlist number is read

**Notation.**
- r_X = X_X / T_X, on the 16 reporting cells (as 5B's readout forms it) and on L and H.
- **e_X** is X's exposure share, POT_X Φ_X / Σ_Y POT_Y Φ_Y. The flux is constant over p_T (to 10⁻¹⁴, `FLUX_FLAT` in
  `fd_ct_period_inputs.py`), so e is the same in every cell. The readout asserts that, because R3's rank bound of 11
  depends on it.
  - Approximately, e runs from 0.0127 (1L) to 0.1575 (1F): 5B's period shares split by data POT
    (`2d-closeout/playlist-spread-20261014/outputs/potcheck.json`).
- Replica k of any combination uses replica k of every member. Every noise σ includes T_X's MC variance (§2).

### R1, where the step is (fine p∥; computed only under stage-0 SEES)

**The reference** A*_X is the exposure-weighted combination of the 1A–1F playlists' D values. It is 2D's reference,
"the earliest periods".
- On each region R, D_{A*}(R) = Σ_Y e_Y D_Y(R) / Σ_Y e_Y over 1A–1F, leaving X out when X is in 1A–1F. That is the
  exposure-weighted mean of the double ratios, the form of R2's m.
- PB* combines 1G, 1L and 1M the same way.

**The noise convention, for all of R1.** Every σ is the sample SD (ddof 1) of the quantity's 30 replica values about
their own mean. T's MC variance is added in quadrature: the Σw² of each member's truth-selected weights in L and in H,
propagated to first order through the step formula.

**The quantities:**
- t_X = s_{X/A*_X}, with σ_X from the 30 replicas;
- **t̄** = the recombined 1G/1L/1M step against A*: s_{PB*/A*}, where PB* is the exposure-weighted combination of
  1G, 1L and 1M. It is the scale, so 5B's pooled s₀, whose mix effect differs, is not used here;
- d_X = t_X − t̄, with σ_d,X the SD of d_X over the replicas. That SD carries t̄'s noise and its correlation with
  t_X.

R1 is computed only if t̄ > 0 and t̄ / σ(t̄) ≥ 3. Otherwise it is **NOT COMPUTED**, and no R1 wording is licensed.

**Classes,** for each X:
- **UNRESOLVED** if max(σ_X, σ_d,X) ≥ t̄/4, or if N0's SIZE-BIAS-g or SIZE-BIAS-t fired and e_X < 0.03 (§4);
- **CARRIES** if |d_X| ≤ 2σ_d,X;
- **FREE** if |t_X| ≤ 2σ_X;
- **PARTIAL** otherwise.

For a resolved X, CARRIES and FREE are disjoint: t_X then lies within 2σ < t̄/2 of both t̄ and 0, which cannot happen.

**Patterns, a partition evaluated in this order.** The first that holds is the outcome:
1. **PERIOD-WIDE:** at least two of 1G, 1L and 1M are resolved, and every resolved one of the three CARRIES; and at
   least one 1A–1F playlist is resolved and every resolved one is FREE.
2. **SUBSET:** among 1G, 1L and 1M, at least one resolved playlist CARRIES, at least one resolved playlist is FREE and
   none is PARTIAL; and at least one 1A–1F playlist is resolved and every resolved one is FREE.
3. **OTHER:** everything else.

Rules 1 and 2 cannot both hold, because 1 requires all resolved 1G/1L/1M to CARRY and 2 requires one to be FREE.
Part 2's tests enumerate every class assignment of the nine playlists 1A–1M (UNRESOLVED, CARRIES, FREE and PARTIAL)
and assert exactly one outcome for each. 1N–1P are printed with their classes and enter no pattern.

**Operating characteristics, and a rule that uses them (stage D, login, after stage 0, before job A).**
- **The design σ.** σ²(t_X) ≈ σ_u² (1/e_X + 1/e_ref), with σ_u fixed so that the PB/PA period step's σ equals stage 0's
  σ₀ at the period shares. No playlist number is used.
- **The table:** the pattern probabilities under four declared truths, PERIOD-WIDE and SUBSET with only 1G, only 1L or
  only 1M carrying, each at t̄ = 3.5% and 7%, from 20,000 Gaussian draws (seed 20261102).
- **The rule, fixed here:** if P(PERIOD-WIDE | the PERIOD-WIDE truth at t̄ = 7%) < 0.5, R1 is **DROPPED** before job A.
  Its classes are still printed at readout, but no R1 wording is licensed. The stage-D report goes to the director
  before job A is submitted.
- **At readout,** the table is printed again with the measured replica σ. It is descriptive and changes no outcome.
- The rough scaling (audit, finding 11) puts 1L and 1B, and probably 1O, as UNRESOLVED at any t̄ below about 6%. If so,
  PERIOD-WIDE then rests on 1G and 1M, and that is stated here.
- **Multiplicity.** About 12 playlists × 2 two-sided 2σ tests. The OC table gives the resulting chance of OTHER under
  each truth.

### R2, do the 16-cell offsets differ between the period groups? (read in every branch)

**The offsets.** g_X = r_X / m − 1 per cell, with m = Σ_X e_X r_X over all 12, so that Σ e_X g_X = 0. For a partition π
into groups g with shares E_g:
- G_g = Σ_{X∈g} e_X g_X / E_g;
- Q_b(π) = Σ_g E_g G_gᵀ M⁻¹ G_g;
- Q_tot = Σ_X e_X g_Xᵀ M⁻¹ g_X;
- F(π) = Q_b(π) / Q_tot.

M = (C_total + C_resp)/(f fᵀ), 5B's metric.

**The test.** p_flux is the fraction of the 9,240 distinct partitions of sizes (6, 3, 3) with F(π) ≥ F(π_flux).
- Ties count, and π_flux itself is included.
- π_flux is the flux-file grouping {1A–1F}, {1G, 1L, 1M}, {1N, 1O, 1P}, which the analysis takes from the reweighter
  (`2d-closeout/playlist-spread-20261014/REPORT.md:152-160`; `2d-closeout/period-unfold-20261014/scripts/periods.py:1-4`).
- **The permutation is approximate, not exact.** The playlists move with their weights e_X, and their noise depends on
  e_X, so the labels are not exchangeable under the null. The test's validity rests on the simulated null below.

**Beside it, descriptive, with no outcome:** p_era, over the 83,160 distinct partitions of sizes (5, 2, 2, 3), for the
beam-intensity grouping {1A–1E}, {1F, 1G}, {1L, 1M}, {1N, 1O, 1P}. It follows the mean `numi_pot` of about 23, 28, 38–39
and 36–48.5 × 10¹² (`2d-closeout/playlist-spread-20261014/REPORT.md:186-188`). It shows whether flux-file grouping and
beam era can be told apart. Nothing is licensed from it.

**The simulated null and the power.** NumPy seed 20261102; 2,000 datasets per point. Each dataset draws, per playlist,
r_X = μ ∘ (1 + δ_X + ε_X), then forms m and g as the data do:
- **μ** = the observed m, so only the shape enters F;
- **ε_X** is one of X's 30 replica deviations (replica minus the replica mean, × √(30/29)), drawn at random. Its T_X
  MC variance is added as an independent Gaussian on the diagonal;
- **δ_X** comes from the model under test.

**Calibration (null S0):** δ_X iid N(0, a·Σ_δ), at a ∈ {0, 0.5, 1, 2}.
- Σ_δ is the exchangeable model's per-playlist offset covariance: Σ_X e_X g_X g_Xᵀ / (1 − V2), less the same
  statistic averaged over noise-only datasets, then projected onto the PSD cone. The discarded trace is printed.
- α̂(a) is the share of datasets with p_flux < 0.05. **Calibrated** iff α̂(a) ≤ 0.0646 at every a.
- The gate passes a true size of 0.060 about 82% of the time, and 0.070 about 18% (audit, §3).

**Power (S1, the observed period structure, held fixed):** δ_X = c Ĝ_{P(X)}, with no within-period offsets.
- Ĝ_P are the three observed period offsets: the per-playlist-recombined period double ratios over m, minus 1. They are
  vectors on the 16 cells, not a random draw.
- c = √max(0, 1 − Q̄_noise / Q_b(π_flux)) shrinks them by their noise share. Q̄_noise is Q_b(π_flux)'s mean over the
  noise-only datasets.
- β̂₁ is the share of datasets with p_flux < 0.05.
- This replaces revision 2's rank-2 Gaussian draw, whose scale mixture capped the power below 0.8 by construction
  (audit 2, M1).
- With S1 fixed, EXCHANGEABLE-COMPATIBLE needs two things: a period structure large enough to be detected if it were
  all there was (β̂₁ ≥ 0.80), and within-period scatter large enough to hide it (p_flux ≥ 0.05). Both can hold.

**Second alternative (S2, mixed), descriptive:** δ_X = (c/√2) Ĝ_{P(X)} + w_X, with w_X iid N(0, ½Σ_δ). Its β̂₂ is
printed and decides nothing.

**Plug-ins.** Σ_δ, Ĝ and c come from the same 12 playlists that are tested. If the period structure is
noise-dominated, c ≈ 0 and β̂₁ ≈ α, and EXCHANGEABLE-COMPATIBLE cannot occur. That is stated, and it is the right
answer: no clustering would have been detectable.

**Reachability, before job A (stage D).** The design-time simulation runs with the real M and e, and noise scaled from
5B's committed period noise by 1/e (`fd/readout/fd_ct_5b_periods.json`). It prints P(CLUSTERED), P(EC) and
P(INCONCLUSIVE) under three declared truths, using 500 outer datasets, each with the full S0/S1 machinery at 200 inner
datasets:
- **T1, exchangeable:** iid playlist offsets whose three-group block has C_PL,5D's size;
- **T2, clustered:** 5B's period offsets g_X (committed in that readout), held by every playlist of the period;
- **T3:** half of each.

**The rule, fixed here:** if P(EC | T1) < 0.2, the stage-D report states that the 12-playlist wording (§6.2's EC rows)
is not expected to be reachable. R3 is still printed: it costs no node-h. The director may then re-scope before job A.

**Outcomes, a partition evaluated in this order:**
1. **INCONCLUSIVE:** N0's SIZE-BIAS-g fired; or the test is not calibrated; or neither of the next two holds.
2. **CLUSTERED:** calibrated and p_flux < 0.05.
3. **EXCHANGEABLE-COMPATIBLE:** calibrated, p_flux ≥ 0.05 and β̂₁ ≥ 0.80. This means the observed period structure,
   which would have been detected on its own, is hidden by within-period scatter. It does not show that the offsets
   are exchangeable.

**Compute on the login node.** About 1.1 × 10⁸ evaluations of F at the readout: 2,000 datasets × 9,240 partitions ×
6 points. Stage D's 500 outer datasets, each with 5 × 200 inner, cost about 5 × 10⁹. Each evaluation is a whitened group sum on 16 cells, so
the work is vectorized. Each run is bounded at 2 h under `nice -n 19` on one login node; past that it stops and is
reported **(estimate)**.

### R3, the size from twelve playlists (always printed; read only under EXCHANGEABLE-COMPATIBLE)

- **The block:** C_PL,12 = Σ_X k₁₂ e_X (f ∘ g_X)(f ∘ g_X)ᵀ, with k₁₂ = V2₁₂ / (1 − V2₁₂), by the estimator of
  `2d-closeout/playlist-term/DESIGN.md` §2. It is printed in relative form through the leak guard.
- **Its noise expectation** is the same estimator on noise-only datasets. The block is printed raw, and debiased and
  PSD-projected with the discarded trace.
- **ν₁₂** = (1 − V2)² / (V2 − 2Σe³ + V2²), with the 68% interval of σ_true/σ_hat from χ²_ν, the formula of the 5D label
  (`nd-unfolding/fd_ct_5b_audit.py:94`).
  - With 5B's three shares it reproduces 1.824 and 0.73–2.56. With the approximate twelve shares it gives 7.98 and
    0.82–1.38 **(arithmetic)**.
  - **The interval depends on e only.** It assumes iid homoscedastic offsets, and it is printed with that label.
- **The size comparison, both pairs named:**
  - ρ_raw = √(tr M⁻¹ C_PL,12,raw / tr M⁻¹ C_PL,5D), raw against raw, since C_PL,5D is undebiased;
  - ρ_deb = the same with both debiased, the 5D block's noise expectation coming from 5B's replicas.
  - Each is printed with per-cell ratios (median, min, max) and its replica-noise reference.

## 6. What the paper may say, decided now

The paper lane drafts, the director reviews and Joseph reads (#690 item 2). These are the **only** changes each outcome
licenses. Everything not listed stays.

**No licensed sentence may suggest that the 12-playlist estimate is independent of the three-group block, or name a
cause.**

### 6.1 "The cause is not known" (lines 81 and 112, `sec_fived16.tex:125`)

**No outcome of this campaign licenses dropping it.**
- A localization says where a difference is, not why. Dropping the clause needs a named mechanism whose predicted
  effect matches the localization and size, tested by its own declared step.
- The two routes to one on record are outside this campaign:
  - an answer from MINERvA. The prepared question (`docs/orchestration/QUESTION-20260920-hadronic-response-coverage-for-eavail-w.md:8`)
    is "PREPARED, NOT SENT", and it concerns hadronic response; sending it is Joseph's act;
  - a declared mechanism test that a localization points to.

**R1 sentences, only under stage-0 SEES and if R1 is not DROPPED.** Each lists every playlist's class from the readout.
In line 112 the sentence is appended after "…these data cannot establish which period is correct." In
`sec_fived16.tex:125` it is appended after "…if any, is right.":

| R1 pattern | line 112 (2D) | `sec_fived16.tex:125` (5D) |
|---|---|---|
| **PERIOD-WIDE** | append: "In the five-dimensional analysis the step appears in each of that group's playlists that the data resolve ([1G/1L/1M list]), which the simulation reweights to the same flux file; no step larger than half of it is seen in the resolved earlier playlists ([1A–1F list]); [list] are not resolved. The cause is not known." | the same sentence, in that section's terms |
| **SUBSET** | append: "In the five-dimensional analysis, of that group's playlists, which the simulation reweights to the same flux file, the step appears in [CARRIES list] and no step larger than half of it is seen in [FREE list]; nor in the resolved earlier playlists ([1A–1F list]); [list] are not resolved. The cause is not known." | the same |
| **OTHER** or **NOT COMPUTED** | no change | no change |

"Reweights to the same flux file" is the code's grouping (`2d-closeout/playlist-spread-20261014/REPORT.md:152-160`).
It is stated as a fact about the analysis, not as a cause. F1 does not test the per-playlist fluxes' equality (§4).

### 6.2 "With three groups its size is poorly determined" (line 81; `sec_fived16.tex:125`)

| R2 outcome | licensed |
|---|---|
| **CLUSTERED** | the clause stays. One may be added: "The offsets of the twelve playlists differ between the three period groups by more than their playlist-to-playlist scatter would give." Nothing is added about whether every playlist shares its group's offset |
| **EXCHANGEABLE-COMPATIBLE**, (ii) C_PL,5D stays the reported block | the clause stays. One may be added: "An estimate from the twelve playlists, using the same events, is [ρ_raw] times the block's size (raw to raw). If the playlists' offsets were exchangeable with equal variance, that estimator's 68% interval would be [a]–[b]; it depends only on the exposure shares." |
| **EXCHANGEABLE-COMPATIBLE**, (i) Joseph adopts C_PL,12 (a covariance change, his) | **this re-opens line 81's block description and `sec_fived16.tex:125`**: the rank, "three groups", the reliability-weight factor, the audit narrative and the noise-dominated cells. The paper lane redrafts them for the director and Joseph. Nothing here recommends adoption: choosing a block after seeing its size is the post-hoc question line 81 already discloses |
| **INCONCLUSIVE** | no change |

### 6.3 Joint table (stage-0 branch × R1 × R2)

R1 is a statement about the fine p∥ step at 8 GeV/c. R2 is a statement about the 16-cell offsets. Every licensed sentence
names its quantity, so the pairs below do not contradict each other.

| stage 0 | R1 | R2 | licensed |
|---|---|---|---|
| SEES | PERIOD-WIDE or SUBSET | CLUSTERED, EC or INCONCLUSIVE | R1's sentence and R2's row, each with its own quantity |
| SEES | OTHER or NOT COMPUTED | any | R2's row only |
| ABSENT or OTHER | not computed | any | R2's row only. Line 112 is unchanged |
| any | any | INCONCLUSIVE because of SIZE-BIAS-g | R1's sentence (if licensed by the rows above) lists every playlist below e = 0.03 as not resolved. R2's row licenses nothing |
| any | DROPPED at stage D | any | R2's row only |

### 6.4 What no outcome licenses

- "validated", "covers" or "coverage" of either block;
- "which period is correct";
- a change to line 81's "is not corrected for the bootstrap noise it contains", unless the reported block changes. R3's
  debiased form is printed beside it.

## 7. Price

From 5B's measured units:
- **Unfolds** (`5B-run/lanes-periods/line{0..7}-60549044.log`): PA (e ≈ 0.53) about 400 s, PB (0.29) 231–236 s, PC (0.17)
  133–142 s on a 32-CPU lane. That is about 780 s × e + 10 s, slightly conservative against the logged times (audit,
  §3). So one round of 12 (pseudo-)playlists takes about 900 lane-s.
- **Inputs:** 5B's ALL lane (all the data) took merge 3:00, dump 7:12, lateral 7:06 and check 3:14 (`FD-CT-5B-REPORT.md:87`).

| job | geometry | projected | limit, so at most |
|---|---|---|---|
| A: 12 input lanes, K2′'s two unfolds, N0's 10 partitions | one node, 8 lanes | about 15 min, so 0.25 node-h **(estimate: per-step start-up and N0's split unpriced)** | 1:00:00, so 1.0 |
| B: 372 + 120 unfolds | one node, 8 lanes, longest first | 41 × 900 / 8 ≈ 4,610 s, so about 1.28 node-h **(estimate)** | 2:00:00, so 2.0 |

**About 1.55 node-h expected, at most 3.0.** The login stages charge nothing. The inventory's guess was about 3–4
(`inventory-answer.txt:133`).

**Stops:** any refusal, any non-zero exit, a lane without its products, a job past its limit, or a FAIL of F1, C1 or
K2′ is reported unrepaired. Each of these stops the campaign before job B. A rerun needs the director and a new `$R`.

## 8. Ledger, storage and HPSS

- `$R` = `$P/fd-rpd-<date>/`, which must not exist beforehand.
- **HPSS is deferred** under `docs/orchestration/RECORD-20261102-director-hpss-deferral.md` (#685) until 2026-11-06
  17:00. That record names other campaigns only. **The binding must extend it to RPD,** under the director's ruling 1
  (`FD-RPD-RULINGS-20261102.txt`). The catch-up archive gains:
  - the 12 zero loops (4.84 GB);
  - 5B's PC dumps;
  - `lat_zero*` (1.55 GB);
  - the flux files;
  - the 492 unfolds, the 12 playlists' MC truths and the 120 pseudo-playlists' MC truths;
  - N0's receipts and seeds. N0's pseudo-npz files and background dumps (about 15.5 GB **(estimate: 10 × 1.55 GB)**)
    stay on pscratch, rebuilt from `lat_zero` and the seeds;
  - the control records and the readout.

  The procedure is the bound one.
- **Committed in the report's PR:** the readouts, logs, `sacct`, receipts, the products' sha256 list and ledger rows.
  The per-playlist dumps stay on pscratch, rebuilt from the loops by job A.
- `$R` goes on the pscratch retention list.

## 9. Scoped separately: 2D per-playlist unfolds (if stage 0 is ABSENT or OTHER)

**The case for them.** Line 112's step is a 2D result. If the 5D chain does not show it, localizing it needs RE-2's
estimator on 12 per-playlist 2D inputs.

**Price, from RE-2's J8:** 37 period unfolds, 1.1358 node-h (job 60195845), so 0.0307 node-h per run; the steps' mean is
0.0274 (0.0196–0.0553) (`2d-closeout/stageF/methods/re2/RE2-PARTB-REPORT.md:52-64`, with per-run figures from its
`steps.psv`).
- 372 runs would cost about 11.4 node-h at J8's mean charge per run, and 7.3–20.6 at its minimum and maximum step.
  132 runs (10 replicas) would cost about 4.1, or 2.6–7.3 **(arithmetic; a playlist run is smaller than a period run,
  so the mean figure is an upper estimate)**.
- **Inputs:** the 12 per-playlist 2D CV omnifiles exist on pscratch, exposed from about 2026-12-10 (`ls`/`stat`,
  login23, 2026-11-02; `COV2D-SCOPING.md` §7–8).
- It would need its own declaration and audit.

## 10. For the director

1. **Two audits:** this design part, then part 2 (the code), before binding.
2. **Thirty replicas,** against 5B's ten (+0.63 node-h), and **N0** with 10 partitions (+0.31 node-h).
3. **Stage 0's thresholds,** R1's 2σ and t̄/4, R2's 0.05 and 0.80, N0's t₂₉ thresholds, and stage D's 0.5 and 0.2 are
   choices fixed here.
4. **The three departures** from the decision's and the director's wording (top). They are for Joseph.
5. **Stage D reports to you before job A.** Its two rules may drop R1, or flag the 12-playlist wording as unreachable.
   You may re-scope then.

## 11. Not changed

The paper, the note, every covariance and block, 5B's records, the CFS copy and the retention list. No run is
authorized.

## 12. Audit 1 dispositions (`FD-RPD-AUDIT-1-SONNET-ANSWER.txt`)

| # | severity | disposition |
|---|---|---|
| 1 | BLOCKING | **Accepted.** §4 C1 gives every key its predicate, from `nn_dump_inputs.py:62-101` and `unfold_nd…py:338/438/567/581-602`. `measured_weights` is self-consistency only, and is not read by (e) (§2). "Otherwise unchanged" is dropped |
| 2 | BLOCKING | **Accepted.** K2′ is `np.array_equal` on `xsec_flat` against `unf/PC/5b_PC_b-_j-.npz`, which is staged |
| 3 | BLOCKING | **Accepted.** The patterns are an ordered partition. PERIOD-WIDE and SUBSET need a resolved 1A–1F playlist, and SUBSET forbids PARTIAL in 1G/1L/1M. An enumeration test goes in part 2. The edge case σ = t̄/4 is UNRESOLVED |
| 4 | MAJOR | **Accepted.** §6.3's joint table. The CLUSTERED sentence is reworded so it names no sharing claim, and every sentence names its quantity |
| 5 | MAJOR | **Accepted.** The test is called approximate, and the null is run at four scales. The noise is resampled from the replicas |
| 6 | MAJOR | **Accepted in substance.** The floor-at-zero mechanism does not reach (e) (§2), but size-dependence through refinement and training remains. N0 measures it, with a fixed consequence |
| 7 | MAJOR | **Accepted.** Σ_X is specified (draw r, then form g; replica resampling), with the 4-point grid and S2. EC's meaning is stated, as is its possible unreachability |
| 8 | MAJOR | **Accepted.** "Reweights to the same flux file", F1's limit stated, every playlist's class listed, the CLUSTERED rewording, and p_era beside p_flux (descriptive) |
| 9 | MAJOR | **Accepted.** σ₀ is the RMS about s₀ over 10; negative steps fall in OTHER; the dilution sources are listed; the 5B reading is disclosed; the SEES row and §6.1 name the same lines |
| 10 | MAJOR | **Accepted.** ρ_raw and ρ_deb, both named; the interval depends on e only; "same events"; adoption (i) re-opens the section |
| 11 | MAJOR | **Accepted.** t̄ is recombined, with σ_d carrying the correlation; R1 is computed only under SEES with t̄/σ ≥ 3; an OC table comes before binding (part 2) and is repeated at readout; multiplicity is stated |
| 12 | MINOR | **Accepted.** S comes before stage 0; the flux is built from staged copies; the production flux is staged |
| 13 | MINOR | **Accepted.** The rulings are verbatim in `FD-RPD-RULINGS-20261102.txt`, and the departures are named at the top for Joseph |
| 14 | MINOR | **Accepted.** The Paths rule is extended, and every path was re-cited |
| 15 | MINOR | **Accepted.** "Distinct partitions", with the tie rule |
| 16 | MINOR | **Accepted.** F1 is relative |
| 17 | MINOR | **Accepted.** e is asserted cell-independent; T_X is not resampled, and its MC variance is added |
| 18 | NIT | Noted: 0.63 node-h |

## 13. Audit 2 dispositions (`FD-RPD-AUDIT-2-SONNET-ANSWER.txt`, of revision 2 `9fc61f3e…`)

| # | disposition |
|---|---|
| M1 | **Accepted.** S1 is the observed period structure, held fixed and noise-shrunk (§5 R2). A reachability simulation under three declared truths runs at stage D, with a rule that tells the director before job A if EC is not expected |
| M2 | **Accepted.** 10 partitions (30 draws); t₂₉ thresholds 3.835 and 2.756; family level about 0.02; power stated; "not firing is not a clearance" |
| M3 | **Accepted.** `denom_nd` is ratio-preserving, so completeness equals ALL's (its consequence stated); flux is ALL's; background-dump meta and expected digests are covered; N0-P is in job B's gate |
| M4 | **Accepted.** mc_pot is read from the staged loops; s_ALL is the sum over playlists, so hadd additivity is tested by the weight predicate; zero weights compare exactly |
| M5 | **Accepted.** C1 compares the npz `flux` with the staged Φ_X; every step passes `--mcfile` explicitly and is refused otherwise (part 2 tests it) |
| M6 | **Accepted.** The flux clause is confined to 1G/1L/1M; "no step larger than half of it is seen in" replaces "not in" |
| M7 | **Accepted.** The sentence carries "If the playlists' offsets were exchangeable with equal variance" |
| M8 | **Accepted.** The OC table is computed at stage D with a rule: P(PERIOD-WIDE \| PERIOD-WIDE truth, t̄ = 7%) < 0.5 drops R1's wording before job A |
| m1 | **Accepted.** The "so" clause is dropped, and nothing is said about every playlist sharing its group's offset |
| m2 | **Accepted.** One noise convention for R1 (ddof 1 about the replica mean), with T's MC variance propagated |
| m3 | **Accepted.** D_{A*} is the exposure-weighted mean of D, R2's form; "every resolved one of the three CARRIES" |
| m4 | **Accepted.** SIZE-BIAS-g and SIZE-BIAS-t act separately. UNRESOLVED requires a fire and e < 0.03. UNRESOLVED playlists stay in A* and t̄, as stated |
| m5 | **Accepted.** The disclosure adds the raw and the other dr contrasts |
| m6 | **Accepted.** OTHER's lost band is named and accepted; the SEES row lists R2/R3's lines |
| m7 | **Accepted.** The binding must extend the HPSS record to RPD; the list adds N0's truths and receipts, and says the pseudo-npz files stay on pscratch |
| m8 | **Accepted.** 4.84 GB cited to `FD-CT-5B-DECLARATION.md:131`, 159.4 GiB to the CFS decision, 1.55 GB to `FD-CT-5B-DECLARATION.md:258` |
| m9 | **Accepted.** K2′ adds 5B's PC replica `b3001` |
| m10 | **Accepted.** F1 runs at stage S (§0 table) |
| m11 | **Accepted.** S1's assembly and C_resp are staged rows with pins |
| m12 | **Accepted.** A third departure is listed at the top |
| n1 | **Accepted.** The append point is named for both lines |
| n2 | **Accepted.** Compute bound: under 2 h per run on one login node, at nice 19 |
| n3 | Noted; no change |
| §9 note | **Accepted.** The 2D per-playlist price gives the mean figure and the min–max range |
