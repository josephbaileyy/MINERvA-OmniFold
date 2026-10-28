F=/cvmfs/larsoft.opensciencegrid.org/products/genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/src/Apps/gEvGen.cxx
grep -n "input-flux\|spectrum\|->Write\|TFile" $F | head -30
sed -n 500,575p $F
