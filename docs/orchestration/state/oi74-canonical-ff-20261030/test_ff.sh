#!/bin/bash
# Local test of ff.sh against a scratch repository, in both directions: each STOP fires on its bad state and leaves
# the tree as it found it (or restores it), and a good state runs to DONE.
#   bash docs/orchestration/state/oi74-canonical-ff-20261030/test_ff.sh <scratch-dir>
# Nothing outside <scratch-dir> is written. ff.sh is copied with only its five path/sha constants substituted.
set -u
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
T=${1:?usage: test_ff.sh <scratch-dir>}
mkdir -p "$T" && T=$(cd "$T" && pwd)
pass=0; fail=0
G() { git -c user.name=t -c user.email=t@t.invalid -c init.defaultBranch=main "$@"; }

build() {  # $1 = case dir. Builds github.git with OLD and NEW, and a checkout R at OLD with the two live-state edits.
  local C=$1; rm -rf "$C"; mkdir -p "$C/bin"
  G init -q "$C/src" && cd "$C/src" || exit 1
  mkdir -p docs/orchestration/state nd-unfolding
  printf 'live v1\n' > docs/orchestration/LIVE-STATE.md
  printf '{"v": 1}\n' > docs/orchestration/state/live-state-last-known.json
  printf '*.npz\n' > .gitignore
  printf 'R=%s\n' "$C/R" > nd-unfolding/run.sh
  G add -A && G commit -q -m old
  OLD=$(git rev-parse HEAD)
  printf 'live v2\n' > docs/orchestration/LIVE-STATE.md
  printf 'new code\n' > nd-unfolding/new.py
  printf 'product bytes\n' > nd-unfolding/p.npz && G add -f nd-unfolding/p.npz
  G add -A && G commit -q -m new
  NEW=$(git rev-parse HEAD)
  G clone -q --bare "$C/src" "$C/github.git"
  G clone -q -o github "$C/github.git" "$C/R" && cd "$C/R" && G reset -q --hard "$OLD"
  printf 'live edited on the cluster\n' > docs/orchestration/LIVE-STATE.md
  printf '{"v": "edited"}\n' > docs/orchestration/state/live-state-last-known.json
  printf 'u\n' > untracked1.txt; printf 'u\n' > untracked2.txt
  printf '#!/bin/sh\ncat "%s/jobs" 2>/dev/null; exit 0\n' "$C" > "$C/bin/squeue"
  printf '#!/bin/sh\nshift; exec "$@"\n' > "$C/bin/timeout"
  chmod +x "$C/bin/squeue" "$C/bin/timeout"
  sed -e "s#^R=.*#R=$C/R#" -e "s#^A=.*#A=$C/aside#" -e "s#^OLD=.*#OLD=$OLD#" \
      -e "s#^LAUNCHER_PATH=.*#LAUNCHER_PATH=$C/R#" "$HERE/ff.sh" > "$C/ff.sh"
  echo "$OLD $NEW" > "$C/shas"
}

run() { local C=$1; (cd "$C" && PATH="$C/bin:$PATH" bash ff.sh > out.txt 2>&1); echo $?; }
state() {  # HEAD and the tracked porcelain of R, plus the two files' bytes.
  local C=$1; (cd "$C/R" && git rev-parse HEAD; git status --porcelain --untracked-files=no;
                cat docs/orchestration/LIVE-STATE.md docs/orchestration/state/live-state-last-known.json) ; }
check() {  # $1 name, $2 expected rc, $3 actual rc, $4 condition (shell expr, 0 = true)
  if [ "$2" = "$3" ] && [ "$4" -eq 0 ]; then pass=$((pass + 1)); echo "PASS  $1 (rc $3)"; else
    fail=$((fail + 1)); echo "FAIL  $1 (expected rc $2, got $3; condition $4)"; sed 's/^/      /' "$C/out.txt" | tail -8; fi
}

# 1. Good state: runs to DONE, HEAD = NEW, no tracked changes, aside copies hold the cluster edits.
C=$T/good; build "$C"; read OLD NEW < "$C/shas"; rc=$(run "$C")
ok=1; [ "$(cd "$C/R" && git rev-parse HEAD)" = "$NEW" ] && [ -z "$(cd "$C/R" && git status --porcelain --untracked-files=no)" ] \
  && grep -q 'live edited on the cluster' "$C/aside/LIVE-STATE.md" && grep -q '^DONE' "$C/out.txt" \
  && [ -e "$C/R/untracked1.txt" ] && ok=0
check "good state runs to DONE and keeps the untracked files" 0 "$rc" "$ok"

# 2. An identical ignored product already at an added path: the overwrite is a no-op, so it proceeds.
C=$T/ignored-identical; build "$C"; printf 'product bytes\n' > "$C/R/nd-unfolding/p.npz"; rc=$(run "$C")
ok=1; grep -q 'present 1 identical 1 differ 0' "$C/out.txt" && grep -q '^DONE' "$C/out.txt" && ok=0
check "an identical ignored file at an added path proceeds" 0 "$rc" "$ok"

# STOPs before any write: the tree must be byte-identical to before.
stop_before_write() {  # $1 name, $2 expected rc, $3 mutation (run in R or C)
  C=$T/$4; build "$C"; (cd "$C" && eval "$3"); before=$(state "$C"); rc=$(run "$C")
  ok=1; [ "$(state "$C")" = "$before" ] && grep -q "^STOP $2:" "$C/out.txt" && ok=0
  check "$1" "$2" "$rc" "$ok"
}
stop_before_write "a job under --me stops before any write" 11 'echo "123|PENDING|x|/w" > jobs' job
stop_before_write "a different HEAD stops before any write" 12 '(cd R && git -c user.name=t -c user.email=t@t.invalid commit -q --allow-empty -m drift)' head
stop_before_write "a third tracked change stops before any write" 15 'echo x >> R/nd-unfolding/run.sh' tracked
stop_before_write "only one of the two live-state edits stops before any write" 15 '(cd R && git checkout -q -- docs/orchestration/LIVE-STATE.md)' onefile
stop_before_write "an existing aside directory stops before any write" 16 'mkdir aside' aside

# STOPs after W2: the two files must be restored to their cluster bytes, HEAD unchanged.
stop_after_write() {  # $1 name, $2 expected rc, $3 mutation
  C=$T/$4; build "$C"; read OLD NEW < "$C/shas"; (cd "$C" && eval "$3"); before=$(state "$C"); rc=$(run "$C")
  ok=1; [ "$(state "$C")" = "$before" ] && grep -q "^STOP $2:" "$C/out.txt" && grep -q 'rollback_tracked OK' "$C/out.txt" && ok=0
  check "$1" "$2" "$rc" "$ok"
}
stop_after_write "a different ignored product at an added path stops and rolls back" 25 'echo other > R/nd-unfolding/p.npz' differ
stop_after_write "an untracked file at an added path stops and rolls back" 26 'echo new code > R/nd-unfolding/new.py' blocking
stop_after_write "a failed fetch stops and rolls back" 23 '(cd R && git remote set-url github /nonexistent)' fetch
stop_after_write "a job appearing before the merge stops and rolls back" 27 \
  'printf "#!/bin/sh\nif [ -e %s/seen ]; then echo 9\\|RUNNING\\|y\\|/w; else touch %s/seen; fi\n" "$PWD" "$PWD" > bin/squeue' late-job

echo "test_ff: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
