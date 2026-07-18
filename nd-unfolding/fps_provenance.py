#!/usr/bin/env python3
"""Fail-closed provenance + gate library for the FPS selection-complete lateral covariance
chain (Agent C, P4-FPS / P6-FPS-final). ROOT-FREE by design: pure python + hashlib + numpy so
every gate is unit-testable without a compute node, and the ROOT-facing scripts (rollup /
validator / adopt / unified-adopt) call these same functions after loading matrices via ROOT.

Motivation (2026-07-18 reconciliation): the ten existing FPS endpoint unfolds were produced with
the unfold default --bkg-mode=purity (both launchers omit --bkg-mode), so they are PURITY CONTROLS,
not publication inputs. The selected publication footing is 'negweight-refined'. These gates make
that distinction structural: a purity/default/missing background mode CANNOT enter a publication
rollup, and every covariance step fails closed on inventory / order / mask / footing / identity.

Every `require_*` raises FpsGateError (fail-closed) with an explicit message; never returns a soft
pass. `check_*` / compute helpers return values for callers to gate on.
"""
import hashlib
import json
import os

import numpy as np

# ----------------------------------------------------------------------------- canonical layout
# FPS extended grid (from both FPS unfold launchers; C-order ravel of (pt, pz)).
PT_EDGES = [0.0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85,
            1.00, 1.25, 1.50, 2.50, 4.50, 30.0]                       # 16 edges -> 15 pt bins
PZ_EDGES = [0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
            6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0, 120.0]  # 20 edges -> 19 pz bins
NPT = len(PT_EDGES) - 1          # 15
NPZ = len(PZ_EDGES) - 1          # 19
NBINS_EXT = NPT * NPZ            # 285 (extended grid, C-order)
RAVEL_ORDER = "C"

# the 5 selection-complete lateral bands x the 2 endpoints
BANDS = ["BeamAngleX", "BeamAngleY", "MuonResolution",
         "Muon_Energy_MINERvA", "Muon_Energy_MINOS"]
ENDPOINTS = (0, 1)
N_ENDPOINTS = len(BANDS) * len(ENDPOINTS)   # 10

# execution footing the publication rollup demands
PUBLICATION_BKG_MODE = "negweight-refined"
CONTROL_BKG_MODE = "purity"
REQUIRED_FOOTING = {
    "estimator": "lgbm",
    "seed": 42,
    "iters": 5,
    "use_weights": True,
    "full_phase_space": True,
}
FOOTING_KEYS = list(REQUIRED_FOOTING) + ["bkg_mode"]


class FpsGateError(Exception):
    """Raised by any fail-closed gate. Message names the exact artifact + failure."""


# ----------------------------------------------------------------------------- hashing helpers
def sha256_file(path):
    if not os.path.exists(path):
        raise FpsGateError(f"sha256_file: missing artifact {path}")
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_partial(path, edge_bytes=8 << 20):
    """Bounded content fingerprint (size + head + tail) for very large files where a full-file
    SHA256 is impractical (the 74GB merged endpoint inputs = 740GB of login-node I/O for all ten).
    NOT a full hash: labeled 'partial-headtail' so a caller can never mistake it for one; the full
    input identity is corroborated by the merged-endpoint audit receipt. A full SHA256 remains a
    recorded residual evidence gap until it can be computed on a compute node."""
    if not os.path.exists(path):
        raise FpsGateError(f"sha256_partial: missing artifact {path}")
    sz = os.path.getsize(path)
    h = hashlib.sha256()
    h.update(f"size={sz};".encode())
    with open(path, "rb") as f:
        h.update(f.read(min(edge_bytes, sz)))
        if sz > edge_bytes:
            f.seek(max(0, sz - edge_bytes))
            h.update(f.read(edge_bytes))
    return f"partial-headtail{edge_bytes}b:{h.hexdigest()}"


