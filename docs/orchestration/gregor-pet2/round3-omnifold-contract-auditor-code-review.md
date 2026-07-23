Continue as the same durable `omnifold_contract_auditor`. ROUND 3 is the
required post-implementation code/schema audit. Do not edit files and do not
start any provider delegate, subagent, or one-shot external process.

Audit every new file under `nd-unfolding/pet2_torch/` and both
`nd-unfolding/tests/test_pet2_torch_*.py` against your Round-1/2 rulings and
the canonical full-event contract. You may run read-only/login-safe tests.
Treat the implementation lead's claims as untrusted until verified.

At minimum inspect:

- exact Step-1/Step-2 ratio direction, class masses, subset/split corrections,
  target normalization, POT scale, `w_reco`/`w_truth`, initial push, native
  misses, fake rejection, and full-order inference;
- whether the G2 adapter really verifies immutable schema/identity/target
  receipts and whether it violates the campaign's no-eager-load rule for
  approximately 40M-event inputs;
- data/signal/background schema symmetry, leakage, sentinel handling,
  categorical conventions, truth PDG isolation, units, periodic truth
  coordinates, masks, malformed/OOV behavior, overflow conservation, and
  physical-vs-row identities;
- whether C, D-view, D-typed, E-muon, E-rich, muon-token, overflow, and F are
  represented without hidden confounders or unsupported G2 labels;
- model parameter parity, explicit-mask behavior, permutation/padding
  invariance, deterministic settings, extraction/artifact integrity,
  checkpoint safety, telemetry completeness, and environment/launcher safety;
- tests for every MUST-FIX item from Round 2, including the still-unfixed
  Gate-2 telemetry `/1000` bug and cross-engine/double-normalization coverage.

Identify bugs with severity (`BLOCKER`, `MAJOR`, `MINOR`) and cite exact
file:line evidence. Distinguish implementation defects from unavailable-G2
evidence. End with:

1. code-acceptance verdict;
2. exact required patches/tests before any Delta result can be accepted;
3. tests/experiments safe to run before revision versus prohibited;
4. remaining G2-only deferrals.

Do not infer a scientific winner.
