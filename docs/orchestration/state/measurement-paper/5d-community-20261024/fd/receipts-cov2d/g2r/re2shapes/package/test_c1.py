"""Tests of c1_compare.py on synthetic inputs. The fake deploy holds, from <M>: re2c_values.py and re2c_values_spec.tsv
whole, re2c_build_q.metrics verbatim (a stub module with only that function) and build_repair.wcov verbatim (a stub
with that function and the constraint's INPUTS/PINNED, pointed at a synthetic constraint file). The pins are re-pointed
at the synthetic files' digests by assignment on the imported module.
    python3 test_c1.py <wt> <M>"""
import hashlib, importlib.util, io, json, os, re, subprocess, sys, tempfile
import numpy as np
WT, M = sys.argv[1], sys.argv[2]
H = os.path.dirname(os.path.abspath(__file__))
show = lambda p: subprocess.run(["git", "-C", WT, "show", f"{M}:{p}"], capture_output=True, text=True, check=True).stdout
fn = lambda src, name: re.search(rf"^def {name}\(.*\):\n(?:(?:    .*)?\n)+", src, re.M).group(0)
T = tempfile.mkdtemp()
dep = os.path.join(T, "deploy"); pc = os.path.join(dep, "2d-unfolding", "re2", "partc"); os.makedirs(pc)
brd = os.path.join(dep, "docs/orchestration/state/2d-closeout/c04-repair/scripts"); os.makedirs(brd)
open(os.path.join(pc, "re2c_build_q.py"), "w").write("import numpy as np\n\n" + fn(show("2d-unfolding/re2/partc/re2c_build_q.py"), "metrics"))
open(os.path.join(pc, "re2c_values.py"), "w").write(show("2d-unfolding/re2/partc/re2c_values.py"))
open(os.path.join(pc, "re2c_values_spec.tsv"), "w").write(show("2d-unfolding/re2/partc/re2c_values_spec.tsv"))
cons = os.path.join(T, "constraint.txt")
rng = np.random.default_rng(1)
w = rng.uniform(0.5, 3, 100)
open(cons, "w").write("".join(f"Flux {i} {float(w[i])!r}\n" for i in range(100)) + "Other 0 1.0\n")
cons_sha = hashlib.sha256(open(cons, "rb").read()).hexdigest()
wc = fn(show("docs/orchestration/state/2d-closeout/c04-repair/scripts/build_repair.py"), "wcov")
open(os.path.join(brd, "build_repair.py"), "w").write(
    f"import numpy as np\nINPUTS = {{'constraint': {cons!r}}}\nPINNED = {{'constraint': {cons_sha!r}}}\n\n" + wc)
sys.path[:0] = [pc]
import re2c_build_q as bq
spec_ns = {}
exec(open(os.path.join(brd, "build_repair.py")).read(), spec_ns)
wcov = spec_ns["wcov"]
n = 205
A = rng.normal(size=(n, n)); C = A @ A.T * 1e-6
x = rng.uniform(1, 2, n); Fm = rng.normal(size=(31, n)); Fm[0] = rng.uniform(0.1, 1, n)
Uold = C * 0.3; Unew = C * 0.31
G2R = ["Flux", "MaRES", "MvRES", "MaCCQE", "MinosEfficiency"]
LAT = ["Muon_Energy_MINOS", "Muon_Energy_MINERvA"]
bands = {b: rng.normal(size=(100 if b == "Flux" else 2, n)) * 0.01 for b in G2R}
lat = {b: {"median_pct": float(rng.uniform(1, 3)), "integral_sigma_pct": float(rng.uniform(0.1, 1))} for b in LAT}
def budget(Q, band_metrics):
    return {"Q": bq.metrics(Q, x, Fm), "bands": band_metrics}
gm = {b: bq.metrics(wcov(bands[b], w if b == "Flux" else np.ones(bands[b].shape[0])), x, Fm) for b in G2R}
def save(p, raw):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "wb").write(raw); return hashlib.sha256(raw).hexdigest()
def npzb(**k):
    b = io.BytesIO(); np.savez(b, **k); return b.getvalue()
