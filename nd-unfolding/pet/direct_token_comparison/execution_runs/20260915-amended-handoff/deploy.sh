set -euo pipefail
root=/pscratch/sd/j/josephrb/pet-amended-exec-20260915
expected=$(cat /pscratch/sd/j/josephrb/pet-amended-commit-20260915.txt)
[[ ! -e "$root" ]]
git clone --no-hardlinks /pscratch/sd/j/josephrb/pet-optimizer-exec-20260915 "$root"
cd "$root"
git fetch /pscratch/sd/j/josephrb/pet-amended-execution-20260915.bundle HEAD
git checkout --detach "$expected"
[[ -z "$(git status --porcelain)" ]]
[[ ! -e /pscratch/sd/j/josephrb/pet-amended-output-20260915 ]]
/usr/bin/python3.11 - <<'PY'
from pathlib import Path
import hashlib,json
base=Path('nd-unfolding/pet/direct_token_comparison')
authority=base/'amended-execution-authorization.json'
assert hashlib.sha256(authority.read_bytes()).hexdigest()=='fc9dcb7dd5667701584de02adc62f3c30c48c00dd76c807e3667022f8030ca1a'
record=json.loads(authority.read_text());manifest=base/'amended-manifest.json'
assert hashlib.sha256(manifest.read_bytes()).hexdigest()==record['manifest_sha256']
for name,digest in json.loads(manifest.read_text())['files'].items():
 assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
print('AUTHORIZATION AND ALL MANIFEST HASHES VERIFIED')
PY
du -sk "$root" /pscratch/sd/j/josephrb/pet-amended-execution-20260915.bundle
sbatch --test-only --output=/pscratch/sd/j/josephrb/pet-amended-20260915.slurm.log nd-unfolding/pet/direct_token_comparison/sbatch_amended_calibration.sh "$root" /pscratch/sd/j/josephrb/pet-direct-token-runtime-20260911 /pscratch/sd/j/josephrb/pet-amended-output-20260915 "$expected" "$root/nd-unfolding/pet/direct_token_comparison/amended-execution-authorization.json" fc9dcb7dd5667701584de02adc62f3c30c48c00dd76c807e3667022f8030ca1a
