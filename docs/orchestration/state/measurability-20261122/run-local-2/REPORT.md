# MSR local step, the rerun: STOP at C-ROUTE; no reading reported (2026-11-23, tier3-design)

The run had the director's GO for the single rerun (Joseph via the director, 2026-11-23). It ran from a clean detached
checkout of the merge commit `88994c9aa544b7cee438de026ad869ca61126525` (PR #1259, Amendment C), with 0 porcelain lines.
The command was the declared one, with only the output path changed to `run-local-2`, at the director's word, because
`run-local/` holds attempt 1's STOP records (`run-env.json`):

    python3 nd-unfolding/msr/msr_project.py run --products docs/orchestration/state/measurability-20261122/run-b/cluster/build --out docs/orchestration/state/measurability-20261122/run-local-2

- **Code and environment:** msr_project.py `ffb88e7b…`, python 3.12.2, numpy 1.26.4, scipy 1.15.2. The LAPACK builds are
  numpy's OpenBLAS 0.3.23.dev and scipy's OpenBLAS 0.3.21 (`run-env.json`).
- **Outcome:** rc 3, after about 21 minutes. `readout.txt` reads "STOP: C-ROUTE failed; no reading reported."
  `readout.json` holds only the controls record (`schema`, `controls`, `stops = ["C-ROUTE"]`).
- **The disposition is terminal:** there is no repair round, and nothing is rerun without the director's word.

## The controls (`readout.json`)

- **Every control before C-ROUTE passed.**
  - C-OPS.
  - C-RID: sigma_rel max rel 0.0.
  - **C-DID**, now on the declared intersection: 151 functionals compared, equal to the pinned 151; sigma_rel max rel
    7.09e-13. The IBU-1-only names `EW_all_ones` and `total_integrated` are recorded, and so are D-ID's 32 one-sided
    names.
  - C-L, C-GRID, C-T3 (max abs 0.0), C-F0B, C-D, C-A2 (max abs 0.0), C-2D, C-MARG, C-RANK.
  - C-RHO: max abs 8.1e-28.
- **C-ROUTE failed:** `max_excess` 0.7114. That is the largest amount by which the independent route's value of some
  statistic differed from the eigen route's, beyond C-ROUTE's bar. The bars are |ΔS| ≤ 1e-10 + 1e-8·|S|,
  |ΔZ| ≤ 1e-10 + 1e-8·|Z| and |Δr| ≤ 1e-10 + 1e-8·|r|.
- **What C-ROUTE's design implies:** the run computes the readings in memory, compares the two routes on each vector, and
  writes no reading unless every comparison passes. They were discarded, and nothing beyond the controls record was
  written, printed or looked at.
<!-- absence-ok: the record of a STOP; "no reading reported" describes this run's own output -->

## What is and is not known about the C-ROUTE failure

- **Known**, from the controls record alone: the worst excess (0.711), and that the failure is in C-ROUTE and not in a
  construction control.
- **Not known without computing statistics**, which the STOP rule withholds:
  - which statistic it is (S_poor, Z_well or an r);
  - which vector and build;
  - the statistic's magnitude.
- **One hypothesis**, not tested here:
  - The two routes agree in exact arithmetic. The eigen route takes Z_well from C_Q's eigenvalues; the independent route
    solves Wᵀ C W directly.
  - A difference beyond a 1e-8 relative bar is what one would expect if Wᵀ C W is ill-conditioned: some well-constrained
    combinations with very small widths, and a large Z.
  - The bar then sits below the conditioning-driven agreement of the two numerical routes, the situation the project
    met before with COV2D's A5 rule (relative ≤ max(1e-9, 10 κ ε)).
  - If so, the failure says nothing about the readings. But it would need a diagnostic that prints, per vector and
    build, only the excess, the statistic's name and κ(Wᵀ C W), and that is the director's call.
<!-- absence-ok: an untested hypothesis stated as such, and a list of what this STOP record does not contain -->

## Files

- `readout.json`: the controls record only; sha256 c20aaf11…
- `readout.txt`: sha256 f8026116…
- `run-env.json`: HEAD 88994c9a, the empty porcelain, the versions, `numpy.show_config()`, threadpoolctl's two BLAS/LAPACK
  builds, the thread env and the exact command; sha256 99e8f1ca…
- `run.stdout.txt` and `run.stderr.txt` (both empty; the C-ROUTE path writes its files and prints nothing).
