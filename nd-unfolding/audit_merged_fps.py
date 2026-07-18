#!/usr/bin/env python3
"""P4-FPS merged-endpoint audit (Agent C). GATE between the P3F merge and the endpoint
unfold: confirms each of the 10 merged FPS active omnifiles carries everything the unfold
(unfold_nd_omnifold_unbinned.py) consumes AND the selection-complete active-universe census.

Per merged endpoint the HARD gates are:
  - the 4 unfold trees present + nonzero entries: mc_signal_reco, mc_background, data, mc_truth_denom
  - POT metadata present, finite, >0: dataPOTUsed, mcPOTUsed (hadd-summed over the 12 playlists)
  - hasTruthOnlyMisses object present (native-miss accounting the unfold reads)
  - identity metadata matches the filename: activeUniverseBand==BAND, activeUniverseIndex==EP,
    activeUniverseIsLateral==1, hasActiveUniverse==1
  - migration census params present (activeUniverse{Truth,Reco}{Entrants,Exits}, hadd-summed)
  - selection-migration is band-dependent: the ANGLE bands (BeamAngleX/Y) cross the muon-angle
    selection cut so zero migration is a HARD FAIL; the ENERGY/momentum bands (MuonResolution,
    Muon_Energy_*) shift muon momentum -> in FPS (muon truth cuts dropped, no reco momentum cut
    they cross at +/-1sigma) they cause (pt,pz) BIN migration, not selection entrant/exit, so zero
    selection-migration is EXPECTED and only a WARNING (the real applied-check is the nonzero
    downstream lateral covariance in p4_validate_active_lateral_fps.py). Confirmed 2026-07-17: all
    5 bands' shifts are applied (endpoints differ per-event; MuonRes rel 1e-2, MINOS 3e-2, MINERvA
    4e-6 -- tiny because MINOS dominates forward-muon p||).
Writes a compact JSON summary; exit 0 iff every endpoint passes every hard gate.

  audit_merged_fps.py --merged-dir active_universe_5d/fps/merged \
      --out active_universe_5d/fps/covariance/audit_merged_fps.json
"""
import argparse, json, os, sys
import ROOT

ROOT.gROOT.SetBatch(True)
BANDS = ["BeamAngleX", "BeamAngleY", "MuonResolution",
         "Muon_Energy_MINERvA", "Muon_Energy_MINOS"]
# angle bands cross the muon-angle selection cut -> MUST show selection migration; energy/momentum
# bands cause (pt,pz) bin migration only in FPS -> zero selection-migration is expected (warn only).
ANGLE_BANDS = {"BeamAngleX", "BeamAngleY"}
TREES = ["mc_signal_reco", "mc_background", "data", "mc_truth_denom"]
CENSUS = ["activeUniverseTruthEntrants", "activeUniverseTruthExits",
          "activeUniverseRecoEntrants", "activeUniverseRecoExits"]


def get_val(f, key):
    o = f.Get(key)
    if not o:
        return None
    try:
        return o.GetVal()
    except AttributeError:
        # TNamed (string metadata) -> GetTitle
        try:
            return o.GetTitle()
        except AttributeError:
            return None


