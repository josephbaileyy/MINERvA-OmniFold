# Binding addendum 4: MP3-B generation abort, chunked rerun and a mixed variant (2026-10-20)

**By** the paper-tighten lane, as director, under [`BINDING-PHASE1-20261019.md`](BINDING-PHASE1-20261019.md) §2
(MP3-B).

**CITABLE FOR:** the rulings on MP3-B's generation.
**NOT CITABLE FOR:** any result.

## What happened (as reported)

Job 60022605 (debug, about 0.02 CPU node-h) stopped through its own STOP guard. Both NuWro hydrogen runs aborted
with `src/particle.h:227: Assertion 'E>=_mass' failed`. That is a Σ hyperon from free-proton DIS fragmentation at
threshold, below its mass by a rounding error. It happens about once per 4×10⁴ DIS events. The debug build is the only
one that runs on this platform. The C12 parity rerun passed. No gate and no cell-level hydrogen output exists.

## Rulings

- **(A) Chunked generation is approved.** The layout follows the frozen C12 production: H_main as 25 × 10k events and
  H_supp as 5 × 5k, on the production card, with seeds declared in `SEEDS.txt` before submission.
  - An aborted chunk is discarded whole, never kept partially.
  - Each chunk has up to two declared alternate seeds. A chunk that fails on both is dropped, and N_total is reduced
    to match.
  - The report gives, per chunk: aborts, seeds used, events, and the DIS fraction. It also gives the excluded fraction
    (aborts per DIS event) as a stated approximation. If that fraction exceeds about 1e-4, the report says so rather
    than assuming the effect is negligible.
  - Gates C0–B4 are unchanged. The chunks are combined by the frozen Σ w r / N_total over those that completed.
- **(B) Patching NuWro is not approved.**
- **(C) A mixed variant is approved, labelled**: "mixed: NuWro carbon + GENIE hydrogen; not NuWro-on-CH". It is reported
  beside (A) with the same readout. If (A) cannot finish before the maintenance window, (C) is the only CH-type number
  until the cluster returns, and it keeps that label.
- **Deadline and budget:** the rulings of [`BINDING-PHASE1-ADDENDUM-3.md`](BINDING-PHASE1-ADDENDUM-3.md) §1 apply,
  including the 2026-10-21 04:00 PDT cutoff. Everything stays within the phase-1 ceiling.
