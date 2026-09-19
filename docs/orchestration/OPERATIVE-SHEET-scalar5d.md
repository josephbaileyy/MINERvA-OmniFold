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

## 1b. `cause2_f7_margin = 0.168` — PROVENANCE, and it is partly retrospective

Asked to justify `3/√318` **without reference to the observed ratio**. Taking the two factors
separately, because they do not have the same standing:

**`√318` — INDEPENDENTLY MOTIVATED.** `318 = 2(N−1)` at `N = 160`, and `1/√(2(N−1))` is the
asymptotic relative standard error of an estimated standard deviation from `N` draws. The branch
point `k·floor` is proportional to `√Tr`, estimated from those same `N` throws, so it **inherits
exactly that relative uncertainty**. This factor depends on `N` alone — fixed by the ensemble long
before any ratio was computed — and someone who had never seen `2.6739` and asked *"what is the
resolving power of this ensemble on the quantity that sets the branch point?"* arrives at it.

**The factor `3` — A CONVENTION, CHOSEN AFTER THE RATIO WAS KNOWN.** Nothing in this problem derives
`3` rather than `2` or `5`; it is the customary 3σ separation. **And the record shows I had the
answer in hand: I reported at the time that `1×`, `2×` and `3×` all clear.** That demonstrates
robustness and it equally demonstrates that candidate multipliers were checked against a known
outcome.

> **DISPOSITION: `0.168` is a DISCLOSED RETROSPECTIVE CHOICE in its multiplier, on an independently
> motivated scale.** Not presented as predeclared, and it is **not** claimed to satisfy §6.4's
> before-production discipline — which is in any case scoped to the null.

**One consequence, marked as consequence and not provenance:** the measured ratio clears the
strictest of the three candidates by `2.29×`, and the multiplier would have had to exceed **`29.85`** to
fail — `(2.673896 − 1)·√318`. *(An earlier draft of this paragraph said `≈16`, computed by eye and wrong; the figure above is evaluated.)* So the retrospection **did not determine the outcome**. That bears on how much the choice
mattered; it does **not** make the choice prospective, and it is recorded here so nobody later reads
robustness as predeclaration.

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
| **C5** | **NOT FALSIFIED on Z's 15-module import closure at `fb9ec356` and on the eight consumed input PATHS; the inputs' PRODUCER CHAINS were not traced.** ⚠ The earlier wording *"scoped to the 15 traced modules"* is **withdrawn**: it tells a ratifier the residual is a 16th module when it is an **untraced producer chain**, which is the dropped-qualifier failure `AGENTS.md:44-55` already records once. §6.1's conditions, which this cell was silent on: **(3)** performed by a lane that does not own cause 5 — reproduced by an independent cross-account lane with a positive control on real PET modules; **ATTESTED by the advisor from its own dispatch record**: a cold `claude -p` on claude-school, read-only tools, dispatched for this check alone with no prior involvement in cause 5 or any of Z's work — so the falsifier check was performed by a **non-owning** lane. ⚠ **Limitation named: that lane shares a model with this one and with the assessor, so it is non-owning but NOT cross-model**. **(4)** this is a **per-cell decision, NOT a mechanical four-MET discharge**, and that distinction is stated here in the cell rather than left inferable from it. **(5)** G's and Y's historical cells are **untouched** |
| **C6** | **REUSE**, risk named: *inputs consistent but unproven* |
| **C7** | ⚠ **REOPENED by Joseph.** The FACT holds — an independent cross-account TKey census **reproduced** 45 bands, V 13 / A 5 / R 27, all four weight-only bands in R. What failed is the evidence chain. **(c) "measured twice, two files" is ONE measurement recorded twice** — both reads trace to `sources["support"].keys()`, and the lane's third read traces to the same TKey list; restated as **one measurement with three records**. **(b) REPAIRED**: `exhaustive: true` could not fail at the production call site, because `z_build` derives `R = inventory − V − A` so `missing` is empty by construction and a one-for-one substitution survives even the count check. `z_contract.check_declared_residual` now compares R against a **declared 27-name set**, is called from the production site gated on `input_kind == "real"`, and both the call site and the gate are asserted by test. **(a) OPEN — needs a ruling, see below** |
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

