#!/usr/bin/env python3
"""Checks L1-L9 of REPAIR.md for the repaired launcher ``code/pilot_run.py``.

Temporary ledgers and lowered caps only; never NuWro, never the campaign ledger
(L8 reads it and verifies it is unchanged). Jobs are ``sleep`` or 1-CPU-second
Python spinners. Every wait has a wall-clock timeout, so a failed bound cannot
spin for long. Writes one JSON document.

Usage: test_pilot_run.py SCRATCH_DIR JSON_OUT
"""

from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CODE = HERE / "code"
PILOT = CODE / "pilot_run.py"
sys.path.insert(0, str(CODE))
import pilot_run as pr  # noqa: E402

PY = sys.executable
SCRATCH = Path(sys.argv[1])
RESERVE = 1 + pr.WATCHDOG_MARGIN_S  # one reservation at --cpu-seconds 1
CAP3 = 3 * RESERVE + 1.0  # admits exactly 3 reservations


def launcher(ledger: Path, run_id: str, cmd: list[str], cpu=1, events=0, cpu_cap=CAP3, event_cap=0,
             extra=()):
    wd = SCRATCH / "work"
    return subprocess.Popen([PY, "-I", str(PILOT), "--ledger", str(ledger), "--run-id", run_id,
                             "--events", str(events), "--cpu-seconds", str(cpu), "--workdir", str(wd),
                             "--log", str(SCRATCH / f"{ledger.stem}-{run_id}.log"),
                             "--cpu-cap", str(cpu_cap), "--event-cap", str(event_cap), *extra, "--", *cmd],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def records(ledger: Path) -> list[dict]:
    return [json.loads(x) for x in ledger.read_text().splitlines() if x.strip()] if ledger.exists() else []


def wait_for(pred, timeout=10.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        if pred():
            return True
        time.sleep(0.05)
    return False


def job_pids(launcher_pid: int, marker: str) -> list[int]:
    """Direct children of the launcher whose command line contains the marker.

    The launcher's own argv contains the marker too, so a bare ``pgrep -f`` would
    match the launcher; the job keeps the launcher's child pid through every exec."""
    out = subprocess.run(["pgrep", "-P", str(launcher_pid), "-f", marker], capture_output=True, text=True).stdout
    return [int(p) for p in out.split()]


def cpu_of(pid: int) -> float | None:
    out = subprocess.run(["ps", "-o", "time=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
    if not out:
        return None
    parts = out.replace("-", ":").split(":")
    secs = 0.0
    for p in parts:
        secs = secs * 60 + float(p)
    return secs


def fresh(name: str) -> Path:
    p = SCRATCH / f"{name}.jsonl"
    for f in (p, Path(f"{p}.lock")):
        if f.exists():
            f.unlink()
    return p


def l1_concurrency() -> dict:
    # (a) end to end: 8 real launchers at once, the cap admits 3 reservations of 2 s
    led = fresh("L1")
    procs = [launcher(led, f"c{i}", ["/bin/sleep", "1"]) for i in range(8)]
    rcs = [p.wait(timeout=30) for p in procs]
    recs = records(led)
    prefix_max, cpu = 0.0, 0.0
    open_res = {}
    for r in recs:  # replay: charged totals after every append
        if r["kind"] == "start":
            continue
        if r["kind"] == "reserve":
            open_res[r["reservation_id"]] = r["cpu_reserved_s"]
        else:
            open_res.pop(r["reservation_id"])
            cpu += r["cpu_charged_s"]
        prefix_max = max(prefix_max, cpu + sum(open_res.values()))
    e2e = {"rcs": rcs, "n_ran": rcs.count(0), "n_refused": rcs.count(3),
           "n_reserve_records": sum(r["kind"] == "reserve" for r in recs), "max_charged_after_any_append": prefix_max}
    # (b) power: reserve() with a 0.3 s delay between reading totals and appending, with and without the lock
    harness = (
        "import sys, time, contextlib; from pathlib import Path\n"
        f"sys.path.insert(0, {str(CODE)!r}); import pilot_run as pr\n"
        "orig = pr.ledger_totals\n"
        "def slow(l):\n    r = orig(l); time.sleep(0.3); return r\n"
        "pr.ledger_totals = slow\n"
        "if sys.argv[2] == 'nolock':\n    pr.locked = lambda l: contextlib.nullcontext()\n"
        "try:\n    pr.reserve(Path(sys.argv[1]), 'x', 2.0, 0, 6.5, 0); print('OK')\n"
        "except PermissionError:\n    print('REFUSED')\n")
    power = {}
    for mode in ("lock", "nolock"):
        led = fresh(f"L1-{mode}")
        ps = [subprocess.Popen([PY, "-I", "-c", harness, str(led), mode], stdout=subprocess.PIPE, text=True)
              for _ in range(8)]
        outs = [p.communicate(timeout=30)[0].strip() for p in ps]
        power[mode] = {"ok": outs.count("OK"), "refused": outs.count("REFUSED"),
                       "charged": pr.ledger_totals(led)[0]}
    passed = (e2e["n_ran"] == 3 and e2e["n_refused"] == 5 and prefix_max <= CAP3
              and power["lock"]["ok"] == 3 and power["nolock"]["ok"] > 3)
    return {"end_to_end": e2e, "lock_power_control": power, "pass": passed}


def l2_crash() -> dict:
    led = fresh("L2")
    cap = 2 * RESERVE - 0.5  # one reservation fits, two do not
    p = launcher(led, "crash", ["/bin/sleep", "2.71"], cpu_cap=cap)
    started = wait_for(lambda: bool(job_pids(p.pid, "sleep 2.71")), 10)
    job = job_pids(p.pid, "sleep 2.71")
    wait_for(lambda: any(r["kind"] == "start" for r in records(led)), 5)
    p.send_signal(signal.SIGKILL)
    p.wait(timeout=10)
    cpu, _, unsettled = pr.ledger_totals(led)
    # (a) while the orphaned job lives, even a request that fits the cap is refused
    qa = launcher(led, "while-alive", ["/bin/sleep", "0.1"], cpu_cap=1e3)
    rc_alive = qa.wait(timeout=20)
    # (b) after it ends, the unsettled reservation still counts in full against the cap
    wait_for(lambda: not job or pr.job_cpu(job[0]) is None, 10)
    qb = launcher(led, "after-exit", ["/bin/sleep", "0.1"], cpu_cap=cap)
    rc_after = qb.wait(timeout=20)
    passed = (started and len(unsettled) == 1 and unsettled[0][1] is not None and cpu == RESERVE
              and rc_alive == 3 and rc_after == 3)
    return {"charged_after_crash": cpu, "unsettled": unsettled, "rc_while_job_alive": rc_alive,
            "stderr_while_alive": qa.stderr.read().strip(), "rc_after_job_exit": rc_after,
            "stderr_after_exit": qb.stderr.read().strip(), "pass": passed}


def l3_interrupt() -> dict:
    led = fresh("L3")
    p = launcher(led, "intr", ["/bin/sleep", "5.31"])
    wait_for(lambda: bool(job_pids(p.pid, "sleep 5.31")), 10)
    job = job_pids(p.pid, "sleep 5.31")
    p.send_signal(signal.SIGTERM)
    rc = p.wait(timeout=20)
    child_gone = bool(job) and wait_for(lambda: pr.job_cpu(job[0]) is None, 5)
    st = [r for r in records(led) if r["kind"] == "settle"]
    passed = (rc == 130 and child_gone and len(st) == 1 and st[0]["basis"] == "full-reservation"
              and st[0]["cpu_charged_s"] == RESERVE)
    return {"rc": rc, "child_killed": child_gone, "settle": st, "pass": passed}


def l4_children() -> dict:
    """Each workload's only evidence of a child is a marker file the child creates."""
    def cases(m: Path) -> dict:
        return {
            "sh_fork": ["/bin/sh", "-c", f"/usr/bin/touch {m}; /usr/bin/true"],
            "bash_background": ["/bin/bash", "-c", f"/usr/bin/touch {m} & wait"],
            "python_subprocess": [PY, "-I", "-c", f"import subprocess; subprocess.run(['/usr/bin/touch', {str(m)!r}])"],
            "python_posix_spawn": [PY, "-I", "-c", f"import os; pid = os.posix_spawn('/usr/bin/touch', ['touch', {str(m)!r}], {{}}); os.waitpid(pid, 0)"],
            "python_fork": [PY, "-I", "-c", f"import os\npid = os.fork()\nif pid == 0:\n    open({str(m)!r}, 'w').close(); os._exit(0)\nos.waitpid(pid, 0)"],
        }
    out, passed = {}, True
    for name in cases(Path("x")):
        mark = SCRATCH / f"L4-{name}.marker"
        mark.unlink(missing_ok=True)
        led = fresh(f"L4-{name}")
        p = launcher(led, name, cases(mark)[name])
        rc = p.wait(timeout=30)
        log = (SCRATCH / f"{led.stem}-{name}.log").read_text()
        st = [r for r in records(led) if r["kind"] == "settle"]
        ok = not mark.exists() and len(st) == 1 and st[0]["cpu_charged_s"] <= RESERVE
        out[name] = {"rc": rc, "child_ran": mark.exists(), "cpu_charged_s": st[0]["cpu_charged_s"] if st else None,
                     "log_tail": log.strip().splitlines()[-1:] if log.strip() else [], "pass": ok}
        passed &= ok
    # positive control: the same workloads create their marker outside the sandbox
    ctl = {}
    for name in cases(Path("x")):
        mark = SCRATCH / f"L4-ctl-{name}.marker"
        mark.unlink(missing_ok=True)
        subprocess.run(cases(mark)[name], capture_output=True, timeout=30)
        ctl[name] = mark.exists()
    out["control_outside_sandbox_child_ran"] = ctl
    out["pass"] = passed and all(ctl.values())
    return out


def l5_spinners() -> dict:
    cases = {"spin": "while True: pass",
             "spin_ignoring_SIGXCPU": "import signal\nsignal.signal(signal.SIGXCPU, signal.SIG_IGN)\nwhile True: pass"}
    out, passed = {}, True
    for name, code in cases.items():
        led = fresh(f"L5-{name}")
        p = launcher(led, name, [PY, "-I", "-c", code])
        try:
            rc = p.wait(timeout=15)
            timed_out = False
        except subprocess.TimeoutExpired:  # bound failed; stop the test's own cost
            timed_out = True
            for pid in job_pids(p.pid, "while True"):
                os.kill(pid, signal.SIGKILL)
            rc = p.wait(timeout=10)
        st = [r for r in records(led) if r["kind"] == "settle"]
        cpu = st[0]["cpu_charged_s"] if st else None
        ok = (not timed_out) and cpu is not None and cpu <= RESERVE
        out[name] = {"rc": rc, "timed_out": timed_out, "cpu_measured_s": cpu, "status": st[0]["status"] if st else None,
                     "overshoot_over_ulimit_s": None if cpu is None else round(cpu - 1, 3), "pass": ok}
        passed &= ok
    out["pass"] = passed
    return out


def l6_fail_closed() -> dict:
    bad = {"truncated": '{"kind": "reserve", "reservation_id": "a", "cpu_res',
           "unknown_kind": json.dumps({"kind": "release", "reservation_id": "a"}),
           "orphan_settle": json.dumps({"kind": "settle", "reservation_id": "zz", "cpu_charged_s": 0, "events_charged": 0}),
           "duplicate_reserve": "\n".join([json.dumps({"kind": "reserve", "reservation_id": "a", "run_id": "x",
                                                       "cpu_reserved_s": 0.1, "events_reserved": 0})] * 2)}
    out, passed = {}, True
    for name, text in bad.items():
        led = fresh(f"L6-{name}")
        led.write_text(text + "\n")
        before = led.read_bytes()
        p = launcher(led, name, ["/bin/sleep", "0.1"], cpu_cap=1e3)
        rc = p.wait(timeout=20)
        ok = rc == 3 and led.read_bytes() == before
        out[name] = {"rc": rc, "ledger_unchanged": led.read_bytes() == before, "stderr": p.stderr.read().strip(), "pass": ok}
        passed &= ok
    out["pass"] = passed
    return out


def l7_caps_only_lower() -> dict:
    led = fresh("L7-cpu")
    led.write_text(json.dumps({"run_id": "legacy", "cpu_charged_s": pr.CPU_CAP_S - 0.5, "events_charged": 0}) + "\n")
    rc_cpu = launcher(led, "raise", ["/bin/sleep", "0.1"], cpu_cap=1e9, event_cap=10 ** 9).wait(timeout=20)
    led2 = fresh("L7-ev")
    led2.write_text(json.dumps({"run_id": "legacy", "cpu_charged_s": 0, "events_charged": pr.EVENT_CAP - 1}) + "\n")
    rc_ev = launcher(led2, "raise", ["/bin/sleep", "0.1"], events=2, cpu_cap=1e9, event_cap=10 ** 9).wait(timeout=20)
    return {"rc_cpu": rc_cpu, "rc_events": rc_ev, "pass": rc_cpu == 3 and rc_ev == 3}


def l8_legacy() -> dict:
    led = HERE / "logs/budget_ledger.jsonl"
    h0 = hashlib.sha256(led.read_bytes()).hexdigest()
    cpu, ev, unsettled = pr.ledger_totals(led)
    rows = [json.loads(x) for x in led.read_text().splitlines() if x.strip()]
    h1 = hashlib.sha256(led.read_bytes()).hexdigest()
    ok = (abs(cpu - sum(r["cpu_charged_s"] for r in rows)) < 1e-9 and ev == sum(r["events_charged"] for r in rows)
          and not unsettled and h0 == h1 and not Path(f"{led}.lock").exists())
    return {"cpu_s": cpu, "events": ev, "sha256": h0, "unchanged": h0 == h1, "pass": ok}


def _orphan(name: str, code: str, timeout: float) -> dict:
    led = fresh(name)
    p = launcher(led, name, [PY, "-I", "-c", code])
    started = wait_for(lambda: bool(job_pids(p.pid, name)), 10)
    job = job_pids(p.pid, name)
    wait_for(lambda: any(r["kind"] == "start" for r in records(led)), 5)
    p.send_signal(signal.SIGKILL)
    p.wait(timeout=10)
    last, t0 = None, time.monotonic()
    refused_while_alive = None
    while job and time.monotonic() - t0 < timeout:
        c = pr.job_cpu(job[0])
        if c is None:
            break
        last = c
        if refused_while_alive is None and c > 0.2:
            q = launcher(led, "next", ["/bin/sleep", "0.1"], cpu_cap=1e3)
            refused_while_alive = q.wait(timeout=20) == 3
        time.sleep(0.05)
    alive = bool(job) and pr.job_cpu(job[0]) is not None
    if alive:  # not bounded: stop the test's own cost
        os.kill(job[0], signal.SIGKILL)
    _, _, unsettled = pr.ledger_totals(led)
    return {"orphan_started": started, "still_running_at_timeout": alive, "timeout_s": timeout,
            "last_observed_cpu_s": last, "next_launch_refused_while_alive": refused_while_alive,
            "reservation_unsettled": len(unsettled) == 1}


def l9_orphan() -> dict:
    """Default SIGXCPU action: the kernel RLIMIT stops the orphan (layer 2)."""
    r = _orphan("L9orphan", "while True: pass  # L9orphan", 10)
    r["pass"] = (r["orphan_started"] and not r["still_running_at_timeout"] and r["reservation_unsettled"]
                 and r["last_observed_cpu_s"] is not None and r["last_observed_cpu_s"] <= RESERVE
                 and r["next_launch_refused_while_alive"] is True)
    return r


def l9b_orphan_ignoring_sigxcpu() -> dict:
    """Residual (added after the freeze): an orphan that ignores SIGXCPU is NOT bounded by
    the kernel. Passes when new launches are refused while it lives; records whether it ran on."""
    r = _orphan("L9borphan", "import signal\nsignal.signal(signal.SIGXCPU, signal.SIG_IGN)\n"
                "while True: pass  # L9borphan", 3)
    r["residual_confirmed_unbounded"] = r["still_running_at_timeout"]
    r["pass"] = r["orphan_started"] and r["next_launch_refused_while_alive"] is True and r["reservation_unsettled"]
    return r


def l10_review_fixes() -> dict:
    """Added in the correction pass: liveness fails closed, and the job does not inherit the
    launcher's temporarily blocked signals; a normal job still settles as completed."""
    dead = pr.job_alive(99999999, "x") is False if not _pid_exists(99999999) else None
    other = pr.job_alive(os.getpid(), "not-my-start-time") is False
    orig = pr._ps
    pr._ps = lambda pid, field: ""  # ps prints nothing for a live process
    try:
        unknown = pr.job_alive(os.getpid(), "whatever") is True
    finally:
        pr._ps = orig
    led = fresh("L10")
    p = launcher(led, "mask", [PY, "-I", "-c",
                               "import signal; print('MASK', sorted(int(x) for x in signal.pthread_sigmask(signal.SIG_BLOCK, [])))"])
    p.wait(timeout=20)
    log = (SCRATCH / f"{led.stem}-mask.log").read_text()
    mask_empty = "MASK []" in log
    led2 = fresh("L10b")
    q = launcher(led2, "normal", ["/bin/sleep", "0.1"])
    q.wait(timeout=20)
    st = [r for r in records(led2) if r["kind"] == "settle"]
    ok = dead is not False and other and unknown and mask_empty and st and st[0]["status"] == "completed"
    return {"nonexistent_pid_dead": dead, "pid_reuse_dead": other, "ps_silent_means_alive": unknown,
            "job_signal_mask_empty": mask_empty, "mask_log": log.strip(), "pass": bool(ok)}


def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except (PermissionError, OverflowError):
        return True
    return True


def main() -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    preflight = pr.fork_denied_preflight()
    res = {"platform": sys.platform, "fork_denied_preflight": preflight, "reserve_per_run_s": RESERVE}
    for name, fn in (("L1", l1_concurrency), ("L2", l2_crash), ("L3", l3_interrupt), ("L4", l4_children),
                     ("L5", l5_spinners), ("L6", l6_fail_closed), ("L7", l7_caps_only_lower), ("L8", l8_legacy),
                     ("L9", l9_orphan), ("L9b", l9b_orphan_ignoring_sigxcpu),
                     ("L10", l10_review_fixes)):
        try:
            res[name] = fn()
        except Exception as exc:  # a crashed check is a failed check
            res[name] = {"error": repr(exc), "pass": False}
        print(name, "PASS" if res[name]["pass"] else "FAIL", flush=True)
    res["all_pass"] = all(res[k]["pass"] for k in [f"L{i}" for i in range(1, 10)] + ["L9b", "L10"])
    Path(sys.argv[2]).write_text(json.dumps(res, indent=1, default=str) + "\n")
    return 0 if res["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
