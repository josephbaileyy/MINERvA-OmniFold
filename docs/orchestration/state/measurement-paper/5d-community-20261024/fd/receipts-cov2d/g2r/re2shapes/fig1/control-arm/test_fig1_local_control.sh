#!/bin/bash
# Stand-in test of re2c_fig1_local.sh's control arm (the director's follow-up, 2026-11-16). The REAL script runs, with
# the REAL re2c_fig1.py and make_figs.py, in the recorded environment, with two shims on PATH:
#   scp  a fetch (host:path ... localdir) logs "FETCH <path>" and copies <inputs>/<basename of path>; an upload (local
#        files ... host:path) logs "UPLOAD <dest>" and copies nothing. SC_TAMPER=chain appends a byte to chain.json.
#   ssh  logs "SSH <args>" and exits 0.
# <inputs> is the local copy of the files the 2026-11-16 control fetched from partc-r2. Each must equal the digest in
# ../control/RUN-fig1.txt; the test checks this first. Nothing reaches the cluster.
# Since Fig. 1 version B' (2026-11-16) the K1 is fee46c1a (../bprime/): fig2 and fig3 still equal the control's.
#   bash test_fig1_local_control.sh <repo worktree> <inputs> <python>
set -u
REPO=$(cd "$1" && pwd); IN=$(cd "$2" && pwd); PY=$3
H=$(cd "$(dirname "$0")" && pwd); SCRIPT=$REPO/2d-unfolding/re2/partc/re2c_fig1_local.sh
A3=/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partc-r2
T0=$(mktemp -d "${TMPDIR:-/tmp}/tf1.XXXXXX"); SH=$T0/shims; mkdir -p "$SH"; fail=0
ok() { echo "PASS $1"; }; bad() { echo "FAIL $1"; fail=1; }
sed -n '/^inputs:/,/^outputs:/p' "$H/../control/RUN-fig1.txt" | grep '  in/' | while read -r d p; do
  [ "$(shasum -a 256 "$IN/${p#in/}" | cut -d' ' -f1)" = "$d" ] || echo "$p"; done > "$T0/bad-inputs"
n=$(grep -c '  in/' "$H/../control/RUN-fig1.txt")
[ ! -s "$T0/bad-inputs" ] && ok "inputs: all $n equal ../control/RUN-fig1.txt" || { bad "inputs differ: $(cat "$T0/bad-inputs")"; exit 1; }
cat > "$SH/scp" <<SHIM
#!/bin/bash
a=(); for x in "\$@"; do [ "\$x" = -q ] || a+=("\$x"); done
dest=\${a[\${#a[@]}-1]}; unset 'a[\${#a[@]}-1]'
case "\$dest" in
  *:*) echo "UPLOAD \$dest" >> "\$SC_LOG"; exit 0 ;;
esac
for s in "\${a[@]}"; do p=\${s#*:}; echo "FETCH \$p" >> "\$SC_LOG"; b=\$(basename "\$p")
  cp "$IN/\$b" "\$dest/" || exit 1
  [ "\${SC_TAMPER:-}" = chain ] && [ "\$b" = chain.json ] && printf ' ' >> "\$dest/\$b"; done
exit 0
SHIM
printf '#!/bin/bash\necho "SSH $*" >> "$SC_LOG"; exit 0\n' > "$SH/ssh"
chmod +x "$SH"/*
run() {  # run <name> <want rc> <script> <args after the workdir and python...> ; env SC_* passed through
  local name=$1 want=$2 sc=$3; shift 3
  local R=$T0/$name; mkdir -p "$R"; : > "$R/log"
  local arm=$1; shift
  (export PATH="$SH:$PATH" SC_LOG="$R/log"; bash "$sc" "$arm" "$R/w" "$PY" "$@") > "$R/stdout" 2>&1; local rc=$?
  [ "$rc" = "$want" ] && ok "$name: rc $rc ($(tail -1 "$R/stdout" | cut -c1-110))" || { bad "$name: rc $rc, want $want"; tail -5 "$R/stdout"; }
}
run control 0 "$SCRIPT" control
R=$T0/control
[ "$(shasum -a 256 "$R/w/out/fig1_validation.pdf" | cut -d' ' -f1)" = fee46c1a8b60a09701444373e9dbfbf106bffdd42759928b0979c8eeb57135d1 ] \
  && grep -q '^K1: fig1_validation.pdf reproduces fee46c1a' "$R/stdout" && ok "control: fig1_validation.pdf is fee46c1a, K1 line printed" || bad "control: output"
! grep -q '^SSH\|^UPLOAD' "$R/log" && ok "control: no ssh and no upload (no cluster write)" || { bad "control: cluster write"; cat "$R/log"; }
nf=$(grep -c '^FETCH' "$R/log"); nout=$(grep '^FETCH' "$R/log" | grep -v "^FETCH $A3/" | grep -vc '^FETCH /pscratch/sd/j/josephrb/pub-release-20261006/figs/fig_arrays.npz$')
[ "$nf" = 9 ] && [ "$nout" = 0 ] && ok "control: 9 fetches, each from partc-r2 except fig_arrays.npz" || { bad "control: fetches ($nf, $nout outside)"; cat "$R/log"; }
diff <(sed -n '/^outputs:/,$p' "$R/w/RUN-fig1.txt" | grep -v fig1_validation) <(sed -n '/^outputs:/,$p' "$H/../control/RUN-fig1.txt" | grep -v fig1_validation) > /dev/null \
  && ok "control: fig2 and fig3 equal the 2026-11-16 control's" || bad "control: fig2 or fig3 differ from ../control/RUN-fig1.txt"
run control-with-dir 2 "$SCRIPT" control /some/dir
grep -q '^control: takes no part C directory' "$T0/control-with-dir/stdout" && [ ! -e "$T0/control-with-dir/w" ] && ok "control-with-dir: refused before the workdir" || bad "control-with-dir: message"
run purity-gone 2 "$SCRIPT" purity
grep -q "^arm: control or refined, not 'purity'" "$T0/purity-gone/stdout" && ok "purity-gone: the retired arm refuses" || bad "purity-gone: message"
SC_TAMPER=chain run control-chain 3 "$SCRIPT" control
grep -q '^in/chain.json: sha256 .* != 81dcf2d0' "$T0/control-chain/stdout" && ! grep -q '^FETCH.*outA' "$T0/control-chain/log" \
  && ok "control-chain: a chain.json other than amendment 3's refuses before any other input" || bad "control-chain: detail"
run refined-no-dir 2 "$SCRIPT" refined
run refined 0 "$SCRIPT" refined /x/partc
R=$T0/refined
grep -q '^SSH -o BatchMode=yes saul.nersc.gov mkdir -p /x/partc/fig1' "$R/log" && grep -q '^UPLOAD saul.nersc.gov:/x/partc/fig1/$' "$R/log" \
  && [ "$(shasum -a 256 "$R/w/out/fig1_validation.pdf" | cut -d' ' -f1)" = fee46c1a8b60a09701444373e9dbfbf106bffdd42759928b0979c8eeb57135d1 ] \
  && ok "refined: unchanged behaviour (fetches from <partc dir>, dir check by ssh, upload to <partc dir>/fig1/)" || { bad "refined: detail"; cat "$R/log"; }
# mutant: the K1 pin changed, in a mirror tree laid out as the repository (REPO = HERE/../../..)
M=$T0/mirror; mkdir -p "$M/2d-unfolding/re2/partc" "$M/publication/release/figs"
cp "$REPO/2d-unfolding/re2/partc/re2c_fig1.py" "$M/2d-unfolding/re2/partc/"; cp "$REPO/publication/release/figs/make_figs.py" "$M/publication/release/figs/"
"$PY" -I - "$SCRIPT" "$M/2d-unfolding/re2/partc/re2c_fig1_local.sh" <<'PYM'
import sys
s = open(sys.argv[1]).read(); a = "want out/fig1_validation.pdf fee46c1a"
assert s.count(a) == 1; open(sys.argv[2], "w").write(s.replace(a, "want out/fig1_validation.pdf fee46c1b"))
PYM
run mutant-k1-pin 3 "$M/2d-unfolding/re2/partc/re2c_fig1_local.sh" control
grep -q '^out/fig1_validation.pdf: sha256 fee46c1a.* != fee46c1b' "$T0/mutant-k1-pin/stdout" && ok "mutant-k1-pin: the K1 check fires" || bad "mutant-k1-pin: detail"
find "$T0" -type f -exec rm -f {} + 2>/dev/null; find "$T0" -type l -exec rm -f {} + 2>/dev/null; find "$T0" -depth -type d -exec rmdir {} \; 2>/dev/null
[ -e "$T0" ] && echo "left: $T0"
[ "$fail" = 0 ] && echo "FIG1 CONTROL-ARM TEST PASS" || echo "FIG1 CONTROL-ARM TEST FAILED"
exit $fail
