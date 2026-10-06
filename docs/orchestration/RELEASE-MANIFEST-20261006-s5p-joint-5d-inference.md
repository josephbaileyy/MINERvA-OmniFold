# s5p (`OI-193`): release manifest of the joint-5D inference family (Stage 7, 2026-10-06)

**CITABLE FOR:**
- the exact identity (path, sha256), access class and role of every product the recorded joint-5D inference result
  depends on;
- the report-only recovery and verification products;
- the reproduction route and its tested scope.

**NOT CITABLE FOR:**
- **A release.** No release, deposit, upload, tag or Data-Availability statement is made or authorized here
  (AUTHORIZATION-20260926 row 164; Joseph's 2026-10-06 approvals item 6, as recorded by the publication lane:
  "Public deposit, release tagging, submission, and any additional scientific work remain separately authorized").
- **The measurement family**, which has its own package (`docs/analysis-note/release-package-20260922/`).
- **Any physics number** beyond what the result record states.

**Companion:** the publication lane's `docs/publication/RELEASE-INVENTORY-20261005.md` (branch
`docs/publication-decision-20261005`) inventories both families against the publication plan's components and gaps.
This manifest fixes the inference family's identities as of the recorded result. Where the inventory says "a
lane-pinned …", this manifest records the digest.

## 1. Result and its records (committed, repository)

| item | path | sha256 / commit |
|---|---|---|
| joint result | `docs/orchestration/RECORD-20261005-s5p-joint-5d-inference-result.md` | origin/main `9b26b8c3` (updated `b354cdf7`) |
| frozen evaluation | `docs/orchestration/state/s5p/stage7/joint/joint-evaluate.json` | `b9604502b1aa263508ba46f0be91846d7a2106f6f2fd0ba5c172b87ee256dd11` |
| ruled robustness labels | `…/stage7/joint/robust-labels.json` | `206655f906bdffac636676f39ed86267f31eb9600ed9d45a335905fdaf7fde2a` |
| missing-seed sensitivity (superseded in its interpretation by the resolution; kept) | `…/stage7/joint/missing-sensitivity.json` | `f48e16ef351ea78c59b7e75f5bf653dc5742857457786e3d8fd1a067be8e2293` |
| seed states (reversible abs-log-path copy; the original `6823e701…` is on the cluster) | `…/stage7/joint/seed-states.abs-log-paths.json` | `bd25f1ec03ac07a205aed533193fa291bef785525529b1e5bf54a45984eaf031` |
| recovery resolution | `docs/orchestration/RECORD-20261006-s5p-lost-seed-recovery-resolution.md`; outputs `docs/orchestration/state/s5p/recovery/phase{0,A,C}/` | `frozen-s.json` `9f4d985e…`; `resolved-evaluate.json` `8503eab8…`; `stopping.json` `c956beb7…`; `determinism.json` `66036819…` |
| owner disposition | `docs/orchestration/DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md` §5 | origin/main `538739ff` |
| independent verification | branch `s5p-parallel-recompute-20260928`: `state/s5p/recompute/final-ext/compare.json` (AGREE 1379/1379); `state/s5p/recompute/recovery-xcheck/crosscheck.json` (856/856) | `97e1666a7e5722b0…`; `6ace7e0824cf2ae1…` |

## 2. Inference definition

