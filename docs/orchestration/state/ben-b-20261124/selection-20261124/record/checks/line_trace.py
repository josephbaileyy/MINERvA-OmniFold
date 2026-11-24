import sys, trace, unittest, os, ast
os.chdir(os.path.expanduser("~/s2r-wt")); sys.path.insert(0, "nd-unfolding/bsel")
tr = trace.Trace(count=1, trace=0)
def go():
    s = unittest.defaultTestLoader.discover("nd-unfolding/bsel", pattern="test_bsel.py", top_level_dir="nd-unfolding/bsel")
    unittest.TextTestRunner(stream=open(os.devnull, "w")).run(s)
tr.runfunc(go)
counts = tr.results().counts
path = os.path.abspath("nd-unfolding/bsel/bsel_select.py"); src = open(path).read()
exe = {n.lineno for n in ast.walk(ast.parse(src)) if isinstance(n, ast.stmt) and not isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))}
hit = {ln for (fn, ln), c in counts.items() if os.path.abspath(fn) == path}
miss = sorted(exe - hit); lines = src.splitlines()
print(f"{len(exe)-len(miss)}/{len(exe)} statement lines hit")
for ln in miss: print(f"  {ln}: {lines[ln-1].strip()[:110]}")
