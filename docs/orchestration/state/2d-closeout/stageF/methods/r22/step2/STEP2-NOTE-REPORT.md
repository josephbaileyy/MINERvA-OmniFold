# r22 Step 2, the note round: report (2026-10-30)

The round followed [STEP2-PLAN.md](../STEP2-PLAN.md). The note is rewritten for register, piece by piece, on the
in-scope WORDING and STRUCTURE gaps of Step 1. Every piece is adopted under the rule committed before any score
(§4). The note's sol2 P1N piece mean rose from 3.122 to 3.222, against a target of 3.875. Under the stopping rule
(§5), that rise is movement, so the rounds continue. Nothing is submitted, deposited or tagged. The paper is
unchanged in this round.

## What was rewritten

- **Gaps.** 197 in-scope note gaps were rewritten, 8 to 16 per piece (`gaps-ws.tsv`; its 13 paper gaps are for the
  paper round). Each piece had one writer, following [WRITER-BRIEF.md](WRITER-BRIEF.md) and its list in `briefs/`.
- **Fact ledger.** Each writer kept a fact ledger ([ledger.md](ledger.md): 541 rows, 910 probes). Every probe holds:
  `check_ledger.py --no-n4-frozen` reports 0 failures.
- **Two-direction review.** A review following [REVIEW-BRIEF.md](REVIEW-BRIEF.md) produced 69 findings, 68 of them
  fixed.
- **Director's rulings.** STEP2-PLAN.md §7 records them. The PPFX expansion and the B03 GENIE glosses were reverted to
  cited text. Parts of those glosses had survived integration; the agy triage found them and they are now gone.
- **Records-move gate.** The first integration failed it with about 36 P7 probes. Integration restored the KEEP pins
  and the lost facts, re-pointed 23 probes (each marked "probe updated for r22 Step 2"), and added row L-r22-1.
- **agy agreement check.** [agy/AGY-REPORT.md](agy/AGY-REPORT.md) covers it. The control caught 26 of 26 planted
  negations. Of the 193 flagged passages, 22 were real changes in meaning, and all 22 are fixed to base wording. Two
  dropped `\pageref` calls are restored. The joint-test conditions now say that they are a restatement.
