# s5p (`OI-193`) Stage 6: independent recomputation — final verification report (2026-10-05)

**CITABLE FOR:**
- that the independent recomputation (reviewed code `0142a228`) was run on production's terminal products;
- what it reproduced: 712 of 712 compared rows agree, with 0 discrepancies;
- the reviewed comparer's verdict and why: **INCOMPLETE**, which is not AGREE;
- the labelled diagnostics: A6, A7-VS, A8, the sequential verdicts, the seed disposition, the missing-experiment
  bounds, and an unreviewed comparison of the fields the comparer leaves unmapped;
- the agreement of the two independent missing-sensitivity implementations.

**UPDATE 2026-10-05 (§8): the reviewed comparer mapping extension returns AGREE** (1379/1379, 0 discrepancies,
0 not located, 0 unresolved) on the unchanged production outputs. §1–§7 are the first run, kept as they were.

**NOT CITABLE FOR:**
- a verification verdict from the FIRST run: it returned INCOMPLETE. The AGREE is §8's;
- the scientific adequacy of the calibration (the nuisance model, the pseudo-experiment process);
- ignorable missingness;
- any adoption, grade or publication claim.

Agreement verifies the calculation from the products, not the calibration.

Lane: `s5p-parallel-recompute-20260928`. Procedure: `HANDOFF-20260928-s5p-recompute.md` §5.1–§5.4, §5.8. Outputs:
`docs/orchestration/state/s5p/recompute/final/` (byte-identical copies of
`/pscratch/sd/j/josephrb/s5p-parallel-recompute/final/`).

## 1. Terminal state, re-measured by this lane (§5.1, 2026-10-05T20:38Z)

The committed §5.1 block was run as written. Every condition holds:
- 5/5 final statuses;
- the pow runner logged `queue done` (r3 log, 2026-10-04T15:42:06Z), with no refusal or stop line;
- `squeue` rc 0 with 0 s5p cal/pow jobs;
- the meter (deploy `e0d7b04a`) rc 0, budget sha256 `be29f2c3009e` = the ledger's, open concurrency cpu 0.0 / gpu 0.0;
- no `s5c_queue.sh` process on login33;
- production's `evaluate` log ended with "sensitivity status: COMPLETE" before any comparison was made.

Production's outputs, whose sha256 equal the campaign's packet:

| file | sha256 |
|---|---|
| `joint-evaluate.json` | `b9604502b1aa263508ba46f0be91846d7a2106f6f2fd0ba5c172b87ee256dd11` |
| `robust-labels.json` | `206655f906bdffac636676f39ed86267f31eb9600ed9d45a335905fdaf7fde2a` |
| `seed-states.json` | `6823e701064b5dfc1286015be88b6d660e8f64099dc5bf3bff99b783724e58a8` |
| `missing-sensitivity.json` | `f48e16ef351ea78c59b7e75f5bf653dc5742857457786e3d8fd1a067be8e2293` |

Production's evaluation deploy `e9372b75` is on origin/main. Its frozen modules equal `4f5a613f`, its design is
identical, and no top-level `nd-unfolding` `.py`/`.sh` changed since the production deploy `756e1d6c`.

## 2. Deploy and run (§5.2, §5.3)

- The §5.2 guard passed: the tip's `nd-unfolding/` equals `0142a228`.
- Deployed digests: `s5p_recompute.py` `05664adb…`, `s5p_recompute_compare.py` `2cef9688…`, design `404446eb…`,
  `s5p_recompute_seed_disposition.py` `bdc19179…`, `s5p_recompute_missingness_bounds.py` `d5fdb27c…` (see §6).
- §5.3 ran detached on login31. Its log is cluster-only, because `*.log` is gitignored:
  `/pscratch/sd/j/josephrb/s5p-parallel-recompute/final-run-s53.log`, sha256 `e93e7a0034e089f5…`.

| step | rc |
|---|---|
| evaluate | 0 |
| compare | **2 (INCOMPLETE)** |
| tables diff | 0 |
| sacct | 0 |
| disposition | 0 |
| bounds | 3 (INCOMPLETE; a defect in the bounds script, §6) |

- After the fix, bounds gave rc 0.

## 3. The reviewed comparison: INCOMPLETE — 712/712 rows agree, 0 discrepancies

`compare.json` (sha256 `4cd73439…`).
- **Every compared row agrees:** 712 of 712, covering every claim and variant p, k and B, the statistics, the
  decisions with thresholds and intervals, the κ = 3 members, the ruled labels, power, and provenance.
