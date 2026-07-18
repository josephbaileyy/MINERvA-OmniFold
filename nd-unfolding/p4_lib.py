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
        return True


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
