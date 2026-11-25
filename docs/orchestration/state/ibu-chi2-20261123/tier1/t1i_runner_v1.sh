#!/bin/bash
# Runs inside `salloc -q interactive` (job ibuchi_t1i). The director's conditions 2-3: hostname, sha256sum of every
# approved file just before use, then t1_t1.sbatch (its own srun steps, 64/1/1/1) and rebuild.py (srun -n1 -c 32
# --mem=96G, rebuild.sbatch's environment), in that order. Writes only under the lane root.
set -o pipefail
R=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123
echo "[t1i] host $(hostname) job=$SLURM_JOB_ID start $(date -u +%FT%TZ)"
case "$(hostname)" in login*) echo "[t1i] REFUSED: on a login node"; exit 2;; esac
cd $R
sha256sum scripts/rebuild.py scripts/rebuild.sbatch scripts/t1_t1.sbatch \
  tier1/deploy_old/2d-unfolding/re2/re2_driver.py tier1/deploy_old/2d-unfolding/ref_c2c1/config.json \
  tier1/deploy_e/2d-unfolding/re2/re2_driver.py tier1/deploy_e/2d-unfolding/ref_c2c1/config.json
want="ecde3a27dbf3d39f34c203400f16248fbad9fea20f1889f389631bfb79df6378 54f00d401fe3712ef6c5f5edc5b559e1c00972bac3ef3756f07db3db13d371a2 33d3eff3474b1cab2d118e9150142862bf6a553c106c4792c5c6bd751657bf12 938c53c5a018d20f5b148f6bdc2949e987a60085c5d0b7913ccdd5bb438b5a3b 58e96b87b7439547b234dad7438e592b4cc545f6dcb416ee79661e77ad2d3d04 677ac75f1d171ca7d71223f62bf3426f056e41b1b6cc8bfd433d49528a1371e8 cf44267e91afe3571a84caf3a4084d0a0ac229f0bdb89e9f9d55432110ed677d"
got=$(sha256sum scripts/rebuild.py scripts/rebuild.sbatch scripts/t1_t1.sbatch tier1/deploy_old/2d-unfolding/re2/re2_driver.py tier1/deploy_old/2d-unfolding/ref_c2c1/config.json tier1/deploy_e/2d-unfolding/re2/re2_driver.py tier1/deploy_e/2d-unfolding/ref_c2c1/config.json | awk '{print $1}' | tr '\n' ' ' | sed 's/ $//')
[ "$got" = "$want" ] || { echo "[t1i] REFUSED: a hash differs"; exit 2; }
for p in tier1/units_old tier1/units_e products/rebuild; do [ ! -e $p ] || { echo "[t1i] REFUSED: $p exists"; exit 2; }; done
echo "[t1i] tier1 start $(date -u +%FT%TZ)"
bash scripts/t1_t1.sbatch > logs/t1i_tier1.out 2>&1; echo "[t1i] tier1 rc=$? $(date -u +%FT%TZ)"
echo "[t1i] rebuild start $(date -u +%FT%TZ)"
( set +u; source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh >/dev/null 2>&1
  srun -n1 -c 32 --mem=96G /usr/bin/time -v python3 $R/scripts/rebuild.py > $R/products/rebuild.json 2> $R/logs/t1i_rebuild.err )
echo "[t1i] rebuild rc=$? $(date -u +%FT%TZ)"
sha256sum $R/products/rebuild/rebuild.npz $R/products/rebuild.json 2>&1
echo "[t1i] end $(date -u +%FT%TZ)"
