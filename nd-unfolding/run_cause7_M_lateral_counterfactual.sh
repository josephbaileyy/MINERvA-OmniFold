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
m = json.load(open(P + "/z-manifest.json"))
SUP = m["sources"]["support"]["path"]
ACT = m["sources"]["active"]["path"]
BANDS = list(p4_lib.BANDS)
print("[M] SPEC 2.7 lateral counterfactual, Z's own inputs")
print("[M] bands (p4_lib.BANDS):", BANDS)
print("[M] support:", SUP)
print("[M] active :", ACT)

def trace_of(fname, key):
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
    t = math.fsum(h.GetBinContent(i, i) for i in range(1, n + 1))
    f.Close()
    return t, n

res = {"support": {}, "active": {}}
for fam, fname, keyfn in (("support", SUP, lambda b: f"hCov_universe5d_{b}"),
                          ("active",  ACT, p4_lib.candidate_band_key)):
    for b in BANDS:
        k = keyfn(b)
        t, n = trace_of(fname, k)
        res[fam][b] = t
        print(f"[M] {fam:8s} {b:22s} {k:34s} n={n}  trace={t:.6e}")

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
FORBIDDEN = ("0.9997122662137712", "0.9997122662", "10.96")
blob = json.dumps(res)
for t in FORBIDDEN:
    if t in blob:
        raise SystemExit(f"[FAIL] a prohibited other-product constant {t} appeared in Z's own M output")
print("[M] prohibition check: none of S's ratio or F's +10.96% appears in this measurement.")
json.dump({"bands": BANDS, "per_band": res, "sqrt_tr_support": s_sup, "sqrt_tr_active": s_act,
           "ratio_active_over_support": (s_act/s_sup if s_sup else None),
           "label": "SPEC 2.7 lateral counterfactual on Z's own inputs; not C_Z - C_G"},
          open("/pscratch/sd/j/josephrb/zdet-DIAGNOSTIC-20260918/cause7_M/cause7_M.json", "w"), indent=2)
print("[M] wrote cause7_M.json")
PYEOF
