# RE-2-shapes, run 1: C0 STOP (2026-11-15T22:49–22:53Z)

**By** the `cov2d` session, under the director's "go fb7c2181 43a7730c", given after coverage-5b-audit cleared rev 2.
The run stopped at C0, so the g2r arm and C1 never ran. The director accepted the STOP as reported and ruled (a2):
c0_sums rev 3, then a fresh connect in a new namespace (`../package/README.md`). The lane draws no outcome.

**CANNOT AUTHORIZE:** any reading of route A. Route A was not produced.

## The run

- **Launch** (`launcher/launch-stdout.txt`): the launcher's fence was clear. Staged `43a7730c…`: DIGEST_MATCH;
  launched rc 0 at 22:49:27Z; `last line: DONE (polls=13 of 360)`. The staged script and log were removed.
- **Connect** (`node/logs/connect.log.txt`), login02, 22:49:25–22:53:38Z, nproc 244, OMP_NUM_THREADS unset:
  - fence (start) clear: every query rc 0, rdx_s1_1A COMPLETED (sacct), squeue showing its header only, 156 sacct rows
    none unended, group C marker absent;
  - partc-r2 SHA256SUMS OK (128 lines); the deploy clean at B = 903fb78b; the 6 staged files OK (`node/stage.sha256.txt`);
  - `arm identity rc=0` (22:50:37–22:53:31Z), `RUN COMPLETE (refined)`,
    `G2R-DRIVER mode=identity rollup_rc=0 redirected labels=0 calls=0`;
  - `c0 comparator rc=1`; `C0 STOP` (`node/c0-sums.json.txt` `3b561b65…`, `node/c0-determinism.json.txt` `e15dbecf…`);
    `RE2SHAPES INVALID (connect)`, DONE.
- **C0's counts:** 128/128 lines (the counts sum to 128): OTHER 1, bitwise 62, path-pairs 26, the three scratch rules
  1 each, skipped PDF 22, skipped logs 14. The five product ROOT files are among the path-pairs, each paired through
  its byte-equal npz twin (4 through outA/cov2d_Q_205.npz, 1 through s5/production_cov.npz); inj.root is under its
  scratch rule. The comparator compared 68 files with 66 equal; its
  differences were `SHA256SUMS` and `receipts/receipt_model_chi2.json`; only_stopped held 8 files.

## The two causes (read O_NOATIME after the run; no file changed)

1. **`receipts/receipt_model_chi2.json` (the one OTHER line).** Field by field, it differs in generated_by (a deploy
   path, which the path pair undoes), generated_utc and host (the comparator's FIELD_SKIP), and **repo_commit**:
   partc-r2 `32e403b8…`, c0 `ed3590ea…`. At B, `receipt_model_chi2_2d.py:56, :307-308` sets it to `git -C $MNV_REPO
   rev-parse HEAD`, and re2c_run.sh sets `MNV_REPO=$A`, the shared `/pscratch/sd/j/josephrb/MINERvA-OmniFold` checkout.
   That checkout's HEAD moved to `ed3590ea` (2026-10-30, #563). No other field differs, so the chi2 values are equal.
2. **The comparator's only_stopped: 8 files** in partc-r2's directory, `fig1/` and `fig1-a2-cabbbbc3/` × {RUN-fig1.txt,
   fig1_run.log, pins.json, uqmedian.tex}. The later Fig. 1 steps added them. They are absent from partc-r2's
   SHA256SUMS. The comparator walks the directory and found them there.

Cause 2 was a gap in my C0 design: the test did not model files added to the reference after its run.

## Files

- `node/`: the run's records, fetched O_NOATIME by `node/fetch_run1.py`. `node/NODE-SHA256.txt` lists all 146 files
  in `$W` except the deploy clone; the 14 fetched copies match it. JSON records carry a `.txt` suffix.
- `launcher/`: the launcher's own record of this run (it was in `g2r/run-re2shapes`, moved aside so that the next
  launch could start).

## Left for removal by Joseph

`/pscratch/sd/j/josephrb/cov2d-re2shapes-20261114/` (the c0 tree and its deploy clone), after this receipt merges.
