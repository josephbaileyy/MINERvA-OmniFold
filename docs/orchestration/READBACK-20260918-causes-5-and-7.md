# READBACK 2026-09-18 — causes 7 and 5 of the audit's seven-cause table

**Owner:** `z-independent-assessor` (`owners.tsv:15`). **Base for all source citations:** `ecdb150f`.
**Plan:** `PLAN-20260918-scalar5d-publication-completion.md`.

## CITABLE FOR / NOT CITABLE FOR

**CITABLE FOR:** findings `X1`–`X6` (cause 7) and `Y1`–`Y3` (cause 5), with the measurements each
rests on.

**NOT CITABLE FOR:** **discharge of the `#16` publication gate — I do not issue it** (`X6`); the
cause-5 *"INAPPLICABLE, DISPOSED BY DECISION"* outcome — **that is a ruling and `SPEC` §6.1 assigns
it to a decision, not to a trace** (`Y3`); any adoption, grade or projection. This is not a PET study
and does not reopen `OI-126`.

## Evidence classes

- **SOURCE** — committed blobs at `ecdb150f`.
- **PAYLOAD (MEASURED BY ME)** — cluster ROOT/directory reads on a login node with `uproot 5.6.9`;
  **no `sbatch`, no `srun`, no job attempt, `R5` untouched**; writes only to `/tmp`.
- **NEW COMPUTATION** — none performed. `C_Z − C_G` was **not** computed: the audit is explicit that
  it mixes several changes and is not this cause's magnitude.

---

# CAUSE 7

## `X1` (SOURCE) — the routed lead's three source facts verify, and the decision rule is NOT a name list

`z_contract.py:67` is `LATERAL_BANDS = tuple(p4_lib.BANDS)  # A, 5 -- enter as L_b, uninflated`;
`p4_lib.py:18-19` is the five; `eavailW_covariance.py:40-42` is the historical nine. All three as
relayed.

**But the load-bearing fact is one the lead did not use, and it is what makes the hypothesis
testable.** `unfold_nd_omnifold_unbinned.py:388` decides laterality by **branch presence**, not by
name: `if t.GetBranch(l_sim) and t.GetBranch(l_mc):   # lateral`. And
`_universe_kine_branches`' docstring (`2d-unfolding/unfold_2d_omnifold_unbinned.py:498-511`) says so:
*"Returns `(None, None)` for vertical-only universes (**caller detects by branch absence in the input
ROOT**)."* **So the code performs the very test the lead needs, at runtime, against the data — and I
can run the same test.**

## `X2` (SOURCE) — the producer states the physics, and it is the authority

`MINERvA101/.../runEventLoopOmniFold.cpp:238-244`, verbatim:

> *"the lateral bands are all muon/beam systematics (BeamAngleX/Y, MuonResolution,
> Muon_Energy_MINERvA/MINOS). They override only muon momentum/angle getters, none of which feed
> `NewEavail()` … So E_avail is invariant under every lateral universe and needs no shifted branch.
> **The GEANT hadronic-response bands (which DO move E_avail physically) are vertical/weight-only and
> are captured by `w_reco_GEANT_*`.**"*

So three of the four excluded are named and disposed **by the producer itself**. The fourth,
`MinosEfficiency`, is constructed at `:1749` as
`PlotUtils::MINOSEfficiencyReweighter<CVUniverse, MichelEvent>` — **a reweighter**, i.e. weight-only
by class. And `sbatch_evloop_array_5d_active_laterals.sh:17,36` independently enumerates
*"**5 kinematic bands** × 2 endpoints × 12 playlists = 120"* with `BANDS=(BeamAngleX BeamAngleY
MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)`.

## `X3` (PAYLOAD, MEASURED BY ME) — the hypothesis SURVIVES the decisive test, on the production tuple

I applied the **code's own criterion** to `runEventLoopOmniFold_5D_1A_universes_full_bkgaware.root`,
tree `mc_signal_reco`, **470 branches**, for all nine bands × both endpoints:

| band | weight branches | kinematic `pt/pz` | shifted `q3`+`W` | verdict |
|---|---|---|---|---|
| BeamAngleX, BeamAngleY, MuonResolution, Muon_Energy_MINERvA, Muon_Energy_MINOS | **2/2** | **4/4** | **4/4** | **LATERAL** |
| MinosEfficiency, GEANT_Neutron, GEANT_Pion, GEANT_Proton | **2/2** | **0/4** | **0/4** | **WEIGHT-ONLY** |

