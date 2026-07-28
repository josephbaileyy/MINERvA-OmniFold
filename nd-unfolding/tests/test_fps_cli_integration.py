#!/usr/bin/env python3
"""Blocker 5 (Agent C, repair-3): REAL CLI integration negatives. Each case subprocess-invokes an
actual chain script with crafted bad input and asserts the INTENDED gate message appears (not merely a
nonzero argparse exit). Login-safe: every case fails at a manifest/receipt/hash gate BEFORE the
consumer imports ROOT (consumers import ROOT lazily only after the gates).

  python tests/test_fps_cli_integration.py     # or via pytest
"""
import json
import os
import subprocess
import sys
import tempfile

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ND)
import fps_provenance as fp

BUILD = "build_active_lateral_fps.py"
P4 = "p4_validate_active_lateral_fps.py"
PUB = "fps_build_publication_manifest.py"


def run(args):
    return subprocess.run([sys.executable] + args, cwd=ND,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)


def _write(p, obj):
    with open(p, "w") as f:
        json.dump(obj, f)
    return p


def make_env(d):
    """Real artifact files + a fully-valid publication manifest (correct hashes) + a valid PASS receipt."""
    eps = []
    for b in fp.BANDS:
        for ep in fp.ENDPOINTS:
            e = {"band": b, "endpoint": ep, "layout_fingerprint": fp.layout_fingerprint(),
                 "reported_mask_hash": fp.REPORTED_MASK_FINGERPRINT, "central_hash": "c" * 64,
                 "footing": {**fp.REQUIRED_FOOTING, "bkg_mode": fp.PUBLICATION_BKG_MODE}}
            for hf, pf in fp.ENDPOINT_ARTIFACTS:
                fpath = os.path.join(d, f"{b}_{ep}_{pf}")
                with open(fpath, "w") as fh:
                    fh.write(f"{b}{ep}{pf}")
                e[pf] = fpath
                e[hf] = fp.sha256_file(fpath)
            eps.append(e)
    man = {"schema": fp.PUBLICATION_SCHEMA, "label": fp.PUBLICATION_LABEL,
           "layout_fingerprint": fp.layout_fingerprint(), "reported_mask_hash": fp.REPORTED_MASK_FINGERPRINT,
           "central_hash": "c" * 64, "central_cv_sha256": "c" * 64, "endpoints": eps}
    mpath = _write(os.path.join(d, "manifest.json"), man)
    dig = fp.sha256_file(mpath)
    rpath = _write(os.path.join(d, "receipt.json"),
                   {"schema": "fps_publication_pass_receipt.v1", "result": "PASS",
                    "manifest_sha256": dig, "validated_utc": "u"})
    return man, mpath, rpath


def _build(mpath, rpath, d):
    return run([BUILD, "--manifest", mpath, "--pass-receipt", rpath,
                "--cv", os.path.join(d, "cv.root"), "--out", os.path.join(d, "o.root"),
                "--out-receipt", os.path.join(d, "cb.json")])


def _assert(r, needle, case):
    blob = (r.stderr or "") + (r.stdout or "")
    assert r.returncode != 0, f"{case}: expected nonzero exit, got 0"
    assert needle in blob, f"{case}: expected '{needle}' in output; got:\n{blob[-600:]}"


# ---------------------------------------------------------------- gate-1 (manifest) via build_active
def test_cli_non_hex_hash():
    d = tempfile.mkdtemp(); man, mp, rp = make_env(d)
    man["endpoints"][0]["unfold_sha256"] = "z" * 64
    _write(mp, man)
    _assert(_build(mp, rp, d), "not a lowercase 64-hex", "non_hex_hash")


def test_cli_purity_label():
    d = tempfile.mkdtemp(); man, mp, rp = make_env(d)
    man["label"] = fp.CONTROL_LABEL; _write(mp, man)
    _assert(_build(mp, rp, d), "label", "purity_label")


def test_cli_wrong_mask():
    d = tempfile.mkdtemp(); man, mp, rp = make_env(d)
    bad = "deadbeef" * 8
    man["reported_mask_hash"] = bad
    for e in man["endpoints"]:
        e["reported_mask_hash"] = bad
    _write(mp, man)
    _assert(_build(mp, rp, d), "reported_mask_hash", "wrong_mask")


def test_cli_missing_path_field():
    d = tempfile.mkdtemp(); man, mp, rp = make_env(d)
    del man["endpoints"][0]["config_path"]; _write(mp, man)
    _assert(_build(mp, rp, d), "config_path", "missing_path")


# ---------------------------------------------------------------- gate-2 (receipt) via build_active
def test_cli_two_field_receipt():
    d = tempfile.mkdtemp(); man, mp, rp = make_env(d)
    _write(rp, {"result": "PASS", "manifest_sha256": fp.sha256_file(mp)})
    _assert(_build(mp, rp, d), "two-field object rejected", "two_field_receipt")


