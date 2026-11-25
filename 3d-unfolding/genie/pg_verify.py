#!/usr/bin/env python3
"""Verification steps for COVFIX PG's private slot-1 product and its traced runs
(state/2d-closeout/covfix-20261122/pg/PLAN-SLOT1-PROBE.md, approved; RULINGS-A2.md). Standard library only.

Every problem is "<reason code>: <detail>", so a test can require the reason it expects. An unexpected exception in
any check is the single reason "internal-error: <exception type>", which is a failure and which no other test expects.

  members-check --root P --members M.json
      P/genie_xsec (a container directory, not itself a member) must hold exactly M's members: each file with its
      sha256, each link with its target, each directory, and nothing else, none writable; P/.upsfiles must hold only
      a read-only dbconfig. No link is followed.
  tool-check (--fd N | --path T) --sha256 H [--self-test]
      the tool's sha256 is read through one descriptor: an inherited descriptor N (as pg_generate.sh passes strace;
      /proc/self/fd/N is a magic link that O_NOFOLLOW refuses, so no path is opened), or T opened once without
      following a link. It must equal H. With --self-test, that descriptor is executed, tracing one open of a file
      this step creates, and the trace must show it and be complete (trace_problems).
  trace-check --trace F --rc N --role {reduce,graphs,gevgen} --tune T --spline S --spline-sha256 H --cwd D
              --record PG-RECORD.json --manifest genie-manifest.json --private-members G2111a-members.json
              --w-root W [--pin PATH=SHA ...] --out J.json
      one traced run (TRACE_SET's path-only calls), against the director's rules:
      - complete: strace's rc 0; not empty; no truncated last line; no killed process; no call left unfinished; every
        process exits 0 (trace_problems);
      - the initial process (the command strace ran) read S, whose bytes are H; no other spline is read;
      - every gated file read (.xml or .xml.gz, a path containing genie or GENIE, a genie library's name) matches its
        pin at its own path: an exact --pin, the genie manifest or the private members (each with its real path equal
        to the manifest's resolution, so links agree on disk); a read is any open without O_WRONLY or O_DIRECTORY, and
        an O_CREAT open under W is an output;
      - a config-type file (.rootrc, system.rootrc, rootlogon*, rootlogoff*, rootalias*, .rootmap, .pcm, .xml,
        .xml.gz, or a file under a non-system etc/) read from outside CVMFS, the private product and W fails, and so
        does one under the private product or W that no pin matches; ROOT's own on CVMFS are recorded with their sha256;
      - a shared library (.so) read must have its real path under CVMFS, a system library directory or the manifest;
      - a path is resolved only when it can be: fchdir is a failure; a gated or config name opened relative to a
        directory descriptor, or by a process whose working directory is unknown (any chdir outside the initial
        process), is a failure; so is any gated or config path with a '..' component;
      - every probe (open, access, stat, readlink) of a gated or config basename is listed; a probe that found it at
        a path other than the one read fails;
      - for graphs and gevgen, every file PG-RECORD.json names as defining the tune is read by the initial process at
        its expected path, and none is read through a link.
  exe-check --manifest genie-manifest.json --path P [--path P ...] [--ld-library-path VALUE] [--system-path S ...]
      each P must be a genie-product file with the manifest's sha256 and real path (the kernel maps a program without
      an open(), so no trace shows which binary ran); each LD_LIBRARY_PATH entry's real path must be under CVMFS or a
      system library directory, or be a genie-manifest directory; each S (awk) must be a root-owned file under /usr/bin
      or /bin that only root can write.
  shape-check --fd N --members M.json --members-check MC.json --tool-check TC.json --traces J.json ...
              --slot2-reduce S2.json
      the director's four real-shape checks, on the node, from the replay's own records: the member listing has no
      container entry and checked clean; /proc/self/fd/N refuses O_NOFOLLOW (ELOOP) while tool-check --fd passed; a
      real O_DIRECTORY open was recorded by a passing trace check; slot 2's reduce read CVMFS's spline at its real path,
      matched by an exact pin.

Exit 0 on pass, 1 on a failed check, 2 on bad arguments.

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
             "chdir,fchdir")
GENIE_ROOT = "/cvmfs/larsoft.opensciencegrid.org/products/genie/v3_04_00"
CVMFS_REPO = "/cvmfs/larsoft.opensciencegrid.org"
PRIVATE_PRODUCTS = "/pscratch/sd/j/josephrb/covfix-pg/products"
SYSTEM_LIBS = ("/lib", "/lib64", "/usr/lib", "/usr/lib64")


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


def _under(p, root):
    return p == root or p.startswith(root.rstrip("/") + "/")


# ------------------------------------------------------------------------------------------------------- members

def members_check(root, members):
    """[problems]: root/genie_xsec holds exactly the pinned members, read-only; root/.upsfiles only a read-only dbconfig."""
    probs, seen = [], {}
    top = os.path.join(root, "genie_xsec")
    st = os.lstat(top)
    if not stat.S_ISDIR(st.st_mode) or st.st_mode & 0o222:
        probs.append("members-type: genie_xsec is not a read-only directory")
    stack = [top]
    while stack:
        d = stack.pop()
        for e in os.scandir(d):
            s = os.lstat(e.path)
            seen[os.path.relpath(e.path, root)] = s
            if stat.S_ISDIR(s.st_mode):
                stack.append(e.path)
    want = {k: v for k, v in members.items() if k.startswith("genie_xsec/")}
    probs += [f"members-extra: {r}" for r in sorted(set(seen) - set(want))]
    probs += [f"members-missing: {r}" for r in sorted(set(want) - set(seen))]
    for rel in sorted(set(want) & set(seen)):
        m, s, p = want[rel], seen[rel], os.path.join(root, rel)
        kind = ("dir" if stat.S_ISDIR(s.st_mode) else "file" if stat.S_ISREG(s.st_mode)
                else "symlink" if stat.S_ISLNK(s.st_mode) else "other")
        if kind != m["type"]:
            probs.append(f"members-type: {rel} is a {kind}, pinned as a {m['type']}")
            continue
        if kind != "symlink" and s.st_mode & 0o222:
            probs.append(f"members-writable: {rel}")
        if kind == "file" and sha_path(p) != m["sha256"]:
            probs.append(f"members-sha: {rel}")
        if kind == "symlink" and os.readlink(p) != m["target"]:
            probs.append(f"members-link: {rel}")
    up = os.path.join(root, ".upsfiles")
    try:
        ust, names = os.lstat(up), sorted(os.listdir(up))
        dst = os.lstat(os.path.join(up, "dbconfig"))
        if (not stat.S_ISDIR(ust.st_mode) or ust.st_mode & 0o222 or names != ["dbconfig"]
                or not stat.S_ISREG(dst.st_mode) or dst.st_mode & 0o222):
            probs.append(f"upsfiles: .upsfiles is not a read-only directory holding only a read-only dbconfig ({names})")
    except OSError as e:
        probs.append(f"upsfiles: {e.strerror}")
    return probs


# ---------------------------------------------------------------------------------------------------------- traces

LINE = re.compile(r"^(\d+) +(.*)$")


def trace_problems(text, rc):
    """[problems] with a trace's completeness."""
    probs = []
    if rc != 0:
        probs.append(f"strace-rc: strace exited {rc}")
    if not text:
        return probs + ["empty: the trace is empty"]
    if not text.endswith("\n"):
        probs.append("truncated: the trace's last line is truncated")
    lines = text.splitlines()
    ms = [LINE.match(ln) for ln in lines]
    if not all(ms):
        return probs + ["no-pid: a trace line has no pid"]
    first = ms[0].group(1)
    pending, exits = set(), {}
    for m in ms:
        pid, rest = m.group(1), m.group(2)
        if rest.endswith("<unfinished ...>"):
            pending.add(pid)
        elif rest.startswith("<... "):
            pending.discard(pid)
        x = re.match(r"\+\+\+ exited with (\d+) \+\+\+", rest)
        if x:
            exits[pid] = int(x.group(1))                     # an exit does not complete a call left unfinished
        if rest.startswith("+++ killed by"):
            probs.append(f"killed: process {pid} was killed")
    if exits.get(first) != 0:
        probs.append("initial-exit: the initial process did not exit 0")
    probs += [f"child-exit: process {p} exited {x}" for p, x in sorted(exits.items()) if p != first and x != 0]
    if pending:
        probs.append(f"unresumed: calls left unfinished in processes {sorted(pending)}")
    return probs


