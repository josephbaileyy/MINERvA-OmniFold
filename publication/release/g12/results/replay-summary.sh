P=/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/pscratch/sd/j/josephrb/pub-release-20261006; A=/global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006
echo "host $(hostname) $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "replay_inference.py sha256 $(sha256sum $P/tools/replay_inference.py | cut -c1-64)"
echo "== frozen regenerated (default threads) vs recorded joint-evaluate.json $(sha256sum $A/stage7/joint/joint-evaluate.json | cut -c1-16)"
venv/bin/python -I $P/tools/replay_inference.py --npz out/frozen/inference_sufficient.npz --compare $A/stage7/joint/joint-evaluate.json | tail -1
echo "== recovery-union regenerated vs recorded resolved-evaluate.json $(sha256sum $A/recovery/resolved-evaluate.json | cut -c1-16)"
venv/bin/python -I $P/tools/replay_inference.py --npz out/recovery-union/inference_sufficient.npz --compare $A/recovery/resolved-evaluate.json | tail -1
echo "== frozen regenerated (OPENBLAS_NUM_THREADS=4) vs recorded"
venv/bin/python -I $P/tools/replay_inference.py --npz out/frozen-blas4/inference_sufficient.npz --compare $A/stage7/joint/joint-evaluate.json | tail -1
echo "done $(date -u +%Y-%m-%dT%H:%M:%SZ)"
