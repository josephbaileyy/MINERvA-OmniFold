"""Build a fake rpd_flux1 root with #848's own private-prepare writer (revision 2).

usage: build_fixture.py ROOT MODE ND_UNFOLDING PROTECTED
  PROTECTED: the fixture's protected tree; PROTECTED/MParamFiles/data/FluxConstraints/<constraint file> plays the
  listed exception and PROTECTED/other a second protected path.
modes: unfinished timeout full leak orphan nopriv fpword big preadmissing otheroverlap productdiffers
"""

import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path

root, mode, nd, protected = Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4])
sys.path.insert(0, nd)
import fd_rpd_reco as r  # noqa: E402
import fd_rpd_reco_custody as c  # noqa: E402

PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
exception = protected / "MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"
other = protected / "other"
if not exception.exists():
    exception.parent.mkdir(parents=True)
    exception.write_text("constraint stand-in\n")
    (other / "x.npz").parent.mkdir(parents=True)
    (other / "x.npz").write_bytes(b"other protected input\n")
    (protected / "dumps").mkdir()
    (protected / "dumps/lat_1A.npz").write_bytes(b"DATA" * 100)

root.mkdir(mode=0o700)
run = root / "run"
for d in ("run/original-inputs", "run/mat-data/MPARAMFILES/FluxConstraints", "run/prepare-check", "run/tmp", "run/real-mnv-check", "clone", "tools"):
    (root / d).mkdir(parents=True)
(root / "clone/big-not-sent.bin").write_bytes(b"clone\n")
(root / "production-config.ready.json").write_text(json.dumps({"cov2d_protected_paths": [str(exception), str(other)]}) + "\n")
(root / "job.id").write_text("4242\n")
(root / "job-host.txt").write_text("jobid=4242 host=nid001 start=2026-11-11T00:00:00Z\n")
for name in ("job.out", "job.err", "rpd_flux1_job.sh", "strace-probe.txt", "fence-overlap.txt", "exception-stat-outer.txt"):
    (root / name).write_text(name + "\n")
(root / "connect.log").write_text("MAT setup exit status: 0\n")
if mode not in ("unfinished", "timeout"):
    (root / "job-host.txt").write_text("jobid=4242 host=nid001 start=2026-11-11T00:00:00Z\nend=2026-11-11T00:30:00Z rc=0\n")
    (root / "job.rc").write_text("rc=0 end=2026-11-11T00:30:00Z\n")
for n in ("cov2d-fence.json", "trace-policy.json", "extract-config.json", "flux-custody.json", "flux-extract.strace"):
    (run / n).write_text(json.dumps({"name": n}) + "\n")
(run / "real-mnv-check/real-mnv-check.json").write_text('{"status": "PASS"}\n')

products = {}
if mode in ("full", "preadmissing", "otheroverlap", "productdiffers"):
    for playlist in PLAYLISTS:  # 12 x 50 MiB, sparse: the real products total about 590 MB
        path = run / f"flux-factors-{playlist}.npz"
        with open(path, "wb") as handle:
            handle.truncate(50 * 1024 * 1024)
        products[playlist] = {"path": str(path), "sha256": r.digest(path), "rows": 1}
if mode == "productdiffers":  # one product changed after flux-extract recorded its sha256
    with open(run / "flux-factors-1M.npz", "r+b") as handle:
        handle.write(b"changed")
(run / "flux-extract.json").write_text(json.dumps({"schema": "fd-rpd-reco-flux-extract/2", "factor_products": products}) + "\n")


def staged_item(original: Path, staged: Path) -> dict:
    data = original.read_bytes()  # macOS has no O_NOATIME: read before the bracket, so the bracket sees no atime move
    started = time.time_ns()
    before = c.source_stat(original)
    staged.write_bytes(data)
    after = c.source_stat(original)
    item = {
        "original": str(original.resolve()),
        "staged": str(staged.resolve()),
        "sha256": r.digest(original),
        "stat_before": before,
        "stat_after": after,
        "staging_utc_ns": {"started": started, "ended": time.time_ns()},
    }
    if mode == "preadmissing":
        del item["staging_utc_ns"]
    return item


os.environ["FD_RPD_RECO_CONNECT_ID"] = str(uuid.uuid4())
snapshot = c.environment_snapshot()
if mode in ("full", "leak", "orphan", "big", "preadmissing", "otheroverlap", "productdiffers"):
    item = staged_item(exception, run / "original-inputs/abcd-sorted_NuEConstraint_FHC_RHC_IMD.txt")
    native = dict(item)
    native["staged"] = str((run / "mat-data/MPARAMFILES/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt").resolve())
    Path(native["staged"]).write_bytes(Path(item["staged"]).read_bytes())
    files = {item["original"]: item}
    dump = staged_item(protected / "dumps/lat_1A.npz", run / "original-inputs/ef01-lat_1A.npz")
    files[dump["original"]] = dump
    if mode == "otheroverlap":
        extra = staged_item(other / "x.npz", run / "original-inputs/9999-x.npz")
        files[extra["original"]] = extra
    prepared = {
        "connect_id": os.environ["FD_RPD_RECO_CONNECT_ID"],
        "environment_snapshot": snapshot,
        "files": files,
        "mat_dependencies": [
            {**native, "environment_key": "MPARAMFILES", "relative_path": "FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"}
        ],
    }
    print("reference", c.write_private_prepare(r, run, "prestage", prepared, protected_roots=[]))
if mode == "leak":
    (run / "flux-custody.json").write_text(json.dumps({"x": snapshot["fingerprints"]["HOME"]}) + "\n")
if mode == "orphan":
    (run / "prestage-reference.json").unlink()
if mode == "fpword":
    (run / "flux-custody.json").write_text('{"fingerprints": {}}\n')
if mode == "big":
    with open(run / "flux-extract.strace", "wb") as handle:
        handle.truncate(70 * 1024 * 1024)
print("built", mode, hashlib.sha256(mode.encode()).hexdigest()[:8])
