"""Controls for EVW2D's launch set: the job script (sbatch_evw2d.sh), the connect's allocation check, the Mac launcher
and fill_pins.sh. Nothing reaches a scheduler or a cluster: scontrol, srun, squeue, ssh, scp and ssh-keygen are stubs.
The scontrol text comes from two records on main, read verbatim:
- a PENDING job (cov2d's connect log; `scontrol show job` filtered to five lines and joined): NumNodes=1-1;
- a RUNNING job (xr-linux's scontrol-job.txt; `scontrol -o show job` in full): NumNodes=1.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

EV = Path(__file__).resolve().parent
REPO = EV.parents[1]
LAUNCH = REPO / "docs/orchestration/state/2d-closeout/evw2d-20261124/launch"
JOB = EV / "sbatch_evw2d.sh"
PENDING_SRC = ("docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/a2/bulk/complete/"
               "connect-complete-1.log.txt")
RUNNING_SRC = "docs/orchestration/state/next-preparation-20261009/xr-linux/results/outroot/L0/a1/scontrol-job.txt"


def real_pending() -> str:
    line = [x for x in (REPO / PENDING_SRC).read_text().splitlines() if x.startswith("JobId=60912517 ")]
    assert len(line) == 1 and " JobState=PENDING " in line[0] and " NumNodes=1-1 " in line[0]
    return line[0]


def real_running() -> str:
    text = (REPO / RUNNING_SRC).read_text().strip()
    assert " JobState=RUNNING " in text and " NumNodes=1 " in text and "\n" not in text
    return text


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def stub(bin_: Path, name: str, body: str) -> None:
    (bin_ / name).write_text("#!/bin/bash\n" + body + "\n")
    (bin_ / name).chmod(0o755)


def git_repo(path: Path, files: dict) -> str:
    path.mkdir(parents=True)
    for rel, text in files.items():
        (path / rel).parent.mkdir(parents=True, exist_ok=True)
        (path / rel).write_bytes(text if isinstance(text, bytes) else text.encode())
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "x"]):
        subprocess.run(["git", "-C", str(path), *cmd], check=True, env=env, capture_output=True)
    return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()


# ------------------------------------------------------------------------------------------------- the job script

@pytest.fixture()
def job(tmp_path):
    """A fake job: the lane root and its logs, deploy_M and deploy_C (tiny git repos with the real evw2d.py and
    config.json), a root_6_28 python3 under a fake HOME, and stubs for scontrol, srun and sha256sum. The print-only
    step runs its real command under the stub's step variables; the wrapper step is only recorded."""
    tmp = Path(os.path.realpath(tmp_path))
    lane = tmp / "evw2d-20261126"
    (lane / "logs").mkdir(parents=True)
    home = tmp / "home"
    py = home / ".conda/envs/root_6_28/bin"
    py.mkdir(parents=True)
    stub(py, "python3", 'echo "python3 $*"')
    setup_ok = f'export PATH="{py}:$PATH"\nreturn 0\n'
    m = git_repo(tmp / "deploy_M", {"setup_salloc_env.sh": setup_ok})
    w, cfg = (EV / "evw2d.py").read_bytes(), (EV / "config.json").read_bytes()
    c = git_repo(tmp / "deploy_C", {"2d-unfolding/evw2d/evw2d.py": w, "2d-unfolding/evw2d/config.json": cfg})
    bin_ = tmp / "bin"
    bin_.mkdir()
    rec = real_running().replace("JobId=59660487 JobName=xrl_L0_a1", "JobId=4242 JobName=evw2d") \
                        .replace("TimeLimit=01:00:00", "TimeLimit=00:30:00")
    (tmp / "scontrol.txt").write_text(rec + "\n")
    stub(bin_, "scontrol", f'cat "{tmp / "scontrol.txt"}"')
    stub(bin_, "sha256sum", 'shasum -a 256 "$@"')
    stub(bin_, "srun", f"""
if [ "$5" = "--mem=1G" ]; then
  shift 5
  echo probe >> "{tmp / "srun.calls"}"
  SLURM_JOB_NUM_NODES="${{STEP_JOB_NUM_NODES-1}}" SLURM_STEP_NUM_NODES=1 SLURM_STEP_ID=0 SLURM_NNODES=1 "$@"
  exit ${{PROBE_RC:-0}}
fi
echo "wrapper $* OMP=$OMP_NUM_THREADS MKL=$MKL_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS B=$PYTHONDONTWRITEBYTECODE" >> "{tmp / "srun.calls"}"
exit ${{WRAPPER_RC:-0}}""")
    env = dict(os.environ, PATH=f"{bin_}:{os.environ['PATH']}", HOME=str(home), SLURM_JOB_ID="4242",
               SLURM_JOB_NAME="evw2d", SLURM_JOB_NUM_NODES="1")
    for k in ("SLURM_ARRAY_JOB_ID", "SLURM_ARRAY_TASK_ID"):
        env.pop(k, None)
    state = {"m": m, "c": c, "wsha": hashlib.sha256(w).hexdigest(), "csha": hashlib.sha256(cfg).hexdigest()}

    def run(extra_env=None, **over):
        a = dict(state, **over)
        args = [str(lane), str(tmp / "deploy_M"), a["m"], str(tmp / "deploy_C"), a["c"], a["wsha"], a["csha"]]
        return subprocess.run(["bash", str(JOB), *args], capture_output=True, text=True, env=dict(env, **(extra_env or {})))

    def done():
        return json.loads((lane / "logs" / "DONE-4242").read_text())

    def calls():
        p = tmp / "srun.calls"
        return p.read_text().splitlines() if p.exists() else []

    def set_setup(text):
        (tmp / "deploy_M" / "setup_salloc_env.sh").write_text(text)
        subprocess.run(["git", "-C", str(tmp / "deploy_M"), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                        "-am", "s"], check=True)
        state["m"] = subprocess.run(["git", "-C", str(tmp / "deploy_M"), "rev-parse", "HEAD"], capture_output=True,
                                    text=True, check=True).stdout.strip()

    return {"run": run, "done": done, "calls": calls, "lane": lane, "tmp": tmp, "state": state, "rec": rec,
            "set_setup": set_setup, "py": py}


