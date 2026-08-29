# Gate 6 GAP 1 — five full-inventory member evaluations

**Fixed before submission. Authorized conditionally by Joseph on 2026-08-30.**

## Question and frozen inventory

The five Gate-6 Leg-1 members were trained and scored on their own 2,000,000-row subsamples, while
the PET nominal cross section was extracted after inference over all 49,152,885 signal-MC rows.
This run asks what the five already-trained members produce when the same full-inventory inference
and extraction path is applied to each of their existing final step-2 checkpoints. It trains
nothing.

The inventory is exactly members 1 through 5 under
`nd-unfolding/pet/fullevent_ml_ensemble/member_<N>/pet_fullevent_ml_member<N>_weights.npz`, with
SHA-256 values, in order:

1. `3e08850d44f773bb50f5cb132a7a1d4d672e0ab15f1d38d785a4eddbf5179b2e`
2. `5b8e129f9dba90659ed0fc17f322499ea41fea505add57ab957ad209152f1c13`
3. `f6087581e320d1bfce1a968e62c737d8fac346dedb94836f7fe173980a5b55e8`
4. `04759d0a07f120bda112b87222b0a91fd0e98a2ce402be12d37f30d06a2a0bfd`
5. `4120a5483255847e9dceb79dc5796dd820fca419cfba8adddabc42924d82eff1`

The common input is `G2_FPS_MEFHC_P12.npz`, 9,897,374,636 bytes, SHA-256
`fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625`. It contains 49,152,885
rows, of which 49,150,928 pass the truth selection. Each member artifact must retain exactly
2,000,000 unique training indices and its recorded final checkpoint must exist before submission.

## Measured quantities

For each member, the inference stage writes the ordered 49,152,885-row `w_push` vector and its
existing extractor telemetry: minimum, maximum, mean, median, non-finite count, off-acceptance row
count and pin check, and the maximum and median relative disagreement on the 2,000,000 shared
training rows. The extraction stage writes the same extended-FPS grid used by the nominal
(285 flattened cells), its reporting mask telemetry, number of populated cells, and
`total_sigma_cm2_per_nucleon`. These five totals and five spectra are the like-for-like
full-inventory normalization and shape readout.

The extraction is a diagnostic product only. A terminal outcome may describe the five numerical
normalizations, their range, and their cell-by-cell spectra. It may not retrospectively apply the
old subsample convergence rule or create any new member-level pass/fail classification.

## Execution and resource boundary

Exactly five logical evaluations run, one per member. TensorFlow inference and ROOT extraction are
separate Slurm arrays and separate environments. The inference array is `1-5%5`, one A100 and one
hour per task: a hard allocation ceiling of **5 A100-hours**. The dependent extraction array is
CPU-only. No training entrypoint is called, no checkpoint is written, and no existing product is
overwritten. A failed or incomplete task is terminal for this authorization; an unchanged retry is
not authorized.

Both interpreters run the extraction entrypoint in-process beneath
`nd-unfolding/mnv_guarded_run.py`. The launcher names one clean detached immutable checkout, binds
its HEAD and source hashes, forbids the primary checkout as the code root, exports that same root
through `MNV_REPO`, and supplies no `--allow`. The dedicated remap adapter translates only the two
known primary-root insertions made by the hash-bound full-event loader to the same relative paths
inside the immutable checkout. Any other checkout resolution is refused.

## What no terminal result can authorize

The five exact Gate-6 prohibitions remain unchanged:

- `do_not_select_passing_subset`
- `do_not_construct_C_ML`
- `do_not_move_central`
- `do_not_start_leg_2`
- `do_not_retry_unchanged`

In addition, the run cannot re-verdict any member, replace or promote a central estimator, support
a publication claim, or authorize any new compute. Gate 6 remains blocked independently of every
possible numerical result from this diagnostic.
