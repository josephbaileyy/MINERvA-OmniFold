# PACKET — scalar-5D completion inventory, the null route, and P1

**Prepared:** 2026-09-18, by the orchestrator lane, on Joseph's instruction to use the audit at
`ebba67ab6af17a159ae395cb06312b0dcbdca841` as the bounded inventory and reconcile it with
`c4baf0d29297de0d0f50d5ea1d8b869ddaf83520` before assigning work.

**CITABLE FOR:** the reconciliation in §1; the closed-route finding on `ε` in §2; the completed P1
projection enumeration in §4; the narrow OI-129 repair scope in §5; the intended-claim scoping in
§6; the dependency table in §7. All of it is source review and record reconciliation.

**NOT CITABLE FOR:** anything adopted. `ε` is **not** adopted — Joseph declined it on the transfer
argument. `θ` is **not** adopted and is **not** a feasibility floor. `B` is not established. Full
`S` is open. Gate 2 remains **FAIL**; `null_epsilon`, `cause3_agg`, `cause3_med` and `cause3_corr`
remain **WITHHELD**. No covariance is adopted, no projection is produced, no significance is
quoted, nothing is graded. **No compute was run and none is requested by this document.** The
completed precursor and the completed pilot stay closed and their products are preserved.

---

## 1. Reconciling `ebba67ab` against `c4baf0d2` and Joseph's rulings

The audit is 293 lines at `docs/literature/2026-09-18-scalar5d-covariance-inference-audit.md`, on
local branch `audit/scalar-5d-publication-gaps`, **based on main `07ccc4f0`** — one commit behind
main at the time of writing. **It has no upstream**; it exists on one machine only.

**It is sound. Every load-bearing claim I checked verified against source.** Four corrections and
one strengthening follow, none of which changes its ranking.

**1.1 It is 24 minutes stale, and the stale part is rank 1.** The audit is timestamped
`2026-09-18 01:21:28 +0900`; `c4baf0d2` is `01:45:40`. The audit read the reconciliation at
`df10748b` **§§10, 13, 15** and therefore cannot contain §§16–19. What it misses:

- **E1 and E2 are discharged** (§19). `r_null` reconstructs to `4.45200021375829101e-14` in three
  summation orders and **bitwise** against the blob-pinned instrument, **1.00 ULP** from the build's
  `…9038e-14`, with the support predicate **recomputed** and elementwise identical. The audit's
  rank-1 row still lists that reconstruction as outstanding.
- **The audit's own evidence-boundary caveat is now partly lifted.** It labels the independent
  assessment "**not** independent cluster-payload verification". That was true when written; the
  assessing lane turned out to have read-only cluster access and its product figures are now
  measured rather than relayed.

**1.2 Its rank-1 next action over-commits to an unadopted framework — the one real correction.**
Rank 1 says: *"Specify the execution envelope, justified B, scientifically justified S, feasibility
B ≤ S, and epsilon within that interval."* That is §3.7a's **proposal**. `SPEC:1552` titles the
section containing it *"§3.7 THE TWO CRITERIA — SPECIFIED BUT NOT COMPLETED, AND ENTIRELY
PROPOSED"*. Joseph's instruction is explicit that `[B,S]` is **proposed rather than automatically
governing**. Rank 1's *gap* is correctly identified; its *prescription* should not be read as the
only admissible shape. §2 below reaches the same gap without routing through `[B,S]`.

My own earlier finding that §3.7a required an **amendment** is **WITHDRAWN** and stays withdrawn:
one does not amend a proposal.

**1.3 It cites `z_contract.Z_BOUNDARIES` without naming a tree, and that file is forked — but the
fork is immaterial.** Measured: main and the audit base carry blob `24379afb40d2`
(`IDENTITY_RTOL` `:83`, `G_FLOOR` `:84`, `Z_BOUNDARIES` `:213`); the pilot lane and the deployment
carry `80325ce5c788` (`:125`, `:126`, `:255`). The whole difference is **42 inserted lines** — the
OI-136 `sys.path` containment comment and a save/restore around the pinned import. **The withheld
set, `IDENTITY_RTOL = 1e-9` and `G_FLOOR = 1.0` are identical on both.** So the audit's boundary
claim is content-correct on every tree; only a line-number citation would have needed a blob.

**1.4 Two cells it marks unresolved are *declared non-checks*, and the audit says so correctly.**
Recorded at its own lines 141–142. The source addresses, for whoever discharges them:
`nd-unfolding/z_build.py:736` **hardcodes** `"lineage_status": "UNVERIFIED"` and
`nd-unfolding/tests/test_z_build.py:211` **asserts that literal**; `nd-unfolding/z_assembly.py:493`
sets `"stored_cv_cross_checked": diag_c_unified_cv is not None`, so the recorded `false` means the
operand was never supplied. Neither is a check that ran and failed. This matters for pricing: they
are unimplemented, not refuted.

**1.5 STRENGTHENED, not corrected.** The B predeclaration's §3 measures
`OMP_DYNAMIC|OMP_SCHEDULE|OMP_PROC_BIND|OMP_PLACES` as **zero occurrences in `nd-unfolding/`**. I
re-measured it **repo-wide: still zero**, with a positive control of **43** `OMP_NUM_THREADS` hits
in `nd-unfolding/` alone, so the pattern is discriminating. The pin set is incomplete across the
whole repository, not just one directory.

---

## 2. The null decision: the missing justification is the **sensitivity** half, and §6.4 names it

Joseph asked for *"the missing subject-specific precision/sensitivity justification, or the
smallest prospective validation proposal if existing evidence cannot supply it."* That phrasing is
§6.4's own requirement. `SPEC:3577-3580` **RULED**: Z's fixed-seed null bound is scale-relative,
fixed before production, *"with its numerical value justified by **precision and sensitivity
controls established before implementation** and **not** chosen from a favourable production
result."*