def test_job_runs_the_probe_then_one_64_cpu_step(job):
    r = job["run"]()
    assert r.returncode == 0, r.stderr
    assert job["done"]()["rc"] == 0
    assert job["done"]()["deploy_M_porcelain_ignored_after"] == "0"
    probe = (job["lane"] / "logs" / "probe-4242.log").read_text()
    assert "SLURM_JOB_NUM_NODES=1\n" in probe and "SLURM_STEP_ID=0\n" in probe and "SLURM_STEP_NUM_NODES=1\n" in probe
    calls = job["calls"]()
    assert calls[0] == "probe" and len(calls) == 2
    w = calls[1]
    assert w.startswith("wrapper --exclusive -n1 -c 64 --mem=200G python3 -B ")
    assert f"--config-sha256 {job['state']['csha']} run --out {job['lane']}/out" in w
    assert w.endswith("OMP=64 MKL=1 OPENBLAS=1 B=1")


@pytest.mark.parametrize("value", ["1-1", "2", "", "01"])
def test_job_stops_before_the_wrapper_when_the_steps_node_count_is_not_1(job, value):
    r = job["run"](extra_env={"STEP_JOB_NUM_NODES": value})
    assert r.returncode == 2
    assert f"SLURM_JOB_NUM_NODES is '{value}', not 1" in job["done"]()["refused"]
    assert job["calls"]() == ["probe"], "the wrapper ran"
    assert f"SLURM_JOB_NUM_NODES={value}\n" in (job["lane"] / "logs" / "probe-4242.log").read_text(), "not on record"


def test_job_stops_when_the_probe_step_fails(job):
    r = job["run"](extra_env={"PROBE_RC": "1"})
    assert r.returncode == 2 and "print-only step returned 1" in job["done"]()["refused"]
    assert job["calls"]() == ["probe"]


@pytest.mark.parametrize("env,reason", [
    ({"SLURM_JOB_NUM_NODES": "2"}, "batch shell SLURM_JOB_NUM_NODES=2, not 1"),
    ({"SLURM_JOB_NUM_NODES": "1-1"}, "batch shell SLURM_JOB_NUM_NODES=1-1, not 1"),
    ({"SLURM_JOB_NAME": "other"}, "job name other"),
    ({"SLURM_ARRAY_JOB_ID": "7", "SLURM_ARRAY_TASK_ID": "0"}, "an array task"),
])
def test_job_refuses_the_batch_shell(job, env, reason):
    r = job["run"](extra_env=env)
    assert r.returncode == 2 and reason in job["done"]()["refused"] and job["calls"]() == []


