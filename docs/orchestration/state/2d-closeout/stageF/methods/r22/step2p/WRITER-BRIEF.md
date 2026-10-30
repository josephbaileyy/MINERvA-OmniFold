# r22 Step 2, paper round: the writer's brief

You rewrite the body of a short physics paper (PRD style) on an unbinned OmniFold cross-section measurement with
MINERvA open data, for register. Raters named the gaps, listed in `step2p/gaps.tsv`. You fix those gaps, and only
those, in `docs/analysis-note/paper_body.tex`. Every fact stays.

Paths:
- `WT=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/wt-con`
  is the repository worktree.
- `D=$WT/docs/orchestration/state/2d-closeout/stageF/methods/r22` holds this brief, the plan (`STEP2-PAPER.md`), the
  gap list and the checker.
- The base text as the raters read it is `$D/step2p/base/manuscript.txt`.

## What you may change

- **Only `paper_body.tex`.** Do not edit any other file in the repository: `main_paper.tex` (title, abstract,
  acknowledgments, Data availability), `values*.tex`, every note source, the bibliography and the registry.
- **The in-scope gaps** are in `$D/step2p/gaps.tsv`, with columns `quote`, `problem` and `change`. Fix each as its
  CHANGE asks, within the rules below.
  - **WORDING:** rewrite in place.
  - **STRUCTURE:** merge, move, cut, split or consolidate passages within the paper.
  - **Pattern gaps:** where a PROBLEM names a pattern, fix the like passages too.
- **The #522 moves.** These are G1:paper-s-02, G1:paper-s-10 and G1b:paper-s-15, and the cuts in G1b:paper-g-05,
  paper-g-10 and paper-g-17. A limitation or disclosure may leave the paper only if all three hold:
  - the note already prints it (prove it with an `N:` probe, quoting the note source);
  - the result it bounds stays correctly stated in the paper;
  - the paper keeps its one pointer to its limitations in the note, the held sentence "The limitations of these
    results are stated with the results they qualify, …".

  Do not edit the note to make a probe pass. If the note does not print the fact, the fact stays in the paper.

## The held sentences: never change them

- **`$D/step2p/held.tsv`** lists 23 sentences quoted by out-of-scope gaps. Each must still print exactly as it is,
  and `tools/check_held.py` checks this after the build.
- **Gaps whose quote is held.** Where an in-scope gap's own quote is a held sentence (the `held_overlap` column), the
  held sentence wins. Apply that gap only to other passages its PROBLEM describes; if there are none, skip the gap
  and say so.
- **The FROZEN sentence** "Interval coverage has not been validated." prints verbatim, exactly once. You may move it,
  or consolidate other coverage statements around it.
  <!-- absence-ok: names the paper's FROZEN printed sentence; not a claim that something has not been run -->


## What you must not change

- **No claim and no number changes.**
  - Every macro stays a macro (`\SI{…}`, `\fvval{…}`, `\uqMedian`, …), and you never type its value.
  - Every `\label`, `\ref`, `\nsec`, `\napp`, `\cite` and equation stays.
  - Add no number, fact, citation or claim. The checker rejects any numeral not in the base.
- **The truth guardrail.** A qualifier stays where leaving it out would make the sentence false as read: "has not
  been tested", "not validated", "descriptive", "conditionally on …", "within the implemented simulation model",
  "not held-out", "does not cover …". You may reword a qualifier and attach it more tightly to its claim, but not drop
  or weaken it.
  <!-- absence-ok: quotes printed qualifiers of the paper as examples; not a claim that a result is absent -->
- **Protections.** The protections inventory,
  `$WT/docs/orchestration/state/2d-closeout/stageF/methods/protections-inventory-20261028/REPORT.md`, binds:
  - A7: what a claim states;
  - B1/B3: the KEEP qualifiers;
  - the HONESTY items C1, C5, C7, C8, C11, C12, C17 and C20, which stay in the paper next to the result they bound.

  `$WT/docs/orchestration/state/2d-closeout/stageF/methods/r21/ledger.md` marks the paper's KEEP and HONESTY facts.
  It is from an older revision, so match them by wording.
