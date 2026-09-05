# PREDECLARATION 2026-09-05 — the cause-7-only successor Y: artifact identities, replacement
# algebra, required magnitude measurements, and the limits of its result

**CITABLE FOR:** the Y specification permitted by `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`
(sha256 `0836139b1c9a057c194a81a94d45c9f979209a9ac293d4bc8434e6b43fc1a064`) `R2`, and for §6's limits.
**NOT CITABLE FOR:** any construction, any authorization to construct, any grade on any leg, any
discharge, any adoption, any count, any gate movement, any spend, or any publication claim.

**Status: SPECIFICATION ONLY.** `R2(iv)`: *"Constructing Y requires its own committed authorization."*
No such authorization exists at this record's base. **All four legs `C`, `P`, `M`, `T` are OPEN and are
not graded here.** Gate 2 remains FAIL; counts hold at CAND `1 of 7`, QUOTED `0 of 7`.

This document exercises exactly the drafting `R2` authorizes — *"naming Y and drafting its producing
path, receipt schema and test contract"* — against `PREDECLARE-20260901-cause7-discharge-criteria.md`
§1's `C`/`P`/`T` criteria and, for `M`, that document's §1 `M` **as closed by `R3`**. It is the
successor pre-execution declaration `R2` says *"returns … when they do"*.

## 0. What Y is, in one paragraph, so it is not read as something larger

Y is **one matrix on G's grid whose only difference from G is the lateral block**. It is a **grading
subject for cause 7 and no other cause** (`R2(i)`). It is **not** a covariance candidate, **not** a
total-covariance candidate, **not** an adoption subject, and **not** a replacement for G — G is
`RETAINED` unchanged under `R1` and remains causes 1–6's grading subject and Y's digest-bound parent.
`(cause 7, G)` is **permanently OPEN** and Y cannot change that. Anything in this file that reads as a
step toward adoption is being misread; §6 states the limits without hedging.

## 1. Artifact identities — every name bound, no definite descriptions

A definite description ("the corrected lateral file") re-points the moment a second file satisfies it.
Every row below is a path plus, where the bytes exist today, a digest.

| name | identity | role for Y | measured at |
|---|---|---|---|
| **G** | `nd-unfolding/uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root`, sha256 `4f168e83eaeb4bc7191a4e13e219c7ff06556e5ad30b9df4fcc249e6720c7ec2`, job `56720356`, **10,694** reported bins on the **65,856**-bin grid (`14×16×7×7×6`, `p4_lib.py:22`) | **required, digest-bound `parent_candidate`**; the minuend of the replacement and the sole `M` comparison baseline | `R1`; `PREDECLARE-20260901-cause7` §0 |
| **G.combined_source** | `uq_universe_5d_covariance_combined_bkgaware.root` | the file the five **support-limited** lateral bands are read from; its own sha256 must be recorded, not inferred | `nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json:28-34` |
| **G.uthrow_source** | `unified_throw_cov_5d_fluxfix_20260806_full160.root` | the vertical inflation G already carries; **must survive Y unchanged** | same receipt |
| **G.centering** | `mean-centered` | Y inherits it; a centering change makes the object something other than a cause-7-only successor | same receipt |
| **Y** | **path, receipt schema/version, and producing revision DO NOT EXIST.** §2.4 declares what must be fixed before construction is authorizable | the object specified here | `R2`; `PREDECLARE-20260901-cause7` §2 |
| **S** | `active_universe_5d/standard/candidate/std_final5_candidate.root`, run `57128458`, covariance content `f26b3bfe…` (5D) / `c1fe11b1…` (4D) | **component donor only**, and only if each donated band is re-digested into Y's receipt | `SCOREBOARD` §5 |
| **F** | `uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root`, **266** bins, job `56431823` | **not evidence for Y**; `266 ≠ 10,694` | `OI-5`, `VL68`, `CRITERIA` §4.1 |
| **J** | the July `uq_universe_5d_covariance_combined_bkgaware_uthrow{,_cvcentered}.root` pair quoted by `values.tex` | **not evidence for Y**; wrong parent digest | `DECISION-20260831` §1 |

**S is not adoptable and may not become Y by promotion.** `SCOREBOARD` §5 records that S carries
`publication_gate_rejects_this: true` and that `p4_adopt_standard.py` **refuses it outright**; that flag
is an assertion, not a label — `fps_build_control_manifest.py:202-204` *dies* if the publication gate
fails to reject the manifest. S may supply bound lateral components; substituting S's whole block-sum
total for G's is forbidden by `PREDECLARE-20260901-cause7` §1 `C`(3).

