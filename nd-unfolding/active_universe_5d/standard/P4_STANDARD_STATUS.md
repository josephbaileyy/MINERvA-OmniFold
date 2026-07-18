# P4 standard-lateral — Agent-A-owned status receipt (2026-07-18)

Co-located Agent-A status (the canonical `ND_OMNIFOLD_STATUS.md` carries a concurrent
session's uncommitted edit and is NOT absorbed, per the commit-gate ownership rule — PG0).

**State: REPAIR round 3 complete; NO covariance candidate exists.** Candidate
construction (component-build → validate → project → adopt) is gated on the
standard-p4-verifier (019f74cb-…) returning PASS on the committed round-3 patch.

- **P3S:** 120/120 endpoint event loops done.
- **Merge:** 10/10 endpoint MEFHC ROOTs. Full-file hashes validated by the owner-neutral
  orchestrator receipt `docs/orchestration/state/merged-input-hashes/p4-merged-20260718/`
  (COMPLETE; size⇥mtime⇥path inventory; 10-line standard.sha256) — reused, NOT re-hashed.
- **Unfold:** 10/10 endpoint xsec ROOTs content-validated (open/non-zombie/not-recovered/
  finite `hXSecND_flat`/65856-bin/positive/10694-central-mask/distinct). Legacy products
  (no `.done`) are attested read-only against the manifest; the transactional driver
  (`run_p4_unfold_std.sh`) writes the receipt LAST after an atomic ROOT publish.
- **Evidence:** EVIDENCE-COMPLETE. Recomputed bindings MATCH the verifier's independent
  observations — central5d `630306e2…`, mask5d `74374b1a…` (10694), endpoint-manifest
  `af568b4a…`, central4d `1fb82508…`, mask4d `c977c643…` (4830). New round-3 bindings:
  config-hash, source git blobs+commits, C++ binary sha256 `6b60fc51…`, edges/bin-volume
  hash (`e05889ac…`/`f71145ce…`), endpoint mask-equality TRUE, orchestrator merged digest
  `6e6c4752…` (10 hashes). Selection migration: BeamAngleX/Y nonzero (4700–4808),
  MuonResolution/Muon_Energy 0 (bin-migration-only) — as expected. Receipts under `evidence/`.
- **Hardening (round 3):** ROOT lazy-imported everywhere (guards/tests run login-side);
  separate canonical stat/ML ROOTs + PURE ADDITION (no subtraction) in
  `p4_build_components.py`; deterministic in-code projection M + byte-identical central
  non-mutation (`p4_project_4d.py`); inseparable merged-evidence gate; later-only adoption
  CLI `p4_adopt_standard.py` (not run/not wired); real-CLI harness `tests/test_p4_repair.py`
  — 28/28 PASS. Canonical driver `run_p4_standard.sh` STOPs at evidence by default and
  requires a `P4_VERIFIER_PASS` token before any covariance stage.

Downstream (P5B/P6) consume ONLY after PASS + a later, separately authorized candidate turn.
