# Point-cloud reweight-then-project demonstration

**Date:** 2026-06-27 · **Script:** `nd-unfolding/pet/pointcloud_projection.py` ·
**Outputs:** `nd-unfolding/products/pet/pointcloud_projection{.root,_summary.json,_validation.png,_xsec.png}`

## The idea (and its achievable form)

The OmniFold/PET truth side is **already a point cloud**: `of_inputs_pc.npz` stores
`part_gen`, shape `(32 849 103, 12, 5)` = `(E, px, py, pz, pdg)` of the top‑12‑by‑energy
truth final‑state **hadrons** (built by `nd-unfolding/pet/dump_pointcloud_inputs.py` from the
`part_gen_*` branches, themselves filled by `CVUniverse::GetTruthFSHadrons`,
`MINERvA101/.../event/CVUniverse.h:289‑304`). The trained‑PET push weights
`products/pet/pet_weights_full.npz['w_push']` give the **unfolded** truth spectrum
`w_truth · w_push` on `pass_truth` events.

So **any truth observable computable from the cloud can be projected post‑hoc by re‑binning
the push‑weighted truth events — no re‑unfolding.** This is *reweight‑then‑project*. It is
**not** a generative truth‑cloud model (synthesising particles the generator never produced);
that is separate, out‑of‑scope research — see the OmniFold caveat at the end.

This memo demonstrates the achievable form on three new observables and reports — honestly —
exactly which observables are trustworthy from the *current* npz and which need a re‑dump.

## What was computed from the cloud

| observable | how (from `part_gen`) | cross‑checkable against |
|---|---|---|
| `Eavail` | exact `GetEAvailableTrue` formula (CVUniverse.h:330‑343): γ total‑E, π± KE, π⁰ total‑E, p KE; needs `E`+`pdg` | stored `MC_eavail` (`truth_scalars[:,2]`) |
| `W_had` | hadronic‑system invariant mass √(ΣE² − \|Σp\|²) from the 4‑vectors | stored leptonic `MC_W` (definitionally different — see below) |
| `n_proton`, `n_pi` | `pdg` counting w/ KE thresholds (CVUniverse.h `GetNProtonsTrue`/`GetNChargedPionsTrue`) | — (new) |

`pdg` is present in the npz (it is only dropped *before training*), so particle identity is
fully available for projections.

## Validation 1 — truncation loss is tiny (the clean probe)

`Eavail` uses the **same formula and same inputs** as the stored `MC_eavail`, so the
cloud‑vs‑stored residual isolates the **top‑12‑hadron truncation** with no definitional
ambiguity. On the 23 849 936 cloud‑carrying `pass_truth` events:

- median residual **0.0 MeV**, mean **−6.3 MeV**, RMS 82 MeV; **98.81 %** within 10 MeV.
- The deficit lives **entirely in the saturated events** (`n_had = 12`, only **2.28 %** of
  cloud events): median deficit there −31 MeV; for `n_had ≤ 11` it is exactly 0.
  (`pointcloud_projection_validation.png`.)

**Conclusion:** top‑12‑by‑energy truncation is essentially lossless for `Eavail`‑scale
observables. It only bites for the rare high‑multiplicity tail, and because the ranking is by
energy, the dropped constituents are the soft mesons — a bounded, one‑sided deficit.

## Validation 2 — cloud availability (the real lossiness)

