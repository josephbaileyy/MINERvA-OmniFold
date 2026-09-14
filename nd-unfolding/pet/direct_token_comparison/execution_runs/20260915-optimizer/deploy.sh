set -euo pipefail
root=/pscratch/sd/j/josephrb/pet-optimizer-exec-20260915
[[ ! -e "$root" ]]
/usr/bin/time -p git clone --no-hardlinks /pscratch/sd/j/josephrb/pet-fp32-exec-20260914 "$root"
cd "$root"
git fetch /pscratch/sd/j/josephrb/pet-optimizer-incremental-20260915.bundle HEAD
git checkout --detach 98fde50e80958659045e385aad762f91ab0364c0
[[ -z "$(git status --porcelain)" ]]
[[ ! -e /pscratch/sd/j/josephrb/pet-optimizer-output-20260915 ]]
/usr/bin/python3.11 - <<'PY'
from pathlib import Path
import hashlib,json
b=Path('nd-unfolding/pet/direct_token_comparison')
a=b/'optimizer-authorization.json'
assert hashlib.sha256(a.read_bytes()).hexdigest()=='59822b41231f026cda5e600fb3597dbbc789be2b70cad3e6e80f92f1d18c702c'
r=json.loads(a.read_text());m=b/'optimizer-manifest.json'
assert hashlib.sha256(m.read_bytes()).hexdigest()==r['manifest_sha256']
for name,sha in json.loads(m.read_text())['files'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha,name
print('AUTHORIZATION AND ALL MANIFEST HASHES VERIFIED')
PY
du -sk "$root" /pscratch/sd/j/josephrb/pet-optimizer-incremental-20260915.bundle
sbatch --test-only --output=/pscratch/sd/j/josephrb/pet-optimizer-20260915.slurm.log nd-unfolding/pet/direct_token_comparison/sbatch_optimizer_diagnostic.sh "$root" /pscratch/sd/j/josephrb/pet-direct-token-runtime-20260911 /pscratch/sd/j/josephrb/pet-optimizer-output-20260915 98fde50e80958659045e385aad762f91ab0364c0 "$root/nd-unfolding/pet/direct_token_comparison/optimizer-authorization.json" 59822b41231f026cda5e600fb3597dbbc789be2b70cad3e6e80f92f1d18c702c
