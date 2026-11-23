# DECISION 2026-11-21 (c) — Joseph: the AI Use Disclosure's model list follows the session records

**Recorded by** journal-editor, for the director, who relayed Joseph's words.

## What led to it

- **Pre-submission checklist item 1.** The note's AI Use Disclosure lists AI tools by name and version, the APS policy's
  "AI tool name and version". The list had been written from memory
  ([DECISION-20261114](DECISION-20261114-joseph-ai-use-statement.md)).
- **The reconciliation.** A read-only reconciliation compared each printed name with the session records: Claude Code,
  Codex, Antigravity and Grok transcripts, the 2026-11-14 session snapshot, commit trailers and the committed run log.
  It is committed beside this record as
  [`state/ai-disclosure-reconciliation-20261121/RECONCILIATION.md`](state/ai-disclosure-reconciliation-20261121/RECONCILIATION.md),
  with its scanner and raw outputs under `raw/`.
  - Of the 17 printed names, 15 have a record of use on this analysis. GPT-5.5 has none. Gemini 3.1 Pro has only a
    July 2026 run-log row of the model the dispatcher requested.
  - Five used models were not listed, and four auxiliary models are invoked by the tools themselves.
- **Redaction.** In the committed copy, every working directory and example path of a session outside this analysis
  reads `<non-analysis>`, as the director instructed. Flags, counts and dates are unchanged.

## Joseph's words, verbatim

As relayed by the director, received by 2026-11-21T16:14:08Z; the sha256 is of the text plus a final newline:

> okay yes remove the models you didn't find and add the new ones not listed and add 5.3 codex

(`203193e4f15e67c47a786f1a251b5c154bf5c5e4da29d035d7f1648399cce4fe`)

## What it decides

1. **Removed:** GPT-5.5, which has no record of use on this analysis, and Gemini 3.1 Pro, which was requested but
   never shown served.
2. **Added:**
   - Claude Fable 5.2.
   - Claude Opus 4.6 (Thinking), through Antigravity. The sentence names it beside Gemini 3.8 Flash, so it no
     longer implies that Antigravity ran Gemini only.
   - GPT-5.3-codex, GPT-5.4 and GPT-5.6 Terra.
   - In one clause, the auxiliary models the tools invoke themselves: Claude Haiku 4.5 and 5.5, Gemini 3.5 Flash
     Lite, and the Codex automatic review model, whose underlying model is not recorded.
3. **Kept:** every other listed name.

## Scope

The AI Use Disclosure in `docs/analysis-note/main_note.tex` and its `%` provenance comment. The companion PET note's
own tool sentence (`pet_note.tex`) is not changed by this record.
