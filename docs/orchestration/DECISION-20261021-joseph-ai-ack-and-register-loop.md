# DECISION 2026-10-21 — Joseph: condense the article's AI acknowledgment; a bounded register-iteration loop

**Recorded by** the paper-tighten lane, as director (Stage F).

**What led to it.** The director ran two outside register checks of the 13-page methods paper. GPT-6.1-sol rated the
register 3/5 and the presentation "nearly" ready; Gemini rated them 3.5/5 and "nearly". The director asked whether to
condense the AI acknowledgment, which Joseph had approved on 2026-10-06/08.

Joseph's answer, verbatim:

> you can condense it (maybe just say the note will have a more full acknowledgement and make sure its there?) also,
> what do you think about doing a few rounds of iteration of the paper to try to get to a 4.5/5 out of 5 with gpt 6.1
> sol and gemini? or should we wait until the 27

sha256 of the text plus a final newline begins `61e2d6ef8390e5b7`.

## What is decided

1. **The AI acknowledgment in the article is condensed.** The article keeps:
   - the tools (Anthropic Claude and OpenAI GPT models, through the Claude Code and OpenAI Codex agents);
   - what they assisted with;
   - that the authors directed the work and verified the results;
   - the figure statement;
   - "AI tools are not authors";
   - the authors' responsibility;
   - a pointer to the note's full statement, which keeps the tool versions.

   The director confirms the note carries the full statement. This amends the approved text of DECISION-20261006 in
   form only; the disclosure's content is kept.
2. **A register loop runs now, before the 2026-10-27 results** (the director's recommendation, which Joseph asked
   for). It covers presentation and language only.
   - **Rounds:** at most 3.
   - **Stop early** if both outside models rate the register at least 4.5/5, or if the rating does not rise between
     two rounds.
   - **Each round is reviewed** by an independent Claude reviewer in both directions before the models rescore it.
   - **No rewrite that drops a fact is adopted.** That covers a limitation, a post-hoc disclosure or a number,
     whatever score it would earn.
   - **What remains** goes to Joseph with the record.

## Not changed

- Claims and numbers.
- The `\pubhold` placeholders and the release text, which are Joseph's.
- J3–J5 provisional.
- No outward act.
