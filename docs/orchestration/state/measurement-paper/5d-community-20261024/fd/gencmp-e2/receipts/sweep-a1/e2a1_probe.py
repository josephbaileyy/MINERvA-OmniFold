"""E2-A1 sweep probe (read-only): E2's controls on the real committed formats, from the deploy at M'' (whose code for
these controls is unchanged by E2-A1), reading the first run's staged, pinned copies O_NOATIME. Prints one JSON."""
import io, json, sys
from pathlib import Path
R = Path("/pscratch/sd/j/josephrb/gencmp-e2-20261102")
sys.path[:0] = [str(R / "deploy/nd-unfolding"), str(R / "deploy/nd-unfolding/pv-ladder")]
import numpy as np
import fd_gencmp as gc
import fd_gencmp_e2 as E2
import pvl_analyze as PA
import pvl_lib as L
import s5n_pseudo
import build_cmodel5d as BC

pins = gc.load_pins(E2.INPUTS)
out = {"deploy_head": (R / "deploy/.git/HEAD").read_text().strip()}

def staged_bytes(rel):
    src = E2.SCRATCH / rel
    data, atime_ok = gc.read_noatime(R / "inputs" / rel)
    import hashlib
    h = hashlib.sha256(data).hexdigest()
    assert h == pins[str(src)], (rel, h)
    return data

def npz(rel):
    return np.load(io.BytesIO(staged_bytes(rel)), allow_pickle=True)

cfg = json.loads(E2.CONFIG.read_text())["rungs"][E2.RUNG]
T = PA.tasks(E2.PVL / "tasks.tsv")
metas = {}
for v in ("tune_v1",) + tuple(BC.VERTICES):
    metas[v] = json.loads(str(npz(f"{E2.PRODUCTS}/L-5D-PV_e_{v}.npz")["meta"]))
out["metas"] = metas
rsha = {v: __import__("hashlib").sha256(staged_bytes(f"{E2.PREP}/{v}.json")).hexdigest() for v in ("tune_v1",) + tuple(BC.VERTICES)}
res = {}
def try_meta(tag, name, meta, task, ratios, ref=None):
    try:
        PA.check_meta(name, meta, task, ratios, cfg, ref); res[tag] = "PASS"
    except SystemExit as e:
        res[tag] = f"FAIL: {e}"
for v, m in metas.items():
    try_meta(f"check_meta seed42 committed {v}", v, m, T[f"L-5D-PV_e_{v}"], {"vertices": {v: {"ratio_sha256": rsha[v]}}})
for v in ("nuwro", "gibuu"):
    m = metas[v]
    try:
        E2.params_but_seed(m["estimator_params"], 42); res[f"params_but_seed committed {v} at 42"] = "PASS"
    except SystemExit as e:
        res[f"params_but_seed committed {v} at 42"] = f"FAIL: {e}"
    res[f"refinement random_state committed {v}"] = m["refinement"].get("classifier_params", {}).get("random_state")
    m43 = json.loads(json.dumps(m))
    m43["estimator_seed"] = 43
    m43["refinement"]["classifier_params"]["random_state"] = 43 + s5n_pseudo.REFINE_SEED_OFFSET
    for p in m43["estimator_params"]:
        p["random_state"] = 43
    with E2.declared_seed(PA, 43):
        try_meta(f"check_meta seed43 on committed (seed-42) {v} [must FAIL]", v, m, T[f"L-5D-PV_e_{v}"], {"vertices": {v: {"ratio_sha256": rsha[v]}}})
        try_meta(f"check_meta seed43 on committed {v} with seed fields at 43 [must PASS]", v, m43, T[f"L-5D-PV_e_{v}"], {"vertices": {v: {"ratio_sha256": rsha[v]}}})
    res[f"params_but_seed committed {v}: 43-variant == 42 original"] = (
        E2.params_but_seed(m43["estimator_params"], 43) == E2.params_but_seed(m["estimator_params"], 42))
# the code record a rerun at M'' in this environment would write (pvl_unfold.py:186-188)
import lightgbm, s5e_trace, pvl_unfold
code_now = {**s5n_pseudo.code_digests(), "pvl_unfold.py": L.sha256_path(Path(pvl_unfold.__file__)),
            "pvl_lib.py": L.sha256_path(L.__file__), "s5e_trace.py": L.sha256_path(Path(s5e_trace.__file__)),
            "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "lightgbm": lightgbm.__version__}}
old = metas["nuwro"]["code_sha256"]
out["code_now"] = code_now
res["B2 code keys differing, committed nuwro vs a rerun here"] = sorted(
    k for k in set(old) | set(code_now) if old.get(k) != code_now.get(k))
res["committed code versions"] = old.get("versions")
# R2's operand
x = np.asarray(npz(f"{E2.PRODUCTS}/L-5D-PV_e_nuwro.npz")["xsec_flat"])
res["R2 operand"] = {"dtype": str(x.dtype), "shape": list(x.shape), "self_equal": bool(np.array_equal(x, x.copy())),
                     "perturbed_equal": bool(np.array_equal(x, np.where(np.arange(x.size) == 7, x * (1 + 1e-15) + 1e-300, x)))}
# C1 on the real committed products, with M''s factor (unchanged by E2-A1)
cm = json.loads(E2.CMODEL5.read_text())
rmap, n, *_ = BC.load_definition(BC._HERE / "readouts" / "h2_definition.json",
                                 E2._REPO / "docs/orchestration/state/s5p/stage1/stage1_inspect.json", BC.EXPECT)
xs = {v: np.asarray(npz(f"{E2.PRODUCTS}/L-5D-PV_e_{v}.npz")["xsec_flat"], float) for v in ("tune_v1",) + tuple(BC.VERTICES)}
S_c = E2.factor(xs, rmap, n)
res["C1 carbon products give cmodel_5d.json S bitwise"] = bool(np.array_equal(S_c, np.asarray(cm["S"], float)))
# leg (iii)'s fields on the committed ratio files
lf = {}
for v in ("gibuu", "nuwro"):
    d = json.loads(staged_bytes(f"{E2.PREP}/{v}.json"))
    lf[v] = {"axes": d.get("axes"), "has_truth_cut": "truth_cut" in d, "truth_cut": d.get("truth_cut"),
             "has_pz_max_cells": "pz_max_cells" in d, "pz_max_cells": d.get("pz_max_cells")}
out["committed_ratio_domain_fields"] = lf
out["results"] = res
print(json.dumps(out, indent=1, default=str))
