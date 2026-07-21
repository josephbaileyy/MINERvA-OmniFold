# Presentation recommendation — reproduction-first / trust-building arc

**Talk:** MINERvA collaboration, ~2026-07-16. 20 min + 5 min discussion.
**Audience:** the MINERvA collaboration — first contact. They own the detector,
the data, and the published flagship measurement being reproduced. They know
traditional unfolding (D'Agostini IBU + binned response matrix); they do **not**
know OmniFold.
**Speaker's stated goal:** teach OmniFold and show what the research has done so
far; cannot cover everything.

*One agent's recommendation among several the user is collecting. Grounded in
`nd-unfolding/ND_OMNIFOLD_STATUS.md`, `docs/analysis-note/sec_execsummary.tex`,
and `sec_intro.tex` as of 2026-07-12 — including the UQ-remediation quarantine.*

---

## Strategic frame: this is a trust-building first contact

You are an outsider presenting an ML method on the collaboration's own open data
to the people who built the detector and published the result you reproduced.
Their default posture will be polite skepticism. The goal of the talk is not to
show everything — it is to **earn credibility early, then spend it on the
payoff.** Every choice below serves that.

### Throughline (the one sentence they should leave remembering)

> Unbinned ML unfolding reproduces MINERvA's published 2D flagship result, and
> then does what binned unfolding structurally cannot — simultaneous
> many-observable cross sections, independent recovery of your own low-recoil
> physics, and eventually unfolding straight from calorimeter clusters.

---

## Recommended arc (~20 min budget)

1. **Who I am + the data product (1 min).** Outsider using the public ME FHC
   CC-inclusive product. Set the frame explicitly: "I'll teach you OmniFold,
   show I can reproduce your result with it, then show what it unlocks."

2. **Teach OmniFold (5–6 min) — the explicit ask; give it real room.** Anchor to
   what they already know (D'Agostini IBU + binned response matrix, as used in
   MINERvA:2021owq). Essence in one breath: *train a classifier to learn a
   per-event weight morphing sim→data, pull that weight back to truth through the
   sim's reco–truth pairing, iterate, and bin only at the very end.* One slide
   with the two-step iteration box (Step 1: reweight at reco; Step 2: pull to
   truth via pairing). Key contrast that carries the whole "why care":
   **adding an observable is adding an input column, not multiplying
   response-matrix bins.**

3. **Reproduction of MINERvA:2021owq (4–5 min) — credibility anchor. Lead with
   this before anything new.** Money slide: unbinned
   d²σ/(dp_T dp_∥) on top of their published points; total ratio ≈ 1; sub-1σ
   per-bin pulls; and — the part experts respect — a *fully independent*
   uncertainty budget whose median per-bin uncertainty matches the published
   value. Message: "I didn't reuse your machinery; I rebuilt it and got your
   answer."

4. **The payoff — what binned can't do (5–6 min).** Three beats:
   - **First simultaneous 3D/4D/5D MINERvA unfolds**, each reproducing the
     lower-D result when marginalized (built-in cross-check — mention it,
     it reassures).
   - **Independent recovery of their own physics:** all four generators
     under-predict at low E_avail; Valencia 2p2h fills the QE–Δ dip — the
     established MINERvA low-recoil/2p2h deficit, re-found by a completely
     different method. **Strongest physics-credibility slide for this audience —
     spend time here.**
   - **A genuinely new result:** the high-E_avail excess that 2p2h can't explain
     localizes in the (E_avail, W) DIS corner (W ≥ 1.8 GeV), and all four
     generators underpredict it.

5. **Where it's going (2 min, teaser tone).** Point-cloud transformer (PET)
   unfolding straight from calorimeter clusters — a path toward unfolding
   raw-ish detector data — plus the full-phase-space extension (muon cuts
   removed). One slide, framed as outlook, not a finished claim.

6. **Summary (1 min):** restate the throughline. Leave the 5 min for discussion.

### Rough time budget
| Segment | Minutes |
|---|---|
| Intro / framing | 1 |
| Teach OmniFold | 5–6 |
| 2D reproduction (credibility) | 4–5 |
| N-D + physics (2p2h + E_avail,W) | 5–6 |
| PET / FPS outlook | 2 |
| Summary | 1 |

---

## What to cut (or push to backup)

- Deep systematics machinery, coverage/closure toy internals, calibrated-
  classifier and NN cross-checks → collapse to one "validation suite" bullet.
- Detailed PET / FPS numbers → teaser only.
- **Cross-source covariance / block-summing methodological finding → backup +
  discussion, NOT a headline.** (See landmine below.)

---

## The UQ landmine — decide before finalizing slides

`ND_OMNIFOLD_STATUS.md` (presentation rule) and the note's executive summary are
explicit: **N-D uncertainty budgets, covariance-based significances, the
unified-throw adoption, and PET–GBDT precision comparisons are currently
quarantined pending corrected production.** For a talk to this audience this
matters twice:

- **Quote only what's cleared:** central values, closure, marginalization
  anchors, and *shape-level* statements (e.g., "the excess concentrates in the
  DIS corner") are fine. The 2D reproduction's uncertainty budget is cleared (it
  matches the published one). Do **not** put a number on the (E_avail, W)
  significance or any N-D budget — say "significance withheld pending the
  corrected covariance."
- **Prepare the honest answer**, because these experts own the systematics and
  will ask. E.g.: "Central values and closure are solid across all dimensions;
  the full N-D uncertainty budget is being regenerated because I found a
  methodological issue in how per-source covariances are combined — I'll show the
  2D budget, which is complete and matches your published one."

On the block-summing finding (per-source covariances omit cross-source terms;
the `GetTotalErrorMatrix` point): it is real and interesting, but presenting
"your standard covariance approach drops terms" as a headline — to the
collaboration whose MAT framework does it, as an outsider, first contact, with
the numerical result still pending (the advisor is still probing the framing in
the note margins) — needlessly puts the room on the defensive. Hold it as a
**discussion point / backup slide**, framed as "a test I'm running on the
block-sum approximation," not a verdict.

---

## Audience-specific tactics

- **Speak their dialect:** "D'Agostini IBU," "response matrix," "low-recoil
  excess," "Valencia 2p2h," "MnvH1D/MAT." Signals you're not an ML tourist.
- **Order = credibility first.** Reproduction before novelty, every time.
- **Be scrupulously honest about UQ status.** Experts smell overclaiming;
  "the budget is being regenerated" builds more trust than a shaky number.

## Anticipated Q&A (have backup slides)

- Prior / model dependence of the unfold.
- Regularization = iteration count **plus** classifier capacity.
- Handling of backgrounds / fakes / misses.
- How uncertainties propagate through a learned classifier.
- GBDT vs NN choice (you have the NN cross-check).
- The block-summing covariance question (above).
