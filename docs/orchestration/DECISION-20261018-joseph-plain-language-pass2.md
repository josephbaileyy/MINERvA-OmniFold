# DECISION 2026-10-18 — Joseph: plain-language pass 2 (themes A–D), cross-model critique rounds, and the abstract's length

**Recorded by** the paper-tighten lane, as director (Stage F). The first plain-language pass merged as PR #161 (`main`
`34650231`). Its implementation record
([`state/2d-closeout/stageF/PLAIN-LANGUAGE-IMPLEMENTATION.md`](state/2d-closeout/stageF/PLAIN-LANGUAGE-IMPLEMENTATION.md)
§8) left four themes to Joseph, A–D, each with the director's recommendation. Joseph's answer, verbatim:

> for my decisions: A. Sure do it if it is expected to be there by th readers and it would make sense to the them. B.
> yes move them. C. Yes say that. D. I'm fine with your recommendation. can you try doing some rounds of open-ended
> agy gemini and codex-school 6.1 sol critique. as a different model it probably can reduce some biases. I'm not sure
> if there is precedent for what type of rounds work best but maybe open-ended critique rounds or domain-expert
> critique or having it rewrite paragraphs or sections in a PRD style and evaluating its output or even doing a
> paragraph main idea/outline analysis. just from a brief glance so far, the abstract has gotten pretty large again
> and I wonder why this keeps happening

sha256 of the text plus a final newline begins `b2afa6de60e6885b`.

## 1. What is decided, as the director reads it

| theme | decision | the director's reading |
|---|---|---|
| **A** | state the numbers the hedges stand in for, "if it is expected to be there by the readers and it would make sense to them" | A number is added where a reader of that deliverable expects it and can interpret it in place. Each comes from a committed record, cited in a LaTeX comment. A number that would need a paragraph of definition to make sense is not added |
| **B** | "yes move them" | History and repeated caveats move from the paper and primer to the note. Before an item leaves, its content must be in the note: P6, which has no note home, gets a note sentence first. Every caveat a reader needs to read a result correctly stays with that result |
| **C** | "Yes say that" | The director's recommendation: paper F1 (the failed five-dimensional coverage test stated as miscoverage at the tested truths) and F15 (the generator rejections are rejections of the hybrid null hypotheses). The other C items stay open for Joseph |
| **D** | "I'm fine with your recommendation" | Fix the bibliography's internal titles and the three missing locators, and `result_status_rows.tex`'s internal register. Leave the `\pubhold` text, the acknowledgments' AI paragraph, the "GENIE CV" label (W10) and the figure legends |
| **Cross-model rounds** | "some rounds of open-ended agy gemini and codex-school 6.1 sol critique", of kinds Joseph lists: open-ended, domain expert, PRD-style rewrites to be evaluated, and paragraph main-idea and outline analysis | Run through agy (`gemini-3.8-flash-high`) and codex-school (`gpt-6.1-sol`), both in the account allowlist (DECISION-20261016). Both are read-only, on copied inputs in the director's scratchpad, with no repository write and no network task beyond the model call. Their output is advice: nothing they write enters a deliverable without the same preservation review |

## 2. Why the abstract keeps growing (the director's diagnosis)

The paper's abstract was 117 words on 2026-10-03. It then grew:
- 236 words on 2026-10-06;
- cut to 164 on 2026-10-11;
- 172 on 2026-10-12;
- 231 in the first plain-language pass (`386ece45`), and 233 after its fixes.

Comparable PRD papers run 97–210 words, median 121 (EDITORIAL-20261008 §2b).

The mechanism is a one-way ratchet in how these passes are run:
- **Every review checks only for loss.** Each review asks whether a qualifier was dropped and restores it. None
  asks whether a sentence earns its place in the abstract.
- **The caveat-attachment rule pulls caveats into the abstract.** Pass 1's rule C2 kept every caveat "attached to
  the claim it qualifies". The abstract names every main claim, so it collected every main claim's caveat.
- **Rewording for plainness lengthens.** Definitions and shorter sentences add words. For example, "pass
  marginal-normalization checks" became "pass checks of their marginal normalizations against the lower-dimensional
  results".
- **No pass carried a length budget.** Nothing set a limit on the abstract's length.

**Rule for pass 2:**
- The abstract has a budget of about 150 words.
- It carries the headline results and only the limitations a reader needs in order not to misread them. Every other
  limitation is stated once, in the body, with its claim.
- Every review checks in both directions: for loss, and for a sentence or qualifier that does not earn its place.

## 3. Not decided

- The C items other than F1 and F15.
- The final wording: J3–J5 stay provisional until the review with Ben.
- Any outward act (J6).
