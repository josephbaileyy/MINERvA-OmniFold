# 2D closeout Stage F: dependency checklist (DRAFT, 2026-10-16)

**Owner:** the paper-tighten lane, as director. Joseph assigned it Stage F integration on 2026-10-16.
**Status: draft.** This checklist authorizes nothing. It lists what must exist, and in what order, before each Stage F
step. Every box is open unless marked otherwise, with the evidence named.

**CITABLE FOR:** the dependency order of Stage F, and the record that closes each dependency.
**NOT CITABLE FOR:** any result, adoption, claim, KI-85 lift, publication change, push, submission, deposit, tag or
contact. Joseph has said: "okay but I am not ready to publish anything yet, I still want to review everything
extensively and also with ben".

Stage F is defined in [`../../../PLAN-20261011-2d-closeout.md`](../../../PLAN-20261011-2d-closeout.md) §4. The endpoint
it serves is **construction complete**. Full scientific closeout is NOT ACHIEVED
([`../../../DECISION-20261014-joseph-2d-endpoint-and-open-items.md`](../../../DECISION-20261014-joseph-2d-endpoint-and-open-items.md) §2).

## 0. Order

```
C production (S1–S4) ──► S5 rollup ──► production REPORT + verifier ─┐
playlist design record ─► verifier ─► playlist block ─► verifier ────┤
driver_p1 PR on main ────────────────────────────────────────────────┤
                                                                     ▼
                                         review with Ben (Joseph's) ─► Joseph's adoption ─► rebuilds ─► records
                                                                                         ─► builds ─► final review
```

Nothing to the right of "Joseph's adoption" starts before it. Joseph decides whether the review with Ben comes
before adoption. This draft assumes it does, because of his statement above.

## 1. Scientific inputs (before adoption)

| # | dependency | closed by | owner | status |
|---|---|---|---|---|
| F1 | Stage C production terminal: every S1–S4 job terminal; every item analysis PASS, or each failure INCONCLUSIVE and named | `state/2d-closeout/stageC/production/REPORT.md` with `sacct` rows, gates and digests | 2d closer | running. 12 of 401 submitted rows COMPLETED on 2026-10-16; moving to regular-QOS packs |
| F2 | The packed submission path bound before migration | the step-2 binding record (build-step record [`AUTHORIZATION-20261016-…-regular-packing.md`](../../../AUTHORIZATION-20261016-2d-closeout-stageC-regular-packing.md) §4) | director | smoke pack approved ([`…-smoke-resubmit.md`](../../../AUTHORIZATION-20261016-2d-closeout-stageC-smoke-resubmit.md)) |
| F3 | S5 rollup: every frozen check passes (pins, control vs VL175 to 1e-12, MAT vs numpy, functionals from vectors, symmetry, PSD); `production_cov.npz`, `s5.json` and `uq_production_covariance.root` written | `s5.json` and the REPORT | 2d closer | waits on F1 |
| F4 | Fresh read-only verifier on the production REPORT, with an independent recomputation of the total from the replica and universe vectors | verifier report attached to the REPORT | director dispatches | waits on F3 |
| F5 | Durable copy: products to CFS `m3246` with sha256 re-measured, including the S5 ROOT rollup (binding §4) | REPORT section | 2d closer | waits on F3 |
| F6 | `driver_p1.py` reaches `main` through its own reviewed PR (binding ruling 1) | that PR's merge | 2d closer, reviewed by the director | open |
| F7 | Playlist-consistency design record: the construction, raw or double ratio, the reference period, the treatment of 1F and the per-period MC responses, all declared before computing | director record, then a fresh verifier | director | **open, next** |
| F8 | Playlist-consistency block computed, added after S5 as a separate block, without editing VL175 or S5 | a block record with digests, verifier-checked | director | waits on F7 and F3 |
| F9 | The quoted total = S5 total + playlist block. Checks: symmetric, PSD, functionals from vectors; the budget with and without the block | the block record | director | waits on F8 |
| F10 | Every disclosure item in [`DRAFT-disclosures.md`](DRAFT-disclosures.md) has its final number from F3/F8, and each number's source line is cited | the disclosure draft, revision 2 | director | waits on F3 and F8 |

## 2. Joseph's decisions (Joseph's alone)

