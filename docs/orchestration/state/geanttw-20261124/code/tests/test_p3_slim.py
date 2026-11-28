"""p3_slim.py (one pass) and slim_tparams.py on fixtures. The 12 playlist blocks model Phase 17: per playlist, signal
and denominator rows are equal in number, and the misses are the signal block's last rows. They are an ordered
subsequence of the truth rows with sim_pass 0, sim -9999 and the CV proxy in every target. UOMNI is the hadd
concatenation; the dumps are the patched blocks. uproot cannot write TParameters, so `tparam` and `top_keys` are
replaced with fixture values; the cluster's verify reads the real ones."""
import hashlib
import importlib.util
import json
import os
import types
from pathlib import Path

import numpy as np
import pytest
import uproot

CODE = Path(__file__).resolve().parents[1]
REPO = Path(os.environ.get("GEANTTW_REPO") or CODE.parents[4])   # a copy of code/ is told the repo
assert (REPO / "2d-unfolding").is_dir(), f"no repository at {REPO}: set GEANTTW_REPO"
DRIVER = REPO / "2d-unfolding" / "unfold_2d_omnifold_unbinned.py"
PLS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
G = [f"GEANT_{b}_{i}" for b in ("Neutron", "Pion", "Proton") for i in (0, 1)]
NS = [5 + i % 3 for i in range(12)]
MS = [1 + i % 2 for i in range(12)]
ND, NB = [3] * 12, [2] * 12
BLOCKS = {"data": ND, "mc_background": NB, "mc_truth_denom": NS, "mc_signal_reco": NS}
os.environ["P3SLIM_TEST"] = "1"
os.environ["P3SLIM_TEST_BLOCKS"] = json.dumps(BLOCKS)


