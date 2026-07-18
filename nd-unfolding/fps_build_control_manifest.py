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
import fps_verify_merged_receipt as fvm

MASK_ARTIFACT = "active_universe_5d/fps/covariance/fps_reported_mask.json"

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


def recover_footing(log_paths):
    """Recover the PURITY-CONTROL footing from artifacts tied to the ACTUAL control run -- NOT the
    current launcher (which was repaired to the negweight-refined publication config after these
    controls were produced). Evidence: (a) the unfold source default --bkg-mode=purity; (b) all ten
    control unfold LOGS carry the fps/lgbm/5-iter config AND announce NO negweight bkg-mode (the
    purity down-weight path); (c) the stable launcher footing tokens (seed 42 / use-weights /
    estimator / iters / full-phase-space) which are unchanged across the negweight patch.
    Fail-closed EVIDENCE-BLOCKED on any inconsistency."""
    ev = {"unfold_source": {}, "logs": {}, "launchers": {}}
    if not os.path.exists(UNFOLD_SRC):
        die_evidence_blocked(f"unfold source {UNFOLD_SRC} absent")
    src = open(UNFOLD_SRC).read()
    m = re.search(r'add_argument\(\s*"--bkg-mode".*?default\s*=\s*"([^"]+)"', src, re.S)
    if not m:
        die_evidence_blocked("cannot parse --bkg-mode default from unfold source")
    src_default_mode = m.group(1)
    ev["unfold_source"] = {"path": UNFOLD_SRC, "sha256": fp.sha256_file(UNFOLD_SRC),
                           "bkg_mode_default": src_default_mode}
    if src_default_mode != fp.CONTROL_BKG_MODE:
        die_evidence_blocked(f"unfold default bkg-mode '{src_default_mode}' != '{fp.CONTROL_BKG_MODE}'")

    # (b) control logs: no negweight announcement + fps/lgbm/5-iter config present
    for lg in log_paths:
        if not os.path.exists(lg):
            die_evidence_blocked(f"control log absent: {lg}")
        txt = open(lg, errors="replace").read()
        if re.search(r"bkg-mode\s*=\s*negweight", txt):
            die_evidence_blocked(f"control log {os.path.basename(lg)} announces negweight (not purity)")
        for needle in ("estimator=lgbm", "OmniFold 5 iters", "FULL PHASE SPACE"):
            if needle not in txt:
                die_evidence_blocked(f"control log {os.path.basename(lg)} missing evidence '{needle}'")
        ev["logs"][os.path.basename(lg)] = fp.sha256_file(lg)

    # (c) stable launcher footing tokens (unchanged across the negweight patch)
    stable = ["--seed 42", "--use-weights", "--estimator lgbm", "--iters 5", "--full-phase-space"]
    proven = set()
    for L in LAUNCHERS:
        if not os.path.exists(L):
            continue
        flat = re.sub(r"\s+", " ", re.sub(r"\\\s*\n", " ", open(L).read()))
        ev["launchers"][L] = {"sha256": fp.sha256_file(L),
                              "note": "current post-repair launcher; used only for stable footing tokens"}
        for tok in stable:
            if tok in flat:
                proven.add(tok)
    missing = [t for t in stable if t not in proven]
    if missing:
        die_evidence_blocked(f"cannot prove stable footing tokens {missing} from any launcher")

    footing = dict(fp.REQUIRED_FOOTING)
    footing["bkg_mode"] = fp.CONTROL_BKG_MODE   # purity: source default + no-negweight in all ten logs
    return footing, ev


def main():
    os.chdir(ND)
    log_paths = [os.path.join(UNFOLD_DIR, LOG_NAME.format(b=b, ep=ep))
                 for b in fp.BANDS for ep in fp.ENDPOINTS]
    footing, evidence = recover_footing(log_paths)
    print(f"[evidence] recovered footing bkg_mode={footing['bkg_mode']} "
          f"(source default + {len(evidence['logs'])}/10 control logs carry no negweight announcement)")

    if not os.path.exists(CV):
        die_evidence_blocked(f"central CV {CV} absent")
    cv_sha = fp.sha256_file(CV)
    # reported mask is now COMMITTED + canonical (no deferred field): bind the exact 266/285 fingerprint
    if not os.path.exists(MASK_ARTIFACT):
        die_evidence_blocked(f"reported-mask artifact absent: {MASK_ARTIFACT} (run sbatch_fps_mask.sh)")
    mask_art = json.load(open(MASK_ARTIFACT))
    if mask_art.get("fingerprint") != fp.REPORTED_MASK_FINGERPRINT:
        die_evidence_blocked("reported-mask artifact fingerprint != canonical REPORTED_MASK_FINGERPRINT")
    if mask_art.get("central_cv_sha256") != cv_sha:
        die_evidence_blocked("reported-mask artifact central_cv_sha256 != current CV sha256")
    reported_mask_hash = fp.REPORTED_MASK_FINGERPRINT
    central_hash = cv_sha
    lay = fp.layout_fingerprint()
    # full merged-input SHA256 from the validated orchestrator receipt (no partial head/tail)
    receipt = fvm.verify()
    input_hashes = receipt["verified_input_sha256"]         # abs_path -> full sha256

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
            abs_mp = os.path.abspath(mp)
            if abs_mp not in input_hashes:
                die_evidence_blocked(f"merged input {mp} not in validated receipt hash set")
            endpoints.append({
                "band": b, "endpoint": ep,
                "unfold_root": up, "unfold_sha256": fp.sha256_file(up),   # full hash (26KB output)
                "input_merged_root": mp,
                "input_merged_sha256": input_hashes[abs_mp],             # FULL, from validated receipt
                "input_merged_bytes": os.path.getsize(mp),
                "unfold_log": lg, "unfold_log_sha256": log_sha,
                "layout_fingerprint": lay,
                "reported_mask_hash": reported_mask_hash,
                "central_hash": central_hash,
                "footing": dict(footing),
            })
            print(f"[hash] {b}_{ep} unfold + full-input(receipt) bound")

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
        "reported_mask_artifact": MASK_ARTIFACT,
        "reported_mask_artifact_sha256": fp.sha256_file(MASK_ARTIFACT),
        "n_reported": mask_art["n_reported"],
        "footing": dict(footing),
        "evidence": evidence,
        "audit_receipt": AUDIT_JSON if os.path.exists(AUDIT_JSON) else None,
        "audit_receipt_sha256": fp.sha256_file(AUDIT_JSON) if os.path.exists(AUDIT_JSON) else None,
        "merged_input_receipt": receipt["receipt_dir"],
        "merged_input_receipt_run_id": receipt["run_id"],
        "merged_input_fps_hash_list_sha256": receipt["fps_hash_list_sha256"],
        "merged_input_fps_inventory_sha256": receipt["fps_inventory_sha256"],
        "residual_evidence_gaps": [],
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
              f"input={e['input_merged_sha256'][:12]} bkg={e['footing']['bkg_mode']}")


if __name__ == "__main__":
    main()
