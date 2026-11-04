import os, re, shutil, subprocess, sys
src = open("control2a_split.py").read()
M = {
 "no_patch": ("    w.write_data_file = stub\n", "    pass\n"),
 "stub_skips_sha": ("        if Path(path) != Path(a.out) or got != a.out_sha:\n", "        if False:\n"),
 "no_array_digest": ("        if d != manifest[k]:\n", "        if False:\n"),
 "no_file_digest": ("    if (got_npz, got_man) != (a.npz_sha, a.manifest_sha):\n", "    if False:\n"),
 "no_call_count": ("    if len(calls) != 1:\n", "    if False:\n"),
 "no_after_sha": ("    if after != a.out_sha:\n", "    if False:\n"),
 "reach_ignores_alias": ("            if len(defs) != 1 or len(calls) != 1 or refs != [(calls[0].lineno, \"Load\")]:\n",
                         "            if len(defs) != 1 or len(calls) != 1:\n"),
 "reach_ignores_imports": ("                bad.append(f\"{rel}:{node.lineno} from {node.module} import {[n.name for n in node.names]}\")\n", "                pass\n"),
}
shutil.copy("control2a_split.py", "control2a_split.py.orig")
res = {}
try:
    for name, (old, new) in M.items():
        assert src.count(old) == 1, name
        open("control2a_split.py", "w").write(src.replace(old, new))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_control2a_split"], capture_output=True, text=True)
        tail = r.stderr.strip().splitlines()[-1]
        res[name] = ("KILLED" if r.returncode else "SURVIVED", tail)
        print(name, *res[name], flush=True)
finally:
    shutil.move("control2a_split.py.orig", "control2a_split.py")
print(f"killed {sum(v[0]=='KILLED' for v in res.values())}/{len(res)}")
