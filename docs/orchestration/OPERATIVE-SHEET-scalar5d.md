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
| **C4** | **DONE, `58547629`.** `SPEC:1237` "condition 4"→"condition 3" — **the correction is recorded HERE because `SPEC` is frozen at rev. 22 and a factual fix living only in a frozen document is the `variant`-in-a-docstring shape.** Measured jitter floor `‖x_cv(s+7) − x_cv‖² = 3.730946e-78`, `sqrt = 1.931566e-39`; **PRINT-ONLY**, the retired `tr_uni − jit_trace` **not** re-added; **condition-3 guard PASSED** (covariance digests identical across the jitter block); 10694 of 65856 reported bins |
| **C5** | closed as **not-falsified**, scoped to the 15 traced modules |
| **C6** | **REUSE**, risk named: *inputs consistent but unproven* |
| **C7** | closed as **sufficient**, on the twice-measured 45-band partition |
| **R5** | registry row amended to `z-cv.npz`; **not bookkeeping** — it had been naming the disqualified variant |

## 4. The source covariance — identified by measurement, not by filename

**`SRC_COV` = `uq_5d/z_pilot_20260916_a5/z-cv.npz`**, sha256
`3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5`, **`variant: "cv"`**.

`z-cv.npz` and `z-mean.npz` share **all seven keys and every array shape**, and are
**byte-identical** in `hXSecND_flat`, `hSupportMask`, `hPinnedMask` and `hRowIndex5D`.

⚠ **Two earlier statements of mine were wrong and are corrected here.** They do **not** have
identical **dtypes** — `metadata_json` is `<U1934` against `<U1936`, *necessarily*, because numpy's
`<U` encodes the string length. And they do **not** differ *only* in the covariance and
`hInflation_g`: **`metadata_json` differs too — and that difference is the entire mechanism
`--expect-variant` reads.** Omitting it described the guard as resting on nothing. The real
differences are `metadata_json`, `hInflation_g`, and the covariance (`√tr` `5.674201e-38` vs
`5.269506e-38`, ratio **`1.0768`**). **Choosing the wrong one understates the uncertainty scale by 7.13%, above `δ = 5%`, while
passing every other gate.** Enforced by **`project_cov_nd.py --expect-variant`, required, no
default**; designated in `z_pilot_20260916_a5/z-primary.json`. `AGENTS.md:29` disqualifies
mean-centering alone, so `--run-class publication` from `variant: "mean"` is refused outright.

### ⚠ RESIDUAL, RECORDED AND DELIBERATELY NOT FIXED

**The `AGENTS.md:29` refusal keys on the DECLARED variant, so it protects a MARKER, not a
property.** `--run-class publication` is refused when the caller declares `mean`. An **unmarked**
mean-centered object declared as `none` would clear it, because there is no `variant` field to
contradict and nothing in the file asserts its centering.

**Narrowed, not open.** The independent assessor formed that bypass hypothesis and **tested it**:
the `none` declaration is itself checked in its own direction — declaring `none` against a **marked**
source is refused outright — so the case it expected to slip is closed. Both pilot products are
marked, so the residual is **hypothetical for every artifact now on the required path** and would
require a future unmarked mean-centered object to become live.

**No guard is being built for it**, on the standing rule: the failure is nameable, the required
deliverable it would unblock is not. Recorded so a later lane meets the limit rather than
rediscovering it — and so nobody reads the variant guard as proving a *property* of the covariance
when what it verifies is an *agreement between a declaration and a marker*.

## 4b. WHAT THE NOTE MUST SAY about criteria that were never computed

**Landed before DOCS, not after.** DOCS re-verification checks the note against this section.

Governed by §1's standing rule — *no criterion may be described as having gated anything unless
production code computed it.* All seven declared boundaries measure `read_by_production: no`, so:

| subject | REQUIRED wording | FORBIDDEN wording |
|---|---|---|
| **C3** | a **predeclared** criterion whose **assessor has no production caller**, so its legs were **never computed** | "no second member was available" (true but weaker, and it invites the inference that the legs ran and were uninformative); "applied", "satisfied", "passed", "met" |
| **`s_proj`** | **implemented code at `z_statistics.py:203`** — the statistic exists and is computable | omitting this, which would make the C3 disclosure sweeping rather than accurate |
| **`δ = 5%`** | **declared and disclosed; not evaluated in production** | "the 5% tolerance was met" |
| **coverage `0.99` / `1.0`** | **declared and disclosed; not evaluated in production** | "coverage was achieved" |

**Why the distinction is load-bearing:** *"the criterion lacked a second member"* and *"the assessor
has never run"* are different disclosures and **only the second is true.** A reader given the first
would reasonably conclude the legs were computed and came out uninformative. They were not computed.

## 4c. PROJ — the mode, the PREDECLARED bounds, and the pairing established by measurement

**MODE: `receiving-cells`.** Not the weaker option — the only one whose premise holds here.
`--dst-cv` exists to compare `M x_src` against an **independently produced** lower-D central value.
For this destination there is no second party: `sec_eavailw.tex:37-39` states the note *projects the
unfolded five-axis result onto `(E_avail,W)` and subtracts the GENIE central value*, so the quantity
quoted in that plane **is** the projection. **TWO GROUNDS, BOTH MEASURED. A third was asserted and is STRUCK — see below.**

1. **No product on disk carries `hXSecND_flat` at 42 bins.** `xsec_2d_CTRL_*` is 224,
   `xsec_2d_FPS_*` is 285. `excess_eavail_W.root` is the right 7×6 grid but under key `hData2D`,
   a `TH2`, not the flat vector `--dst-cv` reads at `:435`.
2. **The quantity in that plane IS the projection — PROVEN, not argued.** `hData2D` equals
   `M x_src` to `1.3e-15` relative (below). So there is no independent **measurement** for
   `--dst-cv` to check against. There is an independent **implementation**, and it is used correctly
   as a cross-check rather than manufactured into a `dst-cv` operand: routing the same projection
   through `--dst-cv` would add a converted file and **no information**.

⚠ **STRUCK, AND IT WAS MINE.** I wrote that `excess_eavail_W.root` *"is an EXCESS not a cross
section"* and used it as a third ground. **It is false.** Measured: `hData2D` is **nonnegative
everywhere** (min `1.408e-44`) — the projected data cross section; `hExcess2D` is a **separate**
histogram that **changes sign** (`-1.930e-40` … `8.500e-40`) — that is the excess. The file is named
for its purpose, not its contents. **I inferred the content of a histogram from the file's name
without reading a bin**, and it survived into a ruling until the numbers contradicted it. Recorded
here rather than deleted, because the ruling would otherwise rest on three grounds of which one is
wrong — the same shape as a record claiming more verification than was performed.
**AND THE NORMALIZATION IS NOW ESTABLISHED, from the producer rather than from the outputs.**
`excess_eavail_W.py` states it: `hData2D` is `md`, the **density** `dσ/(dE_avail dW)` (`:212`);
`hGenCV2D` is `mg`, the GENIE density (`:213`); and `hExcess2D` is `exc = sig_d - sig_g` where
`sig_d = md * dvol` and `dvol = outer(diff(eav_e), diff(W_e))` (`:134-136`, `:165`). So

> **`hExcess2D` = (`hData2D` − `hGenCV2D`) × per-cell bin volume `ΔE_avail·ΔW`.**

"sigma" in its title means **cross section, not standard deviation.** That is why both earlier
guesses missed: `1.272585e-38` is the unweighted density difference, `3.642261e-39` the
volume-weighted one. **No DOCS finding** — the note's percentages (`:166`, `:169`, `:177`) are
fractions of `exc[exc>0].sum()`, i.e. of the **positive integrated** excess, which is the correct
weighting for apportioning a total; a density-weighted percentage would have been the error.

