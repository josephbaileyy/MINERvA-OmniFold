# s5p confirmation review of the production admission (amendment 7 candidate)

**CITABLE FOR:** the independent confirmation review of the production admission candidate at `8ee54a45`,
verbatim. **NOT CITABLE FOR:** the frozen admission (amendment 7) or any result.

- reviewer: independent session with two sub-reviewers (costs/meter/queues; nuisance code), read-only worktree
  `../MINERvA-OmniFold-s5p-review4` detached at `8ee54a45`, left clean; scratch `/pscratch/sd/j/josephrb/s5p-20260926/review4/`
- verdict READY WITH REQUIRED CHANGES; the campaign's changes: the regenerated `state/s5p/prod-draft/` and the
  revised candidate (commit after this file), then the freeze with a mechanical re-check (tests; every generated
  submit through the meter's `validate_request`; the V checks)

## Report (verbatim)

**Verdict: READY WITH REQUIRED CHANGES.** The statistical core holds up under my own checks, and the round-2 repairs are implemented. But the queues as generated cannot launch, and three design or claim defects must be fixed before the freeze. The freeze commit needs a mechanical re-check (tests, the regenerated queues run through the meter's `validate_request`, and the V items at the end), not another review round.

I edited nothing and submitted nothing to Slurm. `git -C /Users/josephbailey/local-research/MINERvA-OmniFold-s5p-review4 status --porcelain` printed nothing (exit 0), HEAD is `8ee54a45`, and `runs/prod` does not exist. Two sub-reviewers covered costs/queues and the nuisance code; I re-read the meter lines behind their HIGH and MEDIUM findings myself.

**Confirmed (measured)**
- **Digests:** all five D16 files and all five prediction files match the design on the cluster. The M1 npz equals fine minus mid exactly, and the J integrals of the fine nulls equal G's to under 1e-14.
- **Loaders:** `j_matrix`, `Model`, `prediction`, `load_shift` (16×109 pairs per null) and the power specs all load. `calibration_count` correctly refuses while no final status exists.
- **Seeds:** the production ranges (1200000–1501099, 1853 lines) do not overlap any earlier table (the highest earlier seed is 970015) or the V pilot (965000–965199).
- **H1:** 34 bands (69 universes) are drawn in every experiment, GEANT is not double-counted, negative ratios are clipped per universe, and every random stream is keyed by the pseudo seed. The 23 pilot products each carry 34 model draws. `pytest` printed 71 passed.
- **M2 and M3:** D16 is half minus quarter, so the protective sign is correct. The shape test is protected about as well as the total test (my proxy: 0.036 vs 0.048 null SD). `holm_determined` and `power_determined` are correct.
- **M6 and the queue flow:** labels become job names `s5p-<label>`, which the wait line matches, and a failed `squeue` counts as "not yet". All 117 queue lines pass `bash -n` on bash 3.2 and 4.4, and the calibration line behaves as intended under stub exit codes.
- **Caps:** 188.147 − 185 leaves 3.1 node-h unallocated. The verification/repair reserve is 62.037, exactly 20%. Cumulative spend would be 35.086 + 307.037 = 342.12 ≤ 345.27. The 10% rule gives about 334.4 against the 310.184 pool (re-measured with iris today; the margin is about 24). Concurrency is 6 × 2 × 1/8 = 1.5 nodes (sacct bills 32 for 32 CPUs and 56 GB).
- **Timing:** a pilot experiment takes 417–1364 s (mean 615 s), and the worst six-seed line is 1.36 h against the 2.5 h limit.

**Findings**

| # | Sev | Finding and evidence |
|---|---|---|
| F1 | HIGH (fails closed, trivial fix) | Every production submit will be refused. The meter requires labels matching `[a-z0-9][a-z0-9_.]{0,40}` (`s5c_meter.py:434`, exit 2). The generator builds mixed-case labels (`s5p_production.py:104,128`), e.g. `s5p_cal_GENIE_2_12_10_MEC_b0`. The queue exits 2 and the runner stops. The `bash -n` test cannot see this. |
| F2 | MEDIUM | The budget stop is not terminal, and it is triggered by reservations rather than spend. `s5p_seqstop.py:68-73` never checks for an existing final status, so the line after a "budget" stop submits batch b+1. That skips seeds, overwrites the final status and breaks "fixed order". A batch reserves 34 × 2.5 × 1/8 = 10.6 node-h but costs about 5.0 (`s5c_meter.py:338,409`). Simulated (inferred): refusals start at about 130–147 node-h of real spend in the k=0 and worst cases, and after one at 158 in the expected case if lines run 15% slower. Also, "stage has no allocation" returns the same exit 3 (`:405`). |
| F3 | MEDIUM | The power lane has no fallback. `pow.q` has no controller, and one missing power product makes the evaluator exit (`s5p_joint.py:321-322`) with no joint result at all. P1g–P3g come last and are the most exposed. |
| F4 | MEDIUM (new) | Power is evaluated at the observed data's stopped B, which can make it zero by construction. The controller can stop at B = 200–600 (my scan of `sequential_decision`: p ≳ 0.95 at 200, p ≈ 0.1 or 0.9 at 400). Determinacy at 0.005 needs k=0 with B ≥ 737, so power at 0.005 is identically 0 for B ≤ 600, and the T6 target cannot be met. The sequential test run on alternative data would have continued to B=1200, so this understates the power exactly where non-rejections need it. |
| F5 | MEDIUM | M1 handling is not adequate for external-null rejections (details below). |
| F6 | LOW–MEDIUM | The non-rejection power sentence gives no power for the MEC, NuWro and GiBUU nulls. Their proxy non-centrality differs strongly from GENIE CV's (λ ≈ 154 / 2212 / 863 vs 216), so GENIE CV's power must not stand in for them. |
| F7 | LOW | "GiBUU: the 36 cells" is wrong. The domain `pz_index<=1` is 72 of 109 cells (measured). |
| F8 | LOW | Amendment 8 M4 froze 200 per GENIE CV power set; the candidate uses 100 without recording that it supersedes amendment 8. |
| F9 | LOW | The D wording. Per cell it is at noise level (0.022–0.075%, correct). Along the bias direction my proxy gives a/se = +4.7 at MnvTune and −3.4 at NuWro, so amendment 8's "consistent with zero" does not hold, though the effect is ≤ 0.05 null SD. |
| F10 | LOW | Stated numbers are off. Products are 184.9 kB, not 96 kB (about 1.2–2.0 GB total). The namespace is 4.4 GB, not 1.6. The wall clock is about 5.1 days expected and 6.8 worst, not 4–5. There are no cost lines for the V build, the independent re-computation or delivery work (round 2 L2 asked for delivery). |
| F11 | LOW | Three M6 repairs have no tests: the partial-file exclusion, the seed-keyed prediction-error draw, and the power size check (the e2e spec omits `n`). The band-sum test is weak (one scalar, 3 synthetic bands). The V digest is never enforced. A controller started before V exists crashes (fails closed). |
| F12 | Advisory | The combined 34-band weight has no cap. Row factors reach 112 (signal) and 987 (background), with Kish effective-size ratio 0.63–0.83; record the per-experiment maximum and effective size. Controller status files expose observed p-values during production, so any later repair is data-informed and should be declared so in advance. P3r at the GENIE CV null should be described as a "MEC-like (E_avail, W) shape". Round 2 has no L5 or L6; its LOW items are L1–L4 and L7, and all five are addressed. |

**Item 4: validity of the joint test (M1)**
- My proxy, using W built from the 22 pilot products available so far (Ledoit-Wolf) or a diagonal W, measures how far the null T moves between grid resolutions:
  - fine vs merged-x2 (M1): GENIE CV −0.12, MEC +0.42, NuWro ≈ 0, GiBUU +0.28 to +0.36 null SD;
  - coarse vs fine (F2): 0.23, 0.48, 1.08 and 0.49–0.62 null SD.
- In W-norm each grid halving shrinks the step only by a factor of 0.45–0.76. That leaves room for a residual below the fine grid of about 1–3 times the last step, up to roughly 1 SD for MEC. A 0.4–1 SD shift moves a 0.005 tail to about 0.013–0.03.
- So the J-level composite null ("the J cells equal G's") is not calibrated uniformly. What is calibrated is the simple hybrid null: G on the fine grid, MnvTune's shape below it.
- "Report its size with the result" gives no rule for borderline outcomes, which makes their reading data-informed. Amendment 8's own rule also asked for this comparison in null-T units, which has not been done yet.
- The MnvTune null is unaffected (rho = 1).

**Required before the freeze**
1. Lowercase the labels (the wait line follows automatically). Add a test that runs `validate_request` on every generated submit.
2. Make "budget" terminal in the controller, and refuse a "budget" stop at B=0. Either retry a cap refusal while the stage's own admissions are still open, or cut the limit to about 2 h. State in the worst-case text that the stop is reservation-driven. Test the force-stop path by executing it.
3. Power: make it independent of the stopped B. For example, require B ≥ 1200 before the MnvTune and GENIE CV nulls may stop (little expected cost if those p's are k=0), or evaluate power as the sequential procedure would behave.
4. Give power priority or run it first, and let the evaluator record an incomplete power set instead of aborting.
5. M1:
   - Restate H0 for external G as the simple fine-grid hybrid null actually calibrated.
   - Compute M1 in null-T units with the frozen V and commit it before the first look, as amendment 8 requires.
   - Pre-declare how it bears on the claims. Recommended: an M1 variant F ± κ·δ_M1 inside the claim rule, with κ declared. Minimum: a frozen "robust to the sub-fine residual" flag, otherwise "rejected conditional on the fine-grid null".
6. Fix the wording in F6–F10: 72 cells, the 100-vs-200 supersession of amendment 8 M4, the non-rejection power sentence per null, the D wording, and storage, wall-clock and cost lines.

Advisory: the missing tests (F11), a V digest check in the design, a recorded per-experiment weight maximum, and a pointer to the data-informed disclosure.

**Checks on V when it lands**
- Exactly 200 products (seeds 965000–965199), none partial, none refused, 34 model draws plus 3 GEANT draws in each.
- From build-v: the shrinkage (22-product proxy: 0.14), the median relative SD (proxy 8.9%), lateral symmetry, and positive-definiteness and condition number of W, including GiBUU's 72-cell domain.
- The sha256 of V and the design sha recorded in V's metadata.
- M1 and F4 in null-T units (compare with the proxy numbers above), and λ for each external null.
- Development power at 0.05 and 0.005 against T6. Note that it is evaluated against the same null draws that built V, so it is slightly optimistic.
- Reconcile the pilot's spend in the ledger, and re-measure the 10% cap at revision 5.

**Scratch files**
- Mine on the cluster, `/pscratch/sd/j/josephrb/s5p-20260926/review4/main/`: `r4_m1.py` and `r4_m1_out.json`, `pred.sha`, `st/` (one B=0 status file), `dummyV.npz`, and copies of the code and design.
- Sub-reviewers on the cluster, same `review4/` directory:
  - `cost/`: the meter measurement, timing, queue-flow scripts, and copies of the queues;
  - `code/`: `meta_check.py`, `extreme_weights.py` and `extreme_weights_out.json`.
- Local, `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/0f65cb75-7b8b-4df3-8592-8430238adac1/scratchpad/`:
  - `r4/`: my `r4_m1.py`, `r4_m1_out.json` and `pred.sha`;
  - `r4code/pytest.out`;
  - `r4_budget_sim.py` and `r4_budget_sim_out.txt`, `r4_alloc.txt`, `r4_timing.py`, `r4_qflow.sh`.