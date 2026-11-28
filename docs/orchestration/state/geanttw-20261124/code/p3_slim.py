#!/usr/bin/env python3
"""geanttw P3's slim omnifiles: UOMNI opened ONCE (cov2d's (C) grant, amendments 1-3; p2p3/AMENDMENT-P2P3.md A3).

    python3 -I p3_slim.py build  --uomni UOMNI --driver DRIVER.py --dumps D_1A ... D_1P --outdir P3 \
                                 --record BUILD.json --c2 C2.json
    python3 -I p3_slim.py verify --driver DRIVER.py --outdir P3 --record BUILD.json --mcfile MCFILE \
                                 --mcfile-sha SHA --out SLIM.json

build:  opens UOMNI once, through an O_NOATIME file object, and does everything that needs it in that open.
        - C1-a. The production driver's expected_loader_branches for the six GEANT universes (use_weights) is
          exactly SLIM (37 branches). KEY_READ (w_truth in each MC tree) is present, tree by tree. The 4 TParameters
          exist. Every lateral name the driver probes for these universes (_universe_kine_branches), and the
          top-level pTmu_fiducial_nucleons it probes at :1690, is absent. The driver is imported with a stub ROOT;
          the rule is pure Python (:991-1030).
        - The record of UOMNI's metadata: each TParameter's class and value, and each slim branch's typename.
          slim_tparams.py writes the TParameters from it, and verify checks against it, so neither opens UOMNI.
        - The walk, playlist block by playlist block in hadd order, of SLIM + KEY_READ only, with the dumps in step.
          Each block's sizes must be C4's per-playlist counts (BLOCKS). For each block:
          - C2: the 25 non-target branches of the dump equal UOMNI's, bitwise.
          - The tail check, in UOMNI and in the dump (build_miss_override.py:94-100): the last nTruthOnlyMisses
            signal rows are misses (sim_pass 0, sim -9999, every target equal to w_truth, the CV proxy), and the row
            before them is not a miss, so the count is the whole run of misses.
          - Both overrides, under C-MISS, keyed on (MC, MC_pz, w_truth, target).
          After the walk, the dumps' misses must sum to UOMNI's nTruthOnlyMisses (and hasTruthOnlyMisses agree).
        It writes slim-pinned.root (UOMNI's columns), slim-pinned-override.root (UOMNI's, misses overridden from
        UOMNI's denominator) and slim-patched.root (the dumps' targets, overridden from the dumps' denominator; every
        other column UOMNI's), and the sha256 of every array written, per file, tree, branch and block. A block over
        MAX_ROWS stops before reading it. Every UOMNI array is read through uread, which refuses a branch outside
        GRANTED, cov2d's 39 (condition 2-a, written out here, not derived from SLIM), and records each one it reads.
        The build fails unless the branches read are exactly GRANTED's.
verify: after slim_tparams.py, it reads each slim back, never UOMNI, and checks against the build record:
        - the top-level key set is exactly the trees and the 4 TParameters, each with UOMNI's class and value;
        - each tree's branch set is SLIM, each typename UOMNI's, and each entry count C4's;
        - the lateral probes are absent;
        - every per-block array's sha256 equals the build record's, which compares the bytes written with the
          in-memory arrays.
        Only then does it write SLIM.json (verdict PASS, each slim's sha256 and size, and MCFILE's single sha256, size
        and mtime).
Exit 0 PASS, 1 FAIL, 2 unusable.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys
import types

import numpy as np
import uproot

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("c2_check", os.path.join(HERE, "c2_check.py"))
C2 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C2)
SLIM, TARGETS, TREES, NON_TARGET = C2.SLIM, C2.TARGETS, C2.TREES, C2.NON_TARGET
MC_TREES = ("mc_truth_denom", "mc_signal_reco")
TPARAMS = ("dataPOTUsed", "mcPOTUsed", "hasTruthOnlyMisses", "nTruthOnlyMisses")
TOP_KEYS = set(TREES) | set(TPARAMS)
KEY_READ = {"mc_signal_reco": ["w_truth"], "mc_truth_denom": ["w_truth"]}   # cov2d's (C) amendment 2: keys only
UNIVERSES = [(f"GEANT_{b}", i) for b in ("Neutron", "Pion", "Proton") for i in (0, 1)]
LOADERS = {"fill_data_reco_2d": "data", "fill_bkg_reco_2d": "mc_background",
           "collect_truth_denom_arrays": "mc_truth_denom", "collect_signal_arrays_2d": "mc_signal_reco"}
PROBES = {"data": (), "mc_background": ("bkg_tree_reco",), "mc_truth_denom": ("truth_tree",),
          "mc_signal_reco": ("reco_tree_truth", "reco_tree_reco")}
PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")   # hadd order
BLOCKS = {   # C4's per-playlist entry counts (p2p3/c4/c4.out), which sum to UOMNI's
    "data": (360123, 75192, 173122, 580834, 408075, 642737, 538406, 49872, 591031, 415928, 110836, 173641),
    "mc_background": (52626, 14182, 26898, 78987, 66077, 92219, 76742, 7820, 120642, 70774, 22038, 29222),
    "mc_truth_denom": (2682267, 721082, 1376832, 4003632, 3350021, 4660210, 3922748, 383848, 5917406, 3416266,
                       1042088, 1372703),
    "mc_signal_reco": (2682267, 721082, 1376832, 4003632, 3350021, 4660210, 3922748, 383848, 5917406, 3416266,
                       1042088, 1372703),
}
_G = [f"GEANT_{b}_{i}" for b in ("Neutron", "Pion", "Proton") for i in (0, 1)]
GRANTED = {   # cov2d's (C) grant, amendments 1-3: the 37 slim branches plus the 2 key reads, written out
    "data": frozenset({"measured", "measured_pz", "measured_pass"}),
    "mc_background": frozenset({"sim_background", "sim_background_pz", "sim_background_pass"}
                               | {f"w_bkg_{g}" for g in _G}),
    "mc_truth_denom": frozenset({"MC", "MC_pz", "w_truth"} | {f"w_truth_{g}" for g in _G}),
    "mc_signal_reco": frozenset({"MC", "MC_pz", "sim", "sim_pz", "sim_pass", "w_truth"}
                                | {f"w_truth_{g}" for g in _G} | {f"w_reco_{g}" for g in _G}),
}
PROBED_TOP = ("pTmu_fiducial_nucleons",)   # the driver's f_in.Get at :1690; absent in UOMNI, its documented path
READ = set()
MAX_ROWS = 6_500_000   # the largest block is 1M's 5,917,406 rows; the job's --mem is sized for this
SENTINEL = -9999.0
SLIMS = {"pin": "slim-pinned.root", "pinov": "slim-pinned-override.root", "patov": "slim-patched.root"}
NOATIME_OPTIONAL = False
if os.environ.get("P3SLIM_TEST"):   # the tests' only door: small fixture blocks, no O_NOATIME needed
    NOATIME_OPTIONAL = True
    BLOCKS = {t: tuple(v) for t, v in json.loads(os.environ["P3SLIM_TEST_BLOCKS"]).items()}
    MAX_ROWS = int(os.environ.get("P3SLIM_TEST_MAX_ROWS", MAX_ROWS))


class Unusable(Exception):
    pass


class Fail(Exception):
    pass


def open_noatime(path):
    flag = getattr(os, "O_NOATIME", None)
    if flag is None and not NOATIME_OPTIONAL:
        raise Unusable("this Python has no O_NOATIME")
    return uproot.open(os.fdopen(os.open(path, os.O_RDONLY | (flag or 0)), "rb"))


def uread(u, t, b, **kw):
    """UOMNI's branch b of tree t, only if the grant covers it."""
    if b not in GRANTED.get(t, ()):
        raise Unusable(f"{t}:{b} is outside cov2d's grant (37 + 2 branches)")
    READ.add((t, b))
    return u[t][b].array(library="np", **kw)


