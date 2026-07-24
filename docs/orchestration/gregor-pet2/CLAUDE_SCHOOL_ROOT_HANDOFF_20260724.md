# Claude School root handoff — Gregor PET2 continuation

Act as the interim **root orchestrator** for the existing Gregor PET2
conditional-information continuation. This is a provider handoff to conserve
the canonical Codex root's nearly exhausted personal-account capacity. It is
not a new campaign, not a replacement auditor, and not authorization to repeat
the broad first campaign.

Work only in:

`/Users/josephbailey/local-research/MINERvA-OmniFold-gregor-pet2`

The branch is `codex/gregor-pet2-omnifold`. Preserve its history, existing
worktree, campaign ledger, products, and durable provider sessions. Do not
work from the neighboring main checkout. Do not push, merge, rewrite history,
or touch unrelated work.

## Mandatory operating rules

Use the repository's `persistent-orchestrator` skill. Read these completely
before acting:

- `AGENTS.md`
- `.agents/skills/persistent-orchestrator/SKILL.md`
- `docs/orchestration/WAKER.md`
- `docs/orchestration/gregor-pet2/CAMPAIGN_LEDGER.md`
- `docs/GREGOR_PET2_OMNIFOLD_ASSESSMENT.md`
- `docs/GREGOR_PET2_CHECKPOINT_COMPATIBILITY_DESIGN.md`
- `docs/orchestration/gregor-pet2/CONDITIONAL_STRESS_PREREGISTRATION.md`
- `VALIDATION_LEDGER.md`
- `nd-unfolding/ND_OMNIFOLD_STATUS.md`
- the tail of `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`
- `docs/orchestration/state/sessions.json`
- the current campaign waker status and the submission/failure/recovery
  receipts named below.

Run `orchestration/usagectl.py snapshot --json` before any provider-dispatch
wave. Codex Personal was at 2% seven-day remaining at
`2026-07-24T05:22:28Z`; conserve it. Codex School was at 91%. Claude capacity
was cache-unknown and agy exposes no percentage. Never consume a reset credit.
Goals remain disabled.

Use `orchestration/agentctl.py send` for every later turn to an existing
durable worker. Do not use raw Claude/Codex/agy one-shot commands, start
duplicate roles, adopt replacement sessions, or send to the historical
`interim-root` role. Preserve these exact identities:

- `gregor_source_archaeologist`, Claude Personal:
  `67e5b4d2-64d5-4bd9-a4e6-9debbfad30cd`
- `pet2_implementation_lead`, Codex School:
  `019f8f08-9e4f-7de0-bfe2-98c63be814c4`
- `omnifold_contract_auditor`, Claude School:
  `0d8740dd-23f7-494f-9664-924f5d6bdc34`
- `evidence_ablation_auditor`, agy:
  `4be5058b-7e1a-49f2-a102-04fe530e5f3a`

You are the interim root, not the `omnifold_contract_auditor`. Keep that
existing Claude School session independent and adversarial; contact it only
through `agentctl.py send` after result artifacts and the revised assessment
are ready. Do not silently edit on an auditor's behalf.

External waiting belongs to `wakerctl.py`, never model polling or sleep loops.
Before changing waker routing, prove that no resume is in flight. The current
runtime config still points to the canonical Codex root. If you can
authoritatively identify your own Claude session UUID, you may migrate the
runtime root to provider `claude`, profile `claude-school`, and that UUID,
then run campaign-specific `preflight` and `smoke`. Never guess a UUID. If a
safe root migration is not possible, leave the existing armed watch intact
and give the user a precise manual continuation instruction rather than
disarming the only wake path.

## Exact state at handoff

Recheck all of this; timestamps and jobs can advance.

- Branch head at `2026-07-24T05:22:27Z`:
  `9f38ef3` (`Refresh PET2 recovery live state`).
- The result-bearing implementation/source commit is immutable
  `ba28bed7e7d5d99a4be22f36eb729cd65da4fa7d`.
- Subsequent commits record launch, failure, and recovery control state:
  `60ffd57`, `48eb705`, `02d14fd`, `7066aef`, `9f38ef3`.
- The local worktree was clean at handoff. Inspect before editing and preserve
  every user/campaign change.
- Local source validation is 83/83 PET2 tests plus 7/7 Gate-2 regressions.
- Clean Delta runtime job `20437380` passed the same tests from exact commit
  `ba28bed` in 32 seconds.
- Initial matrix array `20439948` failed closed before training because
  Delta's `safetensors 0.6.2` did not match reviewed lock `0.5.3`. It produced
  zero scientific summaries/arm results. All 90 logs and a failure receipt
  were committed in `02d14fd`.
- Recovery array `20441096` resubmitted all and only the same 45 cells with
  the sole changed execution input being the isolated
  `safetensors==0.5.3` overlay:
  `/u/jbailey2/pet2-venvs/ba28bed-safetensors053`.
- At `2026-07-24T05:16:42Z`, recovery tasks 15–44 were visible RUNNING;
  earlier tasks had left `squeue` and must be adjudicated from accounting,
  logs, and products rather than assumed complete.
- The recovery deadline watch
  `gregor-pet2-conditional-array-20441096-deadline` is armed for
  `2026-07-24T06:15:00Z`. Read and reconcile its immutable event exactly once
  if it has fired. Do not create a duplicate watch or duplicate inspection.
- Delta SSH is currently healthy:

  `ssh -S /Users/josephbailey/.ssh/controlmasters/delta-codex2.sock jbailey2@login.delta.ncsa.illinois.edu`

