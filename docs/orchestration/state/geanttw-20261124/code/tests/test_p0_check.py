"""p0_check.py: a passing P0 workspace, then one planted failure per control."""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import uproot

CODE = Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("p0_check", CODE / "p0_check.py")
pc = importlib.util.module_from_spec(_s)
_s.loader.exec_module(pc)

N = 8
TARGETS = pc.TARGETS


def write(path, trees):
    path.parent.mkdir(parents=True, exist_ok=True)
    with uproot.recreate(path) as f:
        for t, cols in trees.items():
            f[t] = cols


def trees(patched):
    rng = np.random.default_rng(7)
    ws, wd = rng.uniform(0.5, 2, N), rng.uniform(0.5, 2, N)
    sig = {"w_truth": ws, "w_reco": ws * 1.3, "pt": rng.uniform(0, 2, N)}
    den = {"w_truth": wd, "pt_true": rng.uniform(0, 2, N)}
    for i, t in enumerate(TARGETS):
        f = 1.0 + 0.01 * (i + 1) * patched
        sig[t] = ws * f if patched else ws.copy()
        den[t] = wd * f if patched else wd.copy()
        sig[t.replace("truth", "reco")] = ws * 1.3 * (1 + 0.02 * i)
    bkg = {"w_reco": rng.uniform(0.5, 2, N)}
    for t in TARGETS:
        bkg[t.replace("truth", "bkg")] = bkg["w_reco"] * 1.01
    return {"mc_signal_reco": sig, "mc_truth_denom": den, "mc_background": bkg, "data": {"pt": rng.uniform(0, 2, N)}}


def ref_trees():
    t = trees(False)
    for tree in t.values():
        for k in [k for k in tree if "GEANT" in k]:
            del tree[k]
    return t


def strace_lines(lines):
    return "\n".join(lines) + "\n"