def layout_fingerprint(pt_edges=PT_EDGES, pz_edges=PZ_EDGES):
    """Deterministic hash binding the exact edges + C-order + 285-bin layout."""
    payload = json.dumps(
        {"pt_edges": [float(x) for x in pt_edges],
         "pz_edges": [float(x) for x in pz_edges],
         "npt": len(pt_edges) - 1, "npz": len(pz_edges) - 1,
         "nbins": (len(pt_edges) - 1) * (len(pz_edges) - 1),
         "ravel_order": RAVEL_ORDER},
        sort_keys=True, separators=(",", ":")).encode()
    return sha256_bytes(payload)


def mask_hash(mask_bool):
    """Hash of the reported-bin boolean mask (285 -> reported). Binds a covariance to the exact
    CV>0 reporting mask so a covariance built against a different central can never be adopted."""
    m = np.asarray(mask_bool, dtype=bool)
    if m.ndim != 1:
        raise FpsGateError(f"mask_hash: mask must be 1-D, got {m.shape}")
    return sha256_bytes(m.tobytes()) + f":n{int(m.sum())}/{m.size}"


def endpoint_key(band, ep):
    return f"{band}_{ep}"


# ----------------------------------------------------------------------------- manifest gates
def require_manifest_inventory(manifest):
    """Exactly the 10 named (band, endpoint) entries: no missing, extra, or duplicate."""
    entries = manifest.get("endpoints")
    if not isinstance(entries, list):
        raise FpsGateError("manifest: 'endpoints' missing or not a list")
    keys = [f"{e.get('band')}_{e.get('endpoint')}" for e in entries]
    if len(keys) != len(set(keys)):
        dup = sorted({k for k in keys if keys.count(k) > 1})
        raise FpsGateError(f"manifest inventory: duplicate endpoints {dup}")
    want = {endpoint_key(b, ep) for b in BANDS for ep in ENDPOINTS}
    got = set(keys)
    if got != want:
        raise FpsGateError(
            f"manifest inventory != exactly 10 named endpoints; "
            f"missing={sorted(want - got)} extra={sorted(got - want)}")
    if len(entries) != N_ENDPOINTS:
        raise FpsGateError(f"manifest inventory: {len(entries)} entries != {N_ENDPOINTS}")
    return True


def require_common_fingerprints(manifest):
    """All entries + the manifest header agree on layout, reported-mask, and central hashes."""
    for key in ("layout_fingerprint", "reported_mask_hash", "central_hash"):
        top = manifest.get(key)
        if not top:
            raise FpsGateError(f"manifest: header '{key}' missing")
        for e in manifest["endpoints"]:
            if e.get(key) not in (None, top):
                raise FpsGateError(
                    f"manifest: endpoint {e.get('band')}_{e.get('endpoint')} '{key}'"
                    f" {e.get(key)} != header {top}")
    if manifest["layout_fingerprint"] != layout_fingerprint():
        raise FpsGateError("manifest: layout_fingerprint != canonical FPS 285-bin layout")
    return True


def require_footing(manifest, required_bkg_mode=None):
    """Every entry carries the fixed estimator footing; if required_bkg_mode is given, EVERY
    entry's bkg_mode must equal it (this is how the publication path rejects purity controls)."""
    for e in manifest["endpoints"]:
        foot = e.get("footing", {})
        for k, v in REQUIRED_FOOTING.items():
            if foot.get(k) != v:
                raise FpsGateError(
                    f"footing[{e.get('band')}_{e.get('endpoint')}].{k}={foot.get(k)} != {v}")
        if "bkg_mode" not in foot:
            raise FpsGateError(
                f"footing[{e.get('band')}_{e.get('endpoint')}] has no bkg_mode (unprovable)")
        if required_bkg_mode is not None and foot["bkg_mode"] != required_bkg_mode:
            raise FpsGateError(
                f"footing[{e.get('band')}_{e.get('endpoint')}].bkg_mode="
                f"{foot['bkg_mode']} != required {required_bkg_mode}")
    return True


