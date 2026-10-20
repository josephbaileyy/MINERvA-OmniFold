#!/usr/bin/env python3
"""MP1-A S0: the q0-convention check and the G2 species-sum check on one MC AnaTuple.

Reads at most ``--entries`` (default 20,000) entries of tree ``MasterAnaDev`` with uproot and prints a
plain-text receipt. Nothing is written. Run on a login node:

    ssh saul 'python -I - <mc.root> [--entries N]' < s0_inspect_q0_g2.py

Selection ("selected-like"): the event loop's six reco pre-cuts (runEventLoopOmniFold.cpp:1710-1715), with
the tuple branch ``MasterAnaDev_muon_theta`` standing in for MAT's ``GetThetamu()`` (which rebuilds the
angle from thetaX/thetaY with the beam correction) and ``MasterAnaDev_minos_trk_qp`` for ``GetMuonQP()``.

G2: on selected events, the species pieces of ``blob_recoil_E_tracker`` and ``_ecal`` must sum to the totals
(ratio 1 to 1e-6); the script also reports whether ``_xtalk`` and ``_mu`` are components of the sums and
how the muon fuzz NewEavail subtracts compares with the ``_mu`` piece.

q0: compares ``MasterAnaDev_recoil_E`` event by event with every candidate "sum of parts" and reports,
per candidate, the fraction of events at ratio 1 and at a fixed multiple (the median ratio), both to 1e-6.
"""
from __future__ import annotations

import argparse
import datetime
import sys

import numpy as np
import uproot

TREE = "MasterAnaDev"
BLOB_SPECIES = ("p", "meson", "em", "other", "lown", "midn", "highn", "xtalk", "mu")
PR_SPECIES = ("proton", "meson", "em", "other", "low_neutron", "mid_neutron", "high_neutron",
              "xtalk", "muon", "none")
PR_PROTON_BINS = ("low_proton", "mid_proton", "high_proton")
D1_BANDS = {"p": "proton", "meson": "meson", "em": "em", "other": "other", "xtalk": "xtalk"}
TOL = 1e-6
TRK_LO, TRK_HI = 1504968704, 1560805376      # CVUniverse::GetTrackerECALMuFuzz plane-ID windows
ECAL_LO, ECAL_HI = 1700003840, 1709703168
FUZZ_LO, FUZZ_HI = 1504968704, 1709703168


def stats(x: np.ndarray) -> str:
    """Return a one-line distribution summary of ``x`` (finite values only)."""
    x = x[np.isfinite(x)]
    if x.size == 0:
        return "n=0"
    q = np.percentile(x, [0, 1, 50, 99, 100])
    return (f"n={x.size} min={q[0]:.6g} p1={q[1]:.6g} p50={q[2]:.6g} p99={q[3]:.6g} "
            f"max={q[4]:.6g} mean={x.mean():.6g}")


def ratio_report(name: str, num: np.ndarray, den: np.ndarray, mask: np.ndarray) -> None:
    """Print how ``num/den`` behaves on ``mask & den != 0``: ratio 1 and fixed-multiple fractions."""
    m = mask & (den != 0) & np.isfinite(num) & np.isfinite(den)
    if not m.any():
        print(f"  {name:58s} n=0")
        return
    r = num[m] / den[m]
    med = float(np.median(r))
    at1 = np.mean(np.abs(r - 1.0) <= TOL)
    atmed = np.mean(np.abs(r / med - 1.0) <= TOL) if med != 0 else float("nan")
    print(f"  {name:58s} n={m.sum():6d} frac(|r-1|<=1e-6)={at1:.4f} "
          f"frac(|r/median-1|<=1e-6)={atmed:.4f} median={med:.6g} "
          f"p1={np.percentile(r, 1):.6g} p99={np.percentile(r, 99):.6g}")


