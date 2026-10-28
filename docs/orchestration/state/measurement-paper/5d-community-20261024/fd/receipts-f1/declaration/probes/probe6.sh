#!/bin/bash
echo "host=$(hostname) date=$(date -u +%FT%TZ)"
U=/cvmfs/larsoft.opensciencegrid.org/products
G=$U/genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof
ls $U/pythia/v6_4_28r
P=$(ls -d $U/pythia/v6_4_28r/*gcc930-prof* 2>/dev/null | head -1); echo "P=$P"; ls $P/lib 2>/dev/null | head
R=$U/root/v6_22_08d/Linux64bit+3.10-2.17-e20-p392-prof
L=$U/lhapdf/v6_3_0/Linux64bit+3.10-2.17-e20-p392-prof
X=$U/libxml2/v2_9_10a/Linux64bit+3.10-2.17
C=$U/log4cpp/v1_1_3c/Linux64bit+3.10-2.17-e20-prof
GC=$U/gcc/v9_3_0/Linux64bit+3.10-2.17
T=$U/tbb/v2021_1_1/Linux64bit+3.10-2.17-e20
export LD_LIBRARY_PATH="$HOME/.genie_compatlibs:$G/lib:$R/lib:$L/lib:$X/lib:$C/lib:$GC/lib64:$T/lib:$P/lib"
for b in gevgen gntpc gspl2root; do echo "== ldd $b: resolved=$(ldd $G/bin/$b 2>&1 | grep -c '=> /') notfound:"; ldd $G/bin/$b 2>&1 | grep "not found" | sort -u; done
echo "== v2 sample dir on pscratch"
GD=/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie
ls -la $GD/flux_mefhc_numu.root $GD/flux_mefhc_numu_nuwro.root $GD/gxspl_CH.xml.gz $GD/xsec_graphs.root $GD/genie_mefhc_cv_ALL.gst.root $GD/genie_mefhc_mec_ALL.gst.root 2>&1
ls -d $GD/work_seed* $GD/work_mecseed* 2>&1 | tr '\n' ' '; echo
for d in $GD/work_seed1 $GD/work_mecseed1001; do ls -la $d 2>&1 | head; done
head -30 $GD/work_seed1/gevgen_seed1.log 2>&1
grep -m5 -i "seed\|nevents\|-n " $GD/work_seed1/*.log 2>/dev/null | head
ls /pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie/gevgen3d_*.out 2>/dev/null | head -25
