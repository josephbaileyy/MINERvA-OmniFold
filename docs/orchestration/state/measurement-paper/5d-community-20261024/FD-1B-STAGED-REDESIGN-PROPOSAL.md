# PROPOSAL 1B staged method coverage, stage 1 redesigned: the nature composed to first order (2026-11-02)

**Revision 1** (after `coverage-5b-audit`'s review, issuecomment-6588836213, and its D2 on #696):
- **B1 / D2:** a negative expected count gets a declared treatment, recommended from the code's own mean path, and a
  test through `toy_experiment` (§2a). The choice is the director's and Joseph's.
- **B2:** the rule is pinned as a_{u₁} + Σ_{j≥2} (a_{u_j} − a_CV) in the draw's order, so k = 1 is bitwise.
- **B3:** the narrower claim reaches clause M and CANNOT SUPPORT. The wording is drafted for Joseph (§2c).
- **B4:** the bound's 0/0 and max_b m_b = 0 conventions are stated, and tested against exhaustive enumeration (§2).
- **A1:** a foreseeable STOP on the cap is a choice for the director (§2d).
- **A2:** non-positive denominator cells get a rule (§2b).
- **A3:** the price is unchanged.

**By** the measurement session `coverage-5b`, for `coverage-5b-audit`, then the director, then Joseph before any
binding.

**Under:**
- `DECISION-20261101-joseph-1b-staged-method-coverage.md` (#663);
- Joseph's approval of a stage-1 redesign after stage 1's STOP (by the director, 2026-11-02);
- the director's terms:
  - a redesign of the toy construction, on grounds stated independently of the receipt's values;
  - N1's bound kept at 10;
  - a price;
  - routed to the audit, then the director, then Joseph.

**After:** [`FD-1B-STAGED-STAGE1-STOP-REPORT.md`](FD-1B-STAGED-STAGE1-STOP-REPORT.md), with stage 1 stopped at 0 node-h.

**This proposes one change, and the method choices it needs.** Each drawn nature is composed from its universes
**to first order**: the sum of the single-universe departures from the CV, in place of their product. With it come:
- a declared treatment of negative expected counts (§2a). Binding 2's toys would already have needed one (D2);
- a rule for non-positive denominator cells (§2b);
- the narrower claim's wording (§2c).
- Everything else in declaration revision 2 stands: the truths, the draws, the seeds, the grading, the null, the
  controls, the paper text and N1's bound of 10.
- Stage 0's κ is unaffected. The two rules agree exactly for one universe, which is κ's nature.

**What it cannot do:**
- it does not use the receipt's or the attribution's values to pick the rule, the bound or the cap;
- it does not claim the new composition will pass N1. The receipt under the new rule decides that, after binding, and
  a STOP there stops again at 0 node-h;
- it cannot authorize a job, a change to the reported covariance, or the paper's wording.

## 1. The ground (independent of the receipt's values)

**What the remade covariance is.** S1's covariance, which stage 1 remakes at each truth (declaration §4.3), is a sum
of per-band blocks.
- Each block is built from that band's universes **varied alone**, with every other band at its CV
  (`s5p_universe.universe_inputs`, one universe at a time).
- No block contains a term in which two bands' shifts act on the same event together. So C_T is the covariance of
  a nature whose departure from the CV is the **sum** of the single-band departures, to first order in each band's
  shift.

**What the current composition draws.** Declaration §4.2 composes a toy's nature as a product on rows where
a_CV ≠ 0: a_D = a_{u₁} ⊙ Π_{j≥2} (a_{u_j} / a_CV), over one universe from each of the 38 bands.
- Write a_{u_j} = a_CV (1 + δ_j). The product is then a_CV Π_j (1 + δ_j). This holds every cross-band term
  δ_i δ_j, δ_i δ_j δ_k, and so on, up to the 38-fold term.
- None of these terms is in any block of C_T, by construction. A coverage test against such natures tests the
  method together with the composition's higher-order terms, which C_T omits by design. The declaration's claim is
  narrower: clause M says "drawn with the … uncertainties … and $C_{\mathrm{total}}$ was rebuilt by the same
  procedure".

**What first order draws.** a_D = a_{u₁} + Σ_{j≥2} (a_{u_j} − a_CV), summed in the draw's order. That is
a_CV (1 + Σ_j δ_j) in exact arithmetic. Pinning the first term as a_{u₁} makes k = 1 bitwise a_{u₁} in floating
point (B2): the form a_CV + Σ_j (a_{u_j} − a_CV) differs from a_{u₁} in about 0.17 % of entries in float64 (the
audit's test). The nature's departure
from the CV is then exactly the sum of the departures that C_T's blocks are built from. The test asks the declared
question: does C_T, remade by the reported procedure, cover natures drawn from the model it encodes?

**Two consistency points, both from the declaration's own text:**
- **Where a_CV = 0** the declaration already composes additively (§4.2: "a_D = a_{u₁} + Σ_{j≥2} a_{u_j}"). That
  is the first-order rule with a_CV = 0, term for term. The proposal makes the two branches one formula.
- **For k = 1** the sum is empty, so a_D = a_{u₁} bitwise, and κ's nature is unchanged. Stage 0's PASS, and §9's
  bitwise control against κ's nature, carry over.

**How the STOP came in.** It prompted this re-examination, and that is stated openly. But the ground above uses
only C_T's construction and §4.2's text. It would hold with any receipt values, and it would have held before the
receipt was read. The attribution (the stop report's §3) is cited below only to say which mechanism the change acts on. It does not
select the change.

**Which of the two mechanisms it acts on** (the audit's question; stop report §3). The attribution found two kinds
of row above 10:
- (a) N1's premise: a small CV weight carrying one large ratio that multiplies the others;
- (b) compounding: an ordinary CV weight carrying many modest ratios above 1, multiplied across 38 bands. These are
  most of the count.

The change acts on **both**, by the same ground. Each is a product of shifts from different bands, and a product of
two bands' shifts is exactly a cross-band term absent from C_T.
- In (b) the product of 34 modest factors becomes their sum.
- In (a) the large ratio no longer multiplies the others. The composite becomes that universe's own departure plus
  theirs.

What the change does **not** remove is a large single ratio itself: S1's own universe (k = 1) holds it, and N1's
single ratios keep recording it, descriptive only. N1 stays as declared: a guard at 10, read by the receipt and by
each toy's record. This proposal does not compute, and does not predict, whether it fires under the new rule.

## 2. What changes, exactly

| site | now (declaration rev. 2, `fd_1b_mc` at M2) | proposed |
|---|---|---|
| §4.2, rows a_CV ≠ 0 | a_D = a_{u₁} ⊙ Π_{j≥2} (a_{u_j} / a_CV) | a_D = a_{u₁} + Σ_{j≥2} (a_{u_j} − a_CV), in the draw's order |
| §4.2, rows a_CV = 0 | a_D = a_{u₁} + Σ_{j≥2} a_{u_j} | the same formula; with a_CV = 0 it is this |
| the denominator, per cell | the composite tdw's denominator, and a detector `denom_nd` by its cell ratio | the same first-order rule per cell, d_{u₁} + Σ_{j≥2} (d_{u_j} − d_CV), over each universe's own histogram (binding 2's amended per-cell composition); non-positive cells per §2b |
| flux histogram | the one flux universe's | unchanged (one flux universe per draw) |
| negative weights | kept, never clipped | kept in the nature's arrays and its truth, never clipped. A first-order composite is negative on any row with Σ_j δ_j < −1. The receipt counts these per array over the declared draws (descriptive) |
| a negative expected count in a toy's Poisson draw | `rng.poisson` raises (D2) | §2a |
| N1 | bound 10; stop on the receipt's declared-draw pass and on `n1` | bound 10; the same stop. Below is the receipt's new all-draws bound |
| the cap | 250,000 rows per array | 250,000, unchanged |
| everything else | — | unchanged |

**The receipt's all-draws bound under first order.**
- **The bound.** For each row, the composite |a_D| / max_j |a_{u_j}| is at most (|a_CV| + Σ_b D_b) / max_b m_b, with
  D_b = max over band b's universes of |a_u − a_CV|, and m_b = min over them of |a_u|.
  - The numerator bounds |a_D| by the triangle inequality.
  - Every draw's max_j |a_{u_j}| is at least max_b m_b.
  - **Conventions (B4),** matching `composite_n1`'s existing per-draw rule (r = 1 where the composite and the peak are
    both 0):
    - a numerator of 0 gives a bound of 1;
    - a positive numerator over max_b m_b = 0 gives +∞, so the row is selected;
    - nothing is NaN.
- **How it is used.** It is an upper bound, not the exact maximum that the product rule has. It only selects the
  rows that the exact pass over the 900 declared draws evaluates, and that exact pass decides, as now.
- **If the selection exceeds the cap,** the receipt STOPs on the cap, as binding 2's ruling 4 provides. The proposal
  does not change the cap to avoid that, because the cap must not be chosen from values either. Since the bound is
  loose, that STOP is foreseeable (the audit's A1). §2d puts the choice to the director.

**Code (a new amendment, for a new binding).**
- `fd_1b_mc.compose` and `_single`'s composition change. `composite_n1` takes the first-order bound and the
  first-order exact pass.
- Tests:
  - the k = 1 identity;
  - the a_CV = 0 identity with the current rule;
  - the first-order rule against a direct sum;
  - the bound's validity against **exhaustive enumeration** of every draw on a fixture, so that the exact maximum is
    never above it. This includes rows with a_CV = 0, rows where every universe is 0 (0/0) and rows with
    max_b m_b = 0 (B4);
  - the negative-composite count;
  - **a toy through `toy_experiment`** with a negative composite in `w_reco` and in `bkg_w` (B1, D2). It must not
    raise. Its experiment must equal §2a's construction, and its mean must equal d_T bitwise (§9's d_T
    consistency control);
  - §2b's denominator rule, in both directions;
  - every mutant killed in a mutation receipt, including one reverting each of §2a and §2b.
- A mutation receipt.
- `fd_1b_mc` is otherwise unchanged, so the tables, the null, the readout and the controls carry over.

## 2a. Negative expected counts (B1, D2): a method choice for the director and Joseph

**The fact.** A toy draws pseudo-data as `rng.poisson(λ)` per reco-passing row and per background row
(`fd_1b_toys.build_full`), and numpy refuses λ < 0.
- Under binding 2's product rule, 684 of the 900 declared toys would hold such rows (D2, stop report §5). These come
  from LowQ2_1's and HighQ2_1's negative weights.
- First order can add rows, wherever Σ_j δ_j < −1.

**What the code already does at the mean.** The remade blocks' d_T, and every role that draws at the mean, build
their observed sample as the rows with n > 0 (`build_full`: `obs = … [n_sig > 0]`). So a row with λ ≤ 0 contributes
no event. The unfold's measured side keeps only positive observed counts and positive template weights as well
(`s5n_pseudo.signed_sample`, `s5n_pseudo.py:224–225`). So the analysis's construction, at the mean, already treats a
non-positive expected count as no events.

**The options:**

| option | the toy's draw on a row with λ < 0 | consequence |
|---|---|---|
| **(a) λ⁺ = max(λ, 0)** (recommended) | Poisson(0) = 0: no event | **Matches the mean path exactly.** At its mean, the toy builds d_T's arrays bitwise, so §9's d_T consistency control holds unchanged. The truth keeps the negative weights, as d_T's does. Row for row, the toy's expected sample is d_T's |
| (b) sign(λ) · Poisson(\|λ\|) | a negative count | `signed_sample` drops non-positive counts, so this collapses to (a) at the measured side unless the shared estimator code changes, which it must not (it is S1's). It would add a second implementation |
| (c) the mean on negative rows | λ, negative | dropped at `n > 0`, so it equals (a), less transparently |
| (d) refuse the toy | — | under the product rule, 684 of 900 toys refuse. Not a design |

**Recommendation: (a).** Its ground is consistency with the construction that d_T and the remade blocks already use,
not any value.
- **Where.** In stage 1's own code (`fd_1b_mc.toy_experiment` passes λ⁺ to the draw), without changing
  `fd_1b_toys.build_full`, which is bound for the original 1B and for stage 0.
- **What is counted.** Each toy records, per array, how many rows had λ < 0 and their total λ. `n1`-style, it is
  read before grading and is descriptive.
- **It applies whatever the composition rule.** D2 is a defect of binding 2 under the product rule too.

## 2b. Non-positive denominator cells (the audit's A2)

Under first order, a composite denominator cell d_D = d_{u₁} + Σ_{j≥2} (d_{u_j} − d_CV) can be ≤ 0, and the truth
cross section divides by it.
- **Proposed:** the receipt evaluates d_D over the 900 declared draws in every cell. If any cell is ≤ 0 in any
  declared draw, its verdict is STOP, at 0 node-h, as for N1.
- **Each toy** also refuses such a cell, so a STOP cannot be missed. Failing closed sets no threshold.

## 2c. The narrower claim (B3): wording drafted for Joseph

The claim is now that C_T covers natures drawn from its own first-order model. That must reach the paper text, not
just a note line. The wording is Joseph's. A draft follows.
- **Clause M (declaration §12), amended:**
  > The pseudo-data were drawn with the statistical, flux, interaction, detector, lateral and normalization
  > uncertainties, each universe's departure from the nominal simulation added to first order as
  > $C_{\mathrm{total}}$'s blocks are built, and unfolded with the nominal simulation, and $C_{\mathrm{total}}$ was
  > rebuilt by the same procedure at each tune's truth, with the lateral block carried to each truth rather than
  > rebuilt.
- **§13 CANNOT SUPPORT, added:** *coverage of natures in which two or more bands' shifts act on the same event
  together, beyond first order. C_T omits these terms by construction, and the toys do not draw them.*
- **Clause S, added in every outcome:**
  > The uncertainties were combined to first order, as the covariance is built, so this does not test their joint
  > higher-order effects.

## 2d. The cap: the director's choice (the audit's A1)

- **(i) Keep the cap at 250,000** and the bound-selected exact pass. A STOP on the cap is then possible and fails
  closed at 0 node-h.
- **(ii) Evaluate every row exactly** over the 900 declared draws, with no selection and no cap.
  - **Cost:** per array, a float32 matrix of rows × 175 universes, streamed one array at a time. That is three more
    bank passes on the login node at `nice 19`, about 1 to 2 h more wall at the measured rates, and 0 node-h.
  - **Memory** is rows × 175 × 4 B. The row count is measured at the receipt, before the matrix is allocated. If it
    does not fit in the login node's limit, the pass runs as ruling 5's one-node fallback.

I make no recommendation: either is defensible, and neither is chosen from a value.

## 3. Price

| item | node-h | note |
|---|---:|---|
| the new receipt (login node, `nice 19`) | 0 | measured on the product rule: 1:26:25 wall, 11.76 GB, about 208 GB read. First order needs the same passes, plus the denominator check (§2b). §2d (ii) adds about 1 to 2 h |
| S1-0 | 1.0 | unchanged (declaration §8) |
| the bulk with the plug-in | 72.0 | unchanged: the unfold's cost does not depend on how weights compose |
| **total** | **73.0** | unchanged from binding 2. The balance read at connect 32 was 2,050.9 node-h, half 1,025.5 |

- The engineering is a new amendment: code, tests and a mutation receipt, with no compute.
- If the receipt's fallback job is needed (binding 2 ruling 5), it is at most 1.0 node-h, outside the 73.0.

## 4. Alternatives considered, and why not

- **Keep the product and clip or cap composite weights.** Rejected: any clip level would be set against N1's
  values, which the director's term 4 forbids.
- **One band per toy, rotating.** Rejected: it tests each block's coverage alone, not C_T's. That is a different
  claim from clause M.
- **Continuous draws within each band, keeping the product.** Rejected: the bank holds only ±1σ endpoints (and
  2p2h's 3), so this would need an interpolation the analysis does not use. The cross-band terms would also remain.
- **Stop stage 1 and report method coverage as not validated.** This is the fallback, and it is Joseph's: the paper
  is unchanged and the stopped-attempt disclosure stays (declaration §12).

## 5. For the audit, the director and Joseph

1. **Is the ground sound?** C_T is first order in each band by construction, so natures composed to first order
   test what C_T claims. This is the audit's call first.
2. **The paper's wording** changes as drafted in §2c, which is Joseph's (B3).
3. **The bound stays at 10.** The cap is §2d's choice, which is the director's.
4. **Negative expected counts** take §2a's treatment, which is the director's and Joseph's. (a) is recommended.
5. **Non-positive denominator cells** follow §2b's fail-closed rule.
6. **Joseph** decides whether to run this or to take §4's fallback.
