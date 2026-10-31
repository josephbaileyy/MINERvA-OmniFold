# Independent PRD-reviewer consult on the χ² tables (gpt-6-astra, 2026-10-31)

**By** the paper-tighten lane, as director, under `DECISION-20261031-joseph-rater-account-figures-chi2-consult.md`
item 3. **It rules nothing:** the options go to Joseph.

- **Model:** `gpt-6-astra`, reasoning effort high, on account codex-school, read-only.
- **Inputs:** listed by sha256 in `INPUTS.SHA256SUMS`. They are the paper's text built at `main`, the note Table 16
  excerpt, the 2026-10-27 χ² format decision, and the figure diagnosis's finding.
- **Prompt and answer:** `prompt.txt` and `answer.txt`, verbatim.

**Its recommendation (Option B):**
- put GiBUU in its own labelled block, "8-cell subset: p∥ < 4.5 GeV/c";
- print χ² and ndf in separate columns, with no χ²/ndf ratio;
- replace the caption rather than lengthen it.

The alternative (Option A) is about 24 words appended to the caption. It judges that A leaves the quick-scan misreading.
It also judges that printing χ²/ndf would likely worsen the misreading.

**The director checked** that the consult's table entries equal the paper's printed Table IV at `main`: 109/16, 272/16,
188/16, 58/8 and 330/16, and shape-only 109/15, 258/15, 188/15, 28/7 and 311/15.

**A correction the consult flags:** the figure diagnosis's sentence "58/8 is 7.3 per degree of freedom, against GENIE
CV's 109/16 at 6.8" shows GiBUU *higher* per degree of freedom. So the misreading cannot have been a per-ndf ranking.
It was most likely the raw 58, or the shape-only 28/7, read beside the 16-cell values (inference).
