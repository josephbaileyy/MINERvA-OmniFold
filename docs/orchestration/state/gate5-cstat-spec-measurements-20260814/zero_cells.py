"""Publish the Gate-5 full-event FPS mask's zero-cell indices, with enough provenance that a set
containment test against another mask cannot silently compare two different objects.

D asked for "the FPS mask's 19 zero indices". This family measures 23. Rather than supply a number
to a question whose premise may name a different object, both counts are stated explicitly.
"""
import glob, json, os
import numpy as np

ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/replicas"
paths = sorted(glob.glob(os.path.join(ROOT, "replica_*/extraction/GATE5_REPLICA_XSEC.npz")))
X, idx, accs, pops = [], [], [], []
for p in paths:
    with np.load(p, allow_pickle=True) as z:
        X.append(np.asarray(z["xsec"], float).ravel(order="C"))
        idx.append(int(np.asarray(z["replica_index"])))
        e0 = np.asarray(z["edges_pt"], float); e1 = np.asarray(z["edges_pparallel"], float)
        tel = z["extraction_telemetry"].item()
        accs.append(tel.get("n_cells_masked_zero_acceptance"))
        pops.append(tel.get("n_cells_populated"))
F = np.stack(X); N, D = F.shape
rep = F != 0.0
n_rep = rep.sum(axis=0)

never = np.flatnonzero(n_rep == 0)
flick = np.flatnonzero((n_rep > 0) & (n_rep < N))
always = np.flatnonzero(n_rep == N)

out = {
  "artifact": "gate5-fullevent-fps-zero-cells-20260814.json",
  "lane": "C (PET)",
  "purpose": "zero-cell / reported-cell indices of the Gate-5 full-event FPS grid, for D's mask "
             "nesting test. Published with provenance because a containment test between two masks "
             "is meaningless if they index different grids.",
  "WHICH_OBJECT_THIS_IS": {
    "grid": f"{e0.size-1} x {e1.size-1} = {D} cells",
    "xsec_schema": "pet-fullevent-fps-gate5-replica-xsec-v1",
    "ravel_order": tel["bin_order"],
    "edges_pt": e0.tolist(),
    "edges_pparallel": e1.tolist(),
    "source_family": ROOT,
    "n_members_measured": N,
    "n_members_required": 50,
    "PROVISIONAL": f"measured on {N} of 50; the never-reported set can only SHRINK and the "
                   f"flicker set can only GROW as members arrive, so these are bounds, not final. "
                   f"This string is DERIVED from the member count, not typed -- an earlier draft "
                   f"hardcoded 14 and was already stale by the time it ran at {N}.",
  },
  "THE_19_VS_23_DISCREPANCY_read_this_before_using_the_indices": (
    "D asked for 'the FPS mask's 19 zero indices'. This family measures 23 never-reported cells out "
    "of 285, matching its own telemetry n_cells_no_denominator = 23 exactly. 19 would correspond to "
    "266 reported of 285, which is the count D has been using for the lgbm/GBDT mask. So either the "
    "266-cell object is NOT this FPS grid, or one of the two counts is wrong. A set-containment test "
    "run before that is resolved would compare two different objects and return a confident answer "
    "to the wrong question."
  ),
  "counts": {"n_cells": int(D), "never_reported": int(never.size),
             "reported_in_all_members": int(always.size),
             "flickering": int(flick.size),
             "union_reported": int((n_rep > 0).sum())},
  "telemetry_n_cells_masked_zero_acceptance_per_member": sorted(set(accs)),
  "telemetry_n_cells_populated_per_member": sorted(set(pops)),
  "telemetry_cross_check": {
    "n_cells": tel.get("n_cells"), "n_cells_populated": tel.get("n_cells_populated"),
    "n_cells_no_denominator": tel.get("n_cells_no_denominator"),
    "n_cells_masked_zero_acceptance": tel.get("n_cells_masked_zero_acceptance"),
    "never_reported_equals_n_cells_no_denominator": int(never.size) == tel.get("n_cells_no_denominator"),
  },
  "zero_cells_flat_indices": never.tolist(),
  "zero_cells_as_pt_pparallel": [[int(i // (e1.size-1)), int(i % (e1.size-1))] for i in never],
  "flickering_cells_flat_indices": flick.tolist(),
  "flickering_cells_n_reported": {int(i): int(n_rep[i]) for i in flick},
  "replica_indices_measured": sorted(idx),
}
print(json.dumps(out, indent=2))
