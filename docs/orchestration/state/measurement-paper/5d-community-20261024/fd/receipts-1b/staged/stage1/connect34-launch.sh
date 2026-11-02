# 1B staged, stage 1, connect 34's launcher (run locally from this directory), as connect 32's: place the script and
# n1_attrib.py in a new $W1/attrib, run detached on the login node, poll only the script's own log. No -n on the
# placing ssh: it reads from stdin.
A=/pscratch/sd/j/josephrb/fd-1b-staged-20261102/stage1/attrib
case "${1:?place|launch|poll}" in
  place)  ssh saul.nersc.gov "test ! -e $A && mkdir $A && cat > $A/connect34-attrib.sh && sha256sum $A/connect34-attrib.sh && hostname" < connect34-attrib.sh &&
          ssh saul.nersc.gov "test -d $A && test ! -e $A/n1_attrib.py && cat > $A/n1_attrib.py && sha256sum $A/n1_attrib.py" < attrib/n1_attrib.py ;;
  launch) ssh saul.nersc.gov "test ! -e $A/connect34-attrib.out && cd $A && { setsid nohup bash $A/connect34-attrib.sh > $A/connect34-attrib.out 2>&1 < /dev/null & } ; echo launched host=\$(hostname)" ;;
  poll)   ssh saul.nersc.gov "tail -4 $A/connect34-attrib.out; grep -c '^end=' $A/connect34-attrib.out" ;;
esac
