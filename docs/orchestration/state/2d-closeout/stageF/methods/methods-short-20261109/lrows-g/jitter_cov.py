"""L-row G3b (referee6 major 7): the full 16-cell rounding-jitter covariance C_J of the data result, and the
statistical covariance with and without it. Run from the repository root.

    python3 -I <this file> --copies DIR   builds jitter_cov.json from the fetched copies of I0's 20 data jitters
                                          (the director's go of 2026-11-12; receipt in g3-jitter-read/)
    python3 -I <this file>                recomputes every readout value from jitter_cov.json's committed 16-cell
                                          vectors and the committed S1 replicas, and refuses on any difference

Inputs:
- the 20 data-jitter products data_b-_j{1..20}.npz (s5p study N, FD-1B-INV-DECLARATION.md:131-133), each reduced
  here to its 16 cell integrals U x_hat (U: the float64 functional matrix of the committed H2 definition). Control
  (a STOP if it fails, the director's go): the per-cell SD (ddof 1) reproduces i0.json [sigma_J_data] and
  rs1_r0.json [sigma_J_over_f] to 1e-9 relative;
- S1's statistical replicas committed in s1/readout/s1_assembly/: set A's data_b{1..20}_j{101..120}.npz, 20 of the
  50 S1's C_stat uses (S1-DECLARATION.md:66). Their covariance C_A20 (ddof 1) approximates C_stat; its diagonal is
  compared with S1's committed stat sigma and the ratio reported.
Reading: under R0b's additivity assumption (each replica = sampling + an independent jitter), the bootstrap
covariance without the jitter is C_A - C_J. Correlations are reported for C_A20 and C_A20 - C_J. With 20
replicas the sampling error on a correlation is about (1 - rho^2) / sqrt(19), so a change smaller than that is not
resolved; the readout gives it beside each change. The readout also records whether C_A20 - C_J is a covariance at
all (positive semi-definite, every |rho| <= 1): with 20 replicas on each side it need not be, and if it is not, the
changed correlations are not a result."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "nd-unfolding")
import s1_assemble as sa  # noqa: E402

FD = Path("docs/orchestration/state/measurement-paper/5d-community-20261024")
HERE = Path(__file__).resolve().parent
OUT = HERE / "jitter_cov.json"
I0 = FD / "fd/receipts-1b/inv/i0/i0.json"
R0 = FD / "fd/rounding-stability-20261106/receipts/full-a1/read/rs1_r0.json"
S1J = FD / "s1/readout/s1_assembly.json"
S1D = FD / "s1/readout/s1_assembly"
DP = FD / "fd/with-cpl/data-product/fd_data_product_cpl.json"
DEF = Path("nd-unfolding/pv-ladder/readouts/h2_definition.json")
SOURCE = "/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731


def corr(C):
    s = np.sqrt(np.diag(C))
    return C / np.outer(s, s)


def analyse(XJ, cells):
    """Every readout value from the 20 jitter vectors XJ (20 x 16) and the committed inputs."""
    i0, r0, s1j, dp = (json.loads(Path(p).read_text()) for p in (I0, R0, S1J, DP))
    f = np.array(dp["f"])
    sdJ = XJ.std(axis=0, ddof=1)
    c_i0 = float(np.max(np.abs(sdJ / np.array(i0["sigma_J_data"]) - 1)))
    c_r0 = float(np.max(np.abs((sdJ / f) / np.array(r0["sigma_J_over_f"]) - 1)))
    if max(c_i0, c_r0) > 1e-9:
        raise SystemExit(f"STOP: the jitter SD does not reproduce I0/RS1 ({c_i0:.2e}, {c_r0:.2e})")
    CJ = np.cov(XJ, rowvar=False, ddof=1)
    U = sa.functional_matrix(sa.fine_map(DEF))
    reps = [S1D / f"data_b{b}_j{100 + b}.npz" for b in range(1, 21)]
    XA = np.array([U @ sa.xs(p) for p in reps])
    CA = np.cov(XA, rowvar=False, ddof=1)
    ratio_A20 = np.sqrt(np.diag(CA)) / f / np.array(s1j["relative_sigma"]["stat"])
    Cno = CA - CJ
    ev = np.linalg.eigvalsh(Cno / np.outer(f, f))
    rA, rno, rJ = corr(CA), corr(Cno), corr(CJ)
    iu = np.triu_indices(16, 1)
    d = (rno - rA)[iu]
    se = ((1 - rA ** 2) / np.sqrt(19))[iu]
    k = int(np.argmax(np.abs(d)))
    C_rep = np.array(dp["matrices"]["C_total_plus_C_resp_plus_C_PL5D"])
    return {
        "controls": {"sigma_J_vs_i0_max_rel": c_i0, "sigma_J_over_f_vs_rs1_r0_max_rel": c_r0},
        "C_J_over_ff": (CJ / np.outer(f, f)).tolist(), "corr_J": rJ.tolist(),
        "corr_J_offdiag": {"median_abs": float(np.median(np.abs(rJ[iu]))), "max_abs": float(np.max(np.abs(rJ[iu])))},
        "A20_sigma_over_S1_stat_sigma": ratio_A20.tolist(),
        "A20_sigma_ratio_summary": {"median": float(np.median(ratio_A20)), "min": float(ratio_A20.min()), "max": float(ratio_A20.max())},
        "jitter_share_of_A20_variance": (np.diag(CJ) / np.diag(CA)).tolist(),
        "corr_A20": rA.tolist(), "corr_A20_minus_J": rno.tolist(),
        "corr_change": {"median_abs": float(np.median(np.abs(d))), "max_abs": float(np.max(np.abs(d))),
                        "max_pair": [cells[iu[0][k]], cells[iu[1][k]]], "max_pair_rho": [float(rA[iu][k]), float(rno[iu][k])],
                        "n_pairs": int(d.size), "n_above_sampling_se": int(np.sum(np.abs(d) > se)),
                        "median_sampling_se": float(np.median(se))},
        "A20_minus_J_min_eigenvalue_fractional": float(ev.min()),
        "A20_minus_J_n_abs_rho_above_1": int(np.sum(np.abs(rno[iu]) > 1)),
        "A20_minus_J_is_a_covariance": bool(ev.min() >= 0 and np.all(np.abs(rno[iu]) <= 1)),
        "C_J_frobenius_share_of_reported": float(np.linalg.norm(CJ / np.outer(f, f)) / np.linalg.norm(C_rep / np.outer(f, f))),
        "inputs_sha256": {"i0": sha(I0), "rs1_r0": sha(R0), "s1_json": sha(S1J), "dp_cpl": sha(DP), "definition": sha(DEF),
                          **{str(p): sha(p) for p in reps}},
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--copies", type=Path)
    a = ap.parse_args(argv)
    cells = json.loads(S1J.read_text())["cells"]
    if a.copies:
        U = sa.functional_matrix(sa.fine_map(DEF))
        man = json.loads((a.copies.parent / "manifest.json").read_text())
        dig = {r["copy"]: r["sha256"] for r in man["files"]}
        vecs, srcs = [], {}
        for j in range(1, 21):
            p = a.copies / f"data_b-_j{j}.npz"
            if sha(p) != dig[p.name]:
                raise SystemExit(f"STOP: {p.name} is not the fetched copy")
            z = np.load(p, allow_pickle=False)
            vecs.append((U @ np.asarray(z["xsec_flat"], float)).tolist())
            srcs[f"{SOURCE}/{p.name}"] = dig[p.name]
        out = {"schema": "lrows-g3b-jitter/1", "cells": cells, "jitter_source_digest": srcs,
               "jitter_cell_vectors": vecs, **analyse(np.array(vecs), cells)}
        OUT.write_text(json.dumps(out, indent=1) + "\n")
    else:
        out = json.loads(OUT.read_text())
        again = analyse(np.array(out["jitter_cell_vectors"]), cells)
        if json.dumps(again, sort_keys=True) != json.dumps({k: out[k] for k in again}, sort_keys=True):
            raise SystemExit("REFUSE: jitter_cov.json does not recompute from its committed vectors")
        print("recomputed: identical")
    c = out["corr_change"]
    print(f"controls: {out['controls']}")
    print(f"C_J correlations off-diagonal: median |rho| {out['corr_J_offdiag']['median_abs']:.3f}, max {out['corr_J_offdiag']['max_abs']:.3f}")
    print(f"A20 sigma / S1 stat sigma: {out['A20_sigma_ratio_summary']}")
    print(f"corr change C_A20 -> C_A20 - C_J: median |d| {c['median_abs']:.4f}, max {c['max_abs']:.4f} at {c['max_pair']} "
          f"({c['max_pair_rho'][0]:.3f} -> {c['max_pair_rho'][1]:.3f}); {c['n_above_sampling_se']} of {c['n_pairs']} pairs above the sampling se (median {c['median_sampling_se']:.3f})")
    print(f"C_A20 - C_J a covariance: {out['A20_minus_J_is_a_covariance']} ({out['A20_minus_J_n_abs_rho_above_1']} |rho| > 1); min eigenvalue of (C_A20 - C_J)/ff: {out['A20_minus_J_min_eigenvalue_fractional']:.3e}; C_J Frobenius share of reported: {out['C_J_frobenius_share_of_reported']:.2e}")


if __name__ == "__main__":
    main()
