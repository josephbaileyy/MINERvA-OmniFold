# The caveat cut-list paper round: the independent two-direction review, with dispositions

**The reviewer:** a fresh general-purpose subagent, read-only. It was given:
- the diff `589eb47d0..681eaa6f6` (after the rebases onto `20ab8d002` and `3971bbb47`, `ad83db6af`), with both builds;
- the director's work order, verbatim;
- the cut list (#706) and the Gemini PRD review (#707);
- the held-sentence registry;
- the 1B authorities: `DECISION-20261102-joseph-1b-redesign.md`, and the staged declaration, stage 0 report and stage 1
  STOP report.

It was not given the writer's conclusions.

**The result:** nothing false and no lost fact. Every removed or reworded base sentence still prints in the paper or the
note.
- No `\fvval` key changed, and every `\nsec` target exists.
- G1b:paper-g-14, -19 and -20 print exactly.
- **MV01** attributes the post-hoc addition only to C_PL,5D.
- **MV02**:
  - "No reported interval has validated coverage" is true;
  - "is under way" is not false and not overstated: stage 1 runs on the redesign, stage 0 passed, and no
    pseudo-experiment has run yet.

| # | sev. | finding | disposition |
|---|---|---|---|
| 1 | Medium | IV E's IV F pointer dropped "corrected for the closure bias at nominal truth" and "most strongly when the signal rate is lowered by about 10 %", which the intro's "a coverage test" and the conclusions' lesson rely on | FIXED: the pointer keeps both clauses |
| 2 | Medium | MV08's "against 0.44 for the refined one" reads as exactly 0.44; the base said "within 0.44" | FIXED: "while the refined one lies within 0.44 in every cell" |
| 3 | Medium | MV07's "NuWro's free-proton sample is flagged in its supplement …" garbles the fact, and sits in GiBUU's footnote | FIXED: NuWro's row has its own footnote, "the supplement generated at … 50–100 GeV is flagged: the events lost to generator aborts there were not shown to be negligible"; the caption points to "the footnotes" |
| 4 | Medium | the ledger and its checker were untracked, so the M moves' probes were not yet live | FIXED: committed with the round's records |
| 5 | Low | "its own consistency check cannot fail" now also covered C_PL,5D | FIXED: said of the two-dimensional block only |
| 6 | Low | IV C's block list no longer points to the run-period statement | FIXED: "run period (three period groups; Sec. IV A)" |
| 7 | Low | the new binned and seed pointer repeated IV E's existing pointer | FIXED: folded into that pointer ("the exact binned comparison with its scope, and the joint-test-estimator shapes with the seed sets of their pseudo-experiments") |
| 8 | Low | "Their coverage is stated in Sec. VI A": unclear antecedent | FIXED: "Coverage is discussed in Sec. VI A." |
| 9 | Low | MV15 put the base's "within the data-bootstrap uncertainty" right before "up to 2.6 statistical standard deviations" | PARTLY: the base's own words ("the spread lies inside …") are restored. The tension is the base's, and it goes to the owner (REPORT point 2) |
| 10 | Low | "the covariance rebuilt" simplifies the 1B declaration's Clause M, and the declaration's §12 says the paper is unchanged until a result | REPORTED (REPORT point 1). The wording is Joseph's approved method sentence; the work order asks for the status now |
| 11 | Low | the note's "three held-out shapes" sat next to "not held out" seeds | FIXED: "three shapes not used in the joint-test estimator's selection" |
| 12 | Low | a `% Search:` anchor sat above text that moved | FIXED: it moved beside IV A's run-period statement |

**The register note** (MV04, MV08 and MV10 mostly join sentences; MV06's long clause):
- MV06 is two sentences now, and MV04 two.
- MV08 is three. Its bound receipt phrases limit reordering (REPORT point 3).
<!-- absence-ok: dispositions of a review; it quotes the paper's caveats -->
