#!/bin/bash
# test_cleanup.sh: e1-list.sh, build_remove.sh and e1-remove.sh.in on temporary roots, with GNU find/sha256sum/date,
# sacct and hostname as PATH shims (macOS has no GNU find -printf). The literal roots are replaced by temporary paths
# in throwaway copies; nothing outside the temporary directory is touched.
# usage: bash test_cleanup.sh
HERE=$(cd "$(dirname "$0")" && pwd)
T=$(mktemp -d "${TMPDIR:-/tmp}/e1-cleanup-test.XXXXXX") || exit 9
trap 'rm -rf -- "$T"' EXIT
mkdir -p "$T/bin"
cat > "$T/bin/find" <<'PY'
#!/usr/bin/env python3
import os, stat, sys
a = sys.argv[1:]
root, fmt = a[0], a[a.index("-printf") + 1]
out = []
for dp, dn, fn in os.walk(root):
    for n in dn + fn:
        p = os.path.join(dp, n)
        st = os.lstat(p)
        t = "l" if stat.S_ISLNK(st.st_mode) else "d" if stat.S_ISDIR(st.st_mode) else "f"
        rel = os.path.relpath(p, root)
        out.append(fmt.replace("%y", t).replace("%s", str(st.st_size)).replace("%P", rel).replace("\\n", "\n"))
    dn[:] = [d for d in dn if not os.path.islink(os.path.join(dp, d))]
sys.stdout.write("".join(out))
PY
printf '#!/bin/bash\nshasum -a 256 | sed "s/ .*$/  -/"\n' > "$T/bin/sha256sum"
printf '#!/bin/bash\nif [ "$1" = -u ] && [ "$2" = -d ]; then echo 2026-11-13; else /bin/date "$@"; fi\n' > "$T/bin/date"
printf '#!/bin/bash\nprintf "%%b" "${SACCT_OUT:-1|rpd_flux4|COMPLETED\\n}"\n' > "$T/bin/sacct"
printf '#!/bin/bash\necho "${HOSTNAME_STUB:-login02}"\n' > "$T/bin/hostname"
chmod +x "$T/bin/"*
export PATH="$T/bin:$PATH"
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
export REPO_FOR_LINKS="$REPO"
git -C "$REPO" ls-tree -r 2415e8d66d1a9160e724d426eaeb54d458d4b4f7 | awk -F'\t' '$1 ~ /^120000/ {print $2}' > "$T/links.txt"
[ "$(wc -l < "$T/links.txt" | tr -d ' ')" = 241 ] || { echo "SETUP: S's symlink list is not 241"; exit 9; }
fails=0
check() { if [ "$2" = "$3" ] && printf '%s' "$5" | grep -qF -- "$4"; then echo "ok   $1"; else echo "FAIL $1 (rc $3, wanted $2 and '$4')"; printf '%s\n' "$5" | sed 's/^/     /' | tail -8; fails=$((fails + 1)); fi; }
setup() {  # fresh roots and fresh script copies pointed at them
  rm -rf "$T/case"; mkdir -p "$T/case"
  B="$T/case/pscratch"
  P0="$B/rpd-reco-p0e1-20261126"; F4="$B/rpd-reco-flux4-20261126"; D2="$B/rpd-reco-d2s0e1-20261127"
  mkdir -p "$P0/dry/staged" "$P0/run/staged" "$P0/clone/x" "$F4/run" "$D2/run"
  for d in dry run; do
    for pl in 1A 1M; do printf 'omni %s %s' "$d" "$pl" > "$P0/$d/staged/abcdef0123456789-runEventLoopOmniFold_RDX_$pl.root"; done
    printf 'dump' > "$P0/$d/staged/0123456789abcdef-lat_1A.npz"
  done
  printf 'p0' > "$P0/run/p0.json"; printf 'c' > "$P0/clone/x/f.py"
  for R in "$P0" "$F4" "$D2"; do  # each clone holds exactly S's 241 committed symlinks, and a file with spaces
    mkdir -p "$R/clone"
    while IFS= read -r l; do mkdir -p "$R/clone/$(dirname "$l")"; ln -s target "$R/clone/$l"; done < "$T/links.txt"
    printf 'pdf' > "$R/clone/MINERvA with OmniFold -- 3D+.pdf"
  done
  printf 'factors' > "$F4/run/flux-factors-1A.npz"; printf 'stop' > "$D2/run/d2-predict.STOP.json"
  mkdir -p "$T/case/pkg"
  for f in e1-list.sh e1-remove.sh.in build_remove.sh; do
    sed -e "s#/pscratch/sd/j/josephrb#$B#g" "$HERE/$f" > "$T/case/pkg/$f"
  done
}
list() { bash "$T/case/pkg/e1-list.sh" > "$T/case/listing.txt" 2> "$T/case/list.err"; }
build() { (cd "$T/case/pkg" && bash build_remove.sh "$T/case/listing.txt") > "$T/case/build.out" 2>&1; }
remove() { bash "$T/case/pkg/e1-remove.sh" 2>&1; }

