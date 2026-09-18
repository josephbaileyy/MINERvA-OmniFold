#!/bin/bash
# M1: the 5D -> (E_avail, W) projection. THE ONLY MAP THE ONE DEFERRED PUBLICATION CLAIM CAN USE.
#
# THIS SCRIPT CANNOT RUN TODAY AND IS WRITTEN SO THAT IT CANNOT. Every precondition below is a
# REFUSAL, not a warning, because the trunk is not adopted and a runner that merely warned would be
# one careless invocation away from producing a product nobody authorized. It exists now so that the
# eventual authorization is a SUBMISSION rather than new code written under time pressure.
#
# WHAT IT MEASURES:  C_low = M1 C_Z M1^T on the adopted trunk, 42 dense destination cells, paired
#                    with M1 x_5D -- the MARGINALISED central value, not an independently unfolded
#                    2D estimator. Those differ by ~3% by construction and that is not an error.
# WHAT A TERMINAL RESULT CANNOT AUTHORIZE, stated in advance per AGENTS.md next-action discipline:
#                    it does not calibrate a significance; it does not supply support C_Z never had;
#                    it does not make an independently unfolded 4D/3D estimator the marginal of the
#                    5D one; it licenses no other projection and no event-level fit. Producing it is
#                    construction, and construction is not adoption.
#
# SIZING is measured, not guessed. The projection arithmetic was run at the real 10694 -> 42 shape
# on 2026-09-18: build_projection 0.001 s, M C M^T 0.324 s, peak RSS 1.020 GiB with C at 0.852 GiB.
# The wall and memory requested below are margin for the ROOT I/O of a ~900 MB TH2D, which is the
# UNMEASURED leg -- no interpreter available to this campaign locally has ROOT. The pilot recorded
# that a derived sizing was once low by more than an order of magnitude, so the margin is deliberate.
#
#SBATCH --job-name=m1_proj_eavailW
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=16G --time=00:15:00
#SBATCH --output=uq_5d/m1_proj_%j.out --error=uq_5d/m1_proj_%j.err
set -eo pipefail

# NO APOSTROPHES IN ANY MESSAGE BELOW. An apostrophe inside ${VAR:?...} opens a quote that spans
# newlines and silently swallows the NEXT assignments, voiding the guards between. That has happened
# twice in this campaign, once in a Z pilot launcher and once in a validation launcher a day later.
CODE_ROOT="${MNV_CODE_ROOT:?set it to the reviewed deployment tree for this run}"
DATA_ROOT="${MNV_DATA_ROOT:?set it to the data root holding the adopted trunk}"
ADOPTION="${MNV_ADOPTION_RECORD:?set it to the path of the adoption decision record for the trunk}"
SRC_COV="${MNV_SRC_COV:?set it to the adopted 5D covariance ROOT file}"
SRC_HIST="${MNV_SRC_HIST:?set it to the TH2D key inside the adopted covariance}"
SRC_CV="${MNV_SRC_CV:?set it to the 5D central product supplying the reported mask}"
DST_MASK="${MNV_DST_MASK:?set it to declared-dst-cv or receiving-cells, the destination mask choice}"
# The source covariance is selected by PATH, and on the pilot products a path does not identify the
# object: z-cv.npz and z-mean.npz are structurally identical and differ only in this field. Declared
# here, verified by the projector against the file. No default.
EXPECT_VARIANT="${MNV_EXPECT_VARIANT:?set it to the variant the source must declare, or none}"
OUT="${MNV_OUT:?set it to the output path for the projected covariance}"

# ---- REFUSAL 1: THE TRUNK MUST BE ADOPTED, AND ADOPTION IS A RECORD, NOT A FLAG ----------------
# A boolean env var would let anyone assert adoption. This requires a file that a human decision
# produced, and it must SAY it adopts. Construction success is not adoption; a digest is not a
# decision; and this script deliberately cannot be talked into running by an argument.
if [ ! -f "$ADOPTION" ]; then
  echo "REFUSED -- no adoption record at $ADOPTION. The scalar-5D trunk is QUARANTINED until" >&2
  echo "          Joseph adopts it explicitly. M1 must not be produced from a candidate." >&2
  exit 3
fi
# ---- REFUSAL 1a: ADOPTION IS A DECLARATION BOUND TO BYTES, NOT A WORD NEAR A DIGEST ----------
# MEASURED DEFECT, 2026-09-18. The previous pair of checks was `grep -qiE "adopt(ed|s|ion)"` AND a
# loose `grep -qF "$sha"`. Measured against this repo, THREE documents that adopt nothing passed
# BOTH for the z-cv digest: PLAN-20260918, NAVIGATION-20260917 -- a pure ROUTING document -- and
# DECISION-PACKET-20260918, whose own line reads "A record that authorizes nothing in particular
# authorizes everything". The conjunction is weak for a structural reason: a RECEIPT naturally
# contains the digest, and any document DISCUSSING adoption naturally contains the word, so two
# loose searches over one file are not a decision about it.
#
# Requiring both on ONE line is still not sufficient -- VERDICT-20260821 already co-locates
# "adopt segment" with a 64-hex digest in running prose. So the record must carry a DECLARATIVE
# SENTINEL that prose does not emit by accident, and the digest must be ON that line:
#
#     ADOPTS-SHA256: <64 hex of the covariance being projected>
#
# Zero documents in the repo match it today, which is correct: nothing is adopted yet.
_SRC_SHA="$(sha256sum "$SRC_COV" | awk '{print $1}')"
_SENT="$(grep -nE '^[[:space:]]*[*`>_ -]*ADOPTS-SHA256[*`_]*[[:space:]]*:' "$ADOPTION" || true)"
if [ -z "$_SENT" ]; then
  echo "REFUSED -- $ADOPTION does not state an adoption. A record that does not adopt is not one." >&2
  echo "          It carries no ADOPTS-SHA256: line. A keyword match is not identity: a record" >&2
  echo "          that does not name the bytes it adopts would adopt every candidate equally." >&2
  echo "          measured: $_SRC_SHA" >&2
  echo "          declare:  ADOPTS-SHA256: $_SRC_SHA" >&2
  exit 3
