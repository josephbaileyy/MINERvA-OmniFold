# s5p (`OI-193`): procedure for the report-only lost-seed recovery (owner decision 2026-10-05 §2)

**CITABLE FOR:**
- how the 277 lost seeds are rerun;
- the determinism check and its criterion, fixed before it runs;
- the budget, concurrency and retry rules;
- how the recovered outcomes are reported.

**NOT CITABLE FOR:**
- any revised primary decision;
- any change to a frozen claim, statistic, stopping rule, seed, batch or estimator setting;
- authority to submit before §7 is complete.

**Authority:** `DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md` §2.

**Tool:** `state/s5p/recovery/s5p_recovery.py`, with 33 controls: 27 unit controls in `test_s5p_recovery.py` and 6
end-to-end controls in `test_s5p_recovery_world.py`. The end-to-end controls run the real `s5p_joint.test_null`,
`s5p_seqstop.main` and `s5p_inference` on a synthetic two-cell world, with real controller status files. Its tables are
`state/s5p/recovery/tables/`.

**Review history:** independent review 1 (2026-10-05, a fresh read-only agent in an isolated worktree, of
`0a988bc4`) returned **NOT READY**, with 1 blocking and 7 should-fix findings. Independent review 2 (a fresh agent, of
`baf1d64d`) returned **NOT READY**, with 1 blocking and 6 should-fix findings plus 7 notes. §8 and §9 list each
finding and its resolution.

## 1. Invariants

- **Seeds.** The seeds are exactly those `seed-states.json` (sha256 `6823e701…`) classifies as interrupted or never
  started:

  | population | lost seeds |
  |---|---|
  | calibration | 224: MnvTune 35, GENIE CV 34, GENIE MEC 57, NuWro 49, GiBUU 49 |
  | power | 53: P1 7, P1g 1, P2 5, P2g 7, P3 5, P3g 28 |

  The review recomputed these sets independently, and the recompute lane's seed disposition agrees (its report §5).
- **Arguments.** Each rerun row is the frozen row whose seed range contains the seed, with only three changes:
  `--pseudo-seeds s:s` (one seed per task), `--out <recovery dir>`, and the task name (suffix `-s<seed>-rec`). The
  reviews checked every lane and part row against `prod/tables` (586 rows in this revision): 0 other differences.
- **Isolation.** Recovered products go to `$NS/recovery/recovery/{cal,pow}/<lane>/`, and determinism reruns to
  `$NS/recovery/determinism/{cal,pow}/<lane>/`. They never enter `$NS/runs/prod/` or the frozen globs. The frozen
  `joint-evaluate.json` (`b9604502…`), its B values and its primary decisions are unchanged.
- **Adding products does change the shifted variants (corrected).** `s5p_joint.statistics` keys each product's draw by
  its own pseudo seed, so the unshifted (c = 0) T of every other product is unchanged. The process-shift variants
  c = 0.5 and 1.0, however, use S built from the calibration ensemble's mean (`s5p_joint.shift_vector`,
  `b = F.mean(0) − mu`). A union evaluation therefore moves S, and with it every draw's shifted T. §5 consequently
  reports both readings: (a) the union with S recomputed, and (b) the recovered draws under the FROZEN S. Any
  difference between them is reported as found.

## 2. Phase 0: deploy, tables and self-validation (no submission)