@pytest.mark.parametrize("edit,ok", [
    (("TimeLimit=00:30:00", "TimeLimit=01:00:00"), False),
    (("NumNodes=1 ", "NumNodes=2 "), False),
    (("NumNodes=1 ", "NumNodes=1-2 "), False),
    (("NumNodes=1 ", "NumNodes=11 "), False),
    (("NumNodes=1 ", "NumNodes=1-1 "), True),     # the pending form, accepted as the connect accepts it
    (("NumNodes=1 ", "NumNodes= "), False),
])
def test_job_checks_the_allocation_by_scontrol(job, edit, ok):
    (job["tmp"] / "scontrol.txt").write_text(job["rec"].replace(*edit) + "\n")
    r = job["run"]()
    if ok:
        assert r.returncode == 0, r.stderr
    else:
        assert r.returncode == 2 and "scontrol" in job["done"]()["refused"] and job["calls"]() == []


def test_job_refuses_when_scontrol_fails(job):
    stub(job["tmp"] / "bin", "scontrol", "exit 1")
    r = job["run"]()
    assert r.returncode == 2 and "scontrol show job 4242 failed" in job["done"]()["refused"]


def test_job_refuses_wrong_bytes_and_unclean_checkouts(job):
    cases = [({"wsha": "0" * 64}, "evw2d.py sha256"), ({"csha": "0" * 64}, "config.json sha256"),
             ({"m": "0" * 40}, "deploy_M is not a clean checkout"), ({"c": "0" * 40}, "deploy_C is not a clean checkout")]
    for over, reason in cases:
        r = job["run"](**over)
        assert r.returncode == 2 and reason in job["done"]()["refused"], (over, r.stderr)
        (job["lane"] / "logs" / "DONE-4242").unlink()
    (job["tmp"] / "deploy_C" / "stray.pyc").write_bytes(b"x")
    r = job["run"]()
    assert r.returncode == 2 and "deploy_C is not a clean checkout" in job["done"]()["refused"]
    assert job["calls"]() == []


def test_job_refuses_an_existing_out_and_a_failed_setup(job):
    (job["lane"] / "out").mkdir()
    r = job["run"]()
    assert r.returncode == 2 and "/out exists" in job["done"]()["refused"]
    (job["lane"] / "out").rmdir()
    (job["lane"] / "logs" / "DONE-4242").unlink()
    job["set_setup"]("return 1\n")
    r = job["run"]()
    assert r.returncode == 2 and "setup_salloc_env.sh returned 1" in job["done"]()["refused"]
    (job["lane"] / "logs" / "DONE-4242").unlink()
    (job["lane"] / "logs" / "job-env-4242.log").unlink()
    job["set_setup"]("return 0\n")                       # python3 is not root_6_28's
    r = job["run"]()
    assert r.returncode == 2 and "python3 is not root_6_28's" in job["done"]()["refused"]
    assert job["calls"]() == []


def test_job_refuses_linked_or_existing_log_paths(job):
    target = job["tmp"] / "elsewhere"
    target.mkdir()
    victim = job["tmp"] / "victim.txt"
    victim.write_text("keep")
    (job["lane"] / "logs" / "probe-4242.log").symlink_to(victim)
    r = job["run"]()
    assert r.returncode == 2 and "exists" in r.stderr and victim.read_text() == "keep"
    shutil.rmtree(job["lane"] / "logs")
    (job["lane"] / "logs").symlink_to(target)
    r = job["run"]()
    assert r.returncode == 2 and "refusing: logs" in r.stderr and list(target.iterdir()) == []


def test_job_records_the_wrappers_status(job):
    r = job["run"](extra_env={"WRAPPER_RC": "6"})
    assert r.returncode == 6 and job["done"]()["rc"] == 6


# ------------------------------------------------------------------------------- the connect's allocation check

def _alloc_block(path: Path) -> str:
    lines = path.read_text().split("\n")
    i = lines.index('sj=$(scontrol -o show job "$job")')
    j = lines.index("fi", i)
    return "\n".join(lines[i:j + 1])


