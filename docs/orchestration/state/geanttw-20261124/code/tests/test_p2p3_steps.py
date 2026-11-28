"""geanttw_remote.sh's P2-P3 steps through geanttw_connect.sh (RemoteHarness): each step's prerequisites, its exact
sbatch calls, the one-submission rule, the fences on live predecessors, the pilot, slim.json and C3 gates and the cap
gate."""
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
        self.done_rows, self.live_rows, self.next_id = [], [], 70000

    def _sacct(self):
        self.h.sacct.write_text("".join(r + "\n" for r in self.done_rows + self.live_rows))

    def done(self, *names):
        """Predecessor jobs, each with one SUBMIT line and a COMPLETED sacct row."""
        sp = self.B / "run" / "p2p3" / "submissions.log"
        sp.parent.mkdir(parents=True, exist_ok=True)
        with sp.open("a") as fh:
            for n in names:
                self.next_id += 1
                fh.write(f"SUBMIT id={self.next_id} name={n} limit=00:30:00 utc=x\n")
                self.done_rows.append(f"{self.next_id}|{n}|COMPLETED|600|1|30")
        self._sacct()

    def live(self, *jobs):
        self.live_rows = [f"{i}|{j}|0|1|60" for i, j in enumerate(jobs, 100)]
        self._sacct()

    def c2pre_ok(self):
        self.record("run/p3/c2pre.json", "PASS")
        self.done("geanttw_p2_c2pre")

    def record(self, rel, verdict):
        p = self.B / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"verdict": verdict}))

    def p0_jobs(self, pin="COMPLETED", pat="COMPLETED"):
        """P0's two jobs, in P0's own submissions.log and in sacct (they ran 2026-11-26, COMPLETED 0:0)."""
        sp = self.B / "run" / "p0" / "submissions.log"
        sp.parent.mkdir(parents=True, exist_ok=True)
        sp.write_text("SUBMIT id=62042572 name=geanttw_p0_pin_1L limit=01:00:00 md5=a utc=x\n"
                      "SUBMIT id=62042575 name=geanttw_p0_pat_1L limit=01:00:00 md5=b utc=x\n")
        self.done_rows += [f"62042572|geanttw_p0_pin_1L|{pin}|353|1|60", f"62042575|geanttw_p0_pat_1L|{pat}|435|1|60"]
        self._sacct()

    def p0_done(self):
        self.record("run/p0/p0_check.json", "PASS")
        self.p0_jobs()
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
        d = self.B / "run" / "p0" / "pat"
        d.mkdir(parents=True, exist_ok=True)
        (d / "runEventLoopOmniFold_GEANTTW_pat_1L.root").write_text("out\n")

    def slims(self, verdict="PASS"):
        d = self.B / "p3"
        d.mkdir(parents=True, exist_ok=True)
        for f in ("slim-pinned", "slim-pinned-override", "slim-patched"):
            (d / f"{f}.root").write_text("slim\n")
        self.record("run/p3/slim.json", verdict)
        if verdict == "PASS" and "geanttw_p3_slim" not in "".join(self.done_rows):
            self.done("geanttw_p3_slim")

    def c3_pass(self, tamper=None):
        """A PASSing c3.json bound to six pinned outputs, as extract pin leaves them."""
        import hashlib
        shas = {}
        for b in ("Neutron", "Pion", "Proton"):
            for i in (0, 1):
                x = self.B / "p3" / "out" / "pin" / f"GEANT_{b}_{i}" / "xsec.root"
                x.parent.mkdir(parents=True, exist_ok=True)
                x.write_text(f"{b}{i}")
                shas[f"pin:{b}_{i}"] = hashlib.sha256(x.read_bytes()).hexdigest()
        if tamper:
            (self.B / "p3" / "out" / "pin" / "GEANT_Pion_1" / "xsec.root").write_text("rerun")
        p = self.B / "run" / "p3" / "c3.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"verdict": "PASS", "pin_xsec_sha256": shas}))
        if "geanttw_p3_extract_pin" not in "".join(self.done_rows):
            self.done("geanttw_p3_extract_pin")

    def pilots_done(self, ref="COMPLETED", pil="COMPLETED", e_ref=600, e_pil=660):
        """sacct rows for the pilot pair p2pilot submitted (the stub's ids 90001 and 90002)."""
        self.done_rows += [f"90001|geanttw_p2_pilotref_1B|{ref}|{e_ref}|1|42",
                           f"90002|geanttw_p2_pilot_1B|{pil}|{e_pil}|1|42"]
        self._sacct()


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


