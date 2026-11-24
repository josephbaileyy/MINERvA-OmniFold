#!/usr/bin/env python3
"""Verification steps for COVFIX PG's private slot-1 product and its traced runs
(state/2d-closeout/covfix-20261122/pg/PLAN-SLOT1-PROBE.md, approved). Standard library only.

  members-check --root P --members M.json
      P (a products directory) must hold exactly M's members under genie_xsec/: each file with its sha256, each link
      with its target, each directory, and nothing else. No link is followed and nothing may be writable.
  tool-check --path T --sha256 H [--self-test]
      T is opened once; its sha256 is read through that descriptor and must equal H. With --self-test (strace only)
      the same descriptor is executed, tracing one open of a file this step creates: the trace must show it, and must
      be complete (trace_problems).
  trace-check --trace F --rc N --role {reduce,graphs,gevgen} --tune T --spline S --spline-sha256 H --cwd D
              --record PG-RECORD.json --manifest genie-manifest.json --private-members G2111a-members.json
              --w-root W [--w-pin PATH=SHA ...] --out J.json
      one traced run, against PLAN-SLOT1-PROBE.md's rules as the director tightened them:
      - complete (trace_problems), and the initial process (the command strace ran) opened S, whose bytes are H;
      - every gated file read (each .xml or .xml.gz, each path containing genie or GENIE, each file named like a
        genie library) matches its pin at its own path: the genie manifest, the private members, or a --w-pin;
      - a config-type file (.rootrc, system.rootrc, rootlogon*, rootlogoff*, rootalias*, .rootmap, .pcm, .xml,
        .xml.gz, or a file under a non-system etc/) read from outside the CVMFS repository, the private product and
        W fails; ROOT's own files are recorded with their sha256, gated on location only;
      - every probe (open, access, stat, readlink, ...) of a gated config basename is listed with its result; a probe
        that found it at a path other than the one opened fails;
      - for graphs and gevgen, every file PG-RECORD.json names as defining the tune is opened at its expected path,
        and no defining path is read through a link (a successful readlink on it fails).

  exe-check --manifest genie-manifest.json --path P [--path P ...]
      each P (gevgen and gspl2root as setup_genie_v3.sh's PATH resolves them) must lie in the genie product and match
      the manifest: the kernel maps a program without an open(), so no trace shows which binary ran.

Every refusal names the rule. Exit 0 on pass, 1 on a failed check, 2 on bad arguments.

MEASURES: byte identity and trace completeness. CANNOT AUTHORIZE: anything.
"""
import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile

O_NOATIME = getattr(os, "O_NOATIME", 0)
O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
FD_DIR = "/proc/self/fd" if os.path.isdir("/proc/self/fd") else "/dev/fd"
TRACE_SET = ("trace=open,openat,openat2,access,faccessat,faccessat2,stat,lstat,newfstatat,statx,readlink,readlinkat,"
             "chdir")


class Fail(Exception):
    pass


def _open(path, flags=os.O_RDONLY):
    try:
        return os.open(path, flags | O_NOFOLLOW | O_NOATIME)
    except PermissionError:
        if not O_NOATIME:
            raise
        return os.open(path, flags | O_NOFOLLOW)       # O_NOATIME needs ownership; the read is still unfollowed


def sha_fd(fd):
    h = hashlib.sha256()
    os.lseek(fd, 0, os.SEEK_SET)
    for b in iter(lambda: os.read(fd, 1 << 20), b""):
        h.update(b)
    os.lseek(fd, 0, os.SEEK_SET)        # /dev/fd shares the offset with what later executes this descriptor
    return h.hexdigest()


def sha_path(path):
    fd = _open(path)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise Fail(f"{path} is not a regular file")
        return sha_fd(fd)
    finally:
        os.close(fd)


# ------------------------------------------------------------------------------------------------------- members

