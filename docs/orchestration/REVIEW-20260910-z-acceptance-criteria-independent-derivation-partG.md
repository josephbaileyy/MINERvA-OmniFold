# PART G — the endpoint-A consumer set, measured; and two places where Part F over-demanded

**Owner:** independent-assessment lane (`lane/z-criteria-independent-assessment-20260910`).
**Base of measurement:** `6f24fb00` for code; `a11d6cdd` (`lane/decision-20260910-z-endpoint-a-ruling`)
for the rulings; `173baf44` for the prior packet.
**Continues:** Part F (`c695f209`). Closes Part F §F.7's first open item and corrects `F11` and `F12`.

**CITABLE FOR:** the per-consumer measurement in §G.2, and the two self-corrections in §G.4.
**NOT CITABLE FOR:** adoption, grading, or amendment. Nothing here is a remedy.

---

## G.0 — F-0 IS CLOSED, AND THE RECORD IT PRODUCED SUPERSEDES MY RELAY CITATIONS

Part F `F-0` measured that neither ruling existed as a committed record across 131 refs. That
measurement was correct as of `6f24fb00` and it was correct to scope it as it did — *"proves those
phrasings are absent, not that no differently-worded record exists"* — because that scoping is exactly
what separates the two hypotheses it could not distinguish. **It was genuine-but-unlanded, not
fabricated.** Both rulings are now committed verbatim at `a11d6cdd`:

- `docs/orchestration/DECISION-20260910-joseph-accepts-outcome-2-and-opens-replacement-packet.md`
- `docs/orchestration/DECISION-20260910-joseph-b-deferred-and-finite-ensemble-disclosure.md`

`F21` ("the packet must not assert what Joseph decided beyond what is recorded") is therefore
**satisfied** for both rulings, and every `RELAYED` label in Part F on Rulings 1 and 2 should now be
read as pointing at that sha. **`F-0`'s finding is retained, not withdrawn:** the requirement that a
governing ruling be diffable is what it asserted, and it is now met.

**`F9` survives the landed text.** Neither record defines "verified". The verbatim clause is *"Record
each sample-covariance block's verified ensemble size and normalization convention"* — the word is
used, not defined, so the two readings in `F9` are still both open and still differ by a code change.
`F9` remains reserved to Joseph.

---

## G.1 — THE RULING'S OWN ADEQUACY CHECK CONVERGES WITH `F-I`, DERIVED INDEPENDENTLY OF IT

Joseph's verbatim third paragraph (`…b-deferred-and-finite-ensemble-disclosure.md:115-117`):

> One targeted adequacy check remains: retained-rank and subspace stability do not by themselves
> establish stability of projected uncertainties. Show which criterion controls changes in the actual
> released error bars under estimator-baseline variation. If none exists, propose that criterion and
> its scientific justification. Do not reopen the universal-bound approach.

Part F's `F-I` was committed at `c695f209` before this text was read, and it is the **mechanism** for
that check: a released error bar is `sqrt(diag(M C Mᵀ))_i = sqrt(Σ_{j,k→i} w_j w_k C_jk)`, so it is a
functional of off-diagonal entries that **no diagonal-only leg and no rank-or-subspace declaration
touches**. Retained rank and retained-subspace identity are properties of the *inverse's* support;
the released error bar does not invert anything. The two are about different objects, which is why one
cannot bound the other.

I record the convergence and stop there. **Proposing the criterion is the designer's task under this
ruling, and supplying it would spend this lane's verdict on it** — Part E §E.1, and the reason the
`D1` clause is already not mine to review.

Two further corroborations from the same verbatim text:

- **`F18` is confirmed by the ruling, not merely derived.** *"Do not reopen the universal-bound
  approach."* Part F's `F18` listed the ρ bound, `rho_max`, `rcond`, `ndf` and `s_sig` as out of scope
  for endpoint A on the ground that no significance is released. The ruling bars reopening the bound
  outright.
- **The clause-(d) independence question is now moot for the recommended path.** Part F §F.6 flagged
  it as conditional on whether the bound stayed the acceptance instrument. It does not. My
  non-independence for the retained-subspace clause is live only if the bound is adopted anyway, which
  the ruling forecloses.