def _load(name):
    s = importlib.util.spec_from_file_location(name, CODE / f"{name}.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


PS = _load("p3_slim")
UVALS = {"dataPOTUsed": 1.0e21, "mcPOTUsed": 5.0e21, "hasTruthOnlyMisses": 1, "nTruthOnlyMisses": sum(MS)}
UCLASS = {"dataPOTUsed": "TParameter<double>", "mcPOTUsed": "TParameter<double>", "hasTruthOnlyMisses": "TParameter<int>",
          "nTruthOnlyMisses": "TParameter<long>"}   # p2p3/d1/d1.out


def block(i, rng):
    n, m = NS[i], MS[i]
    den = {"MC": rng.uniform(0, 4, n), "MC_pz": rng.uniform(1.5, 60, n), "w_truth": rng.uniform(0.5, 2, n)}
    pin = {f"w_truth_{g}": den["w_truth"] * (1 + 0.01 * (k + 1)) for k, g in enumerate(G)}
    pat = {f"w_truth_{g}": den["w_truth"] * (1 + 0.1 * (k + 1)) for k, g in enumerate(G)}
    reco = rng.permutation(n)[: n - m]
    miss = np.sort(np.setdiff1d(np.arange(n), reco))
    order = np.concatenate([reco, miss])
    base = {k: v[order] for k, v in den.items()}
    sim = rng.uniform(0, 4, n)
    sim[n - m:] = -9999.0
    base.update(sim=sim, sim_pz=rng.uniform(1.5, 60, n), sim_pass=np.r_[np.ones(n - m), np.zeros(m)].astype(np.uint8))
    for g in G:
        base[f"w_reco_{g}"] = base["w_truth"] * 1.3

    def sig(tw):
        d = dict(base)
        for g in G:
            t = tw[f"w_truth_{g}"][order].copy()
            t[n - m:] = den["w_truth"][miss]
            d[f"w_truth_{g}"] = t
        return d
    data = {"measured": rng.uniform(0, 4, ND[i]), "measured_pz": rng.uniform(1.5, 60, ND[i]),
            "measured_pass": np.ones(ND[i], dtype=np.uint8)}
    bkg = {"sim_background": rng.uniform(0, 4, NB[i]), "sim_background_pz": rng.uniform(1.5, 60, NB[i]),
           "sim_background_pass": np.ones(NB[i], dtype=np.uint8), **{f"w_bkg_{g}": rng.uniform(0, 1, NB[i]) for g in G}}
    return {"n": n, "m": m, "miss": miss, "den": den, "data": data, "bkg": bkg,
            "pin": (sig(pin), {**den, **pin}), "pat": (sig(pat), {**den, **pat})}


def write(path, trees, extra=True):
    with uproot.recreate(path) as f:
        for t, c in trees.items():
            f[t] = {**c, **({"extra": np.zeros(len(next(iter(c.values()))))} if extra else {})}


def names(f):
    fp = f.file_path
    return os.path.basename(fp) if isinstance(fp, str) else "uomni.root"


@pytest.fixture
def ws(tmp_path, monkeypatch):
    rng = np.random.default_rng(1)
    bl = [block(i, rng) for i in range(12)]
    cat = lambda f: {k: np.concatenate([f(b)[k] for b in bl]) for k in f(bl[0])}
    write(tmp_path / "uomni.root", {"data": cat(lambda b: b["data"]), "mc_background": cat(lambda b: b["bkg"]),
                                    "mc_signal_reco": cat(lambda b: b["pin"][0]),
                                    "mc_truth_denom": cat(lambda b: b["pin"][1])})
    dumps = []
    for pl, b in zip(PLS, bl):
        d = tmp_path / f"pat_{pl}.root"
        write(d, {"data": b["data"], "mc_background": b["bkg"], "mc_signal_reco": b["pat"][0],
                  "mc_truth_denom": b["pat"][1]})
        dumps.append(str(d))
    vals = {"uomni.root": UVALS, **{f"pat_{pl}.root": {"nTruthOnlyMisses": m} for pl, m in zip(PLS, MS)}}
    real_top = PS.top_keys
    monkeypatch.setattr(PS, "tparam", lambda f, n: vals.get(names(f), UVALS)[n])
    monkeypatch.setattr(PS, "top_keys", lambda f: real_top(f) | set(PS.TPARAMS))
    monkeypatch.setattr(PS, "tpclass", lambda f, n: UCLASS[n])
    mc = tmp_path / "mc.root"
    mc.write_bytes(b"mcfile")
    out = tmp_path / "p3"
    out.mkdir()
    return {"vals": vals, "tmp": tmp_path, "bl": bl, "dumps": dumps, "u": str(tmp_path / "uomni.root"), "out": out, "mc": mc,
            "mc_sha": hashlib.sha256(b"mcfile").hexdigest()}


def main(*a):
    return PS.main([str(x) for x in a])


def build(ws, u=None, driver=DRIVER):
    return main("build", "--uomni", u or ws["u"], "--driver", driver, "--dumps", *ws["dumps"], "--outdir", ws["out"],
                "--record", ws["tmp"] / "build.json", "--c2", ws["tmp"] / "c2.json")


def verify(ws):
    return main("verify", "--driver", DRIVER, "--outdir", ws["out"], "--record",
                ws["tmp"] / "build.json", "--mcfile", ws["mc"], "--mcfile-sha", ws["mc_sha"], "--out", ws["tmp"] / "slim.json")


def arr(ws, slim, t, b):
    return uproot.open(ws["out"] / PS.SLIMS[slim])[t][b].array(library="np")


def slim_out(ws):
    return json.loads((ws["tmp"] / "slim.json").read_text())


# ── C1-a, in build's one open
def test_c1a_passes_with_the_real_driver(ws, capsys):
    assert build(ws) == 0
    assert "C1-a PASS: the pinned 37 branches" in capsys.readouterr().out


@pytest.mark.parametrize("tree", ["mc_truth_denom", "mc_signal_reco"])
def test_c1a_checks_each_trees_key_branch(ws, tmp_path, tree, capsys):
    f = uproot.open(ws["u"])
    write(tmp_path / "u2.root", {t: {b: f[t][b].array(library="np") for b in f[t].keys()
                                     if not (t == tree and b == "w_truth")} for t in PS.TREES}, extra=False)
    assert build(ws, u=tmp_path / "u2.root") == 1 and f"{tree}:w_truth absent" in capsys.readouterr().out
    assert not (ws["tmp"] / "build.json").exists()


def test_c1a_fails_if_a_lateral_probe_is_present(ws, tmp_path):
    drv = PS.load_driver(DRIVER)
    lat = drv._universe_kine_branches(("GEANT_Pion", 0), "truth_tree")[0]
    f = uproot.open(ws["u"])
    trees = {t: {b: f[t][b].array(library="np") for b in f[t].keys()} for t in PS.TREES}
    trees["mc_truth_denom"][lat] = np.zeros(sum(NS))
    write(tmp_path / "u3.root", trees, extra=False)
    assert build(ws, u=tmp_path / "u3.root") == 1


def test_c1a_fails_if_a_tparameter_is_absent(ws, monkeypatch):
    monkeypatch.setattr(PS, "top_keys", lambda f: set(PS.TREES))
    assert build(ws) == 1


def test_c1a_fails_if_the_driver_probes_top_level_object_is_present(ws, monkeypatch, capsys):
    real = PS.top_keys
    monkeypatch.setattr(PS, "top_keys", lambda f: real(f) | {"pTmu_fiducial_nucleons"})
    assert build(ws) == 1 and "the driver's probe pTmu_fiducial_nucleons is in UOMNI" in capsys.readouterr().out


def test_c1a_fails_if_the_driver_selects_otherwise(ws, tmp_path):
    fake = tmp_path / "drv.py"
    fake.write_text("def expected_loader_branches(l, s, p):\n    return ['measured']\n"
                    "def _universe_kine_branches(u, c):\n    return ('x', 'y')\n")
    assert build(ws, driver=fake) == 1


def test_uomni_is_opened_once_by_build_and_never_by_verify(ws, monkeypatch):
    opened = []
    real = PS.open_noatime
    monkeypatch.setattr(PS, "open_noatime", lambda p: opened.append(p) or real(p))
    assert build(ws) == 0 and opened == [ws["u"]]
    assert verify(ws) == 0 and opened == [ws["u"]]


def test_the_build_records_uomnis_metadata(ws):
    assert build(ws) == 0
    meta = json.loads((ws["tmp"] / "build.json").read_text())["uomni"]
    assert meta["tparams"] == {n: {"class": UCLASS[n], "value": UVALS[n]} for n in PS.TPARAMS}
    assert meta["typenames"]["data"] == {"measured": "double", "measured_pz": "double", "measured_pass": "uint8_t"}


def test_the_grant_is_written_out_and_is_39_branches():
    assert sum(len(v) for v in PS.GRANTED.values()) == 39
    assert {t: set(PS.SLIM[t]) | set(PS.KEY_READ.get(t, [])) for t in PS.TREES} == {t: set(v) for t, v in PS.GRANTED.items()}
    assert "frozenset(SLIM" not in (CODE / "p3_slim.py").read_text()


# ── one pass: build, then verify
def test_build_and_verify_pass(ws, capsys):
    assert build(ws) == 0, capsys.readouterr().out
    assert json.loads((ws["tmp"] / "c2.json").read_text())["verdict"] == "PASS"
    assert verify(ws) == 0, capsys.readouterr().out
    s = slim_out(ws)
    assert s["verdict"] == "PASS" and set(s["slims"]) == {"pin", "pinov", "patov"}
    assert s["mcfile"]["sha256"] == ws["mc_sha"] and s["mcfile"]["size"] == 6
    for k in ("pin", "pinov", "patov"):
        assert set(uproot.open(ws["out"] / PS.SLIMS[k])["mc_signal_reco"].keys()) == set(PS.SLIM["mc_signal_reco"])


def test_build_reads_exactly_the_granted_branches(ws):
    assert build(ws) == 0
    got = json.loads((ws["tmp"] / "build.json").read_text())["uomni_branches_read"]
    assert len(got) == 39 and got == sorted(f"{t}:{b}" for t in PS.TREES for b in PS.GRANTED[t])


@pytest.mark.parametrize("which,val", [("nTruthOnlyMisses", sum(MS) + 1), ("hasTruthOnlyMisses", 0)])
def test_build_refuses_misses_that_are_not_uomnis(ws, monkeypatch, capsys, which, val):
    real = PS.tparam
    monkeypatch.setattr(PS, "tparam", lambda f, n: val if (names(f) == "uomni.root" and n == which) else real(f, n))
    assert build(ws) == 2 and "not UOMNI's nTruthOnlyMisses" in capsys.readouterr().out


def test_uread_refuses_a_branch_outside_the_grant(ws):
    with pytest.raises(PS.Unusable, match="outside cov2d's grant"):
        PS.uread(uproot.open(ws["u"]), "mc_signal_reco", "extra")
    with pytest.raises(PS.Unusable, match="outside cov2d's grant"):
        PS.uread(uproot.open(ws["u"]), "data", "w_truth")


def test_build_refuses_if_it_read_other_than_the_grant(ws, monkeypatch, capsys):
    monkeypatch.setattr(PS, "GRANTED", {**PS.GRANTED, "data": PS.GRANTED["data"] | {"extra"}})
    assert build(ws) == 2 and "not exactly the grant's" in capsys.readouterr().out


def test_the_overrides_put_each_denominator_on_its_misses(ws):
    assert build(ws) == 0
    lo = 0
    pin, pinov, patov = (arr(ws, k, "mc_signal_reco", "w_truth_GEANT_Pion_1") for k in ("pin", "pinov", "patov"))
    for b in ws["bl"]:
        tail = slice(lo + b["n"] - b["m"], lo + b["n"])
        assert np.array_equal(pin[tail], b["den"]["w_truth"][b["miss"]])                     # the CV proxy kept
        assert np.array_equal(pinov[tail], b["pin"][1]["w_truth_GEANT_Pion_1"][b["miss"]])   # pinned truth
        assert np.array_equal(patov[tail], b["pat"][1]["w_truth_GEANT_Pion_1"][b["miss"]])   # patched truth
        lo += b["n"]
    assert np.array_equal(arr(ws, "patov", "mc_truth_denom", "w_truth_GEANT_Pion_1"),
                          np.concatenate([b["pat"][1]["w_truth_GEANT_Pion_1"] for b in ws["bl"]]))
    assert np.array_equal(arr(ws, "pinov", "mc_signal_reco", "sim_pz"), arr(ws, "patov", "mc_signal_reco", "sim_pz"))


def test_c2_fails_on_one_changed_non_target_value(ws, capsys):
    f = uproot.open(ws["dumps"][4])
    trees = {t: {b: f[t][b].array(library="np") for b in f[t].keys()} for t in PS.TREES}
    trees["mc_background"]["w_bkg_GEANT_Pion_0"][0] += 1e-12
    write(ws["dumps"][4], trees, extra=False)
    assert build(ws) == 1
    c2 = json.loads((ws["tmp"] / "c2.json").read_text())
    assert c2["verdict"] == "FAIL" and c2["differ"] == ["1E:mc_background:w_bkg_GEANT_Pion_0"]


@pytest.mark.parametrize("col,val", [("sim_pass", 1), ("sim", 1.0), ("w_truth_GEANT_Pion_0", 7.0)])
def test_a_tail_that_is_not_misses_fails(ws, col, val, capsys):
    """The same change in UOMNI and in the dump, so C2 still passes and the tail check is what fails."""
    f = uproot.open(ws["dumps"][2])
    trees = {t: {b: f[t][b].array(library="np") for b in f[t].keys()} for t in PS.TREES}
    trees["mc_signal_reco"][col][-1] = val
    write(ws["dumps"][2], trees, extra=False)
    if col != "w_truth_GEANT_Pion_0":   # a non-target column: change UOMNI's copy of that row too
        u = uproot.open(ws["u"])
        ut = {t: {b: u[t][b].array(library="np") for b in u[t].keys()} for t in PS.TREES}
        ut["mc_signal_reco"][col][sum(NS[:3]) - 1] = val
        write(ws["u"], ut, extra=False)
    assert build(ws) == 1 and "are not misses with the CV proxy" in capsys.readouterr().out


def test_a_block_split_that_keeps_the_totals_fails(ws, monkeypatch, capsys):
    """1A and 1B's sizes swapped: every total is still UOMNI's, so only the per-block check sees it."""
    mc = (NS[1], NS[0]) + tuple(NS[2:])
    assert NS[0] != NS[1]
    monkeypatch.setattr(PS, "BLOCKS", {**PS.BLOCKS, "mc_truth_denom": mc, "mc_signal_reco": mc})
    assert build(ws) == 1 and "1A: the dump's" in capsys.readouterr().out


def test_an_understated_miss_count_fails(ws, capsys):
    """1B has 2 misses; a dump saying 1 leaves the tail check a valid 1-row suffix, but the row before is a miss."""
    assert MS[1] == 2
    ws["vals"]["pat_1B.root"]["nTruthOnlyMisses"] = 1
    assert build(ws) == 1 and "the row before the last 1 is also a miss" in capsys.readouterr().out


def test_a_dump_block_of_the_wrong_size_fails(ws, monkeypatch, capsys):
    monkeypatch.setattr(PS, "BLOCKS", {**PS.BLOCKS, "data": (4,) + tuple(ND[1:])})
    assert build(ws) == 2   # UOMNI's data total no longer matches C4's


def test_a_block_over_the_memory_cap_stops_before_reading(ws, monkeypatch, capsys):
    monkeypatch.setattr(PS, "MAX_ROWS", 6)
    assert build(ws) == 2 and "blocks over 6 rows" in capsys.readouterr().out


@pytest.mark.parametrize("case", ["eleven", "exists"])
def test_build_refusals(ws, case, capsys):
    if case == "eleven":
        ws["dumps"] = ws["dumps"][:11]
    else:
        (ws["out"] / "slim-patched.root").write_text("x")
    assert build(ws) == 2


@pytest.mark.parametrize("tamper", ["value", "extra_branch", "dtype"])
def test_verify_fails_on_a_tampered_slim(ws, tamper, capsys):
    assert build(ws) == 0
    p = ws["out"] / PS.SLIMS["pinov"]
    f = uproot.open(p)
    trees = {t: {b: f[t][b].array(library="np") for b in f[t].keys()} for t in PS.TREES}
    if tamper == "value":
        trees["mc_signal_reco"]["w_truth_GEANT_Proton_0"][3] *= 2
    elif tamper == "extra_branch":
        trees["data"]["leak"] = np.zeros(sum(ND))
    else:
        trees["mc_truth_denom"]["MC"] = trees["mc_truth_denom"]["MC"].astype(np.float32)
    write(p, trees, extra=False)
    assert verify(ws) == 1 and slim_out(ws)["verdict"] == "FAIL"


def test_verify_fails_on_a_tparameter_class_mismatch(ws, monkeypatch):
    assert build(ws) == 0
    monkeypatch.setattr(PS, "tpclass", lambda f, n: "TParameter<float>" if names(f) == "slim-patched.root" else UCLASS[n])
    assert verify(ws) == 1 and any("slim-patched.root: TParameter" in x for x in slim_out(ws)["problems"])


def test_verify_fails_on_a_tparameter_mismatch(ws, monkeypatch):
    assert build(ws) == 0
    real = PS.tparam
    monkeypatch.setattr(PS, "tparam", lambda f, n: real(f, n) + (1 if names(f) == "slim-pinned-override.root" else 0))
    assert verify(ws) == 1 and any("TParameter" in x for x in slim_out(ws)["problems"])


def test_verify_fails_on_another_mcfile(ws):
    assert build(ws) == 0
    ws["mc_sha"] = "0" * 64
    assert verify(ws) == 1


# ── the override's own refusals
def test_override_refuses_misses_out_of_order():
    b = block(3, np.random.default_rng(2))
    sig, den = b["pat"]
    s2 = {k: v.copy() for k, v in sig.items()}
    m = b["m"] + 1
    for k in ("MC", "MC_pz", "w_truth"):
        s2[k][-m:] = s2[k][-m:][::-1].copy()
    with pytest.raises(PS.Fail):
        PS.override_block(s2, den, m, "x")


def test_override_refuses_duplicate_keys():
    b = block(0, np.random.default_rng(2))
    sig, den = b["pat"]
    den = {k: v.copy() for k, v in den.items()}
    for k in ("MC", "MC_pz", "w_truth"):
        den[k][1] = den[k][0]
    with pytest.raises(PS.Fail, match="not unique"):
        PS.override_block(sig, den, b["m"], "x")


def test_c_miss_keys_include_w_truth():
    """Two truth rows with the same kinematics and different CV weights, with their targets swapped in the
    denominator: the matching is by w_truth, so C-MISS's multiset includes it and still holds."""
    b = block(0, np.random.default_rng(2))
    sig, den = (dict(x) for x in b["pat"])
    out = PS.override_block(sig, den, b["m"], "x")
    for g in G:
        k = f"w_truth_{g}"
        assert PS.sorted_equal(PS.keys(sig["MC"], sig["MC_pz"], sig["w_truth"], out[k]),
                               PS.keys(den["MC"], den["MC_pz"], den["w_truth"], den[k]))


def test_equal_kinematics_misses_are_matched_by_w_truth():
    """Two truth rows with the same (MC, MC_pz) and different w_truth, both misses: each miss gets its own row's
    target, because the key includes w_truth."""
    den = {"MC": np.array([1.0, 2.0, 2.0]), "MC_pz": np.array([5.0, 7.0, 7.0]), "w_truth": np.array([1.0, 1.5, 0.5])}
    for k, g in enumerate(G):
        den[f"w_truth_{g}"] = np.array([10.0, 20.0, 30.0]) + k
    sig = {"MC": den["MC"].copy(), "MC_pz": den["MC_pz"].copy(), "w_truth": den["w_truth"].copy()}
    for g in G:
        sig[f"w_truth_{g}"] = np.r_[den[f"w_truth_{g}"][0], den["w_truth"][1:]]   # the CV proxy on the 2 misses
    out = PS.override_block(sig, den, 2, "x")
    for g in G:
        assert np.array_equal(out[f"w_truth_{g}"], den[f"w_truth_{g}"])


def test_c_miss_fails_when_a_reco_row_disagrees_with_its_denominator():
    """A reco-matched signal row whose target is not its event's denominator value: the multisets then differ."""
    b = block(0, np.random.default_rng(2))
    sig, den = (dict(x) for x in b["pat"])
    sig = {k: v.copy() for k, v in sig.items()}
    sig["w_truth_GEANT_Pion_0"][0] *= 1.0001
    with pytest.raises(PS.Fail, match="C-MISS FAIL"):
        PS.override_block(sig, den, b["m"], "x")


@pytest.mark.skipif(hasattr(os, "O_NOATIME"), reason="this OS has O_NOATIME")
def test_outside_the_tests_no_noatime_is_unusable(ws, monkeypatch, capsys):
    monkeypatch.setattr(PS, "NOATIME_OPTIONAL", False)
    assert build(ws) == 2 and "no O_NOATIME" in capsys.readouterr().out


def test_the_real_blocks_are_c4s():
    s = (CODE / "p3_slim.py").read_text()
    assert '"mc_signal_reco": (2682267, 721082, 1376832, 4003632, 3350021, 4660210, 3922748, 383848, 5917406, 3416266,' in s
    assert "MAX_ROWS = 6_500_000" in s


# ── slim_tparams.py, against a fake ROOT: it writes from build's record and never opens UOMNI
_CURRENT = {}


class _Obj:
    """Writes into the current directory, as ROOT's TObject::Write does after TFile::cd."""
    def __init__(self, cls, name, val):
        self.cls, self.name, self.val = cls, name, val

    def Write(self, name):
        _CURRENT["dir"].written.append((name, self.cls, self.val))
        _CURRENT["dir"].objs[name] = self


class _File:
    def __init__(self, objs, zombie=False):
        self.objs, self.written, self.zombie = dict(objs), [], zombie

    def IsZombie(self):
        return self.zombie

    def Get(self, n):
        return self.objs.get(n)

    def cd(self):
        _CURRENT["dir"] = self

    def Close(self):
        pass


def fake_root(files):
    opened = []

    def open_(p, mode):
        opened.append((p, mode))
        return files.get(p)
    return types.SimpleNamespace(TFile=types.SimpleNamespace(Open=open_),
                                 TParameter=lambda T: (lambda n, v: _Obj(T, n, v)), opened=opened)


def record(**drop):
    tp = {n: {"class": UCLASS[n], "value": UVALS[n]} for n in UCLASS}
    for n, how in drop.items():
        if how == "missing":
            del tp[n]
        else:
            tp[n]["class"] = how
    return {"uomni": {"tparams": tp}}


def test_tparams_are_written_from_the_record_into_each_slim():
    ST = _load("slim_tparams")
    s1, s2 = _File({}), _File({})
    root = fake_root({"S1": s1, "S2": s2})
    assert ST.write(root, record(), ["S1", "S2"]) is None
    want = [(n, UCLASS[n][len("TParameter<"):-1], UVALS[n]) for n in ST.TPARAMS]
    assert s1.written == want and s2.written == want
    assert root.opened == [("S1", "UPDATE"), ("S2", "UPDATE")]   # never UOMNI


@pytest.mark.parametrize("case", ["missing", "badclass", "already", "unopenable", "zombie"])
def test_tparams_refusals(case):
    ST = _load("slim_tparams")
    rec = record(nTruthOnlyMisses="missing") if case == "missing" else (
        record(mcPOTUsed="TParameter<float>") if case == "badclass" else record())
    s = _File({"mcPOTUsed": object()} if case == "already" else {}, zombie=case == "zombie")
    files = {"S": s} if case != "unopenable" else {}
    assert ST.write(fake_root(files), rec, ["S"]) is not None


def test_tparams_cli_refusals(tmp_path, capsys):
    ST = _load("slim_tparams")
    assert ST.main(["only-one"]) == 2
    assert ST.main([str(tmp_path / "absent.json"), "S"]) == 2 and "cannot read" in capsys.readouterr().out



# ── the records' form, argparse, and the defaults
def test_every_record_is_canonical_json(ws):
    assert build(ws) == 0 and verify(ws) == 0
    for f in ("c2.json", "build.json", "slim.json"):
        t = (ws["tmp"] / f).read_text()
        assert t == json.dumps(json.loads(t), indent=1, sort_keys=True), f


def test_a_c2_failure_record_is_canonical_json(ws):
    f = uproot.open(ws["dumps"][4])
    trees = {t: {b: f[t][b].array(library="np") for b in f[t].keys()} for t in PS.TREES}
    trees["data"]["measured"][0] += 1
    write(ws["dumps"][4], trees, extra=False)
    assert build(ws) == 1
    t = (ws["tmp"] / "c2.json").read_text()
    assert t == json.dumps(json.loads(t), indent=1, sort_keys=True) and json.loads(t)["verdict"] == "FAIL"


@pytest.mark.parametrize("args", [
    ["build", "--driver", "d", "--outdir", "o", "--record", "r", "--c2", "c", "--dumps", "x"],
    ["build", "--uomni", "u", "--outdir", "o", "--record", "r", "--c2", "c", "--dumps", "x"],
    ["build", "--uomni", "u", "--driver", "d", "--record", "r", "--c2", "c", "--dumps", "x"],
    ["build", "--uomni", "u", "--driver", "d", "--outdir", "o", "--c2", "c", "--dumps", "x"],
    ["build", "--uomni", "u", "--driver", "d", "--outdir", "o", "--record", "r", "--dumps", "x"],
    ["build", "--uomni", "u", "--driver", "d", "--outdir", "o", "--record", "r", "--c2", "c"],
    ["verify", "--outdir", "o", "--record", "r", "--mcfile", "m", "--mcfile-sha", "s", "--out", "x"],
    ["verify", "--driver", "d", "--record", "r", "--mcfile", "m", "--mcfile-sha", "s", "--out", "x"],
    ["verify", "--driver", "d", "--outdir", "o", "--mcfile", "m", "--mcfile-sha", "s", "--out", "x"],
    ["verify", "--driver", "d", "--outdir", "o", "--record", "r", "--mcfile-sha", "s", "--out", "x"],
    ["verify", "--driver", "d", "--outdir", "o", "--record", "r", "--mcfile", "m", "--out", "x"],
    ["verify", "--driver", "d", "--outdir", "o", "--record", "r", "--mcfile", "m", "--mcfile-sha", "s"],
    [],
])
def test_every_argument_is_required(args):
    with pytest.raises(SystemExit) as e:
        PS.main(args)
    assert e.value.code == 2


def test_noatime_is_required_outside_the_tests():
    import subprocess
    import sys
    env = {k: v for k, v in os.environ.items() if not k.startswith("P3SLIM_TEST")}
    r = subprocess.run([sys.executable, "-I", "-c", "import importlib.util as u, sys; s = u.spec_from_file_location('p', sys.argv[1]); "
                        "m = u.module_from_spec(s); s.loader.exec_module(m); print(m.NOATIME_OPTIONAL)", str(CODE / "p3_slim.py")],
                       capture_output=True, text=True, env=env)
    assert r.stdout.strip() == "False", r.stderr


def test_override_refuses_a_denominator_of_another_length():
    b = block(0, np.random.default_rng(2))
    sig, den = b["pat"]
    den = {k: v[:-1] for k, v in den.items()}
    with pytest.raises(PS.Unusable, match="signal"):
        PS.override_block(sig, den, b["m"], "x")


def test_tparams_main_writes_through_root(tmp_path, monkeypatch):
    """main with a record and a slim imports ROOT, sets batch mode and writes; nothing opens UOMNI."""
    import sys
    ST = _load("slim_tparams")
    s1 = _File({})
    root = fake_root({str(tmp_path / "s.root"): s1})
    batch = []
    root.gROOT = types.SimpleNamespace(SetBatch=lambda v: batch.append(v))
    monkeypatch.setitem(sys.modules, "ROOT", root)
    rec = tmp_path / "build.json"
    rec.write_text(json.dumps(record()))
    assert ST.main([str(rec), str(tmp_path / "s.root")]) == 0
    assert batch == [True] and [w[0] for w in s1.written] == list(ST.TPARAMS)