def members_check(root, members):
    """[problems]: root/genie_xsec must equal the pinned members exactly, and be read-only."""
    probs, seen = [], {}
    top = os.path.join(root, "genie_xsec")
    if not stat.S_ISDIR(os.lstat(top).st_mode):
        return [f"{top} is not a directory"]
    seen["genie_xsec"] = os.lstat(top)
    stack = [top]
    while stack:
        d = stack.pop()
        for e in os.scandir(d):
            rel = os.path.relpath(e.path, root)
            st = os.lstat(e.path)
            seen[rel] = st
            if stat.S_ISDIR(st.st_mode):
                stack.append(e.path)
    want = {k: v for k, v in members.items() if k == "genie_xsec" or k.startswith("genie_xsec/")}
    for rel in sorted(set(seen) - set(want)):
        probs.append(f"extra: {rel}")
    for rel in sorted(set(want) - set(seen)):
        probs.append(f"missing: {rel}")
    for rel in sorted(set(want) & set(seen)):
        m, st, p = want[rel], seen[rel], os.path.join(root, rel)
        kind = ("dir" if stat.S_ISDIR(st.st_mode) else "file" if stat.S_ISREG(st.st_mode)
                else "symlink" if stat.S_ISLNK(st.st_mode) else "other")
        if kind != m["type"]:
            probs.append(f"{rel}: a {kind}, pinned as a {m['type']}")
            continue
        if kind != "symlink" and st.st_mode & 0o222:
            probs.append(f"{rel}: writable")
        if kind == "file" and sha_path(p) != m["sha256"]:
            probs.append(f"{rel}: sha256 differs from the pin")
        if kind == "symlink" and os.readlink(p) != m["target"]:
            probs.append(f"{rel}: link target differs from the pin")
    return probs


# ---------------------------------------------------------------------------------------------------------- traces

LINE = re.compile(r"^(\d+) +(.*)$")


def trace_problems(text, rc):
    """[problems] with a trace's completeness: strace's rc, an empty trace, a kill, a truncated or unfinished end,
    and the initial process (the first line's pid) not exiting 0."""
    probs = []
    if rc != 0:
        probs.append(f"strace exited {rc}")
    if not text:
        return probs + ["the trace is empty"]
    if not text.endswith("\n"):
        probs.append("the trace's last line is truncated")
    lines = text.splitlines()
    pids = [LINE.match(ln) for ln in lines]
    if not all(pids):
        probs.append("a trace line has no pid")
        return probs
    first = pids[0].group(1)
    if any("+++ killed by" in ln for ln in lines):
        probs.append("a traced process was killed")
    if not any(m.group(1) == first and m.group(2).startswith("+++ exited with 0 +++") for m in pids):
        probs.append("the initial process did not exit 0")
    if "<unfinished ...>" in lines[-1]:
        probs.append("the trace ends inside a call")
    return probs


SYSCALL = re.compile(r"^([a-z0-9_]+)\((.*)$")
QUOTED = re.compile(r'"((?:[^"\\]|\\.)*)"')
RESULT = re.compile(r"\)\s+=\s+(-?\d+|\?)(?:\s+([A-Z][A-Z0-9_]+))?")
PATH_ARG = {"open": 0, "access": 0, "stat": 0, "lstat": 0, "readlink": 0, "chdir": 0, "openat": 1, "openat2": 1,
            "faccessat": 1, "faccessat2": 1, "newfstatat": 1, "statx": 1, "readlinkat": 1}
WRITE_FLAGS = ("O_WRONLY", "O_RDWR", "O_CREAT", "O_TRUNC", "O_APPEND")
CONFIG_SUFFIX = (".rootmap", ".pcm", ".xml", ".xml.gz")
GENIE_ROOT = "/cvmfs/larsoft.opensciencegrid.org/products/genie/v3_04_00"
XSEC_ROOT = "/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00"
CVMFS_REPO = "/cvmfs/larsoft.opensciencegrid.org"
PRIVATE_PRODUCTS = "/pscratch/sd/j/josephrb/covfix-pg/products"


