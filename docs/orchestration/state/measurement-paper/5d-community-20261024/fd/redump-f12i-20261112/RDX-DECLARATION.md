# RDX: the event-loop re-dump for F1.2(i), with the C-BKG control (DECLARATION, design rev 1, DRAFT)

**Session:** tier3-design, 2026-11-12. This is its own lane, as RSN-BINDING-1 ruling 6 directs. The F1.2(i) re-dump
is approved in principle: a pilot on 1A first, and a cap of 2.5 node-h with the pilot included. The director's scope
addition of 2026-11-12 adds C-BKG. Rev 1 takes the director's rulings on rev 0 (§8). Joseph decided on 2026-11-12
that the methods paper does not wait for this re-dump; results are folded in if they arrive in time
(DECISION-20261112-joseph-1a-cfs-and-redump-timing.md, #1092). **For:** coverage-5b-audit's design read, then code and tests, then an audit
delta, then the director's binding. **Nothing has run.**
<!-- absence-ok: operational status of this lane's own runs, not a claim that a result does not exist -->

## 0. What this is

The fresh referee's F1.2(i) asks whether the misses regressor's five truth inputs leave out something that matters.
The candidates are the true neutrino energy E_ν, the true vertex (x, y, z) and the leading proton's kinetic energy.
`of_inputs_5d.npz` cannot answer this: it holds the five truth columns and no event identity
(`nn_dump_inputs.py:89-103`). The event loop writes the true vertex and the mc identity only under
`MNV101_DUMP_POINTCLOUD`, and writes no E_ν at all (`runEventLoopOmniFold.cpp:450-473, 985-1035`). So the answer needs
a re-run of the event loop with those quantities written.

C-BKG answers a separate question: what the 2D background template is made of (#977 RESPONSE.md row 4.2). The May
per-playlist files lack the `bkg_*` branches. Current code writes them (`runEventLoopOmniFold.cpp:1322-1339`). The
1A pilot is therefore the cheapest place to test whether current code reproduces the May template, and, if it does,
to split it.

**The results enter the paper only as stated sensitivities, never as calibrated uncertainties.** Wording is Joseph's
call, after a PRD-referee read. So is whether the paper waits for this or cites it as follow-up.

## 1. Which reference the re-run must reproduce

**Not `of_inputs_5d.npz` (`07fccc1a…`).** It was dumped from `runEventLoopOmniFold_5D_MEFHC_universes_full.root`
through `nn_dump_inputs.py` (`FD-CT-5B-INPUTS.md:22-24`). No committed script produces that merged file. Bitwise
equality with a re-run "is not expected": W2b found that "the frozen product came from a different binary and dump
path" (`FD-CT-5B-INPUTS.md:41-43`, citing `publication/w2/W2B-REPORT-20261006.md:71-75`).

**MP-1's chain is reproducible bitwise, and it is the reference:**
- **Per playlist.** MP-1 S0's `base_cv` pass, an unmodified binary (md5 `a6b85ec3…`) built on a login node from
  canonical sources ("base equals canonical"), ran over full 1A. Its CV-pass rows (1,736,833), non-pass rows
  (945,434) and `mc_background` pass rows (52,626) are identical, in file order and over all 15 CV columns, to
  production's bkgaware 1A file and to W2b's `rrzero_1A` (`phase1/mp1/S0-REPORT.md:34-37, 58-66, 213-217`).
- **Merged.** FD-CT-5B's ALL lane rebuilt MP-1's zero chain bitwise. Its `lat_ALL.npz` is byte-identical to
  `lat_zero.npz` (`6ca02c3d…`), and its unfold's `xsec_flat` is bitwise `mp1s1_zero`'s (`f1d5178a…`)
  (`FD-CT-5B-REPORT.md:100-102`).

**So the F1.2(i) arms carry their own nominal (§4).** Their reading is a difference within MP-1's chain, not against
the paper's nominal (S1's f, on `of_inputs_5d.npz`). That chain matches S1's f within τ, not bitwise
(`FD-CT-5B-INPUTS.md:53-55`). This is stated in every RDX reading.

## 2. Code (to be written after the design read; nothing exists yet)

**C1. A narrow new event-loop gate, `MNV101_DUMP_TRUTHX`,** in `runEventLoopOmniFold.cpp`.
- Under it, `mc_signal_reco` and `mc_truth_denom` gain:
  - `truthx_enu`: the true neutrino energy in MeV, from the universe's `GetEnuTrue()`, the accessor the file already uses
    for Q² and W (`event/CVUniverse.h:386, 405`);
  - `truthx_vtx_x`, `truthx_vtx_y`, `truthx_vtx_z`: the true vertex, through the accessors the point-cloud branches use;
  - `truthx_kep_lead`: the largest E − m_p in MeV over final-state protons from `GetTruthFSHadrons`, or 0 if there is none
    (the KE pattern of `CVUniverse.h:252-253`);
  - `truthx_run`, `truthx_subrun`, `truthx_evt`: the mc identity (`mc_run`, `mc_subrun`, `mc_nthEvtInFile`, the
    file's dedupe key, `:150, 532-557`).
- Distinct names, so the branches cannot collide with the point-cloud ones. The loop refuses to start if both gates
  are set.
- With the gate unset, no branch, fill or selection changes. The pilot's alignment check (C-ALIGN-1A) tests this on
  every common branch.
- **The build** follows `build_mp1_s0.sh`: on a login node, into a private directory under the RDX scratch root, from
  canonical sources plus this one patch. Its md5 is recorded. **The shared `MINERvA101/opt` install is never built
  into or written.**

**C2. The dump.** `s5p_input_dumps.py lateral`, the tool that wrote `lat_zero.npz`, gains a `--truthx` flag.
- With the flag, the npz gains `truthx` (one row per MCgen row, five columns), `truthx_names` and `mc_id` (one row per
  MCgen row: run, subrun, event).
- Without it, the output is byte-identical to today's. This is tested.

**C3. The arms' unfold.** RSN's `rsn_unfold.py` gains `--regressor-features std|wide`. `wide` feeds the misses
regressor the five standard truth features plus the five `truthx` columns. Classifiers, seeds, estimator parameters,
the weights and `omnifold_nn_core.py` are unchanged. The regressor-weight and transfer options compose with it, as in
RSN rev 3.

**C4. Checkers.**
- `rdx_align.py` applies W2's `equal` rule, through `phase1/mp1/omnifile_io.py`'s highest-cycle reader. It runs on
  the intersection of branches, and requires that the only extra branches are C1's.
- `rdx_bkg.py` builds C-BKG's histograms and fractions (§5).

Tests and a declared mutation list follow the RSN pattern. A smoke harness is committed with each connect script.

## 3. Stages and gates

1. **Stage 1, the 1A pilot.** Build C1 (login node, 0 node-h). Run the 1A event loop with `MNV101_DUMP_TRUTHX=1` and
   every other `MNV101_*` variable unset: one shared-QOS job over 41 MC and 253 data files (the S0 manifests), with
   the AnaTuple pins of `ANATUPLE-SHA256.tsv` checked.
   - **C-ALIGN-1A (the bitwise gate):**
     - every common scalar branch of every tree equals MP-1 S0's `base_cv` 1A
       (`/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s0/evloop/base_cv.root`) under W2's `equal` rule, at
       the highest cycle;
     - the entry counts are equal;
     - the extra branches are exactly C1's;
     - `truthx_enu > 0`, and every `truthx` value is finite, on every mc row.

     **Any failure is a STOP:** stage 2 never runs, and the director decides.
   - **C-BKG (§5)** runs on the same output, whatever C-ALIGN-1A's result.
2. **Stage 2, the other 11 playlists.** It runs only after C-ALIGN-1A PASSES and the director gives the go.
   - The event loops: 11 shared-QOS jobs, as stage 1.
   - The merge, through 5B's per-period chain (`fd_ct_period_inputs.py merge`).
   - The dump, with `--truthx`.
   - **C-ALIGN-ALL:** the dump equals `lat_zero.npz` on every common key, bitwise (5B's K1 rule), and the `truthx` and
     `mc_id` rows number exactly the MCgen rows. Any failure is a STOP.
3. **Stage 3, the arms (§4).** Two jobs on one exclusive CPU node each, S3a (eight steps) and S3b (four), after
   C-ALIGN-ALL PASSES and the director gives the go.

Every connect script's sha goes to the director before it runs. The job family is `rdx_`. The director announces it
to every fenced lane before the first submit.

**What is never read:** `of_inputs_5d.npz` and the background dump, the LL5D gate inputs, the 2D merged CV and
`$UNI` (cov2d's). The references (S0's `base_cv`, `lat_zero.npz`) are read by O_NOATIME copy.

## 4. The arms and their readings (fixed before any run)

There are twelve steps in two jobs: S3a runs the first eight, and S3b the last four. All use `--estimator-seed 42`, 5 iterations and 32 threads, as RSN does.

| step | regressor features | regressor weight | transfer | truth |
|---|---|---|---|---|
| X0 | std | none | no | data |
| X0_lat | std | none | no | data, on `lat_zero.npz` (the NC partner) |
| X1 | wide | none | no | data |
| X1w | wide | w_push · w_truth | no | data |
| X1t | wide | none | yes (mask seed [20261112, k], 20 %) | data |
| X0c | std | none | no | noise-free closure at the prior (tune_v1) |
| X1c | wide | none | no | the same closure |
| X1wc | wide | w_push · w_truth | no | the same closure |
| X0g | std | none | no | noise-free closure at the A7 GiBUU hybrid (S3b) |
| X1g | wide | none | no | the same closure (S3b) |
| X0q | std | none | no | noise-free closure at the q3 tilt (S3b) |
| X1q | wide | none | no | the same closure (S3b) |

**NC-X.** X0's product equals X0_lat's bitwise. The npz agree on every common key, and `std` never reads `truthx`.
If NC-X fails, nothing is read.

**The readings.** They use RSN's rounding floor φ_c and reported σ_c, and its W and T classes (RSN-DECLARATION.md
rev 3 §3.4-3.5):

| reading | quantity | classes |
|---|---|---|
| R1, the widened inputs (F1.2(i) proper) | δ_c = X1_c / X0_c − 1 | W0 (max \|δ\|/φ ≤ 2), W1 (≤ 0.5 σ), W2 (cells named) |
| R2, the weight on the widened regressor | X1w_c / X1_c − 1 | W0, W1, W2 |
| R3, the widened regressor's transfer | X1t's held-out transfer t_c | T0, T1, T2 |
| R4, the closures | the bias changes X1c − X0c and X1wc − X1c at the prior, X1g − X0g at the A7 GiBUU hybrid, and X1q − X0q at the q3 tilt, each against its own truth | W0, W1, W2, per truth |

**The outcomes. In MP-1's chain:**
- R1 in W0 or W1, with R4's X1 − X0 change in W0 or W1 at all three truths: the five truth features suffice for the misses regressor at the
  stated level. The paper may say so as a stated sensitivity.
- R1 in W2: the omitted quantities matter in the named cells. That is reported as a sensitivity, with the cells.
  Whether the unfolding changes is a separate decision for Joseph.
- R2 and R3 qualify R1 as RSN's WR and TR qualify the standard regressor. They license no further claim.

## 5. C-BKG (the director's scope addition, 2026-11-12)

**What it computes.** It runs on the pilot's `mc_background` tree, over rows with `sim_background_pass == 1`, weighted
by `w_bkg`, and histogrammed on (`sim_background`, `sim_background_pz`). That is the producer's rule
(`playlist-spread-20261014/coverage/scripts/proxy_hists.py:53-54, 59`). It is computed on both of work_proxy's grids:
`ana` (14 × 16) and `proxy` (10 × 10).

**The control.** The pilot's `ana` histogram must reproduce work_proxy's `1A__ana__B`
(`work_proxy.npz` `42ce788b…`, `coverage/outputs/coverage.json:7-9`) to 1e-12 of its largest cell. work_proxy's B is
the raw Σ w_bkg; POT scaling is applied downstream (`proxy_hists.py:1`), so both sides are compared raw. The `proxy`
grid is reported beside it.

**If it passes,** the event loop's own classification gives:
- the out-of-phase-space fraction: Σ w_bkg over `bkg_nuPDG == 14`, `bkg_current == 1`, 5980 < `bkg_vtx_z` < 8422 mm,
  and the transverse vertex inside helper-3's brackets, divided by Σ w_bkg. The brackets are inner r < 850 mm and outer
  r < 850 · 2/√3 mm (`split-20261112/code/split_remote.sh:13-15` @ `b86c387f8`, on #977's branch);
- the genuine-background fraction: one minus that.

Both are reported per bracket, in total and per cell of the `ana` grid.

**If it fails,** current code does not reproduce the May template. That answers "which code" for row 4.2, and it is
reported as a result, not as a STOP of F1.2(i). The fractions are then printed only as current code's, never as the
May template's.

**C-BKG and C-ALIGN-1A are independent.** Neither one's failure voids the other's arm. One mechanism is worth noting
beforehand. The committed skip at `d1bc8813a:443-445` (unchanged at `6a1c85c7:1454-1456`) routes CC signal that
fails the 2D phase space into `mc_background` only through the reco-side `isSignal && inPS_bkg` test. The records'
reading, that the template is mostly out-of-phase-space ν_μ CC (#977 `RESPONSE.md:456-462` @ `b86c387f8`), is therefore not
guaranteed under current code. A C-BKG failure is a live possibility, and so is a pass.

## 6. Price (node-h; the cap is 2.5, the pilot included)

| stage | item | basis | projected | maximum |
|---|---|---|---|---|
| 1 | build | login node | 0 | 0 |
| 1 | the 1A event loop, with the `truthx` branches | MP-1 S0 `base_cv` 1A: 1,598 s, 0.0173 node-h; S1 `zero` 1A: 5,242 s, 0.0569 (`phase1/LEDGER.tsv:3, 25`) | 0.06 | 0.12 (a 4-hour shared limit) |
| 1 | C-ALIGN-1A | login node, or one small shared job | ≤ 0.01 | 0.02 |
| 1 | **C-BKG, marginal** | reads the pilot's `mc_background` only | **≤ 0.01** | 0.02 |
| 2 | 11 event loops | as 1A; MP-1's 132 passes cost 3.913 node-h, about 0.03 each | 0.66 | 1.0 |
| 2 | merge and dump | 5B job A's ALL lane: merge 3:00 and nn_dump 7:12 inside 0.577 node-h for four lanes (`fd/LEDGER.tsv:50`, `FD-CT-5B-REPORT.md:87`) | 0.20 | 0.30 |
| 3 | S3a: eight arms, one node | RSN's basis, the pv-ladder ledger: J1 seven steps, 861 s, 0.2392 node-h | 0.28 | 0.35 |
| 3 | S3b: four closure arms, one node | as RSN's J3: four steps, 0.25 | 0.25 | 0.25 |
| | **total** | | **≈ 1.45** | **≈ 2.05** |

- A projection above 2.5 STOPs to the director.
- **The main risks:**
  - the new gate's cost is unmeasured;
  - C-ALIGN-1A may fail, because a fresh build may not reproduce S0's binary output bitwise. In that case stage 2
    never runs, and about 0.1 node-h has been spent.
<!-- absence-ok: the gate does not exist yet, so its cost is a projection; a scoping statement about this price -->
- **Purge exposure:** S0's `base_cv.root` and `lat_zero.npz` were written in October. The pilot should run well before
  mid-December. A check of their atimes is the first step of connect 1.

## 7. Seeds

The classifier and regressor seed is 42, as RSN. X1t's mask is `default_rng([20261112, k]).random(n) < 0.2` for
iteration k. RSN's TR uses `[20261111, k]`.

## 8. Rulings taken (the director, 2026-11-12)

1. **Process.** This design goes to coverage-5b-audit before C1–C4 are written, so that a design defect costs no
   code. Then come code, tests and mutants, an audit delta, and the binding.
2. **The reference.** MP-1's bitwise chain is accepted: S0's `base_cv` 1A, and `lat_zero.npz`. Each arm carries its
   own nominal (X0 against X0_lat, bitwise). FD-CT-5B-INPUTS:41-43 and 53-55 are cited for why `of_inputs_5d.npz`
   is not the reference.
3. **The closure truths** are the prior, the A7 GiBUU hybrid and the q3 tilt, as in RSN's J3, so the two lanes stay
   comparable. These are the four S3b steps.
4. **C-BKG** at ≤ 0.01 node-h is accepted.
5. **Timing.** The paper does not wait for RDX (#1092), so the lane takes the time it needs.

## 9. CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the design and price of RDX as proposed.
- **Not citable for:** any reading, the C-BKG result, or the claim that any code exists. Nothing has been written or
  run.
