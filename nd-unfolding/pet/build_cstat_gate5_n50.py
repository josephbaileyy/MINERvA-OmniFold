#!/usr/bin/env python3
"""Build the Gate-5 PET `C_stat` from the 50 promoted coherent-replica extractions.

AUTHORITY. `docs/orchestration/SPEC-20260814-gate5-cstat-construction-v1.md`, lane C's ruled spec.
Where this file and lane B's `REQUIREMENTS-20260814-cstat-assembly-conventions.md` disagree, the SPEC
governs (`CSTAT-R6`). Built by lane B as the SOLE builder under `OI-121` after Joseph dropped the
second builder: *"Okay yeah drop the second builder"*.

WHAT THIS MAY AND MAY NOT BE CLAIMED TO BE. It may be claimed to conform to the spec and to have been
regression-compared against the established in-tree recipe. **It MAY NOT be claimed to be
independently constructed or independently verified. There was one builder.** The two-builder
machinery remains in git history and looks like it proved something; it did not.

RUNS ON A LOGIN NODE. Pure numpy + hashlib. No TensorFlow, no ROOT, no GPU, no job submission.

SPEC CLAUSES IMPLEMENTED, each asserted rather than assumed:
  CSTAT-R1a  xsec_schema == pet-fullevent-fps-gate5-replica-xsec-v1 (the nominal path's
             pet-fullevent-fps-xsec-v1 is a different object and is the likely loose-glob catch)
  CSTAT-R1b  the array is a DENSITY; width_weighting_applied = false is recorded
  CSTAT-R2a  edges bit-identical across all 50 members
  CSTAT-R2b  the bin_order STRING is asserted; order is never inferred from shape
  CSTAT-R3a  bootstrap_seed == 50000 + replica_index, per member
  CSTAT-R3b  sorted(replica_index) == range(50)
  CSTAT-R3c  rows ascending by replica_index, recorded
  CSTAT-R3d  atomic_write.is_complete on every member
  CSTAT-R3e  member_xsec_sha256 published, mutually distinct, and matched against the family manifest
  CSTAT-R3f  one producing array id
  CSTAT-D0   BOTH forms emitted: C_full (285,285) + full-grid mask, and the reduced C
  CSTAT-D0a  C == C_full[np.ix_(mask, mask)] asserted BIT-IDENTICALLY
  CSTAT-D0e  n_reported DECLARED from the mask, never inferred from diag
  CSTAT-D1   centred on the REPLICA MEAN
  CSTAT-D1a  refuses to read the NONQUOTABLE-DIAGNOSTIC nominal
  CSTAT-D2   1/(N-1), ddof=1
  CSTAT-D3a  domain is the UNION of per-member reported cells, not the intersection
  CSTAT-D3b  per-cell n_replicas_reported published
  CSTAT-D3c  quotable_mask = (n_replicas_reported == 50)
  CSTAT-D3d  the flicker count is published EVEN IF ZERO
  CSTAT-R4a  symmetry BY CONSTRUCTION; symmetrising is FORBIDDEN; max_abs_asymmetry recorded
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ND = os.path.dirname(HERE)
for _p in (HERE, ND):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from atomic_write import is_complete  # noqa: E402
import fps_provenance as fp  # noqa: E402

CSTAT_SCHEMA = "pet-fullevent-fps-gate5-cstat-v1"
XSEC_SCHEMA = "pet-fullevent-fps-gate5-replica-xsec-v1"
NOMINAL_XSEC_SCHEMA = "pet-fullevent-fps-xsec-v1"          # CSTAT-R1a: must NOT be accepted
BIN_ORDER = "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel"
N_MEMBERS = 50
SHAPE2D = (15, 19)
N_CELLS = 285
SEED_BASE = 50000
FORBIDDEN_SUBSTR = "NONQUOTABLE-DIAGNOSTIC"                # CSTAT-D1a


class SpecViolation(SystemExit):
    pass


def die(clause, msg):
    raise SpecViolation(f"[cstat] {clause} VIOLATED: {msg}")


def sha256_file(path, chunk=16 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as s:
        for b in iter(lambda: s.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def scalar(store, key):
    v = store[key]
    if isinstance(v, np.ndarray) and v.ndim == 0:
        v = v.item()
        return v.decode() if isinstance(v, bytes) else v
    return v


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True,
                    help="GATE5_EXTRACTION_FAMILY_MANIFEST json; the authoritative member list")
    ap.add_argument("--root", required=True, help="family root containing replicas/")
    ap.add_argument("--out", required=True, help="output npz")
    ap.add_argument("--receipt", required=True, help="output receipt json")
    a = ap.parse_args()

    prov = {"clauses": {}, "measured": {}}

    def ok(clause, note=""):
        prov["clauses"][clause] = {"status": "PASS", "note": note}

    # ---------- the manifest is the member list; its verdict is re-derived, not trusted ----------
    man = json.load(open(a.manifest))
    if man.get("verdict") != "GATE5_EXTRACTION_FAMILY_COMPLETE_PASS":
        die("precondition-2", f"family verdict is {man.get('verdict')!r}")
    if man.get("subset_selected") is not False:
        die("precondition-2", "subset_selected is not False")
    if man.get("C_stat") is not None:
        die("precondition-2", "manifest already carries a C_stat")
    members = man["members"]
    if len(members) != N_MEMBERS or man.get("declared_inventory") != N_MEMBERS:
        die("precondition-1", f"{len(members)} members / declared {man.get('declared_inventory')}")
    if man.get("members_present_and_passing") != N_MEMBERS or man.get("members_failing"):
        die("precondition-2", "members_present_and_passing != 50 or members_failing non-empty")
    if any(m.get("verdict") != "PASS" or m.get("failures") for m in members):
        die("precondition-2", "a member is not PASS with empty failures")
    array_id = str(man["source_array_job_id"])
    ok("precondition-1/2", f"verdict re-derived from operands; array {array_id}")
    ok("CSTAT-R3f", f"one producing array id: {array_id}")

    # ---------- read the 50 members in ASCENDING replica_index ----------
    members = sorted(members, key=lambda m: int(m["replica_index"]))
    idxs = [int(m["replica_index"]) for m in members]
    if sorted(idxs) != list(range(N_MEMBERS)):
        die("CSTAT-R3b", f"replica_index set is not range(50): {idxs[:5]}...")
    ok("CSTAT-R3b", "replica_index is exactly range(50), each once")
    ok("CSTAT-R3c", "rows assembled ascending by replica_index")

    F = np.empty((N_MEMBERS, N_CELLS), dtype=np.float64)
    digests, seeds, totals = [], [], []
    edges_pt = edges_pp = None

    for row, m in enumerate(members):
        idx = int(m["replica_index"])
        path = os.path.join(a.root, "replicas", f"replica_{idx:02d}",
                            "extraction", "GATE5_REPLICA_XSEC.npz")
        if FORBIDDEN_SUBSTR in path:
            die("CSTAT-D1a", f"refusing the non-quotable nominal: {path}")
        if not os.path.exists(path):
            die("CSTAT-R1", f"member {idx} absent: {path}")
        if not is_complete(path):
            die("CSTAT-R3d", f"member {idx} has no atomic_write completeness marker: {path}")

        d = sha256_file(path)
        if d != m["xsec_sha256"]:
            die("CSTAT-R3e", f"member {idx} file digest {d[:16]} != manifest {m['xsec_sha256'][:16]}")
        digests.append(d)

        with np.load(path, allow_pickle=True) as z:
            sch = scalar(z, "xsec_schema")
            if sch == NOMINAL_XSEC_SCHEMA:
                die("CSTAT-R1a", f"member {idx} is a NOMINAL-path artifact ({sch}), not a replica")
            if sch != XSEC_SCHEMA:
                die("CSTAT-R1a", f"member {idx} xsec_schema {sch!r} != {XSEC_SCHEMA!r}")
            ridx = int(scalar(z, "replica_index"))
            seed = int(scalar(z, "bootstrap_seed"))
            if ridx != idx:
                die("CSTAT-R3", f"member {idx} carries replica_index {ridx}")
            if seed != SEED_BASE + ridx:
                die("CSTAT-R3a", f"member {idx}: seed {seed} != {SEED_BASE} + {ridx}")
            seeds.append(seed)

            telem = scalar(z, "extraction_telemetry")
            if isinstance(telem, np.ndarray):
                telem = telem.item()
            bo = (telem or {}).get("bin_order") if isinstance(telem, dict) else None
            if bo != BIN_ORDER:
                die("CSTAT-R2b", f"member {idx} bin_order {bo!r} != the pinned string")

            x = np.asarray(z["xsec"], dtype=np.float64)
            if x.shape != SHAPE2D:
                die("CSTAT-R1", f"member {idx} xsec shape {x.shape} != {SHAPE2D}")
            if not np.isfinite(x).all():
                die("CSTAT-R1", f"member {idx} xsec is not finite")
            if (x < 0).any():
                die("CSTAT-R1", f"member {idx} xsec has negative cells")
            F[row] = x.ravel(order="C")

            ept = np.asarray(z["edges_pt"], float)
            epp = np.asarray(z["edges_pparallel"], float)
            if edges_pt is None:
                edges_pt, edges_pp = ept, epp
            else:
                if not (np.array_equal(ept, edges_pt) and np.array_equal(epp, edges_pp)):
                    die("CSTAT-R2a", f"member {idx} edges are not bit-identical to member 0's")
            totals.append(float(scalar(z, "total_sigma_cm2_per_nucleon")))

    ok("CSTAT-R1a", f"all 50 carry {XSEC_SCHEMA}")
    ok("CSTAT-R2b", "the pinned bin_order string asserted on all 50; order never inferred")
    ok("CSTAT-R3a", f"bootstrap_seed == {SEED_BASE} + replica_index on all 50")
    ok("CSTAT-R3d", "atomic_write completeness marker present on all 50")
    if len(set(digests)) != N_MEMBERS:
        die("CSTAT-R3e", "member xsec digests are not mutually distinct")
    ok("CSTAT-R3e", "50 distinct xsec file digests, each matched against the family manifest")
    ok("CSTAT-R2a", "edges bit-identical across all 50")

    # edges must be the canonical extended FPS grid, not the paper grid (CSTAT-R2)
    fp_layout = fp.layout_fingerprint(edges_pt.tolist(), edges_pp.tolist())
    if fp_layout != fp.layout_fingerprint():
        die("CSTAT-R2", "member edges are not the canonical extended-FPS 285-cell layout")
    ok("CSTAT-R2", f"layout_fingerprint {fp_layout[:16]} == canonical extended FPS")

    # ---------- CSTAT-D3: the domain is the UNION of per-member reported cells ----------
    reported_per_member = F > 0.0
    n_replicas_reported_full = reported_per_member.sum(axis=0).astype(np.int64)
    union_mask = n_replicas_reported_full >= 1
    inter_mask = n_replicas_reported_full == N_MEMBERS
    n_union, n_inter = int(union_mask.sum()), int(inter_mask.sum())
    flicker = np.flatnonzero(union_mask & ~inter_mask).astype(np.int64)
    never = np.flatnonzero(n_replicas_reported_full == 0).astype(np.int64)
    ok("CSTAT-D3a", f"UNION domain: {n_union} cells (intersection would be {n_inter})")
    ok("CSTAT-D3d", f"flicker cells published even if zero: {flicker.size}")

    mask = union_mask
    n_reported = int(mask.sum())                      # CSTAT-D0e: DECLARED from the mask
    cell_index = np.flatnonzero(mask).astype(np.int64)
    Fr = F[:, mask]

    # ---------- CSTAT-D1 / D2: replica mean, 1/(N-1) ----------
    mean = Fr.mean(axis=0)
    Z = Fr - mean
    C = (Z.T @ Z) / (Fr.shape[0] - 1)
    ok("CSTAT-D1", "centred on the replica mean")
    ok("CSTAT-D2", "normalization 1/(N-1), ddof=1")

    # CSTAT-R4a: symmetry BY CONSTRUCTION. Do NOT symmetrise. Measure and publish.
    max_abs_asym = float(np.abs(C - C.T).max())
    ok("CSTAT-R4a", f"NOT symmetrised; max|C-C^T| = {max_abs_asym:.3e}")

    # ---------- CSTAT-D0: both forms ----------
    C_full = np.zeros((N_CELLS, N_CELLS), dtype=np.float64)
    C_full[np.ix_(cell_index, cell_index)] = C
    reduction = C_full[np.ix_(mask, mask)]
    reduction_is_exact = bool(np.array_equal(C, reduction)
                              and C.dtype == reduction.dtype
                              and C.tobytes() == reduction.tobytes())
    if not reduction_is_exact:
        die("CSTAT-D0a", "C != C_full[ix_(mask,mask)] bit-identically")
    ok("CSTAT-D0a", "C == C_full[np.ix_(mask,mask)] BIT-IDENTICAL (tobytes compared)")
    ok("CSTAT-D0", f"both forms emitted: C {C.shape}, C_full {C_full.shape}, mask {mask.shape}")

    diag = np.diag(C)
    zero_var = np.flatnonzero(diag == 0.0).astype(np.int64)
    n_reported_if_inferred = int((diag > 0).sum())
    ok("CSTAT-D0e", f"n_reported DECLARED from mask = {n_reported}; "
                    f"inferring from diag>0 would have given {n_reported_if_inferred}")

    nrr = n_replicas_reported_full[mask]
    quotable = (nrr == N_MEMBERS)

    payload = {
        "cstat_schema": np.asarray(CSTAT_SCHEMA),
        "C": C, "C_full": C_full, "reported_mask": mask,
        "n_reported": np.asarray(n_reported, np.int64),
        "layout_fingerprint": np.asarray(fp_layout),
        "dof": np.asarray(N_MEMBERS - 1, np.int64),
        "centering": np.asarray("replica_mean"),
        "centring": np.asarray("replica_mean"),
        "ravel_order": np.asarray("C"),
        "max_abs_asymmetry": np.asarray(max_abs_asym, np.float64),
        "asymmetry_before_symmetrisation": np.asarray(max_abs_asym, np.float64),
        "reduction_is_exact": np.asarray(reduction_is_exact),
        "zero_variance_cells": zero_var,
        "slurm_array_job_id": np.asarray(array_id),
        "mean": mean,
        "n_members": np.asarray(N_MEMBERS, np.int64),
        "D": np.asarray(n_reported, np.int64),
        "cell_index": cell_index,
        "n_replicas_reported": nrr.astype(np.int64),
        "quotable_mask": quotable,
        "replica_index": np.asarray(idxs, np.int64),
        "bootstrap_seed": np.asarray(seeds, np.int64),
        "edges_pt": edges_pt, "edges_pparallel": edges_pp,
        "bin_order": np.asarray(BIN_ORDER),
        "member_xsec_sha256": np.asarray(digests),
        "normalization": np.asarray("1/(N-1)"),
        "width_weighting_applied": np.asarray(False),
        "rank_treatment": np.asarray("UNDECLARED — see CSTAT-O1"),
    }
    np.savez_compressed(a.out, **payload)

    ev = np.linalg.eigvalsh(0.5 * (C + C.T))
    prov["measured"] = {
        "n_members": N_MEMBERS, "dof": N_MEMBERS - 1,
        "D_n_reported_from_mask": n_reported,
        "n_reported_if_inferred_from_diag": n_reported_if_inferred,
        "union_domain": n_union, "intersection_domain": n_inter,
        "flicker_cells_count": int(flicker.size),
        "flicker_cells": flicker.tolist(),
        "never_reported_cells_count": int(never.size),
        "never_reported_cells": never.tolist(),
        "n_replicas_reported_histogram": {str(k): int(v) for k, v in
                                          zip(*np.unique(nrr, return_counts=True))},
        "quotable_cells": int(quotable.sum()),
        "max_abs_asymmetry": max_abs_asym,
        "reduction_is_exact": reduction_is_exact,
        "trace": float(np.trace(C)), "sqrt_trace": float(np.sqrt(max(np.trace(C), 0.0))),
        "min_eig": float(ev.min()), "max_eig": float(ev.max()),
        "min_over_max_eig": float(ev.min() / max(abs(ev.max()), 1e-300)),
        "rank_at_1em10_lambda_max": int((ev > ev.max() * 1e-10).sum()),
        "zero_variance_cells_count": int(zero_var.size),
        "median_relative_sigma": float(np.median(
            np.sqrt(np.clip(diag, 0, None))[mean > 0] / mean[mean > 0])),
        "total_sigma_per_member_mean": float(np.mean(totals)),
        "total_sigma_per_member_relative_sd": float(np.std(totals, ddof=1) / np.mean(totals)),
        "layout_fingerprint": fp_layout,
        "slurm_array_job_id": array_id,
        "out_sha256": sha256_file(a.out),
    }
    prov["out"] = os.path.abspath(a.out)
    prov["manifest"] = os.path.abspath(a.manifest)
    prov["manifest_sha256"] = sha256_file(a.manifest)
    prov["member_xsec_sha256"] = digests
    prov["schema"] = CSTAT_SCHEMA
    with open(a.receipt, "w") as f:
        json.dump(prov, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps(prov["measured"], indent=1, sort_keys=True))
    print(f"[cstat] wrote {a.out}")
    print(f"[cstat] receipt {a.receipt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
