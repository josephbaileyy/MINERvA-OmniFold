# Gregor PET2 OmniFold campaign ledger

Append-only orchestration and experimental ledger for branch
`codex/gregor-pet2-omnifold`.

## 2026-07-23 — campaign initialization

- Isolated worktree:
  `/Users/josephbailey/local-research/MINERvA-OmniFold-gregor-pet2`.
- Base commit: `f7b7a77544f436afea212250254143083d846754`
  (`main == origin/main` at initialization).
- Original checkout was clean and remains on `main`; no existing campaign
  branch or colliding worktree was present.
- Local capacity: 10 logical/physical CPU cores, 16 GiB RAM, memory-pressure
  report 32% free. Sustained local jobs are capped at five threads and one
  memory-heavy process.
- Delta SSH control master verified alive at 2026-07-23 08:49 EDT, 25 minutes
  old. User-described eight-hour access window therefore had approximately
  7.5 hours remaining at verification.
- Delta account `bhvk-delta-gpu` is active. Existing job `20416508`
  (`pet_train_fps_delta`) is RUNNING on `gpua065` with 4 A100 GPUs from the
  separate checkout `/u/jbailey2/MINERvA-OmniFold`; it is out of scope and
  must not be touched.
- First corrected local `usagectl.py snapshot --json`:
  `gate_ok=true`; Codex personal 93% seven-day remaining, reset
  2026-07-30T04:09:42Z, zero reset credits; Codex school 19% remaining,
  reset 2026-07-24T02:51:01Z; Claude capacities unknown (missing fresh
  caches); agy capacity unknown. No reset-credit action is authorized.

## 2026-07-23 — source and compute staging

- Current `gregorkrz/minerva-ml` upstream was inspected at
  `fc9a099d3c9c060f03cef293c294f9de4eb019cd`; the requested pinned commit
  `af5d92ed2b3b448a09b6b7cf6b4f179e5757b4ed` is available locally.
  Model, layer, loader, preprocessing, and training files relevant to this
  campaign are byte-identical between those commits; the intervening changes
  are documentation, plotting, evaluation, and job-file changes.
- The repository carries an MIT license. The public Hugging Face dataset
  `gregorkrzmanc/minerva-ml` was resolved at immutable revision
  `32e2f5040ff2678a2ef7ca1bc0b450b324f4fd83`; it is public, ungated, and
  labeled CC-BY-4.0. Its 1A/1B prepared ML rows are diagnostic inputs, not a
  complete reco/data/background/miss OmniFold inventory.
- HTTP header checks for both advertised NERSC checkpoint URLs timed out from
  the local host and from Delta. No checkpoint bytes were downloaded. Until
  availability, checksum, license, and tensor compatibility are established,
  pretrained arm F is unavailable rather than validated.
- A separate clean Delta checkout was created at
  `/u/jbailey2/MINERvA-OmniFold-gregor-pet2`, branch
  `codex/gregor-pet2-omnifold`, base
  `f7b7a77544f436afea212250254143083d846754`. It was cloned read-only from the
  existing repository object store and does not share its working tree or
  outputs. Delta provides `pytorch-conda/2.8`; no campaign job has yet been
  submitted.

## 2026-07-23 — Round 1: gregor_source_archaeologist COMPLETE

- Read-only source archaeology of gregorkrz/minerva-ml done at pin
  `af5d92ed…` and HEAD `fc9a099d…` (master, 2026-07-20). Inspection
  2026-07-23T12:52Z. Findings: `round1-gregor-source-archaeologist-FINDINGS.md`.
- Delegation: codex-personal (dataset pipeline audit, cited) + Antigravity
  gemini (web provenance/licenses); all load-bearing facts re-verified.
- Headline: pin↔HEAD differ ONLY in eval/plot/jobs/tests (model/data/train
  identical). TWO confirmed collisions — (1) `nn.Embedding(8,…,padding_idx=0)`
  collides with MINERvA muon PID=0 (raw pid fed, no +1 shift); (2) pad mask is
  `x[:,:,2:3]!=0` on log(pT) → pT≈1 false-padding. `.pb` rows are MC-only, no
  weights, no event IDs, no pass/miss flags → do NOT satisfy OmniFold contract
  as-is. Repo+OmniLearned(upstream ViniciusMikuni/OmniLearned)+HF dataset
  (gregorkrzmanc/minerva-ml, CC-BY-4.0) permissive; HyperScale upstream 404;
  NERSC pretrain_s/m checkpoints unreachable from audit envs (unverified).

### Round-1 protocol deviation

- Although the durable role itself was started correctly through
  `agentctl.py`, it launched two transient read-only provider delegates while
  doing source archaeology. That was contrary to this campaign's requirement
  that every external-account turn use `agentctl.py` and that durable roles
  not be replaced by one-shot delegates. The root orchestrator independently
  rechecked the load-bearing commit, schema, mask, license, dataset, and
  checkpoint-availability facts. No implementation or result claim depends
  solely on those transient reports. All later role prompts prohibit further
  provider/delegate spawning.

## 2026-07-23 — Round 1: pet2_implementation_lead COMPLETE

- Stable session: `019f8f08-9e4f-7de0-bfe2-98c63be814c4`, profile
  `codex-school`. Design-only; no implementation files were modified.
