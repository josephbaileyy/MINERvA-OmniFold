"""Mutation coverage for the C_stat comparator (OI-121). Lane D.

For every check in compare_cstat_implementations.py: the perturbation that must make it fail.
Run BEFORE the harness meets a real artifact. A check nobody has made fail is not evidence --
BEN-173 (no control), BEN-180 (one-sided control), BEN-185 (never executed).

TWO DISCIPLINES, both learned the hard way on this campaign:

  1. EVERY mutation first asserts it ACTUALLY CHANGED THE ARRAY. I filed BEN-181 against
     myself for a mutation that matched only a docstring and therefore tested nothing while
     reporting a pass. `_mutated_for_real` is that finding turned into a guard.

  2. THE TOLERANCE IS TESTED FROM BOTH SIDES. M6a must fail just above it and M6b must pass
     just below it. A threshold demonstrated only in the failing direction is unfalsifiable in
     the passing direction, which is where a too-loose tolerance hides.

SYNTHETIC DATA ONLY. The fixture is a gaussian draw with the REAL object's zero-cell geometry
(the 23-cell high-pT / low-p_parallel staircase measured from the nominal) so that the
free-agreement inflation is measurable rather than asserted. It is not C_stat and this file
constructs no covariance from any replica product.
"""
import json
import sys
import pathlib

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import compare_cstat_implementations as H  # noqa: E402

# The 23 cells that are zero in the nominal extraction, measured directly from
# NONQUOTABLE-DIAGNOSTIC.xsec.slurm-56527676.npz: row 12 col 0; row 13 cols 0-6;
# row 14 cols 0-14. One contiguous run per pT row, the high-pT / low-p_parallel corner.
DEAD_CELLS = ([12 * H.N_PP + 0]
              + [13 * H.N_PP + j for j in range(7)]
              + [14 * H.N_PP + j for j in range(15)])


def fixture():
    """A 50 x 285 gaussian draw with the real dead-cell geometry imposed, then its covariance.
    Synthetic. Never a replica product."""
    rng = np.random.default_rng(20260814)
    x = rng.normal(size=(H.N_REPLICAS, H.N_CELLS))
    x[:, DEAD_CELLS] = 0.0
    c = np.cov(x, rowvar=False, ddof=1)
    c = (c + c.T) / 2.0                       # exact symmetry; np.cov is symmetric to ~eps
    c[np.ix_(DEAD_CELLS, DEAD_CELLS)] = 0.0
    c[DEAD_CELLS, :] = 0.0
    c[:, DEAD_CELLS] = 0.0
    return c


def artifact(cov, **over):
    mask = np.ones(H.N_CELLS, bool)
    mask[DEAD_CELLS] = False
    a = {"_path": "<synthetic>", "_sha256": "n/a", "_missing_required": [],
         "C_stat": cov, "ravel_order": H.EXPECTED_RAVEL_ORDER,
         "reported_mask": mask, "layout_fingerprint": "f" * 64,
         "edges_pt": H.CANONICAL_PT_EDGES, "edges_pparallel": H.CANONICAL_PPARALLEL_EDGES,
         "n_replicas": H.N_REPLICAS, "dof": H.N_REPLICAS - 1,
         "centering": H.EXPECTED_CENTERING,
         "replica_ids": np.arange(H.N_REPLICAS),
         "member_sha256": np.array([f"{i:064x}" for i in range(H.N_REPLICAS)])}
    a.update(over)
    return a


def _mutated_for_real(base, mutated):
    """BEN-181 guard. A mutation that did not mutate produces a check that 'passed' against
    nothing. Refuse to score it."""
    if isinstance(mutated, np.ndarray) and isinstance(base, np.ndarray):
        if base.shape == mutated.shape and base.dtype == mutated.dtype:
            return not np.array_equal(base, mutated)
    return True                                # shape/dtype/metadata mutations are self-evident


C = fixture()
BASE = artifact(C)


