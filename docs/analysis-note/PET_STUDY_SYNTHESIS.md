# Completed PET studies in the deliverables

This bounded documentation update starts from canonical remote main
`4e7c20bb16418a7de0909ab034f49fe0a0751f29` and standalone remote main
`c589453dd482521faab552b639ac30568499da11`. One documentation owner checks the
manuscript against committed evidence and inspects the rendered sections. Existing
independent campaign reviews are reused only within their recorded scope; there is
no new independent campaign review. The task ends with consistent sources, three
successful builds in each repository, PDF inspection, synchronized pushed branches
and a canonical PR. The checking budget is a source/claim pass and a rendering/sync
pass, with focused repairs for observed defects. No scientific compute or campaign
review is reopened.

All evidence paths below are relative to the canonical repository at the pinned
commit. The bibliography links the three principal records (the confirmatory results, the final-design
decision record and the comparison report) at that snapshot, so the
standalone manuscript retains an evidence route.

| Manuscript content | Committed evidence | Required interpretation |
|---|---|---|
| Improvement table and no-coverage decision | `nd-unfolding/pet/improvement_campaign/confirm/CONFIRM_RESULTS.md`; `REPORT-20260922.md` sections 11–12; `REVIEW_DISPOSITION-20260924.md`; `REVIEW_DISPOSITION-ROUND2-20260925.md` | No frozen candidate at K*=10 qualifies; C at K=3 is not retroactively promoted; input changes are combined in B; stress mechanism and combined response-case identifiability are not established. |
| Finalists, B2, interval coverage and terminal result | `nd-unfolding/pet/final_design/REPORT-20260926.md`; `DECISION_RECORD-pet-final-design.md`; `REVIEW_DISPOSITION-DECISION-20261005.md`; ledger VL164–VL167 | `NO_ELIGIBLE_DESIGN`; B2 point-decided but statistically unresolved; aggregate over-coverage and low-acceptance under-coverage; C5 skipped and L128 coverage unmeasured. |
| Paired point-estimate results and figures | `nd-unfolding/pet/gbdt_comparison/REPORT-20261005.md`; `results/comparison.json`; `REVIEW_DISPOSITION-20261005.md`; ledger VL168 | Exploratory and conditional on banks; unadjusted intervals; specific HGB comparator; no uncertainty comparison, finalist ranking or adoption. Post-cycle-2 owner wording/design repairs were not re-reviewed. |
| Existing scalar synthesis consistency | `nd-unfolding/gbdt_model_dependence/README.md`; `definition.json`; `results/summary.json`; ledger VL163 | Production LightGBM, historical truth ratios and different functionals; no matched cross-setting variance scan, bias–variance tradeoff or new total uncertainty. Same-analyst checks are not a fresh independent review. |

The detailed account is `sec_pet_campaigns.tex`, included by `sec_pet.tex`. The
primer carries a short account and the paired-endpoint figure; the paper carries
a compact statement with report citations. Abstract and summaries preserve PET's
diagnostic/method-development status. The old real-data comparison remains
withdrawn. No study evidence, decision, threshold, ledger value or scientific code
is changed.

Two figure PDFs are copied byte-for-byte from the committed comparison:

- `results/figures/fig2_paired_differences.pdf` → `figures/pet_gbdt_paired_differences.pdf`.
- `results/figures/fig4_library_paired.pdf` → `figures/pet_gbdt_library_paired.pdf`.

The four existing GBDT synthesis figures were checked against their source PDFs
and are identical. The synthesis's rounded recovery, residual, interval and prior
statements agree with its source account and VL163. The manuscript now explicitly
distinguishes its LightGBM estimator and historical cellwise proxy from the PET
study's HGB comparator and normalized L1 recovery.

Build verification uses `bash build_all.sh` in each source directory, including
fresh-output, reference/citation and struck-value containment checks. Scientific
test suites are unaffected: this change contains only manuscript prose,
bibliography, documentation and copies of existing figures. Delivery heads are
reported with the PR after direct remote verification.

## Delivery checks

Both builds passed with 120-page note, 8-page primer and 5-page paper; no
unresolved references or citations remain. Existing unrelated font and layout
warnings persist. The bibliography URL overflow found on the first rendering
pass was repaired. The new tables, figures, scope text and bibliography were
visually inspected. Full extracted PDF text matches between repositories;
13 rendered pages match pixel-for-pixel: note 44, 58–62, 117–118; primer
3, 7–8; paper 3–4. All 111 corresponding tracked manuscript/figure files
match, excluding repository-specific instructions and ignore rules.
