"""The all-path reference run for LL5D A1a's equality test (the director's ruling on A1, 2026-11-08): A2.1's own gate
path at 342c0ce5 (fd_1b_c2.prepare(rows=True) -> c2_inputs -> c2_truth -> c2_block, and c2_vi) on a shared fixture,
with fd_1b_mc imported from the vendored copy tests/data/fd_1b_mc_at_342c0ce5.py.txt (A2.1's, which main does not
carry) and the --cv-tdw array set to the fixture's tdw_ref. Run in a subprocess by test_ll5d.A21Equality; never on
real data.

    python3 -B ll5d_a21_reference.py <vendor_dir> <fixture.npz> <draws.json> <out.npz>
"""
import argparse
import json
import sys
from pathlib import Path
from unittest import mock

vendor, fixture, draws_json, out = (Path(x) for x in sys.argv[1:5])
ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND))
sys.path.insert(0, str(vendor))                      # first: fd_1b_mc resolves to A2.1's copy

import numpy as np  # noqa: E402

import fd_1b_mc as mc  # noqa: E402
import fd_1b_c2 as c2  # noqa: E402
import fd_1b_inv as inv  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402

if Path(mc.__file__).resolve() != (vendor / "fd_1b_mc.py").resolve():
    raise SystemExit(f"fd_1b_mc came from {mc.__file__}, not the vendored copy")
z = np.load(fixture, allow_pickle=True)
meta = json.loads(str(z["meta"]))
inputs = {k[len("in::"):]: z[k] for k in z.files if k.startswith("in::")}
inputs["edges"] = [z[f"edge::{i}"] for i in range(meta["n_edges"])]
bkg = {k[len("bkg::"):]: z[k] for k in z.files if k.startswith("bkg::")}
bank_cv = {k[len("cv::"):]: z[k] for k in z.files if k.startswith("cv::")}
weights = {}
for k in z.files:
    if k.startswith("w::"):
        _, tag, key = k.split("::")
        weights.setdefault(tag, {})[key] = z[k]
r = {t: z[f"r::{t}"] for t in meta["truths"]}
world = {"inputs": inputs, "bkg": bkg, "bank_cv": bank_cv, "flux": z["flux"], "groups": meta["groups"],
         "pins": None, "npz_sha": "n", "bkg_sha": "b", "tdw_cv": z["tdw_ref"]}
s1 = {"U": z["s1_U"], "f": z["s1_f"]}
draws = json.loads(draws_json.read_text())


def via(reader, path):
    if reader is toys.flux_probabilities:
        return z["flux_p"]
    if reader is fs.load_s1:
        return s1
    raise SystemExit(f"unexpected read of {path}")


a = argparse.Namespace(flux_constraint=Path("constraint"), definition=Path("definition"), truths=meta["truths"],
                       prep=Path("prep"), push=None, expect_push_sha256=None, staged=Path("staged"),
                       bank=Path("bank"), detector_dir=Path("det"))
patches = [mock.patch.object(mc, "_load_world", lambda a: world),
           mock.patch.object(mc, "verified_weights", lambda world, a, tag: (weights[tag], weights[tag])),
           mock.patch.object(mc, "truth_ratio", lambda t, p: (None, None)),
           mock.patch.object(mc, "truth_weight", lambda t, inputs, ratio, push: r[t]),
           mock.patch.object(mc, "via_noatime", via),
           mock.patch.object(sa, "fine_map", lambda p: z["fm"]),
           mock.patch.object(sa, "functional_matrix", lambda fm: z["U"]),
           mock.patch.object(fs, "reported_matrix", lambda s1: z["reported"]),
           mock.patch.object(inv, "NOATIME_FLAG", 0)]
for p in patches:
    p.start()
P = c2.prepare(a, rows=True)
rel, fm, geo, V, cv = c2.c2_inputs(a, P)
res = {"rel": rel, "keep": P["keep"], "D_full": P["D_full"], "D_cv_full": P["D_cv_full"], "phi": P["phi"]}
for k, v in P["H"].items():
    res[f"H::{k}"] = v
for k, v in P["cv"].items():
    res[f"cv::{k}"] = v
for k in ("wt", "wr", "bkgw", "tdw"):
    res[f"V::{k}"] = V[k]
    res[f"cvrow::{k}"] = cv[k]
for k in ("gen", "reco", "bkg", "td"):
    res[f"geo::{k}"] = geo[k]
blocks, vi = {}, c2.c2_vi(P, cv, fm, geo)
for t in meta["truths"]:
    res[f"single_x::{t}"] = P["single_x"][t]
    res[f"ref_x::{t}"] = P["ref_x"][t]
    res[f"ref_count::{t}"] = P["ref_count"][t]
    S = c2.selection(draws[t], P["col"], P["bands"])
    q = c2.c2_truth(V, cv, S, P["r"][t], geo, c2.draw_flux(S, P["flux_cols"], P["phi"]), P["const"])
    for k, v in q.items():
        res[f"q::{t}::{k}"] = v
    blocks[t] = c2.c2_block(q, P["ref_x"][t], rel)
res["json"] = np.array(json.dumps({"blocks": blocks, "vi": vi}, sort_keys=True))
np.savez(out, **res)
print("A21-REFERENCE OK")
