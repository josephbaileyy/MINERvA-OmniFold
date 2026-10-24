# C_model,5D build report (2026-10-24, session "2d test")

**What ran.** The one bound run of `nd-unfolding/pv-ladder/build_cmodel5d.py`:
- bound by `BUILD-BINDING.md` (PR #338, main `44445cfc`), under `BUILD-DECLARATION.md` (PR #337);
- on login node `login12`, from 2026-10-24T21:44:19Z, at 0 node-h;
- with no retries and nothing written to CFS.

**Outcome:**
- **The build completed.** Every guard held.
- **The NC is bitwise.**
- **The PC at NuWro passes on the 27 base H2 cells,** with thin margins on both criteria (§3).
- **The 16-cell readout is not powered,** as declared.

**What this record does not do.** It makes no claim. It makes no comparison with any 5D covariance, because the S1 (e)
covariance is at its declaration stage.

## 1. Deploy and modules

- **The run script:** `receipts/cmodel5d/run_cmodel5d.sh` (sha256 `e9c6ea3c…9cee`). It refuses if the run directory
  exists, checks the pin and a clean tree, and checks module resolution, tests and build in order. Each step stops the
  script on failure.
- **The logs:** in `receipts/cmodel5d/`, with their sha256s in `receipts/cmodel5d/SHA256SUMS`. The originals are under
  `/pscratch/sd/j/josephrb/cmodel5d-20261024/logs/`.
- **The committed copies are `.txt` files,** because the repo ignores `*.log`; the originals on pscratch are named `.log`.
- **One log was filtered for git:** the committed `deploy.txt` drops git's carriage-return progress lines. The
  original `deploy.log` on pscratch has sha256 `d924940e…94db5d2`.

**The deploy log:**

```
2026-10-24T21:44:19Z deploy start on login12
Cloning into '/pscratch/sd/j/josephrb/cmodel5d-20261024/repo'...
HEAD is now at dfcbb2c6 [pv-ladder] Add the C_model,5D builder and its tests (not run)
HEAD dfcbb2c6c1dcb3211b7c6c8c364a6c1f9f171a47
status porcelain lines: 0
aaa81575b211f50e007fa75d318fd8d4f48bfb98ac5ae62b398dbf33db37d4ca  /pscratch/sd/j/josephrb/cmodel5d-20261024/repo/nd-unfolding/pv-ladder/build_cmodel5d.py
```

**Module resolution.** The modules were imported through the builder's own path setup, in Python 3.11.14 from
`setup_salloc_env.sh`. Each one is inside the deploy:

```
build_cmodel5d: /pscratch/sd/j/josephrb/cmodel5d-20261024/repo/nd-unfolding/pv-ladder/build_cmodel5d.py (inside deploy)
build_cmodel: /pscratch/sd/j/josephrb/cmodel5d-20261024/repo/2d-unfolding/pv2d/cmodel/build_cmodel.py (inside deploy)
pv2d_lib: /pscratch/sd/j/josephrb/cmodel5d-20261024/repo/2d-unfolding/pv2d/pv2d_lib.py (inside deploy)
pvl_analyze: /pscratch/sd/j/josephrb/cmodel5d-20261024/repo/nd-unfolding/pv-ladder/pvl_analyze.py (inside deploy)
pvl_lib: /pscratch/sd/j/josephrb/cmodel5d-20261024/repo/nd-unfolding/pv-ladder/pvl_lib.py (inside deploy)
s5p_stage1_inspect: /pscratch/sd/j/josephrb/cmodel5d-20261024/repo/nd-unfolding/s5p_stage1_inspect.py (inside deploy)
MODULES OK
```

**Tests**, `python -W ignore -m unittest test_cmodel5d test_pvl`:

```
Ran 53 tests in 1.916s

OK
```

**The build.**
- **Argv:** exactly as `BUILD-DECLARATION.md` §2 gives it.
- **Result:** exit code 0, in 0.42 s wall-clock with 40 MB peak memory.
- **Output:**

```
[c5d] NC {'a_full_grid_bitwise': True, 'b_cells_bitwise': True, 'b_cells': {'max_rel_diff': 0.0, 'tol': 1e-05, 'bitwise': True, 'pass': True}, 'c_integration_routes_bitwise': True}
[c5d] PC (27 base cells) PASS: n 21, corr 0.7898584115803846, slope 0.6834848810630483; 16-cell readout n 9 (not powered: the 16 reporting cells cannot carry the declared rule (ungraded))
[c5d] rank 3; sqrt diag median 3.34 %, max 11.36 %; h median 2.79 %
[c5d] coverage {'own_vertex_shift': 8, 'leave_own_vertex_out': 17, 'sqrt_diag_in_sample': 17} of 21
[c5d] sha256 C_model 8ab57a5c51a78934eb078e75658a5849fbd474ef864c9b541f3aa0afaf2605b3  C_abs 3f489428245c91287d2822183655c37f8ae80149e0c8da41c6a8a3f20ce77f69
```

## 2. Products and outputs

**Inputs.** Each was checked by the builder against its declared sha256, and each product's provenance passed
`pvl_analyze.check_meta`:

| product | sha256 |
|---|---|
| `L-5D-PV_e_tune_v1.npz` | `dbe9a95e746fba127811182e9a352f6dc243d78ff699e803611b5deedbcb0f4f` |
| `L-5D-PV_e_genie_mec.npz` | `bdff9193b04f17c4aa9d97e7d9c26221b03dc8c9b0d2376cd775e6b195b749c5` |
| `L-5D-PV_e_nuwro.npz` | `caf6eee726ddb128d26cf74fad2a2b4e69273607a2a0e1e4a48750766bddc66f` |
| `L-5D-PV_e_gibuu.npz` | `bdf331570daeb3dc56d6096e2c39ca3e7a6091339680eb58034ee9a14c82f3c3` |
| `L-5D-PV_e_closure_nuwro.npz` | `fff9030e7fd63c538b27c58f2a35417b5d28c3d2f6de2880219b181812215182` |
| `L-5D-PV_e_closure_tune_v1.npz` | `eb3e218866dd36e093c85e85a791f8dd8de1491f4ad0694924644b01c8e55f08` |
| P5, `re1-20261022/out/5d/k1_p5_rerun.npz` | `e36f3b25459e068cec9dba941f7b3aea8f48c6e22c931fde7c9d315e7b1e8de2` |
| definition `readouts/h2_definition.json` | `b67907615fe2e903…da89`, with fine map `930326a3…e18c` |

**Outputs:**

| output | sha256 |
|---|---|
| `readouts/cmodel_5d.json` (committed) | `3cfdc6a5b8c6cea5f99b4678e27f6ca5f7973ee57a79b9d139798f0751cfcd60` |
| `/pscratch/sd/j/josephrb/cmodel5d-20261024/out/cmodel_5d.npz` (file) | `3008d8f6b1f295cdd648f14e1ab2c20d864ce054a19f97e90e1620d22484e882` |
| C_model, fractional (16 × 16, matrix bytes) | `8ab57a5c51a78934eb078e75658a5849fbd474ef864c9b541f3aa0afaf2605b3` |
| C_abs = diag(x) C_model diag(x) (matrix bytes) | `3f489428245c91287d2822183655c37f8ae80149e0c8da41c6a8a3f20ce77f69` |

## 3. Controls

**NC: bitwise.**
- (a) `L-5D-PV_e_tune_v1` equals P5 on the full grid.
- (b) Their integrals on the 16 cells are equal, with a maximum relative difference of 0.
- (c) The two integration routes agree.
- (d) C_model is SᵀS, and h is max_k |s_k|; the builder checks both before writing.

**PC at NuWro, graded on the 27 base H2 cells: PASS.**

| | value | bar |
|---|---|---|
| cells with \|bias\| > 1 % | 21 | ≥ 20 |
| corr | 0.790 | ≥ 0.7 |
| slope | 0.683 | [0.67, 1.5] |

- **Every margin is thin:**
  - one cell above the count bar;
  - 0.09 above the corr bar;
  - 0.013 above the slope floor.
- **The direction of the slope:** a slope below 1 means the data shift moves less than the closure bias it should mirror.
- **Other figures:**
  - the closure floor is at most 3.2e-5;
  - |s_NuWro| ≥ |bias| on 8 of the 21 cells (38 %).

**The 16-cell readout: ungraded, labelled "not powered".** It has 9 cells with |bias| > 1 %, corr 0.18 and slope 0.21.
Under the rule that would be NOT_POWERED. As declared, it is a readout, not a test.

**Descriptive coverage, on the 21 PC cells of the 27, as for C_model,2D:**
- |s_NuWro| ≥ |bias| on 8;
- √(s_GENIE+MEC² + s_GiBUU²) ≥ |bias| on 17;
- √diag ≥ |bias| on 17.

The last count includes the bias's own vertex, so it is not evidence of coverage.

## 4. C_model,5D

**The matrix.**
- Rank 3, with singular values of S of 0.2070, 0.0658 and 0.0214.
- Its minimum eigenvalue is −7.4e-18 (PSD to rounding).
- Share of the trace by vertex: GiBUU 89.0 %, NuWro 9.5 %, GENIE+MEC 1.4 %.
- GiBUU sets h in 12 of the 16 cells, NuWro in 3 and GENIE+MEC in 1.

**Per-cell relative shifts s_k and √diag C_model:**

| cell | H2 cells | s GENIE+MEC | s NuWro | s GiBUU | √diag C_model | h |
|---|---|---:|---:|---:|---:|---:|
| R00 | 0, 1 | +0.11 % | +0.17 % | −0.38 % | 0.43 % | 0.38 % |
| R01 | 3, 7 | +0.12 % | −0.04 % | +0.66 % | 0.67 % | 0.66 % |
| R02 | 4 | −0.31 % | +2.33 % | −11.11 % | 11.36 % | 11.11 % |
| R03 | 5 | −0.36 % | +0.31 % | −9.36 % | 9.38 % | 9.36 % |
| R04 | 8, 9 | −0.25 % | −0.67 % | +0.51 % | 0.88 % | 0.67 % |
| R05 | 11, 15 | +1.00 % | +1.56 % | +2.92 % | 3.46 % | 2.92 % |
| R06 | 12 | −1.64 % | +0.66 % | −2.66 % | 3.19 % | 2.66 % |
| R07 | 13 | +0.41 % | −1.59 % | −3.04 % | 3.45 % | 3.04 % |
| R08 | 16, 18 | −1.04 % | −1.26 % | −0.03 % | 1.63 % | 1.26 % |
| R09 | 17, 19, 21, 23 | −0.03 % | −2.40 % | +2.17 % | 3.24 % | 2.40 % |
| R10 | 20 | +0.19 % | +0.95 % | −3.91 % | 4.03 % | 3.91 % |
| R11 | 22 | +0.99 % | +4.48 % | +10.16 % | 11.15 % | 10.16 % |
| R12 | 24, 25 | +0.40 % | +0.31 % | +0.08 % | 0.51 % | 0.40 % |
| R13 | 26, 30 | +0.36 % | +2.28 % | +6.41 % | 6.81 % | 6.41 % |
| R14 | 27, 31 | +0.03 % | +0.48 % | −0.66 % | 0.82 % | 0.66 % |
| R15 | 28, 29 | −0.40 % | −0.49 % | −4.74 % | 4.78 % | 4.74 % |

**√diag C_model per cell:**

| statistic | value |
|---|---:|
| median | **3.34 %** |
| p84 | **8.35 %** (Weibull 9.87 %) |
| p90 | 10.26 % |
| max | **11.36 %** (R02) |

For h, the median is 2.79 %, the p84 8.18 % and the maximum 11.11 %.

**The integral.** For the integrated cross section over the 16 cells (Σ_c X_c), C_abs gives √(1ᵀ C_abs 1) / Σ_c x_c =
**0.12 %**. The vertices' shifts of that sum are:

| vertex | shift of the sum |
|---|---:|
| GENIE+MEC | −0.017 % |
| NuWro | −0.107 % |
| GiBUU | +0.054 % |

The integral is small because each reweight is a pure shape departure: k keeps the prior's truth weight.

**Where the largest entries sit.** The four largest √diag (R02, R11, R03, R13, at 6.8–11.4 %) are cells the merge rule
left alone or merged at low purity: purity 0.27–0.39, and 0.31 for R13. GiBUU's truth-level departure there is large
(`H2-DEFINITION-DECLARATION.md` §1.3).

## 5. Labels, verbatim from `cmodel_5d.json`

- **component:** "generator-shape model dependence; not a calibrated bound (M2, kappa = 1, unscaled)"
- **coverage:** "coverage at held-out truths was not validated (DECISION-20261024-joseph-5d-community-standard-route.md
  item 3); the paper states this as a limitation"
  <!-- absence-ok: a verbatim label quoting DECISION-20261024-joseph-5d-community-standard-route.md item 3, not a claim about the record -->
