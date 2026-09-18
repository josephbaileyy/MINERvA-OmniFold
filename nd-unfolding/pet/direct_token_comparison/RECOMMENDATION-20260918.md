# Recommendation for Ben: PET object representation

**One page. Diagnostic method development — not a publication product, not an
uncertainty, not a Gate-6 action.** Every number below is measured and cited; nothing
here is a demonstrated superiority claim.

## The recommendation

**Keep family pooling as the production default, and make aggregate overflow — not
individual-object routing — the next thing we test.** That is a practical development
choice under an inconclusive accuracy result, not a finding that pooling is better.

## 1. Individual-object versus pooled attention: no detectable difference, and a real price

Across eight paired seeds on the four-object fixture, individual-object routing gave a
median closure improvement of **+9.7%**, mean **+0.8%**, with seed-to-seed sd **25.8
percentage points**, a 95% interval of **[−20.7%, +22.4%]** and paired **p = 0.50**.
Six of eight seeds favoured it; none of that survives a significance test.

The price is now measured on a real GPU at the multiplicity real events have:

| | training | inference |
|---|---:|---:|
| at the mean operating point (12 blobs) | **1.244×** | **1.257×** |
| in the tail (85 blobs) | **1.879×** | **1.318×** |

**Pooling's cost is nearly flat in multiplicity** (27.2 → 30.0 ms per step across an
eightfold increase in objects); individual routing's is not (27.8 → 65.1 ms). Its cost
grows with exactly the multiplicity that would motivate it.

**Uncertainty, stated as a limit on what we can buy.** At the only scatter ever measured
— 25.8 points, and that is a *planning assumption* from a different fixture, two arms,
and a different denominator — resolving a 10-point effect needs **73 paired seeds ≈ 175
GPU-hours**, above the 130 authorized for the full study. The authorized budget resolves
10 points only if the variance pilot finds the scatter at or below about 11 points. That
is a real possibility — the finished matrix may have been evaluation-limited rather than
seed-limited — but it is not established, and it is the reason I am not recommending we
spend the budget on this question first.

## 2. Aggregation versus truncation: the larger effect, and it is free

Production does **not** keep every object. It truncates clouds to the twelve
highest-energy tokens (`docs/analysis-note/sec_pet.tex:56-57` at `66d35706`). I had this
wrong earlier and corrected it. Measured on the two pinned tuples (job 58470099, 17,930
data and 186,439 MC entries read in full):

* the cap binds in **64.1%** of data events and **84.4%** of MC events;
* the discarded clusters carry a **median 21% (data) / 45% (MC)** of the non-muon
  cluster energy;
* the note's reco-cluster means of 11.09 / 11.15 are *post*-truncation figures and
  saturate against the cap, so they cannot show this.

Aggregate overflow — keep the top eleven, spend the twelfth slot on the summed tail
four-momentum, its mean auxiliary block, a type code and the merged count upstream
discards — **costs nothing**: measured **1.007×** training and **0.978×** inference
against the incumbent, because it has identical token counts by construction.

**No closure measurement of aggregation exists.** What is established is an information
loss that is large and a remedy that is free. That combination is why it should be
tested before the routing question.

Two qualifications that travel with this: measured tail **energy** bounds how much the
cap could matter and does **not** establish predictive importance; and these are
unselected tuple entries, while the note's figure is selected and POT-weighted, so the
cap may bind less often than the table says.

## 3. Safeguards

The finished matrix returned **`NO_PASS`** with **142 of 146** checks holding. Two
failures *were* the inconclusive result; separately `shuffle-71` missed both
projection-difference checks marginally (0.0119 against a 0.01 limit, absolute errors
well inside 0.05) in one of eight null-control jobs.

The execution path for the four-arm experiment was validated across the intended
multiplicity range under criteria frozen before execution
(`VALIDATION_CRITERIA-20260918.json`, sha256 `abccd88b…`): **10 of 13 widths released,
no hard stop at any width**, covering 0 to 160 objects in a family. Repeatability is
bitwise, checkpoint reload is bitwise, masked slots cannot reach the output, the float64
Adam reference tracks all 42 weights, and a duplicate-arm null confirms the pipeline
manufactures no contrast between identically configured arms.

Three widths were not released, all on the finite-difference check alone. I diagnosed
rather than excused it: at the worst coordinate the finite-difference estimate
**converges to the analytic gradient** — relative error 1.8e-2 at the frozen step of
1e-2, 1.7e-3 at 3e-3, and **3.1e-4 at 1e-3** — falling as h², the signature of
truncation. So the gradient is right and the frozen step size was too large for those
coordinates. **I did not relax the criterion after seeing the failures**; releasing
those widths needs an amended criterion, which is Joseph's call.

One numerical result bears directly on the question: where the cross-device comparison
fails at high multiplicity, **pooled and individual fail equally** (gradient 4.96e-5 vs
4.38e-5; updated weights 1.78e-3 vs 1.68e-3 at 48 blobs), and the first failure as
multiplicity grows hits the **pooled** arm. The CPU/GPU discrepancy is not a property of
individual-object routing.

## 4. Applicability to production

Limited, and in a direction worth naming. In the fixture every generic slot is noise and
all signal is typed; in production the cluster cloud carries most of the information.
**Neither the direction nor the magnitude of a synthetic effect transfers
automatically** — a routing that wins when typed objects are the whole signal can lose
when they are largely redundant with the cluster cloud. An earlier draft of mine claimed
direction transfers and that the fixture gives an upper bound; both are withdrawn.

The cap findings transfer better, because they are measured on the real tuples rather
than on a fixture.

## 5. What I recommend now, and what would change it

1. **Keep family pooling.** Cheaper, flat in multiplicity, and no accuracy difference
   has been detected. Practical default, not a verdict.
2. **Test aggregation against truncation first.** It is free in compute and addresses a
   measured 21–45% energy loss in most events. This reverses the priority I started
   with.
3. **Run the variance pilot before committing to the routing study.** Its deliverable is
   the scatter for this endpoint. If that comes back above ~11 points, the routing
   question cannot be resolved to 10 points inside the authorized 130 GPU-hours, and the
   honest move is to say so rather than spend it.
4. **Nothing here is adopted for publication.** No result enters a covariance, a
   systematic, or an uncertainty. Typed objects and aggregate overflow remain
   prospective representation improvements, exactly as the note already says.

**Cost of everything so far: 16.0 GPU device-hours of the campaign's 290-hour ceiling**,
plus 2.0 CPU core-hours. The tail validation used 0.773 of its authorized 1.5 GPU-hours
across four submissions, one of which measured nothing.
