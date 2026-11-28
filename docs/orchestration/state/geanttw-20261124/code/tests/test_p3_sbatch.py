"""geanttw_p3.sbatch: each mode's name, limit, fence, deploy-blob, UOMNI, slim.json and C3 gates, its stamps, and the
exact calls it makes.
The python with uproot is a stub that logs its argv (GEANTTW_TEST_PY). setup_salloc_env.sh puts a stub python3 on
PATH, so the ROOT-side calls (slim_tparams, the driver, the readout's extract) are logged too."""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

CODE = Path(__file__).resolve().parents[1]
SBATCH = CODE / "geanttw_p3.sbatch"
REL = "docs/orchestration/state/geanttw-20261124/code"
SCRIPTS = ("c2_check.py", "p3_slim.py", "slim_tparams.py", "p3_readout.py", "geanttw_sacct.py")
NAMES = {"c2pre": ("geanttw_p2_c2pre", "00:30:00"), "slim": ("geanttw_p3_slim", "02:00:00"),
         "extract": ("geanttw_p3_extract_all", "00:30:00")}
UNIS = [f"GEANT_{b}_{i}" for b in ("Neutron", "Pion", "Proton") for i in (0, 1)]
SLIMFILE = {"pin": "slim-pinned.root", "pinov": "slim-pinned-override.root", "patov": "slim-patched.root"}
MODE_ARGS = {"extract": ["all"]}


