# b4 notes (Sec. VI, Discussion and conclusions, with VI A Limitations): choices a reviewer should know

Revised after the reviewer's ADOPT-AFTER-FIXES verdict:
1. MINOR: the lead's qualifier is restored. F342 now reads "The limitations of these results are stated with the
   results they qualify, in Secs. ...".
2. MAJOR, an accuracy fix rather than a ledger fact: right after the lead, I added "The low stability of four of the
   sixteen cells is stated only here." The lead says each limitation is stated with its result in Secs. III–V, but
   the low-stability cells (item 4, F347) are stated only in this subsection. The base inherited that inaccuracy.
   The new sentence has no row and no numeral, and the F347 item is unchanged.

## Structure

- **Paragraphs.** The section follows the outline:
  - ¶1 states the principal result (F333).
  - Then comes the bare `\label{sec:limits}`, on its own line between ¶1 and ¶2 and attached to no heading, as the
    outline gives it. It resolves to Sec. VI.
  - ¶2 gives the two findings that the result retains part of its prior (F335–F339).
  - ¶3 lists what must be checked (F340).
  - VI A follows.
- **VI A as a numbered list (R2).** The opener (F342) and "The principal ones are these." (F343) come first. Five
  `enumerate` items follow, one per limitation, in outline order:
  1. the 2D covariance (F344);
  2. the 3D and 4D central values (F345);
  3. the sixteen-cell coverage (F346);
  4. the low-stability cells (F347);
  5. the conditions and scope of the note's calibrated tests (F348–F352).

  Every atom, including the verbatim-probed sentences F345, F346 and F347, is unchanged inside its `\item`. If
  the director prefers the base's run-on paragraph, deleting the `enumerate` and `\item` lines restores a paragraph
  without touching any atom.

## Wording chosen to fit an atom

- **F348 and F349.** These were one base sentence. They are now two, per R10: "The note's calibrated tests reject
  hybrid nulls, conditionally on the simulation's hadronic response." and "However, the rejections carry over to the
  generator predictions themselves only under a bound ..., which has not been shown." F349's atom begins lowercase,
  so the opener "However," is mine.
- **F351 and F352.** They stay one sentence with ", and", because F352's atom begins lowercase ("they show no
  evidence ..."). The two rows share that sentence as their `after`.
- **F339.** The atom keeps the result and its open question in one sentence ("..., but whether that bias has the
  same origin is not established"), so R10 cannot split it.
- **F340.** The atom holds the semicolon-separated checklist after the colon. It is a series, not a splice.
- **F346.** The atom contains a semicolon, and it is probed verbatim.

## Cross-batch facts (measured on b1–b4 concatenated)

- The eight bound GATE phrases each print once in the assembled body. All are in b2.
- The FROZEN sentence prints once, as its own sentence, in b1.
- 29 `\label`s, all unique, equal the outline's label set exactly, with none missing and none extra.
- Every `\ref{...}` in the body resolves to a body label. The `\ref*{N-...}` pointers into the note resolve only
  in the real build.
- A smoke compile of b1–b4, run twice in a minimal two-column `article` driver with stub graphics, exits 0. It
  reports no undefined body references. The same four overfull boxes as before are all in verbatim floats: Eq. (1)
  and Tables I–III.

## Checker change

- `check_batch.py` gains the b4 config. In `after` trimming it also strips a leading `\begin{enumerate}` or `\item`
  and cuts a trailing `\item` or `\end{enumerate}`. Rebuilding the b1–b3 ledgers with the changed checker left them
  byte-identical (`cmp`).