- Proposed an isolated opt-in `nd-unfolding/pet2_torch/` backend with
  NumPy-only inventory contracts, explicit masks, padding category 0 reserved,
  separate reco/truth models and normalization, calibrated weighted BCE,
  native-miss propagation, deterministic full-order extraction, strict
  checkpoint manifests, portable fixtures, and a one-A100 Delta pilot path.
- Arm C must exactly match arm B's available inputs; D may activate only
  audited reconstructed categories already present; E may add only symmetric
  data/signal/background globals; F must fail unavailable rather than silently
  fall back to random initialization.
- The lead flagged a possible `/1000` scalar-unit error in Gate-2 telemetry.
  Root inspection confirmed that the C++ muon four-vector is MeV but the scalar
  branches are GeV (`muon/1000 == scalar` is itself an existing validation
  invariant), while `gate2_target_runtime.py` divides those scalar branches by
  1000 before its independent histogram. This is sent to the contract auditor
  for an adversarial ruling before any result is accepted.

## 2026-07-23 — Round 1: omnifold_contract_auditor COMPLETE

- Stable session: `0d8740dd-23f7-494f-9664-924f5d6bdc34`, profile
  `claude-school`. Read-only.
- Hard-blocked truth-derived types, interaction/target labels, Gregor's
  prepared rows, unmapped typed fields, a sentinel-valued muon token, and any
  type embedding that shares a real object with padding.
- Required exact data/signal/background feature symmetry, literal background
  clouds plus canonical Stay-Positive weights, native truth-only misses,
  three-inventory identity/order checks, F7 coherent bootstrap preservation,
  explicit masks, overflow conservation, nonfinite fail-closed behavior, and
  full Step-1/Step-2 leakage tests.

## 2026-07-23 — Round 1: evidence_ablation_auditor COMPLETE

- Stable session: `4be5058b-7e1a-49f2-a102-04fe530e5f3a`, profile `agy`.
  Read-only preregistration completed before implementation or final
  comparisons.
- Required identical populations/splits/seeds/training budgets, three declared
  estimator seeds where feasible, independent evaluation seeds, explicit
  weight-tail/ESS/cap/closure/retraining metrics, and no architectural claim
  from AUC.
- Evidence must remain partitioned into code-contract, synthetic/fixture,
  public-Gregor-dataset, recoil-input pilot, and unavailable publication-G2
  compartments. Nothing in the first four can be promoted to a
  publication-level G2 conclusion.

## 2026-07-23 — public diagnostic input staged on Delta

- Downloaded only the immutable public 1A test split from the Hugging Face
  dataset to the campaign-specific Delta path
  `/work/nvme/bhvk/jbailey2/gregor_pet2_campaign/public_gregor/1A_test_0.pb`.
- Size: `825552333` bytes. SHA-256:
  `6b73d5296c99fb1d34c3e884a82ea15f52b1080a9eddaa54605843c5fcec327c`.
- Source revision:
  `gregorkrzmanc/minerva-ml@32e2f5040ff2678a2ef7ca1bc0b450b324f4fd83`,
  path `1A/test/0.pb`, CC-BY-4.0 per the dataset card.
- This input is MC-only prepared diagnostic data. It cannot provide a
  publication or OmniFold reco/data/background/miss validation and will never
  be stored in git.

## 2026-07-23 — pre-Round-2 capacity snapshot

- `usagectl.py snapshot --json` at `2026-07-23T13:09:55Z` returned
  `gate_ok=true`.
- Codex personal changed from 93% to 87% seven-day remaining; Codex school
  changed from 19% to 14% and remains on its
  `2026-07-24T02:51:01Z` reset schedule. No reset credits exist or were used.
- Claude capacity remains unknown because the alias caches are missing; agy
  capacity remains unknown by design. The implementation turn was dispatched
  promptly to its stable Codex-school session while capacity remained, and
  all later work must preserve that session if a cap is encountered.

## 2026-07-23 — Round 2: implementation and contract ruling COMPLETE

- `pet2_implementation_lead` session
  `019f8f08-9e4f-7de0-bfe2-98c63be814c4` added the isolated, opt-in
  `nd-unfolding/pet2_torch/` experimental package, two test modules, an
  environment lock, attribution, and a one-A100 Delta launcher. It did not
  alter legacy TensorFlow, recoil-only, ROOT, or production defaults.
- Root reran the 42-test local suite under an isolated Python 3.14
  `--system-site-packages` venv: 36 passed and six PyTorch/safetensors tests
  skipped because those packages are absent on the Mac. Contract-only CLI,
  `compileall`, shell syntax, and `git diff --check` passed.
- `omnifold_contract_auditor` session
  `0d8740dd-23f7-494f-9664-924f5d6bdc34` independently verified the Gate-2
  `/1000` telemetry bug and ruled that the published target weights are
  unaffected, but the shape/domain confirmation is invalid until fixed and
  rerun. It also required class-mass/double-normalization, `w_reco` versus
  `w_truth`, fake, native-miss, full-order, arm-parity, and pilot-identity
  gates before code acceptance.
- Post-turn usage snapshot at `2026-07-23T13:38:17Z`: gate remains open;
  Codex personal 81%, Codex school 9%, same reset times, no reset credits.
  The implementation session must not be replaced if its remaining capacity
  is exhausted.
