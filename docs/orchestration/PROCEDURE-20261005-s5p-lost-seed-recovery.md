# s5p (`OI-193`): procedure for the report-only lost-seed recovery (owner decision 2026-10-05 §2)

**CITABLE FOR:**
- how the 277 lost seeds are rerun;
- the determinism check and its criterion, fixed before it runs;
- the budget, concurrency and retry rules;
- how the recovered outcomes are reported.

**NOT CITABLE FOR:**
- any revised primary decision;
- any change to a frozen claim, statistic, stopping rule, seed, batch or estimator setting;
- authority to submit before §6 (independent review) is complete.

**Authority:** `DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md` §2.

**Tool:** `state/s5p/recovery/s5p_recovery.py`, with 10 controls in `test_s5p_recovery.py`. Its tables are
`state/s5p/recovery/tables/`.

## 1. Invariants

- **Seeds.** The seeds are exactly those `seed-states.json` (sha256 `6823e701…`) classifies as interrupted or never
  started:

  | population | lost seeds |
  |---|---|
  | calibration | 224: MnvTune 35, GENIE CV 34, GENIE MEC 57, NuWro 49, GiBUU 49 |
  | power | 53: P1 7, P1g 1, P2 5, P2g 7, P3 5, P3g 28 |

  The recompute lane's independent seed disposition agrees on these sets (its report §5).
- **Arguments.** Each rerun row is the frozen row whose seed range contains the seed, with only three changes:
  `--pseudo-seeds s:s` (one seed per task), `--out <recovery dir>`, and the task name (suffix `-s<seed>-rec`). Every
  other argument is byte-identical: the inputs and their sha256 pins, hypothesis, config, iterations, threads and
  estimator seed. The tests check this.
- **Isolation.** Recovered products go to `$NS/recovery/recovery/{cal,pow}/<lane>/`, and determinism reruns to
  `$NS/recovery/determinism/cal/<null>/`. They never enter `$NS/runs/prod/` or the frozen globs. The frozen
  `joint-evaluate.json` (`b9604502…`), its B values and its primary decisions are unchanged.
- **A product does not depend on its position in the file list.** `s5p_joint.statistics` keys each product's draw by
  its own pseudo seed, so adding products leaves every other product's T unchanged.

## 2. Phase 0: deploy and table check

1. **Deploy.** Make a new clean clone of origin/main at the commit carrying this procedure, as `$NS/deploy/<sha8>`.
   Verify, as `stage7/s5p_terminal_run.sh verify` does:
   - HEAD and a clean tree;
   - frozen modules byte-identical to `4f5a613f`;
   - design `404446eb…` and V `35979ef7…`.
2. **Regenerate the tables from the original classification** (the committed tables were made from the abs-log-path
   copy, whose classification fields are identical):
   `PYTHONPATH=nd-unfolding python3 docs/orchestration/state/s5p/recovery/s5p_recovery.py tables --phase <p>
   --parts <k> --seed-states $NS/stage7/joint/seed-states.json --tables docs/orchestration/state/s5p/prod/tables
   --out-dir $NS/recovery/regen-<p>`, for `determinism` (k = 1) and `recovery` (k = 3).
   `diff` every `.tsv` against the deploy's `state/s5p/recovery/tables/`. They must be identical; otherwise stop.

## 3. Phase A: determinism check (criterion fixed here, before it runs)

- **Seeds:** 10 already-completed calibration seeds, chosen by the tool's rule. For each null they are the smallest
  completed seed of its first batch (originally first in its task) and the last batch's completed seed that ran latest
  in its task (originally sixth). That gives 1220000, 1221205, 1240000, 1241205, 1280000, 1281205, 1200000, 1201205,
  1260000 and 1261605. The second seed of each null tests that a product does not depend on what ran before it in
  the same process; a rerun always runs its seed first.
