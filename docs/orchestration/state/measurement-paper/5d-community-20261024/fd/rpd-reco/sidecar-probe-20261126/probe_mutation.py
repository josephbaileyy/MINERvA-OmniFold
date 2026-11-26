"""Mutation check of the sidecar probe's guards: each mutant must make test_sidecar_probe.py fail.
    python3 probe_mutation.py      (in this directory; restores the reader after each mutant)"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = HERE / "sidecar_probe_remote.py"
MUT = [
    ("PIN", '"sha256_matches": digest == SIDECAR_SHA256', '"sha256_matches": True'),
    ("ATIME", '"atime_unchanged": st1.st_atime == st0.st_atime', '"atime_unchanged": True'),
    ("SIZE_READ", '"size_matches_read": n == st0.st_size', '"size_matches_read": True'),
    ("VERDICT", 'ok = ok and row["sha256_matches"] and row["atime_unchanged"] and row["size_matches_read"]', 'ok = ok'),
    ("MISSING_FAILS", '            report["stat_only"].append({"path": path, "missing": detail})\n            ok = False',
     '            report["stat_only"].append({"path": path, "missing": detail})'),
    ("SYMLINK", '        if stat.S_ISLNK(st.st_mode):\n            return "refused"', '        if False:\n            return "refused"'),
    ("NOATIME", 'os.O_RDONLY | os.O_NOATIME | os.O_NOFOLLOW | os.O_NONBLOCK', 'os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK'),
    ("OPEN_STAT_ONLY", '    for path, (status, st, detail) in pre[:-1]:\n        if status == "ok":',
     '    for path, (status, st, detail) in pre[:-1]:\n        if status == "ok":\n            os.close(open_nofollow(path))'),
]
killed = 0
for name, old, new in MUT:
    orig = R.read_bytes()
    t = orig.decode()
    assert t.count(old) == 1, (name, t.count(old))
    R.write_text(t.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                            "test_sidecar_probe.py", "-k", "not built_wrapper"],   # that test pins the reader's
                           cwd=HERE, capture_output=True, text=True)                    # bytes, so it would kill all
    finally:
        R.write_bytes(orig)
    k = r.returncode != 0
    killed += k
    print(name, "KILLED" if k else "SURVIVED", flush=True)
print("killed", killed, "of", len(MUT))
