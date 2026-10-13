#!/usr/bin/env python3
"""Analyse a pilot event dump (instrumented NuWro, ``save_test_events = 3``).

Every sampled event is one line: index, weight (cm^2 per nucleon; zero for a
rejected trial), dynamics code, then the ``in``, ``out`` and ``post`` (after
transport) particle lists as ``pdg E px py pz`` in MeV, beam along +z.

Outputs one JSON document: cross section with its Monte Carlo error, weight
dispersion, channel fractions, primary-vertex conservation, the partition of the
energy transfer after transport, truth-signal acceptance, the repository's
E_avail (docs/EAVAIL_DEFINITION.md, Eq. 1 of the memo) and, for a flux run, a
check of the sampled neutrino energies against the flux histogram.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

M_P, M_N, M_PI_EAVAIL = 938.27, 939.565, 135.0  # MeV; proton mass and 135 MeV pion as in CVUniverse.h
LEGACY_CM2 = 2.56818808476849e21  # NuWro cm2 constant; v1 dumps divided the weight by it
EAVAIL_EDGES_GEV = [0, 0.1, 0.2, 0.4, 0.8, 1.5, 3, 100]


def parse(path: Path):
    lines = path.read_text().splitlines()
    scale = 1.0 if lines[0].startswith("# v2") else LEGACY_CM2
    events = []
    for line in lines[1:]:
        head, *groups = line.split("|")
        idx, w, dyn = head.split()
        sets = []
        for g in groups[:3]:
            parts = [p.split() for p in g.split(";") if p.strip()]
            sets.append([(int(p[0]), *map(float, p[1:5])) for p in parts])
        events.append((int(idx), float(w) * scale, int(dyn), *sets))
    return events


def weighted_frac(w, mask):
    """Ratio estimator sum(w*mask)/sum(w) with its delta-method standard error."""
    tot = w.sum()
    if tot <= 0:
        return 0.0, 0.0
    f = (w * mask).sum() / tot
    resid = w * (mask - f)
    return float(f), float(np.sqrt((resid ** 2).sum()) / tot)


def kish(w):
    return float(w.sum() ** 2 / (w ** 2).sum()) if (w ** 2).sum() > 0 else 0.0


def analyse(events, flux_npz: Path | None):
    w = np.array([e[1] for e in events])
    n = w.size
    res: dict = {"n_sampled": n, "n_positive": int((w > 0).sum())}
    res["sigma_per_nucleon_cm2"] = float(w.mean())
    res["sigma_mc_error_cm2"] = float(w.std(ddof=1) / np.sqrt(n))
    res["kish_neff"] = kish(w)
    res["kish_neff_over_n"] = kish(w) / n
    res["wmax_over_wmean"] = float(w.max() / w.mean())

    chan, enu, emu, pmu_z, pmu_t, q0, qmag = [], [], [], [], [], [], []
    dp, de, eavail, tp, tn, epi, other_e, nprot, nneut, species = [], [], [], [], [], [], [], [], [], {}
    for _, wt, _, ins, outs, post in events:
        nu = ins[0]
        enu.append(nu[1])
        if wt <= 0:
            for lst in (chan, emu, pmu_z, pmu_t, q0, qmag, dp, de, eavail, tp, tn, epi, other_e, nprot, nneut):
                lst.append(np.nan)
            continue
        lep = outs[0]
        nucl_out = outs[1:]
        pdgs = sorted(p[0] for p in nucl_out)
        chan.append(3 if len(nucl_out) == 3 else (0 if pdgs == [2212, 2212] else 1))
        emu.append(lep[1])
        pmu_z.append(lep[4])
        pmu_t.append(np.hypot(lep[2], lep[3]))
        q0.append(nu[1] - lep[1])
        qmag.append(np.linalg.norm(np.array(nu[2:]) - np.array(lep[2:])))
        pin = np.sum([p[1:] for p in ins], axis=0)
        pout = np.sum([p[1:] for p in outs], axis=0)
        de.append(pin[0] - pout[0])
        dp.append(np.linalg.norm(pin[1:] - pout[1:]))
        ea = t_p = t_n = e_pi = e_oth = 0.0
        npr = nne = 0
        for pdg, E, *_ in post:
            species[pdg] = species.get(pdg, 0) + 1
            if pdg == 2212:
                ea += E - M_P
                t_p += E - M_P
                npr += 1
            elif pdg == 2112:
                t_n += E - M_N
                nne += 1
            elif abs(pdg) == 211:
                ea += E - M_PI_EAVAIL
                e_pi += E
            elif pdg in (111, 22):
                ea += E
                e_pi += E if pdg == 111 else 0.0
                e_oth += E if pdg == 22 else 0.0
            elif pdg != 13:
                e_oth += E
        eavail.append(ea)
        tp.append(t_p)
        tn.append(t_n)
        epi.append(e_pi)
        other_e.append(e_oth)
        nprot.append(npr)
        nneut.append(nne)
    a = {k: np.array(v, dtype=float) for k, v in dict(
        chan=chan, enu=enu, emu=emu, pz=pmu_z, pt=pmu_t, q0=q0, q=qmag, dp=dp, de=de,
        ea=eavail, tp=tp, tn=tn, epi=epi, oth=other_e, npr=nprot, nne=nneut).items()}
    pos = w > 0
    wp = w[pos]

    res["channel_fraction"] = {name: weighted_frac(w, np.nan_to_num(a["chan"] == code).astype(float))
                               for name, code in (("pp", 0), ("np+pn", 1), ("3p3h", 3))}
    res["conservation"] = {
        "max_abs_dp_MeV": float(np.nanmax(a["dp"])),
        "deltaE_in_minus_out_MeV": {"min": float(np.nanmin(a["de"])), "median": float(np.nanmedian(a["de"])),
                                    "max": float(np.nanmax(a["de"]))},
        "n_events_dp_over_1keV": int(np.nansum(a["dp"] > 1e-3)),
    }
    omega = a["q0"][pos]
    rem = omega - a["tp"][pos] - a["tn"][pos] - a["epi"][pos] - a["oth"][pos]
    res["energy_partition_weighted_mean_MeV"] = {
        "omega": float(np.average(omega, weights=wp)),
        "T_protons": float(np.average(a["tp"][pos], weights=wp)),
        "T_neutrons": float(np.average(a["tn"][pos], weights=wp)),
        "pions_total_E": float(np.average(a["epi"][pos], weights=wp)),
        "other_E": float(np.average(a["oth"][pos], weights=wp)),
        "unrecorded_remainder": float(np.average(rem, weights=wp)),
        "E_avail": float(np.average(a["ea"][pos], weights=wp)),
    }
    res["neutron_fraction_of_omega_weighted"] = float((a["tn"][pos] * wp).sum() / (omega * wp).sum())
    res["post_species_counts"] = {str(k): v for k, v in sorted(species.items())}
    res["mean_multiplicity_weighted"] = {"protons": float(np.average(a["npr"][pos], weights=wp)),
                                         "neutrons": float(np.average(a["nne"][pos], weights=wp))}

    theta = np.degrees(np.arctan2(a["pt"], a["pz"]))
    signal = (theta < 20) & (a["pz"] > 1500) & (a["pz"] < 60000) & (a["pt"] < 4500)
    sig = np.nan_to_num(signal).astype(float)
    res["signal_acceptance"] = weighted_frac(w, sig)
    res["signal_kish_neff"] = kish(w * sig)
    eag = a["ea"] / 1000.0
    bins = []
    for lo, hi in zip(EAVAIL_EDGES_GEV[:-1], EAVAIL_EDGES_GEV[1:]):
        m = np.nan_to_num((eag >= lo) & (eag < hi)).astype(float)
        ms = m * sig
        bins.append({"bin_GeV": [lo, hi], "frac_all": weighted_frac(w, m)[0],
                     "frac_of_signal": (w * ms).sum() / max((w * sig).sum(), 1e-300),
                     "kish_neff_signal": kish(w * ms), "n_raw_signal": int(ms.sum())})
    res["eavail_bins"] = bins
    res["q_near_cut"] = {"frac_q_gt_1100MeV": weighted_frac(w, np.nan_to_num(a["q"] > 1100).astype(float))}
    res["enu_weighted_frac_above_1p1GeV"] = weighted_frac(w, (a["enu"] > 1100).astype(float))

    if flux_npz is not None:
        d = np.load(flux_npz)
        edges = d["edges"] * 1000.0
        prob = d["phi_t_density"] * np.diff(d["edges"])
        prob = prob / prob.sum()
        counts, _ = np.histogram(a["enu"], bins=edges)
        expected = prob * n
        use = expected >= 5
        lumped_c = np.append(counts[use], counts[~use].sum())
        lumped_e = np.append(expected[use], expected[~use].sum())
        chi2 = float((((lumped_c - lumped_e) ** 2) / np.maximum(lumped_e, 1e-12)).sum())
        res["flux_sampling_check"] = {"chi2": chi2, "ndf": int(lumped_c.size - 1),
                                      "n_outside_edges": int(((a["enu"] < edges[0]) | (a["enu"] > edges[-1])).sum())}
        # weighted energy-transfer partition and sigma by E_nu decade for the support question
        res["sigma_frac_by_enu_GeV"] = {f"{lo}-{hi}": weighted_frac(w, ((a["enu"] >= lo * 1000) & (a["enu"] < hi * 1000)).astype(float))[0]
                                        for lo, hi in ((0, 1.1), (1.1, 3), (3, 10), (10, 20), (20, 50), (50, 100))}
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dump", type=Path)
    ap.add_argument("--flux-npz", type=Path)
    ap.add_argument("--json-out", type=Path, required=True)
    args = ap.parse_args()
    res = analyse(parse(args.dump), args.flux_npz)
    res["dump"] = str(args.dump.name)
    args.json_out.write_text(json.dumps(res, indent=1, default=float) + "\n")
    print(json.dumps({k: res[k] for k in ("n_sampled", "sigma_per_nucleon_cm2", "sigma_mc_error_cm2",
                                          "kish_neff_over_n", "channel_fraction", "conservation")}, default=float))


if __name__ == "__main__":
    main()