- **The verdict is INCOMPLETE, because the comparer fails closed on two mapping gaps:**
  - **20 required items not located.** These are layout differences from the schema the campaign stated:
    - `joint-evaluate.json:holm_point` is a per-test `{p_raw, p_holm, reject}` (a classical Holm-adjusted p), where
      a decision label was expected (10 items);
    - `robust-labels.json:diagnostics.keep_both.family` is one description string, where per-test member names
      were expected (10 items).
  - **713 production leaves unresolved.** These are fields that no comparer row maps:
    - per-variant `B`, `tail_interval`, `level` and the null-T medians and SDs;
    - the process-shift `a`, `se`, `magnitude`, `bias_norm_W`, `n_pairs`;
    - the power `n`, `alpha`, `B`, `rule`;
    - the MnvTune claim `rule` fields.
- **This was not relaxed.** Making it AGREE needs a comparer mapping extension. That is a code change, and the
  handoff requires a bounded independent review before it is used. Whether to do that is the owner's decision.

**Unreviewed diagnostic of the unmapped fields** (`s5p_recompute_unmapped_diagnostic.py`, output
`unmapped-diagnostic.json`; NOT a verdict). Every field the recompute independently supplies agrees:

| field | agree |
|---|---|
| `holm_point` p_raw / p_holm (classical Holm) / reject | 10 / 10 / 10 |
| per-variant B / CP95 interval / level | 62 / 62 / 62 |
| claim CP95 intervals | 20 |
| shift `a`, `se`, `magnitude`, `bias_norm_W`, `n_pairs` | 5 each |
| power `n` / `B` / `alpha` / set n, declared, incomplete | 72 / 24 / 48 / 6, 6, 6 |
| c = 0 null-T median | 10 |

One field differs by convention only: the **c = 0 null-T SD** (10 of 10). Production reports the population SD
(ddof 0) and the recompute the sample SD (ddof 1); after the factor √((B−1)/B) the residual is ≤ 5.1e-15 relative.
It is descriptive and enters no p-value or decision. The per-variant null-T medians of the shifted variants are not
compared, because the recompute does not output them.

## 4. Decisions recomputed (reproduced by production in every compared row)

| test | k | B | claim p | Holm step | threshold | 95% CP | decision |
|---|---:|---:|---:|---:|---:|---|---|
| NuWro_21_09:total | 0 | 1751 | 0.000571 | 0 | 0.00500 | [0, 0.00210] | rejected |
| GENIE_2_12_10_CV:total | 0 | 1366 | 0.000732 | 1 | 0.00556 | [0, 0.00270] | rejected |
| GENIE_2_12_10_CV:shape | 0 | 1366 | 0.000732 | 2 | 0.00625 | [0, 0.00270] | rejected |
| MnvTune_v1:total | 0 | 1365 | 0.000732 | 3 | 0.00714 | [0, 0.00270] | rejected |
| MnvTune_v1:shape | 0 | 1365 | 0.000732 | 4 | 0.00833 | [0, 0.00270] | rejected |
| GiBUU_2019:total | 0 | 1351 | 0.000740 | 5 | 0.01000 | [0, 0.00273] | rejected |
| GiBUU_2019:shape | 0 | 1351 | 0.000740 | 6 | 0.01250 | [0, 0.00273] | rejected |
| GENIE_2_12_10_MEC:total | 0 | 1343 | 0.000744 | 7 | 0.01667 | [0, 0.00274] | rejected |
| GENIE_2_12_10_MEC:shape | 0 | 1343 | 0.000744 | 8 | 0.02500 | [0, 0.00274] | rejected |
| NuWro_21_09:shape | 1 | 1751 | 0.001142 | 9 | 0.05000 | [≈0, 0.00318] | rejected |

- **R1 BOUND, as predicted (fail-safe):** MnvTune's `total_robust` and `shape_robust` records carry `tail_interval`,
  `level` and `rule` beyond `p`, `k` and `B`, so they are among the unresolved leaves (INCOMPLETE, not a pass).
- **R6 did not bind:** the variant names are exactly `0.0, 0.5, 1.0, m1±2` (MnvTune: the three c-names), with no
  duplicates.
- **R8:** the recompute's threshold and interval for each decision are in the table above.

- **A7 / A7-VS (ruled):** all ten ruled κ = 3 labels are "robust to the sub-fine residual".
  `tests_where_the_sets_differ` is empty, the keep-both labels are identical, and the frozen boolean equivalent is
  true for all ten.
