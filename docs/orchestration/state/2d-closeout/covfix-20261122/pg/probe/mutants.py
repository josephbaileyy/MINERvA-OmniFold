"""Hand mutants of pg-probe.py and pg-probe-launch.sh: each must make test_pg_probe.py fail.

Run: python3 -I -B mutants.py > mutants.log   (from this directory; copies to a temp dir, never edits these files)
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[6]
M = [  # (file, old, new, what it breaks)
    ("pg-probe.py", 'return rec["ccqe"] not in spent_set or rec["2p2h"] not in spent_set',
     'return rec["ccqe"] not in spent_set and rec["2p2h"] not in spent_set', "novelty needs both classes"),
    ("pg-probe.py", 'return rec["ccqe"] not in spent_set or rec["2p2h"] not in spent_set',
     'return rec["ccqe"] not in spent_set', "novelty ignores 2p2h"),
    ("pg-probe.py", '    if status[SLOT2] == "absent":', '    if status[SLOT2] != "qualifies":',
     "fallback on exclusion, not only absence"),
    ("pg-probe.py", 'stops.append(f"slot 1: {SLOT1} {status[SLOT1]}")', 'pass', "slot-1 failure not a stop"),
    ("pg-probe.py", 'and c["readme_version_lines"] == [pin[2]])', ')', "version line not compared"),
    ("pg-probe.py", 'c["spline_sha256"] == pin[0] and ', '', "spline digest not compared"),
    ("pg-probe.py", 'okc = resolved(cls[t]) and (cls[t]["ccqe"], cls[t]["2p2h"]) == spent_classes[t]',
     'okc = resolved(cls[t])', "spent classes not compared"),
    ("pg-probe.py", 'for key, val in _PARAM.findall(_COMMENT.sub("", text)):',
     'for key, val in _PARAM.findall(text):', "comments not removed"),
    ("pg-probe.py", '            if len(vals) > 1:', '            if len(vals) > 2:', "duplicates accepted"),
    ("pg-probe.py", '(QEL-CC|MEC-CC)"', '(QEL-CC|MEC-CC)', "key prefix match (QEL-CC-CHARM read as QEL-CC)"),
    ("pg-probe.py", '    for path in [mc] + overrides:', '    for path in [mc]:', "tune overrides ignored"),
    ("pg-probe.py", 'return tune.replace("_", "") + "-k250-e1000"', 'return tune.replace("_", "")',
     "wrong qualifier"),
    ("pg-probe.py", '"--force-mdc"]', ']', "pinned flag dropped"),
    ("pg-probe.py", 'and rc_t not in (0, None) and rc_w not in (0, None))', ')', "integrity controls ignored"),
    ("pg-probe.py", 'and rec["agents_after_kill"] == [] and rec["gnupghome_removed"]', 'and rec["gnupghome_removed"]',
     "surviving agent ignored"),
    ("pg-probe.py", 'rec["pass"] and rec["gpgconf_kill_rc"] == 0 and ', 'rec["pass"] and ', "failed kill ignored"),
    ("pg-probe.py", 'and rec["agents_before_kill"] is not None\n', '\n', "blind agent check accepted"),
    ("pg-probe.py", '    if p.returncode != 0:\n        return None\n', '', "ps failure read as no agents"),
    ("pg-probe.py", '            shutil.rmtree(home, ignore_errors=True)\n', '            pass\n', "GNUPGHOME left behind"),
    ("pg-probe.py", '                       and rec["user_gnupg_unchanged"])', ')', "touched ~/.gnupg ignored"),
    ("pg-probe.py", '    if _fd_open(3):\n        raise RuntimeError', '    if False:\n        raise RuntimeError',
     "fd 3 clobbered"),
    ("pg-probe.py", '        if not cat[t]["complete"]:\n', '        if False:\n', "incomplete entry treated as present"),
    ("pg-probe.py", '"present": os.path.isdir(q),', '"present": os.path.isfile(spl) and os.path.isfile(readme),',
     "incomplete entry treated as absent (fallback)"),
    ("pg-probe.py", '        if len({c for _, c in over}) > 1:', '        if False:', "override conflict guessed"),
    ("pg-probe.py", 'for sub in (os.path.join(base, tune), os.path.join(config_root, tune)):',
     'for sub in (os.path.join(base, tune),):', "peer tune dir ignored"),
    ("pg-probe.py", '    if fallback and slot2 and same_02 is False:', '    if False:', "02a/02b class mismatch ignored"),
    ("pg-probe.py", '    if not rec["gpg"]["pass"]:\n        stops.append', '    if False:\n        stops.append',
     "gpg failure not a stop"),
    ("pg-probe.py", 'if "QEL-CC" in ln or "MEC-CC" in ln', 'if "Qualifiers" in ln', "context lines"),
    ("pg-probe.py", 'if "Qualifiers" in ln or "GENIE_XSEC_TUNE" in ln', 'if "Qualifiers" in ln', "UPS tune lines"),
    ("pg-probe-launch.sh", '[ "$GOT" = "$WANT" ] ||', 'true ||', "sha check removed"),
    ("pg-probe-launch.sh", '[ ! -e "$O" ] && [ ! -e "$O.partial" ] ||', 'true ||', "overwrite allowed"),
    ("pg-probe-launch.sh", 'exit $RC', 'exit 0', "rc lost"),
    ("pg-probe-launch.sh", "'/usr/bin/python3.11 -I -B -'", "'python3 -'", "isolation flags dropped"),
]


def main():
    killed = 0
    for i, (f, old, new, what) in enumerate(M, 1):
        tmp = Path(tempfile.mkdtemp())
        try:
            for n in ("pg-probe.py", "pg-probe-launch.sh", "test_pg_probe.py"):
                shutil.copy(HERE / n, tmp / n)
            src = (tmp / f).read_text()
            if src.count(old) != 1:
                print(f"M{i:02d} NOT-APPLICABLE ({src.count(old)} matches): {what}")
                continue
            (tmp / f).write_text(src.replace(old, new))
            p = subprocess.run([sys.executable, "-I", "-B", "test_pg_probe.py"], cwd=tmp, capture_output=True,
                               text=True, env=dict(os.environ, PG_REPO_ROOT=str(REPO)))
            ok = p.returncode != 0
            killed += ok
            print(f"M{i:02d} {'KILLED' if ok else 'SURVIVED'}: {what} [{f}]")
        finally:
            shutil.rmtree(tmp)
    print(f"{killed} of {len(M)} killed")
    return 0 if killed == len(M) else 1


if __name__ == "__main__":
    raise SystemExit(main())