class WS:
    def __init__(self, tmp):
        self.tmp = tmp
        self.B = tmp / "B"
        self.deploy = self.B / "deploy"
        self.prod = tmp / "prod-opt"
        self.conda = tmp / "conda-root"
        self.anat = tmp / "anat"
        for d in (self.prod / "lib" / "data" / "flux", self.prod / "etc" / "MParamFiles" / "data", self.conda / "lib",
                  self.anat, self.deploy / "2d-unfolding" / "playlist_manifests"):
            d.mkdir(parents=True, exist_ok=True)
        (self.prod / "lib" / "libMAT.so").write_text("prod")
        (self.prod / "lib" / "libUnfoldUtils.so").write_text("prod")
        (self.prod / "lib" / "data" / "flux" / "f.root").write_text("flux")
        (self.prod / "etc" / "MParamFiles" / "data" / "nue.txt").write_text("nue")
        (self.prod / "etc" / "MParamFiles" / "README").write_text("not data")
        (self.conda / "lib" / "libCore.so").write_text("root")
        self.mc, self.data = self.anat / "mc1.root", self.anat / "data1.root"
        for p in (self.mc, self.data, self.anat / "stray.root"):
            p.write_text("anatuple")
        mf = self.deploy / "2d-unfolding" / "playlist_manifests"
        (mf / "1L_MC.txt").write_text(f"{self.mc}\n")
        (mf / "1L_Data.txt").write_text(f"{self.data}\n")
        for b in ("pin", "pat"):
            lib = self.B / f"prefix-{b}" / "lib"
            lib.mkdir(parents=True)
            (lib / "libMAT.so").write_text("mat")
            (lib / "libMAT-MINERvA.so").write_text(b)
            os.symlink(self.prod / "lib" / "data", lib / "data")
            write(self.dump(b), trees(b == "pat"))
            self.set_strace(b, self.good_strace(b))
        self.ref = self.tmp / "ref.root"
        write(self.ref, ref_trees())
        self.ref_sha = hashlib.sha256(self.ref.read_bytes()).hexdigest()
        self.set_log(dict.fromkeys(pc.CHECKS, "PASS"))

    def dump(self, b):
        return self.B / "run" / "p0" / b / f"runEventLoopOmniFold_GEANTTW_{b}_1L.root"

    def good_strace(self, b):
        lib = self.B / f"prefix-{b}" / "lib"
        return [
            f'101 openat(AT_FDCWD, "{self.conda}/lib/libCore.so", O_RDONLY|O_CLOEXEC) = 3',
            f'101 openat(AT_FDCWD, "{lib}/libMAT.so", O_RDONLY|O_CLOEXEC) = 3',
            f'101 openat(AT_FDCWD, "{lib}/libMAT-MINERvA.so", O_RDONLY|O_CLOEXEC <unfinished ...>',
            f'102 openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY) = 4',
            f'101 <... openat resumed>) = 5',
            f'101 openat(AT_FDCWD, "{self.prod}/lib/libMAT.so", O_RDONLY) = -1 ENOENT (No such file or directory)',
            f'101 openat(AT_FDCWD, "{lib}/data/flux/f.root", O_RDONLY) = 6',
            f'101 openat(AT_FDCWD, "{self.prod}/etc/MParamFiles/data/nue.txt", O_RDONLY) = 7',
            f'101 open("{self.mc}", O_RDONLY) = 8',
            f'101 openat(AT_FDCWD, "{self.data}", O_RDONLY) = 9',
            f'101 openat(AT_FDCWD, "{self.B}/run/p0/{b}/work/out.root", O_RDWR|O_CREAT, 0644) = 10',
            # the binary's own relative opens in its work dir, placed by strace -y (both dirfd spellings)
            f'101 openat(AT_FDCWD, ".", O_RDONLY|O_DIRECTORY) = 13<{self.B}/run/p0/{b}/work_1L_1>',
            f'101 openat(AT_FDCWD</x>, "runEventLoopOmniFold.root", O_RDWR|O_CREAT|O_TRUNC, 0644) = 14'
            f'<{self.B}/run/p0/{b}/work_1L_1/runEventLoopOmniFold.root>',
            f'101 openat(13<{self.B}/run/p0/{b}/work_1L_1>, "sub.txt", O_RDONLY <unfinished ...>',
            f'101 <... openat resumed>) = 15<{self.B}/run/p0/{b}/work_1L_1/sub.txt>',
            f'101 openat(AT_FDCWD, "/global/homes/x/.rootrc", O_RDONLY) = -1 ENOENT (No such file or directory)',
        ]

    def set_strace(self, b, lines):
        p = self.B / "run" / "p0" / b / f"strace.{b}.1L"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(strace_lines(lines))

    def set_log(self, checks):
        p = self.B / "run" / "p0" / "build.log"
        p.write_text("".join(f"CHECK {k} {v}\n" for k, v in checks.items()) + "SO pin x y\n")

    def run(self, smoke=True, ref_sha=None):
        env = dict(os.environ)
        env.pop("GEANTTW_SMOKE_B", None)
        if smoke:
            env.update(GEANTTW_SMOKE_B=str(self.B), GEANTTW_TEST_PROD_OPT=str(self.prod),
                       GEANTTW_TEST_CONDA=str(self.conda))
        out = self.tmp / "p0.json"
        p = subprocess.run([sys.executable, "-I", str(CODE / "p0_check.py"), "--B", str(self.B), "--deploy",
                            str(self.deploy), "--ref", str(self.ref), "--ref-sha", ref_sha or self.ref_sha,
                            "--json", str(out)], capture_output=True, text=True, env=env)
        rep = json.loads(out.read_text()) if out.exists() else None
        return p, rep


def verdicts(rep):
    return {k: v["pass"] for k, v in rep["controls"].items()}


@pytest.fixture
def ws(tmp_path):
    return WS(tmp_path)


def test_passing_workspace(ws):
    p, rep = ws.run()
    assert p.returncode == 0, p.stdout + p.stderr
    assert rep["verdict"] == "PASS" and all(verdicts(rep).values())
    assert "P0 PASS" in p.stdout
    assert str(ws.mc) in rep["opened_outside_B"]
    ev = {k: v["evidence"] for k, v in rep["controls"].items()}
    assert ev["C0a"] == ["both builds open libMAT.so and libMAT-MINERvA.so from their own prefix only"]
    assert ev["C0d"] == []
    assert ev["C0f"] == [f"reference sha256 {ws.ref_sha} == {ws.ref_sha}"]
    assert "C0e PASS 6 distinct files opened outside B" in p.stdout


@pytest.mark.parametrize("drop", ["--B", "--deploy", "--ref", "--ref-sha"])
def test_every_argument_is_required(ws, drop):
    args = {"--B": str(ws.B), "--deploy": str(ws.deploy), "--ref": str(ws.ref), "--ref-sha": ws.ref_sha}
    del args[drop]
    cmd = [sys.executable, "-I", str(CODE / "p0_check.py")] + [x for kv in args.items() for x in kv]
    p = subprocess.run(cmd, capture_output=True, text=True)
    assert p.returncode == 2 and "required" in p.stderr


