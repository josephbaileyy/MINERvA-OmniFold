# lib_substitution_fence.sh -- S1. REFUSE to run an UNHOOKED launcher while a member scan is declared.
#
# THE HAZARD, which is a substitution rather than a bug. `mii_seed_offset_driver.py` prints a plan naming
# the seven HOOKED launchers. Nothing makes the submitting party use them. Swap
# `sbatch_sweep_bank_5d_run.sh` for `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh` at k=1200 and the
# substitute:
#   - stays at its BASELINE seed, because it has no offset hook, and
#   - writes to the CANONICAL archive paths, because it has no member namespacing,
# while the validated plan stays green. The member's product is then the baseline's, or worse, lands in
# the published archive's directory.
#
# WHY THE FENCE IS *HERE* AND NOT IN THE DRIVER. `mii_seed_offset_driver.preflight_launcher()` was called
# only on names taken from the driver's OWN allowlist, which makes those calls TAUTOLOGICAL -- it verified
# that the launchers it chose are the launchers it chose. And the driver does not submit; the printed
# commands execute outside it. C ruled the fence must move into the launchers, because THE ONLY PLACE A
# SUBSTITUTION CAN BE CAUGHT IS INSIDE THE THING SUBSTITUTED IN.
#
# ONE DEFINITION, SOURCED RELATIVELY, NOT NINE COPIES. Nine inline copies drift and each passes its own
# reading. Relative sourcing (`_HERE`) means a frozen deployment gets its own frozen fence -- the same
# reason `lib_member_resume.sh` is sourced that way, and the cluster probe failed 16/16 when a launcher
# sourced a member-axis library through the mutable `${REPO}` instead. See BEN-483.
#
# NOTE THE POLARITY. This is the MIRROR of `mr_require_valid_offset`: the hooked launchers REQUIRE a valid
# offset when one is declared; these REFUSE ANY declaration at all. A launcher is in exactly one set, and
# a launcher in neither is a launcher nobody has classified.

mr_fence_unhooked() {
  # DECLARED-AT-ALL, not truthy. `MNV_EST_SEED_OFFSET=0` must ALSO refuse: an unhooked launcher at k=0
  # writes to the CANONICAL paths, so it would collide with the published archive rather than produce an
  # anchor member. The anchor is a MEMBER and must come from a hooked launcher like every other one.
  # `${VAR+x}` tests declaration; `${VAR:-}` would let set-but-empty through, which is the disagreement
  # that already bit the member library once.
  if [[ -n "${MNV_EST_SEED_OFFSET+x}" ]]; then
    echo "[fence] REFUSING TO RUN: $(basename "${BASH_SOURCE[1]:-this launcher}")" >&2
    echo "[fence]   MNV_EST_SEED_OFFSET is DECLARED (='${MNV_EST_SEED_OFFSET}') but this launcher has" >&2
    echo "[fence]   NO offset hook and NO member namespacing. It would run at its BASELINE seed and" >&2
    echo "[fence]   write to the CANONICAL archive paths -- producing a member that is silently the" >&2
    echo "[fence]   baseline, or writing into the published archive's own directories." >&2
    echo "[fence]   This is the substitution hazard S1 exists for. Use the HOOKED launcher named in" >&2
    echo "[fence]   mii_seed_offset_driver.LEG_LAUNCHERS for this leg." >&2
    echo "[fence]   If you genuinely want a NON-SCAN run of this launcher, unset MNV_EST_SEED_OFFSET." >&2
    exit 3
  fi
  return 0
}
