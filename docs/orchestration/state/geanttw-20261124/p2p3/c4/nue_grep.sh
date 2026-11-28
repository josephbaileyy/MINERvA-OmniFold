#!/bin/bash
# geanttw P2-P3 A4: grep every bound source tree for SetNuEConstraint. Read-only, on a login node, in geanttw's own root.
#   bash nue_grep.sh [SRC_ROOT]      # SRC_ROOT defaults to /pscratch/sd/j/josephrb/geanttw-20261124/src
# The trees are SRC_ROOT/{evloop,MAT,MAT-MINERvA-pin,MAT-MINERvA-pat}. Before any grep, every symlink in them is listed
# with its target. This part STOPs (exit 2) if any symlink resolves outside SRC_ROOT, or if a tree is missing. Then it
# runs `grep -rn` (-r, which never follows symlinks; never -R) over source extensions only. It prints each tree's git
# HEAD and the sha256 of every file with a hit. Writes nothing.
SRC="${1:-${NUE_TEST_SRC:-/pscratch/sd/j/josephrb/geanttw-20261124/src}}"   # NUE_TEST_SRC: the tests' only door
TREES=(evloop MAT MAT-MINERvA-pin MAT-MINERvA-pat)
stop() { echo "STOP: $*"; exit 2; }
root=$(readlink -f "${SRC}") || stop "cannot resolve ${SRC}"
for t in "${TREES[@]}"; do [ -d "${root}/${t}" ] || stop "no tree ${root}/${t}"; done
echo "== symlinks under ${root} (target, resolved)"
bad=0
while IFS= read -r -d '' l; do
  r=$(readlink -f "$l"); echo "link $l -> $(readlink "$l") => ${r:-UNRESOLVED}"
  case "$r" in "${root}"/*) ;; *) bad=1; echo "OUTSIDE: $l => ${r:-UNRESOLVED}";; esac
done < <(for t in "${TREES[@]}"; do find "${root}/${t}" -type l -print0; done)
[ "${bad}" -eq 0 ] || stop "a symlink resolves outside ${root}"
for t in "${TREES[@]}"; do
  d="${root}/${t}"
  head=$(git -C "$d" rev-parse HEAD 2>/dev/null || echo "not-a-git-tree")
  echo "== tree ${t} HEAD ${head}"
  hits=$(grep -rn --include='*.cpp' --include='*.cxx' --include='*.cc' --include='*.h' --include='*.hh' \
    --include='*.C' --include='*.py' --include='*.sh' --include='CMakeLists.txt' --include='*.cmake' \
    SetNuEConstraint "$d"); grc=$?
  [ ${grc} -le 1 ] || stop "grep failed on ${d} (rc ${grc})"
  if [ -z "${hits}" ]; then echo "no hits"; continue; fi
  printf '%s\n' "${hits}"
  printf '%s\n' "${hits}" | cut -d: -f1 | sort -u | while IFS= read -r f; do echo "sha256 $(sha256sum "$f")"; done
done
echo "== nue_grep done"
