# P4 standard-lateral — Agent-A-owned status receipt (2026-07-18)

Co-located Agent-A status (the canonical `ND_OMNIFOLD_STATUS.md` carries a concurrent
session's uncommitted edit and is NOT absorbed, per the commit-gate ownership rule).

**State: REPAIR round 2 complete; NO covariance candidate exists.** Candidate
construction is gated on the standard-p4-verifier (019f74cb-…) returning PASS on the
committed patch.

- **P3S:** 120/120 endpoint event loops done.
- **Merge:** 10/10 endpoint MEFHC ROOTs (audited).
- **Unfold:** 10/10 endpoint xsec ROOTs content-validated (open/non-zombie/not-recovered/
  finite `hXSecND_flat`/65856-bin/positive/10694-central-mask/distinct). Existing products
  have no `.done` markers (old driver) — validated read-only; not rerun.
- **Evidence:** EVIDENCE-COMPLETE. All bindings recomputed and MATCH the verifier's
  independent observations: central5d `630306e2…`, mask5d `74374b1a…` (10694),
  endpoint-manifest `af568b4a…`, central4d `1fb82508…`, mask4d `c977c643…` (4830).
  Selection migration: BeamAngleX/Y nonzero (4700–4808), MuonResolution/Muon_Energy 0
  (bin-migration-only) — as expected. Receipts under `evidence/`.
- **Hardening:** canonical `run_p4_standard.sh` chain wires merge/audit → evidence/manifest
  → unfold → (verifier gate) → component-build → validate → project; old unsafe route
  retired/guarded; fail-closed gates in `p4_lib.py`; tests 20/20.

Downstream (P5B/P6) consume ONLY after PASS + a later authorized candidate turn.