| # | decision | input the director provides | status |
|---|---|---|---|
| J1 | Whether the review with Ben comes before adoption, and when | [`AGENDA-ben-review.md`](AGENDA-ben-review.md) | open |
| J2 | Adopt the uncertainty: S5 total + playlist block, or something else. The central value is already adopted: `E_U`, LightGBM seed 42 ([`DECISION-20261011`](../../../../publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md)) | the REPORT, the block record and a one-page comparison against VL175 | waits on F1–F10 |
| J3 | Adopt the claim wording, inside the narrower endpoint | a claims draft produced from the disclosures | waits on J2 |
| J4 | Adopt the disclosure wording: G2, the playlist term, C07′, `NormDISCC`, C03, the endpoint, and the others in the draft | [`DRAFT-disclosures.md`](DRAFT-disclosures.md) | draft started |
| J5 | KI-85: record its actual outcome. It stays deferred and is not lifted unless Joseph decides otherwise | a KI-85 row text | open |
| J6 | Authorize each outward act separately: the standalone-repo push, any submission, deposit, tag or contact | none drafted until asked | not requested |

## 3. Rebuilds (after J2/J3)

Each item is rebuilt from the adopted products with one central denominator, `E_U`.

| # | item | current location | note |
|---|---|---|---|
| R1 | 2D budget: totals, per-block medians, flux block against published | `docs/analysis-note/values.tex` macros (`\uqMedian`, `\fluxBand`, …); paper §`sec:uq2d` | The paper currently cites the VL170/VL175 band and says "Coverage of the total remains untested" |
| R2 | χ² against the published covariance, and the generator comparisons that use the 2D covariance | paper §`sec:repro2d`; note | Indicative only. The cross-covariance of the two estimates is still missing |
| R3 | Fig. 1 (`paper_fig1_validation`) bands and caption; any note figure that draws the 2D band | paper l.239–251 | The caption lists the covariance blocks. Add the playlist block |
| R4 | Ratios, projections and the integral, from vectors | note | The S5 functional map F (31 × 205) is the source |
| R5 | Claims map: rows L1–L4 and every 2D claim | [`../../../../publication/CLAIMS-20261005-claim-to-evidence.md`](../../../../publication/CLAIMS-20261005-claim-to-evidence.md) | L4 (estimator mismatch) is superseded by the 2026-10-11 central adoption |

## 4. Records (after the rebuilds)

| # | record | content |
|---|---|---|
| K1 | `VALIDATION_LEDGER.md` | a new VL row for the production covariance and for the playlist block, with digests |
| K2 | 2D `RUN_LOG`, `2D_OMNIFOLD_STUDY_STATUS.md`, `2D_OMNIFOLD_REFERENCE.md` | the adopted products, and the endpoint |
| K3 | `KNOWN_ISSUES.md`, each row closed only to the extent its evidence landed | 88 (pairing: seed-42 stat block); 90 (the two consumers' identity checks: **verify they ran**, since this checklist has not seen evidence); 91 (flux identity, Stage B §2.1); 92 (Rvp1pi dropped in S5); 93 (K1 PASS, July qualified); 94 (R5 background stream); 85 (J5); J36 stays closed with its bound |
| K4 | `CATALOG.md` / `MANIFEST-overrides.tsv` rows for every new doc | governance |

## 5. Builds, review and recovery

| # | step | gate |
|---|---|---|
| B1 | `docs/analysis-note/build_all.sh`: note, primer and paper | three PDFs; the known biber cache failure is checked first |
| B2 | Standalone Analysis-Note repo: sync, build and commit there | **push only under J6** |
| B3 | Clean-checkout replay at the supported tiers; input/output hashes on CFS; recovery routes | a replay record |
| B4 | One independent final claims-to-evidence review | a fresh reviewer, read-only |
| B5 | Exit statement: no unresolved blocker to the adopted claims; full scientific closeout NOT ACHIEVED | the Stage F REPORT |

## 6. After the closeout (not Stage F gates)

- Remove the Stage C input backup `2d-closeout-stageC-inputs-20261012/` (538,486,940,672 B), per the plan given to
  Joseph (CFS 1A copy REPORT §2).
- PET folders: decide with Ben (agenda item).
- Scratch leftovers on pscratch: `tmp-mc-checksums-20261014/testfix/`, `tmp-cfs-breakdown-20261014/`,
  `tmp-1A-cfs-copy-20261014/`.
- An optional 1A re-download, after the closeout (2026-10-14 ruling 6).
