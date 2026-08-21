#!/bin/bash
# TESTED RECOVERY ROUTE for the historical negative-weight diagnostic products.
#
# This is the half a `hashverify` cannot supply. `hashverify` recomputes a digest IN PLACE on
# HPSS: it proves the tape copy's bytes are intact, and it proves nothing about whether those
# bytes come back as usable files. RECEIPT-20260820-oi50-hashverify.md says so in its own §5
# -- "no object was restored and re-read end-to-end into a usable file". This script closes
# that, and the receipt it feeds records the run that proves the route works rather than
# describing a route nobody executed.
#
# WHAT IT DOES, in the order that makes each step's failure unambiguous:
#   1. `hsi get` every archive object into a FRESH destination (refuses a non-empty one --
#      extracting over an existing tree is how a stale file passes as a recovered one).
#   2. sha256 each retrieved tar against the committed manifest. Fail here = transfer/tape.
#   3. Extract. Fail here = the tar itself.
#   4. Re-hash EVERY extracted member against the manifest's per-file sha256.
#   5. Coverage as a PATH-SET DIFF in BOTH directions -- extracted-not-in-manifest and
#      manifest-not-extracted. A count match is not a set match: "247 of something" is not
#      "247 of the right thing".
#   6. Usability, not just byte-identity: every recovered ROOT is opened and its key list
#      read. Byte-identity to a digest taken off pscratch would inherit any corruption the
#      original already had, so the file is exercised as a ROOT file.
#
# NOTHING IS WRITTEN INTO THE REPO TREE and nothing is written back to HPSS. The destination
# is created by this script and is the only thing it touches.
#
# ROOT ENVIRONMENT: `import ROOT` SEGFAULTS on a bare Perlmutter login shell (cling include
# paths). setup_salloc_env.sh at the repo root must be sourced, and this session's sandboxed
# $HOME breaks the default conda-prefix resolution, so ROOT628_PREFIX is exported first. If
# ROOT still cannot be imported the script reports step 6 as SKIPPED with its reason and
# exits non-zero -- it does not silently downgrade to a magic-bytes check and call that a
# usability proof.
#
# Usage:
#   bash hpss_recover_negweight.sh <manifest.json> <fresh-destination-dir> [repo-root]
# Exit 0 only if steps 1-6 all pass. Any other status means the route is NOT proven.
set -eo pipefail

MANIFEST="${1:?usage: hpss_recover_negweight.sh <manifest.json> <dest-dir> [repo-root]}"
DEST="${2:?usage: hpss_recover_negweight.sh <manifest.json> <dest-dir> [repo-root]}"
REPO_ROOT="${3:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}"

[ -f "$MANIFEST" ] || { echo "[FATAL] manifest not readable: $MANIFEST" >&2; exit 2; }
if [ -e "$DEST" ] && [ -n "$(ls -A "$DEST" 2>/dev/null)" ]; then
  echo "[FATAL] destination $DEST exists and is not empty." >&2
  echo "[FATAL] Refusing: extracting over an existing tree lets a file that was already" >&2
  echo "[FATAL] there pass as one this run recovered." >&2
  exit 2
fi
mkdir -p "$DEST/objects" "$DEST/tree"

HPSS_DIR=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["hpss_dir"])' "$MANIFEST")
echo "[info] manifest  : $MANIFEST"
echo "[info] hpss_dir  : $HPSS_DIR"
echo "[info] dest      : $DEST"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$DEST/started.marker"

# ---- 1. retrieve -----------------------------------------------------------------------
mapfile -t OBJECTS < <(python3 -c '
import json,sys
m=json.load(open(sys.argv[1]))
for o in m["objects"]: print(o["object"])' "$MANIFEST")
[ "${#OBJECTS[@]}" -gt 0 ] || { echo "[FATAL] manifest lists no objects" >&2; exit 2; }

# set -e already makes a failing get fatal; the explicit test is here so the FAILING
# OBJECT is named. A loop's own status would report only the last iteration.
for obj in "${OBJECTS[@]}"; do
  echo "[get ] $obj"
  if ! hsi -q "get ${DEST}/objects/${obj} : ${HPSS_DIR}/${obj}" 2>&1; then
    echo "[FATAL] hsi get failed for ${obj}" >&2; exit 3
  fi
done
echo "[ok  ] step 1: retrieved ${#OBJECTS[@]} object(s)"

# ---- 2. object digests vs the manifest --------------------------------------------------
# `set +e` around each checker is NOT cosmetic. With -e active the checker's own non-zero
# status aborts the script BEFORE the rc is written and BEFORE the diagnostic is printed, so a
# real failure surfaces as a bare exit 1 with an empty step file -- measured, in the negative
# controls that found this. The rc must be captured, then read.
set +e
python3 - "$MANIFEST" "$DEST/objects" <<'PY' > "$DEST/step2_objects.txt"
import hashlib, json, os, sys
man, d = sys.argv[1], sys.argv[2]
m = json.load(open(man)); bad = 0
for o in m["objects"]:
    p = os.path.join(d, o["object"])
    if not os.path.exists(p):
        print(f"MISSING {o['object']}"); bad += 1; continue
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    size = os.path.getsize(p)
    ok = (h == o["sha256"] and size == o["size"])
    print(f"{'OK     ' if ok else 'MISMATCH'} {o['object']} size={size} sha256={h}")
    bad += 0 if ok else 1
print(f"objects_checked={len(m['objects'])} bad={bad}")
sys.exit(1 if bad else 0)
PY
echo $? > "$DEST/step2.rc"
set -e
[ "$(cat "$DEST/step2.rc")" = "0" ] || { cat "$DEST/step2_objects.txt"; echo "[FATAL] retrieved object digests do not match the manifest." >&2; exit 3; }
echo "[ok  ] step 2: every retrieved object matches its manifest sha256 and size"

# ---- 3. extract -------------------------------------------------------------------------
for obj in "${OBJECTS[@]}"; do
  case "$obj" in
    *.tar) tar -xf "$DEST/objects/$obj" -C "$DEST/tree" ;;
    *)     cp -p "$DEST/objects/$obj" "$DEST/tree/" ;;
  esac
