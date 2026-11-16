#!/bin/bash
# atime-around.sh against a local stand-in: a stub ssh runs atime-stat-list.sh here with its list path and digest
# pointed at a fixture of 1146 files, and its two GNU-only commands (sha256sum; xargs -d/-a with stat --printf) given
# macOS equivalents. This tests the wrapper's logic and the script's control flow, NOT the GNU line itself on
# Perlmutter. Cases:
#   none    pre, then post with nothing touched: post exit 0, NONE-MOVED
#   moved   pre, one listed file's atime set forward, then post: exit 4, MOVED, moved=1
#   missing pre, one listed file removed, then post: exit 3, INCOMPLETE (stat_rc != 0)
#   badlist the list's digest differs: pre exit 3, INCOMPLETE (the script's STOP line)
#   short   one body line lost in transit, the closing line intact: pre exit 3, INCOMPLETE (the 1146-line count)
#   twice   pre run twice: the second is REFUSED, exit 2
#     bash test_atime_around.sh [path/to/atime-around.sh]
set -u
H=$(cd "$(dirname "$0")" && pwd)
A=${1:-$H/atime-around.sh}
T=$(mktemp -d "${TMPDIR:-/tmp}/aar.XXXXXX")
mkdir -p "$T/bin" "$T/files" "$T/w"
for i in $(seq 1 1146); do : > "$T/files/f$i"; done
for i in $(seq 1 1146); do printf '1793496788.0000000000\t%s\n' "$T/files/f$i"; done > "$T/list.tsv"
LSHA=$(shasum -a 256 "$T/list.tsv" | cut -c1-64)
cat > "$T/bin/ssh" <<'EOF'
#!/bin/bash
# the stand-in: the list path and digest from the test, and macOS forms of the two GNU-only lines
awk -v L="$STUB_L" -v W="${STUB_WANT:-$STUB_SHA}" '
    /^L=/ {print "L=" L; next}
    /^WANT=/ {print "WANT=" W; next}
    /^have=/ {print "have=$(shasum -a 256 \"$L\" | cut -c1-64)"; next}
    /^xargs -d / {print "cut -f2 \"$L\" | LC_ALL=C sort | tr \"\\n\" \"\\0\" | xargs -0 stat -f \"%a%t%N\"; rc=${PIPESTATUS[3]}"; next}
    {print}' | bash -s | { if [ "${STUB_DROP:-}" = 1 ]; then sed '5d'; else cat; fi; }
EOF
export STUB_L=$T/list.tsv STUB_SHA=$LSHA
chmod +x "$T/bin/ssh"
ok=0
case_run() {  # case_run <name> <want pre rc> <want post rc or -> <setup between>
    local name=$1 wpre=$2 wpost=$3 between=$4
    rm -rf "$T/w/"*; cp "$A" "$T/w/atime-around.sh"; cp "$H/atime-stat-list.sh" "$T/w/"
    for i in $(seq 1 1146); do [ -e "$T/files/f$i" ] || : > "$T/files/f$i"; touch -a -t 202611010000 "$T/files/f$i"; done
    PATH="$T/bin:$PATH" bash "$T/w/atime-around.sh" pre > "$T/$name.pre" 2>&1; local rpre=$?
    local rpost=-
    eval "$between"
    if [ "$wpost" != - ]; then PATH="$T/bin:$PATH" bash "$T/w/atime-around.sh" post > "$T/$name.post" 2>&1; rpost=$?; fi
    local v=PASS
    [ "$rpre" = "$wpre" ] && [ "$rpost" = "$wpost" ] || v=FAIL
    case $name in
        none) grep -q '^NONE-MOVED$' "$T/$name.post" || v=FAIL ;;
        moved) grep -q '^MOVED:' "$T/$name.post" && grep -q 'moved=1 of 1146' "$T/$name.post" || v=FAIL ;;
        missing) grep -q '^INCOMPLETE: the post reading' "$T/$name.post" || v=FAIL ;;
        badlist|short) grep -q '^INCOMPLETE: the pre reading' "$T/$name.pre" || v=FAIL ;;
    esac
    echo "$v $name pre_rc=$rpre (want $wpre) post_rc=$rpost (want $wpost)"
    [ $v = PASS ] || { ok=1; tail -5 "$T/$name.pre" "$T/$name.post" 2>/dev/null | sed 's/^/    /'; }
}
echo "wrapper $(shasum -a 256 "$A" | cut -c1-64) script $(shasum -a 256 "$H/atime-stat-list.sh" | cut -c1-64)"
case_run none 0 0 ":"
case_run moved 0 4 "touch -a -t 202611200000 '$T/files/f700'"
case_run missing 0 3 "rm -f '$T/files/f5'"
STUB_WANT=0000000000000000000000000000000000000000000000000000000000000000 case_run badlist 3 - ":"
export -n STUB_WANT 2>/dev/null; unset STUB_WANT
STUB_DROP=1 case_run short 3 - ":"
unset STUB_DROP
rm -rf "$T/w/"*; cp "$A" "$T/w/atime-around.sh"; cp "$H/atime-stat-list.sh" "$T/w/"
PATH="$T/bin:$PATH" bash "$T/w/atime-around.sh" pre > /dev/null 2>&1
PATH="$T/bin:$PATH" bash "$T/w/atime-around.sh" pre > "$T/twice" 2>&1; r=$?
if [ "$r" = 2 ] && grep -q '^REFUSED' "$T/twice"; then echo "PASS twice rc=2"; else echo "FAIL twice rc=$r"; ok=1; fi
rm -rf "$T"
[ "$ok" = 0 ] && echo "ATIME-AROUND TEST PASS" || echo "ATIME-AROUND TEST FAILED"
exit $ok
