#!/usr/bin/env python3
"""OI-126 TEST 2 -- the target-level spatial probe named in
`RULING-20260817-lanec-oi126-branch-set-not-exhaustive.md` Section 4.

THIS FILE EXISTS TO MAKE TEST 2's RUNNABILITY A FACT RATHER THAN A PARAGRAPH, per `BEN-384`: an item's
cost is a property of where its code lives, and the ruling explicitly refuses to cost Test 2 from prose.
Running it is a SEPARATE authorisation from writing it; nothing here has been executed against real
inputs, and every input is fail-closed so an unauthorised run cannot silently produce a partial number.

WHAT IT WOULD MEASURE. Histogram the 50 per-replica refined targets and the certified Gate-2 nominal
target into the extended-FPS reco grid using the loader's own canonical edges, then ask whether the
TARGET-LEVEL gap reproduces the measured spatial structure:
    median z below 6 GeV     -0.128
    in band p_par cols 10-15 +3.555
    above 20 GeV             -1.828
(the three numbers are supplied by `--expect-*` and are NOT hardcoded here, so this file makes no claim
about them; it reports what it finds beside what it was told to compare against.)

WHAT IT DOES *NOT* SETTLE, AND THIS IS LOAD-BEARING FOR ANYONE READING ITS OUTPUT. Section 4 designed
Test 2 to adjudicate branch (c), and (c) is ALREADY REFUTED by lane D independently of this probe (the
mass-addition limb is null with power at +0.000179%, 0.03 SE, 19 of 50 above; the redistribution limb
needs a nonlinearity inactive in the band, 0 of 86 cells). **So a PASS here does not establish (c) and a
FAIL here does not refute it -- (c) is already decided.** Test 2's only remaining value is LOCALISATION:
the 2026-08-15 push-versus-extraction split localised the band deficit to TRAINING, but push and
extraction are BOTH downstream of the targets, so nothing on the record probes the layer above them.
This is that probe, and that is the only inference its output supports.

§5 QUOTABILITY, ADDED 2026-08-20. `RULING-20260819-lanec-reconstructed-cell-assignment-admissible.md`
§5 rules that a Test 2 number is quotable ONLY alongside the `-1` count AND its weight share, reported
PER ARM, and that a count alone is insufficient. This file previously reported ONE POOLED COUNT and no
share -- and because the assignment comes from the shared reco kinematics, that count is arm-invariant
by construction, so it was precisely the half that cannot discriminate between arms. Any number this
probe produced would therefore have been unquotable under its own governing ruling. See
`out_of_grid_stats` and the `QUOTABILITY_out_of_grid_by_arm` block.

NO UNFOLDING, NO TRAINING, NO GPU, NO WRITE INSIDE THE PROMOTED ARM. It reads the 51 target arrays and
the source dump's measured kinematics, and writes one JSON to a path the caller names.

Run (all paths required, no defaults -- a default path is how a probe silently reads the wrong tree):
    python3 probe_oi126_test2_target_level_spatial.py \
        --family-root   /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50 \
        --nominal-target REPO/nd-unfolding/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy \
        --nominal-target-sha 544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9 \
        --source-npz    /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz \
        --reconciliation docs/orchestration/state/gate5-target-promotion-evidence-56873858/GATE5_TARGET_FAMILY_RECONCILIATION.slurm-56873858.json \
        --out           /pscratch/.../OI126-TEST2-<jobid>.json \
        --expect-below -0.128 --expect-band 3.555 --expect-above -1.828
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# The grid and its guard come from the PINNED loader by import, never restated here: a copy of the edges
# would be true when written and silent afterwards, and the guard is the measurement-domain authority.
import fullevent_fps_dataloader as fe  # noqa: E402

N_REPLICAS = 50                      # pinned by SEED_POLICY gate5-cstat-n50-v1; not caller-supplied
SEED0 = 50000                        # replica seed = SEED0 + index (launcher :48)
TARGET_LEAF = Path("target") / "GATE5_REPLICA_TARGET.npy"   # launcher :33/:51


def die(msg, code=1):
    raise SystemExit(f"[oi126-test2] FAIL-CLOSED: {msg}")


def sha256_file(p, *, chunk=1 << 22):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def require_file(p, what):
    p = Path(p)
    if not p.is_file() or p.is_symlink():
        die(f"{what} is absent, or is a symlink, at {p}. This probe does not substitute, "
            f"reconstruct or skip an input -- if the array is not visible from HERE, the answer is "
            f"that this probe is not runnable here, which is itself the finding.")
    return p


def cell_index(pt, ppar):
    """Per-event extended-FPS cell index, built from the PINNED loader's canonical edges.

    WHY THIS IS WRITTEN HERE RATHER THAN IMPORTED, and it is the single most important fact this file
    records: THE LOADER HAS NO PER-EVENT RECO-GRID ASSIGNMENT TO IMPORT. `build_fullevent_loaders`
    returns `coord_reco`, and `build_reco_cloud` (`fullevent_fps_dataloader.py:136-177`) shows that is
    the tuple `(1, 2)` -- the point cloud's (pos, z) KNN NEIGHBOURHOOD COLUMNS, not a bin. The binned
    refiner `stay_positive_refine_binned(signed_w, cell, n_cells)` (`:628`) RECEIVES `cell` from its
    caller and does not derive it, and the production nominal does not use it at all: it refines over
    FEATURES via `refine_signed_measured` / `learned_stay_positive_refiner` (`:667`, `:708`).
    So the ruling's phrase "the loader's own per-event assignment" names something that does not exist
    as a callable. The faithful reconstruction is: the loader's OWN canonical edges, its OWN guard, and
    `digitize` -- which is what this is. Any reviewer should check this function first.
    """
    fe.assert_extended_fps_edges(fe.CANONICAL_PT_EDGES, fe.CANONICAL_PPARALLEL_EDGES)
    ept = np.asarray(fe.CANONICAL_PT_EDGES, float)
    epp = np.asarray(fe.CANONICAL_PPARALLEL_EDGES, float)
    n_pt, n_pp = ept.size - 1, epp.size - 1
    ipt = np.digitize(np.asarray(pt, float), ept) - 1
    ipp = np.digitize(np.asarray(ppar, float), epp) - 1
    inside = (ipt >= 0) & (ipt < n_pt) & (ipp >= 0) & (ipp < n_pp)
    # OUT-OF-GRID EVENTS ARE REPORTED, NEVER CLIPPED. `np.clip` would pile the overflow into the edge
    # bins -- and the edge bins ([4.5,30] in pT, [0,0.75] and [20,120] in p_par) are exactly the catch
    # bins the FPS grid was extended to hold, so clipping would corrupt the two regions the -1.828
    # comparison is about.
    cell = np.where(inside, ipt * n_pp + ipp, -1)
    return cell, int(n_pt * n_pp), inside


def out_of_grid_stats(w, inside, miss):
    """The §5 QUOTABILITY payload for ONE arm: the `-1` count AND its weight share.

    `RULING-20260819-lanec-reconstructed-cell-assignment-admissible.md` §5 rules that a Test 2 number
    is quotable ONLY alongside these, per arm, and that a COUNT ALONE IS INSUFFICIENT -- "the comparison
    is over weighted mass, so a small count carrying large weight is the case that matters".

    WHY THIS IS PER ARM WHEN THE COUNT IS NOT. The cell assignment is reconstructed from the SHARED reco
    kinematics of the source dump, so `inside` is identical for every arm and the COUNTS below are
    arm-invariant BY CONSTRUCTION. The WEIGHT SHARE is not: each arm is a different set of per-event
    weights over the same events. So the count is the one quantity that cannot discriminate between arms
    and the share is the one that can -- which is exactly why §5 requires the share and not the count.
    Reporting only the arm-invariant half is the failure this function exists to prevent.

    BOTH A SIGNED AND AN ABSOLUTE SHARE ARE RETURNED, and neither is a substitute for the other. These
    are SIGNED weights (the refined negative-weight targets), so a signed share can be small through
    CANCELLATION while a large amount of weight sits outside the grid. The absolute share cannot cancel.
    A reader comparing arms should look at both; this function ranks neither and draws no conclusion.
    """
    w = np.asarray(w, float)
    out = ~inside                      # out-of-grid OR FPS-miss: everything the histogram drops
    oog = out & ~miss                  # out-of-grid PROPER, i.e. inside the dump but off the grid
    tot_signed, tot_abs = float(w.sum()), float(np.abs(w).sum())

    def _share(num, den):
        # A zero denominator is reported as None rather than as 0.0: "no weight anywhere" and "no weight
        # outside" are different facts, and a 0.0 here would read as the reassuring one.
        return None if den == 0.0 else float(num / den)

    return {
        "n_dropped_total": int(out.sum()),
        "n_out_of_grid_proper": int(oog.sum()),
        "n_fps_miss_SENTINEL": int(miss.sum()),
        "weight_signed_total": tot_signed,
        "weight_signed_dropped": float(w[out].sum()),
        "weight_signed_out_of_grid_proper": float(w[oog].sum()),
        "weight_abs_total": tot_abs,
        "weight_abs_dropped": float(np.abs(w[out]).sum()),
        "weight_abs_out_of_grid_proper": float(np.abs(w[oog]).sum()),
        "share_signed_dropped": _share(float(w[out].sum()), tot_signed),
        "share_abs_dropped": _share(float(np.abs(w[out]).sum()), tot_abs),
        "share_abs_out_of_grid_proper": _share(float(np.abs(w[oog]).sum()), tot_abs),
    }


def band_masks(n_pp):
    """The three regions, expressed in p_parallel EDGE indices so they cannot drift from the grid.

    `cols 10-15` in the ruling are p_parallel column indices; against
    CANONICAL_PPARALLEL_EDGES those are edges 6.0 .. 20.0 GeV, which is why the ruling's own prose
    reads "below 6 GeV" and "above 20 GeV" for the two flanks. Asserted, not assumed.
    """
    epp = np.asarray(fe.CANONICAL_PPARALLEL_EDGES, float)
    if not (abs(epp[10] - 6.0) < 1e-9 and abs(epp[16] - 20.0) < 1e-9):
        die(f"the p_parallel grid no longer places 6.0/20.0 GeV at edges 10/16 "
            f"(got {epp[10]}, {epp[16]}); the band definition in this probe is stale and its three "
            f"regions would silently name different physics")
    col = np.arange(n_pp)
    return {"below_6GeV": col < 10, "band_cols_10_15": (col >= 10) & (col <= 15),
            "above_20GeV": col > 15}


def main():
    ap = argparse.ArgumentParser(description="OI-126 Test 2: target-level spatial probe")
    ap.add_argument("--family-root", required=True)
    ap.add_argument("--nominal-target", required=True)
    ap.add_argument("--nominal-target-sha", required=True)
    ap.add_argument("--source-npz", required=True)
    ap.add_argument("--reconciliation", required=True,
                    help="the inventory carrying target_sha256_measured for all 50 replicas")
    ap.add_argument("--out", required=True)
    ap.add_argument("--expect-below", type=float, required=True)
    ap.add_argument("--expect-band", type=float, required=True)
    ap.add_argument("--expect-above", type=float, required=True)
    a = ap.parse_args()

    if Path(a.out).exists():
        die(f"--out already exists at {a.out}; this probe never clobbers a result")

    # ---- every input proved present and digest-bound BEFORE any array is read ----
    recon = json.loads(require_file(a.reconciliation, "reconciliation inventory").read_text())
    declared = {int(t["replica_index"]): t["target_sha256_measured"] for t in recon["targets"]}
    if sorted(declared) != list(range(N_REPLICAS)):
        die(f"the inventory declares replica indices {sorted(declared)[:5]}..., not 0..{N_REPLICAS-1}")

    nom_p = require_file(a.nominal_target, "certified Gate-2 nominal target")
    nom_sha = sha256_file(nom_p)
    if nom_sha != a.nominal_target_sha:
        die(f"nominal target digest {nom_sha} != declared {a.nominal_target_sha}; this is the "
            f"centring array and a substituted one would move every gap reported below")

    rep_p, rep_sha = [], []
    for i in range(N_REPLICAS):
        p = require_file(Path(a.family_root) / "replicas" / f"replica_{i:02d}" / TARGET_LEAF,
                         f"replica {i} refined target")
        s = sha256_file(p)
        if s != declared[i]:
            die(f"replica {i} target digest {s} != inventoried {declared[i]}; the array on disk is "
                f"not the one the family was certified on")
        rep_p.append(p); rep_sha.append(s)
    if len(set(rep_sha)) != N_REPLICAS:
        die("two replica targets are byte-identical; the reconciler proved them pairwise distinct, "
            "so this means the tree being read is not the certified family")
    if a.nominal_target_sha in set(rep_sha):
        die("a replica target equals the nominal target; the family is centred ON the nominal and "
            "must never equal it")

    src = require_file(a.source_npz, "source dump (measured kinematics)")

    # ---- the per-event assignment, in the TARGET'S OWN ROW ORDER ----
    # ESTABLISHED FROM SOURCE, not guessed. `build_signed_measured_inventory` (`:675-705`) returns
    # `feat = np.vstack([fd, fb])` and `signed = concatenate([data_signed, bkg_signed])` -- so the
    # refined target's rows are the DATA rows followed by the ALIGNED BACKGROUND rows, in that order.
    # The kinematics are therefore two concatenations, and they are COLUMNS of a scalars block rather
    # than standalone npz keys: `SCALAR_COLS` (`:76`) puts pt at column 0 and pparallel at column 1 of
    # `measured_scalars` (data) and `bkg_reco_scalars` (background). Both names and both column indices
    # are IMPORTED from the pinned loader below, never restated, so a schema change breaks this loudly.
    c_pt, c_pp = fe.SCALAR_COLS["pt"], fe.SCALAR_COLS["pparallel"]
    # NO mmap_mode: it is SILENTLY INERT for .npz (measured -- np.load(z, mmap_mode="r")["x"] returns a
    # plain ndarray, not an np.memmap), so writing it would advertise a memory bound this does not have.
    # Each named block is decompressed in full; only the two scalars blocks are touched, never the 9.9 GB.
    with np.load(str(src)) as d:
        for k in ("measured_scalars", "bkg_reco_scalars", "pass_reco"):
            if k not in d.files:
                die(f"source dump has no key {k!r}; it carries {sorted(d.files)}. This probe reads the "
                    f"scalars BLOCKS because the loader does; it does not fall back to a flat key.")
        ms = np.asarray(d["measured_scalars"])
        bs = np.asarray(d["bkg_reco_scalars"])
        if ms.ndim != 2 or bs.ndim != 2 or ms.shape[1] != bs.shape[1]:
            die(f"measured_scalars {ms.shape} / bkg_reco_scalars {bs.shape} are not column-aligned 2-D "
                f"blocks; the concatenation order the target relies on cannot be reconstructed")
        if ms.shape[1] <= max(c_pt, c_pp):
            die(f"scalars block has {ms.shape[1]} columns; the loader's SCALAR_COLS needs > "
                f"{max(c_pt, c_pp)} -- the schema moved and this probe must not index blind")
        pt = np.concatenate([ms[:, c_pt].astype(float), bs[:, c_pt].astype(float)])
        pp = np.concatenate([ms[:, c_pp].astype(float), bs[:, c_pp].astype(float)])
        n_data, n_bkg = int(ms.shape[0]), int(bs.shape[0])
    # FPS misses carry the SENTINEL (-9999) in reco_scalars (`:96`, `:446`). They must be EXCLUDED
    # rather than digitized: -9999 lands below every edge, so they would already fall out of the grid,
    # but naming them separately is what distinguishes "outside the measurement domain" from "a miss".
    miss = (pt <= fe.SENTINEL + 1.0) | (pp <= fe.SENTINEL + 1.0)

    cell, n_cells, inside = cell_index(pt, pp)
    inside = inside & ~miss
    nom = np.asarray(np.load(str(nom_p)), float)
    if nom.shape != pt.shape:
        die(f"nominal target has {nom.shape[0]} rows but the reconstructed inventory has "
            f"{pt.shape[0]} (= n_data {n_data} + n_bkg {n_bkg}); a row-count mismatch means the "
            f"target and the assignment are NOT the same inventory and no gap below would be aligned")

    n_pp = int(np.asarray(fe.CANONICAL_PPARALLEL_EDGES).size - 1)
    masks = band_masks(n_pp)

    def hist(w):
        h = np.bincount(cell[inside], weights=np.asarray(w, float)[inside], minlength=n_cells)
        return h.reshape(-1, n_pp)

    h_nom = hist(nom)
    # §5 quotability accounting, accumulated in the SAME pass that builds the histograms so an arm can
    # never be histogrammed without its out-of-grid share being recorded.
    oog_nominal = out_of_grid_stats(nom, inside, miss)
    oog_replicas = []
    h_rep = np.zeros_like(h_nom)
    for i, (p, s) in enumerate(zip(rep_p, rep_sha)):
        r = np.asarray(np.load(str(p)), float)
        if r.shape != pt.shape:
            die(f"replica target {p} has {r.shape[0]} rows, dump has {pt.shape[0]}")
        h_rep += hist(r)
        oog_replicas.append(dict(replica_index=i, seed=SEED0 + i, **out_of_grid_stats(r, inside, miss)))
    h_rep /= float(N_REPLICAS)

    if len(oog_replicas) != N_REPLICAS:
        die(f"recorded §5 shares for {len(oog_replicas)} replicas, not {N_REPLICAS}; a Test 2 number "
            f"is not quotable without one per arm")

    gap = h_rep - h_nom          # mean replica MINUS nominal, at the TARGET level
    regions = {name: float(gap[:, m].sum()) for name, m in masks.items()}
    expected = {"below_6GeV": a.expect_below, "band_cols_10_15": a.expect_band,
                "above_20GeV": a.expect_above}
    signs_match = {k: bool(np.sign(regions[k]) == np.sign(expected[k])) for k in expected}

    payload = {
        "schema": "oi126-test2-target-level-spatial-v1",
        "ruling": "RULING-20260817-lanec-oi126-branch-set-not-exhaustive.md#4",
        "WHAT_THIS_DOES_NOT_SETTLE": (
            "Branch (c) is ALREADY REFUTED by lane D independently of this probe. This output "
            "adjudicates NOTHING about (c). Its only value is LOCALISATION: whether the band "
            "structure is present at the TARGET level, i.e. upstream of both push and extraction."),
        "n_replicas": N_REPLICAS, "seed0": SEED0,
        "n_rows": int(pt.size), "n_data_rows": n_data, "n_bkg_rows": n_bkg,
        "row_order": "data rows then aligned background rows (build_signed_measured_inventory:703)",
        "n_rows_fps_miss_SENTINEL": int(miss.sum()),
        "n_events_in_grid": int(inside.sum()),
        "n_events_out_of_grid_REPORTED_NOT_CLIPPED": int((~inside).sum()),
        "grid": {"n_pt_bins": int(np.asarray(fe.CANONICAL_PT_EDGES).size - 1),
                 "n_pparallel_bins": n_pp, "n_cells": n_cells},
        "nominal_target_sha256": nom_sha,
        "replica_target_sha256": rep_sha,
        "source_npz_sha256_NOT_COMPUTED": "9.9 GB; digest is the caller's to supply if required",
        # ---- §5 QUOTABILITY CONDITION, per arm and never pooled --------------------------------
        # RULING-20260819-lanec-reconstructed-cell-assignment-admissible.md §5: a Test 2 number is
        # quotable ONLY alongside the -1 count AND its weight share, reported PER ARM. Before
        # 2026-08-20 this file reported a single pooled COUNT and no share at all -- i.e. exactly the
        # arm-invariant half (see out_of_grid_stats) -- so any number it produced was unquotable under
        # the ruling that governs it. The spread below is supplied because §5.2 asks whether the arms
        # differ MATERIALLY; whether they do is a ruling, not a computation, so no verdict is set here.
        "QUOTABILITY_out_of_grid_by_arm": {
            "ruling": "RULING-20260819-lanec-reconstructed-cell-assignment-admissible.md#5",
            "nominal": oog_nominal,
            "replicas": oog_replicas,
            "cross_arm_share_abs_dropped": {
                "nominal": oog_nominal["share_abs_dropped"],
                "replica_min": min(r["share_abs_dropped"] for r in oog_replicas),
                "replica_max": max(r["share_abs_dropped"] for r in oog_replicas),
                "replica_mean": float(np.mean([r["share_abs_dropped"] for r in oog_replicas])),
                "NOTE": ("§5.2: if the nominal and the replicas differ materially here, the "
                         "target-level gap is partly an out-of-grid-fraction difference rather than "
                         "the spatial structure under test -- a confound, not a result. This file "
                         "reports the shares and does not judge materiality."),
            },
            "WHY_COUNTS_ARE_ARM_INVARIANT": (
                "The assignment is reconstructed from the SHARED reco kinematics, so every arm drops "
                "the same EVENTS; only the WEIGHT carried out of the grid differs by arm. A count-only "
                "report therefore cannot discriminate between arms, which is why §5 requires shares."),
        },
        "target_level_gap_by_region": regions,
        "expected_from_the_measured_downstream_structure": expected,
        "sign_agreement_by_region": signs_match,
        "INTERPRETATION_IS_NOT_MADE_HERE": (
            "This file reports the gap and the sign agreement. Whether that constitutes the "
            "structure reproducing at target level is a ruling, not a computation."),
    }
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(a.out) + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    os.replace(tmp, a.out)
    print(f"[oi126-test2] wrote {a.out}")
    print(f"[oi126-test2] gap by region: {json.dumps(regions)}")
    print(f"[oi126-test2] sign agreement: {json.dumps(signs_match)}")
    # Printed, not only written: §5 makes these the condition on quoting anything above, so an operator
    # who reads the gap off the terminal must meet them in the same breath.
    print(f"[oi126-test2] §5 out-of-grid |w| share -- nominal "
          f"{oog_nominal['share_abs_dropped']}, replicas "
          f"[{payload['QUOTABILITY_out_of_grid_by_arm']['cross_arm_share_abs_dropped']['replica_min']}, "
          f"{payload['QUOTABILITY_out_of_grid_by_arm']['cross_arm_share_abs_dropped']['replica_max']}] "
          f"over {len(oog_replicas)} arms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
