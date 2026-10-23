# Qualifier density before and after register round r15

**Instrument:** the register study's density tool, run exactly as its REPORT.md §3.1 states:
- `tex2prose.py` on `main_paper.tex`, with `paper_body.tex` expanded: abstract plus body, without floats, captions,
  comments or math;
- `qcount.py table` and `strict_index.py` on that prose;
- `abstract_stats.py` on the abstract.

The corpus prose is the study's (twelve papers, `register-prd-study/INPUTS.sha256`). It was re-read from the
study's scratch copy, and the three files spot-checked there match `INPUTS.sha256`.

**Inputs measured:**
- before: origin/main afb7e1fa (`prose/ours.txt` sha256 `3311678dd245…`);
- after: this branch's paper sources (sha256 `3242af0ee387…`).

The study measured our paper at 9cf49713, before the RE-1 integration (6,688 words, Q 34.5). The "before" column
here is afb7e1fa, after RE-1 (6,863 words, Q 34.1).

**Calibration caveat (study §3.2):** the counter is accurate on our paper (precision about 0.87). It over-counts
the corpus about fourfold, and it counts tolerances ("within 10%"), definitions ("only reconstructed W") and
findings ("not mutually consistent") as markers. The after text keeps many such technical uses, so the residual
counts overstate the remaining caveat density.

## Main table (per 1,000 words unless marked)

| measure | before (afb7e1fa) | after (r15) | corpus median [min, max] | inside range after? |
|---|---|---|---|---|
| words | 6,863 | 6,579 | — | — |
| sentences | 246 | 256 | — | — |
| mean sentence length | 27.9 | **25.7** | 22.7 [19.1, 28.2] | yes |
| Q (all markers) | 34.1 | 29.3 | 14.4 [7.1, 26.9] | no (+2.4) |
| Q excl. NEG | 23.0 | **18.1** | 10.3 [5.7, 21.5] | yes |
| SCOPE | 11.1 | 9.6 | 3.7 [2.1, 6.0] | no |
| COND | 3.6 | **2.4** | 0.8 [0.3, 9.3] | yes |
| STATUS | 5.5 | 3.6 | 0.2 [0.0, 0.6] | no |
| HEDGE | 1.2 | 0.8 | 1.9 [1.1, 4.0] | below the range |
| CONCESS | 1.6 | **1.7** | 2.5 [0.8, 5.3] | yes |
| NEG | 11.1 | 11.2 | 4.1 [1.5, 5.4] | no |
| sentences with ≥2 markers | 28% | 20% | 5% [2, 12] | no |
| sentences with a scope restriction | 31% | 25% | 10% [6, 21] | no (+4 points) |
| restrictive parentheticals | 0.7 | **0.8** | 0.4 [0.0, 0.9] | yes |
| pointer parentheticals | 8.0 | 1.4 | 0.2 [0.0, 1.3] | no (+0.1) |
| strict index | 16.0 | 12.3 | 2.6 [1.3, 4.2] | no |
| sentences with a strict marker | 33% | 27% | 5.5% [3, 9] | no |
| note-pointer clauses ("Ref. [N], Sec./App.") | 40 | 25 | — | about 1.3 per subsection (20 sections and subsections) |

## Abstract (`abstract_stats.py`)

| | before | after | corpus |
|---|---|---|---|
| words | 135 | 114 | — |
| markers (Q) | 10 (74 per 1,000) | 5 (44 per 1,000) | 0–3 per abstract (0–22 per 1,000) |
| SCOPE + COND + STATUS markers | 7, in 4 of 5 sentences | 4, in 4 of 5 sentences | at most 1 per abstract |

The four after markers:

| marker | status |
|---|---|
| "within about 1%" | a tolerance, not a caveat |
| "central values only" | restored by Joseph's fix round 1 |
| "at the tested truths" | Joseph, plain-language pass 2, item F1 |
| "no evidence of" | KEEP list, E1 |

## What holds the remaining excess

| source | what it holds | measures it raises |
|---|---|---|
| Sec. VIII A, the limitations list that Joseph's decision requires | 8 items, 7 STATUS markers | STATUS, strict index |
| The scope paragraph | the remaining negatives that change meaning (KEEP list R1) | SCOPE, COND, NEG |
| KEEP-list qualifiers in place (§5 list in REPORT.md) | the hybrid nulls; "no evidence of" (twice); "descriptive" on the 2D χ²; the purity bias's own omission sentence (E6); the 2D omission sentence (E5); "for one pair of seed settings" (E7); the D-ID population and scope (E9); "provided the calibration is exact" (E10) | as each marker falls |
| Text a build gate binds to `paper_body.tex` (`check_sec4_receipts.py`) | the post hoc rescoring sentence (97.7%/78.1%) and the phrase "biased by up to 4% in simulation" | REPORT §6 |
| Technical uses the lexicon counts (study §3.2) | "within N%", "at nominal truth", "only part", "except in the highest-W cells", "the tested truths" | SCOPE, NEG |

Neither the scope nor the limitations were deleted to move a number. The round's targets were the measures the
rules act on directly:
- pointer parentheticals: 8.0 → 1.4;
- note pointers: 40 → 25, one plain clause per paragraph;
- sentences with two or more markers: 28% → 20%;
- STATUS outside Sec. VIII A: 38 → 17 instances (24 in all, 7 of them in the list).