## 4e. C7(a) — THE PUBLICATION GATE'S REQUIREMENT IS IN NO LIVE CANONICAL ARTIFACT

**Both texts, verbatim, because the whole point is that they differ:**

| source | text |
|---|---|
| **`KNOWN_ISSUES.md:16`** — the only LIVE canonical text for `#16` | *"Bank-derived lateral covariances remain support-limited **until the promoted-universe migration bound is adopted**."* Routed detail: `[open remediation gate](docs/OPEN_ITEMS.md)` |
| **`ESTIMATOR_REGISTRY:29`** — what C7's evidence actually cites | *"`#16` **five-band coverage** (publication gate)"* |

**These are not two wordings of one condition.** One is *adopt the promoted-universe migration
bound*; the other is *five-band coverage*. They may be related — coverage could be what the bound
buys — but they are different tests, and **C7's evidence chain cites the registry's phrasing, which
appears in no other live artifact.** The registry is a **paraphrase with no source**.

**And the route is dangling.** `KNOWN_ISSUES:16` points at `docs/OPEN_ITEMS.md` as a *file*, with no
row anchor, and **`#16` returns zero matches in that file** — in a file whose own header says to
update the pointer target.

⚠ **I AM NOT PICKING ONE.** On the face of it `KNOWN_ISSUES` governs, because it is the canonical
artifact and its text is the only live statement — but *that reasoning would retire C7's cited
requirement*, which is a scientific call and not mine. Choosing the convenient one is exactly what
the instruction forbade.

### PM-1's evidence — located, cited, and its object named

**The strongest weight-only evidence in the repository is
`PACKET-20260918-scalar5d-completion-inventory-and-null-route.md` §15.1, and C7's row does not cite
it.** It is stronger than a name argument because it tests the thing that actually decides
laterality: `unfold_nd_omnifold_unbinned.py:388` is
`if t.GetBranch(l_sim) and t.GetBranch(l_mc):  # lateral` — **a runtime branch-presence test, not a
name list.**

> Measured on the **470-branch production universe tuple**: the five lateral bands carry kinematics
> **4/4** and shifted `q3`+`W` **4/4**; the four excluded — `MinosEfficiency`, `GEANT_Neutron`,
> `GEANT_Pion`, `GEANT_Proton` — carry kinematics **0/4**; and `measured lateral set ==
> p4_lib.BANDS` is **True**. The producer states it directly, `runEventLoopOmniFold.cpp:238-244`:
> *"the GEANT hadronic-response bands (which DO move E_avail physically) are vertical/weight-only"*,
> and `MinosEfficiency` is a `MINOSEfficiencyReweighter` by class.

⚠ **AND HERE IS THE GAP, WHICH IS THE POINT, NOT A DETAIL.** §2.7 defines `PM-1` as re-measuring the
weight-only claim **on G's own `combined_source`** — because the supporting ledger sentence
(`VALIDATION_LEDGER:788-791`) **sits in the FPS row**, job `56431823`, the 266-bin chain, making it a
**2D/FPS-side claim**. §15.1's measurement is on *the 470-branch production universe tuple*; the
packet **does not name that file** and **does not establish it as G's `combined_source`.** So the
evidence is strong and it is **not yet shown to be PM-1's object.**
### PM-1 — THE PROVENANCE LINK CANNOT BE MADE FROM THE RECORD. That is the finding.

**The route is a provenance link, not a measurement.** `combined_source` is a *covariance* file and
weight-only is a property of the universe **tuple's branches**, so "measure on `combined_source`" is
unavailable by construction — which is why §15.1's branch-presence test is the right kind of
evidence. What would close PM-1 is showing **the tuple §15.1 measured IS the tuple `combined_source`
was built from**, matched by **path AND digest**. Measured, both endpoints fail:

| endpoint | state |
|---|---|
| the tuple §15.1 measured | **described, never named** — *"the 470-branch production universe tuple"*, no path, no digest, no receipt or script recording it |
| the tuple `combined_source` was built from | **not recorded.** `combined_source` is `uq_universe_5d_covariance_combined_bkgaware.root`; three launchers reference that *output* and **none references an omnifile / `OmniFold_5D` input** |

⚠ **A ledger row I nearly misread, recorded because the misreading was available and would have
inverted the result.** `VL11` lists `combined_source` → that filename → **`ABSENT`**, which reads as
*the field is missing*. It is not: `ABSENT` is the **before** value in a before/after control, so the
row records the field being **added**. The field exists; what it does not carry is the tuple the file
was built **from**. Consistent with the C5 lane's finding that `component_provenance` holds only
`{path, sha256, format}` — **no producers**.

> **PM-1 is a NAMED GAP, not something to infer across.** Neither endpoint is identified by path and
> digest, so the link cannot be made from the record as it stands. Closing it needs the tuple path
> and digest for §15.1's measurement, and a producing-input record for `combined_source`. ⚠ *Joseph's ruling §2 forbids justifying the acceptance by asserting the project never recorded input files; that argument is withdrawn and the limitation stands on its own.*

### Is `#16`'s "promoted-universe migration bound" §2.7's lateral counterfactual?

**THE RECORD DOES NOT SAY.** Measured, not inferred: the string `promoted-universe` occurs in the
entire repository **exactly once outside this sheet — in `KNOWN_ISSUES.md:16` itself.** It is used
in the row and **defined nowhere**. So no record connects it to §2.7's `Σ_A L_active` vs
`Σ_A L_support`, and no record separates them either. Recorded as unanswered rather than resolved by
plausibility.

**WHAT CLOSES IT, and it is a ruling and then one edit:** state the publication gate's actual
requirement **once, in one live canonical artifact**, and route the registry to it. If *five-band
coverage* is the intended gate, it has to be written into `KNOWN_ISSUES:16` (or another live
canonical artifact) and **C7 re-evidenced against it** — the 45-band census answers the coverage
question and says nothing about a migration bound. **Joseph re-rules C7 on whatever survives; his
earlier ruling was made on (b) as evidence and does not carry over.**

## 4e2. THE ASSESSOR'S PROJECTOR-LEVEL EVIDENCE — anchored at `5be86f55`, and CREDITED

**Asked to credit it and state by diff whether the guard paths had changed. They had not changed —
they did not EXIST there.** Measured, not inferred:

| | |
|---|---|
| `318b8c06` | the assessor's verdict commit, **2026-09-18 17:22:54** |
| merge-base with `HEAD` | **`d147880f`, 2026-09-10** — the branch diverged eight days earlier |
| `expect-variant` in its `project_cov_nd.py` | **0** |
| `_declared_variant` / `mean-centering alone is disqualified` / `adoption-exception` | **0 / 0 / 0** |
| `git log -S'expect-variant'` over **all** of `318b8c06`'s history | **no commits** |
| where the guard actually enters | **`5be86f55`, 2026-09-18 15:35:34**, on `HEAD`'s line and **not** on the assessor's branch |

**So the four guards are absent from that commit's tree and from everything behind it.** The verdict
is timestamped 1h47m *after* the guard landed on `main`, which is why it looks creditable and is not:
**later in wall-clock, on a branch that never received the code.**

⚠ **WHAT I AM NOT CONCLUDING.** This does **not** establish that the assessor exercised nothing. It
very plausibly ran a worktree checked out at another ref while committing its verdict to its own
branch — that is normal here. What it establishes is narrower and sufficient: **the anchor is
wrong.** Evidence pinned to a commit whose tree lacks the code is not pinned. Crediting it in §4d
would put a real-path claim behind a sha that cannot support it — the same defect class as a record
claiming more than its evidence establishes, which is what this campaign has been counting.

### RESOLVED — the anchor is `5be86f55`, and the evidence IS credited

