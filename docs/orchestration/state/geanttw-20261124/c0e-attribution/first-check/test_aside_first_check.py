"""aside_first_check.sh: it renames the first check's deploy and JSON inside B, or refuses and moves nothing."""
import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / "aside_first_check.sh"
FENCE_REL = "docs/orchestration/state/2d-closeout/cov2d-fence-20261122/cov2d_fence.sh"
ACK = "cov2d-ACK-test-aside-2026-11-26"


class WS:
    def __init__(self, tmp, fence_rc=0):
        self.tmp = tmp
        self.repo = tmp / "repo"
        f = self.repo / FENCE_REL
        f.parent.mkdir(parents=True)
        self.marker = tmp / "fence-ran"
        f.write_text(f"touch {self.marker}\nexit {fence_rc}\n")
        for c in (["init", "-q"], ["add", "-A"],
                  ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "fence"]):
            subprocess.run(["git", "-C", str(self.repo)] + c, check=True)
        self.M = subprocess.run(["git", "-C", str(self.repo), "rev-parse", "HEAD"], capture_output=True, text=True,
                                check=True).stdout.strip()
        self.B = tmp / "B"
        (self.B / "deploy" / ".git").mkdir(parents=True)
        (self.B / "deploy" / ".git" / "geanttw-s0-rehash.txt").write_text("PASS s0 fe0b\n")
        (self.B / "run" / "p0").mkdir(parents=True)
        (self.B / "run" / "p0" / "p0_check.json").write_text('{"verdict": "FAIL"}')

    def run(self, M=None, ack=ACK, test_door=True, ssh="env"):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GEANTTW_")}
        if test_door:
            env.update(GEANTTW_TEST_B=str(self.B), GEANTTW_SSH=ssh, GEANTTW_LOCAL_REPO=str(self.repo))
        elif ssh:
            env["GEANTTW_SSH"] = ssh
        return subprocess.run(["bash", str(SCRIPT), M or self.M, ack], capture_output=True, text=True, env=env)

    def untouched(self):
        return ((self.B / "deploy" / ".git" / "geanttw-s0-rehash.txt").read_text() == "PASS s0 fe0b\n"
                and (self.B / "run" / "p0" / "p0_check.json").exists()
                and not (self.B / "deploy-4fe6add5").exists()
                and not (self.B / "run" / "p0" / "p0_check-4fe6add5.json").exists())


@pytest.fixture
def ws(tmp_path):
    return WS(tmp_path)


def test_renames_both_and_keeps_their_contents(ws):
    p = ws.run()
    assert p.returncode == 0, p.stdout + p.stderr
    assert ws.marker.exists()
    assert (ws.B / "deploy-4fe6add5" / ".git" / "geanttw-s0-rehash.txt").read_text() == "PASS s0 fe0b\n"
    assert (ws.B / "run" / "p0" / "p0_check-4fe6add5.json").read_text() == '{"verdict": "FAIL"}'
    assert not (ws.B / "deploy").exists() and not (ws.B / "run" / "p0" / "p0_check.json").exists()
    assert "fence: clear" in p.stdout and "== geanttw aside rc=0" in p.stdout


def test_fence_failure_stops_before_any_rename(tmp_path):
    w = WS(tmp_path, fence_rc=3)
    p = w.run()
    assert p.returncode == 8 and "STOP: cov2d_fence.sh exited 3" in p.stdout
    assert w.untouched()


@pytest.mark.parametrize("plant", ["deploy-4fe6add5", "run/p0/p0_check-4fe6add5.json"])
def test_an_existing_target_refuses_and_moves_nothing(ws, plant):
    t = ws.B / plant
    t.mkdir() if plant.startswith("deploy") else t.write_text("x")
    p = ws.run()
    assert p.returncode == 8 and f"REFUSED: {t} exists" in p.stdout
    assert (ws.B / "deploy").exists() and (ws.B / "run" / "p0" / "p0_check.json").exists()


@pytest.mark.parametrize("remove", ["deploy", "run/p0/p0_check.json"])
def test_a_missing_source_refuses_and_moves_nothing(ws, remove):
    s = ws.B / remove
    subprocess.run(["rm", "-rf", str(s)], check=True)
    p = ws.run()
    assert p.returncode == 8 and f"REFUSED: {s} is missing" in p.stdout
    assert not (ws.B / "deploy-4fe6add5").exists() and not (ws.B / "run" / "p0" / "p0_check-4fe6add5.json").exists()


@pytest.mark.parametrize("M,ack,msg", [("abc", ACK, "is not a 40-hex commit"),
                                       (None, "short", "a fresh cov2d ack (a token) is required"),
                                       ("0" * 40, ACK, "is not a commit of")])
def test_bad_arguments_refuse_before_any_ssh(ws, M, ack, msg):
    p = ws.run(M=M, ack=ack)
    assert p.returncode == 9 and msg in p.stdout
    assert not ws.marker.exists() and ws.untouched()


def test_ssh_override_outside_the_tests_refuses(ws):
    p = ws.run(test_door=False, ssh="env")
    assert p.returncode == 9 and "GEANTTW_SSH is honoured only by the tests" in p.stdout
    assert not ws.marker.exists() and ws.untouched()


def test_the_real_connection_and_root_are_fixed():
    text = SCRIPT.read_text()
    assert ('SSH="ssh -o ControlMaster=no -o ControlPath=none -o BatchMode=yes -o ProxyJump=none '
            '-o ProxyCommand=none perlmutter.nersc.gov"') in text
    assert "B=/pscratch/sd/j/josephrb/geanttw-20261124\n" in text
    remote = text.split("<<'EOF'", 1)[1].split("\nEOF\n", 1)[0]   # what runs on the login node
    assert "mv -n " in remote
    plain = remote.replace("->", "")   # the messages' arrows are not redirections
    assert all(w not in plain for w in ("rm ", "rmdir", "unlink", ">"))   # it deletes and writes nothing
