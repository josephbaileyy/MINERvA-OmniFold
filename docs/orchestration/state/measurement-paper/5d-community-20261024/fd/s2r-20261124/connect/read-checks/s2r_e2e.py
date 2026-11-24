"""Local end-to-end: s2r_probe.run -> s5p_nullexp.main (refinement, traced unfold, product) with REAL LightGBM on
FD-STAB's synthetic fine-grid inputs, for B0 and S2R at nominal and q3; then pair-like checks and the read's controls
that do not need FD-PRR's products. Writes only under a temp dir."""
import json, os, sys, tempfile, types, contextlib, io
from pathlib import Path
import numpy as np
REPO = Path.home() / "s2r-wt"
ND = REPO / "nd-unfolding"
for p in (ND / "s2r", ND, ND / "tier3", ND / "tests", ND / "pv-ladder", ND / "prior_retention"):
    sys.path.insert(0, str(p))
if not hasattr(os, "O_NOATIME"):
    os.O_NOATIME = 0
os.chdir(REPO)
import types as _t
class _R(_t.ModuleType):
    def __getattr__(self, k):
        if k.startswith('__'): raise AttributeError(k)
        return _R(k)
    def __call__(self, *a, **k): return _R('call')
sys.modules['ROOT'] = _R('ROOT')  # smoke only: no ROOT on this laptop
import s2r_probe as SP, s2r_arm as S, t3p_probe as T
import test_estimator_stability_probe as TS
import s5p_universe
s5p_universe.check_alignment = lambda *a, **k: {}
tmp = Path(tempfile.mkdtemp(prefix="s2r-e2e-", dir=os.environ.get("TMPDIR")))
inp = TS.fine_inputs(20000, 0)
inp["measured"] = inp["MCreco"][:4000].copy(); inp["measured_weights"] = np.ones(4000)
TS.write_npz(tmp / "in.npz", inp)
rng = np.random.default_rng(5)
nb = 1500
np.savez(tmp / "bkg.npz", bkg_reco=inp["MCreco"][rng.integers(0, 20000, nb)], bkg_w=rng.uniform(0.1, 1, nb), bkg_nd=np.zeros(1))
(tmp / "bank").mkdir(); np.savez(tmp / "bank" / "cv.npz", MCgen=inp["MCgen"])
(tmp / "stage").mkdir(); (tmp / "stage.json").write_text(json.dumps({"dest": str(tmp / "stage"), "files": []}))  # the job layout: <OUT>/stage, <OUT>/runs
a = types.SimpleNamespace(npz=tmp / "in.npz", bkg=tmp / "bkg.npz", bank=tmp / "bank", detector_dir=tmp / "det",
                          expect_npz_sha256=T.sha256_path(tmp / "in.npz"), expect_bkg_sha256=T.sha256_path(tmp / "bkg.npz"),
                          closure_ratio_dir=tmp / "pvl", runs=tmp / "runs", stage_json=tmp / "stage.json")
res = {}
for t in ("nominal", "q3"):
    for arm in ("B0", "S2R"):
        argv = SP.runner_argv(a, arm, t)
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = SP.run(arm, t, tmp / "stage.json", argv)
        p = SP.product_path(tmp / "runs", arm, t)
        print(arm, t, "rc", rc, "product", p.exists(), (err.getvalue().strip().splitlines() or [""])[-1][:200])
        if rc == 0 and p.exists():
            with np.load(p, allow_pickle=False) as z:
                meta = json.loads(str(z["meta"]))
                res[(arm, t)] = {k: np.asarray(z[k]) for k in ("xsec_flat", "xtrue_flat", "X16_push")}
                print("   keys ok:", all(k in z.files for k in ("X16_push", "X16_pull", "R16_D", "clip_step2", "xs_k5")),
                      "s2r block:", {k: meta["s2r"][k] for k in ("arm", "truth", "iters")},
                      "refinement ran:", (meta.get("refinement") or {}).get("ran"),
                      "s2r_fits:", meta["s2r"]["evidence"].get("s2r_fits"),
                      "max round trip:", max(meta["s2r"]["evidence"].get("s2r_max_round_trip") or [0]))
for t in ("nominal", "q3"):
    b, s = res.get(("B0", t)), res.get(("S2R", t))
    if b and s:
        print(t, "C-X (truth bitwise):", T.same(s["xtrue_flat"], b["xtrue_flat"])["pass"],
              "C-ONE max rel k=1:", float(np.max(np.abs(s["X16_push"][0] / b["X16_push"][0] - 1))),
              "k=5 differs:", not np.allclose(s["X16_push"][4], b["X16_push"][4], rtol=1e-9))
print("tmp", tmp)
