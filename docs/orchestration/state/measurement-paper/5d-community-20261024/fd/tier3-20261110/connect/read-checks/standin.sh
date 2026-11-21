#!/bin/bash
# Stand-in run of t3p_read_connect.sh inside a Debian container. Stubs: sacct (states from $ST_*), and git's clone URL
# only (rewritten to a --shared clone of the read-only host object store); everything else is the real tool.
# Variant: $1 = ok | incomplete | bail_running | stale_sums
V=${1:?variant}
M=8bb4e3b0e1028d960e39de0c202569a08a1218a0
OUT=/pscratch/sd/j/josephrb/t3p-20261121
git config --global --add safe.directory '*'
mkdir -p /stub /root/.conda/envs/root_6_28/bin
ln -sf /usr/local/bin/python3 /root/.conda/envs/root_6_28/bin/python3
cat > /stub/git <<'EOF'
#!/bin/bash
if [ "$1" = clone ]; then dest=${@: -1}; exec /usr/bin/git clone -q --shared /hostgit "$dest"; fi
exec /usr/bin/git "$@"
EOF
FLOOR_STATE=COMPLETED; [ "$V" = bail_running ] && FLOOR_STATE=RUNNING
cat > /stub/sacct <<EOF
#!/bin/bash
args="\$*"
row() { case "\$1" in 61726250) echo "61726250|t3p_dry|COMPLETED";; 61728686) echo "61728686|t3p_q3|COMPLETED";; 61731751) echo "61731751|t3p_floor|$FLOOR_STATE";; esac; }
if [[ "\$args" == *"-j "* ]]; then
  id=\$(echo "\$args" | sed 's/.*-j \([0-9]*\).*/\1/')
  if [[ "\$args" == *"-o State"* ]]; then row \$id | cut -d'|' -f3; else echo "\$(row \$id)|0:0|2026-11-21T06:12:44|2026-11-21T09:40:31|12467|1"; fi
else row 61726250; row 61728686; row 61731751; echo "99999|cov2d_other|COMPLETED"; fi
EOF
chmod +x /stub/git /stub/sacct
export PATH=/stub:$PATH HOME=/root
# ---- the fixture: test_t3p's planted EndToEnd run, built from a source clone at M_V1, at the real OUT path
/usr/bin/git clone -q --shared /hostgit /src && /usr/bin/git -C /src -c advice.detachedHead=false checkout -q $M || exit 50
mkdir -p "$(dirname $OUT)"
( cd /src && python3 -B - "$OUT" <<'EOF'
import sys
from pathlib import Path
for p in ("nd-unfolding/tier3", "nd-unfolding/prior_retention", "nd-unfolding"):
    sys.path.insert(0, p)
import test_t3p as TT
t = TT.EndToEnd("test_planted_classes"); t.setUp()
t.run = Path(sys.argv[1]); t.build(t.plant)
print("fixture built at", t.run)
EOF
) || exit 51
mkdir -p $OUT/logs && cd $OUT || exit 52
for f in connect-dry.log connect-q3.log connect-floor.log t3p_dry_61726250.out t3p_q3_61728686.out t3p_floor_61731751.out; do echo "stand-in $f" > logs/$f; done
echo '[]' > manifest.json; printf 'cov2d\nll5d_\n' > fence.txt
for j in dry q3 floor; do find runs -type f -name '*.npz' -print0 | sort -z | xargs -0 sha256sum > log-$j/SHA256SUMS; done
[ "$V" = incomplete ] && echo '{"pass": false}' > log-q3/pair.json
[ "$V" = stale_sums ] && sed -i '1s/^./0/' log-floor/SHA256SUMS
echo "== variant $V; npz $(find runs -name '*.npz' | wc -l)"
cp /connect/t3p_read_connect.sh /dev/shm/t3pr.1.sh
WEND=$(( $(date +%s) + 900 ))
bash /dev/shm/t3pr.1.sh /dev/shm/t3pr.1.sh $WEND "cov2d,ll5d_,ibukt,rpd_,prr_,e96,ens1_"
rc=$?
echo "== script rc=$rc; self copy left: $(ls /dev/shm/t3pr.1.sh 2>&1 | head -1)"
echo "== the connect log"; cat $OUT/logs/connect-read.log 2>&1
echo "== done: $(cat $OUT/logs/connect-read.done 2>&1)"
echo "== OUT top level"; ls $OUT
mkdir -p /out/$V
for f in fetch-read.tar logs/connect-read.log logs/connect-read.done; do [ -e $OUT/$f ] && cp $OUT/$f /out/$V/; done
exit 0