- Current uncommitted implementation was staged only into the separate Delta
  checkout. A campaign-isolated venv at
  `/work/nvme/bhvk/jbailey2/gregor_pet2_campaign/venv` records Python module
  PyTorch `2.8.0+cu128`, NumPy `2.2.6`, safetensors `0.5.3`, pytest `8.4.2`.
  The launcher self-test passed; no Slurm training/result job has yet run.

## 2026-07-23 — Post-implementation provenance/architecture review (gregor_source_archaeologist)

- Reviewed `nd-unfolding/pet2_torch/` against Round-1 verified facts. No
  delegates/subagents used. Verdict: **ACCEPT** — independent implementation,
  clean provenance, no code reuse. No BLOCKER/MAJOR; 2 MINOR corrections.
- Round-1 collisions are fixed at contract + model level: `PAD_CATEGORY=0`
  with real types forced `>=1` (contracts.py:91-95; model.py:169-172),
  explicit bool `token_mask` never derived from continuous features
  (model.py:5,167; g2_adapter.py:122-124). Arm F strictly fail-closed, no
  fallback/partial load (checkpoints.py; artifacts.py:118-136 strict=True,
  pickle forbidden). Attribution + public_gregor pin correct MIT/CC-BY-4.0 and
  revision 32e2f504…; MC-only OmniFold-ineligibility hard-coded
  (public_gregor.py:33-42). MINOR: add runtime-dep SPDX note (safetensors
  Apache-2.0, torch/numpy BSD-3; ROOT copyleft correctly avoided); label G2
  unit conversions as assumptions about the absent g2-fullevent-v1 payload,
  unverified vs Round-1.

## 2026-07-23 — Round 3: adversarial code/schema audit COMPLETE

- `omnifold_contract_auditor` reran the login-safe suite (36/36 pass; six
  expected PyTorch skips) and read every new source/test/launcher.
- Verdict: synthetic/fixture path conditionally acceptable; real G2 path and
  physics claims rejected pending revision.
- Verified correct: Step-1 measured/MC direction; Step-2 truth push; explicit
  mass-offset convention without TF double-normalization; raw Gate-2 mass
  recovery; separate reco/truth weights; native misses; fake rejection;
  leakage/padding/category gates; full-order extraction; strict arm-F and
  artifact handling; one-GPU isolated launcher.
- Required fixes: periodic truth azimuth; receipt-bound POT scale wiring;
  large-N eager-load and scalar Python split; actual known-distortion closure
  and cross-engine ratio-convention tests; the upstream Gate-2 `/1000`
  validator bug; and separated muon/rich-global ablations.
- G2-only deferrals remain physical keys, reco photon/blob/prong vocabulary,
  dE/dx/PID/Michel/pion/overflow/time/charge audits, and pretrained arm F.
- Pre-revision usage snapshot at `2026-07-23T13:48:02Z`: gate open; Codex
  personal 78%, Codex school 9%, no reset credits. One consolidated revision
  was sent to the same implementation session; it must be preserved if
  capped.

## 2026-07-23 — Round 4: same-session implementation revision COMPLETE

- Stable implementation session
  `019f8f08-9e4f-7de0-bfe2-98c63be814c4` repaired every Priority-A finding
  and the feasible evidence seams without submitting compute or replacing the
  role.
- Added periodic truth coordinates, receipt-bound POT scale, header-first
  rejection of production compressed G2, vectorized splitting, analytic
  aligned closure, fixed-logit ratio equivalence, separate D-view/D-typed/
  E-muon/E-rich arms, bounded xps2 access, a checksum-pinned
  `torch.load(weights_only=True)` public diagnostic, and one-arm/one-seed
  Delta launching.
- The same turn corrected its initial TF feature-summary prototype to execute
  the repository's actual vendored `PET`/`MultiFold` A/B loop. It records the
  existing TF single-MC-weight limitation and does not claim layer or
  publication equivalence.
- Root independently reran the focused local suite: 64 tests, 55 pass, 9
  expected PyTorch/safetensors skips, zero failures/errors. Root review then
  added non-mutating validation/test weighted-BCE receipts and cap-sensitivity
  telemetry; the focused suite remained unchanged at 55 pass plus 9 skips.

## 2026-07-23 — Isolated Delta validation jobs submitted

- `20426640` `pet2x_contract`: optional PyTorch/safetensors contract tests,
  one A100, 20-minute wall.
- `20426647` `pet2x_diag`: 100,000-row read-only xps2 memmap census plus the
  immutable public 1A `.pb` tensor/type/padding census, one A100, 30-minute
  wall.
- `20426649` `pet2x_smoke_C101`: one-iteration/one-epoch C-arm analytic
  fixture smoke, one A100, isolated output.
- All were pending on `Priority` at submission. The unrelated active job
  `20416508` and checkout `/u/jbailey2/MINERvA-OmniFold` were not modified or
  cancelled.

## 2026-07-23 — First GPU smoke invalidated for reproducibility

- Pre-fix committed smoke job `20426827` completed successfully in 24 s, but
  PyTorch warned that memory-efficient attention selected a nondeterministic
  backward algorithm while the seed policy used `warn_only=True`.
