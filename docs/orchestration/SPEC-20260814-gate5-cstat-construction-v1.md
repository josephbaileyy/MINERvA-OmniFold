# SPEC — Gate-5 `C_stat` construction, v1

**Status:** SPEC, LIVE. **Author:** lane C (PET), owner of Gate 5 / P5B.1 / `C_stat`.
**Authorized by:** `OI-121`, Joseph's *"go ahead"* relayed by `personal-orchestrator` 2026-08-14.
**Companion machine contract:** [`nd-unfolding/pet/gate5_cstat_contract.json`](../../nd-unfolding/pet/gate5_cstat_contract.json)

**What this document is.** The single written specification the builder implements. **Builder: lane B**
(which owns the P5B assembly conventions). **Comparator: D. Judge: `codex` background.**

**THERE IS ONE BUILDER, NOT TWO — and this document must not be read as though an independence claim
were available, because it is not.** Joseph's decision, relayed 2026-08-14: *"Okay yeah drop the second
builder."* Three reasons, and the second is the one that indicts the original design: (a) D measured that
`Xc.T @ Xc` and `np.einsum` are **bitwise identical** because NumPy dispatches both to the same BLAS
`dgemm`, so two builders were likely one computation at the kernel; (b) **this spec pins `dof`,
`centring`, `ravel_order` and member selection — precisely the decisions above the kernel that would have
been the only source of genuine divergence, so the better the spec, the less two builders could differ**;
(c) both `codex` accounts are out of quota, so builder 2 had no home.

**What the artifact therefore gets, stated so nothing larger is claimed later:** spec conformance, a
regression comparison against the established in-tree recipe (`combine_cstat_bkgsub.py`), and D's
element-wise harness catching ordering and permutation errors that every structural check is provably
blind to. **It does not get an independence claim.** That is proportionate for a component measured at
**0.669%/bin against `C_syst`'s 7.27%** — and claiming more would be the exact failure this campaign
keeps filing findings about. Where an earlier draft of this spec argued from "two builders would agree",
that argument is withdrawn, not weakened: see §6, where the consequence is that **the spec's declaration
is now the only protection against the mask hazard.**

**On `REQUIREMENTS-20260814-cstat-assembly-conventions.md`, which is authored by the builder.** D flagged
that a spec-shaped document written by B would compromise the design by construction. The innocent
reading is the correct one and the mediator confirmed it: **the mediator dispatched B to write it as
INPUT to this spec, before this spec existed**, so that a convention conflict would surface before
construction rather than at comparison time. **It is B's input. It is not the spec.** This document
ratifies specific conventions from it — `layout_fingerprint`, `dof`, `centering`, `ravel_order`, the
full-grid `reported_mask`, and the `(n_reported, n_reported)` shape — **explicitly and in C's own voice**
at `CSTAT-R6` and §3.1, and a reader should treat those as C's requirements, not as B's self-certification.
B's document also contains a finding this spec depends on and did not produce: **`receipt_model_chi2_2d.py`
justifies `ndf = n_reported` by a rank-truncation scan whose stated condition — "effective rank is not far
below `n_reported`", measured at 204/205 — is FALSE at 49/262.** That is B's, it is credited, and it is why
§7's disposition is about `N` and not about χ².

**What this document is not.** It contains **no implementation** — no covariance code, no snippets a
builder could paste. Lane C wrote the family and the extractor and deliberately kept covariance code
out of both (`extract_fullevent_replica.py:350,412`, `validate_gate5_extraction_family.py:194,260`,
`submit_gate5_extraction_r2_n50.sh:34` all assert `C_stat: None`). C authors the spec and does not
build, so that property is not eroded by the person who installed it.

**Ids in this document are prefixed `CSTAT-`** per `CLAUDE.md`'s namespace rule. `CSTAT-R*` are
requirements the builder must satisfy. `CSTAT-D*` are declarations the spec makes so the builder does
not. `CSTAT-P*` are predeclarations binding **consumers**. `CSTAT-N*` are notes answering a question that
was asked. `CSTAT-O*` is reserved for what returns to Joseph.

> **ONE ESCALATION IS OPEN: `CSTAT-O2`** — whether this object is entitled to the name `C_stat` at all.
> It was found while writing this spec, it blocks **publishing** rather than **building**, and it is the
> only item here that needs Joseph.
>
> **`CSTAT-O1` (rank) is CLOSED and was never open** — it was dispositioned before launch by the `N=50`
> predeclaration. **If you have just derived that rank ≤ 49 against 262 cells is a problem, read §7 before
> writing anything**: you are the fifth to derive it and it is settled.

---

## 0. Provenance of every number in this document

Every quantity below was measured from the published replica artifacts on 2026-08-14, first at
**14 of 50** members (~05:00 PDT) and **re-checked at 18** (~05:40 PDT) while the extraction array
`56936015` was still mid-flight. Scripts and their verbatim stdout are committed under
[`state/gate5-cstat-spec-measurements-20260814/`](state/gate5-cstat-spec-measurements-20260814/); the
receipt is
[`state/gate5-cstat-spec-measurements-20260814.json`](state/gate5-cstat-spec-measurements-20260814.json).

**Numbers marked `[N=14]` are provisional and MUST be re-measured at 50/50 before publication.**

**What the 14 → 18 re-check bought, since "provisional" is worth nothing without a stability test.**
Unchanged: the grid (285), the union (262), the never-reported set (23 cells, same indices), the
intersection (259), and the flickering set (**the same three cells**, flat 209/254/255). Changed: the
flicker *depth* — cell 255 went from 9-of-14 to 12-of-18, so it keeps flickering rather than having been
an early transient. **Also changed, and it is a finding rather than noise:**
`n_cells_masked_zero_acceptance` widened from `{3,4}` to `{2,3,4,5,6}` — see `CSTAT-D0d`. So the
*structure* the decisions rest on held over four more members while the *per-member internals* moved,
which is the pattern `CSTAT-D3` is designed for.

---

## 1. `CSTAT-R1` — WHAT QUANTITY IS COVARIED

**The array is the `xsec` key, and nothing else in the file.**

| property | value | how known |
|---|---|---|
| file, per member | `<root>/replicas/replica_<II>/extraction/GATE5_REPLICA_XSEC.npz` | launcher `sbatch_gate5_replica_extract_array.sh` |
| `<root>` | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50` | `state/gate5-extraction-r2-active-56936015.json` |
| NPZ key | **`xsec`** | measured; `sorted(z.files)` in the receipt |
| shape | **`(15, 19)`** | measured on 14 of 14 |
| dtype | **`float64`** | measured |
| quantity | **d²σ / d`pT` d`p∥`** — a **DENSITY, not a bin-integrated yield** | `extract_fullevent_fps.py:459` |
| units | **cm² / nucleon / (GeV/c)²** | `total_xsec_2d` at `:561-565` multiplies by both bin widths to reach `cm²/nucleon` |
| schema string | `pet-fullevent-fps-gate5-replica-xsec-v1` | key `xsec_schema` |

**`CSTAT-R1a`** A builder MUST assert `xsec_schema == "pet-fullevent-fps-gate5-replica-xsec-v1"` and
refuse on mismatch. The nominal-path artifacts carry `pet-fullevent-fps-xsec-v1` — a different string
for a differently-produced object, and they are the files most likely to be picked up by a loose glob.

**`CSTAT-R1b` — the density trap, stated because it is silent.** Because `xsec` is a density, a
covariance built from it has units of cm⁴/nucleon²/(GeV/c)⁴ and is **not** the covariance of the
bin-integrated cross section. The two differ by `diag(w) C diag(w)` with `w = outer(Δpt, Δpp)` flattened.
Bin widths here span **0.07 → 25.5 GeV/c in `pT`** and **0.5 → 60 GeV/c in `p∥`**, so the two matrices
differ by more than three orders of magnitude in places. **The spec's object is the DENSITY covariance.**
A builder MUST record `width_weighting_applied: false` in its receipt so a downstream consumer cannot
mistake which one it holds.

## 2. `CSTAT-R2` — BINNING, and the flattening string

**Bin edges are read from the member file, never from `AGENTS.md`.** The source dump is the
**extended-FPS** grid, which is **not** the paper grid in `AGENTS.md:345-351`:

```
edges_pt        16 edges → 15 bins  [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
                                     0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50, 30.0]
