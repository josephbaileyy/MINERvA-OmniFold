import os, re, subprocess, sys, queue, threading
from pathlib import Path
M = Path(__file__).resolve().parent
sys.path.insert(0, str(M.parent / "reviewB"))
from mutants_v2 import MUTANTS
ORIG = (M / "orig.py").read_text()
todo = [m for m in MUTANTS if ORIG.count(m[2]) == 1]
print("applicable", len(todo), "of", len(MUTANTS), "skipped", [m[0] for m in MUTANTS if ORIG.count(m[2]) != 1], flush=True)
q = queue.Queue()
for m in todo: q.put(m)
res = {}
lock = threading.Lock()
def worker(w):
    S = M / f"w{w}"; tgt = S / "nd-unfolding/fd_g_figures.py"
    while True:
        try: mid, desc, old, new = q.get_nowait()
        except queue.Empty: return
        tgt.write_text(ORIG.replace(old, new, 1))
        p = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_fd_g_figures"], cwd=S / "nd-unfolding/tests",
                           env={**os.environ, "TMPDIR": str(S / "tmp")}, capture_output=True, text=True, timeout=600)
        with lock:
            res[mid] = p.returncode != 0
            print(mid, "KILLED" if p.returncode else "SURVIVED", desc, flush=True)
        tgt.write_text(ORIG)
ths = [threading.Thread(target=worker, args=(w,)) for w in (1, 2, 3, 4)]
[t.start() for t in ths]; [t.join() for t in ths]
print("total", len(res), "killed", sum(res.values()), "survived", sorted(k for k, v in res.items() if not v))