def tparam(f, name):
    return f[name].member("fVal")


def tpclass(f, name):
    return f[name].classname


def top_keys(f):
    return {k.split(";")[0] for k in f.keys() if "/" not in k}   # top level only


def load_driver(driver):
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
    return drv


def probes(drv):
    """{tree: [lateral names the driver tests for presence]} for the six universes."""
    return {t: sorted({n for uni in UNIVERSES for c in ctx for n in drv._universe_kine_branches(uni, c)})
            for t, ctx in PROBES.items()}


def c1a(drv, u):
    """C1-a on UOMNI's headers, in build's one open: the refusals, or []."""
    present = {t: set(u[t].keys()) for t in TREES}
    got = {t: [] for t in TREES}
    for uni in UNIVERSES:
        for loader, t in LOADERS.items():
            for n in drv.expected_loader_branches(loader, {"universe_branch": uni, "use_weights": True}, present[t]):
                if n not in got[t]:
                    got[t].append(n)
    top = top_keys(u)
    bad = []
    bad += [f"{t}: driver selects {got[t]}, pinned {SLIM[t]}" for t in TREES if got[t] != SLIM[t]]
    bad += [f"{t}:{n} absent from UOMNI" for t in TREES for n in SLIM[t] + KEY_READ.get(t, []) if n not in present[t]]
    bad += [f"{t}:{n} is a key read and a slim branch" for t in KEY_READ for n in KEY_READ[t] if n in SLIM[t]]
    bad += [f"TParameter {p} absent from UOMNI" for p in TPARAMS if p not in top]
    bad += [f"the driver's probe {n} is in UOMNI" for n in PROBED_TOP if n in top]
    bad += [f"{t}: the driver's lateral probe {n} is in UOMNI" for t, ns in probes(drv).items() for n in ns
            if n in present[t]]
    return bad


