"""Hand mutants of pg-probe.py (rev 2) and pg-probe-launch.py: each must make test_pg_probe.py fail.

Run: python3 -I -B mutants.py > mutants.log   (from this directory; copies to a temp dir, never edits these files)
"""
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
    # decision (codex 3)
    (PR, 'by_class = cls[t]["ccqe"] not in pool or cls[t]["2p2h"] not in pool',
     'by_class = cls[t]["ccqe"] not in pool and cls[t]["2p2h"] not in pool', "novelty needs both classes"),
    (PR, 'by_class = cls[t]["ccqe"] not in pool or cls[t]["2p2h"] not in pool', 'by_class = cls[t]["ccqe"] not in pool',
     "novelty ignores 2p2h"),
    (PR, '        if not nov[t]["agree"]:\n', '        if False:\n', "component disagreement ignored"),
    (PR, '    elif st02b == "absent":', '    elif st02b != "present":', "fallback on an unresolved 02b"),
    (PR, '        if e == "eligible" and same_02 is not True:', '        if e == "eligible" and same_02 is False:',
     "02a fallback with an unchecked premise"),
    (PR, '        if e == "eligible" and same_02 is not True:', '        if False:', "02a/02b mismatch ignored"),
    (PR, '        if not _fd_open(fd):', '        if False:', "closed standard fds not reopened"),
    (PR, 'rec.get("gnupghome_mode") == "0o700" and ', '', "mode not required"),
    (PR, '            slot2, fallback = SLOT2_FALLBACK, True', '            slot2, fallback = SLOT2_FALLBACK, False',
     "fallback not recorded"),
    (PR, '        stops.append(f"slot 1: {SLOT1} {elig[SLOT1]}")', '        pass', "slot-1 failure not a stop"),
    (PR, 'and c.get("readme_version_lines") == [pin[2]])', ')', "version line control"),
    (PR, 'c.get("spline_sha256") == pin[0] and ', '', "spline digest control"),
    (PR, 'okc = resolved(cls[t]) and (cls[t]["ccqe"], cls[t]["2p2h"]) == spent_classes[t]', 'okc = resolved(cls[t])',
     "spent class control"),
    (PR, 'if any(x in cls[u]["components"].get(s, []) for s in SLOTS.values())',
     'if x in cls[u]["components"].get("2p2h", [])', "overlap by slot, not by pool"),
    # catalog (codex 2)
    (PR, '    if not rec["in_listing"] and not rec["in_ups"]:', '    if not rec["in_listing"]:', "absence from the listing alone"),
    (PR, '    if rec["in_ups"] and rec["ups_tune"] != tune:', '    if False:', "GENIE_XSEC_TUNE not checked"),
    (PR, '        if rec["spline_tune"] != tune:', '        if False:', "spline header not checked"),
    (PR, '        if not rec["spline_bytes"]:', '        if False:', "empty spline accepted"),
    (PR, 'if len(rec["readme_version_lines"]) != 1 or qc not in rec["readme_version_lines"][0]:',
     'if len(rec["readme_version_lines"]) != 1:', "README qualifier not checked"),
    # boundary (codex 4)
    (PR, '    raise Unresolved(f"{path} resolves outside the approved roots")', '    return real', "no containment"),
    (PR, '    if not stat.S_ISREG(os.fstat(fd).st_mode):\n        os.close(fd)', '    if False:\n        os.close(fd)',
     "non-regular file read"),
    (PR, '    if not stat.S_ISREG(os.stat(real).st_mode):\n        raise Unresolved(f"{path} exists but',
     '    if False:\n        raise Unresolved(f"{path} exists but', "non-regular config accepted"),
    # configuration (codex 1)
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
    # gpg (codex 7, 8)
    (PR, 'and rc_t == 2 and rec["tampered"]["evidence"]', 'and rc_t != 0', "a crash counts as a refusal"),
    (PR, 'and rc_w == 2\n                       and rec["wrong_passphrase"]["evidence"]', 'and rc_w != 0\n                       and True',
     "wrong passphrase without evidence"),
    (PR, 'and rec["wrong_passphrase"]["evidence"] and rec["confined"])', 'and rec["wrong_passphrase"]["evidence"])',
     "unconfined sockets"),
    (PR, '            gone = False\n', '            gone = True\n', "an unidentified agent counted as gone"),
    (PR, 'rec.get("gnupghome_mode") == "0o700" and rec.get("gpgconf_kill_rc") == 0\n',
     'rec.get("gnupghome_mode") == "0o700"\n', "failed kill accepted"),
    (PR, '                       and rec.get("agent_gone")\n', '                       and True\n', "surviving agent accepted"),
    (PR, '    if rec["parent_fs"] not in LOCAL_FS:', '    if False:', "network parent accepted"),
    (PR, '    bad[last[0] + last[1] - 1] ^= 0x01', '    bad[len(bad) // 2] ^= 0x01', "tamper not in the MDC"),
    (PR, '                    if not partial:\n                        break', '                    break',
     "partial lengths not followed"),
    (PR, '    if _fd_open(3):\n        raise RuntimeError', '    if False:\n        raise RuntimeError', "fd 3 clobbered"),
    (PR, '    if not rec["identity"]["pass"]:', '    if False:', "identity not enforced"),
    # launcher (codex 5, 6)
    (LA, '    if got != argv[0]:', '    if False:', "sha check removed"),
    (LA, 'os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW', 'os.O_WRONLY | os.O_CREAT | os.O_TRUNC',
     "output not reserved"),
    (LA, '    if len(hits) != 1 or not lines or lines[-1] != hits[0]:', '    if not hits:', "receipt shape"),
    (LA, '    if v not in RC_FOR or RC_FOR[v] != rc:', '    if v not in RC_FOR:', "verdict/rc mismatch"),
    (LA, '    return p.returncode if ok else 4', '    return p.returncode', "invalid receipt exit"),
    (LA, 'SSH_OPTS = ["-F", "/dev/null", ', 'SSH_OPTS = [', "user ssh config used"),
    (LA, '"-o", "ForwardAgent=no", ', '', "agent forwarding allowed"),
    (LA, 'REMOTE = "env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -"',
     'REMOTE = "/usr/bin/python3.11 -I -B -"', "remote environment not minimal"),
    (LA, 'input=body,', 'input=open(probe_path, "rb").read() + b"\\n",', "sent bytes differ from hashed bytes"),
]


def main():
    killed = 0
    for i, (f, old, new, what) in enumerate(M, 1):
        tmp = Path(tempfile.mkdtemp())
        try:
            for n in (PR, LA, "test_pg_probe.py"):
                shutil.copy(HERE / n, tmp / n)
            src = (tmp / f).read_text()
            if src.count(old) != 1:
                print(f"M{i:02d} NOT-APPLICABLE ({src.count(old)} matches): {what}")
                continue
            (tmp / f).write_text(src.replace(old, new))
            p = subprocess.run([sys.executable, "-I", "-B", "test_pg_probe.py"], cwd=tmp, capture_output=True,
                               text=True, env=dict(os.environ, PG_REPO_ROOT=str(REPO)), timeout=600)
            ok = p.returncode != 0
            killed += ok
            print(f"M{i:02d} {'KILLED' if ok else 'SURVIVED'}: {what} [{f}]", flush=True)
        except subprocess.TimeoutExpired:
            killed += 1
            print(f"M{i:02d} KILLED (timeout): {what} [{f}]", flush=True)
        finally:
            shutil.rmtree(tmp)
    print(f"{killed} of {len(M)} killed")
    return 0 if killed == len(M) else 1


if __name__ == "__main__":
    raise SystemExit(main())