⚠ **This also strengthens the pairing check above, unintentionally.** `hCV_marginal` was compared
against `hData2D`, which is a **density** — and they agree to `1.3e-15`. Had the projector emitted
an integrated `M x_src` instead, the two would have differed by `dvol` and the check would have
**failed**. So the comparison silently verified **unit consistency** between the covariance's
central values and the figure's, not only provenance.

Forcing `--dst-cv` would require producing a frozen `(E_avail,W)` central value first — new
scientific work outside the §2 table.

### PREDECLARED before the run, per §6.4's discipline that bounds are fixed before production

| quantity | status | why |
|---|---|---|
| `src_cells_dropped` | **must be `0` — structural requirement** | a source cell mapping outside the destination is **discarded uncertainty**. Computed OUTSIDE the `--dst-cv` branch, so it is a genuine measurement in both modes |
| `rel` (CV reproduction) | **does not exist here; nothing reported** | gated behind `--dst-cv`; it was **never computed for the diagnostic either** |
| PSD, exact symmetry, `hRowIndex` readback digest | reported, as the diagnostic did | |

⚠ **`n_empty` IS NOT ON THAT LIST, and its absence is the point.** It was going to appear
annotated *"recorded, not evidence"*. That is not enough: **a quantity that is zero by construction,
left in a check list with a caveat, gets re-read as verification** — which is exactly how it reached
Joseph as evidence the first time. It is therefore **removed from the declared checks entirely**.
The projector still *writes* the field (`:488`), because a recorded quantity is not the same thing
as a checked one; nothing may cite it as a check.

⚠ **The withdrawal, kept so the correction travels with the number:** the diagnostic M1 was reported
as *"verified: `n_empty 0`"*.
Its receipt records `dst_cv_sha256: None`, so it ran in this same mode and **that zero was
structurally guaranteed and was never evidence.** `src_cells_dropped 0` stands as real.

### The pairing is ESTABLISHED BY MEASUREMENT, not asserted from the algebra

*"By construction"* is exactly how a pairing fails silently: the risk is not that `M C Mᵀ` is wrong,
it is that the note's figure was produced by a **different `M`, or a different source**, than the
covariance quoted beside it. Both were measured, and both pass:

| | check | result |
|---|---|---|
| **PRIMARY — the claim** | **same source, by DIGEST** | the figure's `xsec_5d_MEFHC_5iter_lgbm.root:hXSecND_flat` and PROJ's `z-cv.npz:hXSecND_flat` are **byte-identical**, digest `d94daca9251d0951`, `65856` entries, `10694` reported |
| corroboration | same `M`, by agreement | M1's `hCV_marginal` against the figure's `hData2D`, **C-order**: sums agree to seven digits (`1.676366e-37`), **max abs diff `5.220244e-54`** on elements of order `4e-39` — relative `~1.3e-15` |
| corroboration | row order | F-order gives `3.07e-38`, three orders larger, so **C-order is measured, not assumed** |

**The ordering is deliberate.** Numerical agreement shows two arrays hold the same numbers; it does
**not** show they came from the same **run**, which is what *paired* must mean once a rebuild can
change the source. **Digest identity is the claim; two-implementation agreement corroborates it.**

`excess_eavail_W.py` reaches `(E_avail,W)` by its own summation, a **different code path** from
`project_cov_nd.build_projection`. They agree at round-off anyway, which is what makes this a
falsifiable check rather than a restatement.

> **BINDING, not a courtesy:** repeat (a) and (b) against the **publication** product when PROJ
> runs — **(a), the digest, is the binding one**; (b) corroborates. **Any disagreement is a FINDING, not a tolerance question**, and the figure is regenerated
> from the adopted product before DOCS is re-verified.

## 4d. THE GENERAL RULE, and the exercise state of all six catalogued protections

> ### A STEP WHOSE VERIFICATION IS NOT ON THE PATH THE FAILURE TAKES CANNOT CATCH THAT FAILURE.

