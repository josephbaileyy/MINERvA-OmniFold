# r22 Step 3: the note writer's brief (common to all pieces)

You rewrite one piece of a long technical companion note: the analysis note posted beside a PRD paper, on an unbinned
OmniFold cross-section measurement with MINERvA open data. The aim is register. An earlier rater asked for each change
on your list. A protection kept it out until an independent reviewer allowed it, usually in a narrowed form. You make
those changes, and only those, in the LaTeX sources. Every fact stays.

**Paths:**
- `WT=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/wt-con`
  is the repository worktree. Your files are in `$WT/docs/analysis-note/`.
- `D=$WT/docs/orchestration/state/2d-closeout/stageF/methods/r22`.
- Your list is `$D/step3/briefs/<piece>.md`. The blinded text the raters read is `$D/step2/pieces/<piece>.txt`.

**The rules of Step 2's brief bind you,** except where this brief changes them. Read `$D/step2/WRITER-BRIEF.md`
first. It covers what you may and may not change, the truth guardrail, the ledger format and the probe kinds `N:`,
`X:`, `R:` and `L:`.

## What is different in Step 3

- **Make the CHANGE TO MAKE and no more.** For an ALLOW-NARROW gap, it is the reviewer's narrowed form. The rater's
  original request is shown so that you can see what was refused. Do not go beyond the narrowed form, even partly.
- **These gaps all touch protected text:** qualifiers (B1), run history (B2) and honesty-required disclosures (C1, C2
  and C9). The reviewer's reason says what must survive. For each:
  - **No limitation, disclosure, qualifier or reported number leaves the note.** You may state one once, more
    cleanly, where it qualifies its result, and cut a pure repetition whose fact still prints elsewhere in the note
    (`N:`).
  - **Run history** may leave the note only where the narrowed form allows it, and only with an `R:` or `L:` probe to
    its home in the records or the internal ledger. If you cannot find that home, keep the history in the note.
  - **Nothing is softened.** "Has not been established", "not validated", "is not a coverage test" and the like keep
    their exact strength.
  - **Add no new fact.** A narrowed form that asks you to "state explicitly that …" may only restate what the note
    already prints, with an `N:` probe to where it prints. If it would need a fact the note does not print, skip that
    part and say so.
- **The held sentences** in your list stay exactly as they are. `tools/check_held_note.py` checks them exactly, so a
  one-word change fails.
- **B01:** B01-g-07 is the note's abstract.
  - Do NOT edit `main_note.tex`.
  - Write one before/after pair to `$D/step3/abstract-pairs.md`. Its before is the exact current source text, which
    must occur once in `main_note.tex`. Its after is your proposed text, with every fact, macro and number kept, made
    as the narrowed form asks.
  - The director passes it to Joseph.
- **Your ledger** is `$D/step3/ledger-<piece>.md`, with ids `<piece>-<n>`, in Step 2's table format.
- **Check until 0 failures:**

```
python3 -I $D/step3/check_ledger.py $WT --no-n4-frozen --files <your files, comma-separated> --ledger $D/step3/ledger-<piece>.md
python3 -I $D/step3/check_ledger.py $WT --no-n4-frozen --files <your files> --list
python3 -I $WT/docs/analysis-note/reflow_tex.py --note --check
```

## Rules of work

- Read-only outside your files, your ledger, and `abstract-pairs.md` for B01.
- No git command that writes, no build, and no model, CLI or network call.
- Other writers are editing other files at the same time. Do not touch them.
- Do not lengthen your files overall.
- If a gap cannot be made under these rules, skip it and say why.
- **Report back** in under 250 words:
  - each gap: made, partly made or skipped, with the reason;
  - the checker's last line;
  - words before and after (`wc -w` of your files);
  - anything you were unsure of.
