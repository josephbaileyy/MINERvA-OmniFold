# Decision packet: 2D closeout J3–J6 (claims, disclosure wording, KI-85, outward acts)

**Prepared by** the paper-tighten lane, as director (Stage F), 2026-10-18, for Joseph and for the review with Ben.
**Base:** `main` `b246c253` (phase 2 merged, PR #157). Line numbers are at that commit.

**CITABLE FOR:** the open decisions, their options, the director's recommendations, and where each lands.
**NOT CITABLE FOR:** a decision. Every choice here is Joseph's. Nothing in it changes a deliverable until he decides.

## 0. Where things stand

- **Adopted:** Q = S5 total + C_PL (J1, J2; [`DECISION-20261017`](../../../DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md)).
- **Numbers and figures are in the documents:**
  - phase 1 produced them ([`rebuild/REPORT.md`](rebuild/REPORT.md));
  - phase 2 wrote them in ([`rebuild/PHASE2-IMPLEMENTATION.md`](rebuild/PHASE2-IMPLEMENTATION.md)), with an
    independent review and all four PDFs building in a scratch copy.
- **Where the open text is:** every sentence still waiting on you carries a `% J3 pending` or `% J4 pending (Dn)`
  marker in `docs/analysis-note/*.tex`. There are 52; `grep -n 'J[345] pending' docs/analysis-note/*.tex` lists them.
  The Dn ids point to [`DRAFT-disclosures.md`](DRAFT-disclosures.md) (revision 3).
- **Headline values now in the text:**
  - per-bin median 6.45% (published 6.85%);
  - integral 4.75% (published 4.61%);
  - flux 3.75% (published 4.01%);
  - χ²/ndf against paper + ours 0.964; log-normal 0.987; with the paper's statistical part removed, 6.01.

**Suggested order.**
1. Joseph gives provisional answers to J3–J5.
2. The director writes them into a branch and builds the four PDFs locally. Nothing is pushed.
3. Joseph and Ben review the built PDFs (the [agenda](AGENDA-ben-review.md)).
4. Joseph finalizes J3–J5.
5. J6 for anything outward.

This keeps "review everything extensively with Ben" ahead of any final wording, without blocking the drafting.

---

## J3. The claims

The bounds Joseph already set (DECISION-20261014 §2) are:
- no validated coverage;
- no calibrated intervals;
- no goodness-of-fit significance beyond what the construction supports;
- full closeout is **not** achieved, and the package must say so (l.49).

Each claim below is a 2D claim the deliverables make now.

| # | claim (where) | current text | options | recommendation |
|---|---|---|---|---|
| C1 | reproduction includes the "uncertainty scale" (`main_note.tex:50`, `sec_summary.tex:10`) | "reproduces the published … cross section …, including its spectrum and uncertainty scale" | keep / drop "and uncertainty scale" | **Keep.** Under Q the scale agrees on every summary: median 6.45 vs 6.85, integral 4.75 vs 4.61, √Tr ratio 1.071. |
| C2 | our uncertainty against the published one (`paper_body.tex:270–273`, `sec_results.tex:146–156`, `primer_body.tex:207–210`, `sec_execsummary.tex:26–27`) | the median only, now scoped "per-bin median" | (a) median only, as now; (b) median and integral | **(b).** The median alone (6.45 < 6.85) reads as "ours is smaller", but the integral is larger (4.75 > 4.61). One clause: "…6.45% per bin (published 6.85%) and 4.75% on the integrated cross section (4.61%)". |
| C3 | "Validated total intervals … require new inputs and construction repairs" (`paper_body.tex:319–322`, `sec_validation.tex:286–292`) | as quoted | (a) keep; (b) "require new inputs" and name what is outside every block (D1); (c) drop | **(b).** "Construction repairs" no longer describes Q, which is construction-complete under its conventions. The truthful version is the D1 list: G2 not repaired, learner dependence and C09/C10 in no block. |
| C4 | "Coverage of the total remains untested"; "the quoted … statistical block awaits an independent coverage test" (`paper_body.tex:290`, `:801–803`; `primer_body.tex:106`; `sec_summary.tex:18`) | as quoted | keep / strengthen to the D2 sentence | **Keep**, and take D2's sentence in the note (J4). |
| C5 | the combined χ² as a "descriptive distance" / "indicative" (`sec_results.tex:58–85`, `app_statmethods.tex`) | 0.964, called indicative | keep the register / quote no χ² in the paper | **Keep the note register.** The paper quotes no combined χ²; keep it that way. The cross-covariance is missing (CHECKLIST l.72), so it cannot be a goodness-of-fit. |
| C6 | learner dependence "at the level of one unit of χ²/ndf" (`paper_body.tex:805`) | published-covariance χ² 3.66 → 2.65 | keep | **Keep.** It does not depend on Q. |
| C7 | the regularization scan (`sec_results.tex:73`) and the post hoc rescoring (`app_statmethods.tex:786`, `:819`) | historical values, labelled | keep labelled / remove | **Keep, labelled as historical.** They describe earlier objects, so no Q claim rests on them. |
| C8 | the abstract's construction sentence (`main_note.tex:50–55`) | "computed with the central value's tree-learning implementation, its universe and statistical blocks at the central value's training seed" | keep / shorten | **Keep.** True after review fix M1. |

**After J3:** the claims map (R5, `docs/publication/CLAIMS-20261005-claim-to-evidence.md`) is updated to the decided
claims, and B4 is a fresh claims-to-evidence review.

---

## J4. The disclosure wording

The drafts are [`DRAFT-disclosures.md`](DRAFT-disclosures.md) revision 3, D0–D12. The paper's 2D subsection currently
has none of D1's exclusions and none of D5's text.

| # | choice | options | recommendation |
|---|---|---|---|
| W1 | **D1 register** | (a) the director's draft (no "closeout" phrase); (b) the packet's alternative ("Full scientific closeout is not achieved: …"); (c) both: (b)'s first two sentences, then (a)'s list of what lies outside every block | **(c).** Your ruling says the package "must say so" (DECISION-20261014 l.49), and (b) is the only draft that does. (a) carries the J2 condition: G2, learner, C09/C10 named. |
| W2 | **D5's required clause** (shrinkage, noise, few groups; "containment … is not evidence of coverage") | append the packet's clause verbatim / equivalent wording | **Append verbatim.** It is marked Required, and your J2 condition said "containment by construction, not coverage". |
| W3 | **Placement** of D9–D12 | paper / note only, cited from the paper | **Note only**, with one paper pointer sentence. D0–D5 go in the paper. |
| W4 | **Log-normal χ²** (REPORT §5) | (a) the definition only, as now in the note; (b) also list the alternatives (1.197, 0.958, 0.963, 1.015) in one note sentence | **(b) in the note.** The paper quotes no log-normal value. Ben will ask why 0.987 is the one quoted, and the answer is that it is the script's definition. |
| W5 | **History clauses** ("an earlier version … quoted 6.87%": paper l.277, primer l.216, exec summary l.26, results l.151) | keep / add the VL175 6.09% step / drop from the paper and primer, keep in the note's history appendix | **Drop from the paper and primer.** No earlier version was published (the Analysis-Note repository is private), so a reader has no earlier version to reconcile. The note's history appendix and errata keep the chain. |
| W6 | **D3: the learner dependence** | median only (draft) / median and maximum (0.98%, max 12.2%) | **Add the maximum.** The briefing found it omitted, and Ben is likely to ask. |
| W7 | **Flux sentence** (D10; paper l.278–281) | keep "for a reason the release does not establish" / remove | **Keep.** 3.75% against 4.01%, unexplained, as Ben's agenda item 10. |
| W8 | **KI-90 sentence** (D10), now writable | note sentence: "the two publication consumers check that a covariance's stored cell set equals the published one (rebuild REPORT §2)" / none | **Note sentence.** |
| W9 | **D11: the two universes where noise ≥ shift** (`2p2h:0`, `MaCCQE:0`) | note only / paper too | **Note only**, inside D11. |
| W10 | **Legend labels** "Training seed", "Run period" (Figs. 6/7) | keep / rename | **Keep.** They match the block names in the text. |

**After J4:** the director writes D0–D5 into the paper's §`sec:uq2d`, and D0–D12 into the note, at the marked sites.
Every number comes from the existing records. The PDFs are rebuilt locally, and a fresh reviewer checks the wording
against the decisions.

---

## J5. KI-85 (`KNOWN_ISSUES.md` row 85)

The row describes VL170, the earlier band. The quoted statistical block is now S1: 300 replicas, seed 42, three
streams, median 0.684%. S1 has never been coverage-tested, and VL169 does not grade it (PLAN-20261011 l.122).

| option | meaning |
|---|---|
| **(a) keep deferred, re-scope to S1** | add a dated status sentence; nothing is lifted |
| (b) keep as is | the row stays about VL170 and is silent on what is quoted |
| (c) lift | reverses the endpoint ruling, and no test supports it |

**Recommendation: (a).** Draft status addition, to follow the current status cell:

> **Re-scoped 2026-10-XX (Joseph, J5):** the quoted 2D statistical block is now S1 of the adopted Q = S5 total + C_PL
> (DECISION-20261017): 300 Poisson replicas at the central value's seed 42 in three streams (data, signal and
> background simulation), median 0.684% per cell. S1 has not been coverage-tested. The VL169/VL170 findings in this
> row describe the earlier band and do not grade S1. The held-out re-test remains deferred until after the publication
> package and is not pre-registered.

The row closes at K3 only to that extent. The `KNOWN_ISSUES` edit goes through the KI-cleanup peer's process
(memory: known-issues-cleanup-peer).

---

## J6. Outward acts

Nothing outward is requested now. The acts, and what each needs first:

| act | needs first |
|---|---|
| push the standalone `MINERvA-OmniFold-Analysis-Note` repository (B2) | J3–J5 final, local builds B1, the final review |
| submission, arXiv deposit, tag | the above, plus PKT l.69's author inputs: funding acknowledgment, ORCIDs, deposit location/licence/scope, cover-letter history |
| contact (MINERvA on `NormDISCC`, the flux gap, the period step) | your act alone; it can come before the push |

**Recommendation:** no J6 decision until after the Ben review.

---

## What the director does on each answer

- **J3 + J4 (provisional):**
  - write them on a branch;
  - rebuild the four PDFs locally;
  - run a fresh review;
  - hand you the PDFs for the Ben review.
- **J5:** draft the KI-85 row edit for the KI owner. K1–K4 then update the VL rows, AGENTS.md, the 2D status file and
  the claim tables.
- **J6:** only the acts you name.

**Same-model caveat:** every reviewer so far is Claude Opus 5.5. Ben's review is the first check by someone else.
