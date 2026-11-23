# DECISION 2026-11-22 (c) — Joseph: readability pass 2 and the third review's edits, including the Tier 3 paragraph split into shorter sentences

**Recorded by** the director. The rewrite helper relayed Joseph's answers.

## What led to it

- **A second outside writing review** led to readability pass 2 (`rh/readability2-20261122`): a shorter abstract,
  procedural-language edits and de-duplicated section openings. It also split the Tier 3 paragraph of Sec. 4.4 into
  shorter sentences, at Joseph's request.
- **A third outside review** proposed five targeted edits and a page-break fix (commit `7f4b746b3`):
  - the abstract's order and list;
  - deleting the Table 4 bookkeeping sentence from the Sec. 4 introduction;
  - the Sec. 4.3 W wording;
  - the Sec. 4.4 bias sentence;
  - a shorter Sec. 5 introduction;
  - `\mbox` around "$W<1.1$ GeV".

  That reviewer also recommended no further general prose passes.
- **The director's referee read of the split Tier 3 paragraph** (agy, PDF only, against the T3 declaration's
  NOT CITABLE list) found every declared limit and every "consistent with" attachment OK. It found one FIX: "this
  oracle input" had become ambiguous. Joseph took option 1, "No data analysis has either oracle input."
  (commit `368dc2946`).

## Joseph's answers, verbatim (as relayed by the rewrite helper)

1. **On the Tier 3 wording:**

   > I don't think we need to pin this wording, I still think it can be improved but this is better than the older version

   The sha256 of the text plus a final newline begins `4779738b4f9b3657`.
2. **On pass 2,** asked "Do you approve it as it stands?":

   > looks good

   The sha256 begins `4c7cedfabdc9c683`.
3. **On the third review's batch,** asked "does the batch look good to send?":

   > yes looks good

   The sha256 begins `5e9f66e843495f9f`.

## What this decides

1. **The text.** It is `rh/readability2-20261122` at `368dc29463a66c59c6247158be19ba849da49b98`, on rewrite `703c391a1`.
   The director merged it into the rewrite branch as `58aa9fcc8`, a merge commit whose tree equals `368dc2946`.
2. **The Tier 3 paragraph.** Its quoted text in `DECISION-20261122-joseph-t3-note-wording.md` is **superseded** by the
   split text at `368dc2946`. The facts are the same, and so are the 8 `\fvval` keys, the 8 math expressions and the 3
   "consistent with" clauses, as the rewrite helper checked mechanically. The wording is no longer pinned, per answer 1.
   Any later change still goes through the T3 declaration's route: the paper lane, a referee read, and Joseph.
3. **Two meaning-read findings are accepted as Joseph's approved cuts and not applied.** These are Gemini on
   `50614b8df..7f4b746b3`, report `~/codex-reports/note-measurement/reads/rh-readability2d-7f4b746b3/gemini/report.md`.
   Grok was out of balance.
   - **DROPPED:** the Sec. 4 introduction's Table 4 sentence. The reviewer asked for the cut. Table 4 is still referenced
     in Sec. 4 and in Sec. 6's table caption, and its own caption defines its classes.
   - **WEAKENED:** the Sec. 5 introduction's reasons are condensed. Each one is still stated, in Secs. 4.4–4.5, with
     pointers.

   Joseph accepted both with the trade-off stated to him.
4. **No further general prose passes** before the Zenodo release. Figs. 7, 8 and 9 follow as a separate change, from main
   after the integration (#1247).

## Checks at `368dc2946`

- **The rewrite helper's checks:** build rc 0, 0 errors, 0 undefined or multiply-defined references, 64 pp;
  VALUES-FIVED16; LIMITATIONS-EXPORT (90 rows, review 0); SEC4-RECEIPTS 17/17; absence claims against `703c391a1`
  (0 new); pre-commit 21/21.
- **Meaning reads.**
  - Cumulative to `557581eda`: Grok PASS and Gemini PASS.
  - The Tier 3 split: Gemini PASS, together with the mechanical check above.
  - The third-review delta: the two accepted findings above.
- **The director's own build** of a git archive: rc 0, 0/0, 64 pp. The printed numbers match the previous pass, apart
  from section references and pdftotext merges of figure-internal labels.

**CITABLE FOR:** what Joseph decided and which text he accepted. **NOT CITABLE FOR:** any result.
