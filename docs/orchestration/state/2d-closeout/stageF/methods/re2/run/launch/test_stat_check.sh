#!/bin/bash
# Test of re2b_stat_check (re2b_env.sh), in both directions (RE2-DECLARATION-B.md §4.2). Run on Perlmutter (GNU
# stat):   bash test_stat_check.sh <deploy or checkout>
# A stub sha256sum on PATH logs each call, so the test sees whether a re-hash happened. Each case runs in a
# subshell, since the check exits on refusal.
set -u
C=$(cd "$1" && pwd)
W=$(mktemp -d "${TMPDIR:-/tmp}/re2b-stat.XXXXXX"); trap 'rm -rf "$W"' EXIT
mkdir -p "$W/bin"
cat > "$W/bin/sha256sum" <<EOF
#!/bin/bash
echo "\$*" >> "$W/hash.calls"
exec /usr/bin/sha256sum "\$@"
EOF
chmod +x "$W/bin/sha256sum"
fail=0
f=$W/input.root
record() {  # a fresh input and its DTN-style record
    printf 'payload-%s\n' "$1" > "$f"; touch -d '2026-07-18 01:04:00' "$f"
    echo "$(/usr/bin/sha256sum "$f" | cut -d' ' -f1) $(stat -c '%s %Y %i' "$f") $f" > "$W/inputs.stat"
    : > "$W/hash.calls"
}
run() {  # run <declared sha>: the check in a subshell; prints rc and the number of re-hashes
    (PATH=$W/bin:$PATH; source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2b_env.sh"
     STATS=$W/inputs.stat; re2b_stat_check "$f" "$1") > "$W/out" 2>&1
    echo "$? $(grep -c . "$W/hash.calls")"
}
expect() {  # expect <case> <got "rc calls"> <want "rc calls">
    if [ "$2" = "$3" ]; then echo "ok   $1 ($2)"; else echo "FAIL $1: got '$2', want '$3'"; cat "$W/out"; fail=1; fi
}
export C
record a; good=$(/usr/bin/sha256sum "$f" | cut -d' ' -f1)
expect "unchanged stat: no re-hash" "$(run "$good")" "0 0"
record a; touch -d '2026-10-24 00:00:00' "$f"
expect "touched mtime: re-hash, same bytes pass" "$(run "$good")" "0 1"
record a; printf 'x' >> "$f"; touch -d '2026-07-18 01:04:00' "$f"
expect "changed size (mtime restored): re-hash, refused" "$(run "$good")" "4 1"
record a; cp -p "$f" "$f.new"; mv "$f.new" "$f"
expect "changed inode (same bytes, mtime kept): re-hash, pass" "$(run "$good")" "0 1"
record a; cp -p "$f" "$f.new"; printf 'payload-b\n' > "$f.new"; touch -d '2026-07-18 01:04:00' "$f.new"; mv "$f.new" "$f"
expect "changed inode and bytes, same size and mtime: re-hash, refused" "$(run "$good")" "4 1"
record a
expect "record's sha is not the declared one: refused before any hash" "$(run "$(printf '0%.0s' {1..64})")" "5 0"
record a; cat "$W/inputs.stat" "$W/inputs.stat" > "$W/two"; mv "$W/two" "$W/inputs.stat"
expect "two record rows: refused" "$(run "$good")" "5 0"
record a; : > "$W/inputs.stat"
expect "no record row: refused" "$(run "$good")" "5 0"
[ $fail = 0 ] && echo "test_stat_check: 8/8 passed" || { echo "test_stat_check: FAILED"; exit 1; }
