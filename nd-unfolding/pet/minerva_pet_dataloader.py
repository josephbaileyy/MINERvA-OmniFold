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
import os
import random
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
        ("part_reco_E",   "cluster_energy[] non-muon (isMuontrack==0), MeV"),
        ("part_reco_pos", "cluster_pos[] transverse position in the view, mm"),
        ("part_reco_z",   "cluster_z[] z position, mm"),
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
                  bootstrap=False, bootstrap_seed=None, seed=0, rank=0, size=1,
                  memmap_dir=None):
    """Return (data_loader, mc_loader) vendored DataLoaders from our OmniFold arrays.

    rank/size + memmap_dir: for horovod point-cloud training, load from a .npy dir
    (npz_to_npy.py output) and materialize only this rank's [rank::size] stride, so each
    of `size` ranks holds ~1/size of the 32.8M-event cloud (fits a 229 GB node at full
    stats instead of OOMing). The plain (rank=0, size=1, memmap_dir=None) path is
    byte-for-byte the original behaviour.
    """
    from omnifold import DataLoader  # vendored

    if memmap_dir and mode == "pointcloud":
        return _build_pointcloud_memmap(memmap_dir, max_events, bootstrap, bootstrap_seed,
                                        seed, rank, size)

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

    if bootstrap_seed is None and bootstrap:
        bootstrap_seed = seed
    if bootstrap_seed is not None:
        from pet_bootstrap import poisson_event_weights
        measured_weights, w_truth = poisson_event_weights(
            measured_weights, w_truth, int(bootstrap_seed))
        print(f"[bootstrap] measured-data and MC Poisson draws seed={bootstrap_seed} "
              "(independent RNGs; one coherent full-sample MC event draw)")

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
                      bootstrap=False)
    mc = DataLoader(reco=MCreco, gen=MCgen, pass_reco=pass_reco, pass_gen=pass_truth,
                    weight=w_truth, normalize=True, bootstrap=False)
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
    # Sanitize: a single non-finite entry in part_reco was enough to NaN the step-1
    # reco classifier mid-epoch once the larger (>=8M) training sample sampled it (the
    # 2M probe never hit it). Map non-finite -> 0, which is also the pad/mask sentinel
    # (PET masks particles by feature-0==0), so a corrupt particle becomes a masked slot.
    gen = np.nan_to_num(gen, nan=0.0, posinf=0.0, neginf=0.0)
    reco = np.nan_to_num(reco, nan=0.0, posinf=0.0, neginf=0.0)
    measured = np.nan_to_num(measured, nan=0.0, posinf=0.0, neginf=0.0)
    return gen, reco, measured


def _pc_scale(a):
    """Same preprocessing _load_pointcloud applies: MeV->GeV / mm->m, then non-finite->0
    (0 is the PET energy-mask sentinel). Elementwise, so subsample-then-scale is identical
    to scale-then-subsample."""
    return np.nan_to_num(a.astype(np.float32) / 1000.0, nan=0.0, posinf=0.0, neginf=0.0)


