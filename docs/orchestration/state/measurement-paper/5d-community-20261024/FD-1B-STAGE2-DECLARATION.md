# DECLARATION 1B with 4A, stage 2: the derivation runs, gate D and the nominal control (2026-10-31)

**By** the measurement session `coverage-5b`, for the director to bind.

**Under** [`FD-1B-BINDING.md`](FD-1B-BINDING.md) (#556), which binds [`FD-1B-DECLARATION.md`](FD-1B-DECLARATION.md)
(`07d0e0b6…`, the protocol), and [`FD-1B-STAGE1-REPORT.md`](FD-1B-STAGE1-REPORT.md) (#569, the code). Every statistic,
window, verdict and stop rule is the protocol's §4–§5. This declaration fixes only how stage 2 runs.

**ASKS TO AUTHORIZE:** stage 2, within its bound ceiling of **23.0 CPU node-h**:
- the login-node steps (0 node-h);
- jobs 2a-0 and 2a (ruling 1);
- the reproduction check, the walls rules and gate D;
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

## 2. Pins and names

| what | pin |
|---|---|
| code | **M**, the merge of this PR into `main`; the code it runs is `main` at `d3087e82` (#569) plus this PR's `fd_1b_tasks.py` and its tests |
| run pin | **R**, the head commit of the L3 records branch, cut from M; `git diff --name-only M R` may list only what L3 names. Deploys are clean clones at R, which `s5c_array.sh` checks against `--pin` |
| inputs | `of_inputs_5d.npz` `07fccc1a…`, `bkg_dump.npz` `2addac8f…` (`s1_assemble`'s constants, which the toy mode re-checks) |
| S1 | `s1_assembly.npz` `db000707…`; the 10 lateral unfolds against the sf1 manifest; X01 `8912376e…`; the definition `b6790761…` |
| flux | the constraint file `e38ad7d2…` |
| truths | none in stage 2 beyond the nominal; the reproduction runs' bridged ratios `25477aae…` (G18) and `eab33d6d…` (AR23), against the committed F1 prep sums |
| F1c targets | `$F1C/pe/genie_v3_g18/ratio_nd_a1_s806000.npz` and `$F1C/pe/genie_v3_ar23/ratio_nd_a1_s807000.npz`, against `$SUMS` (both present on login37 on 2026-10-31) |
| weight files | the pins file `$B/pins.json` (L2), whose sha256 the tables carry |
| the reported matrix | `fd_data_product.json` `b79556f0…`, read from the deploy |

The names used below:

```
P=/pscratch/sd/j/josephrb   B=$P/fd-1b-20261030   PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
DP=$B/deploy/stage2-pins (at M, for L2 only)   D=$B/deploy/stage2 (at R, every job)
TK="$PY $D/nd-unfolding/fd_1b_tasks.py"   SC="$PY $D/nd-unfolding/fd_1b_score.py"
BANK=$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware   DET=$P/s5p-20260926/bank_detector
CON=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
S1NPZ=$P/s1-20261024/s1_assembly.npz   F1C=$P/fd-f1-20261027/f1c
R1B=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b
SUMS=$D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/run/cluster/manifest/f1-products-SHA256SUMS
TOYREAD="--s1-npz $S1NPZ --flux-constraint $CON --lateral-dir $P/s5p-20260926/runs/s3/latunf
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json --inputs-npz $P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
  --x01 $P/2d-closeout-c04repair-20261012/build/minos_rescaled.npz
  --manifest $D/docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt"
```

Every command writes its output to a file under `$B/logs` or `$B/score` and records its exit status with
`; echo rc=$? >> <log>`, never through a pipe. Nothing goes to CFS.

## 3. Login-node steps (0 node-h), in order

Any step that does not end as stated is a STOP, reported unrepaired.

- **L1. The pins deploy.** Run `mkdir -p $B/deploy $B/logs $B/runs $B/score`, then `git clone --quiet
  https://github.com/josephbaileyy/MINERvA-OmniFold $DP && git -C $DP checkout --quiet --detach M`.
  - `git -C $DP status --porcelain` must be empty.
  - `git -C $DP rev-parse HEAD` must be M.
- **L2. Pins.** Run `nice -n 19 $PY $DP/nd-unfolding/fd_1b_toys.py pins --bank $BANK --detector-dir $DET --manifest
  $DP/docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt --detector-receipt
  $DET/detector-dump.json --out $B/pins.json > $B/logs/l2-pins.log 2>&1`.
  - It must end with rc 0. It hashes 701 files, about 70 GB, each against its recorded digest, and any mismatch
    refuses.
  - Then `sha256sum $B/pins.json > $B/logs/l2-pins.sha256`. Its digest is PINS below.
- **L3. Tables and records** (this session's local worktree, 0 node-h).
  - Cut a branch from M. For each J in 2a-0, 2a, 2b and 2c, run `python3 nd-unfolding/fd_1b_tasks.py tables --job J
    --deploy $D --pins-sha256 PINS --out-dir $R1B/tables`. The tables name `$D`, the run deploy, which L4 clones
    later. Nothing is moved.
  - Commit the eight tables, `pins.json`, `l2-pins.log` and `l2-pins.sha256` under `$R1B/stage2/`, with their
    MANIFEST-overrides, MANIFEST and CATALOG rows. No other path is committed.
  - Push the branch. Its head is **R**, and it opens as the records PR (ruling 2).
- **L4. The run deploy, after the records PR merges.** Run `git clone --quiet
  https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach R`.
  - `git -C $D status --porcelain` must be empty.
  - `git -C $D rev-parse HEAD` must be R.
  - `git -C $D diff --name-only M R` must list only L3's paths.
- **L5. Preflight** (in `$D`):
  - **Submit lines.** For each J, run `$TK submit --job J --deploy $D --pin R > $B/logs/l5-submit-J.txt`. The file
    must have §4's node count, with `-t` at §4's limit, and every table it names must exist under `$D`.
  - **The pins file.** `sha256sum $B/pins.json` must equal PINS. Then run
    `$PY -c "import json, sys; from pathlib import Path; sys.path.insert(0, '$D/nd-unfolding'); import fd_1b_toys as t;
    t.check_pins(json.load(open('$B/pins.json')), Path('$BANK'), Path('$DET')); print('pins unchanged')"
    > $B/logs/l5-pins.log 2>&1`, which must end with rc 0.
  - **The derivation check.** Run `$PY $D/$R1B/stage1/derivation_check.py --deploy $D > $B/logs/l5-derivation-check.json
    2> $B/logs/l5-derivation-check.err`. It must end with rc 0, and `diff <(sed '1,3d;$d'
    $D/$R1B/stage1/derivation-check.out) $B/logs/l5-derivation-check.json` must be empty.
  - **The queue.** `squeue --me -h -o %j > $B/logs/l5-squeue.txt` must name no `fd1b` job.
  - **The balance.** `iris` must show half of m3246's remaining balance at 23.0 node-h or more (the director's
    half-of-remaining rule), and is recorded.

## 4. The jobs

Each job is one or more single-node submissions of the committed packer, run as `bash $B/logs/l5-submit-J.txt`:
`s5c_array.sh` → `fd_f1_lane.py` → `fd_1b_toys.py run`, with `-A m3246 -q regular -C cpu`, `--exclusive
--no-requeue` (in the packer), and 8 lanes of 32 CPUs and 56 GB. The packer splits each job's items, in the order
below, into contiguous lanes.

| job | contents, in order | nodes | most per lane | projected wall | limit | enforced cap |
|---|---|---:|---:|---:|---:|---:|
| **2a-0** | 8 unfolds, one per lane: derivation `CV`, `Flux_0`, `MaRES_1`, `GEANT_Pion_0`; pilot toys 2,600,000 and 2,600,001; reproduction G18 806,000 and AR23 807,000 (half-MC, `--no-draws`) | 1 | 1 | 832 s | 1:00 | **1.00** |
| **2a** | 194 unfolds: pilot toys 2,600,002–015; half-MC pilot toys 2,600,000–007; the other 172 derivation universes, in S1's order | 3 | 9 | 2.08 h | 2:40 | **8.00** |
| **2b** | control toys 2,610,000–099 | 2 | 7 | 1.62 h | 2:30 | **5.00** |
| **2c** | control toys 2,610,100–299 | 3 | 9 | 2.08 h | 3:00 | **9.00** |
| **stage 2** | 502 unfolds | | | **15.95 node-h projected** | | **23.00** |

- 2a-0 and 2a together are the first declaration's job 2a: its 202 unfolds, each exactly once, and its 9.00 node-h.
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
- `fd_1b_tasks.py walls` computes §5's re-price rules from the products and the job tables.
- `tests/test_fd_1b.py` holds the two jobs against this table:
  - 2a-0 and 2a together are the first declaration's 202 unfolds, each exactly once;
  - 2a-0's eight are the ones named above;
  - each job's nodes, fullest lane, projected wall, limit and cap match this table's row;
  - each limit is at least 1.25 × its projected wall.

  The tests also hold `walls` at each threshold, on both sides. The suite passes (59 tests). The mutation receipt
  `$R1B/stage2/mutation.out` covers the changed code.

## 5. Gates and stop rules, in order

A gate passes only on the verdict named. Any other verdict (FAIL, INSUFFICIENT, INVALID, REPRICE) or a refusal
(non-zero exit) is a STOP, except that REPRICE goes to the director as an amendment.

1. **After 2a-0** (login node):
   - `$SC repro --pair $B/runs/repro-g18/fd1b_repro-g18_s806000.npz=$F1C/pe/genie_v3_g18/ratio_nd_a1_s806000.npz
     --pair $B/runs/repro-ar23/fd1b_repro-ar23_s807000.npz=$F1C/pe/genie_v3_ar23/ratio_nd_a1_s807000.npz --f1c-sums
     $SUMS --f1c-runs $F1C --out $B/score/repro.json` must read PASS: both pairs bitwise equal.
   - `$TK walls --after 2a-0 --out $B/score/walls-2a-0.json` must read PASS.
     - It refuses a missing product, and any product made under a numpy other than the login's 1.26.4. So an
       environment mismatch shows here, before 194 unfolds, not at the scorer.
     - Let w and L be the largest `seconds_unfold` and `seconds_load` among 2a-0's products.
     - 2a's fullest lane has 2 steps and 9 unfolds, and each step pays its own load. 2a is re-priced if 2L + 9w
       exceeds 0.8 × 2:40 = 7,680 s. With no load, that is the director's w > 853 s, so counting the load only
       tightens it.
     - 2a is also re-priced if any product's `peak_rss_kib` exceeds 75 % of 56 GiB, 44,040,192 KiB (the protocol's
       "75 % of its 56 GB", the director's "42 GB").
     - A re-price goes to the director as an amendment before 2a is submitted (ruling 1).
2. **2a is submitted** on both PASSes.
3. **After 2a** (login node):
   - **Gate D.** `$SC gate-d --derivation $B/runs/derivation --tag fd1b_derivation --s1-npz $S1NPZ --flux-constraint
     $CON --out $B/score/gate-d.json` reads all 176 derivation products.
     - PASS iff every ρ_c is in [0.9, 1.1].
     - A FAIL is a STOP before any coverage toy, reported as a measurement.
   - **The half-MC pairs.** `$SC pairs --full $B/runs/pilot --full-tag fd1b_pilot --half $B/runs/pilot-half
     --half-tag fd1b_pilot_half --n 8 $TOYREAD --out $B/score/pairs.json` prints the pairs with no verdict.
     - Its refusal is a STOP, since it reads the pilot toys through the control's own read-back.
   - **The pilot's walls.** `$TK walls --after 2a --out $B/score/walls-2a.json` must read PASS.
     - It applies the protocol's §6 re-price rule: the 16 pilot toys' median `seconds_unfold` against 1.25 × 832 =
       1,040 s, and every 2a-0 and 2a product's peak RSS against 44,040,192 KiB.
     - `seconds_unfold` is the per-toy wall: it includes the draw and the pseudo-data build. It leaves out the step's
       one-time load.
     - A REPRICE re-prices 2b and 2c by amendment before 2b. As the protocol says, it also carries into stage 3's
       declaration.
4. **2b is submitted** when the reproduction, both walls rules and gate D have passed. It also needs a message to the
   director giving gate D's readout, and the director's "go" (ruling 3).
5. **After 2b: the interim look.** `$SC score --arm control --look interim --toys $B/runs/control --tag fd1b_control
   $TOYREAD --out $B/score/control-interim.json`, on toys 2,610,000–099 at 99.5 %.
   - A FAIL is the control's verdict and a STOP.
   - CONTINUE is the only pass.
6. **2c is submitted** on the interim's CONTINUE, after a message to the director and the director's "go"
   (ruling 3).
7. **After 2c: the final look.** `$SC score --arm control --look final --toys $B/runs/control --tag fd1b_control
   $TOYREAD --out $B/score/control-final.json`, on all 300 toys at 95 %, with ×0.7 and ×1.3, and 4A at the control.
   - The control's verdict is the protocol's §5.1.
   - Anything but PASS is a STOP: no stage-3 declaration is made, and the control is reported unrepaired.
8. **On every job:**
   - **The ledger.** When the job ends, run `sacct -j <its job ids> -X -P -n -o
     JobID,JobName,State,ExitCode,Elapsed,NNodes,Start,End,AllocTRES >> $B/logs/LEDGER.psv`. Its rows are committed as
     `$R1B/stage2/LEDGER.psv` in the stage-2 report, with node-h charged as NNodes × Elapsed.
   - **The time limit is the enforced cap.** No watcher cancels a job early: a cancel at 1.25 × the projected wall
     would kill 2a-0's measurement exactly when the wall is long. A job running past its projection is reported.
   - **A failed job is a STOP.** That means a state other than COMPLETED, an exit code other than 0:0, or a step with
     a non-zero rc in its lane log.
     - The protocol's same-seed rerun of a failed step (protocol §5.1, "A failed step is rerun with the same seed") has
       no pre-declared job, because the caps fill the 23.0 ceiling.
     - It comes to the director as an amendment, giving the rerun's single-node limit and cap and the node-h charged
       so far.
     - Any `*.npz.partial-*` is moved to `$B/quarantine/`, not deleted, before the rerun.
     - The toy mode skips any product already written, so a rerun redoes only the missing ones.
9. **Storage.** About 0.3 GB of products go to `$B/runs`, and logs and readouts to `$B/logs` and `$B/score`. At the
   stage's end:
   - `tar -cf $B/stage2.tar -C $B runs logs score pins.json`;
   - `hsi mkdir -p fd-1b-20261030`, then `hsi put $B/stage2.tar : fd-1b-20261030/stage2.tar`;
   - `hsi hashcreate fd-1b-20261030/stage2.tar`, then `hsi hashverify fd-1b-20261030/stage2.tar`;
   - a retrieval check: `hsi get $B/stage2-retrieved.tar : fd-1b-20261030/stage2.tar`, then `cmp` against
     `$B/stage2.tar`.

   Nothing goes to CFS.

## 6. What stage 2 reports

- **Gate D's readout,** labelled DERIVATION: ρ_c per cell and the per-group σ ratios. That is the first measurement
  of how far the fixed-truth mechanics reproduce S1's blocks, the prior-part gap.
- **The reproduction check, the half-MC pairs and both walls readouts,** labelled DERIVATION.
- **The control's interim and final readouts,** labelled RESULT, each naming the matrix tested.
  - Every report states that the lateral and normalization surrogates carry 29.0 % of C_e's trace, that the control
    carries them but does not test them, and that only 71.0 % is tested through the estimator (binding ruling 2).
- **4A at the control,** gating nothing.
- **The walls, RSS and node-h,** from the ledger, against §4.

A control FAIL says the machinery is ungraded and nothing about the reported intervals (protocol §5.1).

## 7. Price

- **Projected:** 0.23 + 6.24 + 3.24 + 6.24 = **15.95 node-h**, at the protocol's 832 s per unfold, which the stage-1
  arithmetic derived from S1's and A7's measured walls **(arithmetic)**.
  - The protocol projected 15.7 for stage 2 (`FD-1B-DECLARATION.md` §7).
  - The 0.23 difference is 2a-0's own node, for one unfold per lane.
- **Enforced caps:** 1.00 + 8.00 + 5.00 + 9.00 = **23.00**, the bound stage-2 ceiling. Nothing is padded.
- **Balance:** `iris` on login37 at 2026-10-31T10:50:53Z showed m3246 at 17,919.8 of 20,000 charged. That leaves
  2,080.2, half of it 1,040.1, against the 23.00. L5 measures it again.

## 8. Rulings (the director, by cross-session message on 2026-10-31, ahead of the binding)

1. **2a-0, then 2a** (§4), with the re-price trigger of §5 item 1. The `JOBS` change is in this PR.
2. **The L3 records PR** carries the generated tables, `pins.json`, its digest and the L2 log, with no code. It
   merges on the director's review without a new binding.
3. **2b and 2c follow their gates (§5) under this stage-2 binding.** Each needs a message to the director and the
   director's "go".

**The independent review** of this declaration (a separate read-only Claude agent in this session's account) found
2 blockers, 9 should-fix items and 11 nits. Its findings and dispositions are on the PR.

The review's fixes change two things the rulings accepted, for the binding to confirm:
- §5 item 1's trigger now counts each step's load, so it is tighter than w > 853 s, never looser;
- the declared watcher is removed (§5 item 8).

## 9. Not changed

The protocol, the reported covariance, κ, every claim and number, and the data product. Nothing is submitted,
deposited or tagged. The paper's statement that coverage was not validated stands.
<!-- absence-ok: a reference to the decision record's own wording, quoted at DECISION-20261024-joseph-5d-community-standard-route.md:46-47; it claims no search -->
