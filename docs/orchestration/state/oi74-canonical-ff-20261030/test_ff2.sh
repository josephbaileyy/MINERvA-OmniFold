#!/bin/bash
# Local test of ff2.sh against a scratch repository, in both directions: each STOP fires on its bad state and leaves
# the tree as it found it (or restores all six files), and a good state runs to DONE.
#   bash docs/orchestration/state/oi74-canonical-ff-20261030/test_ff2.sh <scratch-dir>
# Nothing outside <scratch-dir> is written. ff2.sh is copied with only its four path/sha constants substituted.
set -u
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
T=${1:?usage: test_ff2.sh <scratch-dir>}
mkdir -p "$T" && T=$(cd "$T" && pwd)
pass=0; fail=0
G() { git -c user.name=t -c user.email=t@t.invalid -c init.defaultBranch=main "$@"; }
FOUR="docs/orchestration/dashboard.html docs/orchestration/dashboard_collector.py docs/orchestration/test_dashboard_collector.py nd-unfolding/tests/test_cstat_100rep.py"

build() {  # $1 = case dir. github.git holds OLD and NEW; R is at OLD with the two live-state edits, the four untracked
           # files byte-identical to NEW's, and the aside directory exactly as the first run left it.
  local C=$1 p; rm -rf "$C"; mkdir -p "$C/bin"
  G init -q "$C/src" && cd "$C/src" || exit 1
  mkdir -p docs/orchestration/state nd-unfolding/tests
  printf 'live v1\n' > docs/orchestration/LIVE-STATE.md
  printf '{"v": 1}\n' > docs/orchestration/state/live-state-last-known.json
  printf '*.npz\n' > .gitignore
  printf 'R=%s\n' "$C/R" > nd-unfolding/run.sh
  G add -A && G commit -q -m old
  OLD=$(git rev-parse HEAD)
  printf 'live v2\n' > docs/orchestration/LIVE-STATE.md
  for p in $FOUR; do printf 'main bytes of %s\n' "$p" > "$p"; done
  printf 'new code\n' > nd-unfolding/new.py
  printf 'product bytes\n' > nd-unfolding/p.npz && G add -f nd-unfolding/p.npz
  G add -A && G commit -q -m new
  NEW=$(git rev-parse HEAD)
  G clone -q --bare "$C/src" "$C/github.git"
  G clone -q -o github "$C/github.git" "$C/R" && cd "$C/R" && G reset -q --hard "$OLD"
  printf 'live edited on the cluster\n' > docs/orchestration/LIVE-STATE.md
  printf '{"v": "edited"}\n' > docs/orchestration/state/live-state-last-known.json
  mkdir -p docs/orchestration nd-unfolding/tests
  for p in $FOUR; do printf 'main bytes of %s\n' "$p" > "$p"; done
  printf 'u\n' > untracked1.txt; printf 'u\n' > untracked2.txt
  mkdir "$C/aside"
  cp -p docs/orchestration/LIVE-STATE.md "$C/aside/LIVE-STATE.md"
  cp -p docs/orchestration/state/live-state-last-known.json "$C/aside/live-state-last-known.json"
  (cd "$C/aside" && sha256sum LIVE-STATE.md live-state-last-known.json > SHA256SUMS)
  printf '#!/bin/sh\ncat "%s/jobs" 2>/dev/null; exit 0\n' "$C" > "$C/bin/squeue"
  printf '#!/bin/sh\nshift; exec "$@"\n' > "$C/bin/timeout"
  chmod +x "$C/bin/squeue" "$C/bin/timeout"
  sed -e "s#^R=.*#R=$C/R#" -e "s#^A=.*#A=$C/aside#" -e "s#^OLD=.*#OLD=$OLD#" \
      -e "s#^LAUNCHER_PATH=.*#LAUNCHER_PATH=$C/R#" "$HERE/ff2.sh" > "$C/ff2.sh"
  echo "$OLD $NEW" > "$C/shas"
}

run() { local C=$1; (cd "$C" && PATH="$C/bin:$PATH" bash ff2.sh > out.txt 2>&1); echo $?; }
state() {  # HEAD, the tracked porcelain, all six files' bytes (or "absent"), and the first run's aside directory.
  local C=$1 p; (cd "$C/R" && git rev-parse HEAD; git status --porcelain --untracked-files=no
    for p in docs/orchestration/LIVE-STATE.md docs/orchestration/state/live-state-last-known.json $FOUR; do
      echo "== $p"; cat "$p" 2>/dev/null || echo absent; done
    cd "$C/aside" 2>/dev/null && ls -A | grep -v '^untracked-at-added-paths$'
    cat LIVE-STATE.md live-state-last-known.json SHA256SUMS 2>/dev/null); }
left_in_u() {  # files other than SHA256SUMS left in the subdirectory for the four; a rollback must leave none.
  if [ -d "$1/aside/untracked-at-added-paths" ]; then
    find "$1/aside/untracked-at-added-paths" -type f ! -name SHA256SUMS | wc -l | tr -d ' '; else echo 0; fi; }
check() {  # $1 name, $2 expected rc, $3 actual rc, $4 condition (0 = true)
  if [ "$2" = "$3" ] && [ "$4" -eq 0 ]; then pass=$((pass + 1)); echo "PASS  $1 (rc $3)"; else
    fail=$((fail + 1)); echo "FAIL  $1 (expected rc $2, got $3; condition $4)"; sed 's/^/      /' "$C/out.txt" | tail -10; fi
}

