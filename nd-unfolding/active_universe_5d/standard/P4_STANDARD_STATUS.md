# P4 standard-lateral — Agent-A-owned status receipt (2026-07-18)

Co-located Agent-A status (the canonical `ND_OMNIFOLD_STATUS.md` carries a concurrent
session's uncommitted edit and is NOT absorbed, per the commit-gate ownership rule — PG0).

**State: REPAIR round 3 complete; NO covariance candidate exists.** Candidate
construction (component-build → validate → project → adopt) is gated on the
standard-p4-verifier (019f74cb-…) returning PASS on the committed round-3 patch.

> **CORRECTED 2026-08-07 (BEN-046) — read this before sizing any remaining work.** The line
> above says "repair round 3 complete", which describes the work *submitted* and is silent on
> the *verdict returned*. The verdict was **BLOCK**: the same `standard-p4-verifier` UUID
> blocked `74fa362` with **six ranked defects**, and
> `docs/orchestration/followup-agent-A-standard-05.md` was written as the repair-4 brief.
> **No repair-4 commit was ever made** — `git log 74fa362..HEAD` over `p4_*` / `run_p4_*` /
> `tests/test_p4_repair.py` returns only `d5bd5da` (an unrelated note-overclaims commit that
> incidentally touched three of the same files), the FPS lane's own repairs, and the
> 2026-08-07 G-0/G-1/G-3 close-out commits. So the six defects are outstanding and stages 4–6
> are **not** merely awaiting a formality. `MIGRATION-TAKEOVER-STATUS.md` rows T2 and PG3S
> carry the BLOCK; `RUNBOOK-20260807-gbdt-closeout.md` §1 does not, which is the finding.

**Addendum 2026-08-07 — close-out packets G-0/G-1/G-3 (see the RUN_LOG entries of that date).**

- **G-1 landed (code only):** the lane can now express a background footing. `P4Config` carries
  a validated `bkg_mode` inside `config_hash`; `p4_evidence.py` writes a nested `footing` block
  plus per-endpoint `footing_evidence` classified from the unfold logs and blocks when they
  disagree; `run_p4_unfold_std.sh` passes `--bkg-mode` explicitly and stamps it into both
  receipt shapes. Value is `purity`, the recorded 2026-08-07 decision. Tests 41/41.
  **Not yet on the cluster checkout** — that tree is shared with a live concurrent lane.
- **G-3 preflight PASSED** (job `56445593`, ~71 s): 10/10 merges valid, audit 120/120,
  `EVIDENCE-COMPLETE`, all five cross-checks MATCH, `mask5d n=10694`, `mask4d n=4830`.
- **Attestation is available, measured not assumed:** all ten endpoint ROOTs sha256-match the
  committed manifest (10/10), so stage 3 legacy-attests with no re-unfold.
- **Stage 3 deliberately NOT run:** on pre-G-1 code it would write ten receipts with no
  `bkg_mode`, and the launcher skips any endpoint that already has a receipt — with deletions
  frozen, that would be an unfixable provenance regression.
- **Still true:** the ten ROOTs have **zero** `.done` receipts (`KNOWN_ISSUES.md` #20(c)).

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
