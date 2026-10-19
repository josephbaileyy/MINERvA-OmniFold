# Plain-language pass 2: frozen brief (themes A–D, the abstract budget, cross-model rounds)

**Owner:** the paper-tighten lane, as director (Stage F), 2026-10-18, under
[`DECISION-20261018-joseph-plain-language-pass2`](../../../DECISION-20261018-joseph-plain-language-pass2.md).
**Base:** `main` `34650231` (pass 1, PR #161). Pass 1's brief [`PLAIN-LANGUAGE.md`](PLAIN-LANGUAGE.md) still applies
except where this brief says otherwise.

**CITABLE FOR:** the rules, scope, workflow and acceptance of pass 2.
**NOT CITABLE FOR:** any claim or number beyond those listed under theme A; final wording (J3–J5 provisional until
the review with Ben); any outward act (J6).

## 1. What changes from pass 1

| pass-1 rule | pass 2 |
|---|---|
| C1: no number added or removed | **Theme A.** Numbers the text hedges around are added where a reader expects them and can read them in place. Each comes from a committed record or a values macro and is cited in a LaTeX comment. Each is listed in the implementation record with its source. A number leaves the paper or primer only by moving to the note (theme B) |
| C2: every caveat stays attached to its claim | **Kept in the body.** In the **abstract**, only the limitations a reader needs in order not to misread a headline result. Every other limitation is stated once in the body, at the claim it qualifies |
| C3: no change of claim strength | **Kept**, except theme C: paper F1 (the failed five-dimensional coverage test is stated as miscoverage at the tested truths) and F15 (the rejections are of the hybrid null hypotheses for the five predictions) |
| C4: nothing moves between deliverables | **Theme B.** History and repeated caveats move from the paper and primer to the note: paper P2–P9, P15, P16; primer P1–P9 and P-new-3; note P1–P5. Before an item leaves, its content must be in the note at the cited location, checked by grep, or added there first (P6). The paper keeps a one-clause pointer where a reader needs one |
| scope (§2 there) | **Theme D** adds the bibliography's internal titles and its three missing locators (`publication.bib`, `technote.bib`) and `result_status_rows.tex`. The `\pubhold` text, the acknowledgments, the "GENIE CV" label and the figures stay out |
| reviews check for loss | **Reviews check both directions:** for a lost or weakened limitation, and for a sentence or qualifier that does not earn its place |

**Length budgets:**
- the paper's abstract: about 150 words;
- the primer's abstract: about 150 words;
- the paper: at most 12 pages, and expected to shrink.

## 2. Workflow

1. **X1, diagnostic rounds.** Two outside models, Gemini 3.8 Flash via agy and GPT-6.1-sol via codex-school, each
   run two prompts on the pass-1 PDF text:
   - a domain-expert PRD referee report, with a presentation critique and a rewritten abstract;
   - a paragraph main-idea and outline analysis of the paper and the primer.

   The runs are read-only and in the director's scratchpad. Their output is advice.
2. **Sources for theme A.** A Claude agent finds each candidate number's committed source and judges whether
   readers expect it.
3. **X2, rewrite rounds.** Both outside models rewrite the abstract and the worst sections (paper IV B, VI A–C, VII;
   primer pp. 8–11) in PRD style, from the pass-1 text plus the theme-A sources.
4. **Integration.** Claude writers produce the new text. They use the X1 findings, the best of the X2 rewrites
   (evaluated against the base for content), the theme-A numbers and the theme-B moves.
5. **Review.**
   - An independent Claude preservation review, in both directions.
   - X3: both outside models re-review the rebuilt PDFs with the X1 prompts, so the before and after are comparable.
6. **Fix, build, merge.** The final PDFs go to Joseph.

## 3. Acceptance

1. `check_invariance.py` against `34650231`. Each difference is explained:
   - a theme-A number with its source;
   - a theme-B move with the note location that carries it;
   - otherwise the reason.
2. The four builds in a scratch copy: rc 0, no unresolved references, both gates PASS, and pytest passes. Page counts
   and the abstracts' word counts are reported.
3. The preservation review's MATERIAL findings are fixed, and the fixes are verified.
4. The before and after of the X1/X3 outside reports are reported to Joseph.

**Model caveat:** the integration and preservation review are Claude Opus 5.5 on claude-school. The outside models
reduce, but do not remove, the single-model bias. Ben is the first human outside reader.
