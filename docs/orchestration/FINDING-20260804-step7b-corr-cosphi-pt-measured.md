# FINDING 2026-08-04 — RESTORE Step 7b measured: corr(cos φ, pT) ≈ +0.002 to +0.006. The φ channel survives by ~137×.

*Measured on Perlmutter 2026-08-04 against the hash-frozen G2 dump. Ran in **46 seconds**. The
result is not close to the decision boundary under any convention, and two of the four convention
axes turn out to be provable identities rather than choices.*

## The number

Clearance is **corr = +0.777**, band **[+0.764, +0.794]**. Below it the extension's φ channel buys
measurable capability; above it, it does not.

| leg | n | weighting | corr(cos φ, pT) | margin to clearance |
|---|---|---|---|---|
| data (`data_muon`, `measured_scalars`) | 4,116,128 | unweighted | **+0.001595** | +0.7754 |
| mc_signal_reco (`reco_muon`, `reco_scalars`) | 20,573,521 | unweighted | **+0.005656** | +0.7713 |
| mc_signal_reco | 20,573,521 | `w_reco` | **+0.005138** | +0.7719 |
| mc_background (`bkg_muon`, `bkg_reco_scalars`) | 564,591 | unweighted | **+0.005024** | +0.7720 |
| mc_background | 564,591 | `w_bkg` | **+0.003220** | +0.7738 |

**Full spread: +0.001595 to +0.005656.** The largest value sits a factor of **~137 below** the
clearance. The runbook predicted "a comfortable pass with ~3× of margin"; the real margin is two
orders of magnitude larger than that.

## No ROOT read was needed, and no 72 GB ntuple

Step 7b prescribed "a small ROOT read of two branches" from the source ntuples. That is
unnecessary: **φ is already in the G2 dump.** The dump carries three 7-column muon blocks matching
`RECO_MUON_BRANCHES`, so φ is column 4 and `minos_ok` column 6:

| leg | muon block | pT scalars |
|---|---|---|
| data | `data_muon` (4,116,128, 7) | `measured_scalars` |
| mc signal reco | `reco_muon` (49,152,885, 7) | `reco_scalars` |
| background | `bkg_muon` (564,591, 7) | `bkg_reco_scalars` |

The runbook's "φ is NOT in the npz — verified" is correct but scoped to
`of_inputs_pc_fps_xps2.npz`, the **reduced** dump with 18 keys. The full-event G2 dump has **42**
keys and postdates that check (the full-event schema landed 2026-08-01). Reading the frozen dump is
also better-provenanced than reading an ntuple, since the dump is the artifact the campaign has
hash-bound.

## Two of the four convention axes are degenerate — provably, not coincidentally

The user asked for every plausible convention. Two axes turn out not to be choices at all, and
saying so is more honest than reporting "24 conventions" as if they were independent:

1. **Selection is one selection, not three.** `pass_reco`, `minos_ok != 0`, and "inside the FPS
   domain" are *exactly coextensive* — each selects **20,573,521** of 49,152,885 rows (41.8562%),
   and every intersection is the same 20,573,521. `pass_reco` within the FPS domain is 1.000000.
   The mechanism: non-reco rows are filled with the sentinel **−9999** in φ *and* in pt/pz, so
   `pt >= 0` excludes them by construction. Verified directly: over all rows φ ∈ [−9999, 3.1416]
   with 28,579,364 sentinel entries; over the selected rows φ ∈ [−3.1416, +3.1416] with **zero**
   sentinels. So the cut is sound rather than luckily sufficient.
2. **The two pT definitions are the same quantity in different units.**
   `hypot(mu_reco_px, mu_reco_py) / scalars[:,0]` has median **1000.000000** (p1 999.999926,
   p99 1000.000074). Pearson correlation is scale-invariant, so the two give bit-identical corr.

So the genuinely distinct results are **5** (3 legs × weighted/unweighted where a non-negative
weight exists), not 24. The conclusion is *stronger* for it: the degeneracies are identities, so no
unexamined convention is hiding a different answer.

`w_bkg` weighted variants were computed but flagged where the weight can go negative — a Pearson
frequency weight cannot represent a subtraction weight, and the script says so rather than
silently producing a number.

## By-product worth its own attention: the dump mixes MeV and GeV

`reco_muon[:, 0:3]` (px, py, pz) are in **MeV** — `|px|` max 29,903.91 — while
`reco_scalars[:, 0:2]` (pt, p∥) are in **GeV**, max 29.9909. Both travel in the same npz with no
naming distinction.

This is the same shape as the Gate-2 defect resolved today
([FINDING-20260804-gate2-units-resolved-gev](FINDING-20260804-gate2-units-resolved-gev.md)): anyone
deriving pT from the muon block and binning it against the canonical GeV grid would be wrong by
exactly 1000, and — because both canonical axes start at 0.0 — a domain-membership check would not
notice. Worth a contract note next to the muon block, and worth checking any consumer that reads
`*_muon` columns 0-2 alongside the scalar grid.

## What this does and does not settle

It settles the coupling-axis question the sweep left open: real data carries essentially **no**
azimuthal correlation with the muon block, so the baseline is nowhere near blind enough to erode
the extension's marginal value. It does **not** establish that real data carries an azimuthal
mismatch at all — the sweep's crossing is a property of a synthetic acceptance thinning, and
recovering a tilt through a pT proxy is not the same as seeing φ.

Per the runbook, `leak = corr²` was **not** used; it is falsified out of sample and only a lower
bound.

## Artifacts

* `~/step7b-20260804/corr_cosphi_pt_all_conventions.json` — every row, with n, corr, margin and
  verdict, plus the recorded spread.
* Script: `step7b.sh` (reads the frozen dump; no ROOT, no ntuple).
