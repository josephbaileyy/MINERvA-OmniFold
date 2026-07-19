#!/usr/bin/env python3
"""Additive exhaustive scalar-domain validator for G2 full-event ROOTs.

WHY THIS EXISTS (additive, does NOT modify the hash-bound
validate_g2_fullevent_smoke.py used by the active production array):
The base structural validator samples only 20,000 background/data rows for its
reco-muon sanity check. Playlist 1D exposed an UPSTREAM-corrupt AnaTuple muon
(one background row: identity (mc_run,mc_subrun,mc_nthEvtInFile)=(111114,296,375),
a ~3.137e10 MeV reco four-vector -> scalar pT~2.96e6 GeV, p_par~3.12e7 GeV). That
is far outside the canonical extended-FPS PET domain (pT<=30, p_par<=120 GeV), so
the downstream publication inventory must REJECT it before training.

This validator, run read-only:
  1. EXHAUSTIVELY (every row, via C++-speed TTree::Draw selection) validates
     scalar reco-domain membership / finiteness / sentinel discipline;
  2. FAILS CLOSED on any corrupt row that could ENTER the extended-FPS domain
     (non-finite live scalar, or a sentinel/missing muon on a selected row);
  3. CENSUSES and BINDS finite out-of-domain rows by tree/index/identity/values,
     proving downstream exclusion instead of silently accepting them;
  4. COMPOSES the base validator's 50 structural checks (all must pass except the
     two 20k-sampled reco-muon-validity checks, which this file SUPERSEDES with an
     exhaustive census); records the base receipt path+sha;
  5. is READ-ONLY: writes only its own receipt path, never the original.

It does NOT publish anything. Use recover_g2_playlist.sh for no-clobber recovery.

Usage:
  python3 validate_g2_fullevent_domain.py <omnifile.root> <domain_receipt.json>
          [--no-structural] [--base-validator PATH]
Exit 0 = PASS (recovery-eligible), 1 = FAIL (fatal corruption), 2 = open/error.
"""
import json
import math
import os
import subprocess
import sys
import tempfile

# ---- Canonical extended-FPS PET domain (fullevent_fps_dataloader CANONICAL_* max edges) ----
PT_MIN, PT_MAX = 0.0, 30.0        # GeV
PPAR_MIN, PPAR_MAX = 0.0, 120.0   # GeV
SENTINEL = -9999.0
MU_COMPONENT_ABS_MAX = 1.0e8       # MeV; loose corruption guard, not a physics cut
# Base-validator checks superseded by this file's exhaustive census (the 20k-sampled
# reco-muon-validity heuristics). Every OTHER base check must still pass.
SUPERSEDED_BASE_CHECKS = {"bkg_reco_muon_valid", "data_reco_muon_valid"}


# ======================= pure, ROOT-free classification (unit-tested) =======================
def is_finite(x):
    try:
        return math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def is_sentinel(x):
    return is_finite(x) and abs(float(x) - SENTINEL) < 1e-3


def in_domain(pt, ppar):
    return (PT_MIN <= pt <= PT_MAX) and (PPAR_MIN <= ppar <= PPAR_MAX)


def classify_scalar_pair(pt, ppar):
    """Return (verdict, fatal, in_domain_bool) for a LIVE reco/data scalar pair.

    - non-finite            -> ('nonfinite', True, False)   # cannot be domain-filtered => fatal
    - finite & in-domain    -> ('ok', False, True)
    - finite & out-of-domain-> ('out_of_domain', False, False)  # censused; downstream excludes
    """
    if not (is_finite(pt) and is_finite(ppar)):
        return ("nonfinite", True, False)
    ind = in_domain(pt, ppar)
    return ("ok", False, True) if ind else ("out_of_domain", False, False)


def selected_reco_row_verdict(pt, ppar):
    """A SELECTED reco row (background, data, pass_reco signal) must carry a real
    muon: a sentinel value means a missing muon on a selected row -> FATAL."""
    if is_sentinel(pt) or is_sentinel(ppar):
        return ("sentinel_on_selected", True, False)
    return classify_scalar_pair(pt, ppar)


def truth_row_verdict(pt, ppar):
    """Truth scalars (step-2). Non-finite is FATAL. Out-of-domain truth is the
    prior-dominated extension tail (informational census), NOT fatal."""
    if not (is_finite(pt) and is_finite(ppar)):
        return ("nonfinite", True, False)
    return ("ok", False, True) if in_domain(pt, ppar) else ("out_of_domain", False, False)


