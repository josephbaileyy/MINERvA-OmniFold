# HANDOFF — July-16 talk, slide-feedback round 1 (2026-07-13)

> **STATUS 2026-07-14: ALL ITEMS COMPLETE.** Items 1–12 done and verified by
> headless render (35 slides, no JS errors); deck + dark figures pushed to the
> design project; scripts/figures/deck committed. Kept as a record of the
> feedback round and for the regen recipes below.

Continue in a fresh session. Deck = `docs/jul-16-presentation/design-talk/talk/index.html`
(local mirror of claude.ai/design project `61fbccfd-65d5-44bf-98c7-5831aa807b82`;
push back via DesignSync MCP: finalize_plan localDir=design-talk, writes
`["talk/index.html","talk/anims.js","talk/figures-dark/*.png"]`, then write_files
by localPath). Slide numbers below = deck-stage's 1-based "N / 34" counter.
User feedback quoted in the last user message of the previous session.

## Environment / regen recipe (critical)

- Plot env: `HOME=/global/homes/j/josephrb bash -c 'source setup_salloc_env.sh; ...'`
- Dark figures: run any make_figures.sh invocation with `TECHNOTE_DARK=1`
  (gated block at end of `technote_style.py`), copy PNGs to
  `design-talk/talk/figures-dark/`, then **restore canonical light outputs** —
  a backup tar of all pre-existing pngs/pdfs is at
  `/tmp/claude-112498/-pscratch-sd-j-josephrb-MINERvA-OmniFold/ad1257c5-448d-4099-b58e-8cea5bedbbd1/scratchpad/fig_backup.tgz`
  (untar from repo root; NOTE this session-scratchpad path may be cleaned —
  if gone, re-tar the same file set BEFORE running dark: all maxdepth-1
  *.png/*.pdf under 2d-unfolding, 3d-unfolding, 3d-unfolding/genie,
  nd-unfolding/products/5d, 2d-unfolding/uq/universe_stage2_MEFHC_full_matcorr_fluxfix).
- Note figures that changed at source (landscape, negweight, fig6_7): ALSO
  regenerate LIGHT (no env var) and let make_figures.sh's sync block copy the
  new PDFs into docs/analysis-note/figures/ (it syncs `-newer` by basename).
- Analysis note: already up to date (school session subtree-pulled today;
  `git diff bf83a1d:docs/analysis-note analysis-note/main` is empty).
- Headless verify: puppeteer-core + chrome-headless-shell installed in the
  session scratchpad (`scratchpad/shot.js` pattern); reinstall if scratchpad
  gone: `npm i puppeteer-core @puppeteer/browsers && npx @puppeteer/browsers
  install chrome-headless-shell@stable --path ./browsers`.

## DONE (edits made, NOT yet regenerated/verified unless noted)

1. **Slide 4 / note fig** — `3d-unfolding/plot_minerva_landscape.py`: single
   "this work" star at 5D (pT,p∥,Eavail,q3,W), yticks 1–5, legend one entry,
   docstring updated. NEEDS: regen light + dark, sync note PDF.
2. **Slide 22 / note fig** — `2d-unfolding/plot_negweight_ratio.py`: color
   window ±15% → ±5% (deviations are ~1–2% RMS; worst bin −12.6% saturates
   into extend arrows). NEEDS: regen light, sync note PDF (backup slide uses
   white plate → no dark needed).
3. **Slide 11 + all dark heatmaps** — `technote_style.py` TECHNOTE_DARK block:
   new `DARK_DIV_CMAP` (bright blue → dark #20233A center → bright red),
   swapped for RdBu_r/coolwarm/bwr on `ax.images` and colormapped collections
   at savefig; colormapped collections are now protected from the facecolor
   fixup. NEEDS: regen dark for `MEFHC_5iter_pull_full`,
   `eavail_marginal_vs_paper_pull_full`, `excess_eavail_W` (all RdBu_r).
4. **Slide 12 / note fig** — `2d-unfolding/uq/plot_uncertainty_fig6_7_style.py`:
   (a) ML line decision now joint across pt+pz (was per-axis auto threshold →
   pz had ML, pt didn't — the user-reported imbalance); (b) new `--paper-root`
   option overlays "Published total" (dash-dot) computed from the release's
   TotalCovariance + pt_pl_cross_section (ordering verified: paper global id
   = ipt*16+ipz = this script's reported.ravel(C)). NEEDS: run once WITH
   `--paper-root 2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root`
   (answers the user's "compare to paper?" question: yes — one overlay line),
   regen light+dark, sync note PDFs, VERIFY the overlay ≈ our Total (~7%)
   before trusting (fresh code, never run!).

## TODO (not started)

5. **Slide 1**: title slide meta "Graduate researcher" → "Stanford undergrad
   researcher" (in `talk/index.html` cover slide; also speaker notes say
   "graduate researcher").
6. **Slide 7 (A3 anim)**: truth-zone histograms clip the panel top —
   in `talk/anims.js` specA3, hScale is fixed 7.2 with tBase=380 (panel top
   y=20). Make the scale dynamic: after precomputing A/S weight snapshots,
   peak = max over makeHist(simT,A[k]) & makeHist(simR,S[k]) & datH/datHT;
   hScale = min(7.2, ~330/peak). Same scale for both zones.
7. **Slide 10 (money)**: fig13 (two stacked grids) is illegibly small next to
   the stat rail. Swap to the pT-slices-only reproduction:
   `cd 2d-unfolding && TECHNOTE_DARK=1 python plot_2d_paper_comparison.py`
   → dark `MEFHC_5iter_xsec_paper_pt_slices.png` → figures-dark, and point the
   money slide's img at it (keep stat rail + caption; maybe keep fig13 as an
   extra backup slide).
8. **Slide 19 (outlook)**: split into TWO slides — PET point-cloud slide +
   FPS slide — so each figure gets full width. The white `pet_event_displays`
   is harsh on dark: no generating script exists in the repo (ad-hoc product).
   Either write `nd-unfolding/pet/plot_event_displays.py` from
   `nd-unfolding/of_inputs_pc.npz` (5.9 GB, exists; light+dark, fixes the
   note's missing-script gap too — add to make_figures.sh) or keep white
   plate and note it in KNOWN_ISSUES.md as "pet_event_displays has no script".
9. **Slide 25 (B3)**: left figure `classifier_calibration.png` shows the OLD
   subsampled sklearn-MLP that underfit to a constant — the note REPLACED it
   with the validated full Keras-MLP comparison `nn_vs_gbdt_full` (see
   sec_validation.tex line ~92 and the \jrb reply). Swap B3's left img to
   `../uploads/claude-design-package/figures/`... nn_vs_gbdt_full.png is NOT
   in the design package uploads — add it to figures-dark (regen dark via
   `cd nd-unfolding && TECHNOTE_DARK=1 python plot_nn_vs_gbdt_full.py --gbdt
   res_lgbm_3d.npz --nn res_nn_3d.npz --out nn_vs_gbdt_full.png`) or push the
   light PNG into the project. Rewrite B3 caption + speaker notes (currently
   claim "the NN collapses to a constant — why the GBDT carries the analysis"
   — that claim is retired; new message: independent Keras-MLP cross-check
   agrees, ratio 1.0078).
10. **Slide 31 (B7b, eavailW_band)**: figure doesn't fit the slide well —
    inspect `figures-quarantined-backup-only/eavailW_band.png` aspect; likely
    fix = drop the fig-caption to one short line and let the panel take the
    full content height, or crop/split panels. Keep the PRELIM tag.
11. **Regen batch**: one background run regenerating (dark): landscape,
    pull_full, marginal pull, excess, fig6_7 pt+pz (with --paper-root),
    pt_slices, nn_vs_gbdt_full; (light, for the note): landscape,
    negweight_ratio_2d, fig6_7 pt+pz; then restore-from-tar the rest,
    copy darks into figures-dark/.
12. **Verify** headless screenshots (esp. slides 4, 7, 10, 11, 12, 19/20, 25,
    31 in NEW numbering — splitting slide 19 shifts backups by +1!). Update
    any stale slide-number references in captions/notes (B6b χ² backup, B7).
13. **Push** updated index.html + anims.js + figures-dark to the design
    project (plan may need `talk/figures-dark/nn_vs_gbdt_full.png` etc. —
    the existing plan glob covers talk/figures-dark/*.png; a NEW finalize_plan
    is required per session).
14. **Commit** (user allows direct-to-main when asked): technote_style.py,
    plot script fixes, design-talk/, COMPARISON.md, this handoff. Ask user or
    just do it if they say so.

## Numbers guardrails

values.tex is the source of truth (χ² distances 3.66 paper / 1.48 combined,
with no shared-data cross-covariance and therefore no calibrated GoF claim;
6.87% vs 6.86%; 1.011/1.006/94.1%; same-ensemble mean-|r| 0.794 vs 0.798 as a
Gaussianity diagnostic, not coverage; iter 0.026%; NN/GBDT 1.0078; descriptive
C2ST AUC 0.535→0.501 with no calibrated p-value or equivalence claim). N-D
covariance significances stay withheld (quarantine).
Landscape claim of 5D = central-value dimensionality, fine per presentation
rule in ND_OMNIFOLD_STATUS.md.
