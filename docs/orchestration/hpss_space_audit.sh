#!/bin/bash
#
# HPSS SPACE AUDIT -- READ-ONLY. Produces the ingredients for an allocation-overage decision.
# It does NOT decide anything and it CANNOT delete anything; see the guard below.
#
# WHY THIS EXISTS. Joseph, verbatim, relayed via the mediator: "try to reduce HPSS space when
# possible, I am exceeding my allocation". Reducing space is a DELETION decision and deletions
# on HPSS are irreversible -- on a filesystem whose scratch side is purgeable, an HPSS object
# may be the only surviving copy. So the standing instruction is DELETE NOTHING: every
# candidate is reported, routed to the mediator, and disposed of by Joseph PER ITEM. This
# script is the reporting half and there is deliberately no acting half.
#
# WHY IT IS A COMMITTED SCRIPT RATHER THAN A TYPED COMMAND. BEN-084(B)/BEN-097: an audit
# retyped from memory at the prompt has already produced a bogus 56-item backlog in this
# campaign by reading the wrong directory, and the literal correct command was in the prompt
# at the time. A committed script is the structural fix -- it is reviewable, diffable, and
# its defects are found once.
#
# ---------------------------------------------------------------------------------------
# HONESTY BOUND -- READ THIS BEFORE TRUSTING ANY NUMBER IT PRINTS.
#
# This script was written on 2026-08-12 with NO CLUSTER ACCESS: the NERSC sshproxy
# certificate expired 2026-08-12T11:58:50Z and renewal needs Joseph (password + MFA).
# So the hsi half of this script is UNRUN and UNVERIFIED. Consequences, by design:
#
#   * Every hsi call prints its RAW OUTPUT to the log in addition to anything parsed from
#     it. If a parse is wrong, the raw text is there to contradict it. A parser I could not
#     test must not be the only witness to its own output.
#   * Commands whose availability I could not confirm (`du`, `lsquota`, `hashlist`) are
#     ATTEMPTED IN SEQUENCE and the script records WHICH ONE WORKED rather than assuming.
#   * The self-test (`--self-test`) covers the safety guard ONLY -- that part runs locally
#     and IS verified. It says nothing about whether the audit's numbers are right.
#
# Do not promote anything this prints past ASSUMED until a human has read the raw output.
# ---------------------------------------------------------------------------------------
#
# THE DENOMINATOR IS THE POINT. Nobody in this loop knows the allocation figure. The mediator
# reasoned about a 0.322 TB copy for a full day with no idea whether that was 3% or 30% of
# budget, and a "reduce space" instruction cannot be prioritised without it. If no hsi command
# yields a quota, that is a REPORTED FAILURE, not a blank -- the figure then has to come from
# the NERSC Iris portal, which only Joseph can read.
#
# NEGATIVE RESULTS HERE CAN BE VACUOUS, AND THE SCRIPT SAYS SO. Digest-based duplicate
# detection only works on objects that HAVE a stored digest. The 240 P3F-PET objects and the
# 36 quoted products got `hsi hashcreate`, so they do. `backups` has never been measured at
# all and probably has none. "0 duplicates found" across objects with no digests means "no
# digests to compare", NOT "no duplicates" -- the same vacuous-pass shape as a gate over zero
# files (BEN-186 family). So the duplicate section prints its DENOMINATOR: how many objects
# carried a comparable digest out of how many were seen.
#
# NAME MATCHING IS WRONG FOR THIS SET SPECIFICALLY. The quoted set contains FIVE basename
# collisions across ten files, every pair `X/` vs `X/corrected/`, differing by ~2 KB with
# DISTINCT md5s. They are not duplicates. A basename-based dedup would report five phantom
# wins and propose deleting the corrected products of a campaign whose entire story is which
# products are corrected. Digest only.
#
# USAGE
#   ./hpss_space_audit.sh --self-test          # local, no cluster, verifies the guard
#   ./hpss_space_audit.sh --out FILE           # the audit; needs a live NERSC cert
#   sbatch --qos=xfer ... hpss_space_audit.sh  # optional; login-node hsi is fine for metadata
#
# Redirect the whole stream to a file and filter READS of it. Never pipe this through
# tail/head -- truncating at write time destroys the evidence and buys a second run (BEN-026,
# done twice in one day).
#
set -uo pipefail

