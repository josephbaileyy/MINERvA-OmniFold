"""Measure #981's build at a #977 head (argv[1]) twice in memory: the .tex text as read, and with LaTeX comments (an
unescaped % to the end of the line) stripped in at_ref. Prints the failure counts and each failure in only one set.
Writes nothing. Run from the #981 worktree root."""
import importlib.util, sys, re, subprocess
sys.dont_write_bytecode = True
N = sys.argv[1]
p = "docs/orchestration/state/2d-closeout/stageF/methods/result-package-20261109/build_package.py"
def run(strip):
    spec = importlib.util.spec_from_file_location("bp", p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.PAPER_REF = N
    fails = []; m.need = lambda ok, msg: ok or fails.append(msg)
    if strip:
        orig = m.at_ref
        m.at_ref = lambda path: re.sub(r"(?m)(?<!\\)%.*$", "", orig(path)) if path.endswith(".tex") else orig(path)
    try: m.assemble()
    except Exception as e: fails.append(f"EXCEPTION {type(e).__name__}: {e}")
    return list(dict.fromkeys(fails))
print("#981 tree", subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(), "; #977 head", N)
a, b = run(False), run(True)
print("failures as read:", len(a), "; with comments stripped:", len(b))
for f in b:
    if f not in a: print("ONLY WITH COMMENTS STRIPPED:", f)
for f in a:
    if f not in b: print("ONLY AS READ:", f)