def perm_matrix_indices():
    """C-order -> F-order re-flatten, as a permutation of the 285 cell indices.
    k = i*N_PP + j  ->  j*N_PT + i. Symmetry, PSD, rank, trace and the eigenvalue spectrum
    all survive this exactly; only a per-cell comparison sees it."""
    p = np.empty(H.N_CELLS, dtype=int)
    for i in range(H.N_PT):
        for j in range(H.N_PP):
            p[i * H.N_PP + j] = j * H.N_PT + i
    return p


def mutations():
    """(id, description, predeclared_catcher, builder) -> builder returns the B artifact."""
    def m1():
        return artifact(C.reshape(H.N_PT, H.N_PP, H.N_PT, H.N_PP))

    def m2():
        return artifact(C.astype(np.float32))

    def m3():
        p = perm_matrix_indices()
        return artifact(C[np.ix_(p, p)])

    def m4():
        return artifact(C * (49.0 / 50.0))

    def m5():
        b = C.copy()
        i, j = 3, 40                            # both live cells, off-diagonal
        b[i, j] = -b[i, j]
        b[j, i] = -b[j, i]
        return artifact(b)

    def _nudge(k):
        b = C.copy()
        i, j = 5, 60
        scale = np.sqrt(C[i, i] * C[j, j])
        d = k * H.TOL_CORR_ABS * scale
        b[i, j] += d
        b[j, i] += d
        return artifact(b)

    def m6a():
        return _nudge(1.1)

    def m6b():
        return _nudge(0.9)

    def m7():
        b = C.copy()
        b[7, 7] = np.nan
        return artifact(b)

    def m8():
        return artifact(C + 1e-9 * np.eye(H.N_CELLS))

    def m9():
        b = C.copy()
        row = 100                               # a live cell, nonzero in A
        b[row, :] = 0.0
        b[:, row] = 0.0
        return artifact(b)

    def m10():
        p = np.arange(H.N_CELLS)
        p[10], p[200] = p[200], p[10]           # two live cells swapped, rows AND cols
        return artifact(C[np.ix_(p, p)])

    def m11():
        a = artifact(C.copy())
        a["ravel_order"] = "F"
        return a

    def m12():
        a = artifact(C.copy())
        e = H.CANONICAL_PT_EDGES.copy()
        e[-1] = 4.5                             # the PAPER grid top edge
        a["edges_pt"] = e
        return a

    def m13():
        a = artifact(C.copy())
        s = np.arange(H.N_REPLICAS)
        s[17] = s[16]                           # a duplicated replica id
        a["replica_ids"] = s
        return a

    def m14():
        a = artifact(C.copy())
        m = np.array([f"{i:064x}" for i in range(H.N_REPLICAS)])
        m[23] = "deadbeef" * 8                  # one member from a different family
        a["member_sha256"] = m
        return a

    def m15():
        a = artifact(C.copy())
        del a["dof"]
        a["_missing_required"] = ["dof"]
        return a

    return [
        ("M0", "B := A exactly (NEGATIVE CONTROL)", "nothing -- must AGREE",
         lambda: artifact(C.copy())),
        ("M1", "reshape B to (15,19,15,19)", "tier0 shape", m1),
        ("M2", "cast B to float32", "tier0 dtype", m2),
        ("M3", "re-flatten B in F-order (C-vs-F convention)", "tier2 ONLY", m3),
        ("M4", "B *= 49/50  (ddof=0 vs ddof=1)", "tier2 + tier3", m4),
        ("M5", "flip sign of one off-diagonal pair", "tier2", m5),
        ("M6a", "nudge one element by 1.1 x TOL", "tier2 (tolerance bites above)", m6a),
        ("M6b", "nudge one element by 0.9 x TOL", "NOTHING -- must AGREE", m6b),
        ("M7", "inject NaN on the diagonal", "tier1 finiteness", m7),
        ("M8", "B += 1e-9 * I  (quiet regularisation)", "tier1 rank + tier2", m8),
        ("M9", "zero one structurally-NONZERO row/col", "tier2 exact-zero mismatch", m9),
        ("M10", "swap two live bins consistently (rows AND cols)", "tier2 ONLY", m10),
        ("M11", "declare ravel_order = F", "tier0 ravel_order", m11),
        ("M12", "substitute the PAPER pT grid top edge", "tier0 edges", m12),
        ("M13", "duplicate a replica id", "tier4 ids distinct", m13),
        ("M14", "one member sha256 from a different family", "tier4 member lists", m14),
        ("M15", "omit a REQUIRED key (dof)", "tier0 -> UNRESOLVED, not AGREE", m15),
    ]


