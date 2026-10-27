# Absence-audit items 3 and 4: MP-5 printed, App. history corrected in place (2026-10-27)

**Authority:** Joseph, `DECISION-20261027-joseph-absence-audit-items-3-4.md`. This follows the audit, PR #400 (`absence-audit-20261027/REPORT.md`), which held these two claims for him.

**Who:** the paper rewrite lane (claude-school, Claude Opus 5.5). agy (gemini-3.8-flash-high, through `run_x.sh`) checked both corrections.

## Commits

| commit | what |
|---|---|
| `5f25c3e5` | `check_note_records.py`: the R-FIX ledger row kind, with seven planted-defect self-tests |
| `3c3a6f74` | records: Section R1 entry `mp5-truth-axis` (R1.18), and App. history's paragraph corrected in place under R-FIX-1. **Pinned by NoteRecords2026, so it must never be rewritten; merge, don't squash** |
| `94b44a5d` | NoteRecords2026 pinned to `3c3a6f74` |
| this commit | `sec_eavailw.tex` prints MP-5's result and cites R1.18; this record |

## Item 3: `sec_eavailw.tex`, the generators' pT convention

**Before:** "…their $\pT$ differs from the analysis truth $\pT$ by ±4 MeV for 68% of events, and the net effect of this difference on the cell contents has not been measured."
<!-- absence-ok: quotes the note's corrected sentences as they stood before this correction, as the FIX record; not a new absence claim -->

**After** (Joseph's option (A)): "…for 68% of events. Over the 109 joint-test cells, this convention changes the analysis simulation's cell contents by factors between 0.9965 and 1.0035 (median 1.000008), at the level of its Monte Carlo precision, and shifts GENIE's central prediction by between −0.47 and +0.53 of each cell's null spread. For GENIE with MEC, NuWro and GiBUU its effect is not reliably determined (Ref. [41], R1.18)."

**Source:** `state/measurement-paper/phase1/mp5/REPORT.md` (job 60017887, commit `494b3404`, 2026-10-20). The lines used:
- :66: "R_c over the 109 cells is 0.99649 / 1.000008 / 1.00346 (min / median / max)". The note rounds the extremes to four decimals.
- :68: "It is at the MC floor."
- :87-90: the proxy check is "UNRELIABLE by the declared 0.2 σ_c rule … UNRELIABLE for GENIE MEC, NuWro and GiBUU".
- :100: GENIE CV's "Δ/σ_c is −0.47 / 0.00 / +0.53".

**Records:**
- The new entry `mp5-truth-axis` holds MP-5's identity and these lines. Its ledger row is L-n3-1.
- The note's citation updates `records-move-ledger.md` row L-sec_eavailw, which had recorded that the file cites no records entry.
- The paragraph's other two absence claims (the origin of the near-degenerate directions; the information added by W) are true. They now carry a Search line, following the audit's research (`absence-audit-20261027/research/G3.txt`).

**agy:** AGREE (`agy/run1.*`).

## Item 4: `app_history.tex`, the two pre-J28 background-aware constructions

Joseph: "I thought we are not listing things like corrections in the note, which is only for the internal ledger. I thought the note should just have the latest updated records". So the record paragraph is corrected in place, and no correction notice prints. This section is the FIX record: it holds the paragraph's history.

**Old text** (sha256 `b7530087…14355c`, as P5 reads it). The two false or incomplete clauses:
- "…and the corrected J28 products are footed on the \emph{non}-background-aware configuration --- so no substitution is available, and supplying one would make the sentence false rather than current."
- "No positive-semidefiniteness measurement exists for either: \texttt{VL16} and \texttt{VL17} record that property for the \emph{successor} background-aware products only, and it does not transfer by inheritance."
<!-- absence-ok: quotes the note's corrected sentences as they stood before this correction, as the FIX record; not a new absence claim -->

**New text** (sha256 `3def6ba8…59c207`):
- "…footed on the \emph{non}-background-aware configuration. Background-aware-footed J28 candidates exist (\texttt{VL16}, \texttt{VL17}), but none has been adopted --- so no substitution is available, and supplying one would make the sentence false rather than current."
- "Both passed the positive-semidefiniteness check of their build, with most-negative-to-largest eigenvalue ratios of $-2.4\times10^{-16}$ (mean-centered) and $-4.1\times10^{-16}$ (CV-centered); \texttt{VL16} and \texttt{VL17} record the same property, measured separately, for the background-aware candidates."

**The evidence, quoted:**
- `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md:735`: "*** B5' #13 COMPLETE - finalize 55912230 COMPLETED, all 3 outputs, BOTH PSD OK ***". At `:740-741`: "Adopted MEAN … 5.8077e-38 (x1.333, ~0%) PSD OK (min eig/max -2.4e-16)" and "Adopted CV(F7) … 6.2367e-38 (x1.431, ~0%) PSD OK (min eig/max -4.1e-16)". This is a production status log, not a hashed receipt.
- `nd-unfolding/adopt_unified_5d.py:149-165` @ `0d919b1a` (`:138-155` @ `07c18aee`, the 2026-07-14 commit that built them): `ev = np.linalg.eigvalsh(C_new)` … `if ev[0] < -1e-12 * ev[-1]: raise SystemExit("[FAIL] adopted covariance is not PSD")`. The check stops the build on failure.
- The match to the paragraph's two constructions: `VALIDATION_LEDGER.md:499`, VL20, pre-J28 background-aware 5.807716e-38, against "Adopted MEAN 5.8077e-38".
- `VALIDATION_LEDGER.md:464`: "**NOTHING IS ADOPTED.** … This produces the footing-matched *candidate*". At `:478-479`: VL16 and VL17, background-aware arms on the J28 throws, each recording its own most-negative/maximum eigenvalue ratio (−3.19e-16, −3.23e-16).

**Mechanism:** R-FIX-1 in `records-move-ledger.md` holds the old and new digests, the reason and the authority. `check_note_records.py` P5 accepts the edited paragraph only under that row. With the row removed, P5 fails on exactly this paragraph.

**agy:** AGREE (`agy/run1.*`). In run 1, agy's reasoning noted that the kept clause "and it does not transfer by inheritance" no longer fitted once both constructions had their own measurement. The clause became "measured separately", and run 2 is AGREE (`agy/run2-I4.*`).

## The R-FIX row kind (`check_note_records.py`, `5f25c3e5`)

| id | old sha256 | new sha256 | reason | authority |
|---|---|---|---|---|

P5 accepts the base paragraph `<old>` only if all of these hold:
- it no longer prints verbatim;
- a records paragraph has the digest `<new>`;
- the authority names an existing `DECISION-*.md`.

R-FIX has no pointer-only constraint; R-EDIT keeps its own.

The self-test plants a recorded fix (silent, the control) and six defects, each of which must fire:
- a row with no authority;
- an authority that names a missing decision record;
- a wrong old digest;
- new text that is not the row's;
- a deleted paragraph;
- an unchanged paragraph (stale).

`--self-test`: 41 of 41 fired, 4 of 4 silent.

## Checks

See the PR. They are the records probe and its self-test, RECORDS-PIN at `3c3a6f74`, entry numbers, absence claims (both paragraphs now bare-free), reflow, printed_diff (only the corrected sentences change), and the build.
