#!/usr/bin/env python3
"""MP-2 S1 (PLAN.md section 3.3): the aligned final-state dump for the s5p analysis-MC rows.

No new event loop. The s5p inputs ``of_inputs_5d.npz`` take ``MCgen`` from the 5D omnifile's ``mc_signal_reco`` tree
(``nn_dump_inputs.py:84``, ``collect_signal_nd``), which carries no event identity. That tree is NOT in
``mc_truth_denom`` order: the event loop fills it from the reco loop and then appends the truth-only misses
(``runEventLoopOmniFold.cpp`` ``AppendTruthOnlyMisses``). The G2 full-phase-space production wrote the same
``mc_signal_reco`` structure with identity (mc_run, mc_subrun, mc_nthEvtInFile). So:

  1. read each playlist's G2 ``mc_signal_reco`` rows and keep those inside the kinematic truth phase space
     (pT, p_par box and theta_mu < 20 deg, the rule MP-5's T1 used on ``mc_truth_denom``);
  2. ADMISSION: those blocks, concatenated in playlist order, must equal ``MCgen`` BITWISE after the float32 cast
     ``nn_dump_inputs.py`` applies, ``w_truth x pot_scale`` must equal ``of_inputs_5d.w_truth`` bitwise, and the
     recomputed ``pass_truth`` must equal the stored one. Any failure: exit 3 before anything is joined or written;
  3. join each row by identity (``event_identity.pack_identity``) to its MasterAnaDev ``Truth`` entry (first
     occurrence in manifest order, then tree order, as the event loop's dedupe keeps) and carry the final-state
     particle list ``mc_FSPart{PDG,E,Px,Py,Pz}`` (MeV, detector frame, as stored), ``mc_targetZ/A``, ``mc_incomingE``
     and a few truth scalars;
  4. join controls: every row matched; duplicate MAD keys identical in every carried field; the MAD lepton rotated
     into the MAT beam frame equals the G2 truth muon; E_avail recomputed from the carried particle list by MAT's
     ``GetEAvailableTrue`` (CVUniverse.h:361-374, sequential sum, MeV -> GeV) against the stored ``MC_eavail``.

Output, one uncompressed npz per playlist (``s1_<pl>.npz``), rows in MCgen order, the block starting at global MCgen
row ``mcgen_row0``. Ragged particles: particles of row i are ``fs_*[fs_offsets[i]:fs_offsets[i+1]]``.

Usage (omnifold_py310: uproot + awkward, no ROOT): python3 mp2_s1_dump.py OUTDIR NPROC TMPDIR
"""
import hashlib
import json
import math
import multiprocessing as mp
import os
import resource
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

NS = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
G2_DIR = f"{NS}/nd-unfolding/g2_fullevent/final"
OMNI5D = f"{NS}/nd-unfolding/runEventLoopOmniFold_5D_MEFHC.root"
OMNI5D_SHA = "b6d2651cfdbc52790cc7ed6032f2062a3e0ea50c12d63725beba29098dd5175a"
OFIN = f"{NS}/nd-unfolding/of_inputs_5d.npz"
OFIN_SHA = "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f"
MANIFESTS = f"{NS}/2d-unfolding/playlist_manifests"
PLAYLISTS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
A_BEAM = -0.05887                         # MinervaUnits::numi_beam_angle_rad
MAX_THETA = math.radians(20.0)            # unfold_2d_omnifold_unbinned.MAX_MUON_THETA_RAD
SCAL = ["MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W"]   # MCgen column order (pt, pz, eavail, q3, W)
G2COLS = SCAL + ["w_truth", "mc_run", "mc_subrun", "mc_nthEvtInFile", "mu_true_px", "mu_true_py", "mu_true_pz",
                 "mu_true_E", "sim_pass"]
MAD_SCALARS = ["mc_run", "mc_subrun", "mc_nthEvtInFile", "mc_nFSPart", "mc_targetZ", "mc_targetA", "mc_targetNucleon",
               "mc_intType", "mc_current", "mc_incoming", "mc_incomingE", "mc_Q2"]