edges_pparallel 20 edges → 19 bins  [0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                                     6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0, 120.0]
```

`AGENTS.md` documents 14×16 = 224 paper bins. **The artifacts carry 15×19 = 285.** The extra edges are
the overflow/underflow extensions (`pT` to 30.0; `p∥` 0→0.75 and 60→120). **A builder that trusts the
documented paper grid produces a 224-cell object and every element of the comparison is misaligned.**
It is stated first because it is the single most likely way to get a plausible, symmetric,
positive-semidefinite matrix of the wrong object — and with one builder there is no second implementation
whose disagreement would reveal it.

**`CSTAT-R2a`** A builder MUST verify `edges_pt` and `edges_pparallel` are **bit-identical across all
50 members** and refuse otherwise. Measured identical across 14 of 14.

**`CSTAT-R2b` — FLATTENING: pin the declared STRING, not a convention.**

```
bin_order = "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel"
```

This string is published in each member's `extraction_telemetry` and **five existing consumers already
fail closed on it** — `validate_pet_nominal_gate4.py:102,514`, `preflight_powered_closure.py:188`,
`acceptance_map_fullevent_fps.py:201`, `test_pet_nominal_gate4_validator.py:68` (located by D).
It is equivalent to NumPy C-order; verified by measurement, `F[0] == X[0].ravel(order="C")` on 14 of 14.

The builder MUST **assert the string** and MUST NOT infer order from the shape. Credit to D for the
reason, which is decisive: a C-order/F-order disagreement produces a covariance that is **symmetric,
positive-semidefinite, and wrong**, and no structural check can see it. Since `15 != 19` a transpose would
be caught by shape; the *flatten* order would not. **With one builder this is the argument for asserting
the published string rather than any convention** — the string is the only external witness left, and D's
harness asserts the string rather than the shape for the same reason.

## 3. `CSTAT-R3` — REPLICA ORDERING, and how to prove you have 50 distinct members

**Ordering is by the `replica_index` scalar INSIDE each NPZ. Never by filename, never by glob order,
never by `readdir`.**

**`CSTAT-R3a`** For each member, read `replica_index` and `bootstrap_seed` from the file and assert
`bootstrap_seed == 50000 + replica_index` — the predeclared `gate5-cstat-n50-v1` policy, independently
enforced at `extract_fullevent_replica.py:443-446` and `train_fullevent_replica.py:319-321`.

**`CSTAT-R3b`** Assert `sorted(replica_index for all members) == list(range(50))` — i.e. **exactly 50
members, each index present exactly once**. This is the check that distinguishes "50 files" from "50
distinct replicas": a doubled symlink or a re-run leaving two copies passes a count and fails this.

**`CSTAT-R3c`** Assert the row order of the assembled `(50, D)` matrix is ascending `replica_index`, and
record that assertion in the receipt. Covariance is invariant to member permutation, so this cannot
change the matrix — it exists so that any **per-member** quantity the receipt publishes (residuals,
`n_replicas_reported` contributions, outlier ids) refers to the member a reader thinks it does.

**`CSTAT-R3d`** Assert `is_complete(path)` (the `atomic_write` marker) for every member.
**Known limit, not repaired here:** `atomic_write.is_complete` compares recorded size and
`int(st_mtime)` at **whole-second** resolution, so a same-size same-second rewrite is invisible to it
(lane C residual, carried in `state/gate5-family-complete-pass-20260814.json`). A marker is the only
integrity evidence these artifacts carry — **no receipt in this campaign is hashed against anything.**

**`CSTAT-R3e` — `member_xsec_sha256` is REQUIRED, and the reason is a measured hazard, not hygiene.**
Assert the 50 members are mutually distinct by `xsec` digest, and **publish the 50 digests**. Measured
distinct on every member so far, as is `total_sigma`.

The reason `replica_ids` alone is insufficient: **ids prove which replicas the builder BELIEVES it used;
digests prove which bytes it READ.** And the two can diverge here, because **the failed r1 array
`56935552` and the live r2 array `56936015` write to the SAME output root**,
`/pscratch/.../pet/fullevent_cstat_n50`. Measured by the mediator: that directory currently holds only r2
products, because r1 died at the data-root binding **before writing any product**, so its residue is logs
only. **The contamination is therefore not realised — but a glob would have taken r1's products had any
existed, and that is luck, not design.** A digest list closes it for the cost of one `sha256sum` per
member.

**`CSTAT-R3f` — and close it at the source too: require a constant producing array.** Each member's
receipt records `execution.slurm_array_job_id`. The builder MUST read it for all 50 members, assert it is
**constant**, and publish the value. This catches a mixed-array family *directly* rather than inferring it
from digests, and it is the check that would have fired had r1 written products. Neither check subsumes the
other: digests catch a stale byte-level duplicate within one array, the array id catches a clean product
from the wrong array.

## 3.1 `CSTAT-D0` — **THE SHAPE RULING.** Emit BOTH forms and the full-grid mask.

**This was contested and the ruling is mine as spec author.** D had built for `(285, 285)`; B disputed
that and proposed `(285,285)` + a full-grid mask with the reduction happening once in assembly; the
mediator initially relayed D's concession as settled and then correctly withdrew that, because B disputed
it on independent grounds. **Ruling:**

**The builder emits BOTH representations in the one artifact, plus the full-grid boolean mask.**

| key | shape | role |
|---|---|---|
| `C_full` | `(285, 285)` | full-grid form; zero outside the mask |
| `C` | `(n_reported, n_reported)` | **the deliverable** — what `assemble_ctotal_bkgsub.py` consumes |
| `reported_mask` | `(285,)` `bool` | full-grid, C-order; the map between them |

**`CSTAT-D0a` — the check that makes this worth doing.** The builder MUST assert

```
C == C_full[np.ix_(reported_mask, reported_mask)]      BIT-IDENTICAL, not to a tolerance
```

and record the result. `np.ix_` is the canonical form (credit B); `C_full[m][:, m]` is equivalent for a
boolean mask but allocates an intermediate. **Bit-identical, not approximate, for three reasons and the
third is the one that matters:** it is a pure gather with no arithmetic, so *any* difference is a defect
rather than float noise; it needs no reference artifact, so it keeps its power even if the regression
comparison is unavailable; and it is **the only check that fires on the exact failure being guarded — a
correct full matrix reduced through a wrong index set.** A tolerance here would convert the one exact
check in the chain into an approximate one. This is the
whole reason for emitting both, and with one builder it is the shape of check that can still fail:
**the reduction is the one operation B and D independently flagged as error-prone**, because the reported
set is contiguous *only within rows* — flat runs `[0..227] + [229..246] + [254..265] + [281..284]`. Two
consumers slicing independently can silently differ. Emitting only the full form leaves the reduction
verified by nobody, so *"the comparison passed"* becomes a true statement about an object that is not the
deliverable. Emitting only the reduced form loses the fixed dimension. **Emitting both, with the
restriction asserted, closes the gap for one numpy line and ~650 KB.**

**Credit and a disclosure that raises rather than lowers its weight.** The both-forms proposal is D's. D
volunteered that its harness was already written for `(285,285)`, so it was **not neutral** on a question
whose answer is "adopt D's convention" — and then argued for the option that costs it rework, adding that
if only one form could ship it should be the **reduced** one, because *"the published object should be the
verified object."* That is the right instinct and it is adopted.

**`CSTAT-D0b` — THE PUBLISHED DOMAIN IS `C_full` ON THE FULL 285-CELL GRID, PLUS A REDUCED FORM ON THIS
FAMILY'S OWN `262`. THE FPS `266` MASK IS NOT ADOPTED.**

**This reverses an earlier draft of this section, which adopted `266` on the argument that "the authority is
the consumer, not the measurement."** The argument was right; **I had the wrong consumer.** Measured this
turn, from the tree:

1. **`assemble_ctotal_bkgsub.py` cannot consume this object at all.** It is hard-coded 5D:
   `SHAPE5 = (14, 16, 7, 7, 6)` at `:33`, every shipped component carries
   **`n_reported_bins: 10550`**, `--cstat` defaults to `pet_cstat_bkgsub_5d.npz`, and it forms a 5D→4D
   marginal. Its own shape gate (`C.shape != (nrep, nrep)` with `nrep = 10550`) would **reject** a 266×266
   matrix. Note also that its first two dimensions are `(14, 16)` — the **paper** grid — where this object
   is `(15, 19)` extended-FPS. **So the mask check I cited as authority belongs to a different chain, and
   three lanes spent the morning arguing about a mask for an assembler that will not consume it.** Whether
   the 2D P5B chain gets its own assembler is `CSTAT-O3` below and is not mine to decide.
2. **The `266` mask's central is a different estimator's.** `fps_reported_mask.json` records
   `central_cv = uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` — an **LGBM** central.
   `RUNBOOK:213` requires every P5B component to use the P5A central/mask/order **and the exact
   `pet-fullevent-fps-v1` fingerprint**. Adopting `266` would import the reporting domain of a different
   estimator into a component the runbook binds to `pet-fullevent-fps-v1`. Its lineage also runs through
   the purity-control family, whose manifests carry `publication_gate_rejects_this = true` — and
   `fps_build_control_manifest.py:202-204` *dies if the publication gate fails to reject it*, so that flag
   is an assertion about the class, not an incidental label.
3. **The authority `RUNBOOK:213` names was never produced.** `state/annealed-nominal-complete-56563761.json`
   records `scope.extraction_run = false` and `scope.cross_section_run = false`. **P5A trained; P5A never
   extracted.** A frozen central vector and reported-bin mask are *products of extraction*, so there is no
   P5A mask to conform to. The only in-tree source of "262" outside this family is a file whose own name is
   `NONQUOTABLE-DIAGNOSTIC`. Credit for this to the read-only session that established it.

**The ruling, and why the both-forms decision makes it cheap.** `C_full` on the **full 285-cell grid** is
the primary published object and is **consumer-agnostic**: any future assembler re-reduces it to whatever
common mask that assembler ratifies, using `reported_mask`, with **no translation step** — which is exactly
what `OI-121` exists to prevent. The reduced `C` ships on **this family's own measured `262`-cell union**,
because that is the only domain whose provenance is measured from these artifacts rather than inherited from
another estimator. **`n_reported = 262` for this artifact.**

**So the 262-vs-266 question is not decided here; it is made deferrable at zero cost.** That is the right
outcome for a question whose named authority does not exist yet, and it is strictly better than picking
either number now and being wrong in a way that only surfaces at assembly.

**The census on the adopted `262` domain is exact and the builder MUST reproduce it:**

```
259  reported in every member
  3  flickering  (flat 209, 254, 255)          <-- CSTAT-D3
