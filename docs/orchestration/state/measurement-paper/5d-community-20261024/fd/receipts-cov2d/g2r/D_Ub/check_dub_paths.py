"""The director's pre-launch condition for D_Ub (2026-11-13): from `g2r_jobs.py tables` at M, (a) every run label appears
once across all jobs, and D_Ub's labels and D_Ua's are disjoint; (b) every path a D_U* job writes under $O, as
g2r_job.sbatch and g2r_env.sh's g2r_preflight write them at M, is per-job or per-label, and D_Ub's set shares none with
D_Ua's. The write sites are listed from the bound files' text, and any $O or $TMPDIR write the list does not cover
fails the check. Exit 0 only if all of it holds.
    python3 -I check_dub_paths.py <tables dir> <deploy at M> <D_Ua job id> <D_Ub job id or 'next'>"""
import re
import subprocess
import sys
from pathlib import Path

tables, deploy, ua_id, ub_id = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
head = subprocess.run(["git", "-C", str(deploy), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
print("deploy HEAD", head)
rows = [ln.split("\t") for ln in (tables / "runs_g2r.tsv").read_text().splitlines()]
hdr, rows = rows[0], rows[1:]
J, L, LAB = hdr.index("job"), hdr.index("lane"), hdr.index("label")
labels = [r[LAB] for r in rows]
dups = sorted({x for x in labels if labels.count(x) > 1})
print(f"(a) runs {len(rows)}, labels {len(labels)}, distinct {len(set(labels))}, duplicated {dups}")
by = {j: [r for r in rows if r[J] == j] for j in ("D_Ua", "D_Ub")}
ua, ub = {r[LAB] for r in by["D_Ua"]}, {r[LAB] for r in by["D_Ub"]}
print(f"    D_Ua labels {len(ua)}, D_Ub labels {len(ub)}, shared {sorted(ua & ub)}")
print(f"    D_Ub labels: {' '.join(sorted(ub))}")

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


wa, wb = writes("D_Ua", ua_id), writes("D_Ub", ub_id if ub_id != "next" else "<D_Ub id>")
shared = sorted(wa & wb)
print(f"    D_Ua writes {len(wa)} paths, D_Ub writes {len(wb)} paths, shared {shared}")
print("    D_Ub per-job paths:", " ".join(sorted(p for p in wb if not p.startswith(("out/", "inventory/", "logs/A_")))))
ok = not dups and not (ua & ub) and not uncovered and not shared and len(ub) == len(by["D_Ub"])
print("DUB-PATHS", "PASS" if ok else "STOP", f"(uncovered {uncovered})" if uncovered else "")
sys.exit(0 if ok else 1)
