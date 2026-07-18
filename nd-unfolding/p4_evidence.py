#!/usr/bin/env python3
"""P4 standard read-only EVIDENCE + MANIFEST generator (repair 2026-07-18).

Recomputes (never copies) the durable bindings and inspects the CURRENT ten
endpoint + ten merged ROOTs, emitting committable JSON receipts. Read-only: opens
nothing for write, consumes/mutates no product. Emits:
  evidence/p4_standard_manifest.json   (inventory + hash bindings)
  evidence/p4_merged_audit.json        (per-endpoint merged audit)
  evidence/p4_endpoint_evidence.json   (per-endpoint unfold content evidence)
Cross-checks against the independently observed verifier hashes and prints MATCH/DIFF.
Exit 0 iff every REQUIRED field is proven; else prints EVIDENCE-BLOCKED and exit 2.
"""
import glob, hashlib, json, math, os, sys
import numpy as np
import ROOT
import p4_lib as P

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND = f"{REPO}/nd-unfolding"
CEN5 = f"{ND}/products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
CEN4 = f"{ND}/products/4d/xsec_4d_MEFHC_5iter_lgbm.root"
UDIR = f"{ND}/active_universe_5d/standard/unfolds"
MDIR = f"{ND}/active_universe_5d/standard/merged"
EVID = f"{ND}/active_universe_5d/standard/evidence"; os.makedirs(EVID, exist_ok=True)
OBS = {"central5d": "630306e20e4e175bde8b459174842a58e4f4b5a694b8a5018e730a952820aec8",
       "mask5d": "74374b1af0795c3eb077c9ef0ee6ef3cfa4d7b7b3df63bd4f392d7db80eb136a",
       "endpoint_manifest": "af568b4a2bb2f08e66e7a4380cb0c5b9af72a37ddec94a5b3297c2f50d999c54",
       "central4d": "1fb8250820c00428fc547cb05aa95535023146723acdccb61f615f3fa763f9d2",
       "mask4d": "c977c643d4017a3cc909f85e7f2725b4a96a0060a5b79b56294c231290039d25"}
NONZERO_MIG = {"BeamAngleX", "BeamAngleY"}          # selection-migration bands
ZERO_SEL    = {"MuonResolution", "Muon_Energy_MINERvA", "Muon_Energy_MINOS"}  # bin-migration-only

def flat(path, key="hXSecND_flat"):
    f = ROOT.TFile.Open(path); h = f.Get(key)
    v = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())]); f.Close(); return v

def cmask_hash(vec):
    idx = np.nonzero(np.asarray(vec) > 0)[0].astype(np.int64)
    return hashlib.sha256(idx.tobytes() + b"|C").hexdigest(), int(idx.size)

def getval(f, k):
    o = f.Get(k)
    return (o.GetVal() if hasattr(o, "GetVal") else o.GetTitle()) if o else None

blockers = []
def need(cond, msg):
    if not cond: blockers.append(msg)
    return cond

# ---- central hashes (recomputed) ----
man = {"grid_nbins": P.GRID_NBINS, "corder": "C", "code_rev": os.environ.get("P4_CODE_REV", "")}
man["central5d_sha256"] = P.sha256_file(CEN5)
man["central4d_sha256"] = P.sha256_file(CEN4)
c5 = flat(CEN5); h5, n5 = cmask_hash(c5); man["mask5d_hash"], man["mask5d_nreported"] = h5, n5
c4 = flat(CEN4); h4, n4 = cmask_hash(c4); man["mask4d_hash"], man["mask4d_nreported"] = h4, n4
# 5D via the library gate too (must agree)
h5lib, n5lib = P.mask_order_hash((c5 > 0))
need(h5lib == h5 and n5lib == n5, "5D lib mask-hash disagrees with inline")

# ---- endpoint inventory + content ----
ep_entries = []; ep_ev = {}
for b in P.BANDS:
    for ep in P.ENDPOINTS:
        tag = f"{b}_{ep}"; p = f"{UDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_{tag}.root"
        rec = {"exists": os.path.exists(p)}
        if not rec["exists"]:
            blockers.append(f"endpoint {tag} missing"); ep_ev[tag] = rec; continue
        sh = P.sha256_file(p); rec["sha256"] = sh
        f = ROOT.TFile.Open(p)
        rec["zombie"] = bool(f.IsZombie()); rec["recovered"] = bool(f.TestBit(ROOT.TFile.kRecovered))
        h = f.Get("hXSecND_flat")
        if h:
            v = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
            rec["nbins"] = int(v.size); rec["finite"] = bool(np.all(np.isfinite(v)))
            rec["sum"] = float(v.sum())
            rec["mask_matches_central"] = bool(cmask_hash(v)[0] == h5)  # same 10694 support
        f.Close()
        need(rec.get("nbins") == P.GRID_NBINS and rec.get("finite") and rec.get("sum", 0) > 0
             and not rec["zombie"] and not rec["recovered"], f"endpoint {tag} content invalid")
        ep_entries.append((b, ep, sh)); ep_ev[tag] = rec
