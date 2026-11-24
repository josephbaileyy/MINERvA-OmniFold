"""Hand mutants of pg-probe.py (rev 4) and pg-probe-launch.py, under the director's kill rule (../mutrun.py): only an
assertion FAIL in test_pg_probe.py kills; import errors, other errors and timeouts are INVALID and count against it.

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
    (PR, '        except (OSError, AttributeError) as e:\n            probs.append(f"xattr',
     '        except (OSError, AttributeError) as e:\n            0 and probs.append(f"xattr', "unreadable xattrs pass"),
    (PR, '    if rec["repo"]["pass"]:\n', '    if True:\n', "pins read on an unverified repository"),
    # reading by descriptor
    (PR, '            nfd = os.open(p, os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW, dir_fd=fd)',
     '            nfd = os.open(p, os.O_RDONLY | O_DIRECTORY, dir_fd=fd)', "links followed in directory components"),
    (PR, '        return os.open(name, flags | O_NOFOLLOW | O_NOATIME, dir_fd=dirfd)',
     '        return os.open(name, flags | O_NOATIME, dir_fd=dirfd)', "a pinned file through a link"),
    (PR, '    if not rel or rel.startswith("/") or any(p in ("", ".", "..") for p in parts):',
     '    if not rel:', "odd relative paths walked"),
    (PR, '        if not stat.S_ISREG(os.fstat(fd).st_mode):\n            raise Unverified(f"{rel} is not a regular file")',
     '        if False:\n            raise Unverified(f"{rel} is not a regular file")', "non-regular pinned file"),
    (PR, '        if not stat.S_ISLNK(os.stat(name, dir_fd=dfd, follow_symlinks=False).st_mode):',
     '        if False:', "a pinned link that is not a link"),
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
    (PR, '            if missing:\n                rec["problems"].append(f"required qualifiers missing',
     '            if False:\n                rec["problems"].append(f"required qualifiers missing', "a qualifier missing"),
    (PR, '            elif shadow:', '            elif False:', "config-like data/ names"),
    (PR, '    bad = sorted(k for k, v in rec["files"].items() if not v["match"])\n    if bad:\n        rec["problems"].append(f"{len(bad)} genie_xsec',
     '    bad = sorted(k for k, v in rec["files"].items() if not v["match"])\n    if False:\n        rec["problems"].append(f"{len(bad)} genie_xsec',
     "a spline mismatch not a stop"),
    (PR, '        if got is None:\n            rec["problems"].append(f"dbconfig: {err}")',
     '        if False:\n            rec["problems"].append(f"dbconfig: {err}")', "no dbconfig"),
    # tools
    (PR, '            if not r["rpm_match"]:\n                r["problem"]', '            if False:\n                r["problem"]',
     "an RPM mismatch accepted"),
    (PR, '            fd = fcntl.fcntl(low, fcntl.F_DUPFD, 10)', '            fd = os.dup(low)', "a tool on fd 3"),
    (PR, '        os.lseek(fd, 0, os.SEEK_SET)\n        r["sha256"]', '        r["sha256"]', "the offset left at the end"),
    (PR, '        if not stat.S_ISREG(os.fstat(fd).st_mode):\n            os.close(fd)\n            r["problem"] = "not a regular file"',
     '        if False:\n            os.close(fd)\n            r["problem"] = "not a regular file"', "a non-regular tool"),
    # the strace self-test
    (PR, '        if not re.search(r\'open(at)?\\((AT_FDCWD, )?"\' + re.escape(probe)',
     '        if False and not re.search(r\'open(at)?\\((AT_FDCWD, )?"\' + re.escape(probe)', "the self-test's open"),
    (PR, '    if rc != 0:\n        probs.append(f"strace exited {rc}")', '    if False:\n        probs.append(f"strace exited {rc}")',
     "strace's rc"),
    (PR, '    if any("+++ killed by" in ln for ln in lines):', '    if False:', "a killed tracee"),
    (PR, '    if not text.endswith("\\n"):', '    if False:', "a truncated trace"),
    (PR, '        return probs + ["the trace is empty"]', '        return probs', "an empty trace"),
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
    (LA, 'or sorted(got) != sorted(pins.get(pk, {})) \\\n', '\\\n', "a pinned item left out"),
    (LA, '                or not all(isinstance(x, dict) and _is(x.get("match"), True) for x in got.values()):',
     '                or False:', "a mismatch in a GO"),
    (LA, '        p.append("required qualifiers")', '        pass', "qualifiers in a GO"),
    (LA, 'and x.get("config_like") == []', 'and True', "config-like names in a GO"),
    (LA, '    if not _hex64(_get(rec, "xsec", "dbconfig", "sha256")):', '    if False:', "dbconfig in a GO"),
    (LA, '                    or t.get("rpm_match") not in (True, None):', '                    or False:', "an RPM mismatch in a GO"),
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
]]

if __name__ == "__main__":
    raise SystemExit(R.main(M))
