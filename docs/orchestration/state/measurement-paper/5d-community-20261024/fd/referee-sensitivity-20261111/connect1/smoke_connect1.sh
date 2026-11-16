#!/bin/bash
# Local smoke of rsn_connect1.sh's plumbing (macOS or Linux; never connects). Usage:
#   bash smoke_connect1.sh <new empty work dir> <a local clone that contains M_RSN>
# It builds a copy of rsn_connect1.sh with only these substitutions: P -> <work>/p; REPO -> the local clone; the four
# input pins -> synthetic files' sha256s; PY -> a wrapper; the host test -> $FAKE_HOST; and, on macOS (no O_NOATIME),
# the O_NOATIME flag dropped and the atime comparison neutralized (case "atime" keeps the comparison and sets the
# sources' atimes older than their mtimes, so a plain read must STOP). The wrapper stands in for the bound code, which
# needs cluster inputs: for rsn_prep.py it writes three reweights and prints their sums; for rsn_regrade.py it writes an
# rsn-nc-r/1 PASS record whose code_sha256 is the deployed file's (or a wrong one, with SMOKE_R1=bad). Stubs: squeue,
# hostname, timeout. The real NC-R and prep run only on the cluster; this tests the gates around them.
W=${1:?work dir}; CLONE=${2:?local clone}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$W" ] && [ -z "$(ls -A "$W")" ] || { echo "STOP: $W is not a new empty directory"; exit 9; }
mkdir -p "$W/bin" "$W/src" "$W/p/pv-ladder-20261024/prep/ratios/L-5D-PV"
cat > "$W/bin/squeue" <<'EOF'
#!/bin/bash
[ -n "$SMOKE_SQUEUE" ] && printf '%s\n' "$SMOKE_SQUEUE"; exit 0
EOF
cat > "$W/bin/hostname" <<'EOF'
#!/bin/bash
echo "${FAKE_HOST:-login27}"
EOF
printf '#!/bin/bash\nshift\nexec "$@"\n' > "$W/bin/timeout"   # macOS has none; the login node has /usr/bin/timeout
cat > "$W/py" <<'EOF'
#!/bin/bash
# stands in for root_6_28's python3: dispatch on the script, else run python3
args=("$@"); script=""
for a in "$@"; do case "$a" in */rsn_prep.py|*/rsn_regrade.py) script=$a ;; esac; done
get() { local k=$1; shift; while [ $# -gt 0 ]; do [ "$1" = "$k" ] && { echo "$2"; return; }; shift; done; }
case "$script" in
  */rsn_prep.py)
    out=$(get --out "${args[@]}"); mkdir -p "$out/G6" "$out/SM"
    for f in G6/gibuu SM/genie_mec SM/nuwro; do echo "{\"r\": \"$f\"}" > "$out/$f.json"; done
    echo '{"schema": "smoke"}' > "$out/prep.json"
    (cd "$out" && for f in G6/gibuu SM/genie_mec SM/nuwro; do echo "$(shasum -a 256 "$f.json" | cut -d' ' -f1)  ./$f.json"; done)
    [ -n "$SMOKE_PREP_EXTRA" ] && echo "an extra stdout line"
    [ -n "$SMOKE_PREP_UNLISTED" ] && echo x > "$out/SM/unlisted.json"
    echo "[rsn] G6 k 1.201200; SM built at radius 1" >&2; exit 0 ;;
  */rsn_regrade.py)
    out=$(get --out "${args[@]}"); sha=$(shasum -a 256 "$script" | cut -d' ' -f1)
    [ "$SMOKE_R1" = bad ] && sha=0000000000000000000000000000000000000000000000000000000000000000
    printf '{\n "schema": "rsn-nc-r/1",\n "verdict": "PASS",\n "records": 22,\n "code_sha256": {"rsn_regrade.py": "%s"}\n}\n' "$sha" > "$out"
    echo "[rsn] NC-R PASS: 22 records reproduce the committed F1 readout"; exit 0 ;;
  *) exec python3 "${args[@]}" ;;
esac
EOF
chmod +x "$W/bin/"* "$W/py"
python3 - "$W" <<'EOF'
import hashlib, os, sys
W = sys.argv[1]
names = {"table": "fd-f1-20261027/grade/fd_f1_experiments.npz", "s1_npz": "s1-20261024/s1_assembly.npz",
         "extra_block": "fd-ct-5b-addition-20261031/with/block/cpl_block.npz",
         "flux": "MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"}