done
echo "[ok  ] step 3: extracted"

# ---- 4 + 5. per-member digests and a two-way path-set diff -----------------------------
set +e
python3 - "$MANIFEST" "$DEST/tree" <<'PY' > "$DEST/step45_members.txt"
import hashlib, json, os, sys
man, tree = sys.argv[1], sys.argv[2]
m = json.load(open(man))
want = {e["path"]: e for e in m["ruled_products"]}
got = set()
for root, _dirs, files in os.walk(tree):
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, tree)
        got.add(rel)
bad = 0
for rel, e in sorted(want.items()):
    p = os.path.join(tree, rel)
    if not os.path.exists(p):
        print(f"MISSING  {rel}"); bad += 1; continue
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    s = os.path.getsize(p)
    if h != e["sha256"] or s != e["size"]:
        print(f"MISMATCH {rel} want {e['sha256']} got {h}"); bad += 1
missing = sorted(set(want) - got)
extra   = sorted(got - set(want))
print(f"\nruled_members_in_manifest={len(want)} recovered_and_matched={len(want)-bad} bad={bad}")
print(f"manifest_not_recovered={len(missing)}")
for x in missing: print(f"  ONLY_IN_MANIFEST {x}")
# `extra` is expected and is not an error: the sidecar tar and LABEL.txt are beside-scope by
# construction. It is PRINTED rather than filtered so the beside-scope set stays visible.
side = {e["path"] for e in m.get("sidecar_products", [])}
unexplained = [x for x in extra if x not in side and x != "LABEL.txt"]
print(f"recovered_beside_scope={len([x for x in extra if x in side or x=='LABEL.txt'])}")
print(f"recovered_unexplained={len(unexplained)}")
for x in unexplained: print(f"  UNEXPLAINED {x}")
sys.exit(1 if (bad or missing or unexplained) else 0)
PY
echo $? > "$DEST/step45.rc"
set -e
[ "$(cat "$DEST/step45.rc")" = "0" ] || { tail -30 "$DEST/step45_members.txt"; echo "[FATAL] member digests or the path-set diff failed." >&2; exit 4; }
echo "[ok  ] steps 4-5: every ruled member recovered, digest-matched, and the path sets agree both ways"

# ---- 6. usability: open every recovered ROOT ------------------------------------------
export ROOT628_PREFIX=${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}
if [ -f "$REPO_ROOT/setup_salloc_env.sh" ]; then
  # env before any -u discipline, and never piped: sourcing this under `set -u` or through
  # a pipe is how the ROOT 6.28 setup has failed here before.
  set +u
  # shellcheck disable=SC1090
  . "$REPO_ROOT/setup_salloc_env.sh" >/dev/null 2>&1 || true
fi
set +e
python3 - "$MANIFEST" "$DEST/tree" <<'PY' > "$DEST/step6_root_open.txt" 2>&1
import json, os, sys
try:
    import ROOT
except Exception as e:
    print(f"SKIPPED: ROOT unimportable: {type(e).__name__}: {e}")
    sys.exit(2)
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kError
man, tree = sys.argv[1], sys.argv[2]
m = json.load(open(man))
bad, keys_total = 0, 0
for e in m["ruled_products"]:
    p = os.path.join(tree, e["path"])
    f = ROOT.TFile.Open(p)
    if not f or f.IsZombie() or f.TestBit(ROOT.TFile.kRecovered):
        print(f"UNUSABLE {e['path']}"); bad += 1
        if f: f.Close()
        continue
    n = len(f.GetListOfKeys())
    if n == 0:
        print(f"NOKEYS   {e['path']}"); bad += 1
    keys_total += n
    f.Close()
print(f"root_files_opened={len(m['ruled_products'])} unusable={bad} total_keys={keys_total}")
sys.exit(1 if bad else 0)
PY
rc6=$?
set -e
echo "$rc6" > "$DEST/step6.rc"
if [ "$rc6" = "2" ]; then
  cat "$DEST/step6_root_open.txt"
  echo "[FATAL] step 6 could not run: ROOT unimportable. The route is NOT proven usable." >&2
  echo "[FATAL] Source setup_salloc_env.sh in an environment that has ROOT 6.28 and re-run." >&2
  exit 6
fi
[ "$rc6" = "0" ] || { tail -20 "$DEST/step6_root_open.txt"; echo "[FATAL] step 6: recovered ROOT files are not usable." >&2; exit 6; }
tail -1 "$DEST/step6_root_open.txt"
echo "[ok  ] step 6: every recovered ROOT opens and carries keys"

date -u '+%Y-%m-%dT%H:%M:%SZ' > "$DEST/finished.marker"
echo
echo "RECOVERY ROUTE PROVEN: steps 1-6 all pass. Evidence under $DEST"
exit 0