**The record declares its own base and I verified it rather than take it.**
`VERIFICATION-20260918-scalar5d-adopt-clause-c.md` states **"Base: `5be86f55`"** in its header and
**"Measured at `5be86f55`"** in its body. At that commit `project_cov_nd.py` contains
`expect-variant` **5×**, `adoption-exception` **3×**, and the `mean-centering alone is disqualified`
refusal **2×**, and `5be86f55` **is an ancestor of `HEAD`**. `318b8c06` is where the verdict was
**committed**, not the tree that was **exercised** — those are different questions, and pinning to
the first is the error.

**GUARD PATHS DIFFED `5be86f55 → HEAD`, and all four are unchanged:**

| guard path | `5be86f55` | `HEAD` | |
|---|---|---|---|
| `_declared_variant == "none"` | 1 | 1 | same |
| `_actual_variant != _declared_variant` | 1 | 1 | same |
| `mean-centering alone is disqualified` | 2 | 2 | same |
| `adoptable …lower() == "false"` | 1 | 1 | same |
| `_src_digest not in _exc_text` (exception validation) | 1 | 1 | same |

**The ONLY non-comment code change to the whole file since `5be86f55` is the `import ROOT`
relocation** — and its direction matters: it makes the guards **more** reachable, never less, so it
cannot weaken evidence gathered when ROOT was present. The other diffs are a help **string** (the
dtype correction) and comments. ⚠ **`n_empty` was NOT removed from the code** — `n_empty_recorded`
appears **5×** in both trees; what was removed was its entry in this sheet's *declared check list*,
which is a document change.

> **CREDITED: §4d items 3 and 5's PROJECTOR-level refusals are exercised on the real products in the
> production environment, at `5be86f55`.** Variant mismatch, publication-from-mean on
> `AGENTS.md:29`, `none` against a marked file, publication from `adoptable:false`, and a positive
> control that produced the product with the `hRowIndex` readback.

⚠ **LIMITATION, KEPT:** the base is **declared by the record and corroborated**, not independently
observed by us. Corroboration is behavioural — e.g. argparse returning **rc 2** for a missing
required `--expect-variant` cannot come from a tree lacking the flag — which is strong but is not
the same as having watched the checkout.

**What remains unexercised is the LAUNCHER passing flags through**, which no projector-level run can
cover: `--run-class` (the defect once passed zero times), `--adoption-exception` in both arms
including A3's set-but-missing `rc 3`, B5's `adoptable:false` refusal reached *through* the
launcher, and item 6's reachability without the production environment. That is exactly run 4's
scope.

## 4f2. ✅ RUN 5 — EVERY LEG PASSES. The guard-set control is COMPLETE.

`58565755`, 77 s, **zero `CONTROL FAILED` lines.** Legs in B4's configuration: sourced environment,
real ROOT, no shadow, so `_verify_canonical_edges()` passes and the guards at `:364` are reached.

| leg | result |
|---|---|
| A1 no adoption record | `rc 3` ✅ |
| A3 exception set but missing | `rc 3` ✅ |
| A2 §6.4 amendment offered AS an adoption record | `rc 3`, printing `declare: ADOPTS-SHA256: 3d7465f6…` ✅ |
| B1 publication from the **mean** variant | `rc 1`, **`AGENTS.md:29` refusal fires** ✅ |
| B2 cv file declared mean | `rc 1`, *"declares variant 'cv'"* ✅ |
| B3 mean file declared cv | `rc 1`, *"declares variant 'mean'"* ✅ |
| **B5 publication + cv + NO exception** | `rc 1`, *"records `adoptable: false`"* ✅ **— gap 4 closed, the most load-bearing guard, reached through the real path** |
| B4 positive control | `rc 0`, product written ✅ |
| **Q2 assertion on B4's product** | `rc 0`, **PASS** ✅ |

**Every protection in §4d's enumeration now has real-path refusal evidence with a positive control**
— except item 6, recorded as **by-design unreachable** without the production environment.

## 4f. THE GUARD-SET CONTROL FAILED THREE TIMES BEFORE THAT — kept, because the failures are the record

**Stopped, not retried.** The advisor's condition on the third submission was: *if this run fails it
is a diagnosis, not a fourth try.*

