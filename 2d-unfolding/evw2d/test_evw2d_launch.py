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
    stub(py, "python3", 'case "$*" in *sched_getaffinity*) echo "affinity=${STEP_AFFINITY-64}";; *) echo "python3 $*";; esac')
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
    stub(bin_, "nproc", 'echo 128   # GNU nproc honours OMP_NUM_THREADS; the probe must not use it')
    stub(bin_, "srun", f"""
if [ "$6" = "bash" ]; then
  echo "$1 $2 $3 $4 $5" >> "{tmp / "srun.probe_opts"}"
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
    assert (job["tmp"] / "srun.probe_opts").read_text() == "--exclusive -n1 -c 64 --mem=200G\n", "probe options differ"
    assert "affinity=64\n" in probe and "SLURM_JOB_NUM_NODES=1\n" in probe and "SLURM_STEP_ID=0\n" in probe and "SLURM_STEP_NUM_NODES=1\n" in probe
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


@pytest.mark.parametrize("value", ["32", "128", ""])
def test_job_stops_before_the_wrapper_when_the_steps_affinity_is_not_64(job, value):
    r = job["run"](extra_env={"STEP_AFFINITY": value})
    assert r.returncode == 2 and f"CPU affinity is '{value}', not 64" in job["done"]()["refused"]
    assert job["calls"]() == ["probe"]


def test_job_refusal_receipt_is_json_with_quotes_escaped(job):
    r = job["run"](extra_env={"SLURM_JOB_NAME": 'x"y\\z'})
    assert r.returncode == 2 and job["done"]()["refused"] == 'job name x"y\\z'


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
    text = path.read_text()
    i = text.index("# ---- the allocation check (begin)")
    j = text.index("# ---- the allocation check (end)")
    return text[i:j]


def _run_alloc(tmp: Path, block: str, text: str, tlimit: str, job: str, show_rc="0", release_rc="0", later=None):
    """Runs the connect's allocation block as written, with scontrol answering `text`; show_rc is a space-separated
    list of exit statuses for successive `scontrol show job` calls (the last repeats); `later`, if given, is the text
    of every call after the first."""
    b = tmp / "bin"
    b.mkdir(exist_ok=True)
    (tmp / "scontrol.txt").write_text(text)
    (tmp / "scontrol-later.txt").write_text(text if later is None else later)
    (tmp / "show_rc").write_text(show_rc)
    for m in ("cancelled", "released", "show_n"):
        if (tmp / m).exists():
            (tmp / m).unlink()
    stub(b, "scontrol", f"""
if [ "$1" = release ]; then echo "$2" > "{tmp / "released"}"; exit {release_rc}; fi
n=$(cat "{tmp / "show_n"}" 2>/dev/null || echo 0); n=$((n + 1)); echo $n > "{tmp / "show_n"}"
set -- $(cat "{tmp / "show_rc"}"); rc=${{!n:-${{@: -1}}}}
if [ "$n" -gt 1 ]; then cat "{tmp / "scontrol-later.txt"}"; else cat "{tmp / "scontrol.txt"}"; fi; exit $rc""")
    stub(b, "scancel", f'echo "$1" > "{tmp / "cancelled"}"')
    stub(b, "sacct", "true")
    stub(b, "sleep", "true")
    script = (f"TLIMIT={tlimit}; job={job}\nfinish() {{ echo FINISH $1; exit $1; }}\n" + block + "\necho PASSED\n")
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                       env=dict(os.environ, PATH=f"{b}:{os.environ['PATH']}"))
    return r.returncode, r.stdout, (tmp / "cancelled").exists(), (tmp / "released").exists()


def _connects():
    out = [LAUNCH / "evw2d_connect.sh"]
    if (LAUNCH / "bound" / "evw2d_connect.sh").exists():
        out.append(LAUNCH / "bound" / "evw2d_connect.sh")
    return out


def _accepts(tmp, block, text, tl, job, **kw):
    rc, out, cancelled, released = _run_alloc(tmp, block, text, tl, job, **kw)
    return rc == 0 and "PASSED" in out and not cancelled and released, (rc, out, cancelled, released)


def _cancels(tmp, block, text, tl, job, **kw):
    rc, out, cancelled, released = _run_alloc(tmp, block, text, tl, job, **kw)
    return rc == 6 and "FINISH 6" in out and cancelled and not released, (rc, out, cancelled, released)


@pytest.mark.parametrize("path", _connects(), ids=lambda p: p.parent.name)
def test_connect_allocation_check_on_real_records(tmp_path, path):
    block = _alloc_block(path)
    assert block == _alloc_block(LAUNCH / "evw2d_connect.sh"), "the bound check differs from the template's"
    pend, run = real_pending(), real_running()
    PJ, RJ = "60912517", "59660487"
    for text, tl, j in ((pend, "01:19:00", PJ), (run, "01:00:00", RJ)):   # verbatim, at their own limits
        ok, why = _accepts(tmp_path, block, text, tl, j)
        assert ok, (tl, why)
    p30 = pend.replace("TimeLimit=01:19:00", "TimeLimit=00:30:00")
    r30 = run.replace("TimeLimit=01:00:00", "TimeLimit=00:30:00")
    good = [(p30, PJ), (r30, RJ)]
    bad = [
        (p30.replace("NumNodes=1-1", "NumNodes=2-2"), PJ),
        (p30.replace("NumNodes=1-1", "NumNodes=1-2"), PJ),
        (r30.replace("NumNodes=1 ", "NumNodes=2 "), RJ),
        (r30.replace("NumNodes=1 ", "NumNodes=11 "), RJ),
        (r30.replace(" NumNodes=1 ", " "), RJ),                   # no NumNodes; NodeList and ReqNodeList do not count
        (pend, PJ),                                               # 01:19:00 against the declared 00:30:00
        (p30.replace("JobState=PENDING", "ArrayJobId=60912517 ArrayTaskId=0 JobState=PENDING"), PJ),
        (p30.replace("JobState=PENDING", "ArrayTaskId=0 JobState=PENDING"), PJ),
        (p30, RJ),                                                # another job's record
        (p30 + "\n" + p30, PJ),                                  # two records
        ("", PJ),                                                 # scontrol printed nothing
    ]
    for text, j in good:
        ok, why = _accepts(tmp_path, block, text, "00:30:00", j)
        assert ok, (text[:60], why)
    for text, j in bad:
        ok, why = _cancels(tmp_path, block, text, "00:30:00", j)
        assert ok, (text[:60], why)


def test_connect_scontrol_status_and_release(tmp_path):
    block = _alloc_block(LAUNCH / "evw2d_connect.sh")
    p30 = real_pending().replace("TimeLimit=01:19:00", "TimeLimit=00:30:00")
    ok, why = _cancels(tmp_path, block, p30, "00:30:00", "60912517", show_rc="1")      # plausible text, failed command
    assert ok, why
    ok, why = _accepts(tmp_path, block, p30, "00:30:00", "60912517", show_rc="1 1 0")  # a transient failure, retried
    assert ok, why
    ok, why = _cancels(tmp_path, block, p30, "00:30:00", "60912517", show_rc="1 1 1 0")  # three failures: no fourth try
    assert ok, why
    ok, why = _accepts(tmp_path, block, p30, "00:30:00", "60912517", release_rc="1")   # reply lost, job not held
    assert ok and "the release took effect" in why[1], why
    held = p30.replace("Reason=Priority", "Reason=JobHeldUser")
    rc, out, cancelled, released = _run_alloc(tmp_path, block, held, "00:30:00", "60912517", release_rc="1")
    assert rc == 6 and cancelled and "still held" in out, out
    admin = p30.replace("Priority=67679", "Priority=0").replace("Reason=Priority", "Reason=JobHeldAdmin")
    rc, out, cancelled, released = _run_alloc(tmp_path, block, admin, "00:30:00", "60912517", release_rc="1")
    assert rc == 6 and cancelled and "still held" in out, out
    zero = p30.replace("Priority=67679", "Priority=0")                                 # held, whatever the reason
    rc, out, cancelled, released = _run_alloc(tmp_path, block, zero, "00:30:00", "60912517", release_rc="1")
    assert rc == 6 and cancelled, out
    for later in (p30 + "\n" + p30, p30.replace("JobId=60912517 ", "JobId=60912518 ")):  # two records, another
        rc, out, cancelled, released = _run_alloc(tmp_path, block, p30, "00:30:00", "60912517", release_rc="1",
                                                  later=later)
        assert rc == 6 and cancelled and "still held or unseen" in out, (later[:40], out)
    rc, out, cancelled, released = _run_alloc(tmp_path, block, p30, "00:30:00", "60912517", release_rc="1",
                                              later="")                              # rc 0, no record: not an answer
    assert rc == 4 and not cancelled and "try 3" in out and "see sacct" in out, out
    r30 = real_running().replace("TimeLimit=01:00:00", "TimeLimit=00:30:00")
    sx = p30.replace("JobState=PENDING", "JobState=SPECIAL_EXIT").replace("Reason=Priority", "Reason=JobHeldUser")
    for later in (sx, sx.replace("Reason=JobHeldUser", "Reason=None").replace("Priority=67679", "Priority=0"),
                  r30.replace("Reason=None", "Reason=JobHeldAdmin")):               # requeue-held; any state, held
        rc, out, cancelled, released = _run_alloc(tmp_path, block, p30, "00:30:00", "60912517", release_rc="1",
                                                  later=later.replace("JobId=59660487 ", "JobId=60912517 "))
        assert rc == 6 and cancelled and "still held" in out, (later[:60], out)
    ok, why = _accepts(tmp_path, block, r30, "00:30:00", "59660487", release_rc="1")   # started at once
    assert ok and "the release took effect" in why[1], why
    ok, why = _accepts(tmp_path, block, p30, "00:30:00", "60912517", release_rc="1", show_rc="0 1 1 0")  # retried
    assert ok and "try 3: rc=0" in why[1], why
    rc, out, cancelled, released = _run_alloc(tmp_path, block, p30, "00:30:00", "60912517", release_rc="1",
                                              show_rc="0 1 1 1 0")                   # never answers: kept
    assert rc == 4 and not cancelled and "FINISH 4" in out and "see sacct" in out and "try 4" not in out, out


def test_connect_submits_held_and_saves_the_id_before_the_check():
    text = (LAUNCH / "evw2d_connect.sh").read_text()
    sub = text.index("sbatch --parsable --hold ")
    saved = text.index('echo "$job" > "$L/evw2d.jobid"')
    begin = text.index("# ---- the allocation check (begin)")
    release = text.index('scontrol release "$job"')
    assert sub < saved < begin < release and sum(x.startswith("sbatch ") for x in text.splitlines()) == 1


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
    stub(b, "ssh", f'if [ "$1" = -G ]; then printf "identitiesonly yes\\nidentityfile {tmp / "key"}\\n'
                   f'certificatefile {tmp / "key-cert.pub"}\\n${{SSH_G_EXTRA-}}"; exit 0; fi\n'
                   f'echo "ssh $*" >> "{tmp / "ssh.calls"}"\nlast="${{@: -1}}"\nexec bash -c "${{last//\\/dev\\/shm/{shm}}}"')
    stub(b, "sha256sum", 'shasum -a 256 "$@"')
    stub(b, "ssh-keygen", f'[ "$TZ" = UTC ] || exit 3\n'
                          f'echo "        Type: ssh-rsa-cert-v01@openssh.com user certificate"\n'
                          f'echo "        Valid: from ${{CERT_FROM:-2026-01-01T00:00:00}} to {cert_to}"\n'
                          f'exit ${{KEYGEN_RC:-0}}')   # a failed ssh-keygen with a plausible window still stops
    env = dict(os.environ, PATH=f"{b}:{os.environ['PATH']}", EVW2D_CERT=str(tmp / "key-cert.pub"))
    return ld, shm, env


def _local(seconds: int) -> str:
    """A UTC time `seconds` from now, as `TZ=UTC ssh-keygen -L` prints it."""
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() + seconds))


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
    ld, shm, env = _launcher(tmp, _local(6 * 3600), "#!/bin/bash\necho refused >&2\nexit 9\n")
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


@pytest.mark.skipif(sys.platform != "darwin", reason="the launcher runs on the Mac (BSD date -j)")
@pytest.mark.parametrize("extra", [{"KEYGEN_RC": "1"}, {"CERT_FROM": "2099-01-01T00:00:00"},
                                   {"SSH_G_EXTRA": "identityfile ~/.ssh/id_ed25519\\n"},
                                   {"SSH_G_EXTRA": "certificatefile ~/.ssh/other-cert.pub\\n"}])
def test_launcher_refuses_a_failed_or_future_certificate(tmp_path, extra):
    tmp = Path(os.path.realpath(tmp_path))
    ld, shm, env = _launcher(tmp, _local(6 * 3600))
    sess = tmp / "s1"
    sess.mkdir()
    r = subprocess.run(["bash", str(ld / "evw2d_launch.sh"), "connect", str(sess), "login27"], capture_output=True,
                       text=True, env=dict(env, **extra))
    assert r.returncode == 7 and "STOP" in r.stdout and not (tmp / "ssh.calls").exists(), r.stdout


@pytest.mark.skipif(sys.platform != "darwin", reason="the launcher runs on the Mac (BSD date -j)")
def test_launcher_presents_the_checked_certificate(tmp_path):
    tmp = Path(os.path.realpath(tmp_path))
    ld, shm, env = _launcher(tmp, _local(6 * 3600))
    sess = tmp / "s1"
    sess.mkdir()
    r = subprocess.run(["bash", str(ld / "evw2d_launch.sh"), "connect", str(sess), "login27"], capture_output=True,
                       text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    first = (tmp / "ssh.calls").read_text().splitlines()[0]
    assert f"CertificateFile={tmp / 'key-cert.pub'} " in first and f"IdentityFile={tmp / 'key'} " in first
    assert "IdentitiesOnly=yes" in first and "ControlPath=none" in first


@pytest.mark.skipif(sys.platform != "darwin", reason="the launcher runs on the Mac (BSD date -j)")
def test_launcher_fetch_distinguishes_absent_from_unreachable(tmp_path):
    tmp = Path(os.path.realpath(tmp_path))
    ld, shm, env = _launcher(tmp, _local(6 * 3600))
    remote = tmp / "remote"
    remote.mkdir()
    (remote / "post.tar.gz").write_bytes(b"p")
    b = tmp / "stubbin"
    stub(b, "ssh", f'if [ "$1" = -G ]; then printf "identitiesonly yes\\nidentityfile {tmp / "key"}\\n"; exit 0; fi\n'
                   f'cmd="${{@: -1}}"; [ -n "$SSH_RC" ] && exit "$SSH_RC"\n'
                   f'exec bash -c "${{cmd//\\/pscratch\\/sd\\/j\\/josephrb\\/evw2d-20261126/{remote}}}"')
    stub(b, "scp", f'src="${{@: -2:1}}"; cp "{remote}/${{src##*/}}" "${{@: -1}}"')
    def fetch(**e):
        d = tmp / f"f{len(list(tmp.glob('f*')))}"
        d.mkdir()
        return subprocess.run(["bash", str(ld / "evw2d_launch.sh"), "fetch", str(d)], capture_output=True, text=True,
                              env=dict(env, **e)), d
    r, d = fetch()
    assert r.returncode == 0 and (d / "post.tar.gz").exists() and "cleanup.tar.gz absent" in r.stdout, r.stdout
    (remote / "post.tar.gz").unlink()
    r, d = fetch()
    assert r.returncode == 4 and "post.tar.gz absent" in r.stdout
    r, d = fetch(SSH_RC="255")
    assert r.returncode == 255 and "could not ask saul" in r.stdout


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
    for f in ("evw2d.py", "sbatch_evw2d.sh", "references.npz"):
        (top / "2d-unfolding/evw2d").mkdir(parents=True, exist_ok=True)
        shutil.copy(EV / f, top / "2d-unfolding/evw2d" / f)
    # the reviewed config.json's bytes, from its merge (the working copy is bound from the binding commit on)
    (top / "2d-unfolding/evw2d/config.json").write_bytes(subprocess.run(
        ["git", "-C", str(REPO), "show", "4d9147f9a94c14b0c313f2e611a35e044b327704:2d-unfolding/evw2d/config.json"],
        capture_output=True, check=True).stdout)
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


def test_the_probe_prints_its_own_affinity_line_with_no_startup_hooks():
    """GNU nproc honours OMP_NUM_THREADS, and a startup hook could print to stdout: the affinity line comes whole from
    os.sched_getaffinity in an isolated interpreter with no site import (r1c)."""
    text = JOB.read_text()
    assert text.count('python3 -B -I -S -c "import os; print(\\"affinity=%d\\" % len(os.sched_getaffinity(0)))"') == 1
    assert "nproc" not in text.split("STEP=(", 1)[1].split("refuse", 1)[0]


def test_the_scripts_remove_nothing_and_only_the_launcher_removes_its_staged_copy():
    """The director's condition (2026-11-25): only the two staged input copies are removed, by evw2d.py cleanup's exact
    paths; no script removes products, anything under the output, or anything by glob."""
    import re as _re
    for f in [JOB, *LAUNCH.glob("*.sh")]:
        for n, line in enumerate(f.read_text().splitlines(), 1):
            code = line.split("#", 1)[0] if not line.lstrip().startswith("R=") else line
            for m in _re.finditer(r"\b(rm|rmdir|unlink|shred|find\b.*-delete)\b[^;|&]*", code):
                assert f.name == "evw2d_launch.sh" and m.group(0).strip() == 'rm -f -- \\"\\$f\\"', (f.name, n, m.group(0))
    src = (EV / "evw2d.py").read_text()
    body = src[src.index("def cleanup("):src.index("\n\n\ndef ", src.index("def cleanup("))]
    assert body.count(".unlink(") == 1 and "for key, path in staged(cfg).items():\n                got, size = sizes[key]\n" \
        "                path.unlink()" in body
    assert "rmtree" not in body and "glob" not in body


# ------------------------------------------------------------------------------------------- the post and cleanup

FAKE_EVW2D = '''import json, os, sys
from pathlib import Path


def accepted(out):
    return {"pass": os.environ.get("ACC", "1") == "1"}


if __name__ == "__main__" and "cleanup" in sys.argv:
    out = Path(sys.argv[sys.argv.index("--out") + 1])
    rc = int(os.environ.get("CLEAN_RC", "0"))
    if rc == 0:
        with open(out.parent / "deletions.tsv", "a") as fh:
            fh.write("t\\tstaged\\tdigest\\t1\\treason\\n")
        print(json.dumps({"deleted": 2}))
    sys.exit(rc)
'''


@pytest.fixture()
def lane(tmp_path):
    """A finished lane: logs with the job id, products with their SHA256SUMS, two staged copies, deploy_M (a setup that
    selects a root_6_28 python3) and deploy_C (a stand-in evw2d with accepted() and cleanup), and scheduler stubs."""
    tmp = Path(os.path.realpath(tmp_path))
    L = tmp / "evw2d-20261126"
    (L / "logs").mkdir(parents=True)
    (L / "logs" / "evw2d.jobid").write_text("4242\n")
    (L / "logs" / "connect.log").write_text("connect\n")
    csha = "c" * 64
    out = L / "out"
    out.mkdir()
    for n, b in (("constants.json", b"{}"), ("run.json", json.dumps({"config_sha256": csha, "slurm_job": "4242"}).encode()),
                 ("weights.npz", b"w" * 100), ("xsec.root", b"x"), ("evw2d.done", b"{}")):
        (out / n).write_bytes(b)
    (out / "SHA256SUMS").write_text("".join(f"{sha(out / n)}  {n}\n" for n in
                                            ("constants.json", "run.json", "weights.npz", "xsec.root")))
    (L / "stage").mkdir()
    for n in ("runEventLoopOmniFold_MEFHC.root", "runEventLoopMC_MEFHC.root"):
        (L / "stage" / n).write_bytes(b"s")
    home = tmp / "home"
    py = home / ".conda/envs/root_6_28/bin"
    py.mkdir(parents=True)
    stub(py, "python3", f'exec "{sys.executable}" "$@"')
    git_repo(L / "deploy_M", {"setup_salloc_env.sh": f'export PATH="{py}:$PATH"\nreturn 0\n'})
    git_repo(L / "deploy_C", {"2d-unfolding/evw2d/evw2d.py": FAKE_EVW2D})
    b = tmp / "bin"
    b.mkdir()
    stub(b, "squeue", 'printf "%b" "${SQ_OUT-}"; exit ${SQ_RC:-0}')
    stub(b, "sacct", 'case " $* " in *" -X "*) printf "%s\\n" "${SACCT_ROW-4242|COMPLETED|0:0|1|600}"; exit ${SACCT_RC:-0};; esac\n'
                     'echo "4242|evw2d|COMPLETED|0:0|600|1|s|e|"')
    stub(b, "sha256sum", 'a=(); for x; do [ "$x" = --strict ] || a+=("$x"); done; shasum -a 256 "${a[@]}"')
    stub(b, "stat", '[ -n "$STAT_RC" ] && exit "$STAT_RC"; shift 2; for f; do [ -e "$f" ] || exit 1; echo "$f|1|2|3|4"; done')
    env = dict(os.environ, PATH=f"{b}:{os.environ['PATH']}", HOME=str(home))

    def run(script, **e):
        src = (LAUNCH / script).read_text().replace("__LANE_ROOT__", str(L)).replace("__CONFIG_SHA256__", csha)
        shm = tmp / "dev" / "shm"
        shm.mkdir(parents=True, exist_ok=True)
        f = shm / f"evw2d-{script}.copy"
        f.write_text(src)
        r = subprocess.run(["bash", str(f), str(f)], capture_output=True, text=True, env=dict(env, **e))
        assert f.read_text() == src, "the script changed or removed its /dev/shm copy (the launcher removes it)"
        return r

    def run_direct(script, arg1, **e):   # a mistaken direct run, not through the launcher
        src = (LAUNCH / script).read_text().replace("__LANE_ROOT__", str(L)).replace("__CONFIG_SHA256__", csha)
        f = tmp / f"direct-{script}"
        f.write_text(src)
        return subprocess.run(["bash", str(f), str(arg1)], capture_output=True, text=True, env=dict(env, **e))

    return {"L": L, "run": run, "run_direct": run_direct, "csha": csha, "bin": b}


def test_post_passes_and_publishes_post_pass_last(lane):
    r = lane["run"]("evw2d_post.sh")
    L = lane["L"]
    log = (L / "post" / "post.log").read_text()
    assert r.returncode == 0, log
    assert (L / "post.pass").read_text() == (f"job=4242\nconfig_sha256={lane['csha']}\n"
                                             f"products_SHA256SUMS_sha256={sha(L / 'out' / 'SHA256SUMS')}\n")
    assert (L / "post.tar.gz").exists() and not (L / "post.tar.gz.partial").exists()
    assert "ACCOUNTING_OK=true" in log and "VERIFY=PASS" in log and "ACCEPTED=true" in log
    assert (L / "post" / "charge_node_h.txt").read_text().strip() == "0.1667"


@pytest.mark.parametrize("env,why", [
    ({"SACCT_ROW": ""}, "no single allocation row"),
    ({"SACCT_ROW": "4242|RUNNING|0:0|1|60"}, "'RUNNING' in sacct, not a terminal state"),
    ({"SACCT_ROW": "4242|PENDING|0:0|1|0"}, "'PENDING' in sacct"),
    ({"SACCT_ROW": "4242|COMPLETED|0:0|1|600\n4242|COMPLETED|0:0|1|600"}, "no single allocation row"),
    ({"SACCT_RC": "1"}, "sacct did not answer"),
    ({"SQ_OUT": "17\\n4242\\n"}, "still queued or running"),
    ({"SQ_RC": "1"}, "squeue did not answer"),
])
def test_post_writes_nothing_until_the_job_has_one_terminal_row(lane, env, why):
    r = lane["run"]("evw2d_post.sh", **env)
    assert r.returncode == 9 and why in r.stdout, r.stdout
    assert not (lane["L"] / "post").exists() and not (lane["L"] / "post.pass").exists()


@pytest.mark.parametrize("env", [
    {"SACCT_ROW": "4242|FAILED|1:0|1|600"},
    {"SACCT_ROW": "4242|CANCELLED by 112498|0:0|1|600"},
    {"SACCT_ROW": "4242|TIMEOUT|0:0|1|1800"},
    {"SACCT_ROW": "4242|COMPLETED|0:0|2|600"},
    {"ACC": "0"},
    {"STAT_RC": "1"},
])
def test_post_fails_without_post_pass(lane, env):
    r = lane["run"]("evw2d_post.sh", **env)
    assert r.returncode == 5, (lane["L"] / "post" / "post.log").read_text()
    assert (lane["L"] / "post").is_dir() and not (lane["L"] / "post.pass").exists()


def test_post_fails_on_changed_products_wrong_config_or_a_failed_archive(lane):
    L = lane["L"]
    (L / "out" / "run.json").write_text(json.dumps({"config_sha256": "d" * 64, "slurm_job": "4242"}))
    sums = "".join(f"{sha(L / 'out' / n)}  {n}\n" for n in ("constants.json", "run.json", "weights.npz", "xsec.root"))
    (L / "out" / "SHA256SUMS").write_text(sums)
    r = lane["run"]("evw2d_post.sh")
    assert r.returncode == 5 and not (L / "post.pass").exists()            # run.json bound to another config
    shutil.rmtree(L / "post")
    (L / "post.tar.gz").unlink()
    (L / "out" / "run.json").write_text(json.dumps({"config_sha256": lane["csha"], "slurm_job": "4242", "x": 1}))
    r = lane["run"]("evw2d_post.sh")
    assert r.returncode == 5 and "VERIFY=FAIL" in (L / "post" / "post.log").read_text()
    shutil.rmtree(L / "post")
    (L / "post.tar.gz").unlink()
    sums = "".join(f"{sha(L / 'out' / n)}  {n}\n" for n in ("constants.json", "run.json", "weights.npz", "xsec.root"))
    (L / "out" / "SHA256SUMS").write_text(sums)
    stub(lane["bin"], "tar", "exit 1")
    r = lane["run"]("evw2d_post.sh")
    assert r.returncode == 5 and not (L / "post.pass").exists() and not (L / "post.tar.gz").exists()


def test_cleanup_needs_a_matching_post_pass(lane):
    L = lane["L"]
    r = lane["run"]("evw2d_cleanup.sh")
    assert r.returncode == 9 and "no post.pass" in r.stdout and not (L / "cleanup").exists()
    assert lane["run"]("evw2d_post.sh", ACC="0").returncode == 5          # a failed post
    r = lane["run"]("evw2d_cleanup.sh")
    assert r.returncode == 9 and "no post.pass" in r.stdout and not (L / "deletions.tsv").exists()
    shutil.rmtree(L / "post")
    (L / "post.tar.gz").unlink()
    assert lane["run"]("evw2d_post.sh").returncode == 0
    (L / "out" / "SHA256SUMS").write_text((L / "out" / "SHA256SUMS").read_text() + "\n")   # products changed since
    r = lane["run"]("evw2d_cleanup.sh")
    assert r.returncode == 9 and "does not name this job" in r.stdout and not (L / "deletions.tsv").exists()


def test_cleanup_runs_evw2d_cleanup_and_keeps_its_receipts(lane):
    L = lane["L"]
    assert lane["run"]("evw2d_post.sh").returncode == 0
    r = lane["run"]("evw2d_cleanup.sh")
    assert r.returncode == 0, (L / "cleanup" / "cleanup.log").read_text()
    assert (L / "cleanup" / "deletions.tsv").exists() and (L / "cleanup.tar.gz").exists()
    assert sorted(p.name for p in (L / "out").iterdir()) == ["SHA256SUMS", "constants.json", "evw2d.done", "run.json",
                                                             "weights.npz", "xsec.root"], "a product was touched"
    shutil.rmtree(L / "cleanup")
    (L / "cleanup.tar.gz").unlink()
    r = lane["run"]("evw2d_cleanup.sh", CLEAN_RC="4")
    assert r.returncode == 4 and (L / "cleanup.tar.gz").exists()


def test_post_needs_run_json_to_name_this_job(lane):
    L = lane["L"]
    (L / "out" / "run.json").write_text(json.dumps({"config_sha256": lane["csha"], "slurm_job": "999"}))
    (L / "out" / "SHA256SUMS").write_text("".join(f"{sha(L / 'out' / n)}  {n}\n" for n in
                                                  ("constants.json", "run.json", "weights.npz", "xsec.root")))
    r = lane["run"]("evw2d_post.sh")
    assert r.returncode == 5 and not (L / "post.pass").exists()
    assert json.loads((L / "post" / "accepted.json").read_text())["job_bound"] is False


def test_cleanup_refuses_a_linked_staging_directory_or_staged_link(lane):
    L = lane["L"]
    assert lane["run"]("evw2d_post.sh").returncode == 0
    (L / "stage").rename(L / "elsewhere")
    (L / "stage").symlink_to(L / "elsewhere")
    r = lane["run"]("evw2d_cleanup.sh")
    assert r.returncode == 9 and "not the real staging directory" in r.stdout and not (L / "deletions.tsv").exists()
    (L / "stage").unlink()
    (L / "elsewhere").rename(L / "stage")
    (L / "stage" / "runEventLoopMC_MEFHC.root").unlink()
    (L / "stage" / "runEventLoopMC_MEFHC.root").symlink_to(L / "stage" / "runEventLoopOmniFold_MEFHC.root")
    r = lane["run"]("evw2d_cleanup.sh")
    assert r.returncode == 9 and "not a regular file" in r.stdout and not (L / "deletions.tsv").exists()


@pytest.mark.parametrize("script", ["evw2d_post.sh", "evw2d_cleanup.sh", "evw2d_connect.sh"])
def test_a_mistaken_direct_run_never_removes_its_argument(lane, script):
    victim = lane["L"] / "out" / "run.json"
    before = victim.read_bytes()
    r = lane["run_direct"](script, victim)
    assert victim.read_bytes() == before, r.stdout