def audit_one(path, band, ep):
    rec = {"path": os.path.basename(path), "band": band, "endpoint": ep, "fails": []}
    if not os.path.exists(path):
        rec["fails"].append("missing merged file")
        return rec
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        rec["fails"].append("cannot open / zombie")
        return rec
    # trees + entries
    ents = {}
    for tn in TREES:
        t = f.Get(tn)
        if not t:
            rec["fails"].append(f"missing tree {tn}")
            ents[tn] = None
        else:
            ents[tn] = int(t.GetEntries())
            if ents[tn] <= 0:
                rec["fails"].append(f"tree {tn} has 0 entries")
    rec["entries"] = ents
    # POT
    dp, mp = get_val(f, "dataPOTUsed"), get_val(f, "mcPOTUsed")
    rec["dataPOTUsed"], rec["mcPOTUsed"] = dp, mp
    if dp is None or mp is None:
        rec["fails"].append("missing POT metadata")
    else:
        import math
        if not (math.isfinite(dp) and math.isfinite(mp) and mp > 0 and dp > 0):
            rec["fails"].append(f"invalid POT data={dp} mc={mp}")
    # native-miss object
    if not f.Get("hasTruthOnlyMisses"):
        rec["fails"].append("missing hasTruthOnlyMisses")
    # identity metadata
    aBand = get_val(f, "activeUniverseBand")
    aIdx = get_val(f, "activeUniverseIndex")
    aLat = get_val(f, "activeUniverseIsLateral")
    aEn = get_val(f, "hasActiveUniverse")
    rec["identity"] = {"band": aBand, "idx": aIdx, "isLateral": aLat, "hasActive": aEn}
    if str(aBand) != band:
        rec["fails"].append(f"activeUniverseBand '{aBand}' != '{band}'")
    if aIdx is None or int(aIdx) != ep:
        rec["fails"].append(f"activeUniverseIndex {aIdx} != {ep}")
    if aLat is None or int(aLat) != 1:
        rec["fails"].append(f"activeUniverseIsLateral {aLat} != 1")
    if aEn is None or int(aEn) != 1:
        rec["fails"].append(f"hasActiveUniverse {aEn} != 1")
    # migration census (hadd-summed TParameter<long> over the 12 playlists)
    cen = {k: get_val(f, k) for k in CENSUS}
    rec["census"] = cen
    rec["warnings"] = []
    if any(v is None for v in cen.values()):
        rec["fails"].append("missing migration census param(s)")
    else:
        tot = sum(abs(int(v)) for v in cen.values())
        rec["migration_abs_total"] = tot
        if tot == 0:
            if band in ANGLE_BANDS:
                rec["fails"].append("zero selection-migration (angle band must cross the angle cut)")
            else:
                rec["warnings"].append(
                    "zero selection-migration (expected for an energy/momentum lateral in FPS: "
                    "the shift drives (pt,pz) bin migration, not selection entrant/exit; the applied "
                    "shift + nonzero covariance are verified downstream)")
    f.Close()
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--merged-dir", default="active_universe_5d/fps/merged")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    out = {"merged_dir": a.merged_dir, "endpoints": [], "result": None}
    all_fail = []; all_warn = []
    for band in BANDS:
        for ep in (0, 1):
            path = os.path.join(
                a.merged_dir,
                f"runEventLoopOmniFold_5D_FPS_active_{band}_{ep}_universes_full.root")
            rec = audit_one(path, band, ep)
            out["endpoints"].append(rec)
            mig = rec.get("migration_abs_total")
            warns = rec.get("warnings", [])
            status = "OK" if not rec["fails"] else "FAIL " + "; ".join(rec["fails"])
            if not rec["fails"] and warns:
                status = "OK (WARN: zero selection-migration; bin-migration band)"
            print(f"[{band:22s} ep{ep}] entries={rec.get('entries')} "
                  f"POT(d/mc)={rec.get('dataPOTUsed')}/{rec.get('mcPOTUsed')} "
                  f"mig={mig} :: {status}")
            all_fail += [f"{band}_{ep}: {m}" for m in rec["fails"]]
            all_warn += [f"{band}_{ep}: {m}" for m in warns]

    out["result"] = "PASS" if not all_fail else "FAIL"
    out["n_endpoints"] = len(out["endpoints"])
    out["fails"] = all_fail
    out["warnings"] = all_warn
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nRESULT {out['result']} ({out['n_endpoints']}/10 endpoints)"
          + ("" if not all_fail else " :: " + str(len(all_fail)) + " hard failures")
          + (f" :: {len(all_warn)} warnings" if all_warn else ""))
    print(f"summary -> {a.out}")
    sys.exit(0 if not all_fail else 1)


if __name__ == "__main__":
    main()
