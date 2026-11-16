# LL5D: the meaning read of the codex referee report's Minors 1, 3 and 4 (2026-11-15)

**What it read:** `read-text.txt`, the rendered text of prep/ll5d-fill-20261115 at 72020af16:
- the abstract, in its approved form and its referee form;
- §6.3's results;
- §7's Discussion sentence and checklist;
- §7.1 item 5.

It read them against:
- the readout records, readout-g18.json and readout-ar23.json;
- LL5D-DECLARATION.md;
- Table S15 (tab:ll5d-results);
- the referee report (`~/codex-reports/referee-paper-3d75ed5d4….md`).

The reader was an independent general-purpose subagent, read-only.

**Verdict: DEFECT, one.** §6.3's pointer was typed as \stab{S14}{tab:ll5d-results}, but the build numbers the table
S15. The draft's Table S13 (tab:prr-levels), merged at a8784a176, shifted the numbering. **Fixed:** the pointer is now
S15. check_supp_pointers.py failed before the fix and passes after it, with 78 pointers and 0 failures.
director-helper-3's gate did not run that check; it now runs it, along with check_supplement_constants and
make_values --check.

**OK:**
- **The referee abstract form:** what it says is drawn and graded matches the declaration (:268-272, :305-307, :318).
  "Separate bias tests flag none" matches paper §5.2 (:402, :238). "Joint at both tunes, and at AR23 also in cell R07"
  holds in both variants, from the records.
- **§7 and the checklist:** they hold against the records, and "descriptive" is attached correctly.
- **§6.3's class sentences, the over-coverage sentence (D:476) and Table S15's values:** all hold.

**Notes, put to the director and not applied:**
- "flag none" lacks a noun.
- The approved abstract form does not answer Minor 1. That is Joseph's choice.
- The checklist qualifies only the five-observable test's matrix, although the 2D test also did not draw the run-period
  block.
- §7.1 item 5's two "covariance" phrases sit awkwardly together.
- §6.3 no longer shows the failure's size (1-14 of 300 against ≤195; χ²/ndf 3.0-3.7). A keyed magnitude clause could
  restore it.
- Row 10 and Table 2 don't say "joint" or name R07. That is the finer-words question already before Joseph.