# ======================================================================================
# THE SAFETY GUARD. This is the only part of this script that is verified.
#
# It is fail-closed and it sits ON THE CALL PATH: every hsi invocation goes through hsi_ro(),
# which calls assert_readonly() before exec. A guard that exists but is not on the path is a
# guard that passes -- that failure has already shipped in this campaign twice (a substring
# lane match, and a `--lane ""` short-circuit that skipped the check it was testing).
#
# MATCHING IS WHOLE-TOKEN, NEVER SUBSTRING. `_lane_key`'s bug was `"c" in "b -- uncertainty
# construction"` passing lane C on lane B's row. Here the same bug would refuse
# `ls -l /a/format/b` because "format" contains "rm", and -- far worse -- a naive check could
# be talked out of whole-token matching to fix that false refusal, which is how a false
# refusal becomes a false pass. Negative controls for exactly this are in the self-test.
# ======================================================================================

# Mutating hsi/HPSS verbs. Anything not on the allow-list is refused, so this list being
# incomplete is safe; the allow-list is the authority.
READONLY_VERBS="ls lsquota quota du df pwd cd hashlist status version out end lscos"

assert_readonly() {
  local cmd="$1"

  # STEP 1 -- refuse constructs a read-only audit never needs and that defeat clause parsing.
  # Fail-closed on the CONSTRUCT rather than trying to parse inside it: command substitution
  # can smuggle any verb past a clause split, and `>` is a write by definition.
  case "$cmd" in
    *'$('*|*'`'*|*'>'*|*'<'*)
      echo "REFUSED: command substitution or redirection is not permitted in an audit command" >&2
      echo "  command: $cmd" >&2
      return 1 ;;
  esac

  # STEP 2 -- MATCH THE GRAMMAR. hsi's grammar is `verb [flags] [operands]`, clauses separated
  # by `;` `|` `&`. So the verb is the FIRST NON-FLAG TOKEN OF EACH CLAUSE, and operands are
  # never verbs. Checking every token instead (the first version of this function) refused
  # `du -s backups` because the bare directory name `backups` has no slash and therefore
  # looked like a verb -- a false refusal whose obvious "fix" is to stop checking tokens that
  # resemble operands, which is precisely how a false refusal turns into a false pass.
  # Clause-splitting keeps the hidden-verb case closed: `ls -l a; rm b` has TWO clauses and
  # the second one's verb is `rm`.
  local clauses clause tok verb checked=0
  clauses=$(printf '%s' "$cmd" | tr ';|&' '\n')

  local IFS_SAVE="$IFS"
  while IFS= read -r clause; do
    verb=""
    for tok in $clause; do
      case "$tok" in
        -*) continue ;;   # flags are not verbs
        '') continue ;;
      esac
      verb="$tok"; break
    done
    # An empty clause (e.g. trailing `;`) contributes nothing and is not an error.
    [ -z "$verb" ] && continue
    checked=$((checked+1))
    if ! printf '%s\n' $READONLY_VERBS | grep -qxF -- "$verb"; then
      echo "REFUSED: verb '$verb' is not on the read-only allow-list" >&2
      echo "  command: $cmd" >&2
      IFS="$IFS_SAVE"
      return 1
    fi
  done <<EOF
$clauses
EOF
  IFS="$IFS_SAVE"

  if [ "$checked" -eq 0 ]; then
    echo "REFUSED: no recognisable read-only verb in hsi command" >&2
    echo "  command: $cmd" >&2
    return 1
  fi
  return 0
}

