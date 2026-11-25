"""pg-node-launch.py <script> <sha256 of script> -- run one of PG's reviewed node scripts once on a Perlmutter login
node, from this laptop: B2 (pg-install-g2111a.py) or B3 (pg-replay-g2111a.py).

Run as `python3 -I -S -B pg-node-launch.py <script> <sha256>`, only on the director's GO for this exact launcher and
script. The rules are pg-probe-launch.py's:
- the script is read once, hashed, and exactly those bytes are sent on ssh's stdin;
- <script>.out beside it is reserved exclusively (O_CREAT | O_EXCL | O_NOFOLLOW);
- ssh runs with no user configuration and pg-probe-launch.py's SSH_OPTS and REMOTE (a test keeps them equal);
- the receipt is valid only with exactly one `PG-RESULT <json>` line, last, whose schema is the script's, whose
  verdict matches the exit code (GO 0, STOP 3), with no stops for a GO and at least one for a STOP;
- and whose payload matches the pins parsed from the sent bytes (payload_problems): B2's root, tarball pin, members
  count and dbconfig pin, and for a GO the hashes and empty problem lists; B3's commit, archive pin and blob count,
  and for a GO the driver's rc 0 and a complete replay record (nine named checks, four spline opens, four real
  shapes, all true) and a deleted-file record;
- the footer's sha256 is read back through the reserved descriptor.
Exit: the script's rc when the receipt is valid; 4 for an invalid receipt; 5 for a refusal before ssh.
"""
import ast
import hashlib
import json
import re
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


REPLAY_CHECKS = ("tool_check_strace.json", "revision_start.json", "members_check.json", "dbconfig_check.json",
                 "exe_check.json", "reduce_check.json", "argv_check.json", "trace_check_reduce.json",
                 "trace_check_graphs.json", "messenger_check.json", "trace_check_coverage.json", "coverage_check.json",
                 "trace_check_gevgen.json", "trace_check_gntpc.json", "trace_check_reduce_slot2.json",
                 "reduce_check_slot2.json", "trace_check_coverage_slot2.json", "coverage_check_slot2.json",
                 "shape_check.json", "host_check.json", "revision_end.json", "revision_compare.json")
TRACES = tuple(n for n in REPLAY_CHECKS if n.startswith("trace_check"))
SPLINE_TRACES = tuple(n for n in TRACES if n != "trace_check_gntpc.json")
SHAPES = ("real_members_listing", "proc_fd_magic_link", "directory_open_recorded", "slot2_reduce_real_path")
HOST_CHECKS = ("st_dev_final_dir", "no_submounts", "result_anchor_real_strace")
# C18: the replay's identity, and what each trace must show: the role's own program first, and these files gated
IDENTITY = {"schema": "covfix-pg-replay-run/3", "tune": "G21_11a_00_000", "slot2": "G18_02a_00_000", "seed": 123456789,
            "events": 100}
PROGRAM = {"trace_check_reduce.json": "awk", "trace_check_reduce_slot2.json": "awk", "trace_check_graphs.json": "gspl2root",
           "trace_check_coverage.json": "gevgen", "trace_check_coverage_slot2.json": "gevgen",
           "trace_check_gevgen.json": "gevgen", "trace_check_gntpc.json": "gntpc"}
GATED = {"trace_check_reduce.json": ("gxspl-NUsmall.xml",), "trace_check_reduce_slot2.json": ("gxspl-NUsmall.xml",),
         "trace_check_graphs.json": ("G21_11a_00_000_CH.xml.gz", "ModelConfiguration.xml"),
         "trace_check_coverage.json": ("G21_11a_00_000_CH.xml.gz", "ModelConfiguration.xml", "Messenger_pg.xml"),
         "trace_check_coverage_slot2.json": ("G18_02a_00_000_CH.xml.gz", "ModelConfiguration.xml", "Messenger_pg.xml"),
         "trace_check_gevgen.json": ("G21_11a_00_000_CH.xml.gz", "ModelConfiguration.xml"), "trace_check_gntpc.json": ()}
DELETABLE = {"t0": ("genie_v3.gst.root", "gevgen.status", "gntp.ghep.root", "input-flux.root"),
             "coverage_slot1": ("gevgen.log", "gevgen.status", "gntp.ghep.root", "input-flux.root"),
             "coverage_slot2": ("gevgen.log", "gevgen.status", "gntp.ghep.root", "input-flux.root")}


def _hex64(x):
    return type(x) is str and re.fullmatch(r"[0-9a-f]{64}", x) is not None


def _all_true(d, keys):
    return type(d) is dict and sorted(d) == sorted(keys) and all(v is True for v in d.values())


