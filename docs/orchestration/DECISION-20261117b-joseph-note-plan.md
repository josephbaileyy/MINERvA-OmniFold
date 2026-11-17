# DECISION 2026-11-17 (b) — Joseph: the combined note plan, all five items; the IBU test; PILOT-FB

**Recorded by** director-helper-3, for the director.

## What led to it

DECISION-20261117-joseph-note-measurement.md (#1209) made the analysis note the release, as a cross-section measurement. The director then prepared a combined plan for that note: `~/codex-reports/note-measurement/COMBINED-PLAN.md`, an untracked draft of 2026-11-17, sha256 of the file `51e9a3779eafde54`.
- **Inputs.** The plan drew on three architecture reads, three figure audits, a skim test, a currency check and the framing map.
- **Questions.** Its §8 put five decisions to Joseph, each with a recommendation. The director also put an IBU test to him.

Earlier the same day, the director had put PILOT-FB to Joseph: `PILOT-FB-DECLARATION.md`, design only, at `d5dc0a366` on `decl/pilot-fb-20261117`. It tests fixed LightGBM bin edges against the rounding instability on RS1's pseudo-experiment.

## Joseph's words, verbatim

(a) On the combined plan:

> yes to all five, and go ahead with the IBU test

(`dd6c33d4dea05fa6`, the sha256 of the text plus a final newline.)

(b) On PILOT-FB, earlier on 2026-11-17:

> yes I meant the pilot and the bin edge fixing

(`59d53dc8af4f4831`.)

## The five items as approved (the plan's §8, quoted as written there)

1. **Where the framing hold applies.** Change the document-level self-description now: the abstract's first sentence, the executive summary's opening, the introduction's purpose, and the summary. Hold every product-level `[P]` sentence verbatim, and show "decision open" in the what-is-measured box. *Recommend yes.* Otherwise the abstract says "measurement" while §9's title says "Illustrative", with no explanation.
2. **Palette.** Adopt the paper's colors, with `#CC79A7` for GENIE CV, and "this work" red in every figure. The 3D and 5D unfolded points change from black to red. *Recommend yes.* It removes the red = GENIE-CV versus red = this-work collision.
3. **Order.** Move the sixteen-cell section ahead of the 5D development tests and §12 to App. J, with the appendix letters unchanged. *Recommend yes,* with the one-line revert as the fallback.
4. **Currency in Ben's copy.** All 19 UPDATEs in two batches. U6 goes in only after its record is on main, and any unlanded item is named in the cover note. *Recommend yes.*
5. **Version line and Zenodo sentence (A2, A19).** *Recommend* "Version 1.1 (draft for co-author), 19 November 2026", and "before the note is submitted" with the DOI hold kept.

(The §8 block is the plan's lines 338–354. The sha256 of those lines is `8022481b6fae4053`.)

## What is decided

1. **Items 1–5 above, as written.** The product-level `[P]` sentences stay verbatim until Joseph and Ben decide the reporting protocol (DECISION-20261117-joseph-note-measurement.md item 6).
2. **The IBU test goes ahead**, from (a). This record gives the go only. Its design, price and binding are in its own declaration, which the director names. Like every campaign, it is declared, priced and bound before it runs (DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md item 2).
3. **PILOT-FB is approved**, from (b): the pilot and the fixed bin edges, as declared at `d5dc0a366`.
   - It runs after its audit and the director's go, within its declared cap of 0.9 CPU node-h.
   - Its declaration's own terms hold: no outcome changes any note or paper wording, and the outcome goes to Joseph and Ben as an option.
4. **The schedule.** Work starts on 2026-11-17, ahead of the plan's Wednesday start. The content freeze is Thursday 2026-11-19 at 11:00.

## The director's calls, recorded here

5. **The read-only fetch for Figs. 6–14 (the plan's tier 2) is approved.** It fetches two files, E_R `xsec.root` (`a5c13fc3…`) and `cov_ptpl_…6GeV.root` (`6c6dce72…`). Both shas are checked on arrival.
6. **There is no word target for this pass.** DECISION-20261116-joseph-paper-batch.md item 34's target of about 45,900 words was set for the methods-study framing, and it is not applied to the measurement framing. The word count is measured at the freeze.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the plan's five items, the IBU test's go and PILOT-FB's approval, as Joseph's; items 5–6, as the director's.
- **Not citable for:**
  - any result of the IBU test or of PILOT-FB;
  - any cross-section value, uncertainty or coverage result;
  - the reporting protocol, which stays open;
  - any note sentence.

Nothing is submitted, deposited or tagged.
