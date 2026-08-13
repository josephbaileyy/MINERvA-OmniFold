#!/bin/bash
# Snapshot the code an array will run, so members cannot diverge mid-flight.
#
# WHY THIS EXISTS, measured rather than supposed. Gate 6 array 56834281 ran FIVE members on TWO code
# identities: members 1-4 used driver sha 5fda80df..., member 5 used 91144bee..., because
# annealed_estimator.py and train_fullevent_nominal.py were copied onto the cluster tree at
# 04:52:08Z / 04:52:10Z -- between member 4's start (04:46:03Z) and member 5's (05:06:03Z). Detail:
# docs/orchestration/state/gate6-member-code-identity-split-56834281.json.
#
# The launcher LOGGED the driver sha and FAIL-CLOSED ONLY ON THE TARGET SHA. So the ensemble's own
# "members must be one thing" guard covered the DATA and left the CODE free, which is the wrong way
# round for an ensemble: it permits the one difference members may not have while refusing one they
# would never make. The split was detectable after the fact and not preventable at submit.
#
# TWO REASONS THIS SNAPSHOTS RATHER THAN PINS. A sha guard per member would only DETECT the race, and
# it would detect it one member at a time, after the earlier ones had already run. And the cluster
# checkout is a git repo on `main` with a github remote, 309 commits behind only because nobody has
# pulled -- so a single `git pull` moves every file at once. Copying the code out from under the
# array's feet is the failure mode; execing from a private copy removes it instead of reporting it.
#
# A pin would also have to know how many files the code lives in, and it does not: the annealed
# estimator moved out of the driver into a SECOND file on 2026-08-13, so a one-file driver pin now
# misses the estimator class entirely.
#
# USAGE
#   snapshot_array_code.sh create <snapdir> <file> [<file> ...]
#       Copies each file into <snapdir>/code/ and writes <snapdir>/code/MANIFEST.json with each
#       file's sha256, size and basename. Refuses to overwrite an existing snapshot.
#   snapshot_array_code.sh verify <snapdir>
#       Re-hashes every file in the snapshot against its manifest. Exit 0 only if all match.
#       This is what a member runs before importing anything.
#
# Members then exec from <snapdir>/code/, so a mid-array copy or pull to the repo tree cannot reach
# them. `verify` still exists because a snapshot on a shared filesystem is not immutable either --
# it is merely not the path anyone edits.
set -euo pipefail

die() { echo "[snapshot][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }

MODE="${1:?usage: $0 create <snapdir> <file>... | verify <snapdir>}"
SNAPDIR="${2:?snapshot directory required}"
CODE="${SNAPDIR%/}/code"
MANIFEST="${CODE}/MANIFEST.json"

case "$MODE" in
create)
  shift 2
  [[ $# -ge 1 ]] || die "create needs at least one file"
  [[ -e "$MANIFEST" ]] && die "snapshot already exists at ${MANIFEST}; refusing to overwrite -- a
    second create would silently re-point a running array at different code" 4
  mkdir -p "$CODE"

  # Fail closed on a basename collision BEFORE copying anything: two files with the same basename
  # would land on top of each other and the manifest would claim both. Same class as the HPSS
  # flat-destination collision that would have destroyed five corrected products.
  n_in=$#
  n_base=$(for f in "$@"; do basename "$f"; done | sort -u | wc -l | tr -d ' ')
  [[ "$n_in" -eq "$n_base" ]] || die "$n_in inputs share only $n_base distinct basenames; a flat
    snapshot would overwrite one with another" 5

  tmp="${MANIFEST}.tmp.$$"
  printf '{\n  "created_utc": "%s",\n  "files": [\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$tmp"
  i=0
  for f in "$@"; do
    [[ -f "$f" ]] || die "not a file: $f"
    b=$(basename "$f"); s=$(sha_of "$f"); z=$(wc -c < "$f" | tr -d ' ')
    cp -p "$f" "${CODE}/${b}"
    # Verify the COPY, not the source: cp can short-write on a full filesystem and exit 0 is not
    # a guarantee that the bytes landed.
    c=$(sha_of "${CODE}/${b}")
    [[ "$c" == "$s" ]] || die "copy of $b differs from source ($c != $s)" 6
    [[ $i -gt 0 ]] && printf ',\n' >> "$tmp"
    printf '    {"basename": "%s", "source": "%s", "sha256": "%s", "size": %s}' \
           "$b" "$f" "$s" "$z" >> "$tmp"
    i=$((i+1))
  done
  printf '\n  ],\n  "n_files": %d\n}\n' "$i" >> "$tmp"
  mv "$tmp" "$MANIFEST"          # write-to-temp + rename: a crashed create leaves no manifest
  echo "[snapshot] wrote ${MANIFEST} with ${i} file(s)"
  ;;

verify)
  [[ -f "$MANIFEST" ]] || die "no manifest at ${MANIFEST}; a member must never run without one" 2
  # Parsed with python3 rather than grep/sed: a hand-rolled JSON reader that silently matches
  # nothing is how a verifier passes over an empty set.
  python3 - "$MANIFEST" "$CODE" <<'PY'
import hashlib, json, sys
manifest, code = sys.argv[1], sys.argv[2]
m = json.load(open(manifest))
files = m.get("files") or []
if not files:
    sys.exit("[snapshot][FAIL] manifest lists zero files; refusing to call that verified")
if len(files) != m.get("n_files"):
    sys.exit("[snapshot][FAIL] manifest says n_files=%r but lists %d"
             % (m.get("n_files"), len(files)))
bad = []
for e in files:
    p = "%s/%s" % (code, e["basename"])
    try:
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    except OSError as exc:
        bad.append("%s: %s" % (e["basename"], exc)); continue
    if h != e["sha256"]:
        bad.append("%s: %s != %s" % (e["basename"], h, e["sha256"]))
if bad:
    sys.exit("[snapshot][FAIL] snapshot altered since create:\n  " + "\n  ".join(bad))
print("[snapshot] verified %d file(s) against %s" % (len(files), manifest))
PY
  ;;

*) die "unknown mode ${MODE}; use create or verify" ;;
esac