def _replay_problems(r):
    """[problems] with pg_replay.sh's replay.json: every named check, spline open, gated list, real shape and host
    check present, exactly, and true; typed records only."""
    p = []
    if r.get("pass") is not True:
        p.append("pass")
    if not _all_true(r.get("checks"), REPLAY_CHECKS):
        p.append("checks")
    if not _all_true(r.get("spline_opened"), SPLINE_TRACES):
        p.append("spline opens")
    g = r.get("gated")
    if not (type(g) is dict and sorted(g) == sorted(TRACES) and all(
            type(v) is list and v and all(type(x) is dict and type(x.get("path")) is str and _hex64(x.get("sha256"))
                                          and type(x.get("pinned_by")) is str for x in v) for v in g.values())):
        p.append("gated files")
    if not _all_true(r.get("real_shapes"), SHAPES):
        p.append("real shapes")
    if not _all_true(r.get("host"), HOST_CHECKS):
        p.append("host checks")
    c = r.get("coverage_log_sha256")
    if not (type(c) is dict and sorted(c) == ["coverage_check.json", "coverage_check_slot2.json"]
            and all(_hex64(v) for v in c.values())):
        p.append("coverage log hashes")
    p += [f"identity {k}" for k, v in IDENTITY.items() if not (type(r.get(k)) is type(v) and r.get(k) == v)]
    x = r.get("execs")
    if not (type(x) is dict and sorted(x) == sorted(TRACES) and all(
            type(v) is list and v and all(type(e) is dict and all(type(e.get(k)) is str for k in ("path", "real", "bound_by"))
                                          and _hex64(e.get("sha256")) for e in v)
            and v[0]["path"].rsplit("/", 1)[-1] == PROGRAM[n] for n, v in x.items())):
        p.append("execs")
    rv = r.get("revision")
    if not (type(rv) is dict and sorted(rv) == ["end", "start"] and all(
            type(v) is dict and all(type(v.get(k)) is str and v[k].strip() for k in ("revision", "root_hash"))
            for v in rv.values())):
        p.append("revision values")
    if type(g) is dict and sorted(g) == sorted(TRACES):
        p += [f"gated {n}: {b}" for n, bs in sorted(GATED.items()) for b in bs
              if not any(type(e) is dict and str(e.get("path", "")).rsplit("/", 1)[-1] == b for e in g[n])]
    s = r.get("gst_schema")
    if not (type(s) is dict and sorted(s) == ["keys", "streamer_sha256"] and type(s["keys"]) is list and s["keys"]
            and all(type(k) is list and len(k) == 3 and all(type(y) is str for y in k) for k in s["keys"])
            and _hex64(s["streamer_sha256"])):
        p.append("gst schema")
    return p


def _deleted_problems(d):
    """[problems] with deleted.json: the three runs, the t0 gst among them, only deletable names, typed records."""
    if not (type(d) is dict and sorted(d) == sorted(DELETABLE) and all(type(v) is dict for v in d.values())
            and "genie_v3.gst.root" in d["t0"] and all(set(d[k]) <= set(DELETABLE[k]) for k in d)):
        return ["names"]
    def root_ok(n, v):   # C4's positive control: each ROOT file decoded (inflated), the gst's schema recorded
        if not n.endswith(".root"):
            return True
        c = v.get("decoded")
        return (type(c) is dict and type(c.get("holds_seed")) is bool and type(c.get("int32_count")) is int
                and type(c.get("codecs")) is dict and type(c.get("bytes_inflated")) is int
                and (n != "genie_v3.gst.root" or type(v.get("schema")) is dict))
    return [f"{k}/{n}" for k in sorted(d) for n, v in sorted(d[k].items())
            if not (type(v) is dict and _hex64(v.get("sha256")) and type(v.get("bytes")) is int and v["bytes"] >= 0
                    and type(v.get("holds_public_seed")) is bool and root_ok(n, v))]


def script_pins(body):
    """The top-level constant assignments of the sent script, read without running it."""
    out = {}
    for n in ast.parse(body.decode()).body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            try:
                out[n.targets[0].id] = ast.literal_eval(n.value)
            except ValueError:
                pass
    return out


def payload_problems(rec, schema, pins):
    p, go = [], rec.get("verdict") == "GO"
    if schema == "covfix-pg-install/1":
        members = json.loads(pins["MEMBERS_JSON"])["members"]
        if rec.get("root") != pins["ROOT"] or rec.get("tarball_sha256_pin") != pins["TARBALL_SHA256"]:
            p.append("root or tarball pin")
        if type(rec.get("n_members_pinned")) is not int or rec.get("n_members_pinned") != len(members):
            p.append("members count")
        if go and not (rec.get("tarball_sha256") == pins["TARBALL_SHA256"] and _hex64(pins.get("DBCONFIG_SHA256"))
                       and rec.get("dbconfig_sha256") == pins["DBCONFIG_SHA256"] and rec.get("scan_problems") == []
                       and rec.get("tree_problems") == [] and (rec.get("identity") or {}).get("pass") is True
                       and type(rec.get("install_utc")) is str):
            p.append("a GO without its hashes, pins and empty problem lists")
    elif schema == "covfix-pg-replay/1":
        blobs = json.loads(pins["BLOBS_JSON"])
        if (rec.get("commit") != pins["COMMIT"] or rec.get("archive_sha256_pin") != pins["ARCHIVE_SHA256"]
                or type(rec.get("n_blobs")) is not int or rec.get("n_blobs") != len(blobs)):
            p.append("commit, archive pin or blob count")
        if go:
            if not (rec.get("archive_sha256") == pins["ARCHIVE_SHA256"] and type(rec.get("n_files_checked")) is int
                    and rec.get("n_files_checked") == len(blobs) and type(rec.get("driver_rc")) is int
                    and rec.get("driver_rc") == 0 and (rec.get("identity") or {}).get("pass") is True):
                p.append("a GO without its archive, blobs, driver rc or identity")
            p += [f"replay {x}" for x in _replay_problems(rec.get("replay") or {})]
            p += [f"deleted {x}" for x in _deleted_problems(rec.get("deleted"))]
    return p


def validate(text, rc, schema, pins=None):
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
    if pins is not None:
        try:
            bad = payload_problems(rec, schema, pins)
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            bad = [f"payload unreadable: {type(e).__name__}"]
        if bad:
            return False, f"payload: {bad}"
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
    try:
        pins = script_pins(body)
    except (SyntaxError, UnicodeDecodeError, ValueError) as e:
        print(f"STOP: {script}'s pins cannot be read: {type(e).__name__}", file=sys.stderr)
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
        ok, why = validate(p.stdout.decode(errors="replace"), p.returncode, schema, pins)
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
