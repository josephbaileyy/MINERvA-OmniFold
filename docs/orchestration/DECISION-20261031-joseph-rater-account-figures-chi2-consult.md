# DECISION 2026-10-31 — Joseph: codex-school is usable; restyle the note's 2D figures; a PRD-reviewer consult on the χ² tables

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The figure diagnosis
([`state/2d-closeout/stageF/methods/figure-diagnosis-20261030/FIGURE-DIAGNOSIS-REPORT.md`](state/2d-closeout/stageF/methods/figure-diagnosis-20261030/FIGURE-DIAGNOSIS-REPORT.md),
PR #570) found three things:
- the note's 2D result figures, Figs. 7–14, are below the anchors' standard, and every proposed fix is STYLE;
- two of 128 quick reads ranked the generator χ² by χ²/ndf across unequal cell sets;
- a figure–caption mismatch in two figures.

Separately, the paper rewrite lane reported both allowed GPT accounts unusable.

> Both GPT rater accounts are out (codex-school2 until Nov 4; codex-school out of credits). The note round's adoption needs 60 sol runs. What should we do?

Joseph's answer, verbatim:

> codex-school still has usage left

sha256 of the text plus a final newline begins `c2f453981b988ed0`.

> Restyle the note's 2D result figures (Figs. 7–14): readable font sizes, proper axis labels and units, panel labels, no blank bands. Style only, no number changes; needs a small CPU run of the plotting scripts at NERSC.

Joseph's answer, verbatim:

> Yes, restyle them (Recommended)

sha256 of the text plus a final newline begins `b4e5dbbdf6e1447c`.

> The generator χ² tables (paper Table IV, note Table 16) led two quick reads to rank by χ²/ndf and call GiBUU (8 cells) best. Your 10-27 decision set the format. Change it?

Joseph's answer, verbatim:

> can we get some PRD reviewer session to suggest a fix? I'm not sure if the caveat line would introduce too much disclosure information than typical

sha256 of the text plus a final newline begins `2c1c81300c3cc083`.

## What is decided

1. **codex-school is used for sol** (gpt-6.1-sol).
   - The director tested it on 2026-10-31 with one trivial call, and it answered (rc 0). codex-school2 still reports its
     limit until Nov 4.
   - Step 3's 60 sol adoption runs go first, because they gate a merge. The figure study's remaining 25 sol pairwise
     calls go after.
   - Every output records its account.
2. **The note's 2D result figures (Figs. 7–14) are restyled.** The option offered read: "Style only, no number changes;
   needs a small CPU run of the plotting scripts at NERSC."
   - The restyle covers font sizes, axis labels and units, panel labels and blank bands.
   - It is declared and bound as usual. Each figure's underlying data are checked equal before and after, and the new
     figures pass through the note's checks.
3. **An independent PRD-reviewer consult** proposes a fix for the χ² tables' reading risk (paper Table IV, note Table 16).
   - It weighs Joseph's concern that a caveat line may add more disclosure than is typical.
   - It compares the χ² presentations of published PRD measurement papers.
   - Its options come to Joseph. Nothing changes in the tables before he decides.
4. **The two caption mismatches,** note Fig. 13's colour and Fig. 25's described feature, are corrected as truth fixes
   on the caption side, by the director's ruling, through the usual ledger and agy checks.

## Not changed

- Every number and claim, and the χ² table format until Joseph decides. Nothing is submitted, deposited or tagged.
