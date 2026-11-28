"""tools/p0_supervise.py with real processes and signals, run locally (no cluster).

usage: python3 -I -B -m pytest -q -p no:cacheprovider tests/test_p0_supervise.py

TERM_LEAD is shortened through a wrapper module so the deadline cases take seconds, not minutes; the supervisor's code is
otherwise run unchanged, in its own process, as the runner runs it.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parent.parent / "tools" / "p0_supervise.py"
LEAD = 1.0


def run(
    tmp_path: Path, worker: str, seconds: float, *, lead: float = LEAD, after_start=None
) -> tuple[int, dict, float]:
    """Run the supervisor on `python3 -c WORKER` with a deadline SECONDS ahead; return (exit, result, elapsed)."""
    wrapper = tmp_path / "wrap.py"
    wrapper.write_text(
        "import importlib.util, sys\n"
        f"spec = importlib.util.spec_from_file_location('p0_supervise', {str(TOOL)!r})\n"
        "tool = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(tool)\n"
        f"tool.TERM_LEAD = {lead!r}\n"
        "sys.exit(tool.main([sys.argv[0]] + sys.argv[1:]))\n"
    )
    result = tmp_path / "sup.json"
    deadline = time.monotonic() + seconds
    t0 = time.monotonic()
    proc = subprocess.Popen(
        [
            sys.executable,
            "-I",
            "-B",
            str(wrapper),
            repr(deadline),
            str(result),
            "--",
            sys.executable,
            "-I",
            "-c",
            worker,
        ]
    )
    if after_start is not None:
        after_start(proc, tmp_path)
    code = proc.wait(timeout=60)
    elapsed = time.monotonic() - t0
    data = json.loads(result.read_text()) if result.exists() else {}
    return code, data, elapsed


def test_clean_exit(tmp_path: Path) -> None:
    code, data, _ = run(tmp_path, "print('ok')", 30)
    assert code == 0
    assert data["rc"] == 0 and data["signal"] is None and not data["deadline_signalled"] and data["forwarded"] is None
    assert not data["leftover_group_killed"] and data["group_gone"] and not data["past_deadline"]
    assert data["peak_rss_bytes"] > 0 and (tmp_path / "sup.json.pgid").read_text().strip() == str(data["pgid"])


def test_nonzero_exit(tmp_path: Path) -> None:
    code, data, _ = run(tmp_path, "import sys; sys.exit(4)", 30)
    assert code == 1 and data["rc"] == 4 and not data["deadline_signalled"]


def test_deadline_term(tmp_path: Path) -> None:
    code, data, elapsed = run(tmp_path, "import time; time.sleep(60)", 3)
    assert code == 1 and data["deadline_signalled"] and data["signal"] == "SIGTERM"
    assert elapsed < 3 - LEAD + 0.5, elapsed  # TERM at deadline - LEAD, within one poll


def test_deadline_kill_when_term_is_ignored(tmp_path: Path) -> None:
    worker = "import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)"
    code, data, elapsed = run(tmp_path, worker, 3)
    assert code == 1 and data["deadline_signalled"] and data["signal"] == "SIGKILL"
    assert 3 - 0.3 <= elapsed < 3 + 0.5, elapsed  # KILL at the deadline itself (the clock is read before each poll)


def test_outside_kill_is_not_a_deadline_kill(tmp_path: Path) -> None:
    worker = "import os, signal, time; time.sleep(0.5); os.kill(os.getpid(), signal.SIGKILL)"
    code, data, _ = run(tmp_path, worker, 30)
    assert code == 1 and data["signal"] == "SIGKILL" and data["rc"] == -9
    assert not data["deadline_signalled"] and data["forwarded"] is None


def test_forwarded_term_reaches_the_group(tmp_path: Path) -> None:
    def send(proc: subprocess.Popen, _tmp: Path) -> None:
        time.sleep(1.0)
        proc.send_signal(signal.SIGTERM)

    code, data, elapsed = run(tmp_path, "import time; time.sleep(60)", 30, after_start=send)
    assert code == 1 and data["forwarded"] == "SIGTERM" and data["signal"] == "SIGTERM"
    assert not data["deadline_signalled"] and elapsed < 5


def test_forwarded_term_escalates_to_kill(tmp_path: Path) -> None:
    def send(proc: subprocess.Popen, _tmp: Path) -> None:
        time.sleep(1.0)
        proc.send_signal(signal.SIGTERM)

    worker = "import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)"
    code, data, elapsed = run(tmp_path, worker, 30, after_start=send)
    assert code == 1 and data["forwarded"] == "SIGTERM" and data["signal"] == "SIGKILL"
    assert elapsed < 1.0 + LEAD + 2


def test_leftover_group_member_is_killed(tmp_path: Path) -> None:
    pidfile = tmp_path / "child.pid"
    worker = (
        "import subprocess, sys; "
        f"p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']); "
        f"open({str(pidfile)!r}, 'w').write(str(p.pid))"
    )
    code, data, _ = run(tmp_path, worker, 30)
    assert code == 1 and data["rc"] == 0 and data["leftover_group_killed"]
    child = int(pidfile.read_text())
    time.sleep(0.3)
    with pytest.raises(ProcessLookupError):
        os.kill(child, 0)  # killed (and reaped by init, having been orphaned)


def test_worker_is_outside_the_supervisor_group(tmp_path: Path) -> None:
    out = tmp_path / "ids.json"
    worker = (
        "import json, os; p = os.getppid(); "
        f"json.dump([os.getpgid(0), os.getsid(0), os.getpgid(p), os.getsid(p), os.getpid()], open({str(out)!r}, 'w'))"
    )
    code, _, _ = run(tmp_path, worker, 30)
    pgid, sid, parent_pgid, parent_sid, pid = json.loads(out.read_text())
    assert code == 0 and pgid == sid == pid  # the worker leads its own session and group
    assert pgid != parent_pgid and sid != parent_sid  # the supervisor is outside both


def test_passed_deadline_starts_nothing(tmp_path: Path) -> None:
    code, data, _ = run(tmp_path, "open('should-not-exist', 'w')", -1)
    assert code == 2 and data == {} and not Path("should-not-exist").exists()


def test_usage(tmp_path: Path) -> None:
    proc = subprocess.run([sys.executable, "-I", "-B", str(TOOL), "1", str(tmp_path / "r.json")], capture_output=True)
    assert proc.returncode == 2 and not (tmp_path / "r.json").exists()


def test_a_worker_reaped_after_the_deadline_is_never_clean(tmp_path: Path) -> None:
    """A controlled clock: no deadline signal is due while the worker runs, but it is reaped after the deadline."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("p0_supervise_clock", TOOL)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    now = [0.0]

    class Clock:
        @staticmethod
        def monotonic() -> float:
            return now[0]

        @staticmethod
        def sleep(seconds: float) -> None:
            time.sleep(min(seconds, 0.01))

    real_reap = tool.reap

    def late_reap(pid: int):  # the worker is reaped only after the deadline
        code = real_reap(pid)
        if code is not None:
            now[0] = 100.0
        return code

    tool.time = Clock
    tool.reap = late_reap
    code = tool.supervise(50.0, str(tmp_path / "sup.json"), [sys.executable, "-I", "-c", "pass"])
    data = json.loads((tmp_path / "sup.json").read_text())
    assert code == 1 and data["rc"] == 0 and not data["deadline_signalled"] and data["past_deadline"]


