#!/usr/bin/env python3
"""MINERvA -> vendored-OmniFold (ViniciusMikuni/omnifold) DataLoader adapter.

Phase 2 of docs/HIGHER_DIM_OMNIFOLD_DESIGN.md: the point-cloud / NN track. The NN
*engine* was validated against the GBDT on scalar inputs (ND_OMNIFOLD_STATUS.md, ratio
1.0078); the remaining piece is the data interface that feeds our event-loop arrays into
the vendored `omnifold.DataLoader` so its PET (point cloud) and MLP models can run. This
module is that glue, mirroring how `unbinned_unfolding/` was ported (sibling folder +
sys.path import; here `../omnifold_nn`).

Two input modes:

  scalar      -- wrap the per-event scalar kinematics (pt, pz, eavail[, q3]) as the
                 feature vector. Runs end-to-end on the EXISTING npz dumps via the
                 vendored MLP (and via PET with local=False so num_part can be small).
                 This proves the vendored engine unfolds our data and is the natural
                 home for the NTRIAL ensemble-mean CV (prepub item #2).

  pointcloud  -- the real Phase-2 target: per-hadron 4-vectors as a (N, num_part,
                 num_feat) point cloud for PET. Our event loop does NOT yet dump
                 per-hadron arrays, so this mode reads them from a point-cloud npz with
                 the schema documented in PARTICLE_SCHEMA below and raises an actionable
                 error (naming the exact branches to add to runEventLoopOmniFold.cpp) if
                 they are absent. THIS is the one remaining event-loop change for the
                 point-cloud showcase.

Vendored-loader semantics (omnifold_nn/omnifold/dataloader.py):
  * data loader  = DataLoader(reco=<data feats>, weight=<purity weights>)        (no gen)
  * mc   loader  = DataLoader(reco=<mc reco feats>, gen=<mc gen feats>,
                              pass_reco=<bool>, pass_gen=<bool>, weight=<prior w>)
  * reco and gen MUST be the same length (paired per event); misses = pass_gen & ~pass_reco,
    fakes = pass_reco & ~pass_gen. The vendored loop uses a single mc.weight for both
    steps, so we pass the truth/prior weight (w_truth); reco acceptance lives in pass_reco.
"""
import argparse
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/omnifold_nn", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Per-hadron point-cloud feature schema for the Phase-2 PET track. Each is the
# event-loop branch that must be dumped (variable-length, one row per reconstructed
# hadronic cluster / truth FS hadron), zero-padded to num_part with a validity mask.
PARTICLE_SCHEMA = {
    "reco": [
        # name              source branch (to add to runEventLoopOmniFold.cpp)
        ("part_reco_E",     "blob/cluster energy (MeV)        e.g. *_recoil_cluster_E[]"),
        ("part_reco_px",    "cluster px (MeV)                 from cluster position+E"),
        ("part_reco_py",    "cluster py (MeV)"),
        ("part_reco_pz",    "cluster pz (MeV)"),
        ("part_reco_z",     "cluster z position (mm)          detector geometry feature"),
    ],
    "gen": [
        ("part_gen_E",      "mc_FSPartE[]   (truth FS hadron energy, MeV)"),
        ("part_gen_px",     "mc_FSPartPx[]"),
        ("part_gen_py",     "mc_FSPartPy[]"),
        ("part_gen_pz",     "mc_FSPartPz[]"),
        ("part_gen_pdg",    "mc_FSPartPDG[] (encode/one-hot; drop the muon)"),
    ],
}
SCALAR_AXES = ["pt", "pz", "eavail", "q3"]  # the high-level event features (num_evt path)


def _scalar_feats(d, ndim):
    """Column-stack the scalar features present in the npz (pt,pz + extra axes)."""
    # of_inputs_*.npz stores MCgen/MCreco/measured as (N, ndim) already in axis order.
    return d["MCgen"], d["MCreco"], d["measured"]


def build_loaders(inputs_npz, mode="scalar", num_part=1, max_events=None,
                  bootstrap=False, seed=0):
    """Return (data_loader, mc_loader) vendored DataLoaders from our OmniFold arrays."""
    from omnifold import DataLoader  # vendored

    d = np.load(inputs_npz, allow_pickle=True)
    pass_reco = d["pass_reco"]; pass_truth = d["pass_truth"]
    w_truth = d["w_truth"].astype(np.float32)
    measured_weights = d["measured_weights"].astype(np.float32)
    ndim = int(d["nedges"]) if "nedges" in d.files else d["MCgen"].shape[1]

    if mode == "scalar":
        MCgen, MCreco, measured = _scalar_feats(d, ndim)
        MCgen = MCgen.astype(np.float32); MCreco = MCreco.astype(np.float32)
        measured = measured.astype(np.float32)
        if num_part > 1:
            # tile the scalar vector across num_part "particles" so PET (local kNN)
            # can run as a wiring smoke test; not physically a cloud.
            MCgen = np.repeat(MCgen[:, None, :], num_part, axis=1)
            MCreco = np.repeat(MCreco[:, None, :], num_part, axis=1)
            measured = np.repeat(measured[:, None, :], num_part, axis=1)
    elif mode == "pointcloud":
        MCgen, MCreco, measured = _load_pointcloud(inputs_npz, num_part)
    else:
        raise ValueError(f"unknown mode {mode!r} (scalar|pointcloud)")

    if max_events is not None:
        rng = np.random.default_rng(seed)
        nmc = min(max_events, MCgen.shape[0])
        nda = min(max_events, measured.shape[0])
        imc = rng.choice(MCgen.shape[0], nmc, replace=False)
        ida = rng.choice(measured.shape[0], nda, replace=False)
        MCgen, MCreco = MCgen[imc], MCreco[imc]
        pass_reco, pass_truth, w_truth = pass_reco[imc], pass_truth[imc], w_truth[imc]
        measured, measured_weights = measured[ida], measured_weights[ida]

    data = DataLoader(reco=measured, weight=measured_weights, normalize=True,
                      bootstrap=bootstrap)
    mc = DataLoader(reco=MCreco, gen=MCgen, pass_reco=pass_reco, pass_gen=pass_truth,
                    weight=w_truth, normalize=True, bootstrap=bootstrap)
    return data, mc