SYSCALL = re.compile(r"^([a-z0-9_]+)\((.*)$")
QUOTED = re.compile(r'"((?:[^"\\]|\\.)*)"')
RESULT = re.compile(r"\)\s+=\s+(-?\d+|\?)(?:\s+([A-Z][A-Z0-9_]+))?(?:\s+\(.*\))?\s*$")
PATH_ARG = {"open": 0, "access": 0, "stat": 0, "lstat": 0, "readlink": 0, "chdir": 0, "openat": 1, "openat2": 1,
            "faccessat": 1, "faccessat2": 1, "newfstatat": 1, "statx": 1, "readlinkat": 1}
CONFIG_SUFFIX = (".rootmap", ".pcm", ".xml", ".xml.gz")


def _unescape(s):
    """strace's escapes, decoded as bytes (an octal sequence may be one byte of a UTF-8 character)."""
    out, i = bytearray(), 0
    while i < len(s):
        c = s[i]
        if c != "\\":
            out += c.encode()
            i += 1
            continue
        n = s[i + 1] if i + 1 < len(s) else ""
        if n == "x":
            out.append(int(s[i + 2:i + 4], 16))
            i += 4
        elif n.isdigit():
            j = i + 1
            while j < len(s) and j < i + 4 and s[j].isdigit():
                j += 1
            out.append(int(s[i + 1:j], 8))
            i = j
        else:
            out += {"n": "\n", "t": "\t", "r": "\r", "v": "\v", "f": "\f"}.get(n, n).encode()
            i += 2
    return os.fsdecode(bytes(out))


