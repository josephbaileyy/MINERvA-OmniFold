"""FD-G-FOLLOWUP-DECLARATION.md section 6.1: run main's fd_g_diag.py (at the given source file) and this tree's
refactored one on the same synthetic trees, and compare their readouts as parsed JSON with exact float equality,
code_sha256 and argv aside. Usage: python3 -I -B refactor_identity.py <worktree> <main's fd_g_diag.py>"""
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from unittest import mock

wt, main_src = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(wt / "nd-unfolding"))
sys.path.insert(0, str(wt / "nd-unfolding/tests"))
import fd_g_diag as NEW  # noqa: E402
import test_fd_g_followup as T  # noqa: E402

spec = importlib.util.spec_from_file_location("fd_g_diag_main", main_src)
OLD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(OLD)
for m, p in (("main", main_src), ("refactored", Path(NEW.__file__))):
    print(f"{m}: {p.name} sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}")
bad = 0
for seed in (0, 1, 2):
    for role in ("adopted", "sensitivity"):
        tree = T.FollowupTree(Path(tempfile.mkdtemp()) / "t", seed=seed).write(role=role)
        outs = {}
        for name, mod in (("main", OLD), ("refactored", NEW)):
            o = tree.out / f"{name}.json"
            with mock.patch("sys.stdout"):
                rc = mod.run(mod.build_args(tree.dargv[:-1] + [str(o)]), tree.dpins, tree.predictions)
            r = json.loads(o.read_text())
            r.pop("code_sha256")
            r.pop("argv")
            outs[name] = (rc, r)
        same = outs["main"] == outs["refactored"]
        bad += not same
        print(f"seed {seed} role {role}: rc {outs['main'][0]}/{outs['refactored'][0]}, readouts "
              f"{'identical' if same else 'DIFFER'}")
print("identical on all 6" if not bad else f"{bad} DIFFER")
raise SystemExit(1 if bad else 0)
