#!/usr/bin/env python3
"""geanttw P3's slim omnifiles (p2p3/AMENDMENT-P2P3.md A3, cov2d's (C) grant): build them and prove them.

    python3 -I p3_slim.py select --driver DRIVER.py --uomni UOMNI
    python3 -I p3_slim.py build  --uomni UOMNI --out SLIM [--dumps D_1A ... D_1P [--override | --pinned-override]]
    python3 -I p3_slim.py check  --uomni UOMNI --slim SLIM_PINNED
    python3 -I p3_slim.py patchcheck --pinned SLIM_PINNED --patched SLIM_PATCHED --dumps D_1A ... D_1P [--override]

select (C1-a): the production driver's expected_loader_branches for the six GEANT universes (use_weights) must be
        exactly the pinned 37 branches, given UOMNI's branch names. The driver is imported with a stub ROOT: the
        rule is pure Python (:991-1030) and this job's python has no ROOT.
build:  the pinned slim copies the 37 branches from UOMNI, chunk by chunk. With --dumps, the patched slim takes the
        six w_truth_GEANT_* columns of mc_signal_reco and mc_truth_denom from the 12 dumps instead, concatenated in
        hadd order. With --override, each playlist's last nTruthOnlyMisses signal rows (the misses, which carry the
        CV proxy) get the patched denominator weights of their truth rows, matched by exact key (MC, MC_pz, w_truth).
        C-MISS requires the overridden signal rows' (MC, MC_pz, w_truth_<u>) multiset to equal the denominator's,
        per playlist and per universe. With --pinned-override (the director's D2 ruling (a)), the slim keeps UOMNI's
        own pinned columns, and the same override uses UOMNI's mc_truth_denom values. UOMNI's w_truth, in both trees
        (cov2d's (C) amendment), is read for the key only and never written. The dumps give only each playlist's
        block sizes and miss counts, which must sum to UOMNI's entries and nTruthOnlyMisses. The four TParameters
        are added afterwards by slim_tparams.py, under PyROOT.
check:  C-SLIM. Each branch is bitwise equal to UOMNI's, with the same type and entry count. The top-level key set
        equals UOMNI's, and each TParameter value equals UOMNI's.
patchcheck: C-PATCH. The patched slim equals the pinned slim bitwise everywhere except the twelve target columns,
        which equal the dumps' values (overridden, if --override). The keys and TParameters are equal.

UOMNI is read only through an O_NOATIME file object, so a Python without O_NOATIME refuses. Exit 0 PASS, 1 FAIL,
2 unusable.
"""
import argparse
import importlib.util
import os
import sys
import types

import numpy as np
import uproot

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("c2_check", os.path.join(HERE, "c2_check.py"))
C2 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C2)
SLIM, TARGETS, TREES = C2.SLIM, C2.TARGETS, C2.TREES
TPARAMS = ("dataPOTUsed", "mcPOTUsed", "hasTruthOnlyMisses", "nTruthOnlyMisses")
KEY_READ = {"mc_signal_reco": ["w_truth"], "mc_truth_denom": ["w_truth"]}   # cov2d's (C) amendment 2: keys only
TOP_KEYS = set(TREES) | set(TPARAMS)
UNIVERSES = [(f"GEANT_{b}", i) for b in ("Neutron", "Pion", "Proton") for i in (0, 1)]
LOADERS = {"fill_data_reco_2d": "data", "fill_bkg_reco_2d": "mc_background",
           "collect_truth_denom_arrays": "mc_truth_denom", "collect_signal_arrays_2d": "mc_signal_reco"}
CHUNK = 4_000_000
NOATIME_OPTIONAL = bool(os.environ.get("P3SLIM_TEST"))   # the tests' only door


class Unusable(Exception):
    pass


def open_noatime(path):
    flag = getattr(os, "O_NOATIME", None)
    if flag is None and not NOATIME_OPTIONAL:
        raise Unusable("this Python has no O_NOATIME")
    return uproot.open(os.fdopen(os.open(path, os.O_RDONLY | (flag or 0)), "rb"))