1. **Deploy.** Make a new clean clone of origin/main at the commit carrying this procedure, as `$NS/deploy/<sha8>`
   (`D`). Verify:
   - HEAD and a clean tree;
   - **The whole producer side is frozen.** Rather than a hand-listed closure, which would miss an import:
     `git -C $D diff --name-only 4f5a613f HEAD -- nd-unfolding ':(exclude)nd-unfolding/pet/**'
     ':(exclude)nd-unfolding/tests/**' ':(exclude)nd-unfolding/gbdt_model_dependence/**'
     ':(exclude)nd-unfolding/*.md'` must print exactly `s5p_missing_sensitivity.py`, `s5p_requeue.py` and
     `s5p_robust_labels.py`. These are report-step and requeue tools, not imported by the producer; this was
     measured at the procedure's commit. In addition, `git -C $D diff --quiet 4f5a613f HEAD --
     docs/orchestration/state/s5p/ratios docs/orchestration/state/s5p/prod/tables
     2d-unfolding/unfold_2d_omnifold_unbinned.py setup_salloc_env.sh` must give rc 0. That covers the hypotheses, the
     frozen tables, the refinement module that `s5n_pseudo` imports and hashes, and the environment script that
     `s5c_array.sh` sources;
   - design `404446eb…` and V `35979ef7…`; budget `be29f2c3…`, equal to the ledger's last budget record;
   - `sha256sum $NS/stage7/joint/seed-states.json` is `6823e701…`.
2. **Unpinned inputs unchanged.** Let REF be the earliest production status file, `ls -tr
   $NS/runs/prod/status/*-B0.json | head -1`; it was written before any batch was submitted. Then
   `find -L <bank> <detector-dir> \( -newer REF -o -cnewer REF \)` must print nothing. `-L` follows symlinks, and
   `-cnewer` catches an older file copied in with its mtime preserved. This guards the unpinned inputs as a whole;
   the determinism check alone would cover only the 16 seeds' universes. The bank is `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware`;
   the detector directory is `$NS/bank_detector`. The npz and bkg inputs are sha256-pinned in every row.
3. **Fresh, isolated output.**
   - `$NS/recovery/determinism`, `$NS/recovery/recovery` and `$NS/recovery/union` must not exist.
   - `realpath $NS/recovery` must not lie under `$NS/runs/prod`.
   - Then `mkdir -p $NS/recovery/logs $NS/recovery/tasks`, because Slurm does not create `--output` directories.
4. **Tables.** Regenerate the tables from the original classification:
   `PYTHONPATH=nd-unfolding python3 docs/orchestration/state/s5p/recovery/s5p_recovery.py tables --phase <p>
   --parts <k> --seed-states $NS/stage7/joint/seed-states.json --tables docs/orchestration/state/s5p/prod/tables
   --out-dir $NS/recovery/regen-<p>`, for `determinism` (k = 1) and `recovery` (k = 3). `diff` every `.tsv` against
   the deploy's `state/s5p/recovery/tables/`; they must be identical. Each regenerated manifest must record
   `seed_states_sha256` `6823e701…`. Its per-lane seed lists must equal the committed manifest's, which was made
   from the abs-log-path copy and so records `bd25f1ec…`.
5. **Self-validation of the resolution code on the frozen products** (login node, no submission; every command
   with `PYTHONPATH=nd-unfolding`):
   - **`frozen-s`** with the frozen design and an empty recovery manifest (a copy of the recovery manifest with every
     `seeds` list emptied). It checks against the FROZEN ARTIFACT `joint-evaluate.json`, not only against itself.
     For every null it must reproduce exactly:
     - the claim and robust variant names, in order;
     - each variant's p, k, B, interval, and null-T median and SD (ddof 0);
     - each robust variant's p, k and B;
     - `T_total_obs` and `T_shape_obs`;
     - every power set's `claim_rule` values.

     It raises otherwise. Its complete-set decisions must equal the primary decisions.
   - **`stopping`** with the frozen design as `--design`. Every look must have `reproduces_frozen_look: true`: the
     controller's B, the per-test k, B and stop, the overall stop, `min` and `thresholds`, at every frozen look.

   Any failure stops the procedure.

## 3. Phase A: determinism check (criterion fixed here, before it runs)

- **Seeds:** 16 already-completed seeds, chosen by the tool's rule.
  - **Calibration, per null:** the smallest completed seed of the first batch (originally first in its task), and the
    last batch's completed seed that ran latest in its task (originally sixth). That gives 1220000, 1221205, 1240000,
    1241205, 1280000, 1281205, 1200000, 1201205, 1260000 and 1261605.
  - **Power, per lane:** the completed seed that ran latest in its task. That gives 1451005, 1481005, 1461005,
    1491005, 1471005 and 1501029. These cover the `--alternative` code path, which 53 of the 277 seeds use.
  - **Why late positions:** a rerun always runs its seed first in a fresh process, so the late-position seeds test
    that a product does not depend on what ran before it.
- **Submit** one array through the meter from `D`:
  `s5c_meter.py --budget docs/orchestration/state/s5p/budget.json --ledger $NS/ledger/admissions.jsonl submit
  --stage verification_repair --pool cpu --qos shared --ntasks 16 --throttle 16 --timelimit-h 2.0 --billing 32
  --label s5p_rec_determinism --measures "s5p report-only determinism rerun of 16 completed seeds"
  --cannot-authorize "a p-value, decision or certification" -- -C cpu --cpus-per-task=32 --mem=56G
  --output=$NS/recovery/logs/%x-%A_%a.out "$D/nd-unfolding/s5c_array.sh" "$D" "<full sha>"
  "$D/docs/orchestration/state/s5p/recovery/tables/rec-determinism-part1.tsv" $NS/recovery/tasks`.
  The reservation is 16 × 2.0 × 32/256 = 4.0 node-h, at 2.0 nodes.
- **When it has left the scheduler:**
  1. `sacct -j <array> -n -X -o JobID,JobIDRaw -P | tr '|' '\n' > $NS/recovery/determinism-jobids.txt`, which gives
     both id forms of every task.
  2. `s5p_recovery.py determinism --manifest <tables>/rec-determinism-manifest.json --tables <prod tables>
     --job-ids $NS/recovery/determinism-jobids.txt --out $NS/recovery/determinism.json`.
- **Criterion: PASS** only if, for every one of the 16 seeds, all of the following hold. Anything else is **FAIL**,
  reported per seed. No tolerance is applied after the fact.
  - Every non-`meta` array (`xsec_flat`, `xtrue_flat`) is bitwise identical in dtype, shape and bytes. Since T is a
    deterministic function of `xsec_flat` and of draws keyed by the pseudo seed, this makes T identical.
  - The `meta` JSON is equal after removing exactly the per-run fields: top-level `slurm_job` and `seconds_unfold`,
    and `seconds` inside any `refinement` dict. Everything else must match, including `pseudo_seed`, `split_key`,
    `nuisance_draw`, the code and input sha256 and the hypothesis and alternative sha256.
  - The rerun's `slurm_job` is a task id of the determinism array and differs from the original's.
  - The original and the rerun are different files.
- **On FAIL:** recovery stops. The campaign reports to Joseph, and the wording question for the missing-seed
  sensitivity returns to him (decision §2). A rerun would then be a fresh draw for the same seed, not the lost draw.

## 4. Phase B: recovery (only after a Phase A PASS)

- **Arrays:** the `rec-recovery-part1.tsv` (92 tasks), `part2` (92) and `part3` (93) tables. Each is submitted as in
  §3 with `--ntasks <n> --throttle 8 --timelimit-h 2.0`, labels `s5p_rec_recovery_p<k>` and the same output and tasks
  directories.
- **Time limit:** the slowest completed seed took 5856 s and the longest setup 57 s, which is 82% of 2 h.
- **Concurrency:** parts 1 and 2 are open together (8 + 8 = 16 slots = 2.0 nodes, the cap). Part 3 is submitted when
  one of them has left the scheduler.
- **Reservations:** 23.0, 23.0 and 23.25. At most two arrays are open at once (46.0 or 46.25 reserved). The stage
  total adds the measured charges of the closed arrays: determinism about 2–3, and each closed part about 2.5. The
  meter's cap check enforces `verification_repair` 68.287 mechanically. Opening all three at once (69.25 reserved)
  would be refused, which is why they are sequenced.
- **Measured cost:** first-position seeds average 783 s, so about 7.5 billed node-h, within the 8–12 estimate.
- **Retry (once):**
  1. When all three arrays have left the scheduler, `s5p_recovery.py missing` lists the manifest seeds with no
     finished product.
  2. `tables --phase retry --seeds-file <that list>` builds one further array of those seeds. It writes to the same
     recovery directories and is submitted with `--timelimit-h 4.0`, so a seed that is slow in itself is not lost twice
     for the same reason. Its reservation is n × 0.5.
  3. A seed still without a product after the retry is **residual missing**.
  - There is no other retry.
- **Refusals:** a meter refusal (exit 3 cap, 4 concurrency) is waited out or reported, never forced. More hours need
  Joseph's decision.

## 5. Phase C: resolution (report only)

1. **`resolve`** (with `PYTHONPATH=nd-unfolding`, which its split-key check needs) `--design docs/orchestration/state/s5p/prod/design.json --manifest
   <tables>/rec-recovery-manifest.json --seed-states $NS/stage7/joint/seed-states.json [--residual <residual seeds>]
   --union-root $NS/recovery/union --out-design $NS/recovery/resolution-design.json`.
   - **Checks:** it refuses unless each lane's union equals its submitted seeds minus the declared residual (which must
     be lost seeds), no seed is both frozen and recovered, and the recovered set equals the manifest's minus the
     residual.
   - **Provenance:** each recovered product's `pseudo_seed` must equal its file's seed, and its `split_key` must
     equal `s5c_pseudo.split_key_for(seed)`. The following must match the lane's frozen products: the code and input
     sha256, schema, config, iterations, capacity, `estimator_params`, `development`, the detector and model bands, the
     refinement classifier parameters, and the hypothesis and alternative sha256.
   - **Atomicity:** it builds into `<union-root>.building` and renames only when every lane passes, so a failed run
     leaves no final union.
   - **Outputs:** the union directories (symlinks, partials excluded) and a `_report_only` design copy with union globs
     and counts.
2. **(a) Union, S recomputed:** from `D`, run the frozen `s5p_joint.py evaluate --design
   $NS/recovery/resolution-design.json --v $NS/stage3/V/V-s3v.npz --out $NS/recovery/resolved-evaluate.json`, then
   `s5p_robust_labels.py --evaluate $NS/recovery/resolved-evaluate.json --design $NS/recovery/resolution-design.json
   --out $NS/recovery/resolved-robust-labels.json`.
3. **(b) Frozen S:** `s5p_recovery.py frozen-s --design docs/orchestration/state/s5p/prod/design.json --evaluate
   $NS/stage7/joint/joint-evaluate.json --v $NS/stage3/V/V-s3v.npz --manifest <recovery manifest> --tables <prod
   tables> [--residual …] --out $NS/recovery/frozen-s.json`.
   - It first re-derives and checks the frozen nulls (§2.5).
   - It then counts, per claim and robustness variant, the recovered draws at or above the observed statistic, and the
     largest recovered T.
   - It gives the complete-set claim p and the Holm-with-determinacy decisions (claim and κ = 3).
   - For any residual missing draws it gives the worst (all exceed) and best (none exceed) corners. These exist only
     for (b); under (a), S itself depends on the residual draws' values.
   - It gives the ruled κ = 3 replace family with its labels, the keep-both family, and power against the frozen null
     ensembles over the complete power sets.
4. **Stopping:** `s5p_recovery.py stopping --design $NS/recovery/resolution-design.json --frozen-design
   docs/orchestration/state/s5p/prod/design.json --v … --tables <prod tables> --status-dir $NS/runs/prod/status --out
   $NS/recovery/stopping.json` (with `PYTHONPATH=nd-unfolding`). It re-applies the frozen sequential rule at each
   frozen look to the complete products of the batches before that look.
   - It reports each null's earliest look at which the complete-batch rule stops.
   - Where every null stops by its frozen final look, it gives the Holm-with-determinacy decisions at those earliest
     stops: primary and κ = 3 replace.
   - In the best case (no lost draw exceeds), `missing-sensitivity.json` already shows four nulls stopping one batch
     earlier (B ≈ 1200) than they did. (a) and (b) are evaluated at the frozen final batches; this step evaluates the
     complete-batch procedure where it would have stopped.
5. **Report, per test:**
   - k and B for the frozen evaluation, for (a) and for (b);
   - the recovered draws at or above the observed statistic;
   - the decisions under (a) and (b), and any residual corners;
   - per look, whether the frozen rule holds with the complete batches;
   - power under the complete power sets (from (a));
   - any difference between (a) and (b), reported as found.

   This is a resolution of the missing-seed sensitivity, labelled report-only. **The primary decisions remain those of
   the frozen evaluation.** "Can change" is resolved by observation only if all three of these hold, with no residual
   missing draw or with residual corners that change nothing:
   - (a) leaves every decision unchanged;
   - (b) leaves every decision unchanged;
   - the decisions at the earliest complete-batch stops (§5.4) are unchanged.

   Otherwise the outcome is reported as found.

## 6. Independent cross-check

The recompute lane computes T for the recovered products with its own code, which it agreed to do (2026-10-05). Its
agreement is required before the resolution is quoted.

## 7. Before any submission

- Independent re-review of this revision (the tool, the tests, the tables and this text), with its findings resolved
  and recorded.
- A Phase 0 PASS, including the §2.5 self-validation.

## 8. Review 1 findings and their resolution

| # | severity | finding | resolution |
|---|---|---|---|
| 1 | blocking | the bitwise check compared `meta`, which holds per-run fields; a stale file could pass without a rerun | criterion revised (§3): exact volatile fields removed, everything else must match; the rerun's job id must be a determinism task id and differ from the original's; same-file refused; tests for each direction |
| 2 | should-fix | "T unchanged" was false for the shifted variants (S uses F.mean) | text corrected (§1); report both (a) the union and (b) the frozen S (`frozen-s`, self-validating) |
| 3 | should-fix | no route for a seed lost twice | `--residual` in `resolve` and `frozen-s` (worst and best corners); a declared residual must be a lost seed |
| 4 | should-fix | no working retry classifier | `missing` plus `tables --phase retry --seeds-file`, at a 4 h limit |
| 5 | should-fix | Phase 0 did not verify the producer code or the unpinned inputs | §2.1–2.3: a whole-`nd-unfolding` diff against `4f5a613f` with only named exclusions (the hand-listed closure in the first draft of this revision missed imports), an unpinned-input mtime check, the seed-states sha, isolation checks; provenance checks in `resolve`; the unused `recovered` set is now enforced |
| 6 | should-fix | determinism skipped the power path | 6 power seeds added (16 tasks, 4.0 node-h) |
| 7 | should-fix | log directory never created | `mkdir -p` in §2.3 |
| 8 | should-fix | stopping not addressed | `stopping` subcommand (§5.4), self-validated against every frozen look (§2.5) |
| notes | — | part 3 reservation is 23.25; `s5p_robust_labels` needs `--design` | both corrected (§4, §5.2) |

## 9. Review 2 findings and their resolution

| # | severity | finding | resolution |
|---|---|---|---|
| 1 | blocking | `stopping` sorted a list of dicts and crashed on the real status files; no control exercised it | sort by B (and refuse two status files at the same B); 6 end-to-end controls (`test_s5p_recovery_world.py`) run the real controller and require every look reproduced |
| 2 | should-fix | frozen-s's self-check had little power (9 of 10 claim k = 0) and compared the process with itself | checks against `joint-evaluate.json` (§2.5): variant names in order, every variant's p, k, B, interval and null-T median and SD, the robust variants, T_obs, and power `claim_rule`; tampering controls |
| 3 | should-fix | `reproduces_frozen_look` ignored the overall stop, `min` and the thresholds | all three now compared; a wrong-minimum control |
| 4 | should-fix | the resolution criterion ignored stopping (the best case stops a batch earlier) | `stopping` gives the earliest complete-batch stop and the decisions there; the criterion requires them (§5.5) |
| 5 | should-fix | the "whole producer side" diff missed `2d-unfolding/unfold_2d_omnifold_unbinned.py` and `setup_salloc_env.sh` | added (§2.1) |
| 6 | should-fix | the mtime guard was weak (mtime preserved, symlinks skipped, a single-lane reference) | `find -L … \( -newer -o -cnewer \)` against the earliest B0 status (§2.2) |
| 7 | should-fix | the fixture put `refinement` under `experiment` | the fixture now has the real top-level layout with `estimator_params`; controls for both locations |
| notes | — | provenance fields; split key; residual validation; atomic resolve; the 51.5 wording; 586 rows; the manifest sha; PYTHONPATH; residual corners only for (b) | all applied (§1, §2.4, §4, §5) |

The power block of `frozen-s` is not exercised by the end-to-end controls, whose world has no power lanes. Its
guard is the §2.5 reproduction of `joint-evaluate.json`'s real power values before any recovered product is scored.