def _run_alloc(tmp: Path, block: str, text: str, tlimit: str) -> tuple[int, str, bool]:
    b = tmp / "bin"
    b.mkdir(exist_ok=True)
    (tmp / "scontrol.txt").write_text(text)
    marker = tmp / "cancelled"
    if marker.exists():
        marker.unlink()
    for name, body in (("scontrol", f'cat "{tmp / "scontrol.txt"}"'), ("scancel", f'touch "{marker}"'),
                       ("sacct", "true"), ("sleep", "true")):
        stub(b, name, body)
    script = f"TLIMIT={tlimit}; job=4242\nfinish() {{ echo FINISH $1; exit $1; }}\n" + block + "\necho PASSED\n"
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                       env=dict(os.environ, PATH=f"{b}:{os.environ['PATH']}"))
    return r.returncode, r.stdout, marker.exists()


def _connects():
    out = [LAUNCH / "evw2d_connect.sh"]
    if (LAUNCH / "bound" / "evw2d_connect.sh").exists():
        out.append(LAUNCH / "bound" / "evw2d_connect.sh")
    return out


@pytest.mark.parametrize("path", _connects(), ids=lambda p: p.parent.name)
def test_connect_allocation_check_on_real_records(tmp_path, path):
    block = _alloc_block(path)
    assert block == _alloc_block(LAUNCH / "evw2d_connect.sh"), "the bound check differs from the template's"
    pend, run = real_pending(), real_running()
    # the records verbatim, at their own time limits: both accepted
    for text, tl in ((pend, "01:19:00"), (run, "01:00:00")):
        rc, out, cancelled = _run_alloc(tmp_path, block, text, tl)
        assert rc == 0 and "PASSED" in out and not cancelled, (tl, out)
    p30 = pend.replace("TimeLimit=01:19:00", "TimeLimit=00:30:00")
    r30 = run.replace("TimeLimit=01:00:00", "TimeLimit=00:30:00")
    cases = [  # (text, accepted)
        (p30, True),                                            # pending, NumNodes=1-1
        (r30, True),                                            # running, NumNodes=1
        (p30.replace("NumNodes=1-1", "NumNodes=2-2"), False),
        (p30.replace("NumNodes=1-1", "NumNodes=1-2"), False),
        (r30.replace("NumNodes=1 ", "NumNodes=2 "), False),
        (r30.replace("NumNodes=1 ", "NumNodes=11 "), False),
        (pend, False),                                          # 01:19:00 against the declared 00:30:00
        (p30.replace("JobState=PENDING", "ArrayJobId=4242 ArrayTaskId=0 JobState=PENDING"), False),
        ("", False),                                            # scontrol printed nothing
    ]
    for text, ok in cases:
        rc, out, cancelled = _run_alloc(tmp_path, block, text, "00:30:00")
        if ok:
            assert rc == 0 and "PASSED" in out and not cancelled, (text[:80], out)
        else:
            assert rc == 6 and "FINISH 6" in out and cancelled, (text[:80], out)


def test_connect_reads_reqnodelist_and_nodelist_not_as_numnodes(tmp_path):
    """NodeList=, ReqNodeList= and ExcNodeList= tokens never stand in for NumNodes=."""
    block = _alloc_block(LAUNCH / "evw2d_connect.sh")
    text = real_running().replace("TimeLimit=01:00:00", "TimeLimit=00:30:00").replace(" NumNodes=1 ", " ")
    rc, out, cancelled = _run_alloc(tmp_path, block, text, "00:30:00")
    assert rc == 6 and cancelled


# ---------------------------------------------------------------------------------------------- the launcher

def _launcher(tmp: Path, cert_to: str, script_body: str = "#!/bin/bash\necho remote-ran\nrm -f -- \"$1\"\nexit 0\n"):
    ld = tmp / "launch"
    ld.mkdir()
    (ld / "evw2d_connect.sh").write_text(script_body)
    s = sha(ld / "evw2d_connect.sh")
    text = (LAUNCH / "evw2d_launch.sh").read_text().replace("__CONNECT_SHA256__", s) \
        .replace("__LANE_ROOT__", "/pscratch/sd/j/josephrb/evw2d-20261126")
    (ld / "evw2d_launch.sh").write_text(text)
    shm = tmp / "shm"
    shm.mkdir()
    b = tmp / "stubbin"
    b.mkdir()
    stub(b, "ssh", f'echo ssh >> "{tmp / "ssh.calls"}"\nlast="${{@: -1}}"\nexec bash -c "${{last//\\/dev\\/shm/{shm}}}"')
    stub(b, "sha256sum", 'shasum -a 256 "$@"')
    stub(b, "ssh-keygen", f'echo "        Type: ssh-rsa-cert-v01@openssh.com user certificate"\n'
                          f'echo "        Valid: from 2026-01-01T00:00:00 to {cert_to}"')
    env = dict(os.environ, PATH=f"{b}:{os.environ['PATH']}", EVW2D_CERT=str(tmp / "cert.pub"))
    return ld, shm, env