def stub(d, name, body):
    p = d / name
    p.write_text("#!/bin/bash\n" + body + "\n")
    p.chmod(0o755)
    return p


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class H:
    def __init__(self, tmp):
        self.tmp, self.B = tmp, tmp / "B"
        self.B.mkdir()
        self.deploy = tmp / "deploy"
        (self.deploy / REL).mkdir(parents=True)
        for f in SCRIPTS:
            shutil.copy(CODE / f, self.deploy / REL / f)
        self.bin, self.rootbin = tmp / "bin", tmp / "rootbin"
        self.bin.mkdir()
        self.rootbin.mkdir()
        self.log = tmp / "calls.log"
        (self.deploy / "setup_salloc_env.sh").write_text(f'export PATH="{self.rootbin}:$PATH"\n')
        drv = self.deploy / "2d-unfolding" / "unfold_2d_omnifold_unbinned.py"
        drv.parent.mkdir()
        drv.write_text("# a stand-in for the production driver\n")
        for args in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "M"]):
            subprocess.run(["git", "-C", str(self.deploy)] + args, check=True)
        self.uomni = tmp / "uomni.root"
        self.uomni.write_bytes(b"x" * 1234)
        for n in ("helper.py", "mc.root", "fluxu.root", "nue.txt"):
            (tmp / n).write_text(n)
        stub(self.bin, "stat", 'if [ "$1" = -c ]; then python3 -c "import os,sys; print(os.stat(sys.argv[1]).st_size)" "$3"; '
                               'else exec /usr/bin/stat "$@"; fi')
        stub(self.bin, "sha256sum", 'exec shasum -a 256 "$@"')
        # the uproot python: log, and fail the subcommand named in STUB_FAIL
        stub(self.bin, "upy", f'echo "UPY $*" >> "{self.log}"; [ -n "$STUB_FAIL" ] && [[ " $* " == *" $STUB_FAIL "* ]] && exit 1; exit 0')
        # the ROOT-side python3: log; as the driver, write --out (and touch STUB_TOUCH's file, with STUB_TOUCH_FLAG)
        stub(self.rootbin, "python3", f'''echo "PY3 $*" >> "{self.log}"; echo "TMPDIR=$TMPDIR" >> "{self.tmp}/tmpdir.log"
[ -n "$STUB_FAIL" ] && [[ " $* " == *"$STUB_FAIL"* ]] && exit 1
[ -n "$STUB_TOUCH" ] && touch "$STUB_TOUCH_FLAG" -t 202001010000 "$STUB_TOUCH"
out=""; while [ $# -gt 0 ]; do [ "$1" = --out ] && out="$2"; shift; done
[ -n "$out" ] && echo xsec > "$out"; exit 0''')
        self.fence(("",))

    def fence(self, lines, timelimit="00:30:00"):
        f = self.tmp / "fence.json"
        f.write_text(json.dumps(list(lines)))
        cnt = self.tmp / "fence.n"
        cnt.write_text("0")
        stub(self.bin, "sacct", f'''case " $* " in *" -j "*) echo "{timelimit}"; exit 0 ;; esac
python3 - "{f}" "{cnt}" <<'PY'
import json, sys
lines = json.load(open(sys.argv[1])); c = int(open(sys.argv[2]).read()); open(sys.argv[2], "w").write(str(c + 1))
print(lines[min(c, len(lines) - 1)])
PY''')

    def env(self, **kw):
        e = {k: v for k, v in os.environ.items() if not k.startswith(("GEANTTW_", "SLURM_", "STUB_"))}
        e.update(PATH=f"{self.bin}:{e['PATH']}", GEANTTW_TEST_UOMNI=str(self.uomni), GEANTTW_TEST_UOMNI_SIZE="1234",
                 GEANTTW_TEST_PY=str(self.bin / "upy"), GEANTTW_TEST_SETUP=str(self.deploy / "setup_salloc_env.sh"),
                 GEANTTW_TEST_PROD_SHA=sha(self.deploy / "2d-unfolding" / "unfold_2d_omnifold_unbinned.py"),
                 GEANTTW_TEST_HELPER=str(self.tmp / "helper.py"), GEANTTW_TEST_HELPER_SHA=sha(self.tmp / "helper.py"),
                 GEANTTW_TEST_MCFILE=str(self.tmp / "mc.root"), GEANTTW_TEST_MCFILE_SHA=sha(self.tmp / "mc.root"),
                 GEANTTW_TEST_FLUXU=str(self.tmp / "fluxu.root"), GEANTTW_TEST_NUE=str(self.tmp / "nue.txt"))
        e.update(kw)
        return e

    def smoke(self, mode, *args, name=None, limit=None, **kw):
        n, lim = NAMES.get(mode, (None, "00:30:00"))
        return self.run(mode, *args, env=self.env(GEANTTW_SMOKE="1", GEANTTW_NAME=name or n,
                                                   GEANTTW_TIMELIMIT=limit or lim, **kw))

    def real(self, mode, *args, name=None, limit=None, **kw):
        n, lim = NAMES.get(mode, (None, "00:30:00"))
        self.fence(("",), timelimit=limit or lim)
        return self.run(mode, *args, env=self.env(SLURM_JOB_ID="77", SLURM_JOB_NAME=name or n, **kw))

    def run(self, mode, *args, env):
        return subprocess.run(["bash", str(SBATCH), mode, str(self.B), str(self.deploy), *args],
                              capture_output=True, text=True, env=env)

    def ready(self, c3="PASS", slim="PASS"):
        """The slim job's and C3's records, as a PASSing P3 leaves them, for the unfolds and the readout."""
        out, p3 = self.B / "run" / "p3", self.B / "p3"
        out.mkdir(parents=True, exist_ok=True)
        p3.mkdir(parents=True, exist_ok=True)
        for f in SLIMFILE.values():
            (p3 / f).write_text(f)
        st = (self.tmp / "mc.root").stat()
        (out / "slim.json").write_text(json.dumps({"verdict": slim, "slims": {k: {"sha256": sha(p3 / f)} for k, f in
                                                   SLIMFILE.items()}, "mcfile": {"size": st.st_size, "mtime_ns": st.st_mtime_ns}}))
        shas = {}
        for u in UNIS:
            x = p3 / "out" / "pin" / u / "xsec.root"
            x.parent.mkdir(parents=True, exist_ok=True)
            x.write_text(u)
            shas[f"pin:{u[len('GEANT_'):]}"] = sha(x)
        (out / "c3.json").write_text(json.dumps({"verdict": c3, "pin_xsec_sha256": shas}))

    def unf(self, slim, uni, real=True, **kw):
        name = f"geanttw_p3_unf_{slim}_{uni.replace(':', '_')}"
        if slim == "pin":   # ready() leaves every pinned output, as C3 needs; this unfold makes its own
            (self.B / "p3" / "out" / "pin" / uni.replace(":", "_") / "xsec.root").unlink(missing_ok=True)
        return (self.real if real else self.smoke)("unf", slim, uni, name=name, **kw)

    def calls(self):
        return self.log.read_text().splitlines() if self.log.exists() else []


