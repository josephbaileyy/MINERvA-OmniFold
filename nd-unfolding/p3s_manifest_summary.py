#!/usr/bin/env python3
"""P3S/P3F receipt: enumerate the 5x2x12 active-universe endpoint ROOTs, verify
each, and emit an exact manifest + per-endpoint summary for the campaign commit
gate. Fingerprint per file = size + per-tree entry counts + POT + native-miss and
migration-census TParameters (cheaper and more meaningful than md5 of ~6.7 GB).

Usage: p3s_manifest_summary.py [--mode standard|fps] [--out <json>]
"""
import argparse, glob, json, os, sys
import ROOT

BANDS = ["BeamAngleX", "BeamAngleY", "MuonResolution",
         "Muon_Energy_MINERvA", "Muon_Energy_MINOS"]
PLAYLISTS = ["1A","1B","1C","1D","1E","1F","1G","1L","1M","1N","1O","1P"]
TREES = ["mc_truth_denom", "mc_signal_reco", "mc_background", "data"]
PARAMS = ["mcPOTUsed","dataPOTUsed","nTruthOnlyMisses","hasActiveUniverse",
          "activeUniverseIsLateral","activeUniverseTruthEntrants",
          "activeUniverseTruthExits","activeUniverseRecoEntrants",
          "activeUniverseRecoExits"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="standard")
    ap.add_argument("--repo", default="/pscratch/sd/j/josephrb/MINERvA-OmniFold")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    base = os.path.join(a.repo, "nd-unfolding", "active_universe_5d", a.mode)
    out = a.out or os.path.join(base, f"p3s_{a.mode}_manifest.json")

    files, present, missing = [], 0, []
    endpoints = {}
    for band in BANDS:
        for ep in (0, 1):
            key = f"{band}_{ep}"
            agg = {"playlists_present": 0, "size_bytes": 0,
                   "entries": {t: 0 for t in TREES},
                   "mcPOT": 0.0, "dataPOT": 0.0, "nMisses": 0,
                   "migration_abs": 0, "isLateral": None}
            for pl in PLAYLISTS:
                p = os.path.join(base, key,
                                 f"runEventLoopOmniFold_5D_{pl}_active_{band}_{ep}.root")
                rec = {"band": band, "endpoint": ep, "playlist": pl,
                       "path": os.path.relpath(p, a.repo), "exists": os.path.exists(p)}
                if not rec["exists"] or os.path.getsize(p) == 0:
                    missing.append(f"{key}/{pl}"); files.append(rec); continue
                rec["size"] = os.path.getsize(p)
                f = ROOT.TFile.Open(p)
                ok = f and not f.IsZombie()
                rec["readable"] = bool(ok)
                if ok:
                    ent = {}
                    for t in TREES:
                        tr = f.Get(t); ent[t] = int(tr.GetEntries()) if tr else -1
                    rec["entries"] = ent
                    pv = {}
                    for k in PARAMS:
                        o = f.Get(k); pv[k] = (o.GetVal() if o else None)
                    rec["params"] = pv
                    agg["playlists_present"] += 1
                    agg["size_bytes"] += rec["size"]
                    for t in TREES:
                        if ent[t] > 0: agg["entries"][t] += ent[t]
                    agg["mcPOT"] += pv.get("mcPOTUsed") or 0.0
                    agg["dataPOT"] += pv.get("dataPOTUsed") or 0.0
                    agg["nMisses"] += int(pv.get("nTruthOnlyMisses") or 0)
                    agg["migration_abs"] += sum(abs(int(pv.get(k) or 0)) for k in
                        ("activeUniverseTruthEntrants","activeUniverseTruthExits",
                         "activeUniverseRecoEntrants","activeUniverseRecoExits"))
                    if agg["isLateral"] is None and pv.get("activeUniverseIsLateral") is not None:
                        agg["isLateral"] = int(pv["activeUniverseIsLateral"])
                    present += 1
                f.Close()
                files.append(rec)
            # completeness self-check: signal_reco == truth_denom (Phase 18.2)
            td, sg = agg["entries"]["mc_truth_denom"], agg["entries"]["mc_signal_reco"]
            agg["completeness_sig_over_td"] = (sg / td) if td else None
            endpoints[key] = agg

    summary = {
        "mode": a.mode, "expected": 120, "present": present,
        "complete": present == 120, "missing": missing,
        "endpoints": endpoints,
    }
    with open(out, "w") as fh:
        json.dump({"summary": summary, "files": files}, fh, indent=2)

    print(f"[p3s-manifest] mode={a.mode} present={present}/120 "
          f"complete={summary['complete']} missing={len(missing)}")
    for key, agg in endpoints.items():
        c = agg["completeness_sig_over_td"]
        print(f"  {key:26s} {agg['playlists_present']:2d}/12  lat={agg['isLateral']}  "
              f"td={agg['entries']['mc_truth_denom']:>10d}  "
              f"c={('%.6f'%c) if c else 'NA':>8}  mig|abs|={agg['migration_abs']:>6d}  "
              f"misses={agg['nMisses']}")
    print(f"summary -> {out}")
    sys.exit(0 if summary["complete"] else 2)

if __name__ == "__main__":
    main()
