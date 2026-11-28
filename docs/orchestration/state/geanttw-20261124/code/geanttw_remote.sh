#!/bin/bash
# geanttw_remote.sh: the geanttw campaign's steps, run on a Perlmutter login node by geanttw_connect.sh, one step per
# go (DECLARATION.md §3, §4 P0, §6, §8).
#   bash geanttw_remote.sh STEP M COV2D_ACK NUE_ACK [ARG]
# Every step: refuses off a login node or inside a Slurm job; takes the cov2d session's fresh ack and the NuE
# exception's ack (tokens, no spaces) and appends them to B/run/acks.log with the step and UTC time.
# STEP
#   deploy  clone the repository at M into B/deploy; STOP unless it is clean at M; print the code's sha256s; re-hash
#           S0's MANIFEST.sha256 with O_NOATIME and STOP unless it is the ruling's (S0_PATH, S0_SHA); record the pass.
# build, p0 and check first require the deploy clean at M and that recorded S0 pass.
#   build   run geanttw_build.sh once (nice -n 19); print build.log.
#   p0      ARG is cov2d's LL5D atime-post UTC time as the director passes it on (§6 (a)): it must be given, well formed
#           and already past. Then build.log's CHECKs must all PASS; the sacct fence must show
#           no live cov2d/t2a job and no live geanttw_p0_ job; p0 must not have been submitted before; the launcher's
#           smoke must pass for BOTH builds. Only then is the atime-post recorded (once) and, for each build, the
#           fence re-read, the cap gate passed and the job submitted (geanttw_p0_<build>_1L, --time=01:00:00).
#   check   both P0 outputs exist and no geanttw_p0_ job is live; copy MP-1 S1's 1L zero loop with O_NOATIME, its
#           sha256 taken from the committed retention manifest; run p0_check.py (C0a–C0f).
# sacct only, never squeue (the standing rule). No set -u (conda's activation references unset variables).
set -o pipefail
STEP="${1:?step}"; M="${2:?M}"; COV2D_ACK="${3:-}"; NUE_ACK="${4:-}"; ARG="${5:-}"
B=/pscratch/sd/j/josephrb/geanttw-20261124
REPO=https://github.com/josephbaileyy/MINERvA-OmniFold.git
HOST_RE='^login[0-9]+'
SYSPY=/usr/bin/python3
CHKPY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
REF=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s1/evloop/zero/runEventLoopOmniFold_5D_1L_zero.root
NOATIME_OPTIONAL=0   # every O_NOATIME read refuses on a Python without O_NOATIME
# the director's ruling of 2026-11-25: the S0 file read once after the certificate expired, and its sha256 then
S0_PATH=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s0/build/MANIFEST.sha256
S0_SHA=fe0bc458b6bcbabcb3f589858e118e325a1c9d33de04edbdf677d06d5696f591
if [[ -n "${GEANTTW_TEST_B:-}" ]]; then   # the tests' only door: scratch paths, a local repository, any host name
  B="${GEANTTW_TEST_B}"; REPO="${GEANTTW_TEST_REPO:?}"; HOST_RE="${GEANTTW_TEST_HOST_RE:-${HOST_RE}}"
  SYSPY="${GEANTTW_TEST_PY:-python3}"; CHKPY="${GEANTTW_TEST_PY:-python3}"; REF="${GEANTTW_TEST_REF:-${REF}}"
  NOATIME_OPTIONAL="${GEANTTW_TEST_NOATIME_OPTIONAL:-1}"   # macOS has no O_NOATIME
  S0_PATH="${GEANTTW_TEST_S0_PATH:-${S0_PATH}}"; S0_SHA="${GEANTTW_TEST_S0_SHA:-${S0_SHA}}"
fi
D="${B}/deploy"
CODE_REL=docs/orchestration/state/geanttw-20261124/code
SUMS_REL=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/retention-20261110/hpss-20261111/manifests/SHA256SUMS.zero_loops
FENCE_RE='^(cov2d|t2a|covfix_)'
ACK_RE='^[A-Za-z0-9._:@/+=-]{8,200}$'

bail() { echo "REFUSED (nothing written): $*"; exit 9; }
stop() { echo "STOP: $*"; echo "== geanttw remote ${STEP} rc=8 $(date -u +%FT%TZ)"; exit 8; }

