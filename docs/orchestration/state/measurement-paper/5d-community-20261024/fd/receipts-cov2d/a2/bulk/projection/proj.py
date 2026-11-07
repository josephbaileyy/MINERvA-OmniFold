"""Read-only projection of the COV2D cap total (director's request 2026-11-06). Input: out.txt (sacct, walls, runs)."""
import sys, statistics as st
from datetime import datetime, timezone, timedelta
CAP = 165.8; PST = timezone(timedelta(hours=-8))
sec = {}; cur = None
for ln in open(sys.argv[1]).read().splitlines():
    if ln.startswith("NOW "): now = datetime.fromisoformat(ln[4:].replace("Z", "+00:00")).timestamp(); continue
    if ln.startswith("== "): cur = ln[3:]; sec[cur] = []; continue
    if cur and ln.strip(): sec[cur].append(ln)
def lt(s): return datetime.fromisoformat(s).replace(tzinfo=PST).timestamp()
jobs = {}
for ln in sec["SACCT"]:
    f = ln.split("|")
    if not f[1].startswith("cov2d-"): continue
    jobs[f[0]] = dict(id=f[0], name=f[1][6:], state=f[2].split()[0], el=int(f[3]), lim=int(f[5]) * 60,
                      start=None if f[7] == "Unknown" else lt(f[7]))
walls = {}  # (job, lane) -> {label: (t0, t1)}
for ln in sec["WALLS"]:
    b, lab, t0, t1, rc = ln.split("\t")
    _, job, lane, _ = b.split(".")
    walls.setdefault((job, lane), {})[lab] = (int(t0), int(t1))
runs = {}  # job -> lane -> [(label, est)]
for ln in sec["RUNS"]:
    f = ln.split("\t")
    runs.setdefault(f[1], {}).setdefault(f[2].split(".")[1], []).append((f[3], int(f[-1])))
SKIP = {"G18_Ba": {"B_G18_001"}, "G18_Ta": {"T_G18_5720000"}, "G18_Ua": {"U_G18_Flux_0"},
        "G18_L": {"L_G18_BeamAngleX_0", "X_G18"}}
def cls(job): t, c = job.split("_"); return t, c[0]
# per (truth, class) wall/est ratios from every finished run
est = {lab: e for j in runs for l in runs[j] for lab, e in runs[j][l]}
ratios = {}
for (job, lane), d in walls.items():
    if job == "pilot": continue
    for lab, (t0, t1) in d.items(): ratios.setdefault(cls(job), []).append((t1 - t0) / est[lab])
print("ratio wall/est_s by class: n, mean, sd, min, p90, max")
for k in sorted(ratios):
    r = sorted(ratios[k]); print("  %-10s %3d %.3f %.3f %.3f %.3f %.3f" % (k, len(r), st.mean(r), st.pstdev(r), r[0], r[int(.9 * len(r))], r[-1]))
# calibrate the job tail: elapsed - (last t1 - start) on ended jobs
tails = []
for j in jobs.values():
    if j["state"] != "RUNNING" and j["name"] in runs and j["start"]:
        last = max(t1 for (jb, l), d in walls.items() if jb == j["name"] for t0, t1 in d.values())
        tails.append(j["start"] + j["el"] - last)
tail = max(tails); print("job tail after last run (s), ended jobs:", tails)
def project(job, start, q):
    """projected elapsed (s) at ratio quantile fn q(class) for the remaining runs; the in-progress run is at least its age"""
    ends = []
    for lane, rows in runs[job].items():
        d = walls.get((job, lane), {})
        t = max([t1 for t0, t1 in d.values()] or [start + 60])
        rem = [(lab, e) for lab, e in rows if lab not in d and lab not in SKIP.get(job, ())]
        if not rem: ends.append(t); continue
        r = q(cls(job))
        first = max(rem[0][1] * r, now - t) if t <= now else rem[0][1] * r
        ends.append(t + first + sum(e * r for lab, e in rem[1:]))
    return max(ends) + tail - start
qs = {"low": lambda k: min(ratios[k]), "point": lambda k: st.mean(ratios[k]), "p90": lambda k: sorted(ratios[k])[int(.9 * len(ratios[k]))],
      "high": lambda k: max(ratios[k])}
spent = sum(j["el"] for j in jobs.values() if j["state"] not in ("RUNNING", "PENDING")) / 3600
print("\nspent (ended, actual): %.3f node-h" % spent)
proj = {}
print("\n%-9s %-9s %-8s %7s | projected charge node-h (low/point/p90/high) | limit | projected end UTC (point)" % ("job", "id", "state", "age_h"))
for j in sorted(jobs.values(), key=lambda j: j["id"]):
    if j["state"] not in ("RUNNING", "PENDING"): continue
    s = j["start"] or now
    p = {k: min(project(j["name"], s, q), j["lim"]) / 3600 for k, q in qs.items()}
    proj[j["id"]] = dict(j, p=p, end=s + p["point"] * 3600)
    print("%-9s %-9s %-8s %7.2f | %.2f / %.2f / %.2f / %.2f | %.2f | %s" % (j["name"], j["id"], j["state"], (now - s) / 3600 if j["start"] else 0,
          p["low"], p["point"], p["p90"], p["high"], j["lim"] / 3600, datetime.fromtimestamp(s + p["point"] * 3600, timezone.utc).strftime("%H:%MZ") if j["start"] else "(not started)"))
# Tc as a full T job (AR23); G18_C as its own longest lane 3464 s at the class-L ratio
tc = {k: min(project("AR23_Tc", now, q), 458 * 60) / 3600 for k, q in qs.items()}
gc = {k: min(3464 * qs[k](("G18", "L")) + tail, 79 * 60) / 3600 for k in qs}
print("AR23_Tc (not submitted)  %s | 7.63" % " / ".join("%.2f" % tc[k] for k in qs))
print("G18_C   (not submitted)  %s | 1.32" % " / ".join("%.2f" % gc[k] for k in qs))
print("\nprojected FINAL actual spend (everything incl. Tb, Tc, G18_C): " + "  ".join(
    "%s=%.2f" % (k, spent + sum(v["p"][k] for v in proj.values()) + tc[k] + gc[k]) for k in qs) + "   cap=%.1f" % CAP)
print("all-at-limit bound: %.2f" % (spent + sum(v["lim"] for v in proj.values()) / 3600 + 458 / 60 + 79 / 60))
# gate-time simulation: held = limits of unfinished; Tb pending charged at its limit until it ends
running = sorted([v for v in proj.values() if v["state"] == "RUNNING"], key=lambda v: v["end"])
def gate_total(t, extra):
    sp = spent + sum(v["p"]["point"] for v in running if v["end"] <= t)
    held = sum(v["lim"] for v in proj.values() if not (v["state"] == "RUNNING" and v["end"] <= t)) / 3600
    return sp + held + extra
print("\ngate total (point) after each projected end; Tc wants 7.633, G18_C wants 1.317, both 8.950:")
for v in running:
    t = v["end"]
    print("  %s %-9s ends -> Tc alone %.2f | G18_C alone %.2f | both %.2f" % (datetime.fromtimestamp(t, timezone.utc).strftime("%H:%MZ"), v["name"],
          gate_total(t, 7.633), gate_total(t, 1.317), gate_total(t, 8.950)))
