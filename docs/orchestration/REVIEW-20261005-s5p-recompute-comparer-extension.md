# s5p Stage-6 recompute lane: independent read-only review of the comparer mapping extension (2026-10-05)

**CITABLE FOR:** the independent reviewer's findings on `git diff 80edc4d6 02df81e6 -- nd-unfolding/` (the comparer
mapping extension and the evaluator's added output fields), quoted verbatim below. **NOT CITABLE FOR:** any repair
(the dispositions are in `REPORT-20261005-s5p-recompute-final-verification.md` §8); the verification verdict itself
(§8 of that report); any p-value or decision.

- Required by the owner's decision 1, "Extend, review, then record"
  (`DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md`, origin/main `d2fe7525`, §4 at `18af90c3`).
- Reviewer: a fresh independent agent with no authorship of the reviewed code, briefed only from the records.
- Worktree: the read-only detached worktree `../MINERvA-OmniFold-s5p-recompute-review-ext` at `02df81e6`, left clean
  (`git status --short --ignored` empty).
- The reviewer did not read the production evaluator bodies.
- Its first turn stopped on a usage limit and was resumed with its context; the report is from the resumed turn.
- The development run it was told to treat as the author's claim is `scratch ext-dev/` (AGREE 1379/1379). The
  reviewer re-ran it and found identical rows.

## Report (verbatim)

# Independent review of the s5p recompute comparer mapping extension (commit `02df81e6`)

**Verdict: APPROVE.** I found nothing at MEDIUM or above in `git diff 80edc4d6 02df81e6 -- nd-unfolding/`. There are 4 LOW findings and 3 NOTEs. One caveat: the full test suite did not finish under the machine's load, so I have no runner summary line (see Q5 and the "not checked" list).

**Commit reviewed:** `02df81e6`, worktree `/Users/josephbailey/local-research/MINERvA-OmniFold-s5p-recompute-review-ext`, against `80edc4d6` (whose `nd-unfolding/` equals `0142a228`).

**Rules followed:** I opened no code bodies of `s5p_joint.py`, `s5p_inference.py` or `s5p_seqstop.py`, and used no ssh. Every command ran with `PYTHONDONTWRITEBYTECODE=1`, and pytest also with `-p no:cacheprovider`. Scratch files went only under `scratchpad/review-ext/`.

## Q1. Are the existing outputs byte-identical?

**Answer: YES.** No existing value changed, and no existing computation changed.

**New keys, taken from the diff:**
- **`claim()` (`s5p_recompute.py:570,574`):** each variant gains `B`, `interval` and `level`; the claim gains `level`. This also applies to `unshifted`, which is the same dict object as `variants["c=0"]`, and to both κ = 3 robust claims.
- **Per test:** `implied_size_detail` (`:732`), `null_T_by_variant` (`:751`) and `median_shift_in_null_sd_A16_ruled` (`:755`).
- **Top level:** `family.holm_point_classical` (`:855`), `power_levels` (`:858`) and `ambiguities.A16_descriptive_null_T_summaries`.

**Real data** (`structdiff.py`, then `strip.py`, comparing `recompute.json` from `0142a228` with `recompute-dev.json`):
- No key was removed.
- Exactly one existing value changed: `inputs/code_sha256`, from `05664adb…` to `81b879ae…`. The new value equals `sha256(nd-unfolding/s5p_recompute.py)` at `02df81e6`, so the development run did come from the reviewed code.
- The added key patterns are exactly the list above, e.g. `46 nulls/<N>/tests/<t>/variants/<v>/{B,interval,level}`.
- After stripping only those keys and restoring `code_sha256`, re-serialising (`indent=1, sort_keys=True`) gives a file **byte-identical** to the old `recompute.json` (361402 = 361402 bytes).

