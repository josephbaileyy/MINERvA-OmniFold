# FINDING 2026-08-17 — append-only is load-bearing infrastructure, and 443 citations are why

**BEN-254.** Lane D (verifier). Found by trying three times to close a findability gap and being
told "append-only" three times; the fourth answer was a measurement, and it changed the conclusion.
Every operand below re-derived at `origin/main` rather than relayed.

## What I wanted to do, and why it was wrong

`ND_OMNIFOLD_RUN_LOG.md:7922` pins a preserved stdout by sha256. That stdout prints a **false**
`LEAKAGE` banner (see `BEN-250`, `OI-120(c)`), and the corrected receipt lives elsewhere. A reader
verifying the pin lands beside the false banner with nothing adjacent pointing at the correction.
**One line inserted at `:7922` would close that.** It is the obvious fix and I proposed it three
times.

**Measured, it would have manufactured at least three dangling citations:**

```
443   line-number citations of the form ND_OMNIFOLD_RUN_LOG.md:<n>  across origin/main
  3   distinct cited lines BELOW 7922:  :8805  :8864  :9546
```

An insertion at `:7922` shifts every one of those by one, **silently**. Nothing errors, nothing
fails a test; the citations simply stop pointing where they say.

## This is not hypothetical — the same failure is already realised in the tree

`VALIDATION_LEDGER.md:65-88` is cited as *"the seven construction causes"* from two places:

```
docs/INTEGRATION_CHECKLIST.md:57
docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md:8
```

Those lines now hold **`VL119`** and **`VL114`** — replica-deviation rows — because the ledger grew.
The citation is dangling and it failed exactly as this class does: quietly, months later, to a
reader who trusts the number.

## The reframe, which is the finding

**Append-only is not a style rule this repo has chosen to respect. It is a constraint with a
measurable cost to violating it, and the cost is 443 citations deep.** I had been treating it as a
convention I was deferring to on standing; it is infrastructure. So had the mediator, who checked,
confirmed the RUN_LOG carries **no content digest anywhere** and has only one `MANIFEST.tsv` row
(an ARCHIVAL predeclaration), concluded the edit was permitted — and then declined anyway on the
citation count. **Permitted and safe are different questions, and only the second one was measured.**

## The remedy that works today, with no edit

**Cite an immutable handle, not a line number.** The pin at `:7922` already *is* one: the sha256
`ec5581363f…912c` is content-addressed and cannot drift. Verified — `git grep` of that digest
returns four sites:

```
nd-unfolding/ND_OMNIFOLD_RUN_LOG.md                                  the pin
docs/orchestration/state/oi120c-loader-purity-perturbation-56975592.json   the CORRECTED receipt
docs/orchestration/CLAIMS.md
docs/orchestration/FINDING-20260814-a-sentinel-that-collided-with-a-result.md
```

**A reader standing at `:7922` who greps the sha they are looking at reaches the corrected receipt.**
That works now, survives the file growing, and needs no insertion.

> **Check:** before inserting into any append-only chronology, count the line-number citations that
> resolve *below* the insertion point. If the answer is not zero, the insertion silently breaks them
> and the fix is a content handle, not a line. To point *into* a RUN_LOG, cite a digest the entry
> already records.

## What is still missing

**The digest-keyed workaround is nowhere written as the convention for pointing into the RUN_LOG.**
It works by accident of the pin happening to be a sha, not because anyone specified it. The 443
existing citations are all line numbers, so every one of them carries this exposure and none of them
is protected by the remedy.

## Disposition

The findability gap that started this is **ANSWERED-AND-NOT-ACTIONABLE-AS-SCOPED**: met by the three
router rows (`KNOWN_ISSUES` 49, `OI-124`, `CLM-002`) plus digest lookup; the adjacent-line form is
foreclosed by the citation count. Recorded so the next session does not re-ask, and so that the
reason is the measurement rather than the convention.
