#!/bin/bash
# Submit the six SB1 jobs from an ADMITTED record:   sb1_submit.sh ADMISSION.json
#
# Run on a Perlmutter login node from the admitted checkout. Refuses (sb1_admit.py check) unless the
# record is ADMITTED, its authorization is committed, HEAD and every manifest digest match, and the
# inputs still have the admitted size, mtime and inode. Creates the record's outroot (refusing an
# existing one), writes run.env and submission.json there, and submits H0 -> UL -> SL -> J1 -> C
# (afterok, --kill-on-invalid-dep=yes) and H1 (afterany on all five). No retries under an
# admission (launch-spec retry_rule); `sb1_verify.py ledger` accounts the charge.
set -eo pipefail
ADM_IN="${1:?usage: sb1_submit.sh ADMISSION.json}"
PKG="docs/orchestration/state/next-preparation-20261009/sb1-prep"
source "${SB1_ENV_SETUP:=/pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh}"
PY="${SB1_PY:-python}"
SBATCH="${SB1_SBATCH:-sbatch}"
ADM="$(realpath "${ADM_IN}")"
CODE="$("${PY}" -c 'import json,sys; print(json.load(open(sys.argv[1]))["checkout"])' "${ADM}")"
OUT="$("${PY}" -c 'import json,sys; print(json.load(open(sys.argv[1]))["outroot"])' "${ADM}")"
"${PY}" "${CODE}/${PKG}/sb1_admit.py" check --admission "${ADM}"
mkdir "${OUT}"
cp "${ADM}" "${OUT}/admission.json"
"${PY}" - "${CODE}/${PKG}/launch/launch-spec.json" "${OUT}" "${CODE}" "${PKG}" "${SB1_ENV_SETUP}" \
  "${PY}" > "${OUT}/run.env" <<'PYEOF'
import hashlib, json, shlex, sys
spec, out, code, pkg, setup, py = sys.argv[1:7]
s = json.load(open(spec))
env = {"SB1_CODE": code, "SB1_PKG": pkg, "SB1_OUT": out, "SB1_ADMISSION": f"{out}/admission.json",
       "SB1_ENV_SETUP": setup, "SB1_PY": py, "SB1_UNI": s["inputs"]["omnifile_universe"],
       "SB1_CV": s["inputs"]["omnifile_cv"], "SB1_MC": s["inputs"]["mcfile"],
       "SB1_LATERAL": s["universes"]["lateral"], "SB1_VERTICAL": s["universes"]["vertical"],
       "SB1_REF_UL": s["unmatched_references"]["UL_SL"], "SB1_REF_C": s["unmatched_references"]["C"]}
env["SB1_ENV_SETUP_SHA256"] = hashlib.sha256(open(setup, "rb").read()).hexdigest()
for k, v in env.items():
    print(f"export {k}={shlex.quote(v)}")
# Every job runs this check and then sources the setup at top level (not inside a function, so
# the setup's own variables keep their scope): refuse if it changed after submission, so the two
# arms cannot run under different environments unrecorded.
print("""sb1_check_env() {
  local h
  h="$( (sha256sum "${SB1_ENV_SETUP}" 2>/dev/null || shasum -a 256 "${SB1_ENV_SETUP}") | cut -d' ' -f1)"
  if [[ "${h}" != "${SB1_ENV_SETUP_SHA256}" ]]; then
    echo "[sb1] REFUSED: ${SB1_ENV_SETUP} changed since submission" >&2
    return 3
  fi
}""")
PYEOF
L="${CODE}/${PKG}/launch"
E="ALL,SB1_RUN_ENV=${OUT}/run.env"
S=("${SBATCH}" --parsable --kill-on-invalid-dep=yes --chdir="${OUT}"
   --output="${OUT}/%x_%j.out" --error="${OUT}/%x_%j.err")
on_error() {   # a partial submission must not leave charged jobs queued without H1
  echo "[sb1] submission stopped; cancelling: H0=${H0:-} UL=${UL:-} SL=${SL:-} J1=${J1:-} C=${C:-} H1=${H1:-}" >&2
  for id in ${H0:-} ${UL:-} ${SL:-} ${J1:-} ${C:-} ${H1:-}; do "${SB1_SCANCEL:-scancel}" "${id}" || true; done
}
trap on_error ERR
# A failed sbatch must stop the submission: errexit does not reach inside $(...), so submit()
# returns non-zero itself, the assignment in this shell then fails, and set -e runs on_error.
submit() {
  local id
  id="$("${S[@]}" "$@")" || return 1
  id="${id%%;*}"                       # --parsable prints "id[;cluster]"
  [[ "${id}" =~ ^[0-9]+$ ]] || return 1
  echo "${id}"
}
H0=$(submit --job-name=sb1_H0 --time=00:45:00 --export="${E},SB1_STAGE=H0" "${L}/sb1_hash.sbatch")
UL=$(submit --job-name=sb1_UL --time=00:50:00 --dependency="afterok:${H0}" \
     --export="${E},SB1_JOB=UL,SB1_ARM=all" "${L}/sb1_unfold.sbatch")
SL=$(submit --job-name=sb1_SL --time=00:30:00 --dependency="afterok:${UL}" \
     --export="${E},SB1_JOB=SL,SB1_ARM=selective" "${L}/sb1_unfold.sbatch")
J1=$(submit --job-name=sb1_J1 --time=00:45:00 --dependency="afterok:${SL}" \
     --export="${E}" "${L}/sb1_identity.sbatch")
C=$(submit --job-name=sb1_C --time=00:40:00 --dependency="afterok:${J1}" \
    --export="${E}" "${L}/sb1_cv.sbatch")
H1=$(submit --job-name=sb1_H1 --time=00:45:00 \
     --dependency="afterany:${H0}:${UL}:${SL}:${J1}:${C}" --export="${E},SB1_STAGE=H1" \
     "${L}/sb1_hash.sbatch")
"${PY}" - "${OUT}" "${ADM}" "${H0}" "${UL}" "${SL}" "${J1}" "${C}" "${H1}" <<'PYEOF'
import datetime, hashlib, json, sys
out, adm, *ids = sys.argv[1:]
rec = {"schema": "sb1-submission/1",
       "submitted_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "admission_sha256": hashlib.sha256(open(adm, "rb").read()).hexdigest(),
       "jobs": dict(zip(("H0", "UL", "SL", "J1", "C", "H1"), ids))}
with open(f"{out}/submission.json", "x") as fh:
    json.dump(rec, fh, indent=1)
print(json.dumps(rec["jobs"]))
PYEOF
