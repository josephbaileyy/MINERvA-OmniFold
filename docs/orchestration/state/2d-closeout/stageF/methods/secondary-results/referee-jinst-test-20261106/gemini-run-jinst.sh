#!/usr/bin/env bash
# usage: run.sh <version> <k> ; runs Gemini via agy from an empty dir
R=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/be6e903d-7ae7-440f-b5aa-de78760f31e0/scratchpad/rr6
E=$(mktemp -d); cd "$E"
{ cat "$R/gem/preamble.txt"; cat "$R/referee-prompt-jinst.txt"; echo; cat "$R/$1.blind.txt"; } > "$R/gem/input-jinst-$1-$2.txt"
agy --model gemini-3.8-flash-high --sandbox -p "$(cat "$R/gem/input-jinst-$1-$2.txt")" > "$R/gem/answer-jinst-$1-$2.txt" 2> "$R/gem/err-jinst-$1-$2.txt"
echo "rc=$? emptydir_after=$(ls -A "$E" | wc -l)" > "$R/gem/status-jinst-$1-$2.txt"
