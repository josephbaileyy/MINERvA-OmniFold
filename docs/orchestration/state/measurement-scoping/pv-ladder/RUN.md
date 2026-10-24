# PV ladder: the run record (2026-10-24, session "2d test")

**Under** [`BINDING.md`](BINDING.md) ("Before any job", items 1–3), for [`DECLARATION.md`](DECLARATION.md) as amended
by PR #313. **No job has been submitted.** This record is updated at each step, and the ledger is in `LEDGER.tsv`.

## 1. Code

- **The code commit is `a307facaf0aa453362883f6ba55942143400983c`**, on `pvladder/run-20261024`. It is
  `06436fb3`, the reviewed code, plus `a307faca`, which moves L-5D-PV's NC into the pilot (§4). It adds
  `nd-unfolding/pv-ladder/`, and no existing producer is edited. It passes 20 local tests:
  `cd nd-unfolding/pv-ladder && python3 -m unittest test_pvl -v`.
- **The run pin** is a later commit. It adds the prep job's ratio and cell files (§3) and nothing else, and is
  recorded in §3 before J1.
- **The sha256 of every script, at `a307faca`:**

| file | sha256 (first 16) |
|---|---|
| `nd-unfolding/pv-ladder/pvl_lib.py` | `2be72153752e4ae9` |
| `nd-unfolding/pv-ladder/pvl_ratios.py` | `c09a7349e7076c11` |
| `nd-unfolding/pv-ladder/pvl_cells.py` | `c52a7dddee70b3a8` |
| `nd-unfolding/pv-ladder/pvl_unfold.py` | `59ab0e1154ca2870` |
| `nd-unfolding/pv-ladder/pvl_analyze.py` | `2898f2ed7b77784c` |
| `nd-unfolding/pv-ladder/test_pvl.py` | `8020e92321f10508` |
| `nd-unfolding/pv-ladder/tasks.tsv` | `4cebbc994710c9b8` |
| `nd-unfolding/pv-ladder/config.json` | `078df3b6f361eca3` |
| `nd-unfolding/pv-ladder/sbatch_pvl.sh` | `e032c72fc63bd9bd` |
| `nd-unfolding/pv-ladder/sbatch_pvl_prep.sh` | `54cb0c151ef42bdb` |

- **The s5 stack it calls is unchanged.** Each module's sha256 equals the digest RE-1's P5 recorded
  (`re1/RE1-REPORT-2.md` §1, K1-ND):
  - `s5n_pseudo` `8981f97b…`, `s5c_pseudo` `d81d4f46…`, `s5c_unfold` `510d749a…`;
  - `s5e_candidate` `bda8c48c…`, `s5e_deform` `6726ff99…`;
  - `omnifold_nn_core` `24f87f11…`, `xsec_nd` `454001f3…`.
- **Also called:**
  - `s5e_trace.py` `c47e9dd3feef9eab`;
  - `mnv_guarded_run.py` `30162f57771c9d5a`;
  - the 2D driver for the refinement, `unfold_2d_omnifold_unbinned.py` `74a4ed69c3fa9c4a`;
  - `pv2d_lib.py` `03aedc97c0941bcc`;
  - `gen5d_to_rootpreds.py` `bd7d0d7f82b73cf3`.

## 2. The pre-run review

An independent read-only reviewer read the code against the declaration before any job. It found no blockers.

**Its two major findings are fixed:**
- **M1. The closure counted fakes.** The closure's pseudo-data included reco-passing rows that fail the truth
  selection, and reweighted them. PV-2D excludes them (`unfold_2d_pv2d.py:1975`).
  - Now the pseudo-data are reco- and truth-passing rows only.
  - r is applied only to truth-passing rows inside the npz's full grid, PV-2D's `apply_prior_ratio` convention and the
    declaration's "every truth-passing MC row".
  - The 5D npz has no such rows, but the 3D and 4D npz may.
