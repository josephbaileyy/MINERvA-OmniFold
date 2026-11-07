# stat-only: paths for the prologue policy config; reads no file content
hostname; date -u +%FT%TZ
M=/pscratch/sd/j/josephrb/MINERvA-OmniFold
ls -ld $M/MINERvA101/opt/lib/data $M/MINERvA101/opt/include $M/MINERvA101/opt/lib $M/MINERvA101/opt/etc/MParamFiles 2>&1
readlink -f $M/MINERvA101/opt/lib/data
ls -la $M/MINERvA101/opt/lib/data/ 2>&1 | head -20
find $M -maxdepth 6 -type d -name MATFluxAndReweightFiles 2>/dev/null
find /pscratch/sd/j/josephrb -maxdepth 5 -type d -name MATFluxAndReweightFiles 2>/dev/null | head
ls -l $M/MINERvA101/MAT/PlotUtils/FluxReweighter.cxx 2>&1
grep -n "MPARAMFILES\|PLOTUTILSROOT" $M/MINERvA101/opt/bin/setup_MAT.sh $M/MINERvA101/opt/bin/setup.sh $M/setup_salloc_env.sh 2>/dev/null | head -20
ls -ld /global/homes/j/josephrb/.conda/envs/root_6_28; readlink -f /global/homes/j/josephrb/.conda/envs/root_6_28
ls -ld /pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/ER/xsec.root /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root $M/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt /pscratch/sd/j/josephrb/cov2d-run-20261104 /pscratch/sd/j/josephrb/fd-rpd-20261103/dumps 2>&1
ls -d /pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/S1_*/xsec.root | wc -l
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' | awk -F'|' '$2 ~ /^cov2d-/'
