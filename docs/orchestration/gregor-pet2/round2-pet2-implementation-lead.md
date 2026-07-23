You are continuing the same durable `pet2_implementation_lead` session.
ROUND 2 authorizes implementation code in the shared campaign worktree. Do
not start any provider delegate, subagent, one-shot Codex/Claude/agy process,
or external account turn yourself; this campaign requires the root to route
every provider turn through `agentctl.py`.

Implement the smallest clean, independent, opt-in PyTorch PET2-family
experimental backend justified by your Round-1 design. Preserve every legacy
TensorFlow/Keras and recoil-only file and default. Do not copy Gregor's source.
The source audit established that the ideas are MIT-reimplementable with
attribution, but the checkpoint files are inaccessible and unlicensed; arm F
must be an explicit, tested `unavailable` outcome, never silent random init.

Hard decisions from Round 1:

- Use an explicit boolean token mask. Never infer padding from a continuous
  physics feature.
- Category 0 is pad/unknown only; every real type starts at 1.
- Step 1 must have only detector-observable reco/data/background fields.
  Truth PDG and generator bookkeeping are Step-2/audit only.
- Preserve separate `w_reco` and `w_truth`, literal aligned backgrounds,
  canonical nonnegative Stay-Positive target input, native truth-only misses,
  deterministic row order, full-order extraction, and calibrated weighted
  density-ratio conventions.
- The G2 publication NPZ and Gate-2 target payload are absent locally. Code
  must fail closed on absent real inputs and must not claim G2 validation.
- Current G2 does not contain reco photon/blob/prong identities or dE/dx.
  Implement the typed-token schema and synthetic/public-data adapter seams,
  but do not invent those labels for G2. The available G2 `view` category is a
  separate detector-view ablation, not a substitute for object type.
- Implement muon-token versus muon-global, overflow aggregate, type, and
  richer-global feature masks so the declared arm difference is machine
  auditable. Unsupported fields stay disabled with a reason.
- Arm C: architecture-matched random backend on the baseline-available
  generic token/global footing. Arm D: same training rows and capacity with
  real reconstructed types only when supplied. Arm E: D plus an explicitly
  declared audited global block. Arm F: strict manifest/checksum/license/shape
  gate, currently expected to reject.

Required implementation scope:

1. An isolated `nd-unfolding/pet2_torch/` package with NumPy-only contract
   validation, feature/arm manifests, fitted preprocessing, a compact
   independent PET2-family model, weighted BCE plus class-mass correction,
   one-iteration Step-1/Step-2 engine, checkpoint/receipt utilities, and
   deterministic full-order inference.
2. Explicit configuration/recipe fingerprints and telemetry for seeds,
   splits, weights, prior offsets, cap saturation, ESS, weight quantiles,
   masks/padding/overflow, runtime, throughput, peak GPU memory, environment,
   and output hashes.
3. Portable synthetic fixtures containing data, signal reco/truth,
   backgrounds, native misses, uneven class masses, typed objects, overflow,
   and a known conditional distortion. Provide a CLI that runs matched
   C/D/E ablations and emits machine-readable JSON. The fixture must be small
   enough for CPU tests but scalable for a one-A100 pilot.
4. Tests for schema/data-MC symmetry, no truth leakage, shape/mask/padding,
   pad/type separation, permutation invariance, overflow conservation,
   NaN/OOV/malformed failure, deterministic alignment and split, analytic
   density-ratio recovery, native misses, tiny overfit, save/load, exact arm
   diffs, and strict F rejection.
5. An optional reader/seam for the immutable public Gregor dataset revision
   `32e2f5040ff2678a2ef7ca1bc0b450b324f4fd83`, clearly tagged diagnostic
   MC-only evidence. Do not download the 826 MB file from this turn or place
   external data in git.
6. A Delta one-A100 Slurm launcher using `module load pytorch-conda/2.8`,
   unique campaign job/output names, bounded CPUs, and no writes to
   `/u/jbailey2/MINERvA-OmniFold` or its active job/output paths.
7. A minimal environment manifest/lock that records the tested PyTorch/NumPy/
   safetensors versions without destabilizing ROOT or TensorFlow.

Tests on the Mac may skip cleanly when PyTorch is absent. You may edit code,
tests, docs local to the package, and launchers, but do not edit the canonical
ND status/run log, VALIDATION_LEDGER, assessment, or commit results; the root
will handle the repository commit gate after independent review.

Before finishing:

- inspect your complete diff;
- run every login-safe test that does not require PyTorch;
- report exact files changed, tests run/results, known omissions, and commands
  the root should run under Delta's PyTorch module;
- do not commit, submit Slurm, download data, or call external providers.