**Existing evidence cannot supply it, and the reason is structural rather than a shortfall of
effort.** The SPEC separates the two halves itself, at `:1404-1410`:

> *"…**(ii)** derive the boundary appropriate to that relationship; only then **(iii)** attach a
> number. **And a reproducibility floor is not a substitute for step (ii).** A measured
> process-to-process floor on the target hardware tells you what repeatability is **achievable**;
> it does not tell you what error is **scientifically acceptable**, and the two coincide only by
> accident. It may bound `ε` from below as a feasibility constraint; it cannot justify `ε`.*
> ***`ε` may not be read off Z's own null.** §6.4 is explicit."*

So the **precision** half is available and the **sensitivity** half is the gap. Precisely:

**2.1 Every route to `ε` is presently closed.** Not "not yet derived" — closed.

| Candidate source for `ε` | Status | Authority |
|---|---|---|
| `n_iters × n_rep × eps` | **WITHDRAWN** in rev. 17 — *"a summation bound over a computation that is not a summation"* | `z_contract.py` `null_epsilon` withheld-reason |
| From `B` | `B` is declared **BOOLEAN**, range `{0, undefined}`. Its own author: *"`B = 0` … **does not give `ε`**"*; a gate at `ε = 0` fails on any nonzero deviation whatever | `78a8c2ee` §1.4 |
| From the observed `4.452e-14`, or from any repeat of it | **FORBIDDEN.** *"`ε` may not be read off Z's own null"* | `SPEC:1410` |
| Transfer of `1e-9` from `p4_lib.py` | **DECLINED by Joseph:** a tolerance predating production does not, by its age alone, establish that its application to Z was fixed or scientifically justified beforehand | this instruction |
| From `θ` | **not adopted**, and not to be relabeled a floor | Joseph, §16 |
| From full `S` | **OPEN**; only the F7 channel is argued, §7 item 4 unassessed | `SPEC` §3.7a, reconciliation §10 |

**The consequence that is easy to miss: a repeat experiment cannot produce `ε` either.** More
observations of Z's null are still readings off Z's own null, which `SPEC:1410` forbids. Any
proposal whose deliverable is "measure the floor across allocation shapes, then set `ε` from it"
re-enters the prohibition at one indirection — the same shape as the barred fallback that
`78a8c2ee` §1.2 was written to refuse.

**2.2 Retrospective assessment versus compliance with a predeclared criterion.** Joseph asked for
these to be distinguished; they are different objects and only one is available.

- **Retrospective assessment — available now, zero compute.** `r_null = 4.452e-14`, independently
  reconstructed to 1 ULP by a non-owning lane with the predicate recomputed. As a *scale-relative*
  figure it is two orders of magnitude below G's accepted relative null, which `SPEC:3588` records
  as `5.8223e-50` = `1.31e-12` of the sqrt-trace and characterises as *"genuinely small relative to
  the scale."* **What this licenses:** a statement that no gross nondeterminism is present, and a
  feasibility floor. **What it does not license:** `ε`. It is one draw from the **narrowest possible
  envelope** — one process, one seed, one node — and it is an assessment of an observed value, not
  compliance with anything.
- **Compliance with a predeclared criterion — not available for these products.** §6.4 requires the
  bound fixed before production. Production has happened. No act now can make a bound have been
  fixed then.

**These do not compose into "therefore the products are irrecoverable", and Joseph is right to
reject that inference. §6.4 supplies the precedent in its own words.** The ruling that created this
requirement also says, twice, *"This does not retrospectively regrade G"* — where G's null guard
was **defective by a factor of roughly `10^25`** (`unified_throw_cov.py:517`'s
`tol = 1e-12 * max(‖base‖, 1.0)` evaluating to an absolute `1e-12` on a vector of norm order
`1e-37`). §6.4's reason is the general principle: ***"The defect is in the guard, not in the
product."*** An incomplete acceptance criterion is a defect in the guard. It does not condemn the
products, and — symmetrically, and this is the limit — it does not confer standing on them either.
Not regrading cuts both ways.

**2.3 What is actually wrong with the null as it stands, and it is a live finding.**
`nd-unfolding/sbatch_uthrow_combine_5d_fast.sh:9` — byte-identical on main and on the pilot lane —
asserts:

> *"`--null` repeats CV at the identical seed and **must be zero** (no jitter subtraction)."*

The measured value is `4.452e-14`. **The production launcher's own stated property is not
satisfied by the production receipt.** And the deviating pair is the *strictest* case available:
`z_statistics.py:87-89` records that *"the numerator compares two INTERNALLY re-unfolded CVs"* —
same process, same seed, same node.

⚠ **This does not falsify `B = 0`, and saying so would be applying an estimator outside its declared
population.** `78a8c2ee` §1's estimator ranges over the CV vectors of *n arm-7 runs*; no such runs
exist, so `B` is **UNEVALUATED**, not refuted. But it does identify the mechanism question that has
to be answered before any repeat is worth buying: the two internal re-unfolds share process state,
so their disagreement may have a cause — warmed caches, an advanced RNG, accumulated allocator or
float state — that would *not* act between two separate runs each taking its own first unfold.
Until that is resolved, a "not identical" outcome from the arm-7 runs would be **ambiguous**, which
is exactly the ambiguity `78a8c2ee` §3 flags for the unpinned OpenMP variables.

**2.4 The smallest prospective validation proposal.** Its objective is **not to establish `ε`** —
§2.1 shows that is unreachable — but to **make `ε` unnecessary**, by testing bitwise identity, for
which no tolerance is needed. This also answers Joseph's standing question about the required
reproducibility property: **bitwise identity, and the reason is that the tolerance route is closed,
not that bitwise is more virtuous.**

