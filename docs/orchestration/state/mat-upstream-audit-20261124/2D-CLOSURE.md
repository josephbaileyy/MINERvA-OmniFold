# 2D closure of the GEANT truth-weighting difference (MAT-MINERvA `3e411c0d`), 2026-11-24

Lane: `minerva-lib`. Zero compute. This record follows `README.md` in this directory, which records the
upstream difference: at our pin `50d76314`, the `GEANT_Neutron`, `GEANT_Pion` and `GEANT_Proton`
universes leave the efficiency denominator at weight 1. Joseph ruled that no open item is added, and
the director asked for this record.

**Verdict for 2D: CLOSED as negligible, within the bound below.** No new open item.

## 1. The measured bound

`closure_2d.py` reads its inputs through `git show` at main `c720db69b9975443344b93bd6d5619f388ccf77f`.
Its full output is in `closure_2d.txt`; every number below is copied from there.

| input | path | sha256 |
|---|---|---|
| per-band GEANT sizes (VL175) | `docs/orchestration/state/2d-closeout/c04-repair/products/budget.json`, `/adopted/per_band` | `aab8a24ebd61df54e7277999d49300c3bdaa045710835bfa05adf3bfc71dd8fa` |
| Q's sizes | `docs/orchestration/state/2d-closeout/stageF/rebuild/outputs/recompute/recompute_results.json`, `/sigma/Q` | `35e00182ec934d678c32185d4fde6406daf406bdd9dca01b5d0110f451a58e03` |

| quantity | median per cell (%) | integral (%) |
|---|---:|---:|
| `full_GEANT_Neutron` | 0.125545 | 0.020422 |
| `full_GEANT_Pion` | 0.259702 | 0.040644 |
| `full_GEANT_Proton` | 0.088865 | 0.018279 |
| the three in quadrature | 0.301834 | 0.049021 |
| Q | 6.447900 | 4.754980 |
| variance fraction of Q | 0.002191 | 0.00010628 |
| Q with the three removed | 6.440832 | 4.754727 |
| Q with the three doubled | 6.469059 | 4.755738 |

Removing the bands is the extreme of the direction README §3 reasons toward, which is NOT MEASURED.
Doubling them is an extreme in the other direction. Between those extremes:
Search: 3e411c0d; GeantHadronUniverse; GeantNeutronCVReweighter; IsTruth (git grep, excluding this directory and MANIFEST.tsv; the only hit is a numbered MAT MuonSystematics.cxx copy under fd/runperiod-loc-20261110, which has nothing to do with GEANT) @ c720db69b9975443344b93bd6d5619f388ccf77f

- **The integral cannot move.** It stays within 4.7547–4.7557, so the quoted 4.75 is unchanged.
- **The median moves by at most 0.021 percentage points.** It stays within 6.4408–6.4691, against a
  quoted 6.45. At the quoted two decimals that is at most one unit in the last digit: 6.44 at full
  removal, 6.47 at doubling. No quoted 2D median is moved by more than that.

## 2. Caveats

1. **The per-band values come from VL175's budget, which Q superseded.** S5's per-band GEANT values were
   not read. The bound above therefore holds only if S5's GEANT pieces are of the same size as VL175's.
   This record does not show that they are.
2. **Combining per-bin medians in quadrature is an approximate bound, not a recomputation.** Each band's
   median comes from a different set of cells. Q was not rebuilt without the bands.

Caveat 1 is the reason the verdict says "within the bound below". Neither caveat changes the
conclusion that the three bands are about 0.2% of Q's median variance in the VL175 budget.

## 3. 5D: attached to the existing thread, not a new item

The open 5D question for these bands is the `GEANT_Neutron` and `GEANT_Proton` departure. It is
recorded in `docs/orchestration/OUTCOME-20261108-1b-precheck-part1.md`: rule S DEPARTS and rule K FAIL
in named cells. The diagnosis in `docs/orchestration/OUTCOME-20261109-band-diagnosis.md` found the
inputs EQUAL and the departure seed-stable. Its scale test read MIXED, so it licenses no mechanism.
It places the cause "inside the estimator" and leaves the truth dependence (its item c) NOT CITABLE.

- **MAT-MINERvA `3e411c0d` is a CANDIDATE INPUT to that question, NOT A MECHANISM.** It changes
  exactly the truth-side weighting of these bands, and at our pin their truth weight ratio is 1.
- **Against it:** `GEANT_Pion` has the same truth-side treatment at our pin, and it reproduces.
  The pre-check records rule K PASS for bands Flux, `GEANT_Pion` and MinosEfficiency
  (`OUTCOME-20261108-1b-precheck-part1.md`).
- **LL5D's primary reading is unchanged.** It already excludes `GEANT_Neutron` and `GEANT_Proton`
  (`docs/orchestration/DECISION-20261108-joseph-5d-coverage-and-parallel-studies.md`, item 1).
- Whether to declare a further study of the two bands stays Joseph's decision. The director does not
  recommend one (`OUTCOME-20261109-band-diagnosis.md`, "What it changes").

## 4. Quantification

**NOT AUTHORIZED, and not proposed.** The quantification would be an event-loop pass with the three GEANT
truth bands, built against MAT-MINERvA without the early return, then a re-projection of those bands.
**ESTIMATE, not measured:** a few CPU node-h, scaled from the 4.808 node-h of the MP1-A S1 event-loop
pass (`docs/orchestration/state/data-survey-20261022/SURVEY.md`). The MAT-MINERvA rebuild, the binding
and the director's GO would cost more than the compute.

## 5. Correction to the 2026-11-24 message to the director

That message said neither caveat "could move a quoted 2D number". **That is wrong for the median.** Full
removal or doubling changes the quoted 6.45 by one unit in the last digit, as §1 shows. The integral
claim holds. §1 replaces the sentence with the bound.
