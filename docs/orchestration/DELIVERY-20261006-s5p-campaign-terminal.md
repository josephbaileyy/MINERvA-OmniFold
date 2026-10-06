# s5p (`OI-193`): terminal delivery of the precision-measurement campaign (2026-10-06)

**CITABLE FOR:**
- the campaign's honest terminal disposition: the four final status fields, worded under CHECKLIST-20261001 §4;
- paper-wide readiness;
- the evidence routes, the measured spend and both remote heads;
- the costed remaining requirements.

**NOT CITABLE FOR:**
- any measurement or new reportable uncertainty;
- publication readiness, which is NOT READY;
- a release, deposit, tag or submission (none is made or authorized here);
- any change to frozen claims, statistics or grades.

**Authority:** `AUTHORIZATION-20260926-precision-measurement-completion.md` and
`GOAL-20260926-precision-measurement-completion.txt`, with amendments 1–8 and the owner decisions recorded in
`DECISION-20261004-*`, `AMENDMENT-20261004-*` and `DECISION-20261005-*`.

## 1. The four final fields

**`campaign_disposition`:** the bounded campaign is **TERMINAL**. Its two branches are distinct.
1. **Measurement branch: NOT ADMITTED** at the Stage-2 exit (amendment 4; `RECORD-20260927-s5p-stage2-exit.md`
   §4), verbatim: "no reporting definition can meet the frozen useful-precision targets with any configuration the
   rules support within the budget". No measurement construction was run, and the targets were not relaxed.
2. **Joint-5D inference: executed** under amendment 7 (frozen at `4f5a613f`), with its result recorded after the
   independent verification: `RECORD-20261005-s5p-joint-5d-inference-result.md`.

**`reportable_uncertainty_scope`:** **no new reportable uncertainty.** s5p constructed and adopted no measurement or
covariance product. The adopted scalar-5D trunk `3d7465f6…` and its four travelling measurements are unchanged, and
s5p does not re-qualify them.

**`joint_5d_inference_status`:** all **ten** simple hypotheses H0(G) (amendment 7 `claims.family`; five predictions ×
total and shape) are **rejected** at familywise α = 0.05 (Holm with determinacy, 95% Clopper–Pearson intervals).

| test | final B | stop reason | k | claim p | label (κ = 3 replace) | missing draws |
|---|---:|---|---:|---:|---|---|
| MnvTune total / shape | 1365 | rule met for both tests | 0 / 0 | 1/1366 | robust / robust | all observed; none reaches T_obs |
| GENIE CV total / shape | 1366 | rule met for both tests | 0 / 0 | 1/1367 | robust / robust | all observed; none reaches T_obs |
| GENIE MEC total / shape | 1343 | rule met for both tests | 0 / 0 | 1/1344 | robust / robust | all observed; closest margin 4.6 T units (shape, κ = 3) |
| NuWro total / shape | 1751 | rule met for both tests | 0 / 1 | 1/1752, 2/1752 | robust / robust | all observed; none reaches T_obs |
| GiBUU total / shape | 1351 | rule met for both tests | 0 / 0 | 1/1352 | robust / robust | all observed; none reaches T_obs |

- **Conditions:** every claim is stated with amendment 7's six `conditions_stated_with_every_claim`, quoted verbatim
  in the result record §3.