- **gibuu:** "GiBUU's shape is applied on p_parallel < 10 GeV/c; above it the prior is unchanged. At 6 <= p_parallel <
  10 GeV/c GiBUU's sample lacks the E_nu > 20 GeV part, 4.9-5.3 % of the cross section there. The paper's joint tests
  use the narrower p_parallel < 6 GeV/c (H2-DEFINITION-ADDENDUM-GIBUU-DOMAIN.md)"
- **step_adjacent:** "in every reporting cell 77-100 % of the prior weight lies beside a step in r > 0.1 drawn by the
  noise gate or a cut, where PV-2D found the large-shift tail; the shifts go in as measured
  (H2-DEFINITION-DECLARATION.md §1.3, §3.4)"
- **positive_control:** "positive control passed on the 27 base H2 cells"
- **The 16-cell readout:** "not powered: the 16 reporting cells cannot carry the declared rule (ungraded)"

## 6. What follows (not done here)

- **Adding C_model,5D to the (e) covariance** waits for S1's covariance on the same 16 cells and order (fine map
  `930326a3…`).
- **The PC's thin margins** are for the director to report to Joseph, with the verdict.
- **Retention:** the npz and the run deploy (`/pscratch/sd/j/josephrb/cmodel5d-20261024/`) join the retention item due
  before 2026-11-20, beside S2's ≈ 18 MB.

**MEASURES:** C_model,5D on the 16 H2 reporting cells, and its controls. **CANNOT AUTHORIZE:** any claim, folding
C_model,5D into another covariance, any printed wording, or a coverage statement.