def parse_trace(text):
    """[event]: {pid, call, path, dirfd, ok, errno, write_only, creat, directory}; unfinished calls joined."""
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
        if not sm:
            continue
        call, args = sm.group(1), sm.group(2)
        bare = QUOTED.sub('""', args)
        rm = RESULT.search(bare)
        ok = bool(rm) and rm.group(1) not in ("-1", "?")
        if call == "fchdir":
            events.append({"pid": pid, "call": call, "path": None, "dirfd": None, "ok": ok, "errno": None,
                           "write_only": False, "creat": False, "directory": False})
            continue
        if call not in PATH_ARG:
            continue
        quoted = QUOTED.findall(args)
        if not quoted:
            continue
        parts = [x.strip() for x in bare.split(",")]
        flags = ""
        if call in ("open", "openat"):
            k = PATH_ARG[call] + 1
            flags = parts[k] if len(parts) > k else ""
        elif call == "openat2":
            fm = re.search(r"flags=([A-Z_|0-9]+)", bare)
            flags = fm.group(1) if fm else ""
        events.append({"pid": pid, "call": call, "path": _unescape(quoted[0]),
                       "dirfd": parts[0] if PATH_ARG[call] == 1 else "AT_FDCWD", "ok": ok,
                       "errno": rm.group(2) if rm and not ok else None,
                       "write_only": "O_WRONLY" in flags, "creat": "O_CREAT" in flags,
                       "directory": "O_DIRECTORY" in flags})
    return events


def config_type(p):
    b = os.path.basename(p)
    return (b in (".rootrc", "system.rootrc") or b.startswith(("rootlogon", "rootlogoff", "rootalias"))
            or b.endswith(CONFIG_SUFFIX) or ("/etc/" in "/" + p and not p.startswith("/etc/")))


def _manifest_file(members, rel, depth=0):
    """(rel of the regular file a member resolves to inside the manifest, its record), following in-manifest links."""
    rel = os.path.normpath(rel)
    m = members.get(rel)
    if m is None or depth > 8:
        return None, None
    if m["type"] == "symlink":
        return _manifest_file(members, os.path.join(os.path.dirname(rel), m["target"]), depth + 1)
    return rel, m


def _is_so(p):
    return re.search(r"\.so(\.\d+)*$", os.path.basename(p)) is not None      # libX.so, libX.so.10; not ld.so.cache


def trace_check(text, rc, role, tune, spline, spline_sha, cwd, record, manifest, private, w_root, pins,
                genie_root=GENIE_ROOT, repo=CVMFS_REPO, private_root=PRIVATE_PRODUCTS, sha=None):
    """The check's record: pass, problems (each "<code>: <detail>"), the gated files read, ROOT's config files."""
    try:
        return _trace_check(text, rc, role, tune, spline, spline_sha, cwd, record, manifest, private, w_root, pins,
                            genie_root, repo, private_root, sha or sha_path)
    except Exception as e:                                  # fail closed, with a reason no other test expects
        return {"role": role, "tune": tune, "pass": False, "problems": [f"internal-error: {type(e).__name__}"]}