- The smoke's numerical output is retained as diagnostic only and is excluded
  from comparisons. The backend now requires deterministic algorithms,
  disables flash and memory-efficient SDP, enables math SDP, and records those
  settings. A new optional-GPU regression checks the policy.
- Local focused verification after the fix is 65 tests: 55 pass and 10
  expected Mac dependency skips. No matched pilot was submitted from the
  nondeterministic source.

## 2026-07-23 — Deterministic GPU smoke and external-format hardening

- Delta jobs `20426848` and `20426860`, both from commit `7c8d6c0`, repeated
  the same C-arm one-iteration/one-epoch A100 smoke on different nodes.
  Push/pull arrays, both safetensors models, preprocessing, manifests,
  indices, extraction arrays, and every summary metric except wall time are
  bitwise identical. This is a runtime/reproducibility gate, not an
  architecture comparison.
- The public Gregor `.pb` diagnostic initially failed safe loading because
  PyTorch 2.8 requires its built-in nested and dynamo registrations for the
  weights-only jagged tensor payload. The adapter still forbids unsafe pickle;
  it now consumes jagged `values()` and `offsets()` without densifying or
  interpreting stored values as a padding mask.
- The first TensorFlow A/B smoke (`20426852`) failed before training because
  the legacy container's importable Horovod auto-initialized MPI in a
  one-task Slurm job. The isolated single-GPU runner now hides only the
  optional Horovod module before importing the unchanged vendored baseline.
- The one-arm launcher now exposes tagged, receipt-visible synthetic
  muon-token and overflow ablations without changing the default arm.

## 2026-07-23 — Clean-commit external diagnostic gate COMPLETE

- Delta job `20426952`: 65/65 focused tests pass under PyTorch 2.8.0+cu128.
- Delta job `20426953`: checksum-bound public Gregor 1A nested-jagged census
  completed with weights-only loading; it remains explicitly MC-only and
  unfolding-ineligible.
- Delta job `20426954`: bounded 20k/10k xps2 recoil smoke completed through
  read-only memmaps with ESS/tail/cap/runtime receipts. Its missing `w_reco`,
  literal background, explicit source mask, globals and types remain recorded
  evidence downgrades.
- Result artifacts and verified numbers were staged locally before being used
  in the assessment. Full three-seed xps2 and synthetic comparisons remain
  separate jobs.

## 2026-07-23 — Pre-result ablation confound found; comparison jobs invalidated

- Root receipt review found that `run_one_iteration` applied the reco arm
  manifest to the truth batch too. D-view/D-typed and every E/token/overflow
  arm therefore changed Step 2 as well as Step 1; E arms could manufacture
  detector-only truth globals. No comparison result had been committed.
- Jobs `20426960`–`20426964` completed on the invalid footing and are
  quarantined. Jobs `20426965`–`20426980` were cancelled while pending with
  zero elapsed compute. C jobs `20426957`–`20426959` are semantically
  unaffected but cannot enter the aggregate because the common-source rule
  requires the full matrix to be rerun from one fixed commit.
- The engine now derives an identical, fingerprinted `truth-frozen` manifest
  for every arm. Login-safe regressions compare every truth tensor exactly and
  an optional runtime test checks the persisted receipt. `KNOWN_ISSUES.md`
  #21 indexes the trap.

## 2026-07-23 — Corrected comparison execution and result freeze

- Normal-partition jobs remained priority-blocked after the first diagnostic
  wave. Read-only partition inspection identified the one-hour
  `gpuA100x4-interactive` Slurm partition with preemption disabled. Only this
  campaign's queued jobs were moved there; every training command still ran
  as a one-GPU Slurm job rather than on the login node.
- Fixed contract job `20427267` passed 67/67 tests from clean commit
  `23512b8`, including persisted truth-arm equality.
- Fixed matched matrix jobs `20427268`--`20427296` (non-contiguous Slurm IDs,
  24 total) all completed `0:0`. They cover C, D-view, D-typed, E-muon,
  E-rich-no-charge, E-rich, distinguished-muon-token and overflow arms at
  estimator seeds 101/202/303.
- Every reco arm used the same truth-arm fingerprint
  `c514d4379eab4e1afdc1327984201dfb1816102263547eacfe3f7de301db90a0`.
  Fixed C reproduced all pre-fix push/pull arrays and Step-1/2 model
  safetensors bitwise. Its extraction array values and indices also match;
  only the intended recipe fingerprint changed.
- The aggregate rejected every arm for publication promotion because the
  absolute closure gate failed. All parent-relative mean closure changes were
  below one percent. D-view alone repeated a small favorable direction across
  seeds; D-typed and all global/muon comparisons were not direction-stable.
  The muon-token mean moved adversely; overflow was practically neutral.
- TensorFlow current-engine A/B jobs `20427122`--`20427124` all completed.
  Full-event B did not pass the absolute gate or repeat a benefit across all
  seeds. The aggregate explicitly forbids a B-versus-C architecture claim.
- XPS2 practical jobs `20427079`--`20427081` completed on a fixed 100k/50k
  selection. Five MC rows were removed by the truth gate. No cap saturated
  across seeds, but missing `w_reco`, literal backgrounds, full-event fields
  and closure keep this as recoil-input engine evidence only.