- **Step P0 — zero compute, do this first, and it may end the matter.** Diagnose the `4.452e-14`
  from preserved data and source alone: determine from `z_receipt.load_null_operands` and the arm-7
  producer whether the two internal re-unfolds are a like-for-like pair, and whether the deviation
  is confined to shared-process state. **Outcomes:** if the pair is not like-for-like, the launcher's
  `must be zero` is mis-stated rather than violated and the finding is a documentation repair; if it
  is like-for-like, the pinned design does **not** deliver determinism within a single process and
  the arm-7 experiment would fail — **so the 1.73–2.31 CPU task-h should not be spent until P0
  returns.** Either outcome is decision-relevant and neither costs an allocation.
- **Step P1n — complete the pin set, a code change, not a measurement.** Set or capture the four
  OpenMP variables (§1.5: zero occurrences repo-wide). `78a8c2ee` §3 is explicit that without this
  a negative result cannot distinguish *"the design cannot be pinned"* from *"the design was never
  fully pinned."* This is `lane_b`'s to make.
- **Step P2 — the repeat, only if P0 and P1n clear it.** `78a8c2ee` §2.2's Model-A minimum: two runs
  on the same node (tests same-shape determinism) plus one on a different node (tests cross-shape),
  `n = 3`, **reservation bound 1.73 CPU task-h**; `n = 4` at **2.31** to make a single-run anomaly
  separable. Priced from the measured per-invocation maximum `0.5764` CPU task-h
  (`uthrow5d_combF`, `SPEC` §5.9 row 13; the three recorded runs `0.3875 / 0.4239 / 0.5764`), as
  enforced-cap reservation bounds and not completions. **`78a8c2ee` §2.3's receipt requirement is
  binding: ≥ 2 distinct node names, or item 2 is INCONCLUSIVE — not a pass.** Model B, if Model A
  is refuted, costs 3.46 CPU task-h to exclude a coin flip and 17.29 to exclude `p ≥ 0.10`; that is
  a cost finding, not a licence to keep sampling.
- **What P2 would and would not buy.** It operates on the **preserved** operands and the **pinned**
  code, so a bitwise result is a property of *the configuration that made the existing products* —
  that is a justified transfer, and it is a different argument from "the tolerance is old." It does
  **not** make a bound have been fixed before production. **It does not require regenerating the
  campaign**; it re-executes one combine step, not the unfolding campaign.
- **Two open items that are Joseph's and not a lane's**, both recorded at `78a8c2ee` §4:
  whether the arm-7 control may run on Z's own bank (`SPEC:3140`: *"if the control runs on Z's own
  bank, §6.4 is engaged and needs a ruling"*), and the residue that `ε`'s own falsifier is
  UNEVALUATED.

---

## 3. What this does *not* hold up

Per Joseph's instruction, nothing below waits on §2. Task 1 (cause-3) is with
`z-criteria-designer`; task 2's rank-3 leg is with `z-independent-assessor`, which is the only
non-owning lane with cluster access and therefore the only one that can close a payload check.
Both were dispatched with the §1 reconciliation attached.

---

## 4. P1 — the projection definitions, COMPLETE

All source-only, at main `ce72abbc`. Axis order is C-order throughout.

**4.1 The grid and the maps.** `project_cov_nd.py:44-52` `AXIS_EDGES`: `pt` 14 bins, `pz` 16,
`eavail` 7, `q3` 7, `W` 6 → **65,856 dense**, reported support **10,694** (`x_cv > 0`).
`_verify_canonical_edges` (`:55-64`) **fails closed** against `unfold_2d_omnifold_unbinned.PT_EDGES`
/ `PZ_EDGES` and `unfold_nd_omnifold_unbinned.EXTRA_AXES`, so edge drift cannot pass silently.

| # | Map | Dense destination | Producer | On the intended claim's path? |
|---|---|---|---|---|
| M1 | 5D → `(eavail, W)` | 7 × 6 = **42** | `project_cov_nd.py --keep-axes eavail,W` | **YES — the only one. See §6.** |
| M2 | 5D → `(pt, pz, eavail, q3)` | 14·16·7·7 = 10,976 | `p4_project_4d.py` (pinned writer) | No — supports reported central values |
| M3 | 5D → `eavail` | 7 | `project_cov_nd.py --keep-axes eavail` | No — diagnostic / marginal anchor |
| M4 | 5D → 3D | per keep-axes | `project_cov_nd.py` | No — marginal anchor |

**4.2 Bin-width factors and units.** `build_projection:87-90` sets each entry to the **product of
the dropped axes' bin widths**, `w = Π_{a∈drop} diff(AXIS_EDGES[a])[idx]`. Kept-axis widths are
**not** applied. So the map integrates out the dropped axes and the destination is a **differential
density in the kept axes** — the correct convention for `dσ/dX`, and it is what makes
`C_low = M C M^T` a covariance of densities rather than of counts.

**4.3 Masks, ordering, support exclusions.** Source rows are `np.where(xsrc > 0)[0]` — the reported
predicate, never a hardcoded count. Destination rows come from `--dst-cv`'s own `CV > 0` mask when
supplied, otherwise from the dense bins that receive at least one source cell (`:151-160`).
`:123-124` **refuses** keep-axes that do not preserve source C-order. **Both support censuses are
present and printed:** `src_cells_dropped` (source cells whose destination bin is unreported —
weight zero, excluded) and `n_empty` (destination-reported bins receiving **no** source cell). The
audit is right that `SPEC` §2.6 withdrew the claim that these guards were missing; I confirm they
exist and are bidirectional.

**4.4 The central estimate paired with each projected covariance.** `:168` computes
`y = M @ xsrc[src_report]` — **the marginalized 5D central value** — and compares it against the
frozen lower-D CV, printing `max|rel|` and the median with *"expected ~<=3% — independent lower-D
central vs marginal"*. **This is a printed diagnostic, not a gate, and it must stay that way.** The
paired central estimate for a projected covariance is `M x_5D`, *not* the independently unfolded
lower-D estimator; those are different estimators and the ~3% is the measure of their difference,
not an error. Any downstream packet must name which of the two it pairs.

