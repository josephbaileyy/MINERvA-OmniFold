#!/usr/bin/env python3
"""P4 standard-lateral hardening library (repair, 2026-07-18).

Fail-closed gates + exact-inventory hashing for the standard selection-complete
scalar lateral chain. ROOT-free by design (ROOT-dependent audits live in
p4_lib_root helpers, imported lazily) so the covariance-math / manifest / gate
logic is unit-testable without PyROOT. The MAT two-endpoint formula is preserved
by reusing uq_math.mat_covariance / uq_math.project_covariance unchanged.

Nothing here BUILDS or ADOPTS a covariance; it only validates/guards. Candidate
construction is authorized only after the standard-p4-verifier returns PASS.
"""
from __future__ import annotations
import hashlib, json, os
import numpy as np

# Canonical standard lateral inventory (exactly these; order fixed).
BANDS = ("BeamAngleX", "BeamAngleY", "MuonResolution",
         "Muon_Energy_MINERvA", "Muon_Energy_MINOS")
ENDPOINTS = (0, 1)                      # -1 sigma, +1 sigma (MAT two-endpoint pair)
N_ENDPOINTS = len(BANDS) * len(ENDPOINTS)   # 10
GRID_NBINS = 65856                      # 14*16*7*7*6 full 5D grid (pt,pz,eavail,q3,W)


class P4GateError(RuntimeError):
    """Raised by any fail-closed gate. Never swallow."""


def require(cond, msg):
    if not cond:
        raise P4GateError(msg)


# ---------------------------------------------------------------- config / hashes
class P4Config:
    """Frozen unfold configuration; its hash pins seed/axes/iters/estimator so a
    covariance can never be built from mismatched-config endpoints."""
    def __init__(self, axes="eavail,q3,W", iters=5, seed=42, estimator="lgbm",
                 use_weights=True, universe=None):
        self.axes = axes; self.iters = int(iters); self.seed = int(seed)
        self.estimator = estimator; self.use_weights = bool(use_weights)
        self.universe = universe          # MUST be None for active endpoints
    def as_dict(self):
        return {"axes": self.axes, "iters": self.iters, "seed": self.seed,
                "estimator": self.estimator, "use_weights": self.use_weights,
                "universe": self.universe}
    def hash(self):
        return hashlib.sha256(json.dumps(self.as_dict(), sort_keys=True).encode()).hexdigest()
    def validate(self):
        require(self.universe is None, "active endpoint config must not set --universe")
        require(self.seed == 42, f"standard P4 requires fixed seed 42 (got {self.seed})")
        require(self.use_weights, "standard P4 requires --use-weights")
        require(self.iters == 5, f"standard P4 production uses 5 iters (got {self.iters})")
        require(self.axes == "eavail,q3,W", f"standard P4 requires axes=eavail,q3,W (got {self.axes})")
        require(self.estimator == "lgbm", f"standard P4 requires estimator=lgbm (got {self.estimator})")
        return True


# canonical candidate area (pre-adoption). Adopted/protected areas are forbidden outputs.
CANDIDATE_SUBDIR = "active_universe_5d/standard/candidate"
_ADOPTED_TOKENS = ("uq_universe_5d_covariance_combined", "_uthrow", "_cvcentered",
                   "adopted", "uq_4d/corrected", "universe_stage2_5d",
                   "products/5d/xsec", "products/4d/xsec")


def require_candidate_path(path):
    """Positive allowlist + negative denylist: a candidate MUST live under the
    candidate subdir and MUST NOT match any adopted/protected token. Prevents both
    the round-2 self-rejection (candidate name containing '_final') and any write
    onto an adopted/central path."""
    require(CANDIDATE_SUBDIR in path, f"candidate must be under {CANDIDATE_SUBDIR} (got {path})")
    for t in _ADOPTED_TOKENS:
        require(t not in path, f"refusing candidate onto adopted/protected path (token {t!r})")
    return True


def prove_identity(A, B, rtol, label):
    """Fail-closed max-relative-difference identity gate (no subtraction hidden)."""
    A = np.asarray(A, dtype=float); B = np.asarray(B, dtype=float)
    require(A.shape == B.shape, f"{label}: shape {A.shape} != {B.shape}")
    denom = max(1e-300, float(np.max(np.abs(A))))
    err = float(np.max(np.abs(A - B)) / denom)
    require(err <= rtol, f"{label}: identity broken (rel {err:.2e} > {rtol:.0e})")
    return err


