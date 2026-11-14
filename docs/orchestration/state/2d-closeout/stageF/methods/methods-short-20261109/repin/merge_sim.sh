#!/bin/bash
# Merge simulation for #981's re-pin: a detached worktree at a #977 head with #981's package directory checked out
# into it from #981's head, then dryrun.py run there. The build then reads the head's values producer and values files.
# Usage, from any checkout that has fetched both branches:
#   bash merge_sim.sh <new empty dir> <#977 head> <#981 head>
# Afterwards remove the worktree with: git worktree remove --force <dir>
set -u
DIR=${1:?new empty dir}; H977=${2:?#977 head}; H981=${3:?#981 head}
PKG=docs/orchestration/state/2d-closeout/stageF/methods/result-package-20261109
HERE=$(cd "$(dirname "$0")" && pwd)
[ -e "$DIR" ] && { echo "STOP: $DIR exists"; exit 2; }
git worktree add -q --detach "$DIR" "$H977" || exit 2
git -C "$DIR" checkout -q "$H981" -- "$PKG" || exit 2
echo "merge simulation: tree $(git -C "$DIR" rev-parse --short=9 HEAD) with $PKG from $(git rev-parse --short=9 "$H981")"
cd "$DIR" && python3 -B "$HERE/dryrun.py" "$H977"