def _trace_check(text, rc, role, tune, spline, spline_sha, cwd, record, manifest, private, w_root, pins, genie_root,
                 repo, private_root, sha):
    probs = trace_problems(text, rc)
    events = parse_trace(text)
    lines = text.splitlines()
    first = LINE.match(lines[0]).group(1) if lines and LINE.match(lines[0]) else None
    w_root = os.path.normpath(w_root)
    real_genie = os.path.realpath(genie_root)
    pins = {os.path.normpath(k): v for k, v in pins.items()}
    libnames = {os.path.basename(k) for k, v in manifest.items() if k.split("/")[-2:-1] == ["lib"]}

    # working directories: the initial process's chdirs are followed; any other process's make cwds unknown
    if any(e["call"] == "fchdir" and e["ok"] for e in events):
        probs.append("fchdir: a traced process changed directory by descriptor")
    other_chdir = any(e["call"] == "chdir" and e["ok"] and e["pid"] != first for e in events)
    cur = cwd
    for e in events:
        if e["call"] == "fchdir":
            e["abs"] = None
            continue
        p = e["path"]
        if p.startswith("/"):
            e["abs"] = os.path.normpath(p)
        elif e["dirfd"] != "AT_FDCWD" or (e["pid"] != first and other_chdir):
            e["abs"] = None
        else:
            e["abs"] = os.path.normpath(os.path.join(cur if e["pid"] == first else cwd, p))
        if e["call"] == "chdir" and e["ok"] and e["pid"] == first and e["abs"]:
            cur = e["abs"]

    def watched(raw):
        b = os.path.basename(raw)
        return (config_type(raw) or "genie" in raw.lower() or b in libnames or _is_so(raw) or raw.startswith("etc/")
                or "/etc/" in raw)

    for e in events:
        if e["call"] == "fchdir":
            continue
        raw = e["path"]
        if e["abs"] is None and watched(raw):
            code = "dirfd-relative" if e["dirfd"] not in (None, "AT_FDCWD") else "cwd-unknown"
            probs.append(f"{code}: {e['call']} of {raw!r} cannot be resolved")
        if ".." in raw.split("/") and watched(raw):
            probs.append(f"dotdot: {raw!r} has a '..' component")

    opens = [e for e in events if e["call"].startswith("open") and e["ok"] and e["abs"]]
    reads = [e for e in opens if not e["write_only"] and not e["directory"]
             and not (e["creat"] and _under(e["abs"], w_root))]
    rec = {"role": role, "tune": tune, "spline": os.path.normpath(spline), "n_events": len(events), "gated": [], "root_config": [], "probes": {},
           "directories_opened": sum(1 for e in opens if e["directory"])}

    spl = os.path.normpath(spline)
    rec["initial_opened_spline"] = any(e["pid"] == first and e["abs"] == spl for e in reads)
    if not rec["initial_opened_spline"]:
        probs.append("spline-not-opened: the initial process did not read the expected spline")
    else:
        try:
            got = sha(spl)
        except (OSError, Fail):
            got = None
        if got != spline_sha:
            probs.append("spline-sha: the spline read differs from its pin")
    for e in reads:
        b = os.path.basename(e["abs"])
        if e["abs"] != spl and (b.startswith("gxspl-") or b.endswith("_CH.xml.gz")):
            probs.append(f"other-spline: {e['abs']}")

    gated_paths = {}
    for e in reads:
        p = e["abs"]
        name = os.path.relpath(p, w_root) if _under(p, w_root) else p      # W's own path does not gate its files
        gated = p.endswith((".xml", ".xml.gz")) or "genie" in name.lower() or os.path.basename(p) in libnames
        if gated and p not in gated_paths:
            pin, where, want_real = None, None, p
            if p in pins:
                pin, where = pins[p], "exact pin"
            elif _under(p, genie_root):
                rel, m = _manifest_file(manifest, "genie/v3_04_00/" + os.path.relpath(p, genie_root))
                pin, where = (m or {}).get("sha256"), "genie manifest"
                want_real = os.path.join(real_genie, rel[len("genie/v3_04_00/"):]) if rel else None
            elif _under(p, private_root):
                rel, m = _manifest_file(private, os.path.relpath(p, private_root))
                pin, where = (m or {}).get("sha256"), "private members"
                want_real = os.path.join(os.path.realpath(private_root), rel) if rel else None
            try:
                got = sha(want_real) if want_real and os.path.realpath(p) == want_real else None
            except (OSError, Fail):
                got = None
            gated_paths[p] = {"path": p, "sha256": got, "pinned_by": where, "match": got is not None and got == pin}
            if not gated_paths[p]["match"]:
                probs.append(f"gated-mismatch: {p} ({where or 'no pin'})")
        if _is_so(p):
            real = os.path.realpath(p)
            if not (any(_under(real, r) for r in (repo,) + SYSTEM_LIBS) or gated_paths.get(p, {}).get("match")):
                probs.append(f"so-outside-roots: {p} -> {real}")
        if config_type(p):
            if not (_under(p, repo) or _under(p, private_root) or _under(p, w_root)):
                probs.append(f"config-outside-roots: {p}")
            elif not gated and (_under(p, private_root) or _under(p, w_root)):   # a .rootrc in W is read by ROOT
                probs.append(f"config-unpinned: {p}")
            elif not gated and _under(p, repo):
                try:
                    got = sha(p)
                except (OSError, Fail):
                    got = None
                rec["root_config"].append({"path": p, "sha256": got})
    rec["gated"] = sorted(gated_paths.values(), key=lambda x: x["path"])

    names = {os.path.basename(e["abs"]) for e in reads if e["abs"] in gated_paths or config_type(e["abs"])}
    for b in sorted(names):
        probes = [e for e in events if e.get("abs") and os.path.basename(e["abs"]) == b]
        rec["probes"][b] = [{"call": e["call"], "path": e["abs"], "ok": e["ok"], "errno": e["errno"]} for e in probes]
        read_at = {e["abs"] for e in reads if os.path.basename(e["abs"]) == b}
        found = {e["abs"] for e in probes if e["ok"] and not e["call"].startswith("readlink") and not e["directory"]}
        if found - read_at:
            probs.append(f"search-order: {b} was found at {sorted(found - read_at)} but read at {sorted(read_at)}")

    if role in ("graphs", "gevgen"):
        t = record["tunes"][tune]
        want = {t["model_configuration"], t["event_generator"], t["tune_generator_list"],
                t["model_configuration"].rsplit("/config/", 1)[0] + "/config/master_config.xml"}
        for s in ("ccqe", "2p2h"):
            x = t[s]
            want |= ({x["hybrid"]["file"]} | {z["file"] for z in x["leaves"]}) if "hybrid" in x else {x["registry"]["file"]}
        rec["defining_files"] = sorted(want)
        first_reads = {e["abs"] for e in reads if e["pid"] == first}
        for rel in sorted(want):
            p = os.path.normpath(os.path.join(genie_root, rel))
            if p not in first_reads or p not in gated_paths:
                probs.append(f"defining-not-opened: {rel}")
            if any(e["call"].startswith("readlink") and e["ok"] and e.get("abs") == p for e in events):
                probs.append(f"defining-link: {rel}")
    rec["problems"], rec["pass"] = probs, not probs
    return rec


