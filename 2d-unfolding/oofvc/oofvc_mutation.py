#!/usr/bin/env python3
"""OOFVC mutation campaign: each mutant is one exact edit to a lane file, run against the tests named for it; the mutant
is killed if those tests fail. A copy of 2d-unfolding/oofvc is made inside the repository (so the tests' REPO is the
same), mutated, tested, and removed. Driver mutants edit the patched driver itself: the copy's oofvc_driver.diff and
make_tree.sh's pin are regenerated for the mutated driver, so the tree builds and the tests see the mutant.

  OOFVC_PY=python3 python3 oofvc_mutation.py OUT.json [NAME ...]      (all mutants, or the named ones)
A control run (no edit) must pass first; the record lists each mutant's verdict and the tests' tail.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PY = os.environ.get("OOFVC_PY", sys.executable)
M = "77d76cfc2d621f8faa010b75006811868494652a"

PURE = "Identity or MatchesRefC2C1 or (Join and not JoinTool) or Moved or Readings or ScorerArgv or ReadFlags"
MUTANTS = [
    # oofvc_lib.py
    ("LIB_BAND_LOWER", "oofvc_lib.py", '("LOWER", lambda r: r <= 0.80)', '("LOWER", lambda r: r <= 0.85)', "Readings"),
    ("LIB_BAND_LITTLE", "oofvc_lib.py", "0.95 <= r <= 1 / 0.95", "0.95 <= r <= 1.06", "Readings"),
    ("LIB_BAND_HIGHER", "oofvc_lib.py", '("HIGHER", lambda r: r >= 1.25)', '("HIGHER", lambda r: r > 1.25)', "Readings"),
    ("LIB_NFACTOR", "oofvc_lib.py", "return np.divide(sum_m, sum_m + o, out=np.ones_like(sum_m), where=sum_m > 0)",
     "return np.divide(sum_m, sum_m + 2 * o, out=np.ones_like(sum_m), where=sum_m > 0)", "Identity"),
    ("LIB_NFACTOR_ZERO", "oofvc_lib.py", "out=np.ones_like(sum_m), where=sum_m > 0)",
     "out=np.zeros_like(sum_m), where=sum_m > 0)", "Identity"),
    ("LIB_JOIN_EVENTS", "oofvc_lib.py", "if np.unique(ev[members]).size != 1 or np.unique(vals[members]).size != 1:",
     "if np.unique(vals[members]).size != 1:", "Join"),
    ("LIB_JOIN_VALUES", "oofvc_lib.py", "if np.unique(ev[members]).size != 1 or np.unique(vals[members]).size != 1:",
     "if np.unique(ev[members]).size != 1:", "Join"),
    ("LIB_JOIN_COPIES", "oofvc_lib.py", "int(cl[tied].max()) > max_copies", "int(cl[tied].max()) > max_copies + 1", "Join"),
    ("LIB_JOIN_COUNTS", "oofvc_lib.py", "bad = np.flatnonzero(cl != cr)", "bad = np.flatnonzero((cl == 0) | (cr == 0))",
     "Join"),
    ("LIB_JOIN_BITS", "oofvc_lib.py", "a = np.ascontiguousarray(np.column_stack([np.asarray(c, np.float64) for c in cols]))",
     "a = np.ascontiguousarray(np.round(np.column_stack([np.asarray(c, np.float64) for c in cols]), 12) + 0.0)", "Join"),
    ("LIB_TIE_BOUND", "oofvc_lib.py", "if tied_weight > frac * reference_weight:", "if tied_weight >= frac * reference_weight:",
     "Join"),
    ("LIB_BINS_CLOSED", "oofvc_lib.py", "    return global_index(pt, pz, pt_edges, pz_edges) >= 0\n",
     "    return in_rectangle(pt, pz, pt_edges, pz_edges)\n", "Moved"),
    ("LIB_TIE_ZERO", "oofvc_lib.py", "    if tied_weight == 0:  # no tie: nothing to bound (codex-school r1 #9)\n        return\n", "",
     "Join"),
    ("LIB_NUMU_CC", "oofvc_lib.py", "return (np.asarray(nu_pdg) == 14) & (np.asarray(current) == 1)",
     "return (np.abs(np.asarray(nu_pdg)) == 14) & (np.asarray(current) == 1)", "Moved"),
    ("LIB_HIGHER_FIRST", "oofvc_lib.py", 'if b_ibu == "HIGHER" or b_er == "HIGHER":', 'if b_ibu == "HIGHER":', "Readings"),
    ("LIB_NDF", "oofvc_lib.py", "return float(d @ ci @ d) / ndf, ndf", "return float(d @ ci @ d) / x.size, ndf", "Readings"),
    ("LIB_COLUMN_AREA", "oofvc_lib.py", "return float(np.dot(area, np.asarray(x, float)[idx]) / np.dot(area, np.asarray(pub, float)[idx]))",
     "return float(np.asarray(x, float)[idx].sum() / np.asarray(pub, float)[idx].sum())", "Readings"),
    ("LIB_READ_ORD", "oofvc_lib.py", "    if a.dtype != object:\n        return a\n", "    return a\n", "ReadFlags"),
    ("LIB_READ_REFUSE", "oofvc_lib.py",
     '        raise ReadRefusal(f"column {name}: an object column that is not one-character strings")', "        pass",
     "ReadFlags"),
    ("LIB_FLAG_RANGE", "oofvc_lib.py", "    if a.size and not np.all((a == 0) | (a == 1)):", "    if False:", "ReadFlags"),
    # oofvc_join.py
    ("JOIN_ROUTE", "oofvc_join.py", "n_dis = L.route_disagree(to_bkg, to_sig)", "n_dis = 0", "JoinTool"),
    ("JOIN_SIGW_TRUTH", "oofvc_join.py", '"pass": all(truth_equal.values())}', '"pass": True}\n    truth_equal = {}',
     "JoinTool"),
    ("JOIN_LAB_TOL", "oofvc_join.py", "LAB_RTOL = 1e-9", "LAB_RTOL = 1.0", "JoinTool"),
    ("JOIN_LAB_FINITE", "oofvc_join.py", '"pass": bool(finite and worst <= LAB_RTOL and cnt_ok)}',
     '"pass": bool(worst <= LAB_RTOL and cnt_ok)}', "JoinTool"),
    ("JOIN_DUP_KEPT", "oofvc_join.py", "rs = np.flatnonzero(to_sig & ~dup)", "rs = np.flatnonzero(to_sig)", "JoinTool"),
    ("JOIN_MOVED_RECO", "oofvc_join.py",
     'moved = L.moved_mask(d["nu_pdg"][m], d["current"][m], d["true_pt"][m], d["true_pz"][m], PT_OLD, PZ)',
     'moved = L.moved_mask(d["nu_pdg"][m], d["current"][m], d["reco_pt"][m], d["reco_pz"][m], PT_OLD, PZ)', "JoinTool"),
    ("JOIN_ROWS_WTRUTH", "oofvc_join.py", '"w_truth": d["w_truth"][m[e]].astype(np.float64)}',
     '"w_truth": bkg["w_bkg"][e].astype(np.float64)}', "JoinTool"),
    ("JOIN_TIE_BOUND", "oofvc_join.py", "        L.check_tie_bound(j[\"tied_weight\"], moved_w)\n",
     "        L.check_tie_bound(0.0, moved_w)\n", "JoinTool"),
    # oofvc_run.py
    ("RUN_ARGV", "oofvc_run.py", 'cfg_u["e_r"]["argv"] = list(cfg["e_r"]["argv"]) + MINERVA_ARGV + [str(a.rows)]',
     'cfg_u["e_r"]["argv"] = list(cfg["e_r"]["argv"])', "Runner"),
    ("RUN_O_MOVED", "oofvc_run.py", "    O_all = O + o_moved\n", "    O_all = O\n", "Runner"),
    ("RUN_O_SIGNAL", "oofvc_run.py", "o_rows = sel & pt_ok & (t >= 0) & (r < 0)", "o_rows = pt_ok & (t >= 0) & (r < 0)",
     "Runner"),
    ("RUN_NMOVED", "oofvc_run.py", "    dev = float(np.max(np.abs(o_moved - direct_moved))) if o_moved.size else 0.0\n",
     "    dev = 0.0\n    o_moved = o_moved * 0.5\n", "Runner"),
    ("RUN_FACTOR", "oofvc_run.py", "traj_n = {K: cap[\"traj\"][K] * fac for K in ks}",
     "traj_n = {K: cap[\"traj\"][K] * fac * fac for K in ks}", "Runner"),
    ("RUN_ROWS_SHA", "oofvc_run.py", "if sha256(a.rows) != a.rows_sha256:", "if False:", "Runner"),
    # oofvc_score.py (through the scorer test on the fixture units)
    ("SCORE_ROO_RAN", "oofvc_score.py", 'c["C-ROO_ran"] = ("C-ROO" in meta["controls"]) is not expect["numpy_unfolder"]',
     'c["C-ROO_ran"] = True', "Runner"),
    ("SCORE_FIX", "oofvc_score.py",
     'fix.update({f"{tag}:{k}": hist_identity(pair["off"], k) == hist_identity(pair["R"], k) for k in FIXED})',
     'fix.update({f"{tag}:{k}": hist_identity(pair["off"], k) == hist_identity(pair["R"], k) for k in FIXED + ("hBkgReco2D",)})',
     "Runner"),
    ("SCORE_MANIFEST", "oofvc_score.py", '                if set(p["outputs"][u]) != want:',
     '                if not set(p["outputs"][u]) <= want:', "Runner"),
    ("SCORE_JOIN_PIN", "oofvc_score.py", '"join_record": b.get("join_record") == expect["join_record"], "outputs"',
     '"join_record": True, "outputs"', "Runner"),
    ("SCORE_STAGE_PATH", "oofvc_score.py",
     'and base[1] == f"{STAGE}/runEventLoopOmniFold_MEFHC.root" and base[2] == "--mcfile"',
     'and Path(base[1]).name == "runEventLoopOmniFold_MEFHC.root" and base[2] == "--mcfile"', "ScorerArgv"),
    ("SCORE_OUTPUTS", "oofvc_score.py", '"outputs": outputs_ok(p)}', '"outputs": True}', "Runner"),
    ("SCORE_MOVE_COUNT", "oofvc_score.py", 'and grew == in_grid - counts.get("dropped_appended_weight", 0))}',
     'and grew == in_grid + 1 - counts.get("dropped_appended_weight", 0))}', "Runner"),
    ("SCORE_DIGEST", "oofvc_score.py", '"npz_digest": done["sha256"] == sha256(d / f"{kind}.npz"),',
     '"npz_digest": done["sha256"] != sha256(d / f"{kind}.npz"),', "Runner"),
    ("SCORE_CONVENTION", "oofvc_score.py", '"convention": bool(conv_ok),', '"convention": not conv_ok,', "Runner"),
    # the launch scripts: cov2d's protected reads (the director's request of 2026-11-26), through the Shell tests
    ("SH_FENCE_STATE", "launch/oofvc_dump.sh", "if (s[1] !~ /^(COMPLETED|FAILED|CANCELLED|",
     "if (s[1] !~ /^(RUNNING|COMPLETED|FAILED|CANCELLED|", "Shell"),
    ("SH_FENCE_SACCT", "launch/dump_array.sbatch",
     '|| { echo "[oofvc_dump] STOP: sacct failed ($1)"; exit 2; }', "|| true", "Shell"),
    ("SH_GATE_PAST", "launch/oofvc_dump.sh", '&& [ "$(date -u -d "$POST" +%s)" -lt "$(date -u +%s)" ]', "", "Shell"),
    ("SH_NUE_ORDER", "launch/dump_array.sbatch", 'fence_check "immediately before the binary"\nnue before',
     'nue before\nfence_check "immediately before the binary"', "Shell"),
    ("SH_NUE_PATH", "launch/dump_array.sbatch", 'nue_path_ok "$NUE" "$NUE_DECLARED" || {',
     'true || {', "Shell"),
    ("SH_NUE_CANON", "launch/dump_array.sbatch", '[ "$(readlink -f "$1")" = "$(readlink -f "$2")" ]',
     '[ "$(readlink -f "$1")" = "$2" ]', "Shell"),
    ("SH_NUE_EXISTS", "launch/dump_array.sbatch", '[ -f "$1" ] && [ -f "$2" ] && [ -n "$(readlink -f "$1")" ] && ', "",
     "Shell"),
    # the patched driver (re2_driver.py in the tree; the diff and the pin are regenerated)
    ("DRV_SKIP_VALUES", "DRIVER", "            if not (sim_bkg_pass[0] != 0 and float(sim_bkg[0]) == ept and",
     "            if False and (sim_bkg_pass[0] != 0 and float(sim_bkg[0]) == ept and", "Driver"),
    ("DRV_SKIP_COUNT", "DRIVER", "        if n_oofvc != len(oofvc_skip):", "        if n_oofvc > len(oofvc_skip):", "Driver"),
    ("DRV_THETA_CUT", "DRIVER", "            prc.append(True); ptr.append(True)",
     "            prc.append(True); ptr.append(math.atan2(t_pt, t_pz) < MAX_MUON_THETA_RAD)", "Driver"),
    ("DRV_APPEND_OUTSIDE", "DRIVER", "        if pt_lo <= r_pt < pt_hi and pz_lo <= r_pz < pz_hi:", "        if True:",
     "Driver"),
    ("DRV_TRUTH_CLOSED", "DRIVER", "        if not (pt_lo <= t_pt < pt_hi and pz_lo <= t_pz < pz_hi):",
     "        if not (pt_lo <= t_pt <= pt_hi and pz_lo <= t_pz <= pz_hi):", "Driver"),
    ("DRV_WEIGHT_ABORT", "DRIVER", '                counts["dropped_appended_weight"] += 1\n                continue',
     '                raise RuntimeError("[FAIL] OOFVC: weight")', "Driver"),
    ("DRV_USE_WEIGHTS", "DRIVER", " or not args.use_weights):", "):", "Driver"),
    ("DRV_WTRUTH", "DRIVER", "            wtl.append(w_t * pot_scale); wrl.append(w_r * pot_scale); sel.append(True)",
     "            wtl.append(w_r * pot_scale); wrl.append(w_r * pot_scale); sel.append(True)", "Driver"),
    ("DRV_REFUSE_CLOSURE", "DRIVER", "            args.closure or args.universe is not None", "            args.universe is not None",
     "Driver"),
    ("DRV_DEFAULT", "DRIVER", '                    default="production",', '                    default="minerva",', "Driver"),
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def driver_mutant(work: Path, old: str, new: str) -> None:
    """Edit the patched driver, regenerate the copy's diff against Tier 1's edge driver, and re-pin make_tree.sh."""
    td = Path(tempfile.mkdtemp(prefix="oofvc-mut-tree-"))
    try:
        subprocess.run(["bash", str(HERE / "make_tree.sh"), str(td / "t"), "archive", str(REPO), str(td / "s")],
                       check=True, capture_output=True, env=dict(os.environ, OOFVC_PY=PY))
        drv = td / "t" / "2d-unfolding" / "re2" / "re2_driver.py"
        text = drv.read_text()
        if text.count(old) != 1:
            raise SystemExit(f"driver mutant anchor found {text.count(old)} times: {old[:70]!r}")
        mutated = text.replace(old, new)
        plain = td / "plain.py"
        plain_text = subprocess.run(["git", "-C", str(REPO), "show", f"{M}:2d-unfolding/re2/re2_driver.py"],
                                    check=True, capture_output=True, text=True).stdout
        lines = plain_text.split("\n")
        lines[43] = "PT_EDGES = [0, 0.075, 0.15, 0.25, 0.325, 0.40, 0.475, 0.55,"
        plain.write_text("\n".join(lines))
        mpath = td / "mutated.py"
        mpath.write_text(mutated)
        diff = subprocess.run(["diff", "-u", "--label", "a/2d-unfolding/re2/re2_driver.py", "--label",
                               "b/2d-unfolding/re2/re2_driver.py", str(plain), str(mpath)],
                              capture_output=True, text=True).stdout
        (work / "oofvc_driver.diff").write_text(diff)
        mt = work / "make_tree.sh"
        s = mt.read_text()
        s2 = re.sub(r"OOFVC_SHA=[0-9a-f]{64}", f"OOFVC_SHA={sha(mpath)}", s)
        if s2 == s:
            raise SystemExit("make_tree.sh pin not found")
        mt.write_text(s2)
    finally:
        shutil.rmtree(td, ignore_errors=True)


def run_tests(work: Path, k: str) -> tuple[int, str]:
    p = subprocess.run([PY, "-B", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "test_oofvc.py", "-k", k],
                       cwd=str(work), capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS="1"))
    return p.returncode, (p.stdout + p.stderr)[-1500:]


def one(name, path, old, new, k) -> dict:
    work = REPO / "2d-unfolding" / f"oofvc_mut_{name.lower()}"
    if work.exists():
        raise SystemExit(f"{work} exists")
    shutil.copytree(HERE, work, ignore=shutil.ignore_patterns("__pycache__", "oofvc_mut_*"))
    t0 = time.time()
    try:
        if path == "DRIVER":
            driver_mutant(work, old, new)
        elif path is not None:
            f = work / path
            s = f.read_text()
            if s.count(old) != 1:
                raise SystemExit(f"{name}: anchor found {s.count(old)} times")
            f.write_text(s.replace(old, new))
        rc, tail = run_tests(work, k)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return {"name": name, "file": path, "tests": k, "rc": rc, "seconds": round(time.time() - t0, 1),
            "verdict": ("PASS" if rc == 0 else "FAIL") if name == "CONTROL" else ("KILLED" if rc != 0 else "SURVIVED"),
            "tail": tail}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    out = Path(argv[0])
    names = set(argv[1:])
    rec = {"schema": "oofvc-mutation/1", "python": PY, "files": {p.name: sha(p) for p in sorted(HERE.glob("*.py"))
                                                                 if not p.name.startswith("oofvc_mut_")},
           "diff_sha256": sha(HERE / "oofvc_driver.diff"), "results": []}
    ctl = one("CONTROL", None, "", "", PURE + " or JoinTool or Driver or Runner or Shell")
    rec["results"].append(ctl)
    if ctl["verdict"] != "PASS":
        out.write_text(json.dumps(rec, indent=1) + "\n")
        print("control FAILED")
        return 1
    for m in MUTANTS:
        if names and m[0] not in names:
            continue
        r = one(*m)
        rec["results"].append(r)
        print(r["name"], r["verdict"], r["seconds"], flush=True)
        out.write_text(json.dumps(rec, indent=1) + "\n")
    killed = sum(r["verdict"] == "KILLED" for r in rec["results"][1:])
    rec["summary"] = f"{killed}/{len(rec['results']) - 1} killed"
    out.write_text(json.dumps(rec, indent=1) + "\n")
    print(rec["summary"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
