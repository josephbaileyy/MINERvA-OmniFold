#!/usr/bin/env python3
"""MP-2 S2 step 1 (omnifold_py310, uproot): the generator final states, every entry in file order, for S2's
harmonization (frozen feature contract feature_contract_draft.json 98141c2f..., addenda 8 and 9).

No physics is computed here: every entry of every declared GENIE gst and NuWro treeout file is written as read
(CC or not, in file order), with its final-state particle list ragged by offsets. GiBUU (text) and Tune v1 (the
S1 dump) are read directly by step 2 (mp2_s2_harmonize.py, root_6_28), which aligns these arrays bitwise with the
frozen chains' own readers before any harmonized quantity is formed.

Samples (the contract's file order: C12 main, C12 supplement, H main, H supplement):
  genie_cv_main, genie_cv_supp, genie_mec_main, genie_mec_supp  (gst; H events are inside, tgt == 2212)
  nuwro_c12_main (work_nuwro_p1..p8 in order), nuwro_c12_supp, nuwro_h_main (MP3-B H_main c01..c25, the RESULT
  attempt), nuwro_h_supp (H_supp c01..c05)
Energies and momenta are stored in the files' own units (GENIE GeV, NuWro MeV).
Usage: python3 mp2_s2_dump.py OUTDIR
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

NS = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
G = f"{NS}/3d-unfolding/genie"
S5P = "/pscratch/sd/j/josephrb/s5p-20260926"
P1 = "/pscratch/sd/j/josephrb/measurement-paper/phase1"
GST_SCALARS = ["cc", "mec", "tgt", "hitnuc", "Ev", "pxv", "pyv", "pzv", "El", "pxl", "pyl", "pzl", "nf"]
GST_FS = ["pdgf", "Ef", "pxf", "pyf", "pzf"]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def result_attempt(chunkdir):
    """MP3-B: the attempt a chunk's RESULT names ('ok <k> <seed>'); a chunk not 'ok' is excluded."""
    p = Path(chunkdir, "RESULT").read_text().split()
    return (int(p[1]), int(p[2])) if p and p[0] == "ok" else (None, None)


def samples():
    h_main, h_supp = [], []
    for name, n, out in (("H_main", 25, h_main), ("H_supp", 5, h_supp)):
        for c in range(1, n + 1):
            C = f"{P1}/mp3b/runA/gen/{name}/c{c:02d}"
            k, seed = result_attempt(C)
            if k is not None:
                out.append({"chunk": c, "attempt": k, "seed": seed, "root": f"{C}/a{k}/nuwro.root",
                            "flat": f"{C}/a{k}/flat5d.root"})
    return {
        "genie_cv_main": {"kind": "gst", "files": [f"{G}/genie_mefhc_cv_ALL.gst.root"]},
        "genie_cv_supp": {"kind": "gst", "files": [f"{S5P}/gen5d_fluxfix/supp/genie_cv/genie_supp_cv.gst.root"]},
        "genie_mec_main": {"kind": "gst", "files": [f"{G}/genie_mefhc_mec_ALL.gst.root"]},
        "genie_mec_supp": {"kind": "gst", "files": [f"{S5P}/gen5d_fluxfix/supp/genie_mec/genie_supp_mec.gst.root"]},
        "nuwro_c12_main": {"kind": "nuwro", "files": [f"{G}/work_nuwro_p{i}/nuwro_p{i}.root" for i in range(1, 9)],
                           "flats": [f"{S5P}/gen5d/nuwro_flat5d/nuwro_flat5d_p{i}.root" for i in range(1, 9)]},
        "nuwro_c12_supp": {"kind": "nuwro", "files": [f"{S5P}/gen5d_fluxfix/supp/nuwro/nuwro_supp.root"],
                           "flats": [f"{S5P}/gen5d_fluxfix/supp/nuwro/nuwro_supp_flat5d.root"]},
        "nuwro_h_main": {"kind": "nuwro", "files": [c["root"] for c in h_main], "flats": [c["flat"] for c in h_main],
                         "chunks": h_main},
        "nuwro_h_supp": {"kind": "nuwro", "files": [c["root"] for c in h_supp], "flats": [c["flat"] for c in h_supp],
                         "chunks": h_supp},
    }


def ragged(ak, arrs, keys):
    off = np.zeros(len(arrs[keys[0]]) + 1, np.int64)
    np.cumsum(ak.to_numpy(ak.num(arrs[keys[0]])), out=off[1:])
    return off, {k: ak.to_numpy(ak.flatten(arrs[k])) for k in keys}


