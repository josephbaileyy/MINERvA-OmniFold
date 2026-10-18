# DECISION 2026-10-17 — Joseph: adopt S5 + C_PL as the 2D uncertainty, before the review with Ben

**Recorded by** the paper-tighten lane, as director (Stage F). On 2026-10-17, in his session, the director put the
Stage F decisions J1 and J2 ([`state/2d-closeout/stageF/CHECKLIST.md`](state/2d-closeout/stageF/CHECKLIST.md) §2)
to Joseph. Before he decided, a fresh read-only session wrote an independent briefing of the options from the
committed records alone, with no recommendation. The director checked its citations and reported its findings to
Joseph. The briefing is uncommitted: it is in the director's session scratchpad, `briefing-J1-J6.md`. Joseph's answers, verbatim:

- **J1** (whether the review with Ben comes before adoption): "okay J1, we should adopt first". sha256 of the text
  plus a final newline begins `05187919828178c7`.
- **J2** (which uncertainty), after asking for the director's recommendation, which was option A, S5 + C_PL, without
  adding X02 or X03 (§3): "okay I agree with that". sha256 of the text plus a final newline begins
  `39f39d66814d1f8f`.

**CITABLE FOR:**
- J1: adoption precedes the review with Ben;
- J2: the adopted 2D covariance is S5 total + C_PL, with the products and digests in §1.

**NOT CITABLE FOR:**
- any claim or disclosure wording (J3, J4), or KI-85 (J5). These are later decisions;
- any outward act: a push, submission, deposit, tag, or contact with Ben, coauthors, the collaboration, MINERvA or
  NERSC (J6). Joseph is not ready to publish and will review everything extensively, including with Ben;
- a coverage, calibration or validation statement about the adopted covariance;
- a cause for the run-period inconsistency, or a statement about which period is right.

## 1. What is adopted

The quoted 2D uncertainty becomes **Q = S5 total + C_PL**, on S5's 205 cells and its 31 functionals. The central
value is unchanged: `E_U`, LightGBM seed 42
([`../publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md`](../publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md)).

| product | sha256 | record |
|---|---|---|
| S5 `production_cov.npz` | `6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc` | [production REPORT](state/2d-closeout/stageC/production/REPORT.md) (PR #150), verified in [`F4-VERIFICATION.md`](state/2d-closeout/stageF/F4-VERIFICATION.md) (PR #151) |
| S5 summary `s5.json` | `8c815149517857302af4b3a64b0db4148a13515b8182bd6eebb2f89c57d92510` | production REPORT |
| `playlist_term.npz` (C_PL) | `c1723cb5e185ae7a6176fbbe523432ab87877c8cddcfe721eaed71f0a43b9476` | [playlist REPORT](state/2d-closeout/playlist-term/REPORT.md) (PR #144) |
| `s5_plus_playlist.npz` (Q) | `8ccb4d723c3dbf737a7fb1d5236e5e25409c41b42b64ac55dccbbc12f595600e` | [COMBINATION-REPORT](state/2d-closeout/playlist-term/COMBINATION-REPORT.md) (PR #149); budget, effect and χ² reproduced independently |
| `combination.json` | `050e256023277ec9da492ffa7b9d129275c3afa2bfc6c47091999d88de5bf18d` | committed with the COMBINATION-REPORT |

The npz files are on CFS, each with `SHA256SUMS`: `m3246/josephrb/2d-closeout-stageC-production-20261015/results/s5/`,
`m3246/josephrb/2d-closeout-playlist-term-20261016/` (playlist REPORT) and
`m3246/josephrb/2d-closeout-playlist-combination-20261017/`. The director re-measured
`production_cov.npz` and the combination `SHA256SUMS` on CFS on 2026-10-17.

**Sizes** (COMBINATION-REPORT §2, relative σ in percent of `E_U`): per-cell median 6.45, p84 9.18, max 23.6;
integral 4.75. S5 alone gives 6.04 / 8.95 / 23.3 / 4.33; VL175, which this replaces, 6.09 / 9.02 / 23.1 / 4.23.

**What is superseded:** VL175 as the quoted 2D covariance
([`../publication/DECISION-20261012-joseph-adopt-2d-c04-repair.md`](../publication/DECISION-20261012-joseph-adopt-2d-c04-repair.md)).
VL175 stays on record as the earlier construction. Its flux repair carries into S5.

## 2. Not added

- **X02** (bootstrap × seed interaction) and **X03** (universe × retraining) are reported, not added, as rulings R5
  and R7 already set: ruling R7 reports them rather than adding them (Stage B REPORT; production REPORT §3).
- **The learner dependence** (exact-split against LightGBM, median 0.98% per bin) is in no block. It is disclosed
  (draft D3).
- **G2** is carried as a disclosed approximation
  ([`DECISION-20261015-joseph-g2-carry.md`](DECISION-20261015-joseph-g2-carry.md)), unmeasured.
- **C09** (unfolding-model and regularization dependence) and **C10** (response departures) are Stage D and unpriced
  (Stage B REPORT §3, R8).

## 3. The recommendation Joseph accepted

The director's reasons, as given to Joseph:
- the 1G–1M p_∥ step is measured (+6.94% ± 0.41 after unfolding), and only Q includes it: the raw diluted p_∥ χ² is
  34.8 against S5 and 1.97 against Q (a sensitivity reading only);
- it carries out the 2026-10-15 ruling ([`DECISION-20261015-joseph-playlist-consistency-term.md`](DECISION-20261015-joseph-playlist-consistency-term.md));
  the block was frozen before any S5 number was read and combined under a reviewed specification;
- X02 is negligible against the total. X03 is training noise already inside the universe block, because each universe
  shift is a single-seed unfold, so adding it would count that noise twice.

Conditions the director attached, which go to J3/J4:
- the disclosure states that C_PL accounts for the run-period disagreement in the budget but does not explain it
  (the director's word to Joseph was "covers"; it means containment by construction, not coverage); that its
  double-ratio check is passed by construction; and that which period is right is unknown;
- the endpoint sentence names what is outside every block: G2, the learner dependence and C09/C10.

## 4. What follows

The rebuilds R1–R4 (CHECKLIST §3) from Q and `E_U`, with KI-90 checked there; R5 (the claims map) waits on J3; then the records K1–K4 and the
builds B1–B5. Every number reaching a deliverable is read from the products in §1. Nothing is pushed without J6.

**Same-model caveat:** the director, the briefing session and the verifiers are Claude Opus 5.5 on the
claude-school account.
