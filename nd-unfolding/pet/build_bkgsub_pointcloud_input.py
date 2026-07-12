#!/usr/bin/env python3
"""Phase 1 of the corrected PET UQ campaign: build the background-subtracted
5D point-cloud OmniFold input, with a strict event-by-event alignment gate.

Problem
-------
`of_inputs_pc_fullcloud.npz` (the full-cloud PET input) carries UNIT
`measured_weights` -- an UNSUBTRACTED measured target. The corrected PET budget
must train on the same background-subtracted 5D purity target that the scalar
GBDT result uses, which lives in `of_inputs_5d.npz["measured_weights"]`
(per-interior-reco-bin max(0, N_data - N_bkg)/N_data; see
`unfold_nd_omnifold_unbinned.build_measured_training_nd`). We must attach those
per-event weights to the point-cloud data rows WITHOUT re-running the C++ event
loop -- but only after PROVING the two dumps' data rows are the same events in
the same order (equal counts alone are NOT proof; the two npz were built from
different ROOTs by different loops).

What this does
--------------
1. Reads the five reconstructed DATA scalar coordinates
   (measured, measured_pz, measured_eavail, measured_q3, measured_W) from the
   full-cloud source ROOT's `data` tree, using the SAME accepted-data gate and
   sequential order as `pet/dump_pointcloud_inputs.py` (which wrote
   `measured_pc`). -> `measured_scalars` (N,5), in measured_pc row order.
2. DATA ALIGNMENT GATE: requires event-by-event equality (at float32, the
   stored precision) between `measured_scalars` and `of_inputs_5d["measured"]`.
3. MC ALIGNMENT GATE: requires w_truth / w_reco / pass_reco / pass_truth to be
   byte-identical (CRC32) between the full-cloud npz and `of_inputs_5d.npz`.
4. WEIGHT GATE: the attached bkgsub weights are finite, in [0,1], exactly equal
   to `of_inputs_5d["measured_weights"]`, with the exact total target weight.
5. Builds `of_inputs_pc_fullcloud_bkgsub_5d.npz`: the full-cloud tensors with
   `measured_weights` swapped to the bkgsub target, plus `measured_scalars`
   (provenance/alignment) and the W edge. The unsubtracted input is untouched.
6. Writes a provenance JSON (paths, counts, hashes, mismatch counts, weight
   stats, binning, output path).

The numpy gate helpers below are import-safe (no ROOT) so the test suite can
exercise them on synthetic fixtures; only `read_data_scalars_root` needs
PyROOT and is imported lazily.

Usage (under the ROOT env, on a compute node):
  python3 pet/build_bkgsub_pointcloud_input.py            # full build
  python3 pet/build_bkgsub_pointcloud_input.py --check-only   # gates + provenance, no heavy npz build
"""
import argparse
import hashlib
import json
import os
import sys
import zipfile

import numpy as np

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
ND = os.path.join(REPO, "nd-unfolding")

DEFAULT_FULLCLOUD_NPZ = os.path.join(ND, "of_inputs_pc_fullcloud.npz")
DEFAULT_REF5D_NPZ = os.path.join(ND, "of_inputs_5d.npz")
DEFAULT_SOURCE_ROOT = os.path.join(ND, "runEventLoopOmniFold_PC_MEFHC_fullcloud.root")
DEFAULT_OUT_NPZ = os.path.join(ND, "of_inputs_pc_fullcloud_bkgsub_5d.npz")
DEFAULT_PROV_DIR = os.path.join(ND, "products", "pet", "bkgsub")

# 5D reco-coordinate column order (matches of_inputs_5d["measured"] and axes).
SCALAR_COLS = ["pt", "pz", "eavail", "q3", "W"]
DATA_BRANCHES = ["measured", "measured_pz", "measured_eavail", "measured_q3", "measured_W"]
MC_ALIGN_MEMBERS = ["w_truth", "w_reco", "pass_reco", "pass_truth"]
N_DATA_EXPECTED = 4_091_707


