# Correction to the data phase's overlap line (2026-11-14)

**By** the `cov2d` session, at the director's ruling (2026-11-14). The receipt's original files are left unchanged.

## What the receipt says, and what it missed

`README.md` line 14 and `readout-ovl-data.out.txt` (sha256 `552cec7c…`) read
`… 21637 readout inputs (under $O 21629, MAT 8) x 1146 LL5D paths (1146 inodes): hits []`.

The check that printed it, `../readout_ovl.py` (sha256 `8b881cf8571ff494faa09d1bdd07cde500448ece7708dde808549a2da9001c6c`),
stats three things: every file under `$O`, `runEventLoopMC_1A.root`, and the MAT setup scripts (its lines 3-5). It
does not check the data phase's rollup-pinned inputs. Those are the 28 entries under `"inputs"` in `data_g2r.json`
(sha256 `cd975b64402325da489ae608277faf5f6d7a7cbebe4974465f90b07c336e083f`):
- the 24 `baseline_flux/runEventLoop{MC,Data}_{1A…1P}.root`;
- `constraint`, `flux_mefhc`, `vl175_build_json` and `vl175_minos_npz`.

One of them is among LL5D's 1146 protected paths:
- **`constraint`**: `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`.
  The rollup's pin is `re2c_rollup.py`:93, `BR.INPUTS["constraint"]`. `BR` is
  `docs/orchestration/state/2d-closeout/c04-repair/scripts/build_repair.py` (loaded at `re2c_rollup.py`:73), which
  builds the path from `R` (:51) and :65-66 and pins sha256
  `e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2` (:74). All are at
  `401733bce290ce122cfbf38f1526e120f174b3ec`. `data_g2r.json`:123 records the same sha256.

A check covering this input set would have printed this path as a hit. Under the director's condition, that hit was a
STOP before the data phase. The other 27 pinned inputs are not among the 1146. The G18 and AR23 records carry no
`constraint` input.

## The evidence that no LL5D atime moved (the director's ruling: the data phase result stands; no re-check, no rerun)

- **How it was read:** the data phase read the constraint through `cov2d_blocks.noatime_inputs`, an O_NOATIME copy
  (`cov2d_blocks.py`:360-374 at `401733bc`).
- **The data phase's own atime ledger:** `data_g2r.json`:61-62 reads `"atime_checked": 359`, `"atime_moved": []`.
- **Its open audit:** `data_g2r.json`:162-163 reads 392 guarded opens, all 392 with the noatime bit.
- **When it ran:** 2026-11-14T03:53:34Z to 03:54:39Z (`connect.log.txt`:1 and :51).
- **The LL5D atime record across that window:** the LL5D rc-129 rerun's atime-pre, taken at 03:55:47Z, is
  byte-identical (sha256 `908d3922e81fa25eff7e61932ed690fc55a1cd8f04c5b26dbc1905c5b0da04f3`) to the LL5D bulk's atime-pre
  of 2026-11-13T06:10:24Z. The two snapshots bracket the data phase, and both read the constraint at
  atime_epoch 1793891894. The rerun's atime-post at 2026-11-14T10:42:35Z reads SAME-SET-NONE-MOVED against that
  atime-pre (its `compare_atime.out.txt`, sha256 `20d3aa5ade9e072f4bd72613c76910219d785703789e68dbe49ac87213400a4d`).
- **What was running:** no LL5D job ran at 03:53Z. The bulk had ended (2026-11-13), and the rerun 61255888 was PENDING
  until 05:57:32Z (sacct).

## Follow-up

`readout_ovl.py` should take each phase's inputs from the readout's own recorded `"inputs"` plus the rollup's PIN paths,
not from a directory walk. G2R has no further readout phase. Any overlap check written for the LL5D null or readout
uses the job's recorded or declared input set.
