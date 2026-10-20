#!/usr/bin/env python3
"""MP3-C probe readout (numpy only): one GiBUU free-proton task against one frozen C12 task.

Per event (rows grouped by (run, event) as gen_to_xsec5d.extract_gibuu groups them; the lepton row carries the
event's perweight, production_ID and E_nu): channel content by production_ID, the hadronic charge sum (free-proton
CC requires +2), sigma per nucleon = sum perweight / M x 1e-38 (M = 1 file), and counts. Usage:
  python3 mp3c_probe.py H_FinalEvents.dat C12_FinalEvents.dat TIME_FILE OUT.json
"""
import json
import sys

import numpy as np

MUON = (901, 902, 903)   # gibuu_to_xsec_eavailW.MUON_IDS
NAMES = {1: "QE", 2: "Delta", 32: "1pi bkg (32)", 33: "1pi bkg (33)", 34: "DIS", 35: "2p2h QE", 36: "2p2h Delta",
         37: "2pi bkg"}


def per_event(path):
    d = np.loadtxt(path, comments="#")
    run, ev = d[:, 0].astype(np.int64), d[:, 1].astype(np.int64)
    pid, ch, pw = d[:, 2].astype(int), d[:, 3].astype(int), d[:, 4]
    prod, enu = d[:, 13].astype(int), d[:, 14]
    key = run * 10_000_000 + ev
    uk, inv = np.unique(key, return_inverse=True)
    lep = np.isin(pid, MUON)
    n = uk.size
    w = np.zeros(n); pr = np.full(n, -1); en = np.full(n, np.nan); nlep = np.zeros(n, int)
    w[inv[lep]] = pw[lep]; pr[inv[lep]] = prod[lep]; en[inv[lep]] = enu[lep]
    np.add.at(nlep, inv[lep], 1)
    pert, real = (pw != 0) & (~lep), (pw == 0) & (~lep)       # pw = 0 rows: real (unstruck) target particles,
    qhad = np.zeros(n, int)                                     # which the frozen converter excludes from E_avail
    np.add.at(qhad, inv[pert], ch[pert])
    nreal = np.zeros(n, int); np.add.at(nreal, inv[real], 1)
    realp = np.zeros(n, int); np.add.at(realp, inv[real & (pid == 1) & (ch == 1)], 1)
    return {"n_rows": int(d.shape[0]), "n_events": int(n), "w": w, "prod": pr, "enu": en, "nlep": nlep, "qhad": qhad,
            "nreal": nreal, "realp": realp,
            "pids": {str(k): int(v) for k, v in zip(*np.unique(pid, return_counts=True))}}


def summary(e):
    ok = e["w"] > 0
    tot = float(e["w"][ok].sum())
    chans = {}
    for p in np.unique(e["prod"][ok]):
        m = ok & (e["prod"] == p)
        chans[f"{int(p)} {NAMES.get(int(p), 'resonance' if 3 <= p <= 31 else '?')}"] = {
            "n_events": int(m.sum()), "sigma_fraction": float(e["w"][m].sum() / tot)}
    return {"n_rows": e["n_rows"], "n_events": e["n_events"], "n_events_w_gt_0": int(ok.sum()),
            "n_events_without_muon": int(np.sum(e["nlep"] == 0)), "pid_row_counts": e["pids"],
            "sigma_per_nucleon_cm2_cut_flux": tot * 1e-38, "channels": chans,
            "hadronic_charge_sum_counts": {str(int(k)): int(v) for k, v in zip(*np.unique(e["qhad"][ok], return_counts=True))},
            "hadronic_charge_note": "sum over perturbative (perweight != 0) non-lepton rows; free-proton CC conserves +2",
            "real_rows_per_event_counts": {str(int(k)): int(v) for k, v in zip(*np.unique(e["nreal"], return_counts=True))},
            "events_whose_real_rows_are_exactly_one_proton": int(np.sum((e["nreal"] == 1) & (e["realp"] == 1))),
            "sigma_fraction_charge_not_2": float(e["w"][ok & (e["qhad"] != 2)].sum() / e["w"][ok].sum()),
            "mean_enu_GeV_sigma_weighted": float(np.sum(e["w"][ok] * e["enu"][ok]) / tot),
            "max_enu_GeV": float(np.nanmax(e["enu"])),
            "effective_N": float(tot ** 2 / np.sum(e["w"][ok] ** 2))}


def main():
    h, c = per_event(sys.argv[1]), per_event(sys.argv[2])
    sh, sc = summary(h), summary(c)
    t = {}
    for line in open(sys.argv[3], errors="replace"):
        for key in ("Elapsed (wall clock)", "Maximum resident set size", "User time", "Percent of CPU", "Exit status"):
            if key in line:
                t[key] = line.split(":", 1)[1].strip() if key != "Elapsed (wall clock)" else line.rsplit(" ", 1)[1].strip()
    no_qe = not any(k.split()[0] in ("1", "35", "36") for k in sh["channels"])
    charge_ok = sh["events_whose_real_rows_are_exactly_one_proton"] == sh["n_events"]
    ratio = sh["sigma_per_nucleon_cm2_cut_flux"] / sc["sigma_per_nucleon_cm2_cut_flux"]
    out = {"H": sh, "C12_reference_task": sc, "sigma_H_over_C12_per_nucleon_cut_flux": ratio, "time": t,
           "checks": {"completed": sh["n_events_w_gt_0"] > 0,
                      "no_QE_no_2p2h": no_qe,
                      "target_is_one_real_proton_in_every_event": charge_ok,
                      "sigma_ratio_in_0.55_0.75 (NuWro probe 0.642, GENIE 0.66)": bool(0.55 <= ratio <= 0.75)},
           "files": {"H": sys.argv[1], "C12": sys.argv[2]}}
    out["PROBE_VERDICT"] = "PASS" if all(out["checks"].values()) else "FAIL"
    open(sys.argv[4], "w").write(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("sigma_H_over_C12_per_nucleon_cut_flux", "time", "checks", "PROBE_VERDICT")}))
    print("H channels", json.dumps(sh["channels"]))
    print("C12 channels", json.dumps(sc["channels"]))
    print("H charge (perturbative)", sh["hadronic_charge_sum_counts"], "real rows", sh["real_rows_per_event_counts"], "events", sh["n_events"], "w>0", sh["n_events_w_gt_0"],
          "noMuon", sh["n_events_without_muon"], "Neff", round(sh["effective_N"]), "pids", sh["pid_row_counts"])
    print("C12 events", sc["n_events"], "Neff", round(sc["effective_N"]))


if __name__ == "__main__":
    main()
