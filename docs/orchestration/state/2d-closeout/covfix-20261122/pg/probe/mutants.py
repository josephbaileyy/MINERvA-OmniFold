"""Hand mutants of pg-probe.py (rev 4) and pg-probe-launch.py, under the director's kill rule (../mutrun.py,
mutrun.RULE, 2026-11-25): an import or collection error is INVALID; otherwise a FAIL or an ERROR with a non-zero exit
in test_pg_probe.py kills; a timeout, or a FAIL with exit 0, is INVALID and counts against it.

Run: python3 -B mutants.py > mutants.log   (from this directory; every mutant runs in a throwaway copy)
"""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
_s = importlib.util.spec_from_file_location("mutrun", HERE.parent / "mutrun.py")
R = importlib.util.module_from_spec(_s)
_s.loader.exec_module(R)
D = "docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe"
PR, LA = f"{D}/pg-probe.py", f"{D}/pg-probe-launch.py"
M = [(f, old, new, what, "probe") for f, old, new, what in [
    # identity and the repository
    (PR, '    if not rec["identity"]["pass"]:', '    if False:', "identity not enforced"),
    (PR, '    if os.path.realpath(repo) != repo:\n        probs.append', '    if False:\n        probs.append',
     "a repository path through a link"),
    (PR, '    if mp not in (repo, os.path.dirname(repo)) or typ is None or typ in LOCAL_FS:',
     '    if typ is None:', "the repository's mount not checked"),
    (PR, '    if rec["xattrs"].get("user.fqrn") != FQRN:', '    if False:', "fqrn not required"),
    (PR, '    if rec["repo"]["pass"]:\n', '    if True:\n', "pins read on an unverified repository"),
    # reading by descriptor
    (PR, '            nfd = os.open(p, os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW, dir_fd=fd)',
     '            nfd = os.open(p, os.O_RDONLY | O_DIRECTORY, dir_fd=fd)', "links followed in directory components"),
    (PR, '        return os.open(name, flags | O_NOFOLLOW | O_NOATIME, dir_fd=dirfd)',
     '        return os.open(name, flags | O_NOATIME, dir_fd=dirfd)', "a pinned file through a link"),
    (PR, '    if not rel or rel.startswith("/") or any(p in ("", ".", "..") for p in parts):',
     '    if not rel:', "odd relative paths walked"),
    (PR, '        except FileNotFoundError:\n            return None\n    finally:',
     '        except FileNotFoundError:\n            return []\n    finally:', "an absent pinned directory"),
    # the genie product
    (PR, '    if os.path.realpath(genie_root) != genie_root:', '    if False:', "a genie root through a link"),
    (PR, '            got, err = _try(sha_rel, rfd, rel)\n            rec["files"][rel] = {"sha256": got, "match": got == want,',
     '            got, err = _try(sha_rel, rfd, rel)\n            rec["files"][rel] = {"sha256": got, "match": got is not None,',
     "file bytes not compared"),
    (PR, '            got, err = _try(sha_rel, rfd, f"{XSEC_REL}/{rel}")\n            rec["files"][rel] = {"sha256": got, "match": got == want,',
     '            got, err = _try(sha_rel, rfd, f"{XSEC_REL}/{rel}")\n            rec["files"][rel] = {"sha256": got, "match": got is not None,',
     "spline bytes not compared"),
    (PR, '            rec["links"][rel] = {"target": got, "match": got == want,',
     '            rec["links"][rel] = {"target": got, "match": True,', "link targets not compared"),
    (PR, '"match": err is None and got == want,', '"match": err is None,', "listings not compared"),
    (PR, '        bad = sorted(k for k, v in rec[kind].items() if not v["match"])\n        if bad:',
     '        bad = sorted(k for k, v in rec[kind].items() if not v["match"])\n        if False:',
     "genie mismatches not a stop"),
    # genie_xsec
    (PR, '            elif shadow:', '            elif False:', "config-like data/ names"),
    # tools
    (PR, '            if not r["rpm_match"]:\n                r["problem"]', '            if False:\n                r["problem"]',
     "an RPM mismatch accepted"),
    (PR, '            fd = fcntl.fcntl(low, fcntl.F_DUPFD, 10)', '            fd = os.dup(low)', "a tool on fd 3"),
    (PR, '        os.lseek(fd, 0, os.SEEK_SET)\n        r["sha256"]', '        r["sha256"]', "the offset left at the end"),
    # the strace self-test
    (PR, '        if not re.search(r\'open(at)?\\((AT_FDCWD, )?"\' + re.escape(probe)',
     '        if False and not re.search(r\'open(at)?\\((AT_FDCWD, )?"\' + re.escape(probe)', "the self-test's open"),
    (PR, '    if not text.endswith("\\n"):', '    if False:', "a truncated trace"),
    # gpg
    (PR, '              if os.path.realpath(os.path.dirname(v)) != real_sd]', '              if not _inside(v, home) and not _inside(v, real_sd)]',
     "sockets outside the reported socket dir"),
    (PR, '        if sd != want:', '        if not sd.startswith(os.path.dirname(want) + "/d."):', "the socket dir hash"),
    (PR, '        if mount_fs(sd, mounts_text) != "tmpfs":', '        if False:', "the socket dir's mount"),
    (PR, '        if not rec["confined"]:\n            raise RuntimeError', '        if False:\n            raise RuntimeError',
     "gpg run on unconfined sockets"),
    (PR, '        rec["confined"] = ok and ld.returncode == 0', '        rec["confined"] = ok', "a failing --list-dirs"),
    (PR, '        if home and crypto:', '        if home:', "commands after a failed preflight"),
    (PR, '        rec["gpg_started"] = crypto = True', '        rec["gpg_started"] = True\n        crypto = rec.get("pass")',
     "no agent identification after a crypto failure"),
    (PR, '            if outside and gone:', '            if outside:', "sockets removed before the agent is gone"),
    (PR, 'rec["socketdir_absent"] = _confirmed_absent(canonical) if canonical else False', 'rec["socketdir_absent"] = True',
     "socket dir absence"),
    (PR, '                       and rec.get("agent_gone")\n', '                       and True\n', "a surviving agent"),
    (PR, '\n                       and rec.get("gpgconf_kill_rc") == 0\n', '\n', "a failed kill"),
    (PR, ' and rec.get("gnupghome_mode") == "0o700"\n', '\n', "mode 700"),
    (PR, 'and rc_t == 2 and rec["tampered"]["evidence"]', 'and rc_t != 0', "a crash counts as a refusal"),
    (PR, 'and rc_w == 2\n                       and rec["wrong_passphrase"]["evidence"]', 'and rc_w != 0\n                       and True',
     "wrong passphrase evidence"),
    (PR, '    if rec["parent_fs"] not in LOCAL_FS:', '    if False:', "a network parent"),
    (PR, '    if _fd_open(3):\n        raise RuntimeError', '    if False:\n        raise RuntimeError', "fd 3 clobbered"),
    (PR, '        if not _fd_open(fd):', '        if False:', "closed standard fds"),
    (PR, '    bad[last[0] + last[1] - 1] ^= 0x01', '    bad[len(bad) // 2] ^= 0x01', "tamper not in the MDC"),
    (PR, '                    if not partial:\n                        break', '                    break', "partial lengths"),
    # the launcher
    (LA, '    if got != argv[0]:', '    if False:', "sha check removed"),
    (LA, 'os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW', 'os.O_RDWR | os.O_CREAT | os.O_TRUNC', "output not reserved"),
    (LA, '    if len(hits) != 1 or not lines or lines[-1] != hits[0]:', '    if not hits:', "receipt shape"),
    (LA, '    if v not in RC_FOR or RC_FOR[v] != rc:', '    if v not in RC_FOR:', "verdict/rc mismatch"),
    (LA, '    return p.returncode if ok else 4', '    return p.returncode', "invalid receipt exit"),
    (LA, '        return p + ([] if stops else ["a STOP with no stops"])', '        return p', "a STOP without stops"),
    (LA, '    if v != "GO":\n        return p\n', '    if True:\n        return p\n', "a GO's evidence not required"),
    (LA, '    if not _is(rec.get("pins_sha256"), want) or', '    if False and', "the receipt's pins"),
    (LA, '(("repo", "xattrs", "user.fqrn"), FQRN),', '', "the fqrn in a GO"),
    (LA, '                or not all(isinstance(x, dict) and _is(x.get("match"), True) for x in got.values()):',
     '                or False:', "a mismatch in a GO"),
    (LA, '        p.append("required qualifiers")', '        pass', "qualifiers in a GO"),
    (LA, 'and x.get("config_like") == []', 'and True', "config-like names in a GO"),
    (LA, '    if not _hex64(_get(rec, "xsec", "dbconfig", "sha256")):', '    if False:', "dbconfig in a GO"),
    (LA, '(("socketdir_absent",), True), ', '', "gpg socket dir absence in a GO"),
    (LA, '(("gpg_started",), True), ', '', "gpg started in a GO"),
    (LA, '    return type(got) is type(want) and got == want', '    return got == want', "1 taken for True"),
    (LA, '        digest = _sha_through(fd)', '        digest = hashlib.sha256(open(out_path, "rb").read()).hexdigest()',
     "footer hash by pathname"),
    (LA, 'SSH_OPTS = ["-F", "/dev/null", ', 'SSH_OPTS = [', "user ssh config used"),
    (LA, '"-o", "ForwardAgent=no", ', '', "agent forwarding allowed"),
    (LA, 'REMOTE = "env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -"',
     'REMOTE = "/usr/bin/python3.11 -I -B -"', "remote environment not minimal"),
    (LA, 'input=body,', 'input=open(probe_path, "rb").read() + b"\\n",', "sent bytes differ from hashed bytes"),
    # agy's read of 135571b9 and the director's GO (2026-11-24)
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '            probs.append(f"repo-xattr: xattr {k}: {type(e).__name__}: {e}")', '            pass', 'unreadable xattrs pass'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '        st = os.fstat(fd)\n        if not stat.S_ISREG(st.st_mode):', '        st = os.fstat(fd)\n        if False:', 'non-regular pinned file'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '            if missing:\n                rec["problems"].append(f"xsec-qualifiers:', '            if False:\n                rec["problems"].append(f"xsec-qualifiers:', 'a qualifier missing'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '    if bad:\n        rec["problems"].append(f"xsec-files:', '    if False:\n        rec["problems"].append(f"xsec-files:', 'a spline mismatch not a stop'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '        if got is None:\n            rec["problems"].append(f"xsec-dbconfig: {err}")', '        if False:\n            rec["problems"].append(f"xsec-dbconfig: {err}")', 'no dbconfig'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '        probs.append(f"strace-rc: strace exited {rc}")', '        pass', "strace's rc"),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '        if rest.startswith("+++ killed by"):\n            probs.append(f"killed: process {pid} was killed")', '        if False:\n            probs.append(f"killed: process {pid} was killed")', 'a killed tracee'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '        return probs + ["empty: the trace is empty"]', '        return probs', 'an empty trace'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '    probs += [f"child-exit: process {q} exited {v}" for q, v in sorted(exits.items()) if q != first and v != 0]\n', '', "a child's non-zero exit"),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '    if pending:\n        probs.append(f"unresumed:', '    if False:\n        probs.append(f"unresumed:', 'an unresumed call'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '            if os.fstat(fd).st_dev != dev:\n                raise Unverified(f"{rel}: {p} is another mount")', '            if False:\n                pass', 'a walk crossing a mount'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '            if st.st_dev != dev:\n                raise Unverified(f"{rel}/{n} is another mount")', '            if False:\n                pass', 'a listed entry on another mount'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '        if k in rec["xattrs"] and not str(rec["xattrs"][k]).strip():', '        if False:', 'an empty revision or root hash'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', 'if not (n in DATA_NAMES or re.fullmatch(r"gxspl-[A-Za-z]+\\.xml(\\.gz)?", n))]', 'if n.endswith((".xml", ".xml.gz")) and not n.startswith("gxspl-")]', 'data/ by suffix, not an allowlist'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/make_pins.py', '        xsec[f"{qualifier(t)}/ups/genie_xsec.table"] = s["ups_table_sha256"]     # setup executes it\n', '', 'genie_xsec.table unpinned'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', 'not st.st_mode & (0o077 if private else 0o022)', 'not st.st_mode & (0o077 if private else 0)', 'a writable /run/user/<uid>'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '    probs += [f"socket-link: {k} {v} is a link" for k, v in sorted(socks.items()) if os.path.islink(v)]\n', '', 'a socket that is a link'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '"stops": [f"internal-error: {type(e).__name__}"]}', '"stops": [f"repo: {type(e).__name__}"]}', 'a crash posing as another stop'),
    # round 3: agy (16bbb74c) and codex-school (f23847ad) reads of 5f141f7a, the director's GO and D1-D8
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '        st = os.stat(name, dir_fd=dfd, follow_symlinks=False)\n        if not stat.S_ISLNK(st.st_mode):', '        st = os.stat(name, dir_fd=dfd, follow_symlinks=False)\n        if False:', 'a pinned link that is not a link'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe-launch.py', '        if not isinstance(got, dict) or sorted(got) != sorted(want_) \\\n', '        if not isinstance(got, dict) \\\n', 'a pinned item left out'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe-launch.py', '        elif not all(got[k].get(field) == want_[k] for k in want_):', '        elif False:', 'r3: a claimed match with another value'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe-launch.py', '            elif not ((t.get("rpm_match") is True and t.get("rpm_status") == "recorded"', '            elif False and ((t.get("rpm_match") is True and t.get("rpm_status") == "recorded"', "r3: a tool's RPM basis"),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', ' and stat.S_ISREG(os.lstat(p).st_mode)), None)', '), None)', 'r3: a linked first candidate taken'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '    if out is None or out[0] != 0 or not out[1].strip():\n        raise Unverified("the RPM query failed")', '    if out is None or out[0] != 0 or not out[1].strip():\n        return None, None, None', 'r3: a failed RPM query as no record'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '    if repo is not None and os.fstat(rfd).st_dev != os.stat(repo, follow_symlinks=False).st_dev:', '    if False:', 'r3: a mount at the genie product'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '         "awk": ("/usr/bin/gawk", "/bin/gawk", "/usr/bin/awk")}', '         }', 'r3: awk unpinned'),
    # the director's ruling: guards this host cannot reach by a real mount or race, tested by injection
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '        if not stat.S_ISREG(os.fstat(fd).st_mode):\n            os.close(fd)\n            r["problem"] = "not a regular file"', '        if False:\n            os.close(fd)\n            r["problem"] = "not a regular file"', 'a tool that changes after its lstat (injected)'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '        if os.fstat(fd).st_dev != dev:\n            raise Unverified(f"{rel} is another mount")', '        if False:\n            raise Unverified(f"{rel} is another mount")', "r3: list_rel's final directory on another device (injected)"),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '    if not rec["mount_control"]["pass"]:', '    if False:', 'r3: a failed mount control'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '        list_rel(fd, rel)\n        return {"pass": False, "refused": None}', '        list_rel(fd, rel)\n        return {"pass": True, "refused": None}', 'r3: a mount control that never refused'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe-launch.py', '(("mount_control", "pass"), True), ', '', 'r3: the launcher ignores the mount control'),
    # round 4 (RULINGS-A2.md, round 4)
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', 'chdir,fchdir,execve,execveat,rename', 'chdir,fchdir,execve,rename', "r4: the probe's trace set"),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '            if pending.pop(pid, None) != r.group(1):', '            if False:', 'r4: a resumed call of another syscall'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '    if open_ended:\n        probs.append(f"no-terminal', '    if False:\n        probs.append(f"no-terminal', 'r4: a pid with no exit'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '    if dump is None or dump[0] != 0:\n        raise Unverified', '    if False:\n        raise Unverified', 'r4: a failed RPM dump as first use'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '    if digest is None:\n        raise Unverified', '    if False:\n        raise Unverified', 'r4: an owned file missing from its dump'),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '    return {"options": opts[-1], "hidepid": hp[-1] if hp else "0"}', '    return {"options": opts[-1], "hidepid": hp[-1] if hp else None}', "r4: hidepid's default"),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe.py', '    rec["proc_mount"] = proc_mount(mounts_text)\n', '', "r4: /proc's mount not recorded"),
    ('docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe/pg-probe-launch.py', '        p.append("proc_mount is not recorded")', '        pass', "r4: the launcher without /proc's record"),
]]

if __name__ == "__main__":
    raise SystemExit(R.main(M))
