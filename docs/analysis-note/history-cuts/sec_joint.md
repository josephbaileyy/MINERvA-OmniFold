# History restructure, §11 (sec_joint.tex): cut log

**Under** DECISION-20261113-joseph-note-n4-n5-role.md, the addendum recording Joseph's go of 2026-11-13, and the
director's ruling (A) of 2026-11-14 (recorded in sec_5d.md): each timing use of "declared" or "in advance" is written
out with its object, and each method use of "declared" becomes "specified".

**The rule, verbatim as adopted:** history stays in the note only if removing it would change a reader's understanding
of the reported object, its reproducibility, its evidential independence or its limitations. Everything else goes to
the ledger. Each "fixed before" names its object, and "declared" alone is replaced.

**Referee:** for §11 it gave "15–25%, Compress, chiefly §§11.3 and 11.6. Keep design exposure, budget adaptation,
recovery outcomes, calibration assumptions, and correction sensitivities". Its item 7 (§11.6) reads: "**Cut (ledger)**
the counterfactual stopping chronology. **Keep** the interruption/recovery counts, recovered outcomes, original
decision ensemble, and differing scopes of independent verification."

**Base:** `docs/analysis-note/sec_joint.tex` at `d4c7494f8`. It is unchanged since 619a1d9b6. Line numbers are the
base's.

**Outcome for §11:** ten wording changes. No passage is cut.
- **§11.3** (`sec:joint5d-frozen`) holds the design exposure (the reviewers had seen descriptive per-cell residuals)
  and the budget adaptation (a bounded extension decided while monitoring showed observed claim $p$ values). These are
  the referee's own keep list.
- **§11.6** (`sec:joint5d-lost`) holds the five disclosures that Joseph's disposition requires "beside the claim"
  (DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md §5, :117-131). The note's source comment at
  :244 records that "all of which this subsection prints".

## Item 7 is not cut: the counterfactual is a required disclosure

The referee's item 7 would cut :239's last sentence: "With complete batches the predeclared rule would have stopped the
Tune~v1, GENIE~2.12.10, GENIE~2.12.10 + MEC and GiBUU nulls one batch earlier ($B=1200$), with the same decisions."
That sentence is disclosure 4 of Joseph's disposition (:125-126): "**With complete batches**, the frozen rule would have
stopped MnvTune, GENIE CV, GENIE MEC and GiBUU one batch earlier (B = 1200), with the same decisions". The disposition
also selects it in its answer (:113-114): "Disclose … that complete batches would have stopped four nulls one batch
earlier, with the same decisions."

:241's "The earlier stops rest on the calibration run's own re-application of the sequential rule and have no
independent check" is disclosure 5's third item (:131, "the earliest-stop decisions rest on the campaign's
self-validated `stopping.json`"). It keeps its referent because :239 stays.

The history rule does not overrule a disclosure that Joseph required beside the claim, so both stay. The sentence
changes only to name its rule's object (J9).

## The changes

| id | base line | old text | new text | ledger home, and the records for each object |
|---|---|---|---|---|
| J1 | :5 | "the six conditions of the declared model" | "… of the specified model" | a method use: no timing |
| J2 | :50 | "the largest over the declared \emph{claim variants}" | "… the specified \emph{claim variants}" | as J1 |
| J3 | :139 | "Each decision holds under six conditions of the declared model." | "… of the specified model." | as J1 |
| J4 | :230 | "two of the three declared alternatives" | "two of the three specified alternatives" | as J1 |
| J5 | :286 | "The declared nuisance model here includes …" | "The specified nuisance model here includes …" | as J1 |
| J6 | :359 | "the declared nuisances into each null distribution" | "the specified nuisances …" | as J1 |
| J7 | :359 | "predictions under the declared model." | "… under the specified model." | as J1 |
| J8 | :239 | "A determinism check fixed in advance (16 of 16 completed seeds rerun bitwise identically)" | "A determinism check fixed before the rerun (16 of 16 …)" | d4c7494f8:sec_joint.tex:239. PROCEDURE-20261005-s5p-lost-seed-recovery.md:5, "the determinism check and its criterion, fixed before it runs" (first commit 0a988bc44, 2026-10-05 14:09 -0700); RECORD-20261006-s5p-lost-seed-recovery-resolution.md:24, the determinism array 59397841, PASS 16/16 (11a266c6c, 2026-10-05 22:25); the disposition's disclosure 2, "Determinism 16/16 was fixed in advance" (:121-122). The sentence before, "fixed, and reviewed independently, before the rerun", names the same object. |
| J9 | :239 | "With complete batches the predeclared rule would have stopped …" | "With complete batches the stopping rule, fixed before any production pseudo-experiment, would have stopped …" | d4c7494f8:sec_joint.tex:239. The object is §11.3's own, :126: "The hypotheses, statistics, variants, multiplicity rule, stopping rule and every input were fixed before any production pseudo-experiment or observed statistic". The disposition's disclosure 4 calls it "the frozen rule". The record: state/s5p/contract-amendment-7-production-admission.json, "the production admission of the joint test", whose status is "FROZEN at the commit that first adds this file" (:6; 4f5a613f3, 2026-09-28 09:10 -0700), states the rule as "sequential_rule" (:23): "batches of 200 seeds in fixed order per null, at most 1999; before each batch s5p_seqstop.py evaluates … and stops the null …". |
| J10 | :344 | "Its criterion, … was declared before the check was computed." | "… was specified before the check was computed." | the object is already named; the word only. The disclosure "A bias check of that check's premise was added post hoc" stays. |