## 2. The replacement algebra, and the five bands it is over

### 2.1 The algebra

    C_Y  =  C_G  −  L_support(G.combined_source)  +  L_active(selection-complete endpoints)

with the closure identity the writer and the validator must **each independently recompute**:

    C_Y − C_G  ==  L_active − L_support

Closure tolerance: the existing standard-P4 relative `1e-9` (`p4_build_components.py:140-171`). **That is
a numerical closure tolerance and is not, and may not be reported as, an `M`-leg materiality threshold**
(`PREDECLARE-20260901-cause7` §1 `C`(4)).

### 2.2 The five bands — bound by import, never by a retyped list

`L_support` and `L_active` are each **exactly** the five-band sum over `p4_lib.BANDS`
(`nd-unfolding/p4_lib.py:18-19`, *"Canonical standard lateral inventory (exactly these; order fixed)"*):

    BeamAngleX, BeamAngleY, MuonResolution, Muon_Energy_MINERvA, Muon_Energy_MINOS

with `ENDPOINTS = (0, 1)` and `N_ENDPOINTS = 10` (`p4_lib.py:20-21`). Support keys are
`hCov_universe5d_<band>`; active keys are `p4_lib.candidate_band_key(band)`.

**The producing code must import this tuple, not restate it.** A retyped list is a second
implementation of a rule that already has one, and this repository already carries a **conflicting**
lateral inventory: `nd-unfolding/pet_lateral_correction.py:42` defines `LATERAL` with **six** entries,
adding `MinosEfficiency`. That module is a different lane's, but a name-matched copy is one edit from
disagreeing with the canonical five.

### 2.3 Why five and not nine — checked against evidence, and what it costs Y's scope

`nd-unfolding/uq_5d/detector_universes.txt` enumerates **nine** detector lateral bands: the five above
plus `MinosEfficiency`, `GEANT_Neutron`, `GEANT_Pion`, `GEANT_Proton`. `adopt_unified_5d.py:19` states
that G's construction leaves *"the 9 detector-lateral bands"* untouched. Y replaces **five of those
nine**.

The four-band remainder is **justified, not overlooked**: `VALIDATION_LEDGER.md:790` records the five as
*"the five genuinely kinematic ones; `MinosEfficiency` and `GEANT_*` are weight-only and were correctly
left as ordinary universe bands"*, and `2d-unfolding/2D_OMNIFOLD_REFERENCE.md:241` says the same. A
weight-only band reweights events; it cannot move an event across the selection boundary, which is the
defect cause 7 names.

**This justification is a claim about the 5D producer and must be re-measured on G's own
`combined_source` before construction, not inherited from a 2D-side reference.** Required
pre-construction measurement `PM-1` (§4). If any of the four weight-only bands is found to carry
selection-dependent support in the 5D chain, Y as specified is **incomplete for cause 7** and this
document must be amended before it is used — a scope limit is not a defect only while it is measured
and stated.

### 2.4 What does not exist and must be declared before construction is authorizable

Per `PREDECLARE-20260901-cause7` §2, three things do not exist. `R2` authorizes drafting them; it
authorizes nothing that writes them:

1. **Y's output path.** Must be a new path under a Y-specific directory, never a rewrite of G's path and
   never a name a later run can silently re-point.
2. **Y's receipt schema and version.** §3's field set, versioned, written **last**.
3. **Y's producing revision.** A pinned commit plus executable import-closure digests, bound to the run
   rather than inferred from a nearby checkout. *A clean implementation at an unpinned revision is not
   `C` for Y* (`PREDECLARE-20260901-cause7` §1 `C`(5)).

## 3. Receipt schema — the fields, and the two that are usually missing

Written **last**, identifying the exact Y it describes (`PREDECLARE-20260901-cause7` §1 `P`):

- **Y:** path, byte size, sha256, reported-bin count, mask digest, row-order digest, producing job/run.
- **Parent:** G's exact path and **full** sha256 as `parent_candidate`; G's committed `combined_source`
  name **and the digest of the support-family ROOT actually read**.
- **Removed:** the five support band keys and their content digests.
- **Added:** the ten active endpoint inputs and digests, their **selection-migration censuses and
  declared policies**, and the five constructed active-band content digests.
- **Manifests:** endpoint, merged, and component manifest digests.
- **Code identity:** pinned producing revision plus executable import-closure digests.
- **Closure:** measured operands and residuals for `C_Y − C_G = L_active − L_support`; the unchanged
  non-lateral block; exact band inventories; symmetry; PSD.
