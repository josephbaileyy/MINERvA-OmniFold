# DECISION 2026-11-04 (later) — Joseph: #753 merges with the referee's rewording of the run-period sentence

**Recorded by** the paper-tighten lane, as director.

**Amends** `DECISION-20261104-joseph-rpd-sentence.md` item 1: the sentence goes in reworded, not verbatim.

## What led to it

#753 is the paper lane's round under `DECISION-20261104-joseph-rpd-sentence.md`. It inserted `FD-RPD-DECLARATION.md`
§6.2's CLUSTERED sentence verbatim in the paper (Sec. IV A) and in the note's run-period section, and added the
note's description of the twelve-playlist test.

The director's PRD-referee read of the diff is in `fd/consult-rpd-sentence-20261104/PRD-REVIEW-753-GEMINI-{PROMPT,ANSWER}.txt`.
It asked for four things:
- reword the paper sentence's "by more than their playlist-to-playlist scatter would give" into PRD register;
- use neutral wording for the note's "beam-intensity era";
- state the pre-declaration once;
- condense the era test's disclaimers.

The director applied the last three in the note at `6be612c2`. The first was kept verbatim, as licensed, and put to
Joseph.

## Joseph's answer, verbatim

Asked how #753 should proceed, after reading the 3-page copy:

> Merge, reword sentence

sha256 of the text plus a final newline begins `555da20e9ef2a1cd`.

The option as put to him: use the referee's phrasing ('…by more than expected from their playlist-to-playlist
scatter'), recorded as a small departure from the pre-declared licence; then merge and re-sync.

## What is decided

1. **In both the paper and the note,** the sentence reads: "The offsets of the twelve playlists differ between the
   three period groups by more than expected from their playlist-to-playlist scatter." The pointer stays.
2. **A declared departure from §6.2's literal text,** with the same meaning and no claim added. §6.1 and §6.4 still
   bind: no cause is named, and none of the barred words appears. `check_licence.py` requires the reworded sentence
   and names this record.
3. **#753 is merged** through the CI-gated merge once the lane's checks pass, and the Overleaf standalone is re-synced.

Nothing is submitted, deposited or tagged.
