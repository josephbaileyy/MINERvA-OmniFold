# DECISION 2026-10-22 (fifth) — Joseph: the open note items, the input and RHC timing, and when to rewrite

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The director put the open decisions to Joseph with options, pros, cons and a recommendation
each, and advised against starting a new model-scored rewrite session now (it would reverse
`DECISION-20261022-joseph-note-records-refs-and-stop.md` while Joseph and Ben read, the RE-1 integration will change
the text anyway, and the absolute rating no longer resolves versions). Items were numbered:
1. the background-treatment revisit (OI-6);
2. the narrowed RC7 verifier sentence (note App. H, release status; `methods/note-bhi/REPORT.md`);
3. S11, "hybrid null hypotheses" (`METHODS-IMPLEMENTATION.md` §18);
4. "since superseded" in place of ruling C7's "historical" (`methods/note-b4/REPORT.md` Q3);
5. V5 before S3 (moot while MP-2 is held closed; not asked);
6. the newer FHC inputs (`state/data-survey-20261022/SURVEY.md` §2);
7. RHC as a later second measurement (SURVEY.md §§3, 7).

Joseph's answer, verbatim:

> 1. yes we can wait but as a preliminary result I think it might be worth doing the negative reweighting to try and get an accepted uncertainty, but maybe we need to be more confident that it will work first? also maybe we can use this as a chance to use new fhc inputs and add rhc? 2. yes if we would do a new release candidate we can add the recomputation but otherwise we can just confirm for now 3. keep it 4. confirm. 6. I agree with your recommendation 7. agree with recommendation. lastly, okay lets wait for the note round, let me know when its time to do the rewriting

sha256 of the text plus a final newline begins `88e3f90461af4356`.

## What is decided

1. **OI-6 waits for RE-1 report 2** and its movement table. Joseph's proposal of the negative-weight background
   treatment as a route to validated uncertainties is a **question, not a grant**: he asks whether there is enough
   confidence first. It goes to the validation lane's scoping memo as a candidate route with its decisive cheap test
   (see "Routing" below). No coverage campaign under the negative-weight treatment is authorized by this record.
2. **The narrowed verifier sentence is confirmed** as printed. If a new release candidate is ever made, it adds the
   recomputation of `observed_jitter_p` to the package verifier; otherwise nothing changes.
3. **S11 is kept.** The joint-test chapter keeps "hybrid null hypotheses about five predictions".
4. **"Since superseded" is confirmed** as satisfying ruling C7.
5. (V5 was not asked; it stays moot while MP-2 is held closed, `DECISION-20261022-joseph-mp2-hold.md`.)
6. **Inputs (director's recommendation, adopted):** the methods paper and the note keep the current ME-FHC inputs,
   which they already disclose as an earlier production. A measurement paper switches to the public release once,
   after MINERvA's planned late-2026 fixes, since its products are new anyway.
7. **RHC (director's recommendation, adopted):** decided after the validation lane's scoping memo says which
   dimensionality the FHC measurement can validate.
8. **Rewrite timing:** no new register rewrite session now. The director tells Joseph when it is time: after Joseph's
   and Ben's read and after the RE-1 integration. The director's proposed conditions for that round (a writer of a
   different model family from the raters, a before-against-before control, the weakest pieces only, its own branch
   with the director's two-direction review) are proposals for Joseph then, not settled here.

## Routing

- **To the validation lane** (scoping memo, `state/measurement-scoping/SCOPING.md`): assess the negative-weight
  background treatment, configuration (e), as a route to validated coverage. The memo must weigh the record that bears
  on it, and name the decisive cheap test before any campaign:
  - KI 98 arm (b): the W-graded residual persists with no background at all (R_b = +2.84, consistent with arm (a);
    `state/ki98-wbias-test/REPORT.md`), so the residual is not shown to come from the background treatment;
  - D-ID: exact binned IBU leaves about the same residual (`state/next-preparation-20261009/d-id/REPORT.md` §11);
  - IBU-1's per-truth reading, when it lands;
  - RE1-SPEC §1 "NOT CITABLE FOR": RE-1 builds no covariance or coverage for configuration (e). *(Corrected; see
    below.)*
- **Joseph's "new FHC inputs and add RHC" in item 1** is answered by items 6 and 7: a preliminary coverage test stays
  on the current inputs, so that it is comparable with s5c, KI 98, D-ID and IBU-1; the inputs change once, for the
  measurement production.

## Not changed

- Claims, the printed note and paper text (items 2–4 confirm text already printed), the other lanes' grants, MP-2's
  hold.

## Correction (2026-10-22, same day)

The first version of the routing list said "no covariance or coverage exists for configuration (e)". That was false.
RE1-SPEC §1 says only that RE-1 does not build one. Configuration (e) is the s5e/s5p contracts' estimator R
(`methods/r12/REVIEW.md:48`), and its development-scale intervals were measured in s5e
(`state/s5e/cand/assess_receipt.json`: pooled 68% coverage 0.680 at nominal, 0.017–0.157 at the five departures).
The validation lane found this (scoping memo draft, R9). No validated coverage exists for (e); development-scale
coverage does. The director told Joseph the route was untested, and corrected that the same day.
