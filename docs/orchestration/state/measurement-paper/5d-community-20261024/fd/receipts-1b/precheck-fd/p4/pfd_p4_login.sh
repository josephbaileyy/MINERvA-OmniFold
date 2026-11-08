#!/bin/bash
# 1B pre-check Part 1, P4: the readout (FD-1B-PRECHECK-FD-DECLARATION.md sections 4, 5 and 7; Binding 1, addendum A1).
# Login node, nice 19, 0 node-h, from a fresh clone at M_A1 with empty porcelain. In order:
#   1. the COV2D fence (rs1_* and ens1_* allowed; an fd1b job still queued refuses);
#   2. the clone: HEAD and porcelain; the module a7fbbb58 and the four committed readout inputs gated on their sha256
#      (gate-d.json, diag.json, i0.json, h2_definition.json); $V/p4 must not exist; $V/unf must hold all 327 products;
#   3. thread environment as I0's and P1r's (A1, ruling 2): nothing exported; recorded as inherited, and in Python;
#   4. the stage: staged.json and every staged copy re-hashed with O_NOATIME against P1's record; stage atime recorded
#      before and after the rehash and after the readout;
#   5. the originals (the spec's 355 staging sources): stat only, before the readout, compared byte for byte with P1's
#      stat-before.txt and stat-after.txt (section 5's last control; P1r's matched both); any difference STOPs (rc 4)
#      before the readout;
#   6. the readout: `fd_1b_precheck_fd.py readout` with the staged copies, the 327 products, gate-d.json, diag.json,
#      i0.json and the committed h2_definition.json, writing $V/p4/readout.json (the module refuses to overwrite). Any
#      failed control is fs.Invalid, rc 4, the run INVALID, reported unrepaired;
#   7. the originals re-stat'd after the readout and compared again (STOP rc 4 on a difference);
#   8. the readout's own stdout and readout.json printed, with its sha256.
# The clone is under the literal root /dev/shm/limres-pfd-p4-20261108, removed at exit. Launched from a /dev/shm copy.
SELF=$1
M=8d7a40c23b3b6b70c2913ba363a10a22e152aee4
MOD_SHA=a7fbbb5850733b248c89c3f4e9527c40b8531228b88241ab2d3f2063c0863d2d
STAGED_SHA=f2f0641975d810172ad946f650d9b59c52fea57e3b70947c12cb87656bf31189
GATED_SHA=e1838c0ae2e66c1a0dffd505c41da44381a2d2b798cfc17d353e2d1260542c63
DIAG_SHA=6fd6669efdae5e8dd0934962b4547537a92d37371df6ad481c7df7dd2dfb2a4f
I0_SHA=9a4142d348f591134ba4912a2197ca958ea387ec58b095622bce5f206d007021
DEF_SHA=b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
W=/dev/shm/limres-pfd-p4-20261108
R=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b
finish() { echo "== pfd-p4 rc=$1 $(date -u +%FT%TZ)"; rm -rf -- /dev/shm/limres-pfd-p4-20261108; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node"; rm -f -- "$SELF"; exit 9 ;; esac
[ ! -e /dev/shm/limres-pfd-p4-20261108 ] || { echo "STOP: /dev/shm/limres-pfd-p4-20261108 exists"; rm -f -- "$SELF"; exit 9; }
[ ! -e "$V/p4" ] || { echo "STOP: $V/p4 exists"; rm -f -- "$SELF"; exit 9; }
n=$(ls "$V"/unf/fd1b_pfd_*.npz 2>/dev/null | wc -l)
[ "$n" -eq 327 ] || { echo "STOP: $V/unf holds $n products, not 327"; rm -f -- "$SELF"; exit 9; }
mkdir /dev/shm/limres-pfd-p4-20261108 || { rm -f -- "$SELF"; exit 9; }
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== 1. fence"
out=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
printf '%s\n' "$out"
bad=$(printf '%s\n' "$out" | awk -F'|' 'NF && $2 !~ /^(rs1_|ens1_)/')
echo "squeue rc=$frc; refusing rows: [$bad]"
[ "$frc" -eq 0 ] && [ -z "$bad" ] || { echo "STOP: the fence is not clear"; finish 3; }
echo "== 2. the clone and its gated inputs"
git clone --quiet --filter=blob:none --no-checkout https://github.com/josephbaileyy/MINERvA-OmniFold.git "$W/repo" || { echo "STOP: clone failed"; finish 5; }
git -C "$W/repo" -c advice.detachedHead=false checkout --quiet "$M" || { echo "STOP: checkout"; finish 5; }
head=$(git -C "$W/repo" rev-parse HEAD); porc=$(git -C "$W/repo" status --porcelain | wc -l)
echo "HEAD $head; porcelain lines $porc"; [ "$head" = "$M" ] && [ "$porc" -eq 0 ] || { echo "STOP: clone not M_A1 clean"; finish 5; }
for pair in "nd-unfolding/fd_1b_precheck_fd.py:$MOD_SHA" "$R/stage2/run/score/gate-d.json:$GATED_SHA" "$R/diag/diag.json:$DIAG_SHA" \
            "$R/inv/i0/i0.json:$I0_SHA" "nd-unfolding/pv-ladder/readouts/h2_definition.json:$DEF_SHA"; do
  f=${pair%%:*}; w=${pair##*:}; got=$(sha256sum "$W/repo/$f" | cut -d' ' -f1)
  echo "sha256 $got (expected $w) $f"; [ "$got" = "$w" ] || { echo "STOP: $f"; finish 5; }
done
cd "$W/repo/nd-unfolding" || finish 5
export PYTHONDONTWRITEBYTECODE=1
echo "== 3. thread variables as inherited (A1 ruling 2: none exported): OMP_NUM_THREADS=${OMP_NUM_THREADS-<unset>} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS-<unset>} MKL_NUM_THREADS=${MKL_NUM_THREADS-<unset>} NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS-<unset>}"
echo "== 4. the stage, re-hashed with O_NOATIME against P1's record"
nice -n 19 env -u PYTHONPATH "$PY" -B - "$V" "$STAGED_SHA" "$W" <<'PYEOF' || { echo "STOP: the stage is not P1's record"; finish 4; }
import hashlib, json, os, sys
from pathlib import Path
V, want, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
S = V / "stage"
def snap():
    return {str(p.relative_to(S)): os.stat(p).st_atime_ns for p in sorted(S.rglob("*")) if p.is_file()}
def digest(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOATIME)
    h, data = hashlib.sha256(), []
    try:
        while True:
            b = os.read(fd, 1 << 24)
            if not b:
                break
            h.update(b)
            if path.name == "staged.json":
                data.append(b)
    finally:
        os.close(fd)
    return h.hexdigest(), b"".join(data)
def write(name, m):
    (out / name).write_text("".join(f"{k}\t{v}\n" for k, v in sorted(m.items())))
before = snap(); write("stage-atime-before.tsv", before)
got, raw = digest(S / "staged.json")
print(f"staged.json sha256 {got} (P1 recorded {want}), read with O_NOATIME")
if got != want:
    sys.exit(1)
rec = json.loads(raw)
bad = [e["dest"] for e in rec["staged"] if digest(S / e["dest"])[0] != e["sha256"]]
want_files = sorted([e["dest"] for e in rec["staged"]] + ["staged.json"])
after = snap(); write("stage-atime-after-rehash.tsv", after)
moved = sorted(k for k in before if after.get(k) != before[k])
print(f"staged copies re-hashed with O_NOATIME: {len(rec['staged'])}; mismatches: {len(bad)} {bad[:5]}; "
      f"extra {sorted(set(before) - set(want_files))}; missing {sorted(set(want_files) - set(before))}")
print(f"stage atime before vs after the rehash: {len(before)} files, {len(moved)} moved {moved[:20]}")
sys.exit(1 if bad or set(before) != set(want_files) or rec["missing"] else 0)
PYEOF
echo "== 5. the originals before the readout (stat only), against P1's stat-before and stat-after"
env -u PYTHONPATH "$PY" -B -c 'import json,sys; [print(e["src"]) for e in json.load(open(sys.argv[1]))]' "$V/spec.json" \
  | while read -r f; do stat -c '%n|%s|%Y|%X' "$f" 2>&1; done > "$W/stat-p4-before.txt"
echo "stat-p4-before.txt: $(wc -l < "$W/stat-p4-before.txt") lines; sha256 $(sha256sum "$W/stat-p4-before.txt" | cut -d' ' -f1)"
for ref in stat-before.txt stat-after.txt; do
  if cmp -s "$V/$ref" "$W/stat-p4-before.txt"; then echo "originals: byte-identical to P1's $ref"
  else echo "STOP: an original's stat differs from P1's $ref:"; diff "$V/$ref" "$W/stat-p4-before.txt" | head -40; finish 4; fi
done
echo "== 6. the readout, $(date -u +%FT%TZ)"
mkdir "$V/p4" || finish 9
nice -n 19 env -u PYTHONPATH "$PY" -B - <<'PYEOF'
import os, numpy as np
print("thread variables (python):", {k: os.environ.get(k, "<unset>") for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")}, "numpy", np.__version__)
try:
    import threadpoolctl
    print("threadpools:", [(i.get("internal_api"), i.get("num_threads"), i.get("version"), i.get("filepath")) for i in threadpoolctl.threadpool_info()])
except ImportError:
    print("threadpoolctl not installed"); np.show_config()
PYEOF
nice -n 19 env -u PYTHONPATH "$PY" -B fd_1b_precheck_fd.py readout --staged "$V/stage" --unfolds "$V/unf" \
  --gate-d "../$R/stage2/run/score/gate-d.json" --diag "../$R/diag/diag.json" --i0 "../$R/inv/i0/i0.json" \
  --definition pv-ladder/readouts/h2_definition.json --out "$V/p4/readout.json" > "$W/readout.stdout" 2> "$W/readout.stderr"
rrc=$?
echo "readout rc=$rrc $(date -u +%FT%TZ)"
echo "-- readout stdout"; cat "$W/readout.stdout"; echo "-- readout stderr (last 40 lines)"; tail -40 "$W/readout.stderr"
cp "$W/readout.stdout" "$V/p4/readout.stdout"; cp "$W/readout.stderr" "$V/p4/readout.stderr"
[ "$rrc" -eq 0 ] || echo "INVALID or refused: the readout exited $rrc (reported unrepaired)"
echo "== 7. stage atime after the readout, and the originals again"
env -u PYTHONPATH "$PY" -B - "$V" "$W" <<'PYEOF'
import os, sys
from pathlib import Path
V, out = Path(sys.argv[1]), Path(sys.argv[2])
S = V / "stage"
now = {str(p.relative_to(S)): os.stat(p).st_atime_ns for p in sorted(S.rglob("*")) if p.is_file()}
(out / "stage-atime-after-readout.tsv").write_text("".join(f"{k}\t{v}\n" for k, v in sorted(now.items())))
prev = dict(l.split("\t") for l in (out / "stage-atime-after-rehash.tsv").read_text().splitlines())
moved = sorted(k for k in now if str(now[k]) != prev.get(k))
print(f"stage atime after the rehash vs after the readout: {len(now)} files, {len(moved)} moved (the bound module's reads)")
PYEOF
env -u PYTHONPATH "$PY" -B -c 'import json,sys; [print(e["src"]) for e in json.load(open(sys.argv[1]))]' "$V/spec.json" \
  | while read -r f; do stat -c '%n|%s|%Y|%X' "$f" 2>&1; done > "$W/stat-p4-after.txt"
for f in stage-atime-before.tsv stage-atime-after-rehash.tsv stage-atime-after-readout.tsv stat-p4-before.txt stat-p4-after.txt; do
  cp "$W/$f" "$V/p4/$f"; echo "$f: sha256 $(sha256sum "$V/p4/$f" | cut -d' ' -f1)"
done
orc=0
if cmp -s "$W/stat-p4-before.txt" "$W/stat-p4-after.txt"; then echo "originals: unchanged through the readout"
else echo "STOP: an original's stat moved during the readout:"; diff "$W/stat-p4-before.txt" "$W/stat-p4-after.txt" | head -40; orc=4; fi
echo "== 8. readout.json"
if [ -f "$V/p4/readout.json" ]; then echo "readout.json sha256 $(sha256sum "$V/p4/readout.json" | cut -d' ' -f1)"; cat "$V/p4/readout.json"; else echo "readout.json: absent"; fi
[ "$orc" -ne 0 ] && finish "$orc"
finish "$rrc"
