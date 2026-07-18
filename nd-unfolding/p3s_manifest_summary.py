#!/usr/bin/env python3
"""P3S/P3F acceptance audit + receipt: enumerate the 5x2x12 active-universe
endpoint ROOTs for a mode, validate each against the acceptance checks, and emit
a compact machine-readable summary + downstream file map for the commit gate.

Per-file acceptance checks:
  schema (4 trees present), finite POT, event counts, native-miss metadata,
  ENDPOINT IDENTITY (metadata band/idx match the filename), truth-authoritative
  completeness (signal_reco==truth_denom), and point-cloud branch presence
  (signal part_gen_*+part_reco_*; background+data part_reco_*) since these ROOTs
  are dumped with MNV101_DUMP_POINTCLOUD=1.

Campaign provenance recorded: git HEAD (source commit), installed-binary md5+mtime,
launcher path + git blob hash (manifest hash proxy).

Usage: p3s_manifest_summary.py [--mode standard|fps] [--out <json>]
Exit 0 iff mode is 120/120 complete AND every present file passes; 2 otherwise.
"""
import argparse, hashlib, json, os, subprocess, sys
import ROOT

BANDS = ["BeamAngleX", "BeamAngleY", "MuonResolution",
         "Muon_Energy_MINERvA", "Muon_Energy_MINOS"]
PLAYLISTS = ["1A","1B","1C","1D","1E","1F","1G","1L","1M","1N","1O","1P"]
TREES = ["mc_truth_denom", "mc_signal_reco", "mc_background", "data"]
SIG_PC = ["part_gen_E", "part_gen_pdg", "part_reco_E", "part_reco_pos", "part_reco_z"]
RECO_PC = ["part_reco_E", "part_reco_pos", "part_reco_z"]