- **The note abstract's two pairs.** B01-s-04 (pin `d2075a04421dcc5e`) and B01-s-10 (pin `2b0420a3ab1e1432`) are
  applied as Joseph approved them, in
  [DECISION-20261030-joseph-note-abstract-pairs.md](../../../../../../DECISION-20261030-joseph-note-abstract-pairs.md)
  (#536). They are registered in `check_ledger.py`; a changed abstract fails the check, and the approved one passes.

## The B01 discard

B01's seven adoption runs (P2N sol2 and gemini in both orders, and P1N r1–r3) were run first on the pairless B01.
All seven had finished before #536 arrived. As the director ruled, they were discarded unread and rerun on the B01
that carries the pairs, which is the text that would be adopted. The discarded runs are not committed. Their status
rows and the reason are in
[runs-discarded-B01-pairless/](runs-discarded-B01-pairless/README.txt). The first seven B01 rows of
`runs/status.tsv` are the discarded runs.

## Adoption (§4)

The measured pieces are in `pieces/`, cut by `tools/split_base.py` from main_note.pdf at commit `97bf3571`. B02–B15
are byte-identical to the cut at `1b872953` on which their runs were made. The base pieces are `../base/pieces/`,
and the base P1N runs are `../measure/P1N__<id>__sol2__r{1,2,3}.txt`. `tools/adopt_step2.py` writes
[runs/adoption.tsv](runs/adoption.tsv). The rater outputs are committed verbatim as `runs/<P2N|P1N>.<id>.<model>.<AB|BA|rN>.txt`,
which is Step 1's `.txt` convention and keeps them outside the absence-claim scan of `.md` files. `adopt_step2.py` reads
them as `.md`; recomputing from copies renamed to `.md` gives a byte-identical `adoption.tsv`:

| piece | P2N NEW wins (of 4) | sol2 same in both orders | P1N new | P1N base | words base → new | adopted |
|---|---|---|---|---|---|---|
| B01 | 4 | yes | 3.5, 3.5, 3.5 | 3.5, 3.0, 3.5 | 1758 → 1807 | YES |
| B02 | 4 | yes | 3.0, 3.0, 3.0 | 3.0, 3.0, 3.0 | 4645 → 4644 | YES |
| B03 | 4 | yes | 3.0, 3.0, 3.0 | 3.0, 3.0, 3.0 | 4088 → 4060 | YES |
| B04 | 4 | yes | 3.5, 3.5, 3.5 | 3.5, 3.5, 3.0 | 2785 → 2846 | YES |
| B05 | 4 | yes | 3.5, 3.5, 3.5 | 3.5, 3.5, 3.5 | 3103 → 3112 | YES |
| B06 | 4 | yes | 3.0, 3.0, 3.0 | 3.0, 3.0, 3.0 | 4548 → 4611 | YES |
| B07 | 4 | yes | 4.0, 4.0, 3.5 | 3.5, 3.5, 3.5 | 2302 → 2340 | YES |
| B08 | 4 | yes | 3.0, 3.0, 3.0 | 3.0, 3.0, 3.0 | 5621 → 5659 | YES |
| B09 | 4 | yes | 3.5, 3.5, 3.0 | 3.0, 3.0, 3.0 | 3766 → 4078 | YES |
| B10 | 4 | yes | 3.0, 3.0, 3.5 | 3.0, 3.0, 3.0 | 6282 → 5820 | YES |
| B11 | 4 | yes | 3.5, 3.5, 3.0 | 3.0, 3.0, 3.5 | 1581 → 1586 | YES |
| B12 | 4 | yes | 3.0, 3.0, 3.0 | 3.0, 3.0, 3.0 | 7058 → 7089 | YES |
| B13 | 4 | yes | 3.0, 3.0, 3.0 | 3.0, 3.0, 3.0 | 5455 → 5421 | YES |
| B14 | 4 | yes | 3.0, 3.0, 3.0 | 3.0, 3.0, 3.0 | 908 → 910 | YES |
| B15 | 4 | yes | 3.0, 3.5, 3.0 | 3.0, 3.0, 3.0 | 2067 → 2360 | YES |

- **Pairwise.** NEW won 60 of 60 pairwise runs. All 105 runs answered on the first attempt; none failed. The
  STRENGTH answers (1 slight, 2 clear, 3 strong):
  - sol2: 1 in 7 runs, 2 in 23;
  - gemini: 2 in 25 runs, 3 in 5.
- **P1N.** No piece's P1N mean fell. Seven rose and eight were unchanged. No lowest run fell below the base's lowest
  run.

Since every piece is adopted, nothing reverts. The adopted note is the tree at `97bf3571` together with the records
added by this report's commit.

## Score and the stopping rule (§5)

- **Note.** The sol2 P1N piece mean is 3.122 for the base and 3.222 for the new note, against a target of 3.875. This
  is movement: the mean rose. Over the 45 runs, the rating total rose by 4.5 points, that is, nine 0.5 steps net.
- **Paper.** Not measured in this round, because the paper is unchanged. The paper round follows.
- **Resolution limit.** P1N's resolution in the 3 band is low.
  - Base runs: 34 of 45 are exactly 3.0, and 11 are 3.5.
  - New runs: 27 are 3.0, 16 are 3.5 and 2 are 4.0.
  - The rise is therefore nine 0.5 steps net, over 45 runs. That is a coarse signal, and the round's P1N result
    should be read at that resolution.

## Length

The writers' brief said not to lengthen any piece. Two measures disagree on how much the note grew:

- **Piece total.** The pdftotext piece total rose from 55,967 to 56,343 words, by 376 (+0.7%). Of that, B09 (Sec. 10)
  rose by 312, B15 (Apps. G–I) by 293, and B10 (Sec. 11) fell by 462.
- **Source total.** Comment-stripped source words, summed over the note's .tex files, rose by 63. The largest changes
  are:
  - sec_joint.tex −167, where the verbatim joint-test conditions moved to the records;
  - app_negweight.tex −109;
  - app_statmethods_nd.tex +79;
  - sec_3d.tex +73.
- **Why the two differ.** sec_fived16.tex, the main source of B09, is unchanged in word count. So B09's +312 is text
  that now prints inside Sec. 10's page range. That fits a float of a neighbouring section being placed differently.
  It also fits macro expansion, and the running header and page number of the extra page. The gap between the two
  measures is not attributed further here.
- **PDF.** main_note.pdf grew from 126 to 127 pages.

## Exceptions and registry changes

- **Out-of-scope check.** 67 out-of-scope quotes were checked, with 1 failure, B09-g-09. B06 added a table, which
  renumbered Table 15 to Table 16 in the quoted sentence. The source of that sentence is unchanged, so this is
  recorded as an explained exception. B12-g-02 was skipped as UNVERIFIED, since it is not located at the base.
- **Registry.** ALIASES rows 2, 35, 57 and 67 cite note lines whose digests changed. Each was re-cited with
  `check_registry.py --cite`, and `results_index.py --write` regenerated the index (commit `ee520a19`).
- **records-move-ledger.md.** Row L-r22-1 was added (READER `2e4dfdaf3190`). L-thin-C58's probe follows the restored
  Rvp1pi wording.

## Limits of this round's evidence

- **The rule cannot fail here in practice.** NEW won every pairwise run, so §4 decided nothing at the margin. A
  uniform preference for the edited version would look the same. Both orders were run, which rules out position
  bias, but a preference for any careful edit is not excluded.
- **The raters judge register, not correctness.** Correctness rests on the fact ledger, the two-direction review,
  the agy check and the gates. The agy check covers only flagged passages: one unflagged gloss (SY118) was found by
  triage. <!-- absence-ok: states a limit of a check's coverage, not a result -->
- **The triage, review and integration were done by agents in this lane.** Each REAL finding quotes base text, so a
  reader can re-check it.

## Next

- **Paper round.** Use G1b's in-scope paper gaps and the pinned A1/A4 pairs for Joseph. Apply the B4 re-pin of
  `registry/ALIASES.tsv:38` and ATTRIBUTION, with a record naming the old and new digests (§7 ruling 4).
- **Following round.** #534's 41 allowed gemini gaps enter the next round (§7 ruling 5), now that this round is
  measured.
