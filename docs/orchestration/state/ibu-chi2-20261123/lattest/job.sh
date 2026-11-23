eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook 2>/dev/null)"; set +u; conda activate $HOME/.conda/envs/root_6_28
W=/pscratch/sd/j/josephrb/oflow-split-20261123
cd $W && srun -A m3246 -C cpu -q interactive -N 1 -c 64 -t 01:00:00 -J lattest-ibu /usr/bin/time -v python3 build.py > build.out 2> build.err
echo "srun rc=$?"; cat build.out; grep -E 'Elapsed|Maximum resident' build.err; tail -3 build.err | grep -v -E 'Elapsed|Maximum'
cd lat && sha256sum *.npz