# ======================================================================================
# SELF-TEST -- local, no cluster. Verifies the guard, and NOTHING ELSE.
# ======================================================================================
self_test() {
  local pass=0 fail=0
  _expect_ok()  { if assert_readonly "$1" 2>/dev/null; then pass=$((pass+1)); else echo "FAIL(should allow): $1"; fail=$((fail+1)); fi; }
  _expect_no()  { if assert_readonly "$1" 2>/dev/null; then echo "FAIL(should refuse): $1"; fail=$((fail+1)); else pass=$((pass+1)); fi; }

  # --- allowed: the audit's own vocabulary
  _expect_ok  "ls -1"
  _expect_ok  "ls -l /home/j/josephrb"
  _expect_ok  "ls -lR mnv-quoted-products-20260812"
  _expect_ok  "du -s backups"
  _expect_ok  "lsquota"
  _expect_ok  "hashlist mnv-p3f-pet-fullevent-final"
  _expect_ok  "ls -l a; ls -l b"

  # --- refused: every mutating verb the audit must never emit
  _expect_no  "rm foo"
  _expect_no  "rmdir foo"
  _expect_no  "delete foo"
  _expect_no  "put a : b"
  _expect_no  "cput a : b"
  _expect_no  "get a : b"
  _expect_no  "mv a b"
  _expect_no  "rename a b"
  _expect_no  "mkdir -p x"
  _expect_no  "chmod 700 x"
  _expect_no  "chown me x"
  _expect_no  "hashcreate x"
  _expect_no  "hashdelete x"
  _expect_no  "trash x"
  _expect_no  "touch x"

  # --- refused: a mutating verb hidden after a separator. This is the case a
  #     first-token-only check would pass, and it is the reason the guard checks every token.
  _expect_no  "ls -l a; rm b"
  _expect_no  "ls -l a | rm b"
  _expect_no  "ls -l a && delete b"
  _expect_no  "du -s x ; hashdelete y"

  # --- NEGATIVE CONTROLS: paths that CONTAIN a mutating verb as a substring and must still
  #     be allowed. If these fail, someone replaced whole-token matching with `case *rm*`,
  #     and the next edit to "fix" them is what reintroduces the false pass.
  _expect_ok  "ls -l /pscratch/format/x"          # 'format' contains rm
  _expect_ok  "ls -l /a/put_files/b"              # contains put
  _expect_ok  "ls -l /a/removed_backups/b"        # contains rm AND mv
  _expect_ok  "ls -l /a/b.mv"                     # extension looks like a verb
  _expect_ok  "du -s mnv-p3f-pet-fullevent-final" # contains 'et', 'in', harmless
  _expect_ok  "ls -l /a/chmod_notes/b"            # contains chmod
  # Bare operands that are not paths: the case the first version of this guard got WRONG.
  _expect_ok  "du -s backups"
  _expect_ok  "ls -lR mnv-quoted-products-20260812"
  _expect_ok  "hashlist mnv-p3f-pet-fullevent-final"
  # An operand that IS spelled like a mutating verb. Under grammar matching the verb is `ls`,
  # so listing a file named `rm` is allowed -- it reads, it does not delete.
  _expect_ok  "ls -l rm"
  _expect_ok  "ls -l delete"

  # --- refused: constructs that defeat clause parsing, refused as constructs
  _expect_no  'ls -l $(rm x)'
  _expect_no  'ls -l `rm x`'
  _expect_no  "ls -l a > /somewhere"
  _expect_no  "ls -l a < /somewhere"

  # --- refused: empty / verbless, so a bug that builds an empty command cannot slip through
  _expect_no  ""
  _expect_no  "-l -R"
  _expect_no  "/some/path/only"

  # ------------------------------------------------------------------------------------
  # DIGEST-PARSE TESTS, against a fixture carrying BOTH hsi output formats plus the exact
  # real-world lines that broke version 1. The fixture includes a known duplicate pair, a
  # unique object, and NEGATIVE CONTROLS -- header noise, a short non-digest hex, and a
  # line whose second field merely resembles a digest label.
  # ------------------------------------------------------------------------------------
  local fixture cov dup
  fixture=$(cat <<'FIX'
/home/j/josephrb:
5e89461934bf030f0c4881f8dd0a2779 md5 /home/j/josephrb/mnv-p3f-smoketest/smoketest.json [hsi]
5e89461934bf030f0c4881f8dd0a2779 md5 /home/j/josephrb/mnv-p3f-pet-fullevent-final/P3F_PET_receipt_BeamAngleX_0_1A.json [hsi]
c3aa17d6714abed95f38fd73ef6d0a03 md5 /home/j/josephrb/mnv-quoted-products-20260812/genie/gibuu.root [hsi]
96c912c71c459fc88507ff27766c4c22 (md5) /home/j/josephrb/legacy/hashcreate_format.root
deadbeef md5 /home/j/josephrb/too-short-to-be-a-digest.root [hsi]
notahash md5sum /home/j/josephrb/label-lookalike.root
-----------------------
FIX
)
  cov=$(printf '%s\n' "$fixture" | parse_digest_coverage)
  if [ "$cov" = "objects_with_stored_digest=4" ]; then
    pass=$((pass+1))
  else
    echo "FAIL(digest coverage): expected 4, got '$cov'"; fail=$((fail+1))
  fi

  dup=$(printf '%s\n' "$fixture" | parse_digest_duplicates)
  if printf '%s' "$dup" | grep -q 'distinct_digests_repeated=1'; then
    pass=$((pass+1))
  else
    echo "FAIL(digest duplicates): expected 1 repeated digest, got '$dup'"; fail=$((fail+1))
  fi
  if printf '%s' "$dup" | grep -q '2 x 5e89461934bf030f0c4881f8dd0a2779'; then
    pass=$((pass+1))
  else
    echo "FAIL(digest duplicates): did not identify the smoketest/receipt pair"; fail=$((fail+1))
  fi
  # A parser that matched ONLY `(md5)` -- version 1's bug -- would score 1 on coverage and 0
  # duplicates against this fixture. That is what these three checks exist to catch.
  if printf '%s\n' "$fixture" | parse_digest_coverage | grep -q 'objects_with_stored_digest=1'; then
    echo "FAIL(regression): parser is matching only the hashcreate format again"; fail=$((fail+1))
  else
    pass=$((pass+1))
  fi

  echo "self-test: ${pass} passed, ${fail} failed"
  [ "$fail" -eq 0 ] || return 1
  return 0
}