def edges_bin_volume_hash(edges):
    """Hash the ordered 5-axis edge arrays + the C-order per-bin volume vector."""
    import numpy as _np
    parts = []
    for e in edges:
        a = _np.asarray(e, dtype=float); require(a.ndim == 1 and a.size >= 2, "bad edge array")
        parts.append(a.tobytes())
    edge_hash = hashlib.sha256(b"|".join(parts)).hexdigest()
    widths = [(_np.asarray(e, float)[1:] - _np.asarray(e, float)[:-1]) for e in edges]
    vol = widths[0]
    for w in widths[1:]:
        vol = _np.multiply.outer(vol, w).ravel()   # C-order product of bin widths
    vol_hash = hashlib.sha256(vol.astype(float).tobytes() + b"|C").hexdigest()
    return {"edge_hash": edge_hash, "bin_volume_hash": vol_hash, "n_bins": int(vol.size)}


def validate_orchestrator_merged_receipt(recdir, live_stat):
    """Consume the owner-neutral merged-hash receipt: require COMPLETE + the four
    files, recompute live size/integer-mtime vs the inventory, and return the
    committed hash-list digest bound into our manifest. live_stat: dict path->(size,mtime)."""
    import os as _os
    for f in ("COMPLETE", "summary.tsv", "validation.tsv", "standard.sha256", "standard.inventory.tsv"):
        require(_os.path.exists(_os.path.join(recdir, f)), f"orchestrator receipt missing {f}")
    sha_lines = [l for l in open(_os.path.join(recdir, "standard.sha256")).read().splitlines() if l.strip()]
    require(len(sha_lines) == N_ENDPOINTS, f"receipt standard.sha256 has {len(sha_lines)} != 10 lines")
    merged = {}
    for l in sha_lines:
        h, p = l.split(None, 1); merged[p.strip()] = h
    # recompute live size + integer mtime against the committed inventory
    inv = {}
    for l in open(_os.path.join(recdir, "standard.inventory.tsv")).read().splitlines():
        if not l.strip() or l.startswith("#"):
            continue
        cols = l.split("\t")
        if len(cols) >= 3:                       # orchestrator format: size<TAB>mtime<TAB>path
            inv[cols[2]] = (int(cols[0]), int(float(cols[1])))
    for p, (sz, mt) in inv.items():
        require(p in live_stat, f"inventory path not live: {p}")
        lsz, lmt = live_stat[p]
        require(lsz == sz and int(lmt) == mt, f"live size/mtime drift for {p}")
    digest = hashlib.sha256("\n".join(sorted(f"{merged[p]}  {p}" for p in merged)).encode()).hexdigest()
    return {"merged_sha256": merged, "hash_list_digest": digest, "n": len(merged)}