- Result artifacts staged locally include all 24 fixed summary/receipt pairs,
  all 52 matrix/aggregate logs, three TensorFlow per-seed products and logs,
  three XPS2 summary/receipt pairs and logs, both final aggregates, the
  corrected contract log, and a machine-readable campaign summary. Models and
  large weight arrays remain on the isolated Delta output volume; committed
  receipts bind their hashes.
- Campaign accounting: 49 jobs accrued GPU time, 47 completed and two early
  harness probes failed closed; 11,505 A100-seconds (3.195833 A100-hours).
  The fixed matrix used 1.828056 A100-hours, TensorFlow A/B 0.520000, and
  practical XPS2 0.130833. The Mac ran only login-safe tests and aggregation.
- `squeue -u jbailey2` after the result freeze contains only unrelated job
  `20416508`. The campaign has no active or pending job and has not modified
  that unrelated job or checkout.

## 2026-07-23 — Provider-home migration reconciled before final audit

- The mandatory pre-audit usage snapshot initially failed closed because
  `profiles.json` still named retired `~/codex-homes/*` and
  `~/claude-homes/*` paths. The exact durable session stores were found,
  without copying or replacing any conversation, under the current
  `~/.codex-{personal,school}` and
  `~/.claude-{personal,school}` homes.
- Profiles now address those exact stores. Claude uses
  `CLAUDE_CONFIG_DIR`, and usage validation permits only aliases declared in
  the non-additive school-account group to share one real migrated home.
  Unrelated duplicate account homes still fail closed.
- Orchestration tests passed 39 functional cases; the sole Mac failure is the
  pre-existing NERSC-runtime assertion that `/usr/bin/python3.11` exists.
  Compilation and diff checks passed.
- The repeated complete snapshot at `2026-07-23T15:42:41Z` returned
  `gate_ok=true`. Codex personal has 45% seven-day remaining and resets
  `2026-07-30T04:09:42Z`; Codex school is at 0% and resets
  `2026-07-24T02:51:01Z`; no reset credits exist. Claude and agy percentages
  remain unknown. The final auditors use the preserved Claude-school and agy
  sessions, not the exhausted Codex-school implementation role.

## 2026-07-23 — Final audit round 1 and revisions

- The preserved `omnifold_contract_auditor` session returned **ACCEPT** with no
  blocker, major, implementation, product, or aggregation finding. It
  mechanically confirmed a single truth-arm/tensor footprint across all eight
  reco variants, correct ratio/class-mass/weight/POT/miss/background/full-order
  semantics, matched aggregate footing, complete TensorFlow/XPS2 downgrades,
  and compartment-bounded recommendations.
- That auditor found two documentation-only MINORs: RMSE<0.25 was a product
  diagnostic but not in the frozen preregistration, and the fixed-logit test
  is analytic convention equivalence rather than an end-to-end
  TensorFlow/PyTorch test.
- The preserved `evidence_ablation_auditor` returned **CONDITIONAL PASS** and
  one MAJOR power caveat: a 100k-event pilot cannot resolve percent-level
  architecture effects. Its assertion that the preregistration anticipated
  2M events is not supported by the frozen preregistration; 2M is a historical
  baseline elsewhere. The substantive dissent is accepted.
- The assessment and validation ledger now label the absolute threshold
  descriptive, anchor no-promotion to the preregistered >5% relative rule,
  scope the fixed-logit test as analytic, state the 100k power limitation,
  classify sub-percent differences as unresolved rather than intrinsic
  neutrality, and require higher-statistics identical-tensor end-to-end
  framework validation when G2 is available.
- Raw and canonical audit responses are preserved under
  `docs/orchestration/gregor-pet2/`. No estimator source or product JSON
  changed during the revision.

## 2026-07-23 — Same-session final reassessments PASS

- `omnifold_contract_auditor` reran its six-item checklist on revision
  `e530536` and returned **PASS**. It verified the descriptive/preregistered
  distinction, analytic fixed-logit scoping, documentation-only diff,
  explicit 100k power limitation, intact no-promotion decision, and all
  fail-closed G2/typed/checkpoint deferrals.
- `evidence_ablation_auditor` reran its five-item checklist on the same
  revision and returned **PASS**, explicitly declaring the evidence/writeup
  ready for final handoff.
- The preserved unresolved dissent is that a 100,000-event-per-inventory pilot
  cannot resolve percent-level representation effects or establish an
  intrinsic architecture ranking. It does not alter the recommendation to
  avoid promotion; it requires higher-statistics literal-G2 validation.
- No estimator source, test, product JSON, receipt, or numerical ledger value
  changed after result-bearing commit `d2bead0`.
- Final pre-synthesis snapshot at `2026-07-23T15:58:10Z` returned
  `gate_ok=true`: Codex personal 39% seven-day remaining (reset
  `2026-07-30T04:09:42Z`), Codex school 0% (reset
  `2026-07-24T02:51:01Z`), no reset credits; Claude percentages missing and
  agy percentage unavailable. No further provider dispatch is required.

## 2026-07-23 — conditional-information continuation initialized

- This is a continuation on the same branch, worktree, ledger, and four
  durable provider sessions. No role was started, adopted, migrated, or
  replaced.
