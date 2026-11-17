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

## Round 2: the director's rulings (a), (c) and (d), d2581e7ef (2026-11-15)

**What changed:**
- (a): the referee form says "where separate bias tests flag no bias".
- (c): the checklist qualifies the 2D test's graded matrix ("for a matrix without the run-period term";
  COV2D-DECLARATION.md:214, :221).
- (d): §6.3's keyed magnitude clause ("1 to 14 of 300 … against a threshold of 195 … 3.0 to 3.7").

**The read:** a second independent read-only subagent.

**Verdict: MINOR, no defects:**
- (a) holds (paper :402, :238).
- (c) holds: the 2D analysis has no recoil-response term, so "without the run-period term" is the right contrast.
- (d) holds against the readouts (joint 14, 12, 4, 1; k_joint 195 at all four; flagged when the count is at or below it,
  fd_1b_mc.py:682; χ²/ndf 3.036 to 3.696), and make_values' asserts guard the sentence.

**Notes:**
- The ll5d-route-record comment had moved onto the new loop's line. It is restored.
- "of 300" comes from ll5d-ntoys (D §3.6's seeds). The readouts carry no toy-count field to check it against; each
  reading's counts are asserted ≤ 300.
- Other mentions of the 2D under-coverage (paper :247, :556) keep their unqualified wording; §6.2 states the scope.
