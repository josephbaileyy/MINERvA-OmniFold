# The paper's AI-use statement: the meaning read (2026-11-14)

**What changed:** the AI sentences of main_paper.tex's acknowledgments, replaced byte for byte by "The paper's
condensed statement" of docs/orchestration/DECISION-20261114-joseph-ai-use-statement.md (#1152). The director's
instruction of 2026-11-14 was: one small commit on draft/methods-short-20261109, independent of D1 and LL5D, then merged
into prep/d1-cnew-20261114.

**The read:** an independent general-purpose subagent read the first draft (`diff-as-read.txt`) read-only, against the
decision's census. Its report is `MEANING.txt`.
- **Verdict: DEFECT (coupling only), since resolved.** Items 1-3 and 6 are OK: the wording is byte for byte, nothing else in the
  acknowledgments changed, the census is covered, and nothing overstates the decision.
- **Item 4:** the paper's pointer ("The analysis note gives the full statement, including the tool versions") and its
  delegation sentence are accurate only once main_note.tex:115-131 carries the decision's full statement. The note's
  statement was still the old one when read. **Resolved:** director-helper-2's 978bbe64
  (draft/note-round2-20261108) puts the decision's full statement in main_note.tex. I checked it whitespace-normalized
  on 2026-11-15, with Gemini, Grok 4.7, Sonnet 5 or 5.5, GPT-6 Sol, the delegation sentence and "unless it is labelled
  descriptive" all present.
- **Item 5 notes, applied to the source comment:**
  - it now cites Joseph's second quote (c23237e29e3186ce) for "the first author";
  - it says that the earlier comments record the old text's provenance, while git holds the text;
  - it records the coupling's resolution by 978bbe64.
