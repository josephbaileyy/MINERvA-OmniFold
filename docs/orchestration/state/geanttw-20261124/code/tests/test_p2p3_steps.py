"""geanttw_remote.sh's P2-P3 steps through geanttw_connect.sh (RemoteHarness): each step's prerequisites, its exact
sbatch calls, the one-submission rule, the fences on live predecessors, the C3 gate and the cap gate."""
import importlib.util
import json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
_s = importlib.util.spec_from_file_location("tss", HERE / "test_shell_scripts.py")
T = importlib.util.module_from_spec(_s)
_s.loader.exec_module(T)
UNIS = ["GEANT_Neutron:0", "GEANT_Neutron:1", "GEANT_Pion:0", "GEANT_Pion:1", "GEANT_Proton:0", "GEANT_Proton:1"]
P2_PLS = ["1A", "1C", "1D", "1E", "1F", "1G", "1M", "1N", "1O", "1P"]


class S:
    def __init__(self, tmp):
        self.h = T.RemoteHarness(tmp)
        r = self.h.connect("deploy")
        assert r.returncode == 0, r.stdout
        self.B, self.D = self.h.B, self.h.B / "deploy"
        self.code = self.D / T.CODE_REL

    def record(self, rel, verdict):
        p = self.B / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"verdict": verdict}))

    def p0_done(self):
        self.record("run/p0/p0_check.json", "PASS")
        g = self.B / "run" / "gates" / "ll5d_atime_post.txt"
        g.parent.mkdir(parents=True, exist_ok=True)
        g.write_text("ll5d_atime_post_utc=2026-11-15T02:21:21Z\n")
        b = self.B / "prefix-pat" / "bin" / "runEventLoopOmniFold"
        b.parent.mkdir(parents=True, exist_ok=True)
        b.write_text("bin-pat\n")
        b.chmod(0o755)

    def step(self, name, *args, **kw):
        return self.h.connect(name, *args, **kw)

    def sbatches(self):
        return [ln for ln in self.h.calls_lines() if ln.startswith("sbatch ")]

    def p2_outputs(self):
        d = self.B / "run" / "p2" / "pat"
        d.mkdir(parents=True, exist_ok=True)
        for pl in P2_PLS + ["pilotref_1B"]:
            (d / f"runEventLoopOmniFold_GEANTTW_pat_{pl}.root").write_text("out\n")

    def slims(self):
        d = self.B / "p3"
        d.mkdir(parents=True, exist_ok=True)
        for f in ("slim-pinned", "slim-pinned-override", "slim-patched-override"):
            (d / f"{f}.root").write_text("slim\n")


@pytest.fixture
def st(tmp_path):
    return S(tmp_path)


def test_c2pre_submits_one_job(st):
    st.p0_done()
    r = st.step("c2pre")
    assert r.returncode == 0, r.stdout
    (sb,) = st.sbatches()
    assert sb == (f"sbatch --parsable --job-name=geanttw_p2_c2pre --time=00:30:00 --output={st.B}/run/logs/%x_%j.out "
                  f"-c 2 --mem=16G {st.code}/geanttw_p3.sbatch c2pre {st.B} {st.D}")
    assert "SUBMIT id=" in r.stdout and "name=geanttw_p2_c2pre limit=00:30:00" in r.stdout
    r2 = st.step("c2pre")
    assert r2.returncode == 8 and "geanttw_p2_c2pre was already submitted" in r2.stdout


def test_c2pre_needs_p0_pass(st):
    st.record("run/p0/p0_check.json", "FAIL")
    r = st.step("c2pre")
    assert r.returncode == 8 and "P0's check is not PASS" in r.stdout and not st.sbatches()


def test_p2pilot_submits_the_pair_after_c2pre(st):
    st.p0_done()
    r = st.step("p2pilot")
    assert r.returncode == 8 and "the C2 pre-check is not PASS" in r.stdout
    st.record("run/p3/c2pre.json", "PASS")
    r = st.step("p2pilot")
    assert r.returncode == 0, r.stdout
    names = [s.split("--job-name=")[1].split()[0] for s in st.sbatches()]
    assert names == ["geanttw_p2_pilotref_1B", "geanttw_p2_pilot_1B"]
    assert all(f"geanttw_evloop.sbatch {st.B} pat 1B " in s and s.endswith(f"{st.code}/p2_limits.txt " +
               __import__("hashlib").sha256((st.code / "p2_limits.txt").read_bytes()).hexdigest()) for s in st.sbatches())


def test_p2pilot_needs_the_atime_post_record(st):
    st.p0_done()
    st.record("run/p3/c2pre.json", "PASS")
    (st.B / "run" / "gates" / "ll5d_atime_post.txt").unlink()
    r = st.step("p2pilot")
    assert r.returncode == 8 and "no LL5D atime-post record" in r.stdout


def test_p2run_needs_the_pilot_then_submits_ten_in_order(st):
    st.p0_done()
    st.record("run/p3/c2pre.json", "PASS")
    r = st.step("p2run")
    assert r.returncode == 8 and "the pilot pair was not submitted" in r.stdout
    assert st.step("p2pilot").returncode == 0
    r = st.step("p2run")
    assert r.returncode == 0, r.stdout
    names = [s.split("--job-name=")[1].split()[0] for s in st.sbatches()][2:]
    assert names == [f"geanttw_p2_{pl}" for pl in P2_PLS]