MAD_VEC4 = ["mc_incomingPartVec", "mc_primFSLepton", "mc_vtx"]
FS = ["mc_FSPartPDG", "mc_FSPartE", "mc_FSPartPx", "mc_FSPartPy", "mc_FSPartPz"]
FS_OUT = {"mc_FSPartPDG": "fs_pdg", "mc_FSPartE": "fs_E", "mc_FSPartPx": "fs_px", "mc_FSPartPy": "fs_py",
          "mc_FSPartPz": "fs_pz"}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def in_ps(pt, pz, lo_t, hi_t, lo_z, hi_z):
    """u2d.in_truth_phase_space, vectorized; theta re-decided with math.atan2 within 1e-12 of 20 deg (MP-5)."""
    fin = np.isfinite(pt) & np.isfinite(pz)
    with np.errstate(invalid="ignore"):
        box = fin & (pt >= lo_t) & (pt <= hi_t) & (pz >= lo_z) & (pz <= hi_z)
        th = np.arctan2(pt, pz)
    ok = box & (th < MAX_THETA)
    near = np.where(box & (np.abs(th - MAX_THETA) < 1e-12))[0]
    for i in near:
        ok[i] = math.atan2(float(pt[i]), float(pz[i])) < MAX_THETA
    return ok, int(near.size)


def read_g2(p):
    import uproot
    t = uproot.open(f"{G2_DIR}/runEventLoopOmniFold_G2_FPS_{p}.root")["mc_signal_reco"]
    d = t.arrays(G2COLS, library="np")
    return p, int(t.num_entries), {k: np.asarray(v) for k, v in d.items()}


def read_mad(task):
    """One MasterAnaDev Truth tree: the entries whose identity is in the playlist's key set, in tree order."""
    import awkward as ak
    import uproot
    import event_identity as eid
    ifile, fn, keyfile = task
    K = np.load(keyfile, mmap_mode="r")
    t = uproot.open(fn)["Truth"]
    n_all = int(t.num_entries)
    s = t.arrays(MAD_SCALARS + MAD_VEC4, library="np")
    key = eid.pack_identity(s["mc_run"], s["mc_subrun"], s["mc_nthEvtInFile"])
    pos = np.clip(np.searchsorted(K, key), 0, K.size - 1)
    idx = np.nonzero(np.asarray(K[pos]) == key)[0]
    out = {"ifile": ifile, "n_all": n_all, "key": key[idx], "tree_entry": idx.astype(np.int64)}
    for k in MAD_SCALARS:
        out[k] = np.asarray(s[k])[idx]
    for k in MAD_VEC4:
        out[k] = np.asarray(s[k])[idx].reshape(-1, 4)
    a = t.arrays(FS, library="ak")[idx]
    out["fs_n"] = ak.to_numpy(ak.num(a["mc_FSPartPDG"])).astype(np.int64)
    for k in FS:
        out[FS_OUT[k]] = ak.to_numpy(ak.flatten(a[k]))
    return out


def eavail_mat(pdg, E, off):
    """CVUniverse::GetEAvailableTrue, in particle order (sequential double sum), MeV."""
    contrib = np.where(pdg == 22, E, 0.0)
    contrib = np.where(np.abs(pdg) == 211, E - 135.0, contrib)
    contrib = np.where(pdg == 111, E, contrib)
    contrib = np.where(pdg == 2212, E - 938.27, contrib)
    n = np.diff(off)
    rec = np.zeros(n.size)
    for k in range(int(n.max()) if n.size else 0):
        m = n > k
        rec[m] = rec[m] + contrib[off[:-1][m] + k]
    return rec


