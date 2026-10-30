# 5B step 9 (section 2.7; binding condition 4): the small products and the ALL dumps to HPSS, login node, 0 node-h.
set -o pipefail
B=/pscratch/sd/j/josephrb/fd-ct-5b-20261030; D=$B/deploy/2c960659; W=$B/preserve; H=/home/j/josephrb/mnv-5d-ct-5b-20261030
[ -e "$W" ] && { echo "STOP: $W exists"; exit 2; }
mkdir -p "$W"
ls $B/unf/ALL/*.npz $B/unf/PA/*.npz $B/unf/PB/*.npz $B/unf/PC/*.npz $B/truth/*.npz $B/inputs/check_*.json \
   $B/merged/*.root.json $B/control/fd_ct_5b_precheck.json $B/control/fd_ct_5b_control.json $B/fd_ct_5b_periods.json \
   $B/dumps/lat_ALL.npz $B/dumps/lat_ALL_bkg.npz | sort > "$W/files.list"
n=$(wc -l < "$W/files.list"); [ "$n" -eq 51 ] || { echo "STOP: $n files, 51 declared (34 unfolds, 4 truths, 4 checks, 4 merge receipts, 2 controls, the readout, 2 ALL dumps)"; exit 3; }
xargs sha256sum < "$W/files.list" > "$W/INVENTORY.sha256"
bash $D/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/stage0_preserve.sh "$W/INVENTORY.sha256" "$W" "$H"
echo "preserve rc=$?"