with open(f"{W}/pins.txt", "w") as o:
    for k, rel in names.items():
        p = f"{W}/p/{rel}"; os.makedirs(os.path.dirname(p), exist_ok=True)
        b = os.urandom(4096); open(p, "wb").write(b)
        o.write(f"{k} {hashlib.sha256(b).hexdigest()}\n")
EOF
mk() {  # mk <name> <atime: real|neutral> [bad-pin key]
  python3 - "$HERE/rsn_connect1.sh" "$W" "$CLONE" "$1" "$2" "$3" <<'EOF'
import re, sys
src, W, clone, name, atime, badkey = sys.argv[1:7]
s = open(src).read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)
rep("P=/pscratch/sd/j/josephrb", f"P={W}/p-{name}")
rep("REPO=https://github.com/josephbaileyy/MINERvA-OmniFold.git", f"REPO={clone}")
rep("PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3", f"PY={W}/py")
rep('case "$(hostname -s)" in login[0-9][0-9])', 'case "${FAKE_HOST:-login27}" in login[0-9][0-9])')
real = dict(l.split() for l in open(f"{W}/pins.txt"))
for key in ("table", "s1_npz", "extra_block", "flux"):
    m = re.search(rf"\b{key} \S+ ([0-9a-f]{{64}})\"?$", s, re.M)
    pin = "f" * 64 if key == badkey else real[key]
    s = s[:m.start(1)] + pin + s[m.end(1):]
import platform
if platform.system() == "Darwin":
    rep("os.O_RDONLY | os.O_NOATIME", "os.O_RDONLY")
    if atime == "neutral":
        rep("(s0.st_size, s0.st_mtime_ns, s0.st_atime_ns) != (s1.st_size, s1.st_mtime_ns, s1.st_atime_ns)",
            "(s0.st_size, s0.st_mtime_ns) != (s1.st_size, s1.st_mtime_ns)")
open(f"{W}/{name}.sh", "w").write(s)
EOF
  rm -rf "$W/p-$1"; cp -R "$W/p" "$W/p-$1"
}
run() {  # run <name> <atime> <badkey|-> [env...]
  local n=$1 a=$2 k=$3; shift 3; [ "$k" = - ] && k=""
  mk "$n" "$a" "$k"
  [ "$a" = real ] && for f in $(find "$W/p-$n" -type f); do touch -a -t 202001010000 "$f"; done
  cp "$W/$n.sh" "$W/$n.self.sh"
  env PATH="$W/bin:$PATH" "$@" bash "$W/$n.self.sh" "$W/$n.self.sh" > "$W/$n.out" 2>&1
  echo "## case $n rc=$?"
  grep -E 'REFUSED|STOP|STAGE OK|rsn_prep rc|stdout:|NC-R PASS|recorded|deployed|bound |R1 EQUAL|CONNECT 1 PASS|porcelain|HEAD |fence.txt|== rsn connect' "$W/$n.out" \
    | sed -E -e "s|$W|<w>|g" -e 's/ [0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:]{8}Z$//' -e 's/\([0-9]+ [0-9]+ [0-9]+\)/(stat)/'
  echo "self copy removed: $([ -e "$W/$n.self.sh" ] && echo no || echo yes)"
}
run pass neutral -
run atime real -
run badpin neutral flux
run r1bad neutral - SMOKE_R1=bad
run prep_extra_line neutral - SMOKE_PREP_EXTRA=1
run prep_unlisted neutral - SMOKE_PREP_UNLISTED=1
run host neutral - FAKE_HOST=dtn01
run slurm neutral - SLURM_JOB_ID=123
run rsnqueued neutral - "SMOKE_SQUEUE=61099999|rsn_J1|PENDING"
mk exists neutral ""; rm -rf "$W/p-exists"; cp -R "$W/p" "$W/p-exists"; mkdir -p "$W/p-exists/rsn-20261112"
cp "$W/exists.sh" "$W/exists.self.sh"; env PATH="$W/bin:$PATH" bash "$W/exists.self.sh" "$W/exists.self.sh" > "$W/exists.out" 2>&1
echo "## case exists rc=$?"; sed "s|$W|<w>|g" "$W/exists.out"
mk noinput neutral ""; rm -rf "$W/p-noinput"; cp -R "$W/p" "$W/p-noinput"; rm -f "$W/p-noinput/s1-20261024/s1_assembly.npz"
cp "$W/noinput.sh" "$W/noinput.self.sh"; env PATH="$W/bin:$PATH" bash "$W/noinput.self.sh" "$W/noinput.self.sh" > "$W/noinput.out" 2>&1
echo "## case noinput rc=$?"; sed "s|$W|<w>|g" "$W/noinput.out"
