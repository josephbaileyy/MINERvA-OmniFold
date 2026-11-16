"""The director's batch condition (2026-11-13), widened from check_dub_paths.py (1f083854): from `g2r_jobs.py tables` at
M, (a) all 529 run labels are distinct; (b) every path an unfold job (g2r_job.sbatch) writes under $O, as g2r_job.sbatch
and g2r_env.sh's g2r_preflight write them at M, is per-job, per-lane, per-label or per-job-id, and the write sets of all
the unfold jobs are pairwise disjoint. The write sites are listed from the bound files' text, and any $O path the list
does not cover fails the check. Exit 0 only if all of it holds.
    python3 -I check_g2r_paths.py <tables dir> <deploy at M> <job=id> ...   (jobs not given get the placeholder <job id>)"""
import re
import subprocess
import sys
from pathlib import Path

tables, deploy = Path(sys.argv[1]), Path(sys.argv[2])
ids = dict(a.split("=", 1) for a in sys.argv[3:])
head = subprocess.run(["git", "-C", str(deploy), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
print("deploy HEAD", head)
rows = [ln.split("\t") for ln in (tables / "runs_g2r.tsv").read_text().splitlines()]
hdr, rows = rows[0], rows[1:]
J, L, LAB = hdr.index("job"), hdr.index("lane"), hdr.index("label")
labels = [r[LAB] for r in rows]
dups = sorted({x for x in labels if labels.count(x) > 1})
print(f"(a) runs {len(rows)}, labels {len(labels)}, distinct {len(set(labels))}, duplicated {dups}")
UNFOLD = [j for j in dict.fromkeys(r[J] for r in rows) if j != "envtest"]
by = {j: [r for r in rows if r[J] == j] for j in UNFOLD}
print(f"    unfold jobs {len(UNFOLD)}: " + ", ".join(f"{j} {len(by[j])}" for j in UNFOLD)
      + f"; envtest {sum(1 for r in rows if r[J] == 'envtest')}")

sb = subprocess.run(["git", "-C", str(deploy), "show", f"{head}:2d-unfolding/cov2d/g2r/jobs/g2r_job.sbatch"],
                    capture_output=True, text=True).stdout
env = subprocess.run(["git", "-C", str(deploy), "show", f"{head}:2d-unfolding/cov2d/g2r/jobs/g2r_env.sh"],
                     capture_output=True, text=True).stdout
pre = env[env.index("g2r_preflight()"):]
pre = pre[:pre.index("\n}\n")]
# every $O-rooted path each file names (writes and reads); the reads are the tables, listed as such
named = sorted(set(re.findall(r'\$O/[^"\s);]*', sb + "\n" + pre)) | set(re.findall(r'#SBATCH --output=(\S+)', sb)))
COVERED = {
    "$O/tables/runs_g2r.tsv": "read", "$O/tables/jobs_g2r.tsv": "read",
    "$O/tmp/${SLURM_JOB_ID:-dry}": "per job id", "$O/tmp/${SLURM_JOB_ID:-local}": "per job id",
    "$O/logs/check-$JOB-$SLURM_JOB_ID.json": "per job", "$O/logs/mat-${SLURM_JOB_ID:-local}.json": "per job id",
    "$O/out/$label": "per label", "$O/out/$label/xsec.root": "per label", "$O/inventory/$label.jsonl": "per label",
    "$O/logs/$label.log": "per label", "$O/SHA256SUMS.$JOB.${want#$JOB.}": "per job lane",
    "$O/walls.$JOB.${want#$JOB.}.tsv": "per job lane", "$O/out": "shared dir (mkdir -p)", "$O/logs": "shared dir (mkdir -p)",
    "$O/inventory": "shared dir (mkdir -p)",
    "/pscratch/sd/j/josephrb/cov2d-g2r-20261112/logs/%x-%j.out": "per job name and id",
}
uncovered = [p for p in named if p not in COVERED]
print("(b) $O paths named in g2r_job.sbatch and g2r_preflight at M:")
for p in named:
    print(f"    {COVERED.get(p, 'NOT COVERED')}: {p}")


def writes(job, jid):
    lanes = sorted({r[L] for r in by[job]})
    s = {f"tmp/{jid}/", f"logs/check-{job}-{jid}.json", f"logs/mat-{jid}.json", f"logs/cov2dg2r-{job}-{jid}.out"}
    for ln in lanes:
        s |= {f"walls.{job}.{ln[len(job) + 1:]}.tsv", f"SHA256SUMS.{job}.{ln[len(job) + 1:]}"}
    for r in by[job]:
        s |= {f"out/{r[LAB]}/", f"out/{r[LAB]}/xsec.root", f"inventory/{r[LAB]}.jsonl", f"logs/{r[LAB]}.log"}
    return s


W = {j: writes(j, ids.get(j, f"<{j} id>")) for j in UNFOLD}
shared = []
for i, a in enumerate(UNFOLD):
    for b in UNFOLD[i + 1:]:
        x = W[a] & W[b]
        if x:
            shared.append((a, b, sorted(x)[:5]))
        lab = {r[LAB] for r in by[a]} & {r[LAB] for r in by[b]}
        if lab:
            shared.append((a, b, sorted(lab)[:5]))
pairs = len(UNFOLD) * (len(UNFOLD) - 1) // 2
print(f"    write sets: " + ", ".join(f"{j} {len(W[j])}" for j in UNFOLD))
print(f"    pairs checked {pairs}; pairs sharing a path or label: {len(shared)} {shared}")
for j in UNFOLD:
    print(f"    {j} per-job paths:", " ".join(sorted(p for p in W[j] if not p.startswith(("out/", "inventory/"))
                                                 and not (p.startswith("logs/") and p[5:-4] in {r[LAB] for r in by[j]}))))
ok = not dups and not uncovered and not shared and len(labels) == 529
print("G2R-PATHS", "PASS" if ok else "STOP", f"(uncovered {uncovered})" if uncovered else "")
sys.exit(0 if ok else 1)
