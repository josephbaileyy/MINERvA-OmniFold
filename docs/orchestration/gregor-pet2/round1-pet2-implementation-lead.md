You are the durable role `pet2_implementation_lead` in a persistent
multi-round MINERvA OmniFold campaign. You are the only delegate that may
later write implementation code, but ROUND 1 is DESIGN-ONLY: inspect and
report; do not modify any file yet.

Working tree:
`/Users/josephbailey/local-research/MINERvA-OmniFold-gregor-pet2`

Read the relevant repository instructions and at minimum:

- `KNOWN_ISSUES.md`
- `nd-unfolding/ND_OMNIFOLD_STATUS.md`
- `nd-unfolding/PET_UQ_REMEDIATION_STATUS.md`
- `nd-unfolding/pet/FULL_EVENT_FEATURE_CONTRACT.md`
- `docs/GREGOR_FOUNDATION_MODEL_REFERENCE.md`
- `docs/HIGHER_DIM_OMNIFOLD_DESIGN.md`
- current PET/OmniFold loaders, engine, Gate-4 launcher/driver, and tests

Design the smallest clean *experimental* native PyTorch PET2 backend that
preserves every current TensorFlow/Keras and recoil-only baseline. It must be
an opt-in arm, not a silent replacement, and must support:

- weighted binary density-ratio training with correct class-prior
  calibration;
- separate Step-1 reco/data/background and Step-2 truth inputs;
- native truth-only misses and deterministic event/index correspondence;
- literal background-cloud injection plus the canonical Stay-Positive target;
- nonnegative training weights, negative-weight provenance, and full
  extraction ordering;
- typed-token and richer-global ablations without schema drift;
- checkpoint initialization only when architecture, preprocessing, and
  licensing match;
- portable CPU fixtures and a Delta A100 Slurm pilot path;
- complete seed/config/fingerprint/telemetry receipts.

Deliver a design review, not code:

1. map the existing baseline dataflow and identify the exact extension seams;
2. propose file/module/API boundaries, tensor schemas, loss/calibration
   formulae, mask/type conventions, normalization fitting, save/load format,
   and failure behavior;
3. distinguish architecture-matched arm C, typed arm D, richer-global arm E,
   and checkpoint arm F without confounding representation and initialization;
4. give an environment/dependency strategy that does not destabilize the
   ROOT or TensorFlow paths;
5. enumerate tests and the minimum synthetic/fixture pilot needed before any
   real-data claim;
6. flag design decisions that must await the source archaeologist or contract
   auditor.

Do not assume Gregor's code or weights are reusable. Prefer an independent,
small implementation until licensing and dimensional compatibility are
proven. End with a change plan granular enough for adversarial review.
