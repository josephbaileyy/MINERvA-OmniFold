#!/usr/bin/env python3
"""Phase A2, Part 3: what physics summaries already exist in PRODUCED files, and what would need
extraction -- measured from the files, not from their names.

Runs under `nd-unfolding/mnv_guarded_run.py` (`--expect-root` = this branch's clean checkout,
`--allow` = the 68cf9d29 checkout for `stage_splits`), in the `module load python` environment
(uproot 5.x). Writes `feature_inventory.json` under --outdir.

What it measures
  1. Every member of the G2 inventory npz: shape, dtype (from the zip headers). Real-data members
     are listed by NAME only; they are not read and no statistic of them is recorded.
  2. The reco E_avail in the inventory (`reco_scalars[:,2]`) against the analysis's own 3D
     pipeline value (`sim_eavail` of `runEventLoopOmniFold_MEFHC_3D.root`), event by event, joined
     on the exact float values of (reco pT, reco p||, true pT, true p||) since the 3D file carries
     no identity branch.
  3. Token-cap saturation in the inventory (12 tokens) on the whole signal inventory, and the
     PRE-truncation multiplicity and energy lost beyond the cap from the untruncated per-cluster
     vectors of one playlist's G2 omnifile, row-aligned to the inventory by event identity.
  4. The theirs-arm globals (hadron_recoil, passive energies, per-PID energy sums) against the
     analysis reco E_avail on the final prior half.
  5. Branch lists read from ACTUAL files: one MasterAnaDev MC AnaTuple named by the committed
     playlist manifest, one R4 slim file, one theirs shard, the G2 merged omnifile; a data tuple is
     opened only to test the PRESENCE of the same branch names (no values read).
  6. The event budget: signal rows, truth-denominator rows, what the comparison used, and how many
     identity-disjoint draws of a given size the inventory supports, including inside the
     identity-hashed stage partition applied to the whole inventory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import time
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import numpy.lib.format as npf


def sha256(path: Path | str, chunk: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        while block := handle.read(chunk):
            h.update(block)
    return h.hexdigest()


def jsonable(o: Any) -> Any:
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, float) and not math.isfinite(o):
        return repr(o)
    return o


def npz_members(path: Path) -> dict[str, Any]:
    out = {}
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            with z.open(info) as f:
                version = npf.read_magic(f)
                shape, fortran, dtype = (npf.read_array_header_1_0(f) if version == (1, 0)
                                         else npf.read_array_header_2_0(f))
            out[info.filename[:-4]] = {"shape": list(shape), "dtype": str(dtype),
                                       "fortran_order": fortran,
                                       "uncompressed_bytes": info.file_size}
    return out


# Column meanings, each traced to the code that WROTE the array (file:line at 68cf9d29).
WRITERS = {
    "part_reco": ("(N,12,3) float32 = per non-muon cluster (E MeV, pos mm, z mm), top-12 by E, "
                  "zero-padded, surplus DROPPED",
                  "dump_pointcloud_inputs.py:90-112 (_pad_tokens/pad_reco_cloud_tokens), "
                  ":270-285 (_reco_row); branches part_reco_E/pos/z filled by "
                  "CVUniverse.h:340-352 GetRecoClusters (cluster_energy/pos/z, "
                  "cluster_isMuontrack==0) via runEventLoopOmniFold.cpp:1007-1011"),
    "reco_view": ("(N,12) view code 1=X 2=U 3=V per kept token", "same permutation; "
                  "runEventLoopOmniFold.cpp:1010 (cluster_view)"),
    "reco_time": ("(N,12) cluster time, ns", "runEventLoopOmniFold.cpp:1011 (cluster_time)"),
    "reco_scalars": ("(N,4) float32 = (sim, sim_pz, sim_eavail, sim_q3) = reco muon pT GeV, reco "
                     "muon p|| GeV, reco E_avail GeV (= NewEavail()/1000), reco q3 GeV; -9999 on "
                     "!pass_reco",
                     "dump_pointcloud_inputs.py:78 SIG_SCALAR_BRANCHES, :147-154, :335; "
                     "runEventLoopOmniFold.cpp:1175-1180; NewEavail at CVUniverse.h:185-193"),
    "truth_scalars": ("(N,4) float32 = (MC, MC_pz, MC_eavail, MC_q3) GeV",
                      "dump_pointcloud_inputs.py:79, :339; runEventLoopOmniFold.cpp:589-590 "
                      "(GetEAvailableTrue CVUniverse.h:361-374, Getq3True)"),
    "reco_muon": ("(N,7) = (px,py,pz,E MeV, phi rad, q/p, minos_ok 0/1); -9999 on !pass_reco",
                  "dump_pointcloud_inputs.py:73-74,156-161; runEventLoopOmniFold.cpp:1014-1020"),
    "reco_vertex": ("(N,3) reco vertex mm; -9999 on !pass_reco",
                    "dump_pointcloud_inputs.py:75,163-168"),
    "part_gen": ("(N,12,5) float32 = truth FS hadrons (E,px,py,pz MeV, pdg), muon and neutrinos "
                 "removed, top-12 by E, surplus DROPPED",
                 "dump_pointcloud_inputs.py:114-116,336-338; CVUniverse.h:289-304 "
                 "GetTruthFSHadrons (mc_FSPart*)"),
    "w_truth": ("(N,) raw truth-leg CV weight", "runEventLoopOmniFold.cpp:595; dump :200"),
    "w_reco": ("(N,) raw reco-leg CV weight; := w_truth on truth-only misses",
               "runEventLoopOmniFold.cpp:1174, :887; dump :201"),
    "pass_reco": ("(N,) bool: sim_pass != 0 AND reco (pT,p||) in the FPS domain",
                  "dump_pointcloud_inputs.py:134-144"),
    "pass_truth": ("(N,) bool: truth (pT,p||) in the FPS domain", "dump_pointcloud_inputs.py:134-144"),
}
REAL_DATA_PREFIXES = ("measured_", "data_")

# Branch families the Phase C summaries need, as regular expressions over the tuple's branch list.
BRANCH_PATTERNS = {
    "analysis_reco_eavail_inputs": r"^(blob_recoil_E_tracker|blob_recoil_E_ecal|"
                                   r"muon_fuzz_per_plane_r80_planeIDs|"
                                   r"muon_fuzz_per_plane_r80_energies)(_sz)?$",
    "calorimetric_recoil": r"(^MasterAnaDev_recoil_E$|^MasterAnaDev_hadron_recoil|recoil_E|"
                           r"_recoil_|[Rr]ecoil)",
    "clusters_pre_truncation": r"^cluster_",
    "blobs": r"^(MasterAnaDev_Blob|blob_)",
    "prongs": r"^prong_",
    "muon_fuzz_iso_passive": r"(muon_fuzz|muon_iso|passive)",
    "michel": r"[Mm]ichel",
    "visible_or_total_energy": r"(visE|visible|_totE|total_E|Evis|energy_sum|E_sum)",
    "multiplicity": r"(^n_|_n$|_nclus|NClusters|nTracks|n_prongs|multiplicity)",
    "truth_final_state": r"^mc_FSPart|^mc_nFSPart",
    "truth_kinematics": r"^mc_(Q2|w|q3|incomingE|intType|current|er_|targetZ|hadronic|X|Y)",
}
ANALYSIS_EAVAIL_BRANCHES = ("blob_recoil_E_tracker", "blob_recoil_E_ecal",
                            "muon_fuzz_per_plane_r80_planeIDs",
                            "muon_fuzz_per_plane_r80_energies",
                            "muon_fuzz_per_plane_r80_planeIDs_sz")
PRE_TRUNCATION_BRANCHES = ("cluster_energy", "cluster_isMuontrack", "cluster_view", "cluster_time",
                           "cluster_pos", "cluster_z", "MasterAnaDev_recoil_E",
                           "MasterAnaDev_hadron_recoil", "mc_nFSPart", "mc_FSPartE",
                           "mc_FSPartPDG")


def branch_listing(path: Path) -> dict[str, Any]:
    import uproot
    f = uproot.open(path)
    trees = {k.split(";")[0]: f[k] for k in f.keys() if f[k].classname == "TTree"}
    out = {"path": str(path), "bytes": path.stat().st_size, "trees": {}}
    for name, tree in trees.items():
        names = list(tree.keys(recursive=False))
        types = {b: str(tree[b].typename) for b in names}
        fam = {k: sorted(b for b in names if re.search(pat, b)) for k, pat in BRANCH_PATTERNS.items()}
        out["trees"][name] = {"entries": int(tree.num_entries), "n_branches": len(names),
                              "families": {k: {b: types[b] for b in v} for k, v in fam.items()}}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--comparison-root", type=Path, required=True)
    ap.add_argument("--closure-npz", type=Path, required=True)
    ap.add_argument("--identity-sidecar", type=Path, required=True)
    ap.add_argument("--omnifile-3d", type=Path, required=True)
    ap.add_argument("--omnifile-g2-playlist", type=Path, required=True)
    ap.add_argument("--omnifile-g2-merged", type=Path, required=True)
    ap.add_argument("--mc-manifest", type=Path, required=True)
    ap.add_argument("--data-manifest", type=Path, required=True)
    ap.add_argument("--r4-slim", type=Path, required=True)
    ap.add_argument("--theirs-shard", type=Path, required=True)
    ap.add_argument("--theirs-cache", type=Path, required=True)
    ap.add_argument("--final-weights", type=Path, required=True,
                    help="one final-stage weights npz, for the halves")
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args(argv)
    args.outdir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    root = args.comparison_root.resolve()
    sys.path.insert(0, str(root / "nd-unfolding" / "pet" / "configuration_comparison"))
    import stage_splits as ss
    import uproot

    out: dict[str, Any] = {"scope": "Phase A2 Part 3: feature inventory for Phases C and D"}

    # ---------------------------------------------------------------- 1. npz members
    members = npz_members(args.closure_npz)
    inv = {}
    for name, m in members.items():
        real = name.startswith(REAL_DATA_PREFIXES)
        ent = {"dtype": m["dtype"], "population": (
            "REAL DATA -- not read, no statistic recorded" if real else
            "MC background" if name.startswith("bkg_") or name == "w_bkg" else
            "metadata" if len(m["shape"]) == 0 else "MC signal inventory")}
        if not real:
            ent["shape"] = m["shape"]
        if name in WRITERS:
            ent["meaning"], ent["written_by"] = WRITERS[name]
        inv[name] = ent
    out["inventory_npz"] = {"path": str(args.closure_npz), "sha256": sha256(args.closure_npz),
                            "members": inv}
    print(f"[fi] npz members listed ({time.time() - t0:.0f}s)", flush=True)

    with np.load(args.closure_npz, allow_pickle=False) as h:
        reco_scalars = np.asarray(h["reco_scalars"])
        truth_scalars = np.asarray(h["truth_scalars"])
        pass_reco = np.asarray(h["pass_reco"]).astype(bool)
        pass_truth = np.asarray(h["pass_truth"]).astype(bool)
        w_reco = np.asarray(h["w_reco"]).astype(np.float64)
        num_part = int(np.asarray(h["num_part"]).item())
    N = pass_truth.size
    both = pass_reco & pass_truth
    ea_reco, ea_true = reco_scalars[:, 2].astype(np.float64), truth_scalars[:, 2].astype(np.float64)

    # ---------------------------------------------------------------- 2. reco E_avail vs 3D
    t3 = uproot.open(args.omnifile_3d)["mc_signal_reco"]
    arr = t3.arrays(["sim", "sim_pz", "MC", "MC_pz", "sim_eavail", "sim_pass"], library="np")
    ok3 = (arr["sim_pass"] != 0) & (arr["sim"] > -9000)

    def key(a, b, c, d):
        a, b, c, d = (np.asarray(x, np.float32).view(np.uint32).astype(np.uint64) for x in (a, b, c, d))
        k1 = (a << np.uint64(32)) | b
        k2 = (c << np.uint64(32)) | d
        return k1 * np.uint64(0x9E3779B97F4A7C15) ^ k2
    k3 = key(arr["sim"][ok3], arr["sim_pz"][ok3], arr["MC"][ok3], arr["MC_pz"][ok3])
    kg = key(reco_scalars[both, 0], reco_scalars[both, 1], truth_scalars[both, 0],
             truth_scalars[both, 1])
    u3, c3 = np.unique(k3, return_counts=True)
    ug, cg = np.unique(kg, return_counts=True)
    single = np.intersect1d(u3[c3 == 1], ug[cg == 1])
    i3 = np.flatnonzero(ok3)[np.isin(k3, single)]
    ig = np.flatnonzero(both)[np.isin(kg, single)]
    o3 = np.argsort(key(arr["sim"][i3], arr["sim_pz"][i3], arr["MC"][i3], arr["MC_pz"][i3]))
    og = np.argsort(key(reco_scalars[ig, 0], reco_scalars[ig, 1], truth_scalars[ig, 0],
                        truth_scalars[ig, 1]))
    i3, ig = i3[o3], ig[og]
    exact_tuple = (np.float32(arr["sim"][i3]) == reco_scalars[ig, 0]) & \
                  (np.float32(arr["sim_pz"][i3]) == reco_scalars[ig, 1]) & \
                  (np.float32(arr["MC"][i3]) == truth_scalars[ig, 0]) & \
                  (np.float32(arr["MC_pz"][i3]) == truth_scalars[ig, 1])
    same_ea = np.float32(arr["sim_eavail"][i3]) == reco_scalars[ig, 2]
    diff = np.abs(np.float64(np.float32(arr["sim_eavail"][i3])) - reco_scalars[ig, 2].astype(np.float64))
    out["reco_eavail_vs_3d_pipeline"] = {
        "g2_field": "reco_scalars[:, 2] (sim_eavail)",
        "3d_file": {"path": str(args.omnifile_3d), "bytes": args.omnifile_3d.stat().st_size,
                    "tree": "mc_signal_reco", "entries": int(t3.num_entries),
                    "reco_passing_entries": int(ok3.sum())},
        "join": ("exact float32 equality of (reco pT, reco p||, true pT, true p||); keys that "
                 "occur once on both sides only"),
        "g2_both_rows": int(both.sum()),
        "matched_events": int(i3.size),
        "matched_with_exact_4tuple": int(exact_tuple.sum()),
        "reco_eavail_bit_equal_float32": int(same_ea[exact_tuple].sum()),
        "reco_eavail_fraction_equal": float(same_ea[exact_tuple].mean()) if exact_tuple.any() else None,
        "max_abs_difference_gev": float(diff[exact_tuple].max()) if exact_tuple.any() else None,
        "definition": ("both are the branch `sim_eavail` = CVUniverse::NewEavail()/1000 = "
                       "1.17 x [(blob_recoil_E_tracker - tracker muon fuzz) + (blob_recoil_E_ecal - "
                       "ECAL muon fuzz)] MeV->GeV, written by runEventLoopOmniFold.cpp:1178; the 3D "
                       "pipeline reads the same branch (3d-unfolding/unfold_3d_omnifold_unbinned.py:"
                       "228, :476)"),
    }
    del arr, t3
    print(f"[fi] 3D reco E_avail join done ({time.time() - t0:.0f}s)", flush=True)

    # reco vs true E_avail on both-rows, the step-1 / step-2 pairing
    r, t = ea_reco[both], ea_true[both]
    w = w_reco[both]
    out["reco_vs_true_eavail_on_both"] = {
        "rows": int(both.sum()),
        "reco_quantiles_gev_5_25_50_75_95": np.quantile(r, [.05, .25, .5, .75, .95]),
        "true_quantiles_gev_5_25_50_75_95": np.quantile(t, [.05, .25, .5, .75, .95]),
        "reco_fraction_exactly_zero": float(np.mean(r == 0)),
        "reco_fraction_negative": float(np.mean(r < 0)),
        "pearson_r": float(np.corrcoef(r, t)[0, 1]),
        "median_reco_over_true_where_true_gt_0.1": float(np.median(r[t > 0.1] / t[t > 0.1])),
        "w_reco_weighted_mean_reco_gev": float(np.average(r, weights=w)),
    }

    # ---------------------------------------------------------------- 3. cap saturation + omnifile
    with np.load(args.closure_npz, allow_pickle=False) as h:
        part_reco = np.asarray(h["part_reco"])
        ntok_r = (part_reco[:, :, 0] != 0).sum(1)
        e_kept_reco = part_reco[:, :, 0].astype(np.float64).sum(1)
        del part_reco
        part_gen = np.asarray(h["part_gen"])
        ntok_g = (part_gen[:, :, 0] != 0).sum(1)
        del part_gen
    out["token_cap_in_inventory"] = {
        "cap": num_part,
        "reco_pass_reco_rows": int(pass_reco.sum()),
        "reco_fraction_at_cap": float(np.mean(ntok_r[pass_reco] == num_part)),
        "reco_tokens_per_event_hist": np.bincount(ntok_r[pass_reco], minlength=num_part + 1),
        "gen_pass_truth_rows": int(pass_truth.sum()),
        "gen_fraction_at_cap": float(np.mean(ntok_g[pass_truth] == num_part)),
        "gen_tokens_per_event_hist": np.bincount(ntok_g[pass_truth], minlength=num_part + 1),
        "reading": "at-cap events are those whose surplus tokens were DROPPED by the dump",
    }
    side = np.load(args.identity_sidecar, allow_pickle=False)
    ev_id = np.asarray(side["sig_event_id"]).astype(np.int64)
    packed = (ev_id[:, 0] << 42) | (ev_id[:, 1] << 21) | ev_id[:, 2]
    order = np.argsort(packed)
    tp = uproot.open(args.omnifile_g2_playlist)["mc_signal_reco"]
    om = tp.arrays(["mc_run", "mc_subrun", "mc_nthEvtInFile", "sim_pass", "part_reco_E",
                    "part_gen_E", "sim_eavail", "MC_eavail"], library="np")
    okey = (om["mc_run"].astype(np.int64) << 42) | (om["mc_subrun"].astype(np.int64) << 21) | \
        om["mc_nthEvtInFile"].astype(np.int64)
    pos = np.searchsorted(packed[order], okey)
    pos = np.clip(pos, 0, packed.size - 1)
    found = packed[order][pos] == okey
    inv_row = np.where(found, order[pos], -1)
    n_clu = np.array([len(x) for x in om["part_reco_E"]])
    n_gen = np.array([len(x) for x in om["part_gen_E"]])
    e_all = np.array([float(np.sum(x)) for x in om["part_reco_E"]])
    e_top = np.array([float(np.sum(np.sort(np.asarray(x))[::-1][:num_part])) for x in om["part_reco_E"]])
    g_all = np.array([float(np.sum(x)) for x in om["part_gen_E"]])
    g_top = np.array([float(np.sum(np.sort(np.asarray(x))[::-1][:num_part])) for x in om["part_gen_E"]])
    rp = (om["sim_pass"] != 0) & found
    rp = rp & pass_reco[np.where(found, inv_row, 0)]
    # row alignment: the omnifile's top-12 energy sum must equal the inventory's kept energy
    align = np.isclose(np.float32(e_top[rp]), np.float32(e_kept_reco[inv_row[rp]]), rtol=1e-5,
                       atol=1e-3)
    tr = found & pass_truth[np.where(found, inv_row, 0)]
    with np.errstate(divide="ignore", invalid="ignore"):
        lost_frac_reco = np.where(e_all > 0, 1 - e_top / e_all, 0.0)
        lost_frac_gen = np.where(g_all > 0, 1 - g_top / g_all, 0.0)
    ea_units = np.float32(om["sim_eavail"][rp]) == reco_scalars[inv_row[rp], 2]
    out["pre_truncation_from_g2_omnifile"] = {
        "file": str(args.omnifile_g2_playlist), "bytes": args.omnifile_g2_playlist.stat().st_size,
        "entries": int(tp.num_entries),
        "rows_found_in_inventory_by_identity": int(found.sum()),
        "pass_reco_rows_compared": int(rp.sum()),
        "row_alignment_top12_energy_equal_fraction": float(align.mean()) if rp.any() else None,
        "sim_eavail_equal_inventory_fraction": float(ea_units.mean()) if rp.any() else None,
        "reco_clusters_per_event_quantiles_50_90_99_max": np.quantile(n_clu[rp], [.5, .9, .99, 1.]),
        "reco_fraction_events_over_cap": float(np.mean(n_clu[rp] > num_part)),
        "reco_energy_fraction_beyond_cap_mean": float(lost_frac_reco[rp].mean()),
        "reco_energy_fraction_beyond_cap_quantiles_50_90_99":
            np.quantile(lost_frac_reco[rp], [.5, .9, .99]),
        "reco_energy_fraction_beyond_cap_on_over_cap_events_mean":
            float(lost_frac_reco[rp][n_clu[rp] > num_part].mean())
            if (n_clu[rp] > num_part).any() else None,
        "sum_all_cluster_E_vs_reco_eavail_pearson": float(np.corrcoef(
            e_all[rp], np.asarray(om["sim_eavail"][rp], float))[0, 1]),
        "gen_hadrons_per_event_quantiles_50_90_99_max": np.quantile(n_gen[tr], [.5, .9, .99, 1.]),
        "gen_fraction_events_over_cap": float(np.mean(n_gen[tr] > num_part)),
        "gen_energy_fraction_beyond_cap_mean": float(lost_frac_gen[tr].mean()),
        "reading": ("part_reco_E / part_gen_E in the G2 omnifiles are the UNTRUNCATED per-event "
                    "vectors the dump truncates to 12; pre-truncation sums, multiplicities and "
                    "overflow energy/count are derivable from these produced files for every "
                    "inventory row, joined by (mc_run, mc_subrun, mc_nthEvtInFile)"),
    }
    del om, tp
    print(f"[fi] omnifile pre-truncation done ({time.time() - t0:.0f}s)", flush=True)

    # ---------------------------------------------------------------- 4. theirs globals
    with np.load(args.final_weights) as blob:
        rows_b = np.asarray(blob["dump_rows_b"]).astype(np.int64)
    cache = np.load(args.theirs_cache)
    glob = np.asarray(cache["prior_globals"])
    prb = pass_reco[rows_b]
    names = ["log muon_fuzz_energy", "log muon_iso_blobs_energy", "log hadron_recoil",
             "log passive_id", "log passive_od", "log passive_sum", "improved_nmichel",
             "muon_present", "diphoton_mass", "charged_pion_prongs",
             "log sumE pid2 blob", "log sumE pid3 prong3", "log sumE pid4 prong8",
             "log sumE pid5 prong13", "log sumE pid6 agg-blob", "log sumE pid7 agg-prong"]
    er = ea_reco[rows_b][prb]
    corr = {}
    for j, nm in enumerate(names):
        v = glob[prb, j].astype(np.float64)
        corr[nm] = {"pearson_with_reco_eavail": float(np.corrcoef(v, er)[0, 1])
                    if v.std() > 0 else None,
                    "median": float(np.median(v))}
    had = np.exp(glob[prb, 2].astype(np.float64)) - 1e-5
    sum_e = sum(np.exp(glob[prb, j].astype(np.float64)) - 1e-3 for j in range(10, 16))
    out["theirs_globals_on_final_prior"] = {
        "cache": str(args.theirs_cache), "rows_pass_reco": int(prb.sum()),
        "columns": corr,
        "hadron_recoil_mev_over_reco_eavail_gev_median": float(np.median(had[er > 0.05] /
                                                                   er[er > 0.05])),
        "sum_of_pid_energy_sums_mev_over_reco_eavail_gev_median":
            float(np.median(sum_e[er > 0.05] / er[er > 0.05])),
        "pearson_hadron_recoil_vs_reco_eavail": float(np.corrcoef(had, er)[0, 1]),
        "reading": ("his globals carry MasterAnaDev_hadron_recoil and energy-preserving per-PID "
                    "sums (aggregate tokens pid 6/7 hold the overflow), computed per event BEFORE "
                    "his cap bites; they exist for every joined signal row via join_sig, not only "
                    "the cache's rows. hadron_recoil is not the analysis E_avail definition"),
    }
    del cache, glob

    # ---------------------------------------------------------------- 5. branch lists
    mc_files = [l.strip() for l in args.mc_manifest.read_text().splitlines() if l.strip()]
    data_files = [l.strip() for l in args.data_manifest.read_text().splitlines() if l.strip()]
    tuple_listing = branch_listing(Path(mc_files[0]))
    tuple_listing["manifest"] = {"path": str(args.mc_manifest), "files": len(mc_files),
                                 "sha256": sha256(args.mc_manifest)}
    f = uproot.open(mc_files[0])
    tree_name = [k.split(";")[0] for k in f.keys() if f[k].classname == "TTree"][0]
    names_mc = set(f[tree_name].keys(recursive=False))
    tuple_listing["tree_used"] = tree_name
    tuple_listing["required_for_analysis_reco_eavail_present"] = {
        b: (b in names_mc) for b in ANALYSIS_EAVAIL_BRANCHES}
    tuple_listing["pre_truncation_and_recoil_branches_present"] = {
        b: (b in names_mc) for b in PRE_TRUNCATION_BRANCHES}
    fd_ = uproot.open(data_files[0])
    dtree = [k.split(";")[0] for k in fd_.keys() if fd_[k].classname == "TTree"][0]
    names_data = set(fd_[dtree].keys(recursive=False))
    out["anatuple_branches"] = {
        "mc": tuple_listing,
        "data_presence_only": {
            "manifest": str(args.data_manifest), "first_file": data_files[0], "tree": dtree,
            "note": "branch NAMES only; no value read",
            "present": {b: (b in names_data) for b in ANALYSIS_EAVAIL_BRANCHES
                        + PRE_TRUNCATION_BRANCHES if not b.startswith("mc_")}},
    }
    out["g2_merged_omnifile"] = branch_listing(args.omnifile_g2_merged)
    out["r4_slim_example"] = branch_listing(args.r4_slim)
    out["theirs_shard_example"] = {"path": str(args.theirs_shard),
                                   "members": npz_members(args.theirs_shard)}
    print(f"[fi] branch lists done ({time.time() - t0:.0f}s)", flush=True)

    # ---------------------------------------------------------------- 6. event budget
    labels = ss.assign(ev_id)
    stage_counts = {s: int((labels == s).sum()) for s in ss.STAGES}
    stage_truth = {s: int(((labels == s) & pass_truth).sum()) for s in ss.STAGES}
    rng_imc = np.sort(np.random.default_rng(0).choice(N, 2_000_000, replace=False))
    in_sub = np.zeros(N, bool)
    in_sub[rng_imc] = True
    final_outside = int(((labels == "final") & ~in_sub).sum())
    budget = {
        "signal_inventory_rows": int(N),
        "truth_denominator_rows_pass_truth": int(pass_truth.sum()),
        "reco_rows_pass_reco": int(pass_reco.sum()),
        "both": int(both.sum()),
        "distinct_events": int(np.unique(packed).size),
        "comparison_used": {"subsample_rows": 2_000_000, "final_stage_rows": 1_200_286,
                            "half_rows_each": 600_143, "half_a_truth_passing": 600_130,
                            "half_b_truth_passing": 600_111, "pseudodata_step1_rows": 250_501,
                            "fraction_of_inventory_in_subsample": 2_000_000 / N},
        "stage_hash_applied_to_whole_inventory": {
            "counts": stage_counts, "pass_truth_counts": stage_truth,
            "final_rows_outside_historical_subsample": final_outside},
        "identity_disjoint_draws": {
            str(n): {"pairs_of_halves_whole_inventory": int(N // (2 * n)),
                     "pairs_inside_final_partition": int(stage_counts["final"] // (2 * n)),
                     "pairs_inside_final_partition_excluding_historical_subsample":
                         int(final_outside // (2 * n))}
            for n in (100_000, 300_000, 600_143, 1_000_000, 2_000_000, 5_000_000)},
        "reading": ("rows are unique events (see recompute_data_path identity_uniqueness), so a "
                    "row-disjoint draw is identity-disjoint. The stage hash is per event, so "
                    "applying it to the whole inventory keeps the historical tuning/pilot/final "
                    "membership of the 2M rows unchanged"),
    }
    try:
        tt = uproot.open(args.omnifile_g2_merged)["mc_truth_denom"]
        budget["g2_merged_mc_truth_denom_entries"] = int(tt.num_entries)
    except Exception as exc:  # pragma: no cover
        budget["g2_merged_mc_truth_denom_entries"] = f"unreadable: {exc}"
    out["event_budget"] = budget
    out["seconds"] = time.time() - t0
    path = args.outdir / "feature_inventory.json"
    path.write_text(json.dumps(jsonable(out), indent=1) + "\n")
    print(f"[fi] wrote {path} ({time.time() - t0:.0f}s)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
