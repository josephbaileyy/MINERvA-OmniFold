# 5B's input source, decided from the records, and the bkgaware loops' risk (2026-10-29)

**By** the measurement session (`coverage`), for the director.

**Under** the director's ruling (3) of 2026-10-28, given in a message after PR #460. In it: fix 5B's input design by
2026-11-05, "the bkgaware universe loops or MP-1's zero per-playlist loops"; if the design does not use the bkgaware
loops, "accept the risk" and "record their regeneration cost from the records … measured if it's on record, labelled
an estimate if not"; bring it back only if the design needs them and the timeline cannot be met.

**MEASURES:** nothing. It reads records at `origin/main` `b94afda6`. The record search was delegated to a read-only
subagent (claude-school); this session re-read every citation below.

**CANNOT AUTHORIZE:** 5B's declaration, binding or any run; any deletion; any retention request.

**CITABLE FOR:** which event loops S1's inputs came from; what 5B's per-period build would read; the bkgaware loops'
regeneration cost as recorded.

**NOT CITABLE FOR:** that a per-period build from either source reproduces S1. 5B's pooled control decides that.

## 1. Where S1's inputs came from

- **`of_inputs_5d.npz`** (`07fccc1a…`) was written by `nn_dump_inputs.py` from the merged
  `runEventLoopOmniFold_5D_MEFHC_universes_full.root`, which is **not** the bkgaware file
  (`nd-unfolding/sbatch_nn_dump_5d.sh:13-15`).
- **`bkg_dump.npz`** (`2addac8f…`) was written by `s5c_dump_bkg.py` from the CV omnifile
  `runEventLoopOmniFold_5D_MEFHC.root` (`docs/orchestration/state/s5c/p2-tasks.tsv:2`). The tool refuses unless it
  reproduces the npz's data rows and purity weights exactly.
- So neither candidate is S1's own source. Both are later event loops, compared with production as follows.

## 2. How each candidate compares with production

- **The bkgaware loops** (`$P/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_<PL>_universes_full_bkgaware.root`):
  for 1A, the production bkgaware file's CV-pass rows (1,736,833) and `mc_background` pass rows (52,626) are identical,
  in file order and as a multiset over all 15 CV columns, to MP-1 S0's `base_cv` and to W2b's `rrzero_1A`
  (`state/measurement-paper/phase1/mp1/S0-REPORT.md:58-76`). Its CV columns "equal the lateral-only pass"; it differs
  "only by its extra per-universe branches (454 in `mc_signal_reco`)" (`:74-76`).
- **MP-1's zero loops** (`$P/measurement-paper/phase1/mp1/s1/evloop/zero/runEventLoopOmniFold_5D_<PL>_zero.root`):
  each of the 12 equals W2b's rrzero pass of its playlist under W2's `equal` rule (G1, `S1-REPORT.md:122-125`). Their
  lateral dump is bitwise W2b's rrzero dump (`:206-208`), and its data rows and flux equal the CV npz's, as
  `s5p_input_dumps.py lateral` requires (`nd-unfolding/s5p_input_dumps.py:165-166`).
- **The product-level difference** from production is the same for both chains. W2b's δ = 0 unfold is not bitwise
  `data_b-_j-.npz`, because "the frozen product came from a different binary and dump path"; it passed by the
  fallback jitter criterion (`publication/w2/W2B-REPORT-20261006.md:71-75`).

## 3. The decision

**5B's per-period inputs are built from MP-1's zero per-playlist loops.**
- They carry every tree 5B needs (`mc_signal_reco`, `mc_truth_denom`, `mc_background`, `data`), with CV columns that
  the records tie to the bkgaware loops' for 1A and to W2b's rrzero for all 12.
- They are 4.5 GiB in all, against the bkgaware loops' 159.4 GiB of universe branches that 5B does not use
  (`fd/receipts-ct/retention/ret1.out`, `ret4.out`).
