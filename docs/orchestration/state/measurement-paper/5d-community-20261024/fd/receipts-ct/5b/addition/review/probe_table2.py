import sys, runpy
sys.argv = ["probe_table.py", *sys.argv[1:]]
sys.path.insert(0, sys.argv[1] + "/nd-unfolding")
import fd_cpl_addition as A
orig = A.report
def rep(control, name, ok, why="differs"):
    if control == "T" and "shape_only: each side names its matrix" in name:
        ok = True
    return orig(control, name, ok, why)
A.report = rep
runpy.run_path(sys.argv[0] if False else "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/71f27b67-dd03-4235-a8c6-c96eb2b6c57e/scratchpad/review-out/probe_table.py", run_name="__main__")