def which_tiers_fired(rep):
    """Attribute the catch, so 'tier2 ONLY' claims are MEASURED and not asserted."""
    if rep["verdict"] == "UNRESOLVED":
        return ["tier0(UNRESOLVED)"]
    fired = []
    if rep["tier0_identity"]["fails"]:
        fired.append("tier0")
    if rep["tier1_structure_A"]["fails"] or rep["tier1_structure_B"]["fails"]:
        fired.append("tier1")
    if rep["tier2_elementwise"]["fails"]:
        fired.append("tier2")
    if rep["tier3_derived"]["fails"]:
        fired.append("tier3")
    if rep["tier4_inputs"]["fails"]:
        fired.append("tier4")
    return fired


def scalar_invariants(rep):
    """For M3/M10: which SCALAR summaries were blind? Measured, not claimed."""
    if rep["verdict"] == "UNRESOLVED":
        return None
    t3 = rep["tier3_derived"]
    if "skipped" in t3:
        return {"skipped": t3["skipped"]}
    return {
        "trace_rel_diff": t3["trace"]["relative_difference"],
        "eigenvalue_spectrum_worst_rel":
            t3["eigenvalue_spectrum_worst_abs_over_lambda_max"],
        "per_bin_sigma_worst_rel": t3["per_bin_sigma_worst_relative"]["value"],
        "trace_blind": t3["trace"]["relative_difference"] <= H.TOL_DIAG_REL,
        "eigenvalues_blind":
            t3["eigenvalue_spectrum_worst_abs_over_lambda_max"] <= H.TOL_DIAG_REL,
    }


