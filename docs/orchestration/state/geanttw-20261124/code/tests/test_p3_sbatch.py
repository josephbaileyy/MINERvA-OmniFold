"""geanttw_p3.sbatch: each mode's name, limit, fence, deploy-blob and UOMNI gates, and the exact calls it makes.
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
NAMES = {"c2pre": ("geanttw_p2_c2pre", "00:30:00"), "c2": ("geanttw_p3_c2", "01:00:00"),
         "slim": ("geanttw_p3_slim", "01:00:00"), "extract": ("geanttw_p3_extract_all", "00:30:00")}
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
        for n in ("helper.py", "mc.root", "fluxu.root"):
            (tmp / n).write_text(n)
        stub(self.bin, "stat", 'if [ "$1" = -c ]; then python3 -c "import os,sys; print(os.stat(sys.argv[1]).st_size)" "$3"; '
                               'else exec /usr/bin/stat "$@"; fi')
        stub(self.bin, "sha256sum", 'exec shasum -a 256 "$@"')
        # the uproot python: log, and fail the subcommand named in STUB_FAIL
        stub(self.bin, "upy", f'echo "UPY $*" >> "{self.log}"; [ -n "$STUB_FAIL" ] && [[ " $* " == *" $STUB_FAIL "* ]] && exit 1; exit 0')
        # the ROOT-side python3: log; as the driver, write --out
        stub(self.rootbin, "python3", f'''echo "PY3 $*" >> "{self.log}"
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
                 GEANTTW_TEST_FLUXU=str(self.tmp / "fluxu.root"), GEANTTW_TEST_FLUXU_SHA=sha(self.tmp / "fluxu.root"))
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

    def calls(self):
        return self.log.read_text().splitlines() if self.log.exists() else []


@pytest.fixture
def h(tmp_path):
    return H(tmp_path)


@pytest.mark.parametrize("mode", sorted(NAMES))
def test_each_mode_smoke_passes(h, mode):
    r = h.smoke(mode, *MODE_ARGS.get(mode, []))
    assert r.returncode == 0, r.stderr
    assert f"smoke: checks passed for {mode}" in r.stdout and not h.calls()


def test_unf_smoke_passes(h):
    r = h.smoke("unf", "pinov", "GEANT_Pion:0", name="geanttw_p3_unf_pinov_GEANT_Pion_0")
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("mode,args,name,limit,msg", [
    ("c2", [], "geanttw_p3_c2x", None, "job name 'geanttw_p3_c2x' is not 'geanttw_p3_c2'"),
    ("c2", [], None, "02:00:00", "Slurm TimeLimit '02:00:00' is not 01:00:00"),
    ("slim2", [], "x", None, "mode 'slim2' is not"),
    ("unf", ["pat", "GEANT_Pion:0"], "x", None, "slim 'pat' is not pin, pinov or patov"),
    ("unf", ["pin", "GEANT_Pion:2"], "x", None, "universe 'GEANT_Pion:2' is not GEANT_<b>:<i>"),
    ("unf", ["pin", "GEANT_Pion:0"], "geanttw_p3_unf_pin_GEANT_Pion_1", None, "is not 'geanttw_p3_unf_pin_GEANT_Pion_0'"),
])
def test_name_limit_and_argument_refusals(h, mode, args, name, limit, msg):
    r = h.smoke(mode, *args, name=name, limit=limit)
    assert r.returncode == 2 and msg in r.stderr


def test_outside_slurm_without_smoke_refuses(h):
    r = h.run("c2", env=h.env())
    assert r.returncode == 2 and "not inside a Slurm job" in r.stderr


@pytest.mark.parametrize("row", ["5|cov2d_x|RUNNING|0|1|60", "6|t2a_y|PENDING|0|1|60", "7|covfix_pv_writer|RUNNING|0|1|60"])
def test_the_fence_refuses_at_start(h, row):
    h.fence((row,))
    r = h.smoke("c2")
    assert r.returncode == 2 and "fenced jobs are live" in r.stderr and "(at start" in r.stderr


def test_the_fence_refuses_before_the_work(h):
    h.fence(("", "8|cov2d_late|PENDING|0|1|60"), timelimit="01:00:00")
    r = h.run("c2", env=h.env(SLURM_JOB_ID="77", SLURM_JOB_NAME="geanttw_p3_c2"))
    assert r.returncode == 2 and "(immediately before the work" in r.stderr and not h.calls()


def test_a_script_that_is_not_its_committed_blob_refuses(h):
    (h.deploy / REL / "p3_slim.py").write_text("# changed\n")
    r = h.smoke("slim")
    assert r.returncode == 2 and "p3_slim.py is not the deploy's committed blob" in r.stderr


@pytest.mark.parametrize("mode", ["c2pre", "c2", "slim"])
def test_uomnis_size_is_checked_where_it_is_read(h, mode):
    r = h.smoke(mode, GEANTTW_TEST_UOMNI_SIZE="1235")
    assert r.returncode == 2 and "UOMNI's size is not 1235" in r.stderr


def test_extract_does_not_read_uomni(h):
    assert h.smoke("extract", "all", GEANTTW_TEST_UOMNI_SIZE="1235").returncode == 0


def test_extract_takes_pin_or_all(h):
    r = h.smoke("extract", "some", name="geanttw_p3_extract_some")
    assert r.returncode == 2 and "extract takes pin or all, got 'some'" in r.stderr


def test_c2pre_runs_the_pre_check_and_logs_uomni(h):
    r = h.real("c2pre")
    assert r.returncode == 0, r.stderr
    assert h.calls() == [f"UPY -I {h.deploy / REL}/c2_check.py pre --uomni {h.uomni} --dump "
                         f"{h.B}/run/p0/pin/runEventLoopOmniFold_GEANTTW_pin_1L.root --json {h.B}/run/p3/c2pre.json"]
    assert "UOMNI before utc=" in r.stderr and "UOMNI after utc=" in r.stderr


def test_c2_passes_the_dumps_in_hadd_order(h):
    r = h.real("c2")
    assert r.returncode == 0, r.stderr
    (c,) = h.calls()
    d = c.split(" --dumps ")[1].split(" --json ")[0].split()
    assert [Path(x).name for x in d] == (
        ["runEventLoopOmniFold_GEANTTW_pat_1A.root", "runEventLoopOmniFold_GEANTTW_pat_pilotref_1B.root"]
        + [f"runEventLoopOmniFold_GEANTTW_pat_{p}.root" for p in ("1C", "1D", "1E", "1F", "1G")]
        + ["runEventLoopOmniFold_GEANTTW_pat_1L.root"]
        + [f"runEventLoopOmniFold_GEANTTW_pat_{p}.root" for p in ("1M", "1N", "1O", "1P")])
    assert "/run/p0/pat/" in d[7]


def test_a_failing_check_is_the_jobs_rc(h):
    r = h.real("c2", STUB_FAIL="full")
    assert r.returncode == 1 and "UOMNI after utc=" in r.stderr


def test_slim_runs_its_steps_in_order(h):
    r = h.real("slim")
    assert r.returncode == 0, r.stderr
    steps = [c.split()[3] if c.startswith("UPY") else "tparams" for c in h.calls()]
    assert steps == ["select", "build", "build", "build", "tparams", "check", "patchcheck"]
    calls = h.calls()
    assert "--pinned-override" in calls[2] and "slim-pinned-override.root" in calls[2]
    assert calls[3].endswith("--override") and "slim-patched-override.root" in calls[3]
    assert "slim_tparams.py" in calls[4] and calls[4].count("slim-") == 3


@pytest.mark.parametrize("fail,rc", [("select", 10), ("build", 11), ("check", 15), ("patchcheck", 16)])
def test_slim_stops_at_the_first_failing_step(h, fail, rc):
    r = h.real("slim", STUB_FAIL=fail)
    assert r.returncode == rc
    assert not any("patchcheck" in c for c in h.calls()) or fail == "patchcheck"


def test_unf_runs_stage_cs_argv_on_the_named_slim(h):
    name = "geanttw_p3_unf_pinov_GEANT_Pion_0"
    r = h.real("unf", "pinov", "GEANT_Pion:0", name=name)
    assert r.returncode == 0, r.stderr
    (c,) = h.calls()
    out = h.B / "p3" / "out" / "pinov" / "GEANT_Pion_0" / "xsec.root"
    assert c == (f"PY3 unfold_2d_omnifold_unbinned.py --omnifile {h.B}/p3/slim-pinned-override.root "
                 f"--flux-universe-file {h.tmp}/fluxu.root --verbose --mcfile {h.tmp}/mc.root --iters 5 --use-weights "
                 f"--estimator lgbm --bkg-mode purity --out {out} --universe GEANT_Pion:0 --seed 42 --branch-select derived")
    assert out.exists()
    r2 = h.real("unf", "pinov", "GEANT_Pion:0", name=name)
    assert r2.returncode == 2 and "xsec.root exists" in r2.stderr


@pytest.mark.parametrize("pin", ["GEANTTW_TEST_PROD_SHA", "GEANTTW_TEST_HELPER_SHA", "GEANTTW_TEST_MCFILE_SHA",
                                 "GEANTTW_TEST_FLUXU_SHA"])
def test_unf_refuses_an_input_that_is_not_its_pin(h, pin):
    r = h.real("unf", "pin", "GEANT_Proton:1", name="geanttw_p3_unf_pin_GEANT_Proton_1", **{pin: "0" * 64})
    assert r.returncode == 2 and "is not its pinned sha256" in r.stderr and not h.calls()


def test_unf_refuses_a_setup_that_is_not_the_committed_one(h):
    other = h.tmp / "other_setup.sh"
    other.write_text("export X=1\n")
    r = h.real("unf", "pin", "GEANT_Proton:1", name="geanttw_p3_unf_pin_GEANT_Proton_1", GEANTTW_TEST_SETUP=str(other))
    assert r.returncode == 2 and "is not the deploy's committed setup_salloc_env.sh" in r.stderr


def test_extract_all_runs_the_readout(h):
    r = h.real("extract", "all")
    assert r.returncode == 0, r.stderr
    (c,) = h.calls()
    assert c == (f"PY3 {h.deploy / REL}/p3_readout.py extract --repo {h.deploy} --outs {h.B}/p3/out "
                 f"--out {h.B}/run/p3/p3_vectors_all.npz --slims pin pinov patov")


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
    (h.B / "p3" / "out").mkdir(parents=True)
    (h.B / "p3" / "out" / "pin").write_text("a file in the way\n")
    r = h.real("unf", "pin", "GEANT_Pion:1", name="geanttw_p3_unf_pin_GEANT_Pion_1")
    assert r.returncode == 2 and "cannot make" in r.stderr and not h.calls()


def test_unf_stops_without_the_drivers_directory(h):
    h.fence(("",), timelimit="00:30:00")
    env = h.env(SLURM_JOB_ID="77", SLURM_JOB_NAME="geanttw_p3_unf_pin_GEANT_Pion_1")   # pins taken first
    shutil.rmtree(h.deploy / "2d-unfolding")
    r = h.run("unf", "pin", "GEANT_Pion:1", env=env)
    assert r.returncode == 2 and f"REFUSE: no {h.deploy}/2d-unfolding" in r.stderr and not h.calls()