The dominant limitation is **not** truncation but **cloud coverage**. The cloud (`part_gen`)
is filled in the reco‑signal loop (`runEventLoopOmniFold.cpp:916`); the truth‑only "miss"
rows appended by `AppendTruthOnlyMisses` are **not** all given a cloud (KNOWN_ISSUES #12).
Event census (`pointcloud_projection_summary.json['event_census']`):

| set | events | % |
|---|---:|---:|
| `pass_truth` (npz total) | 32 849 103 | 100.00 |
| `pass_truth & reco` | 20 404 292 | 62.12 |
| truth‑only miss (`pass_truth & ~reco`) | 12 444 811 | 37.88 |
| **has cloud (`n_had > 0`)** | **23 849 936** | **72.60** |
| empty cloud | 8 999 167 | 27.40 |

Cross‑tab: every reco‑passing event has a cloud (only 158 empty); the empty clouds are
**8 999 009 truth‑only misses** (the other 3 445 802 misses happen to carry one). So **cloud
observables are projectable only on the ~72.6 % has‑cloud subset**; the ~27 % truth‑only
misses with no cloud cannot contribute to a cloud projection.

This shows up directly in the projected cross sections (`pointcloud_projection_xsec.png`,
centre panel): the cloud‑recomputed `dσ/dEavail` lands **exactly on** the stored‑`MC_eavail`
projection *restricted to the has‑cloud subset* (validating the projection chain to ≲0.3 %/bin),
and both sit below the **full** unfold by the truth‑only‑miss gap (~1.5–2× per bin). The full
stored projection tracks the GBDT 5D reference (`hXSec_eavail`) to ~15–25 %.

## Validation 3 — `W_had` ≠ `MC_W` by **definition**, not truncation

`GetTrueExperimentersW` (CVUniverse.h:365‑379) is a **leptonic** estimator —
W = √(M² + 2(Eν−Eμ)M − Q²) from muon kinematics with a single struck nucleon at rest. The
cloud `W_had` is the **invariant mass of the final‑state hadron system**. On has‑cloud
events `W_had − MC_W` has median **+0.96 GeV** (mean +1.84). The 2‑D hexbin
(`pointcloud_projection_xsec.png`, left) makes the physics explicit:

- a sharp horizontal locus at `W_had ≈ 0.94 GeV` — QE/single‑nucleon final states, whose
  hadronic invariant mass is just the nucleon rest mass regardless of leptonic W;
- diagonal bands offset **above** the `y=x` line by ~0.94 GeV steps — events with ≥2
  final‑state baryons (FSI knockout, 2p2h), each extra baryon adding ~one nucleon mass to the
  system invariant mass, plus Fermi‑motion smear.

So `W_had` is a **genuinely new, physically meaningful observable** (the true hadronic‑system
mass), *not* a lossy reconstruction of the leptonic `MC_W`. Its `dσ/dW_had` (right panel) has
a correspondingly different shape from the leptonic‑W reference — as it should.

## What IS projectable from the current `of_inputs_pc.npz` (demonstrated)

On the **has‑cloud subset (72.6 %)**, any function of the top‑12 truth‑hadron 4‑vectors + pdg:
`Eavail`, hadronic‑system invariant mass `W_had`, hadron multiplicities (`n_p`, `n_π±`,
`n_π⁰`, `n_γ`, …), the summed‑hadron angle (`GetHadronAngleTrue`, CVUniverse.h:269‑282),
leading‑hadron kinematics, transverse hadronic momentum, etc. The truncation error on all of
these is bounded by Validation 1 (≲6 MeV‑scale on energy sums; only the 2.28 % saturated tail
is affected).

## What NEEDS a re‑dump (clearly separated)

1. **The full truth spectrum (incl. the 37.9 % truth‑only misses).** ~9.0 M miss rows carry no
   cloud, so a cloud projection is acceptance‑limited. Fix: in the re‑dump, fill `part_gen_*`
   for the `AppendTruthOnlyMisses` rows (the accessors already exist; this is the
   KNOWN_ISSUES #12 dangling‑branch problem on the truth side).
2. **Muon‑dependent observables.** The muon (and neutrinos) are removed from the cloud
   (CVUniverse.h:296‑297). Use the stored truth scalars `truth_scalars` (`pt`, `pz`, plus
   `eavail`, `q3`) for muon kinematics, **or** re‑dump with the muon added as a tagged
   constituent (its accessors exist; just stop dropping `pdg == ±13`).
3. **Very‑high‑multiplicity tails (> 12 hadrons).** Raise `num_part` in
   `dump_pointcloud_inputs.py:53` (`--num-part`). Only matters for the 2.28 % saturated tail.
4. **Whole‑event / neutrino‑frame quantities** needing particles outside the kept hadron set.

## The fundamental OmniFold caveat (applies to every projection)

Reweighting can only **redistribute** weight among truth configurations the generator
**already produced**; it cannot populate truth phase space the prior never sampled. A
projected observable is therefore trustworthy only where the generator populated that region
of the (now higher‑dimensional) hadronic phase space — exactly the extrapolation limit flagged
for the full‑phase‑space (FPS) study. Projecting a new observable does **not** add information
about correlations the generator never produced; recovering those is the generative
truth‑cloud problem, which is out of scope here.

## Reproduce

```bash
# interactive node (login-node per-user memory cgroup OOM-kills the 32.85M-row load)
salloc -N1 -C cpu -q interactive -A m3246 -t 01:00:00 \
  bash -lc 'source $REPO/setup_salloc_env.sh; cd $REPO/nd-unfolding; \
            python3 pet/pointcloud_projection.py'
```
Reads (all read‑only): `of_inputs_pc.npz`, `products/pet/pet_weights_full.npz`,
`runEventLoopOmniFold_5D_MEFHC_universes_full.root` (row‑aligned; the `MC == truth_scalars[:,0]`
assertion passes on all 32 849 103 rows, per `pet_lateral_band.py`), and the GBDT reference
`products/5d/xsec_5d_MEFHC_5iter_lgbm.root`.
