# Running the Gate-4 PET training on NCSA Delta (Perlmutter shutdown 2026-07-22 → 08-03)

Step-by-step to train the headline FPS PET nominal on Delta A100x4 while
Perlmutter is down. Delta's A100s match the Perlmutter training baseline, so this
is the scientifically preferable off-site target (an H100 port would change the
GPU-nondeterminism baseline of the publication nominal).

**Scientific intent (do not lose it in the port).** This is the publication
nominal. Keep the recipe frozen (`--niter 5 --epochs 8`, full stats
`--max-events 40000000`), run one **matched repeat** (same recipe, same
`--seed`) to bound GPU nondeterminism, and record in `RUNS.tsv` that both ran on
Delta A100 (cluster + GPU type are provenance). Nothing here relaxes the Gate-4
launch authorization — you are choosing to run it manually off-cluster.

Companion launcher: `sbatch_pet_train_fps_delta.sh` (this directory).

---

## Step 0 — Verify access and Globus (do first; ~15 min)
1. `ssh <ncsa_user>@login.delta.ncsa.illinois.edu` succeeds (NCSA identity + MFA).
2. `source /projects/bhvk/setup.sh && accounts` shows remaining GPU-hours. One
   full train ≈ 8 h × 4 GPU = **32 GPU-hr**; nominal + matched repeat ≈ 64 GPU-hr
   (~6% of the 1000-hr group pool). Confirm headroom and coordinate with the group.
3. In the Globus web app (`app.globus.org`), confirm you can see both the
   **NERSC DTN** and **NCSA Delta** collections (authenticate each once).

## Step 1 — Get the code on Delta (~5 min)
```bash
cd $HOME
git clone git@github.com:josephbaileyy/MINERvA-OmniFold.git   # or https://
cd MINERvA-OmniFold && git log --oneline -1     # expect b03ed56 or later
```
The clone brings the launcher, `pet/`, and the vendored `omnifold_nn/` PET
package. It does **not** bring data (not in git) — that's Step 3.

## Step 2 — Environment: squirrel + horovod (the one platform-specific step)
```bash
source /projects/bhvk/setup.sh                  # activates the squirrel conda env (tensorflow)
python -c "import tensorflow as tf; print('TF', tf.__version__)"
python -c "import horovod.tensorflow as hvd; print('HVD', hvd.__version__)"   # target: 0.28.x
```
- **If horovod imports:** you're done — go to Step 2b.
- **If horovod is missing** (likely, and the main porting risk): don't pip-install
  into the shared squirrel env. Make a private venv layered on it, or use a
  container. Venv route:
  ```bash
  python -m venv --system-site-packages $HOME/petenv && source $HOME/petenv/bin/activate
  module load cudnn/cuda12 cudatoolkit           # CUDA/NCCL for the build
  HOROVOD_WITH_TENSORFLOW=1 HOROVOD_GPU_OPERATIONS=NCCL \
    pip install --no-cache-dir horovod==0.28.1
  python -c "import horovod.tensorflow as hvd; print(hvd.__version__)"
  ```
  If the source build fights the toolchain, fall back to the NGC TensorFlow
  container (ships horovod) via apptainer — see Delta docs "containers". If you
  use a venv/container, `source` it in the launcher in place of / after
  `setup.sh`.

**Step 2b — put `omnifold` on the path** (sidesteps the hardcoded `_REPO =
/pscratch/...` in `pet/minerva_pet_dataloader.py:42`):
```bash
pip install -e $HOME/MINERvA-OmniFold/omnifold_nn
python -c "from omnifold import MultiFold, PET, MLP, DataLoader; print('omnifold ok')"
```

## Step 3 — Transfer the training input (Globus, CFS → Delta)
Source is CFS (stays up through the shutdown), so this works even during the
July 22–24 DTN gap. Web app: left = **NERSC DTN** →
`/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/pet_inputs`;
right = **NCSA Delta** → `/work/nvme/bhvk/<user>/pet_inputs`. Enable
"verify file integrity". You need only `of_inputs_pc_fps_xps2.npz` (9 GB) for the
nominal; grab `of_inputs_pc.npz` too if you want the base/closure. CLI form:
```bash
globus login
NERSC=$(globus endpoint search "NERSC DTN"  --jq 'DATA[0].id' -F unix)
DELTA=$(globus endpoint search "NCSA Delta" --jq 'DATA[0].id' -F unix)
globus transfer --verify-checksum \
  "$NERSC:/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/pet_inputs/of_inputs_pc_fps_xps2.npz" \
  "$DELTA:/work/nvme/bhvk/$USER/pet_inputs/of_inputs_pc_fps_xps2.npz"
```
Verify against the staged manifest: compare `sha256sum` of the landed file with
the matching line in the stage's `SHA256SUMS`. Also drop a backed-up copy in
Delta `$HOME` (100 GB, backed up) since `/work` is not.

## Step 4 — Build the memmap (once, ~10 min, CPU)
The 4-GPU stride-loader reads a `.npy` memmap dir, not the npz (npz can't mmap).
Rebuild it on Delta from the npz (19 GB output):
```bash
cd $HOME/MINERvA-OmniFold/nd-unfolding
ln -sf /work/nvme/bhvk/$USER/pet_inputs/of_inputs_pc_fps_xps2.npz of_inputs_pc_fps_xps2.npz
srun --account=bhvk-delta-cpu --partition=cpu --nodes=1 --ntasks=1 \
     --cpus-per-task=16 --mem=64g --time=00:30:00 \
     python3 pet/npz_to_npy.py --inputs of_inputs_pc_fps_xps2.npz --out of_inputs_pc_fps_xps2_npy
ls -sh of_inputs_pc_fps_xps2_npy/     # 8 .npy files (~19 GB)
```
(Put the memmap on `/work/nvme` for speed if `$HOME` quota is tight — symlink it
into `nd-unfolding/`.)

## Step 5 — Submit the training
```bash
cd $HOME/MINERvA-OmniFold/nd-unfolding
# fast sanity first (10M events, ~2 h): confirms env/GPUs/omnifold before the full run
sbatch --time=03:00:00 --export=ALL,TRAIN_EVENTS=10000000,SEED=101 sbatch_pet_train_fps_delta.sh
# full nominal (40M events, ~8 h):
sbatch sbatch_pet_train_fps_delta.sh
# matched repeat (same recipe/seed, bounds GPU nondeterminism):
sbatch --export=ALL,SAVE_WEIGHTS=products/pet/pet_weights_fps_xps2_delta_s101_rep.npz sbatch_pet_train_fps_delta.sh
```
Edit `REPO`/`DATA` at the top of the launcher if your layout differs, and confirm
the partition/cores/mem match your A100x4 nodes (`sinfo -s | grep A100`).

## Step 6 — Monitor and retrieve
```bash
squeue --me
tail -f pet_train_fps_delta_<jobid>.out    # rank-0 prints per-iteration progress
```
Output is `products/pet/pet_weights_fps_xps2_delta_s101.npz` (small, ~MBs). When
done, Globus it **back to CFS**
(`/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/results/`) so it's
durable and the Perlmutter orchestrator can pick it up after the 08-03 restore.

## After the restore (Perlmutter)
Pull the Delta-trained weights from CFS into
`nd-unfolding/products/pet/`, record the Delta run(s) in `RUNS.tsv` (cluster =
Delta A100, seeds, matched-repeat spread), and hand to the downstream extraction
(`extract_cross_section_nd` + GBDT completeness) exactly as the Perlmutter path
would. The Gate-4 launch-code gate the orchestrator built still governs
promotion; a Delta-trained nominal is evidence into that gate, not a bypass of it.