def _load_pointcloud(inputs_npz, num_part):
    """Load per-hadron point clouds. Raises an actionable error until the event loop
    dumps the PARTICLE_SCHEMA branches."""
    d = np.load(inputs_npz, allow_pickle=True)
    need_reco = [n for n, _ in PARTICLE_SCHEMA["reco"]]
    need_gen = [n for n, _ in PARTICLE_SCHEMA["gen"]]
    missing = [n for n in need_reco + need_gen if n not in d.files]
    if missing:
        lines = ["[pointcloud] the per-hadron arrays are not in this npz; the event loop",
                 "  must dump them first. Required branches (add to "
                 "runEventLoopOmniFold.cpp,",
                 "  one row per reconstructed cluster / truth FS hadron, then re-dump via",
                 "  nn_dump_inputs.py with a --pointcloud flag):"]
        for grp in ("reco", "gen"):
            for nm, src in PARTICLE_SCHEMA[grp]:
                flag = "MISSING" if nm in missing else "ok"
                lines.append(f"    [{flag:7s}] {nm:16s} <- {src}")
        raise SystemExit("\n".join(lines))
    # shape (N, num_part, num_feat); already zero-padded + masked upstream.
    reco = np.stack([d[n] for n in need_reco], axis=-1).astype(np.float32)
    gen = np.stack([d[n] for n in need_gen], axis=-1).astype(np.float32)
    return gen, reco, gen  # measured PC not available in MC npz; pointcloud data npz separate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default="of_inputs_3d.npz")
    ap.add_argument("--mode", default="scalar", choices=["scalar", "pointcloud"])
    ap.add_argument("--num-part", type=int, default=1)
    ap.add_argument("--max-events", type=int, default=None)
    ap.add_argument("--smoke", action="store_true",
                    help="instantiate the vendored MLP/PET + run a 1-iter MultiFold on a "
                         "subsample to prove the engine unfolds our data (needs TF/GPU).")
    ap.add_argument("--model", default="mlp", choices=["mlp", "pet"])
    ap.add_argument("--niter", type=int, default=1)
    ap.add_argument("--epochs", type=int, default=2)
    args = ap.parse_args()

    data, mc = build_loaders(args.inputs, mode=args.mode, num_part=args.num_part,
                             max_events=args.max_events)
    print(f"[loaders] data reco shape={np.asarray(data.reco).shape} "
          f"(sumw={data.weight.sum():.3e})")
    print(f"[loaders] mc   reco shape={np.asarray(mc.reco).shape} gen shape="
          f"{np.asarray(mc.gen).shape}")
    print(f"[loaders] mc   pass_reco={mc.pass_reco.mean():.3f}  "
          f"pass_gen={mc.pass_gen.mean():.3f}")

    if not args.smoke:
        print("[ok] DataLoaders built. Pass --smoke (TF/GPU env) to run a MultiFold step.")
        return

    from omnifold import MultiFold, MLP, PET
    reco_arr = np.asarray(mc.reco)
    if args.model == "mlp":
        nvars = reco_arr.shape[-1] if reco_arr.ndim == 2 else int(np.prod(reco_arr.shape[1:]))
        if reco_arr.ndim == 3:  # flatten the trivial cloud for the MLP
            mc.reco = reco_arr.reshape(reco_arr.shape[0], -1)
            mc.gen = np.asarray(mc.gen).reshape(np.asarray(mc.gen).shape[0], -1)
            data.reco = np.asarray(data.reco).reshape(np.asarray(data.reco).shape[0], -1)
        m1, m2 = MLP(nvars), MLP(nvars)
    else:
        num_feat = reco_arr.shape[-1]; num_part = reco_arr.shape[1]
        # local=False so a small (even 1-particle) cloud runs without the K>=3 kNN check
        m1 = PET(num_feat, num_part=num_part, local=(num_part >= 3))
        m2 = PET(num_feat, num_part=num_part, local=(num_part >= 3))

    of = MultiFold(f"minerva_{args.model}", m1, m2, data, mc,
                   niter=args.niter, epochs=args.epochs, batch_size=1024,
                   weights_folder="/tmp/minerva_pet_weights", verbose=True)
    of.Unfold()
    w = of.reweight(mc.gen, of.model2, batch_size=1000)
    print(f"[smoke] OK: unfolded weights n={len(w)} mean={w.mean():.4f} "
          f"std={w.std():.4f} (finite={np.isfinite(w).all()})")


if __name__ == "__main__":
    main()
