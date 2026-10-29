# DECLARATION 3b: response-mismatch closures from the existing shifted dumps (2026-10-29)

**By** the measurement session (`coverage`), for the director to bind.

**Under:**
- [`DECISION-20261028-joseph-d2-approved-and-cheap-tier.md`](../../../DECISION-20261028-joseph-d2-approved-and-cheap-tier.md)
  item 2: the cheap tier, "3b, mismatch closures from existing shifted dumps, at about 0.6–3.5 node-h", runs "under the
  standing approval for jobs under 12 h, declared and bound as usual";
- the director's ruling (1) of 2026-10-28, given in a message, that 3b has its own declaration, and the director's
  go-ahead of 2026-10-29 after #497.

**After:**
- [`LIMITATION-PLAN-ADDENDUM-20261028.md`](LIMITATION-PLAN-ADDENDUM-20261028.md) §3.2, design 3b;
- the inputs' preservation in [`FD-CT-PRESERVE-REPORT.md`](FD-CT-PRESERVE-REPORT.md): every npz this reads is on
  HPSS (`mnv-5d-ct-3b-inputs-20261028`).

**Declares:**
- a new driver, `nd-unfolding/fd_ct_closure.py`;
- a new reader, `fd_ct_readers.py mismatch`;
- the step and lane tables, written by `make_3b_tables.py`;
- a submit line, `nd-unfolding/submit_fd_ct.sh`;
- their tests, the argv, the controls, the readout and the stop rule.

**MEASURES:** nothing. The code has run only on synthetic fixtures. One read-only probe of the real dumps' truth sides
was run (§1, `fd/receipts-ct/3b/probe/`).
<!-- absence-ok: a scoping statement about this session's own work: the code is new in this branch, and the probe compared array digests only -->

**CANNOT AUTHORIZE:**
- running it, which needs the director's binding;
- a pass threshold or a decision statistic. The note's closure has none (`docs/analysis-note/app_response_mismatch.tex:22`),
  and Joseph deferred its settings, "the amplitude ε and the decision statistic", on 2026-10-14
  (`DECISION-20261014-joseph-2d-endpoint-and-open-items.md:29`);
- any covariance component, change to C_resp or to the reported matrix, claim or printed wording.

**CITABLE FOR:** what 3b will compute, from which inputs, at what cost, and what makes it stop.

**NOT CITABLE FOR:** any result. Once run:
- not a bias under the true detector response;
- not a validation of C_resp or of its species sizes;
- nothing about variants outside C_resp's species and W2b's whole-recoil scale.

## 0. Summary

### The question

C_resp shifts the unfolding's simulated response by ±1σ per species and unfolds the data
(`build_cresp.py`; `C-RESP-SPEC.md`). 3b asks the converse at the same amplitudes: when the pseudo-data carry a shifted
response and the unfolding keeps the nominal one, how far does the result move from the truth? To first order the two
agree in size (addendum §3.2, an inference). 3b measures where they do not.

### The closures

**Thirteen noise-free, signal-only closures of configuration (e),** one per lateral dump:

| variant | the pseudo-data's dump | amplitude |
|---|---|---|
| `zero` | MP-1's `lat_zero.npz`, the zero response itself | 0 (the control) |
| `{proton,meson,em,other}_{m1,p1}` | MP-1's species dumps | ±1σ at C_resp's D1 sizes: proton 3.5 %, meson 5 %, EM 3 %, other 20 % |
| `xtalk_{m1,p1}` | MP-1's cross-talk dumps | ±1σ, 20 %, as built beside C_resp (not summed into it) |
| `w2b_rr{0,1}` | W2b's whole-recoil dumps | s = 0.96 and 1.04 |

- **Every closure unfolds with the zero dump's response,** `lat_zero.npz` (`6ca02c3d…`), which is bitwise W2b's
  `lat_w2b_rrzero.npz` (`fd/receipts-ct/preserve/INVENTORY.sha256`).
