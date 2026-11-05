"""The full run's gate projection, computed offline from the B4 dry run's own records (limitation-resolver, 2026-11-04).

It calls the bound estimator_stability_probe.project() (blob 25179f9f, at M_A1 cc54d86f) on the committed copies of
the dry run's queue (connect/queue.tsv) and its nine start/end records (dry/tasks/), at now = t0 = the last dry-run
end. That is what the full run's first gate sees, with no full-run time elapsed yet, and it excludes the full job's
own setup time. It reads files only and writes nothing.

    python3 -B project_offline.py <deploy at M_A1> <receipts-stab-a1r dir>
"""
import hashlib
import json
import sys
from pathlib import Path

D, R = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(D / "nd-unfolding"))
import estimator_stability_probe as ep  # noqa: E402

probe = D / "nd-unfolding/estimator_stability_probe.py"
queue_path, log = R / "connect/queue.tsv", R / "dry/tasks"
q, rec = ep.read_queue(queue_path), ep.read_log(log)
t0 = max(v["end"] for v in rec.values() if "end" in v)
p = ep.project(t0, t0, q, rec)
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()  # noqa: E731
print(json.dumps({
    "probe_sha256": sha(probe), "queue_sha256": sha(queue_path),
    "records": {f.name: sha(f) for f in sorted(log.glob("*.start")) + sorted(log.glob("*.end"))},
    "now_equals_t0": t0, "queue_tasks": len(q), "dry_tasks_ended": sum("end" in v for v in rec.values()),
    "CAP_NODE_H": ep.CAP_NODE_H, "B2_STOP_RATIO": ep.B2_STOP_RATIO, "LANES": ep.LANES,
    **p}, indent=1, sort_keys=True))