@pytest.fixture
def h(tmp_path):
    return H(tmp_path)


@pytest.mark.parametrize("mode", sorted(NAMES))
def test_each_mode_smoke_passes(h, mode):
    h.ready()
    r = h.smoke(mode, *MODE_ARGS.get(mode, []))
    assert r.returncode == 0, r.stderr
    assert f"smoke: checks passed for {mode}" in r.stdout and not h.calls()


@pytest.mark.parametrize("slim", ["pin", "pinov", "patov"])
def test_unf_smoke_passes(h, slim):
    h.ready()
    r = h.unf(slim, "GEANT_Pion:0", real=False)
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("mode,args,name,limit,msg", [
    ("slim", [], "geanttw_p3_slimx", None, "job name 'geanttw_p3_slimx' is not 'geanttw_p3_slim'"),
    ("slim", [], None, "01:00:00", "Slurm TimeLimit '01:00:00' is not 02:00:00"),
    ("c2", [], "geanttw_p3_c2", "01:00:00", "mode 'c2' is not c2pre, slim, unf or extract"),
    ("unf", ["pat", "GEANT_Pion:0"], "x", None, "slim 'pat' is not pin, pinov or patov"),
    ("unf", ["pin", "GEANT_Pion:2"], "x", None, "universe 'GEANT_Pion:2' is not GEANT_<b>:<i>"),
    ("unf", ["pin", "GEANT_Pion:0"], "geanttw_p3_unf_pin_GEANT_Pion_1", None, "is not 'geanttw_p3_unf_pin_GEANT_Pion_0'"),
])
def test_name_limit_and_argument_refusals(h, mode, args, name, limit, msg):
    r = h.smoke(mode, *args, name=name, limit=limit)
    assert r.returncode == 2 and msg in r.stderr


def test_outside_slurm_without_smoke_refuses(h):
    r = h.run("slim", env=h.env())
    assert r.returncode == 2 and "not inside a Slurm job" in r.stderr


@pytest.mark.parametrize("row", ["5|cov2d_x|RUNNING|0|1|60", "6|t2a_y|PENDING|0|1|60", "7|covfix_pv_writer|RUNNING|0|1|60"])
def test_the_fence_refuses_at_start(h, row):
    h.fence((row,))
    r = h.smoke("slim")
    assert r.returncode == 2 and "fenced jobs are live" in r.stderr and "(at start" in r.stderr


def test_the_fence_refuses_before_the_work(h):
    h.fence(("", "8|cov2d_late|PENDING|0|1|60"), timelimit="02:00:00")
    r = h.run("slim", env=h.env(SLURM_JOB_ID="77", SLURM_JOB_NAME="geanttw_p3_slim"))
    assert r.returncode == 2 and "(immediately before the work" in r.stderr and not h.calls()
    assert "STAMP before" not in r.stderr


def test_the_fences_file_stays_under_b(h):
    stub(h.bin, "mktemp", f'echo "MKTEMP $*" >> "{h.tmp}/mktemp.log"; exec /usr/bin/mktemp "$@"')
    assert h.smoke("c2pre").returncode == 0
    assert (h.tmp / "mktemp.log").read_text().splitlines() == [f"MKTEMP -p {h.B}/run"]


def test_a_script_that_is_not_its_committed_blob_refuses(h):
    (h.deploy / REL / "p3_slim.py").write_text("# changed\n")
    r = h.smoke("slim")
    assert r.returncode == 2 and "p3_slim.py is not the deploy's committed blob" in r.stderr


@pytest.mark.parametrize("mode", ["c2pre", "slim"])
def test_uomnis_size_is_checked_where_it_is_read(h, mode):
    r = h.smoke(mode, GEANTTW_TEST_UOMNI_SIZE="1235")
    assert r.returncode == 2 and "UOMNI's size is not 1235" in r.stderr


