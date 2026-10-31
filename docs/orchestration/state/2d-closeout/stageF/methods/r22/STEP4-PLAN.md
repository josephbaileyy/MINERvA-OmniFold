# r22 Step 4, the note's truth round: plan and adoption rule

**Started** by the director on 2026-10-31, after #588 and #589. This file is committed before any text is written. The
base is origin/main `4121f185d60d`.

**This is not a register round.**
- Its changes correct what the note says, or carry out a decision Joseph has made. They do not change its register.
- So they are adopted on truth checks (§3), not on rater preference.
- No P2N or P1N run is made.
- The round does not count toward the stopping rule (STEP3-PLAN.md §5), and the note's score stays at 3.278, as
  measured on Step 3's adopted text. §5 records the director's option to amend this.

## 1. The changes

Each change is one ledger row or more in `step4/ledger.md`. Its before-text is the base's exact source text.

| id | file | what | authority | source of the corrected fact |
|---|---|---|---|---|
| T1 | `sec_results.tex`, `fig:model` caption | "MINERvA Tune v1 (orange)" → "(blue)" | DECISION-20261031 item 4 (#574); the director's ruling of 2026-10-31 | `fig-restyle-20261031/CAPTION-FIXES.md`: the producer draws Tune v1 as `C1` = `#4C72B0`, and the pinned PDF strokes only `#C44E52` and `#4C72B0` |
| T2 | `sec_eavailw.tex`, `fig:eavailWband` caption | the corner statement attributed to §`sec:eavailw-band`, not to the panels; "band" replaced; "unchanged" → "essentially unchanged" | as T1 | CAPTION-FIXES.md: `overlay_eavailW_band.py` draws two 1D projections with no band; the corner ratios and "essentially unchanged ($1.142\to1.139$)" print in the section |
| T3 | `sec_results.tex`, `fig:modelmaps` caption | "the panels have no printed titles" removed or reworded | the director's ruling 6 in `fig-restyle-20261031/DECLARATION.md` §6 | made **only with R**: the restyle's panel labels make the sentence stale. Without R the sentence stays true and T3 is not made |
| T4 | `sec_eavailw.tex` | "the leading-hadron angle" → the angle the code stores | review B07–B11 of Step 3 (an older inaccuracy) | `MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:267-268` at `4121f185d60d` (blob `04906da58fe1`): "Polar angle (rad) of the summed final-state hadron 3-momentum wrt the +z beam axis (muon + neutrinos dropped)"; `runEventLoopOmniFold.cpp:438`: "truth hadronic-system angle (rad)" |
| T5 | `sec_fived16.tex`, `tab:fived16-gen` | the structure of Option B | `DECISION-20261031-joseph-chi2-table-option-b.md` (#581) item 1 | the values macros, unchanged |
| R | `make_figures.sh`, `re2-integration/ledger.tsv`, `fig-restyle-20261031/DIGESTS.tsv` | the restyled Figs. 7–14 installed | `fig-restyle-20261031/DECLARATION.md` §5 and BINDING.md | made **only if Joseph approves the restyle** before this round's build |

**T4's wording.** It names what the code computes: the polar angle of the summed final-state hadron momentum, with
muons and neutrinos excluded. The writer may shorten it, but not past the code comment's meaning. The ledger row gets
an `L:` probe of `CVUniverse.h` at the pinned blob, under the director's rule for code homes: a tracked file that states
the fact in plain words.

**T5's structure (Option B, as decided):**
- **Rows:** grouped under "All 16 cells" (GENIE 2.12.10 CV, GENIE 2.12.10 + Valencia MEC, NuWro 21.09 and MINERvA
  Tune v1) and under an "8-cell subset" block for GiBUU 2019.
  - The block's label states the subset with the macro the note already uses, `$\pPar<\fvval{h2-mid-pz}$~GeV/$c$`
    (`sec_fived16.tex:182`), so no number is typed.
- **Columns:** χ², ndf, shape-only χ², ndf. No χ²/ndf ratio is printed.
  - The note's own last column, χ² without $C_{\mathrm{resp}}$ (Step 3, B09-g-09), stays as a χ² column. Its ndf is
    the total's.
- **Kept:** the note keeps its precision (the `-chi2` macros, not the paper's `-chi2int`) and its own caption, which
  stays true of the new structure.
- **Probe:** every number printed in the table is its macro. The table's source may hold no digit outside a `\fvval{}`
  argument, apart from the structural "16" and "8" of the block labels. The rendered table's numbers must equal the
  values file's for those macros.

## 2. What may not change

- **Nothing outside the rows of §1.** Every other note source is byte-identical to the base (`step4/check_ledger.py`,
  a wrapper of `step2/check_ledger.py`, with base `4121f185d60d` and this round's ledger).
- **The values files** (`values*.tex`), every number, and the paper.
- **The held sentences of Step 3** (`step3/held.tsv`) print exactly. `tools/check_held_note.py` runs on this round's
  pieces.
- **No register rewording** rides along with a truth fix.

## 3. Adoption (per change)

A change is adopted when all four hold:
1. **The ledger:** its rows' probes hold, with 0 failures, and every changed base sentence is named in a row.
2. **The two-direction review** by an independent read-only agent finds no loss and no addition beyond the change's
   declared correction.
3. **agy's targeted read.** agy sees each before/after pair and is asked to list every difference in meaning.
   - The change passes if the only difference listed is its declared correction.
   - A planted control, an extra one-word change of meaning in a copy, must be listed.
   - agy reads each pair alone, so it is not told which correction is intended.
4. **The build and all gates:** `build_all.sh`, the record-checks.yml steps with BASE=origin/main, and for T5 its
   number probe. For R, also DECLARATION.md §5's checks:
   - the install's digests;
   - `DIGESTS.tsv` and the re-pointed G rows;
   - the primer;
   - the re-crop as a record.

A change that fails keeps its base text, and its failure is reported unrepaired. T3 is made only with R.

## 4. Outputs

`step4/`, holding:
- `ledger.md`;
- `check_ledger.py`;
- `review.md`;
- `agy/`;
- the pieces cut from a build of the committed tree (as STEP3-PLAN §3 item 7);
- `STEP4-NOTE-REPORT.md`.

## 5. Open to the director before any text

The choice that this round makes no rater runs, and does not count toward the stopping rule, is this plan's own.
- **If the director wants the note's score re-measured on the changed pieces:** STEP3-PLAN's sol2 P1N ×3, on
  codex-school.
- **The pieces that change:**
  - B05 (`sec_results.tex`: T1 and T3);
  - B07 (`sec_eavailw.tex`: T2 and T4);
  - B09 (`sec_fived16.tex`: T5).
  That would be 9 sol calls, for the record only, not for adoption.
