#!/usr/bin/env python3
"""PTMC mutation campaign: each mutant is one exact edit to one PTMC file, run against the tests named for it. A
mutant is killed if those tests fail.
- A copy of 2d-unfolding/ptmc is made inside the repository (so the tests' REPO is the same), mutated, tested and
  removed.
- Driver mutants edit the PTMC-patched driver itself; the copy's ptmc_driver.diff and make_tree.sh's pin are
  regenerated, so the tree builds and the tests see the mutant.
- Shell mutants run the docker harnesses (debian:bookworm-slim) on the mutated copy.

  PTMC_PY=python3 python3 ptmc_mutation.py OUT.json [NAME ...]      (all mutants, or the named ones)
A control run (no edit) must pass first. The record lists each mutant's verdict and the tests' tail.
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
PY = os.environ.get("PTMC_PY", sys.executable)
M = "77d76cfc2d621f8faa010b75006811868494652a"
PURE = "Draws or Completeness or Coupling or Gates or Readings"
T = "test_ptmc.py"
S = "test_ptmc_score.py"
LT = "launch/test_launch.py"
HR, HS = "HARNESS:harness_remote.sh", "HARNESS:harness_sbatch.sh"
MUTANTS = [
    # ptmc_lib.py (the pure tests, and the scorer's through it)
    ("LIB_SIG_OFFSET", "ptmc_lib.py", "SIG_OFFSET, BKG_OFFSET = 0, 10_000_000, 20_000_000",
     "SIG_OFFSET, BKG_OFFSET = 0, 10_000_001, 20_000_000", T, "Draws"),
    ("LIB_APPENDED_ORDER", "ptmc_lib.py", '"appended": b_bkg[app]}', '"appended": b_bkg[app[::-1]]}', T, "Draws"),
    ("LIB_DRAW_TRUTH", "ptmc_lib.py",
     '"w_truth": bool(np.array_equal(np.asarray(w_truth_seen, float), np.asarray(w_truth_cv, float) * f_sig)),',
     '"w_truth": True,', T, "Draws"),
    ("LIB_INJ_OPEN", "ptmc_lib.py", "    keep = (pt >= pt_lo) & (pt <= pt_hi) & (pz >= pz_lo) & (pz <= pz_hi)",
     "    keep = (pt >= pt_lo) & (pt < pt_hi) & (pz >= pz_lo) & (pz < pz_hi)", T, "Draws"),
    ("LIB_LOST_NOT_ZERO", "ptmc_lib.py", "    c[lost] = 0.0\n", "", T, "Completeness"),
    ("LIB_DSTAR", "ptmc_lib.py", "    d_star = d_cv[live] * t_star_orig[live] / t_cv_orig[live]",
     "    d_star = d_cv[live]", T, "Completeness"),
    ("LIB_SUPPORT_UNWEIGHTED", "ptmc_lib.py", "        t_star = cell_sums(g, w * f, m, n)",
     "        t_star = cell_sums(g, f, m, n)", T, "Completeness"),
    ("LIB_COUPLE_ZERO_W", "ptmc_lib.py", "        m = (g >= 0) & (np.asarray(w, float) != 0)", "        m = (g >= 0)",
     T, "Coupling"),
    ("LIB_COUPLE_COUNTS_ONLY", "ptmc_lib.py", "    same = a.size == b.size and bool(np.array_equal(a, b))",
     "    same = a.size == b.size and bool(np.array_equal(a[\"g\"], b[\"g\"]))", T, "Coupling"),
    ("LIB_APPID_WRECO", "ptmc_lib.py",
     '"w_reco": np.array_equal(tail["w_reco"], np.asarray(rows["w_reco"], float)[idx] * pot_scale),',
     '"w_reco": True,', T, "Coupling"),
    ("LIB_RELCLOSE_ZERO", "ptmc_lib.py", "    if np.any(a[z] != 0):", "    if False:", T, "Gates"),
    ("LIB_RELCLOSE_NAN", "ptmc_lib.py",
     "    if a.shape != b.shape or not (np.all(np.isfinite(a)) and np.all(np.isfinite(b))):",
     "    if a.shape != b.shape:", T, "Gates"),
    ("LIB_SHAPE_LOO", "ptmc_lib.py", "    loo_bad = [i for i in range(n) if not ok(np.delete(D, i, axis=0))]",
     "    loo_bad = []", T, "Gates"),
    ("LIB_SHAPE_TOP", "ptmc_lib.py", "np.all(top > 0))", "np.all(top >= 0))", T, "Gates"),
    ("LIB_PROTO_ZEROVAR", "ptmc_lib.py", "    if np.any(diff[:, ~pos] != 0):", "    if False:", T, "Gates"),
    ("LIB_STAGED_INDEX", "ptmc_lib.py", '    return f"{int(b) + 1:03d}_xsec.root"', '    return f"{int(b):03d}_xsec.root"',
     T, "Gates"),
    ("LIB_DISP_MISMATCH", "ptmc_lib.py", "    if optional_mismatch or repoff_pass is False:",
     "    if repoff_pass is False:", T, "Readings"),
    ("LIB_STATEMENT_ROW3", "ptmc_lib.py", '    if b != "differ":', '    if b == "agree":', T, "Readings"),
    # the driver hunk (the diff and the pin are regenerated)
    ("DRV_APPENDED_DRAW", "DRIVER", "            b_truth = np.concatenate([b_truth, b_bkg[ptmc_app]])",
     "            b_truth = np.concatenate([b_truth, rng_mc.poisson(1.0, size=ptmc_app.size).astype(float)])",
     T, "Runner"),
    ("DRV_DRAW_SIZE", "DRIVER",
     '        n_sig_draw = sig["w_truth"].shape[0] - (0 if ptmc_app is None else ptmc_app.size)  # PTMC',
     '        n_sig_draw = sig["w_truth"].shape[0]  # PTMC', T, "Runner"),
    ("DRV_LOST_NOT_ZERO", "DRIVER", "    c_star[lost] = 0.0\n", "", T, "Runner"),
    ("DRV_DSTAR", "DRIVER", "    d_star = d_cv[live] * t_star_orig[live] / t_cv_orig[live]", "    d_star = d_cv[live]",
     T, "Runner"),
    ("DRV_APPENDED_ORDER", "DRIVER",
     '    out["appended_entry"] = np.asarray(appended_entry, dtype=np.int64)  # PTMC',
     '    out["appended_entry"] = np.asarray(appended_entry[::-1], dtype=np.int64)  # PTMC', T, "Runner"),
    ("DRV_STREAMS", "DRIVER",
     '            or (args.bootstrap_seed is not None and (args.bootstrap_streams != "three" or args.unit_factors))',
     '            or (args.bootstrap_seed is not None and args.unit_factors)', T, "Driver"),
    ("DRV_UNIT_FACTORS", "DRIVER",
     '            or (args.bootstrap_seed is not None and (args.bootstrap_streams != "three" or args.unit_factors))',
     '            or (args.bootstrap_seed is not None and args.bootstrap_streams != "three")', T, "Driver"),
    ("DRV_PRODUCTION_TOO", "DRIVER",
     '        if args.signal_convention == "minerva" and w_truth_cv is not None:  # PTMC: R replica (section 2.2)',
     '        if w_truth_cv is not None:  # PTMC: R replica (section 2.2)', T, "Driver"),
    # the runner (through the fixture units)
    ("RUN_NO_MINERVA", "ptmc_run.py",
     '        cfg_u["e_r"]["argv"] = list(cfg["e_r"]["argv"]) + MINERVA_ARGV + [str(rows_path)]',
     '        cfg_u["e_r"]["argv"] = list(cfg["e_r"]["argv"])', T, "Runner"),
    ("RUN_FILL_K", "ptmc_run.py",
     '        h = C.filled(driver, cap["tin"], cap["w_in"], C.event_factors(cap["traj"][K], cap["T"], cap["tin"]),',
     '        h = C.filled(driver, cap["tin"], cap["w_in"], C.event_factors(cap["traj"][ks[0]], cap["T"], cap["tin"]),',
     T, "Runner"),
    ("RUN_APPID_POT", "ptmc_run.py", '        pot = float(f.Get("potScale").GetVal())', "        pot = 1.0", T, "Runner"),
    ("RUN_PAIR_DIGEST", "ptmc_run.py", '        cap["digest_omnifold"] = P.digest(*arrays)',
     '        cap["digest_omnifold"] = P.digest(*arrays[:-1])', T, "Runner"),
    ("RUN_INJ_STORED_REVERSED", "ptmc_run.py",
     '"inj_entries": np.asarray(cap.get("inj_entries", np.zeros(0, np.int64)), np.int64)}',
     '"inj_entries": np.asarray(cap.get("inj_entries", np.zeros(0, np.int64)), np.int64)[::-1]}', T, "Runner"),
    # the scorer (hand-made products)
    ("SC_ABSENT_AS_FORMED", "ptmc_score.py", '    disp = P.disposition(True, True, bool(absent), bool(mismatch), repoff)',
     '    disp = P.disposition(True, True, False, bool(mismatch), repoff)', S, "Scorer"),
    ("SC_FILL_SETS_ONLY", "ptmc_score.py",
     "           and not (all(np.array_equal(np.asarray(U[u][k]), want[k]) for k in want)",
     "           and not (np.array_equal(np.unique(np.asarray(U[u][\"fill_entry\"])), np.unique(want[\"fill_entry\"]))",
     S, "Scorer"),
    ("SC_MISMATCH_IGNORED", "ptmc_score.py", "        if not ok:\n            mismatch.append(name)\n        else:\n            ref_c2[b] = z",
     "        if False:\n            mismatch.append(name)\n        else:\n            ref_c2[b] = z", S, "Scorer"),
    ("SC_RANK_LITERAL", "ptmc_score.py", '        sg = P.shape_gate(delta, D, rank=CONST["RANK"], n=CONST["N"])',
     '        sg = P.shape_gate(delta, D, rank=50, n=CONST["N"])', S, "Scorer"),
    ("SC_DRAW_AGG", "ptmc_score.py", 'and st["n"]["mc"] == d["n_original"] and st["sum"]["mc"] == d["original_sum"]',
     'and st["n"]["mc"] == d["n_original"] and st["sum"]["data"] == d["original_sum"]', S, "Scorer"),
    ("SC_WORDS", "ptmc_score.py", '"reading": RR.classify_t(t, P.WORDS),', '"reading": RR.classify_t(t, P.WORDS[::-1]),',
     S, "Scorer"),
    # the launch helpers
    ("PP_FLOOR", "launch/ptmc_pilot_post.py", "MARGIN, FLOOR = 12.5, 11.5, 5, 10, 1.5, 1.1",
     "MARGIN, FLOOR = 12.5, 11.5, 5, 10, 1.5, 1.0", LT, "PilotPost"),
    ("PP_CAP_PER_NODE", "launch/ptmc_pilot_post.py", "cap_left / NODES * 3600.0)", "cap_left * 3600.0)", LT, "PilotPost"),
    ("PP_STOP_AT", "launch/ptmc_pilot_post.py", "FLOOR = 12.5, 11.5, 5,", "FLOOR = 12.5, 12.6, 5,", LT, "PilotPost"),
    ("PP_COUPLE", "launch/ptmc_pilot_post.py", '                ok = ok and ctl.get("C-COUPLE", {}).get("pass") is True',
     "                ok = ok", LT, "PilotPost"),
    ("D4_ABSENT_FAILS", "launch/ptmc_stage_d4.py",
     '            except FileNotFoundError:\n                manifest["absent"].append(str(src))\n                continue',
     "            except FileNotFoundError:\n                return 5", LT, "StageD4"),
    ("D4_SYMLINK_OK", "launch/ptmc_stage_d4.py", "            if not stat.S_ISREG(st.st_mode):", "            if False:",
     LT, "StageD4"),
    # the shell steps (the docker harnesses)
    ("SH_FENCE_STATE", "launch/ptmc_remote.sh", "if (s[1] !~ /^(COMPLETED|FAILED|CANCELLED|",
     "if (s[1] !~ /^(RUNNING|COMPLETED|FAILED|CANCELLED|", HR, None),
    ("SH_COPY_PIN", "launch/ptmc_remote.sh", '  [ "$(sha_of "$2")" = "$3" ] || stop "the copy of $1 is not $3"', "  true",
     HR, None),
    ("SH_NO_PTMC", "launch/ptmc_remote.sh", '  [ "$n" = 0 ] || stop "a ptmc job is queued or running"', "  true", HR, None),
    ("SH_LIMIT_RANGE", "launch/ptmc_remote.sh", '[ "$L" -le 600 ]', '[ "$L" -le 6000 ]', HR, None),
    ("SH_DEPLOY_CHECK", "launch/ptmc_remote.sh",
     '  (cd "$R/deploy" && sha256sum -c --quiet "$R/logs/deploy.sha256") || stop "the deploy tree differs from its digests"',
     "  true", HR, None),
    ("SH_LANE_SEEDS", "launch/replicas.sbatch", "    b=$((2 + l + 20 * k))", "    b=$((1 + l + 20 * k))", HS, None),
    ("SH_PILOT_UNITS", "launch/pilot.sbatch", "p_off_b2 p_off_b3 p_off_b4 p_off_b5; do", "p_off_b2 p_off_b3 p_off_b4; do",
     HS, None),
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def driver_mutant(work: Path, old: str, new: str) -> None:
    """Edit the PTMC-patched driver, regenerate the copy's ptmc_driver.diff against the OOFVC-on-M driver, and
    re-pin the copy's make_tree.sh."""
    td = Path(tempfile.mkdtemp(prefix="ptmc-mut-"))
    try:
        base = td / "base" / "2d-unfolding" / "re2"
        base.mkdir(parents=True)
        src = subprocess.run(["git", "-C", str(REPO), "show", f"{M}:2d-unfolding/re2/re2_driver.py"],
                             check=True, capture_output=True).stdout
        (base / "re2_driver.py").write_bytes(src)
        subprocess.run(["git", "init", "-q"], cwd=td / "base", check=True)
        subprocess.run(["git", "apply", str(REPO / "2d-unfolding" / "oofvc" / "oofvc_driver.diff")], cwd=td / "base",
                       check=True)
        oofvc_text = (base / "re2_driver.py").read_text()
        subprocess.run(["git", "apply", str(HERE / "ptmc_driver.diff")], cwd=td / "base", check=True)
        text = (base / "re2_driver.py").read_text()
        if text.count(old) != 1:
            raise SystemExit(f"driver mutant anchor found {text.count(old)} times: {old[:70]!r}")
        mutated = text.replace(old, new)
        a, b = td / "a.py", td / "b.py"
        a.write_text(oofvc_text)
        b.write_text(mutated)
        diff = subprocess.run(["diff", "-u", "--label", "a/2d-unfolding/re2/re2_driver.py", "--label",
                               "b/2d-unfolding/re2/re2_driver.py", str(a), str(b)], capture_output=True, text=True).stdout
        (work / "ptmc_driver.diff").write_text(diff)
        mt = work / "make_tree.sh"
        s = mt.read_text()
        s2 = re.sub(r"PTMC_SHA=[0-9a-f]{64}", f"PTMC_SHA={sha(b)}", s)
        if s2 == s:
            raise SystemExit("make_tree.sh pin not found")
        mt.write_text(s2)
    finally:
        shutil.rmtree(td, ignore_errors=True)