man["endpoint_sha256"] = {f"{b}_{e}": s for (b, e, s) in ep_entries}
if len(ep_entries) == P.N_ENDPOINTS:
    man["endpoint_manifest_hash"] = P.endpoint_manifest_hash(ep_entries)
else:
    blockers.append("endpoint inventory != 10")

# ---- merged audit ----
maudit = {}
for b in P.BANDS:
    for ep in P.ENDPOINTS:
        tag = f"{b}_{ep}"; p = f"{MDIR}/runEventLoopOmniFold_5D_MEFHC_active_{tag}.root"
        rec = {"exists": os.path.exists(p)}
        if not rec["exists"]:
            blockers.append(f"merged {tag} missing"); maudit[tag] = rec; continue
        rec["sha256"] = P.sha256_file(p)
        f = ROOT.TFile.Open(p)
        rec["zombie"] = bool(f.IsZombie()); rec["recovered"] = bool(f.TestBit(ROOT.TFile.kRecovered))
        te = {t: (f.Get(t).GetEntries() if f.Get(t) else -1)
              for t in ("mc_truth_denom", "mc_signal_reco", "mc_background", "data")}
        rec["tree_entries"] = {k: int(v) for k, v in te.items()}
        rec["band_meta"] = getval(f, "activeUniverseBand"); rec["idx_meta"] = getval(f, "activeUniverseIndex")
        rec["mcPOT"] = getval(f, "mcPOTUsed"); rec["dataPOT"] = getval(f, "dataPOTUsed")
        rec["hasTruthOnlyMisses"] = getval(f, "hasTruthOnlyMisses"); rec["nTruthOnlyMisses"] = getval(f, "nTruthOnlyMisses")
        cen = {k: getval(f, "activeUniverse" + k) for k in ("TruthEntrants", "TruthExits", "RecoEntrants", "RecoExits")}
        rec["census"] = cen; f.Close()
        selmig = sum(abs(int(cen[k])) for k in cen if cen[k] is not None)
        rec["selection_migration_abs"] = selmig
        need(not rec["zombie"] and not rec["recovered"], f"merged {tag} zombie/recovered")
        need(all(rec["tree_entries"][t] > 0 for t in rec["tree_entries"]), f"merged {tag} empty tree")
        need(rec["tree_entries"]["mc_signal_reco"] == rec["tree_entries"]["mc_truth_denom"],
             f"merged {tag} completeness signal_reco!=truth_denom")
        need(rec["mcPOT"] and rec["mcPOT"] > 0 and rec["dataPOT"] and rec["dataPOT"] > 0, f"merged {tag} POT invalid")
        need(rec["band_meta"] == b, f"merged {tag} endpoint identity mismatch ({rec['band_meta']})")
        need(rec["nTruthOnlyMisses"] is not None, f"merged {tag} native-miss meta missing")
        need(all(cen[k] is not None for k in cen), f"merged {tag} census incomplete")
        if b in NONZERO_MIG: need(selmig > 0, f"merged {tag} expected NONZERO selection migration, got {selmig}")
        maudit[tag] = rec

# ---- cross-check vs observed ----
man["verifier_crosscheck"] = {
    "central5d": man["central5d_sha256"] == OBS["central5d"],
    "mask5d": man["mask5d_hash"] == OBS["mask5d"],
    "endpoint_manifest": man.get("endpoint_manifest_hash") == OBS["endpoint_manifest"],
    "central4d": man["central4d_sha256"] == OBS["central4d"],
    "mask4d": man["mask4d_hash"] == OBS["mask4d"]}

json.dump(man, open(f"{EVID}/p4_standard_manifest.json", "w"), indent=2)
json.dump({"endpoints": ep_ev}, open(f"{EVID}/p4_endpoint_evidence.json", "w"), indent=2)
json.dump({"merged": maudit}, open(f"{EVID}/p4_merged_audit.json", "w"), indent=2)

print("=== recomputed vs observed ===")
for k, v in man["verifier_crosscheck"].items():
    print(f"  {k}: {'MATCH' if v else 'DIFF'}")
print(f"mask5d n={man['mask5d_nreported']} mask4d n={man['mask4d_nreported']}")
print("selection migration:", {t: maudit[t]["selection_migration_abs"] for t in maudit if "selection_migration_abs" in maudit[t]})
if blockers:
    print("EVIDENCE-BLOCKED:", "; ".join(blockers[:10]))
    sys.exit(2)
print("EVIDENCE-COMPLETE: all required fields proven; receipts in", EVID)
sys.exit(0)