| run | outcome |
|---|---|
| `58549890` | legs B **segfaulted**; my checker tested `rc == 0` so three crashes were reported as **three refusals** |
| `58552664` | same segfault, now **correctly named** as a crash; script then aborted before B4 |
| `58562627` | aborted after **13 s**, before the shadow check and before **every** B leg |

**THE CAUSE, MEASURED, AND IT IS THE SAME ONE IN RUNS 2 AND 3.**
`source setup_salloc_env.sh` **aborts the shell under `set -u`**. Reproduced directly:
`bash -c "set -u; source …"` prints `BEFORE` and never prints `AFTER`; without `set -u` both print.
The unbound variable is **`ADDR2LINE`**, in conda's
`activate-binutils_linux-64.sh:68`. **`|| true` cannot catch it** — the abort happens *inside the
sourced file, in the same shell*, so there is no command whose status could be tested.

⚠ **AND RUN 3 IS WORSE THAN RUN 2 BECAUSE OF MY FIX.** In run 2 that `source` sat just before B4, so
B1–B3 at least executed (and crashed). Repairing the segfault required sourcing the environment
*early*, so I moved the line to the top — **where the same latent abort kills everything instead of
one leg.** The segfault repair was correct; moving a line that was already fatal made its blast
radius larger, and nothing in the instrument could see it because the abort is silent.

**The one-line fix is known** — `set +u` around the source, `set -u` after — **and is not being
applied, because the budget for this stage is spent and the instruction was to stop at a
diagnosis.** It needs an explicit fourth authorization.

**WHAT IS AND IS NOT ESTABLISHED.** Leg A has passed on the real launcher in **two independent
runs**: A1 refuses with no adoption record, A2 refuses the §6.4 amendment offered *as* one, printing
the `declare: ADOPTS-SHA256:` line. **Leg B — the variant guard, the `adoptable:false` refusal, and
the exception passthrough — has never executed on the real path.** Their unit coverage is green and
that is not the same thing, which is the whole reason this control exists.

## 4g. RUN 4 AND CAUSE 7's M — both COMPLETED, and the per-bin result is the finding

### Control `58564446` — the shadow worked as an INSTRUMENT even though leg B failed

| leg | expect | got | |
|---|---|---|---|
| A1 no adoption record | `rc 3` + message | `rc 3` | **PASS** |
| **A3** exception set but missing | `rc 3` + message | `rc 3` | **PASS — gap 5's second arm now closed** |
| A2 §6.4 amendment offered AS an adoption record | `rc 3` + message | `rc 3`, printing `declare: ADOPTS-SHA256: 3d7465f6…` | **PASS** |
| B1 / B2 / B3 / B5 | guard messages | `rc 1`, the **shadow's ImportError** | **did not reach the guard** |
| **B4** positive control, cv + exception | `rc 0` | `rc 0`, product written | **PASS** |

**THE SHADOW NAMED THE IMPORTER, which is what it was for.** The traceback:
`project_cov_nd.py:321` → `_verify_canonical_edges()` → **`:59 import unfold_2d_omnifold_unbinned`**
→ `2d-unfolding/unfold_2d_omnifold_unbinned.py:21 import ROOT`. A **function-level** import, called
at `:321`, **before the guards at `:364`**.

⚠ **And my earlier ruling-out was incomplete in a way worth naming.** I reported "module-level
imports are clean, `uq_math` is clean, the readers guard on `_is_npz`" — all true, and I never
checked *function-level* imports reached before the guards. `grep 'import ROOT'` could not find it:
line 59 reads `import unfold_2d_omnifold_unbinned as u2d`, and the words *import ROOT* appear only in
its **trailing comment**. Three runs of segfaults had this one cause, and the instrument found in one
run what inspection had missed in three.

### Cause 7's `M`, `58564281` — measured on Z's own inputs

**Binding is the strongest available:** active source sha256 **measured** = Z's manifest value
`950f8cb1…`, **file digest present in Z's receipt**, and **5/5 per-band active keys named there** →
**per-band plus file digest**, not the SPEC-table claim.

