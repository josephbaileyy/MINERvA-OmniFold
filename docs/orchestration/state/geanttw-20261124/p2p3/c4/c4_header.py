#!/usr/bin/env python3
"""geanttw P2-P3 C4: header-only reads under cov2d's grant (C4), by D1's method.

    python3 -I c4_header.py      # on a Perlmutter login node; prints the results and one JSON line; writes nothing

(i)  UOMNI's sizes for the 37 slim branches: each TBranch's fZipBytes and fTotBytes members and its entry count, all
     metadata. A size check of UOMNI by stat against Stage C's recorded 171,117,087,867 B.
(ii) The 12 per-playlist files' tree entry counts, giving the 1L offset (the sum of 1A-1G) per tree. A consistency
     check requires the 12 to sum to UOMNI's entries per tree.

Every file is opened only through an O_NOATIME descriptor, and uproot reads that file object, never the path. Only
the ROOT directory and TTree/TBranch metadata are read; no basket. Each file is stat'ed before and after, and an
atime or mtime move is a STOP. Every path is pinned here; nothing is globbed. (i) and (ii) each report their own
result. The exit status is 2 if either STOPped, and 0 otherwise.
"""
import json
import os
import stat
import sys

D2 = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
UOMNI = f"{D2}/runEventLoopOmniFold_MEFHC_universes_full.root"
UOMNI_SIZE = 171117087867
PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")   # hadd order, :32-43
PER_PL = {pl: f"{D2}/runEventLoopOmniFold_{pl}_universes_full.root" for pl in PLAYLISTS}
TREES = ("data", "mc_background", "mc_truth_denom", "mc_signal_reco")
G = [f"GEANT_{b}_{i}" for b in ("Neutron", "Pion", "Proton") for i in (0, 1)]
SLIM = {   # the 37 branches, from the production driver's expected_loader_branches (:991-1030)
    "data": ["measured", "measured_pz", "measured_pass"],
    "mc_background": ["sim_background", "sim_background_pz", "sim_background_pass"] + [f"w_bkg_{g}" for g in G],
    "mc_truth_denom": ["MC", "MC_pz"] + [f"w_truth_{g}" for g in G],
    "mc_signal_reco": ["MC", "MC_pz", "sim", "sim_pz", "sim_pass"] + [x for g in G for x in (f"w_truth_{g}", f"w_reco_{g}")],
}
NOATIME_OPTIONAL = False
if os.environ.get("C4_TEST_D2"):   # the tests' only door
    D2 = os.environ["C4_TEST_D2"]
    UOMNI = f"{D2}/runEventLoopOmniFold_MEFHC_universes_full.root"
    UOMNI_SIZE = int(os.environ["C4_TEST_UOMNI_SIZE"])
    PER_PL = {pl: f"{D2}/runEventLoopOmniFold_{pl}_universes_full.root" for pl in PLAYLISTS}
    NOATIME_OPTIONAL = True


class Stop(Exception):
    pass


def open_header(path):
    """(uproot file, stat before, file object): through an O_NOATIME descriptor only."""
    flag = getattr(os, "O_NOATIME", None)
    if flag is None and not NOATIME_OPTIONAL:
        raise Stop("this Python has no O_NOATIME")
    st0 = os.stat(path)
    if not stat.S_ISREG(st0.st_mode):
        raise Stop(f"{path} is not a regular file")
    import uproot
    fobj = os.fdopen(os.open(path, os.O_RDONLY | (flag or 0)), "rb")
    return uproot.open(fobj), st0, fobj


def close_checked(path, st0, fobj):
    fobj.close()
    st1 = os.stat(path)
    if (st1.st_atime_ns, st1.st_mtime_ns) != (st0.st_atime_ns, st0.st_mtime_ns):
        raise Stop(f"{path}: atime/mtime moved {st0.st_atime_ns}->{st1.st_atime_ns} {st0.st_mtime_ns}->{st1.st_mtime_ns}")
    return {"size": st0.st_size, "atime_ns": st0.st_atime_ns, "mtime_ns": st0.st_mtime_ns}


def part_i():
    f, st0, fobj = open_header(UOMNI)
    try:
        if st0.st_size != UOMNI_SIZE:
            raise Stop(f"UOMNI size {st0.st_size} != Stage C's {UOMNI_SIZE}")
        out = {}
        for t, names in SLIM.items():
            tree = f[t]
            for n in names:
                if n not in tree:
                    raise Stop(f"{t}:{n} is not in UOMNI")
                br = tree[n]
                out[f"{t}:{n}"] = {"zip_bytes": int(br.member("fZipBytes")), "tot_bytes": int(br.member("fTotBytes")),
                                   "entries": int(br.num_entries)}
        entries = {t: int(f[t].num_entries) for t in TREES}
    finally:
        info = close_checked(UOMNI, st0, fobj)
    zip_sum = sum(v["zip_bytes"] for v in out.values())
    tot_sum = sum(v["tot_bytes"] for v in out.values())
    print(f"(i) UOMNI {info['size']} B; 37 branches: zip {zip_sum} B, tot {tot_sum} B; entries {entries}")
    return {"file": info, "branches": out, "zip_bytes_sum": zip_sum, "tot_bytes_sum": tot_sum, "entries": entries}


def part_ii(uomni_entries):
    per, missing = {}, []
    for pl in PLAYLISTS:
        p = PER_PL[pl]
        if not os.path.exists(p):
            missing.append(pl)
            continue
        f, st0, fobj = open_header(p)
        try:
            ent = {t: int(f[t].num_entries) for t in TREES}
        finally:
            info = close_checked(p, st0, fobj)
        per[pl] = {"entries": ent, "file": info}
    res = {"per_playlist": per, "missing": missing}
    if missing:
        print(f"(ii) MISSING per-playlist files {missing}: the 1L offset is NOT settled (C3-b: C3 waits)")
        res["offset_settled"] = False
        return res
    pre = PLAYLISTS[:PLAYLISTS.index("1L")]
    res["offset_1L"] = {t: sum(per[pl]["entries"][t] for pl in pre) for t in TREES}
    res["count_1L"] = {t: per["1L"]["entries"][t] for t in TREES}
    sums = {t: sum(per[pl]["entries"][t] for pl in PLAYLISTS) for t in TREES}
    res["sum_equals_uomni"] = {t: (uomni_entries.get(t) == sums[t]) if uomni_entries else None for t in TREES}
    res["offset_settled"] = bool(uomni_entries) and all(res["sum_equals_uomni"].values())
    print(f"(ii) 1L offset {res['offset_1L']}; 1L count {res['count_1L']}; 12-file sums equal UOMNI "
          f"{res['sum_equals_uomni']}; offset settled {res['offset_settled']}")
    return res


def main():
    rep, stops = {}, []
    try:
        rep["i"] = part_i()
    except Stop as e:
        stops.append(f"(i) {e}")
        rep["i"] = None
    try:
        rep["ii"] = part_ii(rep["i"]["entries"] if rep["i"] else None)
    except Stop as e:
        stops.append(f"(ii) {e}")
        rep["ii"] = None
    for s in stops:
        print(f"STOP: {s}")
    print("JSON " + json.dumps(rep, sort_keys=True))
    return 2 if stops else 0


if __name__ == "__main__":
    sys.exit(main())