- **§4's magnitude block**, with every operand.
- **The negative statement, verbatim in the receipt:** F's 266-bin receipt and S's whole-file PASS are
  **not** evidence that Y was produced. Where S supplies a lateral component, that component's digest is
  **rebound into Y's receipt**.

**The two fields whose absence has cost this campaign before:** the migration census/policy per endpoint
(presence of an endpoint is not evidence it was built selection-complete —
`PREDECLARE-20260901-cause7` §1 `C`(2)), and the import-closure digest bound to the run.

**Expected migration policy** is single-sourced at `p4_lib.py:64-65` and must be checked, not assumed:
`NONZERO_MIGRATION_BANDS = {BeamAngleX, BeamAngleY}`;
`ZERO_MIGRATION_BANDS = {MuonResolution, Muon_Energy_MINERvA, Muon_Energy_MINOS}`. A declared-zero band
measuring nonzero migration, or the reverse, must abort rather than be recorded as a note.

## 4. Required magnitude measurements — `R3` closed the threshold, not the measurement

> `R3`, ruled: cause 7's `M` leg carries **no materiality threshold**. *"A large measured difference
> satisfies the criterion exactly as a small one does."*

`R3` **selects a criterion and does nothing more**. It does not shrink the measured set, and it
explicitly does **not grade `M` on delivery**: a receipt is evidence; grading is a separate act by a lane
`BEN-381` does not disqualify. It also creates **no note obligation** — cause 7 acquires none. (The
note obligation that does exist is **cause 1's**, ruled separately in
`DECISION-20260901-joseph-oi172-oi173-magnitude-legs.md` `RULING 1`; do not merge the two.)

The measured set is `PREDECLARE-20260901-cause7` §1 `M`'s own, unchanged, each **with its operands**:

| # | quantity | form |
|---|---|---|
| `M1` | `delta_full` | `sqrt(Tr(C_Y)) / sqrt(Tr(C_G)) − 1` — the primary number |
| `M2` | `delta_lateral` | `sqrt(Tr(L_active)) / sqrt(Tr(L_support)) − 1` — localizes `M1` |
| `M3` | reported-bin σ ratio | `sqrt(diag(C_Y)) / sqrt(diag(C_G))` **as a distribution**: min, p05, median, p95, max, **plus zero/invalid counts**. Not a maximum alone |
| `M4` | shape change | `‖C_Y − C_G‖_F / ‖C_G‖_F` — because a trace can stay fixed while correlations move |
| `M5` | correlation change | largest absolute correlation-matrix change |