- **Submit** one array through the meter from the deploy:
  `s5c_meter.py … submit --stage verification_repair --pool cpu --qos shared --ntasks 10 --throttle 10
  --timelimit-h 2.0 --billing 32 --label s5p_rec_determinism --measures "s5p report-only determinism rerun of 10
  completed seeds" --cannot-authorize "a p-value, decision or certification" -- -C cpu --cpus-per-task=32 --mem=56G
  --output=$NS/recovery/logs/%x-%A_%a.out "$D/nd-unfolding/s5c_array.sh" "$D" "<sha>"
  "$D/docs/orchestration/state/s5p/recovery/tables/rec-determinism-part1.tsv" $NS/recovery/tasks`.
  The reservation is 2.5 node-h.
- **Criterion: PASS** only if every array in every rerun `.npz` is bitwise identical to its original's
  (`s5p_recovery.py determinism`). Anything else is **FAIL**, reported per seed with the largest relative difference.
  No tolerance is applied after the fact.
- **On FAIL:** recovery stops. The campaign reports to Joseph, and the wording question for the missing-seed
  sensitivity returns to him (decision §2). A rerun would then be a fresh draw for the same seed, not the lost draw.

## 4. Phase B: recovery (only after a Phase A PASS)

- **Arrays:** `rec-recovery-part1.tsv` (92 tasks), `part2` (92) and `part3` (93). Each is submitted as above with
  `--ntasks <n> --throttle 8 --timelimit-h 2.0`, labels `s5p_rec_recovery_p<k>`, and the same output and tasks
  directories.
- **Time limit:** the slowest completed seed took 5856 s and p99.9 is 3628 s, so a one-seed task fits 2 h.
- **Concurrency:** parts 1 and 2 are open together (8 + 8 = 16 slots = 2.0 nodes, the cap). Part 3 is submitted when
  one of them has left the scheduler.
- **Reservations:** 23.0 per array, at most 46.0 open at once. The verification/repair stage holds 68.287; with the
  determinism charge (≤ 2.5) the meter's cap check passes.
- **Measured cost:** at the mean of 696 s per seed, about 277 × 696 s × 1/8 node ≈ 6.7 billed node-h. The estimate is
  8–12 including the tail and determinism.
- **Retry rule:** a seed lost again (its task killed, or no product) is resubmitted once, in one further array built
  by `tables` from a classification of the recovery logs. If it is lost a second time, it stays missing and is
  reported with the reduced M. No other retry.
- **Refusals:** a meter refusal (exit 3 cap, 4 concurrency) is waited out or reported, never forced. More hours need
  Joseph's decision.

## 5. Phase C: resolution (report only)

1. `s5p_recovery.py resolve --design docs/orchestration/state/s5p/prod/design.json --manifest
   <tables>/rec-recovery-manifest.json --seed-states $NS/stage7/joint/seed-states.json --union-root
   $NS/recovery/union --out-design $NS/recovery/resolution-design.json`.
   - It builds the union directories: symlinks to every frozen product plus every recovered one, with partials
     excluded.
   - It refuses unless each lane's union equals its submitted seed set and no seed is both frozen and recovered.
   - It writes a report-only design copy (`_report_only`) whose globs name the unions and whose counts are the union
     counts.
2. From the deploy, run the frozen `s5p_joint.py evaluate --design $NS/recovery/resolution-design.json --v
   $NS/stage3/V/V-s3v.npz --out $NS/recovery/resolved-evaluate.json`. Then run `s5p_robust_labels.py` on it to get
   `resolved-robust-labels.json`.
3. **Report, per test:**
   - k and B for the frozen evaluation and for the complete submitted set;
   - how many recovered draws reach or exceed the observed statistic, under the claim variants;
   - the decision under the complete set, under Holm with determinacy.

   This is a resolution of the missing-seed sensitivity, labelled report-only. **The primary decisions remain those
   of the frozen evaluation.** If every test's decision is unchanged under the complete set, the "can change" label
   is resolved by observation for the lost draws. Otherwise the change is reported as found. Power under the complete
   power sets is reported the same way.
4. **Independent cross-check:** the recompute lane computes T for the recovered products with its own code, which it
   agreed to do (2026-10-05). Its agreement is required before the resolution is quoted.

## 6. Before any submission

- An independent review of this procedure, the tool and its tests, with its findings resolved and recorded.
- A Phase 0 PASS.