# ---------------------------------------------------------------------------
# Import-safe (no ROOT) helpers -- exercised by the test suite
# ---------------------------------------------------------------------------
def npz_member_crcs(path):
    """Return {member_stem: (crc32, uncompressed_size)} without decompressing."""
    with zipfile.ZipFile(path) as z:
        return {i.filename[:-4] if i.filename.endswith(".npy") else i.filename:
                (i.CRC, i.file_size) for i in z.infolist()}


def check_mc_alignment(pc_path, ref_path, members=MC_ALIGN_MEMBERS):
    """CRC32 byte-identity check of shared MC arrays between two npz files."""
    c_pc, c_ref = npz_member_crcs(pc_path), npz_member_crcs(ref_path)
    out = {"members": {}, "all_identical": True}
    for m in members:
        if m not in c_pc or m not in c_ref:
            out["members"][m] = {"present": False, "identical": False}
            out["all_identical"] = False
            continue
        ident = (c_pc[m] == c_ref[m])
        out["members"][m] = {"present": True, "identical": bool(ident),
                             "pc_crc": int(c_pc[m][0]), "ref_crc": int(c_ref[m][0])}
        out["all_identical"] = out["all_identical"] and ident
    return out


def check_data_alignment(scalars_dumporder, ref_measured):
    """Event-by-event equality of extracted data scalars (dump/measured_pc order)
    vs the reference measured coordinates, at float32 (the stored precision).

    Returns a dict with row count, exact-match count, per-column mismatch counts
    and max abs diffs, and the first few mismatched row indices. Pure numpy."""
    a = np.asarray(scalars_dumporder, dtype=np.float32)
    b = np.asarray(ref_measured, dtype=np.float32)
    out = {"n_rows_extracted": int(a.shape[0]), "n_rows_ref": int(b.shape[0]),
           "shape_extracted": list(a.shape), "shape_ref": list(b.shape)}
    if a.shape != b.shape:
        out.update(exact=False, n_mismatch_rows=-1,
                   reason="shape mismatch (row count or ncols differ)")
        return out
    eq = (a == b)  # exact at float32
    row_ok = eq.all(axis=1)
    n_mis = int((~row_ok).sum())
    per_col = {}
    diff = np.abs(a.astype(np.float64) - b.astype(np.float64))
    for j, name in enumerate(SCALAR_COLS[:a.shape[1]]):
        per_col[name] = {"n_mismatch": int((~eq[:, j]).sum()),
                         "max_abs_diff": float(diff[:, j].max())}
    out.update(exact=bool(n_mis == 0), n_mismatch_rows=n_mis,
               per_col=per_col,
               first_mismatch_rows=[int(i) for i in np.flatnonzero(~row_ok)[:10]])
    return out


def validate_bkgsub_weights(bkgsub_w, ref_w):
    """Validate the attached bkgsub weights against the canonical 5D target."""
    w = np.asarray(bkgsub_w, dtype=np.float64)
    r = np.asarray(ref_w, dtype=np.float64)
    finite = bool(np.isfinite(w).all())
    in_unit = bool((w >= 0.0).all() and (w <= 1.0).all())
    exact = bool(w.shape == r.shape and np.array_equal(w, r))
    return {"n": int(w.shape[0]), "finite": finite, "in_unit_interval": in_unit,
            "exact_equal_to_ref": exact,
            "min": float(w.min()), "max": float(w.max()),
            "mean": float(w.mean()), "sum": float(w.sum()),
            "sum_ref": float(r.sum()),
            "sum_exact": bool(w.sum() == r.sum())}


def per_bin_purity_report(measured, weights, edges):
    """Descriptive (not a gate): the bkgsub weight is max(0,d-b)/d per INTERIOR
    reco bin (unfold_nd_omnifold_unbinned.build_measured_training_nd). Report how
    piecewise-constant the inherited weights are on the reporting grid; small
    within-bin spread is expected from float32 storage of near-edge coords."""
    m = np.asarray(measured, dtype=np.float64)
    w = np.asarray(weights, dtype=np.float64)
    n = m.shape[0]
    idx = np.zeros(n, dtype=np.int64)
    for j in range(m.shape[1]):
        e = np.asarray(edges[j], float)
        b = np.digitize(m[:, j], e)          # 0..len(e)
        idx = idx * (len(e) + 1) + b
    uniq, inv = np.unique(idx, return_inverse=True)
    order = np.argsort(inv, kind="stable")
    inv_s, w_s = inv[order], w[order]
    starts = np.searchsorted(inv_s, np.arange(len(uniq)))
    gmin = np.minimum.reduceat(w_s, starts)
    gmax = np.maximum.reduceat(w_s, starts)
    spread = gmax - gmin
    return {"n_populated_bins": int(len(uniq)),
            "n_bins_spread_gt_1e-9": int((spread > 1e-9).sum()),
            "max_within_bin_spread": float(spread.max()),
            "n_weight_zero": int((w == 0).sum()),
            "n_weight_one": int((w == 1.0).sum())}