def test_c2_needs_every_p2_output_and_no_live_p2_job(st):
    r = st.step("c2")
    assert r.returncode == 8 and "no P2 output for 1A" in r.stdout
    st.p2_outputs()
    st.h.live("geanttw_p2_1M|RUNNING")
    r = st.step("c2")
    assert r.returncode == 8 and "P2 jobs still live" in r.stdout
    st.h.live()
    r = st.step("c2")
    assert r.returncode == 0, r.stdout
    assert st.sbatches()[-1].endswith(f"-c 2 --mem=16G {st.code}/geanttw_p3.sbatch c2 {st.B} {st.D}")


@pytest.mark.parametrize("c2pre,c2,msg", [("FAIL", "PASS", "the C2 pre-check is not PASS"),
                                           ("PASS", "FAIL", "C2 is not PASS: P3's splice stops")])
def test_p3slim_needs_both_c2s(st, c2pre, c2, msg):
    st.record("run/p3/c2pre.json", c2pre)
    st.record("run/p3/c2.json", c2)
    r = st.step("p3slim")
    assert r.returncode == 8 and msg in r.stdout and not st.sbatches()


def test_p3slim_submits(st):
    st.record("run/p3/c2pre.json", "PASS")
    st.record("run/p3/c2.json", "PASS")
    r = st.step("p3slim")
    assert r.returncode == 0, r.stdout
    assert "--job-name=geanttw_p3_slim --time=01:00:00" in st.sbatches()[0]


def test_p3unf_pin_submits_six_full_requests(st):
    r = st.step("p3unf", "pin")
    assert r.returncode == 8 and "no " in r.stdout and "slim-pinned.root" in r.stdout
    st.slims()
    r = st.step("p3unf", "pin")
    assert r.returncode == 0, r.stdout
    sb = st.sbatches()
    assert [s.split("--job-name=")[1].split()[0] for s in sb] == [f"geanttw_p3_unf_pin_{u.replace(':', '_')}" for u in UNIS]
    assert all("--time=00:30:00" in s and "-c 128 --mem=243840M" in s for s in sb)
    assert sb[0].endswith(f"geanttw_p3.sbatch unf {st.B} {st.D} pin GEANT_Neutron:0")


def test_p3unf_rest_needs_c3_pass(st):
    st.slims()
    for v in ("NOT REPRODUCED", "FAIL"):
        st.record("run/p3/c3.json", v)
        r = st.step("p3unf", "rest")
        assert r.returncode == 8 and "C3 is not PASS" in r.stdout and not st.sbatches()
    st.record("run/p3/c3.json", "PASS")
    r = st.step("p3unf", "rest")
    assert r.returncode == 0, r.stdout
    names = [s.split("--job-name=")[1].split()[0] for s in st.sbatches()]
    assert names == [f"geanttw_p3_unf_{s}_{u.replace(':', '_')}" for s in ("pinov", "patov") for u in UNIS]


def test_p3unf_refuses_while_the_slim_job_is_live(st):
    st.slims()
    st.h.live("geanttw_p3_slim|RUNNING")
    r = st.step("p3unf", "pin")
    assert r.returncode == 8 and "the slim job still live" in r.stdout


@pytest.mark.parametrize("step,arg", [("p3unf", "all"), ("p3extract", "some")])
def test_stage_arguments_are_checked(st, step, arg):
    r = st.step(step, arg)
    assert r.returncode == 8 and f"takes pin or" in r.stdout


def test_p3extract_waits_for_the_unfolds(st):
    st.h.live("geanttw_p3_unf_pin_GEANT_Pion_0|PENDING")
    r = st.step("p3extract", "pin")
    assert r.returncode == 8 and "unfolds still live" in r.stdout
    st.h.live()
    r = st.step("p3extract", "pin")
    assert r.returncode == 0, r.stdout
    assert st.sbatches()[0].endswith(f"geanttw_p3.sbatch extract {st.B} {st.D} pin")


def test_the_cap_gate_refuses_over_eight_node_hours(st):
    st.p0_done()
    st.h.sacct.write_text("100|geanttw_p3_unf_pin_GEANT_Pion_0|RUNNING|0|1|960\n")   # 16 h held at 0.5 node-h/h
    r = st.step("c2pre")
    assert r.returncode == 8 and "the cap gate refuses geanttw_p2_c2pre" in r.stdout and not st.sbatches()


def test_a_changed_limits_file_stops_every_p2p3_step(st):
    st.p0_done()
    r = st.step("c2pre", TEST_LIMITS_RC="1")
    assert r.returncode == 8 and "p2_limits.txt is not the repo's" in r.stdout and not st.sbatches()


@pytest.mark.parametrize("job", ["cov2d_x|RUNNING", "t2a_y|PENDING", "covfix_pg_connect|RUNNING"])
def test_every_p2p3_step_is_fenced(st, job):
    st.p0_done()
    st.h.live(job)
    r = st.step("c2pre")
    assert r.returncode == 8 and "the sacct fence" in r.stdout and not st.sbatches()
