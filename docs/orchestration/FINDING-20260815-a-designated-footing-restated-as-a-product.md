# FINDING 2026-08-15 — a designated footing restated as a delivered measurement

`BEN-350`. Lane A, filed while writing the `OI-6` footing passage into the analysis note.
Episode `EP-2026-08-15-oi6-note-footing`.

## The sentence

Lane A was tasked to write the standard-5D purity footing into `docs/analysis-note/`, under Joseph's
`OI-6` ruling. Both the task text and `RUNBOOK-20260807-gbdt-closeout.md` §2.2 point 2 supplied the
same claim, in almost the same words:

> **The FPS lane already delivers the negweight-footed measurement.** Under (A) the standard chain is
> the matched control/cross-check at a different footing, which is a defensible published pair.

That sentence was to become note prose. It would have read, in a publication-bound document, as *the
extended-fiducial measurement exists and is on `negweight-refined`*.

## What is actually true

**The designation is real.** `nd-unfolding/fps_provenance.py:41`:

```python
PUBLICATION_BKG_MODE = "negweight-refined"
```

and it is enforced — `fps_build_publication_manifest.py:93-94, 140, 171` reject any endpoint whose
config does not carry it. So the FPS lane's *selected* footing is `negweight-refined`, in code, fail
closed.

**The product does not exist.** Measured before writing anything:

| check | command | result |
|---|---|---|
| endpoint unfolds on that footing | `find nd-unfolding/active_universe_5d/fps/unfolds_negweight_refined -type f` | **10 files, all `.config.json`, zero `.root`** |
| the lane's own state doc | `FPS_UQ_CORRECTED_STATE.md:287` | `PRODUCTION REMAINS GATED` |
| the live open item | `docs/OPEN_ITEMS.md` `OI-2` (2026-08-13) | still requires *"a new negweight-refined FPS central/endpoints"*; all purity-footed unfolds quarantined |
| the dependency map | `docs/RESULT_DEPENDENCY_AND_RERUN_MAP.md:93-107` | `BUILD explicit negweight-refined central and endpoint unfolds` is an unrun step |

So the endpoints are **configured and unrun**.

## The part that makes this worth a finding

**The note already said so, in the paragraph immediately above the insertion point.**
`app_negweight.tex`'s J22 correction — audit finding J22, `AUDIT-FINDINGS-20260731.md`, tier A — reads:

> **The $\sigma_{\mathrm{ext}}$ reported in §fps was not produced with negative-weight injection** …
> The negweight-refined FPS production has not been run.

The supplied sentence would therefore have entered a publication document as a present-tense delivery
claim, **contradicted three paragraphs earlier on the same page**, in the same appendix, in a
correction written specifically to stop that claim being made.

The cost of catching it was one `ls`.

## Why the source material was not wrong

This is not "the runbook was wrong", and reading it that way loses the transferable part.
`RUNBOOK-20260807` §2.2 is a **decision rationale**, written to justify choosing reading (A) over
reading (B). In that context *"the FPS lane already delivers the negweight-footed measurement"* is a
true statement about the **analysis design**: the design assigns the negweight footing to FPS and the
purity footing to standard, which is exactly why (A) yields a defensible pair rather than a gap. The
claim is true of the plan.

It becomes false the moment it is copied into a document whose reader takes the present tense as
*produced*. **A designation and a product are the same words at different tenses, and the tense is the
part that does not survive a relay.**

## The rule

**Before writing any "lane X carries / delivers / already has Y" into an outward-facing or
publication-bound document, list the artifact.**

A constant in a provenance module is evidence of *intent*. Only a file on disk is evidence of a
*product*. The two are trivially distinguishable and the distinction is invisible in prose, which is
why it has to be a habit at the point of writing rather than a review catch.

## Family

- `BEN-082` — two gates conflated by a sentence that is true of one and false of the other. Same
  shape: *"FPS is on negweight-refined"* is true of the designation and false of the products.
- `BEN-315` — a claim about code inferred from its structure rather than read at the site. Here the
  structure was a pinned constant and the site was a directory listing.
- `BEN-227` — remedy applied rather than proposed.

## Remedy, and the corroboration that came with it

The passage that landed is `docs/analysis-note/app_negweight.tex` §B.6,
`\label{sec:negweight-footing}`, written by a **concurrent lane on the same prompt** and pushed at
`e61624b` (see `BEN-351` for the duplication itself). It declines the supplied sentence in the same
way this lane's draft did:

> The extended-fiducial lane's **designated** publication footing is negative-weight injection with
> the Stay-Positive refinement (`nd-unfolding/fps_provenance.py`, `PUBLICATION_BKG_MODE`) … what the
> number quoted in §fps actually used is the separate matter stated immediately above.

**That is the useful part of an otherwise wasteful duplication.** Two independent authors, given the
same sentence, both refused to write it and both reached for the word *designated*. That is evidence
the sentence is a trap in the source material rather than evidence that either author was unusually
careful — which is exactly the difference between a finding worth filing and an anecdote.

Note build only; `app_negweight.tex` is in the `main_note` include closure alone.
