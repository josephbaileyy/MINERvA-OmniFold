# r22 Step 4: two-direction review of T1, T2, T4, T5

**Reviewer:** an independent, read-only agent (Claude), 2026-10-31.
**Compared:** base `4121f185d60d` against the worktree `wt-con`, using `git diff 4121f185d60d -- docs/analysis-note/`.
Only `sec_results.tex`, `sec_eavailw.tex` and `sec_fived16.tex` differ.

**Sources read:**
- STEP4-PLAN.md §1–3, `step4/ledger.md`, `fig-restyle-20261031/CAPTION-FIXES.md`;
- DECISION-20261031-joseph-chi2-table-option-b.md;
- `2d-unfolding/compare_to_models.py`, `technote_style.py`;
- `3d-unfolding/genie/overlay_eavailW_band.py`, `make_figures.sh:43,82,235,302`;
- `MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h` (blob `04906da58fe1` at base, as the plan pins) and
  `runEventLoopOmniFold.cpp`;
- `values_fived16.tex`, and the section text of `sec_eavailw.tex` and `sec_fived16.tex`.

No source file outside `docs/analysis-note/` differs from the base.

## Measurements made

- **T1.**
  - `compare_to_models.py:156-163`: the published data are drawn `color="k"`, this measurement `C0` dashed, and model j
    `C{j+1}`. The default model list (`:88`) is Tune v1 only, so Tune v1 is `C1`, and `make_figures.sh:43` passes no
    `--model`.
  - `technote_style.py:59,85,99`: the cycle is `GEN_PALETTE` first, and `GEN_PALETTE[1]="#4C72B0"`. `:52` labels it
    "blue (GENIE + MINERvA Tune v1)".
  - The restyle palette (`:162`) maps it to `#5B8ED6`, which is also blue.
  - The pinned `figures/model_comp_projections.pdf` has sha256 `2c39fe21…f8d8`, which equals the `make_figures.sh:235`
    pin. Its content streams hold the colour operators `#C44E52` RG×4, `#4C72B0` RG×2 and `#4C72B0` rg×4. There is no
    orange.
- **T2.**
  - `overlay_eavailW_band.py`: `c.Divide(2,1)`. Pad 1 (left) is dσ/dE_avail and pad 2 (right) is dσ/dW. The data are
    drawn with `Draw("P")` and each generator with `"HIST P SAME"`. No fill, envelope or band is drawn.
  - The corner is a 2D sum (`np.outer(eav_hi, w_hi)`, `:88-92`).
  - `make_figures.sh:82` passes all four generators, GiBUU included.
  - The plotted histograms drop the `[3,100]` catch bin on both axes (`mk_th1`, `:125-133`). So the corner's largest
    cell, E_avail>3, W>3, is not drawn at all. This supports "which the projections do not resolve".
  - Section numbers (`sec_eavailw.tex:135,146`):
    - corner data/gen: 1.14, 1.14, 1.16 and 1.61;
    - integrated: 1.11, 1.07, 1.15 and 1.39;
    - GENIE and NuWro corner ratios exceed their integrated ratios by 1–7%, against 16% for GiBUU;
    - 2p2h: "essentially unchanged ($1.142\to1.139$)", "since it populates low $W$".
  - The comparison words follow from these numbers:
    - "GENIE and NuWro by about their overall normalization shortfall" is supported: their corner shortfalls of 14–16%
      sit within 1–7% of their integrated shortfalls of 7–15%.
    - "GiBUU by more" is supported in both readings: more than its own integrated shortfall (1.61 against 1.39), and
      more than the others.
- **T4.**
  - `CVUniverse.h:267-282` `GetHadronAngleTrue()` sums `mc_FSPartPx/Py/Pz` over every `mc_FSPart` entry except PDG ±13
    (muons) and ±12, ±14, ±16 (neutrinos). It returns `acos(sz/|p|)`, the polar angle about +z, or −9999 if |p| = 0.
  - `runEventLoopOmniFold.cpp:594` and `:1145` store it as `MC_hadangle`. The comments at `:438` and `:979` read
    "truth hadronic-system angle (rad)".