- They are exposed from about 2026-12-15, against 2026-11-09 for the bkgaware loops (`FD-CT-RETENTION.md` §2).
- **The gate is still 5B's pooled control:** the ALL merge, through the same per-period chain, must reproduce S1's f on
  R00–R15 to a tolerance declared before any period result is read (`LIMITATION-PLAN-ADDENDUM-20261028.md:403-404`).
  Bitwise equality is not expected (§2).
- **If that control fails,** the fallback is a new CV-only event loop over the 12 playlists, not the bkgaware loops.
  Their CV columns are the zero loops' for 1A (§2), so they would not be expected to pass where the zero loops fail.
  MP-1's per-variant event-loop cost was 3.913 node-h for 11 variants, about 0.36 each
  (`S1-REPORT.md:94-102`) **(arithmetic)**.

**So the bkgaware loops' purge risk is accepted,** as the ruling provides. Nothing is copied, read or touched.

## 4. What regenerating the bkgaware loops would cost, from the records

- **What made them:** `evloop_bkgaware_packed_loop.sh` under interactive allocation 55881284, on 3 GPU nodes, after
  array job 55880333 was cancelled while pending (`nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md:554`). It ran
  `MINERvA101/opt/bin/runEventLoopOmniFold` with the per-universe dump on, for all 12 playlists.
- **Measured on record:** the wall time. The loops started by 20:01 PDT and finished at 23:02 PDT on 2026-07-13
  (`:554`, `:563`): about 3.0 h on 3 nodes. That is about 9 GPU-node-hours **(arithmetic, not an sacct charge; no record
  of the charge was found)**.
- **Estimated on record:** before the run, "dump-all evloop (53945111) ~3-3.5h wall / ~4.5 nh", and the whole chain
  with merge and rebank "~7 GPU node-hours" (`:552`).
- **The merge** to the 171 GB `…_MEFHC_universes_full_bkgaware.root` took about 6 minutes (`:563-564`).
- **What a rerun would need beyond compute:** the committed scripts and playlist manifests. The binary's source commit
  is not named in them, so a bitwise rerun is not assured.
<!-- absence-ok: "no record of the charge was found" and "not named in them" are scoped to CORRECTED_UQ_PRODUCTION_STATUS.md:550-566 and the committed evloop_bkgaware_packed_loop.sh, which this record cites -->

## 5. What 5B's input build would read

From the records above and the 2D design (`state/2d-closeout/period-unfold-20261014/scripts/build_inputs.sh`,
`build_flux.py`):
1. per period PA (1A–1F), PB (1G, 1L, 1M), PC (1N–1P) and ALL: a merge of the MP-1 zero per-playlist loops, in
   production order, with `2d-unfolding/uq/hadd_universes_full.py` as MP-1 merged them
   (`measurement-paper/phase1/mp1/mp1_s1_pipeline.sh:38-48`);
2. per period: `nn_dump_inputs.py --axes eavail,q3,W` on that merge, with a period flux file as `--mcfile`;
3. per period: `s5c_dump_bkg.py --omnifile <period merge> --npz <period npz>`, which checks itself;
4. per period: a data-POT-weighted flux over the period's playlists, as `build_flux.py` does in 2D;
5. the ALL control, as §3.

No existing 5D tool takes a playlist subset; the per-period merge and flux steps are 5B's development. `nn_dump_inputs.py`
and `s5c_dump_bkg.py` accept any omnifile and flux file as they stand. `s5p_input_dumps.py lateral` cannot be used,
because it refuses unless the data rows and flux equal the full CV npz's (`s5p_input_dumps.py:165-166`).
<!-- absence-ok: "no existing 5D tool takes a playlist subset" is scoped to the delegated search of --playlist/--period arguments in nd-unfolding at b94afda6, which found only r10_extract.py, analyze_p4.py and a PET validator -->

## 6. Not changed

The retention list, the bkgaware loops and every product. 5B's declaration is separate and is not started here.