---
262   = n_reported for this artifact
```

and on the full grid `285 = 262 reported + 23 never-reported`, the 23 listed by index in the zero-cells
receipt. Had `266` been adopted the census would read `259 + 3 + 4 = 266`; it is not.

**`CSTAT-O3` — OPEN, NOT MINE: which assembler consumes the 2D P5B `C_stat`, and what ratifies its common
mask?** `RUNBOOK:213` points at a P5A product that was never built, and the code has already picked a
substitute silently — `assemble_ctotal_bkgsub.py:104-107` uses `ref_mask = masks["C_syst"]` with a hard
`SystemExit`, while the *central-value* mismatch at `:113-115` only **warns**. So in code, whatever `C_syst`
was built on **is** the grid. **This is `OI-122`'s shape and worse: there, two documents disagree; here a
document and the code disagree and the code wins silently.** Someone must either run the P5A extraction or
**ratify a substitute authority in writing.** That is a documented supersession, not a lane's default, and
this spec does not make it. **It does not block building `C_stat`** — `C_full` is grid-complete, so the
reduction can be re-derived whenever the authority is settled.

**`CSTAT-D0e` — `n_reported` IS DECLARED FROM THE MASK, NEVER INFERRED FROM THE DIAGONAL. This is a trap the
both-forms ruling creates, and it already exists in tracked code.** `p4_validate_active_lateral_fps.py` does
exactly the wrong thing, and I read the lines rather than take them on relay:

```
:67   r["min_over_max_eig"] = float(ev[0] / max(1e-300, abs(ev[-1])))
:68   r["psd"]              = bool(ev[0] >= -1e-12 * abs(ev[-1]))
:72   r["n_reported"]       = int(np.sum(d > 0))
```

`:72` is **not** the reported-bin count. **A cell can be reported (`comp > 0`) and still carry exactly zero
replica variance** — if every draw lands on the same value, which is not far-fetched in a low-occupancy cell,
and the extended-FPS grid has catch bins precisely where occupancy is thinnest. Its diagonal is then `0.0`
and the inferred count **silently undercounts**. **The mask choice does not save you:** on the adopted 262
domain, a flickering cell whose sample variance happens to vanish makes `sum(d > 0)` read **259**; had `266`
been adopted it would read **262**, because that mask deliberately contains four identically-zero cells.

**`CSTAT-D0e(i)`** `n_reported` MUST be taken from `reported_mask.sum()` and published; it MUST NOT be derived
from `diag(C)`. **`CSTAT-D0e(ii)`** A zero on the reduced diagonal is **a fact to REPORT by index, not a cell
to drop** — dropping one would silently change the published dimension. The trap is only reachable because
both forms exist, and it is only *visible* because both forms exist, which is an argument for the ruling
rather than against it.

**And the PSD gate at `:68` cannot fail on this object either**, worth stating in the same breath since a
reader meets both: `ev[0] >= -1e-12 * |ev[-1]|` is a **negativity** test, and an exact zero satisfies it, so a
rank-49 matrix passes `psd=True` silently. The evidence needed to catch that is *already recorded two lines
above* — `min_over_max_eig` at `:67` — so what is missing is a rank threshold, not a measurement. **Out of
scope for this spec** (another lane's validator path, and `CSTAT-O1a` already forbids the builder from making
the matrix invertible), but recorded in `KNOWN_ISSUES.md` so the next reader of that file does not take
`psd=True` as evidence of full rank.

**`CSTAT-D0c`** The nesting result is retained and remains useful even though `266` is not adopted: D
committed the containment check at `b9d0803` showing **PET's 262 is a strict subset of FPS's 266**, the four
cells between them being flat `{228, 251, 252, 253}` = `(12,0), (13,4), (13,5), (13,6)`; B derived the same
four independently from the other direction; and **C confirmed it from a third artifact** — subtracting those
four from this family's 23 never-reported cells leaves exactly **19**, the zero count a 266-reported mask
must have on a 285-cell grid. Receipt:
[`state/gate5-fullevent-fps-zero-cells-20260814.json`](state/gate5-fullevent-fps-zero-cells-20260814.json).
**Why it still matters:** it means adopting `266` later would *add* four identically-zero rows and *drop
nothing*, so `CSTAT-O3` can be settled either way without rebuilding anything. Should `266` ever be adopted,
those four rows MUST be declared by index — four undeclared zero rows in a published covariance read as a
failure, and the cost of disproving that falls on whoever inherits it. Mechanism: PET truth mass with **zero
reco acceptance**.

**`CSTAT-D0d` — a correction to how those four have been justified.** The four have been cross-referenced to
PET telemetry's `n_cells_masked_zero_acceptance = 4`, described as the count and the mechanism agreeing from
two artifacts that did not know about each other. **The nesting stands — it is confirmed three ways above and
does not depend on this — but the agreement is narrower than that phrasing.** Measured over the 18 published
members, `n_cells_masked_zero_acceptance` takes the values **{2, 3, 4, 5, 6}**. It is a **per-replica draw**,
because the completeness mask is computed with the replica's signal Poisson factor applied
(`extract_fullevent_replica.py:190-196`) — `BEN-231`'s mechanism surfacing in a second telemetry field. **`4`
is a property of the NOMINAL extraction, a single artifact; against the replica family the matching quantity
is a distribution, not a number.** Safe for the nesting; **not to be carried into a technote as family-level
agreement**, because a reader who then measures the family will find 2–6 and conclude the record overstated
its evidence.

## 4. `CSTAT-D1` — CENTRING: **the replica mean. Decided, not deferred.**

**The estimator is centred on the sample mean of the 50 replicas.**

**Reason minus-one, found last and outranking everything below: `RUNBOOK:213` PREDECLARES it.** The
publication runbook's Packet P5B, item 1 (F7 `C_stat`) says, in the same breath as the inventory rule:
**"Center on the replica mean."** So centring is not a spec author's choice at all — it is a locked
estimator decision, predeclared before this family existed, and this section merely records that C reached
the same answer independently and then found the instruction.

**Reason zero: it is also the adopted convention in code.** `combine_cstat_bkgsub.py:57-58`, the Phase-4 builder for the 5D bkgsub `C_stat` that the
analysis already uses, does exactly this:

```
Z = Xr - Xr.mean(0)                                  # replica-mean-centered
C = (Z.T @ Z) / (Xr.shape[0] - 1)
```

Replica-mean-centred, `1/(N-1)`. So `CSTAT-D1` and `CSTAT-D2` are **not new decisions** — they match the
estimator already in production, which means the builders' output composes with the existing chain
**without a convention translation step**, and translation steps are where sign and ordering errors live.
A reviewer should check this file rather than take the spec's word for it.

Two further reasons, independently reached before that precedent was found:

1. **Measured consequence.** Centring on the only 285-cell nominal-like artifact that exists inflates
   the trace by **6.0×** `[N=14]`:

   | | trace |
   |---|---|
   | mean-centred, 1/(N−1) | `1.848970e-76` |
   | nominal-centred, 1/(N−1) | `1.111802e-75` |
   | ratio | **6.013×** |

   The excess is **exactly** the offset term `N/(N-1)·‖mean − nominal‖²` = `9.269051e-76`, which equals
   `trace_nom − trace_mean` to all printed digits. That offset is a **bias**, not a statistical
   fluctuation: the replica mean sits **+7.56%** above that nominal in total cross section. Calling it
   variance would put a systematic shift inside the statistical component.

2. **The nominal alternative does not exist in quotable form.** The only 285-cell nominal artifact on
   disk is
   `nd-unfolding/pet/fullevent_diagnostic_nonquotable/NONQUOTABLE-DIAGNOSTIC.xsec.slurm-56527676.npz`
   — schema `pet-fullevent-fps-xsec-v1`, and **its own filename declares it non-quotable**. There is no
   Gate-5-schema nominal extraction. So nominal-centring is not a methodological option that was
   weighed and rejected; **it is unavailable from quotable evidence.**

**`CSTAT-D1a`** A builder MUST NOT read that non-quotable file. It is named here so that a builder who
finds it by glob knows to refuse, which is the opposite of the usual reason for naming a path.

**`CSTAT-D1b`** Centring on a point other than the sample mean would raise the rank ceiling from
`N−1` to `N` (measured: 13 → 14 at `[N=14]`), and **the extra direction is the bias direction.** Anyone
tempted to prefer nominal-centring for the extra rank is buying a rank whose content is the offset in
`CSTAT-O2`. Stated so the temptation is refused in writing rather than in review.

## 5. `CSTAT-D2` — NORMALIZATION: **1/(N−1). `ddof=1`.**

Unbiased for a covariance about an **estimated** mean, which is what `CSTAT-D1` makes this. `1/N` would
bias every element low by a factor `49/50` = **2.0%** — small, systematic, in the same direction for
every element, and therefore exactly the kind of error that survives an element-wise comparison of two
builders who both chose `1/N`. Declared here so neither has to choose.

## 6. `CSTAT-D3` — THE REPORTING DOMAIN, and the replica-dependent mask

**The reporting mask is drawn per replica. This is measured, not hypothetical.**

Mechanism, found by D: `extract_fullevent_replica.py:190-196` monkey-patches `completeness_2d` so the
replica's **signal Poisson factor multiplies the weights inside the completeness computation**;
`extract_fullevent_fps.py:517-518` then hard-zeroes unreported cells
(`reported = comp > 0; xsec = np.where(reported, xsec, 0.0)`). So `comp > 0` is a **per-replica draw**,
and a thinly-populated cell can be reported in one member and hard zero in another.

**Lane C measured the occurrence on the 14 published members. It occurs:**

| `n_replicas_reported` (of 14) | cells |
|---|---|
| 14 (all) | **259** |
| 13 | 2 |
| **9** | **1** |
| 0 (never) | 23 |

`n_cells_populated` in the telemetry varies **260 / 261 / 262** across members, so the artifacts already
record the flicker. **One cell is reported in only 9 of 14 draws** — in that cell, roughly a third of
the across-replica spread is the mask switching off, i.e. hard zeros, **not fluctuation of the cross
section.**

D's point stood exactly as put when there were two builders: both, given identical member vectors, would
compute the identical wrong variance there and agree with each other perfectly. **Element-wise agreement
has no power over a defect in the input that both implementations faithfully consume.** **And there is now
ONE builder, so the agreement check is gone entirely** — this hazard is no longer merely invisible to the
campaign's main defence, it is upstream of every defence that remains. **The declaration below is the only
protection**, which is why `CSTAT-D3b` and `CSTAT-D3d` are requirements rather than recommendations.

**The declaration:**

- **`CSTAT-D3a` — THE RULE IS UNION, NOT INTERSECTION**, on the `262` domain of `CSTAT-D0b`. The union —
  every cell reported in **≥ 1** member — is used because **the intersection silently deletes cells and its
  deletion set depends on `N`**, so the published dimension would drift with the member count, which is
  indefensible in a technote: it would drop 3 cells at `N=18` and an unknown number at `N=50`, so the same
  analysis would report a different dimension for no physical reason. **Union keeps the dimension a
  property of the grid and pushes the difference into a per-cell caveat, which is where it can be read.**
  The 3 flickering cells are inside the 262 and are flagged, not removed — `CSTAT-D3c`.
- **`CSTAT-D3b` — PUBLISH per-cell `n_replicas_reported`**, an integer array of length `D`, in the
  output contract. Cheap now, expensive to retrofit; without it nobody downstream can distinguish a
  genuinely quiet cell from a flickering one. D asked for this and it is adopted verbatim.
- **`CSTAT-D3c` — the QUOTABLE sub-block is `n_replicas_reported == 50`.** Cells with
  `n_replicas_reported < 50` are **present in the published matrix, flagged, and excluded from any
  downstream inversion or χ², with their cell list recorded by index.** They are not deleted, because
  deleting them would hide that the question was ever asked.
- **`CSTAT-D3d` — the answer is recorded either way.** The receipt MUST publish the flicker cell count
  **even when it is zero**, as an explicit `0` with the union and intersection sizes alongside. A zero
  result must not let the question disappear — the whole point of `CSTAT-D3` is that the *absence* of
  flicker at 50 members would itself be a finding, and an omitted field cannot state it.

**`CSTAT-D3e`** The 23 never-reported cells (`n_cells_no_denominator = 23`, matching exactly) carry
**identically zero variance** and are structurally singular directions. They are retained in the
published `D`-dimensional object for grid alignment and flagged; they are not evidence of precision.

**`CSTAT-D3f` — why the adopted chain does not have this problem, and this one does.** The production 5D
builder masks on the **central value**, not per replica — `combine_cstat_bkgsub.py:56`, `rep = cv > 0` —
which is a **replica-independent** domain and therefore immune to flicker by construction. That is the
better design and it is not available here: the equivalent choice would mask on the nominal extraction,
and per `CSTAT-D1` **the only 285-cell nominal artifact is explicitly non-quotable.** So the flicker in
`BEN-231` is downstream of the same absence that forced `CSTAT-D1`'s centring decision — one missing
quotable nominal, two consequences. Worth recording because it means **producing a quotable nominal
full-event extraction would retire `BEN-231` outright**, rather than managing it with `D3a`–`D3d`. That is
a producer-side fix and is not in this spec's scope.

**Out of scope and explicitly untouched:** the acceptance-supported vs model-dependent **tiering**
decision of `OPEN_ITEMS:430-438`. The extractor's own telemetry says
`reporting_mask_is_not_the_tiering_decision`. This spec inherits the reporting mask and decides
nothing about tiering.

## 7. `CSTAT-O1` — RANK. **NOT OPEN. Dispositioned before launch. This section exists to stop it being re-opened a fourth time.**

**Rank was settled on 2026-08-12, before the replica code path existed**, in
[`PREDECLARATION-20260813-gate5-coherent-replicas-n50.md`](PREDECLARATION-20260813-gate5-coherent-replicas-n50.md)
(committed `6bd3707`, 2026-08-12 23:29), verbatim:

> *"Rank is not the criterion — 1431 bins is unreachable at any affordable `N`, and the rank-deficient
> GoF treatment is already disclosed under `OI-29`. The criterion is **precision on a subdominant
> component**: `1/√(2(N−1))`, giving 10.1% at `N=50` … `N=100` buys 7.1% for double the compute, on a
> term that is not driving the total."*

Joseph's decision in that document, verbatim: **"sounds good, get N=50 up and running."**

**So there is nothing to escalate, and I withdraw the escalation this section previously carried.** The
criterion for `N` was never rank; it was precision on a component measured at **0.669%/bin against
`C_syst`'s 7.27%**. The rank-deficient GoF treatment is disclosed under `OI-29` and awaits
*collaboration endorsement*, not a fresh decision.

**This is the fourth approach to the same already-closed question.** `OI-122` records two agents
re-opening it on 2026-08-14 and escalating as novel; `OI-91` was mine and is now **closed by reference**,
exactly as its narrowed form said it would be if `OI-29`'s treatment extended. It does. **The pattern is
worth naming, because the cost is Joseph's attention:** the rank deficit is *arithmetically obvious* from
`N=50` and any bin count, so every agent that computes it discovers it, and a live predeclaration that
settled it is not where anyone looks. If you have just derived that rank ≤ 49 is a problem — **read the
predeclaration before writing anything.**

**RETRACTED — DO NOT CITE FIELD NORMALITY. An earlier version of this section carried external precedent
that does not survive verification.**

That paragraph reported, from delegate research (Gemini 3.1 Pro) and **explicitly labelled UNVERIFIED**,
that rank-deficient multisim covariances are *"normal, unavoidable practice"*, that MINERvA uses ~100 PPFX
flux and ~50 detector universes, and that the convention is *"released as calculated, regularisation is the
consumer's job."* **Checked against the actual papers, all three are NOT SUPPORTED:**

- The MINERvA Analysis Toolkit paper (`arXiv:2103.08677` — real, correctly identified) contains **zero**
  occurrences of `rank`, `singular`, `invert`, `regulari`, `degenerat`, or `condition number`. **The topic
  is absent, not merely unemphasised** — and the research **converted that absence into positive evidence
  that rank deficiency is accepted.** *Silence is not endorsement.* That inversion is the reason this
  paragraph is retracted rather than softened.
- No checked source states any release or regularisation policy.
- MAT gives **no universe count** anywhere; it says only "a large number of universes", qualitatively.
- One citation was **the wrong paper entirely**: `arXiv:1507.08560`, offered as MINERvA flux PCA, is
  Ankowski et al. on calorimetric vs kinematic energy reconstruction — no PCA, no flux covariance, no
  MINERvA.

**What survives is much less, and supports only that MINERvA publishes 2D differential cross sections** —
`1511.05944` (PRL 116 071802), `2110.13372` (PRD 106 032001, double-differential in available energy and
`|q|`, i.e. our observable), `2312.16631` (PRD 109 092008, double-differential in `E_avail` and `p_T`).
**None says anything about covariance rank.**

**None of this reopens the rank question**, which is closed on our own predeclaration — *"Rank is not the
criterion"* — and never depended on external precedent. What it removes is the *reassurance* that everyone
else does this too. **This spec therefore asserts no field-normality claim**, and a technote drawing on it
must not either. A measurement is under way that would settle it honestly: download a released MINERvA
covariance and measure its rank against its bin count. If it comes back rank-deficient with no remark in
the paper, the claim becomes a measurement instead of an assertion; if it comes back full rank, that
refutes it and we need to know.

**What remains true and is worth keeping is the measurement**, which was not known before 2026-08-14:

| domain | `D` | rank ceiling at `N=50` | singular by |
|---|---|---|---|
| full grid | 285 | 49 | 5.82× |
| union / reported (`CSTAT-D3a`) | **262** | **49** | **5.35×** |
| intersection | 259 | 49 | 5.29× |
| nominal's reported count | 262 | — | — |

The rank deficit was raised against 285; the mediator correctly asked for the count against the
**reported** dimension, since that is the number that decides whether it is a problem. **Lane C has now
measured it and it does not change the answer: 262 ≫ 49.** The matrix is singular against every
candidate domain, by a factor above five. `[N=14]`, `numpy.linalg.matrix_rank` on the 14-member
mean-centred matrix returns exactly `13 = N−1`, confirming the ceiling binds tightly and is not slack.

**`CSTAT-O1a` — the builder's obligation is unchanged by the disposition.** A builder MUST produce the
singular matrix as specified, MUST NOT regularize, condition, pseudo-invert, shrink, diagonal-load, or
clip negative eigenvalues, and MUST record `rank_treatment: "UNDECLARED — see CSTAT-O1"` in its receipt.
Per the precedent above this is also the field convention: **release as calculated, regularise at
consumption.** A builder that returns an invertible matrix has silently made a consumer's decision.

## 7b. `CSTAT-P1` — PREDECLARATION: the Hartlap bias, if anything downstream ever inverts a truncated `C_stat`

**Predeclared now, before any number exists, so it cannot be chosen after seeing a fit.**

Stable inversion of a sample covariance wants `N ≫ p`. For `N > p+2` the inverse of a sample covariance is
biased, and the standard correction factor is `(N − p − 2)/(N − 1)` — **Hartlap, Simon & Schneider 2007,
A&A 464, 399.** This citation **is** real and correctly referenced, unlike the retracted precedent in §7.
*Caveat carried forward honestly: the debiasing factor's algebraic form was read in secondary sources
because the journal page returned 403; the singularity proof and the `P < N` condition are verbatim from
the abstract.*

> **WARNING — WHAT THIS PAPER IS, AND WHAT IT IS NOT.** Its abstract's final sentence gives *"an analytic
> proof for the fact that the estimated covariance matrix is singular if `P > N`."* **Hartlap is the
> canonical citation for why you CANNOT invert a covariance with more bins than realizations — it is not a
> licence to ship one.** At our numbers `(50 − 262 − 2)/(50 − 1) = −4.37`: a **negative** debiasing factor,
> so the formula does not degrade gracefully, it becomes **meaningless**. **If Hartlap is ever cited in a
> technote as support for publishing a rank-deficient `C_stat`, a referee will find it immediately and it
> will damage the section it was meant to defend.** Cite it for the bias correction in a truncated subspace
> where `p_effective < N`, which is the only thing `CSTAT-P1a` uses it for, and nowhere else.

At `N = 50`, `p = 262` the factor is negative, which is the singularity restated: no inverse exists and no
correction rescues one. That much we already knew.

**The part this campaign did not have:** if any downstream step works in a **truncated subspace** where
`p_effective < N` — a rebinning, a projection, a leading-eigenvector subspace, anything that makes the
matrix invertible — then **the precision matrix in that subspace is still biased by the finite `N = 50`**,
and the bias makes χ² too *small*, i.e. it flatters the fit. A truncation chosen to make inversion
possible therefore silently introduces a bias in the optimistic direction.

**`CSTAT-P1a`** Any downstream consumer that inverts a truncated `C_stat` MUST state `p_effective`, `N`,
and whether a Hartlap-style correction was applied — and if not, why not. **Out of scope for both
builders:** no builder truncates, inverts, or corrects anything (§11). This clause binds consumers, and
is recorded here because the spec is where the object's properties are written down.

## 7c. `CSTAT-P2` — PREDECLARATION: Peelle's Pertinent Puzzle

Highly correlated covariances that carry a **normalisation** component are known to make generalised
least-squares fits pathologically suppress normalisation toward unphysically low values — Peelle's
Pertinent Puzzle. **The FPS chain carries a `+ norm 1.4%` component**, so the precondition is present,
not hypothetical.

**`CSTAT-P2a`** Predeclared position: **a GLS fit against `C_stat` (or any total containing it) that
returns a normalisation pulled low is to be treated as a suspected PPP artifact and diagnosed, not
adopted.** The diagnostic is to refit with the normalisation component removed from the covariance and
compare; a large shift indicates PPP rather than data. Predeclaring this matters because the pathology
produces a *better-looking* χ² alongside a wrong normalisation, so nothing in the fit output flags it.

**Neither `CSTAT-P1` nor `CSTAT-P2` blocks anything in this spec.** Both are positions taken before a
number exists, which is the only time they can be taken honestly.

## 7d. `CSTAT-N1` — NOTE: there is **no** separate diagonal data-statistical term in the PET chain

Asked by the mediator, and it is the sharpest question anyone put to this spec: the reported field rescue
for a rank-deficient systematic covariance is *"add the full-rank diagonal data-statistical term, which
makes the total invertible"* — in that convention the **statistical** term is what restores rank. **Ours
cannot, because ours is itself built from replicas and is rank-49.**

**Answered from the source rather than by inference.** `assemble_ctotal_bkgsub.py:4`:

```
C_total = C_syst + C_stat + C_ml + C_retrain (+ C_lateral when available)
```

**There is no diagonal term anywhere in that sum**, and `C_stat` is the replica-built object
(`combine_cstat_bkgsub.py:57-58`). So the answer is **no** — the PET chain has no separate diagonal
data-statistical term distinct from the replica `C_stat`, and this chain does **not** use the reported
convention.

**What supplies the total's rank instead is subadditivity over independent low-rank blocks** —
`rank(A+B) ≤ rank(A) + rank(B)`, with equality generic when the column spaces are independent. Four
components each of rank a few tens sum to a few hundred without any full-rank addend, which is a
sufficient explanation for lane B's measured 222/266 and requires no diagonal term to exist. **The
practical consequence is that the total's rank is a BUDGET**: it is bounded by the sum of the component
ranks, so it degrades if any component's replicate/universe count is reduced. That is exactly the
direction of B's independent concern from the other side — a 124-endpoint PET `C_syst` should carry lower
rank than the GBDT's 144 — and the two readings agree.

**Not measured, and the reason is recorded rather than the omission.** Measuring the per-component ranks
would confirm the budget arithmetic directly. I started it and **killed it**: `numpy.linalg.matrix_rank`
over the 5D component matrices accumulated **76 minutes of CPU in 5 minutes of wall time** on a **shared
login node**, which is antisocial and was my error in launching it there. It also belongs to lane B — B
owns the assembly and already has the 222/266 number on the 266-cell lgbm mask, which is **not** this
spec's 262-cell full-event domain, so the two are not directly comparable and reconciling them is B's
call, not a `C_stat` spec's. **Nothing in this spec depends on the answer.**

## 8. `CSTAT-O2` — **IS THIS OBJECT ENTITLED TO THE NAME `C_stat`? OPEN. Returns to Joseph.**

**This was found while writing this spec, it is not in anyone's dispatch, and C considers it more
serious than `CSTAT-O1`.**

The across-replica spread of the extracted cross section is **~90× larger than counting statistics can
account for**:

| quantity | value |
|---|---|
| relative sd of `total_sigma` across members `[N=14]` | **4.478 %** |
| (max − min) / mean `[N=14]` | 18.187 % |
| median abs deviation / mean `[N=14]` | 1.676 % |
| Poisson expectation, `n_data = 4,116,128` | **0.0493 %** |
| Poisson expectation, `n_sig = 49,152,885` | 0.0143 % |
| per-cell relative sd, median / max `[N=14]` | 0.151 / 0.794 |

A counting-only spread on an integrated quantity over 4.1M data events is **~0.05%**. The measured
spread is **4.5%**. The distribution is heavy-tailed rather than uniformly wide — median deviation
1.68% with `replica_08` at **+9.96%** and `replica_09` at **−8.23%** — which is itself a shape that
counting statistics does not produce.

**And the network is not seeded.** `grep` for `set_seed` across `nd-unfolding/` and `omnifold_nn/`
returns **nothing**; no `tf.random.set_seed`, no `np.random.seed`, no `TF_DETERMINISTIC_OPS` in
`train_fullevent_replica.py` or the extractor. The `bootstrap_seed` plumbing that *is* present
(`:150-173`, `:315-321`) governs the **draw and its provenance validation**, not weight
initialization, batch shuffling, or GPU reduction order.

**Consequence:** each member differs from every other in **two** ways at once — its Poisson draw *and*
its free-running training stochasticity. The published matrix is therefore
**`C_stat` + `C_train` + cross terms**, and **the two are not separable from this family**, because no
two members share a draw and no member was repeated under a different initialization. Naming that
matrix `C_stat` asserts a decomposition the family cannot support. This repo has a name for the shape —
`BEN-149`, a field named for one thing carrying another.

C is **not** claiming which term dominates, and will not: an alternative explanation is genuine
amplification of the data fluctuation by the iterative unfolding, which would be legitimately
statistical and would itself be a significant result. **Both readings are consistent with every number
above, and distinguishing them is one measurement, not an argument:**

**`CSTAT-O2a` — the discriminating test.** Re-**train** one replica index twice at the **same**
`bootstrap_seed`, then extract both. Extraction is deterministic given weights, so a repeat of
extraction alone measures nothing — **the repeat must be of training.** Non-zero spread between that
pair is `C_train` with the draw held fixed, measured directly and at the cost of a couple of
14-minute tasks. A small pair (3–5 same-seed retrains) bounds `C_train` well enough to state what
fraction of the published matrix is not statistical.

**This does not block writing the builders** — the construction is identical whatever the matrix turns
out to be entitled to be called. **It blocks publishing the number under the name `C_stat`,** and it
should be settled before the technote quotes it.

## 9. `CSTAT-R4` — OUTPUT CONTRACT

One NPZ, written with `atomic_write.atomic_savez_compressed(..., overwrite=False, fsync=True,
mark=True)`, plus one JSON receipt published **last**. Builders write to **separate** paths so the
comparison has two independent objects:

```
<root>/cstat/BUILDER_<B1|B2>/GATE5_CSTAT.npz        + .done marker
<root>/cstat/BUILDER_<B1|B2>/GATE5_CSTAT_RECEIPT.json
```

| key | dtype | shape | meaning |
|---|---|---|---|
| `cstat_schema` | str | scalar | **`pet-fullevent-fps-gate5-cstat-v1`** |
| `C` | float64 | `(n_reported, n_reported)` | **the deliverable**, density units (`CSTAT-R1b`) |
| `C_full` | float64 | `(285, 285)` | full-grid form, zero outside the mask (`CSTAT-D0`) |
| `reported_mask` | bool | `(285,)` | full-grid, C-order; the map between the two (`CSTAT-D0b`) |
| `n_reported` | int64 | scalar | `= reported_mask.sum() = 262`; **from the mask, never from `diag`** (`CSTAT-D0e`) |
| `layout_fingerprint` | str | scalar | sha256 over edges, `n_pt`, `n_pparallel`, `n_cells`, `ravel_order` (`CSTAT-R6`) |
| `dof` | int64 | scalar | `= n_members − 1 = 49` (`CSTAT-R6`) |
| `centering` | str | scalar | `"replica_mean"` (`CSTAT-R6`) |
| `ravel_order` | str | scalar | `"C"` (`CSTAT-R6`) |
| `max_abs_asymmetry` | float64 | scalar | `max\|C − Cᵀ\|`, **REQUIRED**, measured before any symmetrising — which is forbidden (`CSTAT-R4a`) |
| `reduction_is_exact` | bool | scalar | the `CSTAT-D0a` bit-identity result |
| `zero_variance_cells` | int64 | `(k,)` | reduced-diagonal zeros, by index — reported, not dropped (`CSTAT-D0e(ii)`) |
| `slurm_array_job_id` | str | scalar | constant across all 50 members (`CSTAT-R3f`) |
| `mean` | float64 | `(D,)` | the centring vector actually used |
| `n_members` | int64 | scalar | **must be 50** |
| `D` | int64 | scalar | cells in the constructed domain |
| `cell_index` | int64 | `(D,)` | flat cell ids into the 285-cell grid, `CSTAT-R2b` order |
| `n_replicas_reported` | int64 | `(D,)` | per-cell, `CSTAT-D3b` |
| `quotable_mask` | bool | `(D,)` | `n_replicas_reported == 50`, `CSTAT-D3c` |
| `replica_index` | int64 | `(50,)` | ascending, `CSTAT-R3c` |
| `bootstrap_seed` | int64 | `(50,)` | row-aligned to `replica_index` |
| `edges_pt`, `edges_pparallel` | float64 | `(16,)`, `(20,)` | copied from the members |
| `bin_order` | str | scalar | the pinned string, `CSTAT-R2b` |
| `member_xsec_sha256` | str | `(50,)` | per-member `xsec` digest, row-aligned |
| `centring` | str | scalar | `"replica_mean"` |
| `normalization` | str | scalar | `"1/(N-1)"` |
| `width_weighting_applied` | bool | scalar | `false`, `CSTAT-R1b` |
| `rank_treatment` | str | scalar | `"UNDECLARED — see CSTAT-O1"` |

**`CSTAT-R4a` — symmetry, and `max_abs_asymmetry` is a REQUIRED FIELD, not a note.** `C` MUST be
symmetric **by construction**, and the builder MUST NOT symmetrise. `(F−mean).T @ (F−mean)` is symmetric
up to floating-point summation order; **a builder that symmetrises destroys the only evidence that its two
triangles ever agreed**, and a symmetry check after symmetrisation passes by construction on every
artifact forever — the vacuous-check family this campaign has four findings on.

**`max_abs_asymmetry` is therefore a required key in the NPZ and a required receipt field**, and it is the
informative quantity: **`1e-9` is a real plumbing defect where `1e-16` is rounding**, and after
symmetrisation the two are indistinguishable because both read exactly zero.

*Provenance note, because it matters that this requirement was not adopted from a misreading.* This
strengthening was relayed to me as a correction to a rule reading *"symmetrise explicitly and record the
asymmetry you symmetrised away."* **This spec never contained that rule** — its first draft already
forbade symmetrisation and already required `max|C − C.T|` as a number, so the relayed text was describing
a different document, most likely D's proposed contract. **The strengthening is adopted anyway** because
promoting the quantity from *reported* to *required and named* is a real improvement over "report it",
which is satisfiable by a log line nobody reads. The misattribution is recorded rather than quietly
corrected, since a spec that accepts changes to rules it does not contain has stopped being the authority
it claims to be.

**`CSTAT-R4b`** All entries finite. `diag(C) >= 0`. Eigenvalues computed and reported; the smallest
will be zero or numerically negative and **that is expected** (`CSTAT-O1`) — report it, do not clip it.

**`CSTAT-R4c`** No overwrite, no clobber, marker written last, receipt published last.

## 9b. `CSTAT-R6` — CONVENTIONS RATIFIED FROM B'S REQUIREMENTS DOCUMENT, in C's own voice

B's `REQUIREMENTS-20260814-cstat-assembly-conventions.md` was written as **input** to this spec (see the
header). The following are **adopted as C's requirements**, so that no one has to treat the builder's own
document as its own authority:

- **`layout_fingerprint`** — a sha256 over the exact edges, `n_pt`, `n_pparallel`, `n_cells` and
  `ravel_order`, per `fps_provenance.py:153-162`. **REQUIRED.** This is the mechanism that makes a silent
  reshape impossible, and it is the single highest-value field in the contract: every other check in this
  spec assumes the grid is what it says it is, and this is the one that proves it. A consumer compares one
  hex string instead of re-deriving twenty numbers.
- **`dof`** — integer, `= n_members − 1 = 49`. **REQUIRED**, so the rank bound is *stated* rather than
  inferred by a reader who might infer it wrongly.
- **`centering`** — the string `"replica_mean"`. **REQUIRED.** Pairs with `CSTAT-D1`.
- **`ravel_order`** — `"C"`, alongside the `bin_order` string of `CSTAT-R2b`. **REQUIRED.**
- **`reported_mask`** — `bool`, **full-grid length**, C-order. **REQUIRED**, and it must be the full-grid
  mask rather than a compressed index list, because `assemble_ctotal_bkgsub.py:106` compares masks with
  `np.array_equal`.

**Where this spec and B's document disagree, this spec governs, and there is one such place:** B's document
resolves the shape question in favour of `(n_reported, n_reported)` alone; **§3.1 requires BOTH forms plus
the mask**, with the reduction asserted. B's conclusion is adopted for *which object is the deliverable*
and extended for *what else must ship beside it*.

## 10. `CSTAT-R5` — RECEIPT INGREDIENTS

Per [`CONVENTION-receipt-ingredients.md`](CONVENTION-receipt-ingredients.md) (BEN-077): **every derived
quantity ships its ingredients, enough that the reported numbers can contradict each other.** A
verdict-only receipt is unfalsifiable. Required, at minimum:

1. **Inputs:** all 50 member paths, their `xsec` sha256, their `replica_index`/`bootstrap_seed`, and the
   `is_complete` result per member.
2. **The centring vector** `mean`, and separately `total_sigma` **per member** — so a reader can
   recompute the mean and the sd independently of `C`.
3. **`trace(C)`, and `diag(C)` in full.** `trace` must be re-derivable from `diag`.
4. **The offset term** `‖mean − x‖²·N/(N−1)` against any comparison point the receipt mentions, so the
   `CSTAT-D1` decision stays auditable rather than becoming a claim. Its exact identity
   (`trace_alt − trace_mean`) is the check.
5. **`n_replicas_reported`** with union size, intersection size, flicker count (**even if 0**), and the
   flickering cell ids.
6. **Rank:** `numpy.linalg.matrix_rank(C)`, the full eigenvalue spectrum, and `D`. `rank <= 49` must be
   stated as an expectation that was checked, not discovered.
7. **Code identity:** sha256 of the builder script, and of every module it imports from this repo.
8. **`max|C − C.T|`** as a measured number.
9. **The three code digests of the producing extraction**, copied from the member receipts:
   `replica_extractor_sha256`, `gate4_pinned_nominal_extractor_sha256`, `loader_sha256`.

**`CSTAT-R5a` — source identity.** Cite `state/gate5-source-npz-verified-20260813.json` and the
recomputed `fa6b3463…` in `state/gate5-family-complete-pass-20260814.json`. **Do NOT quote
`inputs_sha256` out of a replica artifact as verified provenance** — `train_fullevent_replica.py:112`
copies a claim into a field named for a measurement (`BEN-149`, `OI-57`/`OI-58`), and that line is
**deliberately unrepaired**, riding the next launch with a CODE_ROOT sync.

**`CSTAT-R5b`** `artifact.completion_marker_valid` in the member receipts is a **hardcoded producer
literal** (lane C's `OI-66`) and MUST NOT be read as evidence. Call `is_complete` yourself.

## 11. Out of scope — named explicitly

A builder that does any of these has exceeded the spec:

1. **No inversion, pseudo-inversion, regularization, shrinkage, diagonal loading, conditioning, or
   negative-eigenvalue clipping.** `CSTAT-O1a`.
1b. **No symmetrising** (`CSTAT-R4a`) and **no truncation to a subspace** (`CSTAT-P1a` binds consumers, not
   the builder). Both would destroy a required measurement: symmetrising erases `max_abs_asymmetry`,
   truncating erases the rank the receipt must state.
2. **No χ², GoF, p-value, or fit.** This deliverable is a covariance and its receipt.
3. **No `C_syst`, no other uncertainty component, no combination with any.** `C_stat` alone, one of five.
4. **No tiering decision** (`OPEN_ITEMS:430-438`). §6.
5. **No rebinning, no projection to the 224-cell paper grid, no width-weighting.** `CSTAT-R1b`, `CSTAT-R2`.
6. **No promotion, no Gate-5 sign-off, no ledger promotion, no `VALIDATION_LEDGER` entry.** Construction
   is not promotion; `FAMILY_COMPLETE_PASS` was the completeness gate and this is the next separate step.
7. **Do not touch `/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059`.** It is `GATE5_CODE_ROOT`, it
   is **named for a different, already-complete job**, and it therefore looks disposable and is not.
   No clean, no pull, no write, no `git` operation inside it.
8. **No repair of `train_fullevent_replica.py:112`**, and no re-use of the withdrawn
   "it would break `GATE5_EXPECTED_TRAIN_DRIVER_SHA`" reason — the pin floats by design.
9. **No `scancel`, `scontrol update`, or resubmission** of `56936015` / `56936016`.
10. **Do not construct anything from a partial family.** `CSTAT-R3b` — exactly 50, each index once.
    The extraction array was at 14/50 when this spec was written; **the spec is written during the wait
    precisely so that no one is tempted to start early.**

## 12. Preconditions before either builder starts

| # | precondition | state 2026-08-14 ~05:00 PDT |
|---|---|---|
| 1 | extraction array `56936015` terminal at 50/50 | **NOT MET** — 18 published at ~05:40 PDT, 1 running |
| 2 | family validator `56936016` reports `GATE5_EXTRACTION_FAMILY_COMPLETE_PASS`, exactly 50/50 | **NOT MET** — PENDING on `afterany:56936015` |
| 3 | `[N=14]` numbers re-measured at 50/50 | **NOT MET** — structure stable over 14 → 18 (§0) |
| 4 | ~~`CSTAT-O1` rank treatment~~ | **CLOSED, never open** — dispositioned pre-launch (§7) |
| 5 | `CSTAT-O2` naming settled, or `CSTAT-O2a` run | **OPEN** — blocks publication, not build |
| 6 | ~~common mask confirmed against `C_syst`~~ | **WITHDRAWN** — the assembler that check belongs to is 5D and cannot consume this object (`CSTAT-D0b`). Superseded by `CSTAT-O3`, which blocks assembly, not this build. |

Preconditions 1–3 gate **construction**. 4–5 gate **publication**. Builders may be written and their
harnesses tested against fixtures while 1–3 are outstanding; nothing may be constructed from the
partial family.