**4.5 Two tolerances in the projector that are not the contract's.** `:184` hardcodes `rc = 1e-12`
for a **printed** rank report and `:190` uses `psd_ok = ev[0] >= -1e-10 * ev[-1]`. Neither is
`IDENTITY_RTOL = 1e-9`, and neither is a scientific boundary. The retained-rank **declaration**
that rank 6 requires does not exist here — a printed `rank~k/n` is not a declared subspace.

**4.6 ⚠ NEW FINDING, and it is the stronger half of the OI-129 family.**
**`project_cov_nd.py` records no digest of anything.** Measured: `grep -c 'sha256\|hashlib\|digest'`
returns **0**, against a positive control of **13** on `p4_project_4d.py`. It writes
`hCov_proj_<axes>`, `hCV_marginal`, `sqrt_tr`, `n_dst` and `src_cells_dropped` — and binds neither
its input covariance, nor its output file, nor `M`, nor the row index. OI-129 is filed against
`p4_project_4d.py`, which is the **better**-instrumented of the two. **M1, the one map the intended
claim needs, would be produced by the uninstrumented projector.**

---

## 5. OI-129 narrow repair scope — PREPARED, NOT IMPLEMENTED

Not implemented and not run, per instruction. Ownership is unchanged: OI-129's row assigns the
write path to the standard-P4 lane, and the repair carries its owning re-verification.

**5.1 `p4_project_4d.py` — the filed residual, confirmed at this revision.** `:200-202` writes
`hRowIndex4D` via `SetBinContent`, then `:229-231` computes `row_index_sha256` from
`np.nonzero(m4_eff)[0]` — **the same in-memory array**, never reopening the stored object. And no
field digests the written covariance file. Two additions, both after `fo.Close()`:
1. `"proj4d_sha256": P.sha256_file(args.out)` — the object's own digest.
2. Reopen the closed file, read `hRowIndex4D` **back out**, digest that, and require it to equal
   `row_index_sha256`. This converts a self-consistent record into a readback.

**5.2 Extend the scope to `project_cov_nd.py`** (§4.6). Minimum to reach parity with the pinned
writer: digest the input covariance file, `M`'s contents, the output file after close, and the row
index read back out. This is the larger half of the work and it is currently unfiled.

**5.3 Sequencing.** Both are code changes to write paths. They should land **before** M1 is ever
produced, because their whole purpose is to make the produced object identifiable; retrofitting a
digest onto an existing file records only that the file has not changed since the retrofit.

---

## 6. Downstream inference: exactly one claim is intended

Joseph's instruction — *"Identify which of those claims are actually intended before proposing
additional studies"* — has a sharp answer, measured from the manuscript source rather than from a
status table. `docs/analysis-note/main_paper.tex:49-51`:

> *"They recover the established low-recoil discrepancy and localize a generator deficit in the
> joint high-available-energy, high-mass region. **The latter is a central-value result; its
> significance awaits adoption of a common five-dimensional covariance.**"*

**One deferred claim. It lives on the `(E_avail, W)` plane — 42 dense bins.** This is consistent
with OI-187's both-halves ruling and narrows the downstream work substantially:

- **Rank 6 is on the intended path, for M1 only.** Ranks 7 and 8 are *not* required by any written
  claim: coverage of the reported band and an inferential unbinned GoF are upgrades nobody has
  asked for. They should stay as assumption tables, exactly as the audit scopes them.
- **The consumer for the intended claim does not read a 5D covariance at all.** Measured:
  `eavailW_covariance.py` builds its **own** component sum — 13 ±1σ knob bands plus
  `(1/Nflux) Σ_u outer(y_u − y_cv)` at MAT `1/N` centering — reads the **historical** 4D combined
  covariance via `--cov4d`, and at `:445-448` obtains the detector contribution by marginalizing
  each 4D lateral band to `E_avail`, taking the per-`E_avail` variance as a **fractional**
  uncertainty and spreading it over `W` by the CV shape: *"flat-in-W fractional — documented
  approximation."* **So what adoption actually buys the one deferred claim is concrete: it replaces
  a self-documented flat-in-W approximation with a derived correlation structure.** That is a real
  scientific gain and it is worth stating plainly, because it is the answer to "what would this
  permit."
- **The audit is right that re-pointing an input path is not the repair.** I verified both
  consumers myself: `eavail_generator_significance.py:107-108` and `eavailW_covariance.py:544,549`
  call `np.linalg.pinv` with **no explicit `rcond`** — and `:99` of the former already comments that
  the matrix *"can be near-singular -> pinv amplifies shape directions"*, so the hazard is known
  and unaddressed. Degrees of freedom are **bin counts**: the printed header is literally
  `chi2/ndf(all7)`. A replacement consumer contract is required, not a filename.
- **One answerable provenance question, put as a question and not an accusation.**
  `eavail_generator_significance.py:106` fixes `E_avail >= 0.8` in code;
  `eavailW_covariance.py:546-548` fixes the corner at `E_avail >= 0.4 & W >= 1.8` and attributes it
  to *"open question 6."* If that open question predates the inspection of these data, the region is
  prespecified and no selection penalty applies; if it does not, the claim needs selection-aware
  calibration. **This is settleable from the open-question record at zero cost**, and it should be
  settled before anyone designs a calibration for it.

**What a valid covariance and an exact projection do not license**, restating the audit's finding
because it is the guard against the tempting inference: a successful `C_low = M C_5D M^T` identity
proves **propagation** of its input. It does not calibrate a significance, does not supply support
the 5D object never had, does not make an independently unfolded 4D/3D estimator the marginal of the
5D one, and does not license arbitrary event-level fits.

