# RDX: the event-loop re-dump for F1.2(i) (DECLARATION, design rev 3, DRAFT)

**Session:** tier3-design, 2026-11-12. This is its own lane, as RSN-BINDING-1 ruling 6 directs. The F1.2(i) re-dump
is approved in principle: a pilot on 1A first, and a cap of 2.5 node-h with the pilot included.
- Rev 1 took the director's rulings on rev 0. Rev 2 answers coverage-5b-audit's design read of rev 1 (five majors,
  D1–D5, and lows x1–x6) under the director's rulings on it. Rev 3 answers its re-read of rev 2: one new major,
  D6, only, at the director's ruling. The re-read's lows y1–y4 are on the follow-up list (§8).
- Joseph decided on 2026-11-12 that the methods paper does not wait for this re-dump. Results are folded in if they
  arrive in time (DECISION-20261112-joseph-1a-cfs-and-redump-timing.md, #1092).

**For:** coverage-5b-audit's D6 delta, then the director, then code and tests, then an audit delta, then the director's binding.
**Nothing has run, and no code exists.**
<!-- absence-ok: operational status of this lane's own runs and code, not a claim that a result does not exist -->

## 0. What this is

The fresh referee's F1.2(i) asks whether the misses regressor's five truth inputs leave out something that matters.
The candidates are the true neutrino energy E_ν, the true vertex (x, y, z) and the leading proton's kinetic energy.
- `of_inputs_5d.npz` cannot answer this. It holds the five truth columns and no event identity
  (`nn_dump_inputs.py:89-103`).
- The event loop writes the true vertex and the mc identity only under `MNV101_DUMP_POINTCLOUD`, and writes no E_ν at
  all (`runEventLoopOmniFold.cpp:450-473, 985-1035`).
- So the answer needs a re-run of the event loop with those quantities written.

**RDX tests only those three quantities.** It is silent on anything not added, such as neutron or pion content (§4).

**C-BKG has left RDX (the director, 2026-11-12, D2).** S0's `base_cv` already carries `bkg_*` and `w_bkg`, and its
52,626 background rows equal production's (`phase1/mp1/receipts/checks/r4_prod_vs_base_cv.json`). So the composition
is measured at 0 node-h without a pilot. director-helper-3 runs it.

**The results enter the paper only as stated sensitivities, never as calibrated uncertainties.** Wording is Joseph's
call, after a PRD-referee read.

## 1. Which reference the re-run must reproduce

**Not `of_inputs_5d.npz` (`07fccc1a…`).**
- It was dumped from `runEventLoopOmniFold_5D_MEFHC_universes_full.root` through `nn_dump_inputs.py`
  (`FD-CT-5B-INPUTS.md:22-24`).
- No committed script produces that merged file.
- Bitwise equality with a re-run "is not expected". W2b found that "the frozen product came from a different binary
  and dump path" (`FD-CT-5B-INPUTS.md:41-43`, citing `publication/w2/W2B-REPORT-20261006.md:71-75`).

**MP-1's chain is reproducible bitwise, and it is the reference:**
- **Per playlist.** MP-1 S0's `base_cv` pass ran over full 1A with an unmodified binary (md5 `a6b85ec3…`). That
  binary was built on a login node from canonical sources ("base equals canonical"). Its CV-pass rows (1,736,833),
  non-pass rows (945,434) and `mc_background` pass rows (52,626) are identical, in file order and over all 15 CV
  columns, to production's bkgaware 1A file and to W2b's `rrzero_1A` (`phase1/mp1/S0-REPORT.md:34-37, 58-66,
  213-217`).
- **Same source.** The committed `runEventLoopOmniFold.cpp`, `CVUniverse.h`, `MaxPtMu.h` and `CMakeLists.txt` equal
  `build_mp1_s0.sh`'s pins. The source file's last commit is `486e53e6` (2026-07-18). S0 was therefore built from the
  current source (coverage-5b-audit, design read of rev 1).
- **Merged.** FD-CT-5B's ALL lane rebuilt MP-1's zero chain bitwise. Its `lat_ALL.npz` is byte-identical to
  `lat_zero.npz` (`6ca02c3d…`), and its unfold's `xsec_flat` is bitwise `mp1s1_zero`'s (`f1d5178a…`)
  (`FD-CT-5B-REPORT.md:100-102`).

**So the F1.2(i) arms carry their own nominal (§4).** Their reading is a difference within MP-1's chain, not against
the paper's nominal (S1's f, on `of_inputs_5d.npz`). That chain matches S1's f within τ, not bitwise
(`FD-CT-5B-INPUTS.md:53-55`). Every RDX reading states this.

