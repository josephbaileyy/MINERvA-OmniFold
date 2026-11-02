# PROPOSAL 1B staged method coverage, stage 1 redesigned: the nature composed to first order (2026-11-02)

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

**This proposes one change.** Each drawn nature is composed from its universes **to first order**: the sum of the
single-universe departures from the CV, in place of their product.
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

**What first order draws.** a_D = a_CV + Σ_j (a_{u_j} − a_CV), that is a_CV (1 + Σ_j δ_j). The nature's departure
from the CV is then exactly the sum of the departures that C_T's blocks are built from. The test asks the declared
question: does C_T, remade by the reported procedure, cover natures drawn from the model it encodes?

**Two consistency points, both from the declaration's own text:**
- **Where a_CV = 0** the declaration already composes additively (§4.2: "a_D = a_{u₁} + Σ_{j≥2} a_{u_j}"). That
  is the first-order rule with a_CV = 0. The proposal makes the two branches one formula.
- **For k = 1** the sum is empty, so a_D = a_{u₁} exactly, and κ's nature is unchanged. Stage 0's PASS, and §9's
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
| §4.2, rows a_CV ≠ 0 | a_D = a_{u₁} ⊙ Π_{j≥2} (a_{u_j} / a_CV) | a_D = a_CV + Σ_j (a_{u_j} − a_CV) |
| §4.2, rows a_CV = 0 | a_D = a_{u₁} + Σ_{j≥2} a_{u_j} | the same formula; with a_CV = 0 it is this |
| the denominator, per cell | the composite tdw's denominator, and a detector `denom_nd` by its cell ratio | the same first-order rule per cell over each universe's own histogram (binding 2's amended per-cell composition) |
| flux histogram | the one flux universe's | unchanged (one flux universe per draw) |
| negative weights | kept, never clipped | kept, never clipped. A first-order composite can be negative where the CV is positive. The receipt counts these per array over the declared draws (descriptive) |
| N1 | bound 10; stop on the receipt's declared-draw pass and on `n1` | bound 10; the same stop. Below is the receipt's new all-draws bound |
| the cap | 250,000 rows per array | 250,000, unchanged |
| everything else | — | unchanged |

**The receipt's all-draws bound under first order.**
- **The bound.** For each row, the composite |a_D| / max_j |a_{u_j}| is at most (|a_CV| + Σ_b D_b) / max_b m_b, with
  D_b = max over band b's universes of |a_u − a_CV|, and m_b = min over them of |a_u|.
  - The numerator bounds |a_D| by the triangle inequality.
  - Every draw's max_j |a_{u_j}| is at least max_b m_b.
- **How it is used.** It is an upper bound, not the exact maximum that the product rule has. It only selects the
  rows that the exact pass over the 900 declared draws evaluates, and that exact pass decides, as now.
- **If the selection exceeds the cap,** the receipt STOPs on the cap, as binding 2's ruling 4 provides. The proposal
  does not change the cap to avoid that, because the cap must not be chosen from values either.

**Code (a new amendment, for a new binding).**
- `fd_1b_mc.compose` and `_single`'s composition change. `composite_n1` takes the first-order bound and the
  first-order exact pass.
- Tests:
  - the k = 1 identity;
  - the a_CV = 0 identity with the current rule;
  - the first-order rule against a direct sum;
  - the bound's validity on a fixture, so that the exact maximum over every draw is never above it;
  - the negative-composite count.
- A mutation receipt.
- `fd_1b_mc` is otherwise unchanged, so the tables, the null, the readout and the controls carry over.

## 3. Price

| item | node-h | note |
|---|---:|---|
| the new receipt (login node, `nice 19`) | 0 | measured on the product rule: 1:26:25 wall, 11.76 GB, about 208 GB read. First order needs the same passes, so similar |
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
2. **Does it change the paper's clause M?** It doesn't need to. "Drawn with the … uncertainties" is still true. The
   note would add one line: natures are composed to first order in each band's shift, as C_T is built.
3. **The cap and the bound stay** at 250,000 and 10.
4. **Joseph** decides whether to run this or to take §4's fallback.
