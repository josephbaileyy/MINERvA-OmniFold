# RPD-RECO d2-predict + step0 for e1 at 2415e8d6 (d2s0e1): config and scripts (2026-11-27)

**By** limitation-resolver, for the director's binding. Nothing in this directory has run. The connect runs only on
the director's GO for its exact sha256. It needs a three-lane ack file (cov2d, tier3-design, minerva-lib), and ibu-chi
is asked by message first.

**What it is.** The next step of RPD-RECO amendment 1's chain after e1's P0 (p0e1, `../p0e1-20261126/run-20261127/`:
DONE, C-JOIN part 2 PASS 792/792). It runs `d2-predict`, the pre-data MC prediction, in which **C-E3 is retested with
true Eν**, then `step0`, the MC-only axes and strata.
- It is login-only at 0 node-h, with no job and no job-name family.
- Everything about how it runs is d2s0-20261124's, as described in
  [`../d2s0-20261124/README.md`](../d2s0-20261124/README.md). That covers:
  - the connect's steps, and the staging of P0's two records into the new run directory;
  - the iris read;
  - the runner with a 7200 s deadline per step, and no dry run (the bound code's `DRY_RUN_SCOPE`);
  - the supervisor, the RSS cap and the fetch;
  - "no measured key before the prediction is committed".
- This README covers only what changes.

## What changes from d2s0-20261124

[`tools/gen_d2s0e1.py`](tools/gen_d2s0e1.py) generates every output from the bound d2s0 files, by counted
replacements. Every input is asserted at its sha256 and every count is asserted. The changes are the ones p0e1 made to
P0, now pointed at p0e1:

1. **The clone and pins.** The clone moves to S = `2415e8d66d1a9160e724d426eaeb54d458d4b4f7`. The 14 pins become
   p0e1's, compared row by row with p0e1's connect. Exactly #1308's four move: reco `7302cc1d` → `12f68102`, custody
   `634670b3` → `6428dead`, test `e1b92ef0` → `eee5ae4c`, mutation `f2612369` → `8dfdeaf1`.
2. **The config** is p0e1's bound `f92d034d…`, unchanged. The bound CLI's `require_predecessors` compares it with the
   two staged P0 records, and p0e1's records carry it.
3. **The in-place inputs** (`tools/d2s0_expected.json`, 16) are:
   - p0e1's 14: flux4's extract, custody record and 12 factor products at run-62051670's sha256s;
   - p0e1's `run/pins.json` (`2a22bdbf…`) and `run/p0.json` (`ab8d3600…`) from p0e1's root, at the committed
     run-20261127 values. `p0.json` is committed. `pins.json` is checked through its byte-exact `pins.json.gz`.

   The stage loop copies these two records from `/pscratch/sd/j/josephrb/rpd-reco-p0e1-20261126/run/` into the new run
   directory, with the new digests.
4. **The fences** are p0e1's.
   - The sacct block is flux4's (geanttw* added); the generator asserts it equals p0e1's byte for byte.
   - The launcher's ack guard is flux4's three-lane guard.
   - The overlap fence is p0e1's (it also lists the 12 omnifiles), at the new root. On the real config at S it reads
     70 originals and CLEAR ([`tests/fence_overlap_real_config.out.txt`](tests/fence_overlap_real_config.out.txt)).
5. **The retention stat** is p0e1's 40 entries: S1's 27, plus the 12 RDX omnifiles and the sidecar at the probe's size
   and inode. The checks tool's wording changes as p0e1's did; its code does not.
6. **Unchanged:**
   - `tools/p0_supervise.py`, byte for byte (`6ad0f68f…`);
   - the runner, except its root and the config digest (asserted);
   - the 7200 s per-step deadlines and the 8e9 B RSS cap;
   - the fetch, except its root and header;
   - the iris read;
   - the script names (`rpd_d2s0_*.sh`). The new root is `/pscratch/sd/j/josephrb/rpd-reco-d2s0e1-20261127`.

The normalized diff from d2s0-20261124 (roots folded, blobs masked) holds only these lines.

## C-E3 with true Eν

`d2-predict` first runs `aggregate` over all MC rows, then `prediction_controls`, which evaluates the energy controls
C-E1 to C-E3 per p∥ stratum (`fd_rpd_reco.py:3441-3444` and `:2825-2827` at S). Only after that does it build the
prediction. Each control is a STOP on failure, with the gates unchanged (amendment 1 §5):
- the weighted median of |q₃′/q₃ − 1| must be at most 0.002;
- its 99th percentile must be at most 0.03.

On 11-24, with the inverted Eν, [8, 15) failed C_E3 at 0.0301 against 0.03, 0.45% of the gate over. Here the factors
and the `energy` column are flux4's true Eν, which C-JOIN part 2 checked bitwise. Whether C-E3 passes is measured only
by this run.
- A C_E3 STOP is the declaration's pre-registered branch back to the director, priced, as on 11-24.
- A PASS lets `d2-predict` build the MC prediction and `step0` run.

## The price

- **0 node-h:** login node only, no job.
- **`d2-predict`, measured: about 7 min.** On 11-24 the same step ran its whole `aggregate` pass, then
  `prediction_controls`, which refused at C_E3. It took 6 min 42 s (11:14:16Z to 11:20:58Z,
  `../d2s0-20261124/run-20261124/records/runner.out`) with a peak RSS of 2,003,857,408 B (25% of the cap).
  - The pass covered every MC row, the 200 Poisson replicas and the 5 weight variants: 6,693,569,800 draws, the same
    count as P0's runtime estimate on 11-24 and 11-27.
  - The work left after the controls is small: `predicted_steps`, the group sums and writing the record.
  - The true-Eν `energy` column is the same length and dtype as before, so the pass should cost about the same.
- **`d2-predict`, formula upper bound:** d2s0's basis, S × 1.5 with S = 3.879e-7 s per draw
  (`timing-20261106/timing.json`), gives 3,895 s against its own 7,200 s deadline. p0e1's record gives 2,414.6 s
  (with factor 10) from its own timing sample. Both overstate the measured 6 min 42 s.
- **`step0`:** 0 draws. Its cost is decompression and five weighted-quantile sorts over at most 32.8 M signal rows,
  minutes by d2s0's account.
- **Wall time:** at most about 4 h on one login node, with the two worker budgets plus the handoff and cleanup.
- **Disk:** the staged copies under the new root, like d2s0's. No omnifiles are read or copied. `d2-predict` and
  `step0` use flux4's products and the S1 dumps.

## Binding constraints

- lat_zero's purge exposure begins 2026-12-25T08:53:42Z.
- The S1 dumps' purge exposure begins **2026-12-30T11:38:24Z** (their HPSS copy is `rpd_dumps.tar`;
  `../p0e1-20261126/run-20261127/README.md`).
