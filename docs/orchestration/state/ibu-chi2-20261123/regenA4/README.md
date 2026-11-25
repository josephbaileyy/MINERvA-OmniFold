# Regeneration A4: the note's figures on the paper's pT edges (2026-11-25)

**By** the `ibu-chi-squared-issue` session. It is part of the chain in [`../README.md`](../README.md).
- **Amendment:** [`AMENDMENT-A4.txt`](AMENDMENT-A4.txt), committed at 63c9ec46 before any run.
- **GO:** the director's.
- **The stop after OLD:** [`STOP.md`](STOP.md).
- **Contents:** A4 E for six figures (pull_full, the three tension figures, the two slice figures), and Fig. 2
  (xsec_proj_pt/pz) under [`AMENDMENT-A4b.txt`](AMENDMENT-A4b.txt), committed at 67fe84bd before its run. See
  "Fig. 2 (A4b)" below.

## How it ran

All on this laptop, at 0 node-h, with no NERSC connection.
1. **Step 1**, TIER2-ARGV-EQUAL :: PASS ([`receipts/step1_tier2_argv_equal.out`](receipts/step1_tier2_argv_equal.out)).
2. **Step 2, OLD:** fig2 failed; see STOP.md.
3. **Gate:** the six passed their controls. The director then gave a GO for E on those six.
4. **Step 3, E** ([`out/e/steps.log`](out/e/steps.log)): every step rc 0.
   - The runner cannot skip a step without changing its bytes, so it ran unchanged, fig2 included.
   - fig2's E output is **not a reading**. It is kept in [`out/e_fig2_not_a_reading/`](out/e_fig2_not_a_reading/).
     **A4b's E reading supersedes it.** The two are EQUAL-BUT-DATE.
5. **Step 4,** controls and shas ([`receipts/controls.out`](receipts/controls.out)). The script ends in A4-CONTROLS :: FAIL,
   for fig2's missing OLD files only. For the six, every control passes:
   - C-OLD: EQUAL-BUT-DATE ×4 (pull_full and tension ×3);
   - C-SL-a: EQUAL-BUT-DATE ×2;
   - C-SL-b: BYTE-EQUAL ×2.
6. **Step 5:** [`a4_readout.py`](a4_readout.py) on both inputs → [`out/readout_old.json`](out/readout_old.json) and
   [`out/readout_e.json`](out/readout_e.json).

**Housekeeping:**
- **Environment:** A4_VENV was unset for both runs ([`receipts/prerun.txt`](receipts/prerun.txt),
  [`receipts/prerun_e.txt`](receipts/prerun_e.txt)).
- **C-PINS:** equal before OLD, before E and after E. Every pin equals the amendment's.
- **W:** 06893b0a, porcelain 0 throughout ([`receipts/postrun_W.txt`](receipts/postrun_W.txt)).
- **E's stamp strip:** removed only the stamp ("MINERvA ME FHC, 1.06×10^21 POT"), 2724 pixels, all inside its box.
  This is the same as on OLD.

## Figures for journal-editor, by sha256

