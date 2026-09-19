#!/bin/bash
# CAUSE 7's `M` -- THE LATERAL COUNTERFACTUAL, on Z's OWN inputs. `SPEC` §2.7.
#
# WHY THIS RUNS. §2.7 defines cause 7's M as `Σ_A L_active` against `Σ_A L_support` over
# `p4_lib.BANDS`, on Z's own inputs, and says "Z's receipt reports both, each labelled with what it
# is a difference of." Measured: Z's receipt contains NO `L_support`, `L_active`,
# `support_comparison` or `lateral_counterfactual`. M was never recorded. It is required receipt
# content under any reading of the gate, so this is EVIDENCE, not a decision.
#
# ⚠ PROHIBITED, VERBATIM FROM §2.7 AND ENFORCED BELOW: S's `support_comparison` ratio
# 0.9997122662137712, and F's +10.96% (VL69-VL71), MUST NOT be cited as Z's M, nor as a reason M
# need not be measured. They are other products' numbers. The script refuses to emit them.
#
# ⚠ NOT `C_Z - C_G`. §2.7 says that difference contains six other causes' movement.
set -uo pipefail
W="${MNV_W:?}"; D="${MNV_D:?}"
OUT="$D/cause7_M"; mkdir -p "$OUT"
source "$W/setup_salloc_env.sh" >/dev/null 2>&1 || true
cd "$W/nd-unfolding"
~/.conda/envs/root_6_28/bin/python3 - <<'PYEOF' 2>&1 | tee "$OUT/cause7_M.txt"
import sys, json, math
sys.path.insert(0, ".")
import ROOT; ROOT.gROOT.SetBatch(True)
import p4_lib

P = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5"
OUTJ = "/pscratch/sd/j/josephrb/zdet-DIAGNOSTIC-20260918/cause7_M/cause7_M.json"
m = json.load(open(P + "/z-manifest.json"))
SUP = m["sources"]["support"]["path"]
ACT = m["sources"]["active"]["path"]
BANDS = list(p4_lib.BANDS)
print("[M] SPEC 2.7 lateral counterfactual, Z's own inputs")
print("[M] bands (p4_lib.BANDS):", BANDS)
print("[M] support:", SUP)
print("[M] active :", ACT)

