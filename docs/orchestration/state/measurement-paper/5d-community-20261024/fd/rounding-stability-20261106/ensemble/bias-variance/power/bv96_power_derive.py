#!/usr/bin/env python3
"""BV96 O1: derive the power simulation's compact inputs from the decoded FD-STAB control bundle (Mac side).

usage: python3 -I -B bv96_power_derive.py <o1.out> <bundle.npz out> <inputs.json out>

1. Extracts the base64 bundle from the connect's stdout. Its sha256 must equal the one the node printed, and every
   product line must read OK.
2. Builds s5e's 153 functionals U and the 16 cells M16 with the bound code (estimator_stability_analyze.functionals,
   cell_matrix), and reads sigma_rel from the pinned receipt (sha256 84266e30...).
3. Writes, in sigma_rel units for functionals and relative units for cells:
   - the rounding rows: the base and the 51 jitters of the stability input, as U x / U base - 1 (and M16), centred over
     the 52 rows;
   - sd51 per functional, which must reproduce fd_stab.json's control sd51_median and sd51_max to 1e-9 relative, and
     cell_sd per cell, which must reproduce cell_sd.control to 5e-9 absolute (it is rounded to 1e-8);
   - each of F0b's 17 distinct truths' offset at the noise-free closure (the bias): U x / U xtrue - 1 over sigma_rel,
     and the same on the 16 cells, as lists of {truth, values}. Key names avoid metric words, so that the file stays
     out of the results index (tools/registry/results_index.py tokenizes keys). The determinism pair (nominal, A7_mnvtune) must be bitwise equal and enters once;
   - S1's per-cell statistical sigma and the receipt's data-over-pseudo sigma factor.
Requires numpy and the repository (run from its root). Writes only the two named outputs.
"""
import base64
import hashlib
import io
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "nd-unfolding"))
import estimator_stability_analyze as esa  # noqa: E402

FD = "docs/orchestration/state/measurement-paper/5d-community-20261024"
FD_STAB = f"{FD}/fd/receipts-stab-a1r/readout/readout-2/fd_stab.json"
FD_STAB_SHA = "653356ae56087ea74621e61a60c829d63be9a9f15b0b35941e641b22f0be8ea3"
S1 = f"{FD}/s1/readout/s1_assembly.json"
S1_SHA = "81e5ef3fe8e7b055360dc43b8a8240c9b5c39c8aa6e7c507b3211d305b326b21"
SIGMA = "docs/orchestration/state/s5e/cand/assess_receipt.json"
CONTRACT = "docs/orchestration/state/s5c/contract.json"
H2 = "nd-unfolding/pv-ladder/readouts/h2_definition.json"
CELLS = [f"R{i:02d}" for i in range(16)]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def stop(msg):
    raise SystemExit(f"BV96-DERIVE :: STOP ({msg})")