def test_malformed_check_line_is_ignored(ws):
    p = ws.B / "run" / "p0" / "build.log"
    p.write_text(p.read_text() + "CHECK BROKEN\nNOTE a b\n")
    proc, rep = ws.run()
    assert proc.returncode == 0 and rep["verdict"] == "PASS"


def only_fails(rep, *names):
    assert rep["verdict"] == "FAIL"
    v = verdicts(rep)
    assert {k for k, ok in v.items() if not ok} == set(names), v


# ── build.log ──
@pytest.mark.parametrize("check,value", [("RPATH_CLEAN", "FAIL"), ("SOURCE_PROVENANCE", None),
                                         ("DIFF_EQUALS_UPSTREAM", "FAIL")])
def test_build_log_checks(ws, check, value):
    c = dict.fromkeys(pc.CHECKS, "PASS")
    if value is None:
        del c[check]
    else:
        c[check] = value
    ws.set_log(c)
    p, rep = ws.run()
    assert p.returncode == 1
    only_fails(rep, "build.log")


# ── C0a ──
def test_c0a_production_libmat(ws):
    lines = ws.good_strace("pat")
    lines[1] = f'101 openat(AT_FDCWD, "{ws.prod}/lib/libMAT.so", O_RDONLY|O_CLOEXEC) = 3'
    ws.set_strace("pat", lines)
    p, rep = ws.run()
    only_fails(rep, "C0a", "C0e")   # production opt/lib is not an allowed family for C0e either


def test_c0a_other_production_so(ws):
    ws.set_strace("pin", ws.good_strace("pin") + [f'101 openat(AT_FDCWD, "{ws.prod}/lib/libUnfoldUtils.so", 0) = 11'])
    p, rep = ws.run()
    assert not verdicts(rep)["C0a"]


def test_c0a_library_never_opened(ws):
    ws.set_strace("pin", [ln for ln in ws.good_strace("pin") if "libMAT-MINERvA" not in ln and "resumed" not in ln])
    p, rep = ws.run()
    only_fails(rep, "C0a")


def test_c0a_unfinished_open_that_failed_is_not_an_open(ws):
    lines = ws.good_strace("pin")
    lines[4] = "101 <... openat resumed>) = -1 ENOENT (No such file or directory)"
    ws.set_strace("pin", lines)
    p, rep = ws.run()
    only_fails(rep, "C0a")


def test_c0a_other_builds_prefix(ws):
    lines = ws.good_strace("pin")
    lines[1] = lines[1].replace("prefix-pin", "prefix-pat")
    ws.set_strace("pin", lines)
    p, rep = ws.run()
    only_fails(rep, "C0a")


# ── C0b / C0c / C0d ──
def mutate(ws, b, tree, branch, fn):
    with uproot.open(ws.dump(b)) as f:
        t = {name: {k: f[name][k].array(library="np") for k in f[name].keys()} for name in
             [k.split(";")[0] for k in f.keys(filter_classname="TTree", cycle=False)]}
    fn(t[tree], branch)
    write(ws.dump(b), t)


def test_c0b_one_target_unchanged_in_truth_denom(ws):
    mutate(ws, "pat", "mc_truth_denom", "w_truth_GEANT_Proton_1", lambda t, k: t.__setitem__(k, t["w_truth"].copy()))
    p, rep = ws.run()
    only_fails(rep, "C0b")


def test_c0b_one_target_unchanged_in_signal_reco(ws):
    mutate(ws, "pat", "mc_signal_reco", "w_truth_GEANT_Neutron_0", lambda t, k: t.__setitem__(k, t["w_truth"].copy()))
    p, rep = ws.run()
    assert not verdicts(rep)["C0b"]


@pytest.mark.parametrize("bad", [0.0, -1.0, np.inf, np.nan])
def test_c0b_bad_values(ws, bad):
    def f(t, k):
        t[k] = t[k].copy()
        t[k][2] = bad
    mutate(ws, "pat", "mc_truth_denom", "w_truth_GEANT_Pion_0", f)
    p, rep = ws.run()
    assert not verdicts(rep)["C0b"]


