#!/usr/bin/env python3
"""Blocker 1 (Agent C, fail-closed repair round): build a READ-ONLY provenance manifest for the ten
EXISTING FPS endpoint unfolds and truthfully label them 'purity-control'. ROOT-FREE: evidence is
recovered only from durable launcher/log/source artifacts + file SHA256s; the background mode is
NEVER inferred as negweight-refined -- it is read from what the launchers actually ran.

For each of the 5 bands x {0,1} it binds: unfold ROOT sha256, input merged-endpoint sha256, the
15x19 extended edges / C-order / 285-bin layout fingerprint, the common central-CV sha256 (the
durable object that determines the 285->266 reported mask; the exact mask hash is (re)computed with
ROOT at publication-rollup time and must match), and the execution footing (lgbm / seed 42 / 5 iters
/ weights / full-phase-space / bkg_mode). bkg_mode is proven from: (a) the launcher invocation omits
--bkg-mode AND (b) the unfold source default is 'purity'. If any footing token cannot be proven from
a durable artifact -> exit EVIDENCE-BLOCKED (no manifest written).

The publication manifest/validator (fps_provenance.require_publication_manifest) REQUIRES
bkg_mode=negweight-refined and therefore rejects this control manifest -- verified here.

  python fps_build_control_manifest.py            # writes active_universe_5d/fps/covariance/fps_control_manifest.json
"""
import json
import os
import re
import sys

import fps_provenance as fp

ND = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
UNFOLD_DIR = "active_universe_5d/fps/unfolds"
MERGE_DIR = "active_universe_5d/fps/merged"
CV = "uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
UNFOLD_NAME = "fps2d_xsec_MEFHC_5iter_lgbm_uni_full_{b}_{ep}.root"
MERGE_NAME = "runEventLoopOmniFold_5D_FPS_active_{b}_{ep}_universes_full.root"
LOG_NAME = "unfold_{b}_{ep}.log"
LAUNCHERS = ["sbatch_unfold_active_fps.sh", "run_active_fps_unfolds_interactive.sh"]
UNFOLD_SRC = "unfold_nd_omnifold_unbinned.py"
AUDIT_JSON = "active_universe_5d/fps/covariance/audit_merged_fps.json"
OUT = "active_universe_5d/fps/covariance/fps_control_manifest.json"


def die_evidence_blocked(msg):
    print(f"\nEVIDENCE-BLOCKED :: {msg}", file=sys.stderr)
    sys.exit(3)


def recover_footing():
    """Prove the footing tokens from durable launcher + unfold-source artifacts. Returns
    (footing dict, evidence dict). Fail-closed: any unprovable token -> EVIDENCE-BLOCKED."""
    ev = {"launchers": {}, "unfold_source": {}}
    # unfold source: parse the --bkg-mode default
    if not os.path.exists(UNFOLD_SRC):
        die_evidence_blocked(f"unfold source {UNFOLD_SRC} absent")
    src = open(UNFOLD_SRC).read()
    m = re.search(r'add_argument\(\s*"--bkg-mode".*?default\s*=\s*"([^"]+)"', src, re.S)
    if not m:
        die_evidence_blocked("cannot parse --bkg-mode default from unfold source")
    src_default_mode = m.group(1)
    ev["unfold_source"] = {"path": UNFOLD_SRC, "sha256": fp.sha256_file(UNFOLD_SRC),
                           "bkg_mode_default": src_default_mode}

    # launchers: each must invoke the unfold; record whether it passes --bkg-mode; confirm the
    # fixed footing tokens are present; fail closed if a launcher is ambiguous.
    modes_seen = set()
    tokens_required = ["--estimator lgbm", "--seed 42", "--iters 5",
                       "--use-weights", "--full-phase-space"]
    for L in LAUNCHERS:
        if not os.path.exists(L):
            die_evidence_blocked(f"launcher {L} absent")
        txt = open(L).read()
        if "unfold_nd_omnifold_unbinned.py" not in txt:
            die_evidence_blocked(f"launcher {L} does not invoke the unfold")
        # collapse line-continuations/whitespace for token matching
        flat = re.sub(r"\\\s*\n", " ", txt)
        flat = re.sub(r"\s+", " ", flat)
        missing = [t for t in tokens_required if t not in flat]
        if missing:
            die_evidence_blocked(f"launcher {L}: cannot prove footing tokens {missing}")
        bkg = re.search(r"--bkg-mode\s+(\S+)", flat)
        mode = bkg.group(1) if bkg else src_default_mode  # omitted -> unfold default
        modes_seen.add(mode)
        ev["launchers"][L] = {"sha256": fp.sha256_file(L),
                              "passes_bkg_mode": bool(bkg),
                              "resolved_bkg_mode": mode}
    if len(modes_seen) != 1:
        die_evidence_blocked(f"launchers disagree on bkg_mode: {sorted(modes_seen)}")
    bkg_mode = modes_seen.pop()
    footing = dict(fp.REQUIRED_FOOTING)
    footing["bkg_mode"] = bkg_mode
    return footing, ev


