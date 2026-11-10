# Note round 2: blind referee reads (2026-11-10)

**What was read:** the analysis note at PR #952's head `1a16763347b9a17224f9e943f722b1cfa4c12810`, built blind by
`note-round1-20261108/make_note_rater_copy.sh`. The build was 139 pages, and the blinded copy is 69,598 words with
every caption, appendix and the last body section present. The blinded text's sha256 is in `run-header.txt`; the
text itself is not committed.

**Readers:**
- `gpt.txt`: codex-school gpt-6.1-sol, high, read-only, with the note in its working directory;
- `gemini.txt`: gemini-3.8-flash-high through `agy --sandbox`. A first attempt produced no output, because a tool
  permission was auto-denied, and it was rerun with the no-tools preamble.

Both were given `prompt.txt`: round 1's referee prompt, plus the out-of-scope note for AUD-N4 and AUD-N5 and the
publication standard.

**Scores:** GPT 4/10, Gemini 3/10. Both recommend major revision.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** what each reader reported about the note at that head.
- **Not citable for:** any finding; any note or paper sentence by itself; Joseph's decision on publishing the note.

Nothing is submitted, deposited or tagged.