**Comparison population, stated on both sides** (`CRITERIA` §0: `M` is measured *on X's own inputs*):
both sides are on **G's own** inputs, mask, row ordering, non-lateral blocks and central value; unit is
the 10,694 reported bins of the 65,856-bin grid. **A comparison of S with G is not sufficient** and may
not be substituted — S embodies a different full construction.

**Pre-construction measurements required before an authorization request is well-formed:**

- **`PM-1`** — the nine-vs-five band census on G's own `combined_source`, per §2.3.
- **`PM-2`** — G's `combined_source` sha256, read from the file, not from the stamps receipt's name field.
- **`PM-3`** — availability and digests of the ten selection-complete endpoints. None of these ROOT
  objects is present in the repository checkout; they are cluster-resident, so `PM-1`–`PM-3` are cluster
  reads and must be costed against `R5`'s meter.

### The FPS precedent is an expectation, and is explicitly not evidence for Y

For F — **266 bins, not 10,694** — the same five-band replacement measured (`VL69`–`VL74`): active
lateral sqrt-trace `8.10399e-39` against the support block `7.30356e-39`, **ratio `1.10960` (+10.96%)**;
combined budget `8.040779e-39 → 8.774217e-39` (**+9.1215%**); per-bin σ ratio min `0.7897`, median
`1.0071`, max `1.4402`.

Two uses, and one prohibition. **Prohibited:** citing any of these as Y's `M`, or as a reason Y's `M`
need not be measured. **Permitted:** sizing the run, and noting that the per-bin ratio **min is below 1
while the max is above it** — the replacement moves σ in **both directions**, which is why §5's fixtures
must be bidirectional.

## 5. Test contract — power-tested in both required directions

`CRITERIA` §0's `T` leg requires a guard that fails when the defect is reintroduced **and** fails when
the guarded object disappears. Per `PREDECLARE-20260901-cause7` §1 `T`:

**Direction 1 — defect reintroduced.** Substitute the CV-support-limited bands for the selection-complete
active endpoints, leaving every other input valid. The test must fail **specifically because selection
migration was lost**, even though dimensions, PSD, total trace and internal sums still pass. Fixtures must
contain events migrating **into and out of** nominal support, so a one-sign guard cannot pass by accident.

**Direction 2 — guarded object disappears.** Delete or rename, one at a time: an active endpoint; an
active-band object; the selection-migration census/policy; G's parent digest; the cause-7 closure
identity. Each must **fail**, never skip, never reduce the band count, never read absence as zero
migration.

**Positive control** passes with exactly five ± endpoint pairs, the exact G parent digest, the exact
10,694-bin mask and row order, unchanged non-lateral content, and the closure identity within `1e-9`.

**Artifact-confusion controls** must fail: F (wrong 266-bin grid), J (wrong parent digest), a whole S
total (changes more than the lateral block).

**Two things that do not satisfy `T`:** a source-string assertion, and a test of
`check_support_comparison` alone — that helper records a finite trace ratio and **deliberately bounds
nothing** (`p4_lib.py:1309-1318`; the committed receipt carries
`support_ratio_is_diagnostic_not_bounded`, `p4_validate_active_lateral.py:240-248`).

**Fixture provenance.** Build fixtures from the **producer's** own endpoint objects and migration
metadata. A fixture derived from the replacement predicate cannot disagree with it.

**Mutation discipline.** Each mutation must be shown to reach the guard it targets. A digest check that
refuses a mutated input **first**, with the same exit status, tests the digest check and not the guard;
call the unit directly where that is a risk.

## 6. The limits — what a completed, four-leg-MET Y could and could not establish

Stated flatly, because every one of these is a live misreading route.

**A completed Y with `C`, `P`, `M`, `T` all MET would establish exactly one thing:** that quarantine
cause 7 is discharged **for the artifact Y**. Nothing else.

It would **not**:

1. **Move `(cause 7, G)`.** `R1`: permanently OPEN, an immutable historical cell. Y cannot discharge a
   cause for a different artifact's bytes; that is `CRITERIA` §0's whole framing, and the FPS discharge
   is the standing example of the error.
2. **Combine with G's causes 1–6 grades.** `R2(iii)`: **never**. Y has **no** causes 1–6 grades — those
   causes are graded against G (`R2`, "LEAVES UNCHANGED"). A "6 from G + 1 from Y = 7" tally is the
   precise arithmetic `R2(iii)` forbids.
3. **Move any count.** CAND stays `1 of 7`, QUOTED stays `0 of 7`.
4. **Move Gate 2**, which remains FAIL.
5. **Make Y adoptable, or adopted.** Y is not a covariance candidate (`R2`). Adoption is not among the
   outcomes of grading a cause.
6. **License a projection.** 3D/4D covariances must be exact projections from an **adopted** trunk; Y is
   not one.
7. **Touch `values.tex`**, any publication claim, or `R5`'s scoped-Letter default.
8. **Authorize its own construction.** `R2(iv)`; and `R5`'s ceilings are *"a prohibition and an
   accounting boundary … NOT authorization to spend up to"* them.

**The reject-Y conditions**, so the specification is falsifiable: Y is rejected if the closure identity
fails outside `1e-9`; if the five-band inventory is not exact on either side; if any non-lateral content
differs from G other than through `L_active − L_support`; if PSD or symmetry fails; if any endpoint lacks
a migration census or contradicts `p4_lib.py:64-65`'s declared policy; if the parent digest is not G's; or
if `PM-1` shows the five-band scope does not cover cause 7's defect class on G's `combined_source`.
**A large `M` is not a reject condition** (`R3`).

## 7. What this record does not do

It constructs nothing, authorizes nothing, launches nothing, grades no leg, discharges no cause, moves no
count and no gate, adopts nothing, spends nothing, writes no scheduler state, changes no publication
claim, and closes no `OI-*`. It does not perform the decision record's §4 owner applications. It does not
alter `CRITERIA`, `SCOREBOARD`, `MAP`, `OPEN_ITEMS`, `VALIDATION_LEDGER`, or
`PREDECLARE-20260901-cause7-discharge-criteria.md` — §4's item 3 is that document's author lane's to
apply, not this one's. It regenerates no state; `OI-73`'s hold stands and `--check-freshness` reports
STALE at this base by design.