- **M2. The analysis checked too little.** Now it refuses any product that differs, from the declaration or from the
  rung's other products, in:
  - its features, seed, iterations or threads;
  - its estimator parameters or code sha256s;
  - its refinement (R's 400/31, random_state 45, on every arm-(e) data run; none elsewhere);
  - either prior guard.

  It also checks the inputs of the cells and ratio files, and the covariance's sha256.

**Minor findings, fixed or recorded:**
- **The NC can now be bitwise.** The denominator rescaling is computed as `dn × (of1/of0)`, which is exact at r = 1.
  The weights are float64 already, so the declaration's "through float64 weights" reason does not apply here.
- **Both measured sides are tested,** arm (e)'s refinement input and arm (c)'s, for the feature restriction.
- **The J self-check** compares the exact list from `s5c/contract.json`, 109 cells.
- **The environment is RE-1's:** `$A/setup_salloc_env.sh` and `python`, with no `OMP_NUM_THREADS` override.
- **The launcher** validates every task before it starts any step. Every job after J1 needs a gate file naming the
  pin (§4).
- **L-EW's sentinel rows:** a row outside the 5D grid on any axis keeps r = 1, as on the other rungs. That includes
  the 2,801 −9999 sentinels.
- **Provenance:** the products also record `s5e_trace.py` and the python, numpy and lightgbm versions.

**A correction to the declaration's §5 cost basis.** The closure trains on about 20.4 M reco-passing MC rows as
pseudo-data, not "about as many MC rows" as the 4.09 M data rows. It has no refinement. Its runs are projected at
1.7× a data run (§4).

## 3. Preparation: cells and reweights (no unfolding)

- **Paths:** OUT = `/pscratch/sd/j/josephrb/pv-ladder-20261024` and D = `$OUT/deploy/repo`.
- **The deploy** is a partial clone of `origin` at the pin, as PV-2D's was:
  `git clone --filter=blob:none https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --detach <sha>`.

```
sbatch --qos=debug --time=0:20:00 --job-name=pvl_prep --output=$OUT/logs/%x_%j.out \
    $D/nd-unfolding/pv-ladder/sbatch_pvl_prep.sh $D a307facaf0aa453362883f6ba55942143400983c $OUT \
    L-EW L-3D L-4D L-5D-PV
```

- **The job** reads each rung's npz once for the cells and once for the ratios, plus the four gen5d files. It is
  projected at **16 min, 0.27 node-h**, with `--time` 0:20, which is 1.25×.
  - Revised before submission: the first figure, 0.05 node-h, assumed a shared allocation, but debug QOS charges the
    whole node.
  - Eight reads of 1.1–1.5 GB npz files, each followed by histogramming 33 M rows, are budgeted at about 2 min apiece.
- **It writes** `$OUT/prep/cells/<rung>.json` and `$OUT/prep/ratios/<rung>/`, with every sha256 printed.
- **The pvl_cells self-check must pass,** reproducing s5p's 39 EW and s5c's 109 J cells on the 5D npz. A failure
  stops the ladder and is reported.
- **The files are copied** to `nd-unfolding/pv-ladder/{cells,ratios}/` and committed as the run pin. This step is
  the only one that turns prep output into run input. Its sha256s are checked against the job's printout, and the pin
  is recorded here.

## 4. The jobs

Each job runs one declared group of `tasks.tsv` concurrently:
- each step is `srun -n1 -c <c> --exact --cpu-bind=cores`, with c = 42 as RE-1's for up to six steps, and 256/N for
  more (36 in J1). LightGBM's `num_threads` is fixed at 32 either way, and the launcher refuses below 32.
- each step gets an equal share of 95 % of the job's memory (about 64 GiB in J1, 75 GiB otherwise, against s5p's
  largest recorded MaxRSS of 42 GiB), so every step starts at once;
- `sacct`'s step start times are the check on that.

```
sbatch --qos=regular --time=<limit> --job-name=pvl_<job> --output=$OUT/logs/%x_%j.out \
    $D/nd-unfolding/pv-ladder/sbatch_pvl.sh $D <pin> $OUT <job>
```

**The limits are set at 1.25× the projection,** so the binding's stop rule is enforced by the scheduler. That is
tighter than the declaration's limits, which were longer than 1.25×.

| job | runs | projection | `--time` |
|---|---|---|---|
| **J1 pilot** (alone) | every NC: L-3D, L-4D, L-EW (e) and (c) with all features, L-5D-PV; and E_EW (e) and (c) | **0.40 node-h** (24 min) | 0:30:00 |
| J2 | L-3D: 3 vertices, 2 closures; L-4D: NuWro | revised from J1: max(data step) × 1.7 for the closures | 1.25× |
| J3 | L-4D: GENIE+MEC, GiBUU, 2 closures; L-EW (e): NuWro, GiBUU | revised from J1 | 1.25× |
| J4 | L-EW (e): GENIE+MEC, 2 closures; L-EW (c): 3 vertices | revised from J1 | 1.25× |
| J5 | L-5D-PV: 3 vertices, 2 closures (D3, admitted) | revised from J1 | 1.25× |
| F | the ρ² fallback, per rung, only on NOT_POWERED | revised | 1.25× |

**The pilot's projection** comes from RE-1's `re1-nd`, which ran six data unfolds at once (two 5D, two 4D, two 3D) in
913 s.
- J1 has four 5D-sized runs, two with only two features, plus one 3D and one 4D. Its longest step should be the 5D
  arm-(e) NC, like RE-1's K1.
- 24 min is 1.6× RE-1's elapsed time.

**Gates.** A job after J1 starts only if `$OUT/gates/<job>.ok` exists and contains the line `pin=<pin>`.
- I write J2's, J3's, J4's and J5's gate only after `pvl_analyze.py` reports a PASS on the NC of every rung the job
  contains. Every NC is in J1, L-5D-PV's included, because the binding submits a rung only after its own NC passes.
- L-5D-PV's NC and L-EW (e)'s all-features NC are the same computation: the 5D npz, all features, r = 1. Only the
  ratio file's axes differ. Their equality is a free reproducibility check, and it is reported.
- I write F's gate only on a NOT_POWERED verdict.

**The cap is 4.0 CPU node-h.** I stop and report past 1.25× any projection, and ask before exceeding the cap.

**The projected total,** recomputed with closures at 1.7× a data run (the director's check, before J1). Every
job's longest step is taken as J1's 24 min, and a job with a closure as 1.7 × 24 min:

| | node-h |
|---|---|
| prep | 0.27 |
| J1 | 0.40 |
| J2, J3, J4, J5, each with closures, 0.68 each | 2.72 |
| **total without the fallback** | **3.39** |
| F, if every rung's PC is NOT_POWERED (eight steps, closures 1.7×) | +0.68 → **4.07** |

- **Without the fallback the total is within the cap.** With F at its worst, every rung NOT_POWERED, it is 4.07,
  0.07 over.
- NOT_POWERED needs fewer than 20 headline cells with |bias| > 1 %. PV-2D had 127 such cells on 205.
- **The director was told before J1.** If F is needed, I ask before submitting it rather than trimming a rung.
- These figures are replaced by J1's measured times before J2 is submitted.

## 5. Status

- [ ] Prep submitted; cells and ratios committed as the pin.
- [ ] J1 submitted alone; NCs read.