**Kept as they are:**
- **:37** "Since $V$ was fixed before the calibration", **:126** "fixed before any production pseudo-experiment or
  observed statistic", **:134** "Each was specified before it ran; the projection comparison was specified after the
  five-dimensional outcomes were known", **:154** and **:157** "$V$ fixed before any observed statistic", **:254**
  "specified after the five-dimensional outcomes were known but bef[ore] …": each names its object.
- **:126**, the two data-informed elements: the design's reviewers had seen descriptive residuals, and the budget was
  extended while the monitoring showed observed claim $p$ values. These are the design exposure and the budget
  adaptation.
- **:237–241**, the lost pseudo-experiments: the counts, the sensitivity analysis computed before the lost outcomes were
  known, the recovery, the closest margins, the counterfactual (above) and the scopes of the checks. These are
  disclosures 1–5.
- **:254** and **:279**, "a post hoc observation", and **:344** "added post hoc": disclosures of choices made after
  results.

**Numbers and keys:** `numdiff.py` on the base and new files, comments stripped: none removed, none added; value keys
and macros unchanged.

**Also in this commit:** `app_statmethods_nd.tex` (§10's G1, 8347688e6) gains one blank line between the opening
paragraph and the moved text. They had been set as one paragraph. No word changes.

## The Development-history appendix

No new row. §11 reports no superseded configuration and no stopped test. Its lost-draw sensitivity analysis is
superseded by the recovery's observed outcomes, as :241 says ("The observed outcomes of the lost draws supersede the
finding of the sensitivity analysis described above"), and both stay printed in §11.6 as required disclosures.

## Disclosure checklist

| disclosure | in §11? | survives |
|---|---|---|
| the 2D adoption after the published distance was known | no (§3) | — |
| the post-observation run-period term | no (§4, §10) | — |
| reused samples and seeds | the recovered draws are the lost draws (determinism, :239); the recomputed-shift evaluation's check is a rerun of the same code (:241) | ✓ unchanged |
| the invalid q3 deformation | no (§9) | — |
| the stopped coverage tests | no (§5, §9, §10) | — |
| the data-informed joint-test design and budget extension | yes, :126 | ✓ unchanged |
| the missing response uncertainty | the hadronic-response condition (§11.8, :283 onward) | ✓ unchanged (J5 is the method word only) |
| the generator-sample problems | the hydrocarbon target correction for NuWro and GiBUU (§11.9) | ✓ unchanged |
| the target-correction sensitivity | yes, §11.9, with the post hoc bias check (:344) | ✓ unchanged (J10 is the word only) |
| also found: the projection comparison specified after the five-dimensional outcomes were known (:134, :254) and the post hoc GENIE~2.12.10 observation (:254, :279) | yes | ✓ unchanged |
| also found: Joseph's five required disclosures for the recovery (§11.6) | yes, :237–241 | ✓ unchanged (J8, J9 name objects) |

## Unreleased support

`UNRELEASED-SUPPORT.md` lists §11's sites. None changes its citation here.

## Meaning read (codex-school gpt-6.1-sol, high, read-only; reads/sec_joint-prompt.txt, the form of §9's pass 3, with reads/sec_joint-records.txt)

- **Pass 1:** OVERALL FAIL on J9 alone. The records then attached named the rule only as "the frozen rule", and the
  read would not take §11.3's own :126 as record support. Every other row passed: J1–J8 and J10. Nothing was removed,
  the item-7 sentences remain, and no disclosure was lost. reads/sec_joint-pass1.txt.
- **Pass 2, with amendment 7's lines 6 and 23 attached (records.txt's last excerpt):** OVERALL PASS, with no FAILs.
  J1–J10 pass; no NEEDED item lost; the item-7 sentences remain; no disclosure lost. reads/sec_joint-pass2.txt.
