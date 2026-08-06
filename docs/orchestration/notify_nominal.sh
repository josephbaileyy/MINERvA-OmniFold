#!/bin/bash
# Fired by wakerctl when the full-event PET nominal training job leaves the queue.
#
# usage: notify_nominal.sh <job_id>
#
# The job id is a PARAMETER, not a constant. notify_pwclosure.sh carried a hardcoded one and had to
# be parameterised the moment its job was cancelled and re-submitted; do not repeat that here.
#
# It reports the OUTCOME, not merely that the job ended -- a notifier that only says "job finished"
# is the vacuous-pass defect in different clothing. Three things specifically:
#
#   1. DID BOTH TRAININGS FINISH? The launcher runs the nominal AND a matched GPU-floor repeat in one
#      job. A walltime kill between them leaves the nominal artifact present and the floor artifact
#      absent, and a plain resubmit then hits `is_complete(args.out)`
#      (train_fullevent_nominal.py:349-352) -> `die` -> the floor repeat never runs. That state is
#      UNRECOVERABLE without hand intervention, so it is called out explicitly rather than left for a
#      reader to infer from two file listings.
#   2. WHAT SEED POLICY DID THE RUN ACTUALLY USE? The artifact persists argv, not the policy constant
#      (train_fullevent_nominal.py:472-475). A launcher-vs-policy mismatch cost a cancelled
#      submission on 2026-08-06 (job 56410365 would have trained at niter=2). niter MUST read 3, or
#      `freeze:seed_policy` will reject the finished result.
#   3. THAT THE PRODUCT IS NOT QUOTABLE. Gate-4 cannot PASS while the powered-closure criterion is
#      unreachable as written, so this is a central value for the first time, not a result.
set -uo pipefail
JOB="${1:?usage: notify_nominal.sh <job_id>}"
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
OUT="${REPO}/nd-unfolding/pet/fullevent_nominal"
NOM="${OUT}/pet_fullevent_nominal_weights.npz"
FLR="${OUT}/pet_fullevent_floor_weights.npz"
BODY=/pscratch/sd/j/josephrb/.nominal_notify_body.txt

# Reading the artifact needs numpy, which /usr/bin/python3.11 does NOT have -- it is the correct
# interpreter for wakerctl and for send_channel_mail.py (both stdlib-only, and the login-node
# `python3` is 3.6, which wakerctl cannot run on) but it cannot open an .npz. This is the same
# resolution the launcher itself uses for its login-safe gate (sbatch_pet_fullevent_nominal.sh:106-109).
# Verified 2026-08-06 that BOTH interpreters round-trip the pickled 0-d object array that
# `seed_policy=np.asarray(..., dtype=object)` produces: numpy caps the object-array pickle protocol
# rather than using pickle.HIGHEST_PROTOCOL, so the 3.6 fallback reads a file written by the
# tensorflow/2.15.0 module's python 3.9 / numpy 1.26.3 without complaint.
PY_NUMPY="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}/bin/python3"
[[ -x "${PY_NUMPY}" ]] || PY_NUMPY="python3"

{
  echo "RESTORE Step 4 -- the full-event PET nominal training (job ${JOB}) has left the queue."
  echo "Fired by wakerctl on $(hostname) at $(date -u +%Y-%m-%dT%H:%M:%SZ), independent of any session."
  echo
  echo "=== sacct ==="
  sacct -j "${JOB}" --format=JobID,State,Elapsed,ExitCode,MaxRSS -P 2>/dev/null | head -5
  echo
  echo "=== did BOTH trainings finish? ==="
  for f in "${NOM}" "${FLR}"; do
    if [[ -s "${f}" ]]; then
      echo "  PRESENT  $(basename "${f}")  $(stat -c %s "${f}") bytes  sha $(sha256sum "${f}" | cut -c1-16)"
    else
      echo "  ABSENT   $(basename "${f}")"
    fi
  done
  if [[ -s "${NOM}" && ! -s "${FLR}" ]]; then
    echo
    echo "  *** PARTIAL RESULT. Nominal present, floor repeat ABSENT. A plain resubmit will DIE on"
    echo "      is_complete(nominal_out) before it reaches the floor repeat. Hand intervention needed."
  fi
  echo
  echo "=== what policy did the run ACTUALLY use? (argv-derived, not the constant) ==="
  if [[ -s "${NOM}" ]]; then
    # NOT /usr/bin/python3.11: that is the right interpreter for wakerctl (stdlib only, and the
    # login-node `python3` is 3.6) but it has no numpy, so reading an .npz needs a real environment.
    # PY_NUMPY is resolved by probing, and the probe result is reported rather than assumed.
    "${PY_NUMPY}" - "${NOM}" <<'PY'
import sys
import numpy as np
with np.load(sys.argv[1], allow_pickle=True) as d:
    for k in ("seed_policy", "estimator_fingerprint", "bkg_mode", "tag", "argv"):
        if k in d.files:
            v = d[k]
            print("  %s = %s" % (k, v.item() if getattr(v, "shape", None) == () else v))
    sp = d["seed_policy"].item() if "seed_policy" in d.files else {}
    n = (sp or {}).get("niter")
    verdict = "OK" if n == 3 else "*** EXPECTED 3 -- freeze:seed_policy WILL REJECT THIS RUN"
    print("  niter check: %r -- %s" % (n, verdict))
PY
  else
    echo "  no artifact to read"
  fi
  echo
  echo "=== NOT QUOTABLE ==="
  echo "  Gate-4 cannot PASS on present evidence: the powered closure FAILED at niter=3 with"
  echo "  recovery 0.5469 against a 0.80 bar whose achievable value is 0.6347, so the criterion"
  echo "  itself needs redesign. This is a central value for the first time, not a result."
  echo
  echo "Log: nd-unfolding/pet/AUTONOMOUS_LOG_20260805.md (tracked in git)"
} > "${BODY}" 2>&1

/usr/bin/python3.11 /pscratch/sd/j/josephrb/send_channel_mail.py \
  "[MNV-AUTO] Step 4 nominal training ${JOB} left the queue (wakerctl)" "${BODY}"
