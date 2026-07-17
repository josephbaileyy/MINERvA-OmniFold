# P5B FPS lateral source: (a) sidecar-reuse vs (b) fresh full-event P3F — decision

Owner: Agent B (PET). 2026-07-17. Requested by the fe-fps orchestrator (P5B dependency
correction). Decides how the full-event FPS **selection-complete lateral** endpoints are
sourced. Central rule: **fail closed** — no publication lateral launches on an endpoint whose
schema/alignment/provenance is not proven.

## Evidence — current P3F endpoint schema (audited 2026-07-17)
Per-playlist ROOTs under `active_universe_5d/fps/<BAND>_<IDX>/` (99 present, 0 merged), produced
by the PRE-full-event binary. Trees + branches:
- `mc_signal_reco` (24): scalar muon `sim,sim_pz` + `sim_eavail/q3/W/pass`, truth `MC,MC_pz,
  MC_eavail/q3/W,MC_hadangle,MC_nproton,MC_npip`, `w_reco/w_truth`, recoil cloud
  `part_reco_E/pos/z`, truth cloud `part_gen_E/px/py/pz/pdg`.
- `data` (9): `measured,measured_pz,measured_eavail/q3/W/pass`, recoil cloud `part_reco_*`.
- `mc_background` (16): `sim_background_*`, `w_bkg`, `bkg_vtx_{x,y,z}`, `bkg_nuPDG/current/inttype`
  (generator labels — NOT classifier features), recoil cloud.
- Per-endpoint active metadata: `activeUniverseBand/Index`, `hasActiveUniverse`,
  `activeUniverseIsLateral`, `activeUniverse{Truth,Reco}{Entrants,Exits}` (migration census).

**PRESENT:** recoil + truth clouds (with PDG), scalar muon (pT,p‖), Eavail/q3/W, migration
counters. **ABSENT:** muon 4-vector (mu_px/py/pz/E), φ, charge/qp, MINOS match/range/quality,
reco/data vertex, recoil view-ID, timing, residual-energy tokens, and STABLE EVENT KEYS.

Key consequence: clouds + scalars live in the SAME `mc_signal_reco` tree, so a single dump
yields an INTERNALLY row-aligned endpoint npz (cloud rows ↔ scalar/weight rows) with no
cross-npz join. The cross-npz CRC join (fe_pilot) is needed only when muon features come from a
SEPARATE source (the full muon object, or the DATA-side scalars — see CLM-007).

## The two options
### (a) Sidecar reuse of existing P3F clouds — REDUCED muon schema only
Build endpoint full-event inputs by dumping the committed P3F endpoint ROOTs (merge 12
playlists via `2d-unfolding/uq/hadd_universes_full.py`, then a `dump_pointcloud_inputs`-style
read of `mc_signal_reco`/`data`), retrain PET per endpoint on the shifted cloud + scalar muon
{pT,p‖}, extract x_u, and build the MAT-centered C_lateral. Feasible NOW (once P3F is merged +
committed) because these ROOTs carry the reduced schema this estimator already uses. Does NOT
require the C++ branches. CANNOT deliver the full muon object.

### (b) Fresh full-event P3F — FULL muon schema
Regenerate FPS active endpoints after the C++ full-event dump branches land
(FULL_EVENT_INTERFACE_REQUEST.md): muon 4-vec/φ/charge/MINOS, reco/data vertex, view/timing,
residual-energy, AND stable event keys. Publication-complete; the long pole (C++ branch work
coordinated with Agent A only after its arrays drain, + a fresh 5×2×12 production).

## Required proof battery for (a) — fail closed at every gate (adapt fe_pilot CRC method)
Per endpoint, before ANY lateral use:
1. **Schema gate:** endpoint tree carries the full reduced-schema branch set above; assert the
   adopted feature list is a subset; fail closed on any missing branch. (Muon-4vec/vertex/etc.
   absence => this endpoint is REDUCED-schema; label it so, never claim the full object.)
2. **Internal alignment:** single-tree dump ⇒ cloud/scalar/weight rows aligned by entry order;
   assert equal row counts across all dumped arrays; finite; pad-mask consistent.
3. **CV/data-scalar join (CLM-007):** the DATA muon scalars come from the endpoint's own `data`
   tree `measured,measured_pz` (present) — no external join needed for the reduced set. If any
   feature is sourced from a separate npz, require CRC32 byte-exact shared-array agreement
   (pass_*/w_* truth-INVARIANT arrays for detector universes) + Spearman physics gate ≥0.8 +
   SHA256 provenance, exactly as `fe_pilot/build_data_scalars_xps2.py`.
4. **Migration accounting:** cross-check `activeUniverse*Entrants/Exits` against the dumped
   pass_reco/pass_truth deltas vs CV; the selection-complete migration IS the systematic — it
   must be captured, not silently dropped (KNOWN_ISSUES #16).
5. **Provenance + STABLE KEYS:** compute + store SHA256 of every endpoint ROOT/npz; because the
   ROOTs lack event keys, ADD a derived stable key (e.g., hash of an ordered truth-invariant
   tuple) to the dumped npz for future provenance, per the orchestrator directive.
6. **Estimator fingerprint:** the reduced-schema laterals carry the SAME `pet-fullevent-fps-v1`
   (reduced-muon) fingerprint as the nominal; reject on mismatch (never mix schemas).

If ANY gate fails or exact alignment cannot be proven ⇒ **regenerate via (b).**

## RECOMMENDATION
- **Publication-complete path = (b)** (full muon object). Required by the feature contract's full
  schema; gated on the C++ branches + fresh P3F. This is the ultimate deliverable.
- **Economical bridge = (a)**, adopted ONLY under the full proof battery above and ONLY as a
  REDUCED-muon-schema lateral (pT,p‖), consistent with the P5A-validated reduced nominal and
  explicitly labeled reduced. It delivers a P5B reduced-schema lateral baseline as soon as P3F
  is merged+committed, without waiting for the C++ branches — while (b) proceeds in parallel.
- Both share `pet-fullevent-fps-v1`; a full-schema (b) run is a NEW estimator fingerprint
  (`-v2`/full) and does NOT mix with (a) reduced products.
- **Do NOT open P5B laterals on "merged>0" alone** — run gate 1 (schema) first; the current
  P3F is reduced-schema, so any launch must be labeled reduced or deferred to (b).

## Immediate status
P3F not yet merged/committed; even when merged it is reduced-schema. C++ branches not started
(coordinate with Agent A after its arrays drain). So (a) is not launchable yet (needs merged+
committed P3F + the proof battery); (b) is gated on the branches. Meanwhile: implement the
F2/F3/F7/F8 engine fixes (safe, authorized) so either path launches on a clean engine.