## 2. Code (to be written after this read; nothing exists yet)

### C1. A narrow new event-loop gate, `MNV101_DUMP_TRUTHX`, in `runEventLoopOmniFold.cpp`

**The quantities.** Under the gate, `mc_signal_reco` and `mc_truth_denom` gain:
- `truthx_enu`: the true neutrino energy in MeV, from the universe's `GetEnuTrue()`. The file already uses this
  accessor for Q² and W (`event/CVUniverse.h:386, 405`).
- `truthx_vtx_x`, `truthx_vtx_y`, `truthx_vtx_z`: the true vertex in mm, from `GetTrueVertex()`, as the point-cloud
  branches take it (`runEventLoopOmniFold.cpp:633-634, 1270-1271`).
- `truthx_kep_lead`: the largest `mc_FSPartE − 938.272` over final-state particles with `mc_FSPartPDG == 2212`, in MeV,
  or 0 if there is none. This is exactly `GetNProtonsTrue`'s proton mass and rule (`CVUniverse.h:248-253`), so the two
  agree.
- `truthx_run`, `truthx_subrun`, `truthx_evt`: the mc identity (`mc_run`, `mc_subrun`, `mc_nthEvtInFile`). This is
  the file's dedupe key (`:150, 532-557`), in the types of the existing identity branches.

**Names.** The names are distinct, so they cannot collide with the point-cloud branches. The loop refuses to start if
both gates are set.

**Truth-only miss rows (D1).** `AppendTruthOnlyMisses` (`:686-915`) writes only what it binds explicitly. Every other
`mc_signal_reco` branch falls into the KNOWN_ISSUES #12 rebind (`:806-850`):
- A double outside `explicitNames` (`:809-822`) and outside the prefixes gets `MissCat::Other`, which "stays 0"
  (`:871`).
- An int would be bound to a `double*` (`:843`), which leaves it dangling.

C1 therefore:
1. caches the `truthx` fields in `TruthDenomEntry` (`:188-219`), filled from the truth loop's universe under the new
   gate. They are filled the way G2 caches the identity and vertex (`:642-653`), but not under the point-cloud gate,
   since the cached vertex is filled only there (`:461, 649`).
2. binds and writes them in `AppendTruthOnlyMisses` from the cached entry, with every `truthx_*` name added to
   `explicitNames`.

The per-row check C-TRUTHX (§3) tests this on every row.

**Gate unset (x6).** All new code sits inside `if (dumpTruthx)` blocks, and the code path without the gate is the
existing one. The audit delta reads the patch for this. The pilot runs with the gate set, so C-ALIGN-1A tests only
that setting the gate leaves every existing branch unchanged.

**The build (D5).** It follows `build_mp1_s0.sh` on a login node, into a private directory under the RDX scratch root.
**The shared `MINERvA101/opt` install is never built into or written.**
1. One synced source tree. From it, a **base** binary (no patch) and a **patched** binary (C1) are built, as S0 built
   base and mod.
2. **Before any pilot (0 node-h; a mismatch STOPs before the build):**
   - the six pins of `build_mp1_s0.sh:28-34` must equal S0's `MANIFEST.sha256` rows. That covers the four tracked
     files and the two untracked compiled inputs, `cuts/MaxPzMu.h` and `systematics/Systematics.h`;
   - every `opt/lib/*.so` must equal its row in S0's MANIFEST, which `build_mp1_s0.sh:43-69` writes;
   - the synced tree's file digests are recorded beside S0's `src_base` rows, and every difference is listed.
