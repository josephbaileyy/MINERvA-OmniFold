G=/cvmfs/larsoft.opensciencegrid.org/products/genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof/GENIE-Generator
F=$G/src/Physics/Common/KineGeneratorWithCache.cxx; [ -f $F ] || F=$(find $G/src -name KineGeneratorWithCache.cxx | head -1); echo F=$F
grep -n "AssertXSecLimits" -A25 $F | sed -n 1,45p
echo "== who calls AssertXSecLimits"; grep -rn "AssertXSecLimits" $G/src --include=*.cxx | head
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
echo "== AR23 messages: which generator logged them"; grep -n "Negative cross section" -B2 $OUT/f1a/pilot/AR23_20i_00_000/gevgen.log | grep -oE "<[A-Za-z]+\.cxx::[A-Za-z]+ \([0-9]+\)>" | sort | uniq -c | head
grep -n "Negative cross section" -B1 $OUT/f1a/pilot/AR23_20i_00_000/gevgen.log | head -6