# ======================================================================================
# DIGEST PARSING -- extracted into functions so it can be TESTED, because the first version
# of it was WRONG and failed in the worst available direction.
#
# WHAT HAPPENED, recorded here because the fix is uninteresting and the failure mode is not:
# the first version matched `(md5)` -- the PARENTHESISED form that `hsi hashcreate` prints.
# `hsi hashlist` prints a DIFFERENT format with no parentheses:
#
#     hashcreate:  5e894619...2779 (md5) /home/j/josephrb/x.json
#     hashlist:    5e894619...2779 md5 /home/j/josephrb/x.json [hsi]
#
# So on real output the coverage count came back `objects_with_stored_digest=0` and the
# duplicate list came back EMPTY. Read at face value that says "HPSS stores no digests, so
# there is nothing to compare" -- when the truth was 277 of 279 objects carry an md5 and
# there is exactly one duplicate pair. The correct parse found it in seconds from the SAME
# saved output.
#
# THE POINT, AND IT IS WHY THIS COMMENT IS LONG: section 4 exists specifically to stop a
# vacuous negative by printing its denominator. The denominator was computed by the broken
# parser, so THE SAFEGUARD FAILED IN THE SAME DIRECTION AS THE THING IT GUARDED -- it
# reported the one value ("0 digests") that makes an empty duplicate list look expected.
# A denominator is only a safeguard if it is derived independently of what it certifies.
# Two properties saved this: the raw output was dumped alongside the parse, so the parse
# could be contradicted without re-running hsi; and the parse is now under test below.
# ======================================================================================

# Count objects carrying a stored digest. Accepts BOTH hsi formats. Reads stdin.
parse_digest_coverage() {
  awk '
    # hashlist:   <hex> md5 /path [hsi]        -> $2 == "md5"
    # hashcreate: <hex> (md5) /path            -> $2 == "(md5)"
    ($2=="md5" || $2=="(md5)" || $2=="sha256" || $2=="(sha256)") && $1 ~ /^[0-9a-fA-F]{32,64}$/ { n++ }
    END { printf "objects_with_stored_digest=%d\n", n+0 }'
}

# Emit repeated digests as duplicate CANDIDATES. Accepts both formats. Reads stdin.
parse_digest_duplicates() {
  awk '
    ($2=="md5" || $2=="(md5)" || $2=="sha256" || $2=="(sha256)") && $1 ~ /^[0-9a-fA-F]{32,64}$/ {
      c[$1]++; p[$1] = p[$1] "\n      " $3
    }
    END {
      d=0
      for (k in c) if (c[k] > 1) { d++; printf "%d x %s%s\n", c[k], k, p[k] }
      printf "distinct_digests_repeated=%d\n", d
    }'
}

