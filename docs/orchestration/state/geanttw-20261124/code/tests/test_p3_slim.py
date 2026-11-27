"""p3_slim.py and slim_tparams.py on fixtures. The 12 playlist blocks model Phase 17: per playlist, signal and
denominator rows are equal in number, the misses are the signal block's last rows (an ordered subsequence of the
truth rows, carrying the CV proxy), and UOMNI is the hadd concatenation. TParameters cannot be written by uproot,
so `tparam` is replaced with fixture values; the cluster's C-SLIM reads the real ones."""
import importlib.util
import os
import types
from pathlib import Path

import numpy as np
import pytest
import uproot

CODE = Path(__file__).resolve().parents[1]
REPO = CODE.parents[4]
DRIVER = REPO / "2d-unfolding" / "unfold_2d_omnifold_unbinned.py"


def _load(name):
    s = importlib.util.spec_from_file_location(name, CODE / f"{name}.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


PS = _load("p3_slim")
PLS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
G = [f"GEANT_{b}_{i}" for b in ("Neutron", "Pion", "Proton") for i in (0, 1)]


def blocks(seed=1):
    """Per playlist: pinned and patched (signal, denominator) column dicts, and the miss count."""
    rng = np.random.default_rng(seed)
    out = []
    for i, pl in enumerate(PLS):
        n, m = 5 + i % 3, 1 + i % 2
        den = {"MC": rng.uniform(0, 4, n), "MC_pz": rng.uniform(1.5, 60, n), "w_truth": rng.uniform(0.5, 2, n)}
        pin_den = {f"w_truth_{g}": den["w_truth"] * (1 + 0.01 * (k + 1)) for k, g in enumerate(G)}
        pat_den = {f"w_truth_{g}": den["w_truth"] * (1 + 0.1 * (k + 1)) for k, g in enumerate(G)}
        reco = rng.permutation(n)[: n - m]                  # the reco-matched truth rows, in reco order
        miss = np.sort(np.setdiff1d(np.arange(n), reco))    # the rest, in truth order
        order = np.concatenate([reco, miss])
        sig_base = {k: v[order] for k, v in den.items()}
        sig_base.update(sim=rng.uniform(0, 4, n), sim_pz=rng.uniform(1.5, 60, n), sim_pass=np.ones(n, dtype=bool))
        def sig(tw):
            d = dict(sig_base)
            for k, g in enumerate(G):
                t = tw[f"w_truth_{g}"][order].copy()
                t[n - m:] = den["w_truth"][miss]           # the CV proxy on the misses
                d[f"w_truth_{g}"] = t
                d[f"w_reco_{g}"] = sig_base["w_truth"] * 1.3
            return d
        out.append({"pl": pl, "m": m, "den": den, "pin": (sig(pin_den), {**den, **pin_den}),
                    "pat": (sig(pat_den), {**den, **pat_den}), "miss": miss, "n": n})
    return out


def other_trees(n_data=7, n_bkg=4):
    rng = np.random.default_rng(5)
    data = {"measured": rng.uniform(0, 4, n_data), "measured_pz": rng.uniform(1.5, 60, n_data),
            "measured_pass": np.ones(n_data, dtype=bool)}
    bkg = {"sim_background": rng.uniform(0, 4, n_bkg), "sim_background_pz": rng.uniform(1.5, 60, n_bkg),
           "sim_background_pass": np.ones(n_bkg, dtype=bool), **{f"w_bkg_{g}": rng.uniform(0, 1, n_bkg) for g in G}}
    return data, bkg


def write(path, trees):
    with uproot.recreate(path) as f:
        for t, c in trees.items():
            f[t] = {**c, "extra": np.zeros(len(next(iter(c.values()))))}


@pytest.fixture
def ws(tmp_path, monkeypatch):
    bl = blocks()
    data, bkg = other_trees()
    cat = lambda side, j: {k: np.concatenate([b[side][j][k] for b in bl]) for k in bl[0][side][j]}
    write(tmp_path / "uomni.root", {"data": data, "mc_background": bkg, "mc_signal_reco": cat("pin", 0),
                                    "mc_truth_denom": cat("pin", 1)})
    dumps = []
    for b in bl:
        d = tmp_path / f"pat_{b['pl']}.root"
        write(d, {"data": data, "mc_background": bkg, "mc_signal_reco": b["pat"][0], "mc_truth_denom": b["pat"][1]})
        dumps.append(d)
    tp = {("uomni.root", "nTruthOnlyMisses"): sum(b["m"] for b in bl)}
    for b in bl:
        tp[(f"pat_{b['pl']}.root", "nTruthOnlyMisses")] = b["m"]
    monkeypatch.setattr(PS, "NOATIME_OPTIONAL", True)
    monkeypatch.setattr(PS, "tparam", lambda f, name: tp[(_fname(f), name)])
    monkeypatch.setattr(PS, "TOP_KEYS", set(PS.TREES))   # the fixtures carry no TParameters
    return {"tmp": tmp_path, "bl": bl, "dumps": [str(d) for d in dumps], "u": str(tmp_path / "uomni.root")}


def _fname(f):
    """The fixture file's name. UOMNI is opened through a file object, whose path is not a string."""
    return os.path.basename(f.file_path) if isinstance(f.file_path, str) else "uomni.root"


def main(*argv):
    return PS.main([str(a) for a in argv])


def arr(path, t, b):
    return uproot.open(path)[t][b].array(library="np")


# ── C1-a
def test_select_passes_with_the_real_driver(ws, capsys):
    assert main("select", "--driver", DRIVER, "--uomni", ws["u"]) == 0
    assert "C1-a PASS: the driver's selection is the pinned 37 branches" in capsys.readouterr().out


def test_select_fails_if_a_key_read_branch_is_absent(ws, tmp_path):
    f = uproot.open(ws["u"])
    trees = {t: {b: f[t][b].array(library="np") for b in f[t].keys() if not (t == "mc_truth_denom" and b == "w_truth")}
             for t in PS.TREES}
    write(tmp_path / "u2.root", trees)
    assert main("select", "--driver", DRIVER, "--uomni", tmp_path / "u2.root") == 1


def test_select_fails_if_the_driver_selects_otherwise(ws, tmp_path):
    fake = tmp_path / "drv.py"
    fake.write_text("import ROOT\ndef expected_loader_branches(loader, settings, present):\n"
                    "    return ['measured'] if loader == 'fill_data_reco_2d' else []\n")
    assert main("select", "--driver", fake, "--uomni", ws["u"]) == 1


# ── the pinned slim and C-SLIM
def test_pinned_slim_passes_c_slim(ws, capsys):
    out = ws["tmp"] / "slim-pinned.root"
    assert main("build", "--uomni", ws["u"], "--out", out) == 0
    assert main("check", "--uomni", ws["u"], "--slim", out) == 0
    assert "C-SLIM PASS" in capsys.readouterr().out
    assert set(uproot.open(out)["mc_signal_reco"].keys()) == set(PS.SLIM["mc_signal_reco"])   # no w_truth, no extra


@pytest.mark.parametrize("tamper", ["value", "extra_branch", "short"])
def test_c_slim_fails_on_a_tampered_slim(ws, tamper, capsys):
    out = ws["tmp"] / "slim-pinned.root"
    main("build", "--uomni", ws["u"], "--out", out)
    f = uproot.open(out)
    trees = {t: {b: f[t][b].array(library="np") for b in f[t].keys()} for t in PS.TREES}
    if tamper == "value":
        trees["mc_truth_denom"]["MC_pz"][2] += 1e-9
    elif tamper == "extra_branch":
        trees["data"]["leak"] = np.zeros(len(trees["data"]["measured"]))
    else:
        trees["mc_background"] = {b: v[:-1] for b, v in trees["mc_background"].items()}
    with uproot.recreate(out) as g:
        for t, c in trees.items():
            g[t] = c
    assert main("check", "--uomni", ws["u"], "--slim", out) == 1
    assert "C-SLIM FAIL" in capsys.readouterr().out


# ── the patched slims and C-PATCH
@pytest.mark.parametrize("override", [False, True])
def test_patched_slim_passes_c_patch(ws, override, capsys):
    pin, pat = ws["tmp"] / "pin.root", ws["tmp"] / "pat.root"
    main("build", "--uomni", ws["u"], "--out", pin)
    flags = ["--override"] if override else []
    assert main("build", "--uomni", ws["u"], "--out", pat, "--dumps", *ws["dumps"], *flags) == 0
    assert main("patchcheck", "--pinned", pin, "--patched", pat, "--dumps", *ws["dumps"], *flags) == 0
    assert "C-PATCH PASS" in capsys.readouterr().out
    # the misses: the CV proxy without the override; the patched truth weights with it
    lo, sig = 0, arr(pat, "mc_signal_reco", "w_truth_GEANT_Pion_0")
    for b in ws["bl"]:
        got = sig[lo + b["n"] - b["m"]: lo + b["n"]]
        want = b["pat"][1]["w_truth_GEANT_Pion_0"][b["miss"]] if override else b["den"]["w_truth"][b["miss"]]
        assert np.array_equal(got, want)
        lo += b["n"]


def test_c_patch_fails_on_a_changed_non_target(ws, capsys):
    pin, pat = ws["tmp"] / "pin.root", ws["tmp"] / "pat.root"
    main("build", "--uomni", ws["u"], "--out", pin)
    main("build", "--uomni", ws["u"], "--out", pat, "--dumps", *ws["dumps"])
    f = uproot.open(pat)
    trees = {t: {b: f[t][b].array(library="np") for b in f[t].keys()} for t in PS.TREES}
    trees["mc_signal_reco"]["w_reco_GEANT_Pion_0"][0] *= 2
    with uproot.recreate(pat) as g:
        for t, c in trees.items():
            g[t] = c
    assert main("patchcheck", "--pinned", pin, "--patched", pat, "--dumps", *ws["dumps"]) == 1
    assert "w_reco_GEANT_Pion_0 differs from pinned" in capsys.readouterr().out


def test_pinned_override_puts_uomnis_denominator_on_the_misses(ws):
    out = ws["tmp"] / "pin-ov.root"
    assert main("build", "--uomni", ws["u"], "--out", out, "--dumps", *ws["dumps"], "--pinned-override") == 0
    lo, sig = 0, arr(out, "mc_signal_reco", "w_truth_GEANT_Proton_1")
    for b in ws["bl"]:
        assert np.array_equal(sig[lo + b["n"] - b["m"]: lo + b["n"]], b["pin"][1]["w_truth_GEANT_Proton_1"][b["miss"]])
        lo += b["n"]
    assert np.array_equal(arr(out, "mc_truth_denom", "w_truth_GEANT_Proton_1"),
                          np.concatenate([b["pin"][1]["w_truth_GEANT_Proton_1"] for b in ws["bl"]]))


def test_pinned_override_refuses_if_the_miss_counts_do_not_sum(ws, monkeypatch, capsys):
    real = PS.tparam
    monkeypatch.setattr(PS, "tparam", lambda f, n: real(f, n) + (1 if _fname(f) == "uomni.root" else 0))
    assert main("build", "--uomni", ws["u"], "--out", ws["tmp"] / "x.root", "--dumps", *ws["dumps"], "--pinned-override") == 2
    assert "not UOMNI's nTruthOnlyMisses" in capsys.readouterr().out


# ── the override's own refusals (C-MISS and the matching)
def test_override_block_refuses_misses_out_of_order():
    b = blocks()[3]
    sig, den = b["pat"]
    n, m = b["n"], b["m"] + 1
    s2 = {k: v.copy() for k, v in sig.items()}
    s2["MC"][n - m:], s2["MC_pz"][n - m:], s2["w_truth"][n - m:] = (s2[k][n - m:][::-1].copy() for k in ("MC", "MC_pz", "w_truth"))
    with pytest.raises(PS.Unusable):
        PS.override_block(s2, den, m)


def test_override_block_refuses_duplicate_keys():
    b = blocks()[0]
    sig, den = b["pat"]
    den = {k: v.copy() for k, v in den.items()}
    for k in ("MC", "MC_pz", "w_truth"):
        den[k][1] = den[k][0]
    with pytest.raises(PS.Unusable, match="not unique"):
        PS.override_block(sig, den, b["m"])


def test_override_block_c_miss_catches_a_wrong_denominator_value():
    b = blocks()[0]
    sig, den = b["pat"]
    den = {k: v.copy() for k, v in den.items()}
    den["w_truth_GEANT_Pion_0"][b["miss"][0]] = np.nan   # what the override copies differs from the multiset's
    with pytest.raises(PS.Unusable, match="C-MISS FAIL"):
        PS.override_block({**sig, "w_truth_GEANT_Pion_0": sig["w_truth_GEANT_Pion_0"] + 0}, den, b["m"] - 1)


# ── usage refusals
@pytest.mark.parametrize("args,msg", [
    (["--override"], "need --dumps"), (["--pinned-override"], "need --dumps"),
])
def test_override_flags_need_dumps(ws, args, msg, capsys):
    assert main("build", "--uomni", ws["u"], "--out", ws["tmp"] / "x.root", *args) == 2
    assert msg in capsys.readouterr().out


def test_override_flags_are_exclusive(ws, capsys):
    assert main("build", "--uomni", ws["u"], "--out", ws["tmp"] / "x.root", "--dumps", *ws["dumps"],
                "--override", "--pinned-override") == 2


def test_build_refuses_an_existing_output(ws, capsys):
    out = ws["tmp"] / "slim.root"
    out.write_text("x")
    assert main("build", "--uomni", ws["u"], "--out", out) == 2 and "exists" in capsys.readouterr().out


def test_patched_needs_twelve_dumps(ws, capsys):
    assert main("build", "--uomni", ws["u"], "--out", ws["tmp"] / "x.root", "--dumps", *ws["dumps"][:11]) == 2


@pytest.mark.skipif(hasattr(os, "O_NOATIME"), reason="this OS has O_NOATIME")
def test_outside_the_tests_no_noatime_is_unusable(ws, monkeypatch, capsys):
    monkeypatch.setattr(PS, "NOATIME_OPTIONAL", False)
    assert main("check", "--uomni", ws["u"], "--slim", ws["u"]) == 2
    assert "no O_NOATIME" in capsys.readouterr().out


# ── slim_tparams.py, against a fake ROOT
_CURRENT = {}


class _Obj:
    """Writes into the current directory, as ROOT's TObject::Write does after TFile::cd."""
    def __init__(self, store, name):
        self.store, self.name = store, name

    def Write(self, name):
        _CURRENT["dir"].written.append(name)
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
    return types.SimpleNamespace(TFile=types.SimpleNamespace(Open=lambda p, mode: files.get(p)))


def test_tparams_are_copied_into_each_slim():
    ST = _load("slim_tparams")
    u = _File({})
    u.objs = {n: _Obj(u, n) for n in ST.TPARAMS}
    s1, s2 = _File({}), _File({})
    assert ST.copy(fake_root({"U": u, "S1": s1, "S2": s2}), "U", ["S1", "S2"]) is None
    assert s1.written == list(ST.TPARAMS) and s2.written == list(ST.TPARAMS)


@pytest.mark.parametrize("case", ["missing", "already", "unopenable"])
def test_tparams_refusals(case):
    ST = _load("slim_tparams")
    u = _File({})
    u.objs = {n: _Obj(u, n) for n in ST.TPARAMS if not (case == "missing" and n == "nTruthOnlyMisses")}
    s = _File({"mcPOTUsed": object()} if case == "already" else {})
    files = {"U": u, "S": s} if case != "unopenable" else {"U": u}
    assert ST.copy(fake_root(files), "U", ["S"]) is not None
