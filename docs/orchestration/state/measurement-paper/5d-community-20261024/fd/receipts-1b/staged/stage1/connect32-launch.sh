# 1B staged, stage 1, connect 32's launcher (run locally from this directory). The receipt makes about four passes over
# the bank, too long to hold an ssh session open, so the script is placed in a new $W1 and run detached on the login
# node; the polls read only the script's own log. No -n on the placing ssh: it reads the script from stdin.
W1=/pscratch/sd/j/josephrb/fd-1b-staged-20261102/stage1
case "${1:?place|launch|poll}" in
  place)  ssh saul.nersc.gov "test ! -e $W1 && mkdir $W1 $W1/logs && cat > $W1/logs/connect32-s1-0.sh && sha256sum $W1/logs/connect32-s1-0.sh && hostname" < connect32-s1-0.sh ;;
  launch) ssh saul.nersc.gov "test ! -e $W1/logs/connect32-s1-0.out && cd $W1/logs && { setsid nohup bash $W1/logs/connect32-s1-0.sh > $W1/logs/connect32-s1-0.out 2>&1 < /dev/null & } ; echo launched host=\$(hostname)" ;;
  poll)   ssh saul.nersc.gov "tail -4 $W1/logs/connect32-s1-0.out; grep -c '^end=' $W1/logs/connect32-s1-0.out" ;;
esac