def _build_pointcloud_memmap(npy_dir, max_events, bootstrap, bootstrap_seed,
                             seed, rank, size):
    """Memory-mapped, rank-strided point-cloud loader (see build_loaders docstring).

    Materializes only this rank's rows: draws the global subsample indices with the SAME
    rng draw-order as build_loaders, strides them [rank::size], then fancy-indexes the
    memmaps (reads ~len/size rows from disk, never the full array). Row order within a
    rank is irrelevant (OmniFold shuffles internally), so indices are sorted for
    sequential I/O. Returns (data, mc, imc) like build_loaders."""
    import os
    from omnifold import DataLoader  # vendored
    j = lambda k: os.path.join(npy_dir, f"{k}.npy")
    mm_gen  = np.load(j("part_gen"),  mmap_mode="r")    # (N,12,5) E,px,py,pz,pdg
    mm_reco = np.load(j("part_reco"), mmap_mode="r")    # (N,12,3) E,x,y,z
    mm_meas = np.load(j("measured_pc"), mmap_mode="r")  # (M,12,3)
    pass_reco_all  = np.load(j("pass_reco"),  mmap_mode="r")
    pass_truth_all = np.load(j("pass_truth"), mmap_mode="r")
    w_truth_all    = np.load(j("w_truth"),    mmap_mode="r")
    meas_w_all     = np.load(j("measured_weights"), mmap_mode="r")
    N, M = mm_gen.shape[0], mm_meas.shape[0]

    # Global subsample indices — identical rng draw-order to the original build_loaders
    # (default_rng(seed): mc choice first, then data choice) so a size=1 run reproduces it.
    if max_events is None:
        all_imc, all_ida = np.arange(N), np.arange(M)
    else:
        rng = np.random.default_rng(seed)
        all_imc = rng.choice(N, min(max_events, N), replace=False)
        all_ida = rng.choice(M, min(max_events, M), replace=False)
    imc = np.sort(all_imc[rank::size])   # this rank's clean 1/size partition
    ida = np.sort(all_ida[rank::size])

    MCgen  = _pc_scale(mm_gen[imc][:, :, :4])   # drop categorical pdg col -> E,px,py,pz
    MCreco = _pc_scale(mm_reco[imc])            # E,x,y,z
    measured = _pc_scale(mm_meas[ida])
    pass_reco  = np.asarray(pass_reco_all[imc])
    pass_truth = np.asarray(pass_truth_all[imc])
    w_truth    = np.asarray(w_truth_all[imc]).astype(np.float32)
    meas_w     = np.asarray(meas_w_all[ida]).astype(np.float32)

    if bootstrap_seed is None and bootstrap:
        bootstrap_seed = seed
    if bootstrap_seed is not None:
        # Draw on the GLOBAL event ids, then select this rank/subsample so the
        # training and full-sample extraction use one coherent draw per MC event.
        rd = np.random.default_rng(int(bootstrap_seed))
        rm = np.random.default_rng(int(bootstrap_seed) + 10_000_000)
        data_factor = rd.poisson(1.0, M).astype(np.float32)
        mc_factor = rm.poisson(1.0, N).astype(np.float32)
        meas_w *= data_factor[ida]
        w_truth *= mc_factor[imc]
        print(f"[bootstrap] rank={rank} coherent global data/MC Poisson seed={bootstrap_seed}")
    data = DataLoader(reco=measured, weight=meas_w, normalize=True, bootstrap=False)
    mc = DataLoader(reco=MCreco, gen=MCgen, pass_reco=pass_reco, pass_gen=pass_truth,
                    weight=w_truth, normalize=True, bootstrap=False)
    return data, mc, imc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default="of_inputs_3d.npz")
    ap.add_argument("--mode", default="scalar", choices=["scalar", "pointcloud"])
    ap.add_argument("--num-part", type=int, default=1)
    ap.add_argument("--max-events", type=int, default=None)
    ap.add_argument("--memmap-dir", default=None,
                    help="dir of .npy files (npz_to_npy.py output) for memory-mapped, "
                         "rank-strided point-cloud loading under horovod (srun -n N); each "
                         "rank materializes only its 1/size stride -> full 32.8M fits one node.")
    ap.add_argument("--smoke", action="store_true",
                    help="instantiate the vendored MLP/PET + run a 1-iter MultiFold on a "
                         "subsample to prove the engine unfolds our data (needs TF/GPU).")
    ap.add_argument("--model", default="mlp", choices=["mlp", "pet"])
    ap.add_argument("--niter", type=int, default=1)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--save-weights", default="",
                    help="npz to save the gen push weights + mc subsample indices "
                         "(for pet_vs_gbdt.py binning).")
    ap.add_argument("--reweight-all", action="store_true",
                    help="after training (on the --max-events subsample), evaluate the push "
                         "weights on the FULL gen cloud via batched inference, so the "
                         "downstream absolute cross section uses full statistics. "
                         "--save-weights then stores full-stats w_push + mc_indices=arange(N).")
    ap.add_argument("--closure", action="store_true",
                    help="self-consistency closure: use MC reco (pass_reco events) as "
                         "pseudo-data instead of the real data; the recovered truth should "
                         "reproduce the MC truth (validated downstream with completeness=1).")
    ap.add_argument("--seed", type=int, default=0,
                    help="RNG seed for the --max-events subsample draw (build_loaders' "
                         "rng.choice); network init/dropout/batch-shuffle are already "
                         "TF-unseeded (genuinely different every process). Vary this across "
                         "job-array tasks to get independent seed replicas for a "
                         "retraining-response convergence check.")
    ap.add_argument("--bootstrap-seed", type=int, default=None,
                    help="full PET statistical replica: Poisson-fluctuate measured data "
                         "and MC with independent RNGs, then retrain from scratch")
    ap.add_argument("--estimator-seed", type=int, default=42,
                    help="fixed Python/NumPy/TensorFlow estimator seed; keep constant "
                         "across statistical replicas so C_stat varies only the bootstrap")
    args = ap.parse_args()

    # Horovod data-parallel rank/size, read from env (not horovod) so we don't import TF
    # before omnifold runs hvd.init(). Two launchers must both work and both equal
    # hvd.rank()/hvd.size():
    #   * bare `srun -n N` (Perlmutter): sets SLURM_PROCID(0..N-1)/SLURM_NTASKS(N).
    #   * an MPI launcher `horovodrun/mpirun -np N` (e.g. inside an Apptainer container
    #     whose horovod has MPI but no Gloo -- Delta NGC path): sets OMPI_COMM_WORLD_*,
    #     while an outer `srun -n1` would otherwise pin SLURM_PROCID=0 for all ranks.
    # Prefer the MPI vars when an MPI launcher is in charge; else SLURM; else single-process.
    if "OMPI_COMM_WORLD_SIZE" in os.environ:
        rank = int(os.environ["OMPI_COMM_WORLD_RANK"])
        size = int(os.environ["OMPI_COMM_WORLD_SIZE"])
    else:
        rank = int(os.environ.get("SLURM_PROCID", 0))
        size = int(os.environ.get("SLURM_NTASKS", 1))

    data, mc, imc = build_loaders(args.inputs, mode=args.mode, num_part=args.num_part,
                                  max_events=args.max_events, rank=rank, size=size,
                                  memmap_dir=args.memmap_dir, seed=args.seed,
                                  bootstrap_seed=args.bootstrap_seed)

    if args.closure:
        # Pseudo-data = MC reco of the reco-passing events, weighted by the (normalized)
        # prior. A perfect unfold then pushes the truth back onto the MC truth.
        from omnifold import DataLoader
        reco_mc = np.asarray(mc.reco); prc = np.asarray(mc.pass_reco)
        data = DataLoader(reco=reco_mc[prc], weight=np.asarray(mc.weight)[prc],
                          normalize=True)
        print(f"[closure] pseudo-data = MC reco (pass_reco) n={int(prc.sum())} "
              "-> recovered truth should reproduce MC truth")
    print(f"[loaders] data reco shape={np.asarray(data.reco).shape} "
          f"(sumw={data.weight.sum():.3e})")
    print(f"[loaders] mc   reco shape={np.asarray(mc.reco).shape} gen shape="
          f"{np.asarray(mc.gen).shape}")
    print(f"[loaders] mc   pass_reco={mc.pass_reco.mean():.3f}  "
          f"pass_gen={mc.pass_gen.mean():.3f}")

    if not args.smoke:
        print("[ok] DataLoaders built. Pass --smoke (TF/GPU env) to run a MultiFold step.")
        return

    # Statistical replicas must not fold estimator jitter into C_stat. Seed all
    # classifier-side RNGs after data/subsample construction but before model
    # creation. ML-seed studies can vary this explicitly in their own campaign.
    random.seed(args.estimator_seed)
    np.random.seed(args.estimator_seed)
    import tensorflow as tf
    tf.keras.utils.set_random_seed(args.estimator_seed)
    print(f"[estimator] fixed Python/NumPy/TensorFlow seed={args.estimator_seed}")

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

    # Multi-GPU via horovod. build_loaders already gave this rank its own [rank::size] data
    # stride, so MultiFold gets size=1 (its internal step-counting + DataLoader slicing must
    # NOT slice again) but the real rank so only rank 0 writes checkpoints/logs. The horovod
    # gradient allreduce is wired in omnifold via hvd.DistributedOptimizer (gated on the
    # horovod import, independent of `size`), so the 4 ranks still train data-parallel.
    of = MultiFold(f"minerva_{args.model}", m1, m2, data, mc,
                   niter=args.niter, epochs=args.epochs, batch_size=1024,
                   size=1, rank=rank,
                   weights_folder="/tmp/minerva_pet_weights", verbose=(rank == 0))
    of.Unfold()

    # Unfold() (incl. horovod gradient allreduce + weight broadcast) runs on all ranks; after
    # it the trained model2 is identical everywhere. Only rank 0 evaluates the push weights on
    # the full gen cloud and writes the output, so workers exit here to avoid redundant work
    # and clobbering the same --save-weights file.
    if rank != 0:
        return

    w = of.reweight(mc.gen, of.model2, batch_size=1000)
    print(f"[smoke] OK: unfolded weights n={len(w)} mean={w.mean():.4f} "
          f"std={w.std():.4f} (finite={np.isfinite(w).all()})")
    save_pass_gen = np.asarray(mc.pass_gen)

    if args.reweight_all:
        # Trained on the subsample; now apply the FINAL gen model (model2) to the FULL gen
        # cloud so the absolute cross section is binned over full statistics. The push weight
        # is a per-event likelihood ratio (normalization-independent), so evaluating it on the
        # full set is valid even though training used a subsample.
        # rank 0 only (workers already returned): load the FULL gen cloud unstrided
        # (rank=0,size=1) so the saved push weights cover all 32.8M events.
        _, full_mc, full_imc = build_loaders(args.inputs, mode=args.mode,
                                             num_part=args.num_part, max_events=None,
                                             rank=0, size=1, memmap_dir=args.memmap_dir)
        full_gen = np.asarray(full_mc.gen)
        if args.model == "mlp" and full_gen.ndim == 3:
            full_gen = full_gen.reshape(full_gen.shape[0], -1)
        print(f"[reweight-all] evaluating push weights on FULL gen n={full_gen.shape[0]}")
        w = of.reweight(full_gen, of.model2, batch_size=4096)
        imc = full_imc
        save_pass_gen = np.asarray(full_mc.pass_gen)
        print(f"[reweight-all] full-stats w_push n={len(w)} mean={w.mean():.4f} "
              f"std={w.std():.4f} (finite={np.isfinite(w).all()})")
        del full_mc, full_gen

    if args.save_weights:
        extra = {}
        if args.bootstrap_seed is not None:
            # Persist the SAME global MC-event Poisson draw used by build_loaders.
            # Downstream PET xsec extraction multiplies w_truth by this factor, so
            # the replica remains coherent from classifier training through final
            # truth binning (the previous frozen-w_push C_stat did neither).
            if args.memmap_dir:
                n_global = int(np.load(os.path.join(args.memmap_dir, "w_truth.npy"),
                                       mmap_mode="r").shape[0])
            else:
                with np.load(args.inputs, allow_pickle=True) as zin:
                    n_global = int(zin["w_truth"].shape[0])
            from pet_bootstrap import mc_poisson_factor
            mc_factor_global = mc_poisson_factor(n_global, args.bootstrap_seed)
            extra["mc_bootstrap_factor"] = mc_factor_global[np.asarray(imc, dtype=np.int64)]
            extra["bootstrap_seed"] = np.asarray(int(args.bootstrap_seed))
            extra["bootstrap_contract"] = np.asarray(
                "measured data fluctuated + PET retrained + coherent MC factor applied in extraction")
        np.savez_compressed(args.save_weights, w_push=np.asarray(w),
                            mc_indices=imc, model=args.model,
                            pass_truth=save_pass_gen, closure=bool(args.closure),
                            **extra)
        print(f"[smoke] saved push weights + mc indices -> {args.save_weights}")


if __name__ == "__main__":
    main()
