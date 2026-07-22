# Running the Gate-4 PET training on NCSA Delta (Perlmutter shutdown 2026-07-22 → 08-03)

Step-by-step to train the headline FPS PET nominal on Delta A100x4 while
Perlmutter is down, via an **Apptainer/NGC TensorFlow container**.

**Why a container (not squirrel).** Delta's shared `squirrel` env is TF 2.21 /
Python 3.12 with no horovod, and horovod 0.28.1 won't build against TF 2.21. The
NGC TF container ships TF 2.14 + horovod 0.28.1 + a consistent CUDA/NCCL — close
to Perlmutter's TF 2.15 baseline and known-good. This Delta run is the
**during-shutdown result**; the authoritative TF-2.15 nominal is retrained on
Perlmutter after the 08-03 restore under the Gate-4 gate. Record TF 2.14 + Delta
A100 in `RUNS.tsv` provenance.

**Scientific intent.** Publication nominal: keep the recipe frozen
(`--niter 5 --epochs 8`, full stats `--max-events 40000000`), run one matched
repeat (same recipe/seed) to bound GPU nondeterminism, record provenance. You are
choosing to run it manually off-cluster; the Gate-4 launch gate still governs
final promotion.

Launcher: `sbatch_pet_train_fps_delta.sh` (this directory).

---

## Step 0 — Access + budget (~15 min)
1. `ssh <ncsa_user>@login.delta.ncsa.illinois.edu` (NCSA identity + MFA).
2. `source /projects/bhvk/setup.sh && accounts` — one train ≈ 8 h × 4 GPU =
   32 GPU-hr; nominal + matched repeat ≈ 64 GPU-hr (~6% of the 1000-hr pool).
3. Confirm you can see the **NERSC DTN** and **NCSA Delta** collections in the
   Globus web app (`app.globus.org`).

## Step 1 — Code (~5 min)
```bash
cd $HOME && git clone git@github.com:josephbaileyy/MINERvA-OmniFold.git
cd MINERvA-OmniFold && git log --oneline -1     # expect the Delta-container commit or later
```

## Step 2 — Container + omnifold deps (one-time)
```bash
module load apptainer 2>/dev/null || true
apptainer pull $HOME/tf215.sif docker://nvcr.io/nvidia/tensorflow:24.01-tf2-py3
# sanity (the cuDNN/cuFFT "already registered" lines are harmless NGC noise):
apptainer exec --nv $HOME/tf215.sif python -c \
  "import horovod, tensorflow as tf; print('TF', tf.__version__, 'HVD', horovod.__version__)"   # TF 2.14.0 HVD 0.28.1
apptainer exec --nv $HOME/tf215.sif horovodrun --check-build                                    # TensorFlow[X], MPI[X], NCCL[X]
```
The image lacks two omnifold deps (`matplotlib`, `PyYAML`). Install them to a host
dir with the **container's own pip** (so the wheels match the container's Python
3.10), then put that dir on `PYTHONPATH` alongside the vendored `omnifold`.
**Pin `numpy<2`:** the image is numpy 1.x (TF 2.14 is built against it), but the
latest matplotlib drags in numpy 2.x, which would shadow and break the container's
TF once `petpkgs` is on `PYTHONPATH`.
```bash
apptainer exec --nv $HOME/tf215.sif pip install --target=$HOME/petpkgs "matplotlib<3.9" "numpy<2" PyYAML
REPO=$HOME/MINERvA-OmniFold
apptainer exec --nv --bind $REPO --env PYTHONPATH=$REPO/omnifold_nn:$HOME/petpkgs $HOME/tf215.sif \
  python -c "from omnifold import MultiFold, PET, MLP, DataLoader; print('omnifold ok')"        # expect: omnifold ok
```
(The `CUDA_ERROR_NO_DEVICE` warning on a login node is fine — no GPU there.)

## Step 3 — Transfer the training input (Globus, CFS → Delta)
Source is CFS (up through the shutdown), so this works even during the July 22–24
DTN gap. Web app: left **NERSC DTN** →
`/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/pet_inputs`; right
**NCSA Delta** → `/work/nvme/bhvk/<user>/pet_inputs`; enable "verify integrity".
You need `of_inputs_pc_fps_xps2.npz` (9 GB). Verify the landed file's `sha256sum`
against the stage's `SHA256SUMS`, and keep a copy in Delta `$HOME` (backed up;
`/work` is not).