def run_tests(work: Path, test: str, k: str | None) -> tuple[int, str]:
    if test.startswith("HARNESS:"):
        h = test.split(":", 1)[1]
        p = subprocess.run(["docker", "run", "--rm", "-v", f"{work / 'launch'}:/h:ro", "debian:bookworm-slim",
                            "bash", f"/h/{h}"], capture_output=True, text=True)
    else:
        cmd = [PY, "-B", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", test] + (["-k", k] if k else [])
        p = subprocess.run(cmd, cwd=str(work), capture_output=True, text=True,
                           env=dict(os.environ, OMP_NUM_THREADS="1", PTMC_PY=PY))
    return p.returncode, (p.stdout + p.stderr)[-1500:]


def one(name, path, old, new, test, k) -> dict:
    work = REPO / "2d-unfolding" / f"ptmc_mut_{name.lower()}"
    if work.exists():
        raise SystemExit(f"{work} exists")
    shutil.copytree(HERE, work, ignore=shutil.ignore_patterns("__pycache__", "ptmc_mut_*"))
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
        rcs, tails = [], []
        for t in ([test] if not isinstance(test, list) else test):
            rc, tail = run_tests(work, t, k)
            rcs.append(rc)
            tails.append(tail)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    bad = any(r != 0 for r in rcs)
    return {"name": name, "file": path, "tests": [test, k], "rc": rcs, "seconds": round(time.time() - t0, 1),
            "verdict": ("FAIL" if bad else "PASS") if name == "CONTROL" else ("KILLED" if bad else "SURVIVED"),
            "tail": tails[-1]}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    out = Path(argv[0])
    names = set(argv[1:])
    files = sorted(p for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    rec = {"schema": "ptmc-mutation/1", "python": PY,
           "files": {str(p.relative_to(HERE)): sha(p) for p in files}, "results": []}
    ctl = one("CONTROL", None, "", "", [T, S, LT, HR, HS], None)
    rec["results"].append(ctl)
    out.write_text(json.dumps(rec, indent=1) + "\n")
    if ctl["verdict"] != "PASS":
        print("control FAILED", ctl["rc"])
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
