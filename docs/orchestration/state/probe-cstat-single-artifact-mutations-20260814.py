"""Mutation coverage for the SINGLE-ARTIFACT validator (OI-121, one-builder world). Lane D.

The second builder was cancelled 2026-08-14, so `validate_single_artifact` is now the load-bearing
path and `compare()`'s tier 2 has no second input. A validator nobody has made fail is not
evidence -- and that applies with more force here, because with nothing to compare against these
checks are all that is left.

Each mutation names the check that MUST catch it. The BEN-181 guard applies: a mutation that did
not actually change the artifact is not scored.

SYNTHETIC ONLY. The fixture is a gaussian covariance carrying the REAL 262-cell PET mask geometry.
It is not C_stat and nothing here reads a replica product.
"""
import copy
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "nd-unfolding"))
import compare_cstat_implementations as H  # noqa: E402
import fps_provenance as FP  # noqa: E402

DEAD = ([12 * H.N_PP + 0] + [13 * H.N_PP + j for j in range(7)]
        + [14 * H.N_PP + j for j in range(15)])


def fixture():
    mask = np.ones(H.N_CELLS, bool)
    mask[DEAD] = False
    rng = np.random.default_rng(20260814)
    x = rng.normal(size=(H.N_REPLICAS, H.N_CELLS))
    x[:, DEAD] = 0.0
    c = np.cov(x, rowvar=False, ddof=1)
    c = (c + c.T) / 2.0
    c[DEAD, :] = 0.0
    c[:, DEAD] = 0.0
    ev = np.linalg.eigvalsh(c)
    lmax = float(np.max(np.abs(ev)))
    rank = int((np.abs(ev) >= 1e-10 * lmax).sum())
    return {
        "C_stat": c,
        "reported_mask": mask,
        "cv": np.where(mask, 1.0, 0.0),
        "edges_pt": H.CANONICAL_PT_EDGES,
        "edges_pparallel": H.CANONICAL_PPARALLEL_EDGES,
        "layout_fingerprint": FP.layout_fingerprint(H.CANONICAL_PT_EDGES,
                                                    H.CANONICAL_PPARALLEL_EDGES),
        "central_sha256": "a" * 64,
        "n_replicas": H.N_REPLICAS,
        "replica_ids": np.arange(H.N_REPLICAS),
        "dof": H.N_REPLICAS - 1,
        "rank_at_1em10_lambda_max": rank,
        "ravel_order": "C",
        "centering": "replica_mean",
        "units": "cm^2/nucleon/GeV^2, squared",
        "member_sha256": np.array([f"{i:064x}" for i in range(H.N_REPLICAS)]),
        "asymmetry_before_symmetrisation": 3.2e-17,
    }


BASE = fixture()


def muts():
    def drop_key():
        a = copy.deepcopy(BASE); del a["dof"]; return a

    def bad_edges():
        a = copy.deepcopy(BASE)
        e = H.CANONICAL_PT_EDGES.copy(); e[-1] = 4.5          # the PAPER grid
        a["edges_pt"] = e
        return a

    def bad_layout_fp():
        a = copy.deepcopy(BASE); a["layout_fingerprint"] = "b" * 64; return a

    def stale_layout_fp():
        # the subtle one: fingerprint correct for the PAPER grid, edges correct for FPS
        a = copy.deepcopy(BASE)
        e = H.CANONICAL_PT_EDGES.copy(); e[-1] = 4.5
        a["layout_fingerprint"] = FP.layout_fingerprint(e, H.CANONICAL_PPARALLEL_EDGES)
        return a

    def short_mask():
        a = copy.deepcopy(BASE); a["reported_mask"] = BASE["reported_mask"][:262]; return a

    def shape_mask_mismatch():
        a = copy.deepcopy(BASE)
        m = BASE["reported_mask"].copy(); m[5] = False        # mask says 261, C_stat still 285
        a["reported_mask"] = m
        return a                                              # 285x285 still legal -> must NOT fail
    def wrong_rank():
        a = copy.deepcopy(BASE); a["rank_at_1em10_lambda_max"] = 285; return a

    def dup_member():
        a = copy.deepcopy(BASE)
        m = np.asarray(BASE["member_sha256"]).copy(); m[7] = m[6]
        a["member_sha256"] = m
        return a

    def dup_id():
        a = copy.deepcopy(BASE)
        i = np.asarray(BASE["replica_ids"]).copy(); i[3] = i[2]
        a["replica_ids"] = i
        return a

    def big_asym():
        a = copy.deepcopy(BASE); a["asymmetry_before_symmetrisation"] = 4.7e-6; return a

    def bad_dof():
        a = copy.deepcopy(BASE); a["dof"] = 50; return a

    def bad_centering():
        a = copy.deepcopy(BASE); a["centering"] = "nominal"; return a

    def bad_ravel():
        a = copy.deepcopy(BASE); a["ravel_order"] = "F"; return a

    def nan_cov():
        a = copy.deepcopy(BASE)
        c = BASE["C_stat"].copy(); c[3, 3] = np.nan
        a["C_stat"] = c
        return a

    def bad_reduction():
        a = copy.deepcopy(BASE)
        idx = np.flatnonzero(BASE["reported_mask"])
        red = BASE["C_stat"][np.ix_(idx, idx)].copy()
        red[0, 0] *= 1.000001                                 # a wrong reduction
        a["C_stat_reduced"] = red
        return a

    def good_reduction():
        a = copy.deepcopy(BASE)
        idx = np.flatnonzero(BASE["reported_mask"])
        a["C_stat_reduced"] = BASE["C_stat"][np.ix_(idx, idx)].copy()
        return a

    return [
        ("S0", "unmodified (NEGATIVE CONTROL)", "nothing -- must PASS",
         lambda: copy.deepcopy(BASE)),
        ("S1", "omit required key 'dof'", "UNRESOLVED, not PASS", drop_key),
        ("S2", "paper pT grid substituted", "edges_pt_canonical", bad_edges),
        ("S3", "layout_fingerprint garbage", "layout_fingerprint_recomputed", bad_layout_fp),
        ("S4", "layout_fingerprint valid but for the WRONG grid",
         "layout_fingerprint_recomputed", stale_layout_fp),
        ("S5", "mask not full-grid length", "mask_is_full_grid_length", short_mask),
        ("S6", "mask loses a cell, C_stat still 285", "nothing -- full grid stays legal",
         shape_mask_mismatch),
        ("S7", "declared rank 285", "rank_matches_declared", wrong_rank),
        ("S8", "duplicate member sha256", "member_digests_distinct", dup_member),
        ("S9", "duplicate replica id", "replica_ids_distinct", dup_id),
        ("S10", "pre-symmetrisation asymmetry 4.7e-6", "presymmetrisation_asymmetry_is_roundoff",
         big_asym),
        ("S11", "dof = n_replicas (not n-1)", "dof_equals_n_replicas_minus_1", bad_dof),
        ("S12", "centering = 'nominal'", "centering_as_specified", bad_centering),
        ("S13", "ravel_order = 'F'", "ravel_order_C", bad_ravel),
        ("S14", "NaN in C_stat", "structure finiteness", nan_cov),
        ("S15", "C_stat_reduced does NOT match the restriction",
         "reduced_equals_full_restricted_to_mask", bad_reduction),
        ("S16", "C_stat_reduced correct", "nothing -- must PASS", good_reduction),
    ]