# ============================ ROOT-backed exhaustive scan ============================
def _draw_indices(tree, cut, cap=100000):
    """Return the entry indices satisfying `cut` (C++-speed selection over ALL rows)."""
    n = tree.Draw(">>__el", cut, "goff")
    el = tree.GetDirectory().Get("__el") if hasattr(tree, "GetDirectory") else None
    import ROOT  # noqa
    el = ROOT.gDirectory.Get("__el")
    out = []
    if el:
        m = min(el.GetN(), cap)
        for i in range(m):
            out.append(int(el.GetEntry(i)))
    return int(n), out


def _census_rows(tree, indices, scalar_pt, scalar_pz, id_kind, mu_prefix):
    rows = []
    for idx in indices:
        tree.GetEntry(idx)
        rec = {"index": idx,
               "pt": float(getattr(tree, scalar_pt)),
               "p_par": float(getattr(tree, scalar_pz))}
        if id_kind == "mc":
            rec["identity"] = {"mc_run": int(tree.mc_run), "mc_subrun": int(tree.mc_subrun),
                               "mc_nthEvtInFile": int(tree.mc_nthEvtInFile)}
        elif id_kind == "data":
            rec["identity"] = {"ev_run": int(tree.ev_run), "ev_subrun": int(tree.ev_subrun),
                               "ev_gate": int(tree.ev_gate)}
        if mu_prefix:
            rec["muon4v"] = {c: float(getattr(tree, f"{mu_prefix}{c}"))
                             for c in ("px", "py", "pz", "E")}
        rows.append(rec)
    return rows


