# DECISION 2026-10-26 — Joseph: the short scope fix for the extended-fiducial sentence, the R04 look and the correlation-sensitivity check, and one-line paragraphs in the TeX sources

**Recorded by** the paper-tighten lane, as director.

## 1. The extended-fiducial absence claim

**What led to it.**
- n2's writer n2-E and the paper rewrite lane found that "no extended-fiducial production with refined negative-weight
  subtraction has been run" (`sec_fps.tex:121-122`; `app_negweight.tex:~359-363`, at `be045af4`) is false as read.
- **The evidence:**
  - Ten `negweight-refined` extended-fiducial endpoint unfolds ran as job `56430128_[0-9]`, from an enforced launcher
    (`nd-unfolding/sbatch_unfold_active_fps.sh:18, 34-35, 60`; `RUNBOOK-20260807-gbdt-closeout.md:34`).
  - They fed the lateral-band blocks of an extended-fiducial covariance (job `56431823`), which is not quoted
    (`AGENTS.md:36`).
- **The note's quoted extended-fiducial value** comes from the purity battery of 2026-06-10 (job `54244120`).
- The director offered Joseph three choices: a full correction naming the later run and covariance, a short scope fix,
  or holding the sentences for the review with Ben.

Joseph's answer, verbatim, the option he selected:

> Short scope fix

sha256 of the text plus a final newline begins `2f0eacf73061b0c7`. The option read: "The extended-fiducial central
value was produced with the binned purity correction (the battery of 2026-06-10), not with refined negative-weight
subtraction." It drops the false absence claim and says nothing about the later run or the unquoted covariance.

**What is decided.**
1. **Both sites print the short scope fix.** The wording may follow the surrounding sentence's grammar, but it claims no
   more and no less than that text. agy agrees on each site.
2. **A third site** was found after the question was put: `sec_fps.tex:8-9`, "No corrected covariance exists for it".
   - It is false as read in the repository's own vocabulary
     (`nd-unfolding/uq_fps/corrected/FPS_UQ_CORRECTED_STATE.md:127`).
   - The director applies the same choice to it: a scope fix that states only what is true and says nothing about the
     unquoted product. That is "No covariance is quoted for it, so the result consists of central values and these
     validation tests."
   - Joseph is told this in the same turn, and may overrule it.
3. **"No extended-domain covariance has been constructed with re-selected lateral bands under the procedure of §4.5"**
   (`sec_fps.tex:131-132`) is true as scoped. It stays, with a Search line citing `AGENTS.md:36`, the audit at
   `AUDIT-FINDINGS-20260820-fps.md:217-221, 389-390`, and C_PL's adoption on 2026-10-17.

## 2. R04 and the correlation-sensitivity check

**What led to it.**
- G-DIAG (`FD-G-DIAG-REPORT.md`, PR #383) found that each 16-cell prediction's χ² is carried by two to three
  cell-contrast modes with relative σ of about 0.6–3 %.
- R04 leads the largest mode of three of the four 16-cell predictions, and is in the smallest-σ mode of all four.
- The director offered (a) a per-cell look at R04, (b) a sensitivity check that weakens the cell-to-cell correlations of
  the interaction-model uncertainty, and (c) keeping the χ² internal.

Joseph's answer, verbatim:

> yes lets look at R04 and do the sensitivty check

sha256 of the text plus a final newline begins `a1edf4afa82a8931`.

**What is decided.**
1. **(a) and (b) are approved,** at 0 node-h on a login node, each through a declaration and a binding.
2. **Both are descriptive.** Neither changes the reported covariance, C_resp, κ, any cell or the Stage G readout.
3. **Neither is a claim,** and the interpretation is Joseph's.

## 3. One-line paragraphs and comments in the TeX sources

Joseph's words, verbatim:

> also in all of the notes can you fix how paragraphs and comments are split into multiple lines? in overleaf, there is automatic text wrapping, so it is easiest to read the tex if the paragraphs and comments are all one line.

sha256 of the text plus a final newline begins `21eeff5cd747f3ee`.

**What is decided.**
1. **The hand-written TeX sources of the documents are reflowed.** These are the note, paper, primer, PET document and
   records under `docs/analysis-note/`. Each prose paragraph becomes one source line, and each block of consecutive
   full-line comments becomes one comment line.
2. **It is a formatting change only.** It must leave the typeset text unchanged. The proof is that each PDF's extracted
   text, with whitespace normalized, is identical before and after. Every note checker must still pass.
3. **Lines whose breaks carry meaning are left alone:**
   - tables, alignments, verbatim and code listings;
   - list items, each `\item` on its own line;
   - macro definitions;
   - lines ending in `%` where the line break is suppressed;
   - any line with a trailing comment.
4. **Generated files are not reflowed by hand.** Their generators own them.
5. **It lands as one mechanical PR after n2 merges and before n3 branches,** so that it does not conflict with a round
   in progress.
6. **Line citations in earlier records stay as they are.** Each one is dated by its commit.

## Not changed

- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.
