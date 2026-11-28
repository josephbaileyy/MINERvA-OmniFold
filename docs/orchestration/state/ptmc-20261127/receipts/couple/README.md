# PTMC: C-COUPLE measured on the real CV omnifile (2026-11-27)

**What it was for.** The director asked, before merging the declaration, whether the exact C-COUPLE identity holds on
real rows. A last-bit difference between the denominator's and the signal's w_truth would false-STOP a correctly
coupled run.
- The event loop computes the two trees' truth values on different trees: `model.GetWeight(*truthCV, evt)` at
  `runEventLoopOmniFold.cpp:595`, against `model.GetWeight(*recoCV, evt)` at `:1132-1146`.
- So equality had to be measured, not assumed.

**The check.** `2d-unfolding/ptmc/launch/ptmc_couple_check.py`, sha256 `13901cbe…`. It is read-only.
- It reproduces the two loaders' row rules (re2_driver.py at M) with RDataFrame.AsNumpy.
- It compares, per truth cell of M's grid, the multisets of (truth pT, truth p∥, w_truth), with w = 0 left out.
- It writes nothing.

**The launcher.** `2d-unfolding/ptmc/launch/ptmc_couple_launch.sh`, the stat-connect form, one ssh session to a login
node. It reads r3's staged copy, `/pscratch/sd/j/josephrb/oofvc-20261126-r3/stage/runEventLoopOmniFold_MEFHC.root`,
and refuses unless the copy's sha256 is `43f8cc16…`.

| run | launcher | authorisation | result |
|---|---|---|---|
| 1 | v1 `4cf2d915…` (`run1/ptmc_couple_launch.v1.sh.txt`) | the director's GO; cov2d's ack 17:29:22Z; cert `run1/cert.txt` | login04, 17:29:40–17:29:56Z, **rc 139**: ROOT segfaulted at `import ROOT` because the conda environment was not activated (cling: "cannot extract standard library include paths!"). It read nothing and wrote nothing, and was not retried |
| 2 | v2 `584c7c8a…` (activates root_6_28 as OOFVC's units.sbatch does; `launch-v1-to-v2.diff.txt`) | the director's read of the diff and GO; cov2d's fresh ack 17:31:11Z; cert `run2/cert.txt` | login04, 17:31:29–17:35:04Z, **rc 0** |

**Run 2's result** (`run2/session-out.txt`, verbatim):
- **The identity is exact.** `multiset_exact_equal: true`.
- **Rows:** 32,849,103 denominator rows, all kept by its rules; 32,849,103 signal rows, 0 with bad weights, all
  truth-passing.
- **Agreement:**
  - 0 per-cell count mismatches and 0 one-sided cells;
  - a maximum per-cell sum deviation of 0.0;
  - sorted-pair deviations of 0.0 in pT, p∥ and relative w;
  - all 32,849,103 signal tuples have an exact denominator twin.
- **Flags:**
  - `hasTruthOnlyMisses` = 12 (hadd sums the per-playlist flag), and `nTruthOnlyMisses` = 8,999,007;
  - neither tree has event-ID branches.

**Files** (all byte for byte):
- for each run: `launcher.txt` (the Mac-side output), `session-out.txt` and `session-err.txt` (the login node's stdout
  and stderr; run 1's stderr holds ROOT's stack), and `cert.txt`;
- the old launcher, as `run1/ptmc_couple_launch.v1.sh.txt`;
- the diff, as `launch-v1-to-v2.diff.txt`.
