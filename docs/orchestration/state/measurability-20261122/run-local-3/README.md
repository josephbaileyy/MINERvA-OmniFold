# MSR local step: the one rerun after Amendment E (run-local-3; 2026-11-24, tier3-design)

**The run.** Once, under the director's GO of 2026-11-24, from a clean detached checkout of merge commit
`779c20380aa63ac65e8485ea4672f5b756d8dc49` (PR #1275). That checkout had 0 porcelain lines with `--ignored` before the
run; afterwards it had only the ignored `__pycache__/` directory. msr_project.py was `f073cb94…`, as fixed by the
declaration (rev 4, with Amendments B, C and E). The command was exactly the declared one (`run-env.json`):

    python3 nd-unfolding/msr/msr_project.py run --products docs/orchestration/state/measurability-20261122/run-b/cluster/build --out docs/orchestration/state/measurability-20261122/run-local-3

- **Timing:** 2026-11-24T06:37:33Z to 08:48:06Z. It was local, with 0 node-h. While it ran, the laptop also ran the q0
  study's unit tests, its Docker stand-in, and its login-node connect and fetch. They shared CPU and memory with this
  run, but no file and no code.
- **Outcome:** rc 0, stderr empty, stdout `{"stops": [], "readout": ".../run-local-3/readout.json"}`. Every STOP
  control passed, so the run wrote its readings.
- **Environment** (`run-env.json`): python 3.12.2, numpy 1.26.4, scipy 1.15.2, threadpoolctl's BLAS/LAPACK, and the
  thread environment. N-PREC's driver pair is the Amendment E mapping: gesdd through numpy, gesvd through scipy.

**Handling.** The readings (`readout.json`, `readout.txt`) go to the director first. This README states none of them.
Their wording, and any use in the note, is Joseph's.

## Files (sha256)

- `readout.json` f965b271…
- `readout.txt` 5342d918…
- `run-env.json` 466d843a…
- `run.stdout.txt` f6546311…
- `run.stderr.txt` e3b0c442… (empty)