- **A6:** `decisions_changed_by_product_reading` is empty.
- **Implied size:** no test is flagged "not calibrated for the data process".
- **Sequential rule, all five nulls:** `stop_verdict` is "consistent" under the primary and every A8 reading, and no
  A8 reading differs at any look. Each null's rule first stops exactly at its final B (1365, 1366, 1343, 1751, 1351)
  with reason "rule met for both tests". Every look pairs with its status file, the final look is the final B, there
  is no batch without products, and no status file lacks a look.
- **Calibration:** for each null the count equals the final B, with no partials, no seed outside the submitted
  batches, and no count mismatch.
- **NuWro throttle (r4–r6), from the ledger:** b6 `%8`; b7 and b8 `%14`, each with its frozen table.
- **Power** (determined claim at 0.005, total / shape), conditional on the retained null ensembles:

| set | n present / declared | total | shape |
|---|---|---:|---:|
| P1 | 193/200 | 1.000 | 1.000 |
| P2 | 195/200 | 1.000 | 1.000 |
| P3 | 195/200 | 0.862 | 0.231 |
| P1g | 199/200 | 1.000 | 0.739 |
| P2g | 193/200 | 0.088 | 0.021 |
| P3g | 172/200 | 0.000 | 0.000 |

## 5. Missing seeds and missing-experiment sensitivity

**Seed disposition** (`seed-disposition.json`, `eb780ffa…`), against the submission records: tables, ledger, logs,
`sacct`.
- Calibration: **224 lost**, all submitted (111 interrupted, 113 never started). 0 not submitted, 0 not established.
  `recompute_missing_seeds_equal` is true for every null.
- Power: 53 lost (26 interrupted, 27 never started).
- The FAILED-129 task `59321575_0` lost no seed (§5.7 note).

**Bounds** (`missingness-bounds.json`, `2e609c44…`, status complete). L is the count of missing experiments per
null:

| population | MnvTune | CV | MEC | NuWro | GiBUU |
|---|---:|---:|---:|---:|---:|
| (a) interrupted | 22 | 17 | 25 | 27 | 20 |
| (b) all lost | 35 | 34 | 57 | 49 | 49 |

- **Neither certificate form holds in either population.** Each null has k ≤ 1, so L draws exceeding T_obs move the
  worst p to 0.013–0.019 under (a) and 0.025–0.041 under (b), far above α/m = 0.005.
- **The all-worst corner is a realizable assignment, and in it every one of the ten decisions becomes "not
  rejected"** in both populations. In the all-best corner, all ten stay rejected.
- Read: the rejections hold on the retained products, but **they are not robust to an adversarial assignment of the
  lost experiments**. Whether the missingness is ignorable is not established by these records. The campaign's
  lost-seed diagnostic gives supporting evidence only. **This is routed to the owner.**

**Agreement with the campaign's independent implementation** (`missing-sensitivity.json`, `f48e16ef…`;
`d0cca826`), on every quantity the agreed mapping compares, with 0 differences:

| quantity | agree |
|---|---|
| L per null, both populations | 5 + 5 |
| exact missing-seed sets by class | 11 + 11 |
| completed = products | 11 |
| simple certificate | 2 |
| corner claims k / B / p (three corners × 10 tests) | 90 |
| corner survival | 30 |
| power values (power, missing, lower, upper) | 288 |
| status | 1 |

As agreed, this lane's step-aware certificate and the campaign's κ = 3 certificate are not compared; both are "not
certified" here anyway.

## 6. A defect in this lane's report-side bounds script, found at the terminal run and fixed

- `s5p_recompute_missingness_bounds.py` at `d5fdb27c…` read the null order from `recompute.json`. That file is
  written with sorted keys, so the order was alphabetical. Two consequences:
  - a false identity failure (INCOMPLETE);
  - the corner runs used the wrong Holm tie order (A10), which matters with k = 0 ties.
- Its tests used the in-memory record and so never met the hazard. The certificate is order-free and was unaffected.
- Fixed at sha256 `5a3beaf3…`: the order is read from `family.decisions`, and identity checks the family order.
  Two regression tests use the on-disk JSON and the tie order, and **both fail on `d5fdb27c`**. Tests: 11.
- The first output is kept as `missingness-bounds-d5fdb27c-WITHDRAWN.json` (`3d4d719a…`). It is not cited.
- The fix is report-side and outside the reviewed code (`nd-unfolding/` = `0142a228`). It had no independent review.

## 7. What remains open

1. **The reviewed verdict is INCOMPLETE, not AGREE.** A bounded comparer extension for the two layout gaps and the
   unmapped fields, with its own independent review, is what could turn it into AGREE. That needs an owner decision.
