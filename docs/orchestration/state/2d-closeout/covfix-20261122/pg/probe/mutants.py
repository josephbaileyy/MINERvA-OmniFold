"""Hand mutants of pg-probe.py (rev 3) and pg-probe-launch.py: each must make test_pg_probe.py fail.

Run: python3 -I -B mutants.py > mutants.log   (from this directory; copies to a temp dir, never edits these files;
PG_MUTANT_JOBS sets how many run at once, default 6)
"""
import concurrent.futures
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("PG_REPO_ROOT") or HERE.parents[6])
PR, LA = "pg-probe.py", "pg-probe-launch.py"
M = [  # (file, old, new, what it breaks)
    # decision (codex 1.3; 2.1)
    (PR, '"novel": any(by_slot[s][cls[t][s]] for s in SLOTS.values())', '"novel": all(by_slot[s][cls[t][s]] for s in SLOTS.values())',
     "novelty needs both classes"),
    (PR, '"novel": any(by_slot[s][cls[t][s]] for s in SLOTS.values())', '"novel": by_slot["ccqe"][cls[t]["ccqe"]]',
     "novelty ignores 2p2h"),
    (PR, '        if not nov[t]["branches_agree"]:\n', '        if False:\n', "branch disagreement ignored"),
    (PR, '        bad = undeclared(t)\n', '        bad = []\n', "u0 not held to section 4.1"),
    (PR, 'if c["sources"]["ccqe"]["alg"] != d["ccqe_alg"] or ', 'if ', "u0's hybrid reference not checked"),
    (PR, ' or c["ccqe"] != d["ccqe"]:', ':', "u0's CCQE default not checked"),
    (PR, 'if c["components"]["2p2h"] != d["2p2h_branches"] or ', 'if ', "u0's 2p2h class not checked"),
    (PR, ' or users(c["2p2h"]) != d["2p2h_users"]:', ':', "u0's 2p2h overlap not checked"),
    (PR, '    elif st02b == "absent":', '    elif st02b != "present":', "fallback on an unresolved 02b"),
    (PR, '        if e == "eligible" and same_02 is not True:', '        if e == "eligible" and same_02 is False:',
     "02a fallback with an unchecked premise"),
    (PR, '        if e == "eligible" and same_02 is not True:', '        if False:', "02a/02b mismatch ignored"),
    (PR, '            slot2, fallback = SLOT2_FALLBACK, True', '            slot2, fallback = SLOT2_FALLBACK, False',
     "fallback not recorded"),
    (PR, '        stops.append(f"slot 1: {SLOT1} {elig[SLOT1]}")', '        pass', "slot-1 failure not a stop"),
    (PR, 'and c.get("readme_version_lines") == [pin[2]])', ')', "version line control"),
    (PR, 'c.get("spline_sha256") == pin[0] and ', '', "spline digest control"),
    (PR, 'okc = resolved(cls[t]) and (cls[t]["ccqe"], cls[t]["2p2h"]) == spent_classes[t]', 'okc = resolved(cls[t])',
     "spent class control"),
    (PR, 'if any(x in cls[u]["components"].get(s, []) for s in SLOTS.values())]',
     'if x in cls[u]["components"].get("2p2h", [])]', "overlap by slot, not by pool"),
    # catalog (codex 1.2; 2.3)
    (PR, '    if not rec["in_listing"] and not rec["in_ups"]:', '    if not rec["in_listing"]:', "absence from the listing alone"),
    (PR, '        if rec["other_entries"]:\n', '        if False:\n', "absence despite another entry naming the tune"),
    (PR, '    if tune == SLOT2 and rec["other_entries"]:', '    if False:', "a second 02b entry ignored"),
    (PR, '(k in _key(u) or v == tune)', 'k in _key(u)', "UPS entries setting the tune under another name ignored"),
    (PR, '    if rec["in_ups"] and rec["ups_tune"] != tune:', '    if False:', "GENIE_XSEC_TUNE not checked"),
    (PR, '        if rec["spline_root"] != "genie_xsec_spline_list" or ', '        if ', "spline root not checked"),
    (PR, 'or rec["spline_tunes"] != [tune]:', 'or tune not in rec["spline_tunes"]:', "several spline tunes accepted"),
    (PR, '        elif st["depth"] == 1 and name == "genie_tune":', '        elif name == "genie_tune":',
     "a nested genie_tune taken as the header"),
    (PR, '    p.StartDoctypeDeclHandler = p.EntityDeclHandler = refuse\n', '', "spline DOCTYPE accepted"),
    (PR, 'm = VERSION_LINE.fullmatch(lines[0])', 'm = VERSION_LINE.search(lines[0])', "README line matched in part"),
    (PR, '        if not m or m.group(2) != qc:', '        if not m:', "README qualifier not checked"),
    # roots and the read boundary (codex 1.4; 2.4)
    (PR, '        roots, rec["roots_verified"] = verify_roots(roots, repo, mounts())',
     '        rec["roots_verified"] = {"pass": True}', "roots not verified"),
    (PR, '        if not real.startswith(repo + "/"):', '        if False:', "a root outside the repository accepted"),
    (PR, '    if mp not in (repo, os.path.dirname(repo)) or typ is None', '    if typ is None',
     "the repository's own mount not required"),
    (PR, ' or typ in LOCAL_FS:\n        raise Unresolved(f"{repo} is not', ':\n        raise Unresolved(f"{repo} is not',
     "a node-local repository mount accepted"),
    (PR, '        if mount_entry(real, mounts_text)[0] != mp:', '        if False:', "a root on another mount accepted"),
    (PR, '            if not stat.S_ISDIR(os.lstat(real).st_mode):', '            if False:', "a non-directory root accepted"),
    (PR, '    raise Unresolved(f"{path} resolves outside the approved roots")', '    return real, roots[0]', "no containment"),
    (PR, '        return os.open(os.path.relpath(real, rr), flags | O_NOFOLLOW, dir_fd=rfd)',
     '        return os.open(real, flags | O_NOFOLLOW)', "reads not relative to the verified root"),
    (PR, '    if not stat.S_ISREG(os.fstat(fd).st_mode):\n        os.close(fd)', '    if False:\n        os.close(fd)',
     "non-regular file read"),
    # configuration (codex 1.1; 2.2)
    (PR, '        if _absent(d) or name not in list_dir(d, roots):', '        if not os.path.lexists(os.path.join(d, name)):',
     "lookup falls through on an error"),
    (PR, '    except FileNotFoundError:\n        return True\n    except OSError as e:\n        raise Unresolved',
     '    except OSError:\n        return True\n    except OSError as e:\n        raise Unresolved', "an lstat error taken as absence"),
    (PR, '                src["registry"] = resolve_ref(config_root, tune, cls, conf, master, roots)[1]',
     '                src["registry"] = {}', "plain class not resolved"),
    (PR, '    if n != 1:\n        raise Unresolved(f"{path}: {n} param_set named', '    if n > 1:\n        raise Unresolved(f"{path}: {n} param_set named',
     "unknown set accepted"),
    (PR, '    if len(files) != 1 or not re.fullmatch', '    if not files or not re.fullmatch', "two registry entries accepted"),
    (PR, '            ref = resolve_ref(config_root, tune, *alg_value(*v, f"{hpath} {conf} {k}"), master, roots)[1]',
     '            ref = dict(zip(("class", "set"), alg_value(*v, f"{hpath} {conf} {k}")))', "hybrid branches not resolved"),
    (PR, '    default = resolve_ref(config_root, tune, *alg_value(*params["DefaultXSecAlg"], f"{hpath} {conf} DefaultXSecAlg"),\n                          master, roots)[1]',
     '    default = dict(zip(("class", "set"), alg_value(*params["DefaultXSecAlg"], "")))', "hybrid default not resolved"),
    (PR, '    if root.tag != "alg_conf":\n        raise Unresolved(f"{path}: root <{root.tag}>")\n    n = len',
     '    if False:\n        raise Unresolved(f"{path}: root <{root.tag}>")\n    n = len', "registry file root not checked"),
    (PR, 'if re.search(rb"<!DOCTYPE|<!ENTITY", data):', 'if False:', "DOCTYPE accepted"),
    (PR, '    if not raw:\n        raise Unresolved(f"{where}: empty value")', '    if False:\n        raise Unresolved("")',
     "empty value accepted"),
    (PR, '    if typ != "alg":', '    if False:', "non-alg type accepted"),
    (PR, '        if k in params:\n            raise Unresolved(f"{path}: {k} twice in {set_name}")',
     '        if False:\n            raise Unresolved("")', "duplicate accepted"),
    (PR, '    if len(sets) != 1:\n        raise Unresolved(f"{path}: {len(sets)} param_set', '    if not sets:\n        raise '
     'Unresolved(f"{path}: {len(sets)} param_set', "two Default sets accepted"),
    (PR, '"param_set" and (s.get("name") or "").strip() == set_name]', '"param_set"]', "inactive sets read"),
    (PR, '        if root.tag != "global_param_list":', '        if False:', "wrong root accepted"),
    (PR, 'for d in (os.path.join(config_root, cmc(tune), tune), os.path.join(config_root, cmc(tune)), config_root):',
     'for d in (os.path.join(config_root, cmc(tune)), os.path.join(config_root, cmc(tune), tune), config_root):',
     "search order reversed"),
    (PR, '            if v in genie_ups_text:\n', '            if False:\n', "search-path variables ignored"),
    (PR, '            if cls == "HybridXSecAlgorithm":', '            if False:', "hybrid not resolved"),
    (PR, '        elif k != "DefaultXSecAlg":\n            raise', '        elif False:\n            raise',
     "unexpected hybrid parameter accepted"),
    (PR, '    if len(parts) not in (1, 2) or', '    if len(parts) > 3 or', "value with two slashes"),
    # gpg (codex 1.7, 1.8; 2.6)
    (PR, '        if not _fd_open(fd):', '        if False:', "closed standard fds not reopened"),
    (PR, '\n                       and rec.get("gpgconf_kill_rc") == 0\n', '\n', "failed kill accepted"),
    (PR, ' and rec.get("gnupghome_mode") == "0o700"\n', '\n', "mode not required"),
    (PR, 'and rc_t == 2 and rec["tampered"]["evidence"]', 'and rc_t != 0', "a crash counts as a refusal"),
    (PR, 'and rc_w == 2\n                       and rec["wrong_passphrase"]["evidence"]', 'and rc_w != 0\n                       and True',
     "wrong passphrase without evidence"),
    (PR, '        if not rec["confined"]:\n            raise RuntimeError', '        if False:\n            raise RuntimeError',
     "gpg run before the sockets are verified"),
    (PR, '        rec["confined"] = rec["confined"] and ld.returncode == 0\n', '', "a failing --list-dirs accepted"),
    (PR, '        if sd != want:', '        if not sd.startswith(os.path.dirname(want) + "/d."):', "socket dir hash not checked"),
    (PR, 'not (private and st.st_mode & 0o077)', 'True', "socket dir mode not checked"),
    (PR, '        if os.path.realpath(sd) != sd:', '        if False:', "socket dir through a link accepted"),
    (PR, '        if mount_fs(sd, mounts_text) != "tmpfs":', '        if False:', "socket dir mount not checked"),
    (PR, '    probs += [f"{k} {v} is outside {target}"', '    probs += [] and [', "reported sockets not checked"),
    (PR, 'zb32(hashlib.sha1(home.encode()).digest(), 8 * 15)', 'zb32(hashlib.sha1(home.encode()).digest(), 8 * 10)',
     "the wrong hash length"),
    (PR, '            if outside:\n                try:', '            if False:\n                try:', "socket dir not removed"),
    (PR, 'rec["socketdir_absent"] = _confirmed_absent(canonical) if canonical else False', 'rec["socketdir_absent"] = True',
     "socket dir absence not checked"),
    (PR, '            gone = False\n', '            gone = True\n', "an unidentified agent counted as gone"),
    (PR, '                       and rec.get("agent_gone")\n', '                       and True\n', "surviving agent accepted"),
    (PR, '    if rec["parent_fs"] not in LOCAL_FS:', '    if False:', "network parent accepted"),
    (PR, '    bad[last[0] + last[1] - 1] ^= 0x01', '    bad[len(bad) // 2] ^= 0x01', "tamper not in the MDC"),
    (PR, '                    if not partial:\n                        break', '                    break',
     "partial lengths not followed"),
    (PR, '    if _fd_open(3):\n        raise RuntimeError', '    if False:\n        raise RuntimeError', "fd 3 clobbered"),
    (PR, '    if not rec["identity"]["pass"]:', '    if False:', "identity not enforced"),
    # launcher (codex 1.5, 1.6; 2.5)
    (LA, '    if got != argv[0]:', '    if False:', "sha check removed"),
    (LA, 'os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW', 'os.O_RDWR | os.O_CREAT | os.O_TRUNC', "output not reserved"),
    (LA, '    if len(hits) != 1 or not lines or lines[-1] != hits[0]:', '    if not hits:', "receipt shape"),
    (LA, '    if v not in RC_FOR or RC_FOR[v] != rc:', '    if v not in RC_FOR:', "verdict/rc mismatch"),
    (LA, '    return p.returncode if ok else 4', '    return p.returncode', "invalid receipt exit"),
    (LA, '    if v != "GO":\n        return p\n', '    if True:\n        return p\n', "a GO's evidence not required"),
    (LA, '    return type(got) is type(want) and got == want', '    return got == want', "1 taken for True"),
    (LA, '(("socketdir_absent",), True), ', '', "socket dir absence not required"),
    (LA, 'or len(ctl) != 4 or not all(_is(x, True) for x in ctl.values()):', ':', "controls not required"),
    (LA, '    if not _is(fb, u1 == U1_FALLBACK) or', '    if False and', "fallback consistency not required"),
    (LA, '        if _get(d, "eligibility", t) != "eligible":', '        if False:', "slot eligibility not required"),
    (LA, ' or not isinstance(c.get("readme_version"), str):', ':', "catalog evidence not required"),
    (LA, '        return p + ([] if stops else ["a STOP with no stops"])', '        return p', "a STOP without stops accepted"),
    (LA, '        digest = _sha_through(fd)', '        digest = hashlib.sha256(open(out_path, "rb").read()).hexdigest()',
     "footer hash by pathname"),
    (LA, 'SSH_OPTS = ["-F", "/dev/null", ', 'SSH_OPTS = [', "user ssh config used"),
    (LA, '"-o", "ForwardAgent=no", ', '', "agent forwarding allowed"),
    (LA, 'REMOTE = "env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -"',
     'REMOTE = "/usr/bin/python3.11 -I -B -"', "remote environment not minimal"),
    (LA, 'input=body,', 'input=open(probe_path, "rb").read() + b"\\n",', "sent bytes differ from hashed bytes"),
]