- Delta account: `bhvk-delta-gpu`.
- Exact clean source checkout:
  `/u/jbailey2/MINERvA-OmniFold-gregor-pet2-conditional-ba28bed`
- Isolated output:
  `/work/nvme/bhvk/jbailey2/gregor_pet2_conditional/ba28bed`
- Unrelated job `20434188` (`pet_train_fps_delta`) is out of scope. Never
  cancel it, edit its checkout, or overwrite its output.
- Machine receipts:
  - `docs/orchestration/state/gregor-pet2-conditional-array-submit-20439948.json`
  - `docs/orchestration/state/gregor-pet2-conditional-array-recovery-submit-20441096.json`
  - `nd-unfolding/pet2_torch/products/conditional_stress/delta_runtime/job20439948_failure_receipt.json`
  - `nd-unfolding/pet2_torch/products/conditional_stress/delta_runtime/job20437380/receipt.json`

## Scientific and evidence boundaries

The completed original 100k matrix is now correctly labeled a
**baseline-sufficient null-feature test** because its injected ratio depends
only on C-visible `mu_pt` and total token energy. Its sub-percent D/E/token/
overflow differences are safety/null evidence, not a unique-information
test.

The recovery matrix is the preregistered five-family channel-capacity test:

- families: detector view, reconstructed type, rich globals, additive
  distinguished-muon geometry, and overflow;
- modes: signal, unity-sham, carrier-shuffle;
- seeds: 101, 202, 303;
- exactly 45 jobs, each containing matched parent and enriched arms;
- 100,000 signal and 10,000 background rows, two iterations, eight epochs,
  matched rows/splits/budgets, literal signed-background provenance, native
  misses, and a common truth-frozen Step 2.

Every product is `synthetic-fixture` evidence with
`g2_validation_claim=false` and
`publication_promotion_permitted=false`. A passing family proves only that the
channel can transmit an injected conditional through this harness. It does
not prove that MINERvA data contains that conditional, improve publication
closure, or justify feature adoption.

The production G2 NPZ remains literally unavailable on this Mac and Delta.
The receipt-bound chunked/memmap converter and loader are code-contract
evidence only. Do not claim G2 validation.

The checkpoint-compatible Gregor PET2 document is a concrete design separate
from `independent-pet2-small-concept-match-v1`. Advertised generic OmniLearned
jet-pretrained artifacts are not MINERvA-fine-tuned weights. No licensed,
accessible, hashed, strictly compatible weight exists; arm F remains
`unavailable`. Do not claim pretrained evidence.

## Dependency-ready continuation

When the recovery watch fires, or if it has already fired:

1. Validate the waker event and ledger it once. Perform one bounded Delta
   inspection of array `20441096` using scheduler accounting plus output
   artifacts. Do not infer success from missing `squeue` rows.
2. Require exactly 45 unique complete cell summaries and 90 arm results from
   exact clean source `ba28bed`, with no dirty/mixed source or mixed footing.
   If any cell failed, first write and commit a failure/recovery receipt, then
   relaunch only failed cells with unchanged science/configuration. Never
   outcome-select or silently omit a cell.
3. Stage locally all small summaries, receipts, task maps, checksums and
   stdout/stderr logs. Large model weights may remain on Delta only if their
   exact paths and hashes are receipted. Stage everything needed to reproduce
   the aggregate before the SSH socket expires.
4. Run
   `pet2_torch.aggregate_conditional_stress` on the complete staged inventory.
   Its fail-closed gates must reject incomplete, dirty, mixed-source, or
   mixed-footing products. Do not alter the frozen preregistration after
   seeing outcomes.
5. Inspect signal recovery, both negative controls, pull/push RMSE and bias,
   ESS and declared-tail ESS, cap-10/cap-30 count and weight mass, cap
   sensitivity, projections, tails, runtime, throughput and GPU memory for
   every family/seed. Training AUC is not acceptance evidence.
6. Make a result-bearing commit that carries the product summary and the
   appropriate `VALIDATION_LEDGER.md`, `ND_OMNIFOLD_RUN_LOG.md`,
   `ND_OMNIFOLD_STATUS.md`, assessment, known-issue status, and campaign
   ledger updates together. Do not quote uncommitted results.
7. Send the committed results and revised assessment to the same
   `omnifold_contract_auditor` and `evidence_ablation_auditor` sessions with
   `agentctl.py send`. Require adversarial post-results review, repair any
   findings, and send revisions back to those same sessions for final
   reassessment. Preserve unresolved dissent rather than averaging it away.
8. Finalize `docs/GREGOR_PET2_OMNIFOLD_ASSESSMENT.md` with evidence-level
   labels, exact include/exclude/defer decisions, checkpoint/licensing
   boundary, G2 loader status, auditor findings, and exact next steps when
   literal G2 is recovered. Verified numbers live only in
   `VALIDATION_LEDGER.md`; index them elsewhere.
9. Finish only when the worktree is clean, all campaign commits are coherent,
   all feasible products are staged, no campaign job is active or
   unmonitored, stale watches are reconciled/disarmed, unrelated work remains
   untouched, and the final handoff reports branch, commits, tests, Delta
   jobs/paths/resource use, conclusions and blockers.

The likely scientific conclusion remains conservative unless the committed
evidence says otherwise: channel-capacity success is not real-MINERvA benefit;
typed/rich/muon/overflow adoption and pretrained initialization remain
deferred pending symmetric reconstructed inventories and literal G2 closure.
Do not change the recommendation merely because an injected feature is easy
to learn.
