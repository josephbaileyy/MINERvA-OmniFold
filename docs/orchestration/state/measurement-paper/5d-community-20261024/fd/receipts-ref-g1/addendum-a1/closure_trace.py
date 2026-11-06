"""Run REF-G1's suite under sys.monitoring LINE events and check the closure grep's "not reached" rows.

    python3 -B closure_trace.py REPO DISPOSITIONS.tsv OUT.txt

Every grep hit whose disposition says "not reached" must not execute with a REF-G1 production frame (ref_g1.py,
ref_g1_read.py) on the stack; such a hit is printed as REACHED and the exit status is 1. One that executes only from
the test file's own fixtures is printed as "fixture-only". Hits classed otherwise are listed with whether the suite executed them
(informative: the suite reaches only what its fixtures exercise, so silence is not proof of absence)."""
import csv
import sys
import unittest
from pathlib import Path

repo, tsv, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]), Path(sys.argv[3])
rows = list(csv.DictReader(open(tsv), delimiter="\t", quoting=csv.QUOTE_NONE))
files = {str((repo / r["file"]).resolve()) for r in rows}
hit, via_run = set(), set()
watch = {(str((repo / r["file"]).resolve()), int(r["line"])) for r in rows if r["disposition"].startswith("not reached")}
PROD = {str((repo / "nd-unfolding" / "ref_g1" / f).resolve()) for f in ("ref_g1.py", "ref_g1_read.py")}
mon = sys.monitoring
TOOL = mon.PROFILER_ID


def on_line(code, line):
    f = code.co_filename
    if f in files:
        hit.add((f, line))
        if (f, line) in watch:
            fr = sys._getframe(1)
            while fr is not None:
                if fr.f_code.co_filename in PROD:
                    via_run.add((f, line))
                    return mon.DISABLE
                fr = fr.f_back
            return None  # keep watching: a later call may come from the run path
    return mon.DISABLE


mon.use_tool_id(TOOL, "closure-trace")
mon.register_callback(TOOL, mon.events.LINE, on_line)
mon.set_events(TOOL, mon.events.LINE)
sys.path.insert(0, str(repo / "nd-unfolding" / "ref_g1"))
sys.argv = ["test_ref_g1"]
import test_ref_g1  # noqa: E402

result = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromModule(test_ref_g1))
mon.set_events(TOOL, 0)
bad, lines = 0, []
for r in rows:
    key = (str((repo / r["file"]).resolve()), int(r["line"]))
    ran = key in hit
    nr = r["disposition"].startswith("not reached")
    if nr and key in via_run:
        bad += 1
    tag = "REACHED" if nr and key in via_run else ("fixture-only" if nr and ran else ("ran" if ran else "not-run"))
    lines.append(f"{tag}\t{r['file']}:{r['line']}\t"
                 f"{r['function']}\t{r['disposition'][:60]}")
summary = (f"suite ran={result.testsRun} ok={result.wasSuccessful()}; rows={len(rows)}; "
           f"not-reached rows={sum(r['disposition'].startswith('not reached') for r in rows)}; "
           f"not-reached rows executed from the run path={bad}; fixture-only={sum(l.startswith('fixture-only') for l in lines)}")
out.write_text(summary + "\n" + "\n".join(lines) + "\n")
print(summary)
sys.exit(1 if bad or not result.wasSuccessful() else 0)