- **T5.** Every cell was checked against the base row, macro by macro (table below). `values_fived16.tex` has no
  `-nocresp-ndf` macro. The base printed `-total-ndf` as the "without C_resp" ndf, and so does the new table. The ndf
  values are 16 (shape-only 15) for GENIE CV, GENIE+MEC, NuWro and Tune v1, and 8 (shape-only 7) for GiBUU. These agree
  with the block labels "All 16 cells" and "8-cell subset", and with the body's "the 8 cells below
  $\pPar=\fvval{h2-mid-pz}$" (`h2-mid-pz` = 4.5, which matches the decision's "p∥ < 4.5 GeV/c").

| row | base col 2 (χ²/ndf) | new cols 2, 3 | base col 3 (shape) | new cols 4, 5 | base col 4 (no C_resp) | new cols 6, 7 | same? |
|---|---|---|---|---|---|---|---|
| gcv | total-chi2 / total-ndf | total-chi2, total-ndf | shape_only-chi2 / shape_only-ndf | shape_only-chi2, shape_only-ndf | nocresp-chi2 / total-ndf | nocresp-chi2, total-ndf | yes |
| gmec | as gcv | as gcv | as gcv | as gcv | as gcv | as gcv | yes |
| nuwro | as gcv | as gcv | as gcv | as gcv | as gcv | as gcv | yes |
| tune | as gcv | as gcv | as gcv | as gcv | as gcv | as gcv | yes |
| gibuu | as gcv | as gcv | as gcv | as gcv | as gcv | as gcv | yes (moved to the 8-cell block, as declared) |

No value moved between columns or rows. Every row keeps its own prefix (`g-gcv-`, `g-gmec-`, `g-nuwro-`, `g-tune-`,
`g-gibuu-`).

## Findings

### F1: T4, `sec_eavailw.tex`, "the polar angle of the summed final-state hadronic momentum, with muons and neutrinos excluded."

- **Direction:** UNSUPPORTED (minor).
- **Base:** "the proton and pion multiplicities and the leading-hadron angle."
- **New:** "the proton and pion multiplicities and the polar angle of the summed final-state hadronic momentum, with
  muons and neutrinos excluded."
- **Why:**
  - "Hadronic" asserts that every summed particle is a hadron. The code does not test for hadrons. It sums every
    `mc_FSPart` entry that is not a muon or a neutrino.
  - So any final-state photon (PDG 22), electron or other non-hadron in the list enters the sum. The same file's
    `GetEAvailableTrue()` (`CVUniverse.h:368`) reads PDG 22 from this very list, so the code expects photons to be
    present.
  - The new wording follows the code comment's "hadron 3-momentum" and the plan's "hadron momentum". But the code
    defines the quantity by exclusion, not by species. "Hadronic … with muons and neutrinos excluded" also reads as if
    muons and neutrinos were a subset of hadrons.
  - The correction of "leading-hadron" itself is right: no leading particle is selected, and the vector sum is taken.
- **Fix (no number added):** "…and the polar angle of the summed momentum of all final-state particles other than
  muons and neutrinos." If the plan's wording must be kept, add "(photons included)" only if a source states it. The
  safe form is the exclusion-only wording.

### F2: T5, `sec_fived16.tex`, `tab:fived16-gen` header: `\multicolumn{2}{c}{$C_{\mathrm{total}}+C_{\mathrm{resp}}+V_g$} & \multicolumn{2}{c}{shape-only} & \multicolumn{2}{c}{without $C_{\mathrm{resp}}$}`