def test_extract_and_unf_do_not_check_uomnis_size(h):
    h.ready()
    assert h.smoke("extract", "all", GEANTTW_TEST_UOMNI_SIZE="1235").returncode == 0
    assert h.unf("pin", "GEANT_Pion:0", real=False, GEANTTW_TEST_UOMNI_SIZE="1235").returncode == 0


def test_extract_takes_pin_or_all(h):
    r = h.smoke("extract", "some", name="geanttw_p3_extract_some")
    assert r.returncode == 2 and "extract takes pin or all, got 'some'" in r.stderr


def stamped(r, when, *paths):
    lines = [ln for ln in r.stderr.splitlines() if f"STAMP {when} " in ln]
    return [ln.split()[3] for ln in lines] == [str(p) for p in paths] and all("atime_ns=" in ln and "utc=" in ln
                                                                               for ln in lines)


def test_c2pre_runs_the_pre_check_and_stamps_uomni_and_nue(h):
    r = h.real("c2pre")
    assert r.returncode == 0, r.stderr
    assert h.calls() == [f"UPY -I {h.deploy / REL}/c2_check.py pre --uomni {h.uomni} --dump "
                         f"{h.B}/run/p0/pin/runEventLoopOmniFold_GEANTTW_pin_1L.root --json {h.B}/run/p3/c2pre.json"]
    for w in ("before", "after"):
        assert stamped(r, w, h.uomni, h.tmp / "nue.txt")


def test_a_failing_check_is_the_jobs_rc(h):
    r = h.real("c2pre", STUB_FAIL="pre")
    assert r.returncode == 1 and stamped(r, "after", h.uomni, h.tmp / "nue.txt")


def test_slim_runs_one_pass_then_tparams_then_verify(h):
    r = h.real("slim")
    assert r.returncode == 0, r.stderr
    c = [""] + h.calls()   # c[1] build, c[2] tparams, c[3] verify
    steps = [x.split()[3] if x.startswith("UPY") else "tparams" for x in c[1:]]
    assert steps == ["build", "tparams", "verify"]
    assert c[1].startswith(f"UPY -I {h.deploy / REL}/p3_slim.py build --uomni {h.uomni} --driver ")
    assert all(str(h.uomni) not in x for x in c[2:])   # UOMNI's one open is build's
    d = c[1].split(" --dumps ")[1].split(" --outdir ")[0].split()
    assert [Path(x).name for x in d] == (
        ["runEventLoopOmniFold_GEANTTW_pat_1A.root", "runEventLoopOmniFold_GEANTTW_pat_pilotref_1B.root"]
        + [f"runEventLoopOmniFold_GEANTTW_pat_{p}.root" for p in ("1C", "1D", "1E", "1F", "1G")]
        + ["runEventLoopOmniFold_GEANTTW_pat_1L.root"]
        + [f"runEventLoopOmniFold_GEANTTW_pat_{p}.root" for p in ("1M", "1N", "1O", "1P")])
    assert "/run/p0/pat/" in d[7]
    assert c[1].endswith(f"--outdir {h.B}/p3 --record {h.B}/run/p3/slim_build.json --c2 {h.B}/run/p3/c2.json")
    assert c[2] == (f"PY3 {h.deploy / REL}/slim_tparams.py {h.B}/run/p3/slim_build.json {h.B}/p3/slim-pinned.root "
                    f"{h.B}/p3/slim-pinned-override.root {h.B}/p3/slim-patched.root")
    assert c[3].endswith(f"--mcfile {h.tmp}/mc.root --mcfile-sha {sha(h.tmp / 'mc.root')} --out {h.B}/run/p3/slim.json")
    assert stamped(r, "before", h.uomni, h.tmp / "nue.txt", h.tmp / "mc.root")


@pytest.mark.parametrize("fail,rc,last", [("build", 11, "build"),
                                          ("slim_tparams.py", 14, "tparams"), ("verify", 15, "verify")])
def test_slim_stops_at_the_first_failing_step(h, fail, rc, last):
    r = h.real("slim", STUB_FAIL=fail)
    assert r.returncode == rc
    c = h.calls()[-1]
    assert (c.split()[3] if c.startswith("UPY") else "tparams") == last