@pytest.mark.parametrize("pin,pat", [("FAILED", "COMPLETED"), ("COMPLETED", "FAILED")])
def test_c2pre_and_p3slim_need_their_p0_job_completed(st, pin, pat):
    st.record("run/p0/p0_check.json", "PASS")
    st.p0_jobs(pin=pin, pat=pat)
    if pin == "FAILED":
        r = st.step("c2pre")
        assert r.returncode == 8 and "geanttw_p0_pin_1L is FAILED, not COMPLETED" in r.stdout and not st.sbatches()
        return
    st.c2pre_ok()
    st.p2_outputs()
    st.done(*[f"geanttw_p2_{pl}" for pl in P2_PLS], "geanttw_p2_pilotref_1B")
    r = st.step("p3slim")
    assert r.returncode == 8 and "geanttw_p0_pat_1L is FAILED, not COMPLETED" in r.stdout
    assert not any("geanttw_p3_slim" in s for s in st.sbatches())


def test_p3slim_needs_the_c2pre_job_completed(st):
    st.p0_jobs()
    st.record("run/p3/c2pre.json", "PASS")   # a PASS left by a c2pre that then exited 20
    st.p2_outputs()
    st.done(*[f"geanttw_p2_{pl}" for pl in P2_PLS], "geanttw_p2_pilotref_1B")
    r = st.step("p3slim")
    assert r.returncode == 8 and "geanttw_p2_c2pre has 0 submissions.log lines" in r.stdout and not st.sbatches()


def test_c2pre_needs_p0_pass(st):
    st.record("run/p0/p0_check.json", "FAIL")
    r = st.step("c2pre")
    assert r.returncode == 8 and "P0's check is not PASS" in r.stdout and not st.sbatches()


def test_p2pilot_submits_the_pair_after_c2pre(st):
    st.p0_done()
    r = st.step("p2pilot")
    assert r.returncode == 8 and "the C2 pre-check is not PASS" in r.stdout
    st.c2pre_ok()
    r = st.step("p2pilot")
    assert r.returncode == 0, r.stdout
    names = [s.split("--job-name=")[1].split()[0] for s in st.sbatches()]
    assert names == ["geanttw_p2_pilotref_1B", "geanttw_p2_pilot_1B"]
    assert all(f"geanttw_evloop.sbatch {st.B} pat 1B " in s and s.endswith(f"{st.code}/p2_limits.txt " +
               __import__("hashlib").sha256((st.code / "p2_limits.txt").read_bytes()).hexdigest()) for s in st.sbatches())


def test_p2pilot_needs_the_atime_post_record(st):
    st.p0_done()
    st.c2pre_ok()
    (st.B / "run" / "gates" / "ll5d_atime_post.txt").unlink()
    r = st.step("p2pilot")
    assert r.returncode == 8 and "no LL5D atime-post record" in r.stdout


def test_p2run_needs_the_pilot_then_submits_ten_in_order(st):
    st.p0_done()
    st.c2pre_ok()
    r = st.step("p2run")
    assert r.returncode == 8 and "the pilot pair was not submitted" in r.stdout
    assert st.step("p2pilot").returncode == 0
    st.pilots_done()
    r = st.step("p2run")
    assert r.returncode == 0, r.stdout
    names = [s.split("--job-name=")[1].split()[0] for s in st.sbatches()][2:]
    assert names == [f"geanttw_p2_{pl}" for pl in P2_PLS]
    rec = json.loads((st.B / "run" / "p2p3" / "pilot.json").read_text())
    assert rec["pass"] and rec["geanttw_p2_pilot_1B"]["id"] == "90002"


@pytest.mark.parametrize("ref,pil,e_pil,msg", [("COMPLETED", "RUNNING", 660, "not COMPLETED"),
                                               ("FAILED", "COMPLETED", 660, "not COMPLETED"),
                                               ("COMPLETED", "COMPLETED", 1801, "over 3x: STOP to the director")])
def test_p2run_stops_unless_the_pilot_gate_passes(st, ref, pil, e_pil, msg):
    st.p0_done()
    st.c2pre_ok()
    assert st.step("p2pilot").returncode == 0
    st.pilots_done(ref, pil, e_pil=e_pil)
    r = st.step("p2run")
    assert r.returncode == 8 and "the pilot gate refuses" in r.stdout and msg in r.stdout
    assert len(st.sbatches()) == 2