2. **The missing-experiment sensitivity is not certified:** in the all-worst corner every rejection changes. This
   is routed to the owner.
3. **CLOSED 2026-10-05:** the committed copies on origin/main (`0afd9ef5`,
   `docs/orchestration/state/s5p/stage7/joint/`) are byte-identical to the cluster files: `joint-evaluate.json`
   `b9604502…`, `robust-labels.json` `206655f9…`, `missing-sensitivity.json` `f48e16ef…`.

The campaign has put decisions (1) and (2) to the owner (campaign-state at `9f257847`). It frames (1) as whether
INCOMPLETE with 0 discrepancies satisfies amendment 7 (v). No joint result is recorded.

## 8. Comparer mapping extension: reviewed, rerun, AGREE (2026-10-05)

*Authority.* Owner decision 1, "Extend, review, then record", and §4 (A16 ruled report-only; new output fields
allowed): `DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md` (origin/main `d2fe7525`,
`18af90c3`). Both were read from origin/main by this lane before acting.

*The change* (`02df81e6`):
- the evaluator gains OUTPUT fields only;
- the comparer maps production's layout as observed in its outputs;
- A16 (the descriptive null-T SD and `median_shift_in_null_sd`) is compared against the ruled reading, and the
  recompute's own reading is reported outside the verdict;
- only rule-description texts and the two family-definition strings are excluded, by anchored pattern.

*Independent review.* `REVIEW-20261005-s5p-recompute-comparer-extension.md`, verbatim: a fresh read-only agent in an
isolated worktree, left clean. **APPROVE** (nothing at MEDIUM or above).
- It confirmed every existing output byte-identical to `0142a228`, on the real terminal record and on toy worlds.
- It confirmed the A16 ruled reading in the verdict, with the own reading outside it.
- It confirmed the mapping, by exact CP and Holm restatements and 13 direct spot checks.
- It confirmed the exclusions are text only, and the layout signature regenerated from the real files.
- It re-ran the real comparison.

The reviewer's full pytest run did not finish under machine load (30 passed, no failure seen). This lane's own run of
the same code gave 84 passed (73 recompute + 11 bounds) before the commit.

*Review findings, disposition.* Not changed, because a change would void the review; each is acted on only with its
own review round:
- **LOW 1** (the new test class sits after `unittest.main()`, so it runs only under pytest, the documented runner): a
  move above the `__main__` block is owed.
- **LOW 2** (the fixture has k = 0 throughout, so a per-variant/claim or keep-both/replace swap would pass the tests):
  the swap is excluded on the real data by production's own rule text and by member-wise variant comparison; a k > 0
  fixture is owed.
- **LOW 3** (`diagnostics.keep_both.family` is checked for existence only): its text, read directly, is *"claim
  variants union F +- kappa_robust delta_M1 (the frozen decisions_robust_kappa)"*. That is the recompute's keep-both
  (retain) definition. Its members are compared member by member in `variants` and `robustness_variants`.
- **LOW 4** (latent null-level rows on the non-ruled reading): they fire on 0 rows here.
- **NOTEs 1–3:** recorded.

*The verification run* (`final-ext/`). The reviewed code was deployed by the §5.2 guard at `02df81e6`: recompute
`81b879ae…`, comparer `bc924f31…`, design `404446eb…`, contract `d54fd7c9…`. It ran after re-checking that production's
outputs are unchanged (`b9604502…`, `206655f9…`), with 5/5 finals and no s5p job.

| step | result |
|---|---|
| `evaluate --require-terminal` | rc 0; `recompute.json` sha256 `550a95fcd9b98452…` |
| `compare` | **AGREE (rc 0): 1379/1379 rows agree, 0 discrepancies, 0 required items not located, 0 unresolved production leaves**; `compare.json` sha256 `97e1666a7e5722b0…` |

- 61 paths excluded: the schema, rule texts, lateral-symmetry metadata, and the two family strings.
- A16 own-reading rows: 82, 4 agree; reported, outside the verdict.
- Decisions: all ten rejected, and all ten ruled labels "robust to the sub-fine residual", as in §4.
- Outputs: `state/s5p/recompute/final-ext/` (byte-identical to the cluster).

**Verdict: the independent recomputation AGREES with production's joint evaluation on every compared quantity.** This
verifies the calculation from the products. It does not establish the calibration's scientific adequacy or ignorable
missingness: §5's missing-experiment sensitivity still stands, pending the owner's lost-seed recovery (decision 2).
