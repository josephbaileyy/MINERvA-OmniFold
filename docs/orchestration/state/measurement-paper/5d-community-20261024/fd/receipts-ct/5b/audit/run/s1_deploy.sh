# 5B audit step 1 (FD-CT-5B-AUDIT-DECLARATION.md section 10.1; FD-CT-5B-AUDIT-BINDING.md condition 1): deploy and tests, login node.
set -o pipefail   # NOT set -u (conda activation)
P=/pscratch/sd/j/josephrb; BA=$P/fd-ct-5b-audit-20261030; PIN=6dd415391da44d3d996bed7ab39a0654a2a5345e; D=$BA/deploy/6dd41539
[ -e "$BA" ] && { echo "STOP: $BA exists"; exit 2; }
mkdir -p "$BA/logs" "$BA/tmp"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$D" && git -C "$D" checkout --quiet --detach "$PIN" || { echo "STOP: clone"; exit 3; }
{ date -u +%FT%TZ; hostname; echo "head $(git -C "$D" rev-parse HEAD)"
  echo "porcelain_ignored_lines $(git -C "$D" status --porcelain --ignored | wc -l)"
  cd "$D" && /usr/bin/python3 -I -B - <<'PY'
import re, hashlib
s = open("docs/orchestration/state/measurement-paper/5d-community-20261024/FD-CT-5B-AUDIT-DECLARATION.md").read()
print("declaration_sha256", hashlib.sha256(s.encode()).hexdigest())
i = s.index("## 14. Pinned bytes")
sec = s[i:s.index("\n## ", i + 1)]
bad = []
rows = re.findall(r"\| `([^`]+)` \| `([0-9a-f]{64})`", sec)
for path, h in rows:
    got = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print(got, path, "OK" if got == h else "MISMATCH")
    if got != h: bad.append(path)
print(f"pins {len(rows)} mismatches {len(bad)}")
PY
} > "$BA/logs/deploy.log" 2>&1
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
echo "python $(command -v python3) $(python3 -V 2>&1)" >> "$BA/logs/deploy.log"
cd "$D/nd-unfolding/tests" && TMPDIR=$BA/tmp env -u PYTHONPATH python3 -B -m unittest -v \
  test_fd_ct_5b_audit test_fd_ct_periods test_fd_ct_readers > "$BA/logs/deploy-tests.log" 2>&1
echo "tests rc=$?" >> "$BA/logs/deploy.log"
grep -E "^Ran |^OK|^FAILED" "$BA/logs/deploy-tests.log" >> "$BA/logs/deploy.log"
echo "skipped_lines $(grep -c 'skipped' "$BA/logs/deploy-tests.log")" >> "$BA/logs/deploy.log"
echo "porcelain_ignored_lines_after_tests $(git -C "$D" status --porcelain --ignored | wc -l)" >> "$BA/logs/deploy.log"
cat "$BA/logs/deploy.log"