> **⚠ WITHDRAWN 2026-09-10, see Part J.** The mootness claim in this item is **FALSE**. Measured at `05bf8647`: the endpoint-A packet's §2 table carries **A-4** — *"retained rank and retained-subspace projector gap across members, `‖P_0 − P_k‖_2 ≤ 1e-8`"*, which is clause (d)'s exact test — as a live endpoint-A requirement **with no dependence on the ρ bound**. The claim is true only of clause (d) *as a terminal-outcome sub-clause of the ρ-leg* at `RECOMMENDATION:392`, and false of the **test** the clause states. **Anyone acting on "clause (d) is moot" drops a live A-4 requirement.** My disqualification is unchanged; what changes is that it is a spent verdict on a LIVE object, not a dead one.


---

## G.2 — F-III: MEASURED. THE PREMISE IS FALSE FOR ONE OF FIVE CONSUMERS, ON ITS OWN CITED LINES

Part F §F.7 left open whether `C5stat` is a block of Z and whether an endpoint-A consumer projects it.
Both are now measured, and the answer is narrower and more useful than "the premise is false".

`PACKET-20260910:232-235` classifies endpoint A's declared consumers `C5, C6, C7, D1, D2` as
**"NO — `sqrt(diag)`, `sqrt(trace)`, displayed bands. Every one is a function of the diagonal."**
Measured per consumer at `6f24fb00`:

| consumer | cited at | what it actually reads | reads off-diagonals? |
|---|---|---|---|
| **C5** | `eavailW_covariance.py:441,466` | `:441` `C_stat = project_covariance(C5stat, Mew)`; `:466` `np.diag(C_lat_e)` where `:464` builds `C_lat_e += Me @ C_b @ Me.T` with `Me` from `:456` | **YES — both cited lines** |
| **C6** | `coverage_valid_nd.py` | `_load_cov_diag` at `:44-54`: `h.GetBinContent(i+1, i+1)` — the stored TH2's diagonal elements only, no projection | **NO** |
| **C7** | `mii_anchor_comparator.py:238` | `_sqrt_trace_from_diag`, applied at `:255-265` to `C_unified`, `C_blocksum`, `hCov_combined5d_total_uthrow`, `hDiagCombinedOldRaw` — trunk-level, and its own docstring says *"no matrix is materialised"* | **NO** |
| **D1** | `sec_3d.tex:193,:261` | bands of the **historical 3D** covariance; the packet's own row says *"quarantined pending 5D→3D projection"* | **NO today; YES once that projection lands** |
| **D2** | `sec_3d.tex:210` | *"historical covariance band … shown for orientation only and is not final"* | same as `D1` |

**So the table is right in three cells, conditional in two, and wrong in one — and the wrong one is
enough.** A deferral resting on "no released consumer reads off-diagonal structure" fails if a single
released consumer does.

### The chain to Z is closed

1. `eavailW_covariance.py:143,145` default `--stat5d` to `uq_cov_stat_5d.root` and `--stat5d-hist` to
   `hCov_stat5d_reported`.
2. `SPEC-20260906` §:504 binds `S.stat_cov` to `uq_cov_stat_5d.root:hCov_stat5d_reported`, sha256
   `6580016fa7136e6f98867707f4d48557350b26a91773d0c300be20113c2c6934`, and names it *"Z's candidate
   `C_stat` … input"*.
3. `SPEC-20260906` §:610 has `C_Z^c = … + C_stat + C_ML`.

**Therefore `C5`'s released band at `:441` is a linear functional of the off-diagonal entries of the
object the spec names as Z's candidate `C_stat` block, by default path and default histogram name.**
Part F §F.7's first open item is closed. The one caveat that survives is the spec's own: §2.6b leaves
open whether Z **reuses** `S.stat_cov` or regenerates it, so the block is Z's *candidate* input rather
than a settled member.

### The defect is the classification method, not the diligence

