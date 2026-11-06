# OUTCOME 2026-11-06 — 1B stage 1: the receipt STOPs on §2b, and stage 1 ends under rule (iii)

**Recorded by** the paper-tighten lane, as director.

**The record:** `state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/b3/receipt-run-60893641/`, on the
campaign branch `decl/1b-staged-a2-1-20261103` at commit `b3f27fab309c132f3303d252d20ba865cae97e63` (coverage-5b).
- `receipt.json` has sha256 `9995f55adb7846e230c2e982221d20e7c5c1136daf5cb4576e355544bb54fa3d` (253,512 bytes).
- `receipt.txt` states it.
- The director read both from that commit.

## The readings, as the record states them

**The job:** 60893641, under binding 3's stage 3 (v2). It is COMPLETED, at 01:18:42 and 1.312 node-h. The step line0 is
COMPLETED with MaxRSS 365.2 GiB of the 448G step. Every connect check passed.

**The first attempt, 60889950, is INVALID, not a STOP** (amendment 2 §4; its `receipt.txt`):
- its step asked for 480G against a 487,802M allocation, so `fd_1b_mc.py` never started;
- it wrote no `receipt.json`;
- it cost 1.681 node-h.

**N1 is clean:**
- the exact `wt`, `wr` and `bkgw` rows above the bound number 0;
- the validation agrees for all three;
- the denominator's N1 pairs above number 0 over 65,856 cells, with a maximum of 2.146.

**§2b is the STOP:**
- `denominator.draws_with_nonpositive_cells` holds **892 of the 900** declared draws;
- the 8 unflagged draws are 84, 98, 260, 460, 550, 690, 787 and 835;
- `max_cells` is 62;
- `stop_reasons` is `['2b: 892 draws with a non-positive denominator cell']`.

**The read discipline is clean:**
- of 708 files opened, none had its atime moved;
- the stat records before and after are byte-identical (20,135 sources);
- the tables are byte-identical to the first attempt's.

**The breakdown.** coverage-5b produced a record-only breakdown at the director's request. It is
`b3/receipt-run-60893641/breakdown.{py,out}`, on the campaign branch at `206bfd508ea6a7b9d8737413a3da144c6edd50fa`. It
reads `receipt.json` and the bound modules' constants only, each checked by sha. It is descriptive and reads no bar.

**Per truth:**

| truth | draws | flagged |
|---|---|---:|
| G18 | 0–299 | 297 of 300 |
| AR23 | 300–599 | 298 of 300 |
| the plug-in | 600–899 | 297 of 300 |

- Binding 3 runs G18 and AR23 only. The receipt checks all 900 declared draws, and the truth labels only the seed range.
- **The universes in each draw**, by construction: 38, of which 34 depart in the composite denominator (1 flux and 33
  interaction). The 4 detector universes carry the CV's denominator.
- **The per-row record beside it:** `wr` has a clipped fraction per draw with median 0.0064 and maximum 0.0393.
- **Not in the record:**
  - the cell identities, because `receipt.json`'s `denominator` block keeps only the draw list, `max_cells` and `n1`;
  - the per-draw distribution below its maximum;
  - whether the flagged cells are sparse ones with low d_CV;
  - what the 8 clean draws' universes are.

**A disclosure on reads.** Before the director narrowed the request, coverage-5b read one declared input to rebuild
the clean draws' universes. The input was the flux constraint `sorted_NuEConstraint_FHC_RHC_IMD.txt` (sha `e38ad7d2`).
The lane reports:
- the read was once, through O_NOATIME, from login;
- the file's stat before and after was identical;
- it discarded everything derived from the read, deleted its local copy, and committed nothing that depends on it.

Those derived frequency differences are not findings. They are unadjusted, over about 67 comparisons, and are not in
the record. The breakdown request is where that read came from: the director's item 5 asked for something only the
inputs could answer.

## The rule that decides it

1. **The STOP.** Amendment 2 says at `FD-1B-STAGED-AMENDMENT-2.md:222` @ `b3f27fab`: "**STOP** is only N1 … or §2b
   (`denominator.draws_with_nonpositive_cells` non-empty), on a receipt that completed and wrote `receipt.json`". Here
   §2b is non-empty and the receipt completed, so this is a STOP. It is not an INVALID.