| | |
|---|---|
| `sqrt_tr( Σ_A L_support )` | `1.4747098387e-38` |
| `sqrt_tr( Σ_A L_active )` | `1.4742855149e-38` |
| ratio active/support | **`0.9997122662`** |
| relative movement | **`−0.0288%`** |

**This REPRODUCES S's committed `support_comparison` to ten digits — as an IDENTITY CONFIRMATION,
not as independent physics.** ⚠ *Tempering my own phrasing:* if Z's lateral blocks **are** S's
donated blocks, and the digests say they are, then ten-digit agreement is **expected**. It confirms
the binding — these really are the same blocks — and it **cannot** corroborate anything beyond that.
Recorded so the agreement is not read as evidence it is not.* The underlying point stands: — §2.7 records
`1.4742855148740122e-38` / `1.474709838719496e-38`, ratio `0.9997122662137712`, `−0.0288%`.
**That is a reproduction, not a citation**: §2.7 prohibits *citing S's ratio as Z's M*, and Z's M was
measured independently from Z's own bound inputs and agrees.

> ### ⚠ AND THE PER-BIN RESULT IS WHY THE REFINEMENT MATTERED
> `sqrt(diag_active / diag_support)` over all **10694** bins: **min `0.177248`, median `1.005070`,
> max `3.061947`** (argmax at index 3357).
>
> **The trace moves `−0.0288%` while individual bins move by a factor of 3 up and 5.6× down.** That
> is precisely the hazard §2.7 names when it contrasts S's trace move with F's per-bin spread — and
> a trace-only `M`, which is what was asked for originally, would have reported `−0.03%` and shown
> none of it.

### NOW MEASURED from the persisted diagonals, at no compute — and it changes the reading

**The extreme movers carry essentially none of the variance.**

| | |
|---|---|
| Spearman `ρ(support variance, ratio)` | **`−0.0048`, `p = 0.621`** — **no correlation**, unlike the null's `−0.3103` at `p = 2.5e-237` |
| median ratio by variance decile | **flat at ≈1.00** across all ten; not monotone |
| `ratio > 2.0` | 48 bins (0.45%) carrying **`0.0002%`** of total support variance |
| `ratio < 0.5` | 67 bins (0.63%) carrying **`0.0555%`** |
| `ratio < 0.8` | 830 bins (7.76%) carrying **`1.16%`** |
| the argmax bin, ratio `3.062` | support variance `7.36e-96` = **`0.000000%`** of total |
| the argmin bin, ratio `0.177` | **`0.000006%`** of total |
| **top 1% of bins by variance — carrying `74.11%` of the total** | ratios **`0.687` … `1.153`, median `0.999`** |

**So the `0.177`–`3.06` span is real and it lives where the variance is not.** Where the variance
actually is, the ratios run **`0.687` to `1.153`**. ⚠ **CORRECTED per Joseph's ruling §3: I wrote
"at most ±15%", which is wrong on the downside — `0.687` is a decrease of about `31%`.** The trace's
`−0.0288%` is a change in the lateral block's **square-root trace**; it is **not a bound on every
bin, nor on the complete covariance.**

⚠ **TWO LIMITS. Joseph's ruling §3: SMALL AGGREGATE VARIANCE SHARE DOES NOT MAKE A BIN IRRELEVANT
TO A QUOTED RESULT** — so any framing that these movements "sit where they barely matter" is
withdrawn. A quoted number drawn from a
**low-variance** bin still carries that bin's own ratio — a 3× σ change in a negligible-variance bin
is still 3× *for that bin*. And `830` bins (7.76%) sit below `0.8`, carrying `1.16%` of variance:
small in aggregate, not nothing. **No threshold is applied here and none is proposed**; the
distribution is the report.

⚠ **MY PROHIBITION CHECK IS VACUOUS AND ITS MESSAGE IS FALSE.** It prints *"none of S's ratio or F's
+10.96% appears in this measurement"* — but it inspects only the **per-band trace dict**, which is
computed **before** the ratio. The ratio `0.9997122662` **does** appear, as Z's own measured result.
The check looked at the wrong object, which is the operand failure again, in my own guard.

