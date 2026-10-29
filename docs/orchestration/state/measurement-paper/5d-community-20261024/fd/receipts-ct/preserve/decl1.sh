set -u
P=/pscratch/sd/j/josephrb
echo "host=$(hostname) date=$(date -u +%FT%TZ)"
tail -4 $P/fd-ct-preserve-20261028/preserve.log
sha256sum $P/w2-recoil-20261006/w2b/unf/*.npz $P/tmp-playlist-term-20261016/out/playlist_term.npz $P/s5p-20260926/runs/s2/num/data/data_b-_j-.npz $P/s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz $P/cresp-20261026/out/cresp.npz $P/s1-20261024/s1_assembly.npz 2>&1
grep -h w2-recoil $P/fd-ct-preserve-20261028/INVENTORY.sha256
cat /global/cfs/cdirs/m3246/josephrb/2d-closeout-playlist-term-20261016/SHA256SUMS
grep -c . /global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/SHA256SUMS; grep 'w2b/unf' /global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/SHA256SUMS
echo "== product metas"
env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B - <<'PY'
import json, numpy as np, glob
for p in sorted(glob.glob('/pscratch/sd/j/josephrb/w2-recoil-20261006/w2b/unf/*.npz'))+['/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz','/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s1/unf/mp1s1_zero_b-_j-.npz']:
    z=np.load(p,allow_pickle=False); m=json.loads(str(z['meta']))
    print(p.split('/')[-1], sorted(z.files), {k:m.get(k) for k in ('schema','construction','truth','input_npz_sha256','bkg_dump_sha256','bootstrap_seed','jitter_seed','coords')})
z=np.load('/pscratch/sd/j/josephrb/tmp-playlist-term-20261016/out/playlist_term.npz',allow_pickle=False)
print('playlist_term', {k:z[k].shape for k in z.files})
for X in ('PA','PB','PC'): print(X,'e ptp',float(np.ptp(z['e_'+X])),'e mean',float(np.mean(z['e_'+X])))
z=np.load('/pscratch/sd/j/josephrb/s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz',allow_pickle=False); print('mnvtune', z.files)
PY
