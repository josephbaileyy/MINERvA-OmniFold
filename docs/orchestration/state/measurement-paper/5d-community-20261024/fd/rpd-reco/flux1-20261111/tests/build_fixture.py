"""Build a fake flux1 root with #848's own private-prepare writer. usage: build_fixture.py ROOT MODE"""
import json, os, sys, uuid
from pathlib import Path
sys.path.insert(0, sys.argv[3])
import fd_rpd_reco as r
import fd_rpd_reco_custody as c
root = Path(sys.argv[1]); mode = sys.argv[2]
root.mkdir(mode=0o700)
run = root / "run"
for d in ("run/original-inputs", "run/mat-data/PLOTUTILSROOT", "run/prepare-check", "run/tmp", "run/real-mnv-check"):
    (root / d).mkdir(parents=True)
(root / "run/original-inputs/abcd-lat_1A.npz").write_bytes(b"DATA" * 100)
(root / "run/mat-data/PLOTUTILSROOT/flux.root").write_bytes(b"MAT")
for n in ("runner.sh", "strace-probe.txt"):
    (root / n).write_text(n + "\n")
(root / "connect.log").write_text("== runner start\nMAT setup exit status: 0\n== runner end rc=0\n")
if mode != "unfinished":
    (root / "connect.rc").write_text("rc=0 end=2026-11-11T00:00:00Z\n")
for n in ("cov2d-fence.json", "trace-policy.json", "extract-config.json", "flux-extract.json", "flux-custody.json", "flux-extract.strace"):
    (run / n).write_text(json.dumps({"name": n}) + "\n")
(run / "real-mnv-check/real-mnv-check.json").write_text('{"status": "PASS"}\n')
os.environ["FD_RPD_RECO_CONNECT_ID"] = str(uuid.uuid4())
snap = c.environment_snapshot()
if mode in ("full", "leak", "orphan", "big"):
    ref = c.write_private_prepare(r, run, "prestage", {"connect_id": os.environ["FD_RPD_RECO_CONNECT_ID"], "environment_snapshot": snap}, protected_roots=[])
    print("reference", ref)
if mode == "leak":
    value = snap["fingerprints"]["HOME"]
    (run / "flux-custody.json").write_text(json.dumps({"x": value}) + "\n")
if mode == "orphan":
    (run / "prestage-reference.json").unlink()
if mode == "fpword":
    (run / "flux-custody.json").write_text('{"fingerprints": {}}\n')
if mode == "big":
    with open(run / "flux-extract.strace", "wb") as f:
        f.truncate(70 * 1024 * 1024)