---

## 7. The dependency table

`SOURCE` = source review · `PAYLOAD` = payload verification · `COMPUTE` = new computation ·
`DECISION` = Joseph's ruling. The three are kept distinct per instruction.

| Item | Kind | Complete | What existing evidence can settle | Scientific decision needed | Named measurement needing authorization |
|---|---|---|---|---|---|
| Pilot construction, PSD/identity gates, precursor persistence | — | **YES**, closed and preserved | — | — | none |
| E1 null reconstruction | SOURCE+PAYLOAD | **YES** — 1.00 ULP, predicate recomputed | — | — | none |
| E2 tolerance provenance | SOURCE | **YES** — `5d617da8`, 2026-08-08 | — | — | none |
| `ε` / `null_epsilon` | DECISION | no | Nothing. **Every route is closed** (§2.1) | **The §6.4 route question**, and whether the arm-7 control may use Z's own bank (`SPEC:3140`) | P2 only after P0/P1n: **1.73 CPU task-h** (n=3) or **2.31** (n=4), reservation bounds |
| Why `r_null ≠ 0` at all (§2.3) | SOURCE | no | **YES — fully, at zero compute.** This is P0 and it is the cheapest decision-relevant item in the package | — | none |
| Pin-set completion (4 OpenMP vars) | SOURCE→code | no | The gap is measured: **zero occurrences repo-wide** | — | none; it is a `lane_b` code change |
| `B` | COMPUTE | no | Estimator and coverage objective **exist** (`78a8c2ee`) and are predeclared | — | same P2 runs |
| Full `S`, §7 item 4 | DECISION | no | F7 channel only; item 4 **unassessed and unrouted** | **YES** — `S` is a scientific cap | none |
| `θ` | — | **CLOSED, not adopted, not a floor** | — | — | none |
| cause-3 boundaries (`agg`, `med`, `corr`) | DECISION | no | A member/design proposal exists | **YES** — with `z-criteria-designer` now; assessment pre-authorized | member production, **after** approval |
| **Grid vs diagonal member family** (§10.3) | DECISION | no | The split is measured invariant under `k`, so the diagonal family **cannot** resolve it | **YES — NEW.** Must be decided **before** offsets are declared | none; a launcher change and a second offset axis, **code not compute** |
| L3 statistic | SOURCE | requirement endorsed; statistic **refuted**; replacement supplied (§10) | Whether to accept a **hybrid** statistic — disjointness and actuality cannot both be had | **YES** — that trade-off | none |
| Registry reject-on-mismatch rule | DECISION | no | Shown **unsatisfiable at every `k`** (§10.2) | **YES** — amend the estimator-seed field; do not unify seeds | none |
| Lineage / `parent.lineage_status` | PAYLOAD | no | Nothing — it is an unimplemented non-check (§1.4) | — | none; with `z-independent-assessor` |
| Component footing, per-component compatibility | PAYLOAD | no | Partly — source fixes estimator/units/normalization | — | none; same lane |
| External CV cross-check | PAYLOAD | **YES — performed** (§9.3), 65,856/65,856, `max abs diff` 0 | — | — | none |
| `globalCompleteness > 1` | PAYLOAD | no | Numerator/denominator **semantics** | **YES** — a disposition. Do not normalize into range | none |
| Causes 1, 2, 4, 5, 6, 7 | mixed | no | See the audit's seven-cause table; several are source-closable | per cause | cause-specific counterfactuals |
| **P1 projection definitions** | SOURCE | **YES — §4** | — | Which central estimate pairs with M1 (§4.4) | none |
| OI-129 repair, both projectors | SOURCE→code | scope **prepared**, §5 | — | — | none to scope; owning re-verification to land |
| M1 `(E_avail, W)` product | COMPUTE | no | — | Adoption of the trunk first | projection production |
| Rank 6 consumer contract | DECISION | no | The defects are source-established (§6) | **YES** — retained rank, `rcond`, null law, ndf | none to specify |
| Corner prespecification (§6) | SOURCE | no | **YES** — from the open-question record | only if it was not prespecified | none |
| Ranks 7, 8 | — | no | Already dispositioned descriptive/diagnostic | **Not required by any written claim** | separate authorization |
| Rank 9 disclosure / OI-172 | SOURCE | no | Reconcilable against actual note text | — | none |

**The smallest decisive next action in the whole package is P0** (§2.4): it costs nothing, it is
source-and-preserved-data only, and it determines whether the 1.73–2.31 CPU task-h of P2 is worth
requesting at all. Nothing else in the table gates it.

---

## 8. Standing constraints carried forward

No new cluster compute. No production projections. No criterion adoption. No covariance adoption.
No publication. No grading. The completed precursor and pilot stay closed and all products are
preserved. `θ` stays not-adopted and is not relabeled. Neither the completed 2D central campaign
nor Gate 6 nor OI-126 is reopened.

---

## 9. CORRECTIONS AND INCOMING RESULTS (appended 2026-09-18)

### 9.1 ⚠ I had the aggregation factor's two directions REVERSED

I told both lanes that a per-bin tolerance is *"non-conservative under movement coherent across a
destination cell's 1,568 contributors, over-conservative under cancelling movement."* **Both halves
are wrong.** `[91eaa2]` caught it; I re-measured independently and it is right.
`probes/probe-20260918-aggregation-channel-directions.py` is the self-checking record, mutation-tested
in both directions (killing the near-cancellation fires claim 3; making the coherent move
N-dependent fires claim 1b).

**Coherent movement is the BENIGN channel and it is exact:** `σ → (1+δ)σ` sends `C → (1+δ)²C`
identically, so *every* quadratic form — every projected variance, on every map — moves by exactly
`(1+δ)² − 1`. Measured invariant across `N ∈ {2, 10, 200, 1568}` **and** across uncorrelated,
`ρ = +0.5` and near-cancelling structures. **Aggregation averages a coherent move; it does not
amplify it, and 1,568 does not multiply it.** The factor 2 is variance being quadratic in `σ`.

