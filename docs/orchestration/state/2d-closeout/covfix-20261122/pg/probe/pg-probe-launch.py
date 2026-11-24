"""pg-probe-launch.py <sha256 of pg-probe.py> -- run PG's probe once on a Perlmutter login node, from this laptop.

Run as `python3 -I -S -B pg-probe-launch.py <sha256>`, only on the director's GO for this exact launcher and probe.
- It reads pg-probe.py once, hashes those bytes, and sends exactly those bytes on ssh's stdin.
- It reserves pg-probe.out exclusively (O_CREAT | O_EXCL | O_NOFOLLOW), so an existing file or link refuses.
- ssh runs with no user configuration (-F /dev/null) and the options in SSH_OPTS: the NERSC key and its sshproxy
  certificate, strict host-key checking against ~/.ssh/known_hosts, and no agent, X11 or port forwarding, no
  control socket and no local command.
- The remote command is `env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -`. The probe checks the
  node's identity before it reads anything.
- Every write is checked. The receipt is valid only with exactly one `PG-PROBE-RESULT <json>` line, last, whose
  verdict matches the exit code (GO with 0, STOP with 3).
- A failed or invalid attempt keeps its output file as the failure receipt. Rerunning one is the director's call.
Exit: the probe's rc when the receipt is valid; 4 for an invalid receipt; 5 for a refusal before ssh.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.join(HERE, "pg-probe.py")
OUT = os.path.join(HERE, "pg-probe.out")
HOME = os.path.expanduser("~")
HOST = "saul.nersc.gov"
SSH = "/usr/bin/ssh"
SSH_OPTS = ["-F", "/dev/null", "-o", "BatchMode=yes", "-o", "User=josephrb", "-o", "IdentitiesOnly=yes",
            "-o", f"IdentityFile={HOME}/.ssh/nersc", "-o", f"CertificateFile={HOME}/.ssh/nersc-cert.pub",
            "-o", "StrictHostKeyChecking=yes", "-o", f"UserKnownHostsFile={HOME}/.ssh/known_hosts",
            "-o", "ForwardAgent=no", "-o", "ForwardX11=no", "-o", "ClearAllForwardings=yes",
            "-o", "PermitLocalCommand=no", "-o", "ControlMaster=no", "-o", "ControlPath=none",
            "-o", "ConnectTimeout=30"]
REMOTE = "env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -"
RC_FOR = {"GO": 0, "STOP": 3}


def write_all(fd, data):
    view = memoryview(data)
    while view:
        n = os.write(fd, view)
        if n <= 0:
            raise OSError("short write")
        view = view[n:]


def validate(text, rc):
    """(valid, reason): exactly one result line, the last non-empty one, parseable, verdict matching rc."""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    hits = [ln for ln in lines if ln.startswith("PG-PROBE-RESULT ")]
    if len(hits) != 1 or not lines or lines[-1] != hits[0]:
        return False, f"{len(hits)} result lines, or not last"
    try:
        rec = json.loads(hits[0].split(" ", 1)[1])
    except ValueError:
        return False, "the result is not JSON"
    v = rec.get("verdict") if isinstance(rec, dict) else None
    if v not in RC_FOR or RC_FOR[v] != rc:
        return False, f"verdict {v!r} does not match rc {rc}"
    return True, f"verdict {v}"


def main(argv=None, ssh=SSH, probe_path=PROBE, out_path=OUT):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: pg-probe-launch.py <sha256 of pg-probe.py>", file=sys.stderr)
        return 5
    with open(probe_path, "rb") as f:
        body = f.read()
    got = hashlib.sha256(body).hexdigest()
    if got != argv[0]:
        print(f"STOP: pg-probe.py is {got}, not {argv[0]}", file=sys.stderr)
        return 5
    try:
        fd = os.open(out_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    except OSError as e:
        print(f"STOP: cannot reserve {out_path}: {e.strerror}", file=sys.stderr)
        return 5
    try:
        write_all(fd, f"# pg-probe.py sha256 {got}\n# ssh {' '.join(SSH_OPTS)} {HOST} {REMOTE!r}\n".encode())
        env = {"PATH": "/usr/bin:/bin", "HOME": HOME, "LC_ALL": "C"}
        p = subprocess.run([ssh] + SSH_OPTS + [HOST, REMOTE], input=body, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, env=env)
        write_all(fd, p.stdout)
        text = p.stdout.decode(errors="replace")
        ok, why = validate(text, p.returncode)
        write_all(fd, f"\n# rc {p.returncode}; receipt {'valid' if ok else 'INVALID'}: {why}\n".encode())
        os.fsync(fd)
    finally:
        os.close(fd)
    print(f"probe rc={p.returncode}; receipt {'valid' if ok else 'INVALID'} ({why}); "
          f"{hashlib.sha256(open(out_path, 'rb').read()).hexdigest()}  {out_path}")
    return p.returncode if ok else 4


if __name__ == "__main__":
    raise SystemExit(main())
