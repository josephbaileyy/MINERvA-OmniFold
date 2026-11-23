# DECISION 2026-11-22 (b) — Joseph: the readability pass goes into the note before the Zenodo tag, the measurement framing stays, and every change is accepted

**Recorded by** the director. The rewrite helper relayed Joseph's answers.

## What led to it

- An outside writing review of the note at `3e5ad55a0` suggested five things:
  - an abstract that leads with findings;
  - one narrative, carried by the section openings;
  - moving the six interpretation conditions of Sec. 5.3 to App. A.5;
  - cutting repeated procedural qualifiers;
  - simpler Figs. 7 and 9.
- The director asked whether the pass should go into the Zenodo release. The rewrite helper put that question to Joseph.

## Joseph's answers, verbatim (as relayed by the rewrite helper)

1. > and lets do the edits now and the tag after. and can you do it all? I think we should keep the measurement framing for now

   The sha256 of the text plus a final newline begins `5c2a28d4631f7454`.
2. On the change ledgers and the seven open wording questions:

   > accept all recommendations

   The sha256 of the text plus a final newline begins `ee3205789ca35bdc`.

## What this decides

1. **The order.** The readability pass is merged into `rewrite/journal-voice-20261121` before the Zenodo tag. The tag
   waits for the pass, for the rewrite→main integration, and for the build_all repair that main's record-checks require.
2. **The framing.** The measurement framing of the `3e5ad55a0` abstract stays: a 2D cross-section measurement, with the
   3D–5D results as extensions and the sixteen-cell result for illustrative use. It supersedes the methods reframing of
   `DECISION-20261108-joseph-note-framing-and-estimator-dependence.md` for the note as released.
3. **The text.** Every row of the rewrite helper's ledgers is accepted, together with its recommendation on each of the
   seven open questions. The ledgers are `CHANGES-A.md` and `CHANGES-B.md` in
   `~/codex-reports/note-measurement/narrative-20261122/`. The accepted text is
   `rh/readability-20261122` at `53f21c37de4be0dc4b261bed12e395b0df48e16d`, two commits on `3e5ad55a0`. The director
   merged it into the rewrite branch as `8abb4f255`, a merge commit whose tree equals `53f21c37d`. The Tier 3 paragraph
   (`DECISION-20261122-joseph-t3-note-wording.md`) is unchanged. Sec. 6.2 adds one sentence restating it in its
   "consistent with" wording.
4. **Figs. 7 and 9** follow as a separate change, after the integration lands. They are redrawn from their producers.

## Checks at `53f21c37d`

- **The rewrite helper's checks:**
  - VALUES-FIVED16 --check and --self-test;
  - LIMITATIONS-EXPORT (90 rows, review 0) and --self-test;
  - SEC4-RECEIPTS 17/17;
  - MANIFEST and RESULTS-INDEX;
  - absence claims against `3e5ad55a0` (0 new);
  - pre-commit 21/21;
  - the meaning reads: Grok PASS and Gemini PASS on the full pass and on the delta. The third reader (agy opus46) was
    out of quota.
- **The director's own build** of a git archive of the sha: rc 0, 0 errors, 0 undefined or multiply-defined references,
  64 pp. Every changed or added printed number was compared against the base. Only page and section numbers, restated
  existing values, and "GENIE 2.12.10" differ; the note's Sec. 4 already prints that version for the same predictions.

**CITABLE FOR:** what Joseph decided and which text he accepted. **NOT CITABLE FOR:** any result.