# ======================================================================================
# hsi wrapper -- the ONLY way this script talks to HPSS.
# ======================================================================================
HSI_CALLS=0
hsi_ro() {
  local cmd="$1"
  assert_readonly "$cmd" || return 3
  HSI_CALLS=$((HSI_CALLS+1))
  # -q quiet, no interactive prompt. stderr folded in because hsi reports on both.
  hsi -q "$cmd" 2>&1
}

# Try a list of candidate commands; print raw output of each attempt and report which
# succeeded. Used where I could not confirm the command exists on NERSC's hsi build.
try_candidates() {
  local label="$1"; shift
  echo "### ${label}"
  local c out rc
  for c in "$@"; do
    echo "--- attempt: hsi -q \"${c}\""
    out=$(hsi_ro "$c"); rc=$?
    echo "$out"
    echo "--- exit=${rc}"
    if [ "$rc" -eq 0 ] && [ -n "${out//[[:space:]]/}" ]; then
      echo "### ${label}: SUCCEEDED with: ${c}"
      return 0
    fi
  done
  echo "### ${label}: ALL CANDIDATES FAILED -- this figure is UNKNOWN, not zero."
  return 1
}

# ======================================================================================
main_audit() {
  echo "# HPSS SPACE AUDIT -- read-only"
  echo "# generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# host: $(hostname)"
  echo "# git: $(git -C "$(dirname "$0")/../.." rev-parse --short HEAD 2>/dev/null || echo unknown)"
  echo "# guard: every hsi call passes assert_readonly(); mutating verbs are impossible here."
  echo

  echo "=== 0. GUARD SELF-TEST (must pass before any audit output is trusted) ==="
  self_test || { echo "FATAL: guard self-test failed; refusing to run the audit."; return 2; }
  echo

  echo "=== 1. THE DENOMINATOR: allocation and total residency ==="
  echo "# If this section fails, the overage cannot be quantified from the cluster and the"
  echo "# figure must come from the NERSC Iris portal (https://iris.nersc.gov) -- a Joseph action."
  try_candidates "quota" "lsquota" "quota" "lsquota -h"
  echo
  try_candidates "total residency at HPSS home" "du -s ." "du -s"
  echo

  echo "=== 2. SIZE BY TOP-LEVEL DIRECTORY -- counts do not reduce an allocation ==="
  echo "# Discovered, not hardcoded: previous reports gave COUNTS only, and 'backups' has"
  echo "# never been measured at all, which makes it the most likely home of the overage."
  echo "--- top-level listing (raw)"
  hsi_ro "ls -l"
  echo
  local dirs d
  dirs=$(hsi_ro "ls -1" | awk '/[^[:space:]]/ {print $NF}' | grep -vE '^(\.|\.\.)$' || true)
  echo "--- discovered top-level entries:"
  printf '%s\n' "$dirs"
  echo
  for d in $dirs; do
    echo "--- du -s ${d}"
    hsi_ro "du -s ${d}"
  done
  echo

  echo "=== 3. CONCENTRATION -- report this BEFORE enumerating everything ==="
  echo "# 71% of the 0.322 TB copy was four files. If residency is similarly concentrated,"
  echo "# this is a decision about a handful of objects, not a 19,570-file review."
  echo "--- full recursive listing, sizes included (RAW; sorted extract follows)"
  local listing
  listing=$(hsi_ro "ls -lR")
  echo "$listing"
  echo
  echo "--- largest objects (parsed from the above; if this looks wrong, the raw text above wins)"
  # hsi `ls -l` columns vary by build, so key on 'a numeric field followed by a path-like
  # final field' rather than a fixed column index, and print what was matched.
  printf '%s\n' "$listing" \
    | awk 'NF>=5 { for(i=1;i<=NF;i++) if ($i ~ /^[0-9]{6,}$/) { print $i"\t"$NF; break } }' \
    | sort -rn | head -40
  echo
  echo "--- byte total from the same parse (compare against section 1's du; they must agree)"
  printf '%s\n' "$listing" \
    | awk 'NF>=5 { for(i=1;i<=NF;i++) if ($i ~ /^[0-9]+$/ && length($i)>=6) { s+=$i; n++; break } } END { printf "objects_parsed=%d bytes=%d TB=%.4f\n", n, s, s/1e12 }'
  echo

  echo "=== 4. TRUE DUPLICATES BY DIGEST -- with its denominator, because a negative here can be vacuous ==="
  echo "# Name matching is WRONG for this set: five basename collisions in the quoted products"
  echo "# are corrected-vs-uncorrected pairs with distinct md5s. Digest only."
  echo "# hashlist returns STORED digests; it does not read bytes and costs no tape time."
  local hl
  hl=$(hsi_ro "hashlist -R ." || true)
  echo "--- hashlist raw"
  echo "$hl"
  echo
  echo "--- digest coverage (THE DENOMINATOR)"
  printf '%s\n' "$hl" | parse_digest_coverage
  echo "objects_seen_by_hashlist=$(printf '%s\n' "$hl" | grep -c '\[hsi\]' || true)"
  echo "# Compare BOTH against section 1's file count from du. Objects with NO stored digest"
  echo "# are NOT covered by the duplicate scan below and cannot be declared unique."
  echo "# If coverage is 0, SUSPECT THE PARSER BEFORE BELIEVING IT -- that exact reading was"
  echo "# wrong once, on output that had 277 digests in it."
  echo
  echo "--- repeated digests (duplicate CANDIDATES -- flag only, never act)"
  printf '%s\n' "$hl" | parse_digest_duplicates
  echo

  echo "=== 5. SUPERSEDED-PRODUCT CANDIDATES -- FLAGGED, NOT ACTED ON ==="
  echo "# Deliberately not computed here. Deciding a product is superseded needs the"
  echo "# VALIDATION_LEDGER and the analysis note, which are LOCAL artifacts, and it is a"
  echo "# physics-provenance judgement rather than a storage one. Routed to the owning lane."
  echo

  echo "=== SUMMARY ==="
  echo "hsi_calls_made=${HSI_CALLS}"
  echo "mutating_calls_made=0  (structurally impossible: assert_readonly gates hsi_ro)"
  echo "DELETIONS PERFORMED: none. This script has no delete path."
  echo "NEXT: raw output above goes to the mediator; Joseph disposes per item."
}

