"""COV2D metadata probe 2 (login node, 0 node-h): stat of every input the declaration names, for its retention
table, and the branch interpretations of $CV's and $UNI's data trees, for the writer's schema. Branch metadata only,
through O_NOATIME descriptors; no event content is read. atime before and after on every ROOT file opened."""
import os
import sys
import time

CV = "/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root"
UNI = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root"
D2 = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
STAT = [
    CV, UNI,
    f"{D2}/baseline_flux/runEventLoopMC_MEFHC.root",
    f"{D2}/baseline_flux/flux_integral_universes_MEFHC.root",
    "/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/"
    "sorted_NuEConstraint_FHC_RHC_IMD.txt",
    "/pscratch/sd/j/josephrb/fd-f1-20261027/f1b3/prep/bridged/genie_v3_g18.json",
    "/pscratch/sd/j/josephrb/fd-f1-20261027/f1b3/prep/bridged/genie_v3_ar23.json",
    "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/ER/xsec.root",
]
LAT = "/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-inputs-20261012/active_universe_5d_standard_merged"


def st(p):
    s = os.stat(p)
    return f"size={s.st_size} mtime={int(s.st_mtime)} atime={int(s.st_atime)}"


def main():
    import uproot
    print(f"host={os.uname().nodename} utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} uproot={uproot.__version__}")
    for p in STAT:
        print(f"STAT {p} {st(p) if os.path.exists(p) else 'MISSING'}")
    for n in sorted(os.listdir(LAT)):
        print(f"STAT {LAT}/{n} {st(os.path.join(LAT, n))}")
    for p in (CV, UNI):
        before = st(p)
        with os.fdopen(os.open(p, os.O_RDONLY | os.O_NOATIME), "rb") as fh:
            t = uproot.open(fh)["data"]
            for b in t.keys():
                br = t[b]
                print(f"BRANCH {os.path.basename(p)} data.{b} interp={br.interpretation} title={br.title!r} "
                      f"leaf={br.member('fLeaves')[0].member('fTitle') if br.member('fLeaves') else ''}")
        print(f"ATIME {os.path.basename(p)} before {before} after {st(p)}")


if __name__ == "__main__":
    sys.exit(main())
