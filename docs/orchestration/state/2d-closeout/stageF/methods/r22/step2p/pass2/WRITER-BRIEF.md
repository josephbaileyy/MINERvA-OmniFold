# r22 Step 2, paper pass 2: the writer's brief

You continue a register rewrite of the body of a short physics paper (PRD style), `docs/analysis-note/paper_body.tex`.
The first pass is merged. This pass rewords a few sentences that the first pass had to leave byte for byte, under a
new rule: they are held for their **facts**, not their bytes.

Paths:
- `WT=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/wt-con`
  is the worktree.
- `D=$WT/docs/orchestration/state/2d-closeout/stageF/methods/r22`.

Read first:
- `$D/STEP2-PAPER.md` §5, the rule;
- `$D/step2p/WRITER-BRIEF.md`, the first pass's brief. Every rule in it still binds, except where this brief says
  otherwise;
- `$D/step2p/pass2/oos-changes.tsv`, the change you must **not** make for each sentence, with the classifiers'
  reasons;
- `$D/step2p/gaps.tsv`, the in-scope gaps (`problem`, `change`) named below.

## The sentences you may reword, and the gaps that act on them

| sentence (held id) | in-scope gaps to apply |
|---|---|
| the note pointer, "The companion analysis note [14] gives the full validation record …" (G1b:paper-g-01) | G1:paper-g-01 |
| the seed-42 sentence, "The two-observable central value uses LightGBM at seed~42 …" (G1b:paper-g-06) | G1:paper-g-04 |
| the Scope sentence, "The findings are those of one OmniFold implementation …" (G1b:paper-g-03) | G1b:paper-s-08 (G1:paper-g-07 is done) |
| the five-iterations sentence (G1:paper-g-02, G1b:paper-g-08) | G1:paper-s-03 ("residual proxy"), G1b:paper-s-10 |
| the envelope target, "With the envelope added, none of the reporting definitions … meets this target." (G1:paper-g-06) | G1b:paper-g-11 |
| the run-period block, "Because the block is built from the observed differences …" (G1b:paper-g-18) | G1b:paper-s-17 |
| the limitations pointer and "is stated only here" (G1b:paper-s-20) | G1:paper-s-10, G1b:paper-s-15 |

Apply each gap's CHANGE to its sentence, in a form that obeys the three conditions below. You may also adjust the
words next to a sentence so that the passage reads well, but only where those words were already changed in pass 1
or are named by these gaps.

**Do not touch.** These must stay byte for byte; a checker enforces it:
- every other held sentence in `$D/step2p/held.tsv`;
- in particular, these three, which wait on a ruling: the flux reason ("for a reason the released inputs do not let us
  determine"), the Fig. 3 covariance ("… that fails its specified acceptance criteria"), and "We make no coverage claim
  …". Their gaps G1b:paper-g-12, -s-04 and -s-19 stay skipped;
- `main_paper.tex`, which now carries Joseph's two approved pairs;
- the FROZEN sentence, the eight GATE phrases, and the alias "the joint-test estimator, a deterministic LightGBM".

<!-- absence-ok: names printed paper sentences the writer must keep; not a claim that something has not been run -->

## The three conditions (STEP2-PAPER.md §5)

- **(a) The out-of-scope change is not made.** For each sentence, `oos-changes.tsv` gives the change some rater asked
  for and the classifiers refused. Do not make it, even partly: no fact, qualifier or KEEP item dropped, and nothing
  softened. Examples:
  - the five-iterations sentence still says that 10, 15 or 20 iterations did not reduce the model dependence, and how
    that dependence is measured (F109 KEEP). You may define "residual proxy" operationally, using wording the note
    prints;
  - the run-period block still says that its size is not validated and that its own consistency check cannot fail
    (C5). Only the metatext may go;
    <!-- absence-ok: quotes the paper's printed run-period sentence; not a claim that something has not been run -->
  - the envelope target still says that no tested reporting definition meets the target with the envelope added;
  - the seed-42 sentence keeps seed 42, the negative-weight subtraction and the 400-tree, 31-leaf refinement. Nothing
    moves to a code repository;
  - the note pointer keeps the note's citation and what the note gives. The paper keeps its references to the note;
  - the limitations pointer keeps "The limitations of these results are stated with the results they qualify, …" in
    substance, as the paper's one pointer to its limitations in the note (#522 item 2). Drop the sentence "The low
    stability of four of the sixteen cells is stated only here." The low-stability fact itself (C18: R02, R06, R10,
    R15 and their stability) stays in the Limitations list, where it already prints.
- **(b) Every fact and qualifier gets a probe.** In `$D/step2p/ledger.md`, add rows P-33, P-34, … (format as in pass
  1).
  - The `before` column names the PB ids from `check_paper.py --list` for every base sentence your change touches.
    The base is still f47b1b4a, so rows P-1 to P-32 stay as they are. If you reword a sentence that a pass-1 row
    probes with `P::`, update that probe to the new wording instead of adding a contradiction.
  - Each fact and qualifier of a reworded sentence gets a `P::` probe of its new paper wording.
  - Where the note prints that fact, it also gets an `N:<note file>::<text>` probe quoting the note source. Use grep in
    `$WT/docs/analysis-note/*.tex` to find it. Where only the paper prints it, a `P::` probe is enough, and the fact
    stays in the paper.
  - **KEEP items.** If your change makes any r21 KEEP row stop printing verbatim (`$D/../r21/ledger.md`, rows with
    status KEEP), its F-id must appear in the fact column of a row of yours that has a `P::` probe of the new wording.
    F109 is the five-iterations sentence; F187 is "We make no coverage claim", which you do not touch. The checker
    names any KEEP row you miss.
- **(c) agy reads old and new as SAME.** I run this after you; you do not.

## Rules of work

- Edit only `paper_body.tex` and `$D/step2p/ledger.md`.
- Read-only everywhere else. Use no git command that writes, run no build, and make no model, CLI or network call.
- Add no number, fact, citation or claim, and do not lengthen the paper.
- Line 50 of paper_body.tex (the estimator paragraph, with the seed-42 sentence) is registry-pinned. You may change
  it, and I re-pin it. Keep one source line per paragraph, and do not pad blank lines to keep line numbers.
- Check until these report no failures:

```
python3 -I $D/step2p/check_paper.py $WT --ledger $D/step2p/ledger.md
python3 -I $D/step2p/check_paper.py $WT --list
python3 -I $WT/docs/analysis-note/reflow_tex.py --note --check
```

- Report back in under 300 words:
  - each gap: applied, partly applied or skipped, with the reason;
  - for each reworded sentence, the old and new text;
  - the checker's last line, and the `wc -w` of the printed paper_body.tex text before and after;
  - anything you were unsure of.