## 4h. DRAFT — C7's PM-1 disclosure, for Joseph's ruling. **NOT A CLOSURE.**

**Recommendation put to Joseph: DISCLOSE WITH EVIDENCE, not require-provenance.** Ground: weight-only
is established at the **implementation** level, so it holds for any tuple the event loop produced;
what cannot be linked is only **file-level provenance of G's input**, which this project never
recorded for any input.

### 1. Implementation evidence — verified by opening the file, not via the packet

`MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp`, the `NOTE (3D E_avail)` block:

> *"the lateral bands are all muon/beam systematics (BeamAngleX/Y, MuonResolution,
> Muon_Energy_MINERvA/MINOS). They override only muon momentum/angle getters, none of which feed
> `NewEavail()` … So E_avail is invariant under every lateral universe and needs no shifted branch.
> **The GEANT hadronic-response bands (which DO move E_avail physically) are vertical/weight-only
> and are captured by `w_reco_GEANT_*`.**"*

⚠ **It is a COMMENT — `//`-prefixed prose stating intent, not executable code.**

⚠ **AND A CONFLATION OF MINE, CORRECTED.** I first flagged the notes' per-axis structure as
qualifying *weight-only*. **It does not, and the correction matters.** `NOTE (3D E_avail)` and
`NOTE (4D q3)` reason about which getters the **LATERAL** (muon/beam) bands override and which
quantities those getters feed — E_avail invariant, q3 shifted, W never addressed. That is per-axis
and it does stop before W, **but it is about the five lateral bands.**
**Weight-only is NOT per-axis.** The four PM-1 bands are implemented as **weights** — `w_reco_GEANT_*`
and `MINOSEfficiencyReweighter`. **A reweight overrides no kinematic getter, so it shifts no axis, W
included, by construction**; there is nothing for a W note to reason about. And the executable half
covers W directly: §15.1 measured the five lateral bands carrying shifted **q3 and W** 4/4 and the
four carrying **0/4**. **So weight-only is uniform across axes.** ⚠ *Graded per the ruling's §2, because
"doubly evidenced" overstated it:* the source comment **documents intent and is not executable
verification**; the implementation trace establishes behaviour **only for the inspected
implementation**; and the tuple observation **has no recorded path or digest**, so it is **limited
corroboration** and must not be called independently reproducible or bound to G. **Repeated accounts
of that observation count as ONE observation.**

`MinosEfficiency` is a reweighter **by class**: `#include "PlotUtils/MINOSEfficiencyReweighter.h"`
at `:70`, instantiated into `MnvTunev1` at `:1749`.

### 2. Runtime corroboration — an executable test, which the comment is not

`unfold_nd_omnifold_unbinned.py:388` is `if t.GetBranch(l_sim) and t.GetBranch(l_mc):   # lateral` —
**laterality is decided at runtime by branch presence, not by a name list.** Packet §15.1 measured
it on the production universe tuple: the five lateral bands carry shifted kinematics **4/4**, the
four bands left in `R` carry **0/4**, and `measured lateral set == p4_lib.BANDS` is **True**.

### 3. The gap, stated plainly

**Neither tuple is named anywhere in the record.** Not the 470-branch tuple §15.1 measured — no path,
no digest, no receipt — and not the input tuple `combined_source` was built from; three launchers
reference that output and none references an omnifile input. **The file-level link cannot be made.**

### 4. ⚠ THE PHYSICS CAVEAT, disclosed rather than passed over

