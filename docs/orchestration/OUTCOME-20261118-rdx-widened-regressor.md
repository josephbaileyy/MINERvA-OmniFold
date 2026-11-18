# OUTCOME 2026-11-18: RDX, the widened misses regressor. LICENSED

**Recorded by** session tier3-design, for the director. **The design:** `RDX-DECLARATION.md` (§4 fixes the readings
and outcomes before any run), bound by `RDX-BINDING-1.md`. **The reader:** `nd-unfolding/rdx/rdx_read.py`, bound by
addendum J7 at M_RDXR = `9de8ef0d` (sha256 `cc25f176…`). **The run:** stage 3, jobs 61478320 (S3a) and 61481240 (S3b),
both COMPLETED, receipts #1208 and #1214.

**Status.** The director reviewed this record uncommitted, including the X1p check, and accepted it on 2026-11-18. It
contains no note or paper wording. The one sentence in quotation marks below is §4's own declared sentence. Any
note-facing text goes to a side branch, off draft/note-round2, until Joseph and Ben agree (J7 ruling 4).
<!-- absence-ok: an operational status of this record, not a claim that a result does not exist -->

## The records

All of these are in the receipt `fd/redump-f12i-20261112/read-20261118/`.

- `rdx_readout.json`, sha256 `0f5158f46656283455659d9120f7ec731ac3cfb10b13e54860546515dce189f8`. The bound reader
  produced it in a clean clone at M_RDXR, on the laptop, under Python 3.12.2 and numpy 1.26.4. It read only the
  fetched files, the reader's committed inputs (i0.json, cmodel_5d.json, the F1 readout, the H2 definition, the task
  table and the input sums) and RSN's bound reader. Its `inputs` and `code_sha256` blocks pin every one of them.
  Exit 0 (`run.txt`). Console line: `NC-X PASS; R1p W0; R1 W1 (excess cells []); R2 W0; R3 X1t T1, X0t T1; R4 prior W0, gibuu W1,
  q3 W1, weight W0; OUTCOME LICENSED`.