fi
# A sentinel that negates or defers itself is not an adoption. The repo idiom for refusing is
# literally "adopts nothing", and the exception is held "as drafted, not executed" -- so a line
# carrying either shape must not be read as a decision.
if printf '%s\n' "$_SENT" | grep -qiE 'nothing|never|withheld|[[:space:]]not[[:space:]]|pending|proposed|draft|held'; then
  echo "REFUSED -- the ADOPTS-SHA256 line in $ADOPTION is negated, provisional or held:" >&2
  printf '%s\n' "$_SENT" | sed 's/^/            /' >&2
  exit 3
fi
if ! printf '%s\n' "$_SENT" | grep -oE '[0-9a-f]{64}' | grep -qxF "$_SRC_SHA"; then
  echo "REFUSED -- $ADOPTION does not name the measured digest of $SRC_COV" >&2
  echo "          measured: $_SRC_SHA" >&2
  echo "          declared: $(printf '%s\n' "$_SENT" | grep -oE '[0-9a-f]{64}' | tr '\n' ' ')" >&2
  echo "          A keyword match is not identity: a record that does not name the bytes it" >&2
  echo "          adopts would adopt every candidate equally." >&2
  exit 3
fi
echo "[adoption] record names the measured source digest ${_SRC_SHA:0:16}..."

# ---- REFUSAL 2: THE PROJECTOR MUST BE INSTRUMENTED BEFORE IT PRODUCES ANYTHING -----------------
# A digest retrofitted onto an existing file records only that the file has not changed SINCE the
# retrofit. So the instrumentation has to be present BEFORE the product exists, not after.
PROJ="$CODE_ROOT/nd-unfolding/project_cov_nd.py"
for _need in "proj_sha256" "hRowIndex" "row_index_sha256_readback"; do
  if ! grep -q "$_need" "$PROJ"; then
    echo "REFUSED -- $PROJ lacks $_need. OI-129: a product whose rows cannot be bound to physical" >&2
    echo "          bins, or whose bytes are not digested, is not verifiable after the fact." >&2
    exit 4
  fi
done

# ---- REFUSAL 3: THE DESTINATION MASK IS A DECLARATION, NOT A DEFAULT ---------------------------
# project_cov_nd.py offers two destination masks and on 42 bins they can differ materially. Which
# one is used changes the population every downstream criterion is stated over, so it is declared
# prospectively or not at all.
case "$DST_MASK" in
  declared-dst-cv)
    DST_ARG=(--dst-cv "${MNV_DST_CV:?declared-dst-cv requires MNV_DST_CV, the frozen lower-D CV}") ;;
  receiving-cells)
    DST_ARG=() ;;
  *)
    echo "REFUSED -- MNV_DST_MASK must be declared-dst-cv or receiving-cells, got: $DST_MASK" >&2
    exit 5 ;;
esac

# ---- FRESH RESOURCE STATE, because historical sizing is not current capacity -------------------
echo "=== resource state at dispatch ==="
date -u +"%Y-%m-%dT%H:%M:%SZ"
showquota 2>/dev/null || echo "showquota unavailable -- record this and do not substitute df"
echo "=== operands ==="
for _v in CODE_ROOT DATA_ROOT ADOPTION SRC_COV SRC_HIST SRC_CV DST_MASK OUT; do
  eval "echo \"  $_v = \$$_v\""
done

# ---- THE RUN. One invocation. NO AUTOMATIC RETRY. ----------------------------------------------
# A failure returns for a new decision. It does not resubmit itself, and nothing downstream may
# treat a retry as authorized by this script.
cd "$CODE_ROOT/nd-unfolding"
# `--run-class publication` was ABSENT here. The projector defaults to None, which records
# UNDECLARED -- so this launcher could not produce the publication-class M1 the order requires,
# and the `adoptable: false` refusal never fired, because that refusal is conditioned on exactly
# this value. The launcher that exists to build the publication product has to say so.
python3 project_cov_nd.py \
  --src-cov "$SRC_COV" --src-hist "$SRC_HIST" --src-cv "$SRC_CV" \
  --src-axes pt,pz,eavail,q3,W --keep-axes eavail,W \
  --run-class publication --expect-variant "$EXPECT_VARIANT" \
  "${DST_ARG[@]}" --out "$OUT" || _rc=$?
# `set -e` made the assignment below unreachable on failure, so the NO AUTOMATIC RETRY message it
# guards never printed. The exit status propagated regardless; what was lost was the disclosure.
_rc="${_rc:-0}"

if [ $_rc -ne 0 ]; then
  echo "M1 FAILED rc=$_rc. NO AUTOMATIC RETRY -- this returns for a decision." >&2
  exit $_rc
fi

# ---- THE RECEIPT MUST EXIST, or the run produced an unverifiable object ------------------------
if [ ! -f "${OUT}.receipt.json" ]; then
  echo "REFUSED -- ${OUT}.receipt.json absent. The product exists but nothing binds it." >&2
  exit 6
fi
echo "M1 COMPLETE -- CANDIDATE. Construction is not adoption, and this product is not quotable"
echo "until its independent verification lands. Receipt: ${OUT}.receipt.json"