def main():
    print("=== C_stat comparator: mutation coverage ===")
    vc = H.verify_constants_against_loader()
    print(f"frozen-grid copy vs loader: ok={vc['ok']} "
          f"(pt={vc.get('pt_matches')} pparallel={vc.get('pparallel_matches')})")
    if not vc["ok"]:
        print(f"*** {vc.get('why')} *** -- refusing to score mutations against a stale grid")
        return 2
    # Positive control for the guard itself: a stale-grid detector that has never detected a
    # stale grid is not evidence. Point it at a synthesised loader with one edge moved.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td) / "nd-unfolding" / "pet"
        d.mkdir(parents=True)
        (d / "fullevent_fps_dataloader.py").write_text(
            "import numpy as np\n"
            "CANONICAL_PT_EDGES = np.array(\n"
            "    [0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5,\n"
            "     2.5, 4.5, 25.0], dtype=float)\n"          # 30.0 -> 25.0
            "CANONICAL_PPARALLEL_EDGES = np.array(\n"
            "    [0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0,\n"
            "     10.0, 15.0, 20.0, 40.0, 60.0, 120.0], dtype=float)\n")
        ctl = H.verify_constants_against_loader(td)
    print(f"  guard control (one pT edge moved 30.0 -> 25.0): detected={not ctl['ok']} "
          f"{'as predeclared' if not ctl['ok'] else '*** DID NOT FIRE ***'}")
    if ctl["ok"]:
        print("*** the stale-grid guard cannot fail; it is not evidence. Refusing to score. ***")
        return 2
    print(f"fixture: synthetic 50 x 285 gaussian, {len(DEAD_CELLS)} dead cells "
          f"(real nominal geometry), cov ddof=1")
    live = H.N_CELLS - len(DEAD_CELLS)
    print(f"live cells: {live}   free (0==0) entries: "
          f"{H.N_CELLS ** 2 - live ** 2} of {H.N_CELLS ** 2} "
          f"({100.0 * (H.N_CELLS ** 2 - live ** 2) / H.N_CELLS ** 2:.1f}%)\n")

    rows, results = [], {}
    for mid, desc, predeclared, build in mutations():
        b = build()
        void = None
        # The key name here MUST track REQUIRED_KEYS. When "cov" was renamed to "C_stat" this
        # line still said b.get("cov") -> None, so `void` stayed None and the BEN-181 guard
        # silently stopped running: a rename disabled the very check that exists to catch
        # mutations that do not mutate. Hence the assertion below rather than a soft get().
        assert "C_stat" in b, "artifact key renamed; the void guard would silently no-op"
        if isinstance(b.get("C_stat"), np.ndarray):
            void = not _mutated_for_real(C, b["C_stat"])
        # metadata-only mutations legitimately leave cov untouched
        if void and mid not in ("M0", "M11", "M12", "M13", "M14", "M15"):
            print(f"[{mid}] *** VOID MUTATION -- the array did not change. NOT SCORED. ***")
            rows.append((mid, desc, predeclared, "VOID", "", ""))
            continue

        rep = H.compare(BASE, b)
        fired = which_tiers_fired(rep)
        must_agree = mid in ("M0", "M6b")
        caught = rep["verdict"] != "AGREE"
        ok = (not caught) if must_agree else caught
        results[mid] = {"verdict": rep["verdict"], "tiers_fired": fired,
                        "as_predeclared": ok, "predeclared": predeclared,
                        "scalar_invariants": scalar_invariants(rep)}
        flag = "as predeclared" if ok else "*** NOT AS PREDECLARED ***"
        print(f"[{mid:4s}] {desc:52s} -> {rep['verdict']:10s} "
              f"fired={','.join(fired) or 'none':22s} {flag}")
        rows.append((mid, desc, predeclared, rep["verdict"], ",".join(fired), flag))

    # --- the two claims that justify the element-wise design, MEASURED ------------------
    print("\n-- are M3 / M10 really invisible to the scalar summaries? --")
    for mid in ("M3", "M10"):
        si = results.get(mid, {}).get("scalar_invariants")
        if si:
            print(f"  {mid}: trace rel={si['trace_rel_diff']:.3e} blind={si['trace_blind']} | "
                  f"eig rel={si['eigenvalue_spectrum_worst_rel']:.3e} "
                  f"blind={si['eigenvalues_blind']} | "
                  f"per-bin sigma rel={si['per_bin_sigma_worst_rel']:.3e}")

    # --- M9: would the GLOBAL agreement fraction have hidden it? ------------------------
    b9 = [m for m in mutations() if m[0] == "M9"][0][3]()
    r9 = H.compare(BASE, b9)
    t2 = r9["tier2_elementwise"]
    print(f"\n-- M9 dilution check --\n  global agreement     = "
          f"{t2['agreement_fraction_global']:.6f}\n  nontrivial agreement = "
          f"{t2['agreement_fraction_nontrivial']:.6f}\n  exact 0-vs-nonzero   = "
          f"{t2['n_exact_zero_vs_nonzero_mismatch']}")

    n_ok = sum(1 for v in results.values() if v["as_predeclared"])
    print(f"\n=== {n_ok}/{len(results)} mutations behaved as predeclared ===")

    out = {
        "what": "mutation coverage for the OI-121 C_stat comparator harness",
        "harness": "docs/orchestration/state/compare_cstat_implementations.py",
        "predeclaration": "docs/orchestration/COMPARATOR-PREDECLARATION-20260814-cstat.md",
        "fixture": {"synthetic": True, "shape": [H.N_REPLICAS, H.N_CELLS],
                    "dead_cells": len(DEAD_CELLS), "live_cells": live,
                    "dead_cell_geometry_source":
                        "measured from NONQUOTABLE-DIAGNOSTIC.xsec.slurm-56527676.npz"},
        "tolerances": {"TOL_CORR_ABS": H.TOL_CORR_ABS, "TOL_DIAG_REL": H.TOL_DIAG_REL},
        "results": results,
        "n_as_predeclared": n_ok, "n_mutations": len(results),
        "all_as_predeclared": n_ok == len(results),
        "comparator_built_no_covariance": True,
    }
    print("\n<<<RECEIPT_JSON>>>")
    print(json.dumps(out, indent=1, sort_keys=True, default=str))
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
