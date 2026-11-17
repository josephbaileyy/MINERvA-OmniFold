# Fix requested by the director, 2026-11-16: which predictions the run-period falls are for (sec_fived16.tex, §10.4)

Not a cutdown row. From the director's cross-document check at paper `3d4d33144` and note `8342963c1`.

**Base:** `sec_fived16.tex:198` at `8342963c1`.

**Old:** "With the block, each prediction's total χ² is lower by ⟨pl-chi2fall-total-lo⟩–⟨pl-chi2fall-total-hi⟩% of its
value without it, and each shape-only χ² by ⟨pl-chi2fall-shape_only-lo⟩–⟨…-hi⟩% (Table tab:fived16-gen)."

**New:** the same, ending "…%, for the five predictions with NuWro and GiBUU corrected to CH (Tables tab:fived16-gen
and tab:fived16-gen-target)."

**Why this form.** The four keys are computed by `make_values_fived16.py` (the loop over `PRED` after `table4`) from
the five predictions with NuWro and GiBUU CH-corrected. Table `tab:fived16-gen` now prints those two on carbon, so
the sentence cited a table that does not give its numbers. The director offered two repairs: print the carbon
ranges from existing keys, or say the ranges are the CH comparison's and cite its table. The note's
`values_fived16.tex` has no key for the carbon ranges (the paper branch's `pl-chi2fall-b5-*` keys are not ported), and
no value may be typed, so the second repair is taken. No key, value or number changes.

**Meaning read** (the editor's own, not an independent model's).
(a) Does the sentence still say what it said, or less? It says the same falls and adds which predictions they are
for, which was true before and unstated. Nothing else in the sentence changes.
(b) Do antecedents and pointers hold? Table `tab:fived16-gen` gives both arms for GENIE CV, GENIE + MEC and Tune v1;
Table `tab:fived16-gen-target`'s rows "CH" give both arms for NuWro and GiBUU. Together they are the five
predictions the keys are computed from. The next sentence ("We infer from these falls …") refers to the same falls.

**Left for the director:** the Supplement prints the carbon ranges. The note now prints the CH ranges, labelled.
If the note should print carbon's instead, the paper's `pl-chi2fall-b5-*` keys need porting into the note's
generator, as the LL5D and T2A keys were.