uniform across both endpoints, all eighteen combinations.

**`measured lateral set == p4_lib.BANDS` → `True`. `the four excluded are all weight-only` → `True`.**

**So the lead is confirmed, and not by what the names denote:** every one of the five writes shifted
reconstructed kinematics into the tuple and **none of the four does**, tested by the same predicate
the driver evaluates at runtime. **The five-of-nine scope is correct.**

## `X4` (SOURCE + PAYLOAD) — I tried to break it on the 5D-specific axis, and it HELD

The producer's note covers `E_avail` (invariant) and `q3` (shifted) — **it predates the `W` axis**, so
I checked whether 5D's fifth axis had been left lateral-invariant by omission, which would understate
every lateral band. **It has not**, on four independent legs:

1. `unfold_nd_omnifold_unbinned.py:115-120` declares `"W": dict(..., lateral_invariant=False)` with
   the reason — *"Truth `GetTrueExperimentersW()`, reco `RecoW()` (both muon+recoil dependent), so W
   is NOT lateral-invariant"*.
2. The C++ **writes** the shifted branches: `W_truth_`/`MC_W_`/`sim_W_` at `:361`, `:367`, `:373`.
3. The Python **refuses** a missing one rather than falling back — `:395-401`, *"[FAIL] shifted branch
   … missing … Retaining the CV branch would understate this lateral band"*, explicitly marked as the
   `J33` repair of a **silent CV fallback**.
4. **PAYLOAD:** `q3`+`W` shifted branches are `4/4` present for all five (`X3`).

**Recorded as an attempted refutation that failed, not as a confirmation I went looking for.**

## `X5` (PAYLOAD, MEASURED BY ME) — the ten endpoints, the active/support footing, and one scope clarification

**The ten endpoint identities — VERIFIED.** `active_universe_5d/standard/` contains exactly ten
band-endpoint directories, and they are uniform: **12 ROOT files and 53.8 GB each**, matching the
launcher's `--array=0-119%12` (`5 × 2 × 12 = 120`) and `p4_lib.py:21`'s
`N_ENDPOINTS = len(BANDS) × len(ENDPOINTS) = 10`.

**Active versus support lateral blocks, on identical footing:**

| | keys | `hCov_*` | band names | prefixes |
|---|---|---|---|---|
| ACTIVE `std_final5_candidate.root` (42.3 GB) | 49 | 48 | 47 | `hCov_active5d_`, `hCov_retained5d_`, `hCov_stdcombined5d_`, `hCov_stdsyst5d_` |
| SUPPORT `…_combined_bkgaware.root` (41.4 GB) | 47 | 47 | 46 | `hCov_combined5d_`, `hCov_universe5d_` |

**Both carry all five laterals and all four weight-only bands**, at the same `10694` footing.

⚠ **THE SCOPE CLARIFICATION, and it is the thing most likely to be mis-read.** The four are excluded
from the **active lateral swap**, **not from the covariance.** I measured them present as `hCov_*`
blocks in *both* files. A reader taking *"the four excluded"* to mean *"absent from `C_Z`"* would be
wrong: the nine all contribute systematic covariance; only the five need an active,
selection-migrating treatment because only they move the selection.

**The selection migrations, source-declared:** `p4_lib.py:64-65` partitions exactly the five —
`NONZERO_MIGRATION_BANDS = {BeamAngleX, BeamAngleY}` and
`ZERO_MIGRATION_BANDS = {MuonResolution, Muon_Energy_MINERvA, Muon_Energy_MINOS}`, `2 + 3 = 5`.

## `X6` — what I do NOT close: the `#16` gate itself

`AGENTS.md:27` requires the quotable covariance be projected from a **selection-complete** trunk, and
`ESTIMATOR_REGISTRY.md:29` carries *"lateral still support-limited until #16 five-band coverage
(publication gate)"*.

**What the evidence establishes:** the five-band **scope** is correct (`X3`), the `W` axis is handled
(`X4`), and the active five-band coverage **exists and is complete at the event-loop level** — ten
endpoints, twelve playlists each, uniform size (`X5`).

