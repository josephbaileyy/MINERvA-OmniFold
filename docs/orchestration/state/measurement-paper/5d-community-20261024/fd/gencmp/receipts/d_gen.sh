#!/bin/bash
#SBATCH -q regular
#SBATCH -C cpu
#SBATCH -N 1
#SBATCH -t 00:45:00
#SBATCH -A m3246
#SBATCH -J gencmp-dgen
#SBATCH -o /pscratch/sd/j/josephrb/gencmp-20261101/logs/dgen-%j.out
# GENCMP step D production (FD-GENCMP-DECLARATION.md section 5; binding ruling 1): the MAIN and SUPP chunks of
# d_SEEDS.txt, all concurrent, each with MP3-B's chain: an aborted attempt is discarded whole (.root/.part), then ALT1,
# then ALT2, then DROPPED. Each completed attempt is converted with the frozen flat macro. Writes only under $B/d.
# No set -u (UPS/conda). Paths absolute (sbatch runs a copy).
B=/pscratch/sd/j/josephrb/gencmp-20261101
G=/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie
FLAT=/pscratch/sd/j/josephrb/s5p-20260926/gen5d/code/nuwro_to_flat_5d.C
FLUX_MAIN=$G/flux_mefhc_numu_nuwro.root
FLUX_SUPP=/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/supp/flux_phi_t_50_100.root
source $B/receipts/d_card.sh
[ -e "$B/d/gen" ] && { echo "STOP: $B/d/gen exists"; exit 2; }
mkdir -p "$B/d/gen" || exit 2
echo "host $(hostname) start $(date -u +%FT%TZ) job ${SLURM_JOB_ID:-none} nproc $(nproc)"
sha256sum "$G/setup_nuwro.sh" "$FLAT" "$FLUX_MAIN" "$FLUX_SUPP" "$B/receipts/d_SEEDS.txt" "$B/receipts/d_card.sh"

attempt() {  # W SEED N FLUX -> 0 ok, 5 flat failure, else NuWro's rc (outputs discarded)
  local W=$1 rc
  mkdir -p "$W" && cd "$W" || return 2
  write_card "$2" "$3" "$4"
  "$NUWRO_HOME/bin/nuwro" -i params.txt -o nuwro.root > nuwro.log 2>&1
  rc=$?
  if [ $rc = 0 ]; then
    root -l -b -q "$FLAT(\"nuwro.root\",\"flat5d.root\")" > flat.log 2>&1 || return 5
    return 0
  fi
  rm -f nuwro.root nuwro.root.*.part
  return $rc
}

chain() {  # TAG I N FLUX S0 S1 S2
  local C k rc
  C=$B/d/gen/$1/c$(printf %03d "$2")
  local seeds=("$5" "$6" "$7")
  mkdir -p "$C" && cp "$G/setup_nuwro.sh" "$C/" && source "$C/setup_nuwro.sh" > "$C/setup.log" 2>&1
  for k in 0 1 2; do
    attempt "$C/a$k" "${seeds[$k]}" "$3" "$4"
    rc=$?
    printf '%s\t%s\t%s\n' "$k" "${seeds[$k]}" "$rc" >> "$C/attempts.tsv"
    [ $rc = 0 ] && { echo "ok $k ${seeds[$k]}" > "$C/RESULT"; return 0; }
    [ $rc = 5 ] && { echo "flatfail $k ${seeds[$k]}" > "$C/RESULT"; return 0; }
  done
  echo "dropped" > "$C/RESULT"
}

while read -r tag i s a1 a2 n; do
  case "$tag" in
    MAIN) ( chain main "$i" "$n" "$FLUX_MAIN" "$s" "$a1" "$a2" ) & ;;
    SUPP) ( chain supp "$i" "$n" "$FLUX_SUPP" "$s" "$a1" "$a2" ) & ;;
  esac
done < "$B/receipts/d_SEEDS.txt"
wait

echo "results:"
for t in main supp; do
  echo "$t: $(cut -d' ' -f1 "$B"/d/gen/$t/c*/RESULT | sort | uniq -c | tr '\n' ' ')"
done
echo "non-zero attempts:"
grep -H -v $'\t0$' "$B"/d/gen/*/c*/attempts.tsv | head -40
: > "$B/d/native_main.txt"
: > "$B/d/native_supp.txt"
for t in main supp; do
  for c in "$B"/d/gen/$t/c*; do
    read -r st k s < "$c/RESULT"
    [ "$st" = ok ] && echo "$c/a$k/flat5d.root" >> "$B/d/native_$t.txt"
  done
done
wc -l "$B/d/native_main.txt" "$B/d/native_supp.txt"
/usr/bin/python3.11 "$B/receipts/noatime_sha.py" $(cat "$B/d/native_main.txt" "$B/d/native_supp.txt") \
  | awk '{print $1"  "$2}' > "$B/d/native_pins.sha256"
wc -l < "$B/d/native_pins.sha256"
echo "end $(date -u +%FT%TZ)"
