#!/bin/bash
# Clean-environment check of the whole RC10 deposit (zenodo-draft/checks/clean_env_check.sh, which RC8 and RC9 used,
# with the replay's name read from the package instead of fixed). A copy of the package in an empty directory, a fresh
# venv with the replay's pinned requirements, env -i with an empty HOME. Every step's exit status is read directly (no
# pipes). The package itself is only read. The BLAS thread pool is capped at one thread (CAPS), as the replay README
# advises on a loaded machine: uncapped, at load ~270, replay_inference.py ran 9 h 50 min without finishing
# (2026-11-27); capped, 94 s. The caps set only the thread count.
# usage: bash clean_env_check_rc10.sh PACKAGE SCRATCH
set -u
CAPS="OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 MKL_NUM_THREADS=1"
PKG=$1; S=$2
rm -rf "$S"; mkdir -p "$S/run" "$S/home"
cp -R "$PKG" "$S/run/deposit"; cd "$S/run/deposit" || exit 9
shasum -a 256 -c SHA256SUMS > "$S/deposit-sums.txt"; echo "deposit SHA256SUMS rc=$?"
TB=$(ls replay/*.tar.gz); [ "$(printf '%s\n' "$TB" | wc -l | tr -d ' ')" = 1 ] || { echo "not exactly one replay tarball"; exit 9; }
NAME=$(basename "$TB" .tar.gz); echo "replay tarball: $NAME"
shasum -a 256 "$TB" > "$S/tarball-sha.txt"; cat "$S/tarball-sha.txt"
/Users/josephbailey/miniconda3/bin/python3 -m venv "$S/venv" > "$S/venv.log" 2>&1
mkdir -p "$S/rc" && tar -xzf "$TB" -C "$S/rc"
"$S/venv/bin/pip" install -q -r "$S/rc/$NAME/requirements.txt" > "$S/pip.log" 2>&1; echo "pip rc=$?"
"$S/venv/bin/pip" freeze > "$S/freeze.txt"
# the README's reading example, extracted from the README itself
python3 -I -c "
import re; s=open('README.md').read(); m=re.search(r'## Reading example\n\n\`\`\`python\n(.*?)\`\`\`', s, re.S); open('$S/readme_example.py','w').write(m.group(1))"
env -i PATH="$S/venv/bin:/usr/bin:/bin" HOME="$S/home" $CAPS "$S/venv/bin/python3" -I "$S/readme_example.py" > "$S/example.out" 2>&1; echo "README example rc=$?"
cd "$S/rc/$NAME" || exit 9
shasum -a 256 -c SHA256SUMS > "$S/replay-pre.txt"; echo "replay SHA256SUMS before rc=$?"
env -i PATH="$S/venv/bin:/usr/bin:/bin" HOME="$S/home" $CAPS "$S/venv/bin/python3" code/verify_rc.py > "$S/verify.out" 2> "$S/verify.err"; echo "verify rc=$?"
shasum -a 256 -c SHA256SUMS > "$S/replay-post.txt"; echo "replay SHA256SUMS after rc=$?"
tail -1 "$S/verify.out"; wc -l < "$S/verify.err"