def _sh(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None

def get_val(f, name):
    o = f.Get(name)
    if o is None:
        return None
    if hasattr(o, "GetVal"):
        return o.GetVal()
    if hasattr(o, "GetTitle"):
        return o.GetTitle()
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="standard")
    ap.add_argument("--repo", default="/pscratch/sd/j/josephrb/MINERvA-OmniFold")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    base = os.path.join(a.repo, "nd-unfolding", "active_universe_5d", a.mode)
    out = a.out or os.path.join(base, f"p3s_{a.mode}_manifest.json")
    os.makedirs(base, exist_ok=True)

    binpath = os.path.join(a.repo, "MINERvA101/opt/bin/runEventLoopOmniFold")
    launcher = "nd-unfolding/sbatch_evloop_array_5d_active_laterals.sh"
    prov = {
        "mode": a.mode,
        "source_commit": _sh(f"cd {a.repo} && git rev-parse HEAD"),
        "binary_md5": _sh(f"md5sum {binpath} | cut -d' ' -f1"),
        "binary_mtime": _sh(f"stat -c '%y' {binpath}"),
        "launcher": launcher,
        "launcher_git_blob": _sh(f"cd {a.repo} && git hash-object {launcher}"),
        "expected_full_phase_space": (a.mode == "fps"),
    }

    files, present, missing, bad = [], 0, [], []
    endpoints = {}
    for band in BANDS:
        for ep in (0, 1):
            key = f"{band}_{ep}"
            agg = {"playlists_present": 0, "size_bytes": 0,
                   "entries": {t: 0 for t in TREES},
                   "mcPOT": 0.0, "dataPOT": 0.0, "nMisses": 0,
                   "migration_abs": 0, "isLateral": None, "identity_ok": 0}
            for pl in PLAYLISTS:
                p = os.path.join(base, key,
                                 f"runEventLoopOmniFold_5D_{pl}_active_{band}_{ep}.root")
                rec = {"band": band, "endpoint": ep, "playlist": pl,
                       "path": os.path.relpath(p, a.repo),
                       "exists": os.path.exists(p) and os.path.getsize(p) > 0}
                if not rec["exists"]:
                    missing.append(f"{key}/{pl}"); files.append(rec); continue
                rec["size"] = os.path.getsize(p)
                f = ROOT.TFile.Open(p)
                if not f or f.IsZombie():
                    rec["readable"] = False; bad.append(f"{key}/{pl}:zombie")
                    files.append(rec); continue
                rec["readable"] = True
                checks = {}
                # schema
                ent = {}
                for t in TREES:
                    tr = f.Get(t); ent[t] = int(tr.GetEntries()) if tr else -1
                rec["entries"] = ent
                checks["schema_4trees"] = all(f.Get(t) for t in TREES)
                checks["counts_positive"] = ent["mc_truth_denom"] > 0 and ent["mc_signal_reco"] > 0
                # POT finite
                mcPOT = get_val(f, "mcPOTUsed"); dataPOT = get_val(f, "dataPOTUsed")
                import math
                checks["pot_finite"] = (mcPOT is not None and dataPOT is not None
                                        and math.isfinite(mcPOT) and math.isfinite(dataPOT)
                                        and mcPOT > 0 and dataPOT > 0)
                # native-miss metadata
                nMiss = get_val(f, "nTruthOnlyMisses"); hasMiss = get_val(f, "hasTruthOnlyMisses")
                checks["misses_meta"] = (nMiss is not None and hasMiss is not None)
                # endpoint identity
                aBand = get_val(f, "activeUniverseBand"); aIdx = get_val(f, "activeUniverseIndex")
                aEn = get_val(f, "hasActiveUniverse"); aLat = get_val(f, "activeUniverseIsLateral")
                checks["identity"] = (aBand == band and aIdx is not None and int(aIdx) == ep
                                      and aEn == 1 and aLat == 1)
                rec["identity"] = {"band": aBand, "idx": aIdx, "hasActive": aEn, "isLateral": aLat}
                # completeness (Phase 18.2)
                td, sg = ent["mc_truth_denom"], ent["mc_signal_reco"]
                comp = (sg / td) if td else None
                rec["completeness"] = comp
                checks["completeness"] = (comp is not None and abs(comp - 1.0) < 0.02)
                # point-cloud presence
                sigtr, bkgtr, datr = f.Get("mc_signal_reco"), f.Get("mc_background"), f.Get("data")
                checks["pc_signal"] = all(sigtr and sigtr.GetBranch(b) for b in SIG_PC)
                checks["pc_bkg"] = all(bkgtr and bkgtr.GetBranch(b) for b in RECO_PC)
                checks["pc_data"] = all(datr and datr.GetBranch(b) for b in RECO_PC)
                f.Close()
                rec["checks"] = checks
                rec["pass"] = all(checks.values())
                mig = 0
                files.append(rec)
                if rec["pass"]:
                    present += 1
                    agg["playlists_present"] += 1
                    agg["size_bytes"] += rec["size"]
                    for t in TREES:
                        if ent[t] > 0: agg["entries"][t] += ent[t]
                    agg["mcPOT"] += mcPOT or 0.0; agg["dataPOT"] += dataPOT or 0.0
                    agg["nMisses"] += int(nMiss or 0)
                    if aLat is not None: agg["isLateral"] = int(aLat)
                    agg["identity_ok"] += 1
                else:
                    bad.append(f"{key}/{pl}:" + ",".join(k for k, v in checks.items() if not v))
            td, sg = agg["entries"]["mc_truth_denom"], agg["entries"]["mc_signal_reco"]
            agg["completeness_sig_over_td"] = (sg / td) if td else None
            endpoints[key] = agg

    summary = {"provenance": prov, "expected": 120, "present_and_passing": present,
               "complete": present == 120, "missing": missing, "failing": bad,
               "endpoints": endpoints}
    with open(out, "w") as fh:
        json.dump({"summary": summary, "files": files}, fh, indent=2)

    print(f"[audit {a.mode}] passing={present}/120 complete={summary['complete']} "
          f"missing={len(missing)} failing={len(bad)}")
    print(f"[prov] commit={prov['source_commit'][:10] if prov['source_commit'] else '?'} "
          f"bin_md5={prov['binary_md5']} launcher_blob={ (prov['launcher_git_blob'] or '?')[:10]}")
    for key, agg in endpoints.items():
        c = agg["completeness_sig_over_td"]
        print(f"  {key:26s} {agg['playlists_present']:2d}/12  lat={agg['isLateral']}  "
              f"id_ok={agg['identity_ok']}  c={('%.6f'%c) if c else 'NA':>8}  misses={agg['nMisses']}")
    if bad:
        print("FAILING:", "; ".join(bad[:12]))
    print(f"summary -> {out}")
    sys.exit(0 if summary["complete"] and not bad else 2)

if __name__ == "__main__":
    main()
