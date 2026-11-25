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
  trace-check --trace F --rc N --role {reduce,graphs,gevgen,gntpc,coverage} --tune T --spline S --spline-sha256 H
              --cwd D --record PG-RECORD.json --manifest genie-manifest.json --private-members G2111a-members.json
              --w-root W [--pin PATH=SHA ...] [--system-pin REALPATH=SHA ...] [--gxmlpath V --xsec-data DIR] --out J
      one traced run (TRACE_SET: the open, access, stat, readlink, chdir and execve families), against the rules
      (RULINGS-A2.md, rounds 1-3):
      - complete: strace's rc 0, a whole last line, no killed process, every unfinished call resumed by the same
        syscall, an exit record for every pid, every exit 0, no undecodable line, no openat2 with a resolve flag;
      - every successful exec: a genie-manifest file with its bytes and real path, or a pinned system tool;
      - the initial process read S (O_PATH is not a read), whose bytes are H; nothing else under a genie_xsec data
        directory, and no other spline, is read (gntpc's role reads none);
      - every gated file read (.xml or .xml.gz, a path with genie, a genie library's name) matches its pin at its own
        path: an exact --pin, the genie manifest or the private members, its real path the manifest's resolution; an
        output is only an O_TRUNC or O_EXCL creation under W that no loader could read as config or code;
      - a config-type file from outside CVMFS, the private product and W fails, and so does an unpinned one in W;
        ROOT's on CVMFS are hashed, with their real path under the repository;
      - a shared library's real path is under CVMFS, a system library directory or the manifest;
      - paths: relative ones against the launch cwd until any process changes directory (then unknown); fchdir and
        a relative watched name against a directory descriptor fail; a '..' path is resolved on the node now
        (realpath of its directory), must stay under an allowed root, and is recorded raw and resolved;
      - for graphs, gevgen and coverage, GXMLPATH is exactly the tune's genie_xsec data directory, each config
        basename is read at the first existing path of GXMLPATH then the record's search_dirs, and every defining
        file is read by the initial process at its expected path, with no link on it (realpath(p) == p).
      Probes of watched names outside W are recorded (W's own names may carry the seed).
  exe-check --manifest genie-manifest.json --path P [--path P ...] [--ld-library-path VALUE] [--system-path S ...]
      each P a genie-product file with the manifest's sha256 and real path; LD_LIBRARY_PATH's entries non-empty and
      under CVMFS, a system library directory or the manifest; each S (awk), itself and its real path, a root-owned
      file under /usr/bin or /bin that only root can write.
  shape-check, host-check
      the real-shape checks on the node (the member listing, the /proc/self/fd magic link, a directory open of
      $GENIE/lib by the gevgen's initial process, slot 2's reduce at its real path), and the three this laptop cannot
      run (a final directory on another mount, no mount inside a walked root, the real strace line for a path holding
      ') = -1').
  revision --repo R; reduce-check --source S --reduced R --script run_gevgen_v3.sh; messenger --laconic L --out M;
  coverage-log --log L; argv-check --script run_gevgen_v3.sh
      the CVMFS revision and root hash; the reduce's completeness for F1's argv pairs; the coverage messenger
      (laconic with only GEVGDriver at DEBUG, pinned); the coverage log (every spline needed was found, none built);
      that gevgen runs only through gevgen_cmd, sealed and coverage argv differing in N, the seed and the messenger.

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
O_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
FD_DIR = "/proc/self/fd" if os.path.isdir("/proc/self/fd") else "/dev/fd"
TRACE_SET = ("trace=open,openat,openat2,access,faccessat,faccessat2,stat,lstat,newfstatat,statx,readlink,readlinkat,"
             "chdir,fchdir,execve")
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
    top_names = sorted(os.listdir(root))
    if top_names != [".upsfiles", "genie_xsec"]:
        probs.append(f"members-top: the products directory holds {top_names}, not exactly .upsfiles and genie_xsec")
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
SYSCALL = re.compile(r"^([a-z0-9_]+)\((.*)$")
RESUMED = re.compile(r"^<\.\.\. ([a-z0-9_]+) resumed>(.*)$")
QUOTED = re.compile(r'"((?:[^"\\]|\\.)*)"')
RESULT = re.compile(r"\)\s+=\s+(-?\d+|\?)(?:\s+([A-Z][A-Z0-9_]+))?(?:\s+\(.*\))?\s*$")
PATH_ARG = {"open": 0, "access": 0, "stat": 0, "lstat": 0, "readlink": 0, "chdir": 0, "execve": 0, "openat": 1,
            "openat2": 1, "faccessat": 1, "faccessat2": 1, "newfstatat": 1, "statx": 1, "readlinkat": 1}
CONFIG_SUFFIX = (".rootmap", ".pcm", ".xml", ".xml.gz")
PROF = "Linux64bit+3.10-2.17-e20-prof"


def trace_problems(text, rc):
    """[problems] with a trace's completeness: strace's rc, a complete last line, a pid on every line, every unfinished
    call resumed by the same syscall, no orphan resumption, a terminal record for every pid, every exit 0."""
    probs = []
    if rc != 0:
        probs.append(f"strace-rc: strace exited {rc}")
    if not text:
        return probs + ["empty: the trace is empty"]
    if not text.endswith("\n"):
        probs.append("truncated: the trace's last line is truncated")
    ms = [LINE.match(ln) for ln in text.splitlines()]
    if not all(ms):
        return probs + ["no-pid: a trace line has no pid"]
    first = ms[0].group(1)
    pending, exits, seen, killed = {}, {}, set(), set()
    for m in ms:
        pid, rest = m.group(1), m.group(2)
        seen.add(pid)
        r = RESUMED.match(rest)
        if r:
            if pending.pop(pid, None) != r.group(1):
                probs.append(f"resume-mismatch: process {pid} resumed {r.group(1)} without its unfinished call")
        elif rest.endswith("<unfinished ...>"):
            sm = SYSCALL.match(rest)
            pending[pid] = sm.group(1) if sm else "?"
        x = re.match(r"\+\+\+ exited with (\d+) \+\+\+", rest)
        if x:
            exits[pid] = int(x.group(1))                     # an exit does not complete a call left unfinished
        if rest.startswith("+++ killed by"):
            probs.append(f"killed: process {pid} was killed")
            killed.add(pid)
    if exits.get(first) != 0:
        probs.append("initial-exit: the initial process did not exit 0")
    probs += [f"child-exit: process {p} exited {x}" for p, x in sorted(exits.items()) if p != first and x != 0]
    if pending:
        probs.append(f"unresumed: calls left unfinished in processes {sorted(pending)}")
    open_ended = sorted(seen - set(exits) - killed)
    if open_ended:
        probs.append(f"no-terminal: processes {open_ended} have no exit record")
    return probs


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
        elif n in "01234567" and n:
            j = i + 1
            while j < len(s) and j < i + 4 and s[j] in "01234567":
                j += 1
            out.append(int(s[i + 1:j], 8))
            i = j
        else:
            out += {"n": "\n", "t": "\t", "r": "\r", "v": "\v", "f": "\f"}.get(n, n).encode()
            i += 2
    return os.fsdecode(bytes(out))


def parse_trace(text):
    """([event], [problems]): each traced call as {pid, call, path, dirfd, ok, errno, flags...}, unfinished calls joined
    to their resumption. A line that is neither a decodable traced call, a signal, nor an exit record is a problem."""
    events, probs, pending = [], [], {}
    for ln in text.splitlines():
        m = LINE.match(ln)
        if not m:
            continue
        pid, rest = m.group(1), m.group(2)
        if rest.startswith(("+++ ", "--- ")):
            continue
        r = RESUMED.match(rest)
        if r:
            if pid not in pending:
                continue                                        # trace_problems reports the orphan
            rest = pending.pop(pid) + r.group(2)
        elif rest.endswith("<unfinished ...>"):
            pending[pid] = rest[: -len("<unfinished ...>")].rstrip()
            continue
        sm = SYSCALL.match(rest)
        if not sm or (sm.group(1) not in PATH_ARG and sm.group(1) != "fchdir"):
            probs.append(f"undecodable: {ln[:200]!r}")
            continue
        call, args = sm.group(1), sm.group(2)
        bare = QUOTED.sub('""', args)
        rm = RESULT.search(bare)
        if not rm:
            probs.append(f"undecodable: {ln[:200]!r}")
            continue
        ok = rm.group(1) not in ("-1", "?")
        if call == "fchdir":
            events.append({"pid": pid, "call": call, "path": None, "dirfd": None, "ok": ok, "errno": None})
            continue
        quoted = QUOTED.findall(args)
        if not quoted:
            probs.append(f"undecodable: {ln[:200]!r}")
            continue
        parts = [x.strip() for x in bare.split(",")]
        flags = ""
        if call in ("open", "openat"):
            k = PATH_ARG[call] + 1
            flags = parts[k].split(")")[0].strip() if len(parts) > k else ""      # the last field carries ") = N"
        elif call == "openat2":
            fm = re.search(r"flags=([A-Z_|0-9]+)", bare)
            flags = fm.group(1) if fm else ""
            res = re.search(r"resolve=([A-Z_|0-9x]+)", bare)
            if res and res.group(1) != "0":
                probs.append(f"openat2-resolve: {ln[:200]!r}")
        fl = set(flags.split("|"))
        events.append({"pid": pid, "call": call, "path": _unescape(quoted[0]),
                       "dirfd": parts[0] if PATH_ARG[call] == 1 else "AT_FDCWD", "ok": ok,
                       "errno": rm.group(2) if not ok else None, "write_only": "O_WRONLY" in fl,
                       "creat": "O_CREAT" in fl, "trunc": "O_TRUNC" in fl, "excl": "O_EXCL" in fl,
                       "directory": "O_DIRECTORY" in fl, "opath": "O_PATH" in fl})
    return events, probs


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


def _xsec_data(p):
    parts = p.split("/")
    return "genie_xsec" in parts and "data" in parts[parts.index("genie_xsec"):-1]


def trace_check(text, rc, role, tune, spline, spline_sha, cwd, record, manifest, private, w_root, pins,
                genie_root=GENIE_ROOT, repo=CVMFS_REPO, private_root=PRIVATE_PRODUCTS, sha=None, system_pins=None,
                gxmlpath=None, xsec_data=None):
    """The check's record: pass, problems (each "<code>: <detail>"), the gated files read, the programs executed,
    ROOT's config files, every watched probe."""
    try:
        return _trace_check(text, rc, role, tune, spline, spline_sha, cwd, record, manifest, private, w_root, pins,
                            genie_root, repo, private_root, sha or sha_path, system_pins or {}, gxmlpath, xsec_data)
    except Exception as e:                                  # fail closed, with a reason no other test expects
        return {"role": role, "tune": tune, "pass": False, "problems": [f"internal-error: {type(e).__name__}"]}


def _trace_check(text, rc, role, tune, spline, spline_sha, cwd, record, manifest, private, w_root, pins, genie_root,
                 repo, private_root, sha, system_pins, gxmlpath, xsec_data):
    probs = trace_problems(text, rc)
    events, pprobs = parse_trace(text)
    probs += pprobs
    lines = text.splitlines()
    first = LINE.match(lines[0]).group(1) if lines and LINE.match(lines[0]) else None
    w_root = os.path.normpath(w_root)
    real_genie = os.path.realpath(genie_root)
    pins = {os.path.normpath(k): v for k, v in pins.items()}
    libnames = {os.path.basename(k) for k, v in manifest.items() if k.split("/")[-2:-1] == ["lib"]}
    allowed = (repo, private_root, w_root) + SYSTEM_LIBS

    def watched(raw):
        b = os.path.basename(raw)
        return (config_type(raw) or "genie" in raw.lower() or b in libnames or _is_so(raw) or raw.startswith("etc/")
                or "/etc/" in raw)

    # paths: relative ones against the launch cwd until any process changes directory, after which they are unknown;
    # a '..' path is resolved on the node now, while W is unchanged (realpath of its directory), and must stay inside
    # an allowed root
    rec = {"role": role, "tune": tune, "spline": os.path.normpath(spline) if spline else None, "n_events": len(events),
           "gated": [], "root_config": [], "probes": [], "execs": [], "dotdot": [], "directories": []}
    chdir_seen = False
    for e in events:
        if e["call"] == "fchdir":
            e["abs"] = None
            if e["ok"]:
                probs.append("fchdir: a traced process changed directory by descriptor")
                chdir_seen = True
            continue
        raw = e["path"]
        if raw.startswith("/"):
            joined = raw
        elif e["dirfd"] != "AT_FDCWD" or chdir_seen:
            joined = None
        else:
            joined = os.path.join(cwd, raw)
        if joined is None:
            e["abs"] = None
            if watched(raw):
                code = "dirfd-relative" if e["dirfd"] not in (None, "AT_FDCWD") else "cwd-unknown"
                probs.append(f"{code}: {e['call']} of {raw!r} cannot be resolved")
        elif ".." in joined.split("/"):
            e["abs"] = os.path.normpath(joined)            # lexical, for a failed probe only
            if e["ok"]:
                try:
                    d, b = os.path.split(joined)
                    res = os.path.realpath(joined if b == ".." else d, strict=True)
                    res = res if b == ".." else os.path.join(res, b)
                except OSError:
                    res = None
                rec["dotdot"].append({"raw": raw, "resolved": res})
                if res is None:
                    probs.append(f"resolve-failed: {raw!r}")
                    e["abs"] = None
                elif not any(_under(res, r) for r in allowed):
                    probs.append(f"dotdot-outside-roots: {raw!r} -> {res}")
                    e["abs"] = None
                else:
                    e["abs"] = res
        else:
            e["abs"] = os.path.normpath(joined)
        if e["call"] == "chdir" and e["ok"]:
            chdir_seen = True
        if watched(raw) and e.get("abs") and not _under(e["abs"], w_root):     # W's own names may hold the seed
            rec["probes"].append({"call": e["call"], "path": e["abs"], "ok": e["ok"], "errno": e["errno"],
                                  "initial": e["pid"] == first})

    def output(e):           # an output: created or truncated under W, and never a name that could be loaded
        p = e["abs"]
        return (e["creat"] and (e["trunc"] or e["excl"]) and _under(p, w_root) and not config_type(p)
                and not p.endswith((".xml", ".xml.gz")) and not _is_so(p))
    opens = [e for e in events if e["call"].startswith("open") and e["ok"] and e["abs"]]
    reads = [e for e in opens if not e["write_only"] and not e["directory"] and not e["opath"] and not output(e)]
    rec["directories"] = [{"path": e["abs"], "initial": e["pid"] == first} for e in opens if e["directory"]]
    rec["directories_opened"] = len(rec["directories"])

    # the programs executed: each a genie-product file with the manifest's bytes, or a pinned system tool
    for e in events:
        if e["call"] != "execve" or not e["ok"] or not e["abs"]:
            continue
        real = os.path.realpath(e["abs"])
        got, bound = None, None
        try:
            if _under(real, real_genie):
                rel, m = _manifest_file(manifest, "genie/v3_04_00/" + os.path.relpath(e["abs"], genie_root))
                want_real = os.path.join(real_genie, rel[len("genie/v3_04_00/"):]) if rel else None
                got = sha(real)
                if want_real == real and m and got == m.get("sha256"):
                    bound = "genie manifest"
            elif real in system_pins:
                got = sha(real)
                if got == system_pins[real]:
                    bound = "system pin"
        except (OSError, Fail):
            got = None
        rec["execs"].append({"path": e["abs"], "real": real, "sha256": got, "bound_by": bound})
        if bound is None:
            probs.append(f"exec-unbound: {e['abs']} -> {real}")

    spl = os.path.normpath(spline) if spline else None
    if spl:
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
        if e["abs"] != spl and (b.startswith("gxspl-") or b.endswith("_CH.xml.gz") or _xsec_data(e["abs"])):
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
            elif not gated:
                real = os.path.realpath(p)
                try:
                    got = sha(real)
                except (OSError, Fail):
                    got = None
                rec["root_config"].append({"path": p, "real": real, "sha256": got})
                if not _under(real, repo):
                    probs.append(f"config-outside-roots: {p} -> {real}")
                elif got is None:
                    probs.append(f"root-config-unhashed: {p}")
    rec["gated"] = sorted(gated_paths.values(), key=lambda x: x["path"])

    if role in ("graphs", "gevgen", "coverage"):
        t = record["tunes"][tune]
        # the search order (GENIE's XmlParserUtils): GXMLPATH's entries, then the tune's search_dirs
        entries = [x for x in (gxmlpath or "").split(":")]
        if gxmlpath is None or any(not x for x in entries) or entries != [os.path.normpath(xsec_data or "")]:
            probs.append(f"gxmlpath: {gxmlpath!r} is not exactly the tune's genie_xsec data directory")
        order = [os.path.normpath(x) for x in entries if x] + [os.path.join(genie_root, d) for d in t["search_dirs"]]

        def exists(d, b):
            p = os.path.join(d, b)
            if _under(p, genie_root):
                return _manifest_file(manifest, "genie/v3_04_00/" + os.path.relpath(p, genie_root))[1] is not None
            if _under(p, private_root):
                return _manifest_file(private, os.path.relpath(p, private_root))[1] is not None
            return os.path.lexists(p)
        cfg_root = os.path.join(genie_root, t["search_dirs"][-1])
        for e in reads:
            p, b = e["abs"], os.path.basename(e["abs"])
            if not p.endswith(".xml") or p == spl or not (_under(p, cfg_root) or any(_under(p, d) for d in order[:len(order) - len(t["search_dirs"])])):
                continue
            want = next((os.path.join(d, b) for d in order if exists(d, b)), None)
            if p != want:
                probs.append(f"search-order: {b} read at {p}, but the search order gives {want}")

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
            if os.path.realpath(p) != p:
                probs.append(f"defining-link: {rel}")
    rec["problems"], rec["pass"] = probs, not probs
    return rec


# ------------------------------------------------------------------------------------------------------------ exe

def system_tool_problems(paths):
    """[problems]: each path itself and its real path under /usr/bin or /bin, a root-owned file only root can write."""
    probs = []
    for p in paths:
        p = os.path.normpath(p) if p else p
        real = os.path.realpath(p) if p else ""
        try:
            st = os.stat(real)
            ok = (bool(p) and all(any(_under(x, r) for r in ("/usr/bin", "/bin")) for x in (p, real))
                  and stat.S_ISREG(st.st_mode) and st.st_uid == 0 and not st.st_mode & 0o022)
        except OSError:
            ok = False
        if not ok:
            probs.append(f"system-tool: {p} -> {real} is not a root-owned file under /usr/bin or /bin")
    return probs


def exe_problems(paths, manifest, genie_root=GENIE_ROOT, ld_library_path=None):
    """[problems]: each program a genie-product file with the manifest's bytes and real path; LD_LIBRARY_PATH's entries
    under CVMFS, the system library directories or a manifest directory, and none empty (an empty entry is the cwd)."""
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
    if ld_library_path:
        dirs = {os.path.normpath("genie/v3_04_00/" + k[len("genie/v3_04_00/"):]) for k, v in manifest.items()
                if v.get("type") == "dir"}
        for entry in ld_library_path.split(":"):
            if not entry:
                probs.append("ld-library-path-empty: an empty LD_LIBRARY_PATH entry searches the working directory")
                continue
            real = os.path.realpath(entry)
            in_manifest = _under(real, real_genie) and os.path.normpath(
                "genie/v3_04_00/" + os.path.relpath(real, real_genie)) in dirs
            if not (in_manifest or any(_under(real, r) for r in (CVMFS_REPO,) + SYSTEM_LIBS)):
                probs.append(f"ld-library-path: {entry} -> {real} is outside CVMFS and the system library directories")
    return probs


# --------------------------------------------------------------------------------------- the spline coverage (D3')

NEED, FOUND, BUILT = "Need xsec spline for ", "Spline was found", "The spline wasn't loaded at initialization"
MESSENGER_LINE = (b'  <priority msgstream="GEVGDriver">                    WARN   </priority>',
                  b'  <priority msgstream="GEVGDriver">                    DEBUG  </priority>')
LACONIC_SHA256 = "13169e5b5b3f1d9a78a632982c70fbb47eb6f7f44451cbe006d6959e63e58129"     # = the genie manifest's
MESSENGER_SHA256 = "aaf85992b47174aa47ae6e5d2c609e48e000ee879eaf256addd77a83b63e62e8"


def messenger(laconic_bytes):
    """The coverage run's messenger: Messenger_laconic.xml with only GEVGDriver raised to DEBUG, or a Fail."""
    if hashlib.sha256(laconic_bytes).hexdigest() != LACONIC_SHA256:
        raise Fail("messenger-laconic: Messenger_laconic.xml differs from its pin")
    if laconic_bytes.count(MESSENGER_LINE[0]) != 1:
        raise Fail("messenger-line: the GEVGDriver line is not there exactly once")
    out = laconic_bytes.replace(*MESSENGER_LINE)
    if hashlib.sha256(out).hexdigest() != MESSENGER_SHA256:
        raise Fail("messenger-sha: the coverage messenger differs from its pin")
    return out


def coverage_problems(log_text):
    """[problems]: every 'Need xsec spline for X' answered by 'Spline was found' before the next one, none built."""
    probs, need, n = [], None, 0
    for ln in log_text.splitlines():
        if NEED in ln:
            if need is not None:
                probs.append(f"coverage-unanswered: {need}")
            need, n = ln.split(NEED, 1)[1].strip(), n + 1
        elif FOUND in ln:
            if need is None:
                probs.append("coverage-orphan: a 'Spline was found' with no spline asked for")
            need = None
        elif BUILT in ln:
            probs.append(f"coverage-built: GENIE computed a spline the pinned file lacks ({need})")
            need = None
    if need is not None:
        probs.append(f"coverage-unanswered: {need}")
    if n == 0:
        probs.append("coverage-none: the log names no spline needed")
    return probs


def argv_pairs(script_text):
    """{(probe pdg, target pdg)}: F1's gevgen argv in run_gevgen_v3.sh (gevgen_cmd's -p and -t)."""
    body = re.search(r"^gevgen_cmd\(\) \{(.*?)^\}", script_text, re.S | re.M)
    if not body:
        raise Fail("argv-none: run_gevgen_v3.sh has no gevgen_cmd")
    p = re.search(r"^\s*-p (\S+) \\$", body.group(1), re.M)
    t = re.search(r"^\s*-t '([^']+)' \\$", body.group(1), re.M)
    if not (p and t):
        raise Fail("argv-none: gevgen_cmd has no -p or -t")
    probes = p.group(1).split(",")
    targets = [re.sub(r"\[.*\]$", "", x) for x in t.group(1).split(",")]
    return {(a, b) for a in probes for b in targets}


def argv_problems(script_text):
    """[problems]: gevgen runs only through gevgen_cmd (F1's argv, from N, SEED and MSG); the genie and coverage modes
    each call it once with no arguments, and coverage sets exactly N=1, the public seed and its messenger file: so their
    argv differ in the event count, the seed and the messenger only."""
    probs = []
    calls = re.findall(r"^[ \t]*(?:\"\$\{PG_TRACE\[@\]\}\" )?gevgen\b(?!_cmd)", script_text, re.M)
    if len(calls) != 1:
        probs.append(f"argv-gevgen: gevgen is invoked {len(calls)} times, not once inside gevgen_cmd")
    uses = re.findall(r"^[ \t]+gevgen_cmd(.*)$", script_text, re.M)            # the calls, indented; not the definition
    if uses != [" > gevgen.log 2>&1", " > gevgen.log 2>&1"]:
        probs.append(f"argv-modes: gevgen_cmd is called as {uses}")
    cov = re.search(r"^  coverage\)(.*?)^    ;;$", script_text, re.M | re.S)
    gen = re.search(r"^  genie\)(.*?)^    ;;$", script_text, re.M | re.S)
    if not (cov and gen) or '    N=1; SEED=123456789; MSG="$MSGFILE"' not in cov.group(1).splitlines():
        probs.append("argv-coverage: the coverage mode does not set exactly N=1, the public seed and its messenger")
    elif not re.search(r"^    TUNE=\$1; SPLDIR=\$2; N=\$3; SEED=\$4; WORK=\$5; FLUX=\$6$", gen.group(1), re.M) or \
            '    MSG="$GENIE/config/Messenger_laconic.xml"' not in gen.group(1).splitlines():
        probs.append("argv-genie: the genie mode's N, SEED or MSG is not F1's")
    return probs


def _spline_keys(path):
    """{(nu, tgt): {spline name: nknots}} of a GENIE spline XML (gzipped or not), streamed."""
    import gzip
    op = gzip.open if path.endswith(".gz") else open
    out = {}
    with op(path, "rt", errors="replace") as f:
        for ln in f:
            if "<spline " not in ln:
                continue
            name = re.search(r'name="([^"]+)"', ln)
            kn = re.search(r'nknots="(\d+)"', ln)
            if not name:
                continue
            fields = dict(re.findall(r"(?:^|[;/])(nu|tgt):([^;]+)", name.group(1)))   # genie::Alg/Cfg/nu:14;tgt:...
            out.setdefault((fields.get("nu"), fields.get("tgt")), {})[name.group(1)] = kn.group(1) if kn else None
    return out


def reduce_problems(source, reduced, pairs):
    """[problems]: for every (nu, target) in F1's argv, the reduced spline holds exactly the source's splines, with
    the same knot counts."""
    src, red, probs = _spline_keys(source), _spline_keys(reduced), []
    for pair in sorted(pairs):
        s, r = src.get(pair, {}), red.get(pair, {})
        if not s:
            probs.append(f"reduce-pair-absent: the source has no spline for nu {pair[0]} on {pair[1]}")
        if s != r:
            probs.append(f"reduce-incomplete: nu {pair[0]} on {pair[1]}: {len(s)} source splines, {len(r)} kept, "
                         f"{len(set(s) ^ set(r))} differ by name, "
                         f"{sum(1 for k in set(s) & set(r) if s[k] != r[k])} by knots")
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


def _kv(xs):
    out = {}
    for x in xs or []:
        k, _, v = x.partition("=")
        out[os.path.normpath(k)] = v
    return out


def cmd_trace(a):
    try:
        text = open(a.trace).read() if os.path.exists(a.trace) else ""
        pins = _kv((a.pin or []) + (a.w_pin or []))
        rec = trace_check(text, a.rc, a.role, a.tune, a.spline or None, a.spline_sha256, a.cwd, json.load(open(a.record)),
                          json.load(open(a.manifest))["members"], json.load(open(a.private_members))["members"],
                          os.path.normpath(a.w_root), pins, system_pins=_kv(a.system_pin), gxmlpath=a.gxmlpath,
                          xsec_data=a.xsec_data)
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
    return _out({"check": "exe", "pass": not probs, "paths": a.path or [], "ld_library_path": a.ld_library_path,
                 "system_paths": a.system_path or [], "problems": probs})


def cmd_revision(a):
    try:
        rec = {k: os.getxattr(a.repo, "user." + k).decode() for k in ("revision", "root_hash")}
        probs = [f"revision-empty: {k}" for k, v in rec.items() if not v.strip()]
    except (OSError, AttributeError) as e:
        rec, probs = {}, [f"revision-unreadable: {type(e).__name__}"]
    except Exception as e:
        rec, probs = {}, [f"internal-error: {type(e).__name__}"]
    return _out(dict(rec, check="revision", repo=a.repo, problems=probs, **{"pass": not probs}))


def cmd_reduce(a):
    try:
        probs = reduce_problems(a.source, a.reduced, argv_pairs(open(a.script).read()))
    except Fail as e:
        probs = [str(e)]
    except OSError as e:
        probs = [f"reduce-unreadable: {e.strerror}"]
    except Exception as e:
        probs = [f"internal-error: {type(e).__name__}"]
    return _out({"check": "reduce", "pass": not probs, "problems": probs})


def cmd_messenger(a):
    try:
        if os.path.lexists(a.out):
            raise Fail(f"messenger-exists: {a.out} already exists")
        fd = _open(a.laconic)
        try:
            data = b"".join(iter(lambda: os.read(fd, 1 << 20), b""))
        finally:
            os.close(fd)
        out = messenger(data)
        with open(a.out, "xb") as f:
            f.write(out)
        probs = []
    except Fail as e:
        probs = [str(e)]
    except OSError as e:
        probs = [f"messenger-io: {e.strerror}"]
    except Exception as e:
        probs = [f"internal-error: {type(e).__name__}"]
    return _out({"check": "messenger", "pass": not probs, "sha256": None if probs else MESSENGER_SHA256,
                 "problems": probs})


def cmd_coverage(a):
    try:
        text = open(a.log, errors="replace").read()
        probs = coverage_problems(text)
        h = hashlib.sha256(text.encode()).hexdigest()
    except OSError as e:
        probs, h = [f"coverage-unreadable: {e.strerror}"], None
    except Exception as e:
        probs, h = [f"internal-error: {type(e).__name__}"], None
    return _out({"check": "coverage", "pass": not probs, "log_sha256": h, "problems": probs})


def cmd_argv(a):
    try:
        probs = argv_problems(open(a.script).read())
    except Exception as e:
        probs = [f"internal-error: {type(e).__name__}"]
    return _out({"check": "argv", "pass": not probs, "problems": probs})


SLOT2_SPLINE = ("/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL/G1802a00000-k250-e1000/data/"
                "gxspl-NUsmall.xml")
GENIE_LIB = f"{GENIE_ROOT}/{PROF}/lib"


def shape_checks(fd, members, mcheck, tcheck, traces, slot2, fd_dir=FD_DIR, genie_lib=GENIE_LIB):
    """{name: bool}, {name: reason}: the real-shape checks the director added to slot 1's replay."""
    c, why = {}, {}
    no_container = bool(members) and all(k.startswith("genie_xsec/") for k in members)
    c["real_members_listing"] = (no_container and mcheck.get("pass") is True
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
    gev = [t for t in traces if t.get("role") == "gevgen"]
    c["directory_open_recorded"] = (bool(traces) and all(t.get("pass") is True for t in traces) and len(gev) == 1
                                    and any(d.get("path") == genie_lib and d.get("initial") is True
                                            for d in gev[0].get("directories", [])))
    g = [x for x in slot2.get("gated", []) if x.get("path") == SLOT2_SPLINE]
    c["slot2_reduce_real_path"] = (slot2.get("pass") is True and slot2.get("spline") == SLOT2_SPLINE
                                   and slot2.get("initial_opened_spline") is True and len(g) == 1
                                   and g[0].get("pinned_by") == "exact pin" and g[0].get("match") is True)
    for k, v in c.items():
        if not v and k not in why:
            why[k] = f"shape-{k.replace('_', '-')}: failed"
    return c, why


def submounts(mountinfo_text, roots):
    """The mount points (mountinfo's fifth field, octal-escaped) that lie strictly inside a root."""
    points = [_unescape(ln.split()[4]) for ln in mountinfo_text.splitlines() if len(ln.split()) > 4]
    return sorted({p for p in points for r in roots if p != r and _under(p, r)})


def host_checks(fd, tmp, roots, mountinfo_text=None, fd_dir=FD_DIR, run=subprocess.run):
    """{name: bool}, {name: reason}: the three checks this laptop cannot run, recorded on the node before slot 2.
    st_dev_final_dir: a walk from / into proc (another mount) refuses at the final directory (a positive control);
    no_submounts: no mount point lies inside a walked root (from /proc/self/mountinfo);
    result_anchor_real_strace: the pinned strace's own line for a path holding ') = -1' parses to that path, read."""
    c, why = {}, {}
    if not os.path.isdir("/proc/self"):
        return {k: False for k in ("st_dev_final_dir", "no_submounts", "result_anchor_real_strace")}, {
            k: "untested-host: no /proc" for k in ("st_dev_final_dir", "no_submounts", "result_anchor_real_strace")}
    rfd = os.open("/", os.O_RDONLY | O_DIRECTORY)
    try:
        nfd = os.open("proc", os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW, dir_fd=rfd)
        c["st_dev_final_dir"] = os.fstat(nfd).st_dev != os.fstat(rfd).st_dev
        os.close(nfd)
    finally:
        os.close(rfd)
    text = mountinfo_text if mountinfo_text is not None else open("/proc/self/mountinfo").read()
    inside = submounts(text, roots)
    c["no_submounts"] = not inside
    if inside:
        why["no_submounts"] = f"host-submount: mount points inside the walked roots: {inside}"
    name = os.path.join(tmp, "pg) = -1 ENOENT.xml")
    with open(name, "w") as f:
        f.write("x")
    out = os.path.join(tmp, "anchor.trace")
    p = run([f"{fd_dir}/{fd}", "-f", "-q", "-e", TRACE_SET, "-o", out, "/bin/cat", name], pass_fds=(fd,),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    ev, pp = parse_trace(open(out).read() if os.path.exists(out) else "")
    hit = [e for e in ev if e["call"].startswith("open") and e["path"] == name]
    c["result_anchor_real_strace"] = p.returncode == 0 and not pp and len(hit) == 1 and hit[0]["ok"]
    for k, v in c.items():
        if not v and k not in why:
            why[k] = f"host-{k.replace('_', '-')}: failed"
    return c, why


def cmd_host(a):
    try:
        c, why = host_checks(a.fd, a.tmp, [os.path.normpath(r) for r in a.root])
        probs = sorted(why.values())
    except Exception as e:
        c, probs = {}, [f"internal-error: {type(e).__name__}"]
    return _out({"check": "host", "checks": c, "pass": bool(c) and all(c.values()) and not probs, "problems": probs})


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
    for k in ("trace", "tune", "spline", "spline-sha256", "cwd", "record", "manifest", "private-members", "w-root",
              "out"):
        r.add_argument("--" + k, required=True)
    r.add_argument("--role", required=True, choices=("reduce", "graphs", "gevgen", "gntpc", "coverage"))
    r.add_argument("--rc", type=int, required=True)
    r.add_argument("--pin", action="append")
    r.add_argument("--w-pin", action="append")
    r.add_argument("--system-pin", action="append")
    r.add_argument("--gxmlpath")
    r.add_argument("--xsec-data")
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
    v = sub.add_parser("revision")
    v.add_argument("--repo", required=True)
    d = sub.add_parser("reduce-check")
    for k in ("source", "reduced", "script"):
        d.add_argument("--" + k, required=True)
    g2 = sub.add_parser("messenger")
    g2.add_argument("--laconic", required=True)
    g2.add_argument("--out", required=True)
    c = sub.add_parser("coverage-log")
    c.add_argument("--log", required=True)
    w = sub.add_parser("argv-check")
    w.add_argument("--script", required=True)
    h = sub.add_parser("host-check")
    h.add_argument("--fd", type=int, required=True)
    h.add_argument("--tmp", required=True)
    h.add_argument("--root", action="append", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "tool-check" and a.fd is not None and a.fd < 3:
        ap.error("--fd must be 3 or more")
    return {"members-check": cmd_members, "tool-check": cmd_tool, "trace-check": cmd_trace, "exe-check": cmd_exe,
            "shape-check": cmd_shape, "revision": cmd_revision, "reduce-check": cmd_reduce,
            "messenger": cmd_messenger, "coverage-log": cmd_coverage, "argv-check": cmd_argv,
            "host-check": cmd_host}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