- **Direction:** AMBIGUOUS (new with the restructure).
- **Base:** `prediction & $\chi^2$ and ndf & shape-only & without $C_{\mathrm{resp}}$`.
- **New:** the three group headers above, over `$\chi^2$ & ndf` pairs.
- **Why:**
  - Two of the three group headers name a covariance ("C_total+C_resp+V_g", "without C_resp"). Set in parallel with
    them, "shape-only" reads as a third covariance choice, as if the shape-only χ² were not against
    C_total+C_resp+V_g.
  - The body (`sec_fived16.tex`, "Each gives the $\chi^2$ against … and the shape-only $\chi^2$, with the normalization
    free") and the Option B paper caption ("using C_total + C_resp + V_g … Shape-only χ² frees the normalization")
    both say that shape-only uses the same covariance with the normalization freed.
  - The base header named no covariance, so it did not suggest this split.
- **Fix:** name the first group by what distinguishes it, for example `\multicolumn{2}{c}{full}` or
  `\multicolumn{2}{c}{normalization included}`, and leave the covariance to the caption. Alternatively, keep the header
  and make the caption say "with the shape-only $\chi^2$ and its ndf, against the same covariance, beside it".

### F3: T5, `sec_fived16.tex`, caption: "with the shape-only $\chi^2$ beside it; the last two columns give the $\chi^2$ without the response block, against $C_{\mathrm{total}}+V_g$, and its ndf."

- **Direction:** AMBIGUOUS (minor).
- **Base:** "…with the shape-only $\chi^2$ beside it; the last column gives the $\chi^2$ without the response block,
  against $C_{\mathrm{total}}+V_g$."
- **New:** as quoted.
- **Why:**
  - The caption is true of the new table, and nothing from the base is lost.
  - It now accounts for the ndf column of the last pair ("and its ndf") but not for the shape-only ndf column, which is
    new as a separate column. A reader who counts columns from the caption gets five, not six (χ², ndf, shape-only χ²,
    then the last two).
  - The base had the same gap inside one cell ("χ²/ndf"), where it did not matter.
- **Fix:** "…with the shape-only $\chi^2$ and its ndf beside it; the last two columns give…". This can be combined with
  F2's second fix.

## Not counted as findings

- **The plan and the ledger disagree on T5's caption.** STEP4-PLAN.md §1 says the note keeps "its own caption, which
  stays true of the new structure". That was not so: the base's "the last column gives" would be false of a
  seven-column table. Ledger row T5-b changes the caption, which is necessary, and the change is correct. The plan's
  line should be reconciled in STEP4-NOTE-REPORT.md.
- **Two Fig. 25 gaps carried over unchanged from the base.**
  - The caption states "every generator lies below the data" without the section's "These are central-value ratios".
  - It gives "GiBUU by more" without the section's explanation, GiBUU's E_ν ≈ 20 GeV sample limit, after which every
    ratio lies close to its integrated ratio (`sec_eavailw.tex:137`).
  - The new pointer to §`sec:eavailw-band` leads the reader to both, and adding them here would be a register change
    outside this round. I record them only.
- **T2 old to new:** every base fact still prints at the same strength:
  - the four generators;
  - "GENIE and NuWro flux-corrected, \S\ref{sec:3d-models}";
  - the corner claim with both comparison clauses;
  - the 2p2h clause and its reason.
  - The only changes are the declared ones: "band", the attribution, and "unchanged" → "essentially unchanged".
- **T1 old to new:** only the colour word changes. "(dashed)" for this measurement (`C0`, red dashed) and "(black)" for
  the published data stay true.

## Verdict per change

- **T1:** OK.
- **T2:** OK.
- **T4:** fix (F1). Replace "hadronic momentum, with muons and neutrinos excluded" with "momentum of all final-state
  particles other than muons and neutrinos".
- **T5:** fix (F2, F3). Rename the first column-group header so that "shape-only" does not read as a covariance choice,
  and say "the shape-only $\chi^2$ and its ndf" in the caption. Every macro is correct.