**The same comment says the GEANT bands "DO move E_avail physically."** So *weight-only* describes
**how they are IMPLEMENTED — as a reweight** — and is **not** a statement that hadronic response
causes no migration.
>
> ⚠ **WITHDRAWN 2026-09-19 BY JOSEPH'S RULING §4, and it was my inference:** *"the bands are
> weight-only; therefore hadronic-response migration is absent from the covariance."* **That does
> not follow.** Weights can alter the population of simulated detector-interaction histories and so
> alter **reconstructed distributions, efficiencies and response matrices** without changing any
> individual event's stored coordinates. Conversely, weight-only implementation does **not** prove
> that all relevant response variations are represented.
>
> **The `RecoW()` finding survives only as a statement of HOW `W` IS BUILT** — `q0 = <tree>_recoil_E`,
> `W = sqrt(M² + 2·M·q0 − Q²)`, `CVUniverse.h:227-235`. ⚠ **It is NOT evidence about where any
> limitation is largest**, and §4 forbids claiming a limitation is greatest at high `E_avail` or high
> `W` merely because those observables involve hadronic energy. **Nor may the treatment be called
> negligible, conservative, complete or deficient without evidence for that description.**
>
> ### THE DISCLOSURE THAT REPLACES IT — §5's substance, for note, primer and paper alike
>
> > The selection-complete replacement covers the five detector bands implemented through shifted
> > reconstructed kinematics. MINOS efficiency and the three GEANT hadron-interaction bands retain
> > their weight-based treatment. This classification establishes their exclusion from the kinematic
> > replacement; it does not independently validate the completeness of the hadronic-response model
> > for the `E_avail` and `W` measurement.

## 4i. ✅ C7 CLOSURE — §3's five citations are COMPLETE, and the closure is recorded

Extracted **by field name**, not substring — a substring scan returned `True` for all nine probes and
**four were false positives.**

| # | required citation | evidence |
|---|---|---|
| 1 | exact five-band inventory | `z-receipt-cv.json` → `inflation.membership.bands_lateral` **n=5**; `bands_vert` 13, `bands_residual` 27, `band_inventory` 45 |
| 2 | **ten endpoints** | **per-endpoint `sha256` in `p4_merged_audit.json`** — 10/10 present, **all distinct**, `exists true`, `zombie false` |
| 3 | **migration censuses** | `EVIDENCE-20260919-…md` — **10/10 agree with policy**; `selection_migration_abs = RecoEntrants + RecoExits` exactly on all ten |
| 4 | **declared policies** | `p4_lib.py:64-65`, consumed at `p4_validate_active_lateral.py:92-93` |
| 5 | required assembly identities | `closure.{G1_closure_identity, G2_g_domain, G3_g_reconstruction, G3R_raw_operand_reconstruction, G4_symmetry_psd, G5_band_partition}` **plus `active_total_eq_sum5` = `0.0`** and **`blocksum_symmetry_psd`** (`rel_asymmetry 0.0`, `neg_fraction_of_max 3.89e-16`) |

**`SPEC:802`'s abort condition does not trigger:** no declared-zero band measures nonzero, and no
declared-nonzero band measures zero.

⚠ **A CORRECTION TO MY OWN EARLIER CITATION.** I cited `PACKET §15.1:952-953` for item 2. Re-read, it
checks **ten directories uniform at 12 ROOT files and 53.8 GB** — a **directory-uniformity census**,
real but **not a digest identity binding**. The reviewer's *"never checked"* was closer to right than
my citation. The digests above are the identity evidence; §15.1 is corroborating structure.

⚠ **ONE CAVEAT CARRIED, NOT CLEARED:** the **12-playlist hadd coverage is NOT confirmed** by this
artifact. Its only `12` is `native_miss_playlists_with_misses` — *playlists with misses*, a different
quantity from *playlists summed*. Consistent with 12; not a confirmation.

### Recorded per §3, in the ruling's own words

> **PM-1: accepted by decision, with historical-input provenance limitation.**
> **Cause 7 for the named Z candidate: closed as sufficient under §2.7, as amended by this ruling.**

**Cause 7's magnitude is Z's measured lateral counterfactual** (§4g): `√tr` ratio **`0.9997122662`**,
**`−0.0288%`**. ⚠ **That is a change in the lateral block's SQUARE-ROOT TRACE — not a bound on every
bin, and not a bound on the complete covariance.** The per-bin ratios run **`0.687`–`1.153`**
(`0.687` is a **31% decrease**), and **small aggregate variance share does not make a bin irrelevant
to a quoted result.** `C_Z − C_G` is **not** substituted. Historical **G** and **Y** dispositions are
**unchanged**.

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