# ------------------------------------------------------------------------------------------------------------ exe

def system_tool_problems(paths):
    probs = []
    for p in paths:
        real = os.path.realpath(p)
        try:
            st = os.stat(real)
            ok = (any(_under(real, r) for r in ("/usr/bin", "/bin")) and stat.S_ISREG(st.st_mode) and st.st_uid == 0
                  and not st.st_mode & 0o022)
        except OSError:
            ok = False
        if not ok:
            probs.append(f"system-tool: {p} -> {real} is not a root-owned file under /usr/bin or /bin")
    return probs


def exe_problems(paths, manifest, genie_root=GENIE_ROOT, ld_library_path=None):
    """[problems]: each program a genie-product file with the manifest's bytes and real path; LD_LIBRARY_PATH's entries
    under CVMFS, the system library directories or a manifest directory."""
    probs, real_genie = [], os.path.realpath(genie_root)
    for p in paths:          # a path outside the product has no manifest key, and a non-file member cannot be hashed
        p = os.path.normpath(p)
        key = os.path.normpath("genie/v3_04_00/" + os.path.relpath(p, genie_root)) if p.startswith("/") else None
        rel, m = _manifest_file(manifest, key) if key else (None, None)
        want_real = os.path.join(real_genie, rel[len("genie/v3_04_00/"):]) if m is not None else None
        try:
            ok = (want_real is not None and os.path.realpath(p) == want_real
                  and sha_path(want_real) == m.get("sha256"))
        except (OSError, Fail):
            ok = False
        if not ok:
            probs.append(f"exe-not-manifest: {p} is not a genie-product file with the manifest's sha256 and real path")
    if ld_library_path is not None:
        dirs = {os.path.normpath("genie/v3_04_00/" + k[len("genie/v3_04_00/"):]) for k, v in manifest.items()
                if v.get("type") == "dir"}
        for entry in ld_library_path.split(":"):
            if not entry:
                continue
            real = os.path.realpath(entry)
            in_manifest = _under(real, real_genie) and os.path.normpath(
                "genie/v3_04_00/" + os.path.relpath(real, real_genie)) in dirs
            if not (in_manifest or any(_under(real, r) for r in (CVMFS_REPO,) + SYSTEM_LIBS)):
                probs.append(f"ld-library-path: {entry} -> {real} is outside CVMFS and the system library directories")
    return probs


