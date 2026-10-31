# AMENDMENT 1 to 1B stage 2: the half-MC truth fix, job 2a-r and the ceiling rule (2026-10-31)

**By** the measurement session `coverage-5b`, for the director to bind.

**Amends** [`FD-1B-STAGE2-DECLARATION.md`](FD-1B-STAGE2-DECLARATION.md) (`6a054423…`), bound by
[`FD-1B-STAGE2-BINDING.md`](FD-1B-STAGE2-BINDING.md) (#587), after the STOP of job 2a. The director's rulings of
2026-10-31, by cross-session message:
- "option 1, because the half-MC defect is real and should be fixed rather than routed around";
- "(a) 12 unfolds";
- "(b) Count an ended job at its ledgered charge … and an unended one at its cap".

Every statistic, window, verdict and stop rule is still the protocol's, and every other step is still the stage-2
declaration's.

**ASKS TO AUTHORIZE:**
- the login steps A1–A5 (0 node-h), including the move of two products to `$B/quarantine/` and a records PR;
- **job 2a-r** (1 node, 1:00, cap 1.00 node-h);
- then gate 2 as the stage-2 declaration's §5 item 3 writes it, run from the fixed code;
- then 2b and 2c as bound, each after its gate and the director's "go".

**CANNOT AUTHORIZE:**
- any rerun beyond 2a-r's twelve unfolds, or a second rerun of 2a-r;
- any change to a statistic, window, verdict or stop rule;
- stage 3.

## 1. What stopped, and why

Job 60624652 (2a, node 0) ended FAILED 1:0. Its lanes 1 and 2 exited 4 with
`Refusal: fd1b_pilot_half_s2600001.npz: its truth differs from this run's first toy's`, and the same for 2,600,005.
Its other six lanes, and jobs 60624653 and 60624654, completed 0:0.

The cause was a defect in the stage-1 code, found in the field.
- **The rule.** `fd_1b_toys.run` held every unfold of a step to the first one's truth.
- **Where it holds.** That is right in toy and derivation mode, where the truth is fixed.
- **Where it fails.** In half mode each seed's truth is its own half-MC split's (`split_key_for(seed)`, then
  `s5n_pseudo.build_pseudo`), so the rule refused the second seed of every multi-seed half step.
- **A second site.** The scorer's half read-back had the same assumption.

**Why no fixture caught it.** Every half run before 2a had a single seed:
- every stage-1 test (`806000:806000`);
- the two reproduction runs;
- 2a-0's layout of one unfold per lane.

A check that compares item k with item 1 cannot fire on one item.
- **Reviews and receipts.** The stage-1 independent review, the stage-2 review and both mutation receipts all passed.
- **The toy-mode guard** had no test in the direction it acts: at R, the guard's message and variable hit the code
  (`fd_1b_toys.py:410`) and nothing under `nd-unfolding/tests`.
  Search: git grep -E "truth differs|first_truth" -- nd-unfolding/tests @ 664c38db

**What was left unmade:**
- six half-MC pilots, 2,600,001–003 and 2,600,005–007;
- the four derivation universes behind them in lane 2: 2p2h_0, 2p2h_1, 2p2h_2 and AGKYxF1pi_0.

192 of 202 products exist. The pre-gate readout (`$B/score/pilot-walls-pregate.json`, read-only, 21:51Z) shows:
- the 16 pilot toys' median `seconds_unfold`: 664.8 s, against 1,040 s;
- the largest peak RSS: 18,439,836 KiB, against 44,040,192 KiB.

## 2. The fix and the code this amendment adds

- **The fix: #602, merged as `2aa16538a08d903a93db7bed4e1c9a863ffc8450`.**
  - In `fd_1b_toys`, one truth per run is required only in `FIXED_TRUTH_MODES` (toy and derivation). In half mode
    each truth must bitwise-equal `half_truth(seed)`, which is recomputed from the seed's split alone.
  - In `fd_1b_score`, the half read-back checks each toy's recorded split and returns one truth per toy.
    `surrogate` carries each toy's own truth.
  - It adds 6 tests; the 2-seed half step fails on the unfixed code. An independent review found no blockers,
    and its six findings are dispositioned on #602. Mutation receipt: `mutation_half.py`, 7 of 7 killed.
- **This PR, in `fd_1b_tasks`:**
  - **Job 2a-r and `DERIVATION_RERUN`.**
  - **The ceiling rule (§4).**
  - **A refusal to submit an ended job again.**
  - **Tests,** which hold 2a-r to §3, the charge constants to the committed `LEDGER.psv`, and the rule in both
    directions: a charge above its cap refuses, and one at its cap is accepted.
  - **Mutation receipt:** `mutation_amend1.py`, 8 of 8 killed on the merged base (`mutation-amend1.out`). The suite
    is 69 tests, and 101 with `test_fd_f1`.

## 3. The quarantine and job 2a-r

**12 unfolds, ruling (a).** The fix changes `fd_1b_toys.py`, and each product records its code's sha256. The scorer
refuses a set made by different code (`load_toys`: "made by different code from the arm's first toy").
- **The two half pilots made before the fix** (job 60624652, at R's `fd_1b_toys.py` `d55c9eee…`) would make the
  8-toy half set two codes. So they move, and are not deleted:

| product | sha256 | bytes | mtime |
|---|---|---:|---|
| `fd1b_pilot_half_s2600000.npz` | `d7b6d0207c05e1c81eee316cffa66ac570ae56ce5a96b918fae835022a46ac14` | 185,460 | 2026-10-31 13:29:03 -0700 |
| `fd1b_pilot_half_s2600004.npz` | `a19f14db359b15949789f21515dca0cda7c4038b0d5c66c79fa87cfbbaaff0af` | 185,191 | 2026-10-31 12:33:02 -0700 |

  Both were read on login37 at 22:01:18Z. All 8 half pilots then run under the fixed code (`e105b38a…`).
- **The four derivation runs are unaffected:** gate D does not check code. Their 172 siblings are at R's code, and
  the two differ only by #602's diff, which leaves the derivation path's computation as it was.

| job | contents, in order | nodes | lanes | most per lane | projected wall | limit | enforced cap |
|---|---|---:|---:|---:|---:|---:|---:|
| **2a-r** | half-MC pilots 2,600,000–007, then derivation 2p2h_0, 2p2h_1, 2p2h_2, AGKYxF1pi_0 | 1 | 8 | 2 | 1,664 s | 1:00 | **1.00** |

- **Lane layout.** Lanes 0–3 each run two half pilots, and lanes 4–7 each run one derivation universe.
- **Measured walls.** Half 380–389 s and derivation 648–801 s, plus each step's load of about 13–16 s, put the
  fullest lane near 830 s.
- **The price.** At the protocol's 832 s unit, the fullest lane is 2 × 832 = 1,664 s. The 1:00 limit is 2.2 times
  that.

## 4. The ceiling rule, ruling (b): a change from the stage-2 binding's sum of caps

The stage-2 binding capped stage 2 at 23.00 node-h. `fd_1b_tasks` read that as the sum of the enforced caps (1 + 8 +
5 + 9). With 2a-r that sum is 24.00, and the check would refuse.
- **The rule.** An ended job counts at its ledgered charge, NNodes × Elapsed from `sacct`, held as committed
  constants (`CHARGED_NODE_S`), with a test that they equal `receipts-1b/stage2/LEDGER.psv`. A job not yet ended
  counts at its cap.
- **Refusals.** A ledgered charge above its job's cap refuses, and so does an ended job submitted again.

| job | state | counts | node-h |
|---|---|---|---:|
| 2a-0 (60623576) | ended, COMPLETED | 1 × 00:13:54 | 0.232 |
| 2a (60624652–54) | ended, 1 FAILED, 2 COMPLETED | 1 × (01:40:22 + 01:40:46 + 01:40:37) | 5.029 |
| 2a-r | not yet run | its cap | 1.000 |
| 2b | not yet run | its cap | 5.000 |
| 2c | not yet run | its cap | 9.000 |
| **stage 2** | | | **20.261 ≤ 23.00** |

## 5. Steps, in order

Any step that does not end as stated is a STOP, reported unrepaired. The director is told before each connect and
each submission. The names are the stage-2 declaration's §2, plus:
- `M2`, this PR's merge;
- `R2`, the head of the A2 records branch, cut from M2;
- `D2=$B/deploy/stage2-r`, at R2;
- `TK2` and `SC2`, `$PY $D2/nd-unfolding/fd_1b_tasks.py` and `$PY $D2/nd-unfolding/fd_1b_score.py`.

- **A1. Tables** (local, 0 node-h). On a branch cut from M2, run `python3 nd-unfolding/fd_1b_tasks.py tables --job
  2a-r --deploy $D2 --pins-sha256 PINS --out-dir $R1B/tables`. PINS is unchanged.
- **A2. Records.** Commit the two 2a-r tables and the regenerated MANIFEST, and nothing else. The head is **R2**,
  which opens as a records PR and merges on the director's review.
- **A3. The deploy.** Run `git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D2 && git -C $D2
  checkout --quiet --detach R2`.
  - The porcelain must be empty, and HEAD must be R2.
  - `git -C $D2 diff --name-only M2 R2` may list only the two tables and `MANIFEST.tsv`.
- **A4. Preflight** (in `$D2`):
  - `$TK2 submit --job 2a-r --deploy $D2 --pin R2 > $B/logs/a4-submit-2a-r.txt` gives one line, with `-t 01:00:00`.
  - `sha256sum $B/pins.json` equals PINS, and `check_pins` returns rc 0, as in L5.
  - The derivation check, run from `$D2`, diffs empty against its committed output.
  - `squeue` names no `fd1b` job.
  - Half of iris's remaining balance must be at least 3.0 node-h, which is 23.00 − 20.26 rounded up.
- **A5. The quarantine.**
  - Run `mkdir -p $B/quarantine && mv $B/runs/pilot-half/fd1b_pilot_half_s2600000.npz
    $B/runs/pilot-half/fd1b_pilot_half_s2600004.npz $B/quarantine/`.
  - `sha256sum $B/quarantine/*.npz` must equal §3's two digests.
  - `$B/runs/pilot-half` must then hold no `.npz`.
- **A6. Job 2a-r,** after a message to the director and the director's "go": `bash $B/logs/a4-submit-2a-r.txt`, once.

## 6. Gate 2, after 2a-r

- **Job checks.** The job must be ledgered, end COMPLETED 0:0, have every step 0:0, and leave no partial. Any
  failure is a STOP.
- **The gate itself.** Gate 2 is the stage-2 declaration's §5 item 3, run with `$SC2` and `$TK2` (the fixed code) in
  place of `$SC` and `$TK`, with the same arguments:
  - gate D on all 176 derivation products;
  - `pairs` on the 8 half-MC pilots, all made by one code, against the 8 full pilots;
  - `walls --after 2a`.
- **Results** go to the director before 2b.
- **2b and 2c** then run as bound: their tables at R, their submit lines `$B/logs/l5-submit-2b.txt` and
  `l5-submit-2c.txt`, and their deploy `$D`.
  - Their toys run toy mode, where #602 changes nothing.
  - Their looks are scored with `$SC2`, so every stage-2 readout comes from one scorer.

## 7. Not changed

The protocol, the reported covariance, κ, every claim and number, and the data product. The stage-2 declaration's
statistics, gates and stop rules are unchanged. Its jobs 2b and 2c are unchanged. Nothing is submitted, deposited or
tagged until the binding.