def _sha256(arr):
    return hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# ROOT-dependent reader (lazy import; NOT imported by tests)
# ---------------------------------------------------------------------------
def read_data_scalars_root(source_root, pt_lo, pt_hi, pz_lo, pz_hi, verbose=True):
    """Walk the full-cloud source ROOT `data` tree in entry order, applying the
    SAME accepted-data gate as pet/dump_pointcloud_inputs.py (measured_pass != 0
    and pt/pz inside the phase-space box, tested on the raw doubles), and return
    `measured_scalars` (N, 5) float64 in measured_pc row order.

    Matching dump's gate (NOT the driver's extra finite/guard checks) is
    deliberate: this array must be in measured_pc order so alignment against
    of_inputs_5d["measured"] proves the point-cloud rows carry the right weights.
    """
    from array import array
    import ROOT  # noqa: F401  (lazy)

    f = ROOT.TFile.Open(source_root)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {source_root}")
    t = f.Get("data")
    if not t:
        raise SystemExit(f"[FAIL] no `data` tree in {source_root}")
    missing = [b for b in DATA_BRANCHES + ["measured_pass"] if not t.GetBranch(b)]
    if missing:
        raise SystemExit(f"[FAIL] data tree missing branches: {missing}")

    addr = {b: array("d", [0.0]) for b in DATA_BRANCHES}
    for b, a in addr.items():
        t.SetBranchAddress(b, a)
    mpass = array("B", [0])
    t.SetBranchAddress("measured_pass", mpass)

    n = int(t.GetEntries())
    buf = np.zeros((n, 5), dtype=np.float64)
    k = 0
    for i in range(n):
        t.GetEntry(i)
        if mpass[0] == 0:
            continue
        pt = float(addr["measured"][0]); pz = float(addr["measured_pz"][0])
        if not (pt_lo <= pt <= pt_hi and pz_lo <= pz <= pz_hi):
            continue
        buf[k, 0] = pt
        buf[k, 1] = pz
        buf[k, 2] = float(addr["measured_eavail"][0])
        buf[k, 3] = float(addr["measured_q3"][0])
        buf[k, 4] = float(addr["measured_W"][0])
        k += 1
        if verbose and (i % 500000 == 0):
            print(f"  data {i}/{n} kept={k}", flush=True)
    f.Close()
    out = buf[:k]
    if verbose:
        print(f"[OK] data scalars: kept {k}/{n} (box "
              f"pt[{pt_lo},{pt_hi}] pz[{pz_lo},{pz_hi}])", flush=True)
    return out