def main():
    out, nproc, tmp = Path(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    import awkward
    import uproot
    import event_identity as eid
    res = {"schema": "mp2-s1-dump/1", "argv": sys.argv, "host": os.uname().nodename,
           "slurm_job": os.environ.get("SLURM_JOB_ID"), "python": sys.version.split()[0],
           "numpy": np.__version__, "uproot": uproot.__version__, "awkward": awkward.__version__,
           "code": {}, "inputs": {}, "controls": {}, "playlists": {}}
    for m in (sys.modules[__name__], eid):
        p = Path(m.__file__).resolve()
        res["code"][m.__name__] = {"file": str(p), "sha256": sha256(p)}
    ctx = mp.get_context("spawn")
    pool = ctx.Pool(nproc)

    # ---- C0: digests. Binding: of_inputs_5d (the admission reference) and the 5D omnifile (its POT scale).
    g2f = {p: f"{G2_DIR}/runEventLoopOmniFold_G2_FPS_{p}.root" for p in PLAYLISTS}
    big = [OFIN, OMNI5D] + [g2f[p] for p in PLAYLISTS]
    digests = dict(zip(big, pool.map(sha256, big)))
    want = {OFIN: OFIN_SHA, OMNI5D: OMNI5D_SHA}
    for p in PLAYLISTS:
        rc = json.loads(Path(f"{G2_DIR}/G2_receipt_{p}.json").read_text())
        want[g2f[p]] = rc.get("final_root", {}).get("sha256")
        man = f"{MANIFESTS}/{p}_MC.txt"
        res["inputs"][man] = {"sha256": sha256(man), "receipt_manifest_mc_sha256": rc.get("manifest_mc", {}).get("sha256")}
    for f in big:
        res["inputs"][f] = {"sha256": digests[f], "expected": want[f], "match": digests[f] == want[f]}
    c0 = {"binding_pass": all(res["inputs"][f]["match"] for f in (OFIN, OMNI5D)),
          "g2_match_receipts": {p: res["inputs"][g2f[p]]["match"] for p in PLAYLISTS},
          "manifest_match_receipts": {p: res["inputs"][f"{MANIFESTS}/{p}_MC.txt"]["sha256"]
                                      == res["inputs"][f"{MANIFESTS}/{p}_MC.txt"]["receipt_manifest_mc_sha256"]
                                      for p in PLAYLISTS}}
    c0["pass"] = c0["binding_pass"]
    res["controls"]["C0_digests"] = c0
    print("C0", json.dumps(c0), flush=True)
    if not c0["pass"]:
        return finish(res, out, t0, 3)

    fo = uproot.open(OMNI5D)
    data_pot, mc_pot = float(fo["dataPOTUsed"].member("fVal")), float(fo["mcPOTUsed"].member("fVal"))
    pot_scale = data_pot / mc_pot          # u2d.get_pot_scales
    n_sig_omni = int(fo["mc_signal_reco"].num_entries)
    res["pot"] = {"data": data_pot, "mc": mc_pot, "scale": pot_scale, "omnifile_mc_signal_reco_entries": n_sig_omni}

    z = np.load(OFIN, allow_pickle=True)
    MCgen = np.asarray(z["MCgen"])
    WT = np.asarray(z["w_truth"])
    PT = np.asarray(z["pass_truth"], bool)
    e0, e1 = np.asarray(z["edges_0"], float), np.asarray(z["edges_1"], float)
    res["of_inputs"] = {"MCgen_shape": list(MCgen.shape), "MCgen_dtype": str(MCgen.dtype), "w_truth_dtype": str(WT.dtype),
                        "n_pass_truth": int(PT.sum()), "axes": [str(a) for a in z["axes"]]}
    print("of_inputs", json.dumps(res["of_inputs"]), flush=True)

    # ---- G2 mc_signal_reco blocks inside the kinematic truth phase space
    blocks = {}
    for p, n_ent, g in pool.imap(read_g2, PLAYLISTS):
        ps, near = in_ps(g["MC"], g["MC_pz"], e0[0], e0[-1], e1[0], e1[-1])
        blocks[p] = {k: v[ps] for k, v in g.items()}
        res["playlists"][p] = {"g2_signal_entries": n_ent, "g2_in_kinematic_ps": int(ps.sum()), "near_20deg": near}
        print(p, json.dumps(res["playlists"][p]), flush=True)
        del g

    # ---- C1 ADMISSION: bitwise against MCgen, w_truth and pass_truth, in a discovered playlist order
    def cast(b):
        # of_inputs_5d.npz (2026-06-27) was written by the producer at 21f2a003, which stored a non-finite truth value
        # as -9999.0 (collect_signal_nd: `tex[k].append(tv if math.isfinite(tv) else -9999.0)`, same for pt/pz);
        # the finite-truth gate replaced that on 2026-07-14 (07c18aee). Restated here, then the float32 cast.
        return np.column_stack([np.where(np.isfinite(b[c]), b[c], -9999.0) for c in SCAL]).astype(np.float32)

    def same(a, b):
        return bool(np.array_equal(a, b, equal_nan=True))
    off, order, left = 0, [], list(PLAYLISTS)
    while left:
        cand = []
        for p in left:
            n = blocks[p]["MC"].size
            if off + n <= MCgen.shape[0] and same(cast({c: blocks[p][c][:64] for c in SCAL}), MCgen[off:off + min(n, 64)]):
                cand.append(p)
        cand = [p for p in cand if same(cast(blocks[p]), MCgen[off:off + blocks[p]["MC"].size])]
        if len(cand) != 1:
            break
        order.append(cand[0])
        res["playlists"][cand[0]]["mcgen_row0"] = off
        off += blocks[cand[0]]["MC"].size
        left.remove(cand[0])
    c1 = {"n_mcgen_rows": int(MCgen.shape[0]), "n_g2_ps_rows": int(sum(b["MC"].size for b in blocks.values())),
          "order": order, "unplaced": left, "rows_placed": int(off)}
    c1["MCgen_bitwise"] = (not left) and off == MCgen.shape[0]
    c1["n_rows_nonfinite_truth_sentinel"] = {c: int(sum(int((~np.isfinite(b[c])).sum()) for b in blocks.values()))
                                             for c in SCAL}
    if c1["MCgen_bitwise"]:
        wcat = np.concatenate([blocks[p]["w_truth"] * pot_scale for p in order])
        c1["w_truth_bitwise"] = bool(np.array_equal(wcat, WT))
        c1["w_truth_max_rel"] = float(np.max(np.abs(wcat - WT) / np.where(WT != 0, np.abs(WT), 1.0)))
        del wcat
        ptc = np.concatenate([in_ps(blocks[p]["MC"], blocks[p]["MC_pz"], e0[0], e0[-1], e1[0], e1[-1])[0]
                              for p in order])
        c1["pass_truth_recomputed_equal"] = bool(np.array_equal(ptc, PT))
        c1["n_pass_truth_false"] = int((~PT).sum())
        del ptc
    c1["pass"] = bool(c1["MCgen_bitwise"] and c1.get("w_truth_bitwise") and c1.get("pass_truth_recomputed_equal"))
    res["controls"]["C1_admission"] = c1
    print("C1", json.dumps(c1), flush=True)
    del MCgen, WT
    if not c1["pass"]:
        return finish(res, out, t0, 3)

    # ---- join to MasterAnaDev Truth, per playlist, and write
    c2 = {"n_rows": 0, "n_matched": 0, "n_mad_dup_keys": 0, "n_mad_dup_fields_differ": 0, "g2_identity_unique": True,
          "mu_true_maxabs_MeV": 0.0, "mu_true_E_maxabs_MeV": 0.0, "nFSPart_equals_len": True}
    c3 = {"eavail_bitwise_rows": 0, "eavail_maxabs_GeV": 0.0, "rows_with_mu_in_fs_equal_primFSLepton_E": 0,
          "n_particles": 0, "max_particles_per_row": 0, "targetZ_counts": {}, "n_rows_targetZ_1": 0}
    for p in order:
        tp = time.time()
        b = blocks.pop(p)
        gk = eid.pack_identity(b["mc_run"], b["mc_subrun"], b["mc_nthEvtInFile"])
        if np.unique(gk).size != gk.size:
            c2["g2_identity_unique"] = False
        K = np.unique(gk)
        kf = tmp / f"keys_{p}.npy"
        np.save(kf, K)
        files = [ln.strip() for ln in Path(f"{MANIFESTS}/{p}_MC.txt").read_text().splitlines() if ln.strip()]
        parts = sorted(pool.map(read_mad, [(i, fn, str(kf)) for i, fn in enumerate(files)], chunksize=1),
                       key=lambda r: r["ifile"])
        n_truth = sum(r["n_all"] for r in parts)
        cat = {k: np.concatenate([r[k] for r in parts]) for k in parts[0] if k not in ("ifile", "n_all")}
        src_file = np.concatenate([np.full(r["key"].size, r["ifile"], np.int32) for r in parts])
        del parts
        moff = np.zeros(cat["fs_n"].size + 1, np.int64)
        np.cumsum(cat["fs_n"], out=moff[1:])
        uk, first = np.unique(cat["key"], return_index=True)    # mergesort: the first occurrence is kept
        dup = np.setdiff1d(np.arange(cat["key"].size), first)
        ndiff = 0
        if dup.size:
            keep_of = first[np.searchsorted(uk, cat["key"][dup])]
            for k in MAD_SCALARS + MAD_VEC4:
                a_, b_ = cat[k][dup], cat[k][keep_of]
                ndiff += int(np.sum(~((a_ == b_) | (np.isnan(a_) & np.isnan(b_)))) if a_.dtype.kind == "f"
                             else np.sum(a_ != b_))
            for i, j in zip(dup.tolist(), keep_of.tolist()):
                for k in FS_OUT.values():
                    if not np.array_equal(cat[k][moff[i]:moff[i + 1]], cat[k][moff[j]:moff[j + 1]]):
                        ndiff += 1
        pos = np.clip(np.searchsorted(uk, gk), 0, uk.size - 1)
        hit = uk[pos] == gk
        c2["n_rows"] += int(gk.size)
        c2["n_matched"] += int(hit.sum())
        c2["n_mad_dup_keys"] += int(dup.size)
        c2["n_mad_dup_fields_differ"] += ndiff
        if not hit.all():
            c2["failed_playlist"] = p
            break
        j = first[pos]
        cnt = cat["fs_n"][j]
        off_o = np.zeros(gk.size + 1, np.int64)
        np.cumsum(cnt, out=off_o[1:])
        gidx = np.repeat(moff[j] - off_o[:-1], cnt) + np.arange(off_o[-1], dtype=np.int64)
        rec = {"mcgen_row0": np.int64(res["playlists"][p]["mcgen_row0"]), "n_rows": np.int64(gk.size),
               "pass_truth": PT[res["playlists"][p]["mcgen_row0"]:res["playlists"][p]["mcgen_row0"] + gk.size],
               "mc_run": b["mc_run"], "mc_subrun": b["mc_subrun"], "mc_nthEvtInFile": b["mc_nthEvtInFile"],
               "sim_pass": b["sim_pass"], "w_truth_raw": b["w_truth"], "pot_scale": np.float64(pot_scale),
               "mad_file_index": src_file[j], "mad_tree_entry": cat["tree_entry"][j], "fs_offsets": off_o}
        for c in SCAL:
            rec["g2_" + c] = b[c]
        for k in MAD_SCALARS[3:] + MAD_VEC4:
            rec[k] = cat[k][j]
        for k in FS_OUT.values():
            rec[k] = cat[k][gidx]
        del cat, gidx
        if not np.array_equal(rec["mc_nFSPart"], cnt):
            c2["nFSPart_equals_len"] = False
        lep = rec["mc_primFSLepton"]
        s_, c_ = math.sin(A_BEAM), math.cos(A_BEAM)
        bx, by, bz = lep[:, 0], c_ * lep[:, 1] - s_ * lep[:, 2], s_ * lep[:, 1] + c_ * lep[:, 2]
        c2["mu_true_maxabs_MeV"] = max(c2["mu_true_maxabs_MeV"], float(np.max(np.abs(bx - b["mu_true_px"]))),
                                       float(np.max(np.abs(by - b["mu_true_py"]))),
                                       float(np.max(np.abs(bz - b["mu_true_pz"]))))
        c2["mu_true_E_maxabs_MeV"] = max(c2["mu_true_E_maxabs_MeV"], float(np.max(np.abs(lep[:, 3] - b["mu_true_E"]))))
        ea = eavail_mat(rec["fs_pdg"], rec["fs_E"], off_o) / 1000.0
        c3["eavail_bitwise_rows"] += int(np.sum(ea == b["MC_eavail"]))
        c3["eavail_maxabs_GeV"] = max(c3["eavail_maxabs_GeV"], float(np.max(np.abs(ea - b["MC_eavail"]))))
        rowid = np.repeat(np.arange(gk.size), cnt)
        mu = (rec["fs_pdg"] == 13) & (rec["fs_E"] == lep[rowid, 3])
        c3["rows_with_mu_in_fs_equal_primFSLepton_E"] += int(np.unique(rowid[mu]).size)
        c3["n_particles"] += int(off_o[-1])
        c3["max_particles_per_row"] = max(c3["max_particles_per_row"], int(cnt.max()))
        for zv, nv in zip(*np.unique(rec["mc_targetZ"], return_counts=True)):
            c3["targetZ_counts"][str(int(zv))] = c3["targetZ_counts"].get(str(int(zv)), 0) + int(nv)
        fn_out = out / f"s1_{p}.npz"
        np.savez(fn_out, **rec)
        res["playlists"][p].update({"n_mad_files": len(files), "n_mad_truth_entries": int(n_truth),
                                    "n_mad_key_hits": int(src_file.size), "n_mad_dup_keys": int(dup.size),
                                    "n_particles": int(off_o[-1]), "file": str(fn_out),
                                    "bytes": fn_out.stat().st_size, "wall_s": round(time.time() - tp, 1)})
        print(p, json.dumps(res["playlists"][p]), flush=True)
        del rec, b, src_file
        kf.unlink()
    pool.close()
    pool.join()
    c3["n_rows_targetZ_1"] = c3["targetZ_counts"].get("1", 0)
    c2["pass"] = bool(c2["n_matched"] == c2["n_rows"] == c1["n_mcgen_rows"] and c2["n_mad_dup_fields_differ"] == 0
                      and c2["g2_identity_unique"] and c2["nFSPart_equals_len"] and c2["mu_true_maxabs_MeV"] <= 1e-6
                      and c2["mu_true_E_maxabs_MeV"] <= 1e-6)
    c3["pass"] = bool(c3["eavail_maxabs_GeV"] <= 1e-9)
    res["controls"]["C2_join"] = c2
    res["controls"]["C3_fs_content"] = c3
    print("C2", json.dumps(c2), flush=True)
    print("C3", json.dumps(c3), flush=True)
    for p in order:
        f = out / f"s1_{p}.npz"
        if f.exists():
            res["playlists"][p]["sha256"] = sha256(f)
    ok = all(res["controls"][k]["pass"] for k in ("C0_digests", "C1_admission", "C2_join", "C3_fs_content"))
    return finish(res, out, t0, 0 if ok else 3)


def finish(res, out, t0, rc):
    ru = resource.getrusage(resource.RUSAGE_SELF)
    res["cpu_s_parent"], res["maxrss_kb_parent"], res["wall_s"], res["exit"] = ru.ru_utime + ru.ru_stime, ru.ru_maxrss, \
        round(time.time() - t0, 1), rc
    (out / "s1_receipt.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print("S1_CONTROLS", {k: v.get("pass") for k, v in res["controls"].items()}, "exit", rc, flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