- **The fetch** (J7 ruling 3, PR #1223 at main `ee6a774c`): launcher `2650c5ca`, remote `89ea886d`, run on login27 on
  2026-11-18 from 19:19:28Z to 19:21:31Z, under cov2d ack `cov2d-ack-rdx-fetch-20261118-c`.
  - It copied 32 files: the 15 products, their 15 inventories and the two job logs.
  - Every read used O_NOATIME, and no file's stat moved.
  - Both sacct fence reads were clear, with 147 rows and no fenced-family job in a non-terminal state.
  - Every sha256 matched at unpack.
  - The tar's sha256 is `585473096f3880a59b8b9623c47074c4d9105511936c0702c337412fadeee116` (`fetch-launch.txt`), and
    its manifest is kept as `fetch-manifest.json`, sha256
    `e4dde4de4686f3462292e37ad00a354de5eb4316e5317e58a825b7e7688f2c1e`.

  This was the third attempt. The first, at 18:40Z, stopped at its own fence because sacct rejected the state code CF
  (`stop-a-launch.txt`); rev 3 fixed that. The second, at 19:15Z, failed at ssh transport (rc 255,
  `stop-b-launch.txt`). Neither attempt read any file. A one-connection probe then reached login27 (`probe.txt`).
- **The reader's own checks** all passed before any reading:
  - the task table is the bound one;
  - each product's sha256 is the one its job printed;
  - the producer's arrays and meta are present;
  - NC-X holds: X0 and X0_lat are bitwise equal;
  - each closure family shares one truth bitwise;
  - φ_c and σ_c are 16 finite positive values.

**The cost:** 1.6695 of the 2.5 CPU node-h cap (s1 0.0704, s2 0.7605, m 0.3183, s3a 0.2606, s3b 0.2597;
`run-s3b-20261117/README.md`). The fetch and the read cost 0 node-h.

## The readings (`RDX-DECLARATION.md` §4)

σ_c is the reported relative σ (0.048–0.141 over the 16 cells). φ_c is RSN's rounding floor (0.00055–0.00252), which §4
calls conservative in MP-1's chain. The classes are RSN's:
- **W0:** every |Δ_c| ≤ 2 φ_c.
- **W1:** above that floor, but no cell beyond 0.5 σ_c.
- **W2:** some cell beyond 0.5 σ_c, which is named.

T0/T1/T2 are the same thresholds applied to the transfer bias. Cells are R00–R15.

| reading | quantity | class | largest \|Δ\|/σ (cell) | cells named |
|---|---|---|---|---|
| R1p, the refit null | X1p / X0 − 1 | **W0** | 0 (every cell) | none |
| R1, the widened inputs | X1 / X0 − 1 | **W1** | 0.0559 (R08); largest \|Δ\|/φ is 3.74 (R01) | none |
| R1's attributable excess | e_c = \|δ1_c\| − \|δp_c\| against 0.5 σ_c | within | max e_c/σ_c = 0.0559 | none |
| R2, the weight (qualifies R1) | X1w / X1 − 1 | **W0** | 0.0269 (R09); largest \|Δ\|/φ is 1.95 | none |
| R3, X1t's transfer | t_c at the last iteration | **T1** | 0.0849 (R11) | none |
| R3, X0t's transfer | t_c at the last iteration | **T1** | 0.1036 (R10) | none |
| R3, the difference | t_c(X1t) − t_c(X0t) | **T0** | 0.0230 (R10) | none |
| R4 at the prior | the signed residual [b(X1c) − b(X0c)] − [b(X1pc) − b(X0c)] (J7 ruling 3) | **W0** | 3.9 × 10⁻⁵ (R14) | none |
| R4 at the A7 GiBUU hybrid | b(X1g) − b(X0g), read in full (J7 ruling 4) | **W1** | 0.0566 (R02); largest \|Δ\|/φ is 4.51 | none |
| R4 at the q3 tilt | b(X1q) − b(X0q), read in full | **W1** | 0.0274 (R15); largest \|Δ\|/φ is 2.05 | none |
| R4, the weight at the prior (qualifier, J7 ruling 5) | X1wc − X1c | **W0** | 2.0 × 10⁻⁵ (R04) | none |

Also recorded:
- X1t's and X0t's unfolded results equal X1's and X0's bitwise (`R3.loop_untouched`): the transfer masking left the
  unfolding untouched.
- X1 does not equal X0 bitwise.

## The outcome

All of §4's conditions for the licensed sentence hold:
- NC-X passes;
- R1p is W0;
- max_c e_c = 0.0559 σ is at most 0.5 σ;
- R4's attributable changes are within W1 at all three truths: W0 at the prior, W1 at GiBUU, W1 at q3.

The outcome is **LICENSED** [`outcome.outcome`]. The declared sentence [`outcome.statement`]:

> "in MP-1's chain, adding E_ν, the true vertex and the leading-proton KE to the misses regressor moves the unfolded
> result by no more than half the reported σ in any cell, beyond the refit null"

It is silent on any quantity not added [`outcome.silent`]. The weight at the prior is W0, with a largest
|change|/σ of 2.0 × 10⁻⁵ [`outcome.weight_at_prior`], so no W2 statement accompanies the outcome. R2 (W0) and R3
(T1, T1; difference T0) qualify R1 and license nothing further.

## X1p bitwise equal to X0: checked, benign mechanism, not an arm defect

**The fact.** X1p's product is bitwise equal to X0's (xsec_flat, same dtype and bytes). X1's is not. X1p is the refit
null: the wide regressor with the five truthx columns permuted jointly across rows (seed 20261113). Its unfolded result
equals the standard regressor's exactly, so R1p's δp is 0 in every cell. The director asked for this to be checked
before the record merges. The check used the fetched files and the committed producer only, at 0 node-h.

**Did X1p's regressor see ten columns?** Yes, by everything recorded:
- The producer is `nd-unfolding/rdx/rdx_unfold.py` at sha256 `83d585a4…`. That is both X1's and X1p's recorded
  `rdx.code_sha256`, and it is the file on main. For `wide`, its wrapper replaces the misses regressor's `fit` and
  `predict` with `np.hstack([X, tx_rows])`, where `tx` is the sidecar's five columns. With `--truthx-permute` (X1p)
  it first applies `tx = tx[default_rng(seed).permutation(n)]` (`permuted()`, `main`). The widening path is the same
  for X1 and X1p. The only difference is the permutation.
- The wrapper refuses unless every one of the five iterations calls the widened fit on all reco-passing truth rows and
  the widened predict on all others. X1p records `fit_calls` 5, `predict_calls` 5 and `rows` 20,402,537, identical to
  X1. Its meta records `regressor_features: wide`, the permutation seed, and the sidecar's sha256 `641ba34c…`, the
  same sidecar as X1.

**Are the permuted columns non-constant, and different from X1's?**
- Indirectly, yes. X1's result differs from X0's (R1: largest |δ1|/σ = 0.056), so the sidecar's columns take splits
  and are not constant. A permutation keeps each column's values, so X1p's columns are not constant either.
- They differ from X1's unless `default_rng(20261113).permutation(n)` is the identity. Over millions of rows, the
  chance of that is negligible.
- Not checked directly: the sidecar itself is on pscratch and was not fetched.

**Why the result can be bitwise identical.** All three products record the same LightGBM parameters:
`colsample_bytree` 1.0, `subsample` 1.0, `subsample_freq` 0, `deterministic` true, `force_row_wise` true,
`num_leaves` 8, `n_estimators` 100, `random_state` 42. So no column sampling and no bagging. Each split takes the
best gain over all columns, and adding columns changes nothing random. If no tree in any of the five iterations
splits on one of the five permuted columns, each tree has the same splits, thresholds and leaf values as the
5-column model. Its predictions, and the unfolded result, are then bitwise equal. §4's premise that "column sampling
and split order change with the feature count" does not hold under these parameters: column sampling is off, and
a column that is never chosen does not change the split order.

**The same code does split on permuted columns elsewhere.** In the closure arm, X1pc (wide, permuted with the same
seed) is not bitwise X0c. Its null at the prior is at most 3.3 × 10⁻⁵ σ (R00), about 0.003 φ. So the permuted columns
reached the regressor and occasionally won a split there, with a negligible effect. In the data arm, with eight-leaf
trees on about 20 million rows, they never won one. That is consistent with permuted columns carrying no information
about the target.

**What is not established, and what a check would need.** The products and inventories record no split counts,
feature importances or model dumps. The inventories are the import guard's provenance records. So it cannot be shown
at 0 node-h that X1p's trees take no split on columns 5–9. A direct check would need one of:
- the regressor's split-feature counts from a refit of X1p (the fit is deterministic, so a refit reproduces the
  model): node-h, a new declaration and a go;
- the sidecar fetched to the laptop and a laptop refit: the inputs are about 20 M rows × 10 features, five
  iterations, which is not 0 node-h in practice and needs the inputs too.

The director placed this split-count check on the after-Ben list as optional. It is not needed for the license.

**Effect on the outcome: none.** δp = 0 means e_c = |δ1_c|, so nothing is subtracted from R1, the conservative
direction. The license stands on R1 alone (max e_c = 0.056 σ against 0.5 σ) and on R4. R1p's null is not void. It
was computed as declared and measured a refit effect of exactly zero in the data arm, for the reason above. Recorded
as **benign**, with the mechanism inferred from the parameters and the closure arm and not observed in X1p's trees.

## Limits (§0, D4)

- MP-1's chain only, and only for the three added quantities (E_ν, the true vertex, the leading-proton KE).
- A difference within MP-1's chain, not against the paper's chain.
- φ_c is the paper chain's floor, which is conservative here.
- One estimator seed (42), as RSN.
- No data-derived statement beyond the products' own unfolded result.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** RDX's readings and the LICENSED outcome as recorded, scoped as above.
- **Not citable for:** any note or paper sentence until Joseph and Ben agree on wording (J7 ruling 4); any quantity not
  added; any change to the reported unfolding.