def _unescape(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c != "\\":
            out.append(c)
            i += 1
            continue
        n = s[i + 1] if i + 1 < len(s) else ""
        if n == "x":
            out.append(chr(int(s[i + 2:i + 4], 16)))
            i += 4
        elif n.isdigit():
            j = i + 1
            while j < len(s) and j < i + 4 and s[j].isdigit():
                j += 1
            out.append(chr(int(s[i + 1:j], 8)))
            i = j
        else:
            out.append({"n": "\n", "t": "\t", "r": "\r", "v": "\v", "f": "\f"}.get(n, n))
            i += 2
    return "".join(out)


def parse_trace(text):
    """[event]: {pid, call, path (raw), dirfd, write, ok, errno}, with unfinished and resumed calls joined."""
    events, pending = [], {}
    for ln in text.splitlines():
        m = LINE.match(ln)
        if not m:
            continue
        pid, rest = m.group(1), m.group(2)
        if rest.startswith("<... "):
            if pid not in pending:
                continue
            rest = pending.pop(pid) + rest.split(" resumed>", 1)[-1]
        elif rest.endswith("<unfinished ...>"):
            pending[pid] = rest[: -len("<unfinished ...>")].rstrip()
            continue
        sm = SYSCALL.match(rest)
        if not sm or sm.group(1) not in PATH_ARG:
            continue
        call, args = sm.group(1), sm.group(2)
        quoted = QUOTED.findall(args)
        if not quoted:
            continue
        path = _unescape(quoted[0])
        dirfd = args.split(",", 1)[0].strip() if PATH_ARG[call] == 1 else "AT_FDCWD"
        rm = RESULT.search(args)
        ok = bool(rm) and rm.group(1) not in ("-1", "?")
        events.append({"pid": pid, "call": call, "path": path, "dirfd": dirfd, "ok": ok,
                       "errno": rm.group(2) if rm and not ok else None,
                       "write": call.startswith("open") and any(f in args for f in WRITE_FLAGS)})
    return events


def _resolve(events, cwd):
    """Each event's absolute normalised path, from its pid's cwd (chdir tracked; the initial cwd otherwise), or None
    for a relative path given against a directory descriptor."""
    cwds = {}
    for e in events:
        base = cwds.get(e["pid"], cwd)
        if e["path"].startswith("/"):
            e["abs"] = os.path.normpath(e["path"])
        elif e["dirfd"] == "AT_FDCWD":
            e["abs"] = os.path.normpath(os.path.join(base, e["path"]))
        else:
            e["abs"] = None
        if e["call"] == "chdir" and e["ok"] and e["abs"]:
            cwds[e["pid"]] = e["abs"]
    return events


def _under(p, root):
    return p == root or p.startswith(root.rstrip("/") + "/")


def _manifest_file(members, rel, depth=0):
    """(rel of the regular file a member resolves to inside the manifest, its record), following in-manifest links."""
    m = members.get(rel)
    if m is None or depth > 8:
        return None, None
    if m["type"] == "symlink":
        return _manifest_file(members, os.path.normpath(os.path.join(os.path.dirname(rel), m["target"])), depth + 1)
    return rel, m


def config_type(p):
    b = os.path.basename(p)
    return (b in (".rootrc", "system.rootrc") or b.startswith(("rootlogon", "rootlogoff", "rootalias"))
            or b.endswith(CONFIG_SUFFIX) or ("/etc/" in p and not p.startswith("/etc/")))


def trace_check(text, rc, role, tune, spline, spline_sha, cwd, record, manifest, private, w_root, w_pins,
                genie_root=GENIE_ROOT, xsec_root=XSEC_ROOT, repo=CVMFS_REPO, private_root=PRIVATE_PRODUCTS,
                sha=None):
    """The check's record: pass, problems, the gated files read with their sha256, ROOT's config files, probes."""
    sha = sha or sha_path
    probs = trace_problems(text, rc)
    events = _resolve(parse_trace(text), cwd)
    lines = text.splitlines()
    first = LINE.match(lines[0]).group(1) if lines and LINE.match(lines[0]) else None
    libnames = {os.path.basename(k) for k, v in manifest.items() if k.split("/")[-2:-1] == ["lib"]}
    reads = [e for e in events if e["call"].startswith("open") and e["ok"] and not e["write"]]
    rec = {"role": role, "tune": tune, "n_events": len(events), "gated": [], "root_config": [], "probes": {}}

    spl = os.path.normpath(spline)
    opened = [e for e in reads if e["pid"] == first and e["abs"] == spl]
    rec["initial_opened_spline"] = bool(opened)
    if not opened:
        probs.append("the initial process did not open the expected spline")
    else:
        try:
            got = sha(spl)
        except (OSError, Fail):
            got = None
        if got != spline_sha:
            probs.append("the opened spline's sha256 differs from the pin")

    gated_paths = {}
    for e in reads:
        p = e["abs"]
        if p is None:
            if config_type(e["path"]) or "genie" in e["path"].lower():
                probs.append(f"a config file opened relative to a directory descriptor: {e['path']}")
            continue
        name = os.path.relpath(p, w_root) if _under(p, w_root) else p      # W's own path does not gate its files
        gated = (p.endswith((".xml", ".xml.gz")) or "genie" in name.lower() or os.path.basename(p) in libnames)
        if gated and p not in gated_paths:
            pin, where, real = None, None, p        # real: the file a manifest link resolves to, never followed on disk
            if _under(p, genie_root):
                rel, m = _manifest_file(manifest, "genie/v3_04_00/" + os.path.relpath(p, genie_root))
                pin, where = (m or {}).get("sha256"), "genie manifest"
                real = os.path.join(genie_root, rel[len("genie/v3_04_00/"):]) if rel else p
            elif _under(p, private_root):
                rel, m = _manifest_file(private, os.path.relpath(p, private_root))
                pin, where = (m or {}).get("sha256"), "private members"
                real = os.path.join(private_root, rel) if rel else p
            elif _under(p, w_root) and p in w_pins:
                pin, where = w_pins[p], "W pin"
            try:
                got = sha(real)
            except (OSError, Fail):
                got = None
            gated_paths[p] = {"path": p, "sha256": got, "pinned_by": where, "match": got is not None and got == pin}
            if not gated_paths[p]["match"]:
                probs.append(f"a gated file does not match its pin: {p} ({where or 'no pin'})")
        if config_type(p):
            if not (_under(p, repo) or _under(p, private_root) or _under(p, w_root)):
                probs.append(f"a config-type file opened outside CVMFS, the private product and W: {p}")
            elif not gated and _under(p, repo):
                try:
                    got = sha(p)
                except (OSError, Fail):
                    got = None
                rec["root_config"].append({"path": p, "sha256": got})
    rec["gated"] = sorted(gated_paths.values(), key=lambda x: x["path"])

    cfg_names = {os.path.basename(p) for p in gated_paths if p.endswith((".xml", ".xml.gz"))}
    for b in sorted(cfg_names):
        probes = [e for e in events if e["abs"] and os.path.basename(e["abs"]) == b]
        rec["probes"][b] = [{"call": e["call"], "path": e["abs"], "ok": e["ok"], "errno": e["errno"]} for e in probes]
        opened_at = {e["abs"] for e in probes if e["call"].startswith("open") and e["ok"]}
        found = {e["abs"] for e in probes if e["ok"] and not e["call"].startswith("readlink")}
        if found - opened_at:
            probs.append(f"{b} was found at {sorted(found - opened_at)} but opened at {sorted(opened_at)}")

    if role in ("graphs", "gevgen"):
        t = record["tunes"].get(tune)
        if t is None:
            probs.append(f"the record has no tune {tune}")
        else:
            want = {t["model_configuration"], t["event_generator"], t["tune_generator_list"],
                    t["model_configuration"].rsplit("/config/", 1)[0] + "/config/master_config.xml"}
            for s in ("ccqe", "2p2h"):
                x = t[s]
                if "hybrid" in x:
                    want |= {x["hybrid"]["file"]} | {z["file"] for z in x["leaves"]}
                else:
                    want.add(x["registry"]["file"])
            rec["defining_files"] = sorted(want)
            for rel in sorted(want):
                p = os.path.normpath(os.path.join(genie_root, rel))
                if p not in gated_paths:
                    probs.append(f"a defining file was not opened at its expected path: {rel}")
                if any(e["call"].startswith("readlink") and e["ok"] and e["abs"] == p for e in events):
                    probs.append(f"a defining file is read through a link: {rel}")
    rec["problems"], rec["pass"] = probs, not probs
    return rec


def cmd_trace(a):
    try:
        text = open(a.trace).read() if os.path.exists(a.trace) else ""
        w_pins = {}
        for x in a.w_pin or []:
            k, _, v = x.partition("=")
            w_pins[os.path.normpath(k)] = v
        rec = trace_check(text, a.rc, a.role, a.tune, a.spline, a.spline_sha256, a.cwd, json.load(open(a.record)),
                          json.load(open(a.manifest))["members"], json.load(open(a.private_members))["members"],
                          os.path.normpath(a.w_root), w_pins)
    except (OSError, ValueError, KeyError, Fail) as e:
        rec = {"role": a.role, "tune": a.tune, "pass": False, "problems": [f"{type(e).__name__}: {e}"]}
    if os.path.exists(a.out):
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 2
    with open(a.out, "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({"check": "trace", "role": a.role, "tune": a.tune, "pass": rec["pass"],
                      "n_problems": len(rec["problems"])}))
    return 0 if rec["pass"] else 1