# 1. Good state: DONE; HEAD = NEW; no tracked changes; the four tracked with main's bytes and their moved copies
#    checked; the first run's aside copies untouched; the other untracked files kept.
C=$T/good; build "$C"; read OLD NEW < "$C/shas"; aside_before=$(cd "$C/aside" && cat SHA256SUMS); rc=$(run "$C")
ok=1; [ "$(cd "$C/R" && git rev-parse HEAD)" = "$NEW" ] && [ -z "$(cd "$C/R" && git status --porcelain --untracked-files=no)" ] \
  && [ "$(grep -c 'tracked_and_equal YES' "$C/out.txt")" -eq 4 ] && (cd "$C/aside/untracked-at-added-paths" && sha256sum -c SHA256SUMS >/dev/null) \
  && [ "$(cd "$C/aside" && cat SHA256SUMS)" = "$aside_before" ] && grep -q 'live edited on the cluster' "$C/aside/LIVE-STATE.md" \
  && grep -q '^DONE' "$C/out.txt" && [ -e "$C/R/untracked1.txt" ] && ok=0
check "good state runs to DONE, the four tracked and their copies checked" 0 "$rc" "$ok"

# 2. An identical ignored product at an added path, beside the four: still proceeds.
C=$T/ignored-identical; build "$C"; printf 'product bytes\n' > "$C/R/nd-unfolding/p.npz"; rc=$(run "$C")
ok=1; grep -q 'present 5 identical 5 differ 0 untracked_not_ignored 4' "$C/out.txt" && grep -q '^DONE' "$C/out.txt" && ok=0
check "an identical ignored file beside the four proceeds" 0 "$rc" "$ok"

# STOPs before any write: everything byte-identical to before.
stop_before_write() {  # $1 name, $2 expected rc, $3 mutation (run in C), $4 case dir
  C=$T/$4; build "$C"; (cd "$C" && eval "$3"); before=$(state "$C"); rc=$(run "$C")
  ok=1; [ "$(state "$C")" = "$before" ] && grep -q "^STOP $2:" "$C/out.txt" && ok=0
  check "$1" "$2" "$rc" "$ok"
}
stop_before_write "a job under --me stops before any write" 11 'echo "123|PENDING|x|/w" > jobs' job
stop_before_write "a different HEAD stops before any write" 12 '(cd R && git -c user.name=t -c user.email=t@t.invalid commit -q --allow-empty -m drift)' head
stop_before_write "a third tracked change stops before any write" 15 'echo x >> R/nd-unfolding/run.sh' tracked
stop_before_write "a missing aside directory stops before any write" 16 'rm -r aside' aside-missing
stop_before_write "an extra file in the aside directory stops before any write" 16 'echo x > aside/extra' aside-extra
stop_before_write "an existing subdirectory for the four stops before any write" 17 'mkdir aside/untracked-at-added-paths' subdir
stop_before_write "an aside copy that fails its SHA256SUMS stops before any write" 18 'echo x >> aside/LIVE-STATE.md' aside-altered
stop_before_write "a live-state file differing from its aside copy stops before any write" 19 'echo regenerated >> R/docs/orchestration/LIVE-STATE.md' regenerated

# STOPs from W2 on: all six files restored to their bytes, HEAD unchanged, the aside copies untouched.
stop_after_write() {  # $1 name, $2 expected rc, $3 mutation, $4 case dir
  C=$T/$4; build "$C"; read OLD NEW < "$C/shas"; (cd "$C" && eval "$3"); before=$(state "$C"); rc=$(run "$C")
  ok=1; [ "$(state "$C")" = "$before" ] && grep -q "^STOP $2:" "$C/out.txt" && grep -q 'rollback_tracked OK' "$C/out.txt" \
    && [ "$(left_in_u "$C")" -eq 0 ] && ok=0
  check "$1" "$2" "$rc" "$ok"
}
stop_after_write "one of the four differing from main stops and rolls back" 25 'echo other >> R/docs/orchestration/dashboard.html' differ
stop_after_write "a fifth untracked file at an added path stops and rolls back" 26 'echo new code > R/nd-unfolding/new.py' fifth
stop_after_write "one of the four missing stops and rolls back" 26 'rm R/nd-unfolding/tests/test_cstat_100rep.py' one-missing
stop_after_write "a failed fetch stops and rolls back" 23 '(cd R && git remote set-url github /nonexistent)' fetch
# A file that changes between P5 and its own move: the first mv call alters the second of the four. The first file has
# moved by then, so the rollback must move it back. The state compared is the one with the alteration applied.
stop_after_write_29() {
  C=$T/rehash; build "$C"; read OLD NEW < "$C/shas"
  printf '#!/bin/sh\nif [ ! -e %s/moved-once ]; then touch %s/moved-once; echo changed >> %s/R/docs/orchestration/dashboard_collector.py; fi\nexec /bin/mv "$@"\n' \
    "$C" "$C" "$C" > "$C/bin/mv"; chmod +x "$C/bin/mv"
  rc=$(run "$C")
  ok=1; grep -q "^STOP 29:" "$C/out.txt" && grep -q 'rollback_move docs/orchestration/dashboard.html rc 0' "$C/out.txt" \
    && grep -q 'rollback_tracked OK' "$C/out.txt" && [ "$(cd "$C/R" && git rev-parse HEAD)" = "$OLD" ] \
    && [ "$(cat "$C/R/docs/orchestration/dashboard.html")" = "main bytes of docs/orchestration/dashboard.html" ] \
    && [ ! -e "$C/aside/untracked-at-added-paths/docs/orchestration/dashboard.html" ] && ok=0
  check "a file changed just before its move stops, and the one already moved comes back" 29 "$rc" "$ok"
}
stop_after_write_29
stop_after_write "a job appearing before the merge stops and moves all four back" 27 \
  'printf "#!/bin/sh\nif [ -e %s/seen ]; then echo 9\\|RUNNING\\|y\\|/w; else touch %s/seen; fi\n" "$PWD" "$PWD" > bin/squeue' late-job

echo "test_ff2: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
