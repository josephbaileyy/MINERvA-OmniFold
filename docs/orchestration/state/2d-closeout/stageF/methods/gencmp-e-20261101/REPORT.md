# REPORT The GENCMP amendment E paper round (2026-11-01)

**By** the paper rewrite lane (Claude), for the director.

**Under:**
- FD-GENCMP-AMENDMENT-E-REPORT.md §4, row 1 "E-1 completes" (#662);
- the declaration's §8 and its addendum E-A1;
- the director's work order of 2026-11-01, and ruling A on the "as first made" table.

**MEASURES:** nothing new. Every value comes from committed readouts through `make_values_fived16.py`.

**CANNOT AUTHORIZE:** a claim, a reading or a wording. The changed values and the sentences that print them go to
Joseph through the director, with before and after (below).

## What changed

| item | change | where |
|---|---|---|
| 1. re-pin | `g`, `diag`, `fup`, `sens2` and `fboot` in both arms → `fd/gencmp-e/rerun1/chain/chdefs/{with,nopl}/readout/` (with: `a19009e0`, `522bfafa`, `586cd741`, `4bc21dfd`, `5bb475ea`; nopl: `d9a1ce38`, `4e77966e`, `748f3af6`, `6626cb73`, `24ff27f9`). `table4` also asserts that Stage G's g and χ² equal the `defs.json` corner to 1e-12 (XC), and the fb-χ² = Stage G assertion now reads the re-pinned g. A new guard requires each downstream readout to name, by sha256, the upstream readouts its arm pins | `make_values_fived16.py` |
| ruling A | the gs- family, which the note's "as first made" table prints, reads Stage G's committed readouts under pin `g0` (`b55366b3` with, `75a9ddee` nopl). Every other former gs- use is merged into `label-`/`g-` | `make_values_fived16.py`; `sec_fived16.tex` |
| 2. scoping | the paper's scoping sentence goes, and "of that χ²" returns to the base's "of the reported value". The note's scoping sentence goes, with the clauses in the sensitivity-table, modes and diag captions. Under ruling A, also the ":343" clause "…, the predictions on which the sensitivities … were computed" and the "as first made" caption's last sentence | `paper_body.tex:263`; `sec_fived16.tex:262`, `:266`, `:311`, `:317`, `:343`, `:376` |
| 3. values | 252 keys change (sens 201, diag 28, fb 23), equal key by key to `values_diff.tsv` without its 64 gs- rows. The 110 gs- keys equal what #656 printed (`VALUES-CHECK.txt`, from `check_values.py`) | `values_fived16.tex` |
| 4. figures | the paper's ratio figure and the note's modes figure are now E-1's with-arm figures (`f547bc92`, `f5f9e530`). The modes caption gains "The predictions are in the analysis definitions." (E-A1). The ratio caption already says so (#656) | `figures/`; `sec_fived16.tex:311` |
| — | `nd-unfolding/fd_gencmp_figures.py` and `fd/gencmp/figures/` stay unchanged as records | — |

**Unchanged:**
- the paper's 2D-quadrant sentence (`paper_body.tex:119`) and the C_model target clause, which stays until E2 runs;
- Table IV and every `g-`, `r04-` and `corr-` value;
- `main_paper.tex`, `main_note.tex`, `sec_execsummary.tex`, `primer_body.tex` and `sec_joint.tex`.

## For Joseph: the changed values, before and after

**The paper prints no changed value.** Its changes are:
- the scoping sentence removed;
- "of the reported value" restored;
- the ratio figure, which plots the same numbers as #656's (review: max relative difference 0). Only its legend text
  differs: E-A1's qualifiers.

**The note.** Of the 252 changed keys, 116 print, all in `sec_fived16.tex`. `VALUES-CHECK.txt` lists each with its
file:line. They print in three places:
- **The bootstrap sentence (`:262`), the only prose that changes.**
  - 16–84 % bands, before → after:
    - GENIE CV 102–108 → 104–110;
    - GENIE + MEC 217–229 → 222–235;
    - NuWro 129–133 → 126–130;
    - GiBUU 45–46 → 47–48.
  - Median offsets:
    - GENIE CV 0.25 → 0.26;
    - GENIE + MEC 0.30 → 0.32;
    - NuWro 0.22 → 0.20.
  - The χ² each band is "around" now prints Table IV's value, not Stage G's original. The key changes from `gs-` to
    `g-`:
    - GENIE CV 105 → 107;
    - GENIE + MEC 224 → 229;
    - NuWro 131 → 128;
    - GiBUU 45 → 48;
    - Tune v1 262, unchanged.
- **The sensitivity table:** 100 cells change.
- **The diag table:** 5 cells change:
  - GENIE CV top share 32.7 → 31.8;
  - GiBUU modes for 99 %, 6 → 7;
  - GiBUU top share 32.5 → 37.5;
  - NuWro top share 27.6 → 24.7;
  - NuWro top σ 2.21 → 2.19.

**The summary keys the work order names:**

| key | before | after | printed? |
|---|---|---|---|
| `sens-detlat-fall-max-nopl` | 18 | 19 | no. The paper and the note print the with-block value, `sens-detlat-fall-max`, which stays 18 |
| `fb-edge-min` | 1.6 | 1.4 | no. Both print `fb-edge-max`, which stays 3.8 |
| `diag-gibuu-reported-modes99` | 6 | 7 | yes, the note's diag table |
| `diag-gibuu-reported-modes99-nopl` | 6 | 7 | no |
| `diag-gmec-reported-modes99-nopl` | 10 | 9 | no |
| `diag-nuwro-variant-modes90` (and `-nopl`) | 6 | 7 | no |

**Unchanged summaries:**
- `sens-flux-fall-lo/hi` 23/38;
- `sens-detlat-fall-max` 18;
- `sens-joint-chi2-min` 41;
- `fb-edge-max` 3.8;
- `fb-offset-relmax` 0.4.

Each still holds against the new table values (review: 23.2–38.3 %, ≤ 17.8 %, 41.91, ≤ 3.79 %, ≤ 0.38 %).

## Checks, on the final text

| check | result |
|---|---|
| plain re-pin, before ruling A | the generator's diff equals `values_diff.tsv` exactly (316 keys) |
| `check_values.py` (`VALUES-CHECK.txt`) | PASS: 252 = the tsv without gs-, and gs- = #656. Planting a changed value of either kind makes it FAIL |
| `make_values_fived16.py --check` and `--self-test` | PASS: 2490 values, 2 figures equal their sources. Two new plants, each refused by its own guard. Swapping diag, fup or sens2 for the old Stage G file is refused |
| the ledger (`check_ledger.py`, base `a4cd6ffcf`) | 6 rows, 26 probes, 10 changed base sentences, 0 failures; self-test PASS |
| `build_all.sh` | PASS: all five PDFs (paper 12 pp, note 131 pp, primer 15 pp); no "??" and no "[PENDING" |
| layout | **NEW:** the paper's page 11 has an 11.2 pt overfull vbox, which the base does not have. The shorter sensitivity paragraph moves the text up, so the first reference starts at the foot of page 11's left column (at the base it started on page 12). The 9.7 pt hbox at Table III is the base's |
| the two-direction review (`review.md`) | no High and nothing false. 1 Medium (the ratio legend's qualifiers in the paper) goes to the director. Of the 3 Low, 2 are fixed and 1 is reported |
| `check_held.py --fact-held` (`CHECK-HELD.txt`) | 3 flags, all pre-existing (G1:paper-g-08, G1:paper-s-08, G1b:paper-s-07) |
| the rater copy | holddiff's multiset check PASSES. **`make_rater_copy.sh` exits 1** at `fix_da_order.py`: "a reference line precedes the DATA AVAILABILITY heading … no case describes this layout". It is the page-11 move above; at the base it exits 0. The rater text, on which check_held ran, is written before that step. The blinded copy is not produced |
| `check_dead_containment.py`; `test_build_all.py` containment tests | PASS; 15 passed |
| `generate_manifest.py --check --at-sha HEAD` | OK after the `[manifest]` commit, which adds the round's seven new files |
| local CI (`run_ci.py`) | 38 of 38 steps pass |
| the reading copy | 22 pages: the paper's pages 9–12 and the note's pages 73–79, each changed page followed by its base page |

## For the director

1. **Page 11's layout** (the overfull box and the rater-copy stop). No word can fix it within the order. It needs a
   layout change (a float or bibliography placement) or a new layout case in `fix_da_order.py`.
2. **The ratio legend in the paper** (review 1). E-A1's qualifiers name a NuWro hydrogen flag and a "B3" closure that
   the paper does not define.
3. **The lost pointer** (review 2). The paper no longer points to `sec:fived16-gen-target`.

Nothing is submitted, deposited or tagged.
