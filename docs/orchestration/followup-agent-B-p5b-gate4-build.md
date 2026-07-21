GATE-4 LAUNCH-CODE GATE BUILD — CODE ONLY, **NO training launch**. You are agent-B-p5b, owner of the PET full-event schema and consumer contract (your context and UUID are unchanged). An interim Claude orchestrator is driving the campaign while the Codex root is paused; you are not replaced.

CONTEXT: Gate 3 is PROMOTED PASS — source manifest `docs/orchestration/state/p3f-pet-gate3-source-manifest-56169838.json` (independently verified). The user authorized building + validating the Gate-4 publication PET **nominal** launch-code gate NOW, WITHOUT launching any training, and it must be finished before 2026-07-21T20:00Z. Training-launch authorization is a separate later decision.

GOAL: Produce a hash-bound, test-covered, CODE-ONLY launch-code gate that mirrors the Gate-3 template `docs/orchestration/state/p3f-pet-gate3-launch-code-gate-20260720.json`.

ABSOLUTE CONSTRAINTS:
- Do NOT sbatch / salloc / submit / train / start any GPU or compute job. Do NOT start PET.
- Do NOT modify frozen Gate-2 / Gate-3 artifacts or any *.root/*.npz data files.
- Minimal changes, matching existing code idiom; deterministic.
- Do NOT git commit — leave all changes in the working tree; the orchestrator commits after independent (agy) verification.

BUILD / ASSEMBLE:
1. The publication full-event PET NOMINAL launcher (GPU sbatch: one unbootstrapped nominal + one matched GPU-floor repeat) that routes through `nd-unfolding/pet/fullevent_fps_dataloader.py` and MUST call `assert_publication_config` (estimator fingerprint `pet-fullevent-fps-v1`, `bkg_mode=negweight-refined`, G2 full-schema markers, background inventory), consuming the negweight-refined literal Gate-2 target and referencing the Gate-3 source manifest. It must FAIL CLOSED if fingerprint/target/inventory mismatch and must NOT auto-submit. The quarantined recoil script `nd-unfolding/pet/sbatch_pet_nominal_bkgsub.sh` is NOT the publication path (KNOWN_ISSUES #19/F7) — do not repurpose it.
2. The Gate-4 validators required by runbook Packet P5A and PET_UQ_REMEDIATION_STATUS Gate 4: ordinary closure, omitted-muon stress closure (reuse `pet/stress_closure_muon.py`, `pet/closure_fullevent_fps.py` where applicable), finite/full-coverage weights, strict MC index/order, exact lower-dimensional marginals, normalization, cap-sensitivity telemetry, and the freeze of estimator fingerprint + central vector + reported-bin mask/order + extended-FPS edges + seed/config policy. Author only the gaps; reuse existing code.
3. Tests under `nd-unfolding/tests/` (launcher test + validator test) plus any frozen-contract regressions. Run them; ALL must pass. Report exact pass/fail counts and the command(s).
4. Synthetic receipt/resume roundtrip + synthetic tamper-rejection proof (mirror Gate 3) using synthetic fixtures only — no real training.
5. Preflight: zero active compute writers, no interactive allocation, clean output namespace.

RETURN STRICT STRUCTURED OUTPUT:
(a) every file created/modified: absolute path + sha256;
(b) exact test command(s) + pass/fail counts;
(c) `assert_publication_config` binding evidence (fingerprint / target / inventory);
(d) preflight result;
(e) explicit confirmation that nothing was launched/submitted and that `nominal_pet_training_allowed` stays false.
Be lean and efficient (conserve quota). End the turn.
