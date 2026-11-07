W=/pscratch/sd/j/josephrb/cov2d-crossterms-20261107
echo "utc=$(date -u +%FT%TZ) host=$(hostname)"
echo "== procs"; ps -u josephrb -o pid,etime,args | grep -E 'connect-x1|cov2d_readouts' | grep -v grep
echo "== staged"; ls -la /dev/shm/josephrb-cov2d-x1.sh 2>&1; sha256sum /dev/shm/josephrb-cov2d-x1.sh 2>&1
echo "== W"; ls -la $W 2>&1
echo "== log tail"; tail -25 $W/connect-x1.log 2>&1
echo "== squeue"; squeue -u josephrb -h -o '%i %j %T'
echo "node end"