**Toy worlds** (`toyrun.py`, running the `0142a228` and `02df81e6` modules on identical toy worlds):
- "gaps" world: MnvTune B = 397 with k = 373, GiBUU B = 120, and power set P1.
- "plain" world.
- The only differing values were the world-root path strings. After normalising those, both worlds are byte-identical once the new keys are stripped (55946 and 48642 bytes).

**No existing computation changed.** The diff only adds lines. The new code calls `np.median` and `.std` on arrays it does not modify, and computes `mc_p_vec` a second time; none of this has side effects.

## Q2. Does the comparer follow the A16 ruling?

**Answer: YES.**

**Which readings enter the verdict:**
- Per-variant `null_T_<t>_sd` is compared with `null_T_by_variant[v].sd_ddof0` (`s5p_recompute_compare.py:340-343`).
- `median_shift_in_null_sd/<t>` is compared with `median_shift_in_null_sd_A16_ruled` (`:346-349`).

**The recompute's own reading is kept, labelled, and outside the verdict:**
- It goes to `Ledger.diag` (`:199-205`, `:345`, `:350`) and is reported as `a16_recompute_own_reading_rows`, with the note "never part of the verdict".
- `compare()` builds the verdict from `L.rows` only (`:663`, `:673-674`).
- The own reading stays in the output unchanged: `median_shift_in_null_sd` (`:747`) and `null_T_summary.sd` with ddof 1 (`:759`). `null_T_by_variant` carries both `sd_ddof1` and `sd_ddof0`.

**The definitions hold on the real record** (`defs.py`):
- `sd_ddof0` equals `sd_ddof1·√((B−1)/B)` to within 2.1e-16 relative (46 values).
- The ruled shift equals `(median_v − median_c0)/sd_ddof0(c=0)` with deviation 0 (36 values).
- `null_T_by_variant[c=0]` equals `null_T_summary`.

**A16 rows on the real data:**
- 82 own-reading rows, 4 of which agree. The 4 are NuWro's c = 0.5 and c = 1 median shifts, where both sides are 0.0.
- The SD rows differ by 2.9e-4 to 3.7e-4 relative, which is the √(B/(B−1)) factor.
- The median-shift rows differ by up to 0.41 relative.
- All 82 verdict rows on the same paths agree.

**No other reading was changed to match production.** The evaluator diff only adds output, and every pre-existing comparer row is unchanged: all 712 old rows are present with the same `mine` and `kind`. Finding 4 is a latent, pre-existing exception that never fires on this data.

## Q3. Is the mapping correct and complete?

**Answer: YES.** I checked each mapping against production's output (`joint-evaluate.json`) and the recompute record. Every one reads the right recompute quantity, with the right kind and tolerance, in the right direction.

**`holm_point` (`:476-481`):**
- `p_raw` is compared with the claim p.
- `p_holm` is compared with `(m−step)·p`, running max, capped at 1, in family order (`:850-854`).
- `reject` is compared with the existing `holm_point` decision.
- Three independent checks agree:
  - my own restatement gives a 0.0 difference over 10 tests;
  - `reject` equals `p_holm ≤ α` in all 10 tests;
  - by hand, `10·0.000570776 = 0.0057078` and `9·0.000731529 = 0.0065838`, and the later tests take the running max. This matches production.
- Tie order cannot change the result: tied p values get the same adjusted p.

**Per-variant and claim-level `B`, `tail_interval` and `level` (`:333-335`, `:419-420`):** these are compared with the per-variant CP interval of (k, B). I checked against my own `scipy.beta` Clopper–Pearson interval: 142 intervals, deviation 0.

**`_robust` (`:448-459`):**
- It is compared with the keep-both claim, which matches production's own rule text ("the claim p with the kappa_robust M1 variants added").
- For MnvTune, which has no M1 variants, it is compared with the claim itself.
- The skip list excludes only recompute-only keys.

**`shift` (`:412`):** this uses `same_names`, so only keys present on both sides are compared. Any extra production key stays unresolved, so the check fails closed.