**Seven instances, same structure every time.** `import ROOT` above argparse, so every guard died
before it could fire. A destination mask defined as *whatever received a source cell*, so `n_empty`
could only be zero. A flag built into an array and never passed to the command. `variant` read by
nothing. An adoption gate satisfied by a routing document. An edit whose match failed silently while
its commit returned zero — in a document about records overstating what they establish. And **the
seventh is mine, in the instrument built to catch the others:** the guard-set control's checker
tested `expect REFUSE and rc == 0`, so three **segfaults** at `rc=139` were reported as three
refusals. Three guards that never executed read as three that fired.

**Corollary, and it is the operative half:** *a unit test is not an exercise, and "exits nonzero" is
not a control.* A refusal must be pinned to its **exact exit code AND its own message**, and a crash
must be named as a crash.

### Exercise state — real path, with a control that could have failed

| # | protection | refuse arm | accept arm / control | state |
|---|---|---|---|---|
| 1 | adoption record — `ADOPTS-SHA256` sentinel | **A2**, real launcher: the §6.4 amendment, which **names the right digest**, refused `rc 3` *"does not state an adoption"* | **not exercised — needs Joseph's record** | **partial, and it cannot be closed before ADOPT** |
| 2 | rc-1 once admitted a routing document | **A2** is that case on the real path; **A1** distinguishes *file absent* from *present but not adopting* | same as 1 | **partial**, same reason |
| 3 | `--expect-variant` | **B2** cv declared mean, **B3** mean declared cv — both directions | **B4** must PRODUCE on cv/cv | **covered, pending `58552664`** |
| 4 | `--run-class`, once passed zero times | **NONE.** every leg passes `publication` **with** the exception, so the `adoptable:false` refusal it gates never fires | — | **GAP** |
| 5 | `--adoption-exception` | **passed-and-valid: B4.** **set-but-missing → rc 3: NONE** | — | **GAP on one arm** |
| 6 | import ordering | **B1–B3 run WITHOUT the production environment** — with the fix they must refuse on a bare interpreter | **B4 sources it and writes** | **covered by design, pending `58552664`** |

### THE OPERATIVE CRITERION — stated so it HAS an exit

An earlier form of this — *"every protection exercised"* — **has no exit condition** if it counts
accept arms that cannot be exercised without the act itself. A criterion that cannot be satisfied is
not a criterion; that is the same defect the assessor withdrew from its own verdict. So:

> **Every protection's REFUSE arm exercised on the real path with a positive control; and every
> ACCEPT arm either exercised, or explicitly DEFERRED TO THE ACT with its failure mode named.**

**Items 1 and 2 are PARTIAL-AND-ACCEPTABLE under that form, and the reason is a category
difference, not a concession.** Their accept arm is deferred to ADOPT, and its failure mode is
**loud and immediate**: Joseph runs the launcher with the real record and it either produces or
refuses **on the spot**, with nothing downstream having happened. That is a **recoverable wasted
step**. Gaps **4** and **5** are categorically worse: a refusal that never fires leaves a **wrong
product indistinguishable from a right one**, and nothing later separates them.

⚠ **No synthetic accept-arm test will be built for items 1–2.** It would require a document carrying
a live `ADOPTS-SHA256` line, and **such a document is an adoption record wherever it sits.** A decoy
would be the thing itself.

**The two gaps, priced rather than built.** Both sit inside the control's existing scope and neither
needs new machinery: **A3** — `MNV_ADOPTION_EXCEPTION` set to a missing path, expect `rc 3`; refuses
before any file is read, so **≈0 cost**. **B5** — `publication` + `cv` + **no** exception, expect the
`adoptable: false` refusal; one more 890 MB read, **≈0.1 CPU task-h**. **Both APPROVED as one follow-on run.**

**Gap 4 is the priority, and its ground is on the record:** `--run-class` is the protection that was
once passed **zero** times, which left the `adoptable: false` refusal unreachable — and that refusal
is **the single most load-bearing guard for this adoption**, because it is what stops a
`NON-PASSING` source being published **without** the exception. Every leg so far passes
`publication` **with** the exception, so **the guard that makes this source special has never
fired.** `B5` is exactly that case and is worth the 890 MB read.

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