def main():
    os.chdir(ND)
    footing, evidence = recover_footing()
    print(f"[evidence] recovered footing bkg_mode={footing['bkg_mode']} "
          f"(launchers omit --bkg-mode: "
          f"{all(not v['passes_bkg_mode'] for v in evidence['launchers'].values())})")

    # durable central binding (ROOT-free): the CV file hash determines the 285->266 reported mask.
    if not os.path.exists(CV):
        die_evidence_blocked(f"central CV {CV} absent")
    cv_sha = fp.sha256_file(CV)
    reported_mask_hash = f"DEFERRED-requires-ROOT:cv_sha256={cv_sha}"
    central_hash = cv_sha
    lay = fp.layout_fingerprint()

    endpoints = []
    for b in fp.BANDS:
        for ep in fp.ENDPOINTS:
            up = os.path.join(UNFOLD_DIR, UNFOLD_NAME.format(b=b, ep=ep))
            mp = os.path.join(MERGE_DIR, MERGE_NAME.format(b=b, ep=ep))
            lg = os.path.join(UNFOLD_DIR, LOG_NAME.format(b=b, ep=ep))
            if not os.path.exists(up):
                die_evidence_blocked(f"control unfold missing: {up}")
            if not os.path.exists(mp):
                die_evidence_blocked(f"input merged endpoint missing: {mp}")
            log_sha = fp.sha256_file(lg) if os.path.exists(lg) else None
            # negative evidence: a purity log must NOT announce a negweight bkg-mode
            if log_sha and footing["bkg_mode"] == fp.CONTROL_BKG_MODE:
                if re.search(r"bkg-mode=negweight", open(lg).read()):
                    die_evidence_blocked(
                        f"log {lg} announces negweight bkg-mode but footing says purity")
            endpoints.append({
                "band": b, "endpoint": ep,
                "unfold_root": up, "unfold_sha256": fp.sha256_file(up),   # full hash (26KB output)
                "input_merged_root": mp,
                "input_merged_partial_sha256": fp.sha256_partial(mp),     # bounded (74GB input)
                "input_merged_bytes": os.path.getsize(mp),
                "unfold_log": lg, "unfold_log_sha256": log_sha,
                "layout_fingerprint": lay,
                "reported_mask_hash": reported_mask_hash,
                "central_hash": central_hash,
                "footing": dict(footing),
            })
            print(f"[hash] {b}_{ep} unfold+partial-input done")

    manifest = {
        "schema": "fps_endpoint_manifest.v1",
        "label": "purity-control",
        "readonly": True,
        "purpose": ("read-only provenance of the ten EXISTING FPS endpoint unfolds; these ran with "
                    "the unfold default --bkg-mode=purity and are PURITY CONTROLS, NOT publication "
                    "inputs. Publication requires bkg_mode=negweight-refined and rejects this file."),
        "nbins_extended": fp.NBINS_EXT, "npt": fp.NPT, "npz": fp.NPZ, "ravel_order": fp.RAVEL_ORDER,
        "pt_edges": fp.PT_EDGES, "pz_edges": fp.PZ_EDGES,
        "layout_fingerprint": lay,
        "reported_mask_hash": reported_mask_hash,
        "central_hash": central_hash,
        "central_cv": CV, "central_cv_sha256": cv_sha,
        "footing": dict(footing),
        "evidence": evidence,
        "audit_receipt": AUDIT_JSON if os.path.exists(AUDIT_JSON) else None,
        "audit_receipt_sha256": fp.sha256_file(AUDIT_JSON) if os.path.exists(AUDIT_JSON) else None,
        "residual_evidence_gaps": [
            "input_merged_*: bounded partial-headtail fingerprint only (full SHA256 of the ten "
            "~74GB merged inputs = 740GB login-node I/O, deferred to a compute node); full input "
            "identity corroborated by audit_receipt (trees/POT/census/identity, content-derived).",
            "reported_mask_hash: DEFERRED (285->266 CV>0 mask requires ROOT); bound here via the "
            "central_cv_sha256 and (re)computed + checked at publication-rollup time.",
        ],
        "endpoints": endpoints,
    }

    # fail-closed self-checks
    fp.require_manifest_inventory(manifest)
    fp.require_common_fingerprints(manifest)
    fp.require_footing(manifest, required_bkg_mode=None)
    cls = fp.classify_manifest(manifest)
    if cls != "purity-control":
        die_evidence_blocked(f"manifest classified {cls}, expected purity-control")
    # the publication gate MUST reject this control manifest
    rejected = False
    try:
        fp.require_publication_manifest(manifest)
    except fp.FpsGateError:
        rejected = True
    if not rejected:
        die_evidence_blocked("publication gate did NOT reject the purity-control manifest")
    manifest["publication_gate_rejects_this"] = True

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if os.path.exists(OUT):
        os.chmod(OUT, 0o644)
    with open(OUT, "w") as f:
        json.dump(manifest, f, indent=2)
    os.chmod(OUT, 0o444)  # read-only receipt
    print(f"[manifest] wrote {OUT} (read-only)  label={manifest['label']}")
    print(f"[manifest] 10/10 endpoints bound; layout={lay[:16]}...  cv_sha={cv_sha[:16]}...")
    print(f"[manifest] classify={cls}; publication gate rejects this control = "
          f"{manifest['publication_gate_rejects_this']}")
    for e in endpoints:
        print(f"   {e['band']}_{e['endpoint']}: unfold={e['unfold_sha256'][:12]} "
              f"input(partial)={e['input_merged_partial_sha256'][-12:]} bkg={e['footing']['bkg_mode']}")


if __name__ == "__main__":
    main()
