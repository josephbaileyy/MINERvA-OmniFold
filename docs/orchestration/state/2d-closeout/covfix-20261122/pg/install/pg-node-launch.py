"""pg-node-launch.py <script> <sha256 of script> -- run one of PG's reviewed node scripts once on a Perlmutter login
node, from this laptop: B2 (pg-install-g2111a.py) or B3 (pg-replay-g2111a.py).

Run as `python3 -I -S -B pg-node-launch.py <script> <sha256>`, only on the director's GO for this exact launcher and
script. The rules are pg-probe-launch.py's:
- the script is read once, hashed, and exactly those bytes are sent on ssh's stdin;
- <script>.out beside it is reserved exclusively (O_CREAT | O_EXCL | O_NOFOLLOW);
- ssh runs with no user configuration and pg-probe-launch.py's SSH_OPTS and REMOTE (a test keeps them equal);
- the receipt is valid only with exactly one `PG-RESULT <json>` line, last, whose schema is the script's, whose
  verdict matches the exit code (GO 0, STOP 3), with no stops for a GO and at least one for a STOP;
- the footer's sha256 is read back through the reserved descriptor.
Exit: the script's rc when the receipt is valid; 4 for an invalid receipt; 5 for a refusal before ssh.
"""
import hashlib
import json
import os
import subprocess
import sys

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
SCHEMAS = {"pg-install-g2111a.py": "covfix-pg-install/1", "pg-replay-g2111a.py": "covfix-pg-replay/1"}


def write_all(fd, data):
    view = memoryview(data)
    while view:
        n = os.write(fd, view)
        if n <= 0:
            raise OSError("short write")
        view = view[n:]


def validate(text, rc, schema):
    lines = [ln for ln in text.splitlines() if ln.strip()]
    hits = [ln for ln in lines if ln.startswith("PG-RESULT ")]
    if len(hits) != 1 or not lines or lines[-1] != hits[0]:
        return False, f"{len(hits)} result lines, or not last"
    try:
        rec = json.loads(hits[0].split(" ", 1)[1])
    except ValueError:
        return False, "the result is not JSON"
    if not isinstance(rec, dict) or rec.get("schema") != schema:
        return False, f"schema {rec.get('schema') if isinstance(rec, dict) else None!r}, not {schema}"
    v, stops = rec.get("verdict"), rec.get("stops")
    if v not in RC_FOR or RC_FOR[v] != rc:
        return False, f"verdict {v!r} does not match rc {rc}"
    if not isinstance(stops, list) or (v == "GO") != (not stops):
        return False, "stops inconsistent with the verdict"
    return True, f"verdict {v}"


def main(argv=None, ssh=SSH):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("usage: pg-node-launch.py <script> <sha256 of script>", file=sys.stderr)
        return 5
    script, want = argv
    schema = SCHEMAS.get(os.path.basename(script))
    if schema is None:
        print(f"STOP: {script} is not a reviewed node script", file=sys.stderr)
        return 5
    with open(script, "rb") as f:
        body = f.read()
    got = hashlib.sha256(body).hexdigest()
    if got != want:
        print(f"STOP: {script} is {got}, not {want}", file=sys.stderr)
        return 5
    out = script + ".out"
    try:
        fd = os.open(out, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    except OSError as e:
        print(f"STOP: cannot reserve {out}: {e.strerror}", file=sys.stderr)
        return 5
    try:
        write_all(fd, f"# {os.path.basename(script)} sha256 {got}\n# ssh {' '.join(SSH_OPTS)} {HOST} {REMOTE!r}\n".encode())
        p = subprocess.run([ssh] + SSH_OPTS + [HOST, REMOTE], input=body, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, env={"PATH": "/usr/bin:/bin", "HOME": HOME, "LC_ALL": "C"})
        write_all(fd, p.stdout)
        ok, why = validate(p.stdout.decode(errors="replace"), p.returncode, schema)
        write_all(fd, f"\n# rc {p.returncode}; receipt {'valid' if ok else 'INVALID'}: {why}\n".encode())
        os.fsync(fd)
        os.lseek(fd, 0, os.SEEK_SET)
        h = hashlib.sha256()
        for b in iter(lambda: os.read(fd, 1 << 20), b""):
            h.update(b)
    finally:
        os.close(fd)
    print(f"{os.path.basename(script)} rc={p.returncode}; receipt {'valid' if ok else 'INVALID'} ({why}); "
          f"{h.hexdigest()}  {out}")
    return p.returncode if ok else 4


if __name__ == "__main__":
    raise SystemExit(main())
