"""Event simulation of sbatch_fd_stab.sh's dry + full runs through the real probe.gate (coverage-5b-audit, #720 r2 and r3).
Run with cwd = a checkout's nd-unfolding, PYTHONDONTWRITEBYTECODE=1. Args: alpha (the dry run's per-unfold time over
the full run's), B2 factor, a scratch dir, and optionally a log-normal per-task noise sigma and a seed.
Committed as the audit wrote it, with this docstring updated (FD-STAB-DECLARATION.md §7)."""
import heapq, shutil, sys, tempfile
from argparse import Namespace
from pathlib import Path
sys.path.insert(0, ".")
import estimator_stability_probe as probe

def queue_file(d):
    a = Namespace(npz="n", bkg="b", bank="k", detector_dir="d", expect_npz_sha256="h", expect_bkg_sha256="h",
                  closure_ratio_dir="r", runs="R")
    lines = probe.task_lines(a)
    (d / "queue.tsv").write_text("\n".join(lines) + "\n")
    dry = [l for l in lines if l.split("\t")[0] in probe.DRY_TASKS]
    (d / "dry.tsv").write_text("\n".join(dry) + "\n")

def run(qpath, log, lanes, rate, t0, cap, overhead=0.0):
    """Feed the queue through gate at each free lane, as xargs -P does; stop starting on the first refusal."""
    q = [t for t, _, _ in probe.read_queue(qpath)]
    n = {t: u for t, _, u in probe.read_queue(qpath)}
    c = {t: cc for t, cc, _ in probe.read_queue(qpath)}
    now, running, i, stopped = t0 + overhead, [], 0, None
    while True:
        while len(running) < lanes and i < len(q) and stopped is None:
            g = probe.gate(q[i], qpath, log, t0, cap, now=now)
            if g == 3:
                stopped = (q[i], (log / "STOP").read_text()[:160].replace("\n", " "))
            elif g == 0:
                heapq.heappush(running, (now + n[q[i]] * rate[c[q[i]]] * (float(RNG.lognormal(0, NOISE)) if NOISE else 1.0), q[i]))
            i += 1
        if not running:
            break
        end, t = heapq.heappop(running)   # xargs aborts on 255 but running tasks finish only if the script waits:
        now = end                          # here they are allowed to finish (optimistic for a STOP)
        (log / f"{t}.end").write_text(f"{now}\n")
    return now, stopped, i, len(q)

alpha, f2 = float(sys.argv[1]), float(sys.argv[2])
NOISE = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
RNG = __import__("numpy").random.default_rng(int(sys.argv[5]) if len(sys.argv) > 5 else 0)
U = probe.UNIT_S
true8 = {"control": U, "B2": f2 * U, "B3a": U, "B3b": U}
dry_rate = {k: alpha * v for k, v in true8.items()}
d = Path(tempfile.mkdtemp(dir=sys.argv[3]))
queue_file(d)
ld, lf = d / "log-dry", d / "log-full"; ld.mkdir(); lf.mkdir()
ov = 120.0  # env setup before T0
end_d, st_d, *_ = run(d / "dry.tsv", ld, 8, dry_rate, 0.0, 8.0)
dry_charge = (end_d + ov) / 3600
for p in list(ld.glob("*.start")) + list(ld.glob("*.end")):
    shutil.copy(p, lf / p.name)
t0 = 100000.0
p0 = probe.project(t0, t0, probe.read_queue(d / "queue.tsv"), probe.read_log(lf))
cap_left = 8.0 - dry_charge
end_f, st_f, started, nq = run(d / "queue.tsv", lf, 8, true8, t0, cap_left)
full_charge = (end_f - t0 + ov) / 3600
print(f"alpha={alpha} B2={f2}x  dry={dry_charge:.2f}  cap_left={cap_left:.2f}  first-gate projection={p0['projected_node_h']:.2f} "
      f"(true remainder {(sum(u*true8[c] for t,c,u in probe.read_queue(d/'queue.tsv') if t not in probe.DRY_TASKS))/8/3600:.2f})  "
      f"full={full_charge:.2f} total={dry_charge+full_charge:.2f}  stop={'none' if st_f is None else st_f[1][:110]}  "
      f"queue reached {started}/{nq}")
outcome = ("SLURM_KILL" if full_charge > cap_left else "COMPLETE") if st_f is None else f"STOP@{started}/{nq}"
print(f"OUTCOME alpha={alpha} B2={f2} {outcome} spent={min(full_charge, cap_left) + dry_charge:.2f}")
shutil.rmtree(d)