**The blow-up is cancelling movement over a near-cancelling source** — the same channel that refuted
my §5.7 projection-bound claim, one level down.

⚠ **But it is NOT "≈ N ×", and that framing should not propagate.** In my construction the factor
*decreases* with `N`: `2.0e6 → 1.23e5 → 5.05e3 → 639`. Severity is set by how small `wᵀCw` is, not
by how many cells aggregate. `[91eaa2]` reported ~200× at `N = 200` where I measure 5050×; the
disagreement across constructions is itself the evidence that `N` is not the governing variable.

**The corrected conclusion is stronger, and it reverses my recommendation.** `δ_bin` is **exact** on
the coherent channel and **vacuous** on the cancelling one. That argues L3's primacy better than
"weak proxy in both directions" did — and **L2 should be kept as a declared diagnostic, not
demoted**, because it is the only free control on the coherent channel. `[91eaa2]` argued this and
I was wrong to push against it.

### 9.2 ⚠ And no a-priori bound exists for `C_Z`, because it is not positive definite

For positive weights and a **positive-definite** `C` the excursion is bounded by
`((1+δ)² − 1) × λ_max/λ_min`, and `z_assembly.py:44-46` records both ends — so this looked like a
zero-compute lookup. It is not. Measured from the pilot's own table:

    C_Z cv (inflated):  lambda_min = -1.2750516323643892e-90   (NEGATIVE)
                        lambda_max =  2.229223998752954e-75
                        neg_fraction_of_max = 5.719710684424999e-16
                        5214 negative eigenvalues of 10,694

`λ_min < 0`, so the bound does not exist and the cancelling channel is **unbounded in principle**
for `C_Z`. **"Passes the PSD gate" supplies no bound**: the gate asserts `λ_min ≥ −rtol·λ_max`, a
statement about arithmetic, not definiteness. The structural gate and this scientific criterion are
decoupled exactly here. `[cb0b6b]` independently confirmed the extrema from `z-receipt-cv.json`.

**What decides it is one object: the diagonal of `M1 C_Z M1ᵀ`** — the projected variance vector,
i.e. the M1 product the one deferred claim already needs. `τ_p`'s evaluability and the claim's
production requirement coincide, so no separate study is owed.

⚠ **`n_negative` NAMES TWO DIFFERENT QUANTITIES.** `unified_throw_cov.py:372` computes
`nonzero(x_cv < 0)` — negative **bin values**, recorded as **zero** in the census.
`z_pilot.py:275,290` computes it on `eigvalsh` — negative **eigenvalues**, the 5214. Anyone grepping
the name hits the wrong one first. And the eigenvalue count lives in the **separately persisted
spectra**, not in `z-receipt-cv.json`, which carries only the extrema.

### 9.3 The external CV cross-check that stood UNPERFORMED is now PERFORMED

`[cb0b6b]`, measured on payload with read-only login-node reads: production `hXSecND_flat` versus
the persisted vector, **65,856 of 65,856 identical, `max|Δ| = 0.000e+00`**; support mask recomputed
as `production > 0`, identical, 10,694 each; `flatnonzero(mask)` versus `hRowIndex5D` identical and
strictly increasing. It correctly declines to flip `G3R.stored_cv_cross_checked`, which records that
the producer was handed no operand and remains accurate. **Check satisfied, flag unchanged — two
different statements**, and §7's row for this item moves from PAYLOAD-open to closed.

### 9.4 ⚠ A record collision that rank 3 surfaced and cause 3 must dispose of

`[cb0b6b]` measured: the registry declares estimator seed 42; the throw payload records
`estimator_seed = 1000`. Both sides verified here:

- `docs/ESTIMATOR_REGISTRY.md:17-22` — *"every covariance component must carry the identical
  estimator fingerprint as its central product (**reject on mismatch**)"*, with estimator seed among
  the nine fields. Row `:29` gives `omnifold-5d-lgbm` **"5 iter, est seed 42"** for the central.
- `sweep_bank_5d.py:354-356` — *"42 is this module's archive value — and it **deliberately DIFFERS**
  from `unified_throw_cov.py`'s 1000. Each module's default-equivalent preserves ITS OWN prior
  behaviour; **unifying them on one number is the instinct a later reader will have** and it
  silently re-seeds one of the two."*

**Both records are internally correct and they cannot both be satisfied.** Read literally, the
fingerprint rule is violated by a difference the source calls deliberate and warns against
"repairing". This is not a payload defect and not a lane's call: cause 3's subject *is* estimator
seeds, so the disposition sits with the cause-3 owner. **Do not unify the seeds** — the source names
that as the trap.

⚠ **An unmeasured mechanism, flagged as such and not asserted.** Mean-centering subtracts the
ensemble mean, so a *common* estimator offset shared by all throw universes cancels; **CV-centering
does not**, because the CV sits at the other seed. If the throw universes are unfolded at 1000 and
the CV at 42, the CV-centered variant could absorb that offset as though it were a throw
fluctuation. The registry's two √tr figures are **mean-centered `5.8077e-38`** and **CV-centered
`6.2367e-38`**, with the mean shift recorded separately as `1.654e-38`; note
`sqrt(5.8077² + 1.654²) = 6.039`, near but not equal to `6.2367`. **I have not established this
mechanism and it should not be repeated as though I had** — it is a question for cause 2's owner,
with the arithmetic shown so it can be checked rather than believed.

### 9.5 Endpoint completeness: two phenomena were pooled, and one dissolves

