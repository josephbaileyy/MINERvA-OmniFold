#!/bin/bash
# RDX c1 env probe (the director's go, 2026-11-15): read-only, writes nothing on the cluster.
# omnifold_py310 imports uproot and numpy; omnifile_io.cycles on the staged base_cv.root opened by O_NOATIME.
B=/pscratch/sd/j/josephrb/rdx-20261112b; D=$B/deploy; F=$B/out/stage/base_cv.root
P=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "deploy HEAD $(git -C "$D" rev-parse HEAD) porcelain $(git -C "$D" status --porcelain --untracked-files=all | wc -l)"
ls -l "$P"
"$P" -I -B - "$D" "$F" <<'EOF'
import json, os, sys, time
d, f = sys.argv[1], sys.argv[2]
import numpy, uproot
print(json.dumps({"python": sys.executable, "version": sys.version.split()[0], "numpy": numpy.__version__,
                  "uproot": uproot.__version__}))
sys.path.insert(0, os.path.join(d, "measurement-paper", "phase1", "mp1"))
import omnifile_io as io
import compare_omnifiles as co
print(json.dumps({"omnifile_io": io.__file__, "compare_omnifiles": co.__file__, "has_same": hasattr(co, "same"),
                  "root_imported": "ROOT" in sys.modules}))
def st(p):
    s = os.stat(p); return {"size": s.st_size, "atime_ns": s.st_atime_ns, "mtime_ns": s.st_mtime_ns}
s0 = st(f)
fd = os.open(f, os.O_RDONLY | os.O_NOATIME)
with os.fdopen(fd, "rb") as fh:
    cyc = io.cycles(fh)
s1 = st(f)
print(json.dumps({"file": f, "cycles": cyc, "stat_before": s0, "stat_after": s1, "unchanged": s0 == s1,
                  "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
EOF
echo "python rc=$?"
