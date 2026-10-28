# Step 11 (FD-F1-BINDING.md section 4.5; the director's ruling (i) on the F1c product root): after F1c job 60439400,
# read-only checks of $OUT/f1c and the product manifest, written by the pin's fd_f1_tasks.py manifest with
# --runs $OUT/f1c (the root the pin's tables name). Login node; writes only $OUT/manifest/. Never touches $OUT/f1b(2).
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
D4=$OUT/deploy/f1c
R=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/run
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
date -u +%FT%TZ; hostname
sacct -j 60439400 -P -o JobID,JobName,State,ExitCode,Start,End,Elapsed,MaxRSS,AllocTRES,NodeList
echo "--- check 1: every file under \$OUT/f1c, by top-level entry (products must be only under closure/ and pe/<truth>/)"
( cd $OUT/f1c && find . -type f | awk -F/ '{print ($2=="pe" ? $2"/"$3 : $2)}' | sort | uniq -c )
echo "--- files under \$OUT/f1c outside closure/ and pe/ that are .npz, .partial or not a log/inventory record"
( cd $OUT/f1c && find . -type f ! -path './closure/*' ! -path './pe/*' | grep -Ev '^\./(line[0-9]+-60439400\.log|probe_[A-Za-z0-9_]+-60439400\.log)$|^\./inventory/' ) ; echo "(end; empty means none)"
echo "--- files under closure/ and pe/ that are not .npz"
( cd $OUT/f1c && find closure pe -type f ! -name '*.npz' ); echo "(end; empty means none)"
echo "--- check 2: the manifest"
[ -e $OUT/manifest ] && { echo "STOP: $OUT/manifest exists"; exit 3; }
mkdir $OUT/manifest
$PY $D4/nd-unfolding/fd_f1_tasks.py manifest --runs $OUT/f1c --out $OUT/manifest/f1-products-SHA256SUMS; echo "manifest rc=$?"
wc -l < $OUT/manifest/f1-products-SHA256SUMS
sha256sum $OUT/manifest/f1-products-SHA256SUMS
echo "--- the 42 outputs the pin's tables declare (closure --out paths and pe dirs x seeds), against the manifest by name"
$PY - $D4/$R/f1c/f1c-steps.tsv $OUT/manifest/f1-products-SHA256SUMS $OUT/f1c <<'PYEOF'
import sys
steps, man, root = sys.argv[1:4]
want = set()
for line in open(steps):
    if line.startswith("#"):
        continue
    f = line.rstrip("\n").split("\t")
    out = f[f.index("--out") + 1]
    if f[2] == "pv-ladder/pvl_unfold.py":
        want.add(out[len(root) + 1:])
    else:
        a, b = map(int, f[f.index("--pseudo-seeds") + 1].split(":"))
        want |= {f"{out[len(root) + 1:]}/ratio_nd_a1_s{s}.npz" for s in range(a, b + 1)}
have = {l.split("  ", 1)[1].strip()[2:] for l in open(man)}
print(f"declared {len(want)}, closures {sum(1 for w in want if w.startswith('closure/'))}, pseudo-experiments {sum(1 for w in want if w.startswith('pe/'))}; manifest {len(have)}; equal by name: {want == have}")
print("only declared:", sorted(want - have)[:5], "only in manifest:", sorted(have - want)[:5])
PYEOF
echo "done $(date -u +%FT%TZ)"