def test_the_pgid_file_recovers_the_group_if_the_supervisor_is_killed(tmp_path: Path) -> None:
    def kill_supervisor(proc: subprocess.Popen, tmp: Path) -> None:
        for _ in range(50):
            if (tmp / "sup.json.pgid").exists():
                break
            time.sleep(0.05)
        time.sleep(0.2)
        proc.send_signal(signal.SIGKILL)

    code, data, _ = run(tmp_path, "import time; time.sleep(30)", 30, after_start=kill_supervisor)
    assert code == -9 and data == {}  # no record: the runner falls back to the pgid file
    pgid = int((tmp_path / "sup.json.pgid").read_text())
    time.sleep(0.3)
    if sys.platform.startswith("linux"):  # PR_SET_PDEATHSIG: the worker died with its supervisor
        with pytest.raises(ProcessLookupError):
            os.killpg(pgid, 0)
    else:  # elsewhere the worker survives; the runner kills the recorded group
        os.killpg(pgid, signal.SIGKILL)
        time.sleep(0.3)
        with pytest.raises(ProcessLookupError):
            os.killpg(pgid, 0)


def test_a_supervisor_killed_before_publishing_the_pgid_runs_no_worker(tmp_path: Path) -> None:
    """The fork gate: the child execs only after the .pgid file is written; if the supervisor dies first, nothing runs."""
    marker = tmp_path / "worker-ran"
    wrapper = tmp_path / "wrap.py"
    wrapper.write_text(
        "import importlib.util, os, signal, sys\n"
        f"spec = importlib.util.spec_from_file_location('p0_supervise', {str(TOOL)!r})\n"
        "tool = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(tool)\n"
        "real = tool.write_atomic\n"
        "def dying(path, text):\n"
        "    if path.endswith('.pgid'):\n"
        "        os.kill(os.getpid(), signal.SIGKILL)\n"
        "    real(path, text)\n"
        "tool.write_atomic = dying\n"
        "sys.exit(tool.main([sys.argv[0]] + sys.argv[1:]))\n"
    )
    deadline = time.monotonic() + 30
    worker = f"open({str(marker)!r}, 'w').write('ran')"
    proc = subprocess.run(
        [sys.executable, "-I", "-B", str(wrapper), repr(deadline), str(tmp_path / "sup.json"), "--"]
        + [sys.executable, "-I", "-c", worker],
        timeout=30,
    )
    time.sleep(1.0)
    assert proc.returncode == -9 and not marker.exists() and not (tmp_path / "sup.json.pgid").exists()