`[cb0b6b]`, measured: `globalCompleteness` on the central product is **exactly 1.0**; per-bin
readings above one number **2,768 of 10,694**, with **median excess `2.220e-16` — one ULP** and max
`1.088e-14` — 49 ULP. **Those are rounding, not a defect.** The **endpoint** readings, `1.001824`
and `1.000521`, are **eleven orders larger** and cannot be rounding; they stay UNRESOLVED with a
reason — `mii_anchor_comparator.py:125-128` classifies the quantity NOT_RECOMPUTABLE / WRITER_GAP
with both ingredients unwritten, so no read settles it. Its larger incidental finding — that `of_in`
and `denom_nd` agree to the last bit across essentially the whole support, so the completeness
division **applies no correction in 5D** — is recorded without disposition and is not mine to issue.

### 9.6 What the rank question cost, and the honest answer

I asked whether a rank figure for `C_Z` was cheaply reachable. **It is not.** `[cb0b6b]` established
that the receipt carries no rank and no eigenvalue count, so a rank or retained-subspace figure needs
an eigendecomposition of the `10,694²` matrix — **new computation, not a read**, and correctly
refused on a shared login node under a no-compute leg. If it is wanted it must be scoped and
authorized as its own item. The reason it would be worth scoping is unchanged: rank deficiency is the
same property that makes `pinv`-without-`rcond` dangerous at rank 6, so one measurement would serve
both. **Z's rank is not the old P4 263** — the audit is explicit that the old rank does not determine
Z's, and it must not be transferred.

---

## 10. L3's statistic is refuted — and a replacement, with its cost

`[cb0b6b]` refuted the cause-3 packet's §4.1 **statistic** while endorsing its **requirement**. I
confirmed the refutation by independent measurement and then supplied the replacement it declined to
offer: `probes/probe-20260918-l3-statistic-diagonal-breach-and-repair.py`.

**The refutation.** §4.1 rightly requires an L3 statistic to be invariant under `C → D C D` in the
**source** basis, so pure per-bin σ movement cannot be reported through L3's instrument. But the
packet's proof is about `corr(C)` while its statistic is `corr(M C Mᵀ)`, and
`M(DCD)Mᵀ = (MD)C(MD)ᵀ` — a projection with a **different map**. A source rescale reweights how
source bins are aggregated, and no diagonal in the destination basis undoes that. Measured here:
`corr(C)` invariant at `4.441e-16`; under a pure diagonal rescale with source correlations identical
to `4.4e-16`, the proposed statistic drifts **`0.0004 / 0.0034 / 0.0179 / 0.0753 / 0.1854`** at
sd `1e-3 / 1e-2 / 0.05 / 0.20 / 0.70`.

⚠ **New, and it is the decision-relevant part: the breach is near-LINEAR in the rescale, at ≈ 0.3× sd
across three orders of magnitude.** So it is real but **bounded and quantifiable** — at a realistic
`δ_bin ≈ 1e-3` the leak into L3 is ≈ `3e-4`, not a swamping. The refutation is fatal to
*disjointness*, not to the statistic's usability as a diagnostic.

**The conflation, named:** `corr(M C Mᵀ)` **is** invariant under a rescale in the **projected** basis
— trivially, it is already a correlation matrix. That is what the packet proves. It is not what §4.1
requires.