[[ "${M}" =~ ^[0-9a-f]{40}$ ]] || bail "M '${M}' is not a 40-hex commit"
[[ "${COV2D_ACK}" =~ ${ACK_RE} ]] || bail "the cov2d ack is missing or not a token"
[[ "${NUE_ACK}" =~ ${ACK_RE} ]] || bail "the NuE exception's ack is missing or not a token"
[[ "$(hostname -s 2>/dev/null || hostname)" =~ ${HOST_RE} ]] || bail "not a login node: $(hostname)"
[[ -z "${SLURM_JOB_ID:-}" ]] || bail "inside Slurm job ${SLURM_JOB_ID}"

ack() {
  mkdir -p "${B}/run" || stop "mkdir ${B}/run"
  printf 'ACK step=%s m=%s utc=%s cov2d=%s nue=%s\n' "${STEP}" "${M}" "$(date -u +%FT%TZ)" "${COV2D_ACK}" "${NUE_ACK}" \
    >> "${B}/run/acks.log" || stop "cannot write ${B}/run/acks.log"
}
clean_at_m() {
  [[ -d "${D}/.git" ]] || stop "no deploy at ${D}"
  local head porc
  head=$(git -C "${D}" rev-parse HEAD) || stop "git rev-parse failed in ${D}"
  [[ "${head}" == "${M}" ]] || stop "deploy is at ${head}, not ${M}"
  porc=$(git -C "${D}" status --porcelain --untracked-files=all | wc -l | tr -d ' ')
  [[ "${porc}" -eq 0 ]] || stop "deploy has ${porc} porcelain lines"
}
# The director's ruling of 2026-11-25: S0's MANIFEST.sha256 was read once after the certificate had expired, so the
# first connect under a fresh certificate (deploy) re-hashes it with O_NOATIME and STOPs unless it is still the file
# read; build, p0 and check refuse unless that re-hash passed. The ruling's path and sha256 are S0_PATH and S0_SHA,
# and the committed S0-src_base.sha256's one "# source" line must name the same two.
S0_OK="${D}/.git/geanttw-s0-rehash.txt"   # inside this checkout's own .git: a replacement checkout has none
s0_header() {
  local n
  read -r n s0_path s0_want < <(awk '$1 == "#" && $2 == "source" && $4 == "sha256" {n++; p=$3; s=$5}
    END {print n+0, p, s}' "${D}/${CODE_REL}/S0-src_base.sha256")
  [[ "${n}" -eq 1 && "${s0_path}" == /* && "${s0_want}" =~ ^[0-9a-f]{64}$ ]] \
    || stop "S0-src_base.sha256 must have exactly one '# source PATH sha256 HEX' line"
  [[ "${s0_path}" == "${S0_PATH}" && "${s0_want}" == "${S0_SHA}" ]] \
    || stop "S0-src_base.sha256's source is ${s0_path} ${s0_want}, not the ruling's ${S0_PATH} ${S0_SHA}"
}
s0_hash() {   # the sha256 of $1, read with O_NOATIME (refused on a Python without it, outside the tests)
  ${SYSPY} -I - "$1" "${NOATIME_OPTIONAL}" <<'EOF'
import hashlib, os, sys
flag = getattr(os, "O_NOATIME", None)
if flag is None and sys.argv[2] != "1":
    sys.exit("this Python has no O_NOATIME")
fd = os.open(sys.argv[1], os.O_RDONLY | (flag or 0))
h = hashlib.sha256()
while True:
    b = os.read(fd, 1 << 20)
    if not b:
        break
    h.update(b)
os.close(fd)
print(h.hexdigest())
EOF
}
ready() {   # build, p0 and check: the deploy is clean at M and its S0 re-hash passed
  clean_at_m
  s0_header
  [[ "$(cat "${S0_OK}" 2>/dev/null)" == "PASS ${s0_path} ${s0_want}" ]] \
    || stop "S0's MANIFEST.sha256 has no passing re-hash in ${S0_OK} (run deploy under a fresh certificate)"
}
SINCE=$(${SYSPY} -c 'import datetime; print((datetime.date.today() - datetime.timedelta(14)).isoformat())')
snapshot() {  # sacct rows for the last 14 days into $1; stderr is kept with them, so any error line refuses
  sacct -X -n -P -S "${SINCE}" -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw,AllocTRES > "$1" 2>&1 || stop "sacct failed"
}
fence() {  # fence REGEX LABEL
  local psv="${B}/run/sacct.psv" rc
  snapshot "${psv}"
  ${SYSPY} -I "${D}/${CODE_REL}/geanttw_sacct.py" fence --sacct "${psv}" --regex "$1"; rc=$?
  [[ ${rc} -eq 0 ]] || stop "the sacct fence ($2) is not clear (rc ${rc})"
}

# ---- P2-P3 steps (p2p3/AMENDMENT-P2P3.md): each needs its own GO and a fresh cov2d ack --------------------------
P2_LIMITS="${D}/${CODE_REL}/p2_limits.txt"
P2_PLS=(1A 1C 1D 1E 1F 1G 1M 1N 1O 1P)   # the pilot playlist 1B runs in p2pilot; 1L is P0's
SP="${B}/run/p2p3/submissions.log"
verdict() {   # verdict FILE: the "verdict" of a JSON record, or nothing
  ${SYSPY} -c 'import json, sys; print(json.load(open(sys.argv[1])).get("verdict", ""))' "$1" 2>/dev/null
}
submitted() { [[ -s "${SP}" ]] && grep -q " name=$1 " "${SP}"; }
c3_bound() {  # c3_bound WHY: C3 PASS, and the six pinned outputs still hash to what c3.json recorded
  ${SYSPY} -c '
import hashlib, json, os, sys
rec = json.load(open(sys.argv[1])); want = rec.get("pin_xsec_sha256") or {}
ok = rec.get("verdict") == "PASS" and len(want) == 6
for b in ("Neutron", "Pion", "Proton"):
    for i in (0, 1):
        p = os.path.join(sys.argv[2], "GEANT_%s_%d" % (b, i), "xsec.root")
        h = want.get("pin:%s_%d" % (b, i), "")
        ok = ok and os.path.isfile(p) and len(h) == 64 and hashlib.sha256(open(p, "rb").read()).hexdigest() == h
sys.exit(0 if ok else 1)' "${B}/run/p3/c3.json" "${B}/p3/out/pin" 2>/dev/null \
    || stop "C3 is not PASS, or the pinned outputs are not the ones it passed: $1"
}
submit() {    # submit NAME LIMIT SBATCH_ARGS... : fence, cap gate, sbatch, then one SUBMIT line
  local name="$1" limit="$2" jid; shift 2
  submitted "${name}" && stop "${name} was already submitted"
  fence "${FENCE_RE}" "before ${name}"
  snapshot "${B}/run/sacct.psv"
  ${SYSPY} -I "${D}/${CODE_REL}/geanttw_sacct.py" cap --sacct "${B}/run/sacct.psv" --submissions "${SP}" \
    --name "${name}" --limit "${limit}" || stop "the cap gate refuses ${name}"
  jid=$(sbatch --parsable --job-name="${name}" --time="${limit}" --output="${B}/run/logs/%x_%j.out" "$@") \
    || stop "sbatch ${name} failed"
  echo "SUBMIT id=${jid} name=${name} limit=${limit} utc=$(date -u +%FT%TZ)" | tee -a "${SP}"
}
need_completed() {   # need_completed NAME...: each predecessor submitted once and COMPLETED in sacct, so an output
                     # left by a job that exited nonzero (20: a failed after-stamp) is never consumed
  snapshot "${B}/run/sacct.psv"
  ${SYSPY} -I "${D}/${CODE_REL}/geanttw_sacct.py" completed --sacct "${B}/run/sacct.psv" --submissions "${SP}" "$@" \
    > "${B}/run/p2p3/completed.json" || stop "a predecessor is not COMPLETED in sacct: $(cat "${B}/run/p2p3/completed.json")"
}
UNIS=(GEANT_Neutron_0 GEANT_Neutron_1 GEANT_Pion_0 GEANT_Pion_1 GEANT_Proton_0 GEANT_Proton_1)
p2_prereqs() {
  [[ "$(verdict "${B}/run/p0/p0_check.json")" == PASS ]] || stop "P0's check is not PASS"
  [[ -s "${B}/run/gates/ll5d_atime_post.txt" ]] || stop "no LL5D atime-post record (P0's p0 step)"
  [[ "$(verdict "${B}/run/p3/c2pre.json")" == PASS ]] || stop "the C2 pre-check is not PASS"
  need_completed geanttw_p2_c2pre
}
evloop() {    # evloop PL: EV = sbatch arguments for P2's patched event loop on PL (no subshell, so a stop stops)
  local bin="${B}/prefix-pat/bin/runEventLoopOmniFold" md5 lim_sha
  [[ -x "${bin}" ]] || stop "no binary ${bin}"
  md5=$(md5sum "${bin}" | cut -d' ' -f1) && [[ -n "${md5}" ]] || stop "cannot md5 ${bin}"
  lim_sha=$(sha256sum "${P2_LIMITS}" | cut -d' ' -f1) && [[ -n "${lim_sha}" ]] || stop "cannot hash ${P2_LIMITS}"
  EV=("${D}/${CODE_REL}/geanttw_evloop.sbatch" "${B}" pat "$1" "${md5}" "${D}" "${P2_LIMITS}" "${lim_sha}")
}
limit_of() { awk -v p="$1" '$1 == p {print $2}' "${P2_LIMITS}"; }
P3SB="${D}/${CODE_REL}/geanttw_p3.sbatch"

case "${STEP}" in
c2pre|p2pilot|p2run|p3slim|p3unf|p3extract)
  ready
  ack
  fence "${FENCE_RE}" "cov2d/t2a/covfix_"
  mkdir -p "${B}/run/p2p3" "${B}/run/logs" || stop "mkdir run dirs"
  ${SYSPY} -I "${D}/${CODE_REL}/p2_limits.py" --repo "${D}" --check "${P2_LIMITS}" || stop "p2_limits.txt is not the repo's"
  ;;
esac
case "${STEP}" in
c2pre)
  [[ "$(verdict "${B}/run/p0/p0_check.json")" == PASS ]] || stop "P0's check is not PASS"
  submit geanttw_p2_c2pre 00:30:00 -c 2 --mem=16G "${P3SB}" c2pre "${B}" "${D}"
  exit 0 ;;
p2pilot)
  p2_prereqs
  for v in pilotref pilot; do
    evloop 1B
    submit "geanttw_p2_${v}_1B" "$(limit_of 1B)" "${EV[@]}"
  done
  exit 0 ;;
p2run)
  p2_prereqs
  submitted geanttw_p2_pilot_1B && submitted geanttw_p2_pilotref_1B || stop "the pilot pair was not submitted"
  snapshot "${B}/run/sacct.psv"   # A2, the director's ruling: both pilots COMPLETED, and traced/untraced <= 3
  ${SYSPY} -I "${D}/${CODE_REL}/geanttw_sacct.py" pilot --sacct "${B}/run/sacct.psv" --submissions "${SP}" \
    | tee "${B}/run/p2p3/pilot.json" || stop "the pilot gate refuses: P2 stops and reports to the director"
  for pl in "${P2_PLS[@]}"; do
    evloop "${pl}"
    submit "geanttw_p2_${pl}" "$(limit_of "${pl}")" "${EV[@]}"
  done
  exit 0 ;;
p3slim)   # one pass over UOMNI: the full C2, the three slims and their read-back (amendment 3)
  [[ "$(verdict "${B}/run/p3/c2pre.json")" == PASS ]] || stop "the C2 pre-check is not PASS"
  for pl in "${P2_PLS[@]}" pilotref_1B; do
    [[ -s "${B}/run/p2/pat/runEventLoopOmniFold_GEANTTW_pat_${pl}.root" ]] || stop "no P2 output for ${pl}"
  done
  [[ -s "${B}/run/p0/pat/runEventLoopOmniFold_GEANTTW_pat_1L.root" ]] || stop "no P0 patched output for 1L"
  fence '^geanttw_p2_' "P2 jobs still live"
  need_completed $(printf 'geanttw_p2_%s ' "${P2_PLS[@]}") geanttw_p2_pilotref_1B
  submit geanttw_p3_slim 02:00:00 -c 2 --mem=32G "${P3SB}" slim "${B}" "${D}"
  exit 0 ;;
p3unf)
  case "${ARG}" in pin) slims=(pin) ;; rest) slims=(pinov patov) ;; *) bail "p3unf takes pin or rest, got '${ARG}'" ;; esac
  fence '^geanttw_p3_slim$' "the slim job still live"
  need_completed geanttw_p3_slim
  [[ "$(verdict "${B}/run/p3/slim.json")" == PASS ]] || stop "slim.json is not PASS: no unfold runs"
  for f in slim-pinned slim-pinned-override slim-patched; do
    [[ -s "${B}/p3/${f}.root" ]] || stop "no ${B}/p3/${f}.root"
  done
  if [[ "${ARG}" == rest ]]; then
    c3_bound "no override unfold runs (the director's term 1)"
    need_completed geanttw_p3_extract_pin
  fi
  for s in "${slims[@]}"; do
    for u in GEANT_Neutron:0 GEANT_Neutron:1 GEANT_Pion:0 GEANT_Pion:1 GEANT_Proton:0 GEANT_Proton:1; do
      submit "geanttw_p3_unf_${s}_${u/:/_}" 00:30:00 -c 128 --mem=243840M "${P3SB}" unf "${B}" "${D}" "${s}" "${u}"
    done
  done
  exit 0 ;;
p3extract)
  [[ "${ARG}" == pin || "${ARG}" == all ]] || bail "p3extract takes pin or all, got '${ARG}'"
  fence '^geanttw_p3_unf_' "unfolds still live"
  if [[ "${ARG}" == pin ]]; then
    need_completed $(printf 'geanttw_p3_unf_pin_%s ' "${UNIS[@]}")
  else
    c3_bound "no patched number is read"
    need_completed geanttw_p3_extract_pin $(printf 'geanttw_p3_unf_%s ' $(for s in pin pinov patov; do printf "${s}_%s " "${UNIS[@]}"; done))
  fi
  submit "geanttw_p3_extract_${ARG}" 00:30:00 -c 2 --mem=16G "${P3SB}" extract "${B}" "${D}" "${ARG}"
  exit 0 ;;
esac

case "${STEP}" in
deploy)
  [[ ! -e "${D}" ]] || bail "${D} exists"
  ack
  git clone --quiet "${REPO}" "${D}" || stop "clone failed"
  git -C "${D}" -c advice.detachedHead=false checkout --quiet "${M}" || stop "checkout ${M} failed"
  clean_at_m
  echo "deploy at ${M}: clean"
  (cd "${D}/${CODE_REL}" && sha256sum geanttw_remote.sh geanttw_build.sh geanttw_evloop.sbatch geanttw_sacct.py \
    geanttw_provenance.py dumpcmp.py p0_check.py S0-src_base.sha256 geanttw_p3.sbatch c2_check.py p3_slim.py \
    slim_tparams.py p3_readout.py p2_limits.txt)
  s0_header
  s0_got=$(s0_hash "${s0_path}") || stop "the O_NOATIME re-hash of ${s0_path} failed"
  [[ "${s0_got}" == "${s0_want}" ]] || stop "${s0_path} is now ${s0_got}, not ${s0_want}: S0 changed since its read"
  echo "PASS ${s0_path} ${s0_got}" > "${S0_OK}" || stop "cannot write ${S0_OK}"
  echo "S0 re-hashed with O_NOATIME: ${s0_path} ${s0_got}"
  ;;
build)
  ready
  [[ ! -e "${B}/run/p0/build.log" ]] || bail "${B}/run/p0/build.log exists"
  ack
  nice -n 19 bash "${D}/${CODE_REL}/geanttw_build.sh" "${B}" "${D}"; rc=$?
  [[ -f "${B}/run/p0/build.log" ]] && cat "${B}/run/p0/build.log"
  [[ ${rc} -eq 0 ]] || stop "geanttw_build.sh exited ${rc}"
  ;;
p0)
  ready
  [[ "${ARG}" =~ ^20[0-9]{2}-[01][0-9]-[0-3][0-9]T[0-2][0-9]:[0-5][0-9]:[0-5][0-9]Z$ ]] \
    || bail "p0 needs cov2d's LL5D atime-post UTC time as YYYY-MM-DDTHH:MM:SSZ, got '${ARG}'"
  now=$(date -u +%Y%m%d%H%M%S); post=$(printf '%s' "${ARG}" | tr -d 'TZ:-')
  [[ "${now}" > "${post}" ]] || bail "the LL5D atime-post ${ARG} is not yet past (now ${now})"
  G="${B}/run/gates/ll5d_atime_post.txt"
  if [[ -e "${G}" ]]; then
    grep -qx "ll5d_atime_post_utc=${ARG}" "${G}" || stop "${G} records another time: $(head -1 "${G}")"
  fi
  ack
  L="${B}/run/p0/build.log"
  [[ -f "${L}" ]] || stop "no build.log"
  for c in DIFF_EQUALS_UPSTREAM SOURCE_PROVENANCE RPATH_CLEAN LIBMAT_IDENTICAL LIBMATMINERVA_DIFFER; do
    grep -qx "CHECK ${c} PASS" "${L}" || stop "build.log's CHECK ${c} is not PASS"
  done
  fence "${FENCE_RE}" "cov2d/t2a"
  fence '^geanttw_p0_' "an earlier p0 job"
  S="${B}/run/p0/submissions.log"
  [[ ! -s "${S}" ]] || stop "p0 was already submitted: $(cat "${S}")"
  mkdir -p "${B}/run/logs" "${B}/run/p0/pin" "${B}/run/p0/pat" || stop "mkdir run dirs"
  for build in pin pat; do   # both smokes pass before either job is submitted
    bin="${B}/prefix-${build}/bin/runEventLoopOmniFold"
    [[ -x "${bin}" ]] || stop "no binary ${bin}"
    printf -v "MD5_${build}" '%s' "$(md5sum "${bin}" | cut -d' ' -f1)"
    md5v="MD5_${build}"
    GEANTTW_SMOKE=1 GEANTTW_NAME="geanttw_p0_${build}_1L" GEANTTW_TIMELIMIT=01:00:00 \
      bash "${D}/${CODE_REL}/geanttw_evloop.sbatch" "${B}" "${build}" 1L "${!md5v}" "${D}" \
      || stop "the launcher's smoke refuses geanttw_p0_${build}_1L"
  done
  if [[ ! -e "${G}" ]]; then
    mkdir -p "${B}/run/gates" && printf 'll5d_atime_post_utc=%s\nrecorded_utc=%s\n' "${ARG}" "$(date -u +%FT%TZ)" > "${G}" \
      || stop "cannot record ${G}"
  fi
  for build in pin pat; do
    name="geanttw_p0_${build}_1L"; md5v="MD5_${build}"
    fence "${FENCE_RE}" "before ${name}"
    snapshot "${B}/run/sacct.psv"
    ${SYSPY} -I "${D}/${CODE_REL}/geanttw_sacct.py" cap --sacct "${B}/run/sacct.psv" --submissions "${S}" \
      --name "${name}" --limit 01:00:00 || stop "the cap gate refuses ${name}"
    jid=$(sbatch --parsable --job-name="${name}" --time=01:00:00 --output="${B}/run/logs/%x_%j.out" "${D}/${CODE_REL}/geanttw_evloop.sbatch" "${B}" "${build}" 1L "${!md5v}" "${D}") || stop "sbatch ${name} failed"
    echo "SUBMIT id=${jid} name=${name} limit=01:00:00 md5=${!md5v} utc=$(date -u +%FT%TZ)" | tee -a "${S}"
  done
  ;;
check)
  ready
  ack
  for build in pin pat; do
    [[ -s "${B}/run/p0/${build}/runEventLoopOmniFold_GEANTTW_${build}_1L.root" ]] || stop "no P0 output for ${build}"
  done
  fence '^geanttw_p0_' "P0 jobs still live"
  want=$(awk -v p="${REF}" '$2 == p {print $1}' "${D}/${SUMS_REL}")
  [[ "${want}" =~ ^[0-9a-f]{64}$ ]] || stop "no committed sha256 for ${REF} in ${SUMS_REL}"
  mkdir -p "${B}/run/p0/ref" || stop "mkdir ref"
  RC="${B}/run/p0/ref/$(basename "${REF}")"
  ${SYSPY} -I - "${REF}" "${RC}" "${NOATIME_OPTIONAL}" <<'EOF' || stop "the O_NOATIME copy of the reference failed"
import os, sys
src, dst = sys.argv[1], sys.argv[2]
flag = getattr(os, "O_NOATIME", None)
if flag is None and sys.argv[3] != "1":
    sys.exit("this Python has no O_NOATIME")
fd = os.open(src, os.O_RDONLY | (flag or 0))
with open(dst, "wb") as out:
    while True:
        b = os.read(fd, 1 << 22)
        if not b:
            break
        out.write(b)
os.close(fd)
EOF
  "${CHKPY}" -I "${D}/${CODE_REL}/p0_check.py" --B "${B}" --deploy "${D}" --ref "${RC}" --ref-sha "${want}" \
    --json "${B}/run/p0/p0_check.json"; rc=$?
  [[ ${rc} -eq 0 ]] || stop "p0_check.py exited ${rc}"
  ;;
*) bail "unknown step '${STEP}' (deploy, build, p0, check, c2pre, p2pilot, p2run, p3slim, p3unf, p3extract)" ;;
esac
echo "== geanttw remote ${STEP} rc=0 $(date -u +%FT%TZ)"
