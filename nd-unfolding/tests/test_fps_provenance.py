#!/usr/bin/env python3
"""Blocker 7 (Agent C): ROOT-free unit tests for the FPS provenance/gate library. Exercises every
fail-closed path the covariance chain depends on: manifest inventory (wrong/missing/extra/dup),
mismatched layout/mask/central/bkg-mode footing, active-rollup band inventory + zero band/total,
pure-sum-vs-subtraction residual, zero-block/nonzero-unified, path aliasing, and the final
adoption identity reconstruction. No ROOT, no compute node: pure numpy + dict fixtures.

  python -m pytest tests/test_fps_provenance.py     # or:  python tests/test_fps_provenance.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import fps_provenance as fp


# --------------------------------------------------------------------------- fixtures / helpers
def _spd(n, seed):
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((n, n))
    return A @ A.T / n + np.eye(n) * 1e-6


def make_manifest(bkg_mode=fp.PUBLICATION_BKG_MODE, drop=None, extra=None, dup=None,
                  bad_layout=False, mixed_mode=False, bad_footing=None):
    lay = "BAD" if bad_layout else fp.layout_fingerprint()
    mh, ch = "maskhash-xyz", "central-xyz"
    eps = []
    pairs = [(b, ep) for b in fp.BANDS for ep in fp.ENDPOINTS]
    if drop:
        pairs = [p for p in pairs if p != drop]
    if extra:
        pairs = pairs + [extra]
    if dup:
        pairs = pairs + [dup]
    for i, (b, ep) in enumerate(pairs):
        foot = dict(fp.REQUIRED_FOOTING)
        foot["bkg_mode"] = bkg_mode
        if mixed_mode and i == 0:
            foot["bkg_mode"] = fp.CONTROL_BKG_MODE
        if bad_footing and (b, ep) == bad_footing[0]:
            foot[bad_footing[1]] = bad_footing[2]
        eps.append({"band": b, "endpoint": ep,
                    "layout_fingerprint": lay, "reported_mask_hash": mh, "central_hash": ch,
                    "footing": foot})
    return {"layout_fingerprint": lay, "reported_mask_hash": mh, "central_hash": ch,
            "endpoints": eps}


def _raises(fn):
    try:
        fn()
    except fp.FpsGateError:
        return True
    return False


# --------------------------------------------------------------------------- manifest inventory
def test_manifest_ok():
    assert fp.require_publication_manifest(make_manifest())


def test_manifest_missing_endpoint():
    assert _raises(lambda: fp.require_manifest_inventory(make_manifest(drop=("MuonResolution", 1))))


def test_manifest_extra_endpoint():
    assert _raises(lambda: fp.require_manifest_inventory(make_manifest(extra=("Bogus", 0))))


def test_manifest_duplicate_endpoint():
    assert _raises(lambda: fp.require_manifest_inventory(make_manifest(dup=("BeamAngleX", 0))))


def test_manifest_bad_layout():
    assert _raises(lambda: fp.require_common_fingerprints(make_manifest(bad_layout=True)))


def test_footing_wrong_bkg_mode_rejected_for_publication():
    # purity controls must be rejected by the publication gate
    assert _raises(lambda: fp.require_publication_manifest(make_manifest(bkg_mode=fp.CONTROL_BKG_MODE)))


def test_footing_missing_token():
    m = make_manifest(bad_footing=(("BeamAngleY", 0), "seed", 999))
    assert _raises(lambda: fp.require_footing(m))


def test_classify_mixed_fails():
    assert _raises(lambda: fp.classify_manifest(make_manifest(mixed_mode=True)))


def test_classify_control_and_publication():
    assert fp.classify_manifest(make_manifest(bkg_mode=fp.CONTROL_BKG_MODE)) == "purity-control"
    assert fp.classify_manifest(make_manifest(bkg_mode=fp.PUBLICATION_BKG_MODE)) == "publication"


# --------------------------------------------------------------------------- active rollup
def test_active_rollup_ok():
    per = {b: _spd(6, i) for i, b in enumerate(fp.BANDS)}
    tot = sum(per.values())
    assert fp.check_active_rollup(per, tot)


def test_active_rollup_missing_band():
    per = {b: _spd(6, i) for i, b in enumerate(fp.BANDS[:-1])}
    tot = sum(per.values())
    assert _raises(lambda: fp.check_active_rollup(per, tot))


def test_active_rollup_zero_band():
    per = {b: _spd(6, i) for i, b in enumerate(fp.BANDS)}
    per["MuonResolution"] = np.zeros((6, 6))     # a band that contributes nothing
    tot = sum(per.values())
    assert _raises(lambda: fp.check_active_rollup(per, tot))


def test_active_rollup_total_mismatch():
    per = {b: _spd(6, i) for i, b in enumerate(fp.BANDS)}
    tot = sum(per.values()) + _spd(6, 99)        # total != sum of the 5
    assert _raises(lambda: fp.check_active_rollup(per, tot))


# --------------------------------------------------------------------------- pure-sum vs subtraction
def test_pure_sum_matches_sub_ok():
    C = _spd(8, 1)
    assert fp.require_pure_sum_matches_sub(C, C + 1e-15)[1] <= 1e-9


def test_pure_sum_vs_sub_mismatch():
    C = _spd(8, 1)
    assert _raises(lambda: fp.require_pure_sum_matches_sub(C, C + 1e-3 * np.max(np.abs(C))))


# --------------------------------------------------------------------------- unified inputs
def test_unified_inputs_ok():
    db = np.array([1.0, 2.0, 0.0, 3.0]); du = np.array([1.1, 2.0, 0.0, 2.9])
    assert fp.require_unified_inputs(db, du)


def test_unified_zero_block_nonzero_unified():
    db = np.array([1.0, 0.0, 3.0]); du = np.array([1.0, 5.0, 3.0])   # bin 1 pathological
    assert _raises(lambda: fp.require_unified_inputs(db, du))


# --------------------------------------------------------------------------- path alias
def test_path_alias_ok(tmp_path=None):
    assert fp.require_no_path_alias("/a/out.root", "/a/in1.root", "/a/in2.root")


def test_path_alias_detected():
    assert _raises(lambda: fp.require_no_path_alias("/a/x.root", "/a/x.root"))


# --------------------------------------------------------------------------- final identity
def test_final_identity_ok():
    C_pre = _spd(10, 2); C_vert = _spd(10, 3) * 0.3
    g = np.linspace(1.0, 1.5, 10)
    C_final = fp.reconstruct_final(C_pre, C_vert, g)
    assert fp.require_final_identity(C_final, C_pre, C_vert, g) < 1e-6


def test_final_identity_violation():
    C_pre = _spd(10, 2); C_vert = _spd(10, 3) * 0.3
    g = np.linspace(1.0, 1.5, 10)
    C_final = fp.reconstruct_final(C_pre, C_vert, g) + 1e-2 * np.max(np.abs(C_pre))
    assert _raises(lambda: fp.require_final_identity(C_final, C_pre, C_vert, g))


# --------------------------------------------------------------------------- matrix gates
def test_reported_cov_mask_binding():
    C = _spd(266, 5)
    assert fp.require_reported_cov(C, 266, "mhX", "mhX")
    assert _raises(lambda: fp.require_reported_cov(C, 266, "mhX", "mhY"))   # mask mismatch
    assert _raises(lambda: fp.require_reported_cov(C, 999, "mhX", "mhX"))   # wrong dim


def test_psd_gate():
    C = _spd(12, 7)
    assert fp.require_psd(C) >= -1e-12
    bad = C.copy(); bad[0, 0] = -abs(C[0, 0]) - 1.0
    assert _raises(lambda: fp.require_psd(bad))


def test_layout_and_mask_hash_deterministic():
    assert fp.layout_fingerprint() == fp.layout_fingerprint()
    m = np.array([True, False, True, True])
    assert fp.mask_hash(m) == fp.mask_hash(m)
    assert fp.mask_hash(m) != fp.mask_hash(~m)


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        fn()
        passed += 1
        print(f"[PASS] {fn.__name__}")
    print(f"\n{passed}/{len(fns)} tests passed")


if __name__ == "__main__":
    _run_all()