# ---------------------------------------------------------------------------
# Corrected-npz assembly
# ---------------------------------------------------------------------------
def build_corrected_npz(fullcloud_npz, ref5d_npz, measured_scalars, out_npz,
                        verbose=True):
    """Copy the full-cloud tensors, swap measured_weights -> the 5D bkgsub
    target, add measured_scalars + the W edge + provenance labels. Writes a
    compressed npz; the unsubtracted input file is never modified."""
    if verbose:
        print(f"[build] loading {fullcloud_npz} ...", flush=True)
    src = np.load(fullcloud_npz, allow_pickle=True)
    ref = np.load(ref5d_npz, allow_pickle=True)
    bkgsub_w = np.asarray(ref["measured_weights"])  # (N,) float64 canonical target
    ms = np.asarray(measured_scalars, dtype=np.float32)

    payload = {}
    for key in src.files:
        if key == "measured_weights":
            continue  # replaced below
        payload[key] = src[key]
    payload["measured_weights"] = bkgsub_w
    payload["measured_scalars"] = ms
    payload["measured_scalars_cols"] = np.array(SCALAR_COLS, dtype=object)
    payload["edges_4"] = np.asarray(ref["edges_4"], float)  # W edge (5th axis)
    payload["campaign"] = np.asarray("bkgsub_5d_corrected")
    payload["measured_weights_source"] = np.asarray(os.path.basename(ref5d_npz))
    payload["clouds_source"] = np.asarray(os.path.basename(fullcloud_npz))
    if verbose:
        print(f"[build] writing {out_npz} (savez_compressed) ...", flush=True)
    tmp = out_npz + ".tmp.npz"
    np.savez_compressed(tmp, **payload)
    os.replace(tmp, out_npz)
    if verbose:
        print(f"[build] wrote {out_npz} ({os.path.getsize(out_npz)/1e9:.2f} GB)",
              flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fullcloud-npz", default=DEFAULT_FULLCLOUD_NPZ)
    ap.add_argument("--ref5d-npz", default=DEFAULT_REF5D_NPZ)
    ap.add_argument("--source-root", default=DEFAULT_SOURCE_ROOT)
    ap.add_argument("--out-npz", default=DEFAULT_OUT_NPZ)
    ap.add_argument("--prov-dir", default=DEFAULT_PROV_DIR)
    ap.add_argument("--check-only", action="store_true",
                    help="run the gates + write provenance/scalars, skip the heavy npz build")
    args = ap.parse_args()

    os.makedirs(args.prov_dir, exist_ok=True)

    ref = np.load(args.ref5d_npz, allow_pickle=True)
    ref_measured = np.asarray(ref["measured"])            # (N,5) float32
    ref_w = np.asarray(ref["measured_weights"])           # (N,) float64
    edges = [np.asarray(ref[f"edges_{i}"], float) for i in range(5)]
    pt_lo, pt_hi = float(edges[0][0]), float(edges[0][-1])
    pz_lo, pz_hi = float(edges[1][0]), float(edges[1][-1])
    print(f"[gate] reference {os.path.basename(args.ref5d_npz)}: "
          f"measured{ref_measured.shape} weights n={ref_w.shape[0]} "
          f"box pt[{pt_lo},{pt_hi}] pz[{pz_lo},{pz_hi}]", flush=True)

    # --- 1. extract data scalars from ROOT in measured_pc (dump) order ---
    scalars = read_data_scalars_root(args.source_root, pt_lo, pt_hi, pz_lo, pz_hi)

    # --- 2. DATA ALIGNMENT GATE ---
    dgate = check_data_alignment(scalars, ref_measured)
    print(f"[gate] DATA alignment: rows_extracted={dgate['n_rows_extracted']} "
          f"rows_ref={dgate['n_rows_ref']} exact={dgate.get('exact')} "
          f"n_mismatch_rows={dgate.get('n_mismatch_rows')}", flush=True)
    if dgate.get("per_col"):
        for c, s in dgate["per_col"].items():
            print(f"         {c:8s} mismatch={s['n_mismatch']} "
                  f"max|d|={s['max_abs_diff']:.3e}", flush=True)

    # --- 3. MC ALIGNMENT GATE (CRC byte-identity) ---
    mgate = check_mc_alignment(args.fullcloud_npz, args.ref5d_npz)
    print(f"[gate] MC alignment (CRC): all_identical={mgate['all_identical']}",
          flush=True)
    for m, s in mgate["members"].items():
        print(f"         {m:12s} identical={s['identical']}", flush=True)

    # --- 4. WEIGHT GATE ---
    wgate = validate_bkgsub_weights(ref_w, ref_w)
    print(f"[gate] WEIGHTS: n={wgate['n']} finite={wgate['finite']} "
          f"in[0,1]={wgate['in_unit_interval']} sum={wgate['sum']:.9f}", flush=True)
    purity = per_bin_purity_report(ref_measured, ref_w, edges)
    print(f"[info] per-bin purity structure: populated_bins={purity['n_populated_bins']} "
          f"bins_with_spread>1e-9={purity['n_bins_spread_gt_1e-9']} "
          f"max_spread={purity['max_within_bin_spread']:.3e}", flush=True)

    # --- provenance + scalars sidecar (always written) ---
    scalars_f32 = scalars.astype(np.float32)
    sidecar = os.path.join(args.prov_dir, "measured_scalars_fullcloud_dumporder.npz")
    np.savez_compressed(sidecar, measured_scalars=scalars_f32,
                        cols=np.array(SCALAR_COLS, dtype=object))
    prov = {
        "campaign": "PET bkgsub 5D corrected point-cloud input (Phase 1)",
        "inputs": {
            "source_root": args.source_root,
            "fullcloud_npz": args.fullcloud_npz,
            "ref5d_npz": args.ref5d_npz,
        },
        "output_npz": args.out_npz,
        "sidecar_scalars_npz": sidecar,
        "n_data_expected": N_DATA_EXPECTED,
        "data_alignment_gate": dgate,
        "mc_alignment_gate": mgate,
        "weight_gate": wgate,
        "per_bin_purity_report": purity,
        "binning_edges": {f"edges_{i}": edges[i].tolist() for i in range(5)},
        "scalar_cols": SCALAR_COLS,
        "hashes": {
            "measured_weights_sha256": _sha256(ref_w),
            "measured_scalars_sha256": _sha256(scalars_f32),
            "ref_measured_sha256": _sha256(np.asarray(ref_measured, np.float32)),
        },
    }
    prov_path = os.path.join(args.prov_dir,
                             "of_inputs_pc_fullcloud_bkgsub_5d.provenance.json")
    with open(prov_path, "w") as fh:
        json.dump(prov, fh, indent=2)
    print(f"[prov] wrote {prov_path}", flush=True)
    print(f"[prov] wrote {sidecar}", flush=True)

    # --- HARD GATES: refuse to build a misaligned/invalid input ---
    problems = []
    if dgate["n_rows_extracted"] != N_DATA_EXPECTED:
        problems.append(f"extracted rows {dgate['n_rows_extracted']} != {N_DATA_EXPECTED}")
    if not dgate.get("exact"):
        problems.append(f"data rows not event-by-event aligned "
                        f"(n_mismatch={dgate.get('n_mismatch_rows')})")
    if not mgate["all_identical"]:
        problems.append("MC arrays not byte-identical to of_inputs_5d")
    if not (wgate["finite"] and wgate["in_unit_interval"]
            and wgate["exact_equal_to_ref"] and wgate["n"] == N_DATA_EXPECTED):
        problems.append("bkgsub weight gate failed")
    if problems:
        print("[FAIL] gates did not pass; NOT building the corrected npz:",
              flush=True)
        for p in problems:
            print(f"        - {p}", flush=True)
        sys.exit(3)
    print("[gate] ALL PHASE-1 GATES PASS.", flush=True)

    if args.check_only:
        print("[done] --check-only: gates passed, provenance written, "
              "corrected npz NOT built.", flush=True)
        return

    build_corrected_npz(args.fullcloud_npz, args.ref5d_npz, scalars, args.out_npz)

    # verify the built file: reopen, confirm weights + scalars + shapes
    chk = np.load(args.out_npz, allow_pickle=True)
    ok = (chk["measured_weights"].shape[0] == N_DATA_EXPECTED
          and np.array_equal(np.asarray(chk["measured_weights"]), ref_w)
          and chk["measured_pc"].shape[0] == N_DATA_EXPECTED
          and chk["measured_scalars"].shape == (N_DATA_EXPECTED, 5))
    print(f"[verify] rebuilt npz: measured_pc{chk['measured_pc'].shape} "
          f"measured_weights n={chk['measured_weights'].shape[0]} "
          f"weights_exact={bool(np.array_equal(np.asarray(chk['measured_weights']), ref_w))} "
          f"OK={bool(ok)}", flush=True)
    if not ok:
        sys.exit(4)
    print("[done] corrected bkgsub 5D point-cloud input built and verified.",
          flush=True)


if __name__ == "__main__":
    main()