**Implied size (`:352-356`, `:728-733`):**
- `n` is compared with `base.size`, which is B; production gives 1366 for CV.
- The interval is `cp_interval(count, n)`; the deviation from my own CP interval is ≤ 2.2e-16 over 36 values.
- `power` equals `count/n` exactly.

**Power (`:527-530`):** `n` is compared with `n_present`, `B` with `B_null` (production: 1366 for P2g, which is CV's B), and `power/levels` with `POWER_LEVELS`.

**Could the mapping produce AGREE while comparing the wrong things?**
- No row compares a production value with itself.
- Some rows compare a constant with a constant (NOTE 1).
- The extended comparer on the old `0142a228` record gives DISCREPANT, with 453 disagreements, all on the new fields (`B`/`tail_interval`/`level` 62 each, null-T 46 + 46, A16 shift 36, implied-size 36 × 3, holm 10 × 3). So these rows really do read the new recompute fields.

## Q4. Exclusions and requirements

**The new `EXCLUDED_SCOPE` patterns (`:98-102`, `:109-110`)** are anchored with exact length and apply to scalars only (`excluded()`, `:259-266`). On the real data they exclude only text:
- 44 rule texts: "the largest p over the declared shift variants", "the claim p with the kappa_robust M1 variants added (report only)" and "claim rule with determinacy";
- 2 family strings.

Nothing computed is excluded. An exclusion also cannot hide a leaf that a row consumes (mutant M14 is equivalent). Excluding a computed leaf *and* dropping its row does make the test fail (M14b).

**Was any required item dropped or weakened?**
- All 712 old rows are still present and unchanged, and the old 20 not-located items are now resolved.
- `holm_point` got stronger: 3 required fields per test instead of 1 label.
- `diagnostics.keep_both.family` got weaker. In the string layout it is only required to exist and be non-empty (`:636-640`); the 10 per-test name comparisons are gone. How the keep-both family is still verified is in Finding 3.
- The `rob` fallback change (`:448`) compares the same p/k/B values as before.

## Q5. Tests

**The new tests run green on unchanged code.** I ran `CompareObservedLayout` through a harness that runs the class's own test methods, with the fixture record built once by its real `setUpClass` at `02df81e6` (`mutharness.py`, `obs_mine.json`): 6 run, 0 failed.

**They fail on the old comparer:** with the `80edc4d6` comparer, the mutation tests fail.

**They fire on most injected defects.** Mutants that are caught:
- M01 (SD with ddof 1)
- M02 (shift in the own reading)
- M03 (A16 rows inside the verdict)
- M04 (A16 rows dropped)
- M05 (`p_holm` compared with `p_raw`)
- M06 (`reject` not mapped)
- M07 (missing keep-both family accepted)
- M08 (power α a constant)
- M09 (power B taken from n)
- M12 (null-T median of c = 0 for every variant)
- M13 (wrong variant's implied size)
- M14b (computed leaf excluded and its row dropped)
- M15 (`shift` not mapped)
- M16 (`power/levels` not mapped)
- Record mutants: Holm without the running max, `sd_ddof0` set to ddof 1, and the ruled shift set to the own reading.

**Two mutants survive:**
- M10: `_robust` compared with the replace family instead of keep-both.
- M11: per-variant `B`/`interval`/`level` compared with the claim's.

Both survive because every value of k in the fixture is 0 (Finding 2).

**The layout-signature test is a real constraint.** I regenerated the signature from the real files with the test's own `_norm_path`/`_signature` functions (`sig.py`): 153 and 31 paths, identical to `tests/data/s5p_production_layout_signature.json`, whose source digests are `b9604502…` and `206655f9…`. It constrains only the *set* of normalised key paths, not values and not which nulls have which keys.

**The fixture is derived from the code under test.** `observed()` builds "production" from `self.mine`, so its AGREE only shows that the comparer reads the paths the fixture writes. The real-data run is what adds evidence that production's values agree, and that every leaf is accounted for in each instance, not just in the union of paths.

**Full suite:** `python3 -m pytest -q -p no:cacheprovider nd-unfolding/tests/test_s5p_recompute.py` (with TMPDIR in scratch) did not finish. The machine load average was 270–370 on 10 cores. After 2 h 06 min it had printed 30 passing dots and no failures; I stopped it (rc 143), so there is no runner summary line. A static count gives 73 tests: the 67 recorded at `0142a228` plus these 6.

## Q6. My re-run of the comparison on the real files

**Command:** `s5p_recompute.py compare --mine recompute-dev.json --production joint-evaluate.json --robust-labels robust-labels.json` printed `AGREE: 1379/1379 rows agree; 0 discrepancies; 0 unresolved leaves; 0 required items not located` (rc 0). My rows are identical to the author's `compare-dev.json`.

**Rows:** 712 old plus 667 new. The new ones break down as:
- holm 30;
- variant B/tail_interval/level 46 × 3;
- robustness variants 16 × 3;
- claim and `_robust` tail_interval/level 10 × 4;
- null-T median/SD 23 × 4;
- A16 shift 36;
- implied-size n/interval/alpha 36 × 3;
- shift 6 × 5;
- power n 72, alpha 48, B 24, levels 1.

**Excluded (61 paths):**
- in `joint-evaluate.json`: `schema`; `tests/<null>/{total,shape,total_robust,shape_robust}/rule` (20); `power/<set>/<t>/<lvl>/claim_rule_determined/rule` (24); `lateral_symmetry/<band>/*` (10);
- in `robust-labels.json`: `schema`, `ruling`, `evaluate`, `code_sha256`, `kappa3_family`, `diagnostics/keep_both/family`.

**A16 own-reading rows:** 82, of which 4 agree (see Q2).

**Spot checks, reading both files directly** (all agree within tolerance):

| Item | Recompute | Production |
|---|---|---|
| NuWro shape claim k | 1 | 1 |
| NuWro shape claim tail_interval | [1.44590e-05, 0.0031778] | same |
| NuWro shape keep-both p | 0.0017123 | 0.0017123 |
| MnvTune total_robust p (equals its claim) | 0.00073206 | 0.00073206 |
| CV m1−2 shape SD | 92.491976082495 (ddof 0) | 92.491976082495 |
| CV c=0.5 total null-T median | 528.85595034733 | same |
| MEC m1+2 total shift (A16 ruled) | 1.72225843633707 | 1.72225843633718 |
| GiBUU m1−2 shape implied size n / interval / alpha | 1351 / [0.0181098, 0.0358471] / 0.05 | same |
| GiBUU robustness m1−3 total k / B / interval | 0 / 1351 / [0, 0.00272676] | same |
| NuWro shift a / se / … | a −0.0715008948600 | relative difference 3.5e-15 |
| holm NuWro shape p_raw / p_holm / reject | 0.00114155 / 0.00658376 / true | same |
| P2g shape 0.005 determined n / B / power | 193 / 1366 / 0.0207254 | same |
| power levels | [0.05, 0.005] | [0.05, 0.005] |

The own-reading CV SD (ddof 1) is 92.5258497, which correctly differs from production.

## Findings

**1. LOW: the new test class runs only under pytest.**
- **Location:** `tests/test_s5p_recompute.py:1214`. `CompareObservedLayout` is defined after `if __name__ == "__main__": unittest.main()` (`:1174-1175`).
- **Failure scenario:** running `python3 nd-unfolding/tests/test_s5p_recompute.py` executes the 67 earlier tests and exits 0 without ever defining the 6 new ones. A green run that way says nothing about the extension.
- **Mitigation:** the documented runner is pytest, which collects all 73. The fix is to move the class above the `__main__` block.

**2. LOW: the fixture cannot distinguish per-variant from claim values, or keep-both from replace.**
- **Evidence:** every k in the fixture is 0, for every variant and both robust families. Mutants M10 and M11 pass all the new tests.
- **Real data:**
  - M11 (variant interval/B/level compared with the claim's) is caught by only one row, `NuWro_21_09:shape:robustness_variants[m1=+3]:tail_interval`.
  - M10 (`_robust` compared with the replace family) gives AGREE 1379/1379 here as well.
- **Why this is not a defect:** the keep-both choice is correct by production's own rule text and predates the extension. No test and no real row could catch a swap, though.
- **Suggestion:** use a fixture with k > 0 that differs across variants and families.

**3. LOW: the keep-both family is now checked only for existence, and the exclusion reason overstates what is compared.**
- **Location:** `:86-87` and `:636-640`.
- **What changed:** the 10 per-test name comparisons from before are gone. The reason text says the family "is compared through family_members, diagnostics.keep_both.labels, decisions_robust_kappa". But `family_members` is the *replace* family, and labels and decisions compare outcomes, which here cannot tell the two families apart (Finding 2). The docstring's "no required item is dropped" (`:50`) does not hold for this content check.
- **What still verifies it:**
  - the family's parts are compared member by member (`variants`, `robustness_variants`);
  - I read the string itself: "claim variants union F +- kappa_robust delta_M1 (the frozen decisions_robust_kappa)". It matches the recompute's retain definition.
- **Suggestion:** quote this string in the record.

**4. LOW (latent, not touched by the diff): some pre-existing rows would put the non-ruled reading into the verdict.**
- **Location:** null-level rows at `:423-426` compare `tests/<null>/null_T_<t>_{median,sd}` with `null_T_summary` (ddof 1); rows at `:442-446` compare null-level `median_shift_in_null_sd` with the own reading.
- **Failure scenario:** if a production layout put these fields at the null level, the verdict would turn DISCREPANT on the reading A16 did not rule.
- **Current impact:** none. Production has no such leaves, so 0 rows fire.

**NOTE 1: some rows compare a constant with a constant.**
- `level` compares `CP_LEVEL` with 0.95.
- Implied-size `alpha` compares 0.05, the same constant as the threshold at `:731`.
- Power `alpha` compares `float(lvl)`, the path key the comparer looked up (`:527`).
- `power:levels` compares `POWER_LEVELS`.
- These echo configuration. The real evidence is the computed interval and power values next to them.

**NOTE 2: implied-size `n` uses `base.size` (`:732`), but the mean is over `e[t].size`.** The two are equal by construction (the same `f_cal`), so the value is correct.

**NOTE 3: a missing new recompute field gives DISCREPANT, not INCOMPLETE** (`row(mine=None)`). This is the existing convention; it showed up as 453 disagreements when I ran the new comparer on the old record.

## What I did not or could not check

- **The full test suite never finished** (load average about 300 on 10 cores): 30 tests passed, no failure was seen, and there is no runner summary. The 6 new tests passed in my harness, not in a pytest run.
- **I did not recompute any statistic from the raw ensembles or products**, which are not local. My checks are internal consistency, exact CP and Holm restatements, and agreement with production.
- **I did not open any production code bodies**, so whether production's internal definitions match is known only through its outputs and rule texts.
- **I did not re-review `0142a228`'s existing logic** beyond confirming that its 712 rows are unchanged.

## Final worktree status

`git -C /Users/josephbailey/local-research/MINERvA-OmniFold-s5p-recompute-review-ext status --short --ignored` printed nothing (rc 0). HEAD is `02df81e64ba10c4d817fc66eb068af1d39ef23eb`.

The scripts and outputs are in `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/c08e8191-491e-4178-a878-a2d92898fc97/scratchpad/review-ext/`, including `c.json`, `structdiff.py`, `strip.py`, `defs.py`, `sig.py`, `mutharness.py`, `mut/`, `realmut.py`, `toy-*.json` and `pytest-full.log`.
