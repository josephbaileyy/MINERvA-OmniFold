# The paper body's sentence pass: meaning read and PRD read for flow (2026-11-12)

**What changed:** paper_body.tex, from b21bcdf7. The pass followed the director's rules: split sentences, restructure,
and swap no connector for another. It was applied in two scripted steps, kept here so the pass can be re-run and
audited:
- `sentence_pass1.py`: 75 exact replacements of semicolons and ", so", plus the draft-only \pubhold list's ten
  semicolons;
- `sentence_pass2.py`: 22 paragraph breaks at topic boundaries, with no sentence changed.

Untouched:
- the protected spans (the B0 sentences, RS1's paragraph);
- the LISTED_CLAIMS anchors and their paragraph;
- the ONCE sentences, two of which keep a semicolon or ", so";
- check_sec4_receipts' anchors. One replacement would have broken "the residual against the changed truth reaches";
  it is a colon instead.

**Meaning read** (`pairs.txt`, 56 changed sentence groups). An independent general-purpose subagent, read-only, found
45 OK, 5 NOTE and 6 DEFECT. All six were fixed with the reader's wording:
- four "so" consequences that "and" had lost are restored with "Because …" or "therefore": the efficiency correction,
  the universe weights of unmatched events, the stability pass on pseudo-data only, and the unmitigated instability;
- "Its number of degrees of freedom" became "The number of degrees of freedom of each χ²";
- "All use simulated pseudo-data" now names the four test kinds.

Three NOTEs were taken: "The target is then D − B pointwise", "The output's limitations", and "The benchmark … / The
rules …".

**Metrics** (check_style's function on the body, base b21bcdf7):
| metric | before | after | references median / max |
|---|---|---|---|
| semicolons /1000 w | 7.5 | 0.9 | 0.9 / 3.4 |
| ", so" /1000 w | 2.0 | 0.2 | 0.3 / 0.7 |
| median paragraph | 133 | 101 | 81 / 111 |
| % over 150 w | 38 | 10 | 20 / 32 |
| words/sentence | 25.4 | 21.8 | 20.85 / 22.8 |

The paragraphs still over 150 words are:
- the variant groups' source, which counts every alternative while one prints;
- the draft-only \pubhold;
- the B0 paragraph, which is protected.

**PRD read for flow** (an independent general-purpose subagent on the blinded rater copy of this head): MINOR,
style 6/10. No further restructure is needed. Its local items are queued for the next commit, the PRD flow batch:
- definitions before use: ρ, the §5.3 notation, the first coverage test, hybrid truths;
- dangling "It", "These" and "This" openings after the splits, and four orphaned short paragraphs;
- one name per truth, and "passes"/"is flagged" as the only verdict verbs;
- a list of repeated caveats to reduce to one statement plus a pointer;
- the remaining semicolons, which sit in the protected B0 and RS1 spans and in two ONCE sentences. They go to the
  director (B0 and RS1) and to the ONCE list.
