# Sourced AFTER improvement_campaign/confirm/jobs/confirm_lib.sh (not executable on its own).
#
# Overrides confirm_lib's `run_row` so a run-manifest row runs the PET final-design study runner
# (final_design/runner/run_design.py) instead of the predecessor's run_replicate.py, through the
# same guard (mnv_guarded_run.py), the same per-run directory, lock and log conventions. Everything
# else of confirm_lib (claim/flock, is_complete, score_row, manifest_rows) is used unchanged.
#
# Manifest row (tab-separated, as confirm_lib):  name config config_hash selection distortion
#   reference_run extra_driver_args
#   config        : relative to improvement_campaign/confirm/configs (as the predecessor's rows)
#   selection     : BANK:<DEV|FB|RB>:<stage>:<replicate>   a study draw (PROTOCOL-20260925 s.3):
#                                                          pseudodata from the bank, prior from DEV
#                   <pool>:<replicate>                     a predecessor-drawn pool replicate
#                                                          (P0-2, F0-11, S0, T0-1; checked against
#                                                          DEV when $BANKS exists)
#                   historical                             the historical halves (positive control)
#   distortion    : dev | null | a phase_e truth-weight id | R1_x<s>+<id>
#   extra         : "-" or extra run_design.py args, e.g. "--step2-miss-mode efficiency_corrected"
#                   or "--bootstrap-member 3 --bootstrap-seed 20260925"; {C} -> the campaign dir,
#                   {STUDY} -> final_design
#
# env: BANKS (banks.npz; default the impl-runner build), BANK_MANIFEST (default the committed
#      final_design/banks/BANK_MANIFEST.json), DESIGN_DRY_RUN=1 (print the command, run nothing)
#
# Use from final_design/jobs/pfd_worker_chain.sh: source this file right after confirm_lib.sh
# (the launcher does so when the file exists in the pinned checkout).
STUDY="$MINE/nd-unfolding/pet/final_design"
D="$STUDY/runner"
BANKS="${BANKS:-/pscratch/sd/j/josephrb/pet-final-design-20260925/impl-runner/banks/banks.npz}"
BANK_MANIFEST="${BANK_MANIFEST:-$STUDY/banks/BANK_MANIFEST.json}"

design_selection_args() {   # SELECTION -> prints one run_design.py argument per line
  local sel=$1 re='^BANK:(DEV|FB|RB):([^:/]+):([0-9]+)$'
  if [[ "$sel" == historical ]]; then
    printf '%s\n' --historical-halves
  elif [[ "$sel" == BANK:* ]]; then
    if [[ ! "$sel" =~ $re ]]; then
      echo "design_lib: malformed selection '$sel' (want BANK:<DEV|FB|RB>:<stage>:<rep>)" >&2
      return 2
    fi
    printf '%s\n' --bank-draw "${BASH_REMATCH[2]}:${BASH_REMATCH[3]}" \
      --pseudo-bank "${BASH_REMATCH[1]}" --banks-npz "$BANKS" --bank-manifest "$BANK_MANIFEST"
  else
    printf '%s\n' --pool "${sel%%:*}" --replicate "${sel##*:}" --pools-npz "$POOLS" \
      --manifest "$C/pools/POOL_MANIFEST.json"
    [[ -e "$BANKS" ]] && printf '%s\n' --banks-npz "$BANKS" --bank-manifest "$BANK_MANIFEST"
  fi
  return 0
}

run_row() {   # ROW DEVICE DEADLINE
  local ROW=$1 DEV=$2 DL=$3 name cfg hash selection distortion ref extra RUN
  local -a SEL CMD
  IFS=$'\t' read -r name cfg hash selection distortion ref extra <<< "$ROW"
  RUN="$OUT/$name"
  mapfile -t SEL < <(design_selection_args "$selection") || return 1
  (( ${#SEL[@]} > 0 )) || { echo "$name: bad selection '$selection'" >> "$OUT/exit-codes.txt"; return 1; }
  [[ "$extra" == "-" ]] && extra=""
  extra=${extra//\{C\}/$C}
  extra=${extra//\{STUDY\}/$STUDY}
  CMD=(python "$GUARD" --expect-root "$MINE" --inventory "$RUN/guard-$SLURM_JOB_ID.json"
       --label "PFD-$name" -- "$D/run_design.py" --config "$V/configs/$cfg" --config-hash "$hash"
       --repo "$MINE" --out "$RUN" --inputs-npz "$INPUTS" --identity-sidecar "$SIDECAR"
       --populations "$POPULATIONS" "${SEL[@]}" --distortion "$distortion"
       --deadline-unix "$DL" --first-iteration-estimate-s "${ITER_ESTIMATE:-800}")
  # word-split the extra args exactly as confirm_lib does ($extra unquoted)
  # shellcheck disable=SC2206
  CMD+=($extra)
  if [[ "${DESIGN_DRY_RUN:-0}" == 1 ]]; then printf '%s\n' "${CMD[@]}"; return 0; fi
  mkdir -p "$RUN"
  CUDA_VISIBLE_DEVICES=$DEV "${CMD[@]}" >> "$RUN/run-$SLURM_JOB_ID.log" 2>&1 \
    || { echo "$name exit $? (job $SLURM_JOB_ID)" >> "$OUT/exit-codes.txt"; return 1; }
}