def _atomic_json(path, payload):
    """Write one receipt atomically in its destination directory."""
    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, temporary = tempfile.mkstemp(prefix=f".{os.path.basename(path)}.", dir=directory)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _run_base_structural(root, base_receipt, base_validator):
    """Compose the base 50 structural checks by running the hash-bound base
    validator read-only to a NEW receipt path (never the original)."""
    r = {"ran": False, "receipt": base_receipt}
    try:
        p = subprocess.run([sys.executable, base_validator, root, base_receipt, "20000"],
                           capture_output=True, text=True, timeout=7200)
        r["ran"] = True
        r["exit"] = p.returncode
    except Exception as e:  # noqa
        r["error"] = str(e)
        return r
    try:
        d = json.load(open(base_receipt))
    except Exception as e:  # noqa
        r["error"] = f"base receipt unreadable: {e}"
        return r
    r["n_checks"] = d.get("n_checks")
    r["n_failed"] = d.get("n_failed")
    failed = [c["name"] for c in d.get("checks", []) if not c["ok"]]
    r["failed_checks"] = failed
    r["non_superseded_failures"] = [c for c in failed if c not in SUPERSEDED_BASE_CHECKS]
    r["superseded_failures"] = [c for c in failed if c in SUPERSEDED_BASE_CHECKS]
    import hashlib
    r["base_receipt_sha256"] = hashlib.sha256(open(base_receipt, "rb").read()).hexdigest()
    r["base_validator"] = os.path.abspath(base_validator)
    r["base_validator_sha256"] = hashlib.sha256(open(base_validator, "rb").read()).hexdigest()
    return r


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    root = sys.argv[1]
    out = sys.argv[2]
    do_structural = "--no-structural" not in sys.argv
    base_validator = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "validate_g2_fullevent_smoke.py")
    if "--base-validator" in sys.argv:
        base_validator = sys.argv[sys.argv.index("--base-validator") + 1]

    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kWarning
    rep = {"receipt_schema": "g2-domain-validation-v1", "file": root,
           "domain": {"pt_max": PT_MAX, "p_par_max": PPAR_MAX},
           "status": "UNKNOWN", "fatal": [], "census": {}, "checks": []}
    fatal = []

    f = ROOT.TFile.Open(root)
    if not f or f.IsZombie():
        rep["status"] = "FAIL_OPEN"
        _atomic_json(out, rep)
        print(f"FAIL: cannot open {root}")
        return 2

    fin = "TMath::Finite"
    # (tree, pt, pz, id_kind, mu_prefix, sel_cut, context)
    reco_specs = [
        ("mc_background", "sim_background", "sim_background_pz", "mc", "mu_reco_", "", "background"),
        ("data", "measured", "measured_pz", "data", "mu_reco_", "", "data"),
        ("mc_signal_reco", "sim", "sim_pz", "mc", "mu_reco_", "sim_pass==1", "signal_reco_pass"),
    ]
    for tname, pt, pz, idk, mup, selcut, ctx in reco_specs:
        t = f.Get(tname)
        if not t:
            fatal.append(f"{ctx}: tree {tname} missing")
            continue
        base = f"({selcut})&&" if selcut else ""
        # non-finite live scalar OR non-finite muon 4v -> FATAL
        nf_cut = (f"{base}(!{fin}({pt})||!{fin}({pz})||!{fin}({mup}E)||!{fin}({mup}px)"
                  f"||!{fin}({mup}py)||!{fin}({mup}pz))")
        n_nf, idx_nf = _draw_indices(t, nf_cut)
        # sentinel on a SELECTED row (missing muon) -> FATAL
        sent_cut = f"{base}({pt}=={SENTINEL}||{pz}=={SENTINEL})"
        n_sent, idx_sent = _draw_indices(t, sent_cut)
        # Every selected row, including an out-of-domain row, must still carry a
        # finite, non-sentinel reconstructed muon and the MINOS-quality bit.
        bad_mu_cut = (f"{base}({mup}E<=0||TMath::Abs({mup}px)>={MU_COMPONENT_ABS_MAX}"
                      f"||TMath::Abs({mup}py)>={MU_COMPONENT_ABS_MAX}"
                      f"||TMath::Abs({mup}pz)>={MU_COMPONENT_ABS_MAX}"
                      f"||TMath::Abs({mup}E)>={MU_COMPONENT_ABS_MAX}"
                      f"||{mup}px=={SENTINEL}||{mup}py=={SENTINEL}"
                      f"||{mup}pz=={SENTINEL}||{mup}E=={SENTINEL}"
                      f"||mu_reco_minos_ok!=1)")
        n_bad_mu, idx_bad_mu = _draw_indices(t, bad_mu_cut)
        # Inside the retained domain, the dumped beam-frame 4-vector must agree
        # with the scalar coordinates used to construct the inventory.
        ind = (f"{fin}({pt})&&{fin}({pz})&&{pt}>={PT_MIN}&&{pt}<={PT_MAX}"
               f"&&{pz}>={PPAR_MIN}&&{pz}<={PPAR_MAX}")
        mismatch_cut = (f"{base}{ind}&&(TMath::Abs(TMath::Sqrt({mup}px*{mup}px+{mup}py*{mup}py)"
                        f"/1000.-{pt})>1e-6*TMath::Max(1.,TMath::Abs({pt}))"
                        f"||TMath::Abs({mup}pz/1000.-{pz})>1e-6*TMath::Max(1.,TMath::Abs({pz})))")
        n_mismatch, idx_mismatch = _draw_indices(t, mismatch_cut)
        # finite, non-sentinel, OUT-of-domain -> census (downstream excludes)
        ood_cut = (f"{base}{fin}({pt})&&{fin}({pz})&&{pt}!={SENTINEL}&&{pz}!={SENTINEL}"
                   f"&&({pt}<{PT_MIN}||{pt}>{PT_MAX}||{pz}<{PPAR_MIN}||{pz}>{PPAR_MAX})")
        n_ood, idx_ood = _draw_indices(t, ood_cut)
        rep["checks"].append({"tree": tname, "context": ctx, "nonfinite": n_nf,
                              "sentinel_on_selected": n_sent,
                              "invalid_muon_or_minos": n_bad_mu,
                              "in_domain_scalar_muon_mismatch": n_mismatch,
                              "out_of_domain": n_ood})
        if n_nf > 0:
            fatal.append(f"{ctx}: {n_nf} non-finite live reco scalar/muon row(s)")
            rep["census"][f"{ctx}_nonfinite"] = _census_rows(t, idx_nf, pt, pz, idk, mup)
        if n_sent > 0:
            fatal.append(f"{ctx}: {n_sent} sentinel(missing-muon) row(s) on selected sample")
            rep["census"][f"{ctx}_sentinel"] = _census_rows(t, idx_sent, pt, pz, idk, mup)
        if n_bad_mu > 0:
            # Out-of-domain corrupt-but-finite muons are recorded and excluded;
            # an in-domain occurrence is fatal below through the scalar-domain
            # and consistency gates. Keep the complete census either way.
            rep["census"][f"{ctx}_invalid_muon"] = _census_rows(
                t, idx_bad_mu, pt, pz, idk, mup)
            in_domain_bad = sum(in_domain(row["pt"], row["p_par"])
                                for row in rep["census"][f"{ctx}_invalid_muon"])
            if in_domain_bad or n_bad_mu > len(idx_bad_mu):
                fatal.append(f"{ctx}: {in_domain_bad} corrupt muon row(s) inside retained domain")
        if n_mismatch > 0:
            fatal.append(f"{ctx}: {n_mismatch} in-domain scalar/muon mismatch row(s)")
            rep["census"][f"{ctx}_in_domain_mismatch"] = _census_rows(
                t, idx_mismatch, pt, pz, idk, mup)
        if n_ood > 0:
            rep["census"][f"{ctx}_out_of_domain"] = _census_rows(t, idx_ood, pt, pz, idk, mup)
            if n_ood > len(idx_ood):
                fatal.append(
                    f"{ctx}: out-of-domain census truncated ({len(idx_ood)}/{n_ood}); "
                    "receipt would not bind every excluded row")

    # truth scalars: non-finite is FATAL; out-of-domain is the prior tail (informational)
    for tname, pt, pz, mup in [("mc_truth_denom", "MC", "MC_pz", "mu_true_"),
                               ("mc_signal_reco", "MC", "MC_pz", "mu_true_")]:
        t = f.Get(tname)
        if not t:
            fatal.append(f"truth:{tname} missing")
            continue
        nf_cut = (f"!{fin}({pt})||!{fin}({pz})||!{fin}({mup}E)||!{fin}({mup}px)"
                  f"||!{fin}({mup}py)||!{fin}({mup}pz)")
        n_nf, idx_nf = _draw_indices(t, nf_cut)
        ood_cut = (f"{fin}({pt})&&{fin}({pz})&&({pt}<{PT_MIN}||{pt}>{PT_MAX}"
                   f"||{pz}<{PPAR_MIN}||{pz}>{PPAR_MAX})")
        n_ood, _ = _draw_indices(t, ood_cut)
        rep["checks"].append({"tree": tname, "context": "truth", "nonfinite": n_nf,
                              "out_of_domain_informational": n_ood})
        if n_nf > 0:
            fatal.append(f"truth:{tname}: {n_nf} non-finite truth scalar/muon row(s)")
            rep["census"][f"truth_{tname}_nonfinite"] = _census_rows(t, idx_nf, pt, pz, "mc", mup)

    # signal misses must be sentinel (structural cross-check)
    t = f.Get("mc_signal_reco")
    if t:
        n_bad, idx_bad = _draw_indices(t, f"sim_pass==0&&(sim!={SENTINEL}||sim_pz!={SENTINEL})")
        rep["checks"].append({"tree": "mc_signal_reco", "context": "miss_sentinel",
                              "nonsentinel_miss": n_bad})
        if n_bad > 0:
            fatal.append(f"signal misses: {n_bad} !pass_reco row(s) without reco sentinel")
            rep["census"]["miss_nonsentinel"] = _census_rows(t, idx_bad, "sim", "sim_pz", "mc", "mu_reco_")

    # compose base structural checks
    if do_structural:
        rep["structural"] = _run_base_structural(root, out + ".base.json", base_validator)
        s = rep["structural"]
        if not s.get("ran"):
            fatal.append(f"structural base validator did not run: {s.get('error')}")
        elif s.get("error"):
            fatal.append(f"structural base validator error: {s.get('error')}")
        elif s.get("non_superseded_failures"):
            fatal.append(f"structural non-superseded failures: {s['non_superseded_failures']}")

    n_censused = sum(len(v) for k, v in rep["census"].items() if k.endswith("out_of_domain"))
    rep["out_of_domain_censused_and_bound"] = n_censused
    rep["fatal"] = fatal
    rep["status"] = "PASS" if not fatal else "FAIL"
    _atomic_json(out, rep)
    try:
        f.Close()
    except Exception:  # noqa
        pass
    print(json.dumps({"status": rep["status"], "n_fatal": len(fatal),
                      "out_of_domain_censused": n_censused,
                      "structural_non_superseded_failures":
                          rep.get("structural", {}).get("non_superseded_failures")}, indent=2))
    if fatal:
        for x in fatal:
            print("  FATAL:", x)
    return 0 if not fatal else 1


if __name__ == "__main__":
    sys.exit(main())