def test_a_missing_binary_stops_p2_before_any_sbatch(st):
    """evloop runs in the step's own shell: its stop ends the step, not a subshell."""
    st.p0_done()
    st.c2pre_ok()
    (st.B / "prefix-pat" / "bin" / "runEventLoopOmniFold").unlink()
    r = st.step("p2pilot")
    assert r.returncode == 8 and "STOP: no binary" in r.stdout and not st.sbatches()


def test_c2_is_no_longer_a_step(st):
    r = st.step("c2")
    assert r.returncode == 9 and "step must be deploy" in r.stdout


def test_p3slim_needs_the_pre_check_every_dump_and_no_live_p2_job(st):
    st.record("run/p3/c2pre.json", "FAIL")
    r = st.step("p3slim")
    assert r.returncode == 8 and "the C2 pre-check is not PASS" in r.stdout
    st.c2pre_ok()
    r = st.step("p3slim")
    assert r.returncode == 8 and "no P2 output for 1A" in r.stdout
    st.p2_outputs()
    (st.B / "run" / "p0" / "pat" / "runEventLoopOmniFold_GEANTTW_pat_1L.root").unlink()
    r = st.step("p3slim")
    assert r.returncode == 8 and "no P0 patched output for 1L" in r.stdout
    st.p2_outputs()
    st.live("geanttw_p2_1M|RUNNING")
    r = st.step("p3slim")
    assert r.returncode == 8 and "P2 jobs still live" in r.stdout and not st.sbatches()


def test_p3slim_submits_one_pass(st):
    st.p0_jobs()
    st.c2pre_ok()
    st.p2_outputs()
    st.done(*[f"geanttw_p2_{pl}" for pl in P2_PLS if pl != "1M"], "geanttw_p2_pilotref_1B")
    st.live_rows = ["7|geanttw_p2_1M|FAILED|60|1|336"]   # exited 20 after writing its output
    st._sacct()
    st.done_rows.append("")   # keep the FAILED row next to the done rows
    sp = st.B / "run" / "p2p3" / "submissions.log"
    sp.write_text(sp.read_text() + "SUBMIT id=7 name=geanttw_p2_1M limit=05:36:00 utc=x\n")
    st.done_rows.pop()
    r = st.step("p3slim")
    assert r.returncode == 8 and "geanttw_p2_1M is FAILED, not COMPLETED" in r.stdout and not st.sbatches()
    st.live_rows = ["7|geanttw_p2_1M|COMPLETED|60|1|336"]
    st._sacct()
    r = st.step("p3slim")
    assert r.returncode == 0, r.stdout
    (sb,) = st.sbatches()
    assert "--job-name=geanttw_p3_slim --time=02:00:00" in sb
    assert sb.endswith(f"-c 2 --mem=32G {st.code}/geanttw_p3.sbatch slim {st.B} {st.D}")


@pytest.mark.parametrize("verdict", ["FAIL", None])
def test_p3unf_needs_slim_json_pass(st, verdict):
    st.slims("PASS")
    if verdict is None:
        (st.B / "run" / "p3" / "slim.json").unlink()
    else:
        st.record("run/p3/slim.json", verdict)
    r = st.step("p3unf", "pin")
    assert r.returncode == 8 and "slim.json is not PASS" in r.stdout and not st.sbatches()


def test_p3unf_pin_submits_six_full_requests(st):
    st.slims()
    (st.B / "p3" / "slim-pinned.root").unlink()
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
    st.c3_pass(tamper=True)
    r = st.step("p3unf", "rest")
    assert r.returncode == 8 and "the pinned outputs are not the ones it passed" in r.stdout and not st.sbatches()
    st.c3_pass()
    r = st.step("p3unf", "rest")
    assert r.returncode == 0, r.stdout
    names = [s.split("--job-name=")[1].split()[0] for s in st.sbatches()]
    assert names == [f"geanttw_p3_unf_{s}_{u.replace(':', '_')}" for s in ("pinov", "patov") for u in UNIS]


def test_p3unf_refuses_while_the_slim_job_is_live(st):
    st.slims()
    st.live("geanttw_p3_slim|RUNNING")
    r = st.step("p3unf", "pin")
    assert r.returncode == 8 and "the slim job still live" in r.stdout


@pytest.mark.parametrize("step,arg", [("p3unf", "all"), ("p3extract", "some")])
def test_stage_arguments_are_checked(st, step, arg):
    r = st.step(step, arg)
    assert r.returncode == 8 and f"takes pin or" in r.stdout


