# Handoff: the complete pretrained comparison, and the one artifact that does not exist

**CITABLE FOR:** what is done and verified, and precisely which artifact blocks the
rest.
**NOT CITABLE FOR:** any comparative result. **No comparison has been run.** Neither
arm has been trained on the endpoint, no recovery has been measured, and nothing
here favours either configuration.

---

## 1. The blocker, named exactly

**Gregor's complete arm cannot be built from any artifact that exists.** Two pieces
are missing, and both live upstream of everything this lane can reach.

**(a) The 46 R4 branches are in no produced file.** Measured 2026-09-20 with ROOT
against `runEventLoopOmniFold_G2_FPS_MEFHC.root` (113,496,440,965 bytes), the
source of every downstream product:

| tree | entries | branches | R4 branches present |
|---|---:|---:|---:|
| `mc_truth_denom` | 49,906,108 | 20 | **0** |
| `mc_signal_reco` | 49,906,108 | 47 | **0** |
| `mc_background` | 566,036 | 31 | **0** |
| `data` | 4,119,797 | 24 | **0** |

What the file holds is cluster-level reco tokens (`part_reco_E/pos/time/view/z`),
muon kinematics, vertices, truth and weights. What it does not hold is every typed
object (blobs, prongs, gammas) and every source branch of Gregor's 16 globals —
`muon_fuzz_energy`, `muon_iso_blobs_energy`, `MasterAnaDev_hadron_recoil`,
`improved_nmichel`, `part_response_total_recoil_passive_allNonMuonClusters_{id,od}`,
and `gamma{1,2}_{px,py,pz,E}`.

**(b) The token cap is 12 and his arm needs 33.** `num_part = 12` and
`part_reco` is `(49152885, 12, 3)`. The cap is applied at dump time, so 33 tokens
is a re-dump, not a re-read.

**The missing artifact, stated so it can be requested or scheduled:**

> A re-run of the MINERvA `runEventLoopOmniFold` event loop over the ME-FHC
> **MasterAnaDev AnaTuples**, emitting the 21 typed-object branches and the 25
> global source branches enumerated in `r4_manifest.py`, at a token cap of **33**
> — producing a new `runEventLoopOmniFold_G2_FPS_MEFHC` ROOT and from it a
> `G2_FPS_MEFHC_P33.npz` with the identity sidecar regenerated.

**Its own input is not reachable from this account.** No MasterAnaDev tuples exist
under `/global/cfs/cdirs/m3246`, under `/pscratch/sd/j/josephrb`, or in this
account's HPSS namespace, which holds only our own product archives. The event loop
itself is a MINERvA analysis program that is not in this repository.

So this is an **unavailable external prerequisite** in the sense of the goal's
item 18, not a task that was skipped. **R4 was authorized and cannot be executed**:
the authorization is to read branches from a file, and the file does not contain
them.

## 2. What a substitute would cost, and why it is not taken

The degraded arm — our clusters, no PID, no auxiliary channel, no globals, cap 12 —
*can* run today. It is not Gregor's complete arm, and F1 and the goal's item 5 both
require that his arm retain "the intended PID, auxiliary inputs, globals and cap".
Reporting a degraded arm's score as his configuration's would be the
asymmetric-comparison failure this lane exists to avoid. It is not done.

Scratch initialization is likewise not a substitute: the goal says so directly, and
the checkpoint is in hand, so the pretrained arm is blocked only on inputs.

## 3. What IS done, verified and committed

| goal item | state |
|---|---|
| 1 — T2, flat projection + XLA | adopted; **the precision question below is open** |
| 2 — thresholds ratified | frozen in `frozen_design.py`, 16 consistency tests |
| 3 — per-arm eligibility | rewritten; one arm's failure no longer vetoes the other |
| 4 — low acceptance retained | band renamed `low_acceptance`, `G-unresolvable` withdrawn, R-low reporting rule added |
| 5 — ceiling 1,000 GPU-h | counted against cumulative spend, ~19 used |
| 6 — R-1 | **verified by me**: 12/12, and the sidecar's order hash equals my own loader's sha256 |
| 7 — R4 manifest | committed before extraction; extraction **blocked by §1** |
| 8 — checkpoint | **obtained**, hashed, inventory measured, reference loading policy executed: body 139/148 tensors (98.47 %), classifier 26/28 (99.96 %) |
| 9 — fullevent inventory | measured: data 4,116,128 / signal 49,152,885 / background 564,591 |
| 10 — production validation | 8 of 11 checks pass; **V1, V3, V7 fail their pre-declared limits** (below) |
| 11 — memory and timing | 33 tokens at batch 2048 runs on a **40 GB** A100, 21.7 GiB, 410.6 µs/example at enforced FP32 |
| 12 — k-NN ties | **censused on the full inventory**: 20,695 coordinate tie pairs; **28,793 ambiguous k-th boundaries at K=3**, 20,778 at K=10, over 280 M centres |
| 13 — freeze | `frozen_design.py` + tests |
| 14–16 — tuning, pilot, final | **not started; blocked by §1** |
| 17 — deck | not built; there is no comparative result to report |

## 4. The open scientific question, which is not blocked

**The XLA path may not be running in the precision the project froze.** With
TensorFlow reporting `tf32_enabled: False` and determinism enabled, the XLA forward
differs from eager on **100 % of rows**, median 6.91e-4, and the *same* XLA program
at batch 2048 differs from itself at batch 256, on the same rows, by a median of
2.27e-3.

A network with no cross-row operation cannot be batch-dependent at 1e-3 unless the
arithmetic changes with the shape, which is what a reduced-precision tensor-core
path does; and 1e-3 is TF32's precision. The working diagnosis is that
`enable_tensor_float_32_execution(False)` binds TensorFlow and **not** the
XLA-compiled path. `NVIDIA_TF32_OVERRIDE=0`, which disables TF32 inside cuBLAS and
cuDNN below both, is under test.

It is not a k-NN tie effect: a tie moves a few rows a long way and leaves the rest
exact, and this moves every row.

**If the override fixes it**, the frozen FP32 policy is enforceable for XLA and the
cost must be re-measured, because true FP32 gives up the tensor cores. **If it does
not**, T2's XLA decision and the frozen precision policy are in conflict, and that
is a decision for Joseph rather than a defect to patch.

## 5. Continuation

Once a cap-33 dump carrying the R4 branches exists:

```sh
# 1. regenerate the identity sidecar for the new dump and verify it
python3 nd-unfolding/pet/verify_event_identity_sidecar.py \
    --inventory <G2_FPS_MEFHC_P33.npz> --sidecar <...identity.npz> \
    --pet-dir nd-unfolding/pet

# 2. build his complete arm's inputs against r4_manifest.py, then
sbatch nd-unfolding/pet/configuration_comparison/sbatch_production_validation.sh \
    <checkout> <output> <commit> <state.npz> <manifest.json>

# 3. tuning -> pilot -> final, under frozen_design.py
```

Everything in `frozen_design.py` is fixed before those runs and must not move
afterwards.

## 6. Scope

PET remains diagnostic method development. Nothing here is a publication adoption,
a covariance, a systematic, a central-value change or a Gate-6 action; nothing
discharges `OI-71`; and nothing has been sent to Ben, to Gregor or to anyone.
