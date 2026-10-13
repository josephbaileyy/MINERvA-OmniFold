#!/bin/bash
# P4 login-node smoke, no-op control and positive control on ONE 1A MC file (run00110018, 15.2 GB) and one
# 1A data file. About 30 s per variant. Four variants, run concurrently:
#   unpatched      the unpatched copy built here
#   patched_off    patched binary, census unset       -> must equal unpatched (trees, objects, stdout)
#   patched_on     patched binary, census set         -> main output must equal unpatched; census file written
#   patched_self   census set + MNV101_G1_CENSUS_SELFTEST=7 -> main output equal; census must record exactly
#                  the skipped keys with key % 7 == 0 (positive control of the detection/recording path)
#   bash smoke.sh <p4 namespace>
NS=${1:?p4 namespace}
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh >/dev/null 2>&1
mkdir -p "$NS/smoke" && cd "$NS/smoke"
echo /pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1A/MasterAnaDev_mc_AnaTuple_run00110018_Playlist.root > mc.txt
head -1 /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/playlist_manifests/1A_Data.txt > data.txt
for v in unpatched patched_off patched_on patched_self; do
  rm -rf "$v"; mkdir -p "$v"
  case $v in unpatched) B=$NS/build/unpatched/runEventLoopOmniFold;; *) B=$NS/build/patched/runEventLoopOmniFold;; esac
  ( cd "$v"
    unset MNV101_G1_CENSUS MNV101_G1_CENSUS_SELFTEST
    case $v in
      patched_on) export MNV101_G1_CENSUS=$NS/smoke/$v/g1_census.root;;
      patched_self) export MNV101_G1_CENSUS=$NS/smoke/$v/g1_census.root MNV101_G1_CENSUS_SELFTEST=7;;
    esac
    /usr/bin/time -v timeout 1200 nice -n 10 "$B" "$NS/smoke/data.txt" "$NS/smoke/mc.txt" > run.log 2> run.err
    echo "rc=$?" >> run.log ) &
done
wait
for v in patched_off patched_on patched_self; do
  python3 "$NS/compare_outputs.py" unpatched/runEventLoopOmniFold.root $v/runEventLoopOmniFold.root --strict \
      --json cmp_$v.json > cmp_$v.txt 2>&1; echo "compare $v rc=$?"
done
diff <(tr '\r' '\n' < unpatched/run.log) <(tr '\r' '\n' < patched_off/run.log) > /dev/null && echo "stdout patched_off == unpatched"
python3 - <<'EOF'
import ROOT
ROOT.gROOT.SetBatch(True)
FILES = {}
def tfile(f):
    if f not in FILES:
        FILES[f] = ROOT.TFile.Open(f)
    return FILES[f]
def par(f, n):
    return tfile(f).Get(n).GetVal()
for v in ("patched_on", "patched_self"):
    f = f"{v}/g1_census.root"
    t = tfile(f).Get("g1_census")
    print(v, {n: par(f, n) for n in ("nBkgSkipped", "nBkgSkippedInReco", "nG1", "nG1Status0", "nG1Status1",
                                     "nG1Status2", "nSelftestInjected", "nSigLoopNoTruth",
                                     "nTruthFidFailStored")}, "rows", t.GetEntries())
f = "patched_self/g1_census.root"
t = tfile(f).Get("g1_census")
# makeEventKey packs in uint64_t, which wraps for 6-digit MC run numbers: reproduce mod 2**64
keys = [((e.run * 100000000 + e.subrun) * 100000000 + e.nth) % 2**64 for e in t]
ok = all(k % 7 == 0 for k in keys) and len(keys) == par(f, "nSelftestInjected") - par(f, "nG1DupKey") \
     and par(f, "nG1Status2") == len(keys)
print("SELFTEST", "PASS" if ok else "FAIL", len(keys))
EOF
echo SMOKE-DONE
