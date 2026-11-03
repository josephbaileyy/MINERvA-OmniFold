# Coder prompt for the caveat re-measure

The 10-25 caveat study coded each document with one Claude subagent under `../caveat-study/CODEBOOK.md`
(`../caveat-study/REPORT.md` §2.3). This re-measure does the same. Below is the prompt each coder received, verbatim
except for the paths, which are shown as `<CODEBOOK>`, `<TEXT>` and `<OUT>`. The 10-25 prompts were not committed,
so this prompt cannot be shown to match theirs. The codebook it hands over is the committed one, unchanged.

Routing: in-session subagents of a session whose `CLAUDE_CONFIG_DIR` is `~/.claude-school` (verified 2026-11-02).

**Re-coding is the one step `remeasure.py` cannot do.** Coding is a judgment, not a computation. After a paper or note
round, re-code each document whose blinded text changed (`remeasure.py` exits 3 and names it), and record the new
text with `--record-coded ours-paper` (or `ours-note`): only the named document's hash is recorded.

## Paper (`<TEXT>` = `WORK/blind/ours-paper.txt`)

> You are a coder in a document-analysis study. Read the codebook at `<CODEBOOK>` and follow it exactly.
>
> Document to inventory (read ALL of it, in chunks if needed): `<TEXT>`
>
> Write the TSV to: `<OUT>`
>
> Requirements:
> - Header line exactly: n	kind	loc	polarity	quant	assigned	issue	quote (tab-separated).
> - Quotes must be exact substrings of the text file (verified mechanically after whitespace collapse); copy
>   character for character, including ligatures and unicode. No tabs inside fields.
> - Reuse the same `issue` label every time the same caveat is restated.
> - Write nothing except the output file. Do not read any other file than the codebook and the document.
> - Before finishing, check with a short python script (python3 -I) that every quote in your TSV is found in the
>   document after collapsing whitespace, and fix any that are not.
>
> Reply with the codebook's ≤200-word summary.

## Note body (`<TEXT>` = `WORK/blind/ours-note-body.txt`)

The paper prompt, with the document line reading "(read ALL of it, in chunks; it is long, about 43,000 words, the
body of a technical document; its appendices are coded separately by someone else)", and one more requirement: "Be
exhaustive: every section, caption and table note. Append rows to the file as you go, section by section, so progress
is not lost."

## Note appendices (`<TEXT>` = `WORK/blind/ours-note-app.txt`)

The paper prompt, with the document line reading "(read ALL of it, in chunks; it is the appendices of a long technical
document, about 16,000 words; the body is coded separately by someone else, and every caveat here has loc `appendix`
unless it is a caption/footnote)", and one more requirement: "Be exhaustive. Append rows to the file as you go, so
progress is not lost."
