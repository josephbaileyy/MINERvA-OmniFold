echo "host=$(hostname) $(date -u +%FT%TZ)"
X=/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL
for q in G1810a0211b-k250-e1000 AR2320i00000-k250-e1000; do
  echo "== $q"; ls -la $X/$q/data/ | head; head -c 1500 $X/$q/data/gxspl-NUsmall.xml; echo; echo "-- grep header-like lines"
  head -200 $X/$q/data/gxspl-NUsmall.xml | grep -niE "version|tune|genie|generated|date" | head -10
  cat $X/$q/data/README* 2>/dev/null | head -20
  ls $X/../ 2>/dev/null | head
done
ls /cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00.version/ 2>/dev/null
P=/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix
ls -la $P/phi_t.npz $P/phi_t.json; sha256sum $P/phi_t.npz
env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B -c "
import json,numpy as np
m=json.load(open('$P/phi_t.json')); print(list(m.keys()))
for k,v in m.items():
  s=json.dumps(v); print(k, s[:300])
z=np.load('$P/phi_t.npz'); print(z.files); e=z['edges']; print(len(e), e[0], e[-1], float(z['Phi_t']))
"
