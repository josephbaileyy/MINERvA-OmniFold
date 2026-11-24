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
  record is complete for its verdict (receipt_problems) and whose verdict matches the exit code (GO 0, STOP 3).
  A GO needs the identity, the verified roots, all five tunes' catalog and classes, the four passing controls, both
  chosen slots eligible and present with their digests, the fallback consistent with 02b's status, every gpg check
  passed, and no stops. A STOP needs at least one stop.
- The footer's sha256 is computed by reading the reserved file back through its own descriptor.
- A failed or invalid attempt keeps its output file as the failure receipt. Rerunning one is the director's call.
Exit: the probe's rc when the receipt is valid; 4 for an invalid receipt; 5 for a refusal before ssh.
"""
import hashlib
import json
import os
import re
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
SCHEMA = "covfix-pg-probe/3"
SPENT = ("G18_10a_02_11b", "AR23_20i_00_000")
U0, U1, U1_FALLBACK = "G21_11b_00_000", "G18_02b_02_11b", "G18_02a_02_11b"
TUNES = SPENT + (U0, U1, U1_FALLBACK)
GPG_REQUIRED = [(("pass",), True), (("confined",), True), (("round_trip_equal",), True), (("decrypt_rc",), 0),
                (("packet_tags",), [3, 18]), (("tampered", "rc"), 2), (("tampered", "evidence"), True),
                (("wrong_passphrase", "rc"), 2), (("wrong_passphrase", "evidence"), True),
                (("gnupghome_mode",), "0o700"), (("gpgconf_kill_rc",), 0), (("agent_gone",), True),
                (("socketdir_absent",), True), (("gnupghome_removed",), True)]


def write_all(fd, data):
    view = memoryview(data)
    while view:
        n = os.write(fd, view)
        if n <= 0:
            raise OSError("short write")
        view = view[n:]


def _get(x, *keys):
    for k in keys:
        x = x.get(k) if isinstance(x, dict) else None
    return x


def _is(got, want):
    return type(got) is type(want) and got == want


def _hex64(x):
    return isinstance(x, str) and re.fullmatch(r"[0-9a-f]{64}", x) is not None


def receipt_problems(rec, rc):
    """What the record lacks for its verdict and rc: [] for a complete receipt."""
    if not isinstance(rec, dict):
        return ["the result is not an object"]
    p, v, stops = [], rec.get("verdict"), rec.get("stops")
    if not _is(rec.get("schema"), SCHEMA):
        p.append(f"schema {rec.get('schema')!r}")
    if v not in RC_FOR or RC_FOR[v] != rc:
        p.append(f"verdict {v!r} does not match rc {rc}")
    if not isinstance(stops, list) or not all(isinstance(s, str) for s in stops):
        return p + ["no list of stops"]
    if not isinstance(rec.get("identity"), dict):
        p.append("no identity")
    if v == "STOP":
        return p + ([] if stops else ["a STOP with no stops"])
    if v != "GO":
        return p
    if stops:
        p.append("a GO with stops")
    if not _is(_get(rec, "identity", "pass"), True):
        p.append("identity not passed")
    if not _is(_get(rec, "roots_verified", "pass"), True):
        p.append("roots not verified")
    for keys, want in GPG_REQUIRED:
        if not _is(_get(rec, "gpg", *keys), want):
            p.append(f"gpg {'.'.join(keys)} is not {want!r}")
    cat, cls, d = rec.get("catalog"), rec.get("classes"), rec.get("decision")
    if not isinstance(cat, dict) or sorted(cat) != sorted(TUNES) or not isinstance(cls, dict) \
            or sorted(cls) != sorted(TUNES) or not isinstance(d, dict):
        return p + ["catalog, classes or decision incomplete"]
    if not _is(d.get("stops"), []):
        p.append("decision stops")
    ctl = d.get("controls")
    if not isinstance(ctl, dict) or len(ctl) != 4 or not all(_is(x, True) for x in ctl.values()):
        p.append("controls")
    u0, u1, fb = _get(d, "chosen", "u0"), _get(d, "chosen", "u1"), d.get("fallback_taken")
    if u0 != U0 or u1 not in (U1, U1_FALLBACK):
        return p + [f"chosen {u0!r}, {u1!r}"]
    if not _is(fb, u1 == U1_FALLBACK) or _get(cat, U1, "status") != ("absent" if fb else "present"):
        p.append("fallback inconsistent with 02b's catalog")
    for t in (u0, u1):
        if _get(d, "eligibility", t) != "eligible":
            p.append(f"{t} not eligible")
        c, m = cat[t], cls[t]
        if not isinstance(c, dict) or c.get("status") != "present" or not _hex64(c.get("spline_sha256")) \
                or not _hex64(c.get("readme_sha256")) or not isinstance(c.get("readme_version"), str):
            p.append(f"{t} catalog evidence")
        if not isinstance(m, dict) or m.get("problems") != [] or not isinstance(m.get("ccqe"), str) \
                or not isinstance(m.get("2p2h"), str) or not isinstance(m.get("sources"), dict):
            p.append(f"{t} class evidence")
    return p


def validate(text, rc):
    """(valid, reason): exactly one result line, the last non-empty one, parseable, complete, verdict matching rc."""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    hits = [ln for ln in lines if ln.startswith("PG-PROBE-RESULT ")]
    if len(hits) != 1 or not lines or lines[-1] != hits[0]:
        return False, f"{len(hits)} result lines, or not last"
    try:
        rec = json.loads(hits[0].split(" ", 1)[1])
    except ValueError:
        return False, "the result is not JSON"
    probs = receipt_problems(rec, rc)
    if probs:
        return False, "; ".join(probs)
    return True, f"verdict {rec['verdict']}"


def _sha_through(fd):
    os.lseek(fd, 0, os.SEEK_SET)
    h = hashlib.sha256()
    for b in iter(lambda: os.read(fd, 1 << 20), b""):
        h.update(b)
    return h.hexdigest()


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
        fd = os.open(out_path, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
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
        digest = _sha_through(fd)
    finally:
        os.close(fd)
    print(f"probe rc={p.returncode}; receipt {'valid' if ok else 'INVALID'} ({why}); {digest}  {out_path}")
    return p.returncode if ok else 4


if __name__ == "__main__":
    raise SystemExit(main())
