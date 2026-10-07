# Recovery classification for Joseph's D3 disposition (2026-10-06)

**CITABLE FOR:** the class this lane assigns to the lost-seed resolution, under its framework fixed before the
outcome (`RECOVERY-INTERPRETATION-20261006.md`, commit `078d1f9d`); the evidence for each criterion; the proposed
article wording; the one-sentence disposition proposed to Joseph.
**NOT CITABLE FOR:** Joseph's disposition, which this file only proposes, or any revised primary decision.

## 1. Evidence (all committed)

| criterion (PROCEDURE §5.5 and §6) | evidence | status |
|---|---|---|
| no residual missing draw | resolution record §1: 277/277 recovered, 0 without a product, 0 partial | met |
| (a) union, S recomputed: every decision unchanged | `RECORD-20261006-s5p-lost-seed-recovery-resolution.md` §3 (`11a266c6`), `resolved-evaluate.json` `8503eab8…` | met |
| (b) frozen S: every decision unchanged | resolution record §2–§3; `frozen-s.json` `9f4d985e…` | met |
| earliest complete-batch stops: decisions unchanged | resolution record §3; `stopping.json` `c956beb7…` | met |
| §6 independent cross-check | `REPORT-20261006-s5p-recompute-recovery-crosscheck.md` (`00009056`, recompute branch): own code, **856 of 856** quantities agree with `frozen-s.json`; k_rec = 0 in all 62 cells; determinism re-verified independently (16/16 bitwise) | **AGREE** |

**Scope of the independent checks:**
- The recompute lane's cross-check covers reading **(b)** only. It did not recompute (a) or the earliest-stop
  evaluation.
- For (a), this lane's standalone replay reproduces `resolved-evaluate.json` with 0 differences (receipt `000cd276`).
  The replay's statistics are an independent implementation, but its per-draw inputs were extracted with the frozen
  code, so this is a consistency check rather than a fully independent recomputation.
- The earliest-stop decisions rest on the campaign's `stopping.json` alone. It was self-validated against all 37
  frozen looks (resolution record §1, Phase 0).

## 2. Class: **R1, resolved, all ten hold**

All five criteria are met, with the scope stated above. The margins are reported as found:
- In every claim variant, the smallest margin T_obs − max recovered T is **64.7** (GENIE MEC shape, m1 = +2).
- In the report-only κ = 3 family, the smallest margin is **4.6** (GENIE MEC shape, m1 = +3: 868.6 against 864.0).

Both are confirmed by the cross-check.

Per test, the complete-set result (report only) is:
- k is unchanged: 0 for nine tests and 1 for NuWro shape;
- B' = 1400 (1800 for both NuWro tests);
- every test is rejected, robust at κ = 3.

## 3. Proposed article wording (replaces the `\pubhold` in §"Lost pseudo-experiments")

> Rerunning every lost pseudo-experiment, as a report-only resolution fixed and independently reviewed before the
> rerun, leaves all ten decisions unchanged: none of the 277 recovered experiments reaches the observed statistic in
> any declared variant, whether the recovered experiments are added to the calibration or evaluated against the
> frozen variant shifts, and at the earliest stopping point of the sequential rule. An independent recomputation
> confirms the frozen-shift reading. The decisions in Table I remain those of the frozen evaluation.

The closest approach goes in the supplement, in the κ = 3 family.

## 4. Proposed one-sentence D3 disposition

> "The lost-seed sensitivity is resolved by observation for all ten tests. The joint-test decisions may be stated
> without the 'can change' qualifier, provided that the report-only resolution, its independent frozen-shift
> cross-check, and the frozen decisions' primacy are stated beside them."

**Deviation from the framework:** none in the class. One addition: the framework did not anticipate that the §6
cross-check would cover only reading (b). That partial coverage is disclosed in §1 rather than treated as class X,
because X is defined by disagreement, and there is none.
