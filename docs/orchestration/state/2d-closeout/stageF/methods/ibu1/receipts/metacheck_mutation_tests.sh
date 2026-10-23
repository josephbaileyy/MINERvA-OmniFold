#!/bin/bash
# IBU-1: ibu1_metacheck.py in both directions. A baseline of real products must pass; each of five mutations must
# fail. Run on Perlmutter from /pscratch/sd/j/josephrb/ibu1-20261022 with the deploy environment sourced. Writes only
# to a temporary directory under kb1/, removed at the end.
set -u
D=deploy/7ea30e3d/nd-unfolding/ibu1
T=$(mktemp -d -p "$PWD/kb1" mtest.XXXX)
mkdir -p "$T/p" "$T/l"
echo "# ibu1_metacheck.py $(sha256sum kb1/ibu1_metacheck.py | cut -c1-64): mutation tests, $(date -u +%FT%TZ)"
run() {
  python3 kb1/ibu1_metacheck.py --code $D/ibu1.py --config $D/config.json --products "$T/p" --logs "$T/l" \
    --jobs A=60130813,B1=60130899,C=60140287 > "$T/out.json"
  local rc=$?
  python3 -c "
import json, os
d = json.load(open('$T/out.json'))
print('$1: rc=$rc pass=%s failing=%s refusals=%s guard_nonzero=%s' % (d['pass'], [os.path.basename(f) for f in d['failing']],
      {k: len(v['refusals']) for k, v in d['jobs'].items()}, {k: v['guard_outside_expect_root_nonzero'] for k, v in d['jobs'].items()}))"
}
reset() {
  rm -f "$T"/p/* "$T"/l/*
  cp run/products/N_gibuu_s301000.npz run/products/D_P.npz "$T/p/"
  cp run/logs/task-N_gibuu_301000-60130899.log run/logs/task-D_P-60130813.log "$T/l/"
}
reset; run "baseline (expect pass)"
python3 -c "
import json, numpy as np
f = '$T/p/N_gibuu_s301000.npz'; z = np.load(f); m = json.loads(str(z['meta'])); m['truth'] = 'nominal'
np.savez_compressed(f, **{k: z[k] for k in z.files if k != 'meta'}, meta=json.dumps(m))"
run "wrong truth (expect fail)"
reset; cp run/products/N_gibuu_s301050.npz "$T/p/"; run "unattributed product (expect fail)"
reset; echo "refusing: test" >> "$T/l/task-N_gibuu_301000-60130899.log"; run "refusal line (expect fail)"
reset; sed -i "s/outside_expect_root=0/outside_expect_root=1/" "$T/l/task-D_P-60130813.log"; run "guard outside root (expect fail)"
reset; cp "$T/l/task-N_gibuu_301000-60130899.log" "$T/l/task-N_gibuu_301000-60140287.log"; run "two writers (expect fail)"
rm -rf "$T"
