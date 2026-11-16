"""Tests of ll5d_mumax.py on synthetic inputs (run from the repository root: python3 -I <this file>).
* products_digest_noatime equals ll5d_b.products_digest (the real one, plain reads) on a synthetic unfolds directory, over
  the BLOCK_ROLES products only; a partial product refuses.
* cmd_ll5d with ll5d_b.setup, ll5d_b.remade and fd_1b_mc.made_from stubbed (synthetic blocks whose minus2 C_T is exactly
  C_T - GN - GP; a synthetic null record): clean PASSes and its mu_max equals geant_full.summarize on the fractional
  matrices; a wrong products digest, a made_from different from the null's and a minus2 C_T that is not C_T - G STOP.
* the director's mutant: G perturbed by 1e-9 in a copy of the script STOPs on the removal control; so does a G built
  from GEANT_Neutron alone."""
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "ll5d_mumax.py"
sys.path.insert(0, "nd-unfolding")
import ll5d_b as lb  # noqa: E402

fails = 0


def ok(name, cond):
    global fails
    fails += not cond
    print(("PASS" if cond else "FAIL"), name)


def load(src_text=None):
    spec = importlib.util.spec_from_loader("ll5d_mumax_t", loader=None)
    m = importlib.util.module_from_spec(spec)
    m.__file__ = str(SCRIPT)
    exec(compile(src_text or SCRIPT.read_text(), str(SCRIPT), "exec"), m.__dict__)
    return m


rng = np.random.default_rng(5)
n = 16


def spd(s=1.0):
    A = rng.normal(size=(n, n))
    return (A @ A.T / n + np.eye(n)) * s


def rank1(s):
    v = rng.normal(size=n) * s
    return np.outer(v, v)


X_T = rng.uniform(1, 2, n) * 1e-39
blocks = {"band:GEANT_Neutron": rank1(1e-40), "band:GEANT_Proton": rank1(1e-40), "band:Flux": spd(1e-80), "stat": spd(1e-81)}
C_mabs = spd(2e-81)
C_e = sum(blocks.values())
RM_ALL = {"X_T": X_T, "blocks": blocks, "C_e": C_e, "C_model_abs": C_mabs, "C_T": C_e + C_mabs}
m2b = {k: v for k, v in blocks.items() if not k.startswith("band:GEANT")}
RM_M2 = {"X_T": X_T, "blocks": m2b, "C_e": sum(m2b.values()), "C_model_abs": C_mabs, "C_T": sum(m2b.values()) + C_mabs}
MINUS = np.full(n, 0.5)


MADE = {"U_sha256": "u" * 64, "cmodel_json_sha256": "c" * 64, "definition_sha256": "d" * 64}


def run_ll5d(mod, unfolds, expect, rm_m2=RM_M2, null_made=MADE):
    import fd_1b_mc as mc
    real = (lb.setup, lb.remade, mc.made_from)
    lb.setup = lambda a: ({}, np.eye(n), None, MINUS, None)
    lb.remade = lambda unf, t, s1, U, w, frac, rd: RM_ALL if rd == "all" else rm_m2
    mc.made_from = lambda a, U: dict(MADE)
    sa = sys.modules["s1_assemble"]
    real_mabs = sa.model_abs
    sa.model_abs = lambda x, frac: C_mabs * 0.9
    try:
        W = Path(tempfile.mkdtemp())
        (W / "staged/s1").mkdir(parents=True); (W / "staged/s1/s1_assembly.npz").write_bytes(b"s1"); (W / "cons.txt").write_bytes(b"c")
        (W / "null-g18.json").write_text(json.dumps({"truth": "g18", "products_sha256": expect, "made_from": null_made}))
        out = W / "m.json"
        rc = mod.main(["ll5d", "--staged", str(W / "staged"), "--definition", "/d", "--unfolds", str(unfolds), "--cmodel-json", "/c",
                       "--flux-constraint", str(W / "cons.txt"), "--null", str(W / "null-g18.json"), "--out", str(out)])
        return rc, json.loads(out.read_text())
    finally:
        lb.setup, lb.remade, mc.made_from = real
        sa.model_abs = real_mabs


with tempfile.TemporaryDirectory() as T:
    U = Path(T)
    for role, items in (("central", ["T"]), ("seed", ["T"]), ("block", ["GEANT_Neutron_0", "Flux_1"]), ("stat", ["1", "2"]),
                        ("toy", ["all_1"])):
        for it in items:
            b = io.BytesIO(); np.savez(b, xsec_flat=rng.normal(size=4)); (U / f"ll5d_g18_{role}_{it}.npz").write_bytes(b.getvalue())
    mod = load()
    d, cnt = mod.products_digest_noatime(U, "g18", lb.BLOCK_ROLES, lb.TAG)
    ok(f"digest: O_NOATIME construction equals ll5d_b.products_digest ({cnt} products, toy excluded)",
       d == lb.products_digest(U, "g18", lb.BLOCK_ROLES) and cnt == 6)
    (U / "ll5d_g18_block_x.partial-1").write_bytes(b"x")
    try:
        mod.products_digest_noatime(U, "g18", lb.BLOCK_ROLES, lb.TAG); ok("digest: a partial product refuses", False)
    except SystemExit:
        ok("digest: a partial product refuses", True)
    (U / "ll5d_g18_block_x.partial-1").unlink()
    gf = mod.load_geant_full()
    rc, rec = run_ll5d(mod, U, d)
    G = blocks["band:GEANT_Neutron"] + blocks["band:GEANT_Proton"]
    ss = np.outer(X_T, X_T)
    want = gf.summarize(G / ss, RM_ALL["C_T"] / ss, mod.json.loads(mod.S1_CELLS_JSON.read_text())["cells"])
    r = rec["truths"]["g18"]
    ok(f"clean: PASS, removal dev {r['removal_control_on_G']['max_abs_dev']:.2e}, mu_max equals geant_full.summarize",
       rc == 0 and rec["verdict"] == "PASS" and r["primary C_T (all)"]["mu_max"] == want["mu_max"]
       and "secondary C_T^- (all, leave-out-MEC)" in r)
    rc, rec = run_ll5d(mod, U, "0" * 64)
    ok("a wrong expected products digest STOPs", rc == 2 and rec["stop"] == ["g18: the products at T are not the null's"])
    rc, rec = run_ll5d(mod, U, d, null_made=dict(MADE, cmodel_json_sha256="e" * 64))
    ok("a made_from different from the null's STOPs", rc == 2 and rec["stop"] == ["g18: made_from is not the null's"])
    bad = dict(RM_M2, C_T=RM_M2["C_T"] + 1e-9 * np.max(np.abs(RM_ALL["C_T"])) * np.eye(n))
    rc, rec = run_ll5d(mod, U, d, bad)
    ok("a minus2 C_T that is not C_T - G STOPs", rc == 2 and "removal control failed" in rec["stop"][0])
    src = SCRIPT.read_text()
    a = 'G = rm_all["blocks"][GEANT[0]] + rm_all["blocks"][GEANT[1]]'
    assert src.count(a) == 1
    for label, b_ in (("G perturbed by 1e-9", '(' + a[4:] + ') * (1 + 1e-9)'), ("G from GEANT_Neutron alone", 'rm_all["blocks"][GEANT[0]]')):
        mut = load(src.replace(a, "G = " + b_))
        rc, rec = run_ll5d(mut, U, d)
        ok(f"mutant {label}: the removal control STOPs", rc == 2 and "removal control failed" in rec["stop"][0])
print("LL5D-MUMAX TEST PASS" if not fails else "LL5D-MUMAX TEST FAILED")
sys.exit(1 if fails else 0)