**What it does not establish, and I will not assert:** that the gate is **discharged**. That is a
disposition on a named **publication gate**, and it is Joseph's. Two things a ruling would still want
and that this readback does not supply: an argument that active coverage of the five is *sufficient*
for selection-completeness given that the four vertical bands' support is CV-selected by
construction; and confirmation that the adopted trunk's lateral term `Σ_A L_b` is drawn from the
**active** blocks rather than the support ones — the plumbing is consistent with it
(`z_contract.py:67`'s *"A, 5 — enter as `L_b`, uninflated"*, and the receipt's membership census
`45 − 13 vert − 27 residual = 5 lateral`), **but consistency is not the same as verification, and I
did not trace the read.**

---

# CAUSE 5

## `Y1` (SOURCE) — the falsifier is named, and it is negative on both named modules

`SPEC` §2.5 records `VL66`'s own scope limit — *"it did **NOT** exhaustively audit
`analyze_universes_5d.py` or `adopt_unified_5d.py` for every input"* — and its falsifier: *"a
PET-derived product consumed by either of those two modules."*

**Audited, both modules, at `ecdb150f`:**

| | `analyze_universes_5d.py` | `adopt_unified_5d.py` |
|---|---|---|
| imports of a `pet` module | **0** | **0** |
| `pet` path literals (`/pet/`, `pet_ctotal`, `bkgsub`, `fullevent`) | **0** | **0** |
| `PET` word on any code line | **0** | **0** |

**The named falsifier is negative on both.** `VL66`'s stated gap is closed by this trace.

## `Y2` (SOURCE) — and the whole of Z's own closure is clean, including the adoption/inflation path

Z's import closure is the **fifteen** modules recorded in the pilot's own `metadata_json`
(`code_identity.import_closure_digests`), which I read from `z-cv.npz`. Across all fifteen:
**no `pet` import and no `pet` path literal.** The eight consumed input paths in `z-manifest.json` —
active, central, ml, null, parent, stat, support, throw — contain **no `/pet/` path**. The
adoption/inflation path is inside the closure (`adopt_unified_5d.py`, `z_assembly.py`) and is covered.

**The only genuine PET mentions in the closure are documentation cross-references, not consumption:**
`unified_throw_cov.py:55` cites `pet/combine_cstat_bkgsub_100rep.py:78` in a comment, and
`mnv_guarded_run.py:5407` cites `pet/pointcloud_projection.py` in a docstring as an example of the
`sys.path[0]` hazard.

⚠ **A methodological note on my own search, recorded because it nearly produced a false alarm.** My
first pattern included `frozen`, which matched **`frozenset` 76 times** in `mnv_guarded_run.py` alone
and returned "77 PET hits" for a file whose genuine count is **one docstring citation**. Token
decomposition showed `frozen 76 / PET 1 / pet_ 0 / /pet/ 1 / fullevent 0`. **An over-broad pattern
manufactures a finding as readily as a narrow one misses it**, and the count was checked rather than
reported.

## `Y3` — the trace supports the ruling; it is not the ruling

`SPEC` §6.1 authorizes an artifact-specific *"INAPPLICABLE, DISPOSED BY DECISION"* outcome **"after
the complete trace and the falsifier check"** — so the trace is a precondition and the **decision is
a separate act**. `Y1` and `Y2` supply the trace and the falsifier check, negative. **I do not issue
the disposition.**

⚠ **And the trace's own boundary, stated so it is not over-read.** It covers Z's import closure, the
two modules `VL66` named, and the eight consumed **input paths**. It does **not** audit the full
upstream producer chain of every consumed byte — a PET-derived product entering several levels
upstream of those inputs would not be visible to it, and neither `VL66`'s trace nor this one covers
that. **That is a bounded negative, which is what the falsifier asked for, and not a proof of
universal absence.**

---

## What is owed, by category

- **SOURCE:** nothing outstanding in this scope.
- **PAYLOAD:** the `Σ_A L_b` read trace (`X6`), which is a read and was not performed here.
- **NEW COMPUTATION:** none is required to report any cell above. `C_Z − C_G` is deliberately not
  computed.
- **RULINGS, not work:** the `#16` gate disposition (`X6`) and the cause-5 outcome (`Y3`).
