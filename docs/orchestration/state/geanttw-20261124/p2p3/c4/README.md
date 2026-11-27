# C4 and the NuE grep: one read-only connect (2026-11-27)

This ran under cov2d's (C4) grant and fresh per-run ack (`../cov2d-grant-C-20261127.md`), and the director's GO for
ONE run of `bash run_c4.sh 5fad20ec… 2fb4108b…`. It ran on login35 at 2026-11-27T17:08:33Z, with
part1 rc 0, part2 rc 0 and connect rc 0. The output is `c4.out`.

- **Part 1 (`c4_header.py`)** read headers only, through O_NOATIME file objects, with atime and mtime unchanged on
  every file.
  - (i) UOMNI is 171,117,087,867 B, equal to Stage C's record. The 37 slim branches take 5,857,242,672 B compressed
    and 6,458,621,231 B uncompressed.
  - (ii) All 12 per-playlist files are present, and their entry sums equal UOMNI's in all four trees. 1L's offset
    is 20,716,792 in both MC trees, with a count of 383,848, the count of P0's 1L dumps.
- **Part 2 (`nue_grep.sh`)** grepped geanttw's own `B/src`. There were no symlinks.
  - `SetNuEConstraint(true)` in the P2 binary's source is at `runEventLoopOmniFold.cpp:1698`.
  - **The other hits are in programs P2 does not run:** `runEventLoop`, `runEventLoopMod`, the `_OLD`/`_OLDEST`
    variants, `.ipynb_checkpoints` copies, and a MAT validation python script.
  - MAT-MINERvA pin and pat contain only the setter's declaration and definition.
- **`test_c4.py`:** 12 tests on fixtures. As positive controls, removing the symlink STOP fails its test, and
  removing the size check fails its test.

Nothing was written on the cluster.
