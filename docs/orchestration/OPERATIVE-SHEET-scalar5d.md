# OPERATIVE SHEET — scalar-5D required deliverables

**CITABLE FOR:** what is currently in force on the required path — the boundaries, the functional
set, the cause dispositions, the execution order, the reserved acts.
**NOT CITABLE FOR:** history, derivations, or why a number is what it is. Those live in
[`AUTHORIZATION-20260918-d-resource-required-deliverable-path.md`](AUTHORIZATION-20260918-d-resource-required-deliverable-path.md)
and in the code that declares each boundary.

**This is an EXTRACT, not a new authority.** `SPEC` is **FROZEN at rev. 22** and is now historical:
no rev. 23, no "what changed in rev. N" section, no packet superseding a packet. **Results go to
the ledger; corrections go inline where the error is.** Where this sheet and a canonical artifact
disagree, **the canonical artifact wins** — every number below is declared in code, and the code is
the authority.

---

## 1. Boundaries — all in `nd-unfolding/z_contract.py`, each with provenance

**`read by production` is MEASURED, never asserted.** Re-measure with
`python3 nd-unfolding/boundary_readership.py`; `tests/test_boundary_readership.py` fails if this
table disagrees with it, so the column cannot go stale the way an index does. A boundary named as a
`boundary_key` string is **not** read — that records an intent to read.

| boundary | value | read by production | note |
|---|---|---|---|
| `cause3_agg` | `0.05` | **no** — named only in `z_validator.py` | **direct movement bound, never quadrature** |
| `cause3_med` | `0.05` | **no** — named only in `z_validator.py` | per-bin leg |
| `cause3_corr` | `0.05` | **no** — named only in `z_validator.py` | `s_proj` leg |
| `cause3_med_coverage` | `0.99` | **no** — not referenced outside its declaration | full reported support |
| `cause3_corr_coverage` | `1.0` | **no** — not referenced outside its declaration | the functional set |
| `cause2_f7_margin` | `0.168` | **no** — not referenced outside its declaration | outside `[0.832, 1.168]` or `INCONCLUSIVE` |
| `null_epsilon` | **WITHHELD** | **no** — named only in `z_validator.py` | §6.4 makes it moot for the required path |

⚠ **Every declared boundary reads `no`, and that is the honest state, not an oversight.** The only
code that reads a boundary's value is `z_validator.assess`, which has **no caller outside `tests/`**;
`z_validator.py` has no `__main__` and no launcher names it. So the cause-3 legs are **predeclared
and never computed in production.**

> **STANDING RULE FOR THE NOTE: no criterion may be described as having gated anything unless
> production code computed it.** A criterion whose `read by production` is `no` may be described as
> *declared*, *predeclared*, or *binding on future members* — never as *applied*, *satisfied*,
> *passed*, or *met*. This is why C3's disclosure says the assessor has never run, rather than the
> weaker and untrue "no second member was available".

**Coverage, in full:** **100%** on bins entering a quoted projection, **≥99%** on the full reported
support, and **every failing bin enumerated in the receipt, never absorbed.**

## 2. `s_proj` — the functional set

The **rows of `project_cov_nd.py`'s `M`, plus the all-ones vector.** `s_proj` is the **maximum
relative change in `√(uᵀCu)` over that set**; reporting class **`per-bin`**. Declared in
`z_validator.py`'s `Z_LEG_SET`, and **implemented as real code at `z_statistics.py:203`** — that
distinction keeps §1's disclosure accurate rather than sweeping: the statistic EXISTS and is
computable; what has never run is the ASSESSOR that would compare it to `cause3_corr`. The set **dissolves** the region question rather than answering it;
the earlier corner-integral criterion is a strictly weaker special case.

## 3. Cause dispositions

| | |
|---|---|
| **C1** | tolerance-free **disclosure**. Done, `58530433`: P leg **MET**, M leg **MEASURED** |
| **C2** | margin `0.168`; measured `2.6739` clears it by `2.29×` |
| **C3** | criterion **declared and UNEVALUATED**, disclosed. Ruling 2 declined the only additional member, so a max over one difference is undefined |
| **C4** | `SPEC:1237` "condition 4"→"condition 3", then the jitter print |
| **C5** | closed as **not-falsified**, scoped to the 15 traced modules |
| **C6** | **REUSE**, risk named: *inputs consistent but unproven* |
| **C7** | closed as **sufficient**, on the twice-measured 45-band partition |
| **R5** | registry row amended to `z-cv.npz`; **not bookkeeping** — it had been naming the disqualified variant |

## 4. The source covariance — identified by measurement, not by filename

**`SRC_COV` = `uq_5d/z_pilot_20260916_a5/z-cv.npz`**, sha256
`3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5`, **`variant: "cv"`**.

`z-cv.npz` and `z-mean.npz` are **structurally identical** — same seven keys, same shapes, same
dtypes, byte-identical `hXSecND_flat`, `hSupportMask`, `hPinnedMask`, `hRowIndex5D`. They differ in
the covariance (`√tr` `5.674201e-38` vs `5.269506e-38`, ratio **`1.0768`**) and in one metadata
field. **Choosing the wrong one understates the uncertainty scale by 7.13%, above `δ = 5%`, while
passing every other gate.** Enforced by **`project_cov_nd.py --expect-variant`, required, no
default**; designated in `z_pilot_20260916_a5/z-primary.json`. `AGENTS.md:29` disqualifies
mean-centering alone, so `--run-class publication` from `variant: "mean"` is refused outright.

## 5. Execution order — fixed

**C1–C7 complete → NULL resolved (P0 first, zero-compute; P2 NOT authorized) → SRC_COV identified
by measurement → ADOPT → PROJ with `--run-class publication` → DOCS re-verified.**

## 6. The three reserved acts

1. **ADOPT**
2. **Any material change to the estimator** — including `deterministic` / `force_row_wise` /
   `num_threads` on `make_estimators`, which stays reserved and is **not** to be routed around
3. **Anything outward-facing**, submission included

**Everything else on the §2 required-row table is delegated: execute and report after.**
**Before any repair round, name the failure it prevents and the required deliverable it unblocks.**
If both cannot be named, it is not on the path.