def test_c0b_target_missing_from_a_tree(ws):
    mutate(ws, "pat", "mc_truth_denom", "w_truth_GEANT_Pion_1", lambda t, k: t.pop(k))
    p, rep = ws.run()
    assert not verdicts(rep)["C0b"] and not verdicts(rep)["C0d"]


def test_c0b_c0c_tree_missing(ws):
    for b in ("pin", "pat"):
        with uproot.open(ws.dump(b)) as f:
            t = {n: {k: f[n][k].array(library="np") for k in f[n].keys()} for n in
                 ("mc_signal_reco", "mc_background", "data")}
        write(ws.dump(b), t)
    p, rep = ws.run()
    assert not verdicts(rep)["C0b"] and not verdicts(rep)["C0c"]


def test_c0c_one_ulp(ws):
    def f(t, k):
        t[k] = t[k].copy()
        t[k][N - 1] = np.nextafter(t[k][N - 1], np.inf)
    mutate(ws, "pin", "mc_signal_reco", "w_truth_GEANT_Pion_1", f)
    p, rep = ws.run()
    assert not verdicts(rep)["C0c"]


def test_c0d_reco_geant_branch_moves(ws):
    def f(t, k):
        t[k] = t[k] * 1.0001
    mutate(ws, "pat", "mc_signal_reco", "w_reco_GEANT_Pion_0", f)
    p, rep = ws.run()
    only_fails(rep, "C0d")


def test_c0d_target_in_an_unexpected_tree(ws):
    for b in ("pin", "pat"):
        mutate(ws, b, "mc_background", "w_truth_GEANT_Pion_0",
               lambda t, k: t.__setitem__(k, t["w_reco"] * (1.1 if b == "pat" else 1.0)))
    p, rep = ws.run()
    assert not verdicts(rep)["C0d"]


# ── C0e ──
def test_c0e_disallowed_home_file(ws):
    home = ws.tmp / "home" / ".rootrc"
    home.parent.mkdir()
    home.write_text("x")
    ws.set_strace("pat", ws.good_strace("pat") + [f'101 openat(AT_FDCWD, "{home}", O_RDONLY) = 12'])
    p, rep = ws.run()
    only_fails(rep, "C0e")
    assert any(str(home) in e for e in rep["controls"]["C0e"]["evidence"])


def test_c0e_relative_open_without_a_y_path_fails(ws):
    """A relative open strace gives no path for cannot be placed: it FAILs, and is never resolved against the
    checker's own cwd (the bug the -y path closes: the binary's work dir is not the checker's)."""
    ws.set_strace("pin", ws.good_strace("pin") + ['101 openat(AT_FDCWD, "runEventLoopOmniFold.root", O_RDONLY) = 12'])
    p, rep = ws.run()
    only_fails(rep, "C0e")
    assert any("NOT ALLOWED UNRESOLVED-RELATIVE:runEventLoopOmniFold.root" == e
               for e in rep["controls"]["C0e"]["evidence"])


def test_c0e_relative_open_is_judged_by_its_y_path(ws):
    out = ws.tmp / "home" / "escaped.txt"
    out.parent.mkdir()
    out.write_text("x")
    ws.set_strace("pat", ws.good_strace("pat") + [f'101 openat(AT_FDCWD, "../../../../home/escaped.txt", O_RDONLY) = 12<{out}>'])
    p, rep = ws.run()
    only_fails(rep, "C0e")
    assert any(e == f"NOT ALLOWED {os.path.realpath(out)}" for e in rep["controls"]["C0e"]["evidence"])


def test_c0a_unresolved_library_open_fails(ws):
    lines = [ln for ln in ws.good_strace("pin") if "libMAT.so" not in ln or "ENOENT" in ln]
    ws.set_strace("pin", lines + ['101 openat(AT_FDCWD, "libMAT.so", O_RDONLY|O_CLOEXEC) = 3'])
    p, rep = ws.run()
    assert rep["controls"]["C0a"]["pass"] is False


def test_c0e_anatuple_not_in_manifest(ws):
    ws.set_strace("pin", ws.good_strace("pin") + [f'101 openat(AT_FDCWD, "{ws.anat}/stray.root", O_RDONLY) = 12'])
    p, rep = ws.run()
    only_fails(rep, "C0e")