def keys(*cols):
    a = np.ascontiguousarray(np.stack([np.asarray(c, dtype=np.float64) for c in cols], axis=1))
    return a.view(f"V{8 * a.shape[1]}").ravel()


def sorted_equal(a, b):
    return a.size == b.size and np.array_equal(np.sort(a), np.sort(b))


def tail_is_misses(sig, n_miss, where):
    """build_miss_override.py:94-100: the last n_miss rows are misses carrying the CV proxy."""
    lo = len(sig["MC"]) - n_miss
    ok = (bool((sig["sim_pass"][lo:] == 0).all()) and bool((sig["sim"][lo:] == SENTINEL).all())
          and all(bool((sig[b][lo:] == sig["w_truth"][lo:]).all()) for b in TARGETS["mc_signal_reco"]))
    if not ok:
        raise Fail(f"{where}: the last {n_miss} signal rows are not misses with the CV proxy")
    if lo > 0 and sig["sim"][lo - 1] == SENTINEL:
        raise Fail(f"{where}: the row before the last {n_miss} is also a miss: the count is not the whole run")


def override_block(sig, den, n_miss, where):
    """The block's signal targets, with the last n_miss rows replaced by their truth rows' denominator values.
    Misses are matched by exact (MC, MC_pz, w_truth) keys, as an ordered subsequence of the truth rows. C-MISS:
    the overridden signal multiset of (MC, MC_pz, w_truth, target) equals the denominator's."""
    n_sig = len(sig["MC"])
    if len(den["MC"]) != n_sig or not 0 <= n_miss <= n_sig:
        raise Unusable(f"{where}: signal {n_sig} vs denominator {len(den['MC'])} rows, {n_miss} misses")
    dk = keys(den["MC"], den["MC_pz"], den["w_truth"])
    if len(np.unique(dk)) != len(dk):
        raise Fail(f"{where}: the denominator's (MC, MC_pz, w_truth) keys are not unique")
    pos = {k.tobytes(): i for i, k in enumerate(dk)}
    lo = n_sig - n_miss
    mk = keys(sig["MC"][lo:], sig["MC_pz"][lo:], sig["w_truth"][lo:])
    idx = np.array([pos.get(k.tobytes(), -1) for k in mk], dtype=np.int64)
    if (idx < 0).any() or (np.diff(idx) <= 0).any():
        raise Fail(f"{where}: the misses are not an ordered subsequence of the truth rows")
    out = {}
    for b in TARGETS["mc_signal_reco"]:
        out[b] = np.array(sig[b], copy=True)
        out[b][lo:] = den[b][idx]
        if not sorted_equal(keys(sig["MC"], sig["MC_pz"], sig["w_truth"], out[b]),
                            keys(den["MC"], den["MC_pz"], den["w_truth"], den[b])):
            raise Fail(f"C-MISS FAIL {where}: {b}'s signal multiset is not the denominator's")
    return out


