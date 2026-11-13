"""Dry run of #981's build against a #977 head (argv[1]). Writes nothing.

Run it from the top of a checkout that holds #981's package. In #981's own worktree it checks #981's quotes at the head
(PAPER_REF patched in memory) while the values producer and values files are #981's own. In a merge simulation
(merge_sim.sh) the whole tree is the head's, so the build also reads the head's make_values_fived16.py,
values_fived16.tex and values.tex. Every failed check is collected. A failure the director has ruled on
(ruled_baseline.txt, or a substring in RULED) is counted. Every other one is printed as NEW FAILURE, and the exit
status is 1. LaTeX comments are stripped before every count, as ruled for the re-pin (RP18)."""
import importlib.util, os, re, sys
sys.dont_write_bytecode = True
N = sys.argv[1]
p = "docs/orchestration/state/2d-closeout/stageF/methods/result-package-20261109/build_package.py"
spec = importlib.util.spec_from_file_location("bp", p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.PAPER_REF = N
_orig_at_ref = m.at_ref
m.at_ref = lambda path: re.sub(r"(?m)(?<!\\)%.*$", "", _orig_at_ref(path)) if path.endswith(".tex") else _orig_at_ref(path)
fails = []
m.need = lambda ok, msg: ok or fails.append(msg)
try:
    m.assemble()
except Exception as e:
    fails.append(f"EXCEPTION {type(e).__name__}: {e}")
RULED = ["is therefore not a measurement", "They are partial evidence on the bias", "reported beside it as a separate",
         "is built from the change in the unfolded", "so that its own size is poorly determined",
         "The source of the shape difference has not been identified"]
_norm = lambda f: re.sub(r"\b[0-9a-f]{8}\b", "HEAD", f)
BASE = set(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ruled_baseline.txt")).read().splitlines())
uniq = list(dict.fromkeys(fails))
new = [f for f in uniq if not any(r in f for r in RULED) and _norm(f)[:220] not in BASE]
print(f"#977 head {N}; ruled failures: {len(uniq) - len(new)}")
for f in new:
    print("NEW FAILURE -", f[:220])
print("DRYRUN", "PASS (only ruled failures)" if not new else f"NEW FAILURES ({len(new)})")
sys.exit(1 if new else 0)
