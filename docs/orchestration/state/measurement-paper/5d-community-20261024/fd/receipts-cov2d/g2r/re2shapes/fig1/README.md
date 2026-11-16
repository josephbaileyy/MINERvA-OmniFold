# RE-2-shapes: the paper's Fig. 1 on route A's Q (2026-11-16)

**By** the `cov2d` session, under the director's go (option (b)), given after coverage-5b-audit's review (no blocker;
one major, carried as (b)). The procedure is RE-2's own `2d-unfolding/re2/partc/re2c_fig1_local.sh` (`02c3090f…`),
calling `re2c_fig1.py` (`2aadeac8…`), which pins `publication/release/figs/make_figs.py` (`4e18c266…`). It ran on
the laptop in a detached clean worktree at main 7fc9ce93, in the recorded environment: python 3.12.2,
matplotlib 3.11.2, numpy 2.5.4, rebuilt with uv outside the repo. The lane draws no outcome.

**CANNOT AUTHORIZE:** any paper wording or figure adoption.

## 1. K1 (purity): STOP, the control unreachable at main (`k1-stop/`)

`re2c_fig1_local.sh purity` exited rc 3: `out/fig1_validation.pdf: sha256 6ee506f5… != 82665808…`. fig2 (`57f3cc60…`)
and fig3 (`e9d1bb01…`) are byte-identical to the 10-24 outputs. The mechanism, from committed records: 82665808 is
the purity Fig. 1 made with make_figs 9c4dbf24. Commit 0b13b747 ("Fig. 1 legend in sentence case (Joseph); re-pin
make_figs.py in re2c_fig1.py") moved make_figs to 4e18c266, which both arms use, and partc_a3's pixel-diff records
place that change inside the legend box. The director accepted the STOP. The stale K1 is on the lane's follow-up list.

## 2. The replacement control: PASS (`control/`)

The director approved it: `re2c_fig1_local.sh refined <workdir> <python>
/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partc-r2` must reproduce amendment 3's refined Fig. 1. It produced
fig1_validation.pdf `71a2ea488ab758a466d40b7d5a7a061ebd95b1cdb90a79427c3da968238b6427`, byte for byte. The script
then exited rc 4 at its copy check (`…/partc-r2/fig1 is not empty`), before any scp, so there was no cluster write.

## 3. Route A: rc 0 (`route-a/`)

`re2c_fig1_local.sh refined <workdir> <python> /pscratch/sd/j/josephrb/cov2d-re2shapes-20261115/g2r` (g2r/fig1
absent beforehand). RUN-fig1.txt reads `commit: 7fc9ce93… clean=yes`. Outputs:
- `fig1_validation.pdf` `1ead58a2223ecf88f3de505d7cbcca76ab306af49814ea7c9d50ec0f2c373e0c`;
- `fig2_joint_localization.pdf` `57f3cc60…` and `fig3_generator_context.pdf` `e9d1bb01…`, unchanged (they don't depend
  on Q);
- `uqmedian.tex` `536f0aaa…`, budget_Q's Q median at 2 decimals; `pins.json` `5f99adb5…`.
The script copied the outputs to `g2r/fig1/`, this procedure's only cluster write.

`route-a/inputs-vs-1167.txt`: every input that is a run output equals #1167's committed digest (main d58d0d18):
budget_Q.json, chain.json, combination.json, cov2d_Q_205.npz, playlist_term.npz, production_cov.npz, reduce.json,
and outA/SHA256SUMS, which is compared to the committed file itself. 0 mismatches.

**Added after the run (option (b)):** `g2r/fig1/` holds 7 files, not in the run's SHA256SUMS. They are listed with
their node digests in `../run2/g2r/SHA256SUMS.added-after-run.txt` (beside that SHA256SUMS) and in
`route-a/g2r-fig1-node.sha256.txt`.

## Files

`*/RUN-fig1.txt`, `*/fig1_run.log.txt` and `*/stdout.txt` for each step; `route-a/` also holds the three PDFs,
`pins.json` and `uqmedian.tex`, identical to the node copies.

## Follow-up (2026-11-16, the director's order): the control arm replaces the stale K1

`re2c_fig1_local.sh`'s `purity` arm is gone. Its K1 (82665808) could no longer pass, as section 1 records. A `control`
arm replaces it: `bash re2c_fig1_local.sh control <workdir> <python>` is section 2's control built into the script.
- It runs the refined arm on amendment 3's part C directory, `/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partc-r2`.
  It takes no directory argument.
- It pins that directory's `chain.json` to `81dcf2d0…`, the one amendment 3's redraw read
  (`stageF/methods/re2/run/partc_a3/RUN-fig1.txt`, and `control/RUN-fig1.txt` above).
- It requires `out/fig1_validation.pdf` to be `71a2ea48…`, amendment 3's refined Fig. 1. That is the copy
  `docs/analysis-note/make_figures.sh` installs, pinned there at :195.
- It never writes to the cluster: no ssh, no upload. Section 2's run reached its rc 4 only because `partc-r2/fig1` is
  not empty. The control arm no longer depends on that.

The refined arm is unchanged. The script's sha256 goes from 02c3090f to 71ac4861.

RE2-DECLARATION-C and its binding amendments 1-3 pin `02c3090f`, as do part C's preflight lists. Those are the records
of the bound procedure that ran, at the commits they name, and they are not re-pinned here. The same goes for
section 1 above, which ran the script at `02c3090f`.

**Test (`control-arm/`).** `test_fig1_local_control.sh` runs the real script, `re2c_fig1.py` and `make_figs.py` in the
recorded environment, with `scp` and `ssh` shimmed. Fetches are served from the local copy of section 2's inputs; the
test first checks all 11 against `control/RUN-fig1.txt`. Nothing reaches the cluster. It checks the following:
- the control prints the K1 line and gives 71a2ea48;
- the control makes no ssh call and no upload;
- the control's 9 fetches all come from partc-r2, except fig_arrays.npz;
- the control's three outputs equal section 2's;
- a control given a directory refuses (rc 2);
- the retired `purity` arm refuses (rc 2);
- a chain.json other than amendment 3's refuses before any other fetch (rc 3);
- refined without a directory refuses;
- refined still checks the dir by ssh and uploads to `<partc dir>/fig1/`;
- a mutant with the K1 pin changed exits rc 3 at the K1 check.

The output is in `test_fig1_local_control.out.txt`.
