# Five-dimensional detector-response-mismatch closure

**Status:** implemented, not run, diagnostic only, no pass threshold adopted.

**Scientific source:** Kevin McFarland suggested deliberately generating
pseudo-data with a smearing model that disagrees with the model supplied to the
unfold, then examining the induced bias at low `W` (private communication to
Joseph Bailey and Benjamin Nachman). The private email and sender address are
not reproduced in this public repository. The analysis-note treatment is
`docs/analysis-note/app_response_mismatch.tex`.

This file is a design and execution contract. It is not authorization to submit
compute, adopt a result, change the central value, or add an uncertainty.

## Question

Do the five-dimensional OmniFold weights create a material bias in `W`,
especially `W < 1.1 GeV`, when the pseudo-data hadronic response is deliberately
incompatible with the nominal MC response used by the unfold?

Existing truth-reweight closures do not answer this. They alter the event
population while retaining the nominal conditional response
`p(x_reco | x_truth)`. This test alters a reconstructed pseudo-data record while
holding the response model and truth reference fixed.

## Pipeline insertion

The test lives in `unfold_nd_omnifold_unbinned.py` at the pseudo-data boundary:

1. select closure events and copy the reconstructed pseudo-data arrays;
2. multiply only copied pseudo-data `E_avail` by `1 + epsilon`;
3. leave nominal MC reco, truth coordinates, weights, and event membership fixed;
4. proceed through the normal background and OmniFold path;
5. compare the result to unmodified nominal truth.

This ordering is load-bearing. Applying the shift in the event reader would
also change the response model and collapse the intended mismatch. Applying it
after training would not test the estimator.

The CLI is:

```text
python nd-unfolding/unfold_nd_omnifold_unbinned.py \
  --omnifile INPUT.root \
  --axes eavail,q3,W --iters 5 --use-weights --estimator lgbm \
  --closure --closure-response-eavail-frac EPSILON \
  --out OUTPUT_DIRECTORY/NONQUOTABLE-DIAGNOSTIC.response-eavail.root
```

The driver rejects this option unless all of the following hold:

- closure mode is active;
- the exact scalar five-dimensional axis list is used;
- no truth-reweight injection or bootstrap is combined with it;
- `epsilon` is finite, nonzero, and greater than `-1`;
- the output basename begins `NONQUOTABLE-DIAGNOSTIC.`.

The ROOT output also carries `analysis_status=NONQUOTABLE-DIAGNOSTIC`, the
closure kind, the shift, and a statement of what remained fixed. In addition to
the ordinary full-dimensional closure products it writes
`hClosureRatio_eavail_W`.

## Pre-run decision still required

The magnitude must be frozen before looking at a result, and both `+epsilon`
and `-epsilon` arms must be run. Do not infer an envelope from the inherited
`1.17` reconstructed-`E_avail` factor: `KNOWN_ISSUES.md` issue 26 / `OI-31`
records that its lineage exists but its justification does not. A run must
instead name either:

- a documented response-systematic magnitude that the arms represent; or
- an explicit assumed stress amplitude and the reason it is informative.

The predeclaration must also fix a decision statistic and threshold. At minimum
it should report signed unfolded/reference bias in each `W` bin, a separate
summary over `W < 1.1 GeV`, the full `(E_avail,W)` ratio map, and the integrated
cross section as a control. The global integral alone cannot decide the test.

No currently running covariance job should be modified, redeployed, or reused
for this diagnostic. Any future execution must use the guarded launch route and
the then-current live authorization.

## Stronger follow-up

The record-only shift is a deliberately inconsistent stress test. The
physically correlated version proposed in the same communication is:

1. identify quasielastic events;
2. shift the leading-nucleon energy up and down;
3. recompute reconstructed `E_avail`, `q3`, `W`, and affected selection from the
   altered low-level record;
4. use those events as pseudo-data while the unfold retains the nominal response.

The present scalar trees do not preserve the low-level leading-nucleon record
and interaction association needed for a faithful recomputation. That version
requires a dedicated diagnostic event-loop output. It is a follow-up unless the
cheap arm produces a material bias or MINERvA requests the stronger closure.

## Interpretation boundary

A small bias supports stability only within the frozen test envelope. A large
bias triggers a scientific decision about response modeling and uncertainty; it
is not automatically an uncertainty component. Neither outcome, by itself,
authorizes adoption or changes the validated central-value products.
