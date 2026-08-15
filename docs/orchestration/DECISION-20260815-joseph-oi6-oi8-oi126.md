# DECISION 2026-08-15 — Joseph rules `OI-6`, `OI-8` and `OI-126`

**All three had sat `WAITING-USER` since 2026-08-12.** Recorded before any of it is acted on, per
`BEN-201`. Transcribed by the personal-orchestrator (mediator); the lanes cannot see the original and
this document is the authority they should read rather than any relay of it.

## The grants, verbatim and complete

> **OI-6:** "Okay keep purity, but make sure this distinction and reasoning is obvious in the note. Go
> forward with the rest of the GBDT"

> **OI-8:** "Okay your recommendation sounds good, go ahead with it if anyone else agrees with you."

> **OI-126:** "just go with the consensus"

---

## `OI-6` — CLOSED. Purity is the footing, and the distinction must be visible.

**Reading (A) is adopted:** the standard 5D chain stays purity-footed, consistently labeled, and the
lateral is built from the **existing** ten unfolds. Reading (B) — that "N-D production uses
`negweight-refined`" reaches the standard chain — is **rejected**. It would have required re-running the
central, 169 vertical, 18 detector and 10 lateral unfolds, **and it would have invalidated the
J28-corrected covariance that was just adopted.** That last consequence, not the cost, is the decisive
one.

### The measured basis (from `RUNBOOK-20260807-gbdt-closeout.md` §2.1, not re-derived here)

| comparison | result |
|---|---|
| SYST covariance, 187 universes, both modes | negweight `2.9828e-39` vs purity `3.0242e-39` → **0.9863** |
| STAT covariance, matched first-50 seeds | `1.7260e-40` vs `1.7576e-40` → **0.982** |
| real-data totals | agree to **−0.13%**, per-bin median 1.000, 1.4% RMS |

**Why it generalises rather than being luck:** a systematic covariance is the *spread across* universes,
and each universe shifts by ~0.1% in **both** modes, so the two covariances agree by construction.

### THE DISTINCTION JOSEPH IS ORDERING INTO THE NOTE

This is the operative half of his ruling and it is a boundary, not a summary:

- **SAY:** the standard 5D chain is purity-footed; this is a recorded choice; the measured footing
  impact is ~1–2%; the FPS lane carries the `negweight-refined` measurement, so the pair is a
  consistent measurement plus a matched control at a different footing.
- **DO NOT SAY, and do not let a later edit drift into saying:** that the footing is *proven irrelevant
  in 5D*. **There is NO full 5D 187-universe both-mode comparison at the publication 5-iter `lgbm`
  config.** The 5D evidence is a two-universe spot check at 1 iter / `hist`, plus the structural
  identity, plus the full-statistics 2D result. That is ample for the first statement and **not** ample
  for the second.

**This ruling opens `docs/analysis-note/` for this text only.** That gate is otherwise Joseph's alone
and every other prohibition on it stands.

### "Go forward with the rest of the GBDT" — what it does and does NOT clear

**It clears the footing decision, which was blocking by decision.** It does **not** clear the
`standard-p4-verifier`, and no reader of this document should infer that it does. The live verdict
(`runs/standard-p4-verifier/20260810T012645Z-repair7-verdict.json`, `code_rev 5c25333`) is:

```
verdict :: BLOCK
defects_outstanding :: 14
self_guards_adequate :: NO
authorizes_covariance_stages_4_6 :: False
```

**So the standard 5D lateral is still "NOT BUILT, AND NOT ONE RUN AWAY".** Joseph's grant authorises
*proceeding with the lane*; the verifier decides when the covariance stages may run. Those are different
gates and conflating them is the `BEN-082` shape.

**The lane's own preconditions survive untouched:** stage 3 must not run on pre-G-1 code, and G-1 is
code-only and not on the cluster checkout. See `OI-8`.

---

## `OI-8` — RULED, **CONDITIONALLY**, and the condition is not yet met

Joseph's grant is explicitly conditional: *"go ahead with it if anyone else agrees with you."* **He is
requiring corroboration, and a mediator's own confidence does not satisfy it** (`BEN-300`: consensus
among restatements of one source is not corroboration). **This section is therefore NOT YET IN FORCE.**

### The ruling put to him

**The G-1 cluster-landing request is DEAD AS SUPERSEDED, and the constraint it protected survives as a
precondition on the run rather than as a landing action.**

Measured basis, from `state/cluster-local-fork-freeze-20260812.json`:

```
cluster_head_is_strict_ancestor_of_origin_main : true
commits_cluster_ahead_of_origin_main           : 0
```

**There are zero unique cluster commits.** Joseph's own item-7 decision — *"use a clean canonical-based
worktree for new cluster work"* — already governs how G-1 reaches any future run, so there is nothing
left to "land" and no conflict with the cluster P4 hold.

**What survives, restated as a precondition:** *no standard-P4 stage-3 run from a tree that does not
contain G-1.* The hazard is real and unfixable if hit — stage 3 writes ten receipts with no `bkg_mode`,
the launcher **skips endpoints that already have one**, and deletions are frozen, so a pre-G-1 stage 3
creates a provenance regression that cannot be repaired.

### THE SPECIFIC CLAIM THAT MUST BE CHECKED IN CODE BEFORE THIS TAKES EFFECT

**That the launcher skips endpoints that already carry a `bkg_mode` receipt.** The whole
irreversibility argument rests on it, the mediator has **not** verified it, and it is asymmetric: cheap
to be wrong about in the direction of re-opening, expensive in the direction of a silent regression.
**Assigned to a lane that did not author the ruling.**

---

## `OI-126` — CLOSED as "go with the consensus"

The consensus is on the record and is **4-0**, reached across lanes that disagreed on the way in:

- `DECISION-20260815-oi126-contrast-not-run.md` — do not run the `Exponential(1)` contrast, because
  `Poisson(1)` **is** the sampling distribution and both outcomes support `C_stat`'s validity.
- The fixed-network arm was **retired by its own author** the same day, on a code trace:
  `extract_xsec` has no measured-weight parameter, so a fixed-net arm's spread under measured
  resampling is **identically zero**. Information loss and refit sensitivity are not separable for this
  estimator.
- The limitation statement is already in the note at `92b2873` (`\label{app:cstatlimit}`), note build
  only, all three builds pass.

**So: `C_stat` publishes with the (a)/(b) fork explicitly stated, and the `67%` described as the spread
of a refit estimator under correct measured-statistics resampling — an upper bound on how poorly the
data constrain the cross-section there.**

**What this does NOT do.** It does not ratify the branch-(b) narrowing. Lane C declined that on one
day's tenure and `VL132` records one builder; ratification still rests with the estimator's owner and
the construction reviewer. **Publishing the fork is exactly the move that does not require it.**

---

## Related

- `AUTHORIZATION-20260815-consensus-grant.md` — the standing grant. **None of the above is a spend.**
- `RUNBOOK-20260807-gbdt-closeout.md` §2.1, §2.2 — the purity backing data and reading (A)/(B).
- `state/cluster-local-fork-freeze-20260812.json` — the ancestry measurement `OI-8` rests on.
- `VL132`, `OI-71`, `OI-125` — untouched by any of this.
