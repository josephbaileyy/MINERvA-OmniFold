#!/usr/bin/env python3
"""MP-2 S2 preflight (binding addendum 8, ruling (g)): REPORT ONLY. No gate, no fit, no weight.

Tabulates, on <= ~100k events per sample, the harmonization items the frozen feature contract
(feature_contract_draft.json sha256 98141c2f...) declares: PDG codes present (pseudo-particles, codes outside a
standard table, nuclei/remnants pdg >= 1e9), photons below 10 MeV, the effect of each declared threshold, GiBUU's
ID -> PDG map (every (ID, charge) seen), the struck-nucleon source, and the nu direction (+z).

Samples: GENIE CV and MEC gst (main + supplement), NuWro C12 (p1, supplement) and H (MP3-B chunks, the RESULT
attempt), GiBUU C12 (work_gibuu_arr) and H (MP3-C prod), Tune v1 (S1 dump). CC events only (generator cc flag;
GiBUU: every event is CC by its jobcard process_ID = 2; Tune v1: every S1 row is nu_mu CC). Energies MeV.

Usage (omnifold_py310, login node): python3 mp2_s2_preflight.py OUT.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

NS = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
G = f"{NS}/3d-unfolding/genie"
S5P = "/pscratch/sd/j/josephrb/s5p-20260926"
P1 = "/pscratch/sd/j/josephrb/measurement-paper/phase1"
NMAX = 100000
NSUPP = 20000

# a standard table (PDG MC numbering) of the particles a nu_mu CC final state can carry
STD = {11, 12, 13, 14, 15, 16, 22, 111, 211, 113, 213, 130, 310, 311, 321, 221, 223, 331, 333, 411, 421, 431, 443,
       2112, 2212, 1114, 2114, 2214, 2224, 3122, 3112, 3212, 3222, 3312, 3322, 3334, 4122, 4112, 4212, 4222, 4132,
       4232, 313, 323}
# the contract's species (feature_contract_draft.json "particles")
EXCL = {11, 12, 13, 14, 16}
THR = {"p": (2212, "KE", 100.0), "n": (2112, "KE", 50.0), "pipm": (211, "KE", 50.0), "gamma": (22, "E", 10.0)}
# the contract's GiBUU map, literally: 1 -> p/n, 101 -> pi, 102 -> eta, 110/111 -> K, 32 -> Lambda, 33 -> Sigma,
# negative -> antiparticle, anything else -> 'other'
GIBUU_MAP = {1: {1: 2212, 0: 2112}, 101: {1: 211, 0: 111, -1: -211}, 102: {0: 221},
             110: {1: 321, 0: 311}, 111: {-1: -321, 0: -311}, 32: {0: 3122}, 33: {1: 3222, 0: 3212, -1: 3112}}


def classify(pdg):
    a = np.abs(pdg)
    return {"nuclei_ge_1e9": int(np.sum((a >= 1_000_000_000) & (a < 2_000_000_000))),
            "pseudo_ge_2e9": int(np.sum(a >= 2_000_000_000)),
            "outside_std_table_lt_1e9": int(np.sum(~np.isin(a, list(STD)) & (a < 1_000_000_000)))}


def tabulate(name, pdg, E, px, py, pz, off, extra):
    """Per-sample tables from ragged particles (MeV)."""
    n_ev = off.size - 1
    row = np.repeat(np.arange(n_ev), np.diff(off))
    p2 = px * px + py * py + pz * pz
    KE = E - np.sqrt(np.maximum(E * E - p2, 0.0))
    codes = Counter(pdg.tolist())
    out = {"sample": name, "n_events": int(n_ev), "n_particles": int(pdg.size),
           "pdg_counts": {str(k): v for k, v in sorted(codes.items(), key=lambda kv: -kv[1])},
           "class_counts": classify(pdg),
           "codes_outside_std_table": sorted(int(c) for c in codes if abs(c) not in STD)}
    g = pdg == 22
    eg = E[g]
    out["photons"] = {"n": int(g.sum()), "n_below_10MeV": int(np.sum(eg < 10.0)),
                      "below_10MeV_bins_MeV_[0,1,2,5,10]": np.histogram(eg[eg < 10.0], [0, 1, 2, 5, 10])[0].tolist(),
                      "events_with_any_photon_below_10MeV": int(np.unique(row[g & (E < 10.0)]).size),
                      "events_with_any_photon": int(np.unique(row[g]).size),
                      "E_quantiles_MeV_0.1_0.5_0.9": [float(x) for x in np.quantile(eg, [0.1, 0.5, 0.9])] if eg.size else []}
    thr = {}
    for sp, (code, var, cut) in THR.items():
        m = (np.abs(pdg) == code) if sp == "pipm" else (pdg == code)
        v = (KE if var == "KE" else E)[m]
        thr[sp] = {"cut": f"{var} > {cut} MeV", "above": int(np.sum(v > cut)), "below_or_equal": int(np.sum(v <= cut)),
                   "events_with_one_above": int(np.unique(row[m][v > cut]).size)}
    thr["pi0"] = {"cut": "none", "n": int(np.sum(pdg == 111))}
    known = np.isin(np.abs(pdg), [2212, 2112, 211, 111, 22]) | np.isin(np.abs(pdg), list(EXCL))
    oth = ~known & (np.abs(pdg) < 1_000_000_000)
    thr["other"] = {"cut": "none", "n": int(oth.sum()),
                    "codes": {str(k): v for k, v in Counter(pdg[oth].tolist()).most_common(25)}}
    out["thresholds"] = thr
    out["muons_per_event"] = np.bincount(np.bincount(row[np.abs(pdg) == 13], minlength=n_ev), minlength=3).tolist()[:4]
    out.update(extra)
    print(name, json.dumps({k: out[k] for k in ("n_events", "class_counts", "codes_outside_std_table")}), flush=True)
    return out


def genie(path, n):
    import uproot
    t = uproot.open(path)["gst"]
    a = t.arrays(["cc", "hitnuc", "tgt", "pxv", "pyv", "pzv", "Ev", "pdgf", "Ef", "pxf", "pyf", "pzf"],
                 entry_stop=n, library="ak")
    import awkward as ak
    cc = ak.to_numpy(a["cc"]).astype(bool)
    a = a[cc]
    off = np.zeros(len(a) + 1, np.int64)
    np.cumsum(ak.to_numpy(ak.num(a["pdgf"])), out=off[1:])
    f = [ak.to_numpy(ak.flatten(a[k])) for k in ("pdgf", "Ef", "pxf", "pyf", "pzf")]
    pxv, pyv = ak.to_numpy(a["pxv"]), ak.to_numpy(a["pyv"])
    hit = ak.to_numpy(a["hitnuc"])
    tgt = ak.to_numpy(a["tgt"])
    extra = {"file": path, "entries_read": int(min(n, t.num_entries)), "n_cc": int(cc.sum()),
             "nu_along_z": {"n_pxv_or_pyv_nonzero": int(np.sum((pxv != 0) | (pyv != 0)))},
             "struck_nucleon_source": "gst hitnuc",
             "struck_nucleon_counts": {str(k): int(v) for k, v in zip(*np.unique(hit, return_counts=True))},
             "struck_nucleon_by_target": {str(tv): {str(k): int(v) for k, v in zip(*np.unique(hit[tgt == tv], return_counts=True))}
                                          for tv in np.unique(tgt)}}
    return tabulate(Path(path).name, f[0], 1000 * f[1], 1000 * f[2], 1000 * f[3], 1000 * f[4], off, extra)


def nuwro(paths, n, name):
    import awkward as ak
    import uproot
    cols = ["e/flag/flag.cc", "e/post/post.pdg", "e/post/post.t", "e/post/post.x", "e/post/post.y", "e/post/post.z",
            "e/in/in.x", "e/in/in.y", "e/in/in.pdg"]
    parts, read = [], 0
    for p in paths:
        if read >= n:
            break
        t = uproot.open(p)["treeout"]
        a = t.arrays(cols, entry_stop=n - read, library="ak")
        read += len(a)
        parts.append(a)
    a = ak.concatenate(parts)
    cc = ak.to_numpy(a["e/flag/flag.cc"]).astype(bool)
    a = a[cc]
    pdg = a["e/post/post.pdg"]
    off = np.zeros(len(a) + 1, np.int64)
    np.cumsum(ak.to_numpy(ak.num(pdg)), out=off[1:])
    f = [ak.to_numpy(ak.flatten(a[k])) for k in ("e/post/post.pdg", "e/post/post.t", "e/post/post.x", "e/post/post.y",
                                                  "e/post/post.z")]
    nux, nuy = ak.to_numpy(a["e/in/in.x"][:, 0]), ak.to_numpy(a["e/in/in.y"][:, 0])
    nin = ak.to_numpy(ak.num(a["e/in/in.pdg"]))
    hit = np.where(nin > 1, ak.to_numpy(ak.fill_none(ak.pad_none(a["e/in/in.pdg"], 2)[:, 1], 0)), 0)
    extra = {"files": paths[:len(parts)], "entries_read": int(read), "n_cc": int(cc.sum()),
             "nu_along_z": {"n_in0_x_or_y_nonzero": int(np.sum((nux != 0) | (nuy != 0)))},
             "struck_nucleon_source": "in[1].pdg (flat-tree hitnuc)",
             "struck_nucleon_counts": {str(k): int(v) for k, v in zip(*np.unique(hit, return_counts=True))},
             "n_in_particles_counts": {str(k): int(v) for k, v in zip(*np.unique(nin, return_counts=True))}}
    return tabulate(name, *f, off, extra)


def gibuu(paths, n, name):
    rows, ev_seen = [], 0
    used = []
    for p in paths:
        if ev_seen >= n:
            break
        d = np.loadtxt(p, comments="#")
        key = d[:, 0].astype(np.int64) * 10_000_000 + d[:, 1].astype(np.int64)
        u = np.unique(key)
        ev_seen += u.size
        rows.append(d)
        used.append(p)
    d = np.concatenate(rows)
    run, evt = d[:, 0].astype(np.int64), d[:, 1].astype(np.int64)
    # the file index keeps events of different files apart
    fidx = np.concatenate([np.full(r.shape[0], i) for i, r in enumerate(rows)])
    key = fidx * 10**12 + run * 10_000_000 + evt
    order = np.argsort(key, kind="stable")
    d, key = d[order], key[order]
    ID, Q, pw = d[:, 2].astype(int), d[:, 3].astype(int), d[:, 4]
    E, px, py, pz = 1000 * d[:, 8], 1000 * d[:, 9], 1000 * d[:, 10], 1000 * d[:, 11]
    prod = d[:, 13].astype(int)
    starts = np.r_[0, np.nonzero(np.diff(key))[0] + 1]
    ev_of = np.repeat(np.arange(starts.size), np.diff(np.r_[starts, key.size]))
    init = pw == 0.0
    idq = Counter(zip(ID.tolist(), Q.tolist()))
    idmap = {}
    for (i, q), c in sorted(idq.items(), key=lambda kv: -kv[1]):
        m = GIBUU_MAP.get(abs(i), {}).get(q if i > 0 else -q)
        if m is not None and i < 0:
            m = -m
        idmap[f"{i},{q}"] = {"count": c, "count_final": int(np.sum((ID == i) & (Q == q) & ~init)),
                             "contract_map": m if m is not None else "other (unmapped)"}
    # final particles mapped literally by the contract, unmapped IDs become 'other' (code 0 here)
    fin = ~init
    pdg = np.array([(GIBUU_MAP.get(abs(i), {}).get(q if i > 0 else -q) or 0) * (1 if i > 0 else -1)
                    for i, q in zip(ID[fin].tolist(), Q[fin].tolist())], dtype=np.int64)
    fe = ev_of[fin]
    off = np.zeros(starts.size + 1, np.int64)
    np.cumsum(np.bincount(fe, minlength=starts.size), out=off[1:])
    n_init = np.bincount(ev_of[init & (ID == 1)], minlength=starts.size)
    q_init = np.full(starts.size, -9)
    one = n_init == 1
    for e_, q_ in zip(ev_of[init & (ID == 1)].tolist(), Q[init & (ID == 1)].tolist()):
        if one[e_]:
            q_init[e_] = q_
    prod_ev = prod[starts]
    two = np.isin(prod_ev, [35, 36])
    sumpt = np.hypot(np.bincount(fe, px[fin], starts.size) - np.bincount(ev_of[init], px[init], starts.size),
                     np.bincount(fe, py[fin], starts.size) - np.bincount(ev_of[init], py[init], starts.size))
    extra = {"files": used, "n_events": int(starts.size),
             "gibuu_id_charge_map": idmap,
             "unmapped_final_ids": sorted({k for k, v in idmap.items() if v["contract_map"] == "other (unmapped)" and v["count_final"] > 0}),
             "production_ID_counts": {str(k): int(v) for k, v in zip(*np.unique(prod_ev, return_counts=True))},
             "struck_nucleon_source": "the single perweight-0 nucleon row (ID 1) by its charge; else the analysis default mass (ruling (g))",
             "initial_nucleon_rows_per_event": {str(k): int(v) for k, v in zip(*np.unique(n_init, return_counts=True))},
             "initial_nucleon_rows_per_event_2p2h": {str(k): int(v) for k, v in zip(*np.unique(n_init[two], return_counts=True))},
             "struck_charge_when_single": {str(k): int(v) for k, v in zip(*np.unique(q_init[one], return_counts=True))},
             "events_taking_default_mass": int((~one).sum()), "events_taking_default_mass_2p2h": int((~one & two).sum()),
             "nu_along_z_proxy": {"what": "|sum pT(final) - sum pT(perweight-0 rows)| per event, MeV (0 if nu along z and no unlisted remnant)",
                                  "quantiles_0.5_0.9_0.99_max": [float(x) for x in np.quantile(sumpt, [0.5, 0.9, 0.99, 1.0])]}}
    out = tabulate(name, pdg, E[fin], px[fin], py[fin], pz[fin], off, extra)
    out["note"] = "pdg 0 = a final GiBUU (ID, charge) the contract's map does not cover (goes to 'other' literally)"
    return out


def tune(n):
    s1 = f"{P1}/mp2/s1"
    rng = np.random.default_rng(2026102150)
    s = np.load(f"{s1}/s1_1A.npz")
    nr = int(s["n_rows"])
    rows = np.sort(rng.choice(nr, size=min(n, nr), replace=False))
    off0 = np.asarray(s["fs_offsets"])
    st, cnt = off0[rows], np.diff(off0)[rows]
    off = np.zeros(rows.size + 1, np.int64)
    np.cumsum(cnt, out=off[1:])
    gi = np.repeat(st - off[:-1], cnt) + np.arange(off[-1])
    f = [np.asarray(s[k])[gi] for k in ("fs_pdg", "fs_E", "fs_px", "fs_py", "fs_pz")]
    tn, tz = np.asarray(s["mc_targetNucleon"])[rows], np.asarray(s["mc_targetZ"])[rows]
    extra = {"file": f"{s1}/s1_1A.npz", "rows": "100k uniform (seed 2026102150) of playlist 1A",
             "struck_nucleon_source": "mc_targetNucleon",
             "struck_nucleon_counts": {str(k): int(v) for k, v in zip(*np.unique(tn, return_counts=True))},
             "struck_nucleon_counts_targetZ_1": {str(k): int(v) for k, v in zip(*np.unique(tn[tz == 1], return_counts=True))},
             "nu_along_z": "not applicable (the analysis MC carries its own nu direction; the generators are rotated onto it)"}
    return tabulate("tune_v1_S1_1A", *f, off, extra)


def first_ok(chunkdir):
    k = Path(chunkdir, "RESULT").read_text().split()[1]
    return f"{chunkdir}/a{k}/nuwro.root"


def main():
    res = {"schema": "mp2-s2-preflight/1", "contract_sha256": "98141c2f22f4fc3f2a7f5b30a0c509d6a29a37d145a72ea802623a2a2d6630cd",
           "rule": "report only; CC events; <= 100k events per main sample, <= 20k per supplement", "samples": []}
    S = res["samples"]
    S.append(genie(f"{G}/genie_mefhc_cv_ALL.gst.root", NMAX))
    S.append(genie(f"{S5P}/gen5d_fluxfix/supp/genie_cv/genie_supp_cv.gst.root", NSUPP))
    S.append(genie(f"{G}/genie_mefhc_mec_ALL.gst.root", NMAX))
    S.append(genie(f"{S5P}/gen5d_fluxfix/supp/genie_mec/genie_supp_mec.gst.root", NSUPP))
    S.append(nuwro([f"{G}/work_nuwro_p1/nuwro_p1.root"], NMAX, "nuwro_C12_p1"))
    S.append(nuwro([f"{S5P}/gen5d_fluxfix/supp/nuwro/nuwro_supp.root"], NSUPP, "nuwro_C12_supp"))
    hm = [first_ok(f"{P1}/mp3b/runA/gen/H_main/c{c:02d}") for c in range(1, 26)]
    S.append(nuwro(hm, NMAX, "nuwro_H_main"))
    hs = [first_ok(f"{P1}/mp3b/runA/gen/H_supp/c{c:02d}") for c in range(1, 6)]
    S.append(nuwro(hs, NSUPP, "nuwro_H_supp"))
    S.append(gibuu([f"{G}/work_gibuu_arr/task{i}/FinalEvents.dat" for i in range(1, 81)], NMAX, "gibuu_C12"))
    S.append(gibuu([f"{P1}/mp3c/prod/task{i}/FinalEvents.dat" for i in range(1001, 1081)], NMAX, "gibuu_H"))
    S.append(tune(NMAX))
    Path(sys.argv[1]).write_text(json.dumps(res, indent=1, default=str) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
