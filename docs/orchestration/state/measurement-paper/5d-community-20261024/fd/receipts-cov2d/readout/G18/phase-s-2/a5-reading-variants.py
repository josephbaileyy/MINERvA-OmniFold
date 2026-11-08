import json, sys
T = sys.argv[1]
def cc(k, tol, mrd, ndf=205, cmp=True):
    d = {"rule": "r", "kappa2": k, "eps": 2.2e-16, "tol": tol}
    if cmp: d["compared"] = {"ndf": ndf, "max_rel_diff": mrd, "tol": tol}
    return d
def w(n, a, b): open(f"{T}/{n}.json", "w").write(json.dumps({"cholesky_check": a, "cholesky_check_minus": b}))
g = cc(9.5e11, 2.1e-3, 4e-8); w("ok", g, cc(9.55e11, 2.1e-3, 5e-8))
w("over", g, cc(9.55e11, 2.1e-3, 3e-3))
w("nan", g, cc(9.55e11, 2.1e-3, float("nan")))
w("inf", cc(float("inf"), float("inf"), 4e-8), g)
w("nocmp", g, cc(9.55e11, 2.1e-3, None, cmp=False))
w("ndf204", cc(1e12, 2e-3, None, ndf=204), cc(1e12, 2e-3, None, ndf=204))
w("none_mrd", g, cc(9.55e11, 2.1e-3, None))