| item | identity |
|---|---|
| contract and amendments | `docs/orchestration/state/s5p/contract*.json`; amendment 7 frozen at commit `4f5a613f` |
| frozen design | `docs/orchestration/state/s5p/prod/design.json` sha256 `404446eb2a770dc4412012c5e182e57a77afa2edd332c75de399a9281f536285` |
| evaluator code (frozen) | `nd-unfolding/s5p_joint.py`, `s5p_inference.py`, `s5p_seqstop.py`, byte-identical to `4f5a613f`; labels `s5p_robust_labels.py` (code sha256 recorded in `robust-labels.json`) |
| metric V | `$NS/stage3/V/V-s3v.npz` sha256 `35979ef75ca1b0fb019c07a20e11a4bf0fe3b230e7cea495930fb572fe8e1c84` |
| process-shift files D16 | MnvTune `c4e9586b…`, GENIE CV `0d7d1b58…`, GENIE MEC `768f942c…`, NuWro `b7b5de71…`, GiBUU `e388a2b2…` (`$NS/stage3/f4/D16-*.npz`; sha256 in the design) |
| sub-fine-grid M1 files | GENIE CV `40d9aa1c…`, GENIE MEC `5e6aa8a6…`, NuWro `706b87d4…`, GiBUU `6fbfc786…` (`$NS/stage3/m1/fine-minus-mid-*.npz`; sha256 in the design) |
| data product on J cells | `$NS/runs/s2/num/data/data_b-_j-.npz` sha256 `fb5cc6798b97b5902ad8f0fecbc49990271f7772f98d3063c1dc8596340e680c` (measured 2026-10-06; equals the publication inventory's) |
| predictions G | MnvTune v1 `gen5d/mnvtune_v1_xsec5d.npz` `bf7bd278…c466c`; GENIE 2.12.10 CV `gen5d_fluxfix/genie_cv_xsec5d_full.npz` `cfa42210…dcc2`; GENIE MEC `…/genie_mec_xsec5d_full.npz` `c179855d…790f`; NuWro 21.09 `…/nuwro_cv_xsec5d_full.npz` `475a2871…c48070`; GiBUU 2019 `…/gibuu_cv_xsec5d_fluxfix.npz` `48917692…cca18` (under `$NS`; measured 2026-10-06, full digests in the campaign-state incident) |

Here `$NS` = `/pscratch/sd/j/josephrb/s5p-20260926`.

## 3. Calibration and power products

- **Calibration:** 7176 frozen products (MnvTune 1365, GENIE CV 1366, GENIE MEC 1343, NuWro 1751, GiBUU 1351), in
  `$NS/runs/prod/cal/<null>/`.
- **Power:** 1147 frozen products (P1 193, P2 195, P3 195, P1g 199, P2g 193, P3g 172), in `$NS/runs/prod/pow/<set>/`.
- **Pins:** every digest is pinned in `reproduction/s5p/pins/unrecorded-inputs-20261006.json` (sha256
  `7ed86877…`, lane-measured), with the five final status files.
- **Recovered products** (report-only, not inputs of the frozen result): 224 calibration and 53 power, in
  `$NS/recovery/recovery/{cal,pow}/<lane>/`, with the 16 determinism reruns in `$NS/recovery/determinism/`. They are
  listed by seed in `docs/orchestration/state/s5p/recovery/tables/rec-recovery-manifest.json`.

## 4. Reproduction (tested scope)

- **Tier D** of `reproduction/s5p/`, made final by `HANDOFF-20261006-s5p-reproduction-tier-d.md` (merged
  `a12e2359`):
  - from a fresh clone, the frozen `s5p_joint.py evaluate` replays **bitwise** to `joint-evaluate.json` at the
    recorded roots, and to 1e-12 relocated;
  - the label step reproduces `robust-labels.json`.
  - Reports: `reproduction/s5p/reports/fresh-3a80aa74/`, `report.json` `4e40bc6c…`, and `reloc-3a80aa74/`,
    `report.json` `bbb8a607…`. Both exit 0.
- **Scope:** an internal Perlmutter replay of stored products. It does not regenerate the calibration
  pseudo-experiments.
  - Tier C has not been run.
  - A public, sufficient-product replay for an external reader does not exist. The publication inventory lists it as
    a gap.
- **Command form:** in a fresh clone, run `python3 reproduction/s5p/repro_s5p.py run --config <config>` (see
  `reproduction/s5p/README.md` for roots and tiers). Recovery commands are in
  `PROCEDURE-20261005-s5p-lost-seed-recovery.md`.

## 5. Units, hypotheses and conventions

- **Statistics:** T_total and T_shape are dimensionless quadratic forms in the metric W = V + diag Var(μ_G) on the J
  cells (s5p_joint). p-values are Monte Carlo, (k + 1)/(B + 1), and never zero. The family is ten tests under Holm
  with determinacy at α = 0.05.
- **Hypotheses:** H0(G) as defined in amendment 7 `claims.family`, quoted verbatim in the result record §1.
- **Units of the predictions and data:** the analysis's 5D cross-section units, as recorded in each product's
  metadata. This manifest does not restate them.

## 6. Access class and licensing

- **Raw data:** MINERvA ME-FHC OpenData. Per the publication lane's reading of the open-data page (2026-10-05) it is
  CC0, with a citation request (DOI 10.15484/3022562). Re-read the page before quoting it.
- **Analysis-produced products** (calibration, power, recovery, predictions, V, D16, M1, data on J cells): on
  purgeable `/pscratch`, releasable by the authors. Not yet deposited.
- **Code and records:** the repository.
- **Persistence risk:** `/pscratch` is purgeable. A deposit or archive of §2–§3 products needs a separate
  authorization; Joseph's approvals item 6 reserves deposits.

## 7. Remaining for an external release (costed in the delivery record)

1. A public sufficient-product package for the inference family: the J-cell data, predictions with Var(μ_G), V, D16
   and M1, the observed statistics, the calibration T arrays per variant, and the outputs. Add a standalone replay
   tested from an empty checkout.
2. An archive of the `/pscratch` products before purge, under separate authorization.
3. The deposit and the tag, under separate authorization.
