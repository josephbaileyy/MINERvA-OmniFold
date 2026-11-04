# The RPD-sentence round: report (paper rewrite lane, 2026-11-04)

**Authority.** `DECISION-20261104-joseph-rpd-sentence.md` (#751, merged at 0469aa858), Joseph's answer "Add verbatim +
note pointer (Recommended)". The licence is `FD-RPD-DECLARATION.md` §6, fixed before any number was read. The numbers
come from the readout record `fd/receipts-rpd/run/readout/fd_rpd.json`, sha256 `c0b06cfd2d11d99fc9226d054e68b951231f5d02e81ea3abc80cf7f89b624658`.
Its receipts are #752, merged at cb3e83517, and its `SHA256SUMS.txt` lists the same digest. The base is cb3e83517.

**What changes.**
- **The paper (item 1).** §6.2's CLUSTERED sentence goes into Sec. IV A word for word, straight after "…differ by more
  than their bootstrap scatter.", with the pointer `(\nsec{sec:fived16-pl})` before its full stop. It renders as
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

## Before and after

### Paper, Sec. IV A (decision item 1): the run-period sentences

**Before:**

> The unfolded results of the three run-period groups, each relative to its own simulation, differ by more than their bootstrap scatter. The cause is not known, and these data cannot establish which period is correct.

**After:**

> The unfolded results of the three run-period groups, each relative to its own simulation, differ by more than their bootstrap scatter. The offsets of the twelve playlists differ between the three period groups by more than their playlist-to-playlist scatter would give (note sec:fived16-pl). The cause is not known, and these data cannot establish which period is correct.

### Note, sec:fived16-pl, first paragraph (decision item 2, the counterpart)

**Before:**

> On the sixteen cells, the unfolded results of the three run-period groups (playlists 1A–1F, 1G–1M and 1N–1P), each over its own simulated truth (the double ratio), differ from one another by more than the scatter of their bootstrap replicas. The cause is not known, and these data cannot establish which period, if any, is right.

**After:**

> On the sixteen cells, the unfolded results of the three run-period groups (playlists 1A–1F, 1G–1M and 1N–1P), each over its own simulated truth (the double ratio), differ from one another by more than the scatter of their bootstrap replicas. The offsets of the twelve playlists differ between the three period groups by more than their playlist-to-playlist scatter would give. The cause is not known, and these data cannot establish which period, if any, is right.

### Note, sec:fived16-pl: the two new paragraphs (decision item 2)

**Before:** (none)

**After:**

> Each of the twelve playlists was also unfolded on its own, with its own simulation and bootstrap replicas, in a study whose tests and their readings were fixed before any playlist result was read. A playlist's offset is its double ratio on the sixteen cells relative to the exposure-weighted mean of the twelve. The statistic F of a division of the playlists into groups is the share of the offsets' exposure-weighted squared size, measured with the inverse of the relative C_total+C_resp, that the groups' exposure-weighted mean offsets carry. For the three run-period groups F=0.70, the largest of all 9,240 divisions of the twelve playlists into groups of six, three and three, so the permutation p-value is 1/9,240=1.08 × 10⁻⁴, the smallest the test can give. The permutation is approximate: the playlists differ in exposure and hence in noise, so their labels are not exchangeable, and the test's validity rests on a simulated null. In each of 2,000 simulated datasets the playlists' offsets are drawn independently from one covariance, estimated from the twelve playlists and scaled by 0, 0.5, 1 or 2, with each playlist's own bootstrap and simulation noise added; the share of datasets with p<0.05 is 0.0395–0.0565 over the four scales, within the bound of 0.0646 fixed in advance. Beside it, and descriptive only, the same statistic for a division by beam-intensity era, into 1A–1E, 1F and 1G, 1L and 1M, and 1N–1P, gives p=5.17 × 10⁻³ over the 83,160 divisions into groups of five, two, two and three; nothing is concluded from it.
>
> In the form of the two-dimensional test (§4.5, sec:uq-combine), the five-observable unfolds of the run-period groups give the double ratio of 1G–1M to 1A–1F a p∥ step of (6.28 ± 0.60) % across 8 GeV/c, 10.5 times its bootstrap scatter. Each playlist's own step, against 1A–1F (leaving the playlist out when it is one of them), was classed as consistent with none within two standard deviations (FREE), larger than half of the 1G–1M group's step, recombined from its three playlists, by two standard deviations (CARRIES), or neither (PARTIAL). The classes are CARRIES for 1L and 1M; PARTIAL for 1G, 1N and 1P; and FREE for 1A–1F and 1O. The patterns fixed in advance were that all three of 1G, 1L and 1M carry the step, or that some carry it and the others are free, each with 1A–1F free. Neither holds, so no statement of where the step lies is drawn from these classes. None of these readings identifies a cause.
>

## For the director: choices made in drafting (each reversible)

1. **Pointer placement.** The paper's pointer sits inside the sentence, before its full stop, as the paper's other
   pointers do. The words are §6.2's verbatim. `check_licence.py` reads the sentence from the declaration's CLUSTERED
   row and requires exactly that text, followed by the pointer.
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
   - **"beam-intensity era"** names the declaration's era grouping (§5 R2, by mean `numi_pot`). It is a grouping,
     not a cause, and the text says nothing is concluded from it.

   `check_licence.py` rejects §6.4's barred words in every added sentence of both files. Its self-test plants 6
   defects and catches all 6.
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

## Checks

| check | result | record |
|---|---|---|
| ledger (`check_ledger.py`, base cb3e83517) | 7 rows, 30 probes, 0 changed base sentences, 0 failures; self-test PASS | `LEDGER-CHECK.txt` |
| licence (`check_licence.py`): §6.2 verbatim in both files, §6.4's words absent from added sentences, kept clauses | PASS; self-test 6/6 | `LICENCE-CHECK.txt` |
| `make_values_fived16.py --check`; `check_sec4_receipts.py` | PASS (2,731 values); 17/17 | `VALUES-CHECK.txt` |
| rater copy (`make_rater_copy.sh`) and `check_held.py` | PASS, with case 6; the 3 known flags | `RATER-COPY.txt`, `CHECK-HELD.txt` |
| builds | paper 11 pp, note 136 pp, as at the base | build_all.sh |
| registry, results index, absence claims, reflow, manifest | see the PR; local CI 38/38 before the push | run_ci.py |

Nothing is submitted, deposited or tagged. Overleaf is not touched.