**The replacement.** Hold the source diagonal at the reference member before projecting:

    D0      = diag(sqrt(diag(C_0)))                 from member k = 0
    renorm  : C_k  ->  D0 @ corr(C_k) @ D0
    L3 STAT :          corr(M @ renorm(C_k) @ M')

Invariance is **exact by construction, not by measurement**: `corr(D C_k D) = corr(C_k)` identically,
so `renorm(D C_k D) = renorm(C_k)` identically. Measured at `3.3e-16` for rescale sd up to **2.0**,
while still responding to genuine correlation change (`0.0021 / 0.0108 / 0.0454` at correlation mix
`0.01 / 0.05 / 0.20`), so it is not vacuous.

⚠ **Its cost, stated rather than buried.** `renorm(C_k)` is a **hybrid** — member `k`'s correlations
on member `0`'s variances — so the statistic does not test member `k`'s *actual* projected
correlation. That is unavoidable and it is the point: the actual projected correlation **cannot** be
disjoint from L1/L2, because source variances set how strongly each bin is weighted inside its
destination cell. **Disjointness and actuality cannot both be had.** Anyone adopting this accepts the
hybrid; anyone wanting the actual object must give up §4.1's invariance requirement and say so.
Preconditions are in the probe: every destination cell must receive ≥1 source bin (the `n_empty`
census already covers it), and the source diagonal must be strictly positive on the reported support
— which the `x_cv > 0` predicate does **not** establish, since that predicate is on the central value,
not the variance.

**Supplies no tolerance, approves nothing, and is a diagnostic transform only** — `renorm(C_k)` is not
a covariance to be used anywhere else.

### 10.1 A methodological finding from `[91eaa2]` worth keeping

Withdrawing its `≈ N ×` claim, it measured *why* the wrong law looked right: at **fixed** cancellation
depth, varying `N` gives `2.0 / 10.0 / 199.8 / 1566.4` — a near-perfect linear fit to `N`, **and it is
spurious**. At **fixed** `N = 200`, varying depth gives `1.8 / 19.8 / 199.8 / 199999.8`. **A
one-directional scan confirmed the wrong law cleanly**, and only varying the other axis exposed that
there was no law there. The governing quantity is the cancellation ratio; `N` enters only through what
it does to `wᵀCw`.

### 10.2 Why the registry rule is worse than a collision

`[91eaa2]`'s disposition is sharper than my §9.4 and I adopt it: applied literally, reject-on-mismatch
rejects **every** throw component at **every** offset `k` — including `k = 0`, which is the archive and
is Z's own build. **So the rule rejects the very product the registry exists to describe, cannot be
satisfied at any `k`, and its only available repair is the act the source names as the trap.** That is
unsatisfiable by construction, the same class as the `1e-12`-clamp defect. The disposition: amend the
rule on the estimator-seed field; **do not unify the seeds**; check within-family identity plus a
declared inter-family map — half already implemented at `analyze_universes_5d.py:137-166`, which
refuses a mixed-seed member; and pending amendment, record the mismatch as declared heterogeneity.

### 10.3 ⚠ A NEW DECISION FOR JOSEPH, raised by `[91eaa2]` and not previously on any list

**The `42`/`1000` split is invariant under `k`** — both groups move together under the offset — **so it
is a property of the architecture, not of any member, and the diagonal member family cannot resolve
whether it matters.** Resolving it needs the two groups varied **independently**: a second offset axis,
i.e. a launcher change and a second environment variable. That is **code, not compute** — but it must
be decided **before** the offsets are declared, because it changes the member set. So the
grid-versus-diagonal question is no longer a design preference; it is an open scientific question with
a named consumer. See §7's table, where it is added.

### 10.4 On my own unestablished mechanism

`[91eaa2]` checked the arithmetic I flagged and it **does not close**: `√(5.8077² + 1.654²) = 6.0386`
against `6.2367` is **3.18% short**, far too large for rounding, so the near-miss is not a derivation.
It stays cause 2's question and unestablished, as I labelled it. One point it drew that I had not:
row `:29` records the adopted product as **"adopted mean-centered"** — the centering for which the
mechanism would predict cancellation — so were it ever established it would bear on the **CV-centered**
variant, which is exactly the branch **L4** decides. That is a reason to keep L4, not to discount it.

### 10.5 A citation of mine that could not be resolved, and why neither side erred

`[cb0b6b]` could not resolve my `unified_throw_cov.py:372` and could not find `z_pilot.py`. Measured:
`unified_throw_cov.py` is forked **three ways** — main blob `65a8f1b8…` and lane blob `41a71ad1…` both
have the `n_negative` line at `:372`, while `937c3847`'s blob `2f29b6ec…` has `nrep = int(rep.sum())`
there. And `z_pilot.py` exists **only** on `lane/z-assembly-pilot-20260914`. So the substance holds on
two trees of three and neither lane mismeasured; **I cited a line without naming a tree.** Third
instance in this project.

---

## 11. The L3 requirement was mis-specified — my hybrid is withdrawn as the criterion

`[91eaa2]` rejected the hybrid and re-specified §4.1's **requirement**. I checked the citation it
turns on and **it is verbatim**, `z_contract.py` `cause3_corr`, blob `24379afb40d2` (main):

> *"no correlation-sensitive leg is adopted, and none has a boundary. **Both adopted statistics are
> functions of the diagonal alone, so a MET result on them licenses nothing about `C_Z`'s
> off-diagonal structure.**"*

That is a complaint that the statistics **cannot see** correlations — a **sensitivity** requirement,
not an **invariance** one. §4.1 asked for the wrong property and I endorsed the wrong property.
`[91eaa2]`'s measurement at *exactly* equal source diagonal settles it: trace ratio `0.0` and per-bin
σ `4.4e-16` both **fail** (blind to correlation), while its statistic and my hybrid both move
`0.003620 / 0.017998 / 0.070526` — **identically**. They must be identical, because holding the
diagonal fixed makes `renorm(C) = C`. **So on the test the boundary actually demands, the hybrid adds
nothing.** It is withdrawn as the criterion and retained only as a secondary diagnostic that isolates
which channel moved.

### 11.1 ⚠ My counter-test REFUTED MY OWN OBJECTION

I expected the leak coefficient to blow up in `C_Z`'s regime — anti-correlated, near-null — which
would have killed the budget. **Measured, and it is the opposite:** leak per unit rescale sd is
`0.415 / 0.297 / 0.345` on a generic PSD source but only `0.023 / 0.027 / 0.023 / 0.025` at
near-cancellation depths `0.90 / 0.99 / 0.999 / 0.99999`. **An order of magnitude smaller in the
regime I expected to be worse.** The objection is withdrawn.

What survives is weaker and still real: **the coefficient moves by ~18× across source families, so
`0.3` is a measurement on one synthetic ensemble, not a bound.** It must be measured on the actual
`M1` and `C_Z` before it enters a criterion — which is again the same object, `M1 C_Z M1ᵀ`.

### 11.2 The consequence of the budget that I think has not been priced

`τ = τ_corr + 0.3·δ_bin` is a bound only if **`δ_bin` is an enforced gate**. But `δ_bin` is
**WITHHELD and blocked** on the same unestablished quantity that closed `θ`, and L2 is being retained
as a **diagnostic**, not a gate. A budget term built on an unenforced, unvalued quantity bounds
nothing, and it has a further effect:

**Under the hybrid, L3 was independent of `δ_bin` by construction. Under the budget, L3 inherits
L2's blockage** — `τ` cannot be evaluated until `δ_bin` has a value, and `δ_bin` is blocked. So the
choice trades L3's independence from the blocked quantity for actuality of the object. That may well
be the right trade — `[91eaa2]`'s argument that `renorm(C_k)` *"is an object that exists in no
product"* is a fair scientific objection, and a criterion on an object nobody publishes protects
nothing. **But it should be made knowingly**, and it moves `τ_p` from "not blocked in principle" to
blocked-with-`δ_bin`.

### 11.3 Two preconditions were accepted and one was strengthened

Both bind whichever instrument is chosen, since both divide by `√diag`. `[91eaa2]` added the part I
had left soft: the `n_empty` census must be declared as a **pass condition**, not merely recorded — a
census recorded but not gated is the green-gate-that-proves-nothing shape. And on the `x_cv > 0`
catch, a zero-variance reported bin must be a **REFUSAL, not a masked bin**, since masking it after
the fact would be a post-hoc population change.
