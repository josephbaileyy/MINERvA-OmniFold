# 5B step 1 (FD-CT-5B-DECLARATION.md section 2.1; FD-CT-5B-BINDING.md condition 1): deploy and tests, login node.
set -o pipefail   # NOT set -u (conda activation)
P=/pscratch/sd/j/josephrb; B=$P/fd-ct-5b-20261030; PIN=2c96065956d59b29a1ec0e7c611d52536f92a785; D=$B/deploy/2c960659
R=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b
[ -e "$B" ] && { echo "STOP: $B exists"; exit 2; }
mkdir -p "$B/logs" "$B/tmp" "$B/tables"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$D" && git -C "$D" checkout --quiet --detach "$PIN" || { echo "STOP: clone"; exit 3; }
{ date -u +%FT%TZ; hostname; echo "head $(git -C "$D" rev-parse HEAD)"
  echo "porcelain_ignored_lines $(git -C "$D" status --porcelain --ignored | wc -l)"
  cd "$D" && /usr/bin/python3 -I -B - <<'PY'
import re, hashlib
s = open("docs/orchestration/state/measurement-paper/5d-community-20261024/FD-CT-5B-DECLARATION.md").read()
print("declaration_sha256", hashlib.sha256(s.encode()).hexdigest())
sec = s[s.index("## 8. Pinned bytes"):s.index("## 9.")]
bad = []
rows = re.findall(r"\| `([^`]+)` \| `([0-9a-f]{64})`", sec)
for path, h in rows:
    got = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print(got, path, "OK" if got == h else "MISMATCH")
    if got != h: bad.append(path)
print(f"pins {len(rows)} mismatches {len(bad)}")
PY
} > "$B/logs/deploy.log" 2>&1
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
echo "python $(command -v python3) $(python3 -V 2>&1)" >> "$B/logs/deploy.log"
cd "$D/nd-unfolding/tests" && TMPDIR=$B/tmp env -u PYTHONPATH python3 -B -m unittest -v \
  test_fd_ct_periods test_fd_ct_readers test_fd_ct_closure test_fd_f0_regrade test_s1_assemble > "$B/logs/deploy-tests.log" 2>&1
echo "tests rc=$?" >> "$B/logs/deploy.log"
grep -E "^Ran |^OK|^FAILED" "$B/logs/deploy-tests.log" >> "$B/logs/deploy.log"
echo "skipped_lines $(grep -c 'skipped' "$B/logs/deploy-tests.log")" >> "$B/logs/deploy.log"
env -u PYTHONPATH python3 -I -B "$D/$R/make_5b_tables.py" "$D" "$B/tables" > /dev/null 2>> "$B/logs/deploy.log"
for n in 5b-inputs-steps.tsv tasks-5b-inputs.tsv 5b-periods-steps.tsv tasks-5b-periods.tsv; do
  cmp "$D/$R/$n" "$B/tables/$n" && echo "table $n identical" || echo "table $n DIFFERS"; done >> "$B/logs/deploy.log"
echo "porcelain_ignored_lines_after_tests $(git -C "$D" status --porcelain --ignored | wc -l)" >> "$B/logs/deploy.log"
cat "$B/logs/deploy.log"
