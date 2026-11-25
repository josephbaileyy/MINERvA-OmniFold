#!/bin/bash
# geanttw_remote.sh: the geanttw campaign's steps, run on a Perlmutter login node by geanttw_connect.sh, one step per
# go (DECLARATION.md §3, §4 P0, §6, §8).
#   bash geanttw_remote.sh STEP M COV2D_ACK NUE_ACK [ARG]
# Every step: refuses off a login node or inside a Slurm job; takes the cov2d session's fresh ack and the NuE
# exception's ack (tokens, no spaces) and appends them to B/run/acks.log with the step and UTC time.
# STEP
#   deploy  clone the repository at M into B/deploy; STOP unless it is clean at M; print the code's sha256s.
#   build   (deploy clean at M) run geanttw_build.sh once (nice -n 19); print build.log.
#   p0      (deploy clean at M) ARG is cov2d's LL5D atime-post UTC time as the director passes it on (§6 (a)): it must
#           be given, well formed and already past. Then build.log's CHECKs must all PASS; the sacct fence must show
#           no live cov2d/t2a job and no live geanttw_p0_ job; p0 must not have been submitted before; the launcher's
#           smoke must pass for BOTH builds. Only then is the atime-post recorded (once) and, for each build, the
#           fence re-read, the cap gate passed and the job submitted (geanttw_p0_<build>_1L, --time=01:00:00).
#   check   (deploy clean at M) both P0 outputs exist and no geanttw_p0_ job is live; copy MP-1 S1's 1L zero loop
#           with O_NOATIME, its sha256 taken from the committed retention manifest; run p0_check.py (C0a–C0f).
# sacct only, never squeue (the standing rule). No set -u (conda's activation references unset variables).
set -o pipefail
STEP="${1:?step}"; M="${2:?M}"; COV2D_ACK="${3:-}"; NUE_ACK="${4:-}"; ARG="${5:-}"
B=/pscratch/sd/j/josephrb/geanttw-20261124
REPO=https://github.com/josephbaileyy/MINERvA-OmniFold.git
HOST_RE='^login[0-9]+'
SYSPY=/usr/bin/python3
CHKPY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
REF=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s1/evloop/zero/runEventLoopOmniFold_5D_1L_zero.root
if [[ -n "${GEANTTW_TEST_B:-}" ]]; then   # the tests' only door: scratch paths, a local repository, any host name
  B="${GEANTTW_TEST_B}"; REPO="${GEANTTW_TEST_REPO:?}"; HOST_RE="${GEANTTW_TEST_HOST_RE:-${HOST_RE}}"
  SYSPY="${GEANTTW_TEST_PY:-python3}"; CHKPY="${GEANTTW_TEST_PY:-python3}"; REF="${GEANTTW_TEST_REF:-${REF}}"
fi
D="${B}/deploy"
CODE_REL=docs/orchestration/state/geanttw-20261124/code
SUMS_REL=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/retention-20261110/hpss-20261111/manifests/SHA256SUMS.zero_loops
FENCE_RE='^(cov2d|t2a)'
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
SINCE=$(${SYSPY} -c 'import datetime; print((datetime.date.today() - datetime.timedelta(14)).isoformat())')
snapshot() {  # sacct rows for the last 14 days into $1; stderr is kept with them, so any error line refuses
  sacct -X -n -P -S "${SINCE}" -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw > "$1" 2>&1 || stop "sacct failed"
}
fence() {  # fence REGEX LABEL
  local psv="${B}/run/sacct.psv" rc
  snapshot "${psv}"
  ${SYSPY} -I "${D}/${CODE_REL}/geanttw_sacct.py" fence --sacct "${psv}" --regex "$1"; rc=$?
  [[ ${rc} -eq 0 ]] || stop "the sacct fence ($2) is not clear (rc ${rc})"
}

case "${STEP}" in
deploy)
  [[ ! -e "${D}" ]] || bail "${D} exists"
  ack
  git clone --quiet "${REPO}" "${D}" || stop "clone failed"
  git -C "${D}" -c advice.detachedHead=false checkout --quiet "${M}" || stop "checkout ${M} failed"
  clean_at_m
  echo "deploy at ${M}: clean"
  (cd "${D}/${CODE_REL}" && sha256sum geanttw_remote.sh geanttw_build.sh geanttw_evloop.sbatch geanttw_sacct.py \
    geanttw_provenance.py dumpcmp.py p0_check.py S0-src_base.sha256)
  ;;
build)
  clean_at_m
  [[ ! -e "${B}/run/p0/build.log" ]] || bail "${B}/run/p0/build.log exists"
  ack
  nice -n 19 bash "${D}/${CODE_REL}/geanttw_build.sh" "${B}" "${D}"; rc=$?
  [[ -f "${B}/run/p0/build.log" ]] && cat "${B}/run/p0/build.log"
  [[ ${rc} -eq 0 ]] || stop "geanttw_build.sh exited ${rc}"
  ;;
p0)
  clean_at_m
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
  clean_at_m
  ack
  for build in pin pat; do
    [[ -s "${B}/run/p0/${build}/runEventLoopOmniFold_GEANTTW_${build}_1L.root" ]] || stop "no P0 output for ${build}"
  done
  fence '^geanttw_p0_' "P0 jobs still live"
  want=$(awk -v p="${REF}" '$2 == p {print $1}' "${D}/${SUMS_REL}")
  [[ "${want}" =~ ^[0-9a-f]{64}$ ]] || stop "no committed sha256 for ${REF} in ${SUMS_REL}"
  mkdir -p "${B}/run/p0/ref" || stop "mkdir ref"
  RC="${B}/run/p0/ref/$(basename "${REF}")"
  ${SYSPY} -I - "${REF}" "${RC}" <<'EOF' || stop "the O_NOATIME copy of the reference failed"
import os, sys
src, dst = sys.argv[1], sys.argv[2]
fd = os.open(src, os.O_RDONLY | getattr(os, "O_NOATIME", 0))
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
*) bail "unknown step '${STEP}' (deploy, build, p0, check; P2's steps come with their own binding)" ;;
esac
echo "== geanttw remote ${STEP} rc=0 $(date -u +%FT%TZ)"