| figure | installed (our edges) | paper's edges (E) |
|---|---|---|
| MEFHC_5iter_pull_full.pdf | 9335a3e3037320c6bb5a0e3d0ad61ac7709c693633ba9c5a1265e61c38c2501e | 8787db1e91688b4faa53088e0ef1f304fead8ff6d4de907e368efbab49bd884c |
| MEFHC_5iter_xsec_paper_pt_slices.pdf | 58e4d16ad6bc68f7bd17bae8d315b99ece6d66b821715d403120e0d6548357a2 | 9fca64a7779ce4f913325b3e551a2b3653fa09e47748ac9bb5608dcb0a0eee8b |
| MEFHC_5iter_xsec_paper_pz_slices.pdf | 4216003cfe47d376b97a3a32575e5fa00342e7528bfb1d2e8e647e9ea9f620b0 | 4d56eb9b5033b855a9c9ea0f83a8829bffccd5ae6f0f6def563b04bfe6ab3bb1 |
| tension_spectrum.pdf | 98d7ce2c9765275be579ef8345fde17f50a8b24b0e2f26846475d6998a163661 | f25ee7d28384cfac6f77dd35844db86ffa7ad31d5b99ab1586d48fdb3aa9772f |
| tension_chi2_map.pdf | 4f18c35be762355f16410bb8798ceae8f303e640e33bda985c90dbfdee23236a | affa1fefae38443f12d28ea938149d57943a83f309210e20810a448966808427 |
| tension_mode_maps.pdf | f4d8a4197aa0318fd9704ab7c0d0011c9a85425e12398966bb552a1b79c80412 | fe405d2fcab8f55e74c2ab37ff42dd83421fc0352f58db77d9c9ba1805b1869d |
| MEFHC_5iter_xsec_proj_pt.pdf (A4b) | d27075c220081054caf51fb6130fe3a671e9dc0dacfb1a97469b3d07829f63af | 82c0d63fc612b196d5a1abb0a187a0392f2ea791ac49011f7558ea94826cdf00 |
| MEFHC_5iter_xsec_proj_pz.pdf (A4b) | caa9286bfec8e7f2b6d6dd06fda6d5fc9f0b8f1c7c95d4bacc290048726b4745 | 4d73ab9210fabf569d126d196ef205b7030257f66996a349657f5615d0a34a1d |

- **E files:** in [`out/e/`](out/e/), and Fig. 2's in [`out/a4b/e/`](out/a4b/e/). The slices' markers layer, before the strip, is beside them as
  `*_markers_layer.pdf`.
- **OLD reruns:** in [`out/old/`](out/old/).

## Caption numbers (a4_readout.py)

The caption wording is Joseph's. These are the numbers.

**tension_mode_maps** (appC:22–23: "three of the six … in panels (a), (b), and (d), concentrate at the highest p∥").
- **Definition:** the panels are the figure's six modes, in its order. "Share" is the fraction of Σu² in p∥ ≥ 20 GeV/c, the
  two highest p∥ bins.
- **Control:** OLD reproduces the caption. Exactly (a), (b) and (d) have a share above one half.

| panel | OLD χ² contribution | OLD share | E χ² contribution | E share |
|---|---|---|---|---|
| (a) | 22.53 | 0.843 | 19.31 | 0.843 |
| (b) | 14.27 | 0.992 | 16.25 | 0.000 |
| (c) | 13.30 | 0.000 | 13.21 | 0.974 |
| (d) | 13.22 | 1.000 | 12.20 | 0.992 |
| (e) | 13.01 | 0.000 | 11.58 | 0.946 |
| (f) | 12.24 | 0.000 | 11.26 | 1.000 |

On the paper's edges, **five of the six** concentrate at the highest p∥: (a), (c), (d), (e) and (f). The mode that was
(c) on OLD, peaking at p∥ bin 9 and pT bin 4, moves up to (b). The order changes because the modes are ranked by our
residual's contribution, and the residual changes with the pT edges.

**Slices** (appC:30: "In all 14 pT slices, the OmniFold points move toward the published values relative to the Tune v1
prior"; appC:37: "In all 16 p∥ slices …").
- **Definition:** per slice, over its reported cells, D = Σ((x − published)/σ_stat,published)² for ours and for the prior.
  A slice is "toward" when D_ours < D_prior.
- **OLD:** 14/14 pT slices and 16/16 p∥ slices are toward.
- **E:** also 14/14 and 16/16.
- **D_ours / D_prior, E:** 0.0082–0.0903 over the pT slices and 0.0076–0.1706 over the p∥ slices. On OLD it is
  0.0082–0.1150 and 0.0073–0.1739.

**Each slice panel's printed χ²/n** (ours against the prior, from the drawn texts in
[`out/e/captures_texts/`](out/e/captures_texts/)):
- **pT slices:** the seven lowest change. 1890.6/16 → 2177.2/16, 3404.9 → 3183.1, 3785.0 → 3785.0, 3947.5 → 3727.0,
  2614.2 → 2835.2, 2819.5 → 3063.8 and 5084.1 → 4840.5. The seven above 0.55 GeV/c are unchanged.
