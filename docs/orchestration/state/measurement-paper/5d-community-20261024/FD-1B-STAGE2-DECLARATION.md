# DECLARATION 1B with 4A, stage 2: the derivation runs, gate D and the nominal control (2026-10-31)

**By** the measurement session `coverage-5b`, for the director to bind.

**Under** [`FD-1B-BINDING.md`](FD-1B-BINDING.md) (#556), which binds [`FD-1B-DECLARATION.md`](FD-1B-DECLARATION.md)
(`07d0e0b6…`, the protocol), and [`FD-1B-STAGE1-REPORT.md`](FD-1B-STAGE1-REPORT.md) (#569, the code). Every statistic,
window, verdict and stop rule is the protocol's §4–§5. This declaration fixes only how stage 2 runs.

**ASKS TO AUTHORIZE:** stage 2, within its bound ceiling of **23.0 CPU node-h**:
- the login-node steps (0 node-h);
- jobs 2a-0 and 2a (ruling 1);
- gate D and the reproduction check;
- jobs 2b and 2c, each only on its gate;
- the control's interim and final readouts and 4A at the control;
- the stage-2 report.

**CANNOT AUTHORIZE:** stage 3, which needs the control's PASS and its own declaration and binding. Nor any change to
the protocol, the reported covariance, κ or any claim.

**The matrix under test** is unchanged: the reported C_total + C_resp of `fd_data_product.json` (`b79556f0…`), as on
`main` at `91a27ad1`, with no run-period block. The 5B block is to be added by a separate declared step, and every
stage-2 readout names the matrix tested.

## 1. Readings recorded before any toy

1. **The laterals are carried to the truth:** x̂ += Σ_b s_b Δ_b^T / 2, Δ_b^T = Δ_b ⊙ x_T / f. This is the binding's
   intended reading of its x̂ += Σ_b s_b Δ_b / 2. The director, by cross-session message on 2026-10-31: "My binding's
   x̂ += Σ s_b Δ_b/2 was shorthand, and the carried form is what makes the control unbiased. Record this in the
   stage-2 declaration as the binding's intended reading". The code is `fd_1b_score.surrogate`.
2. **4A at the test arms carries no verdict.** The binding's ruling 4 ("graded at the control only") governs the
   protocol's §4.2, which graded the test arms' mean-subtracted χ². The director accepted it on 2026-10-31 with the
   review's fixes. Stage 2 grades 4A only at the control, where it gates nothing.
3. **Gate D's carry** is diag(f / x_T), the control's own carry, not diag(f / x̂(CV)) (stage-1 review, finding 1).
4. **The scorer runs in the toys' environment,** `root_6_28` (Python 3.11.14, numpy 1.26.4, LightGBM 4.6.0, measured
   on login37 on 2026-10-31). It refuses under another numpy, since it re-derives every draw from its seed.

## 2. Pins

| what | pin |
|---|---|
| code | `main` at `d3087e8257b7ad45d32660746dc50e638a800790`, the merge of #569. Deploys are clean clones at the pin, refused by `s5c_array.sh` otherwise |
| inputs | `of_inputs_5d.npz` `07fccc1a…`, `bkg_dump.npz` `2addac8f…` (`s1_assemble`'s constants, which the toy mode re-checks) |
| S1 | `s1_assembly.npz` `db000707…`; the 10 lateral unfolds against the sf1 manifest; X01 `8912376e…`; the definition `b6790761…` |
| flux | the constraint file `e38ad7d2…` |
| truths | none in stage 2 beyond the nominal; the reproduction runs' bridged ratios `25477aae…` (G18) and `eab33d6d…` (AR23), against the committed F1 prep sums |
| F1c targets | `pe/genie_v3_g18/ratio_nd_a1_s806000.npz` and `pe/genie_v3_ar23/ratio_nd_a1_s807000.npz`, against `fd/receipts-f1/run/cluster/manifest/f1-products-SHA256SUMS` |
| weight files | the pins file `$B/pins.json` (step L2), whose sha256 the tables carry |
| the reported matrix | `fd_data_product.json` `b79556f0…`, read from the deploy |

`P=/pscratch/sd/j/josephrb`; `B=$P/fd-1b-20261030`; `PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"`.
Nothing goes to CFS.

## 3. Login-node steps (0 node-h), in order

- **L1. Deploy.** Clone `main` at `d3087e82` into `$B/deploy/stage2`, then check that `git status --porcelain` is empty
  and that `HEAD` is §2's full pin.
- **L2. Pins.** Run `nice -n 19 $PY $B/deploy/stage2/nd-unfolding/fd_1b_toys.py pins --bank
  $P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware --detector-dir $P/s5p-20260926/bank_detector --manifest
  $B/deploy/stage2/docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt
  --detector-receipt $P/s5p-20260926/bank_detector/detector-dump.json --out $B/pins.json`.
  - It hashes 701 files, about 70 GB, each against its recorded digest.
  - Any mismatch refuses: a STOP, reported unrepaired.
- **L3. Tables.** Run `fd_1b_tasks.py tables` for each stage-2 job, with `--deploy $B/deploy/stage2` and the pins
  sha256.
  - The tables, `pins.json`'s sha256 and the L2 log are committed as a records PR, with no code change.
  - The deploy is then re-cloned at that records commit, the tables' pin, and re-checked clean.
- **L4. Preflight.** In the deploy:
  - run `fd_1b_tasks.py submit` for each job and check its lines against §5;
  - confirm that the pins file is unchanged since L2, by `check_pins`;
  - run the derivation check of stage 1 (`derivation_check.py`) again, with rc 0;
  - run `squeue`, which must show none of this lane's jobs, and record the `iris` balance.

## 4. The jobs

Every job is one or more single-node submissions of the committed packer through `s5c_array.sh` →
`fd_f1_lane.py` → `fd_1b_toys.py run`: `-A m3246 -q regular -C cpu`, `--exclusive --no-requeue` (in the packer), 8
lanes of 32 CPUs and 56 GB.

| job | contents | nodes | most per lane | projected wall | limit | enforced cap |
|---|---|---:|---:|---:|---:|---:|
| **2a-0** (ruling 1) | 8 unfolds, one per lane: derivation `CV`, `Flux_0`, `MaRES_1`, `GEANT_Pion_0`; pilot toys 2,600,000 and 2,600,001; the 2 reproduction runs | 1 | 1 | 832 s | 1:00 | **1.00** |
| **2a** | the remaining 194: 172 derivation runs, 14 pilot toys, 8 half-MC pilot toys (2,600,000–007) | 3 | 9 | 2.08 h | 2:40 | **8.00** |
| **2b** | control toys 2,610,000–099 | 2 | 7 | 1.62 h | 2:30 | **5.00** |
| **2c** | control toys 2,610,100–299 | 3 | 9 | 2.08 h | 3:00 | **9.00** |
| **stage 2** | 502 unfolds | | | **15.95 node-h projected** | | **23.00** |

- 2a-0 and 2a together keep the first declaration's job 2a: its 202 unfolds and its 9.00 node-h cap.
- 2a-0 measures first what job 2a was priced on without a measurement. The derivation runs' expectation mode puts
  every reco-passing MC row in the observed sample, and their wall is unmeasured (stage-1 report §5 item 5). The only
  timing hit is A7's half-MC expectation runs, about 400 s on another unfold path
  (`state/s5p/prod-draft/ADMISSION-DRAFT-amendment-7.json:38`).
  Search: git grep -i -E "expectation (construction|mode|pseudo)" docs/orchestration/state, for seconds or walls @ d3087e82
- 2a-0 also runs the reproduction check before 194 unfolds are spent.

**Ruling 1 (the director, by cross-session message on 2026-10-31, ahead of the binding):** "the split is accepted.
2a-0 runs first (1 node, 1:00, cap 1.00, 8 unfolds), then 2a (3 nodes, 2:40, cap 8.00, 194 unfolds)." The
alternative, 2a as first declared (3 nodes, 3:00, cap 9.00), is not taken. The director also ruled that the code
change go in this declaration's PR, "so the binding covers the code that submits":
- `fd_1b_tasks.JOBS` gains 2a-0, and 2a takes the remainder at 2:40. The derivation's four first universes are
  `DERIVATION_FIRST`, and a selection naming a universe S1 did not unfold is refused.
- `DECLARED_CAPS` becomes 1.00 and 8.00 for the two jobs. The stage-2 ceiling check is unchanged.
- `tests/test_fd_1b.py` holds the two jobs against this table:
  - 2a-0 and 2a together are the first declaration's 202 unfolds, each exactly once;
  - 2a-0's eight are the ones named above;
  - each job's nodes, fullest lane, projected wall, limit and cap match this table's row;
  - each limit is at least 1.25 × its projected wall.

  The suite passes (56 tests).

## 5. Gates and stop rules, in order

1. **After 2a-0** (login node):
   - `fd_1b_score.py repro` on the two pairs must read PASS, bitwise. A FAIL is a STOP.
   - **Walls and memory:** let w be the largest `seconds_unfold` among 2a-0's products, and m the largest
     `peak_rss_kib`.
     - If w × 9 exceeds 0.8 × 2:40 (that is, w > 853 s), job 2a is re-priced before it is submitted.
     - If m exceeds 75 % of 56 GB, the job is likewise re-priced before it is submitted.
     - A re-price is a declared amendment, which goes to the director before 2a is submitted (ruling 1).
2. **After 2a: gate D** (login node). Run `fd_1b_score.py gate-d` on the 176 derivation products.
   - PASS iff every ρ_c is in [0.9, 1.1]. A FAIL is a STOP before any coverage toy, reported as a measurement.
   - The half-MC pairs (`fd_1b_score.py pairs`, n 8) are printed beside it, with no verdict.
   - The 16 pilot toys' walls apply the protocol's §6 re-price rule to 2b and 2c: median > 1,040 s, or a lane's peak
     RSS above 42 GB.
3. **2b is submitted only** when gate D, the reproduction and the walls all pass. It also needs a message to the
   director giving gate D's readout, and the director's "go" (ruling 3).
4. **After 2b: the interim look.** Run `fd_1b_score.py score --arm control --look interim` on toys 1–100, at 99.5 %.
   Any FAIL is the control's verdict and a STOP.
5. **2c is submitted only** on the interim's CONTINUE, after a message to the director and the director's "go"
   (ruling 3).
6. **After 2c: the final look** on all 300 toys, at 95 %, with ×0.7 and ×1.3, and 4A at the control.
   - The control's verdict is the protocol's §5.1.
   - Anything but PASS is a STOP: no stage-3 declaration is made, and the control is reported unrepaired.
7. **On every job:**
   - it is ledgered from `sacct` in `fd/receipts-1b/stage2/LEDGER.tsv`;
   - a login-node watcher cancels and reports any job past 1.25 × its projected wall;
   - a failed step is rerun once with the same seed, inside the job's own remaining cap. Any other failure, a
     non-COMPLETED state or a non-zero exit stops and is reported.
8. **Storage.** About 0.27 GB of products go to `$B/runs` and the logs to `$B/logs`. At the stage's end they are
   copied to HPSS with `hsi` `hashcreate` and `hashverify` and a retrieval check. Nothing goes to CFS.

## 6. What stage 2 reports

- **Gate D's readout,** labelled DERIVATION: ρ_c per cell and the per-group σ ratios. That is the first measurement
  of how far the fixed-truth mechanics reproduce S1's blocks, the prior-part gap.
- **The reproduction check** and the half-MC pairs, labelled DERIVATION.
- **The control's interim and final readouts,** labelled RESULT, each naming the matrix tested. Every report states
  that the lateral and normalization surrogates carry 29.0 % of C_e's trace, which the control carries but does not
  test.
- **4A at the control,** gating nothing.
- **The walls, RSS and node-h,** from `sacct`, against §4.

A control FAIL says the machinery is ungraded and nothing about the reported intervals (protocol §5.1).

## 7. Price

- **Projected:** 0.23 + 6.24 + 3.24 + 6.24 = **15.95 node-h**, at the protocol's 832 s per unfold, which the stage-1
  arithmetic derived from S1's and A7's measured walls **(arithmetic)**.
- **Enforced caps:** 1.00 + 8.00 + 5.00 + 9.00 = **23.00**, the bound stage-2 ceiling. Nothing is padded.
- **Balance:** `iris` on login37 at 2026-10-31T10:50:53Z showed m3246 at 17,919.8 of 20,000 charged, so 2,080.2 left.

## 8. Rulings (the director, by cross-session message on 2026-10-31, ahead of the binding)

1. **2a-0, then 2a** (§4), with the re-price trigger of §5 item 1. The `JOBS` change is in this PR.
2. **The L3 records PR** carries the generated tables, `pins.json`'s digest and the L2 log, with no code. It merges on
   the director's review without a new binding.
3. **2b and 2c follow their gates (§5) under this stage-2 binding.** Each needs a message to the director and the
   director's "go".

A separate read-only review of this declaration runs on its PR. Its findings and their dispositions are recorded
there before the binding.

## 9. Not changed

The protocol, the reported covariance, κ, every claim and number, and the data product. Nothing is submitted,
deposited or tagged. The paper's statement that coverage was not validated stands.
<!-- absence-ok: a reference to the decision record's own wording, quoted at DECISION-20261024-joseph-5d-community-standard-route.md:46-47; it claims no search -->
