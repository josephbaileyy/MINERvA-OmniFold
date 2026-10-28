G=/cvmfs/larsoft.opensciencegrid.org/products/genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof/GENIE-Generator
sed -n 264,280p $G/src/Physics/Common/KineGeneratorWithCache.cxx
F=$G/src/Physics/Multinucleon/EventGen/MECGenerator.cxx; echo "F=$F"; grep -n "AssertXSecLimits\|xsec_max\|accept\|xsec <\|t <\|gRndm\|Rndm()" $F | head -40
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
echo "== records just before the AR23 messages: the interaction's hit-nucleon cluster"; grep -n "Negative cross section" -B30 $OUT/f1a/pilot/AR23_20i_00_000/gevgen.log | grep -oE "\|\s+[A-Za-z0-9+_-]+ \|\s+2000000[0-9]+" | sort | uniq -c | head
