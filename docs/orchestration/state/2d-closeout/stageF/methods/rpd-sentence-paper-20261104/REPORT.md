# The RPD-sentence round: report (paper rewrite lane, 2026-11-04)

**Authority.** `DECISION-20261104-joseph-rpd-sentence.md` (#751, merged at 0469aa858), Joseph's answer "Add verbatim +
note pointer (Recommended)". The licence is `FD-RPD-DECLARATION.md` §6, fixed before any number was read. The numbers
come from the readout record `fd/receipts-rpd/run/readout/fd_rpd.json`, sha256 `c0b06cfd2d11d99fc9226d054e68b951231f5d02e81ea3abc80cf7f89b624658`.
Its receipts are #752, merged at cb3e83517, and its `SHA256SUMS.txt` lists the same digest. The base is cb3e83517.

**What changes.**
- **The paper (item 1).** §6.2's CLUSTERED sentence goes into Sec. IV A, straight after "…differ by more than their
  bootstrap scatter.", in the wording of Joseph's ruling on #753 (below: a declared departure from §6.2's literal text), with the pointer `(\nsec{sec:fived16-pl})` before its full stop. It renders as
  "(Ref. [14], Sec. 10.4)". Nothing else in the paragraph changes. "The cause is not known", "which period is
  correct", "poorly determined" and the 0.73–2.56 interval all print as before; `check_licence.py` checks each.
- **The note (item 2).** The same sentence goes in after its counterpart in `sec:fived16-pl`. Two new paragraphs give:
  - the (6, 3, 3) permutation test, p_flux = 1/9,240 = 1.08 × 10⁻⁴;
  - the simulated-null calibration;
  - the era test, p_era = 5.17 × 10⁻³;
  - R1's classes, stated descriptively, with the reading that no localisation is drawn from them.
- **No base sentence changes.** `check_ledger.py --list` prints none, so the ledger's seven rows are all additions.
- **Every number in the new note text is generated.** Each is a `\fvval` key that `make_values_fived16.py` (new
  `rpd_values`) computes from the pinned readout. That function also asserts each outcome the text states: stage 0
  SEES; R1 OTHER, not dropped, every playlist resolved; R2 CLUSTERED; α̂ ≤ the gate at every scale; N0's flags not
  fired; R3 not read; and p_flux × 9,240 = 1. A changed readout stops the build.

## Before and after (against the base cb3e83517, as the branch now stands)

### Paper, Sec. IV A (decision item 1): the run-period sentences

**Before:**

> The unfolded results of the three run-period groups, each relative to its own simulation, differ by more than their bootstrap scatter. The cause is not known, and these data cannot establish which period is correct.

**After:**

> The unfolded results of the three run-period groups, each relative to its own simulation, differ by more than their bootstrap scatter. The offsets of the twelve playlists differ between the three period groups by more than expected from their playlist-to-playlist scatter (note sec:fived16-pl). The cause is not known, and these data cannot establish which period is correct.

### Note, sec:fived16-pl, first paragraph (decision item 2, the counterpart)

**Before:**

> On the sixteen cells, the unfolded results of the three run-period groups (playlists 1A–1F, 1G–1M and 1N–1P), each over its own simulated truth (the double ratio), differ from one another by more than the scatter of their bootstrap replicas. The cause is not known, and these data cannot establish which period, if any, is right.

**After:**

> On the sixteen cells, the unfolded results of the three run-period groups (playlists 1A–1F, 1G–1M and 1N–1P), each over its own simulated truth (the double ratio), differ from one another by more than the scatter of their bootstrap replicas. The offsets of the twelve playlists differ between the three period groups by more than expected from their playlist-to-playlist scatter. The cause is not known, and these data cannot establish which period, if any, is right.

### Note, sec:fived16-pl: the two new paragraphs (decision item 2)

**Before:** (none)

**After:**

> Each of the twelve playlists was also unfolded on its own, with its own simulation and bootstrap replicas, in a study whose tests, bounds and readings were fixed before any playlist result was read. A playlist's offset is its double ratio on the sixteen cells relative to the exposure-weighted mean of the twelve. The statistic F of a division of the playlists into groups is the share of the offsets' exposure-weighted squared size, measured with the inverse of the relative C_total+C_resp, that the groups' exposure-weighted mean offsets carry. For the three run-period groups F=0.70, the largest of all 9,240 divisions of the twelve playlists into groups of six, three and three, so the permutation p-value is 1/9,240=1.08 × 10⁻⁴, the smallest the test can give. The permutation is approximate: the playlists differ in exposure and hence in noise, so their labels are not exchangeable, and the test's validity rests on a simulated null. In each of 2,000 simulated datasets the playlists' offsets are drawn independently from one covariance, estimated from the twelve playlists and scaled by 0, 0.5, 1 or 2, with each playlist's own bootstrap and simulation noise added; the share of datasets with p<0.05 is 0.0395–0.0565 over the four scales, within the bound of 0.0646. For an alternative chronological division into groups of five, two, two and three playlists (1A–1E, 1F and 1G, 1L and 1M, and 1N–1P), the same statistic gives p=5.17 × 10⁻³ over its 83,160 divisions; this comparison is descriptive.
>
> In the form of the two-dimensional test (§4.5, sec:uq-combine), the five-observable unfolds of the run-period groups give the double ratio of 1G–1M to 1A–1F a p∥ step of (6.28 ± 0.60) % across 8 GeV/c, 10.5 times its bootstrap scatter. Each playlist's own step, against 1A–1F (leaving the playlist out when it is one of them), was classed as consistent with none within two standard deviations (FREE), larger than half of the 1G–1M group's step, recombined from its three playlists, by two standard deviations (CARRIES), or neither (PARTIAL). The classes are CARRIES for 1L and 1M; PARTIAL for 1G, 1N and 1P; and FREE for 1A–1F and 1O. The study's two patterns are that all three of 1G, 1L and 1M carry the step, or that some carry it and the others are free, each with 1A–1F free. Neither holds, so no statement of where the step lies is drawn from these classes. None of these readings identifies a cause.
>

## For the director: choices made in drafting (each reversible)

1. **Pointer placement.** The paper's pointer sits inside the sentence, before its full stop, as the paper's other
   pointers do. At 74f0b929 the words were §6.2's verbatim, and `check_licence.py` required exactly that text; since
   Joseph's ruling (last section) they are the ruled wording, and the check requires that instead.
2. **α̂ printed as 0.0395–0.0565, not 0.040–0.057.** These are the readout's values exactly (79 and 113 of 2,000).
   The decision's figures are the same values at two significant figures. The gate prints as 0.0646.
3. **Two facts beyond the director's list, both from the readout:**
   - **stage 0's step,** (6.28 ± 0.60) % across 8 GeV/c, 10.5 times its scatter, in the 2D test's form. R1's classes
     are defined relative to that step and are computed only under stage 0's SEES, so without it the classes have no
     referent.
   - **F = 0.70,** the statistic the p-value is a rank of.

   Either can be cut. Cutting stage 0 would leave the classes undefined, so I would keep it.
4. **Citations.** The record's sha, the declaration's sections, the bindings (#703, #727, #741), the decision and the
   receipts PR are cited in the new paragraphs' source comment. The printed note cites no repository files anywhere,
   and the round follows that convention.
5. **Words near §6.4's list:**
   - **"the test's validity rests on a simulated null"** is the readout's own label (`labels.r2`: "its validity rests
     on the simulated null"). "Validity" is not on §6.4's list, and the sentence makes no claim about either block.
   - **"beam-intensity era"** named the declaration's era grouping (§5 R2, by mean `numi_pot`). Superseded: after the
     PRD-referee read it prints as "an alternative chronological division" (below), and the name is in the source
     comment only.

   `check_licence.py` rejects §6.4's barred words, and since the read also "beam-intensity", in every added
   sentence of both files. Its self-test plants 7 defects and catches all 7.
6. **The decision's PRD read is not followed in its framing.** It argues that the sentence "confirms that the three
   operational eras represent genuine, discrete systematic shifts" and "validates the topology" of the covariance.
   Neither reading is licensed (§6.2: nothing is added about whether every playlist shares its group's offset; §6.4
   bars "validated"), and neither appears in the text. Its placement and its request for the p-values in the note are
   followed.
7. **A rater-tool case.** The added sentence reflows the paper's last page, and pdftotext then emits a layout that
   `rater-calibration/tools/fix_da_order.py` had no case for. The emitted order was:
   - the ACKNOWLEDGMENTS heading, ahead of the body's last paragraphs, with the body's final line before it;
   - the first two lines of reference [1], between the body's end and the acknowledgments;
   - the rest of [1], after the data-availability text.

   Case 6 moves the three pieces back and keeps the word multiset. Its entry test requires the acknowledgments' text
   to follow [1], so case 1's layout still reaches case 1; a fixture of each was run. With case 6, make_rater_copy
   passes and check_held gives its three known flags (G1:paper-g-08, G1:paper-s-08, G1b:paper-s-07).
8. **Unchanged.** The note's existing "its size and coverage have not been independently validated" (sec:fived16-pl,
   the audit paragraph) predates the round and is untouched.

## After the PRD-referee read of #753 at 74f0b929

**The read.** The director's Gemini read of the diff is in this directory, verbatim:
- `PRD-REVIEW-GEMINI-PROMPT.txt`, sha256 `52b66cfb0d6cb1d57249d1537ace5d85baa67d530baf466b5a2b8027c810e12a`;
- `PRD-REVIEW-GEMINI-ANSWER.txt`, sha256 `afe86fb488b2bf1afdf67e0fa6e327150a9cd4374bdcc4a99524323bd73f55a5`.

Both equal the director's SHA256SUMS. The director accepted choices 1–6 above, including stage 0's step as the
classes' referent and the exact α̂, and ruled on the read's four edits.

**Not adopted, for Joseph: edit 1** (since adopted by Joseph's ruling; see the next section). The read asks for the paper's sentence to be reworded: "by more than their
playlist-to-playlist scatter would give" becomes "by more than expected from their playlist-to-playlist scatter", or
"…would predict". It is not adopted, because Joseph decided the sentence goes in verbatim
(`DECISION-20261104-joseph-rpd-sentence.md` item 1), and the declaration licenses it word for word (§6.2).
`check_licence.py` holds the paper and the note to the declaration's text. A reworded sentence would need Joseph's
decision and, since §6.2 licenses only its own words, the director's reading of whether a reworded sentence is still
licensed.

**Adopted (the director's ruling), in the note only:**
- **Edit 2.** "division by beam-intensity era" becomes "an alternative chronological division into groups of five,
  two, two and three playlists". The read takes "beam-intensity" to imply a mechanism. The groups are the
  declaration's, consecutive in run order. The declaration's name for them is in the source comment only, and
  `check_licence.py` now fails if "beam-intensity" prints in any added sentence; its self-test has a seventh plant
  for it.
- **Edit 3.** The pre-declaration is stated once, at the start of the diagnostic paragraph: "a study whose tests,
  bounds and readings were fixed before any playlist result was read". Naming the bound and the readings there keeps
  the facts that "fixed in advance" (the calibration bound) and "patterns fixed in advance" (R1's patterns) carried;
  those two repeats are dropped.
- **Edit 4.** The era test is reported with the single qualifier "this comparison is descriptive". "Beside it, and
  descriptive only" and "nothing is concluded from it" are dropped.

"Partition" in the director's example wording is printed as "division", the word the paragraph already uses for the
flux test's 9,240.

**The changed sentences, before (at 74f0b929) and after.** No number changes; the paper is unchanged.

**Before:**

> Each of the twelve playlists was also unfolded on its own, with its own simulation and bootstrap replicas, in a study whose tests and their readings were fixed before any playlist result was read.

**After:**

> Each of the twelve playlists was also unfolded on its own, with its own simulation and bootstrap replicas, in a study whose tests, bounds and readings were fixed before any playlist result was read.

**Before:**

> In each of 2,000 simulated datasets the playlists' offsets are drawn independently from one covariance, estimated from the twelve playlists and scaled by 0, 0.5, 1 or 2, with each playlist's own bootstrap and simulation noise added; the share of datasets with p<0.05 is 0.0395–0.0565 over the four scales, within the bound of 0.0646 fixed in advance.

**After:**

> In each of 2,000 simulated datasets the playlists' offsets are drawn independently from one covariance, estimated from the twelve playlists and scaled by 0, 0.5, 1 or 2, with each playlist's own bootstrap and simulation noise added; the share of datasets with p<0.05 is 0.0395–0.0565 over the four scales, within the bound of 0.0646.

**Before:**

> Beside it, and descriptive only, the same statistic for a division by beam-intensity era, into 1A–1E, 1F and 1G, 1L and 1M, and 1N–1P, gives p=5.17 × 10⁻³ over the 83,160 divisions into groups of five, two, two and three; nothing is concluded from it.

**After:**

> For an alternative chronological division into groups of five, two, two and three playlists (1A–1E, 1F and 1G, 1L and 1M, and 1N–1P), the same statistic gives p=5.17 × 10⁻³ over its 83,160 divisions; this comparison is descriptive.

**Before:**

> The patterns fixed in advance were that all three of 1G, 1L and 1M carry the step, or that some carry it and the others are free, each with 1A–1F free.

**After:**

> The study's two patterns are that all three of 1G, 1L and 1M carry the step, or that some carry it and the others are free, each with 1A–1F free.


## Joseph's ruling: the reworded sentence

**The ruling.** Joseph read #753 at 6be612c2 and answered "Merge, reword sentence". The sha256 of the text plus a
final newline begins `555da20e9ef2a1cd`, which this lane recomputed. The answer is recorded in
`DECISION-20261104-joseph-753-reword-and-merge.md`; it adopts the PRD-referee read's edit 1, which the section above
had recorded for him.

**The departure, declared.** §6.2 of `FD-RPD-DECLARATION.md` licenses one sentence in its own words. Both files now
print the ruled wording instead, which departs from that literal text in one phrase:

| | the sentence |
|---|---|
| §6.2, literal | The offsets of the twelve playlists differ between the three period groups by more than their playlist-to-playlist scatter would give. |
| ruled, printed | The offsets of the twelve playlists differ between the three period groups by more than expected from their playlist-to-playlist scatter. |

- **The meaning is the same, and no claim is added.** Both say the between-group differences exceed what the
  within-group, playlist-to-playlist scatter accounts for; that is R2's CLUSTERED reading (p_flux < 0.05, calibrated).
  Neither names a cause, sizes the offsets, or says whether every playlist shares its group's offset, which §6.2
  excludes. "Expected" is used in its statistical sense, an expectation under the playlist-to-playlist scatter; it
  asserts no prediction from a model.
- **Unchanged:** the paper's pointer, the sentence's place in both files, and every other clause of the paragraph.
  "The cause is not known", "which period is correct", "poorly determined" and the 0.73–2.56 interval all still print.

**Enforced in code.** `check_licence.py` no longer requires §6.2's literal text. It now:
- reads §6.2's sentence from the declaration, applies the one recorded phrase swap (`DEPARTURE`), and requires the
  result to be the ruled sentence (`RULED`), so a change to either side fails;
- requires the ruled sentence once in each file, at its place (with the pointer in the paper), and fails if §6.2's
  literal sentence still prints in either file;
- requires the decision record to exist and to quote the ruled sentence, and names it in the check's source
  (`DECISION`);
- keeps every other check: §6.4's words and "beam-intensity" absent from added sentences, and the kept clauses.

Its self-test plants 10 defects and catches all 10. The 3 new plants are the literal sentence restored in the note, the
record absent, and a record that does not quote the sentence; "reworded again" replaces the old "reworded".


## Checks

| check | result | record |
|---|---|---|
| ledger (`check_ledger.py`, base cb3e83517) | 7 rows, 34 probes, 0 changed base sentences, 0 failures; self-test PASS | `LEDGER-CHECK.txt` |
| licence (`check_licence.py`): the ruled sentence (§6.2 with the recorded departure) in both files and §6.2's literal in neither; the decision record quotes it; §6.4's words and "beam-intensity" absent from added sentences; kept clauses | PASS; self-test 10/10 | `LICENCE-CHECK.txt` |
| `make_values_fived16.py --check`; `check_sec4_receipts.py` | PASS (2,731 values); 17/17 | `VALUES-CHECK.txt` |
| rater copy (`make_rater_copy.sh`) and `check_held.py` | PASS, with case 6; the 3 known flags | `RATER-COPY.txt`, `CHECK-HELD.txt` |
| builds | paper 11 pp, note 136 pp, as at the base | build_all.sh |
| registry, results index, absence claims, reflow, manifest | see the PR; local CI 38/38 before the push | run_ci.py |

Nothing is submitted, deposited or tagged. Overleaf is not touched.
