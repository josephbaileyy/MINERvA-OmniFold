# Caveat density after the targeted round (#731): the paper at b9849126 (2026-11-03)

**Asked for by** the director: one full re-measure of #731's head `b98491263d18…` against `97e30dda`. It is
information only, because Joseph retired the density gate (`DECISION-20261103-joseph-retire-density-gate.md`, #729).

**Done by** the limitations-catalog session, read-only on the paper:
- `../remeasure.py` built and blinded the paper;
- one fresh coder coded it under the committed prompt (`../CODER-PROMPT.md`) and codebook (`../../caveat-study/CODEBOOK.md`);
- the coder ran as an in-session claude-school subagent.

**CITABLE FOR:** the paper's caveat measures at `b9849126`, by the 10-25 caveat study's procedure.

**NOT CITABLE FOR:**
- a change smaller than the coder spread, about ±25% (`../../caveat-study/REPORT.md` §2.4). Every change below is
  inside it;
- a gate (retired);
- the note, which was not re-coded.

## Result

| paper at | words | statements | distinct | distinct /1k | statements per caveat |
|---|---|---|---|---|---|
| 97e30dda (#711; `../after-711-97e30dda/`) | 7,752 | 136 | 77 | 9.93 | 1.77 |
| **b9849126 (#731, the targeted round)** | **7,073** | 119 | **65** | **9.19** | 1.83 |

**By kind**, distinct caveats at 97e30dda and at b9849126:
- (a) history: 5 and 3;
- (b) deviation: 3 and 2;
- (c) untested or omitted: 41 and 36;
- (d) scope: 24 and 21;
- (e) process: 4 and 3.
<!-- absence-ok: names the caveat category "untested or omitted" used to classify statements; not a claim that any result is absent from the repository -->

**The change:** −12 distinct caveats and −679 words, so the density is 7.5% lower. That is inside the coder spread.
The two counts come from different coders, as every comparison in this series does.

## Where the change comes from

**The mechanical lower bound.** Of 97e30dda's 77 coded caveats, 62 still have a verbatim statement in the new text
and 15 do not. Each of the 15 belongs to a row of the round (`targeted-round-paper-20261103/REPORT.md` on #731's
branch); the mapping is mine:

| round row | 97e30dda caveats with no surviving statement |
|---|---|
| T7, III A moved whole | the precision target not met; the envelope a diagnostic, not an interval |
| T8, IV D's background closure moved whole | purity subtraction's closure bias; the treatment dependence; the unpaired pseudo-experiments |
| T9, V C moved whole | the 3D/4D values lack uncertainties, under (c) and (d) |
| T1, the E_avail comparison tightened | the definition differs from the published ones (d) |
| T2, the run-period block's size tightened | the block's size poorly determined |
| T3, "no finite-ensemble correction" to the note | that caveat |
| T4, the fake-data inference to the note | the run-period block not validated (that sentence's coding) |
| T5, GiBUU's footnote shortened | the post hoc check of B3's premise; the internal check name B3; the hydrogen sample's quality |
| T6, the χ² bands' negations to the note | the flux-bootstrap bands are not intervals |

- **The whole moves (T7–T9)** remove 7, as R-P9 priced them (#728: III A 1–2, IV D's closure 3, V C 2).
- **The tightenings (T1–T6)** account for the other 8.
- **The fresh count fell by 12, not 15.** "No verbatim statement" is not "no caveat": some reworded sentences still
  carry their caveat, for example T2 keeps "poorly determined" and T5 keeps the failed check. The fresh coder labels
  these sentences anew.

**Words:** −679 in all. The three whole moves were priced at −590 words.

## Measurement notes

- **Back matter leaked in this layout, and `remeasure.py` now removes it.**
  - pdftotext printed the acknowledgments and the data-availability statement before their heading. The study's
    `blindcount.py` cuts from that heading, so the text would have counted as body: 36 lines, 343 words.
  - `remeasure.py` now drops such text: runs of at least three lines whose letters lie in the back matter's, as
    `main_paper.tex` prints them. It is the companion of its Limitations-item guard.
  - **The baselines stand.** On 97e30dda and 58fa0b89 the new step drops nothing, and their blinded texts keep their
    coded hashes (`2c881c60…`, `286cd1f6…`).
  - One short line of the statement, "decision.]", is below the step's 20-letter minimum and stays in the counted text
    (1 word). The coder noted it.
- **`remeasure.py` no longer writes into the inventory's tree.** The paper rewrite lane ran it and found its tracked
  `tables/` rewritten; they restored them. The tally now reads a copy of the inventory under `--work` and writes its
  tables there. They reach the repository only through `--tables-out`, as they did here.
- **A correction to #728** (`../rp9-reprice-97e30dda/`), found by the paper rewrite lane:
  - III A's third note probe matched an unrelated sentence;
  - the fact does print in the note ("These envelopes are sensitivities: …", sec_5d.tex), and the probe now targets
    it;
  - the count is unchanged at 35 of 38.

## Reproduce

    python3 -I ../remeasure.py --work <scratch> --repo <checkout at b9849126> --inv after-731-b9849126/inv \
        --tables-out after-731-b9849126/tables

This exits 0. `inv/CODED-ON.sha256` pins the blinded text that was coded (`837628bb…`).
