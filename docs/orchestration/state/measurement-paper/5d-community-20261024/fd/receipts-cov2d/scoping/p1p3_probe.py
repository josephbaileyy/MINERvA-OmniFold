"""COV2D P1/P3 metadata probe (scoping, 0 node-h, login node). P3: stat of the 2D inputs. P1: tree names, entry counts
and branch names of the 2D omnifiles, read through an O_NOATIME descriptor. Reads no event content."""
import os
import sys
import time

PATHS = {
    "CV": "/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root",
    "UNI": "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root",
    "MC": "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root",
    "FLUXU": "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root",
    "ACT_DIR": "/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-inputs-20261012/active_universe_5d_standard_merged",
    "PU_DIR": "/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014/inputs",
    "RE2_STAGED": "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/inputs",
    "PL_CV_DIR": "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding",
}
PROBE_TREES = ("CV", "UNI")
TRUTH_HINT = ("eavail", "q3", "w_", "_w", "true", "truth", "q0", "enu")


def st(p):
    s = os.stat(p)
    return f"size={s.st_size} mtime={int(s.st_mtime)} atime={int(s.st_atime)}"


def main():
    print(f"host={os.uname().nodename} utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    print("== P3: stat")
    for k, p in PATHS.items():
        if not os.path.exists(p):
            print(f"{k} MISSING {p}")
            continue
        if os.path.isdir(p):
            names = sorted(os.listdir(p))
            if k == "PL_CV_DIR":
                names = [n for n in names if n.startswith("runEventLoopOmniFold_1") and n.endswith(".root")]
            print(f"{k} DIR {p} entries={len(names)}")
            for n in names:
                print(f"  {n} {st(os.path.join(p, n))}")
        else:
            print(f"{k} FILE {p} {st(p)}")
    import uproot
    print(f"== P1: branches (uproot {uproot.__version__}, O_NOATIME descriptor)")
    for k in PROBE_TREES:
        p = PATHS[k]
        before = st(p)
        fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
        with os.fdopen(fd, "rb") as fh:
            f = uproot.open(fh)
            print(f"{k} {p}")
            for key, cls in sorted(f.classnames(recursive=False).items()):
                if cls != "TTree":
                    print(f"  key {key} {cls}")
                    continue
                t = f[key]
                names = list(t.keys())
                hint = [n for n in names if any(h in n.lower() for h in TRUTH_HINT)]
                print(f"  tree {key} entries={t.num_entries} branches={len(names)}")
                print(f"    first 60: {names[:60]}")
                print(f"    truth-like ({len(hint)}): {hint[:80]}")
        print(f"  stat before {before}")
        print(f"  stat after  {st(p)}")


if __name__ == "__main__":
    sys.exit(main())