@pytest.mark.parametrize("c3", ["NOT REPRODUCED", "FAIL", None])
def test_p3extract_all_needs_c3_pass(st, c3):
    if c3:
        st.record("run/p3/c3.json", c3)
    r = st.step("p3extract", "all")
    assert r.returncode == 8 and "no patched number is read" in r.stdout and not st.sbatches()
    st.c3_pass(tamper=True)
    assert st.step("p3extract", "all").returncode == 8 and not st.sbatches()
    st.c3_pass()
    r = st.step("p3extract", "all")
    assert r.returncode == 8 and "not COMPLETED" in r.stdout or "submissions.log lines" in r.stdout
    st.done(*[f"geanttw_p3_unf_{s}_{u.replace(':', '_')}" for s in ("pin", "pinov", "patov") for u in UNIS])
    assert st.step("p3extract", "all").returncode == 0


def test_p3extract_waits_for_the_unfolds(st):
    st.live("geanttw_p3_unf_pin_GEANT_Pion_0|PENDING")
    r = st.step("p3extract", "pin")
    assert r.returncode == 8 and "unfolds still live" in r.stdout
    st.live()
    r = st.step("p3extract", "pin")
    assert r.returncode == 8 and "a predecessor is not COMPLETED" in r.stdout
    st.done(*[f"geanttw_p3_unf_pin_{u.replace(':', '_')}" for u in UNIS])
    r = st.step("p3extract", "pin")
    assert r.returncode == 0, r.stdout
    assert st.sbatches()[0].endswith(f"geanttw_p3.sbatch extract {st.B} {st.D} pin")


def test_the_cap_gate_refuses_over_eight_node_hours(st):
    st.p0_done()
    st.live_rows = ["100|geanttw_p3_unf_pin_GEANT_Pion_0|RUNNING|0|1|960"]   # 16 h held at 0.5 node-h/h
    st._sacct()   # beside P0's COMPLETED rows, which c2pre now needs
    r = st.step("c2pre")
    assert r.returncode == 8 and "the cap gate refuses geanttw_p2_c2pre" in r.stdout and not st.sbatches()


def test_a_changed_limits_file_stops_every_p2p3_step(st):
    st.p0_done()
    r = st.step("c2pre", TEST_LIMITS_RC="1")
    assert r.returncode == 8 and "p2_limits.txt is not the repo's" in r.stdout and not st.sbatches()


@pytest.mark.parametrize("job", ["cov2d_x|RUNNING", "t2a_y|PENDING", "covfix_pg_connect|RUNNING"])
def test_every_p2p3_step_is_fenced(st, job):
    st.p0_done()
    st.live(job)
    r = st.step("c2pre")
    assert r.returncode == 8 and "the sacct fence" in r.stdout and not st.sbatches()


def ready_for_p2(st):
    st.p0_done()
    st.c2pre_ok()


def test_p2pilot_needs_p0_pass(st):
    ready_for_p2(st)
    st.record("run/p0/p0_check.json", "FAIL")
    r = st.step("p2pilot")
    assert r.returncode == 8 and "P0's check is not PASS" in r.stdout and not st.sbatches()


@pytest.mark.parametrize("tool,match,msg", [("md5sum", "runEventLoopOmniFold", "cannot md5"),
                                            ("sha256sum", "p2_limits.txt", "cannot hash")])
def test_an_unhashable_input_stops_p2(st, tool, match, msg):
    """A hash that comes back empty stops the step before sbatch."""
    ready_for_p2(st)
    real = (st.h.bindir / tool).read_text()
    T._write_stub(st.h.bindir, tool, f'case "$*" in *{match}*) exit 0 ;; esac\n' + real.split("\n", 1)[1])
    r = st.step("p2pilot")
    assert r.returncode == 8 and msg in r.stdout and not st.sbatches()


def test_a_failing_sbatch_stops_without_a_submit_line(st):
    st.p0_done()
    T._write_stub(st.h.bindir, "sbatch", 'echo "sbatch $*" >> "$TEST_CALLS"; exit 1')
    r = st.step("c2pre")
    assert r.returncode == 8 and "sbatch geanttw_p2_c2pre failed" in r.stdout
    assert not (st.B / "run" / "p2p3" / "submissions.log").exists()


def test_unmakeable_run_dirs_stop(st):
    st.p0_done()
    (st.B / "run" / "p2p3").write_text("a file in the way\n")
    r = st.step("c2pre")
    assert r.returncode == 8 and "mkdir run dirs" in r.stdout and not st.sbatches()
