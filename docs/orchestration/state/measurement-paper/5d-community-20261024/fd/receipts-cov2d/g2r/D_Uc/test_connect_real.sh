#!/bin/bash
# The G18/AR23 connects' realization block (from "# --- <T>'s realization" to "# --- the one submission"): the
# realization's O_NOATIME sha256 against the step-B record at $C, then its stat. Run against stand-ins with P and C
# pointed at a temporary tree; stat/date/python3 are shims for macOS (python3 gets O_NOATIME = 0 where os lacks it).
# Cases: pass; a record sha that differs; the realization missing; the record without the file; the file listed twice;
# the record missing. Exit 0 only if every case behaves for every connect given.
#     bash test_connect_real.sh connect-g2r-G18_Ua.sh [...]
set -u
REALPY=$(command -v python3)
T=$(mktemp -d "${TMPDIR:-/tmp}/tcreal.XXXXXX"); mkdir -p "$T/bin"
cat > "$T/bin/py.py" <<'EOF'
import os, sys
if not hasattr(os, "O_NOATIME"):
    os.O_NOATIME = 0
assert sys.argv[1] == "-c", sys.argv
code = sys.argv[2]; sys.argv = ["-c"] + sys.argv[3:]
exec(compile(code, "<connect -c>", "exec"), {"__name__": "__main__"})
EOF
printf '#!/usr/bin/env bash\nexec "%s" "%s" "$@"\n' "$REALPY" "$T/bin/py.py" > "$T/bin/python3"
cat > "$T/bin/stat" <<EOF
#!/usr/bin/env bash
[ "\$1" = --printf ] || exit 99
exec "$REALPY" -c 'import os, sys
fmt, f = sys.argv[1], sys.argv[2]
try: s = os.stat(f)
except OSError: sys.exit(1)
sys.stdout.write(fmt.replace("%s", str(s.st_size)).replace("%X", str(int(s.st_atime))))' "\$2" "\$3"
EOF
cat > "$T/bin/date" <<EOF
#!/usr/bin/env bash
[ "\$1" = -u ] && [ "\$2" = -d ] || exit 99
exec "$REALPY" -c 'import sys, datetime
n = sys.argv[1].lstrip("@")
if not n.isdigit(): sys.exit(1)
print(datetime.datetime.utcfromtimestamp(int(n)).strftime("%Y-%m-%dT%H:%M:%SZ"))' "\$3"
EOF
chmod +x "$T/bin/"*
fail=0
for CONN in "$@"; do
    blk=$(awk '/^# --- (G18|AR23).s realization/ {on = 1} /^# --- the one submission/ {exit} on' "$CONN")
    truth=$(printf '%s\n' "$blk" | sed -n 's/^TRUTH=\([A-Z0-9]*\);.*/\1/p')
    rd=$(printf '%s\n' "$blk" | sed -n 's|^TRUTH=[A-Z0-9]*; RD=\$P/\([^;]*\); RF=.*|\1|p')
    rf=$(printf '%s\n' "$blk" | sed -n 's/.*; RF=\(data_[0-9]*\.root\)$/\1/p')
    echo "== $(basename "$CONN"): block $(printf '%s\n' "$blk" | wc -l | tr -d ' ') lines, TRUTH=$truth RD=\$P/$rd RF=$rf"
    [ -n "$truth" ] && [ -n "$rd" ] && [ -n "$rf" ] || { echo "FAIL block not found"; fail=1; continue; }
    n=0
    run() {
        { printf 'set -u\nP=%q; C=%q\n' "$P" "$C"; printf 'stop() { echo "STOP $*"; echo DONE; exit 2; }\n'
          printf '%s\n' "$blk"; echo 'echo REACHED-SUBMIT'; } > "$T/case.sh"
        PATH=$T/bin:$PATH bash "$T/case.sh" > "$T/out" 2>&1; echo $? > "$T/rc"
    }
    check() {
        local rc; rc=$(cat "$T/rc")
        if [ "$rc" = "$2" ] && grep -qE "$3" "$T/out"; then echo "PASS $1 rc=$rc"
        else echo "FAIL $1 rc=$rc (want $2, /$3/)"; sed 's/^/    /' "$T/out"; fail=1; fi
    }
    reset() {  # a fresh tree per case
        n=$((n + 1)); P=$T/$(basename "$CONN" .sh)-$n/P; C=$T/$(basename "$CONN" .sh)-$n/C
        SBD=$C/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/pseudo/$truth
        mkdir -p "$P/$rd" "$SBD"; printf 'realization bytes %s' "$truth" > "$P/$rd/$rf"
        good=$(shasum -a 256 "$P/$rd/$rf" | cut -c1-64)
    }
    rec() { "$REALPY" -c 'import json, sys
print(json.dumps({"files": [{"path": p, "sha256": s} for p, s in zip(sys.argv[2::2], sys.argv[3::2])]}))' x "$@" > "$SBD/pseudo_b.json"; }
    reset; rec "/x/$rd/data_1.root" 00 "/pscratch/sd/j/josephrb/cov2d-run-20261104/pseudo/$rd/$rf" "$good"; run
    check pass 0 'REACHED-SUBMIT'
    grep -qE "^realization .*/$rf sha256=$good \(O_NOATIME\) step-B record $truth sha256=$good$" "$T/out" \
        && grep -qE "^input .*/$rf size=[0-9]+ atime=" "$T/out" && echo "PASS pass-lines" || { echo "FAIL pass-lines"; fail=1; }
    reset; rec "/p/$rd/$rf" "$(printf 'f%.0s' $(seq 64))"; run; check record-differs 2 "^STOP the realization's sha256 is not $truth's step-B record's"
    reset; rec "/p/$rd/$rf" "$good"; rm -f "$P/$rd/$rf"; run; check realization-missing 2 "^STOP the realization's sha256"
    reset; rec "/p/$rd/data_9.root" "$good"; run; check record-lacks-file 2 "^STOP the realization's sha256"
    reset; rec "/p/$rd/$rf" "$good" "/q/$rd/$rf" "$good"; run; check listed-twice 2 "^STOP the realization's sha256"
    reset; rm -f "$SBD/pseudo_b.json"; run; check record-missing 2 "^STOP the realization's sha256"
done
find "$T" -type f -exec rm -f {} +; find "$T" -depth -type d -exec rmdir {} \;
[ -e "$T" ] && echo "left: $T"
[ "$fail" = 0 ] && echo "CONNECT-REAL BLOCK TEST PASS" || echo "CONNECT-REAL BLOCK TEST FAILED"
exit $fail