def classify_manifest(manifest):
    """Return 'publication' iff all 10 are negweight-refined, 'purity-control' iff all purity.
    A mixed or unknown-mode manifest fails closed."""
    require_manifest_inventory(manifest)
    modes = {e.get("footing", {}).get("bkg_mode") for e in manifest["endpoints"]}
    if modes == {PUBLICATION_BKG_MODE}:
        return "publication"
    if modes == {CONTROL_BKG_MODE}:
        return "purity-control"
    raise FpsGateError(f"manifest classify: non-uniform/unknown bkg modes {sorted(map(str, modes))}")


def require_publication_manifest(manifest):
    """Full gate for a covariance-producing step: inventory + fingerprints + negweight-refined."""
    require_manifest_inventory(manifest)
    require_common_fingerprints(manifest)
    require_footing(manifest, required_bkg_mode=PUBLICATION_BKG_MODE)
    if classify_manifest(manifest) != "publication":
        raise FpsGateError("manifest is not a publication (negweight-refined) manifest")
    return True


# ----------------------------------------------------------------------------- matrix gates
def _sym(C):
    return 0.5 * (C + C.T)


def symmetry_rel(C):
    C = np.asarray(C, float)
    denom = max(1e-300, float(np.max(np.abs(C))))
    return float(np.max(np.abs(C - C.T)) / denom)


def psd_min_eig_ratio(C):
    ev = np.linalg.eigvalsh(_sym(np.asarray(C, float)))
    return float(ev[0] / max(1e-300, abs(ev[-1])))


def require_psd(C, tol=-1e-12, tag="matrix"):
    r = psd_min_eig_ratio(C)
    if r < tol:
        raise FpsGateError(f"{tag}: not PSD (min/max eig ratio {r:.3e} < {tol:.1e})")
    return r


def require_square_finite(C, expected_dim=None, tag="matrix"):
    C = np.asarray(C, float)
    if C.ndim != 2 or C.shape[0] != C.shape[1]:
        raise FpsGateError(f"{tag}: not square {C.shape}")
    if expected_dim is not None and C.shape[0] != expected_dim:
        raise FpsGateError(f"{tag}: dim {C.shape[0]} != expected {expected_dim}")
    if not np.all(np.isfinite(C)):
        raise FpsGateError(f"{tag}: contains non-finite entries")
    return True


def require_reported_cov(C, expected_dim, mask_hash_expected, mask_hash_actual,
                         sym_tol=1e-9, tag="reported_cov"):
    require_square_finite(C, expected_dim, tag)
    if symmetry_rel(C) > sym_tol:
        raise FpsGateError(f"{tag}: rel asymmetry {symmetry_rel(C):.2e} > {sym_tol:.1e}")
    if mask_hash_actual != mask_hash_expected:
        raise FpsGateError(
            f"{tag}: reported-mask hash {mask_hash_actual} != manifest {mask_hash_expected}")
    return True


def check_active_rollup(per_band, total, tol=1e-10):
    """The active five-band lateral rollup must have EXACTLY the 5 named bands, each with a
    finite nonzero-trace PSD-ish block, and total == sum(5 bands) within tol. A zero band or
    zero total (the 'nothing happened' failure) raises."""
    got = set(per_band)
    want = set(BANDS)
    if got != want:
        raise FpsGateError(
            f"active rollup bands != 5 named; missing={sorted(want - got)} extra={sorted(got - want)}")
    acc = None
    for b in BANDS:
        cb = np.asarray(per_band[b], float)
        require_square_finite(cb, tag=f"active band {b}")
        tr = float(np.trace(cb))
        if not np.isfinite(tr) or tr <= 0:
            raise FpsGateError(f"active band {b}: trace {tr:.3e} <= 0 (band contributes nothing)")
        acc = cb.copy() if acc is None else acc + cb
    total = np.asarray(total, float)
    require_square_finite(total, expected_dim=acc.shape[0], tag="active total")
    if float(np.trace(total)) <= 0:
        raise FpsGateError("active total: trace <= 0")
    resid = float(np.max(np.abs(total - acc)))
    denom = max(1e-300, float(np.max(np.abs(total))))
    if resid / denom > tol:
        raise FpsGateError(
            f"active total != sum(5 bands): max|diff|={resid:.3e} rel={resid/denom:.2e} > {tol:.1e}")
    return True