- **The pseudo-data** are the shifted dump's own signal reco rows (reco- and truth-passing, inside the reco window, at
  w_reco), with no background and no Poisson noise. That is pv-ladder's noise-free closure (`pvl_lib.closure_inputs`),
  with only the observed rows taken from the shifted dump. So the Stay-Positive refinement does not run.
- **The truth reference** is the zero dump's, through its own completeness. It is common to all thirteen.
- With the zero dump as both inputs, the closure is pv-ladder's own closure at the nominal prior. A test shows this
  array for array, and, where LightGBM is present, bitwise through the real unfold.

### The statistic

Per closure v, on R00–R15, with X = U · xsec_flat (S1's integration rule):
- **b_v = X_v / X_true − 1,** the closure bias; and **Δ_v = b_v − b_zero,** that bias less the zero-on-zero floor;
- beside each: |Δ_v|/σ and Δ_vᵀ M⁻¹ Δ_v, for M = (C_total + C_resp)/(f fᵀ).

**Per species s, the closure half-span beside the data half-span:**
- **h_s = (Δ_{s,p1} − Δ_{s,m1})/2**, the closure's;
- **d_s = (X^data_{s,p1} − X^data_{s,m1})/(2 f)**, from MP-1's data unfolds: the half-span C_resp is built from
  (`build_cresp.species_block`). For cross-talk, which is built beside C_resp and not summed into it, it is that
  variant's own;
- **the first-order expectation is h_s = −d_s.** Shifting the pseudo-data with the response fixed, and shifting the
  response with the data fixed, move the result in opposite directions: differentiate the closure identity. The
  readout therefore compares h_s with −d_s: their cosine, ‖h_s‖/‖d_s‖, and **the residual h_s + d_s**, with
  |·|/σ per cell and its quadratic form. The residual is where the two constructions differ. This is an expectation
  stated for reading, not a test;
- **h and d differ in construction as well as in sign,** and the readout's label says so:
  - d's data unfolds carry each variant's shifted background template and shifted fakes, are measured at the data's
    truth, and are relative to f;
  - h is signal-only, without fakes, at the MC truth, and relative to it.
  So a residual can come from these differences as well as from anything C_resp misses.
- **W2b's ±4 %:** the same, with d from 3a's committed readout (`fd/readout/fd_ct_recoil.json`, `half_span`, which is
  relative to W2b's own δ = 0 chain).

**Descriptive:**
- **b_zero itself,** the estimator's closure floor;
- **the closure analogue of C_resp,** Σ_{s primary} h_s h_sᵀ, its per-cell σ beside C_resp's. It is printed beside
  C_resp, never as a component.

**No threshold and no pass or fail.** The expectation h = −d is used only to orient the comparison; no tolerance on the
residual is declared.

### Cost

- **One exclusive CPU node, eight lanes of 32 CPUs and 56 GB,** through the committed packer
  (`gpu-timing-20261023/tools/sbatch_timing_packed.sh` → `s5c_array.sh` → `fd_f1_lane.py`), as F1c ran. Lanes 0–4 run
  two closures each, lanes 5–7 one.
- **The measured unit:** a noise-free closure on the full MC took 732.6 s at 32 threads, about 0.045 node-h packed
  (`FD-PLAN.md:472`); F1c's G18 closure took 774.0 s, a lane step of 13.5 min (`fd/receipts-f1/run/cluster/f1c/line0-60439400.log:34`, `:3`, `:42`).
- **Projected:** two closures per lane, about 26 min, so **about 0.45 node-h.** The time limit is 45 min, so the charge
  is at most **0.75 node-h**.
- That is inside the decision's 0.6–3.5 for 3b and the standing approval. **No Poisson experiments are run** (addendum
  §3.2's optional 20 per variant; §7 item 2).

**The readout** runs on a login node afterwards, at 0 node-h.

**Stop rule:** any refusal, any non-zero exit, a lane that ends without its products, or a job past its limit is
reported unrepaired. **There is no resume.** A lane's finished closure refuses to be overwritten, so a rerun needs the
director and recommitted tables under a new `$B`.

## 1. Inputs

`$P` = `/pscratch/sd/j/josephrb`. Every pin is in the code, not the argv.

| input | where | sha256 |
|---|---|---|
| the zero response | `$P/measurement-paper/phase1/mp1/s1/lateral/lat_zero.npz` | `6ca02c3d…` (`build_cresp.PRODUCTS["zero"][1]`; `W2B["rrzero"][1]`) |
| MP-1's 10 species dumps | `…/mp1/s1/lateral/lat_<species>_<m1,p1>.npz` | `build_cresp.PRODUCTS[v][1]` (each data unfold's recorded input dump) |
| W2b's two dumps | `$P/w2-recoil-20261006/w2b/lateral/lat_w2b_rr{0,1}.npz` | `W2B["rr0"][1]`, `W2B["rr1"][1]` (`45de5c7f…`, `4c98d8cb…`) |
| MP-1's 11 data unfolds | `…/mp1/s1/unf/mp1s1_<v>_b-_j-.npz` | `build_cresp.PRODUCTS[v][0]`, with its meta checks |
| 3a's readout | `$D/…/fd/readout/fd_ct_recoil.json` (committed) | `c8458dd0…` (`RECOIL_READOUT_SHA256`) |
| S1 and C_resp | as the readers' declaration | `db000707…`, `4d8b5797…` |

**Every dump here is on HPSS** (`FD-CT-PRESERVE-REPORT.md`); the inventory's digests equal these pins.

**The probe** (`fd/receipts-ct/3b/probe/p1_truthside.{py,out}`, login37, 2026-10-29T10:23Z) found, for all 12 shifted
dumps against the zero dump:
- MCgen, w_truth, pass_truth, w_reco, pass_reco, denom_nd, flux, data_pot, n_nucleons, the edges and the data rows are
  bitwise identical;
- only MCreco differs, and `measured_weights`, the purity weights, which a signal-only closure does not use.

So the driver's truth-side control (§3) is expected to pass. Its refusal stays, for any input that does not.

## 2. Exact commands

`B=$P/fd-ct-3b-20261029` (which must not exist beforehand); `D=$B/deploy/<pin8>`;
`PY=env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B`.

### 2.1 Deploy and tests (login node)

As the readers' declaration §2.1, with:
- the digest list: `fd_ct_closure.py`, `test_fd_ct_closure.py`, `fd_ct_readers.py`, `test_fd_ct_readers.py`,
  `submit_fd_ct.sh`, `fd_f1_lane.py`, `s5c_array.sh`, `sbatch_timing_packed.sh`, `pvl_unfold.py`, `pvl_lib.py`,
  `build_cresp.py`, `3b-steps.tsv`, `tasks-3b.tsv` and this declaration;
- the test modules `test_fd_ct_closure test_fd_ct_readers test_fd_f0_regrade test_build_cresp test_s1_assemble
  test_s1_scripts_isolated`;
- and the committed tables regenerated by `make_3b_tables.py` into `$B/tables`, then compared with `cmp`.

**It must show:** HEAD equal to the pin; 0 porcelain lines before and after; the §8 digests; `tests rc=0` with
**"Ran 184 tests … OK" and no skip**, so the real-unfold test runs; the two tables identical.

### 2.2 The job (login node submits; one compute node)

```bash
bash $D/nd-unfolding/submit_fd_ct.sh 3b $D <pin> $B > $B/logs/submit.out 2>&1; echo "rc=$?" >> $B/logs/submit.out
```

- `submit_fd_ct.sh` refuses unless `$D` is at the pin and neither `$B/closures` nor `$B/lanes` exists.
- It also refuses unless all 13 steps write under `$B/closures/`, so a `$B` other than the tables' own cannot be used.
  Every refusal comes before anything is created.
- It submits one job: account m3246, QOS regular, constraint cpu, one exclusive node, `--no-requeue`, `--time=00:45:00`,
  no GPU.
- Each lane runs under `s5c_array.sh`, which refuses a deploy not at the pin and wraps every interpreter in
  `mnv_guarded_run.py`.
- The thirteen products land in `$B/closures/closure_<variant>.npz`.

**After the job:** `sacct -j <job> -X -o JobID,State,ExitCode,Elapsed,NNodes` and each lane's `[f1-lane]` lines are
recorded. The job must be COMPLETED 0:0, and every lane must end `done`. Anything else is a STOP.

### 2.3 The readout (login node, after §2.2)

```bash
cd $B && TMPDIR=$B/tmp timeout 120 $PY $D/nd-unfolding/fd_ct_readers.py mismatch \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz \
  --closures-dir $B/closures --mp1-unf $P/measurement-paper/phase1/mp1/s1/unf \
  --recoil-readout $D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_ct_recoil.json \
  --out-json $B/fd_ct_mismatch.json > $B/logs/mismatch.out 2> $B/logs/mismatch.err; echo "rc=$?" >> $B/logs/mismatch.out
```

The projected wall is under 1 minute; the timeout is 120 s. The exit codes are as the readers' declaration: 0, 1
(control), 2 (argparse), 3 (leak guard), 124.

### 2.4 Preservation (login node, after §2.3)

The 13 closures and their inventory go to HPSS by the committed `stage0_preserve.sh`, as 3b's inputs did, into
`/home/j/josephrb/mnv-5d-ct-3b-closures-<date>`. They are about 13 MB **(estimate: 13 × two 65,856-float arrays,
compressed)**.

**Committed in the report's PR:** the readout as `fd/readout/fd_ct_mismatch.json`; the logs, `sacct` lines, step
scripts and the closures' sha256 list under `fd/receipts-ct/3b/run/`; ledger rows.

## 3. Controls

**The driver** (`fd_ct_closure.py`; each refusal writes nothing):
- **refuses to overwrite** (exit 3) (`test_refuses_to_overwrite`);
- **requires both input digests** to be the expected ones (exit 4) (`test_refuses_a_digest_that_is_not_expected`);
- **requires both dumps' axes** to be (p_T, p_∥, E_avail, q3, W) (exit 4) (`test_refuses_another_axis_set`);
- **the truth side:** MCgen, w_truth, pass_truth, w_reco, pass_reco, denom_nd, flux, data_pot, n_nucleons and the edges
  must be bitwise equal, in shape, dtype and bytes, and MCreco must have the same shape (exit 4). Each key is tested by
  a one-entry change (`test_each_truth_side_key_is_checked`, including a dtype change alone, and
  `test_refuses_dumps_of_another_truth` through `main()`). It stays silent on dumps that differ only in MCreco
  (`test_two_dumps_that_differ_only_in_mcreco_pass`).
- **It records** whether the pseudo dump's MCreco is identical to the response's (`pseudo_reco_identical`), and the
  reader requires that to be true for `zero` and false for every other variant.

**The reader** (`fd_ct_readers.py mismatch`; exit 1 and nothing written, unless marked):
- **S,** as the readers' declaration;
- **M0:** exactly the 13 declared closure files; each one's meta names its variant, the zero response, its own pseudo
  dump's sha256, arm (e), all five features, seed 42, 5 iterations, a refinement that did not run, and
  `pseudo_reco_identical` as above; three estimators at 100/8/42; **its `code_sha256` for `fd_ct_closure.py`,
  `pvl_unfold.py` and `pvl_lib.py` equal to this deploy's files**, so a pilot or stale product refuses; finite
  `xsec_flat` of the fine grid's length. Tests: a missing closure, another pseudo dump, a refinement that ran, a zero
  closure with shifted reco, another estimator seed, and other code;
- **M1:** the truth and every closure integral are positive. **An assertion,** written under `assertions_passed`:
  every closure's `xtrue_flat` is bitwise the same. It comes from the pinned zero dump, so it guards the code, not the
  inputs (`test_refuses_closures_of_different_truths`);
- **M2:** the 11 MP-1 data unfolds pass `build_cresp.load_product` (their digests, dumps and meta)
  (`test_refuses_a_data_unfold_that_is_not_build_cresps`); 3a's readout matches its pin
  (`test_refuses_another_3a_readout`);
- **the leak guard** (exit 3), with f, the truth integrals, every closure integral and the data unfolds' integrals.
  Following amendment 1, a data integral equal to f to within LEAK_REL is not passed, since it IS f. Tests plant a
  closure integral and a data integral in O(1) units, so only the table can refuse them.

**The tables:** a test regenerates them with `make_3b_tables.py` and compares the committed bytes
(`test_the_committed_tables_are_the_generators`). `closure_pins` is tested against `build_cresp.PRODUCTS` and `W2B`.

**The submit line,** in a throwaway git repo with a stub `sbatch` (`test_fd_ct_closure.Submit`): the committed
arguments (account, QOS regular, cpu, one exclusive node, `--no-requeue`, 45 min, no GPU, the lane geometry); and its
refusals, each before anything is created: a deploy not at the pin, an existing `$B/closures`, a `$B` the tables do not
write under, and another stage.

**The h = −d orientation:** closures planted at exactly h = −d read as cosine 1, norm ratio 1 and a zero residual
(`test_closures_at_exactly_minus_d_read_as_agreement`).

## 4. Statistics, as built

- **Why the zero dump's response, and not the production `of_inputs_5d.npz`:** the shifted dumps were built against
  the zero dump's event set. The lateral dumper drops the 2,801 −9999-sentinel truth rows that `of_inputs_5d.npz` keeps
  (`KNOWN_ISSUES.md:69`): the zero dump has 32,846,302 MC rows (`probe/p1_truthside.out`), the production npz 32,849,103
  (`phase1/mp2/S0-S1-REPORT.md:25`), and 32,849,103 − 32,846,302 = 2,801 **(arithmetic)**. So the production npz and the
  dumps do not share the truth side, which the driver's control requires.
- **Δ, not b:** b_zero is the estimator's own closure floor at the nominal response, the same in every closure.
  Subtracting it isolates the mismatch.
- **Divisors:** b and Δ are relative to the closures' common truth. d_s is relative to f, as C_resp's half-span is.
  W2b's d is relative to its own δ = 0 chain, as 3a reports it. The readout states each.
- **The closure analogue of C_resp** sums the four primary species only, as C_resp does. Cross-talk is reported beside
  them.

## 5. The readout, `fd-ct-mismatch/1`

```text
labels{what, construction, not_citable_for, no_threshold}, controls_passed[S, M0, M1, M2], assertions_passed{M1}, cells,
closure_floor_zero_on_zero, closure_floor_summary_abs, sigma_rel{C_total_resp, C_resp},
variants{v: {delta, abs_delta_over_sigma_total_resp, abs_delta_over_sigma_total_resp_summary, quadratic_form_total_resp}},
species{s: {closure_half_span, data_half_span, cosine_closure_vs_minus_data, norm_ratio_closure_over_data,
            closure_half_span_over_sigma_total_resp, closure_half_span_quadratic_form,
            residual_h_plus_d, residual_over_sigma_total_resp, residual_quadratic_form}},
w2b_recoil_4pct{the same keys},
closure_analogue_of_C_resp{sigma_rel, ratio_to_sigma_C_resp, label},
inputs_sha256{closures, pseudo_dumps, recoil_readout, s1_npz, cresp, definition, mp1_data_unfolds}, code_sha256, argv
```

**stdout:** the PASS lines, one `[3b]` line per species and one for W2b, and the `wrote` line.

## 6. Code and tests

- **`nd-unfolding/fd_ct_closure.py`** (new): `truth_side_problems`, `mismatch_inputs` and `main`.
- **`fd_ct_readers.py`:** adds `closure_pins`, `closure_meta_problems`, `run_mismatch`, the `mismatch` subcommand and its
  labels. The 3a, 4C and 5A readers are unchanged.
- **`nd-unfolding/submit_fd_ct.sh`** (new), and **`make_3b_tables.py`** with the two tables it writes.
- **Tests:** `test_fd_ct_closure.py` (new, 16: `Unit` 4, `Main` 6, `Submit` 5, `RealUnfold` 1) and
  `test_fd_ct_readers.py`'s `Mismatch` (15). That module is now 77.
- **Mutation receipt:** `fd/receipts-ct/3b/mutants_3b.py` (§11).

## 7. For the director

1. **Joseph's deferral of the closure's settings** (2026-10-14) stands. 3b fixes no new amplitude: the species ±1σ are
   C_resp's D1 sizes, and the ±4 % is W2b's. It fixes no decision statistic and sets no threshold. Joseph's decision of
   2026-10-28 named 3b in the cheap tier. If the director reads 3b as reopening the deferral, it waits for Joseph.
2. **No Poisson experiments.** The addendum's optional 20 per variant (about 3.5 node-h) would give the closures' noise.
   They are left out, so the noise-free closures stand alone. They can be added by amendment.
3. **Cross-talk is run and reported, not summed,** as in C_resp.
4. **The zero dump, not the production npz, is the response** (§4).
5. **The products go to HPSS** after the readout (§2.4). They are about 13 MB.
6. **The comparison is oriented by h = −d,** the first-order expectation (§0). The raw cosine of h with +d is not
   written, so a reader cannot mistake agreement for contradiction.
7. **There is no resume** (§0, stop rule). A partial job is a STOP.

## 8. Pinned bytes

At this declaration's commit:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_ct_closure.py` | `85e21d6da8cb595ed40f210a0d10cfabe445091ea6e6b01f1f72ceb8a09d20ad` |
| `nd-unfolding/tests/test_fd_ct_closure.py` | `a84bebc414868e432e4c9af6c5cbd02ee4a1c944073bda51fcccd0d228010450` |
| `nd-unfolding/fd_ct_readers.py` | `f4cc51c8fdba141b4ae3e289ee983d755c0cd5b90a82d40fe71d2e56a4447464` |
| `nd-unfolding/tests/test_fd_ct_readers.py` | `6ca4172937351ff60b8c5611403c0e519b2dbb6ae10a789baf8f578121a543a6` |
| `nd-unfolding/submit_fd_ct.sh` | `7073d4027cf4314432cbcd21d6fce428ed145d34cbe7927ab24ccccd916712d9` |
| `nd-unfolding/fd_f1_lane.py` | `fbcb786923cabd8ab9177525a4b95afaec60486b2a0670ca598d048ebe835a7c` | (unchanged from main) |
| `nd-unfolding/s5c_array.sh` | `dd95db5de1a801eb6b47c8d60bc7da43532ed2ad38e10597ae2db94c0a12526f` | (unchanged from main) |
| `docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh` | `b72aaa627d12e6953ad6b1f40a4ae35ffd9b5439db3c0114defe93742f14c6d3` | (unchanged from main) |
| `nd-unfolding/pv-ladder/pvl_unfold.py` | `59ab0e1154ca287082f6d206d0a344769ef435faef5670b90373312a97636ec1` | (unchanged from main) |
| `nd-unfolding/pv-ladder/pvl_lib.py` | `f8a7d2c2fcd37b025ae3c028088d496b1aea7519d347febb3d63da6511015481` | (unchanged from main) |
| `nd-unfolding/build_cresp.py` | `fe1aec8b74ab59e5ffa3bc824c4284065c5e8e97b2ce3c2e4bd1a34bec192f22` | (unchanged from main) |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/3b/make_3b_tables.py` | `e6ef5eeaca158928f2397aa0214b6bd7b50c3e86f53e002e9d2e6a407b35c10b` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/3b/3b-steps.tsv` | `0d3657ad3a50e81decc559a74d53461185871e8d15da03c39d919789f5ccf68c` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/3b/tasks-3b.tsv` | `680bad854071d77bf4ed3b07b2d26f47cabc2b9932c80b7cf6df7ccbb5406fda` |
| `nd-unfolding/fd_f0_regrade.py` | `0dfa722c2b74abed09fb255ccb7c0e80e6c55eb922ea1326dd74e6c880697aa2` | (unchanged from main) |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` | (unchanged from main) |
| `nd-unfolding/s5p_stage1_inspect.py` | `26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71` | (unchanged from main) |


## 9. Ledger, storage and stops

- **Ledger:** one row each for the deploy and tests, the job (with its `sacct` charge), the readout and the
  preservation.
- **Storage:** `$B` joins the pscratch list. The closures go to HPSS. Nothing goes to CFS.
- **Stops:** §0's stop rule.

## 10. Not changed

C_resp, every covariance, cell, readout and κ; 3a's, 4C's and 5A's readouts; `docs/analysis-note/**`. Claims and
publication are Joseph's.

## 11. Review dispositions

**An independent read-only review** of `1a6955bd`, by a Claude Opus 5.5 subagent on the claude-school account, in its own
detached worktree, which it left clean. Its report is kept verbatim as `fd/receipts-ct/3b/review/REVIEW.txt`
(`25e5043f55c7aa44…`), with its probes and logs.

**It confirmed:**
- the closure construction: zero-on-zero is pv-ladder's closure; a shifted dump changes only the observed rows; the
  zero response is what is unfolded; the window and fakes are handled as pv-ladder and real data;
- the 13 (path, sha256) pairs against the preservation inventory;
- the refinement and estimator checks;
- the leak guard, including a planted data unfold equal to f, which does not refuse falsely;
- the launch plumbing, with the relative steps path resolving from the deploy root;
- the sizing: F1c's packed closures took 812 s per step with a 16.7 GiB peak, so two steps fit the 45-minute limit
  with a 1.6× margin.

**Its findings, and what was done:**
- **H1. The cosine had the sign opposite to agreement.** To first order h = −d, so agreement printed −1. **Done:** the
  readout compares h with −d, writes the residual h + d with its σ ratio and quadratic form, and does not write the
  raw cosine. A test plants h = −d exactly and reads cosine 1, norm ratio 1 and a zero residual (§0, §3, §7 item 6).
- **M1. 3b's readout disowned its own result** through the shared NOT CITABLE list. **Done:** it has its own.
- **M2. h and d differ in construction as well as in sign** (background template, fakes, truth, divisor; cross-talk
  not in C_resp). **Done:** a `construction` label states each, and §0 does too.
- **M3. The output paths were not tied to `$B`, and a partial run cannot resume.** **Done:** the submit line refuses
  unless all 13 steps write under `$B/closures/`, and every refusal precedes any creation. The declaration states that
  there is no resume and that a partial job is a STOP.
- **L1. M1's truth check cannot fire.** **Done:** it is an assertion.
- **L2. No code-digest check on the products.** **Done:** M0 requires each product's `fd_ct_closure.py`,
  `pvl_unfold.py` and `pvl_lib.py` digests to be this deploy's, with a test.
- **L3. Mixed divisors in the closure analogue's ratio.** **Done:** its label says so.
- **L4. A zero norm would hit a format error.** **Done:** the printed line writes "undefined".
- **L5. The tests restated the code, and the submit line had none.** **Done:** the h = −d test encodes the expectation
  independently of the reader's formulas, and `Submit` tests the committed arguments and four refusals.
- **L6. The declaration did not yet exist.** It is this file.
- **L7. MCreco's dtype was not compared, and `$B/logs` was made before the refusals.** **Done:** both.

**Mutation receipt** (`fd/receipts-ct/3b/mutants_3b.log`, on `fd_ct_closure.py` `85e21d6d…`, `fd_ct_readers.py`
`f4cc51c8…` and `submit_fd_ct.sh` `7073d402…`): **36 of 36 killed**, none unapplied, with every file restored. The
mutants cover the driver's truth side, its observed rows and refusals; the reader's M0–M2, its statistics (the floor,
the divisors, the sign, the residual, the half-spans, the analogue) and its guard tables; and the submit line's
refusals, QOS and time limit.

**On the cluster** (login37, at `3dee5faf`): the declared six modules **Ran 184 tests, OK, with none skipped**, so the
real-unfold test ran. The clone had 0 porcelain lines after (`fd/receipts-ct/3b/cluster_tests.out`). Locally the same
set ran 184, OK, with that one skipped.