def digest(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def build(a):
    if len(a.dumps) != 12:
        raise Unusable("build needs the 12 playlists' dumps, in hadd order")
    paths = {k: os.path.join(a.outdir, v) for k, v in SLIMS.items()}
    for p in list(paths.values()) + [a.record, a.c2]:
        if os.path.exists(p):
            raise Unusable(f"{p} exists")
    big = [(t, PLAYLISTS[i], n) for t, ns in BLOCKS.items() for i, n in enumerate(ns) if n > MAX_ROWS]
    if big:
        raise Unusable(f"blocks over {MAX_ROWS} rows {big}: the job's memory is not sized for them")
    drv = load_driver(a.driver)
    READ.clear()
    u = open_noatime(a.uomni)   # the one open
    bad = c1a(drv, u)
    for b in bad:
        print(f"    {b}")
    print(f"C1-a {'PASS' if not bad else 'FAIL'}: the pinned {sum(len(v) for v in SLIM.values())} branches, "
          f"key reads {KEY_READ}, {len(TPARAMS)} TParameters")
    if bad:
        return 1
    meta = {"tparams": {p: {"class": tpclass(u, p), "value": np.asarray(tparam(u, p)).item()} for p in TPARAMS},
            "typenames": {t: {b: u[t][b].typename for b in SLIM[t]} for t in TREES}}
    for t in TREES:
        if u[t].num_entries != sum(BLOCKS[t]):
            raise Unusable(f"UOMNI's {t} has {u[t].num_entries} entries, not C4's {sum(BLOCKS[t])}")
    read = {t: SLIM[t] + KEY_READ.get(t, []) for t in TREES}   # condition 2-a: the 37 + 2, nothing else
    dtypes = {t: {b: uread(u, t, b, entry_stop=0).dtype for b in SLIM[t]} for t in TREES}
    outs = {k: uproot.recreate(p) for k, p in paths.items()}
    rec = {"blocks": {}, "digests": {k: {} for k in SLIMS}, "c2_differ": [], "uomni": meta}
    try:
        for k in outs:
            for t in TREES:
                outs[k].mktree(t, dtypes[t])
        start = {t: 0 for t in TREES}
        for i, (pl, d) in enumerate(zip(PLAYLISTS, a.dumps)):
            fd = uproot.open(d)
            n_miss = int(tparam(fd, "nTruthOnlyMisses"))
            blk = {}
            for t in TREES:
                n = BLOCKS[t][i]
                if fd[t].num_entries != n:
                    raise Fail(f"{pl}: the dump's {t} has {fd[t].num_entries} entries, not C4's {n}")
                lo, hi = start[t], start[t] + n
                ub = {b: uread(u, t, b, entry_start=lo, entry_stop=hi) for b in read[t]}
                want = NON_TARGET[t] + (TARGETS.get(t, []) + ["w_truth"] if t in MC_TREES else [])
                if t == "mc_signal_reco":
                    want += ["sim", "sim_pass"]
                db = {b: fd[t][b].array(library="np") for b in dict.fromkeys(want)}
                for b in NON_TARGET[t]:   # C2
                    if not C2.same_bits(ub[b], db[b]):
                        rec["c2_differ"].append(f"{pl}:{t}:{b}")
                blk[t] = (ub, db)
                start[t] = hi
            if rec["c2_differ"]:
                raise Fail(f"C2 FAIL at {pl}: {rec['c2_differ']}")
            (us, ds), (ud, dd) = blk["mc_signal_reco"], blk["mc_truth_denom"]
            tail_is_misses(us, n_miss, f"{pl} UOMNI")
            tail_is_misses(ds, n_miss, f"{pl} dump")
            ov = {"pin": {}, "pinov": override_block(us, ud, n_miss, f"{pl} pinned"),
                  "patov": override_block(ds, dd, n_miss, f"{pl} patched")}
            den_t = {"pin": {}, "pinov": {}, "patov": {b: dd[b] for b in TARGETS["mc_truth_denom"]}}
            for k in outs:
                for t in TREES:
                    cols = {b: blk[t][0][b] for b in SLIM[t]}
                    if t == "mc_signal_reco":
                        cols.update(ov[k])
                    if t == "mc_truth_denom":
                        cols.update(den_t[k])
                    cols = {b: np.asarray(v).astype(dtypes[t][b]) for b, v in cols.items()}
                    outs[k][t].extend(cols)
                    for b, v in cols.items():
                        rec["digests"][k].setdefault(t, {}).setdefault(b, []).append(digest(v))
            rec["blocks"][pl] = {"misses": n_miss, **{t: BLOCKS[t][i] for t in TREES}}
    except Fail as e:
        with open(a.c2, "w") as fh:
            json.dump({"verdict": "FAIL", "differ": rec["c2_differ"], "reason": str(e)}, fh, indent=1, sort_keys=True)
        print(f"BUILD FAIL: {e}")
        return 1
    finally:
        for o in outs.values():
            o.close()
    n_all, tp = sum(b["misses"] for b in rec["blocks"].values()), meta["tparams"]
    if n_all != int(tp["nTruthOnlyMisses"]["value"]) or bool(n_all) != bool(tp["hasTruthOnlyMisses"]["value"]):
        raise Unusable(f"the dumps' misses sum to {n_all}, not UOMNI's nTruthOnlyMisses {tp['nTruthOnlyMisses']['value']}")
    rec["uomni_branches_read"] = sorted(f"{t}:{b}" for t, b in READ)
    if {(t, b) for t in GRANTED for b in GRANTED[t]} != READ:
        raise Unusable(f"the branches read are not exactly the grant's: {rec['uomni_branches_read']}")
    with open(a.c2, "w") as fh:
        json.dump({"verdict": "PASS", "differ": [], "blocks": rec["blocks"]}, fh, indent=1, sort_keys=True)
    with open(a.record, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
    print(f"C2 PASS; built {sorted(SLIMS.values())} in one pass over UOMNI")
    return 0


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def verify(a):
    rec = json.load(open(a.record))
    drv = load_driver(a.driver)
    pr = probes(drv)
    utypes, utp = rec["uomni"]["typenames"], rec["uomni"]["tparams"]   # UOMNI's, recorded in build's one open
    bad, out = [], {"slims": {}}
    for k, name in SLIMS.items():
        path = os.path.join(a.outdir, name)
        s = uproot.open(path)
        if top_keys(s) != TOP_KEYS:
            bad.append(f"{name}: keys {sorted(top_keys(s))}")
            continue
        bad += [f"{name}: TParameter {p}" for p in TPARAMS
                if (tpclass(s, p), np.asarray(tparam(s, p)).item()) != (utp[p]["class"], utp[p]["value"])]
        for t in TREES:
            if s[t].num_entries != sum(BLOCKS[t]):
                bad.append(f"{name}:{t} entries")
            if set(s[t].keys()) != set(SLIM[t]):
                bad.append(f"{name}:{t} branches {sorted(set(s[t].keys()) ^ set(SLIM[t]))}")
                continue
            bad += [f"{name}:{t}: lateral probe {n} present" for n in pr[t] if n in s[t]]
            for b in SLIM[t]:
                if s[t][b].typename != utypes[t][b]:
                    bad.append(f"{name}:{t}:{b} type {s[t][b].typename} != {utypes[t][b]}")
                    continue
                lo, got = 0, []
                for n in BLOCKS[t]:
                    got.append(digest(s[t][b].array(library="np", entry_start=lo, entry_stop=lo + n)))
                    lo += n
                if got != rec["digests"][k][t][b]:
                    bad.append(f"{name}:{t}:{b} read-back bytes are not the built arrays'")
        out["slims"][k] = {"path": path, "sha256": sha_file(path), "size": os.path.getsize(path)}
    st = os.stat(a.mcfile)
    if sha_file(a.mcfile) != a.mcfile_sha:
        bad.append(f"MCFILE {a.mcfile} is not {a.mcfile_sha}")
    out["mcfile"] = {"path": a.mcfile, "sha256": a.mcfile_sha, "size": st.st_size, "mtime_ns": st.st_mtime_ns}
    out["verdict"] = "PASS" if not bad else "FAIL"
    out["problems"] = bad
    for b in bad:
        print(f"    {b}")
    print(f"C-SLIM/C-PATCH {out['verdict']}: {len(SLIMS)} slims read back")
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    for n in ("--uomni", "--driver", "--outdir", "--record", "--c2"):
        b.add_argument(n, required=True)
    b.add_argument("--dumps", nargs="+", required=True)
    v = sub.add_parser("verify")
    for n in ("--driver", "--outdir", "--record", "--mcfile", "--mcfile-sha", "--out"):
        v.add_argument(n, required=True)
    a = ap.parse_args(argv)
    try:
        return {"build": build, "verify": verify}[a.cmd](a)
    except Unusable as e:
        print(f"UNUSABLE: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
