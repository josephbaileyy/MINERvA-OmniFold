# cr: fd_gencmp cmd_overlap re-run on route A's Q_R (package and run: CR PASS, 2026-11-16)

The director's XCOV ruling: after the RE-2-shapes production (#1167), re-run fd_gencmp cmd_overlap under C_new.
GENCMP amendment E step C-R ran `fd_gencmp.py overlap --arm refined` on partc-r2's Q_R (fd/gencmp-e/c-r/e_cr.sh,
readout overlap_refined.json). cr runs the same command with route A's Q_R, `cov2d-re2shapes-20261115/g2r/
combination/s5_plus_playlist.npz` (81fdd16f), pinned by `INPUTS-g2r.sha256`, beside step C-R's two INPUTS files.
The connect (`connect-g2r-cr.sh`, sent by sha; not in this commit because it pins this commit) first reruns step C-R
exactly, as a control: `cr_compare.py` requires its readout to equal the committed one after dropping argv and the
deploy prefix. Only on PASS does it run the g2r arm.

At main d58d0d18, the four code files the readout records (fd_gencmp.py 4ebaa7cb, fd_g_compare.py 0a3c09cd,
s1_assemble.py b157250a, s5p_stage1_inspect.py 26569afc) and its four deploy-relative inputs equal step C-R's.

| file | what |
|---|---|
| `INPUTS-g2r.sha256` | the pin of route A's Q_R |
| `cr_compare.py`, `test_cr_compare.py` (+ `.out.txt`) | the control's comparison: moved deploy and argv PASS; a reading, an input digest, atime_unchanged, an extra key or code_sha256 each STOP |

**CANNOT AUTHORIZE:** any reading of the agree/differ outcomes or any wording. The director takes them.

## The run (`run/`): CR PASS

**Go:** the director's "go f93cdaee 1a583b17", given after coverage-5b-audit's clearance (no blocker or major).
- **The package files:** connect `connect/connect-g2r-cr.sh` `1a583b17…`, which is `fill_connect_cr.py` applied to the
  template. The launcher is `f93cdaee…`: fb7c2181 plus the `cr)` arm (`connect/launch-g2r-vs-fb7c2181.diff.txt`).
  The stand-in (`connect/test_connect_cr.sh`) passed 12/12.
- **Launch** (`run/launcher/launch-stdout.txt`): the launcher fence was clear; DIGEST_MATCH; launched rc 0 at
  04:20:55Z; DONE after 5 polls.
- **Connect** (`run/node/logs/connect.log.txt`), login02, 04:20:53–04:22:07Z, nproc 244, OMP_NUM_THREADS unset:
  - `fence (start) clear`, and again `fence (before the g2r arm) clear`;
  - the deploy at PKG 31cdef26, porcelain 0 before and after;
  - omnifold_py310: python 3.10.19, numpy 2.2.6, uproot 5.6.9 (`run/node/environment.txt`).
- **Control:** `control rc=0`, readout `run/node/control/overlap_refined.json` (`1118c992…`). Then
  `CR-CONTROL PASS: 0 difference(s) after dropping argv and the deploy prefix`. The match is exact: every reading, input
  digest and atime flag equals step C-R's committed readout.
- **The g2r arm:** `g2r rc=0`, readout `run/node/g2r/overlap_refined.json` (`0734cf4a…`), 17 PASS control lines,
  no FAIL. Then `CR PASS: control reproduced step C-R; g2r arm rc 0`.
- **The readings beside step C-R's** (`run/cr_report.out.txt`, from `run/cr_report.py`, as recorded):
  - every outcome class is the same as step C-R's: the 2D primary, its printed-only variant without C_PL5D, and the
    3D descriptive outcome, in all four quadrants;
  - S, d and d_pct are bitwise equal (they depend only on the central values);
  - sigma_2D, rho_star, z_rho0, bound_any_rho and bound_rho0 differ, as printed there.
- `run/node/`: the 10 records fetched O_NOATIME by `run/node/fetch_cr.py`. They match `run/node/NODE-SHA256.txt`,
  which lists `$W` without the deploy clone and tmp.

## Left for removal by Joseph

`/pscratch/sd/j/josephrb/cov2d-cr-g2r-20261116/`, after this receipt merges.