def exe_problems(paths, manifest, genie_root=GENIE_ROOT):
    """[problems]: each resolved program must be a manifest member of the genie product, with its pinned bytes."""
    probs = []
    for p in paths:          # a path outside the product has no manifest key, and a non-file member cannot be hashed
        p = os.path.normpath(p)
        key = os.path.normpath("genie/v3_04_00/" + os.path.relpath(p, genie_root)) if p.startswith("/") else None
        rel, m = _manifest_file(manifest, key) if key else (None, None)
        try:
            ok = m is not None and sha_path(os.path.join(genie_root, rel[len("genie/v3_04_00/"):])) == m.get("sha256")
        except (OSError, Fail):
            ok = False
        if not ok:
            probs.append(f"{p} is not a genie-product file with the manifest's sha256")
    return probs


def cmd_exe(a):
    try:
        probs = exe_problems(a.path or [], json.load(open(a.manifest))["members"])
    except (OSError, ValueError, KeyError) as e:
        probs = [f"{type(e).__name__}: {e}"]
    if not a.path:
        probs.append("no program given")
    print(json.dumps({"check": "exe", "pass": not probs, "paths": a.path or [], "problems": probs}))
    return 0 if not probs else 1


def cmd_members(a):
    n = None
    try:
        members = json.load(open(a.members))["members"]
        n = len(members)
        probs = members_check(a.root, members)
    except (OSError, ValueError, KeyError, Fail) as e:
        probs = [f"{type(e).__name__}: {e}"]
    print(json.dumps({"check": "members", "pass": not probs, "n_pinned": n, "problems": probs}))
    return 0 if not probs else 1