def test_unf_runs_stage_cs_argv_on_the_named_slim(h):
    h.ready()
    r = h.unf("patov", "GEANT_Pion:0")
    assert r.returncode == 0, r.stderr
    (c,) = h.calls()
    out = h.B / "p3" / "out" / "patov" / "GEANT_Pion_0" / "xsec.root"
    assert c == (f"PY3 unfold_2d_omnifold_unbinned.py --omnifile {h.B}/p3/slim-patched.root "
                 f"--flux-universe-file {h.tmp}/fluxu.root --verbose --mcfile {h.tmp}/mc.root --iters 5 --use-weights "
                 f"--estimator lgbm --bkg-mode purity --out {out} --universe GEANT_Pion:0 --seed 42 --branch-select derived")
    assert out.exists()
    for w in ("before", "after"):
        assert stamped(r, w, h.uomni, h.tmp / "nue.txt", h.tmp / "mc.root", h.tmp / "fluxu.root")
    r2 = h.unf("patov", "GEANT_Pion:0")
    assert r2.returncode == 2 and "xsec.root exists" in r2.stderr


@pytest.mark.parametrize("case,msg", [
    ("no_slim_json", "slim.json is not PASS"), ("slim_fail", "slim.json is not PASS"),
    ("slim_changed", "is not the slim slim.json recorded"), ("mc_touched", "MCFILE's size or mtime is not slim.json's"),
])
def test_unf_needs_the_slim_jobs_pass(h, case, msg):
    h.ready(slim="FAIL" if case == "slim_fail" else "PASS")
    if case == "no_slim_json":
        (h.B / "run" / "p3" / "slim.json").unlink()
    elif case == "slim_changed":
        (h.B / "p3" / "slim-pinned.root").write_text("other")
    elif case == "mc_touched":
        os.utime(h.tmp / "mc.root", ns=(1, 2))
    r = h.unf("pin", "GEANT_Proton:1")
    assert r.returncode == 2 and msg in r.stderr and not h.calls()


C3_CASES = [("NOT REPRODUCED", "C3 is not PASS"), ("FAIL", "C3 is not PASS"), ("none", "C3 is not PASS"),
            ("swapped", "is not the one C3 passed"), ("missing_output", "is not the one C3 passed"),
            ("missing_output_and_key", "is not the one C3 passed")]


def c3_case(h, case):
    h.ready(c3=case if case in ("NOT REPRODUCED", "FAIL") else "PASS")
    c3p, x = h.B / "run" / "p3" / "c3.json", h.B / "p3" / "out" / "pin" / "GEANT_Pion_1" / "xsec.root"
    if case == "none":
        c3p.unlink()
    elif case == "swapped":
        x.write_text("rerun")
    elif case.startswith("missing_output"):
        x.unlink()
        if case.endswith("_and_key"):   # an empty hash must never equal an absent key
            rec = json.loads(c3p.read_text())
            del rec["pin_xsec_sha256"]["pin:Pion_1"]
            c3p.write_text(json.dumps(rec))


@pytest.mark.parametrize("slim", ["pinov", "patov"])
@pytest.mark.parametrize("case,msg", C3_CASES)
def test_override_unfolds_need_c3_pass_and_its_pinned_outputs(h, slim, case, msg):
    c3_case(h, case)
    r = h.unf(slim, "GEANT_Neutron:0")
    assert r.returncode == 2 and msg in r.stderr and not h.calls()


@pytest.mark.parametrize("case,msg", C3_CASES)
def test_extract_all_needs_c3_bound_to_the_pinned_outputs(h, case, msg):
    c3_case(h, case)
    r = h.real("extract", "all")
    assert r.returncode == 2 and msg in r.stderr and not h.calls()


def test_a_missing_slim_and_record_key_never_match(h):
    h.ready()
    (h.B / "p3" / "slim-pinned.root").unlink()
    rec = json.loads((h.B / "run" / "p3" / "slim.json").read_text())
    del rec["slims"]["pin"]
    (h.B / "run" / "p3" / "slim.json").write_text(json.dumps(rec))
    r = h.unf("pin", "GEANT_Proton:1")
    assert r.returncode == 2 and "is not the slim slim.json recorded" in r.stderr and not h.calls()