def _local(seconds: int) -> str:
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() + seconds))


@pytest.mark.skipif(sys.platform != "darwin", reason="the launcher runs on the Mac (BSD date -j)")
def test_launcher_checks_the_certificate_before_the_step(tmp_path):
    tmp = Path(os.path.realpath(tmp_path))
    ld, shm, env = _launcher(tmp, _local(1200))                   # 20 min left; connect needs 45
    sess = tmp / "s1"
    sess.mkdir()
    r = subprocess.run(["bash", str(ld / "evw2d_launch.sh"), "connect", str(sess), "login27"], capture_output=True,
                       text=True, env=env)
    assert r.returncode == 7 and "expires too soon" in r.stdout and not (tmp / "ssh.calls").exists()


@pytest.mark.skipif(sys.platform != "darwin", reason="the launcher runs on the Mac (BSD date -j)")
def test_launcher_runs_the_approved_bytes_and_propagates_the_status(tmp_path):
    tmp = Path(os.path.realpath(tmp_path))
    ld, shm, env = _launcher(tmp, _local(6 * 3600), "#!/bin/bash\necho refused >&2\nrm -f -- \"$1\"\nexit 9\n")
    sess = tmp / "s1"
    sess.mkdir()
    r = subprocess.run(["bash", str(ld / "evw2d_launch.sh"), "connect", str(sess), "login27"], capture_output=True,
                       text=True, env=env)
    assert r.returncode == 9 and "script rc=9" in r.stdout, r.stdout + r.stderr
    assert list(shm.iterdir()) == [], "the staged copy was left"
    (ld / "evw2d_connect.sh").write_text("#!/bin/bash\nexit 0\n")    # not the approved bytes
    sess2 = tmp / "s2"
    sess2.mkdir()
    r = subprocess.run(["bash", str(ld / "evw2d_launch.sh"), "connect", str(sess2), "login27"], capture_output=True,
                       text=True, env=env)
    assert r.returncode == 8 and "not the approved one" in r.stdout


def test_launcher_refuses_unfilled_pins_and_bad_node_names(tmp_path):
    tmp = Path(os.path.realpath(tmp_path))
    sess = tmp / "s"
    sess.mkdir()
    r = subprocess.run(["bash", str(LAUNCH / "evw2d_launch.sh"), "connect", str(sess), "login27"], capture_output=True,
                       text=True)
    assert r.returncode == 9 and "lane root is not filled in" in r.stdout
    ld, shm, env = _launcher(tmp, _local(6 * 3600))
    r = subprocess.run(["bash", str(ld / "evw2d_launch.sh"), "connect", str(sess), "nid001"], capture_output=True,
                       text=True, env=env)
    assert r.returncode == 9 and "not a login node name" in r.stdout


# ---------------------------------------------------------------------------------------------- fill_pins.sh

def _copy_tree(tmp: Path) -> Path:
    """A git repo holding the launch set, evw2d's files and the declaration at their repo paths, with a first commit
    standing in for the reviewed merge (its config.json the reviewed bytes) and a second for C (the binding's)."""
    top = tmp / "top"
    rel_l = LAUNCH.relative_to(REPO)
    rel_d = "docs/orchestration/state/2d-closeout/evw2d-20261124/EVW2D-DECLARATION.md"
    for f in ("evw2d.py", "sbatch_evw2d.sh", "config.json", "references.npz"):
        (top / "2d-unfolding/evw2d").mkdir(parents=True, exist_ok=True)
        shutil.copy(EV / f, top / "2d-unfolding/evw2d" / f)
    (top / rel_l).mkdir(parents=True)
    for f in LAUNCH.glob("*.sh"):
        shutil.copy(f, top / rel_l / f.name)
    shutil.copy(REPO / rel_d, top / rel_d)
    return top


