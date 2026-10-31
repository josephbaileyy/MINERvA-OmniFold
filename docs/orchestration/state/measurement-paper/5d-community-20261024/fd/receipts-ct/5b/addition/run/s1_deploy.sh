# 5B addition step 1 (FD-CT-5B-ADDITION-DECLARATION.md section 6; FD-CT-5B-ADDITION-BINDING.md section 3): deploy and tests, login node.
set -o pipefail   # NOT set -u (conda activation)
P=/pscratch/sd/j/josephrb; BA=$P/fd-ct-5b-addition-20261031; PIN=3b12c451d617b860450f516b3b63266379308f80; D=$BA/deploy/3b12c451
[ -e "$BA" ] && { echo "STOP: $BA exists"; exit 2; }
mkdir -p "$BA/logs" "$BA/tmp"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$D" && git -C "$D" checkout --quiet --detach "$PIN" || { echo "STOP: clone"; exit 3; }
{ date -u +%FT%TZ; hostname; echo "head $(git -C "$D" rev-parse HEAD)"
  echo "porcelain_ignored_lines $(git -C "$D" status --porcelain --ignored | wc -l)"
  cd "$D" && /usr/bin/python3 -I -B - <<'PY'
import re, hashlib
s = open("docs/orchestration/state/measurement-paper/5d-community-20261024/FD-CT-5B-ADDITION-DECLARATION.md").read()
print("declaration_sha256", hashlib.sha256(s.encode()).hexdigest())
i = s.index("### 8.1")
sec = s[i:s.index("### 8.2", i)]
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
  test_fd_cpl_addition test_fd_deposit_candidate test_fd_g_figures test_fd_flux_boot test_fd_data_product \
  test_fd_g_compare test_fd_g_diag test_fd_g_followup test_fd_f0_regrade > "$BA/logs/deploy-tests.log" 2>&1
echo "tests rc=$?" >> "$BA/logs/deploy.log"
grep -E "^Ran |^OK|^FAILED" "$BA/logs/deploy-tests.log" >> "$BA/logs/deploy.log"
echo "skipped_lines $(grep -c 'skipped' "$BA/logs/deploy-tests.log")" >> "$BA/logs/deploy.log"
echo "porcelain_ignored_lines_after_tests $(git -C "$D" status --porcelain --ignored | wc -l)" >> "$BA/logs/deploy.log"
date -u +%FT%TZ >> "$BA/logs/deploy.log"
cat "$BA/logs/deploy.log"
