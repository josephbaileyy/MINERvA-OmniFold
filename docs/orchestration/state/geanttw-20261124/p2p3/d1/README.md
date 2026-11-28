# D1: the production universe dump's header, to settle C2's key (2026-11-27)

This follows the director's ruling D1 for geanttw P2–P3: settle C2's key with a header-only read, before the
package freezes. The target is the cov2d-protected file
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root`.
`../cov2d-grants-20261127.md` holds cov2d's (A) ack, verbatim.

| step | files | result |
|---|---|---|
| run 1, on cov2d's ack and the director's GO | `run_d1-first.sh` (3777b794), `dump_header.py` (21476b68), `d1-first.out` | **STOP rc 1 at the runner's import gate.** The conda `root_6_28` python3 has no uproot. `dump_header.py` was never sent to python, so the file was not opened or stat'ed. There was no rerun, and the ack was spent. |
| probe, on the director's GO | `probe_uproot.sh` (08bd1a75), `probe.out` | One fresh ssh that ran an `import uproot` line on each conda env's python3 and on `module load python`'s. Only `omnifold_py310` has uproot (Python 3.10.19, uproot 5.6.9). The probe touched no data and installed nothing. |
| run 2, on cov2d's fresh ack and the director's GO | `run_d1.sh` (28da44e6; it differs from the first runner only in `PY` and one comment line), `dump_header.py` (21476b68, unchanged), `d1.out` | **rc 0, KEY ENTRY-ORDER.** `mc_signal_reco` has 32,849,103 entries and 470 branches; `mc_truth_denom` has 32,849,103 entries and 236 branches. Neither carries `mc_run`, `mc_subrun` or `mc_nthEvtInFile`. The size is 171,117,087,867 B, and the atime and mtime are unchanged across the read. |

**What follows, per the director's ruling.** P2 joins on entry order, and C2 checks every non-target branch on that
order. P2 runs without `MNV101_DUMP_POINTCLOUD`.

Both runs were one fresh ssh each (`ControlMaster=no`, `BatchMode=yes`), from the Mac, with `D1_TEST_PATH` unset.
Nothing was written on the cluster.
