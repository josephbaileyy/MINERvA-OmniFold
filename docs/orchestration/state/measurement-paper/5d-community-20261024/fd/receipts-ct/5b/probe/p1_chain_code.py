"""5B probe 1 (FD-CT-5B-DECLARATION.md section 4): is main's code for 5B's chain MP-1's zero chain's?

Read-only, local, git objects only. For each file the chain executes, it compares the file at the commit it is run
from (argv[1], the declaration's) with the file at MP-1's deploys: the dump deploy c1cba7bf (s5p_input_dumps.py and the
collectors it imports), the unfold deploy 4e4b4f56 (s5p_numerics.py and its imports), and the merge/evaluate deploy
e9372b75 (hadd_universes_full.py). Where the bytes differ, it lists the top-level functions, classes and assignments
whose AST differs, is added or is removed. It also checks the unfold's recorded code digests in the committed
mp1s1_zero_b-_j-.npz against the files at argv[1]. It reads no data.

    python3 -I -B p1_chain_code.py <commit>
"""
import ast
import hashlib
import json
import subprocess
import sys

import numpy as np

HEAD = sys.argv[1]
DUMP, UNF, EVAL = "c1cba7bfb214a82abde5580c72c9ef3c4704e73f", "4e4b4f56bb0c4715dcf567829ac0449bfac745de", \
    "e9372b757250e9607f52e471d9b0c447b08e65d5"
FILES = {
    DUMP: ["nd-unfolding/s5p_input_dumps.py", "nd-unfolding/nn_dump_inputs.py", "nd-unfolding/unfold_nd_omnifold_unbinned.py",
           "2d-unfolding/unfold_2d_omnifold_unbinned.py"],
    UNF: ["nd-unfolding/s5p_numerics.py", "nd-unfolding/s5n_pseudo.py", "nd-unfolding/s5c_pseudo.py", "nd-unfolding/s5c_unfold.py",
          "nd-unfolding/omnifold_nn_core.py", "nd-unfolding/xsec_nd.py", "nd-unfolding/s5e_candidate.py",
          "nd-unfolding/s5e_deform.py", "nd-unfolding/s5e_trace.py", "nd-unfolding/s5p_truths.py",
          "2d-unfolding/unfold_2d_omnifold_unbinned.py"],
    EVAL: ["2d-unfolding/uq/hadd_universes_full.py"],
}


def show(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, check=True).stdout


def top(src):
    out = {}
    for n in ast.parse(src).body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            out[n.name] = ast.dump(n)
        elif isinstance(n, ast.Assign):
            out["= " + ast.unparse(n.targets[0])] = ast.dump(n)
    return out


res = {"head": HEAD, "files": {}}
for rev, paths in FILES.items():
    for p in paths:
        a, b = show(rev, p), show(HEAD, p)
        r = {"against": rev[:8], "bytes_equal": a == b, "sha256_then": hashlib.sha256(a).hexdigest()[:16],
             "sha256_now": hashlib.sha256(b).hexdigest()[:16]}
        if a != b:
            ta, tb = top(a.decode()), top(b.decode())
            r["changed"] = sorted(k for k in ta if k in tb and ta[k] != tb[k])
            r["added"] = sorted(set(tb) - set(ta))
            r["removed"] = sorted(set(ta) - set(tb))
        res["files"][f"{p} vs {rev[:8]}"] = r
z = np.load("docs/orchestration/state/measurement-paper/phase1/mp1/jitter-receipts/mp1s1_zero_b-_j-.npz", allow_pickle=False)
rec = json.loads(str(z["meta"]))["code_sha256"]
where = {"unfold_2d_omnifold_unbinned.py": "2d-unfolding/"}
res["mp1s1_zero_recorded_code"] = {
    k: {"recorded": v[:16], "at_head": hashlib.sha256(show(HEAD, where.get(k, "nd-unfolding/") + k)).hexdigest()[:16]}
    for k, v in rec.items() if isinstance(v, str) and len(v) == 64}
print(json.dumps(res, indent=1))