- **Missing-seed status** (Joseph's disposition, DECISION-20261005 §5, "Certified, margin disclosed"):
  - all 224 calibration and 53 power draws lost to time limits were recovered by exact deterministic reruns
    (determinism 16/16);
  - none reaches the observed statistic, so no missing-draw assignment changes any decision;
  - with complete batches, four nulls would have stopped one batch earlier (B = 1200), with the same decisions.
  - The recovery is report-only, and the primary decisions are the frozen ones.
  - Check scope: the frozen-shift reading is independently cross-checked (856/856). The union reading is a same-code
    consistency replay. The earliest stops come from the self-validated `stopping.json`.
- **Power per null** (context only, because every decision is a rejection):
  - MnvTune null: P1 and P2 have power 1.000 for both tests at 0.05 and 0.005; P3 (W2) has shape 0.231 at 0.005.
  - GENIE CV null: P1g has shape 0.739 at 0.005; P2g is low; P3g is ≈ 0.
  - The T6 target (shape ≥ 0.80 at 0.005, MnvTune null) is met by P1 and P2, not P3.
- **Independent recomputation verdict:** AGREE, 1379/1379 rows, 0 discrepancies, from the independently reviewed
  comparer extension.
- **What this is:** a statement about H0(G) as amendment 7 defines it, the simple fine-grid hybrid null, not about a
  measured cross section.

**`publication_readiness`:** **NOT READY.**
- The authorization requires the joint result and all retained claims to qualify, and the precision-measurement
  objective (a useful scalar measurement with defensible TOTAL uncertainties) is unmet, because the measurement branch
  was not admitted.
- Joseph's 2026-10-06 approval, recorded by the publication lane, modifies the prerequisite for one PRD-class
  article only. It explicitly preserves "s5p's recorded NOT READY status"; that article's readiness is assessed
  separately by the publication lane.

## 2. Paper-wide readiness

The paper-wide completion table (`CAMPAIGN-s5c-20260924-paper-wide-table.md`) is reconciled in its own
2026-10-06 s5p section:
- **R16 (joint-5D generator inference):** its closure criterion is met.
- **R20 (reproduction and release):** tier D is final, and an inference release manifest exists. It stays OPEN
  because no public package, deposit or tag exists.
- **R21 (builds and sync):** clean builds and a synchronized standalone (§5). It stays OPEN for the nine listed
  consistency defects, which s5p did not re-examine.
- **Every other row** keeps the status recorded there; s5p does not re-grade them.

## 3. Evidence

| deliverable | record |
|---|---|
| joint result with stated conditions | `RECORD-20261005-s5p-joint-5d-inference-result.md` |
| evaluation outputs | `state/s5p/stage7/joint/` (`b9604502…`, `206655f9…`, `f48e16ef…`; seed states `bd25f1ec…` ↔ `6823e701…`) |
| independent recomputation | REPORT-20261005 §8 and REVIEW-20261005-…-comparer-extension (branch `s5p-parallel-recompute-20260928`) |
| lost-seed recovery and resolution | `PROCEDURE-20261005-s5p-lost-seed-recovery.md` (reviews 1–3 plus a delta verification); `RECORD-20261006-s5p-lost-seed-recovery-resolution.md`; REPORT-20261006-…-recovery-crosscheck |
| owner decisions | `DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md` §1, §2, §4, §5 |
| power per null | result record §6; resolution record §4 |
| release materials | `RELEASE-MANIFEST-20261006-s5p-joint-5d-inference.md` |
| reproduction update | `HANDOFF-20261006-s5p-reproduction-tier-d.md`; `reproduction/s5p/reports/{fresh,reloc}-3a80aa74/` |
| note/primer text, build and sync | see §5 |

## 4. Spend (meter, 2026-10-06T05:24Z; budget revision 7, `be29f2c3…`)

| item | billed CPU node-h | allocation |
|---|---:|---:|
| development | 23.930 | 24.0 |
| stage3_design | 2.292 | 2.3 |
| stage3_repair2 | 12.184 | 12.2 |
| production | 207.899 | 234.647 |
| verification/repair (the lost-seed recovery) | 6.887 | 68.287 |
| **campaign pool** | **253.192** | 341.434 |
| **cumulative envelope (with the prior 35.086)** | **288.277** | 376.52 |

- **GPU:** 2.086 node-h (8.346 A100-h) of the 2.5 development stage; cumulative 12.182 of 125 node-h.
- **Concurrency:** never above the 2.0-node cap.
- **Budget rulings:** the owner's two bounded extensions (revisions 6 and 7) and the A2 reading of the 10% pool limit
  are recorded in their decision files. No further hours were requested.

## 5. Builds, sync and remote heads (measured 2026-10-06)

| tree | `bash build_all.sh` | pages note / primer / paper | containment | Overleaf `latexmk -jobname=output main_paper.tex` |
|---|---|---|---|---|
| canonical, fresh worktree at `cbd075e7` | exit 0 | 122 / 9 / 5 | `RESULT :: PASS :: head=cbd075e7… tree=clean`; self-test PASS | exit 0, 5 pp, 0 undefined references, text identical to `main_paper.pdf` |
| standalone at `deeafae` | exit 0 | 122 / 9 / 5 | `RESULT :: PASS` (`head=unknown`: the standalone has no `lib/tree_state.py`, the documented fallback) | exit 0, 5 pp, 0 undefined references |

- **Text comparison:** in the standalone, `pdftotext` of note, primer, paper and `output` is identical to the
  canonical build.
- **Inspection:** the new §8.6, Table 3, the exec-summary item and the primer paragraph were read on the rendered
  pages.
- **Reviews:** the wording review is `REVIEW-20261006-s5p-stage7-note-wording.md`, two rounds with all findings
  resolved.

**Synchronization.** Before the sync, the standalone's head `ea15aee` (authored by Joseph, 2026-10-05) equalled
canonical `e55f6e9f`'s PET content, which is an ancestor of canonical `main`. It lacked the later canonical
`304b8bf0`, which restored PET qualifiers after a read-only accuracy review. The standalone was therefore stale, with
no unmerged direct edit. The sync made it byte-equal to canonical `cbd075e7` `docs/analysis-note/`, except the
standalone-only `.gitignore` and `AGENTS.md`. Seven files changed:
- the five s5p Stage-7 files;
- `PET_STUDY_SYNTHESIS.md` and `sec_pet_campaigns.tex`.

The paper sources were already identical, and the publication lane, which owns the paper's sync, raised no
objection.

**Remote heads** (`git ls-remote`, 2026-10-06T16:03Z):
- **Standalone:** `https://github.com/josephbaileyy/MINERvA-OmniFold-Analysis-Note` `main` =
  **`deeafae28441101a86925835b5c11e12bdd10e89`**, fast-forwarded from `ea15aee`. The primary checkout
  `../MINERvA-OmniFold-Analysis-Note` was clean and was fast-forwarded to it.
- **Canonical:** `https://github.com/josephbaileyy/MINERvA-OmniFold` `main` = **`cbd075e7…`** at the sync. The
  deliverable source is unchanged since. This record and its routing are committed on top. That commit's hash, which
  the record cannot contain, is `git log -1 -- docs/orchestration/DELIVERY-20261006-s5p-campaign-terminal.md`, and it
  is verified with `git branch -r --contains`.

## 6. Costed remaining requirements

1. **Measurement branch.** The limitation is scientific, not financial (Stage-2 exit §4). The prior dependence, about
   10–13% per coarse joint cell, is comparable to the generator differences a user must resolve (3.7–16%).
   - **Needed:** a new estimator or regularization method that meets the frozen T1 and T2 targets.
   - **Cost:** method development first, then a new frozen contract. No compute increment alone can meet them.
2. **External release of the inference family** (RELEASE-MANIFEST §7):
   - **package:** a sufficient-product package with an empty-checkout replay. This is analysis effort and a
     login-node test, with no allocation;
   - **archive:** an archive of about 2.3 GB of `/pscratch` products before purge: calibration 1.3 GB, power 207 MB,
     recovery 50 MB, predictions 0.78 GB, data and shift files about 7 MB;
   - **deposit and tag:** separately authorized acts.
3. **Reproduction tier C** (end-to-end regeneration of the calibration pseudo-experiments) has not been run. Its cost
   is about the production's: about 208 billed CPU node-h for the frozen ensembles. It is not required by the
   authorization, which asks for replay to be distinguished from regeneration.
4. **Paper-wide rows** other than R16 keep their recorded owners and dependencies. Examples are R15
   (BLOCKED-EXTERNAL, the unsent collaborator question) and R1–R14 and R17–R21, as reconciled.
5. **The PRD-class article** is owned by the publication lane under Joseph's 2026-10-06 approvals. Its headline
   wording takes the Stage-7 text verbatim.