@pytest.mark.parametrize("mode,args,name", [("unf", ["pin", "GEANT_Proton:1"], "geanttw_p3_unf_pin_GEANT_Proton_1"),
                                            ("extract", ["all"], None), ("slim", [], None)])
def test_the_root_setup_keeps_tmpdir_under_b(h, mode, args, name):
    h.ready()
    (h.deploy / "setup_salloc_env.sh").write_text(f'export PATH="{h.rootbin}:$PATH"; export TMPDIR=/elsewhere/tmp\n')
    subprocess.run(["git", "-C", str(h.deploy), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "tmp"],
                   check=True)
    if mode == "unf":
        (h.B / "p3" / "out" / "pin" / "GEANT_Proton_1" / "xsec.root").unlink()
    assert h.real(mode, *args, name=name).returncode == 0
    assert set((h.tmp / "tmpdir.log").read_text().split()) == {f"TMPDIR={h.B}/run/tmp"}


def test_the_pinned_unfold_does_not_need_c3(h):
    h.ready(c3="FAIL")
    assert h.unf("pin", "GEANT_Neutron:0").returncode == 0


@pytest.mark.parametrize("pin", ["GEANTTW_TEST_PROD_SHA", "GEANTTW_TEST_HELPER_SHA"])
def test_unf_refuses_an_input_that_is_not_its_pin(h, pin):
    h.ready()
    r = h.unf("pin", "GEANT_Proton:1", **{pin: "0" * 64})
    assert r.returncode == 2 and "is not its pinned sha256" in r.stderr and not h.calls()


def test_unf_never_hashes_mcfile_or_the_flux_universe_file(h):
    stub(h.bin, "sha256sum", f'echo "SHA $*" >> "{h.tmp}/sha.log"; exec shasum -a 256 "$@"')
    h.ready()
    assert h.unf("pin", "GEANT_Proton:1").returncode == 0
    log = (h.tmp / "sha.log").read_text()
    assert "mc.root" not in log and "fluxu.root" not in log


@pytest.mark.parametrize("target,flag,what", [("fluxu.root", "-a", "fluxu.root's atime or mtime moved"),
                                              ("fluxu.root", "-m", "fluxu.root's atime or mtime moved"),
                                              ("mc.root", "-m", "mc.root's mtime moved")])
def test_unf_exits_21_if_a_stamp_moves(h, target, flag, what):
    h.ready()
    r = h.unf("pin", "GEANT_Proton:1", STUB_TOUCH=str(h.tmp / target), STUB_TOUCH_FLAG=flag)
    assert r.returncode == 21 and f"DEVIATION: {h.tmp}/{what}" in r.stderr


def test_mcfiles_atime_may_move(h):
    h.ready()
    r = h.unf("pin", "GEANT_Proton:1", STUB_TOUCH=str(h.tmp / "mc.root"), STUB_TOUCH_FLAG="-a")
    assert r.returncode == 0, r.stderr


def test_a_missing_stamp_file_stops_before_the_work(h):
    r = h.real("c2pre", GEANTTW_TEST_NUE=str(h.tmp / "absent.txt"))
    assert r.returncode == 2 and "cannot log the stamps before the read" in r.stderr and not h.calls()


def test_unf_refuses_a_setup_that_is_not_the_committed_one(h):
    h.ready()
    other = h.tmp / "other_setup.sh"
    other.write_text("export X=1\n")
    r = h.unf("pin", "GEANT_Proton:1", GEANTTW_TEST_SETUP=str(other))
    assert r.returncode == 2 and "is not the deploy's committed setup_salloc_env.sh" in r.stderr


def test_extract_all_runs_the_readout(h):
    h.ready()
    r = h.real("extract", "all")
    assert r.returncode == 0, r.stderr
    (c,) = h.calls()
    assert c == (f"PY3 {h.deploy / REL}/p3_readout.py extract --repo {h.deploy} --outs {h.B}/p3/out "
                 f"--out {h.B}/run/p3/p3_vectors_all.npz --slims pin pinov patov --c3 {h.B}/run/p3/c3.json")
    assert stamped(r, "after", h.uomni, h.tmp / "nue.txt")