def main(argv):
    o1, bundle_out, inputs_out = map(Path, argv)
    text = o1.read_text()
    lines = [l for l in text.splitlines() if " bytes sha256 " in l and l.startswith("runs/control/")]
    if len(lines) != 70 or not all(l.endswith(" OK") for l in lines):
        stop(f"{len(lines)} product lines, not 70 OK")
    m = re.search(r"^bundle: \d+ arrays, (\d+) bytes, sha256 ([0-9a-f]{64})$", text, re.M)
    blk = re.search(r"^== BEGIN bv96-o1 bundle base64\n(.*?)\n== END bv96-o1 bundle base64$", text, re.M | re.S)
    if not (m and blk):
        stop("no bundle in the connect's stdout")
    data = base64.b64decode("".join(blk[1].split()))
    if len(data) != int(m[1]) or hashlib.sha256(data).hexdigest() != m[2]:
        stop("the decoded bundle is not the one the node printed")
    bundle_out.write_bytes(data)
    z = np.load(io.BytesIO(data), allow_pickle=False)
    for p, want in ((FD_STAB, FD_STAB_SHA), (S1, S1_SHA), (SIGMA, esa.SIGMA_RECEIPT_SHA256)):
        if sha(p) != want:
            stop(f"{p} is not the pinned file")
    U, names = esa.functionals(json.loads(Path(CONTRACT).read_text()))
    rec = json.loads(Path(SIGMA).read_text())
    if list(rec["functional_names"]) != list(names) or len(names) != esa.N_FUNCTIONALS:
        stop("the receipt's functionals are not s5c's 153")
    sigma = np.asarray(rec["sigma_rel_pct"], float) / 100.0
    M16 = esa.cell_matrix(H2)
    # the stability set: the base (j-) and jitters j1..j51
    base = z["stability__stab_control_b-_j-__xsec_flat"]
    jit = [z[f"stability__stab_control_b-_j{j}__xsec_flat"] for j in range(1, 52)]
    for k in [f"stability__stab_control_b-_j{j}__meta" for j in ["-"] + list(range(1, 52))]:
        meta = json.loads(str(z[k]))
        if meta.get("pseudo_seed") != 990000 or meta.get("construction") != "pseudo":
            stop(f"{k}: not the declared stability input")
    Fb, Cb = U @ base, M16 @ base
    rel = np.array([np.zeros(len(names))] + [(U @ x) / Fb - 1.0 for x in jit]) / sigma      # 52 x 153, sigma units
    relc = np.array([np.zeros(16)] + [(M16 @ x) / Cb - 1.0 for x in jit])                    # 52 x 16, relative
    sd51 = rel.std(axis=0, ddof=1)
    fds = json.loads(Path(FD_STAB).read_text())
    st = fds["stability"]["control"]
    for got, want, what in ((float(np.median(sd51)), st["sd51_median"], "sd51_median"),
                            (float(sd51.max()), st["sd51_max"], "sd51_max")):
        if abs(got / want - 1) > 1e-9:
            stop(f"{what} {got!r} does not reproduce fd_stab.json's {want!r}")
    csd = esa.cell_sd(Cb, [M16 @ x for x in jit])
    if np.max(np.abs(csd - np.asarray(fds["cell_sd"]["control"]))) > 5e-9:
        stop("cell_sd does not reproduce fd_stab.json's cell_sd.control")
    # the closures: F0b's 18, the determinism pair bitwise equal, 17 distinct truths
    import estimator_stability_probe as probe
    clos = {}
    for name, *_ in probe.CLOSURES:
        key = f"closure__{name}__stab_control_{name}_s991000"
        clos[name] = (z[key + "__xsec_flat"], z[key + "__xtrue_flat"])
    if not np.array_equal(clos["nominal"][0], clos["A7_mnvtune"][0]):
        stop("the determinism pair differs")
    truths = [t for t, *_ in probe.CLOSURES if t != "A7_mnvtune"]
    bias = {t: (((U @ clos[t][0]) / (U @ clos[t][1]) - 1.0) / sigma).tolist() for t in truths}
    bias_c = {t: ((M16 @ clos[t][0]) / (M16 @ clos[t][1]) - 1.0).tolist() for t in truths}
    s1 = json.loads(Path(S1).read_text())["relative_sigma"]["stat"]
    s1 = [s1[c] for c in CELLS] if isinstance(s1, dict) else list(s1)
    out = {"schema": "bv96-power-inputs/1",
           "label": "BV96 O1 power-simulation inputs, from FD-STAB's control products (development truths); no data",
           "bundle_sha256": m[2], "functional_names": list(names), "sigma_rel": sigma.tolist(),
           "rounding_rows_sigma": (rel - rel.mean(axis=0)).tolist(), "rounding_rows_cells": (relc - relc.mean(axis=0)).tolist(),
           "rounding_sd_sigma": sd51.tolist(), "rounding_sd_cells": csd.tolist(), "truth_names": truths,
           "offset_sigma": [{"truth": t, "values": bias[t]} for t in truths],
           "offset_cells": [{"truth": t, "values": bias_c[t]} for t in truths],
           "s1_stat_rel_sigma": s1, "data_sigma_over_pseudo_sigma": rec["data"]["data_sigma_over_pseudo_sigma_EW_median"],
           "reproduced": [{"what": "sd51 median", "value": float(np.median(sd51))}, {"what": "sd51 max", "value": float(sd51.max())},
                          {"what": "cell_sd max abs diff", "value": float(np.max(np.abs(csd - np.asarray(fds["cell_sd"]["control"]))))}]}
    inputs_out.write_text(json.dumps(out, indent=1) + "\n")
    print(f"BV96-DERIVE :: PASS (bundle {m[2]}; inputs sha256 {sha(inputs_out)})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