def cmd_tool(a):
    rec = {"check": "tool", "path": a.path, "pass": False, "problems": []}
    try:
        fd = _open(a.path)
    except OSError as e:
        rec["problems"].append(f"cannot open: {e.strerror}")
        print(json.dumps(rec))
        return 1
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            rec["problems"].append("not a regular file")
        else:
            rec["sha256"] = sha_fd(fd)
            if rec["sha256"] != a.sha256:
                rec["problems"].append("sha256 differs from the pin")
            elif a.self_test:
                with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
                    probe, out = os.path.join(td, "pg-self-test.txt"), os.path.join(td, "trace.txt")
                    with open(probe, "w") as f:
                        f.write("pg\n")
                    p = subprocess.run([f"{FD_DIR}/{fd}", "-f", "-q", "-e", TRACE_SET, "-o", out, "/bin/cat", probe],
                                       pass_fds=(fd,), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60)
                    text = open(out).read() if os.path.exists(out) else ""
                    rec["problems"] += trace_problems(text, p.returncode)
                    if not re.search(r'open(at)?\((AT_FDCWD, )?"' + re.escape(probe) + r'", .*\) = \d+$', text, re.M):
                        rec["problems"].append("the self-test's open is not in the trace")
    finally:
        os.close(fd)
    rec["pass"] = not rec["problems"]
    print(json.dumps(rec))
    return 0 if rec["pass"] else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("members-check")
    m.add_argument("--root", required=True)
    m.add_argument("--members", required=True)
    t = sub.add_parser("tool-check")
    t.add_argument("--path", required=True)
    t.add_argument("--sha256", required=True)
    t.add_argument("--self-test", action="store_true")
    r = sub.add_parser("trace-check")
    for k in ("trace", "role", "tune", "spline", "spline-sha256", "cwd", "record", "manifest", "private-members",
              "w-root", "out"):
        r.add_argument("--" + k, required=True)
    r.add_argument("--rc", type=int, required=True)
    r.add_argument("--w-pin", action="append")
    e = sub.add_parser("exe-check")
    e.add_argument("--manifest", required=True)
    e.add_argument("--path", action="append")
    a = ap.parse_args(argv)
    return {"members-check": cmd_members, "tool-check": cmd_tool, "trace-check": cmd_trace, "exe-check": cmd_exe}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