# ----------------------------------------------------------------------------------------------------------- CLIs

def _out(rec):
    print(json.dumps(rec))
    return 0 if rec["pass"] else 1


def cmd_members(a):
    n = None
    try:
        members = json.load(open(a.members))["members"]
        n = len(members)
        probs = members_check(a.root, members)
    except OSError as e:
        probs = [f"members-unreadable: {e.strerror}"]
    except Exception as e:
        probs = [f"internal-error: {type(e).__name__}"]
    return _out({"check": "members", "pass": not probs, "n_pinned": n, "problems": probs})


def _self_test(fd):
    probs = []
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        probe, out = os.path.join(td, "pg-self-test.txt"), os.path.join(td, "trace.txt")
        with open(probe, "w") as f:
            f.write("pg\n")
        p = subprocess.run([f"{FD_DIR}/{fd}", "-f", "-q", "-e", TRACE_SET, "-o", out, "/bin/cat", probe],
                           pass_fds=(fd,), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60)
        text = ""
        if os.path.exists(out):
            with open(out) as f:
                text = f.read()
        probs += trace_problems(text, p.returncode)
        if not re.search(r'open(at)?\((AT_FDCWD, )?"' + re.escape(probe) + r'", .*\) = \d+$', text, re.M):
            probs.append("self-test-open: the self-test's open is not in the trace")
    return probs


def cmd_tool(a):
    rec = {"check": "tool", "fd" if a.fd is not None else "path": a.fd if a.fd is not None else a.path, "pass": False,
           "problems": []}
    own = a.fd is None
    try:
        if own:
            try:
                fd = _open(a.path)
            except OSError as e:
                rec["problems"].append(f"tool-open: {e.strerror}")
                return _out(rec)
        else:
            fd = a.fd
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                rec["problems"].append("tool-not-regular: not a regular file")
            else:
                rec["sha256"] = sha_fd(fd)
                if rec["sha256"] != a.sha256:
                    rec["problems"].append("tool-sha: the sha256 differs from the pin")
                elif a.self_test:
                    rec["problems"] += _self_test(fd)
        finally:
            if own:
                os.close(fd)
    except OSError as e:
        rec["problems"].append(f"tool-open: {e.strerror}")
    except Exception as e:
        rec["problems"].append(f"internal-error: {type(e).__name__}")
    rec["pass"] = not rec["problems"]
    return _out(rec)


def cmd_trace(a):
    try:
        text = open(a.trace).read() if os.path.exists(a.trace) else ""
        pins = {}
        for x in (a.pin or []) + (a.w_pin or []):
            k, _, v = x.partition("=")
            pins[os.path.normpath(k)] = v
        rec = trace_check(text, a.rc, a.role, a.tune, a.spline, a.spline_sha256, a.cwd, json.load(open(a.record)),
                          json.load(open(a.manifest))["members"], json.load(open(a.private_members))["members"],
                          os.path.normpath(a.w_root), pins)
    except Exception as e:
        rec = {"role": a.role, "tune": a.tune, "pass": False, "problems": [f"internal-error: {type(e).__name__}"]}
    if os.path.exists(a.out):
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 2
    with open(a.out, "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({"check": "trace", "role": a.role, "tune": a.tune, "pass": rec["pass"],
                      "n_problems": len(rec["problems"])}))
    return 0 if rec["pass"] else 1