def sha256_file(path, _bufsz=1 << 20):
    """Durable file digest (login-computable; no ROOT)."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(_bufsz), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_endpoints():
    """The exact 10 (band, endpoint) logical tasks, in fixed order."""
    return [(b, ep) for b in BANDS for ep in ENDPOINTS]


def endpoint_manifest_hash(entries):
    """entries: iterable of (band, endpoint, fingerprint). Hash is order-independent
    over the SET but requires the exact 10-endpoint inventory (fail-closed)."""
    seen = {}
    for band, ep, fp in entries:
        require(band in BANDS, f"unknown band {band!r}")
        require(ep in ENDPOINTS, f"bad endpoint {ep!r}")
        seen[(band, int(ep))] = str(fp)
    require(len(seen) == N_ENDPOINTS,
            f"expected exactly {N_ENDPOINTS} endpoints, got {len(seen)} "
            f"(missing {sorted(set(canonical_endpoints())-set(seen))})")
    blob = json.dumps({f"{b}_{e}": seen[(b, e)] for (b, e) in canonical_endpoints()},
                      sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


def mask_order_hash(mask):
    """Hash of the reported-bin mask + C-order. mask: 1-D bool/int array over the
    full grid. Pins which bins are reported and their order so a projection or a
    component sum can never silently mix masks."""
    m = np.asarray(mask)
    require(m.ndim == 1, "mask must be 1-D (C-order ravel over the 5D grid)")
    require(m.size == GRID_NBINS, f"mask size {m.size} != grid {GRID_NBINS}")
    idx = np.nonzero(m.astype(bool))[0].astype(np.int64)
    require(idx.size > 0, "mask selects zero reported bins")
    return hashlib.sha256(idx.tobytes() + b"|C").hexdigest(), int(idx.size)


# ---------------------------------------------------------------- inventory gates
def require_complete_unfold_set(present_tags):
    """present_tags: iterable of '<band>_<ep>' that passed CONTENT validation.
    Fail-closed unless all 10 canonical endpoints are present+valid."""
    present = set(present_tags)
    need = {f"{b}_{e}" for (b, e) in canonical_endpoints()}
    missing = sorted(need - present)
    require(not missing, f"incomplete unfold set: missing/invalid {missing}")
    require(present == need, f"unexpected unfold tags: {sorted(present - need)}")
    return True


def check_merged_metadata(meta):
    """Merged-endpoint audit on extracted metadata (ROOT-free, so testable).
    meta keys: tree_entries{mc_truth_denom,mc_signal_reco,mc_background,data},
    mcPOT, dataPOT, hasTruthOnlyMisses, nTruthOnlyMisses,
    census{TruthEntrants,TruthExits,RecoEntrants,RecoExits}, migration_policy."""
    te = meta.get("tree_entries", {})
    for t in ("mc_truth_denom", "mc_signal_reco", "mc_background", "data"):
        require(te.get(t, 0) and te[t] > 0, f"merged tree {t} empty/absent")
    mc, da = meta.get("mcPOT"), meta.get("dataPOT")
    require(mc is not None and np.isfinite(mc) and mc > 0, "merged mcPOT not finite-positive")
    require(da is not None and np.isfinite(da) and da > 0, "merged dataPOT not finite-positive")
    require(te["mc_signal_reco"] == te["mc_truth_denom"],
            f"signal_reco {te['mc_signal_reco']} != truth_denom {te['mc_truth_denom']} (completeness broken)")
    require(meta.get("hasTruthOnlyMisses") is not None and meta.get("nTruthOnlyMisses") is not None,
            "native-miss metadata missing")
    cen = meta.get("census", {})
    for k in ("TruthEntrants", "TruthExits", "RecoEntrants", "RecoExits"):
        require(k in cen and cen[k] is not None, f"census counter {k} missing")
    require(meta.get("migration_policy"), "declared migration policy missing")
    return True


# ---------------------------------------------------------------- covariance gates
def check_symmetric_psd(C, rtol_sym=1e-9, psd_atol_ratio=1e-12):
    C = np.asarray(C, dtype=float)
    require(C.ndim == 2 and C.shape[0] == C.shape[1], "covariance must be square 2-D")
    require(np.all(np.isfinite(C)), "covariance has non-finite entries")
    denom = max(1e-300, np.max(np.abs(C)))
    asym = np.max(np.abs(C - C.T)) / denom
    require(asym <= rtol_sym, f"covariance not symmetric (rel {asym:.2e})")
    ev = np.linalg.eigvalsh(0.5 * (C + C.T))
    require(ev[0] >= -psd_atol_ratio * abs(ev[-1]),
            f"covariance not PSD (min/max eig {ev[0]/max(1e-300,abs(ev[-1])):.2e})")
    d = np.diag(C)
    require(np.all(np.isfinite(d)) and np.all(d >= -1e-30), "non-finite/negative diagonal")
    return {"rel_asymmetry": float(asym), "min_eig": float(ev[0]), "max_eig": float(ev[-1])}


def require_exact_bands(band_covs):
    """band_covs: dict band -> cov. Must be EXACTLY the 5 kinematic bands."""
    got = set(band_covs)
    require(got == set(BANDS),
            f"active-lateral bands mismatch: got {sorted(got)}, need {sorted(BANDS)}")
    return True


def component_traces_positive_finite(band_covs):
    tr = {}
    for b in BANDS:
        require(b in band_covs, f"missing component band {b}")
        C = np.asarray(band_covs[b], dtype=float)
        require(np.all(np.isfinite(C)), f"component {b} has non-finite entries")
        t = float(np.trace(C))
        require(np.isfinite(t) and t > 0.0, f"component {b} trace not positive-finite ({t})")
        tr[b] = t
    return tr


def check_component_sum(total, band_covs, rtol=1e-9):
    """total must equal the EXACT sum of the 5 per-band component covariances."""
    require_exact_bands(band_covs)
    total = np.asarray(total, dtype=float)
    s = np.zeros_like(total)
    for b in BANDS:
        Cb = np.asarray(band_covs[b], dtype=float)
        require(Cb.shape == total.shape, f"component {b} shape {Cb.shape} != total {total.shape}")
        s = s + Cb
    denom = max(1e-300, np.max(np.abs(total)))
    err = np.max(np.abs(total - s)) / denom
    require(err <= rtol, f"component sum mismatch (rel {err:.2e}) — total != sum of bands")
    return float(err)


def check_support_comparison(active_cov, support_cov):
    """Complete support comparison: both present, same shape/mask/order. Returns
    sqrt-trace ratio (active/support). Fail-closed if the support block is absent."""
    require(active_cov is not None, "active lateral block missing")
    require(support_cov is not None, "support-limited comparison block missing")
    A = np.asarray(active_cov, dtype=float); S = np.asarray(support_cov, dtype=float)
    require(A.shape == S.shape, f"active/support shape mismatch {A.shape} vs {S.shape}")
    sta = float(np.sqrt(max(0.0, np.trace(A)))); sts = float(np.sqrt(max(0.0, np.trace(S))))
    require(sts > 0, "support block has zero trace")
    return {"sqrt_tr_active": sta, "sqrt_tr_support": sts, "ratio": sta / sts}


# ---------------------------------------------------------------- deterministic projection map
def build_projection_M(edges, drop_axis, mask_high, mask_low):
    """Deterministic 5D->4D map by WIDTH-WEIGHTED marginalization of one axis.
    edges: ordered per-axis edge arrays (pt,pz,eavail,q3,W). drop_axis: axis index to
    marginalize (W=4). mask_high/mask_low: reported-bin bool masks over the full high/low
    grids (C-order). Returns dense M (n_low_reported x n_high_reported) with
    M[a,b] = width_drop[k] when high bin b decomposes to low bin a + dropped index k.
    density convention: x_low = M @ x_high, C_low = M C_high M^T."""
    nb = [np.asarray(e).size - 1 for e in edges]
    require(len(nb) == 5, "expected 5 axes")
    total_high = int(np.prod(nb))
    require(int(np.asarray(mask_high).size) == total_high, "mask_high size != high grid")
    wdrop = np.asarray(edges[drop_axis], float)[1:] - np.asarray(edges[drop_axis], float)[:-1]
    nb_low = [n for i, n in enumerate(nb) if i != drop_axis]
    total_low = int(np.prod(nb_low))
    require(int(np.asarray(mask_low).size) == total_low, "mask_low size != low grid")
    strides_h = np.array([int(np.prod(nb[i + 1:])) for i in range(5)])          # C-order strides
    strides_l = np.array([int(np.prod(nb_low[i + 1:])) for i in range(4)])
    mh = np.nonzero(np.asarray(mask_high).astype(bool))[0]
    ml = np.nonzero(np.asarray(mask_low).astype(bool))[0]
    low_pos = {int(g): r for r, g in enumerate(ml)}                              # low global -> reported row
    M = np.zeros((ml.size, mh.size), dtype=float)
    for col, g in enumerate(mh):
        midx = [(g // strides_h[i]) % nb[i] for i in range(5)]                   # 5D multi-index
        k = midx[drop_axis]
        low_multi = [midx[i] for i in range(5) if i != drop_axis]
        glow = int(np.dot(low_multi, strides_l))
        row = low_pos.get(glow)
        require(row is not None, f"high reported bin {g} maps to non-reported low bin {glow}")
        M[row, col] = wdrop[k]
    return M


# ---------------------------------------------------------------- projection gates
def project(C_high, M):
    """5D->4D (or any) projection C_low = M C_high M^T (preserves density/order)."""
    C_high = np.asarray(C_high, dtype=float); M = np.asarray(M, dtype=float)
    require(M.shape[1] == C_high.shape[0], f"M cols {M.shape[1]} != C dim {C_high.shape[0]}")
    return M @ C_high @ M.T


def check_projection_nonmutation(C_high, M, x_high, x_low_frozen, rtol_central=3e-2):
    """Enforce projected covariance validity AND central non-mutation:
    C_low = M C_high M^T is symmetric/PSD, and M @ x_high reproduces the frozen
    lower-dim central within tolerance (the projection must not mutate the central)."""
    C_low = project(C_high, M)
    stats = check_symmetric_psd(C_low)
    xin = np.asarray(x_high, dtype=float); xfr = np.asarray(x_low_frozen, dtype=float)
    proj = M @ xin
    require(proj.shape == xfr.shape, f"projected central shape {proj.shape} != frozen {xfr.shape}")
    denom = np.where(np.abs(xfr) > 0, np.abs(xfr), 1.0)
    rel = float(np.max(np.abs(proj - xfr) / denom))
    require(rel <= rtol_central, f"projection mutates central (max rel {rel:.2e})")
    stats["central_max_rel"] = rel
    return C_low, stats