# ---------------------------------------------------------------- gate-3 (recompute) via build_active
def test_cli_recompute_mismatch():
    d = tempfile.mkdtemp(); man, mp, rp = make_env(d)
    # substitute the content of a referenced file without updating its hash
    with open(man["endpoints"][0]["unfold_root"], "w") as fh:
        fh.write("TAMPERED-SAME-CLASS")
    _assert(_build(mp, rp, d), "recomputed", "recompute_mismatch")


def test_cli_recompute_missing_path():
    d = tempfile.mkdtemp(); man, mp, rp = make_env(d)
    os.remove(man["endpoints"][0]["source_path"])
    _assert(_build(mp, rp, d), "path absent", "recompute_missing_path")


# ---------------------------------------------------------------- gate-4 (transition receipt) via P4
def test_cli_p4_bad_component_receipt():
    d = tempfile.mkdtemp(); man, mp, rp = make_env(d)
    active = os.path.join(d, "active.root")
    with open(active, "w") as fh:
        fh.write("active-cov")
    badcb = _write(os.path.join(d, "cb.json"),
                   {"schema": "WRONG.v1", "result": "PASS", "candidate_sha256": "a" * 64})
    audit = _write(os.path.join(d, "audit.json"), {"result": "PASS"})
    r = run([P4, "--manifest", mp, "--pass-receipt", rp, "--component-receipt", badcb,
             "--active", active + ":hCov_universe4d_total", "--support", os.path.join(d, "sup.root"),
             "--cv", os.path.join(d, "cv.root"), "--audit-json", audit,
             "--out", os.path.join(d, "p4.json"), "--out-receipt", os.path.join(d, "p4r.json")])
    _assert(r, "component_build receipt schema", "p4_bad_component_receipt")


# ---------------------------------------------------------------- aggregate worker failures via builder
def test_cli_pub_builder_aggregates_missing():
    d = tempfile.mkdtemp()   # empty negweight dir -> all ten endpoints missing
    r = run([PUB, "--negweight-dir", d, "--cv", os.path.join(d, "cv.root"), "--utc", "u",
             "--out-manifest", os.path.join(d, "m.json"), "--out-receipt", os.path.join(d, "r.json")])
    _assert(r, "negweight output missing", "pub_aggregate")


def test_cli_pub_builder_receipt_gate_still_closes_when_endpoints_valid():
    """Ordering guard, paired with test_cli_pub_builder_aggregates_missing.

    That test proves ten ABSENT outputs report "negweight output missing" rather than
    the downstream "receipt: required file absent: COMPLETE" symptom -- i.e. that the
    merged-input receipt gate is resolved lazily, below PASS 1. This test proves the
    gate was only DEFERRED, not weakened: with all ten outputs present and their
    configs valid, the builder must still refuse to emit a manifest.

    Together they pin the ordering from both sides. Hoisting fvm.verify() back above
    PASS 1 breaks the other test; deleting the gate breaks this one.

    Deliberately platform-portable. fps_verify_merged_receipt.REPO is a hardcoded
    /pscratch literal, so verify() RAISES off-Perlmutter ("required file absent") but
    SUCCEEDS on Perlmutter, where the empty temp --merged-dir then fails the receipt
    membership check instead ("merged input not in validated receipt"). Both are the
    gate doing its job, so either message satisfies this test; what must hold on every
    platform is that no manifest is written and that aggregation did not short-circuit.
    """
    d = tempfile.mkdtemp()
    nw = os.path.join(d, "negweight"); os.makedirs(nw)
    cfg = dict(fp.REQUIRED_FOOTING)
    cfg["bkg_mode"] = fp.PUBLICATION_BKG_MODE
    cfg["launcher"] = "sbatch_unfold_active_fps.sh"     # in KNOWN_LAUNCHERS and exists under cwd=ND
    for b in fp.BANDS:
        for ep in fp.ENDPOINTS:
            out = os.path.join(nw, f"fps2d_xsec_MEFHC_5iter_lgbm_uni_full_{b}_{ep}.root")
            with open(out, "w") as fh:
                fh.write("placeholder")                 # never hashed; PASS 1 only checks existence
            _write(out + ".config.json", cfg)
    man = os.path.join(d, "m.json")
    r = run([PUB, "--negweight-dir", nw, "--merged-dir", os.path.join(d, "merged"),
             "--cv", os.path.join(d, "cv.root"), "--utc", "u",
             "--out-manifest", man, "--out-receipt", os.path.join(d, "r.json")])
    blob = (r.stdout or "") + (r.stderr or "")
    assert r.returncode != 0, "pub_receipt_gate: expected nonzero exit, got 0"
    assert any(n in blob for n in ("receipt: required file absent",
                                  "merged input not in validated receipt")), \
        f"pub_receipt_gate: expected a merged-input receipt gate message; got:\n{blob[-600:]}"
    assert "negweight output missing" not in blob, \
        "pub_receipt_gate: aggregation fired, so the ten endpoints were not actually valid -- " \
        "this test no longer exercises the receipt gate"
    assert not os.path.exists(man), \
        "pub_receipt_gate: manifest emitted without a verified merged-input receipt"


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"[PASS] {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} CLI integration negatives passed")


if __name__ == "__main__":
    _run_all()
