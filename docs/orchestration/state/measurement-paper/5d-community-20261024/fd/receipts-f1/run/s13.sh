# Step 13 (FD-F1-BINDING.md section 4.7; FD-F1-DECLARATION.md section 9, with amendment 2's f1b3 and the director's
# ruling (i) on the F1c product root): the HPSS copy, before the report PR. Members: f1a/splines, f1b3/gst, f1b3/gen5d,
# f1b3/prep, f1c/closure, f1c/pe (never f1b/ or f1b2/). The inventory is cross-checked line by line against the
# committed f1a-SHA256SUMS, f1b3-SHA256SUMS and the F1c product manifest before the tar; then the grade deploy's
# stage0_preserve.sh (tar, hsi put, hashcreate, hashverify, get-back, sha256 compare). Login node, detached (nohup).
set -o pipefail
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
DG=$OUT/deploy/grade
RC=$DG/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/run/cluster
W=$OUT/preserve; HDIR=/home/j/josephrb/mnv-5d-f1-20261028; L=$OUT/logs/preserve-f1.log
[ -e $W ] && { echo "STOP: $W exists" > $L; exit 3; }
mkdir -p $W
{ date -u +%FT%TZ; hostname
  echo "grade deploy HEAD $(git -C $DG rev-parse HEAD), porcelain_ignored_lines $(git -C $DG status --porcelain --ignored | wc -l)"
  cd $OUT && find $OUT/f1a/splines $OUT/f1b3/gst $OUT/f1b3/gen5d $OUT/f1b3/prep $OUT/f1c/closure $OUT/f1c/pe -type f | sort | xargs sha256sum > $W/INVENTORY.sha256
  echo "inventory lines $(wc -l < $W/INVENTORY.sha256)"
  env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B - $W/INVENTORY.sha256 $RC $OUT <<'PYEOF'
import sys
inv, rc, out = sys.argv[1:4]
def sums(path, prefix):
    d = {}
    for l in open(path):
        h, p = l.rstrip("\n").split("  ", 1)
        d[prefix + (p[2:] if p.startswith("./") else p)] = h
    return d
ref = {}
ref.update(sums(f"{rc}/f1a/f1a-SHA256SUMS", f"{out}/f1a/"))
ref.update(sums(f"{rc}/f1b3/f1b3-SHA256SUMS", f"{out}/f1b3/"))
ref.update(sums(f"{rc}/manifest/f1-products-SHA256SUMS", f"{out}/f1c/"))
bad, n = [], 0
for l in open(inv):
    h, p = l.rstrip("\n").split("  ", 1)
    n += 1
    if ref.get(p) != h:
        bad.append((p, h, ref.get(p)))
print(f"cross-check: {n} inventory files, {n - len(bad)} match a committed sums line, {len(bad)} do not")
for b in bad[:10]:
    print("  MISMATCH", b)
sys.exit(1 if bad or n == 0 else 0)
PYEOF
  echo "cross-check rc=$?"
} > $L 2>&1
grep -q "^cross-check rc=0$" $L || { echo "STOP: cross-check" >> $L; exit 3; }
bash $DG/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/stage0_preserve.sh $W/INVENTORY.sha256 $W $HDIR > $OUT/logs/preserve-f1.out 2>&1
echo "preserve rc=$?" >> $L
echo "done: $(date -u +%FT%TZ)" >> $L