# ======================================================================================
OUT=""
MODE="audit"
PARSE_FILE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --self-test) MODE="selftest"; shift ;;
    --out) OUT="${2:-}"; shift 2 ;;
    # Re-run the digest parse over a PREVIOUSLY SAVED audit file. No cluster, no HPSS, no
    # tape time. This exists because the parse was wrong once and the raw output was the only
    # reason that was recoverable without a second run -- filter READS of the evidence rather
    # than re-running the thing that produced it (BEN-026).
    --parse-file) MODE="parsefile"; PARSE_FILE="${2:-}"; shift 2 ;;
    -h|--help) sed -n '1,70p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ "$MODE" = "selftest" ]; then
  self_test; exit $?
fi

if [ "$MODE" = "parsefile" ]; then
  [ -r "$PARSE_FILE" ] || { echo "FATAL: cannot read $PARSE_FILE" >&2; exit 2; }
  echo "# digest parse re-run over saved evidence: $PARSE_FILE"
  echo "# parser verified by --self-test; this run touched HPSS zero times."
  parse_digest_coverage    < "$PARSE_FILE"
  echo "objects_seen_by_hashlist=$(grep -c '\[hsi\]' "$PARSE_FILE" || true)"
  echo "--- repeated digests (duplicate CANDIDATES -- flag only, never act)"
  parse_digest_duplicates  < "$PARSE_FILE"
  exit 0
fi

if ! command -v hsi >/dev/null 2>&1; then
  echo "FATAL: hsi not found. This script must run on a NERSC login/xfer node." >&2
  echo "  Local machines have no HPSS client; there is no local fallback." >&2
  exit 2
fi

if [ -n "$OUT" ]; then
  main_audit > "$OUT" 2>&1
  rc=$?
  echo "audit written to: $OUT (exit=$rc)"
  echo "Read it with grep/sed. Do NOT pipe the run through tail/head (BEN-026)."
  exit $rc
else
  main_audit
fi
