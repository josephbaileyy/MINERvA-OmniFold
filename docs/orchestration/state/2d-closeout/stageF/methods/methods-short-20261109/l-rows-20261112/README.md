# #977's L rows: local derivations from the read-only pscratch session and committed sources

Run from the repo root with python -I (miniconda3 numpy 1.26.4). No cluster access.

- `code/r33_leave_gibuu.py`: row 3.3. Its inputs are T2B's five fetched files, which still hash to
  T2B/fetch/SHA256SUMS, and `fd_f0_regrade.py` from the `nd-unfolding` tree at da5f157f (0dfa722c), via `git archive`.
  It re-runs T2B's B0–B3 and reproduces the existing grade on all 16 records, then grades with GiBUU also left out of
  C_model. Output: `derived/r33.json` (log in `session/r33.out.txt`).
- `code/l_rows.py`: rows 4.2/F4.3, 4.3, F5.3, F5.4, 3.3, m5/Fm7 and s11c. Every source is pinned or recorded by sha256
  in the output's `sources`. Output: `derived/l_rows.json`, pinned in make_values_fived16.py READOUTS as `lrows`
  (log in `session/l_rows.out.txt`).

These numbers are descriptive only. The definitions are in each script's docstring, and RESPONSE.md, "The L rows",
says where each one is printed. The 4.3 cell set was fixed by rule before the fractions were read. The gen-side
F5.3 fraction is in the readout but is not printed.