## Step 4 — Build the memmap (once, in-container, ~10 min)
The 4-rank stride-loader reads a `.npy` memmap dir, not the npz. Build it inside
the container so numpy versions match:
```bash
cd $HOME/MINERvA-OmniFold/nd-unfolding
REPO=$HOME/MINERvA-OmniFold; DATA=/work/nvme/bhvk/$USER/pet_inputs
ln -sf $DATA/of_inputs_pc_fps_xps2.npz of_inputs_pc_fps_xps2.npz
srun --account=bhvk-delta-cpu --partition=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 \
     --mem=64g --time=00:30:00 \
  apptainer exec --bind $REPO,$DATA --env PYTHONPATH=$REPO/omnifold_nn:$HOME/petpkgs $HOME/tf215.sif \
    python3 pet/npz_to_npy.py --inputs of_inputs_pc_fps_xps2.npz --out of_inputs_pc_fps_xps2_npy
ls -sh of_inputs_pc_fps_xps2_npy/     # 8 .npy files (~19 GB)
```
The npz was written with numpy 2.0 on Perlmutter and the container has numpy 1.x;
plain float arrays load fine, but this step is where any format issue would
surface — confirm it prints the 8 files before the GPU run.

## Step 5 — Train
The launcher uses **one srun task** running `horovodrun -np 4` inside the
container (the container horovod has MPI, no Gloo; its own OpenMPI spawns 4 local
ranks over NVLink/NCCL — no host-MPI bootstrap). `minerva_pet_dataloader.py` reads
`OMPI_COMM_WORLD_*` for the data striding.
```bash
cd $HOME/MINERvA-OmniFold/nd-unfolding
# 5a. 1-GPU pipeline validation first (no MPI; ~fast at 1M): proves data+omnifold+save
srun --account=bhvk-delta-gpu --partition=gpuA100x4-interactive --nodes=1 --ntasks=1 \
     --gpus-per-node=1 --cpus-per-task=16 --mem=64g --time=00:30:00 \
  apptainer exec --nv --bind $HOME/MINERvA-OmniFold,/work/nvme/bhvk \
     --env PYTHONPATH=$HOME/MINERvA-OmniFold/omnifold_nn:$HOME/petpkgs $HOME/tf215.sif \
     python3 pet/minerva_pet_dataloader.py --inputs of_inputs_pc_fps_xps2.npz --mode pointcloud \
       --model pet --niter 1 --epochs 1 --max-events 1000000 --reweight-all --smoke \
       --save-weights products/pet/pet_smoke_delta.npz --memmap-dir of_inputs_pc_fps_xps2_npy

# 5b. 4-GPU fast check (10M, ~2 h)
sbatch --time=03:00:00 --export=ALL,TRAIN_EVENTS=10000000,SEED=101 sbatch_pet_train_fps_delta.sh
# 5c. full nominal (40M, ~8 h)
sbatch sbatch_pet_train_fps_delta.sh
# 5d. matched repeat
sbatch --export=ALL,SAVE_WEIGHTS=products/pet/pet_weights_fps_xps2_delta_s101_rep.npz sbatch_pet_train_fps_delta.sh
```
Confirm the partition/cores/mem match your A100x4 nodes (`sinfo -s | grep A100`).
If `horovodrun -np 4` errors on MPI startup, fall back to
`srun --mpi=pmix -n4 ... apptainer exec ... python3 ...` (no horovodrun); the
dataloader handles both rank sources.

## Step 6 — Retrieve
Output `products/pet/pet_weights_fps_xps2_delta_s101.npz` is small (~MBs). Globus
it **back to CFS**
(`/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/results/`) so it's
durable and the Perlmutter orchestrator can pick it up after 08-03.

## After the restore (Perlmutter)
Pull the Delta weights from CFS into `nd-unfolding/products/pet/`, record the
Delta run(s) in `RUNS.tsv` (cluster = Delta A100, **TF 2.14**, seeds, matched-
repeat spread), and feed the downstream extraction as the Perlmutter path would.
Retrain the authoritative nominal on Perlmutter (TF 2.15) under the Gate-4 gate;
the Delta result is cross-check/insurance, not the promoted nominal.