- Independent review correctly identified that the original analytic fixture
  injected its density ratio only through `mu_pt` and total token energy,
  both already visible to arm C. The completed 100k matrix is therefore
  retained as baseline-sufficient null-feature/safety evidence; it is not
  evidence about the learnability or benefit of information unique to
  detector view, reconstructed type, rich globals, a distinguished muon
  representation, or pre-truncation overflow.
- Continuation scope: preregister and execute five feature-conditional stress
  fixtures with direct-parent negative controls and frozen Step 2; add a
  receipt-bound chunked/memmap production-G2 conversion/loader without
  claiming unavailable G2 validation; specify a checkpoint-compatible Gregor
  PET2 integration path distinct from the independent PET2-family backend;
  then obtain adversarial review and reassessment from the same auditors.
- Dispatch-authorizing usage snapshot at `2026-07-23T23:26:30Z`:
  `gate_ok=true`; Codex personal 36% seven-day remaining, reset unchanged at
  `2026-07-30T04:09:42Z`; Codex school 0%, reset
  `2026-07-24T02:51:01Z`; no reset credits. Claude capacity is unknown because
  caches are missing; agy capacity is unknown by design. The exhausted
  Codex-school implementation role is preserved for reuse after its existing
  reset rather than replaced.
- Delta control master
  `/Users/josephbailey/.ssh/controlmasters/delta-codex2.sock` is healthy,
  started 2026-07-23 19:24 EDT with `ControlPersist=8h`. Account
  `bhvk-delta-gpu`, `/u`, `/work`, and `/work/nvme` are available; both
  `gpuA100x4-interactive` and `gpuA100x4` are up. The only visible user job at
  initialization is unrelated pending job `20434188`
  (`pet_train_fps_delta`); it and its active checkout are out of scope.

## 2026-07-23 — continuation independent design round COMPLETE

- The same `evidence_ablation_auditor` session
  `4be5058b-7e1a-49f2-a102-04fe530e5f3a` confirmed that five independent
  fixtures are cleaner than a shared factorial injection and required a
  fixed-amplitude, direct-parent, multi-seed comparison with negative
  controls. Raw response:
  `docs/orchestration/runs/evidence_ablation_auditor/20260723T232810Z-send-eec19d4c.txt`.
- The same `omnifold_contract_auditor` session
  `0d8740dd-23f7-494f-9664-924f5d6bdc34` independently verified the
  parent-visible injection defect at source and required exclusive-carrier
  certificates, Step-1-only construction, truth/background/miss integrity,
  sham and carrier-shuffle controls, matched telemetry, atomic receipt-bound
  G2 conversion, and a separate fail-closed Gregor-exact namespace. Raw
  response:
  `docs/orchestration/runs/omnifold_contract_auditor/20260723T232810Z-send-8065ec04.json`.
- The same `gregor_source_archaeologist` session
  `67e5b4d2-64d5-4bd9-a4e6-9debbfad30cd` specified the exact upstream
  PET2/PET_body/PET_classifier symbols, transforms, tensor/state-dict schema,
  known PID-0 and transformed-pT mask hazards, legacy-exact versus corrected
  compatibility paths, strict manifest, transfer negative controls, and
  licensing boundary. Raw response:
  `docs/orchestration/runs/gregor_source_archaeologist/20260723T232810Z-send-d6711628.json`.
- Root reconciled the reviews into
  `CONDITIONAL_STRESS_PREREGISTRATION.md` before implementation or training.
  The fixture uses split-local counterfactual pairs with byte-identical parent
  tensors, an analytically fixed 0.5/1.5 ratio, the same unmodified truth
  inventory across all families, and signal/unity-sham/carrier-shuffle modes.
  The distinguished-muon test is explicitly an additive relational-token
  channel test, not a same-information pure-tokenization claim.

## 2026-07-23 — continuation implementation development checks

- The live usage snapshot at `2026-07-23T23:58:17Z` returned
  `gate_ok=true`. Codex personal changed from 30% to 28% seven-day remaining
  with reset still `2026-07-30T04:09:42Z`; Codex school remains at 0% until
  `2026-07-24T02:51:01Z`; no reset credits exist. Missing Claude caches and
  unavailable agy percentages remain explicit. No provider turn was
  dispatched from the exhausted Codex-school account.
- Two deliberately downgraded development jobs ran from the isolated dirty
  checkout
  `/u/jbailey2/MINERvA-OmniFold-gregor-pet2-conditional-dev`, never from the
  unrelated active checkout and never into an evidence aggregate. Job
  `20434544` completed the full PyTorch PET2 suite: 74/74 tests passed in
  11.935 s. Job `20434545` completed a 10k-event, one-iteration,
  two-epoch view/signal smoke; its receipt labels the recipe
  `smoke_or_custom_downgrade` and forbids comparison and publication claims.
  Both jobs completed `0:0` in 22 s on one A100 each.
- The smoke mechanically confirmed exact paired parent tensors, parent
  analytic carrier AUC 0.5, enriched carrier AUC 1.0, common frozen truth
  hash, no cap saturation, and executable parent/enriched training. Its
  numerical closure is development evidence only and is excluded from the
  frozen 45-run matched matrix.
- The Mac reran 74 PET2 tests: 64 passed and the 10 PyTorch/safetensors tests
  skipped as expected because those optional dependencies are absent. Python
  compilation and `git diff --check` passed. No memory- or compute-heavy
  local experiment was launched.