def driver_selection(driver, present):
    """{tree: [names]}: the union of expected_loader_branches over the six GEANT universes, in first-seen order."""
    class _Any:
        def __getattr__(self, n):
            return _Any()

        def __call__(self, *a, **k):
            return _Any()
    saved = sys.modules.get("ROOT")
    stub = types.ModuleType("ROOT")
    stub.__getattr__ = lambda n: _Any()
    sys.modules["ROOT"] = stub
    try:
        spec = importlib.util.spec_from_file_location("geanttw_driver", driver)
        drv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(drv)
    finally:
        if saved is None:
            sys.modules.pop("ROOT", None)
        else:
            sys.modules["ROOT"] = saved
    out = {t: [] for t in TREES}
    for uni in UNIVERSES:
        for loader, t in LOADERS.items():
            for n in drv.expected_loader_branches(loader, {"universe_branch": uni, "use_weights": True}, present[t]):
                if n not in out[t]:
                    out[t].append(n)
    return out


def select(a):
    f = open_noatime(a.uomni)
    present = {t: set(f[t].keys()) for t in TREES}
    got = driver_selection(a.driver, present)
    bad = {t: (got[t], SLIM[t]) for t in TREES if got[t] != SLIM[t]}
    need = {t: SLIM[t] + KEY_READ.get(t, []) for t in TREES}
    missing = {t: [n for n in need[t] if n not in present[t]] for t in TREES if any(n not in present[t] for n in need[t])}
    overlap = {t: [n for n in KEY_READ[t] if n in SLIM[t]] for t in KEY_READ if any(n in SLIM[t] for n in KEY_READ[t])}
    if bad or missing or overlap:
        print(f"C1-a FAIL: driver selection != pinned list {bad}; absent from UOMNI {missing}; "
              f"key reads inside the slim list {overlap}")
        return 1
    print(f"C1-a PASS: the driver's selection is the pinned {sum(len(v) for v in SLIM.values())} branches; "
          f"the key-read list is {KEY_READ}")
    return 0


def keys(*cols):
    a = np.ascontiguousarray(np.stack([np.asarray(c, dtype=np.float64) for c in cols], axis=1))
    return a.view(f"V{8 * a.shape[1]}").ravel()


def sorted_equal(a, b):
    return a.size == b.size and np.array_equal(np.sort(a), np.sort(b))


def override_block(sig, den, n_miss):
    """The playlist's signal target columns with its last n_miss rows replaced by their truth rows' denominator
    values. Misses are matched by exact (MC, MC_pz, w_truth) keys, as an ordered subsequence of the truth rows.
    Unusable if the matching is not unique and in order. C-MISS is the multiset check."""
    n_sig = len(sig["MC"])
    if len(den["MC"]) != n_sig or not 0 <= n_miss <= n_sig:
        raise Unusable(f"signal {n_sig} vs denominator {len(den['MC'])} rows, {n_miss} misses")
    dk = keys(den["MC"], den["MC_pz"], den["w_truth"])
    if len(np.unique(dk)) != len(dk):
        raise Unusable("the denominator's (MC, MC_pz, w_truth) keys are not unique")
    pos = {k.tobytes(): i for i, k in enumerate(dk)}
    lo = n_sig - n_miss
    mk = keys(sig["MC"][lo:], sig["MC_pz"][lo:], sig["w_truth"][lo:])
    idx = np.array([pos.get(k.tobytes(), -1) for k in mk], dtype=np.int64)
    if (idx < 0).any() or (np.diff(idx) <= 0).any():
        raise Unusable("the misses are not an ordered subsequence of the truth rows")
    out = {b: np.array(sig[b], copy=True) for b in TARGETS["mc_signal_reco"]}
    for b in out:
        out[b][lo:] = den[b][idx]
        if not sorted_equal(keys(sig["MC"], sig["MC_pz"], out[b]), keys(den["MC"], den["MC_pz"], den[b])):
            raise Unusable(f"C-MISS FAIL: {b}'s signal multiset is not the denominator's")
    return out


