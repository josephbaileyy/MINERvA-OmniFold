#!/usr/bin/env python3
"""MP3-C build: controls, gates B1-B3 and the GiBUU free-proton (H) and GiBUU-on-CH fine 5D products
(PLAN.md §4.2 rank 3; the director's grant after MP3-B; the frozen MP3-B pipeline applied to GiBUU).

The frozen GiBUU product is gen5d_fluxfix/gibuu_cv_xsec5d_fluxfix.npz, built by gen5d_flux_supplement.cmd_gibuu:
gibuu_events (= gen_to_xsec5d.extract_gibuu statement for statement, plus E_nu) over the 80 FinalEvents.dat files,
r(E) = (phi_t/Phi_t)/phi_gibuu with phi_gibuu GiBUU's own flux zeroed outside the jobcard's Enu cut [0, 20] GeV
and normalised, x = sum_bin perweight r / M x 1e-38 (M = number of runs; perweight already per target nucleon and
per numEnsembles, so for the A = 1 target the H product is per H nucleon). This module applies the SAME statements
to the H task files (files are parsed per file in parallel processes; every operation is per event, so the
concatenation in file order is the frozen arrays bit for bit, which B2 verifies on the C12 files).

  C0  every H task.job differs from the production task card in exactly the four declared values (mp3c_card.check)
  C1' (converter analogue) extract_gibuu on the 80 frozen C12 files reproduces the frozen PRE-fix product
      gen5d/gibuu_cv_xsec5d.npz bitwise with r = 1 (the frozen build's identity closure)
  B1  every H event: no QE (production_ID 1) and no 2p2h (35, 36), and the target is one real proton (the one
      perweight-0 row of every event: pid 1, charge +1). The perturbative hadronic charge (+2 for free-proton CC)
      is a reported diagnostic: the probe found +1 in 6 of 19,148 events (final nucleon absent).
  B2  the frozen GiBUU fluxfix product rebuilt bitwise (xsec, sumw2, nevt); the frozen sampling statistics
      reproduced field by field
  B3' the closure the frozen GiBUU build recorded, on the H events: alignment of gibuu_events with extract_gibuu,
      no event in a zero-flux bin, and the two sampling tests (counts E >= 1.5 GeV across/within; edge-jump test)
      at the frozen pass rule p >= 1e-3. KNOWN_ISSUES 82: E_nu > 20 GeV is absent here as in the frozen C12 sample.
  BUILD x_CH = (12/13) x_C12 (frozen arrays) + (1/13) x_H; sumw2 likewise squared.

Usage (root_6_28): python3 mp3c_build.py --out OUT --h-glob 'GLOB' --frozen-jobcard JOB --seeds SEEDS --nproc N
Exit 0 written; 2 a control failed; 3 a gate failed.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import multiprocessing as mp
import os
import re
import resource
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

import gen5d_flux_reweight as gfr  # noqa: E402
import gen5d_flux_supplement as sup  # noqa: E402
import mp3c_card as card  # noqa: E402
import mp3c_probe as probe  # noqa: E402

G = gfr.DEFAULTS["genie_dir"]
C12_GLOB = os.path.join(G, "work_gibuu_arr/task*/FinalEvents.dat")
FROZEN = os.path.join(sup.OUT, "gibuu_cv_xsec5d_fluxfix.npz")
PREFIX = os.path.join(gfr.DEFAULTS["gen5d_dir"], "gibuu_cv_xsec5d.npz")
F_C, F_H = 12.0 / 13.0, 1.0 / 13.0
G5 = None


def sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def _one(arg):
    fn, with_b1 = arg
    a, _, n_ev, enu = sup.gibuu_events(G5, [fn])
    ev, _, _ = G5.extract_gibuu([fn])
    b1 = probe.summary(probe.per_event(fn)) if with_b1 else None
    return fn, a, n_ev, enu, {k: ev[k] for k in ("pt", "pz", "eavail", "q3", "W", "weight_raw")}, b1


def events(files, nproc, with_b1=False):
    """sup.gibuu_events and g5.extract_gibuu per file in parallel, concatenated in file order (and, for the H
    files, the B1 event summary of each file)."""
    with mp.get_context("fork").Pool(min(nproc, len(files))) as pool:
        parts = pool.map(_one, [(f, with_b1) for f in files])
    events.b1 = {p[0]: p[5] for p in parts}
    keys = ("pt", "pz", "eavail", "q3", "W", "w", "enu")
    a = {k: np.concatenate([p[1][k] for p in parts]) for k in keys}
    ref = {k: np.concatenate([p[4][k] for p in parts]) for k in ("pt", "pz", "eavail", "q3", "W", "weight_raw")}
    aligned = all(np.array_equal(a[k], ref[kk]) for k, kk in (("pt", "pt"), ("pz", "pz"), ("eavail", "eavail"),
                                                               ("q3", "q3"), ("W", "W"), ("w", "weight_raw")))
    return a, float(len(files)), int(sum(p[2] for p in parts)), np.concatenate([p[3] for p in parts]), aligned


def gibuu_density(jobcard):
    """cmd_gibuu's phi_gibuu: the flux file zeroed outside the jobcard's Enu cut and normalised."""
    fl = np.loadtxt(gfr.DEFAULTS["gibuu_flux"], comments="#")
    Eg, fg = fl[:, 0], fl[:, 1]
    step = float(np.median(np.diff(Eg)))
    if not np.allclose(np.diff(Eg), step):
        raise SystemExit("GiBUU flux points not equally spaced")
    cut_lo, cut_hi = 0.0, 20.0
    for line in open(jobcard).read().splitlines():
        s = line.split("!")[0].strip()
        if s.startswith("Enu_upper_cut"):
            cut_hi = float(s.split("=")[1])
        if s.startswith("Enu_lower_cut"):
            cut_lo = float(s.split("=")[1])
    fcut = np.where((Eg >= cut_lo) & (Eg <= cut_hi), fg, 0.0)
    g_edges = np.concatenate([Eg - 0.5 * step, [Eg[-1] + 0.5 * step]])
    g_edges[0] = max(g_edges[0], 0.0)
    phi_g = fcut / (step * fcut.sum())
    return g_edges, fcut, phi_g, (cut_lo, cut_hi), step


def weights(a, g_edges, phi_g, edges, phi_t, Phi_t):
    ig = np.clip(np.searchsorted(g_edges, a["enu"], side="right") - 1, 0, phi_g.size - 1)
    it = np.clip(np.searchsorted(edges, a["enu"], side="right") - 1, 0, phi_t.size - 1)
    zero = bool(np.any(phi_g[ig] <= 0))
    return (phi_t[it] / Phi_t) / np.where(phi_g[ig] > 0, phi_g[ig], np.inf), zero


def build(g5, a, M, rr):
    AX, E5 = g5.AXES, g5.EDGES
    dV5 = g5.widths(*AX)
    cols = [a[k] for k in AX]
    e5 = [E5[k] for k in AX]
    wr = a["w"] * rr
    x = g5.hist(cols, wr, e5) / M / dV5 * 1.0e-38
    v = g5.hist(cols, wr * wr, e5) / M ** 2 / dV5 ** 2 * 1.0e-38 ** 2
    n = g5.hist(cols, None, e5)
    return x.reshape(-1), v.reshape(-1), n.reshape(-1)


def sampling(enu_every, g_edges, fcut, cut_hi):
    E_TEST_MIN = 1.5
    Et = enu_every[np.isfinite(enu_every)]
    s = [gfr.sampling_test(Et[Et >= E_TEST_MIN], g_edges, fcut * 1.0, E_TEST_MIN, cut_hi, sup.Unit(), False,
                           f"all written events with E_nu >= {E_TEST_MIN} GeV (counts)"),
         sup.edge_jump_test(Et, g_edges, fcut, E_TEST_MIN, cut_hi, 0.1)]
    for x in s:
        x.pop("flux_bin_E_lo", None)
        x["across_bins_content_proportional"].pop("pull_per_bin", None)
        x.pop("edges", None)
    return s, float(Et.max()) if Et.size else None


def brief(s):
    a, w = s["across_bins_content_proportional"], s["within_bin_uniform_x_sigma"]
    return {"population": s["population"], "n_events": s["n_events"], "across_chi2": a["chi2"], "across_ndf": a["ndf"],
            "across_p": a["p"], "within_chi2": w.get("chi2"), "within_ndf": w.get("ndf"), "within_p": w.get("p"),
            "pass": s["pass"]}


def main(argv=None) -> int:
    global G5
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--h-glob", required=True)
    ap.add_argument("--frozen-jobcard", required=True)
    ap.add_argument("--seeds", type=Path, required=True)
    ap.add_argument("--nproc", type=int, default=32)
    a = ap.parse_args(argv)
    t0 = time.time()
    a.out.mkdir(parents=True, exist_ok=False)
    ROOT = gfr.import_root()
    g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
    G5 = g5
    for m in (gfr, sup, card, probe):
        if Path(m.__file__).resolve().parent != HERE:
            raise SystemExit(f"{m.__name__} imported from {m.__file__}")
    res = {"schema": "mp3c-build/1", "argv": sys.argv, "environment": gfr.environment(), "stages": {},
           "code": {m.__name__: {"file": str(Path(m.__file__).resolve()), "sha256": sha256(Path(m.__file__).resolve())}
                    for m in (sys.modules[__name__], gfr, sup, card, probe, g5, g5.gib3d, g5.gibew)},
           "seeds_file": {"path": str(a.seeds), "sha256": sha256(a.seeds)}}

    def finish(code, msg):
        ru = resource.getrusage(resource.RUSAGE_SELF)
        res.update(verdict=msg, exit_code=code, wall_s=time.time() - t0, maxrss_kb=ru.ru_maxrss)
        (a.out / "mp3c_build.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
        print(msg, flush=True)
        return code

    h_files = sorted(glob.glob(a.h_glob))
    declared = {int(p[1]): int(p[2]) for p in (l.split() for l in a.seeds.read_text().splitlines())
                if p and p[0] == "TASK"}
    if not h_files:
        return finish(2, "STOP: no H FinalEvents.dat")
    # ---- C0: every H task card
    c0 = {}
    for f in h_files:
        tdir = Path(f).parent
        n = int(re.search(r"task(\d+)$", str(tdir)).group(1))
        if n not in declared:
            return finish(2, f"STOP: task {n} not declared in {a.seeds}")
        c0[str(n)] = card.check(a.frozen_jobcard, declared[n], str(tdir / "task.job"))
    c0_pass = all(v["pass"] for v in c0.values())
    res["stages"]["C0_card"] = {"n_tasks": len(c0), "pass": c0_pass,
                                "difference_sets": sorted({json.dumps(v["differences_vs_production"], sort_keys=True)
                                                           for v in c0.values()}), "per_task": c0}
    print("C0", json.dumps({"n": len(c0), "pass": c0_pass}), flush=True)
    if not c0_pass:
        return finish(2, "STOP: C0 failed")

    # ---- C12 events (frozen files), C1' and B2
    c12_files = sorted(glob.glob(C12_GLOB))
    z, _, phit_path = gfr.load_phi_t(sup.OUT)
    edges, phi_t, Phi_t = z["edges"], z["phi_t_density"], float(z["Phi_t"])
    ac, Mc, nev_c, enu_c, al_c = events(c12_files, a.nproc)
    fmeta = json.loads(str(np.load(FROZEN, allow_pickle=True)["meta_json"]))
    in_ok = all(sha256(p) == r["sha256"] for p, r in zip(c12_files, [i for i in fmeta["inputs"] if i["role"] == "events"]))
    g_edges, fcut, phi_g, cut, step = gibuu_density(gfr.DEFAULTS["gibuu_jobcard"])
    rc, zero_c = weights(ac, g_edges, phi_g, edges, phi_t, Phi_t)
    x1, v1, n1 = build(g5, ac, Mc, np.ones(rc.size))
    old = np.load(PREFIX, allow_pickle=True)
    c1 = {"xsec": gfr.compare_arrays(x1, np.asarray(old["xsec_flat"])), "sumw2": gfr.compare_arrays(v1, np.asarray(old["sumw2_flat"])),
          "nevt": gfr.compare_arrays(n1, np.asarray(old["nevt_flat"])), "alignment_gibuu_events_vs_extract_gibuu": al_c,
          "n_files": len(c12_files), "inputs_match_frozen_meta": in_ok}
    c1["pass"] = bool(al_c and in_ok and c1["xsec"]["bitwise_equal"] and c1["sumw2"]["bitwise_equal"] and c1["nevt"]["bitwise_equal"])
    res["stages"]["C1_converter_identity"] = c1
    print("C1'", json.dumps({k: (v["bitwise_equal"] if isinstance(v, dict) else v) for k, v in c1.items()}), flush=True)
    if not c1["pass"]:
        return finish(2, "STOP: C1' (identity) failed")
    xc, vc, nc = build(g5, ac, Mc, rc)
    fz = np.load(FROZEN, allow_pickle=True)
    b2 = {"xsec": gfr.compare_arrays(xc, np.asarray(fz["xsec_flat"])), "sumw2": gfr.compare_arrays(vc, np.asarray(fz["sumw2_flat"])),
          "nevt": gfr.compare_arrays(nc, np.asarray(fz["nevt_flat"])), "frozen_sha256": sha256(FROZEN),
          "zero_flux_event": zero_c, "cut_GeV": list(cut)}
    samp_c, _ = sampling(enu_c, g_edges, fcut, cut[1])
    b2["sampling_reproduced"] = [{"mine": brief(m), "frozen": brief(f), "identical": brief(m) == brief(f)}
                                 for m, f in zip(samp_c, fmeta["checks"]["sampling_model"])]
    b2["pass"] = bool(b2["xsec"]["bitwise_equal"] and b2["sumw2"]["bitwise_equal"] and b2["nevt"]["bitwise_equal"])
    res["stages"]["B2"] = b2
    print("B2", json.dumps({"xsec": b2["xsec"]["bitwise_equal"], "sumw2": b2["sumw2"]["bitwise_equal"],
                            "sampling_reproduced": [x["identical"] for x in b2["sampling_reproduced"]], "pass": b2["pass"]}), flush=True)

    # ---- B1 on the H events (event level only); the H files are parsed here once for B1 and B3'
    ah, Mh, nev_h, enu_h, al_h = events(h_files, a.nproc, with_b1=True)
    b1 = {}
    for f in h_files:
        e = events.b1[f]
        bad = [k for k in e["channels"] if k.split()[0] in ("1", "35", "36")]
        target_ok = e["events_whose_real_rows_are_exactly_one_proton"] == e["n_events"]
        b1[Path(f).parent.name] = {"n_events": e["n_events"], "channels": e["channels"], "forbidden_channels": bad,
                                   "target_is_one_real_proton_in_every_event": target_ok,
                                   "perturbative_hadronic_charge_counts (diagnostic)": e["hadronic_charge_sum_counts"],
                                   "sigma_fraction_charge_not_2 (diagnostic)": e["sigma_fraction_charge_not_2"],
                                   "n_events_without_muon": e["n_events_without_muon"],
                                   "pass": (not bad) and target_ok}
    b1_pass = all(v["pass"] for v in b1.values())
    res["stages"]["B1"] = {"per_task": b1, "pass": b1_pass}
    print("B1", json.dumps({"n_tasks": len(b1), "pass": b1_pass}), flush=True)
    if not b1_pass:
        return finish(3, "STOP: gate B1 failed; no CH prediction")
    if not b2["pass"]:
        return finish(3, "STOP: gate B2 failed; no CH prediction")

    # ---- B3' on the H events
    gh = gibuu_density(str(Path(h_files[0]).parent / "task.job"))
    same_density = bool(np.array_equal(gh[2], phi_g) and gh[3] == cut)
    rh, zero_h = weights(ah, g_edges, phi_g, edges, phi_t, Phi_t)
    samp_h, emax_h = sampling(enu_h, g_edges, fcut, cut[1])
    b3 = {"alignment_gibuu_events_vs_extract_gibuu": al_h, "zero_flux_event": zero_h,
          "H_card_flux_density_equals_frozen": same_density, "max_Enu_GeV": emax_h, "cut_GeV": list(cut),
          "sampling_model": [brief(s) for s in samp_h],
          "frozen_C12_sampling_model": [brief(s) for s in fmeta["checks"]["sampling_model"]],
          "r_quantiles_1_50_99": np.percentile(rh, [1, 50, 99]).tolist(),
          "pass_rule": "alignment, no zero-flux event, the H card's flux density = the frozen one, and both sampling "
                       "tests p >= 1e-3 (the frozen GiBUU build's own closure)"}
    b3["pass"] = bool(al_h and not zero_h and same_density and all(s["pass"] for s in samp_h))
    res["stages"]["B3"] = b3
    print("B3", json.dumps({"alignment": al_h, "zero": zero_h, "density": same_density,
                            "sampling": [(s["population"][:40], s["across_bins_content_proportional"]["p"],
                                          s["within_bin_uniform_x_sigma"].get("p"), s["pass"]) for s in samp_h],
                            "pass": b3["pass"]}, default=float), flush=True)
    if not b3["pass"]:
        return finish(3, "STOP: gate B3 failed; no CH prediction")

    # ---- products
    xh, vh, nh = build(g5, ah, Mh, rh)
    x_ch = F_C * np.asarray(fz["xsec_flat"]) + F_H * xh
    v_ch = F_C ** 2 * np.asarray(fz["sumw2_flat"]) + F_H ** 2 * vh
    n_ch = np.asarray(fz["nevt_flat"]) + nh
    np.savez_compressed(a.out / "mp3c_fine_gibuu.npz", xsec_C12_frozen=np.asarray(fz["xsec_flat"]),
                        sumw2_C12_frozen=np.asarray(fz["sumw2_flat"]), nevt_C12_frozen=np.asarray(fz["nevt_flat"]),
                        xsec_C12_rebuilt=xc, sumw2_C12_rebuilt=vc, xsec_H=xh, sumw2_H=vh, nevt_H=nh,
                        xsec_CH=x_ch, sumw2_CH=v_ch, nevt_CH=n_ch)
    vol = g5.widths(*g5.AXES).reshape(-1)
    meta = {"generator": "gibuu_H / gibuu_CH", "label": "GiBUU 2019 on a free proton; CH = (12/13) C12 + (1/13) H",
            "H_files": [{"path": f, "sha256": sha256(f)} for f in h_files], "M_H": Mh, "cut_GeV": list(cut),
            "axes": list(g5.AXES), "shape": list(g5.SHAPE), "code": res["code"]}
    for name, x, v, n in (("gibuu_H_xsec5d_fluxfix", xh, vh, nh), ("gibuu_CH_xsec5d_fluxfix", x_ch, v_ch, n_ch)):
        np.savez(a.out / f"{name}.npz", xsec_flat=x, sumw2_flat=v, nevt_flat=n, n_events=np.int64(n.sum()),
                 **{f"edges_{k}": g5.EDGES[k] for k in g5.AXES}, shape=np.asarray(g5.SHAPE), meta_json=np.asarray(json.dumps(meta)))
    res["integrated_after_gates"] = {
        "sigma_in_grid_H_per_nucleon_cm2": float(xh @ vol), "sigma_in_grid_C12_per_nucleon_cm2": float(np.asarray(fz["xsec_flat"]) @ vol),
        "H_over_C12_per_nucleon_in_grid": float((xh @ vol) / (np.asarray(fz["xsec_flat"]) @ vol)),
        "f_H_in_grid": float(F_H * (xh @ vol) / (x_ch @ vol)), "M_H": Mh, "M_C12": Mc,
        "n_events_H": nev_h, "n_in_grid_H": int(nh.sum()), "n_in_grid_C12": int(np.asarray(fz["nevt_flat"]).sum()),
        "effective_N_in_grid_H": float((ah["w"] * rh).sum() ** 2 / ((ah["w"] * rh) ** 2).sum()),
        "effective_N_in_grid_C12": fmeta["checks"]["effective_N_in_grid"]}
    res["products"] = {p: sha256(a.out / p) for p in ("mp3c_fine_gibuu.npz", "gibuu_H_xsec5d_fluxfix.npz", "gibuu_CH_xsec5d_fluxfix.npz")}
    return finish(0, "GATES_B1_B3_PASS; GiBUU H and CH fine products written")


if __name__ == "__main__":
    raise SystemExit(main())