- **The eight GATE phrases** print exactly once each, byte for byte. They are listed in `step2p/check_paper.py`
  (`GATE`), for example "biased by up to \SI{4}{\percent} in simulation".
- **The registered alias.** "the joint-test estimator" is a registered name and must still print. Do not rename the
  estimator, even where a gap calls the label internal. You may define it at first use.
- **Line 52** of paper_body.tex, which cites `registry/ALIASES.tsv:38` and ATTRIBUTION 17, may change, and I will
  re-pin it. **Line 64**, the table row "negative weights; refinement 400 trees, 31 leaves" (ALIASES 47), stays as it
  is.
- **Comments and markers** stay with the text they serve:
  - every `% Search: … @ <sha>` line, which is an absence-claim support line;
  - every FIVED16 block marker, which `make_values_fived16.py` checks;
  - tables and figure environments, which are copied verbatim.
- **The records.** The paper is not a records document, and nothing moves into the records here. `records-move-ledger.md`
  (`docs/analysis-note/`) governs the note's records move and must not change.
- **Length.** Do not lengthen the paper overall.

## The two Joseph pairs: write them, do not apply them

G1:paper-s-06 (the abstract's χ² sentence, A4) and G1:paper-s-09 (the Data availability package sentence, A1) are
in `main_paper.tex`. Write each as a pair in `$D/step2p/pairs.md`:
- the exact current source text, which must occur once in `main_paper.tex`;
- your proposed text, keeping every fact, macro and number;
- the pin `sha256(before + "\0" + after)[:16]`, computed with `check_paper.pin`.

For the χ² sentence, Joseph has already approved the note abstract's version: "Three external generator predictions,
compared on all sixteen cells, give $\chi^{2}$ between … for 16 degrees of freedom. GiBUU, compared only on the 8
cells its sample covers, gives $\chi^{2}=…$ on those cells." For the Data availability sentence, every statement of
what exists, is deposited or is reproduced must stay true. "Not yet deposited" stays.

## The fact ledger: write `$D/step2p/ledger.md`

One markdown table: `| id | fact | before | disposition | after | probe |`.
- **id:** P-1, P-2, …
- **before:** the PB ids from `--list` for every base sentence you changed. Each changed base sentence must appear in
  some row.
- **disposition:** REWORDED, MERGED, MOVED, SPLIT, CUT-PAPER (the fact prints elsewhere in the paper) or CUT-NOTE (a
  #522 move: the note prints it).
- **probe:** joined by ` && `:
  - `P::<text>` prints in paper_body.tex;
  - `XP::<text>` no longer prints there;
  - `N:<note file>::<text>` prints in that note source.

  The text is the comment-stripped, whitespace-collapsed LaTeX source. Every fact a changed sentence carried needs a
  probe at its home.

Check until the checker reports 0 failures:

```
python3 -I $D/step2p/check_paper.py $WT --ledger $D/step2p/ledger.md
python3 -I $D/step2p/check_paper.py $WT --list    # the changed base sentences
```

Then run `python3 -I $WT/docs/analysis-note/reflow_tex.py --note --check`, which keeps one source line per paragraph.

## Rules of work

- Read-only outside paper_body.tex, `step2p/ledger.md` and `step2p/pairs.md`. Use no git command that writes, run no
  build, and make no model, CLI or network call.
- If a gap cannot be fixed without breaking a rule above, skip it and say why.
- **Report back** in under 300 words:
  - each in-scope gap: fixed, partly fixed or skipped, with the reason for any skip;
  - the checker's last line;
  - the words before and after, from `wc -w` of paper_body.tex's printed text;
  - anything you were unsure of.