def patched_columns(dumps, override):
    """{tree: {target: concatenated array}} from the 12 dumps in hadd order."""
    if len(dumps) != 12:
        raise Unusable("the patched slim needs the 12 playlists' dumps, in hadd order")
    cols = {t: {b: [] for b in TARGETS[t]} for t in TARGETS}
    base = ["MC", "MC_pz", "w_truth"]
    for d in dumps:
        f = uproot.open(d)
        sig = {b: f["mc_signal_reco"][b].array(library="np") for b in base + TARGETS["mc_signal_reco"]}
        den = {b: f["mc_truth_denom"][b].array(library="np") for b in base + TARGETS["mc_truth_denom"]}
        st = override_block(sig, den, int(tparam(f, "nTruthOnlyMisses"))) if override else sig
        for b in TARGETS["mc_signal_reco"]:
            cols["mc_signal_reco"][b].append(st[b])
        for b in TARGETS["mc_truth_denom"]:
            cols["mc_truth_denom"][b].append(den[b])
    return {t: {b: np.concatenate(v) for b, v in c.items()} for t, c in cols.items()}


def pinned_override_columns(u, dumps):
    """{tree: {target: array}}: UOMNI's own target columns, with the misses overridden from UOMNI's denominator.
    Each playlist's block sizes and miss counts come from the dumps, and must sum to UOMNI's."""
    if len(dumps) != 12:
        raise Unusable("the pinned override needs the 12 playlists' dumps (block sizes), in hadd order")
    sizes, misses = [], []
    for d in dumps:
        f = uproot.open(d)
        n = f["mc_signal_reco"].num_entries
        if f["mc_truth_denom"].num_entries != n:
            raise Unusable(f"{d}: signal and denominator entry counts differ")
        sizes.append(n)
        misses.append(int(tparam(f, "nTruthOnlyMisses")))
    if sum(sizes) != u["mc_signal_reco"].num_entries or sum(sizes) != u["mc_truth_denom"].num_entries:
        raise Unusable(f"the dumps' blocks sum to {sum(sizes)}, not UOMNI's entries")
    if sum(misses) != int(tparam(u, "nTruthOnlyMisses")):
        raise Unusable(f"the dumps' misses sum to {sum(misses)}, not UOMNI's nTruthOnlyMisses")
    base = ["MC", "MC_pz"] + KEY_READ["mc_signal_reco"]
    sig_all = {b: u["mc_signal_reco"][b].array(library="np") for b in base + TARGETS["mc_signal_reco"]}
    den_all = {b: u["mc_truth_denom"][b].array(library="np") for b in base + TARGETS["mc_truth_denom"]}
    out = {b: [] for b in TARGETS["mc_signal_reco"]}
    lo = 0
    for n, m in zip(sizes, misses):
        blk = override_block({b: v[lo:lo + n] for b, v in sig_all.items()},
                             {b: v[lo:lo + n] for b, v in den_all.items()}, m)
        for b in out:
            out[b].append(blk[b])
        lo += n
    return {"mc_signal_reco": {b: np.concatenate(v) for b, v in out.items()},
            "mc_truth_denom": {b: den_all[b] for b in TARGETS["mc_truth_denom"]}}


def build(a):
    if os.path.exists(a.out):
        raise Unusable(f"{a.out} exists")
    u = open_noatime(a.uomni)
    if a.pinned_override:
        patch = pinned_override_columns(u, a.dumps)
    else:
        patch = patched_columns(a.dumps, a.override) if a.dumps else None
    with uproot.recreate(a.out) as out:
        for t in TREES:
            src = u[t]
            n = src.num_entries
            if patch and t in patch and any(len(v) != n for v in patch[t].values()):
                raise Unusable(f"{t}: the dumps give {[len(v) for v in patch[t].values()]} rows, UOMNI {n}")
            types_ = {b: src[b].array(library="np", entry_stop=0).dtype for b in SLIM[t]}
            out.mktree(t, types_)
            for lo in range(0, n, CHUNK):
                hi = min(n, lo + CHUNK)
                block = {b: src[b].array(library="np", entry_start=lo, entry_stop=hi) for b in SLIM[t]}
                if patch and t in patch:
                    for b, v in patch[t].items():
                        block[b] = v[lo:hi].astype(types_[b], copy=False)
                out[t].extend(block)
    kind = "pinned + override" if a.pinned_override else (
        ("patched" + (" + override" if a.override else "")) if a.dumps else "pinned")
    print(f"built {a.out} ({kind})")
    return 0