def test_c0e_flux_and_reweight_files_allowed_through_their_symlink(ws):
    real = ws.tmp / "large_files" / "MATFluxAndReweightFiles"
    (real / "flux").mkdir(parents=True)
    (real / "flux" / "g.root").write_text("flux")
    os.symlink(real, ws.prod / "etc" / "MATFluxAndReweightFiles")
    lib = ws.B / "prefix-pin" / "etc"
    lib.mkdir()
    os.symlink(ws.prod / "etc" / "MATFluxAndReweightFiles", lib / "MATFluxAndReweightFiles")
    ws.set_strace("pin", ws.good_strace("pin") + [f'101 openat(AT_FDCWD, "{lib}/MATFluxAndReweightFiles/flux/g.root", 0) = 12'])
    p, rep = ws.run()
    assert p.returncode == 0, p.stdout
    ws.set_strace("pin", ws.good_strace("pin") + [f'101 openat(AT_FDCWD, "{ws.tmp}/large_files/other.root", 0) = 12'])
    (ws.tmp / "large_files" / "other.root").write_text("x")
    p, rep = ws.run()
    only_fails(rep, "C0e")


def test_c0e_mparamfiles_outside_data(ws):
    ws.set_strace("pin", ws.good_strace("pin") + [f'101 openat(AT_FDCWD, "{ws.prod}/etc/MParamFiles/README", 0) = 12'])
    p, rep = ws.run()
    only_fails(rep, "C0e")


def test_c0e_symlink_out_of_B_is_judged_by_its_target(ws):
    leak = ws.tmp / "elsewhere"
    leak.mkdir()
    (leak / "x.txt").write_text("x")
    os.symlink(leak, ws.B / "leak")
    ws.set_strace("pin", ws.good_strace("pin") + [f'101 openat(AT_FDCWD, "{ws.B}/leak/x.txt", O_RDONLY) = 12'])
    p, rep = ws.run()
    only_fails(rep, "C0e")


def test_test_paths_need_smoke_mode(ws):
    p, rep = ws.run(smoke=False)
    assert p.returncode == 1
    assert not verdicts(rep)["C0e"]


# ── C0f ──
def test_c0f_ref_sha_mismatch(ws):
    p, rep = ws.run(ref_sha="0" * 64)
    only_fails(rep, "C0f")
    assert rep["controls"]["C0f"]["evidence"][0] == f"reference sha256 {ws.ref_sha} != {'0' * 64}"


def test_c0f_cv_branch_differs(ws):
    def f(t, k):
        t[k] = t[k].copy()
        t[k][0] = np.nextafter(t[k][0], 0)
    mutate(ws, "pin", "mc_signal_reco", "pt", f)
    mutate(ws, "pat", "mc_signal_reco", "pt", f)
    p, rep = ws.run()
    only_fails(rep, "C0f")


def test_c0f_reference_branch_missing_from_pin(ws):
    with uproot.open(ws.ref) as f:
        t = {n: {k: f[n][k].array(library="np") for k in f[n].keys()} for n in
             [k.split(";")[0] for k in f.keys(filter_classname="TTree", cycle=False)]}
    t["data"]["only_in_ref"] = np.ones(N)
    write(ws.ref, t)
    p, rep = ws.run(ref_sha=hashlib.sha256(ws.ref.read_bytes()).hexdigest())
    only_fails(rep, "C0f")


def test_c0f_non_universe_extra_in_pin(ws):
    for b in ("pin", "pat"):
        mutate(ws, b, "data", "extra_x", lambda t, k: t.__setitem__(k, np.ones(N)))
    p, rep = ws.run()
    only_fails(rep, "C0f")


def test_successful_opens_parser(tmp_path):
    s = tmp_path / "s"
    s.write_text(strace_lines([
        '7 openat(AT_FDCWD, "/a", O_RDONLY) = 3',
        '[pid  8] open("/b", O_RDONLY) = 0',
        '9 openat(AT_FDCWD, "/c", O_RDONLY) = -1 ENOENT (x)',
        '10 openat(AT_FDCWD, "/d", O_RDONLY <unfinished ...>',
        '11 openat(AT_FDCWD, "/e", O_RDONLY <unfinished ...>',
        '11 <... openat resumed>) = -1 EACCES (x)',
        '10 <... openat resumed>) = 4',
        'openat(AT_FDCWD, "/f", O_RDONLY) = 5',
        '12 close(3) = 0',
        '12 +++ exited with 0 +++',
        '13 <... openat resumed>) = 6',
    ]))
    assert pc.successful_opens(s) == ["/a", "/b", "/d", "/f"]
