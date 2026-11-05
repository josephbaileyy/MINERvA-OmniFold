# COV2D flux check: step B's flux read on the real file

**By** the `cov2d` session, 2026-11-04. The auditor proposed it (rolling audit part 3, "Step B and MnvH1D"), and the
director gave the go. Run as a login-node connect on login02 at 0 node-h, 2026-11-04 19:06:31Z–19:07:10Z.

**MEASURES:** whether `re2_driver.load_flux_bins` reads `runEventLoopMC_MEFHC.root`'s `pTmu_reweightedflux_integrated`
in plain root_6_28 and in the pinned MAT environment, and whether the bins agree. **CANNOT AUTHORIZE:** any change to
step B's environment. Step B stays under the pinned MAT environment (the director, 2026-11-04).

## Result: FLUX-CHECK PASS

| | plain root_6_28 | pinned MAT environment |
|---|---|---|
| key class | `TH1D` | `TH1D` |
| `load_flux_bins` | ok, 14 bins | ok, 14 bins |
| bins equal | yes, bitwise (the JSON floats match) | |
| MAT environment checks | n/a | `libMAT.so` the only mapped MINERvA101/opt file; MnvH1D dictionary present |

So **step B's MEFHC flux read does not need MAT**: the object is a plain TH1D. Step B still runs under the pinned MAT
environment, as the director ruled, since the same job reads other MINERvA files.

## The run

- Script: `connect-flux.sh`, sha256 `a6cc83e622630902c5a58923828e7eae5273f4f2a9ac890e99e34e1e9bf4b80a`, sent to the
  director before it ran. The node listing re-hashed it in place (`node_listing.txt`).
- Clone at M `13927a0ed8f28fbb3149786dbb007e9bd6909b76`, porcelain 0. Blobs asserted (`blobs`): `re2_driver.py`
  `97f26a1d`, `fd_rpd_inputs.py` `7c2e018f`.
- Input: one O_NOATIME copy of `2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root`, 5,143 bytes, sha256
  `d40aea69…` (the pinned `$MC`), atime unchanged.
- MAT: `fd_rpd_inputs.run_check_mat_setup` before sourcing `setup_salloc_env.sh`, `mat_environment` after.
- nice 19, `taskset -c 8-11`, one thread.

## Files

| file | sha256 (as fetched; equal to the node listing) |
|---|---|
| `connect-flux.log.txt` (node: `connect-flux.log`) | `49ffbeadd164eae617d48825ba9e04cf7c2a3f1c7edff5ce0f19a6849937f7a3` |
| `plain.log.txt` (node: `plain.log`) | `4f80af0bc091d80047c162d3da06a599ad2b93b0ae7d8b96524e9c5f3bf3d863` |
| `mat.log.txt` (node: `mat.log`) | `50597d0b3820478b9b75707d6c8b4cad6a776bdf42a1d1c605d3efcff91e9583` |
| `blobs` | `699a204da55893413fc9c874ccd371d6297c7668cd6695341e957e53ea4ea97e` |

The `.log` files were renamed `.log.txt` because the repository ignores `*.log`; their contents are unchanged.

## Removals

- In the script: the clone (1.2G) and the copy, 19:07:09Z, rc 0, both confirmed absent.
- Afterwards (`removal.log.txt`, 19:08:06Z): the work directory and the script, each rc 0. `/dev/shm` then held no
  `josephrb` entry.
- The removal log's `grep -c '[c]ov2d-flux'` printed 2. That count was not itemized. The likely matches are the
  removal command's own processes, whose arguments contain the path. The full process listing taken just after it
  (`removal.log.txt`) shows no flux-check process.
