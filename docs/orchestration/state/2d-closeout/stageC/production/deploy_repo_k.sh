#!/bin/bash
# Deploy a package commit into $NS/repo_k (DESIGN §14.4 step 1). Run on a saul login node:
#   bash deploy_repo_k.sh <git-archive tar of the commit> <commit sha> <manifest.json sha256>
# Refuses while ANY 2dc_P_K* pack is in the queue (squeue, any state): Slurm runs a copy of the dispatcher taken at
# submission, which checks the deployed sbatch_prod.sh against the MEMBER_SHA of ITS commit, so a redeploy under a
# queued pack would make it refuse at start (a pack-level STOP, DESIGN §14.3). Also refuses if squeue is unreadable.
# The previous repo_k is moved, not deleted, to $NS/tmp/repo_k.<its commit>.retired. After extracting, it copies
# driver_p1.py into 2d-unfolding/ (as §10.1) and checks every manifest entry; any mismatch exits 1.
set -eo pipefail
NS=/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015
TAR=${1:?tar}; COMMIT=${2:?commit}; MSHA=${3:?manifest sha256}
[ -f "$TAR" ] || { echo "REFUSE: no $TAR"; exit 4; }
Q=$(squeue -h -u "${USER:-josephrb}" -o '%i|%j|%T') || { echo "REFUSE: squeue unreadable"; exit 4; }
K=$(printf '%s\n' "$Q" | awk -F'|' '$2 ~ /^2dc_P_K/' || true)
[ -z "$K" ] || { echo "REFUSE: packs are queued; no redeploy under them:"; echo "$K"; exit 4; }
if [ -e "$NS/repo_k" ]; then
  OLD=$(cat "$NS/repo_k/.deployed_commit" 2>/dev/null || echo unknown)
  mv "$NS/repo_k" "$NS/tmp/repo_k.${OLD:0:8}.retired.$(date -u +%Y%m%dT%H%M%SZ)"
fi
mkdir "$NS/repo_k"
tar -xf "$TAR" -C "$NS/repo_k"
cp "$NS/repo_k/docs/orchestration/state/2d-closeout/stageC/pilot/p1/driver_p1.py" "$NS/repo_k/2d-unfolding/driver_p1.py"
echo "$COMMIT" > "$NS/repo_k/.deployed_commit"
python3 - "$NS/repo_k" "$MSHA" <<'EOF'
import hashlib, json, sys
from pathlib import Path
R = Path(sys.argv[1]); P = R / "docs/orchestration/state/2d-closeout/stageC/production"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
bad = int(sha(P / "manifest.json") != sys.argv[2])
m = json.loads((P / "manifest.json").read_text())
n = 0
for sect in ("package", "code_outside_package"):
    for f, w in m[sect].items():
        n += 1
        if sha(R / f) != w:
            bad += 1; print("BAD", f)
d = sha(R / "2d-unfolding/driver_p1.py")
bad += int(d != "3056e625a22f2ee79621e515aa5a76a4685662ac6fc10ee7e832680dde087578")
print(f"deployed {(R / '.deployed_commit').read_text().strip()}: manifest {sha(P / 'manifest.json')}, "
      f"{n + 1} files checked, mismatches {bad}")
sys.exit(1 if bad else 0)
EOF