def run_one(i, f, old, new, what):
    tmp = Path(tempfile.mkdtemp())
    try:
        for n in (PR, LA, "test_pg_probe.py"):
            shutil.copy(HERE / n, tmp / n)
        src = (tmp / f).read_text()
        if src.count(old) != 1:
            return False, f"M{i:02d} NOT-APPLICABLE ({src.count(old)} matches): {what}"
        (tmp / f).write_text(src.replace(old, new))
        p = subprocess.run([sys.executable, "-I", "-B", "test_pg_probe.py"], cwd=tmp, capture_output=True,
                           text=True, env=dict(os.environ, PG_REPO_ROOT=str(REPO)), timeout=600)
        ok = p.returncode != 0
        return ok, f"M{i:02d} {'KILLED' if ok else 'SURVIVED'}: {what} [{f}]"
    except subprocess.TimeoutExpired:
        return True, f"M{i:02d} KILLED (timeout): {what} [{f}]"
    finally:
        shutil.rmtree(tmp)


def main():
    jobs = int(os.environ.get("PG_MUTANT_JOBS", "6"))
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        results = list(ex.map(lambda a: run_one(a[0], *a[1]), enumerate(M, 1)))
    for _, line in results:
        print(line)
    killed = sum(ok for ok, _ in results)
    print(f"{killed} of {len(M)} killed")
    return 0 if killed == len(M) else 1


if __name__ == "__main__":
    raise SystemExit(main())