def cmd_exe(a):
    try:
        probs = exe_problems(a.path or [], json.load(open(a.manifest))["members"], ld_library_path=a.ld_library_path)
        probs += system_tool_problems(a.system_path or [])
    except Exception as e:
        probs = [f"internal-error: {type(e).__name__}"]
    if not a.path:
        probs.append("exe-none: no program given")
    return _out({"check": "exe", "pass": not probs, "paths": a.path or [], "problems": probs})


SLOT2_SPLINE = ("/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL/G1802a00000-k250-e1000/data/"
                "gxspl-NUsmall.xml")


def shape_checks(fd, members, mcheck, tcheck, traces, slot2, fd_dir=FD_DIR):
    """{name: bool}, {name: reason}: the four real-shape checks the director added to slot 1's replay."""
    c, why = {}, {}
    c["real_members_listing"] = (bool(members) and all(k.startswith("genie_xsec/") for k in members)   # no container and mcheck.get("pass") is True
                                 and mcheck.get("n_pinned") == len(members))
    if fd_dir != "/proc/self/fd":
        c["proc_fd_magic_link"], why["proc_fd_magic_link"] = False, "untested-host: no /proc/self/fd"
    else:
        try:
            os.close(os.open(f"{fd_dir}/{fd}", os.O_RDONLY | O_NOFOLLOW))
            eloop = False
        except OSError as e:
            eloop = e.errno == 40           # ELOOP on Linux
        c["proc_fd_magic_link"] = eloop and tcheck.get("pass") is True and tcheck.get("fd") == fd
    c["directory_open_recorded"] = (bool(traces) and all(t.get("pass") is True for t in traces)
                                    and sum(t.get("directories_opened", 0) for t in traces) >= 1)
    g = [x for x in slot2.get("gated", []) if x.get("path") == SLOT2_SPLINE]
    c["slot2_reduce_real_path"] = (slot2.get("pass") is True and slot2.get("spline") == SLOT2_SPLINE
                                   and slot2.get("initial_opened_spline") is True and len(g) == 1
                                   and g[0].get("pinned_by") == "exact pin" and g[0].get("match") is True)
    for k, v in c.items():
        if not v and k not in why:
            why[k] = f"shape-{k.replace('_', '-')}: failed"
    return c, why


def cmd_shape(a):
    try:
        load = lambda f: json.load(open(f))
        c, why = shape_checks(a.fd, load(a.members)["members"], load(a.members_check), load(a.tool_check),
                              [load(t) for t in a.traces], load(a.slot2_reduce))
        probs = sorted(why.values())
    except Exception as e:
        c, probs = {}, [f"internal-error: {type(e).__name__}"]
    return _out({"check": "shape", "checks": c, "pass": bool(c) and all(c.values()) and not probs, "problems": probs})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("members-check")
    m.add_argument("--root", required=True)
    m.add_argument("--members", required=True)
    t = sub.add_parser("tool-check")
    g = t.add_mutually_exclusive_group(required=True)
    g.add_argument("--fd", type=int)
    g.add_argument("--path")
    t.add_argument("--sha256", required=True)
    t.add_argument("--self-test", action="store_true")
    r = sub.add_parser("trace-check")
    for k in ("trace", "role", "tune", "spline", "spline-sha256", "cwd", "record", "manifest", "private-members",
              "w-root", "out"):
        r.add_argument("--" + k, required=True)
    r.add_argument("--rc", type=int, required=True)
    r.add_argument("--pin", action="append")
    r.add_argument("--w-pin", action="append")
    e = sub.add_parser("exe-check")
    e.add_argument("--manifest", required=True)
    e.add_argument("--path", action="append")
    e.add_argument("--ld-library-path")
    e.add_argument("--system-path", action="append")
    s = sub.add_parser("shape-check")
    s.add_argument("--fd", type=int, required=True)
    for k in ("members", "members-check", "tool-check", "slot2-reduce"):
        s.add_argument("--" + k, required=True)
    s.add_argument("--traces", nargs="+", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "tool-check" and a.fd is not None and a.fd < 3:
        ap.error("--fd must be 3 or more")
    return {"members-check": cmd_members, "tool-check": cmd_tool, "trace-check": cmd_trace, "exe-check": cmd_exe,
            "shape-check": cmd_shape}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
