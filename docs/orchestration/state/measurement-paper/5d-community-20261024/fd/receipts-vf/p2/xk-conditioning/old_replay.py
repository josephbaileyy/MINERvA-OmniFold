# OLD-only replay of xk's step K (rulings (i)-(ii)), for the director's thread-order demonstration: no substitution.
import json, os, sys
from pathlib import Path
sys.path.insert(0, "/Users/josephbailey/s2r-wt/nd-unfolding")
import fd_vf_p2 as V
import fd_gencmp as GC, fd_xcov_steps as XS
work = Path(sys.argv[1])
fetch = Path("/Users/josephbailey/vf-p2-fetch-20261126")
V.xk_run_dir(fetch, work)
log, calls = [], []
rc = V.xk_replay(XS, GC, fetch, work, {}, log, calls)
print("rc", rc, "threads", os.environ.get("OPENBLAS_NUM_THREADS"), "reads", len(log))