3. **Recorded:**
   - the modules and compiler after the maintenance (`module list`, the compiler's `--version`, `root-config --version`);
   - the base binary's md5 beside S0's `a6b85ec3…`. Equality is reported, not gated.
4. **The runtime data the loop opens are pinned:** a sha256 manifest of the MParamFiles data tree and of the flux
   files. S0 recorded none, so this one is the record a later diagnosis would use (the #1064 lesson: a read set
   includes runtime reads).

If C-ALIGN-1A fails, this provenance names the cause:
- a pre-build mismatch would have stopped first;
- a run of the **base** binary over 1A, which needs a separate go from the director, separates the environment from
  the patch.

### C2. The dump

`s5p_input_dumps.py lateral`, the tool that wrote `lat_zero.npz`, gains a `--truthx` flag. With the flag, the npz gains:
- `truthx`: one row per MCgen row, five columns;
- `truthx_names`;
- `mc_id`: one row per MCgen row, with run, subrun, event and **the playlist index** (x4), so the identity is unique
  across the merge.

Without the flag, the output is byte-identical to today's. This is tested.

**The row mask (D6).** The dump builds MCgen through `und`'s collector, whose finite-observable contract drops the
-9999 truth-sentinel rows (`s5p_input_dumps.py:94-103`, KNOWN_ISSUES 76).
- `truthx` and `mc_id` are read in the same tree pass, in the same order.
- They are subset by the **same** row mask, computed from the existing observables only, so the added columns can
  never change which rows are kept.
- C-TRUTHX-NPZ (§3) checks the association row by row. Two declared mutants must be killed by it: one that offsets
  `truthx` by one row, and one that applies the mask to `truthx` alone (or drops it from `truthx` alone).

### C3. The arms' unfold

RSN's `rsn_unfold.py` gains `--regressor-features std|wide` and `--truthx-permute SEED`.
- `wide` feeds the misses regressor the five standard truth features plus the five `truthx` columns.
- `--truthx-permute` permutes the five `truthx` columns **jointly** across MCgen rows, once, by
  `default_rng(SEED).permutation(n)`, before the loop. That makes the null arm X1p (D3).
- The classifiers, seeds, estimator parameters, weights and `omnifold_nn_core.py` are unchanged.
- The regressor-weight and transfer options compose with the new ones, as in RSN rev 3.

### C4. Checkers

- `rdx_provenance.py` runs D5's pre-build comparison against S0's MANIFEST.
- `rdx_align.py` applies W2's `equal` rule through `phase1/mp1/omnifile_io.py`'s highest-cycle reader. It runs on the
  intersection of branches, and requires that the only extra branches are C1's.
- `rdx_truthx_rows.py` is C-TRUTHX (§3).
- `rdx_truthx_npz.py` is C-TRUTHX-NPZ (§3, D6).

Tests and a declared mutation list follow the RSN pattern. A smoke harness is committed with each connect script.

## 3. Stages and gates

1. **Stage 0, the build** (login node, 0 node-h). D5's pre-build comparison runs first; any mismatch STOPs. Then the
   base and patched builds. The provenance record is committed before the pilot.
2. **Stage 1, the 1A pilot.**
   - **The job:** the patched 1A event loop with `MNV101_DUMP_TRUTHX=1` and every other `MNV101_*` variable unset.
     It is one shared-QOS job, with 2 CPUs and 16 GB as MP-1's S1 ran, over S0's manifests (41 MC and 253 data
     files). The AnaTuple pins of `ANATUPLE-SHA256.tsv` are checked.
   - **C-ALIGN-1A (bitwise):**
     - every common scalar branch of every tree equals S0's `base_cv` 1A under W2's `equal` rule, at the highest
       cycle. The reference is `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s0/evloop/base_cv.root`,
       `c76256a4…` (`receipts/checks/mp1s0_base_cv_60017651.out:831`), read by O_NOATIME copy;
     - the entry counts are equal;
     - the extra branches are exactly C1's.
   - **C-TRUTHX (D1, bitwise):**
     - every `mc_signal_reco` row, appended miss rows included, has exactly one `mc_truth_denom` row with the same
       (`truthx_run`, `truthx_subrun`, `truthx_evt`);
     - its five `truthx` values equal that row's bitwise;
     - `truthx_enu > 0` and every value is finite.

     Printed: the counts of reco rows, miss rows, denom rows, matched rows and any row without a partner.
   - **Any failure of C-ALIGN-1A or C-TRUTHX is a STOP:** stage 2 never runs, and the director decides.
3. **Stage 2, the other 11 playlists.** It runs only after both checks PASS and the director gives the go.
   - The event loops: 11 shared-QOS jobs, with each limit set by §5's rule (x5).
   - **Per playlist (x2), on a login node:**
     - C-ALIGN-PL: `equal` against MP-1 S1's zero output for that playlist,
       `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s1/evloop/zero/runEventLoopOmniFold_5D_<PL>_zero.root`.
       Each of the 12 equals W2b's rrzero under `equal` (`FD-CT-5B-INPUTS.md:37-38`);
     - C-TRUTHX on the same output.

     A failure STOPs the merge.
   - The merge, through 5B's per-period chain (`fd_ct_period_inputs.py merge`), then the dump with `--truthx`.
   - **C-ALIGN-ALL:** the dump equals `lat_zero.npz` on every common key, bitwise (5B's K1 rule), and the `truthx` and
     `mc_id` rows number exactly the MCgen rows. Any failure is a STOP.
   - **C-TRUTHX-NPZ (D6), the per-row join, before stage 3:**
     - every `mc_id` value (playlist, run, subrun, event) is unique;
     - for every MCgen row, that event's `mc_signal_reco` row in the per-playlist omnifile has (`MC`, `MC_pz`,
       `w_truth`) equal to the npz row's (`MCgen[:, :2]`, `w_truth`) bitwise at float32, as the dump casts them;
     - its five `truthx` values equal the npz row's `truthx`, bitwise.

     Any failure is a STOP. A count check alone would let a shifted or wrongly masked column through, with the
     right count and marginals but no event association. That is the X1p null itself, and it would produce the
     licensed "no effect" sentence falsely.
4. **Stage 3, the arms (§4).** Two jobs, S3a (eight steps) and S3b (seven), each on one exclusive CPU node. They run
   after C-ALIGN-ALL PASSES and the director gives the go.

Every connect script's sha goes to the director before it runs. The job family is `rdx_`, and the director announces
it to every fenced lane before the first submit.

**Never read:** `of_inputs_5d.npz` and the background dump, the LL5D gate inputs, and the 2D merged CV and `$UNI`
(cov2d's). The references (S0's `base_cv`, S1's zero outputs, `lat_zero.npz`) are read by O_NOATIME copy.

## 4. The arms and their readings (fixed before any run)

There are fifteen steps. All use `--estimator-seed 42`, 5 iterations and 32 threads, as RSN does.

| step | job | regressor features | regressor weight | transfer | truth |
|---|---|---|---|---|---|
| X0 | S3a | std | none | no | data |
| X0_lat | S3a | std | none | no | data, on `lat_zero.npz` (the NC partner) |
| X1 | S3a | wide | none | no | data |
| X1p | S3a | wide, `truthx` permuted (seed 20261113) | none | no | data (the refit null, D3) |
| X1w | S3a | wide | w_push · w_truth | no | data |
| X1t | S3a | wide | none | yes (mask seed [20261112, k], 20 %) | data |
| X0c | S3a | std | none | no | noise-free closure at the prior (tune_v1) |
| X1c | S3a | wide | none | no | the same closure |
| X1pc | S3b | wide, permuted as X1p | none | no | the same closure |
| X1wc | S3b | wide | w_push · w_truth | no | the same closure |
| X0t | S3b | std | none | yes (the same mask) | data (R3's partner, x3) |
| X0g | S3b | std | none | no | noise-free closure at the A7 GiBUU hybrid |
| X1g | S3b | wide | none | no | the same closure |
| X0q | S3b | std | none | no | noise-free closure at the q3 tilt |
| X1q | S3b | wide | none | no | the same closure |

**NC-X.** X0's product equals X0_lat's bitwise. The two npz agree on every common key, and `std` never reads `truthx`.
If NC-X fails, nothing is read.

**The floor and the null (D3).**
- **The floor** φ_c is RSN's rounding floor: i0.json's data jitter over cmodel_5d.json's P5 integrals, measured in the
  paper's chain (RSN-DECLARATION rev 3 §3.4). In MP-1's chain, mp1nf measured no seed scatter: `median_rel_sd` 0.0
  over 109 cells (`phase1/mp1/noisefloor-receipts/noisefloor.json`, `zero_seed_scatter`). So φ_c is a conservative
  floor here, and the reported σ_c is the paper's.
- **The null** is X1p, the refit with five more columns that carry no information. Column sampling and split order
  change with the feature count, so X1 can differ from X0 even when the added quantities are irrelevant. X1p measures
  that refit effect.

**The readings.** They use RSN's W and T classes (RSN-DECLARATION.md rev 3 §3.4-3.5).

| reading | quantity | classes |
|---|---|---|
| R1p, the refit null | δp_c = X1p_c / X0_c − 1 | W0, W1, W2 |
| R1, the widened inputs (F1.2(i) proper) | δ1_c = X1_c / X0_c − 1, and the attributable excess e_c = \|δ1_c\| − \|δp_c\| | W classes on δ1; e_c against 0.5 σ_c, cells named |
| R2, the weight on the widened regressor | X1w_c / X1_c − 1 | W0, W1, W2 |
| R3, the transfer | X1t's held-out transfer t_c beside X0t's | T0, T1, T2 for each, and the difference |
| R4, the closures | X1c − X0c beyond X1pc − X0c at the prior; X1wc − X1c; X1g − X0g at the A7 GiBUU hybrid; X1q − X0q at the q3 tilt; each against its own truth | W0, W1, W2, per truth |

**The outcomes. In MP-1's chain, and only for E_ν, the true vertex and the leading-proton KE (D4):**
- **NC-X fails:** nothing is read.
- **R1p is W2:** the refit alone moves the result in the named cells. R1 is not attributable, and that is reported
  with no claim about the three quantities.
- **R1p is W0 or W1, max_c e_c ≤ 0.5 σ_c, and R4's attributable changes are within W1 at all three truths:** the
  licensed sentence is "in MP-1's chain, adding E_ν, the true vertex and the leading-proton KE to the misses
  regressor moves the unfolded result by no more than half the reported σ in any cell, beyond the refit null". It
  is silent on any quantity not added.
- **Some e_c > 0.5 σ_c, or an attributable R4 change in W2:** a stated sensitivity, with the cells named. Whether the
  unfolding changes is a separate decision for Joseph.
- **R2 and R3** qualify R1 as RSN's WR and TR qualify the standard regressor. They license no further claim.

## 5. Price (node-h; the cap is 2.5, the pilot included)

**The event-loop rule (x1, x5).**
- The shared-QOS charge rate is 0.0391 node-h per wall hour, from S1's 1A row: 0.05688 node-h over 5,242 s
  (`phase1/LEDGER.tsv:25`).
- Each playlist's wall time is projected at S1's 1A rate, scaled by its May signal count (`coverage/outputs/
  proxy_hists_meta.json`).
- Its limit is 1.5 × that, rounded up to 15 minutes, with a minimum of one hour. 1M is projected at 3.0 h with a 4:45
  limit, and 1L at 0.19 h with a 1:00 limit.
- The ceilings below are each limit times the rate.

| stage | item | basis | projected | ceiling |
|---|---|---|---|---|
| 0 | build and provenance | login node | 0 | 0 |
| 1 | the 1A event loop, limit 2:15 | S1 `zero` 1A: 5,242 s, 0.0569 | 0.057 | 0.088 |
| 1 | C-ALIGN-1A, C-TRUTHX | login node | 0 | 0 |
| 2 | 11 event loops, limits summing to 26:00 | the rule above; 15.7 h projected | 0.61 | 1.02 |
| 2 | C-ALIGN-PL and C-TRUTHX, ×11 | login node | 0 | 0 |
| 2 | merge and dump, one node, limit 0:20 | 5B job A's ALL lane: merge 3:00, nn_dump 7:12 (`FD-CT-5B-REPORT.md:87`) | 0.17 | 0.33 |
| 3 | S3a, eight steps, limit 0:22 | the pv-ladder ledger: J1, seven steps, 861 s, 0.2392 | 0.28 | 0.37 |
| 3 | S3b, seven steps, limit 0:22 | the same | 0.28 | 0.37 |
| | **total** | | **≈ 1.40** | **≈ 2.17** |

- Any projection above 2.5 STOPs to the director.
- **The main risks:**
  - The patched loop's cost with the `truthx` branches is projected, not measured.
  - C-ALIGN-1A or C-TRUTHX may fail. Stage 2 then never runs, about 0.06 node-h has been spent, and D5's provenance
    names the cause.
<!-- absence-ok: the gate does not exist yet, so its cost is a projection; a scoping statement about this price -->
- **Purge exposure.** S0's `base_cv.root`, S1's zero loops and `lat_zero.npz` were written in October, and the zero
  loops are exposed from about 2026-12-15 (`FD-CT-5B-INPUTS.md`, §3). Stage 2 should finish before then. Their atimes
  are checked first in each connect.

## 6. Seeds

- The classifier and regressor seed is 42, as RSN's.
- X1t's and X0t's mask is `default_rng([20261112, k]).random(n) < 0.2` for iteration k. RSN's TR uses `[20261111, k]`.
- X1p's and X1pc's joint permutation is `default_rng(20261113).permutation(n_MCgen)`, applied once.

## 7. Rulings taken (the director, 2026-11-12)

1. **Process.** The design goes to coverage-5b-audit before C1–C4 are written. Then code, tests and mutants, an audit
   delta, and the binding.
2. **The reference.** MP-1's bitwise chain is accepted, with each arm carrying its own nominal.
3. **The closure truths** are the prior, the A7 GiBUU hybrid and the q3 tilt, as in RSN's J3.
4. **On the design read of rev 1:**
   - D1, D3, D4 and D5 and the lows are folded in.
   - **C-BKG is removed from RDX's scope and price (D2)** and given to director-helper-3 as its own 0 node-h step.
5. **Timing.** The paper does not wait for RDX (#1092).

## 8. Rev 2 changes (coverage-5b-audit's design read of rev 1, 2026-11-12)

- **D1:** `truthx` is cached in `TruthDenomEntry` and written on truth-only miss rows. The new C-TRUTHX gate checks
  the per-row identity against `mc_truth_denom`. KE uses mp = 938.272, and the vertex comes from `GetTrueVertex()`.
- **D2:** C-BKG is removed (§0).
- **D3:** the X1p and X1pc refit-null arms, and R1's attributable excess. φ is named for MP-1's chain.
- **D4:** the licensing is scoped to the three added quantities and is silent otherwise.
- **D5:** pre-build provenance against S0's MANIFEST, recorded modules, pinned runtime data, and base and patched
  from one tree.
- **x1:** a real price ceiling (≈ 2.17 < 2.5).
- **x2:** the per-playlist C-ALIGN-PL against S1's zero outputs.
- **x3:** the X0t partner for R3.
- **x4:** a playlist index in `mc_id`.
- **x5:** per-playlist limits.
- **x6:** the gate-unset sentence.

## 8b. Rev 3 changes (coverage-5b-audit's re-read of rev 2, 2026-11-12; D6 only, at the director's ruling)

- **D6:** `truthx` and `mc_id` go through the dump's exact row mask. C-TRUTHX-NPZ joins every npz row to its
  omnifile row by `mc_id` (`MC`, `MC_pz`, `w_truth`, `truthx`, bitwise) before stage 3. Two mutants are declared: a
  one-row offset, and the mask applied to `truthx` alone.
- **On the follow-up list, not in this revision:** y1 (a second null draw), y2 (R4's GiBUU and q3 reads have no null
  partner, so they are unadjusted), y3 (all quantities relative, in W1 units) and y4 (the C-TRUTHX cross-tree risk).
- The price is unchanged: projected ≈ 1.40, ceiling ≈ 2.17.

## 9. CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the design and price of RDX as proposed.
- **Not citable for:** any reading, or the claim that any code exists. Nothing has been written or run.
