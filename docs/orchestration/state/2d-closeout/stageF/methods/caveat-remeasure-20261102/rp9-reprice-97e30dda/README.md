# R-P9 re-priced from the measured 77: secondary results moved whole to the note (2026-11-03)

**Asked for by** Joseph's decision `DECISION-20261103-joseph-711-merge-and-rp9-reprice.md` item 2 ("Re-price R-P9 from
77"), through the director. For each candidate secondary result that would move whole to the note, this gives:
- the facts that leave the paper;
- the change in distinct caveats and words, under the caveat study's unit;
- the pointer each move needs, and its note-prints-it probe;
- which combination reaches ≤ 6 per 1k, if any does, and what the paper would then no longer report.

**Done by** limitations-catalog. **Nothing in the paper moved:** every edit was made to a scratch copy. The director's
PRD-referee read is below ("The referee read").

**CITABLE FOR:** the price of each move, and of the combinations measured, at `97e30dda`.

**NOT CITABLE FOR:**
- a decision;
- a change smaller than the study's coder spread, about ±25% (`../../caveat-study/REPORT.md` §2.4). Every change
  below is inside it;
- how a referee would judge a move. The "referee" column is my reading, for the PRD-referee read to check.

This supersedes the starting point of `../cutlist/RP9.md`, which priced from 44 caveats, a number the merges never
reached (`../after-711-97e30dda/README.md` §2).

## The answer

1. **No combination of whole moves reaches 6 per 1k.** The lowest measured is **9.25–9.41 per 1k**. That is every
   candidate moved except IV E, with the abstract's two-dimensional sentence cut: 57–58 distinct caveats in 6,162
   words, against 77 in 7,752 (9.93) now.
2. **Why.** The candidates' caveats are about as dense as the paper's, so moving their words with them barely
   changes the rate. IV E is less dense than average, so moving it **raises** the rate, to 10.37 alone and 9.74–9.91
   with everything else.
3. **What 6 per 1k would take.** In the best configuration, 6,162 words allow at most 36 caveats. That means
   removing about 21 more caveats from the text that stays. Those caveats sit in the main result's own sections: the
   comparison with predictions (13), the data and simulation (7), the reported covariance (7), the Limitations (7),
   the fake-data tests (6) and the extraction (4). That is a different decision from moving secondary results.
4. **Two facts the note does not print** would have to be added to it before their moves (below): the 2D section's
   "no statement about the size of the published analysis's residual", and IV F's comparison with the 0.37%
   data-bootstrap uncertainty.

## Each candidate

Δ is against 77 distinct caveats and 7,752 words. A range comes from one borderline coding (adjudication below).

| move | what leaves the paper | Δ distinct | Δ words | per 1k | pointer | note prints it | referee |
|---|---|---|---|---|---|---|---|
| **III A**, reporting definitions, precision target, envelope | the 10% target and its miss; the envelope as a diagnostic (2 caveats) | −1 to −2 | −187 | 9.91–10.05 | one sentence in III B; III B's first sentence, IV's opening and IV A's envelope clause re-pointed; the conclusions' second finding cites the note | 3 of 3 | movable; the conclusions' finding is re-pointed |
| **IV B + IV C**, the 2D benchmark (Fig. 1) and covariance; the abstract kept | the end-to-end test against the published result, and its 2D covariance: 11 caveats, including the learner chosen after comparison, the unexplained flux difference, the 2D covariance not validated, and the earlier undercovered band | −11 | −883 | 9.61 | one paragraph after IV A; the introduction, the roadmap, III's estimator sentence and V B's reuse sentence re-pointed; the Limitations sentence on the 2D covariance cut | 13 of 14 (**NOTE FIRST:** "no statement on the published residual") | **keep**: the abstract states the reproduction |
| the same, with the abstract's 2D sentence cut | as above, and "the shape difference is unexplained" | −12 | −898 | 9.48 | as above, and an abstract edit | as above | **keep**, and the abstract changes |
| **IV C alone**, the 2D covariance | 5 caveats: the seed block's size, the flux difference, the omitted terms, the run-period check by construction, no statement on the published residual | −5 | −415 | 9.81 | one paragraph after IV B; Fig. 1's caption re-pointed | 4 of 5 (**NOTE FIRST:** as above) | movable with a summary |
| **IV D's background closure** (Fig. 2) | purity subtraction's closure bias, the treatment dependence, the unpaired pseudo-experiments (3) | −3 | −300 | 9.93 | one sentence in IV D; Fig. 3's caption and the introduction re-pointed | 5 of 5 | movable |
| **IV E**, generator-sized truth changes (Fig. 3) and an earlier estimator's coverage | the development-variant test, an earlier covariance failing its criteria, an earlier estimator miscovering (3); the pointer itself codes as one history caveat | −2 | −517 | **10.37** | one sentence after IV D; the conclusions' first finding and III's estimator sentence re-pointed | 5 of 5 | **keep**: the conclusions' first finding |
| **IV F**, input rounding | the instability under rounding (1) | −1 | −99 | 9.93 | one sentence | 3 of 4 (**NOTE FIRST:** the 0.37% comparison) | **keep**: it bounds how exactly the central values reproduce |
| **V C**, 3D/4D descriptive comparisons | the 3D and 4D values carry no uncertainties, under (c) and (d) (2) | −2 | −103 | 9.81 | the introduction's sentence | 2 of 2 | movable |

The labels each move removes are in `singles.json` (`caveats_gone`), and the edits themselves in `reprice.py`
(`CANDIDATES`).

## Combinations, built and measured