def dump_gst(path):
    import awkward as ak
    import uproot
    t = uproot.open(path)["gst"]
    a = t.arrays(GST_SCALARS + GST_FS, library="ak")
    out = {k: ak.to_numpy(a[k]) for k in GST_SCALARS}
    off, fs = ragged(ak, a, GST_FS)
    if not np.array_equal(np.diff(off), out["nf"]):
        raise SystemExit(f"{path}: ragged lengths differ from nf")
    out.update({f"fs_{k}": v for k, v in fs.items()}, fs_offsets=off)
    return out, int(t.num_entries)


NU_COLS = {"cc": "e/flag/flag.cc", "dyn": "e/dyn", "weight": "e/weight",
           "in_pdg": "e/in/in.pdg", "in_t": "e/in/in.t", "in_x": "e/in/in.x", "in_y": "e/in/in.y", "in_z": "e/in/in.z",
           "post_pdg": "e/post/post.pdg", "post_t": "e/post/post.t", "post_x": "e/post/post.x",
           "post_y": "e/post/post.y", "post_z": "e/post/post.z"}


def dump_nuwro(paths):
    import awkward as ak
    import uproot
    parts, n_entries = [], []
    for p in paths:
        t = uproot.open(p)["treeout"]
        a = t.arrays(list(NU_COLS.values()), library="ak")
        n_entries.append(int(t.num_entries))
        o = {"cc": ak.to_numpy(a[NU_COLS["cc"]]), "dyn": ak.to_numpy(a[NU_COLS["dyn"]]),
             "weight": ak.to_numpy(a[NU_COLS["weight"]])}
        off_in, fin = ragged(ak, a, [NU_COLS[k] for k in ("in_pdg", "in_t", "in_x", "in_y", "in_z")])
        off_po, fpo = ragged(ak, a, [NU_COLS[k] for k in ("post_pdg", "post_t", "post_x", "post_y", "post_z")])
        o.update({f"in_{k}": fin[NU_COLS[f'in_{k}']] for k in ("pdg", "t", "x", "y", "z")}, in_offsets=off_in)
        o.update({f"fs_{k}": fpo[NU_COLS[f'post_{k}']] for k in ("pdg", "t", "x", "y", "z")}, fs_offsets=off_po)
        parts.append(o)
    out = {}
    for k in ("cc", "dyn", "weight"):
        out[k] = np.concatenate([o[k] for o in parts])
    for pre in ("in", "fs"):
        offs, base = [], 0
        for o in parts:
            offs.append(o[f"{pre}_offsets"][:-1] + base)
            base += int(o[f"{pre}_offsets"][-1])
        out[f"{pre}_offsets"] = np.concatenate(offs + [np.array([base], np.int64)])
        for k in ("pdg", "t", "x", "y", "z"):
            out[f"{pre}_{k}"] = np.concatenate([o[f"{pre}_{k}"] for o in parts])
    out["file_entries"] = np.asarray(n_entries, np.int64)
    return out, int(sum(n_entries))


def main():
    outd = Path(sys.argv[1])
    outd.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    S = samples()
    rec = {"schema": "mp2-s2-dump/1", "argv": sys.argv, "slurm_job": os.environ.get("SLURM_JOB_ID"),
           "code_sha256": sha256(Path(__file__).resolve()), "samples": {}}
    import awkward
    import uproot
    rec["versions"] = {"numpy": np.__version__, "uproot": uproot.__version__, "awkward": awkward.__version__}
    for name, s in S.items():
        t1 = time.time()
        target = outd / f"{name}.npz"
        if target.exists():
            raise SystemExit(f"refusing to overwrite {target}")
        if s["kind"] == "gst":
            d, n = dump_gst(s["files"][0])
        else:
            d, n = dump_nuwro(s["files"])
        np.savez(target, **d)
        rec["samples"][name] = {"files": [{"path": p, "sha256": sha256(p)} for p in s["files"]],
                                "flats": [{"path": p, "sha256": sha256(p)} for p in s.get("flats", [])],
                                "chunks": s.get("chunks"), "n_entries": n,
                                "n_particles": int(d["fs_offsets"][-1]), "out": str(target),
                                "out_sha256": sha256(target), "wall_s": round(time.time() - t1, 1)}
        print(name, json.dumps({k: rec["samples"][name][k] for k in ("n_entries", "n_particles", "wall_s")}), flush=True)
    rec["wall_s"], rec["exit"] = round(time.time() - t0, 1), 0
    (outd / "s2_dump.json").write_text(json.dumps(rec, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