def load_tool(name: str):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, TOOL)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    return tool


class FakeClock:
    """time.monotonic() from a mutable value; sleep advances it and yields briefly."""

    def __init__(self) -> None:
        self.now = 0.0

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds
        time.sleep(0.001)


def test_the_gate_never_releases_a_worker_into_an_expired_step(tmp_path: Path) -> None:
    tool = load_tool("p0_supervise_gate_clock")
    clock = FakeClock()
    tool.time = clock
    real = tool.write_atomic

    def late_publication(path: str, text: str) -> None:
        real(path, text)
        if path.endswith(".pgid"):
            clock.now = 100.0  # the deadline (50) passes while the pgid is published

    tool.write_atomic = late_publication
    tool.signal_group = lambda _pgid, _sig: "absent"  # no deadline signal: only the gate can stop the worker
    marker = tmp_path / "worker-ran"
    code = tool.supervise(50.0, str(tmp_path / "sup.json"), [sys.executable, "-I", "-c", f"open({str(marker)!r}, 'w')"])
    data = json.loads((tmp_path / "sup.json").read_text())
    time.sleep(0.3)
    assert code == 1 and data["past_deadline"] and data["rc"] == 127 and not marker.exists()


def test_eperm_is_neither_delivery_nor_absence_on_linux(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tool = load_tool("p0_supervise_eperm")
    clock = FakeClock()
    tool.time = clock

    def denied(_pgid: int, _sig: int) -> None:
        raise PermissionError(1, "Operation not permitted")

    monkeypatch.setattr(tool.os, "killpg", denied)
    monkeypatch.setattr(tool.sys, "platform", "linux")
    assert tool.signal_group(4242, 0) == "denied" and tool.group_alive(4242)
    worker = [sys.executable, "-I", "-c", "import time; time.sleep(0.5)"]
    code = tool.supervise(1.0, str(tmp_path / "sup.json"), worker)  # every deadline signal is refused with EPERM
    data = json.loads((tmp_path / "sup.json").read_text())
    assert code == 1 and not data["deadline_signalled"] and data["leftover_group_killed"] and not data["group_gone"]
    monkeypatch.setattr(tool.sys, "platform", "darwin")
    assert not tool.group_alive(4242)  # macOS: EPERM is a zombie-only group


def test_the_child_refuses_a_release_that_arrives_after_the_deadline(tmp_path: Path) -> None:
    """A real clock: the parent's check passes, then a pause before the release byte carries it past the deadline."""
    marker = tmp_path / "worker-ran"
    wrapper = tmp_path / "wrap.py"
    wrapper.write_text(
        "import importlib.util, os, sys, time\n"
        f"spec = importlib.util.spec_from_file_location('p0_supervise', {str(TOOL)!r})\n"
        "tool = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(tool)\n"
        "real_write = os.write\n"
        "def paused(fd, data):\n"
        "    if data == b'g':\n"
        f"        open({str(tmp_path / 'paused')!r}, 'w').close()  # the paused write did run\n"
        "        time.sleep(1.5)  # after the parent's deadline check\n"
        "    return real_write(fd, data)\n"
        "os.write = paused\n"
        "tool.signal_group = lambda _pgid, _sig: 'absent'  # no deadline signal: only the child's check can stop it\n"
        "sys.exit(tool.main([sys.argv[0]] + sys.argv[1:]))\n"
    )
    deadline = time.monotonic() + 1.0
    worker = f"open({str(marker)!r}, 'w').write('ran')"
    proc = subprocess.run(
        [sys.executable, "-I", "-B", str(wrapper), repr(deadline), str(tmp_path / "sup.json"), "--"]
        + [sys.executable, "-I", "-c", worker],
        timeout=30,
    )
    data = json.loads((tmp_path / "sup.json").read_text())
    time.sleep(0.3)
    assert (tmp_path / "paused").exists()  # the release byte was sent: the child's own check refused it
    assert proc.returncode == 1 and data["rc"] == 127 and data["past_deadline"] and not marker.exists()