def muon_fuzz(ids: np.ndarray, energies: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """CVUniverse::GetTrackerECALMuFuzz, vectorised over a jagged (awkward) pair of arrays."""
    trk = np.zeros(len(ids))
    ecal = np.zeros(len(ids))
    for i, (pid, en) in enumerate(zip(ids, energies)):
        pid = np.asarray(pid)
        en = np.asarray(en)
        keep = (pid >= FUZZ_LO) & (pid <= FUZZ_HI)
        trk[i] = en[keep & (pid > TRK_LO) & (pid < TRK_HI)].sum()
        ecal[i] = en[keep & (pid > ECAL_LO) & (pid < ECAL_HI)].sum()
    return trk, ecal


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mc_file")
    ap.add_argument("--entries", type=int, default=20000)
    args = ap.parse_args(argv)
    if args.entries > 20000:
        print("refusing: the S0 inspection reads at most 20,000 entries", file=sys.stderr)
        return 2

    print(f"# UTC {datetime.datetime.now(datetime.timezone.utc).isoformat()} "
          f"uproot {uproot.__version__} numpy {np.__version__}")
    print(f"# FILE {args.mc_file}")
    t = uproot.open(args.mc_file)[TREE]
    keys = set(t.keys())

    scal = ["MasterAnaDev_recoil_E", "MasterAnaDev_recoil_passivecorrected", "MasterAnaDev_recoil_E_wide_window",
            "recoil_E_nopolyline", "recoil_E_polylinecorrected", "blob_recoil_E",
            "part_response_total_recoil_passive_id", "part_response_total_recoil_passive_od",
            "isMinosMatchTrack", "MasterAnaDev_minos_trk_is_ok", "MasterAnaDev_minos_trk_qp",
            "phys_n_dead_discr_pair_upstream_prim_track_proj", "MasterAnaDev_muon_theta",
            "mc_current", "mc_incoming"]
    for det in ("tracker", "ecal", "hcal", "nucl", "od"):
        scal.append(f"blob_recoil_E_{det}")
        scal += [f"blob_recoil_E_{det}_{s}" for s in BLOB_SPECIES]
    for s in PR_SPECIES + PR_PROTON_BINS:
        for suf in ("id", "od", "id_err", "od_err"):
            scal.append(f"part_response_recoil_allNonMuonClusters_{s}_{suf}")
        for suf in ("id", "od"):
            scal.append(f"part_response_recoil_passive_{s}_{suf}")
    missing = [b for b in scal if b not in keys]
    print(f"# branches requested {len(scal)}; missing {len(missing)}: {missing}")
    scal = [b for b in scal if b in keys]
    jag = ["vtx", "muon_fuzz_per_plane_r80_planeIDs", "muon_fuzz_per_plane_r80_energies",
           "MasterAnaDev_sys_recoil_energy_shift"]
    a = t.arrays(scal, entry_stop=args.entries, library="np")
    j = t.arrays(jag, entry_stop=args.entries, library="np")
    n = len(a["MasterAnaDev_recoil_E"])
    print(f"# entries read {n} of {t.num_entries}")
    f = {k: a[k].astype(float) for k in scal}

    vtx = np.stack(j["vtx"]).astype(float)
    x, y, z = vtx[:, 0], vtx[:, 1], vtx[:, 2]
    apo = 850.0
    in_hex = (np.abs(y) < -1.0 / np.sqrt(3.0) * np.abs(x) + 2.0 * apo / np.sqrt(3.0)) & (np.abs(x) < apo)
    sel = ((z >= 5980) & (z <= 8422) & in_hex
           & (f["MasterAnaDev_muon_theta"] < 20.0 * np.pi / 180.0)
           & (f["isMinosMatchTrack"] == 1) & (f["MasterAnaDev_minos_trk_is_ok"] == 1)
           & (f["phys_n_dead_discr_pair_upstream_prim_track_proj"] < 1)
           & (f["MasterAnaDev_minos_trk_qp"] < 0))
    cc = (f["mc_current"] == 1) & (f["mc_incoming"] == 14)
    print(f"# selected-like events: {sel.sum()} (of which true numu CC {np.sum(sel & cc)})")

    q0 = f["MasterAnaDev_recoil_E"]
    print("\n## 0. MasterAnaDev_recoil_E (q0) on selected-like events")
    print("  all     " + stats(q0[sel]))
    neg = sel & (q0 < 0)
    print(f"  negative: {neg.sum()} events; distinct negative values (first 10): "
          f"{np.unique(np.round(q0[neg], 6))[:10].tolist()}")
    print(f"  zero: {np.sum(sel & (q0 == 0))}")

    print("\n## 1. G2: species pieces vs blob_recoil_E_<det> on selected-like events")
    for det in ("tracker", "ecal"):
        tot = f[f"blob_recoil_E_{det}"]
        parts = {s: f[f"blob_recoil_E_{det}_{s}"] for s in BLOB_SPECIES}
        ssum = sum(parts.values())
        m = sel & (tot > 0)
        r = ssum[m] / tot[m]
        print(f"  {det}: events with total>0: {m.sum()}; sum(9 species)/total: max|r-1|={np.max(np.abs(r - 1)):.3e} "
              f"frac(|r-1|<=1e-6)={np.mean(np.abs(r - 1) <= TOL):.6f}; "
              f"max|sum-total|={np.max(np.abs(ssum[m] - tot[m])):.3e} MeV; "
              f"events total==0 with sum!=0: {np.sum(sel & (tot == 0) & (ssum != 0))}")
        for drop in ("xtalk", "mu"):
            rr = (ssum[m] - parts[drop][m]) / tot[m]
            print(f"    without _{drop}: frac(|r-1|<=1e-6)={np.mean(np.abs(rr - 1) <= TOL):.4f} "
                  f"(events with _{drop}>0: {np.mean(parts[drop][m] > 0):.4f}); "
                  f"share of {det} total: mean={np.mean(parts[drop][m] / tot[m]):.4f}")
        negp = {s: int(np.sum(sel & (parts[s] < 0))) for s in BLOB_SPECIES}
        print(f"    negative species pieces: {negp}")

    trk_fz, ecal_fz = muon_fuzz(j["muon_fuzz_per_plane_r80_planeIDs"], j["muon_fuzz_per_plane_r80_energies"])
    trk, ecal = f["blob_recoil_E_tracker"], f["blob_recoil_E_ecal"]
    raw = trk + ecal
    new_eavail = ((trk - trk_fz) + (ecal - ecal_fz)) * 1.17
    print("\n## 2. muon fuzz (CVUniverse::GetTrackerECALMuFuzz) vs the _mu pieces, selected-like")
    for det, fz, mu, xt, tot in (("tracker", trk_fz, f["blob_recoil_E_tracker_mu"], f["blob_recoil_E_tracker_xtalk"], trk),
                                 ("ecal", ecal_fz, f["blob_recoil_E_ecal_mu"], f["blob_recoil_E_ecal_xtalk"], ecal)):
        m = sel
        has = m & (fz > 0)
        print(f"  {det}: events fuzz>0: {has.sum()}; fuzz " + stats(fz[has]))
        print(f"    fuzz <= _mu + 1e-6: {np.mean(fz[has] <= mu[has] + 1e-6):.4f}; "
              f"fuzz <= _mu + _xtalk + 1e-6: {np.mean(fz[has] <= mu[has] + xt[has] + 1e-6):.4f}; "
              f"fuzz <= total + 1e-6: {np.mean(fz[has] <= tot[has] + 1e-6):.4f}")
        ex = np.clip(fz - mu, 0, None)
        print(f"    excess (fuzz - _mu)_+ over events fuzz>0: " + stats(ex[has]))
        print(f"    _mu - fuzz (events fuzz>0): " + stats((mu - fz)[has]))
        print(f"    _mu > 0 with fuzz == 0: {np.sum(m & (mu > 0) & (fz == 0))}")
    m = sel & (raw > 0)
    ex_all = np.clip(trk_fz - f["blob_recoil_E_tracker_mu"], 0, None) + np.clip(ecal_fz - f["blob_recoil_E_ecal_mu"], 0, None)
    print(f"  (fuzz - _mu)_+ summed over tracker+ECAL, as a fraction of the raw sum (selected, raw>0): "
          + stats(ex_all[m] / raw[m]))
    print(f"  NewEavail (MeV) " + stats(new_eavail[sel]))
    print("  species shares of the raw tracker+ECAL sum (mean over selected, raw>0):")
    for s in BLOB_SPECIES:
        es = f[f"blob_recoil_E_tracker_{s}"] + f[f"blob_recoil_E_ecal_{s}"]
        print(f"    {s:6s} mean share={np.mean(es[m] / raw[m]):.4f}  frac events>0={np.mean(es[m] > 0):.4f}")
    fz_all = trk_fz + ecal_fz
    print("  bound on species-s energy inside the subtracted fuzz, summed over selected events, as a fraction of "
          "sum E_s (E_s = tracker_s + ecal_s):")
    print("    strict  = sum min(E_s, fuzz) / sum E_s;  indicative = sum min(E_s, (fuzz - _mu)_+) / sum E_s")
    for s in D1_BANDS:
        es = f[f"blob_recoil_E_tracker_{s}"] + f[f"blob_recoil_E_ecal_{s}"]
        tot_s = es[m].sum()
        strict = np.minimum(es, fz_all)[m].sum() / tot_s
        indic = np.minimum(es, ex_all)[m].sum() / tot_s
        print(f"    {s:6s} strict={strict:.4f} indicative={indic:.4f}")
    frac_conv = np.where(raw > 0, new_eavail / np.where(raw > 0, raw, 1.0), 0.0)
    print("  NewEavail / (1.17 * raw), i.e. the fractional-fuzz factor (selected, raw>0): " + stats(frac_conv[m] / 1.17))

    print("\n## 3. q0 convention: MasterAnaDev_recoil_E against candidate sums of parts (selected-like)")
    A_id = sum(f[f"part_response_recoil_allNonMuonClusters_{s}_id"] for s in PR_SPECIES)
    A_od = sum(f[f"part_response_recoil_allNonMuonClusters_{s}_od"] for s in PR_SPECIES)
    P_id = f["part_response_total_recoil_passive_id"]
    P_od = f["part_response_total_recoil_passive_od"]
    Ps_id = sum(f[f"part_response_recoil_passive_{s}_id"] for s in PR_SPECIES)
    Ps_od = sum(f[f"part_response_recoil_passive_{s}_od"] for s in PR_SPECIES)
    pos = sel & (q0 > 0)
    cands = {
        "sum_s allNonMuonClusters_<s>_id (legacy parts, ID)": A_id,
        "sum_s allNonMuonClusters_<s>_id + _od (legacy parts, ID+OD)": A_id + A_od,
        "part_response_total_recoil_passive_id": P_id,
        "part_response_total_recoil_passive_id + _od": P_id + P_od,
        "sum_s part_response_recoil_passive_<s>_id": Ps_id,
        "sum_s part_response_recoil_passive_<s>_id + _od": Ps_id + Ps_od,
        "MasterAnaDev_recoil_passivecorrected": f["MasterAnaDev_recoil_passivecorrected"],
        "recoil_E_nopolyline": f["recoil_E_nopolyline"],
        "recoil_E_polylinecorrected": f["recoil_E_polylinecorrected"],
        "MasterAnaDev_recoil_E_wide_window": f["MasterAnaDev_recoil_E_wide_window"],
        "blob_recoil_E": f["blob_recoil_E"],
    }
    print("  ratio r = MasterAnaDev_recoil_E / X, events with q0>0:")
    for name, X in cands.items():
        ratio_report(name, q0, X, pos)
    print("  ratio r = MasterAnaDev_recoil_E / X, ALL selected-like events (incl. q0<=0):")
    for name in ("recoil_E_polylinecorrected", "recoil_E_nopolyline", "MasterAnaDev_recoil_passivecorrected"):
        ratio_report(name, q0, cands[name], sel)

    print("  internal identities (selected-like):")
    ratio_report("sum_s passive_<s>_id / total_passive_id", Ps_id, P_id, sel)
    ratio_report("sum_s passive_<s>_od / total_passive_od", Ps_od, P_od, sel)
    ratio_report("passivecorrected / (total_passive_id + _od)", f["MasterAnaDev_recoil_passivecorrected"], P_id + P_od, sel)
    ratio_report("passivecorrected / total_passive_id", f["MasterAnaDev_recoil_passivecorrected"], P_id, sel)
    ratio_report("recoil_E_nopolyline / passivecorrected", f["recoil_E_nopolyline"], f["MasterAnaDev_recoil_passivecorrected"], sel)
    ratio_report("legacy ID parts / blob_recoil_E", A_id, f["blob_recoil_E"], sel)
    ratio_report("legacy ID+OD parts / blob_recoil_E", A_id + A_od, f["blob_recoil_E"], sel)
    prb = sum(f[f"part_response_recoil_allNonMuonClusters_{s}_id"] for s in PR_PROTON_BINS)
    ratio_report("allNonMuon low+mid+high_proton_id / proton_id", prb, f["part_response_recoil_allNonMuonClusters_proton_id"], sel)
    for s in ("proton", "meson", "em", "other", "xtalk"):
        ratio_report(f"allNonMuon_{s}_id_err / _id", f[f"part_response_recoil_allNonMuonClusters_{s}_id_err"],
                     f[f"part_response_recoil_allNonMuonClusters_{s}_id"], sel)
        ratio_report(f"allNonMuon_{s}_od_err / _od", f[f"part_response_recoil_allNonMuonClusters_{s}_od_err"],
                     f[f"part_response_recoil_allNonMuonClusters_{s}_od"], sel)

    print("\n## 4. how the species pieces map between the two families (selected-like, mean over events with both>0)")
    for bs, ps in D1_BANDS.items():
        b = f[f"blob_recoil_E_tracker_{bs}"] + f[f"blob_recoil_E_ecal_{bs}"]
        p_id = f[f"part_response_recoil_allNonMuonClusters_{ps}_id"]
        pp = f[f"part_response_recoil_passive_{ps}_id"]
        ratio_report(f"blob tracker+ecal _{bs} / allNonMuon_{ps}_id", b, p_id, sel & (b > 0))
        ratio_report(f"passive_{ps}_id / allNonMuon_{ps}_id", pp, p_id, sel & (pp > 0))

    print("\n## 5. the producer's own recoil shift MasterAnaDev_sys_recoil_energy_shift[0,1] (selected-like)")
    sh = np.stack(j["MasterAnaDev_sys_recoil_energy_shift"]).astype(float)
    errs_id = [f[f"part_response_recoil_allNonMuonClusters_{s}_id_err"] for s in PR_SPECIES]
    quad = np.sqrt(sum(e * e for e in errs_id))
    lin = sum(errs_id)
    print("  shift[0] " + stats(sh[sel, 0]))
    print("  shift[1] " + stats(sh[sel, 1]))
    ratio_report("shift[1] / q0", sh[:, 1], q0, pos)
    ratio_report("-shift[0] / shift[1]", -sh[:, 0], sh[:, 1], sel)
    ratio_report("shift[1] / sqrt(sum_s _id_err^2)", sh[:, 1], quad, sel)
    ratio_report("shift[1] / sum_s _id_err", sh[:, 1], lin, sel)

    print("\n## 6. is q0 a fixed multiple, or a nonlinear function, of pc = sum_s (allNonMuon_<s>_id + _od)?")
    pc = A_id + A_od
    ratio_report("MasterAnaDev_recoil_passivecorrected / pc", f["MasterAnaDev_recoil_passivecorrected"], pc, sel)
    mm = pos & (pc > 0)
    r = q0[mm] / pc[mm]
    k0 = float(np.median(r[r < np.percentile(r, 5) * (1 + 1e-6)]))
    at_k0 = np.abs(r / k0 - 1) <= TOL
    print(f"  low-energy constant k0 = {k0:.10g}; events at q0 = k0*pc (1e-6): {at_k0.mean():.4f} of {mm.sum()}")
    P = pc[mm]
    for lo, hi in ((0, 100), (100, 300), (300, 500), (500, 1000), (1000, 2000), (2000, 5000), (5000, np.inf)):
        k = (P >= lo) & (P < hi)
        if k.any():
            print(f"    pc in [{lo},{hi}) MeV: n={k.sum():5d} frac at k0={at_k0[k].mean():.3f} "
                  f"q0/pc p1={np.percentile(r[k], 1):.5f} p50={np.median(r[k]):.5f} p99={np.percentile(r[k], 99):.5f}")
    o = np.argsort(P)
    Ps, qs = P[o], q0[mm][o]
    close = np.diff(Ps) / Ps[1:] < 1e-3
    dq = np.abs(np.diff(qs)) / qs[1:]
    print(f"  single-valuedness: {close.sum()} neighbour pairs with pc within 0.1%; |dq0|/q0 > 1%: "
          f"{np.mean(dq[close] > 0.01):.4f}; > 5%: {np.mean(dq[close] > 0.05):.4f}")
    same = sel & (np.abs(pc - f["recoil_E_nopolyline"]) <= TOL * np.maximum(pc, 1.0)) & (q0 > 0)
    ratio_report("q0 / recoil_E_polylinecorrected where pc == recoil_E_nopolyline", q0,
                 f["recoil_E_polylinecorrected"], same)
    ratio_report("recoil_E_nopolyline / blob_recoil_E", f["recoil_E_nopolyline"], f["blob_recoil_E"], sel)
    print("  candidate conventions for one species s at +1 sigma, as (q0' - q0) / (delta_s * pc_s):")
    print("    legacy absolute: 1 (by construction); fractional: q0/pc; the local slope of q0(pc) is what the")
    print("    detector response would give, and equals q0/pc only where q0 = k0*pc.")
    print(f"    fractional/legacy ratio q0/pc on selected q0>0: " + stats(r))

    print("\n## 7. local slope dq0/dpc (least squares within log-spaced pc bins) against the secant q0/pc")
    edges = np.geomspace(max(Ps[0], 1.0), Ps[-1] * 1.0001, 25)
    for lo, hi in zip(edges[:-1], edges[1:]):
        k = (Ps >= lo) & (Ps < hi)
        if k.sum() < 20:
            continue
        slope = np.polyfit(Ps[k], qs[k], 1)[0]
        sec = np.median(qs[k] / Ps[k])
        print(f"    pc in [{lo:8.1f},{hi:8.1f}) n={k.sum():5d} slope={slope:.5f} secant={sec:.5f} "
              f"slope/secant={slope / sec:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
