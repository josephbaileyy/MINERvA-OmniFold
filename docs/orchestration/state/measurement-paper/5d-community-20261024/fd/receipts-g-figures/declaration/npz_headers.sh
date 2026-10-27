# The two pinned products' sizes, sha256 and key names and shapes: zip headers only, no array value read.
hostname; date -u +%FT%TZ
for f in /pscratch/sd/j/josephrb/s1-20261024/s1_assembly.npz /pscratch/sd/j/josephrb/cresp-20261026/out/cresp.npz; do
  stat -c '%s %n' $f; sha256sum $f
done
env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B -c "
import zipfile, numpy.lib.format as fmt
for f in ('/pscratch/sd/j/josephrb/s1-20261024/s1_assembly.npz', '/pscratch/sd/j/josephrb/cresp-20261026/out/cresp.npz'):
    with zipfile.ZipFile(f) as z:
        out = []
        for n in z.namelist():
            with z.open(n) as fh:
                v = fmt.read_magic(fh); shape, order, dtype = fmt._read_array_header(fh, v)
            out.append((n[:-4], shape, str(dtype)))
    print(f, [o for o in out if o[0] in ('f', 'C_e', 'C_model_abs', 'C_total', 'C_resp', 'C_total_resp')], len(out), 'keys')
"
