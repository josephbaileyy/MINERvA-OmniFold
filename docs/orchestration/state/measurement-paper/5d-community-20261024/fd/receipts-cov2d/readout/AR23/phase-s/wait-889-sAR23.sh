#!/bin/bash
# The director's condition for AR23 phase S: launch only after #889 (COV2D-BINDING-2 addendum A5) is merged on
# origin/main. Polls every 60 s (up to 2 h): #889 MERGED (gh), its merge commit an ancestor of freshly fetched
# origin/main, and origin/main's COV2D-BINDING-2.md naming addendum A5. Then runs launch-s5.sh sAR23 (which fences).
H=/Users/josephbailey/cov2d-work; B=docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-BINDING-2.md
cd "$H/wt-m" || exit 2
for i in $(seq 1 120); do
  st=$(gh pr view 889 --json state,mergeCommit -q '.state+" "+(.mergeCommit.oid//"")' 2>&1); grc=$?
  git fetch -q origin main; frc=$?
  set -- $st
  echo "$(date -u +%FT%TZ) gh rc=$grc fetch rc=$frc pr889=$st"
  if [ "$grc" = 0 ] && [ "$frc" = 0 ] && [ "$1" = MERGED ] && [ -n "$2" ] && git merge-base --is-ancestor "$2" origin/main \
     && git show "origin/main:$B" | grep -q 'addendum A5'; then
    echo "889 MERGED as $2, in origin/main $(git rev-parse origin/main); BINDING-2 names addendum A5: launching"
    bash "$H/launch-s5.sh" sAR23 > "$H/a4/launch-sAR23.out" 2>&1; echo "launcher rc=$?" >> "$H/a4/launch-sAR23.out"; exit 0
  fi
  sleep 60
done
echo "gave up after 2 h"; exit 4