- **p∥ slices:** every value moves by at most 16.4 in χ², 0.22 % at most relative. The full lists are in the readout JSON.

## Fig. 2 (A4b)

[`AMENDMENT-A4b.txt`](AMENDMENT-A4b.txt) runs OLD with the code that made the installed file, and E on main.
- **The installing commit:** 434fc800b, whose parent is 177c549c2, the round's recorded base.
- **The code:** every chain tool tree is identical there and at main. Only `2d-unfolding/` differs, through #1318 and
  #1328.
- **What the change combines:** the OLD-to-E change in Fig. 2 combines the pT-edge move with #1318's fix that places
  the published points on the release axis. The installed Fig. 2 drew them at our pT bin centres. This is as in A2.

**The OLD tree.** A `git archive` of 434fc800b, taken without nd-unfolding and the other orchestration records
because the disk was at 98 %. It was extracted in the scratchpad (225 MB, tree 2a655c1a) and deleted after the run.
- The blob check ([`receipts/a4b_tree_check.out`](receipts/a4b_tree_check.out)): 389 files in `2d-unfolding/`,
  `technote_style.py` and the chain's tool trees, each sha256 equal to its blob, with no DIFFER.
- A first invocation of the check, in zsh, was vacuous:
  - the loop variable `path` is tied to `$PATH` there, so every command was "not found";
  - every comparison was empty = empty, so every line read "ok";
  - its output is kept as [`receipts/a4b_tree_check_attempt1_vacuous_zsh.out`](receipts/a4b_tree_check_attempt1_vacuous_zsh.out);
  - the declared command was then run in bash, with an empty comparison counting as DIFFER. Steps 1–3 ran after it.

**Run** ([`receipts/a4b_prerun.txt`](receipts/a4b_prerun.txt)):
- A4_VENV was unset. The runner was unchanged (2d5246a1).
- **Step 1, OLD** in the extraction, and **step 2, E** at main W 06893b0a: every step rc 0
  ([`out/a4b/old/steps.log`](out/a4b/old/steps.log), [`out/a4b/e/steps.log`](out/a4b/e/steps.log)).
- Only fig2's outputs are A4b's.
- **C-PINS:** equal before and after.

**Controls** ([`receipts/a4b_controls.out`](receipts/a4b_controls.out)), A4B-CONTROLS :: PASS:
- **C4b-OLD:** xsec_proj_pt and _pz are EQUAL-BUT-DATE against the installed d27075c2 / caa9286b.
- **C4b-PRE:** on both grids and in both projections, the edge-fix pre-check flagged exactly the declared
  'Tune v1: published prediction' line and nothing in the ratio panel, and the check after the fix flagged nothing.
  The edges recorded are 0.07 / 0.33 / 0.47 on OLD and 0.075 / 0.325 / 0.475 on E.
- **Information:** E is EQUAL-BUT-DATE against A4's E run of fig2, so the draw is deterministic.

**Cross-check with A2.** The figure's lower-panel ratios, ours / published, are recorded in
`compose_fig2_pubratio.json`'s `ratio_to_published`. On each grid they equal A2's projection-ratio readout to at most
4.4e-16. The lowest pT bin is 0.9675 on OLD and 1.041 on E; the highest is 1.0372 on both.

## Not in this record

- **eavail_marginal_vs_paper_pull_full** (appC:214): in regenA/README.md's Deferred tidy-up section.

[`SHA256SUMS`](SHA256SUMS) covers this directory. Files named `*.out` and `*.log` are committed with `git add -f`.
