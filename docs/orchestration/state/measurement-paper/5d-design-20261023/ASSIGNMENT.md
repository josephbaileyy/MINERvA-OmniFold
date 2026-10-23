# Assignment: a serious 5D measurement design (2026-10-23)

**Assigned by** the paper-tighten lane, as director, under
[`DECISION-20261023-joseph-r8-r9-and-5d-scoping.md`](../../../DECISION-20261023-joseph-r8-r9-and-5d-scoping.md)
item 3. **Assigned to** the measurement session. **Compute: none.** This is a design document; any test it proposes
needs its own declaration and binding.

## The question

Joseph: "I still want to try and scope out the 5d measurements as a serious possibility." What would a publishable 5D
CC-inclusive cross-section measurement need, if its total uncertainty includes model dependence (regularization bias
and prior dependence)? What is the most promising route, what are its decisive cheap tests, and what would the full
programme cost in time, node-h (CPU and GPU) and storage?

## What the design must cover

1. **Estimand and reporting definition.** Which 5D cells or functionals are reported (RD1 J, RD2 H2 or RD3 EW from
   s5p, or a new definition), and why. Joseph excluded coarser or selected functionals as an endpoint change
   (DECISION-20261019 §1a). Say whether a proposal touches that, and flag it for him.
2. **The model-dependence uncertainty.** Construction and validation:
   - s5p stage 2 §2 P and §4: h, the prior-variation envelope (median 12.0 / 9.6 / 13.4 %);
   - amendment 6's correction: h is not a per-cell bound, and |shift| ≥ |bias| holds in only 52–78% of cells;
   - how to calibrate a scaled envelope so that it covers the bias at held-out truths. The held-out truths must not
     be the ones used to build it, so say which generators and tilts are available, given MP-2's closure.
3. **Can the model-dependence term shrink?** R10 (more reconstructed information) from the scoping memo, MP4-A's
   finding that a 2× reco refinement brings the floor to the edge of T1, IBU-1's result (UNRESOLVED; IBU leaves about
   the same departure residual as OmniFold), and anything else on the record.
4. **The central-value estimator** ((e) or (a)) and its covariance.
   - The 5D central values are (a) today, and no (e) covariance exists (DECISION-20261023 third).
     <!-- Search: configuration (e); (e) joint-test estimator; (e) joint-test estimator; joint-test estimator; R (s5e candidate); R (s5p baseline_estimator); configuration 1 = R; R = paper configuration (e); s5e candidate R = the joint-test estimator; --candidate R; --candidate R (contract implementation); refinement 400 trees, 31 leaves; refinement 400/31; 400-tree, 31-leaf Stay-Positive refinement; s5p data unfold @ afb7e1faddfb -->
   - Price building the five-axis covariance for the chosen estimator.
5. **Validation.**
   - Stress tests at held-out truths (bias inside the model-dependence term).
   - A coverage test of the total interval, at the sizes the director priced: pooled 400 per truth, about 2,600–7,600
     GPU node-h; per-functional, about 28,300.
   - Re-derive those figures from `gpu-timing-20261023/REPORT.md` and show the arithmetic. Note today's 1.4× CPU
     slowdown.
6. **Targets.** Which frozen targets (T1–T7) the route meets, which it cannot, and what Joseph would have to change.
   Say whether the resulting precision (median total half-width) would still let the measurement distinguish the
   generators the users care about (stage 1: 3.7–16% generator differences).
7. **Comparison with community practice.** Use the corpus in
   `state/2d-closeout/stageF/methods/register-prd-study/` (MINERvA, T2K, MicroBooNE papers): how published unfolded
   measurements validate and report model dependence. Say where our design is stricter or looser.
8. **A staged plan.** Each stage gives its decisive test, a pass rule fixed in advance, its cost and what it unlocks.
   Cheapest first. The plan ends at Joseph's GPU-campaign criterion.
9. **What would make the 5D measurement not worth pursuing,** stated as a falsifiable condition.

## Rules

- `COMMON-RULES.md` applies. Never invent a number: cite file:line for each. Use `tools/registry/whatis.py` for
  estimator names, and put its Search line beside any claim that something does not exist. <!-- absence-ok: states the rule itself, not a claim about a result -->
- Write `DESIGN.md` in this directory, with CATALOG and override rows as usual. Have it independently reviewed in two
  directions, then open a PR to the director. Run `bash .githooks/pre-commit` and
  `python3 tools/registry/absence_claims.py --base origin/main` before pushing. CI runs the record checks on every
  PR.
- No claim change. It goes to Joseph through the director.
