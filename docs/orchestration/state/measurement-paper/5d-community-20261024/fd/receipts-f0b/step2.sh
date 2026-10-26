set -u
P=/pscratch/sd/j/josephrb; B=$P/fd-f0b-20261026; D=$B/deploy/c4396756
T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024
grep -q "^tests rc=0$" $B/logs/deploy.log || { echo "STOP: step 1 not clean"; exit 9; }
test ! -e $B/preserve || { echo "STOP: preserve exists"; exit 9; }
hpssquota > $B/logs/hpssquota-before.txt 2>&1
hsi -q "ls -d /home/j/josephrb/mnv-5d-cresp-20261026" > $B/logs/hsi-precheck.txt 2>&1
cat $B/logs/hpssquota-before.txt | grep HPSS; cat $B/logs/hsi-precheck.txt
grep -q HPSS_ENOENT $B/logs/hsi-precheck.txt || { echo "STOP: HPSS target exists"; exit 9; }
used=$(grep 'usage on HPSS' $B/logs/hpssquota-before.txt | awk -F'|' '{gsub(/[ GiB]/,"",$3); gsub(/[ GiB]/,"",$4); print $4-$3}')
echo "hpss_free_gib $used"
awk -v f="$used" 'BEGIN{exit !(f>=1)}' || { echo "STOP: HPSS free < 1 GiB"; exit 9; }
echo "preserve start $(date -u +%FT%TZ) $(hostname)" > $B/logs/preserve-start.txt
cd $B && setsid nohup bash -c "timeout 375 bash $D/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/stage0_preserve.sh \
  $T/fd/CRESP-PRESERVE-INVENTORY.sha256 $B/preserve /home/j/josephrb/mnv-5d-cresp-20261026; echo rc=\$?" \
  > $B/logs/preserve.out 2>&1 < /dev/null &
echo launched
