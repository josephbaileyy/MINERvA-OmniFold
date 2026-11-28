#!/bin/bash
# Re-apply one harness mutant of ptmc_mutation.py to a copy of launch/ OUTSIDE the repository (under $HOME, for colima)
# and run harness_remote.sh on it in debian:bookworm-slim. It prints every FAIL line and the pass count. It is used where
# the mutation record's 1,500-character tail cut the failing line.
#   bash reapply_harness_mutant.sh PTMC_DIR MUTANT_NAME
set -euo pipefail
P=$(cd "$1" && pwd); N=$2
W=$(mktemp -d "$HOME/ptmc-mutcheck.XXXXXX")
trap 'rm -rf "$W"' EXIT
cp "$P"/launch/*.sh "$P"/launch/*.sbatch "$W"/
python3 - "$P" "$N" "$W" <<'PY'
import importlib.util, sys
from pathlib import Path
p, n, w = sys.argv[1:]
spec = importlib.util.spec_from_file_location("m", f"{p}/ptmc_mutation.py"); m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
mt = [x for x in m.MUTANTS if x[0] == n][0]
assert mt[4] == m.HR, f"{n} is not a harness_remote mutant"
f = Path(w) / Path(mt[1]).name; s = f.read_text(); assert s.count(mt[2]) == 1, "anchor"
f.write_text(s.replace(mt[2], mt[3]))
print(f"mutant {n} applied to {f.name}")
PY
docker run --rm -v "$W":/h:ro debian:bookworm-slim bash /h/harness_remote.sh 2>&1 | grep -E "^FAIL|^pass" || true