def tparam(f, name):
    return f[name].member("fVal")


def check(a):
    u, s = open_noatime(a.uomni), uproot.open(a.slim)
    bad = []
    ukeys, skeys = {k.split(";")[0] for k in u.keys(recursive=False)}, {k.split(";")[0] for k in s.keys(recursive=False)}
    if skeys != ukeys:
        bad.append(f"keys {sorted(skeys ^ ukeys)}")
    for p in TPARAMS:
        if p in skeys and tparam(s, p) != tparam(u, p):
            bad.append(f"TParameter {p}")
    for t in TREES:
        if t not in skeys:
            continue
        if s[t].num_entries != u[t].num_entries:
            bad.append(f"{t} entries")
            continue
        extra = sorted(set(s[t].keys()) - set(SLIM[t]))
        if extra:
            bad.append(f"{t} extra branches {extra}")
        for b in SLIM[t]:
            if b not in s[t]:
                bad.append(f"{t}:{b} missing")
                continue
            if s[t][b].typename != u[t][b].typename:
                bad.append(f"{t}:{b} type")
                continue
            for lo in range(0, u[t].num_entries, CHUNK):
                hi = min(u[t].num_entries, lo + CHUNK)
                if not C2.same_bits(u[t][b].array(library="np", entry_start=lo, entry_stop=hi),
                                    s[t][b].array(library="np", entry_start=lo, entry_stop=hi)):
                    bad.append(f"{t}:{b}")
                    break
    print(f"C-SLIM {'PASS' if not bad else 'FAIL'}" + "".join(f"\n    {x}" for x in bad))
    return 0 if not bad else 1


def patchcheck(a):
    pin, pat = uproot.open(a.pinned), uproot.open(a.patched)
    want = patched_columns(a.dumps, a.override)
    bad = []
    kp, kq = {k.split(";")[0] for k in pin.keys(recursive=False)}, {k.split(";")[0] for k in pat.keys(recursive=False)}
    if kp != kq or kp != TOP_KEYS:
        bad.append(f"keys {sorted(kp)} vs {sorted(kq)}")
    for p in TPARAMS:
        if p in kp and p in kq and tparam(pin, p) != tparam(pat, p):
            bad.append(f"TParameter {p}")
    for t in TREES:
        for b in SLIM[t]:
            x, y = pin[t][b].array(library="np"), pat[t][b].array(library="np")
            if t in want and b in want[t]:
                if not C2.same_bits(y, want[t][b].astype(y.dtype, copy=False)):
                    bad.append(f"{t}:{b} is not the dumps' column")
            elif not C2.same_bits(x, y):
                bad.append(f"{t}:{b} differs from pinned")
    print(f"C-PATCH {'PASS' if not bad else 'FAIL'}" + "".join(f"\n    {x}" for x in bad))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select"); s.add_argument("--driver", required=True); s.add_argument("--uomni", required=True)
    b = sub.add_parser("build"); b.add_argument("--uomni", required=True); b.add_argument("--out", required=True)
    b.add_argument("--dumps", nargs="+"); b.add_argument("--override", action="store_true")
    b.add_argument("--pinned-override", action="store_true")
    c = sub.add_parser("check"); c.add_argument("--uomni", required=True); c.add_argument("--slim", required=True)
    q = sub.add_parser("patchcheck"); q.add_argument("--pinned", required=True); q.add_argument("--patched", required=True)
    q.add_argument("--dumps", nargs="+", required=True); q.add_argument("--override", action="store_true")
    a = ap.parse_args(argv)
    if (getattr(a, "override", False) or getattr(a, "pinned_override", False)) and not getattr(a, "dumps", None):
        print("UNUSABLE: --override and --pinned-override need --dumps")
        return 2
    if getattr(a, "override", False) and getattr(a, "pinned_override", False):
        print("UNUSABLE: --override and --pinned-override are exclusive")
        return 2
    try:
        return {"select": select, "build": build, "check": check, "patchcheck": patchcheck}[a.cmd](a)
    except Unusable as e:
        print(f"UNUSABLE: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