C6 and C7 read the diagonal of a **stored** matrix. C5 reads the diagonal of a matrix **it built by
projection two lines earlier in the same function**. The phrase *"consumes `sqrt(diag)`"* is true of
all three; only for C6 and C7 does it imply independence from off-diagonals. The table classified by
**the last operation performed** rather than by **the provenance of the matrix that operation reads**.

The information needed to catch it was inside the cell that got it wrong: `C5`'s own entry reads
*"**produces** `C_low`; consumes `sqrt(diag)`"*, and producing a low-dimensional covariance from a
high-dimensional one **is** the projection. This is the operand-versus-measurement shape — a correct
predicate applied to the wrong object — and here it sat one column away from its own refutation.

---

## G.3 — CONSEQUENCE FOR THE AMENDMENT THE RULING ASKS FOR

Joseph's verbatim clause: *"Identify the exact contract amendment required to defer `cause3_corr` from
endpoint A; do not silently remove it or mark cause 3 MET."*

`F-III` does not block that deferral. It removes one ground for it. Deferring a boundary while
**naming** the exposure it leaves ungoverned is coherent; deferring it on the ground that no exposure
exists is not, because `C5` is an exposure. Part F's `F5` said this before the consumer set was
measured and stands unchanged.

I note without deciding it: `z_contract.py:231-235`'s withholding text — *"Both adopted statistics are
functions of the diagonal alone, so a `MET` result on them licenses nothing about `C_Z`'s off-diagonal
structure"* — is **correct as written** and is about the grading legs. If the amendment edits that
text, the edit should not be described as correcting an error in it.

---

## G.4 — TWO CORRECTIONS TO PART F: I DEMANDED MORE THAN THE RULING DOES

The assignment says not to demand stronger claims than the publication proposes. Against the landed
verbatim text, two of Part F's requirements over-reach, and both were written while the ruling was
only a relay.

**`F12` — CORRECTED.** Part F required `p` to be *"recorded as not applicable **with its reason**"*.
The ruling says only *"Where no inversion is performed, mark the inverted dimension as not
applicable."* The marking is required; the reason is not. **`F12` is reduced to the marking.** The
reason remains worth having and is now labelled a recommendation, not a requirement, and not a
blocking condition.

**`F11` — RESTATED, and it was overstated in form though not in substance.** Part F said the
declaration *"must distinguish intended N from achieved N"*, i.e. demanded two numbers where the
ruling asks for one. The ruling asks for a *verified* ensemble size. The correct form of the point is
narrower: **"verified" is not satisfiable for a single number when intended and achieved can differ
and the report does not say which one it is.** `--expected-ids` is a launcher constant, so the
fail-closed check at `replica_manifest.py:44-48` proves consistency between the constant and what
landed, never adequacy of the constant; and `OI-17` records `122 of 160` as a live instance with the
resolution — rethrow, or relabel as a 122-throw product — still open. So this is a component of `F9`'s
"what does verified mean", not an independent requirement for a second number. **`F11` is folded into
`F9` and removed from §F.5's block list as a standalone item.**

**§F.5's pre-registered block list is therefore five items, not seven** — conditions 1, 2, 3, 4 and 6
of Part F stand as written; condition 5 (`F11`) is folded into condition 4 (`F9`); condition 7
(`F18`) stands and is now backed by the ruling's own *"Do not reopen the universal-bound approach"*
rather than by my derivation alone.

Nothing else in Part F changes. `F-I` and `F-II` are unaffected, and `F-I` is strengthened by §G.1.

---

## G.5 — WHAT I STILL HAVE NOT MEASURED

- **The designer's endpoint-A packet**, which did not exist at authorship. `F1`–`F21` as corrected
  here are the yardstick I will apply to it.
- **Whether `D1`/`D2`'s pending 5D→3D projection is inside endpoint A's scope.** If it is, two more
  consumers acquire the `F-III` dependence; if it is not, the two rows are correct as written. The
  packet's own wording (*"quarantined pending"*) does not settle which.
- **The bodies of `173baf44`'s two artifacts** beyond the cells cited here and in Part F.
- **`(cause 3, Z)`'s `M(ii)` and the significance leg** — no lane is routed to grade them, which Part
  E recorded as a routing gap and which remains open.