- d2s0e1 reads the dumps with O_NOATIME, so the clock does not reset. The e1 chain's 12-20 target falls before both.

## After the receipts: removal through the director

The new root, and the lists already on file: P0's root (`rpd-reco-p0e1-20261126`, the omnifile copies first) and
flux4's lane. d2s0e1 reads p0e1's two records and flux4's products in place, so both stay until d2s0e1's receipts
merge.

## Checks on these bytes ([`tests/`](tests/))

| suite | result |
|---|---|
| `test_sacct_fence.sh` (p0e1's and flux4's, cut from `rpd_d2s0_connect.sh`) | all cases, mutants 18/18 killed |
| `test_launch.sh` (the three-lane guard, against d2s0's launcher) | all cases, mutants 16/16 killed |
| `test_connect_start.sh`, `test_runner.sh`, `test_fetch.sh` (d2s0's, new root) | mutants 6/6, 25/25 and 12/12 killed |
| `test_p0_supervise.py` | 17 passed |
| `test_d2s0_checks.py` (adds: the 16 inputs against flux4's and p0e1's committed records; the stat table equals p0e1's; p0e1's records carry this config and code, and C-JOIN part 2 PASS) | 11 passed |
| `test_fence_omnifiles.sh` (p0e1's fence at the new root) | PASS, mutant killed |

**Reproducible:** `python3 -I -B tools/gen_d2s0e1.py` rewrites the eight outputs byte for byte.

## Reads

- agy (gemini-4-hydrogen-high), 2026-11-27: **VERDICT: GO**, five non-blocking notes ([`reads/agy/`](reads/agy/)). It
  confirmed:
  - the predecessor chain and blinding;
  - that `aggregate` runs before `prediction_controls`, so 11-24's 6 min 42 s covered the whole pass.

  Taken: the 11-24 C_E3 value rounded to 0.0301; the connect header's DRY_RUN_SCOPE citation moved to S's
  `:3391-3395` (the generator now replaces it); and an empty `price/` directory dropped.

## Files and shas

| file | sha256 |
|---|---|
| `production-config.ready.json` (p0e1's, unchanged) | `f92d034df0db5bf487f689b0efc1eb8862396303647fa1172ad5e6eaa3f4c47a` |
| `rpd_d2s0_connect.sh` | `e1b5084b153d81bbba307f73e83231c7669ec4adeb0992f6ac5971a87db3090b` |
| `rpd_d2s0_fetch.sh` | `0853a02969f35f74c4e37c41b74247de102b2944486d7de81ad6f43306d662ca` |
| `rpd_d2s0_launch.sh` | `24739c022ac04202f9e0fecf017fc07ca36fd60159a8b4294a298f3b1475352c` |
| `tools/d2s0_checks.py` | `06b5e7cb95c551a85738a3fc1366650f351895f528f43f454ff1b42e8a879442` |
| `tools/d2s0_expected.json` | `47d7570677baaee68241d76c059312592e7c8b8a61bfc2885d98add6712a711b` |
| `tools/p0_supervise.py` (unchanged) | `6ad0f68fb309a7b83adc0f65ed709e5e2412e650e115075fe41ebbc7a070134f` |
| `tools/fence_overlap.py` | `6503ab07f5d2b4afe88720064d2f9ceac0dbe03aa4c1425a94805c99710fcb5a` |
| the runner, as the connect's heredoc writes it | `7f7c7e1509cb56401d547d488944b2a0d5db62b97face153df5fbdf43a8b41d1` |
