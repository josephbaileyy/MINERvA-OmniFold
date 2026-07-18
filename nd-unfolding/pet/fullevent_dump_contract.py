#!/usr/bin/env python3
"""Login-safe write/schema CONTRACT for the G2 full-event FPS point-cloud dump.

Pure (no ROOT / no TensorFlow): the schema gate, atomic transactional NPZ write, strict complete
manifest, three-inventory (signal / data / background) alignment + vector-length checks, real
stable-identity/order evidence, and the forbidden-purity-fallback guard that the G2 dumper
(`dump_pointcloud_inputs.py`, PyROOT — RUNTIME-BLOCKED until Agent E's reviewed/built/smoke-
validated G2 ROOT exists) MUST satisfy so its output keys/order/fingerprints match
`fullevent_fps_dataloader.build_fullevent_loaders` and the F7 three-inventory replay EXACTLY.
Unit-testable on the login node with fake in-memory sources.
"""
import os
import tempfile

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
import sys
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from fullevent_fps_dataloader import inventory_order_hash  # noqa: E402  (login-safe: no ROOT/TF)

# Exact G2 full-event schema markers the source ROOT/NPZ must carry (old/recoil-only fail closed).
G2_SCHEMA = {"petSchemaVersion": "g2-fullevent-v1", "hasFullEventSchema": 1, "fullPhaseSpace": 1}

# Distinct reco / data / truth / background feature schemas — NO invented cross-schema
# counterparts (MINOS/range/quality are reco-only; truth has no detector counterpart).
RECO_KEYS = ("part_reco", "reco_scalars", "reco_muon", "reco_vertex", "reco_view", "reco_time")
DATA_KEYS = ("measured_pc", "measured_scalars", "data_muon", "data_vertex", "data_view", "data_time")
TRUTH_KEYS = ("part_gen",)                      # (E,px,py,pz,pdg); truth-muon lives in truth_scalars
BKG_KEYS = ("bkg_part_reco", "bkg_reco_scalars", "bkg_muon", "bkg_vertex", "bkg_view", "bkg_time",
            "w_bkg", "bkg_identity_hash", "bkg_indices")   # background carries its OWN identity/order
GLOBAL_KEYS = ("edges_0", "edges_1", "pass_reco", "pass_truth", "w_truth", "w_reco",
               "truth_scalars", "petSchemaVersion", "hasFullEventSchema", "fullPhaseSpace",
               "estimator_fingerprint", "sig_identity_hash", "data_identity_hash", "data_pot")
# Generator labels: AUDIT METADATA ONLY, never classifier features.
AUDIT_ONLY_KEYS = ("bkg_nuPDG", "bkg_current", "bkg_inttype")
REQUIRED_KEYS = RECO_KEYS + DATA_KEYS + TRUTH_KEYS + BKG_KEYS + GLOBAL_KEYS


def assert_g2_schema(meta):
    """Fail closed unless the source carries the EXACT G2 full-event markers. A recoil-only /
    old input (markers absent or wrong version) is rejected — no purity/recoil fallback."""
    for k, want in G2_SCHEMA.items():
        got = meta.get(k) if hasattr(meta, "get") else (meta[k] if k in meta else None)
        if got is None:
            raise ValueError(f"[G2-SCHEMA] missing marker '{k}' -> old/recoil-only input; fail "
                             f"closed. Require {G2_SCHEMA}.")
        if k == "petSchemaVersion":
            if str(np.asarray(got).item() if hasattr(got, "item") else got) != want:
                raise ValueError(f"[G2-SCHEMA] petSchemaVersion {got!r} != {want!r} (fail closed)")
        elif int(np.asarray(got).item() if hasattr(got, "item") else got) != want:
            raise ValueError(f"[G2-SCHEMA] {k}={got} != {want} (fail closed)")
    return True


def assert_no_purity_fallback(arrays, bkg_mode):
    """The negweight-refined NOMINAL must not silently degrade to the purity placeholder
    (measured_weights all-ones) or an empty background. Fail closed."""
    if bkg_mode == "negweight-refined":
        if "w_bkg" not in arrays or np.asarray(arrays["w_bkg"]).size == 0:
            raise ValueError("[G2] negweight-refined needs a non-empty background inventory (w_bkg)")
        mw = arrays.get("measured_weights") if hasattr(arrays, "get") else None
        if mw is not None and np.asarray(mw).size and np.all(np.asarray(mw) == 1.0):
            raise ValueError("[G2] measured_weights all-ones = PURITY fallback; forbidden for the "
                             "negweight-refined nominal (fail closed)")
    return True


