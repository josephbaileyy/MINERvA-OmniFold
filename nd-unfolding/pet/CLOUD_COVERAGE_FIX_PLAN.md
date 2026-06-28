# Plan: fill the truth cloud on miss rows (full-spectrum cloud projection)

**Goal.** Lift truth-cloud projections from the ~72.6 % has-cloud subset to the
full truth spectrum, by populating `part_gen_*` for the truth-only miss rows
that `AppendTruthOnlyMisses` currently leaves empty. See the demonstration in
`POINTCLOUD_PROJECTION.md` (the coverage gap is the dominant limitation, not
top-12 truncation).

## Root cause (precise — and NOT the same as KNOWN_ISSUES #12)

KNOWN_ISSUES #12 was the *garbage per-universe weight branches* on miss rows;
it was fixed 2026-06-10 by binding those branches to deterministic CV proxies.
This is the **adjacent, still-open** problem: the *truth point cloud*
`part_gen_*` on miss rows is **empty, not garbage**.

`runEventLoopOmniFold.cpp`:
- The truth cloud is filled only in the **reco-signal** loop, line **916**:
  `recoCV->GetTruthFSHadrons(pc_gen_E, pc_gen_px, pc_gen_py, pc_gen_pz, pc_gen_pdg)`.
- `AppendTruthOnlyMisses` (lines **515-536**) deliberately binds `part_gen_*`
  to **empty** vectors with the comment *"a miss has no reco clusters -> empty
  cloud."* That reasoning is correct for the **reco** cloud (`part_reco_*`) —
  a miss genuinely has no reco clusters — but it **wrongly** carries over to
  the **truth** cloud `part_gen_*`. A truth-only miss is a truth-pass event:
  its generator-level FS hadrons exist; they were simply never computed on the
  truth-denominator path.
- The fix surface is therefore three edits, all in
  `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp`.

## The three code edits

1. **`struct TruthDenomEntry` (lines 101-113)** — add the truth cloud:
   ```cpp
   std::vector<float> pg_E, pg_px, pg_py, pg_pz;  // float to halve RAM (see below)
   std::vector<int>   pg_pdg;
   ```

2. **`LoopAndFillUnbinnedMCTruthDenom` (compute ~line 430, push at 463-465)** —
   the loop already holds `CVUniverse* truthCV` and computes `MC_W`,
   `MC_hadangle`, `MC_nproton` on it. Call the *same* accessor used in the
   signal loop so the miss-row cloud is bit-identical in construction:
   ```cpp
   std::vector<double> e,px,py,pz; std::vector<int> pdg;
   truthCV->GetTruthFSHadrons(e,px,py,pz,pdg);
   ```
   and store (narrowed to float) into the pushed `TruthDenomEntry`.

3. **`AppendTruthOnlyMisses` (lines 515-536, fill loop 591-628)** — bind
   `part_gen_*` to **per-event** vectors filled from `tde` instead of the
   permanent empties; keep `part_reco_*` empty (a miss really has no reco
   cloud). Inside the loop, copy `tde.pg_E -> e_gen_E` (etc., float->double for
   the branch type) before `sigOut->Fill()`.

No change to the npz dumper (`dump_pointcloud_inputs.py`) is needed — it reads
`part_gen_*` generically; once the branches are non-empty on miss rows the npz
picks them up.

## Memory note (the one real design choice)

`truthDenomCache` holds **all ~32.8 M** truth-pass events in RAM. Adding the
cloud costs roughly (avg ~5 hadrons) ~300 B/entry with `double`, ~180 B with
`float` -> **~6-10 GB** extra resident. That is fine on a Perlmutter compute
node (256-512 GB) but should be `float` and `reserve()`d. If RAM is ever a
concern, the memory-lean alternative is to **not** cache the cloud in RAM:
the truth cloud can be written to the `mc_truth_denom` TTree (filled in the
same loop at line 460) and read back by entry index in `AppendTruthOnlyMisses`
— add a `long denomEntry` to `TruthDenomEntry` and random-access the branches.
Primary recommendation: in-RAM `float` (simplest, fits).

## Build + re-dump (the gated cost)

- Rebuild/install the driver (cmake, the documented build path).
- **Re-run the event loop across all 12 ME FHC playlists** with
  `MNV101_DUMP_POINTCLOUD` (+ the universe/lateral env as in the existing
  launchers), then `hadd_universes_full.py` -> regenerate
  `runEventLoopOmniFold_5D_MEFHC_universes_full.root`. This is the heavy,
  user-gated job (same class as every prior re-dump). Smoke-test on one
  playlist first and assert `part_gen_E.size()>0` on a sample of `sim_pass==0`
  rows.
- Rebuild the npz (`dump_pointcloud_inputs.py`) from the new root file.

## Validation gates (must pass before quoting full-spectrum numbers)

1. **Coverage**: `has_cloud` fraction in the new npz rises 72.6 % -> ~100 %
   of `pass_truth`; the empty-cloud count drops to ~the genuine zero-hadron
   truth events only.
2. **Non-regression on accepted rows**: on `sim_pass==1` rows the cloud is
   byte-for-byte unchanged (the signal-loop fill is untouched) — re-run the
   `Eavail` residual probe from `pointcloud_projection.py`; the 98.81 %-within-
   10 MeV number must reproduce exactly.
3. **Projection closes the gap**: cloud `dsigma/dEavail` on the full sample now
   matches the **stored-full** projection (not just the has-cloud subset),
   removing the ~1.5-2x/bin miss gap seen in `pointcloud_projection_xsec.png`.

## Two-tier scope (important caveat for the PET side)

- **Tier 1 — projection with the *existing* push weights (cheap, approximate).**
  Once miss rows carry truth clouds, they can be projected immediately using
  the frozen `w_push`. Caveat: those miss rows were assigned weights by a PET
  step-2 reweighter that *saw an empty cloud* for them, so their weights are
  not the weights a cloud-aware network would assign. Good for a first
  full-spectrum look; flag as approximate.
- **Tier 2 — rigorous full retrain (the clean version).** For a defensible
  full-spectrum cloud cross section, **retrain** PET on the re-dumped inputs so
  step-2 sees the real miss-row clouds. This is the GPU-training job from the
  capstone campaign; only worth launching after Tier 1 confirms the gap closes
  as expected.

## Effort estimate

Code: ~30-40 lines across the three edit sites, half a day incl. smoke test.
Compute: one 12-playlist event-loop re-dump (gated) + npz rebuild; optional
PET retrain for Tier 2. No change to the extraction/projection scripts.