# ---- (ii) "Z's OWN inputs" is SHOWN, not asserted -----------------------------------------------
# A matching row in SPEC 1.1's table is a claim about S. What makes these Z's inputs is a matching
# entry in Z's OWN record. 2.7 says each donated band is re-digested into Z's receipt, so the
# binding level actually available is reported rather than assumed.
import hashlib
def sha256_file(fn):
    h = hashlib.sha256()
    with open(fn, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()

rec = json.load(open(P + "/z-receipt-cv.json"))
rec_blob = json.dumps(rec)
measured_act = sha256_file(ACT)
declared_act = m["sources"]["active"]["sha256"]
print(f"[M] active sha256 MEASURED  = {measured_act}")
print(f"[M] active sha256 in Z manifest = {declared_act}")
if measured_act != declared_act:
    raise SystemExit("[FAIL] the active source on disk is NOT the file Z's manifest records. "
                     "This is not Z's input.")
in_receipt = measured_act in rec_blob
per_band = {b: (f"hCov_active5d_{b}" in rec_blob) for b in BANDS}
n_band = sum(per_band.values())
print(f"[M] BINDING LEVEL: file digest present in Z's receipt = {in_receipt}; "
      f"per-band active keys named in Z's receipt = {n_band}/5")
print("[M] -> binding is " + ("PER-BAND plus file digest" if n_band == 5 and in_receipt
                              else "FILE-DIGEST ONLY" if in_receipt
                              else "MANIFEST ONLY -- weaker than 2.7 describes; recorded as such"))

def diag_of(fname, key):
    """Trace only. tr(sum) = sum(tr), so the SUMMED matrices are never formed -- 5 x 915 MB each."""
    f = ROOT.TFile.Open(fname)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {fname}")
    h = f.Get(key)
    if not h:
        keys = [k.GetName() for k in f.GetListOfKeys()]
        hits = [k for k in keys if any(b in k for b in BANDS)]
        raise SystemExit(f"[FAIL] key {key!r} absent from {fname}. Band-matching keys present: "
                         f"{hits[:8]} (of {len(keys)} total)")
    n = h.GetNbinsX()
    if n != h.GetNbinsY():
        raise SystemExit(f"[FAIL] {key} is {n}x{h.GetNbinsY()}, not square")
    d = [h.GetBinContent(i, i) for i in range(1, n + 1)]
    f.Close()
    return d, n

res = {"support": {}, "active": {}}
diags = {}
for fam, fname, keyfn in (("support", SUP, lambda b: f"hCov_universe5d_{b}"),
                          ("active",  ACT, p4_lib.candidate_band_key)):
    for b in BANDS:
        k = keyfn(b)
        d, n = diag_of(fname, k)
        res[fam][b] = math.fsum(d)
        diags.setdefault(fam, []).append(d)
        print(f"[M] {fam:8s} {b:22s} {k:34s} n={n}  trace={math.fsum(d):.6e}")

tr_sup = math.fsum(res["support"].values())
tr_act = math.fsum(res["active"].values())
s_sup, s_act = math.sqrt(max(tr_sup, 0.0)), math.sqrt(max(tr_act, 0.0))
print()
print("[M] ===== CAUSE 7 M, THE LATERAL COUNTERFACTUAL =====")
print(f"[M] sqrt_tr( sum_A L_support ) = {s_sup:.10e}")
print(f"[M] sqrt_tr( sum_A L_active  ) = {s_act:.10e}")
print(f"[M] ratio active/support       = {(s_act/s_sup if s_sup else float('nan')):.10f}")
print(f"[M] relative movement          = {(100*(s_act/s_sup-1) if s_sup else float('nan')):+.4f}%")
print("[M] LABEL: this is a difference of the FIVE-BAND LATERAL BLOCK between the ACTIVE and")
print("[M]        SUPPORT families on Z's own inputs. It is NOT C_Z - C_G, which SPEC 2.7 says")
print("[M]        carries six other causes' movement.")
# ---- (i) PER-BIN, because a sqrt-trace-only M reports exactly the summary 2.7 shows can hide
# per-bin movement: it contrasts S's -0.0288% trace move with F's per-bin sigma ratio running
# 0.7897 to 1.4402 -- different in sign and by two orders. The diagonals are already read.
import numpy as np
ds = np.array([math.fsum(c) for c in zip(*diags["support"])])
da = np.array([math.fsum(c) for c in zip(*diags["active"])])
ok = ds > 0
ratio = np.sqrt(np.divide(da, ds, out=np.zeros_like(da), where=ok))[ok]
print()
print("[M] ----- PER-BIN sigma ratio sqrt(diag_active / diag_support) -----")
print(f"[M] bins with diag_support > 0 : {int(ok.sum())} of {ds.size}")
print(f"[M] min / median / max         : {ratio.min():.6f} / {float(np.median(ratio)):.6f} / {ratio.max():.6f}")
_am = int(np.argmax(ratio))
print(f"[M] argmax bin (index within positive-support set) = {_am}, ratio {ratio.max():.6f}")
print("[M] ⚠ M IS CORRELATION-BLIND. It is built from traces and diagonals only, so it cannot see")
print("[M]   off-diagonal structure (SPEC 3.7d). `s_proj` is NOT computed for it and must not be")
print("[M]   inferred from it; the blindness is named rather than papered over.")
np.savez(OUTJ.replace(".json", "_diagonals.npz"), diag_support=ds, diag_active=da,
         bands=np.array(BANDS))
print("[M] persisted both diagonal vectors (10694 floats each) -- any later statistic needs no rerun")

FORBIDDEN = ("0.9997122662137712", "0.9997122662", "10.96")
blob = json.dumps(res)
for t in FORBIDDEN:
    if t in blob:
        raise SystemExit(f"[FAIL] a prohibited other-product constant {t} appeared in Z's own M output")
print("[M] prohibition check: none of S's ratio or F's +10.96% appears in this measurement.")
json.dump({"per_bin_sigma_ratio": {"min": float(ratio.min()), "median": float(np.median(ratio)),
                                   "max": float(ratio.max()), "n_bins": int(ok.sum())},
           "correlation_blind": "M is trace/diagonal only; s_proj not computed (SPEC 3.7d)",
           "active_binding_level": ("per-band+digest" if n_band == 5 and in_receipt
                                    else "file-digest" if in_receipt else "manifest-only"),
           "bands": BANDS, "per_band": res, "sqrt_tr_support": s_sup, "sqrt_tr_active": s_act,
           "ratio_active_over_support": (s_act/s_sup if s_sup else None),
           "label": "SPEC 2.7 lateral counterfactual on Z's own inputs; not C_Z - C_G"},
          open(OUTJ, "w"), indent=2)
print("[M] wrote cause7_M.json")
PYEOF
