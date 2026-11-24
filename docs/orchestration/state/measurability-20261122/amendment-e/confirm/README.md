# MSR Amendment E: the blind confirmation on the real inputs (2026-11-24, tier3-design)

**The rule, fixed before the run.** It is committed at `21179d7e` in `msr_route_confirm.confirm()` and tested in
`test_msr_route_confirm.Verdict`, and the director reviewed it before the GO. The verdict is **PASS** only if all 24
rows are present: diagnostic 2's 21 2D Z_well rows and its three 5D controls. Each row must have
`ref_partition_equal` true, and both the eigen route and the independent route within 1e-8 relative of the 50-digit
mpmath reference. Anything else is **FAIL**. On FAIL nothing is rerun and nothing is read further, and the record goes
to the director.

**The output contract.** The output has diagnostic 2's fields only, written through `msr_route_diag2.Record`. It holds
no a, b, value, label or band. stdout carries only the verdict and the counts. 5D has 29 parameters, so the 5D rows
also have a 50-digit reference.

## The run

- **When and where:** once, under the director's GO (2026-11-24), from a clean detached checkout of
  `21179d7ec2d3f0a067ca2882f92a0581e1cd23b7`. That checkout had 0 porcelain lines with `--ignored` before the run;
  afterwards it had only the ignored `__pycache__/` directories. Input: `run-b/cluster/build`.
- **Code:** msr_route_confirm.py `a343674f…`, msr_project.py `f073cb94…`, msr_route_diag2.py `35d2357f…`.
- **Duration:** 2026-11-24T03:16:10Z to 04:25:39Z. rc 0, and stderr was empty.
- **stdout:** `{"verdict": "PASS", "rows_passing": 24, "rows": 24}` (`run.stdout.txt`).

**The verdict is PASS, 24 of 24 rows.** It is reported as printed. The one rerun into `run-local-3/` still needs the
director's word on this PR's merged sha.

## Files (sha256)

- `confirm.json` 766bf5ea… (the rows, with the fixed fields only)
- `run-env.json` 7bc34cc6… (HEAD, the porcelain count, the versions, numpy/threadpool config, the thread env, the
  command)
- `run.stdout.txt` 07c90555…
- `run.stderr.txt` e3b0c442… (empty)
<!-- absence-ok: the record's own output contract and the rule's FAIL branch; no search claim -->
