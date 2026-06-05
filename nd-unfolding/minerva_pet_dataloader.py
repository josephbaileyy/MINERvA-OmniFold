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
# These now match the branches the event loop dumps under MNV101_DUMP_POINTCLOUD
# (runEventLoopOmniFold.cpp / CVUniverse::GetTruthFSHadrons + GetRecoClusters).
PARTICLE_SCHEMA = {
    "reco": [
        ("part_reco_E",  "ExtraEnergyClusters_energy[] (cluster energy, MeV)"),
        ("part_reco_x",  "ExtraEnergyClusters_X[] (cluster x position, mm)"),
        ("part_reco_y",  "ExtraEnergyClusters_Y[] (cluster y position, mm)"),
        ("part_reco_z",  "ExtraEnergyClusters_Z[] (cluster z position, mm)"),
    ],
    "gen": [
        ("part_gen_E",   "mc_FSPartE[]   (truth FS hadron energy, MeV; muon+nu dropped)"),
        ("part_gen_px",  "mc_FSPartPx[]"),
        ("part_gen_py",  "mc_FSPartPy[]"),
        ("part_gen_pz",  "mc_FSPartPz[]"),
        ("part_gen_pdg", "mc_FSPartPDG[] (encode/one-hot)"),
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
    if "nedges" in d.files:
        ndim = int(d["nedges"])
    elif "MCgen" in d.files:
        ndim = d["MCgen"].shape[1]
    else:
        ndim = None  # pointcloud npz: ndim is (num_part, num_feat), not a scalar dim

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

    imc = np.arange(MCgen.shape[0])   # mc subsample indices into the input npz (for binning)
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
    return data, mc, imc


def _load_pointcloud(inputs_npz, num_part):
    """Load padded point clouds from a dump_pointcloud_inputs.py npz.

    Expects part_gen (N,P,5), part_reco (N,P,4), measured_pc (M,P,4). Until that npz
    exists (event loop run with MNV101_DUMP_POINTCLOUD=1 + dump_pointcloud_inputs.py),
    raises an actionable error naming the branches the event loop must dump."""
    d = np.load(inputs_npz, allow_pickle=True)
    if not {"part_gen", "part_reco", "measured_pc"}.issubset(set(d.files)):
        lines = ["[pointcloud] this npz has no padded clouds (part_gen/part_reco/measured_pc).",
                 "  Produce them: run the event loop with MNV101_DUMP_POINTCLOUD=1, then",
                 "  dump_pointcloud_inputs.py. Per-particle features the loop dumps:"]
        for grp in ("reco", "gen"):
            for nm, src in PARTICLE_SCHEMA[grp]:
                lines.append(f"    {nm:14s} <- {src}")
        raise SystemExit("\n".join(lines))
    # Preprocess for the vendored PET, which masks particles by feature-0 (energy) == 0
    # (net.py:128). So: (a) DROP the gen pdg column (categorical; also it made gen 5-feat
    # vs reco 4-feat -> a step-2 shape crash), keeping (E,px,py,pz); (b) scale features
    # MULTIPLICATIVELY x1/1000 (MeV->GeV, mm->m) to O(1) -- valid energies stay >0 and the
    # zero-padding stays exactly 0, so the energy-mask is preserved (z-scoring would break
    # it). Raw ~1000s-scale positions were giving NaN training loss.
    gen = (d["part_gen"][:, :, :4].astype(np.float32)) / 1000.0   # E,px,py,pz (GeV)
    reco = (d["part_reco"].astype(np.float32)) / 1000.0           # E(GeV), x,y,z(m)
    measured = (d["measured_pc"].astype(np.float32)) / 1000.0
    return gen, reco, measured


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
    ap.add_argument("--save-weights", default="",
                    help="npz to save the gen push weights + mc subsample indices "
                         "(for pet_vs_gbdt.py binning).")
    args = ap.parse_args()

    data, mc, imc = build_loaders(args.inputs, mode=args.mode, num_part=args.num_part,
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
        gen_arr = np.asarray(mc.gen)
        num_part = reco_arr.shape[1]
        # model1 reweights at RECO (reco feature count), model2 at GEN (gen feature count);
        # these can differ (reco clusters E,x,y,z vs gen hadrons E,px,py,pz).
        m1 = PET(reco_arr.shape[-1], num_part=num_part, local=(num_part >= 3))
        m2 = PET(gen_arr.shape[-1], num_part=num_part, local=(num_part >= 3))

    of = MultiFold(f"minerva_{args.model}", m1, m2, data, mc,
                   niter=args.niter, epochs=args.epochs, batch_size=1024,
                   weights_folder="/tmp/minerva_pet_weights", verbose=True)
    of.Unfold()
    w = of.reweight(mc.gen, of.model2, batch_size=1000)
    print(f"[smoke] OK: unfolded weights n={len(w)} mean={w.mean():.4f} "
          f"std={w.std():.4f} (finite={np.isfinite(w).all()})")
    if args.save_weights:
        np.savez_compressed(args.save_weights, w_push=np.asarray(w),
                            mc_indices=imc, model=args.model,
                            pass_truth=np.asarray(mc.pass_gen))
        print(f"[smoke] saved push weights + mc indices -> {args.save_weights}")


if __name__ == "__main__":
    main()