| moves | distinct | words | per 1k |
|---|---|---|---|
| none (`97e30dda`) | 77 | 7,752 | 9.93 |
| everything except IV E, with the abstract sentence cut | 57–58 | 6,162 | **9.25–9.41** (the lowest) |
| everything, with the abstract sentence cut | 55–56 | 5,649 | 9.74–9.91 |
| only what a referee would not expect kept: III A, IV C, IV D's closure, V C | 65–66 | 6,735 | 9.65–9.80 |

**What the lowest configuration no longer reports:**
- the 2D benchmark against the published result, with Fig. 1, and its covariance, so the abstract's reproduction
  sentence goes too;
- the precision-target study and its envelope;
- the background-closure study, with Fig. 2;
- the sensitivity to input rounding;
- the 3D and 4D descriptive comparisons.

Each would print only in the note. The single-move numbers add up: the built combinations match their sum within one
caveat and 15 words.

## The referee read (director, Gemini, 2026-11-03)

The read is committed verbatim beside this file, with `SHA256SUMS`:
- `PRD-REVIEW-RP9-GEMINI-PROMPT.txt` (`a8e02d0f…`): the director's questions, this README, and pdftotext of the
  paper's standalone build at `4384f022`, the same paper as `97e30dda`;
- `PRD-REVIEW-RP9-GEMINI-ANSWER.txt` (`c5eac29d…`).

It agrees that IV B stays and that IV E is condensed rather than moved. It endorses moving III A, IV C's detail,
IV D's closure, IV F and V C, and it names over-qualified sentences in the main result's sections.

**Two points disagree with earlier reads. They are recorded here, not resolved:**
1. **IV F (input rounding).** This read endorses moving it: "a numerical/computing sanity check … summarized here in
   at most one sentence". The 11-02 read of the cut list (`../cutlist/PRD-REVIEW-GEMINI-ANSWER.txt`) objected to
   moving it (MV15), as a "Strong objection" ("Keep in main paper"), because of the instability of up to 2.6σ. Joseph
   kept MV15 in the paper, condensed (`DECISION-20261102-joseph-caveat-cut-list.md` item 2).
2. **The ≤ 6 target.** This read calls it "an arbitrary, counterproductive proxy". The #707 read called "~6 per 1,000
   words … an appropriate, realistic target" (same file, line 37; the 11-02 decision record paraphrases it as
   "reasonable").

## How it was measured

- **One edit set per move** (`reprice.py`), applied to a copy of `docs/analysis-note` at `97e30dda`:
  - the moved text is deleted;
  - each sentence elsewhere that cites it is cut or re-pointed to the note;
  - one pointer sentence is added.

  Every edit's anchor must occur exactly once, and the build fails on any unresolved reference.
- **Each copy is built and blinded by `../remeasure.py`**, as the paper was, and tallied against the inventory coded
  at `97e30dda` (`../after-711-97e30dda/inv/`). The control run of the unedited copy reproduces 7,752 words, 77
  distinct and the coded text's hash `2c881c60`.
- **The study's unit:**
  - a statement leaves when its quote no longer verifies;
  - a distinct caveat (kind, label) leaves only when all of its statements have.
- **Two layout corrections** (`reprice.py` docstring):
  - **Quotes broken by layout.** A quote broken by a float or a renumbered section letter, whose words are unchanged
    in the source, is kept. There are 0 to 5 such statements per run.
  - **Leaked back matter.** In four of the twelve layouts (IV C, IV F, V C and the all-moves combination),
    acknowledgments text landed before its own heading, which the blinding cuts from. That text (5, 34, 34 and 6
    lines) is removed from the word count. Without this correction IV F and V C would each have *gained* about 340
    words.
- **What the edits add**, coded blind (`coder/`):
  - The pointer and re-pointed sentences of each move were coded by a fresh coder under the study's codebook, with
    nothing else. That coder ran as a claude-school subagent.
  - The sets were shuffled (seed 20261103) and carried no move names.
  - A control set of three known caveats and three non-caveats from the paper was coded 3 of 3 and 0 of 3.
  - The rule (`adjudication.json`):
    - where an edit leaves a sentence's caveat words unchanged, the base coding governs;
    - new text that codes as a caveat adds one.
  - The result:
    - IV C's re-pointed Fig. 1 caption, and IV B + C's Limitations sentence, still carry their caveats, so the
      survival measure's loss of them is reversed;
    - IV E's pointer adds a history caveat;
    - III A's reworded sentence is borderline (0 or 1).
- **The note probes** (`note_probes.py`, `probes.json`): 38 facts the moved text prints, each searched as its value or
  phrase in the note's blinded text at the same commit. 35 are printed. A hit shows the note prints the value, not
  that its sentence matches the paper's.
  - **Correction (2026-11-03, found by the paper-rewrite lane):** III A's third probe,
    `envelope.{0,80}(not an interval|diagnostic)`, matched an unrelated sentence of the extended-domain section
    ("three-prior dependence envelope, … containment diagnostic"). The fact does print in the note, in sec_5d.tex's
    "These envelopes are sensitivities: they provide no probabilities, …", which the probe now targets. The count is
    unchanged at 35.

## Reproduce

    python3 -I reprice.py --src <dir holding docs/analysis-note at 97e30dda, main_note built> \
        --inv ../after-711-97e30dda/inv --work <scratch> --out singles.json
    python3 -I reprice.py --src … --inv … --work … --only "" --out combos.json \
        --combo IIIA+IVBC+IVDbkg+IVE+IVF+VC+ABS2D --combo IIIA+IVBC+IVDbkg+IVF+VC+ABS2D --combo IIIA+IVC+IVDbkg+VC
    python3 -I note_probes.py <scratch>/base/w/blind/ours-note.txt probes.json

Each build takes about 30 s. The scratch copies are not committed.