def _same_artifact(a, b):
    """BEN-181 guard for dicts holding arrays -- `a == b` raises on ndarray members, and an
    exception here would have silently skipped the void check rather than performing it."""
    if set(a) != set(b):
        return False
    for k in a:
        x, y = a[k], b[k]
        if isinstance(x, np.ndarray) or isinstance(y, np.ndarray):
            if not np.array_equal(np.asarray(x), np.asarray(y)):
                return False
        elif x != y:
            return False
    return True


def main():
    print("=== single-artifact validator: mutation coverage ===")
    base = H.validate_single_artifact(copy.deepcopy(BASE))
    print(f"fixture: 285x285, mask {int(BASE['reported_mask'].sum())} live, "
          f"declared rank {BASE['rank_at_1em10_lambda_max']}\n")
    if base["verdict"] != "PASS":
        print(f"*** the unmodified fixture does not pass: {base['fails']} ***")
        return 2

    rows, n_ok = {}, 0
    for sid, desc, catcher, build in muts():
        a = build()
        if sid not in ("S0",) and _same_artifact(a, BASE):
            print(f"[{sid}] *** VOID -- artifact unchanged, NOT SCORED ***")
            continue
        r = H.validate_single_artifact(a)
        must_pass = sid in ("S0", "S6", "S16")
        caught = r["verdict"] != "PASS"
        ok = (not caught) if must_pass else caught
        n_ok += ok
        rows[sid] = {"verdict": r["verdict"], "as_predeclared": ok,
                     "must_catch": catcher, "fails": r.get("fails", [])[:4],
                     "missing": r.get("missing_required")}
        print(f"[{sid:4s}] {desc:48s} -> {r['verdict']:10s} "
              f"{'as predeclared' if ok else '*** NOT AS PREDECLARED ***'}")
        if caught and r.get("fails"):
            print(f"        caught by: {', '.join(r['fails'][:3])}")

    print(f"\n=== {n_ok}/{len(rows)} as predeclared ===")
    print("\nNOTE: passing every check above still does NOT establish that the covariance VALUES "
          "are right.\nWith one builder nothing recomputes them. See predeclaration sec 4.F.")
    out = {"what": "mutation coverage for the OI-121 single-artifact C_stat validator",
           "context": "second builder cancelled 2026-08-14; this is the load-bearing path",
           "results": rows, "n_as_predeclared": n_ok, "n_mutations": len(rows),
           "all_as_predeclared": n_ok == len(rows),
           "SCOPE_LIMIT": ("no check here has power over the covariance values; see "
                           "COMPARATOR-PREDECLARATION-20260814-cstat.md sec 4.F")}
    print("\n<<<RECEIPT_JSON>>>")
    print(json.dumps(out, indent=1, sort_keys=True, default=str))
    return 0 if n_ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