def pure_sum_vs_sub_residual(C_sum, C_sub):
    C_sum = np.asarray(C_sum, float); C_sub = np.asarray(C_sub, float)
    if C_sum.shape != C_sub.shape:
        raise FpsGateError(f"sum/sub shape mismatch {C_sum.shape} vs {C_sub.shape}")
    resid = float(np.max(np.abs(C_sum - C_sub)))
    denom = max(1e-300, float(np.max(np.abs(C_sum))))
    return resid, resid / denom


def require_pure_sum_matches_sub(C_sum, C_sub, tol=1e-9):
    """The PSD-safe pure-sum swap must equal the same-source subtraction to float precision.
    A large residual means the stored combined is NOT SUM(bands)+stat+ML (evidence problem),
    so the pure sum cannot be trusted -> fail closed."""
    resid, rel = pure_sum_vs_sub_residual(C_sum, C_sub)
    if rel > tol:
        raise FpsGateError(
            f"pure-sum vs same-source-subtraction residual rel={rel:.3e} > {tol:.1e} "
            f"(abs {resid:.3e}); stored combined is not a clean component sum")
    return resid, rel


def require_unified_inputs(diag_block, diag_unified, tag="unified"):
    """Reject the pathological throw comparator where a block-sum variance is 0 while the unified
    variance is >0 (division/inflation would be ill-defined; signals a mask/estimator mismatch)."""
    db = np.asarray(diag_block, float); du = np.asarray(diag_unified, float)
    if db.shape != du.shape:
        raise FpsGateError(f"{tag}: block/unified diag shape mismatch {db.shape} vs {du.shape}")
    bad = np.where((db <= 0) & (du > 0))[0]
    if bad.size:
        raise FpsGateError(
            f"{tag}: {bad.size} bins have diag(C_blocksum)<=0 < diag(C_unified) "
            f"(first bins {bad[:5].tolist()})")
    return True


def require_no_path_alias(out_path, *in_paths):
    o = os.path.realpath(out_path)
    for p in in_paths:
        if p and os.path.realpath(p) == o:
            raise FpsGateError(f"path alias: output {out_path} aliases input {p}")
    return True


def reconstruct_final(C_pre, C_vertical, g):
    """C_final = C_pre - C_vertical + (g g^T) o C_vertical  (unified-throw inflation adoption)."""
    C_pre = np.asarray(C_pre, float); C_vertical = np.asarray(C_vertical, float)
    g = np.asarray(g, float)
    G = np.outer(g, g)
    return C_pre - C_vertical + G * C_vertical


def require_final_identity(C_final, C_pre, C_vertical, g, tol=1e-9, tag="final adoption"):
    C_ref = _sym(reconstruct_final(C_pre, C_vertical, g))
    C_fin = _sym(np.asarray(C_final, float))
    resid = float(np.max(np.abs(C_fin - C_ref)))
    denom = max(1e-300, float(np.max(np.abs(C_ref))))
    if resid / denom > tol:
        raise FpsGateError(
            f"{tag}: reconstructed C_pre - C_vert + (gg^T)oC_vert != final "
            f"(rel {resid/denom:.3e} > {tol:.1e})")
    return resid


def cov_fingerprint(C, mask_hash_val=None):
    """Compact, reproducible fingerprint block for receipts."""
    C = _sym(np.asarray(C, float))
    ev = np.linalg.eigvalsh(C)
    d = np.diag(C)
    return {
        "dim": int(C.shape[0]),
        "rank": int(np.sum(ev > ev.max() * 1e-12)) if ev.size and ev.max() > 0 else 0,
        "sqrt_trace": float(np.sqrt(max(np.trace(C), 0.0))),
        "min_over_max_eig": float(ev[0] / max(1e-300, abs(ev[-1]))),
        "symmetry_rel": symmetry_rel(C),
        "n_pos_diag": int(np.sum(d > 0)),
        "mask_hash": mask_hash_val,
    }