def assert_inventory_alignment(arrays):
    """Row-count + view/time vector-length checks for the three inventories (each block shares its
    inventory row count; view/time token length == cloud token dim P)."""
    def rows(k):
        return int(np.asarray(arrays[k]).shape[0])
    ns = rows("part_gen")
    for k in ("part_reco", "reco_scalars", "reco_muon", "reco_vertex", "reco_view", "reco_time",
              "pass_reco", "pass_truth", "w_truth", "w_reco", "truth_scalars"):
        if rows(k) != ns:
            raise ValueError(f"[G2-ALIGN] signal '{k}' rows {rows(k)} != part_gen {ns}")
    nd_ = rows("measured_pc")
    for k in ("measured_scalars", "data_muon", "data_vertex", "data_view", "data_time"):
        if rows(k) != nd_:
            raise ValueError(f"[G2-ALIGN] data '{k}' rows {rows(k)} != measured_pc {nd_}")
    nb = rows("bkg_part_reco")
    for k in ("bkg_reco_scalars", "bkg_muon", "bkg_vertex", "bkg_view", "bkg_time", "w_bkg"):
        if rows(k) != nb:
            raise ValueError(f"[G2-ALIGN] bkg '{k}' rows {rows(k)} != bkg_part_reco {nb}")
    P = int(np.asarray(arrays["part_reco"]).shape[1])
    for cloud, view, time in (("part_reco", "reco_view", "reco_time"),
                              ("measured_pc", "data_view", "data_time"),
                              ("bkg_part_reco", "bkg_view", "bkg_time")):
        for vk in (view, time):
            if int(np.asarray(arrays[vk]).shape[1]) != P:
                raise ValueError(f"[G2-ALIGN] '{vk}' token length {np.asarray(arrays[vk]).shape[1]} "
                                 f"!= cloud '{cloud}' P={P}")
    return True


def assert_identity_consistency(arrays):
    """Each inventory's persisted identity hash must equal a recomputation over its stable-order
    evidence (real identities, not invented). Fail closed on mismatch/omission."""
    checks = (("sig_identity_hash", ("w_truth", "pass_truth")),
              ("data_identity_hash", ("measured_pc",)),
              ("bkg_identity_hash", ("w_bkg", "bkg_indices")))
    for hkey, evid in checks:
        if hkey not in arrays:
            raise ValueError(f"[G2-IDENTITY] missing identity evidence '{hkey}' (fail closed)")
        want = inventory_order_hash(*[np.asarray(arrays[e]) for e in evid])
        got = str(np.asarray(arrays[hkey]).item() if hasattr(arrays[hkey], "item") else arrays[hkey])
        if got != want:
            raise ValueError(f"[G2-IDENTITY] {hkey} mismatch (reordered/wrong inventory)")
    return True


def write_fullevent_npz_atomic(path, arrays, bkg_mode="negweight-refined"):
    """Transactional G2 write. Runs ALL gates (schema, complete manifest, alignment, identity,
    no-purity-fallback) THEN writes a temp NPZ and atomically os.replace()s it into place — an
    interruption leaves NO partial file at `path`. Any gate failure raises before any write."""
    assert_g2_schema({k: arrays.get(k) for k in G2_SCHEMA if (hasattr(arrays, 'get'))} or arrays)
    missing = [k for k in REQUIRED_KEYS if k not in arrays]
    if missing:
        raise ValueError(f"[G2-MANIFEST] incomplete manifest, missing {missing} (fail closed)")
    assert_inventory_alignment(arrays)
    assert_identity_consistency(arrays)
    assert_no_purity_fallback(arrays, bkg_mode)
    dpath = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".g2dump_", suffix=".npz", dir=dpath)
    os.close(fd)
    try:
        np.savez_compressed(tmp, **arrays)
        os.replace(tmp, path)                 # atomic rename
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)                    # interrupted write: no partial survives at `path`
    return path
