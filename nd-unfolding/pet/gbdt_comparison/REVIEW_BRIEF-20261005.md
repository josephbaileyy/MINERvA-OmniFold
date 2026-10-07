# Review brief: PET finalists vs GBDT on existing outputs, plus the cost recommendation

**Reviewer:** one fresh, read-only, independent session working in a clean detached worktree of the commit under
review. Write nothing in the repository, start no compute, and contact no cluster. The budget is at most two focused
cycles: this brief, and then a narrow re-check of any repaired findings. **Do not review or reopen the closed PET
selection study** or its `NO_ELIGIBLE_DESIGN` outcome. Its numbers are inputs here, not subjects.

## What to read

1. `GOAL-20261005-pet-gbdt-existing-outputs.txt` and `HANDOFF-20261005-pet-gbdt-existing-outputs.md` (this
   directory). They define the scope and the prohibitions.
2. `PLAN-20261005.md`, the frozen plan, committed and pushed at `5f9c5a99` before any final-bank fit. Check the
   commit timestamp against the first entry in `results/cpu_ledger.jsonl`.
3. `REPORT-20261005.md` and its machine-readable sources:
   - `results/comparison.json`;
   - `results/gbdt_fb_compact.jsonl.gz`;
   - `results/dev_paired.json`;
   - `results/costs.json`;
   - `results/cpu_ledger*.jsonl`;
   - `results/controls/`.
4. The PET operands at `bc356b0c`:
   - `nd-unfolding/pet/final_design/results/final/scored_fb/`;
   - `results/dev3N/`;
   - `scalar/results/matched_task_rows-20260925.jsonl.gz`;
   - `resources/`;
   - `REPORT-20260926.md`.

## Checks

(a) **Independent reproduction of the consequential numbers.** Write your own minimal code; do not import
    `pgc_compare.py`. From the compact GBDT rows and the committed PET score files, recompute:
    - the E0 and E4 per-method means;
    - the paired differences of each finalist against GBDT at k = 7 (mean, sd, n, 95 % t interval);
    - the B2 D4d n-down values;
    - the E0 per-bin mean residual of one method.

    Report every discrepancy above 1e-9.

(b) **Pairing integrity.** For a sample of at least 10 tasks across stages and cases, confirm three things:
    - the GBDT row's `replicate_arrays_sha256` equals the digest in the committed PET score of the same run, for both
      finalists;
    - the GBDT injected per-bin vector equals PET's at k ∈ {3, 7, 10};
    - every task's PET run appears as COMPLETE in `freeze/COMPLETENESS-look1.tsv`, and no RB or S5 run appears
      anywhere.

(c) **Comparator fidelity.**
    - The recipe in `pgc_run_fb.RECIPE` must be the matched study's frozen `h1`, efficiency-corrected and
      `truth4_species`.
    - The primary k = 7 must equal the matched study's `kF0` for that variant (`SCALAR_AUSSIE_MATCHED-20260925.json`
      → `operating_points`).
    - `control_matched_repro.json` must show identical inputs and |ΔR| = 0.

    Say whether a stronger documented GBDT existed that should have been used instead, and whether the comparator is
    a "convenient weak" one.

(d) **Statistics and wording.** Check each of the following:
    - the unit is the draw;
    - the inference is stated as conditional on the banks;
    - no bins are treated as replicates;
    - the intervals are labelled exploratory and unadjusted;
    - no recovery ratio is used for a near-zero injection;
    - single-run results are not presented as six-member results;
    - residual spread against a moving target is not called estimator variance;
    - species counts are described as truncated-cloud counts;
    - CTL and C are described as old PET, not GBDT.

    Flag any sentence that ranks the two finalists, calls either "best", or claims uncertainty or coverage for the
    GBDT.

(e) **Budget compliance.** Sum `charge_core_hours` and `cpu_core_hours` over every ledger. Confirm:
    - the total is ≤ 8 core-h;
    - no more than 4 fitting threads ran at once (2 workers × 2 threads);
    - no tuning took place;
    - the stop rule was applied as declared;
    - the completed/incomplete case lists match the plan's order.

(f) **Cost model and recommendation.** Recompute `costs.json` by hand from `results/timing/*.fits.jsonl` and the
    stated row counts. Then judge the following:
    - whether every route in the report's cost table separates measured from estimated values, A100-hours from GPU
      node-hours, hardware time from queue time, and production from validation;
    - whether direct production carries its necessary validation;
    - whether the recommended action's resource request and stop conditions are concrete;
    - whether the recommendation follows from the evidence, or is a thousand-hour comparison or a no-validation
      shortcut in disguise.

    State any material disagreement and the decision it would change.

(g) **Scope and prohibitions.** Confirm the work makes none of the following changes:
    - to other workers' jobs, branches or checkouts;
    - to frozen rules or reserve-bank controls;
    - to the note, primer or paper;
    - a merge;
    - a collaborator message;
    - an adoption.

    Confirm also that the goal and handoff are preserved byte-identically
    (`cmp` with the copies at the repository root of the main checkout, if present).

## Output

Give a verdict line, then a findings table. Each finding gets a number, the operand as file:line at the reviewed sha,
its impact, and a suggested disposition. Then list what you could not verify. Quote numbers you recomputed with their
source.
