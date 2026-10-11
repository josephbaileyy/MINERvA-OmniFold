#!/bin/bash
SP=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/c5961a1c-c2f8-4299-b73b-907c4dff568b/scratchpad/selio
cd /Users/josephbailey/local-research/MINERvA-OmniFold
for c in 3892e769043cddebfd58ec19e1ab1a567eb01784 d4335d3b9bc2502002f93390f9555d07e134855f 07428e5d; do
  W=$SP/wt-${c:0:8}
  git worktree add -q --detach $W $c 2>&1 | tail -1
  $SP/run_frozen.sh $W $SP/frozen-at-${c:0:8}.txt
  git worktree remove --force $W
done
echo DONE > $SP/frozen_all.done