def test_extract_all_says_why_it_refuses(h):
    h.ready(c3="FAIL")
    r = h.real("extract", "all")
    assert r.returncode == 2 and "C3 is not PASS: no patched number is read" in r.stderr


def test_extract_pin_then_runs_c3(h):
    r = h.real("extract", "pin", name="geanttw_p3_extract_pin")
    assert r.returncode == 0, r.stderr
    assert h.calls() == [
        f"PY3 {h.deploy / REL}/p3_readout.py extract --repo {h.deploy} --outs {h.B}/p3/out "
        f"--out {h.B}/run/p3/p3_vectors_pin.npz --slims pin",
        f"UPY -I {h.deploy / REL}/p3_readout.py c3 --repo {h.deploy} --vectors {h.B}/run/p3/p3_vectors_pin.npz "
        f"--json {h.B}/run/p3/c3.json"]


def test_extract_pin_returns_c3s_failure(h):
    r = h.real("extract", "pin", name="geanttw_p3_extract_pin", STUB_FAIL="c3")
    assert r.returncode == 1


def test_a_failing_sacct_refuses(h):
    stub(h.bin, "sacct", 'case " $* " in *" -j "*) echo 00:30:00; exit 0 ;; esac; exit 1')
    r = h.smoke("c2pre")
    assert r.returncode == 2 and "sacct failed (at start)" in r.stderr


def test_a_failing_mktemp_refuses(h):
    stub(h.bin, "mktemp", "exit 1")
    r = h.smoke("c2pre")
    assert r.returncode == 2 and "mktemp failed (at start)" in r.stderr


def test_unmakeable_output_dirs_stop(h):
    (h.B / "run").mkdir()
    (h.B / "run" / "p3").write_text("a file in the way\n")
    r = h.real("c2pre")
    assert r.returncode == 2 and "cannot make" in r.stderr and not h.calls()


def test_an_unmakeable_unfold_dir_stops(h):
    h.ready()
    (h.B / "p3" / "out" / "pinov").write_text("a file in the way\n")
    r = h.unf("pinov", "GEANT_Pion:1")
    assert r.returncode == 2 and "cannot make" in r.stderr and not h.calls()


def test_unf_stops_without_the_drivers_directory(h):
    h.ready()
    h.fence(("",), timelimit="00:30:00")
    (h.B / "p3" / "out" / "pin" / "GEANT_Pion_1" / "xsec.root").unlink()
    env = h.env(SLURM_JOB_ID="77", SLURM_JOB_NAME="geanttw_p3_unf_pin_GEANT_Pion_1")   # pins taken first
    shutil.rmtree(h.deploy / "2d-unfolding")
    r = h.run("unf", "pin", "GEANT_Pion:1", env=env)
    assert r.returncode == 2 and f"REFUSE: no {h.deploy}/2d-unfolding" in r.stderr and not h.calls()


def test_no_python3_on_path_refuses_first(h, tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    r = subprocess.run([shutil.which("bash"), str(SBATCH), "c2pre", str(h.B), str(h.deploy)], capture_output=True,
                       text=True, env={**h.env(GEANTTW_SMOKE="1"), "PATH": str(empty)})
    assert r.returncode == 2 and "REFUSE: no python3" in r.stderr


def test_the_after_stamp_failing_exits_20(h):
    h.ready()
    stub(h.rootbin, "python3", f'''echo "PY3 $*" >> "{h.log}"; rm -f "{h.tmp}/nue.txt"
out=""; while [ $# -gt 0 ]; do [ "$1" = --out ] && out="$2"; shift; done
[ -n "$out" ] && echo xsec > "$out"; exit 0''')
    r = h.unf("pin", "GEANT_Proton:1")
    assert r.returncode == 20 and "the stamps after the read cannot be written" in r.stderr


def test_an_unmakeable_tmpdir_stops_the_unfold(h):
    h.ready()
    (h.B / "run" / "tmp").write_text("a file in the way\n")
    r = h.unf("pin", "GEANT_Proton:1")
    assert r.returncode == 2 and f"cannot make {h.B}/run/tmp" in r.stderr and not h.calls()