setup; list; build
out=$(remove); rc=$?
check "approved listing: removes the 4 omnifile copies first, then the 3 roots" 0 $rc "omnifile copies removed: 4" "$out"
first=$(printf '%s\n' "$out" | grep -n -E '^rm .*runEventLoopOmniFold' | head -1 | cut -d: -f1)
root1=$(printf '%s\n' "$out" | grep -n '^removed ' | head -1 | cut -d: -f1)
[ -n "$first" ] && [ -n "$root1" ] && [ "$first" -lt "$root1" ] && echo "ok   omnifile copies come before any root" || { echo "FAIL ordering"; fails=$((fails + 1)); }
[ ! -e "$P0" ] && [ ! -e "$F4" ] && [ ! -e "$D2" ] && [ -d "$B" ] && echo "ok   all three roots gone, their parent kept" || { echo "FAIL roots"; fails=$((fails + 1)); }
grep -q 'lat_1A.npz' <<< "$(printf '%s' "$out" | grep '^rm ')" && { echo "FAIL a non-omnifile was removed in step 3"; fails=$((fails + 1)); } || echo "ok   step 3 removes only omnifile copies"

setup; list; build; printf 'new' > "$F4/run/late.txt"
out=$(remove); rc=$?
check "a file added after the listing: refused, nothing removed" 2 $rc "not the approved one" "$out"
[ -e "$P0/run/staged/abcdef0123456789-runEventLoopOmniFold_RDX_1A.root" ] && echo "ok   nothing removed after a refusal" || { echo "FAIL removal after refusal"; fails=$((fails + 1)); }

setup; ln -s /etc "$D2/run/link"; list; build
out=$(remove); rc=$?
check "a symlink outside clone/ in the approved listing: refused" 2 $rc "a symlink outside" "$out"

setup; rm "$F4/clone/$(head -1 "$T/links.txt")"; list; build
out=$(remove); rc=$?
check "a clone missing one of S's symlinks: refused" 2 $rc "are not the 241 committed at S" "$out"

setup; ln -s target "$P0/clone/extra-link"; list; build
out=$(remove); rc=$?
check "a clone with an extra symlink: refused" 2 $rc "are not the 241 committed at S" "$out"

setup; list; build
out=$(SACCT_OUT='5|rpd_d2s0|RUNNING\n' remove); rc=$?
check "an unended rpd* job: refused" 2 $rc "an rpd* job is unended" "$out"

setup; list; build
out=$(HOSTNAME_STUB=nid001234 remove); rc=$?
check "not a login node: refused" 2 $rc "not a login node" "$out"

setup; rm -rf "$D2"; list; build
out=$(remove); rc=$?
check "a missing root (ROOT-NOT-A-DIRECTORY in the listing): refused" 2 $rc "a root is not a directory" "$out"
[ -e "$P0" ] && echo "ok   the other roots stay" || { echo "FAIL other roots removed"; fails=$((fails + 1)); }

setup; list
printf 'f 1 %s/rpd-reco-flux4-20261126/x\n== summary\nlisting_sha256 0000\n' "$B" > "$T/case/listing.txt"
out=$(cd "$T/case/pkg" && bash build_remove.sh "$T/case/listing.txt" 2>&1); rc=$?
check "build_remove refuses a listing whose sha line does not match its lines" 2 $rc "differs from its lines" "$out"

echo "E1-CLEANUP-TESTS :: $( [ "$fails" -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
[ "$fails" -eq 0 ]
