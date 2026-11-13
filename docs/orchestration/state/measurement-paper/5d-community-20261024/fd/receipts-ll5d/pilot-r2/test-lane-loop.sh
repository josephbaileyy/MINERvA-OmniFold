#!/bin/bash
# The lane loops of connect-pilot.sh and connect-bulk.sh, run for real against a stub srun (the director's ruling after
# the pilot r1 STOP, 61181899: lanes 0, 4 and 5 ran only their first row, because the loop read its table on stdin and
# srun swallowed it). For each connect: its own lanes table (the LANES heredoc) and its own lane() function (the job
# heredoc), extracted verbatim, run over every lane (and, for the bulk, every node) with sentinel lines on the lane's
# stdin. The stub srun reads its stdin: any line it gets is a STDIN-LEAK. PASS needs every table row's "rc=0" line and
# no leak.
#     bash test-lane-loop.sh            the real connects must PASS, and two mutants of each must FAIL:
#                                       M1 srun without "< /dev/null" (killed by the leak check),
#                                       M2 r1's loop (stdin table, no -u 3, no "< /dev/null"; killed by the rows check)
#     bash test-lane-loop.sh one FILE pilot|bulk     one connect file, rc 0 PASS / 1 FAIL
set -u
H=$(cd "$(dirname "$0")" && pwd)

one() {  # one <connect file> <pilot|bulk>; the job scripts run without set -u, so does this
    set +u
    local f=$1 kind=$2 td name rows missing leak
    td=$(mktemp -d "${TMPDIR:-/tmp}/lanes.XXXXXX")
    name=$kind-lanes.tsv
    sed -n "/^cat > \"\$W\/$name\" <<'LANES'\$/,/^LANES\$/p" "$f" | sed '1d;$d' > "$td/$name"
    awk '/^lane\(\) \{$/ {on = 1} on {print} on && /^}$/ {exit}' "$f" > "$td/lane.sh"
    [ -s "$td/$name" ] && [ -s "$td/lane.sh" ] || { echo "FAIL $kind: table or lane() not found in $f"; rm -rf "$td"; return 1; }
    W=$td DD=/dd U=$td/u G18W=/g AR23W=/a G18CP=x AR23CP=y WORLD=(--world)
    mkdir -p "$W/lanes"
    srun() {   # stub: drop the options, read stdin (a leak if anything arrives), report the unit
        while [[ $1 == -* ]]; do case $1 in -c|-n) shift 2 ;; *) shift ;; esac; done
        local got; got=$(cat)
        [ -n "$got" ] && echo "STDIN-LEAK $(echo "$got" | head -1)"
        echo "ran"
        return 0
    }
    # shellcheck disable=SC1090
    source "$td/lane.sh"
    local sentinel; sentinel=$(printf 'sentinel %s\n' 1 2 3 4 5)
    if [ "$kind" = pilot ]; then
        for L in $(awk -F'\t' '!/^#/ {print $1}' "$W/$name" | sort -u); do lane "$L" <<< "$sentinel"; done
        missing=$(awk -F'\t' '!/^#/ {print "lane "$1" "$2" "$3" rc=0"}' "$W/$name" | while IFS= read -r want; do
            grep -qxF "$want" "$W"/lanes/*.out 2>/dev/null || echo "$want"; done | wc -l | tr -d ' ')
    else
        for NODE in $(awk -F'\t' '!/^#/ {print $1}' "$W/$name" | sort -u); do
            for L in 0 1 2 3 4 5 6 7; do lane "$L" <<< "$sentinel"; done
        done
        missing=$(awk -F'\t' '!/^#/ {print "node "$1" lane "$2" "$3" "$4" rc=0"}' "$W/$name" | while IFS= read -r want; do
            grep -qxF "$want" "$W"/lanes/*.out 2>/dev/null || echo "$want"; done | wc -l | tr -d ' ')
    fi
    rows=$(grep -vc '^#' "$W/$name")
    leak=$(cat "$W"/lanes/*.out 2>/dev/null | grep -c '^STDIN-LEAK')
    rm -rf "$td"
    if [ "$missing" = 0 ] && [ "$leak" = 0 ]; then echo "PASS $kind rows=$rows missing=0 leaks=0"; return 0; fi
    echo "FAIL $kind rows=$rows missing=$missing leaks=$leak"; return 1
}

if [ "${1:-}" = one ]; then one "$2" "$3"; exit $?; fi

ok=0
td=$(mktemp -d "${TMPDIR:-/tmp}/mut.XXXXXX")
for kind in pilot bulk; do
    f=$H/connect-$kind.sh
    echo "== $kind: $(shasum -a 256 "$f" | cut -c1-64)"
    ( one "$f" "$kind" ) || ok=1
    sed 's# < /dev/null >> "\$W/lanes/# >> "$W/lanes/#' "$f" > "$td/m1-$kind.sh"
    if cmp -s "$f" "$td/m1-$kind.sh"; then echo "M1 NOT-APPLICABLE $kind"; ok=1
    elif ( one "$td/m1-$kind.sh" "$kind" > "$td/out" ); then echo "M1 SURVIVED $kind: $(cat "$td/out")"; ok=1
    else echo "M1 KILLED $kind (srun without < /dev/null): $(cat "$td/out")"; fi
    sed -e 's#read -r -u 3 #read -r #' -e 's#  done 3< <(#  done < <(#' -e 's# < /dev/null >> "\$W/lanes/# >> "$W/lanes/#' "$f" > "$td/m2-$kind.sh"
    if cmp -s "$f" "$td/m2-$kind.sh"; then echo "M2 NOT-APPLICABLE $kind"; ok=1
    elif ( one "$td/m2-$kind.sh" "$kind" > "$td/out" ); then echo "M2 SURVIVED $kind: $(cat "$td/out")"; ok=1
    else echo "M2 KILLED $kind (r1's loop): $(cat "$td/out")"; fi
done
rm -rf "$td"
[ "$ok" = 0 ] && echo "LANE-LOOP TEST PASS" || echo "LANE-LOOP TEST FAILED"
exit $ok