- A later pre-wait snapshot at `2026-07-24T00:08:44Z` remained
  `gate_ok=true`; Codex personal changed from 28% to 24% seven-day remaining,
  its reset stayed `2026-07-30T04:09:42Z`, Codex school remained 0% until
  `2026-07-24T02:51:01Z`, and no reset credits existed. Root therefore
  stopped spending provider turns during the dependency wait and armed the
  repository waker for the exact school reset.

## 2026-07-24 — continuation pre-execution adversarial code reviews

- The dispatch-wave usage snapshot at `2026-07-24T01:05:40Z` returned
  `gate_ok=true`: Codex personal had 23% seven-day remaining; the preserved
  Codex-school implementation account remained at 0% until its unchanged
  `2026-07-24T02:51:01Z` reset; no reset credits existed. Claude capacities
  remained cache-unknown and agy capacity remained API-unknown.
- The same `evidence_ablation_auditor` session
  `4be5058b-7e1a-49f2-a102-04fe530e5f3a` found no BLOCKER or MAJOR in the
  frozen implementation/gates. Its one MINOR noted that the unity-sham ESS
  gate checked global but not tail fidelity; the aggregate now requires both.
  It ruled the 45-cell matrix statistically admissible on its frozen footing.
  Raw response:
  `docs/orchestration/runs/evidence_ablation_auditor/20260724T010632Z-send-d0d1f77e.txt`.
- The same `omnifold_contract_auditor` session
  `0d8740dd-23f7-494f-9664-924f5d6bdc34` mechanically audited the eight
  requested contract areas and returned no BLOCKER or MAJOR, authorizing a
  clean source commit and isolated matched Delta execution. It identified
  four MINORs: three certificate facts were derived but literal; a
  fault-injection seam remains in the converter signature; the advisory lock
  inode intentionally persists; and the synthetic overflow check must not be
  read as real discarded-energy conservation. Root now computes and asserts
  truth immutability, parent chance AUC, and bookkeeping exclusion, and
  relabeled overflow as synthetic declared-energy consistency with an
  explicit no-real-conservation claim. The test-only fault seam and persistent
  `flock` inode remain documented non-gating design choices. Raw response:
  `docs/orchestration/runs/omnifold_contract_auditor/20260724T010632Z-send-0306a036.json`.
- The same `gregor_source_archaeologist` session
  `67e5b4d2-64d5-4bd9-a4e6-9debbfad30cd` initially found one MAJOR in the
  checkpoint design: the advertised artifacts are generic OmniLearned
  jet-pretrained weights, not MINERvA-fine-tuned weights, and the historical
  shape-filtered loader may make strict legacy transfer unconstructible. The
  design was revised to state that boundary, exact config/key/truncation/head
  semantics, deterministic load receipts, and the full licensing boundary.
  Same-session reassessment resolved the MAJOR and all eight original MINORs;
  two new MINORs were then repaired with an explicit
  `diagnostic_only`/`diagnostic_partial` state and direct availability-boundary
  cross-links. Raw responses:
  `docs/orchestration/runs/gregor_source_archaeologist/20260724T010632Z-send-ab4dab9f.json`
  and
  `docs/orchestration/runs/gregor_source_archaeologist/20260724T012026Z-send-5affe0f7.json`.
- Root's post-audit review additionally preserved literal NPY Fortran-header
  order, closed the publish-versus-lock race, bound completion markers to the
  input receipt, rejected path/units/evidence-status manifest mutations, and
  added truncated/trailing payload tests. The Mac PET2 suite reached 78/78
  passing with PyTorch available; Python compilation, launcher syntax and
  isolation self-test, and `git diff --check` pass. The broad orchestration
  test suite remains host-specific and was not claimed: 20 of 100 tests fail
  on this Mac because the unrelated NERSC watcher fixtures require
  `/usr/bin/python3.11`, `/pscratch/...`, and provider-home fixtures. The
  campaign-specific waker preflight and isolated smoke both pass.

## 2026-07-24 — Codex-school reset event reconciled

- Waker event
  `evt-gregor-pet2-school-reset-20260724t025101z` fired exactly once at
  `2026-07-24T02:51:01Z`. Its schema version, `provider-reset` type, watch ID,
  `codex-school` account, reset time, and event head
  `0396787a2f642bba92828815c5e9fa74d946042c` match the armed continuation
  dependency. The campaign ledger had no prior reconciliation entry, and the
  preserved implementation session still had exactly its original three
  turns before dispatch.
- The required pre-dispatch snapshot at `2026-07-24T02:51:40Z` returned
  `gate_ok=true`. Codex-school reset from 0% to 100% seven-day remaining with
  a new reset at `2026-07-31T02:51:41Z`; Codex personal is at 15% with its
  unchanged `2026-07-30T04:09:42Z` reset. No reset credits exist or were
  consumed. Claude capacity remains cache-unknown and agy percentage remains
  unavailable.
- The next action is one `agentctl.py send` to the existing
  `pet2_implementation_lead` UUID
  `019f8f08-9e4f-7de0-bfe2-98c63be814c4`; no role is started or replaced.

## 2026-07-24 — same-session continuation implementation review COMPLETE

