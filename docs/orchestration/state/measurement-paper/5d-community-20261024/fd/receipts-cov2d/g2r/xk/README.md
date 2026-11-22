# xk: GENCMP X's step K re-pointed to COV2D-G2R (package and run: XK PASS, 2026-11-16)

The director's XCOV ruling and xk design rulings (2026-11-16). `fd_xcov.py k --products g2r` re-points K's 2D side
(`fd_xcov_steps.PRODUCTS`):
- Q_R and S5_R become RE-2-shapes route A's. S5_R's band_<b> blocks are G2R's rebuilt band blocks: K1's 2D reference.
- the 2D band vectors become G2R's `A_<b>_<i>` products (pins: `INPUTS-g2r.sha256`, 177 rows from products.tsv);
- C-R becomes cr's readout (#1169), and cmodel_R becomes route A's (#1167).

C_PL_R, the S3 laterals, the stat replicas and the 5D side are unchanged. `--products re2`, the default, is K as it ran:
its readout has no `products` key and is otherwise produced unchanged. k1() also prints a `[K1 ratios]` line for every
band on stdout only (accepted by the director), so a re2 run and a g2r run show the K1 2D ratios side by side.

**Ruling 1 (V0, V1 and BOOT are reused, not rerun).** They read no 2D covariance product. `xk_copy.py` copies exactly
what cmd_k / k_compute read from `--run-dir` out of the original run directory: v0-a1/v0.json, v1-a2/v1.json, the BOOT
native lane record, boot/xcov (108 files) and inputs/of_inputs_5d.npz. It reads them O_NOATIME, each must equal
`fd/xcov/run/hpss/files.sha256`, and they go into two new run directories. The original k/ is untouched.

**Ruling 2 (V1's pairing).** V1 checks the MEFHC universes file's 2D weights against S1's. G2R unfolded from that file
under the same pin (220c479e = `cov2d.UNI_SHA256`), so the paired/bounded split carries over. The connect STOPs unless
the file hashes to X's pin. x-nbands, -paired and -bounded can then change only through K1's null list, which
`xk_report.py` prints per band, with the K1 ratios old beside new.

**Ruling 3 (the connect).** It runs on a login node: K took 11.27 s and 1.5 GB on login37
(fd/xcov/run/logs/k.log). The control runs re2 into scratch and must reproduce the committed fd/xcov/run/k/k.json
exactly (`xk_compare.py`: parsed equality, with no normalization needed). Then g2r runs. The fence is RE-2-shapes
rev 3's, verbatim. The template here is filled by `fill_connect_xk.py` at the package commit, and the filled connect
is sent by sha.

| file | what |
|---|---|
| `INPUTS-g2r.sha256` | route A's Q_R and S5_R, and G2R's 175 A_* products |
| `xk_copy.py`, `xk_compare.py`, `test_xk_tools.py` (+`.out.txt`) | copies and control comparison; 10/10 |
| `xk_report.py` | old beside new: route, primary, Q_R alone, x-nbands paired/bounded/total, nulls, K1 ratios |
| `test_fd_xcov.out.txt` | nd-unfolding/tests/test_fd_xcov.py with the XkProducts class: all pass |
| `run_xk_mutants.sh` (+`xk_mutants.out.txt`) | 5 mutants. 4 are killed by XkProducts. The 5th, which adds `products` under re2, can only be caught at run time: the control's comparison STOPs on the extra key (test_xk_tools) |
| `connect-g2r-xk.template.sh`, `fill_connect_xk.py`, `test_connect_xk.sh` | the connect and its stand-in |

**CANNOT AUTHORIZE:** any reading of K's outcome or any wording.

## The run (`run/`): XK PASS

**Go:** the director's "go 9d39a6bc 4bf6874e", given after coverage-5b-audit's clearance (no blocker, no major).
- The connect is `connect/connect-g2r-xk.sh` (`4bf6874e…`), filled at PKG c450f2b4. The launcher is `9d39a6bc…`: f93cdaee
  plus the `xk)` arm (`connect/launch-g2r-vs-f93cdaee.diff.txt`). The stand-in passed 13/13.
- **Launch** (`run/launcher/launch-stdout.txt`): the launcher fence was clear; DIGEST_MATCH; launched rc 0 at 08:27:15Z;
  DONE after 15 polls.
- **Connect** (`run/node/logs/connect.log.txt`), login02, 08:27:13–08:32:06Z:
  - both fences clear (at the start, and before the g2r arm);
  - the deploy at PKG, porcelain 0 before and after; the 4 code shas OK;
  - `universes file sha256 220c479e… (X's pin 220c479e…)`;
  - `XK-COPY OK: 112 files to 2 destination(s), each equal to fd/xcov/run/hpss/files.sha256`.
- **Control** (`k --products re2`): rc 0, k wall 7.12 s. Its `run/node/ctl/k/k.json` is `f3dc2a34…`, the committed
  readout's digest. `XK-CONTROL PASS: 0 difference(s); bytes identical`.
- **The g2r arm** (`k --products g2r`): rc 0, k wall 6.21 s. `run/node/run/k/k.json` is `204e4c89…`; `[K] A: agree`.
- **Side by side** (`run/xk_report.out.txt`, from `xk_report.py`, as recorded):
  - route A in both, for the same reason; v1_source and boot are the same;
  - every outcome is agree, with r* None, for the primary, Q_R alone and C_PL_pair_zero;
  - the operands of the printed x-chi2-hi, x-p-min and x-zmax (the primary's chi2_4 at r1, its p min and |z| max):
    1.2402246144489424 → 1.2320619073532983, 0.8714325302854316 → 0.8727921493781984, and 0.9849188109813766 →
    0.9813413078670112;
  - x-nbands: 34 paired, 4 bounded, 38 in all, the same as before, with no band changing sets;
  - K1 null bands: NormDISCC in both;
  - K1 ratios: the 16 side is identical for every band, every kind is unchanged, and the 2D ratios moved, as printed
    there.
- `run/node/`: the 10 records fetched O_NOATIME by `run/node/fetch_xk.py`. They equal `run/node/NODE-SHA256.txt`
  (238 files in `$W`, the deploy clone and tmp excluded).
- `xk_report.py` here is the package's copy plus explicit lines for the x-chi2-hi, x-p-min and x-zmax operands (added
  after the package was sent; a local report tool, not launch code).

## Left for removal by Joseph

`/pscratch/sd/j/josephrb/cov2d-xk-g2r-20261116/` (the two run directories with their copies, and the deploy clone),
after this receipt merges. The original X run directory `gencmp-x-20261102/` is unchanged.

## Follow-up (2026-11-16, the director's order): xk_copy's docstring line numbers

`xk_copy.py`'s docstring cited `fd_xcov_steps.py` line numbers from before #1170 (d670e9a5c). They now cite
`fd_xcov_steps.py` at sha256 `060db550`:
- cmd_k's v0 read: :451;
- v1_state: :428;
- boot_state's native lanes: :417, and its xcov lanes: :421;
- k_compute's paired replicas: :661-667, and its flux5: :614.

Only the docstring changed. `xk_copy.py`'s sha256 goes from 50e0b850 to 1b9ed114. `test_xk_tools.py` still passes,
and its output equals `test_xk_tools.out.txt` except for the temp-dir names.

The filled connect (`connect/connect-g2r-xk.sh`) and `run/node/code.sha256.txt` pin 50e0b850, the version that ran.
They are records and stay as they are. A new connect filled by `fill_connect_xk.py` takes the current sha.
