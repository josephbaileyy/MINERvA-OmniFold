# SCOPING (v2): an added uncertainty for the sixteen-cell fake-data bias (tier3-design, 2026-11-27)

**Status: a plan only, for v2.** No declaration, no code and no compute exist or are authorized by this file. Each step
below needs its own declaration and the director's binding before it runs.

**MEASURES:** nothing. **CANNOT AUTHORIZE:** any compute, any change to a reported covariance, any note or paper wording.

The `fd/` paths are under `docs/orchestration/state/measurement-paper/5d-community-20261024/`.

## Provenance

1. **The pricing.** tier3-design's v2 pricing note to the director, 2026-11-27, "v2 pricing: T2K-style fake-data bias
   uncertainty". It listed the inputs, four method options (second-moment block, T2K envelope, a refit of B5D's C_b, a
   scalar on C_model), three validation tiers (V1 leave-one-truth-out, V2 held-out truths and the REGRADE-VF split, V3
   fresh truths on NERSC), node-h from the committed F0b and F1 charges, and a calendar. It left one question open:
   how to treat the alternative truths that overlap C_model's generator families.
2. **The reader.** An unanchored read of that pricing by codex-school2 (gpt-6.2-sol, high effort), run by the
   director, read at main a0c6c6bb. Its report and prompt are committed verbatim beside this file:
   `reads/codex2-pricing-read.txt` (sha256 `a24f7dcd428cffdd9bc9a4ede583c7c53ea54f6aa6ec86fcc7145aa30a902883`) and
   `reads/codex2-pricing-prompt.txt` (sha256 `ac5cac7e49f68c6d117103a754336cd2f80f5762daadffb01bf8f65066f4ab64`),
   copied byte for byte from the director's scratchpad (the report was `report.md` there; it is saved as `.txt`).
   Their bytes are unchanged, so the read's main commit is recorded here rather than in their headers. Its
   recommendation, as the director relayed it, is item 3.
3. **The decision.** Joseph, 2026-11-27, relayed by the director: "lets agree with the recommendation". The
   recommendation, as the director relayed it:
   - Option 1 (the second-moment block) is built as a prototype and is not added to the reported uncertainty until it
     is validated. It uses signed residuals, the uncentered second moment and the full covariance of each estimated
     mean. Family weights are fixed in advance, so that repeated variants and noise-free counterparts do not get
     extra votes.
   - First, a diagnosis step: how much of the known joint undercoverage is mean bias and how much is underestimated
     scatter. REGRADE-VF's split (item 4) is one input.
   - For truths that overlap C_model: replace the overlapping C_model contribution rather than adding to it, and
     account for the correlation between the prior shift and the residual bias. The director's ruling: this settles
     the pricing's open family question as "net out/replace"; the director told Joseph so and will correct this file
     if Joseph says otherwise.
   - The envelope (option 2) and the scalar (option 4) are sensitivity checks only. The refit of C_b (option 3) is
     done only if it predicts held-out families.
   - Validation: V3 (fresh generator families, end-to-end pseudo-experiments, about 2–4 node-h) is REQUIRED, not
     optional. It checks joint, per-cell and projection coverage, and widths. If the term passes only with broad
     inflation, that is reported instead of the term being adopted.
4. **Input from v1.** REGRADE-VF (`fd/regrade-vf-20261127/`, PR #1428, merged at 5f0f4504): the debiased
   bias/fluctuation split of LL5D's held-out-tune draws under C_rep with C_e^infl. Its §5 circularity applies to any
   reuse: those draws are the ones C_e^infl's factors were fitted to (spread only).

## The plan, in order

### Step 0: diagnosis (local, 0 node-h)

Split the known joint undercoverage into mean bias and underestimated scatter, per held-out truth and band variant,
before any term is built. Inputs: REGRADE-VF's B, F and τ; LL5D's joint and per-cell counts (`fd/receipts-ll5d/`);
F1's per-tune bias (`fd/readout/fd_f1_readout.json`). The diagnosis says which part an added bias term could address.
It is not itself a coverage result.

### Step 1: the prototype term (local, 0 node-h)

- **The build set:** F0b's graded truths and its P-truths (`fd/with-vf/readout/vf-with-S/fd_f0b_readout.json`), each
  with its signed 16-cell residual b_k and the full covariance of its estimated mean.
- **The estimator:** the uncentered second moment of the signed residuals, with each truth's estimated-mean covariance
  netted out (the debiasing), under family weights fixed in the declaration before any residual is read. Repeated
  variants within a family and noise-free counterparts share their family's weight.
- **Overlap with C_model:** for the truths in C_model's generator families, the overlapping C_model contribution is
  replaced, not added to. The declaration must state how the correlation between a truth's prior shift and its
  residual bias is handled.
- **Sensitivity only:** the per-cell envelope (option 2) and a scalar on C_model (option 4), printed beside the
  prototype. The refit of B5D's C_b (option 3) enters only if it predicts the held-out families.
- The prototype is not added to the reported covariance at this step.

### Step 2: validation

- **V1 (local):** leave one family out, recording each left-out family's bias χ² and per-cell z under C_rep plus the
  prototype built without it.
- **V2 (local):** truths the build never saw. These are F1's G18 and AR23 biases, and REGRADE-VF's split rerun with
  the prototype added, on LL5D's draws. The bias reading is fair there; the fluctuation reading stays circular.
- **V3 (NERSC, REQUIRED):** fresh generator families never used in the build, run end to end with pseudo-experiments,
  at about 2–4 node-h. Candidates are other GENIE v3 tunes and NuWro or GiBUU variants. The pass criteria cover joint,
  per-cell and projection coverage and the interval widths, all fixed in the declaration. (b)'s sealed PV truths
  (u = 0, 1, 2) are excluded: they are (b)'s held-out test.
- **The adoption rule:** the term is proposed for the reported covariance only if it passes V3 without broad
  inflation. If it passes only with broad inflation, the record reports that instead, and the term is not adopted.

## Cost and calendar (from the pricing)

- Steps 0–2 without V3: 0 node-h, about 1.5–2 days of declaration, code, tests and mutants, one read, run and receipt.
- V3: about 2–4 node-h with two to four new generator families (F1's two GENIE v3 tunes charged 1.88 node-h including
  generation; F0b's 18 reweighted truths charged 1.33). About 2–3 more days for binding, fences, the run and the fetch.
- About 4–5 working days in total.

## Open before the first declaration

- The family list and the fixed weights.
- The replacement rule for C_model's overlapping contribution, and the correlation treatment.
- V3's families, the number of pseudo-experiments per family, and the pass criteria.
