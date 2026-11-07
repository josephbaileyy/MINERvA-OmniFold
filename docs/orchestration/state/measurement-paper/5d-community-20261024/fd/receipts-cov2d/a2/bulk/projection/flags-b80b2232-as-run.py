"""The director's two flag triggers on the cap projection (2026-11-06), against the 15:22:02Z baseline proj.txt:
  RUN-OVER-MAX  a finished run's wall/est_s ratio exceeds its (truth, class) max in the baseline table;
  END-SLIP      a baseline job still unended more than 1 h past its p90 end (start + p90 charge);
  OVER-1.3MEAN  (the director, 2026-11-06: a trigger that does not move) a run absent from the fixed snapshot whose
                ratio exceeds 1.3x its (truth, class) mean in the fixed projection.
Usage: flags.py proj.txt out-now.txt [fixed-proj.txt fixed-out.txt]
Prints FLAG lines and exits 1 if any trigger fires; 0 otherwise."""
import re, sys
from datetime import datetime, timezone, timedelta
PST = timezone(timedelta(hours=-8))
base = open(sys.argv[1]).read().splitlines()
cmax = {(m.group(1), m.group(2)): float(m.group(3)) for ln in base
        for m in [re.match(r"\s+\('(\w+)', '(\w)'\)\s+\d+ \S+ \S+ \S+ \S+ (\S+)$", ln)] if m}
p90 = {m.group(1): float(m.group(2)) for ln in base
       for m in [re.match(r"\S+\s+(\d+)\s+(?:RUNNING|PENDING)\s+\S+ \| \S+ / \S+ / (\S+) / ", ln)] if m}
assert len(cmax) == 8 and len(p90) == 17, (cmax, p90)
fixed_mean, fixed_runs = {}, None
if len(sys.argv) > 3:
    fixed_mean = {(m.group(1), m.group(2)): float(m.group(3)) for ln in open(sys.argv[3]).read().splitlines()
                  for m in [re.match(r"\s+\('(\w+)', '(\w)'\)\s+\d+ (\S+) \S+ \S+ \S+ \S+$", ln)] if m}
    assert len(fixed_mean) == 8, fixed_mean
    fixed_runs, s0 = set(), None
    for ln in open(sys.argv[4]).read().splitlines():
        if ln.startswith("== "): s0 = ln[3:]; continue
        if s0 == "WALLS" and ln.strip(): f = ln.split("\t"); fixed_runs.add((f[0], f[1]))
sec, cur = {}, None
for ln in open(sys.argv[2]).read().splitlines():
    if ln.startswith("NOW "): now = datetime.fromisoformat(ln[4:].replace("Z", "+00:00")).timestamp(); continue
    if ln.startswith("== "): cur = ln[3:]; sec[cur] = []; continue
    if cur and ln.strip(): sec[cur].append(ln)
est = {ln.split("\t")[3]: int(ln.split("\t")[-1]) for ln in sec["RUNS"]}
flags, nrun = [], 0
for ln in sec["WALLS"]:
    b, lab, t0, t1, rc = ln.split("\t"); job = b.split(".")[1]
    if job == "pilot" or lab not in est: continue
    t, c = job.split("_"); r = (int(t1) - int(t0)) / est[lab]; nrun += 1
    if fixed_runs is not None and (b, lab) not in fixed_runs and round(r, 3) > round(1.3 * fixed_mean[(t, c[0])], 3):
        flags.append("FLAG OVER-1.3MEAN %s %s ratio %.3f > 1.3 x fixed mean %.3f" % (job, lab, r, fixed_mean[(t, c[0])]))
    if round(r, 3) > cmax[(t, c[0])]: flags.append("FLAG RUN-OVER-MAX %s %s ratio %.3f > class max %.3f" % (job, lab, r, cmax[(t, c[0])]))
live = 0
for ln in sec["SACCT"]:
    f = ln.split("|")
    if f[0] not in p90 or f[2].split()[0] not in ("RUNNING", "PENDING") or f[7] == "Unknown": continue
    live += 1
    start = datetime.fromisoformat(f[7]).replace(tzinfo=PST).timestamp(); due = start + (p90[f[0]] + 1) * 3600
    if now > due: flags.append("FLAG END-SLIP %s %s still %s %.2f h past p90+1h" % (f[1], f[0], f[2], (now - due) / 3600))
print("%s runs=%d started-unended=%d flags=%d" % (datetime.fromtimestamp(now, timezone.utc).strftime("%FT%TZ"), nrun, live, len(flags)))
print("\n".join(flags)) if flags else None
sys.exit(1 if flags else 0)