spec = importlib.util.spec_from_file_location("c1", os.path.join(H, "c1_compare.py")); c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)
fails = 0
def case(name, QA, want_rc, xa=x, corrupt=False, bud_a=None, lat_r=None, check=None):
    global fails
    d = os.path.join(T, name)
    c1.DATA_SHA = save(f"{d}/data_g2r.npz", npzb(C_new=C, C_univ_old=Uold, C_univ_new=Unew, **{f"band__{b}": v for b, v in bands.items()}))
    c1.Q_R_SHA = save(f"{d}/r2/outA/cov2d_Q_205.npz", npzb(Q=C * 0.99, x=x))
    c1.S5_R_SHA = save(f"{d}/r2/s5/production_cov.npz", npzb(universe=Uold, functionals=Fm))
    c1.BUDGET_R_SHA = save(f"{d}/r2/outA/budget_Q.json", json.dumps({"bands": lat_r or lat}).encode())
    save(f"{d}/a/outA/cov2d_Q_205.npz", npzb(Q=QA, x=xa))
    save(f"{d}/a/s5/production_cov.npz", npzb(universe=Unew, functionals=Fm))
    save(f"{d}/a/outA/budget_Q.json", json.dumps(bud_a or budget(QA, {**gm, **lat})).encode())
    if corrupt:
        open(f"{d}/data_g2r.npz", "ab").write(b"x")
    sys.argv = ["c1", "--deploy", dep, "--route-a", f"{d}/a", "--partc-r2", f"{d}/r2", "--data-npz", f"{d}/data_g2r.npz", "--out", f"{d}/c1.json"]
    try:
        rc = c1.main()
    except SystemExit as e:
        rc = e.code
    ok = rc == want_rc
    if ok and check:
        ok = check(json.load(open(f"{d}/c1.json")))
    fails += not ok
    print(("PASS" if ok else "FAIL"), name, "rc", rc, "want", want_rc)
case("bitwise", C.copy(), 0, check=lambda r: r["iv_bitwise_equal"] and len(r["b_q_printed"]["rows"]) >= 10 and len(r["c_band_printed"]["rows"]) >= 10)
# an off-diagonal moved by 5e-15 of its diagonal scale: far above 1e-15 of itself if small, within (a)
Q1 = C.copy(); i, j = np.unravel_index(int(np.argmin(np.abs(C))), C.shape); s = np.sqrt(C[i, i] * C[j, j])
Q1[i, j] += 5e-15 * s; Q1[j, i] = Q1[i, j]
case("small-offdiag-within-scaled", Q1, 0, check=lambda r: r["i_per_entry_rel"]["n_above_1e-15"] >= 1 and r["a_entries"]["pass"])
Q2 = C.copy(); Q2[i, j] += 3e-14 * s; Q2[j, i] = Q2[i, j]
case("offdiag-above-scaled", Q2, 1, check=lambda r: not r["a_entries"]["pass"] and r["a_entries"]["n_above"] == 2)
ba = budget(C, {**gm, **lat}); ba["bands"]["Flux"] = dict(ba["bands"]["Flux"], median_pct=ba["bands"]["Flux"]["median_pct"] + 2e-3)
case("g2r-band-median-differs", C.copy(), 1, bud_a=ba, check=lambda r: not r["c_band_printed"]["pass"] and r["b_q_printed"]["pass"])
lr = {b: dict(v) for b, v in lat.items()}; lr["Muon_Energy_MINOS"]["integral_sigma_pct"] += 0.02
case("lateral-differs-from-partc-r2", C.copy(), 1, lat_r=lr, check=lambda r: not r["c_band_printed"]["pass"])
bq_ = budget(C, {**gm, **lat}); bq_["Q"]["median_pct"] += 2e-3
case("route-a-budget-Q-median-differs", C.copy(), 1, bud_a=bq_, check=lambda r: not r["b_q_printed"]["pass"])
case("x-differs", C.copy(), 1, xa=x * (1 + 1e-9))
case("digest", C.copy(), 2, corrupt=True)
for r, ds, fs in os.walk(T, topdown=False):
    for f in fs: os.remove(os.path.join(r, f))
    os.rmdir(r)
print("C1 TEST PASS" if not fails else "C1 TEST FAILED")
sys.exit(1 if fails else 0)
