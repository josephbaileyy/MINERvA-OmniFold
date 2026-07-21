# Reference note — Gregor Krzmanc's MINERvA foundation-model work and what it suggests for us

2026-07-16. Input for orchestrator brainstorming, not a task list. Sources:
paper [arXiv:2604.12364](https://arxiv.org/abs/2604.12364) (Krzmanc, Mikuni,
Nachman, Wilkinson), repo [gregorkrz/minerva-ml](https://github.com/gregorkrz/minerva-ml)
([DATASET.md](https://github.com/gregorkrz/minerva-ml/blob/af5d92ed2b3b448a09b6b7cf6b4f179e5757b4ed/DATASET.md),
[MODELS.md](https://github.com/gregorkrz/minerva-ml/blob/af5d92ed2b3b448a09b6b7cf6b4f179e5757b4ed/MODELS.md)),
HF dataset `gregorkrzmanc/minerva-ml`. Gregor is in our lab — ask him directly
before reverse-engineering anything.

## What the paper shows (and doesn't)

Fine-tunes OmniLearned (PET2 backbone, pretrained on pp/ep collider data;
small = 3M params fully trainable, medium = 53M frozen-backbone) on the same
ME FHC standard MC we use (open-data MasterAnaDev tuples, playlists 1A/1B).
Supervised Eavail regression + CC-pion classification. Pretrained init beats
random init at equal compute (~45–50% fewer steps to comparable validation
loss), gains largest in low-stat/hard regimes; narrower Eavail-residual IQR
across q3 bins than calorimetric baselines.

**Not shown:** OmniFold density ratios, real data, background subtraction,
native misses, covariance coverage, prior sensitivity, or our extended-FPS
domain. It informs classifier design and initialization; it is not evidence
that pretrained PET is a valid OmniFold estimator. The finalized 2D/GBDT
pipeline is unaffected.

## Why it matters here: it lands exactly on our two open PET weaknesses

1. **Recoil-only blindness (OPEN_ITEMS "PET full-event + FPS gate",
   KNOWN_ISSUES #19).** Gregor's successful object is a genuinely full event:
   muon + photons + prongs + blobs as typed tokens (10 features: η, φ, log pT,
   log E, type, dE/dx, x/y/z, t) plus 15 event-level scalars. Independent
   evidence for the direction already requested in
   `nd-unfolding/pet/FULL_EVENT_INTERFACE_REQUEST.md`.
2. **The 2M-train sample-efficiency gap** (PET 16.7% vs GBDT 13.7% median
   frac on unified covs; full-stats retrain ≈29 A100-hr). Foundation-model
   transfer is most valuable precisely in this regime, and OmniLearned *is*
   PET2 — same architecture family as our vendored stack. Cheaper path than
   brute-force full-stats training, if the transfer survives our gates.

## Suggestions (with reasons) — representation

- **Muon as a distinguished typed token** (four-vector, charge, MINOS
  context), because binning a recoil-derived weight in muon coordinates
  leaves the conditional muon distribution at the generator prior. Note the
  minimal version needs no new dump: muon pT/p∥ already sit in the npz
  scalars (see interface request "Available NOW") — enough for the
  stress-closure ablation before any C++ ask.
- **Typed objects instead of generic [E, pos, z] clusters** (photon / prong
  hypothesis / blob, + dE/dx, timing, vertex-relative geometry): his IQR
  result is evidence these features carry real Eavail information our
  3-feature tokens discard. Most are existing tuple branches — dump/loader
  work, not new physics.
- **Aggregate-overflow tokens rather than silent top-12 truncation** (he
  merges beyond-cap blobs/prongs into a summed token). Keeps total energy and
  multiplicity information; our truncation is already the flagged lossiness
  in the truth cloud. Count + discarded-energy summaries are recoverable in
  the loader from the full-length ROOT vectors.
- **Categorical type embeddings, with padding kept distinct from any real
  type** (reserve index 0 for padding). His code reportedly uses muon PID 0
  while the embedding also treats 0 as padding — verify, and don't copy.
- **View-aware neighbor geometry for reco clusters; (η, φ, log pT) only for
  truth four-vectors.** His collider-style coordinates are fine for truth
  but a forced fit for our view-based detector clusters.
- **Reuse his feature definitions and code patterns, not his prepared rows.**
  His preprocessing requires a MINOS-matched muon and filters interaction
  types; our event identity, truth denominator, backgrounds, data, and all
  12 playlists must stay aligned. Keep our schema-parity and truth-leakage
  checks (`fullevent_fps_dataloader.py` is directionally right; its
  two-scalar muon block is a stress-test rig, not the endpoint).

## Suggestions — the model experiment

A controlled four-way pilot on identical events/weights/splits/budgets/seeds:

1. current recoil-only PET (baseline),
2. full-event PET2 from random init,
3. full-event PET2 from generic OmniLearned pretraining,
4. full-event PET2 from Gregor's MINERvA-fine-tuned encoder.

Judge by our gates, not validation loss: omitted-muon stress closure,
ordinary + injected closure, likelihood-ratio calibration, effective sample
size / weight tails, prior swaps, high-W / low-q3 slices, wall-clock. Only
the winner proceeds to the expensive stat/syst retraining campaign — the
pilot exists so we buy that campaign once. Framework note: OmniLearned is
PyTorch, our PET stack is TF/Keras; arms 3–4 imply a port or a PyTorch
OmniFold loop, which is the main integration cost to budget.

## Cautions

- **High-W is a gate, not a freebie:** his multi-pion classifier falls below
  the cut-based baseline at high W — and our interesting discrepancy lives in
  the high-Eavail/high-W corner. Test that region explicitly.
- **Representation can't buy acceptance:** zero-efficiency FPS cells stay
  prior-dominated; the acceptance-supported vs prior-dominated reporting and
  3-prior envelope requirements are unchanged.
- **Eavail definitions differ** (he uses full charged-pion energy + K±; ours
  is arXiv:2312.16631 Eq. 4 pion KE — ~140 MeV/π± offset). Reconcile before
  any numeric comparison.
- **Pin the artifact:** repo has evolved past the paper, no release tags —
  get the exact paper commit/checkpoint hash from Gregor before reproducing.

## Questions for Gregor

Exact arXiv-v1 checkpoint + preprocessing commit; muon/global-feature and
truncation ablations he already ran; diagnostics on the high-W failure;
whether his extractor can preserve our event keys while covering data,
background MC, misses, and all 12 MEFHC playlists.