2. **Its consequence.** Amendment 2 §8 at `:378-382` @ `b3f27fab`, carrying decision item 2 (iii):

   > A STOP of the new receipt, or of `n1` at any truth, ends stage 1 unless Joseph rules otherwise (decision item 2
   > (iii)). It goes to the director and to Joseph unrepaired, with no further redesign.

   Joseph adopted that rule in `DECISION-20261102-joseph-1b-redesign.md:78`, through his answer "Run, with additions
   (Recommended)". Its sha256 begins `9a38b7a8e8f30bb5`. The first STOP was stage 1's N1 stop
   (`FD-1B-STAGED-STAGE1-STOP-REPORT.md`, #696), and this is the second.
3. **The mechanism, as the declaration anticipated it.** Amendment 2 says at `:464-471` @ `b3f27fab` that, in a toy
   fixture, first order's sum of about 37 per-universe departures "drove a sparse cell's composite denominator to ≤ 0".
   It added: "The same mechanism could operate there in sparse cells. §2b then fails closed, and the receipt reports it
   as a STOP, as designed."

   The record is consistent with that mechanism, but it does not test it: the breakdown above lists what the record does
   not hold. <!-- absence-ok: scoping the mechanism reading to what the record measures -->

**So stage 1 has ended, unrepaired.** S1-0b, `clipcheck` and the bulk (binding 3's stages 4–7) do not run. No
redesign is opened. coverage-5b holds and launches nothing. The campaign branch stays as it is.

**Joseph may rule otherwise.** That would mean a new, post-hoc declaration that he authorizes. The director doesn't
recommend it: none of the options named below (a product form, fewer universes, coarser cells, excluding cells) was
declared before the STOP. Any of them would be chosen after seeing it, and the first-order composition was itself
the redesign after the first STOP.

## What this licenses, and what it does not

**It licenses:**
- "the declared 5D coverage test (1B) did not run to a result": its stage-1 receipt stopped under a declared
  fail-closed rule;
- in the note and the report, a description of that rule and of the counts above.

**It does not license:**
- **any statement about whether the 5D intervals cover**, in either direction. The STOP concerns the declared
  composition of the natures, not the estimator's coverage;
- "first-order composition is invalid in 5D", or any mechanism claim. The record does not test a mechanism; see §3 above;
  <!-- absence-ok: scoping what this record licenses, not a claim that a result does not exist -->
- **anything about the 2D result.** The 2D receipt's truth cells are a different binning, and there no declared draw
  made a cell non-positive. The smallest draw-to-CV ratio was 0.379 at G18 and 0.369 at AR23
  (`COV2D-DECLARATION.md:473` @ `3d976a76`). That is a property of COV2D's receipt, not of its result, which is not yet
  reported.

**The paper and the note.** This record changes no text. The paper's existing statement on 5D coverage stands as it is.
Any change in wording, and the question of whether the measurement's headline narrows, belong to the publication-scope
decision (OI-205). That decision is Joseph's, and its wording options go through a PRD-referee read first.

**Moot unless Joseph overrides (iii):** binding 3 ruling 1's reserved item, whether the plug-in truth belongs in 1B
(`FD-1B-STAGED-BINDING-3.md:52` @ `3d976a76`).

## The independent read

**agy** (Antigravity, a different model family) was consulted through the interpreter session. Its prompt and answer
are committed verbatim in `state/measurement-paper/5d-community-20261024/fd/consult-1b-receipt-stop-20261106/`
(`AGY-PROMPT.txt` and `AGY-ANSWER.txt`). It recommended accepting the STOP as terminal, which agrees with rule (iii).

**Where the director's brief to agy fell short:**
- **It omitted rule (iii).** It offered a redesign as an open option, when the adopted rule already ends stage 1 with no
  further redesign unless Joseph rules otherwise.
- **It misplaced a quoted phrase.** It attached "a property to report, not to test away" to the rule itself. In
  amendment 2 (`:471`) the phrase closes the paragraph on the toy fixture's denominators.

**Where the director does not adopt agy's answer.** The interpreter flagged these points, and the director checked them
against the records:
1. **"Where COV2D is sound", and "supported by empirical coverage validation (COV2D)".** These assume COV2D's result,
   which is not yet reported. Nothing here rests on it.
2. **"Cannot resolve the unfixable rounding instability", and "weeks of compute".** The redesign option made neither
   claim. The brief said "weeks", not compute.
3. **"Directly contradicts the pre-declared rule".** A new, post-hoc declaration would not break amendment 2's rule. It
   does run against decision item 2 (iii)'s "no further redesign", unless Joseph overrides that.
4. **"Physical measurement scope narrowed to 2D", and the "exact qualifier" agy proposes.** Both are scope and wording
   choices for OI-205, not this record's.
5. **"A structural limitation … not a statistical artifact".** This is agy's reading. The record does not test it.

## Where it goes

- **Joseph:** informed, and the default (iii) stands unless he rules otherwise.
- **The publication-scope package** (OI-205, the Codex scope lane): its 5D-coverage row reads "1B stage 1 ended,
  §2b STOP under rule (iii)".
- **The register:** updated to match.
