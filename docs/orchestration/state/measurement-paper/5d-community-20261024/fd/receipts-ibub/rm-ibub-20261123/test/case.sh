#!/bin/bash
# one case of the removal script, in a container: $1 = case name
V=$1; U=/pscratch/sd/j/josephrb; P=$U/ibub-20261123
useradd -M josephrb 2>/dev/null; useradd -M other 2>/dev/null
mkdir -p /stub $U/ibub-20261124/logs $U/cov2d-run-20261104 $U/cov2d-2a $U/rpd-reco-p0-20261123
echo keep > $U/ibub-20261124/logs/keep.txt; echo keep > $U/cov2d-run-20261104/keep.txt
mkdir -p $P/deploy/.git $P/stage $P/logs $P/slurm
printf 'abc' > $P/stage/a.root; printf 'hello\n' > $P/logs/connect-run.log; ln -s /etc/hostname $P/logs/alink
chown -R josephrb $P $U/ibub-20261124
ROWS="61914825|ibub_run|CANCELLED by 112498\n61800000|rpd_flux2|COMPLETED\n61870000|unrelated_lane|RUNNING"
case $V in
  symlink)   mv $P $U/real-old && ln -s $U/real-old $P ;;
  notdir)    rm -rf $P && echo x > $P && chown josephrb $P ;;
  owner)     chown other $P ;;
  ancestor)  mv /pscratch/sd/j/josephrb /pscratch/sd/j/realjr && ln -s /pscratch/sd/j/realjr /pscratch/sd/j/josephrb ;;
  running)   ROWS="$ROWS\n61920000|ibub_run|RUNNING" ;;
  pending)   ROWS="$ROWS\n61920000|ibub_run|PENDING" ;;
  notcancel) ROWS="61914825|ibub_run|COMPLETED\n61800000|rpd_flux2|COMPLETED" ;;
  norow)     ROWS="61800000|rpd_flux2|COMPLETED" ;;
  malformed) ROWS="$ROWS\ngarbage line" ;;
  sacctfail) ROWS=FAIL ;;
esac
printf '#!/bin/bash\n[ "%s" = FAIL ] && { echo "sacct: error: stub" >&2; exit 1; }\nprintf "%s\\n"\n' "$ROWS" "$ROWS" > /stub/sacct
chmod +x /stub/sacct; export PATH=/stub:$PATH
if [ "$V" = arg ]; then bash /t/rm.sh extra; else bash /t/rm.sh; fi; echo "exit=$?"
echo "after: old=$( [ -e $P ] || [ -L $P ] && echo present || echo gone ) new=$(cat $U/ibub-20261124/logs/keep.txt 2>&1) cov2d=$(cat $U/cov2d-run-20261104/keep.txt 2>&1) 2a=$( [ -d $U/cov2d-2a ] && echo kept) rpd=$( [ -d $U/rpd-reco-p0-20261123 ] && echo kept) hostname=$(cat /etc/hostname >/dev/null && echo kept)"
