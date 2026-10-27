#!/bin/bash
# usage: ci_merge.sh <pr> <head-sha>; waits for the PR's record-checks on that head, merges only on success
set -u
N=$1; H=$2
for i in $(seq 1 60); do
  r=$(gh pr view "$N" --json headRefOid,statusCheckRollup --jq "if .headRefOid==\"$H\" then ([.statusCheckRollup[]|select(.name==\"record-checks\")|(.status+\":\"+(.conclusion//\"\"))]|join(\" \")) else \"HEAD-MOVED:\"+.headRefOid end")
  [ "$(gh pr view "$N" --json mergeable --jq .mergeable)" = CONFLICTING ] && r="CONFLICTING"
  case "$r" in COMPLETED*|HEAD-MOVED*|CONFLICTING) break;; esac; sleep 20
done
echo "CI: $r"
case "$r" in COMPLETED:SUCCESS*) gh pr merge "$N" --merge --match-head-commit "$H" 2>&1 | tail -1;; *) echo "NOT MERGED"; exit 1;; esac
