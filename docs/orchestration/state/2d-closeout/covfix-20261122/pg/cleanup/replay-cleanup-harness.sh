set -u
R=/pscratch/sd/j/josephrb/covfix-pg
mk() {
  [ -e /pscratch/sd ] && chmod -R u+w /pscratch/sd; rm -rf /pscratch/sd; mkdir -p $R/products/sub $R/other
  echo keep > $R/products/sub/f; echo keep > $R/other/g; chmod -R a-w $R/products
  for t in replay-20261126T205214Z replay-20261126T211924Z; do
    mkdir -p $R/$t/deploy/a $R/$t/run; echo x > $R/$t/deploy/a/file; echo y > $R/$t/run/log
    ln -s $R/products/sub/f $R/$t/run/link-into-products; ln -s $R/products $R/$t/run/dirlink
    chmod -R a-w $R/$t/deploy
  done
}
echo "### case A: normal"; mk; python3.11 -I -S -B - < /t/rc-test.py | tail -3; echo "rc=${PIPESTATUS[0]}"
ls $R; cat $R/products/sub/f; ls $R/products
echo "### case B: a target is a symlink"; mk; chmod -R u+w $R/replay-20261126T211924Z; rm -rf $R/replay-20261126T211924Z; ln -s $R/other $R/replay-20261126T211924Z
python3.11 -I -S -B - < /t/rc-test.py | tail -2; echo "rc=${PIPESTATUS[0]}"; ls $R; ls $R/other
echo "### case C: a target missing"; mk; chmod -R u+w $R/replay-20261126T205214Z; rm -rf $R/replay-20261126T205214Z; python3.11 -I -S -B - < /t/rc-test.py | tail -1; ls $R
echo "### case D: an unreadable dir inside"; mk; chmod 000 $R/replay-20261126T205214Z/run; python3.11 -I -S -B - < /t/rc-test.py | tail -1; ls $R
echo "### case E: a process cwd inside a target"; mk; (cd $R/replay-20261126T211924Z/run && sleep 30) & sleep 1; python3.11 -I -S -B - < /t/rc-test.py | tail -1; ls $R; kill %1