def _commit(top: Path, msg: str) -> str:
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    subprocess.run(["git", "-C", str(top), "add", "-A"], check=True, env=env)
    subprocess.run(["git", "-C", str(top), "commit", "-q", "-m", msg], check=True, env=env)
    return subprocess.run(["git", "-C", str(top), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()


def _bind(top: Path, lane: str, **over) -> None:
    p = top / "2d-unfolding/evw2d/config.json"
    c = json.loads((EV / "config.json").read_text())
    c["declaration_sha256"] = sha(top / "docs/orchestration/state/2d-closeout/evw2d-20261124/EVW2D-DECLARATION.md")
    c["lane_root"] = lane
    c["driver_tree"]["root"] = lane + "/deploy_M"
    c["inputs"]["staging"]["root"] = lane + "/stage"
    for k, v in over.items():
        c[k] = v
    p.write_text(json.dumps(c, indent=1) + "\n")


def _fill(top: Path, c: str, reviewed: str):
    fp = top / LAUNCH.relative_to(REPO) / "fill_pins.sh"
    text = (LAUNCH / "fill_pins.sh").read_text().replace("4d9147f9a94c14b0c313f2e611a35e044b327704", reviewed)
    fp.write_text(text)
    return subprocess.run(["bash", str(fp), c], capture_output=True, text=True)


def test_fill_pins_writes_every_pin_from_c(tmp_path):
    top = _copy_tree(Path(os.path.realpath(tmp_path)))
    subprocess.run(["git", "init", "-q", str(top)], check=True)
    reviewed = _commit(top, "reviewed")
    lane = "/pscratch/sd/j/josephrb/evw2d-20261126"
    _bind(top, lane)
    c = _commit(top, "binding")
    r = _fill(top, c, reviewed)
    assert r.returncode == 0, r.stdout + r.stderr
    b = top / LAUNCH.relative_to(REPO) / "bound"
    pins = dict(re.split(r"\s{2,}", line, maxsplit=1) for line in (b / "PINS.txt").read_text().splitlines())
    assert pins["tool commit"] == c and pins["lane root"] == lane
    assert pins["config.json"] == sha(top / "2d-unfolding/evw2d/config.json")
    assert pins["evw2d_connect.sh"] == sha(b / "evw2d_connect.sh")
    launcher = (b / "evw2d_launch.sh").read_text()
    for name in ("evw2d_connect.sh", "evw2d_post.sh", "evw2d_cleanup.sh"):
        assert sha(b / name) in launcher
    for f in b.glob("*.sh"):
        assert not re.search(r"__[A-Z0-9_]+__", f.read_text()), f
    con = (b / "evw2d_connect.sh").read_text()
    assert f"LANE={lane}\n" in con and f"C={c}\n" in con
    assert _alloc_block(b / "evw2d_connect.sh") == _alloc_block(LAUNCH / "evw2d_connect.sh")


@pytest.mark.parametrize("over", [{"exact_rtol": 1e-6}, {"lane_root": "/pscratch/sd/j/josephrb/other"},
                                  {"declaration_sha256": "0" * 64}, {"cpus": 32}])
def test_fill_pins_refuses_a_config_that_changes_more_than_the_binding(tmp_path, over):
    top = _copy_tree(Path(os.path.realpath(tmp_path)))
    subprocess.run(["git", "init", "-q", str(top)], check=True)
    reviewed = _commit(top, "reviewed")
    _bind(top, "/pscratch/sd/j/josephrb/evw2d-20261126", **over)
    c = _commit(top, "binding")
    r = _fill(top, c, reviewed)
    assert r.returncode != 0 and not (top / LAUNCH.relative_to(REPO) / "bound").exists(), r.stdout + r.stderr


def test_every_launch_script_parses():
    for f in [JOB, *LAUNCH.glob("*.sh")]:
        r = subprocess.run(["bash", "-n", str(f)], capture_output=True, text=True)
        assert r.returncode == 0, (f, r.stderr)


@pytest.mark.parametrize("lane", ["/pscratch/sd/j/josephrb/other", "/pscratch/sd/j/josephrb/evw2d-2026112",
                                  "/global/cfs/cdirs/m3246/josephrb/evw2d-20261126", "/pscratch/sd/j/josephrb"])
def test_fill_pins_refuses_a_lane_root_outside_the_declared_form(tmp_path, lane):
    """A consistent layout (deploy_M and stage under it) with a lane root that is not $SCRATCH/evw2d-<yyyymmdd>."""
    top = _copy_tree(Path(os.path.realpath(tmp_path)))
    subprocess.run(["git", "init", "-q", str(top)], check=True)
    reviewed = _commit(top, "reviewed")
    _bind(top, lane)
    c = _commit(top, "binding")
    r = _fill(top, c, reviewed)
    assert r.returncode != 0 and not (top / LAUNCH.relative_to(REPO) / "bound").exists(), r.stdout + r.stderr