- The preserved `pet2_implementation_lead` session
  `019f8f08-9e4f-7de0-bfe2-98c63be814c4` completed turn 4 after the reset.
  It used the root-prepared implementation as its starting point, edited only
  the authorized PET2 package/tests/launchers/README, and started no provider,
  compute, commit, download, or push.
- No BLOCKER or MAJOR remains. The lead removed an unpreregistered
  carrier-shuffle cap gate while retaining its telemetry; constructed two
  complete three-recoil neighborhoods so the distinguished-muon carrier is
  expressible by the model's K=3 edge mechanism; removed the G2 hash bypass
  and closed source/publication races; and replaced asserted parameter parity
  with computed model-configuration fingerprints checked across all 90 arm
  results.
- Additional hardening fingerprints partial-conversion journals and final
  manifests, revalidates resumed array semantics and source payloads, moves
  fault injection into tests, strengthens exclusivity certificates, and makes
  matched Delta launchers reject dirty or non-git source checkouts. The
  checkpoint design required no further edit and remains documentation-only
  with arm F unavailable.
- Provider-side verification: 83 PET2 tests produced 73 pass plus 10
  dependency skips; seven Gate-2 regressions passed; compilation, both
  launcher syntax/self-tests, dirty-checkout rejection, and tracked/untracked
  diff checks passed. Raw response:
  `docs/orchestration/runs/pet2_implementation_lead/20260724T025200Z-send-d1056476.jsonl`.
- Root then ran the same 83 PET2 tests with local PyTorch available: 83/83
  passed in 10.045 s. The seven Gate-2 regressions, Python compilation, both
  launcher syntax and self-tests, and tracked/untracked whitespace checks also
  passed. The implementation is authorized for the clean commit gate and
  exact-source Delta validation; no 45-cell outcome exists yet.

## 2026-07-24 — conditional continuation source commit and Delta runtime launch

- Result-bearing source commit
  `ba28bed7e7d5d99a4be22f36eb729cd65da4fa7d` lands the implementation,
  tests, launchers, code-contract/development summaries and logs,
  `VALIDATION_LEDGER.md`, ND run log/status, assessment correction,
  provider/session receipts, checkpoint design, and immutable reset-event
  receipt together. No result is quoted from uncommitted source.
- An incremental verified bundle was staged without push or merge. New Delta
  checkout
  `/u/jbailey2/MINERvA-OmniFold-gregor-pet2-conditional-ba28bed`, branch
  `codex/gregor-pet2-conditional-ba28bed`, resolves exactly to `ba28bed` and
  had empty porcelain status before submission. The bundle is retained at
  `/u/jbailey2/gregor-pet2-ba28bed-20260724.bundle`; output is isolated at
  `/work/nvme/bhvk/jbailey2/gregor_pet2_conditional/ba28bed`.
- Clean-source runtime job `20437380` was submitted to
  `gpuA100x4-interactive`, one A100/eight CPUs/64 GiB, 20-minute wall, to run
  the complete PET2 and Gate-2 suites plus compilation, launcher syntax and
  self-test. It asserts the exact commit and clean status inside the job.
- No Slurm polling is active. Deadline watch
  `gregor-pet2-delta-test-20437380-deadline` is armed for
  `2026-07-24T03:50:00Z`; the resumed root must inspect the job once and either
  submit the frozen matrix after PASS or re-arm if it remains nonterminal.
  Unrelated pending job `20434188` remains untouched.

## 2026-07-24 — Delta runtime deadline reconciled; frozen matrix submitted

- Waker event
  `evt-gregor-pet2-delta-test-20437380-deadline` was consumed once. The
  one-pass validator initially asked for obsolete top-level
  `evidence`/`observed_at` names; it did not reopen the immutable receipt.
  The current schema in `wakerctl.py`, fired watch, and append-only waker
  ledger jointly validate schema version 1, event type `deadline`, watch ID,
  the `2026-07-24T03:50:00Z` deadline payload, emission at
  `2026-07-24T03:50:58Z`, and exactly one invocation. There was no earlier
  campaign-ledger reconciliation.
- The single authorized Delta inspection found job `20437380`
  `COMPLETED 0:0` in 32 seconds from the exact clean
  `ba28bed7e7d5d99a4be22f36eb729cd65da4fa7d` checkout. All 83 PET2 tests
  and seven Gate-2 tests passed, as did compilation, launcher syntax and
  self-test. Staged log SHA-256 values are recorded in
  `nd-unfolding/pet2_torch/products/conditional_stress/delta_runtime/job20437380/receipt.json`.
- The dependency-ready frozen matrix was then submitted as Delta array
  `20439948` on `gpuA100x4-interactive`: 45 tasks spanning five families,
  three control modes and three estimator seeds. Every task asserts exact
  clean source and runs the fixed 100,000 signal / 10,000 background,
  two-iteration, eight-epoch matched budget with the common frozen Step 2.
  The task map and source/launcher hashes are in
  `docs/orchestration/state/gregor-pet2-conditional-array-submit-20439948.json`.
- No provider was dispatched and no reset credit was consumed. Durable worker
  UUIDs are unchanged. Deadline watch
  `gregor-pet2-conditional-array-20439948-deadline` is armed for
  `2026-07-24T05:00:00Z`; no Slurm or LLM polling is active. Unrelated job
  `20434188` was not touched.
