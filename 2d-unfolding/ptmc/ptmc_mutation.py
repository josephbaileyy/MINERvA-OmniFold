#!/usr/bin/env python3
"""PTMC mutation campaign: each mutant is one exact edit to one PTMC file, run against the tests named for it. A
mutant is killed if those tests fail.
- A copy of 2d-unfolding/ptmc is made inside the repository (so the tests' REPO is the same), mutated, tested and
  removed.
- Driver mutants edit the PTMC-patched driver itself; the copy's ptmc_driver.diff and make_tree.sh's pin are
  regenerated, so the tree builds and the tests see the mutant.
- Shell mutants run the docker harnesses (debian:bookworm-slim) on the mutated copy; the Mac launcher's mutants run
  its local harness (stubbed ssh and scp).
- A mutant naming several test files is killed if any of them fails.

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
HL = "LOCAL:harness_launch.sh"  # the Mac launcher's own harness (stubs on PATH; macOS shasum)
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
    ("LIB_COND_FLOOR", "ptmc_lib.py", "COND_FLOOR = 1e-10", "COND_FLOOR = 1e-14", T, "Gates"),
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
    ("SC_RANK_LITERAL", "ptmc_score.py", '        sg = P.shape_gate(delta, D, rank=CONST["RANK"], n=CONST["N"])',
     '        sg = P.shape_gate(delta, D, rank=50, n=CONST["N"])', S, "Scorer"),
    ("SC_DRAW_AGG", "ptmc_score.py", 'and st["n"]["mc"] == d["n_original"] and st["sum"]["mc"] == d["original_sum"]',
     'and st["n"]["mc"] == d["n_original"] and st["sum"]["data"] == d["original_sum"]', S, "Scorer"),
    ("SC_WORDS", "ptmc_score.py", '"reading": RR.classify_t(t, P.WORDS),', '"reading": RR.classify_t(t, P.WORDS[::-1]),',
     S, "Scorer"),
    # the launch helpers
    ("D4_SYMLINK_OK", "launch/ptmc_stage_d4.py", "            if not stat.S_ISREG(st.st_mode):", "            if False:",
     LT, "StageD4"),
    # the shell steps (the docker harnesses)
    ("SH_FENCE_STATE", "launch/ptmc_remote.sh", "if (s[1] !~ /^(COMPLETED|FAILED|CANCELLED|",
     "if (s[1] !~ /^(RUNNING|COMPLETED|FAILED|CANCELLED|", HR, None),
    ("SH_NO_PTMC", "launch/ptmc_remote.sh", '  [ "$n" = 0 ] || stop "a ptmc job is queued or running"', "  true", HR, None),
    ("SH_LIMIT_RANGE", "launch/ptmc_remote.sh", '[ "$L" -le 600 ]', '[ "$L" -le 6000 ]', HR, None),
    ("SH_DEPLOY_CHECK", "launch/ptmc_remote.sh",
     '  (cd "$R/deploy" && sha256sum -c --quiet "$R/logs/deploy.sha256") || stop "the deploy tree differs from its digests"',
     "  true", HR, None),
    ("SH_LANE_SEEDS", "launch/replicas.sbatch", "    b=$((2 + l + 20 * k))", "    b=$((1 + l + 20 * k))", HS, None),
    # ptmc_lib.py: the stale anchors, re-anchored
    ("LIB_SHAPE_TOP", "ptmc_lib.py", "np.all(lam[top] > 0))", "np.all(lam[top] >= 0))", T, "Gates"),
    ("LIB_PROTO_ZEROVAR", "ptmc_lib.py", '"zero_variance_cells_differing": int(np.sum(np.any(zv != 0, axis=0))),',
     '"zero_variance_cells_differing": 0,', T, "Gates"),
    # ptmc_lib.py: the hardening's gates
    ("LIB_CSTAR_ONESIDED", "ptmc_lib.py", '"finite": bool(np.all(np.isfinite(c)) and not one_sided.any() and d_ok)}',
     '"finite": bool(np.all(np.isfinite(c)) and d_ok)}', T, "Completeness"),
    ("LIB_CSTAR_NEGATIVE", "ptmc_lib.py", " or any(np.any(x < 0) for x in ops[:4]):", ":", T, "Completeness"),
    ("LIB_COUPLE_NEGATIVE", "ptmc_lib.py",
     "    if np.any(np.asarray(w_d, float) < 0) or np.any(np.asarray(w_s, float) < 0):", "    if False:", T, "Coupling"),
    ("LIB_RECEIPT_DIGEST", "ptmc_lib.py",
     'if sha256_file(npz) != mk.get("sha256") or sha256_file(root) != mk.get("root_sha256"):',
     'if sha256_file(npz) != mk.get("sha256"):', [LT, S], None),
    ("LIB_RECEIPT_ARGS_FINITE", "ptmc_lib.py", '        if meta.get("extract_args_finite") is not True:',
     "        if False:", [LT, S], None),
    ("LIB_RECEIPT_EXTRA_CONTROL", "ptmc_lib.py",
     '        bad += sorted(c for c, v in ctl.items() if not (isinstance(v, dict) and v.get("pass") is True))\n', "",
     [LT, S], None),
    ("LIB_RECEIPT_REQUIRED", "ptmc_lib.py",
     '        bad = sorted(c for c in req if not (isinstance(ctl.get(c), dict) and ctl[c].get("pass") is True))',
     "        bad = []", [LT, S], None),
    ("LIB_RECEIPT_IDENTITY", "ptmc_lib.py",
     'meta.get("convention") == conv and meta.get("bootstrap_seed") == b):', 'meta.get("convention") == conv):',
     [LT, S], None),
    # the runner
    ("RUN_REUSE_DIGEST", "ptmc_run.py",
     ' and sha256(npz) == mk.get("sha256") and sha256(root) == mk.get("root_sha256"))', ")", T, "Runner"),
    ("RUN_ROWS_FILE_PIN", "ptmc_run.py", ' or sha256(a.rows) != PINS["rows"]', "", T, "Runner"),
    ("RUN_DUP_UNIT", "ptmc_run.py", "    if len(set(names)) != len(names):", "    if False:", T, "Runner"),
    ("RUN_PAIR_MASK", "ptmc_run.py", 'and y_r["pass"] and mpr_ok)}', 'and y_r["pass"])}', T, "Runner"),
    ("RUN_REFINE_DIGEST", "ptmc_run.py", "\n                                         and P.digest(rw) == P.digest(mw_raw))}",
     ")}", T, "Runner"),
    ("RUN_ARGS_FINITE", "ptmc_run.py", "    passed = all(c[\"pass\"] is True for c in controls.values()) and args_finite",
     "    passed = all(c[\"pass\"] is True for c in controls.values())", T, "Runner"),
    ("RUN_COMP_AXES", "ptmc_run.py", 'controls["C-COMP"]["pass"] = bool(controls["C-COMP"]["pass"] and axes_ok)',
     'controls["C-COMP"]["pass"] = bool(controls["C-COMP"]["pass"])', T, "Runner"),
    # the scorer: the stale anchors, re-anchored
    ("SC_FILL_SETS_ONLY", "ptmc_score.py",
     'all(np.array_equal(np.asarray(z[k]), mref["want"][k]) for k in FILL_KEYS)',
     'np.array_equal(np.unique(np.asarray(z["fill_entry"])), np.unique(mref["want"]["fill_entry"]))',
     S, "Scorer"),
    ("SC_MISMATCH_IGNORED", "ptmc_score.py", "            ref_c2[b] = {K: ibu(z, K) for K in scan}\n        else:\n            mismatch.append(name)",
     "            ref_c2[b] = {K: ibu(z, K) for K in scan}\n        else:\n            ref_c2[b] = None", S, "Scorer"),
    # the scorer: the hardening's gates
    ("SC_INVENTORY_EXTRA", "ptmc_score.py", "    need(not extra and not missing,", "    need(not missing,", S, None),
    ("SC_CANONICAL_ARGV", "ptmc_score.py", '        need(m["argv"] == canonical_argv(tree_cfg, conv, b, rows),',
     "        need(True,", S, None),
    ("SC_D4_FETCHED", "ptmc_score.py", '    need(have == set(copied) | {"manifest.json"},',
     "    need(set(copied) <= have,", S, None),
    ("SC_DUP_MARKER", "ptmc_score.py", "        need(f.stem not in out,", "        need(True,", S, None),
    ("SC_SIM_COVERAGE", "ptmc_score.py", "        need(set(cells_idx.tolist()) <= cov,", "        need(True,", S, None),
    ("SC_COND_GUARD", "ptmc_score.py", '        need(cond["pass"],', "        need(True,", S, None),
    ("SC_EXCEPTION_STOP", "ptmc_score.py", "    except Exception as e:  # every failure is a STOP",
     "    except Stop as e:  # every failure is a STOP", S, None),
    # the pilot's post: the stale anchors, re-anchored
    ("PP_FLOOR", "launch/ptmc_pilot_post.py", '600 * limit_min >= 11 * runtime', '600 * limit_min >= 10 * runtime',
     LT, "PilotPost"),
    ("PP_CAP_PER_NODE", "launch/ptmc_pilot_post.py", "(CAP_S - pilot_ns) // (NODES * 60))", "(CAP_S - pilot_ns) // 60)",
     LT, "PilotPost"),
    ("PP_STOP_AT", "launch/ptmc_pilot_post.py", "CAP_S, STOP_S = 45000, 41400", "CAP_S, STOP_S = 45000, 43200",
     LT, "PilotPost"),
    ("PP_RECEIPTS", "launch/ptmc_pilot_post.py",
     '    r["every_pilot_unit_passes"] = all(v["ok"] for v in receipts.values())',
     '    r["every_pilot_unit_passes"] = True', LT, "PilotPost"),
    # the pilot's post: the hardening's gates
    ("PP_JOBID", "launch/ptmc_pilot_post.py", "        if head != jobid:", "        if False:", LT, "PilotPost"),
    ("PP_JOB_NODES", "launch/ptmc_pilot_post.py", ' and job["nodes"] == PILOT_NODES', "", LT, "PilotPost"),
    ("PP_STEP_NODES", "launch/ptmc_pilot_post.py", 's["nodes"] == 1 and 0 < s["elapsed"] <= job["elapsed"]',
     '0 < s["elapsed"]', LT, "PilotPost"),
    ("PP_NO_CNORM", "launch/ptmc_pilot_post.py", '    for k in ("C-NORM", "C-FIX", "C-MOVE-seed1", "C-SUPPORT-table"):',
     '    for k in ("C-FIX", "C-MOVE-seed1", "C-SUPPORT-table"):', LT, "PilotPost"),
    ("PP_NO_CFIX", "launch/ptmc_pilot_post.py", '    for k in ("C-NORM", "C-FIX", "C-MOVE-seed1", "C-SUPPORT-table"):',
     '    for k in ("C-NORM", "C-MOVE-seed1", "C-SUPPORT-table"):', LT, "PilotPost"),
    ("PP_NO_CMOVE", "launch/ptmc_pilot_post.py", '    for k in ("C-NORM", "C-FIX", "C-MOVE-seed1", "C-SUPPORT-table"):',
     '    for k in ("C-NORM", "C-FIX", "C-SUPPORT-table"):', LT, "PilotPost"),
    ("PP_NO_CSUPPORT", "launch/ptmc_pilot_post.py", '    for k in ("C-NORM", "C-FIX", "C-MOVE-seed1", "C-SUPPORT-table"):',
     '    for k in ("C-NORM", "C-FIX", "C-MOVE-seed1"):', LT, "PilotPost"),
    ("PP_RECHECK_L", "launch/ptmc_pilot_post.py",
     '\n                and d.get("time_limit_minutes") == prev.get("time_limit_minutes"))', ")", LT, "PilotPost"),
    # the D4 staging
    ("D4_ABSENT_FAILS", "launch/ptmc_stage_d4.py",
     '                manifest["absent"].append(str(src))\n                continue\n            except OSError',
     "                return 5\n            except OSError",
     LT, "StageD4"),
    ("D4_MANDATORY", "launch/ptmc_stage_d4.py", "                if name in MANDATORY:", "                if False:",
     LT, "StageD4"),
    ("D4_PARENT_DIR", "launch/ptmc_stage_d4.py", "            if not stat.S_ISDIR(os.lstat(d).st_mode):",
     "            if False:", LT, "StageD4"),
    ("D4_CHANGED", "launch/ptmc_stage_d4.py", "            if ident(after) != ident(st) or", "            if False or",
     LT, "StageD4"),
    # ptmc_remote.sh: the stale anchor, re-anchored, and the hardening's gates
    ("SH_COPY_PIN", "launch/ptmc_remote.sh", '  [ "$h" = "$3" ] || stop "the copy of $1 is not $3"', "  true", HR, None),
    ("SH_STAGE_HOST", "launch/ptmc_remote.sh", 'stage:*) stop "stage runs on a DTN, not $host";;', "stage:*) ;;", HR, None),
    ("SH_LOGIN_HOST", "launch/ptmc_remote.sh", '*:dtn*) stop "$MODE runs on a login node";;', "*:dtn*) ;;", HR, None),
    ("SH_STAGE_AGE", "launch/ptmc_remote.sh", "[ $((t1 - t0)) -le 900 ]", "[ $((t1 - t0)) -le 9000 ]", HR, None),
    ("SH_CLAIM", "launch/ptmc_remote.sh",
     'claim() { mkdir "$R/claims/$1" 2>/dev/null || stop "phase $1 is already claimed (a second invocation, or it ran)"; }',
     'claim() { mkdir -p "$R/claims/$1"; }', HR, None),
    ("SH_AWK_STATUS", "launch/ptmc_remote.sh", '    || stop "awk failed ($1)"', "    || true", HR, None),
    ("SH_STAGE_LS", "launch/ptmc_remote.sh", 'st=$(ls -A "$R/stage") || stop "ls of the stage failed";',
     'st=$(ls -A "$R/stage" 2>/dev/null);', HR, None),
    ("SH_RECHECK_L", "launch/ptmc_remote.sh",
     '''  printf '%s' "$chk" | grep -q "\\"time_limit_minutes\\": $L}" || stop "the recheck's L is not $L"''', "  true",
     HR, None),
    ("SH_REPLICAS_N5", "launch/ptmc_remote.sh", 'sbatch --parsable -N 5 -t "$L"', 'sbatch --parsable -t "$L"', HR, None),
    ("SH_PILOT_N2", "launch/ptmc_remote.sh", "sbatch --parsable -N 2 ", "sbatch --parsable ", HR, None),
    ("SH_DEPLOY_INVENTORY", "launch/ptmc_remote.sh",
     '  [ "$have" = "$want" ] || stop "the deploy digests do not list exactly the declared files"', "  true", HR, None),
    ("SH_DRIVER_PIN", "launch/ptmc_remote.sh", '    || stop "the deployed driver is not $DRIVER_SHA"', "    || true",
     HR, None),
    ("SH_JOBID_PERSIST", "launch/ptmc_remote.sh",
     '  echo "$2" > "$R/logs/$1.jobid" || stop "the $1 job $2 was submitted but its id could not be recorded"',
     '  echo "$2" > "$R/logs/$1.jobid" 2>/dev/null', HR, None),
    ("SH_POST_OTHER_JOB", "launch/ptmc_remote.sh", '      || stop "sacct for the $f job $j has a row of another job"',
     "      || true", HR, None),
    ("SH_SACCT_EMPTY", "launch/ptmc_remote.sh", '  [ -n "$out" ] || stop "sacct returned nothing for job $j"', "  true",
     HR, None),
    ("SH_THREADS", "launch/ptmc_remote.sh", "export LC_ALL=C OMP_NUM_THREADS=1 MKL_NUM_THREADS=1",
     "export LC_ALL=C MKL_NUM_THREADS=1", HR, None),
    ("SH_SHA_STATUS", "launch/ptmc_remote.sh", '  h=$(sha_of "$LIB") || stop "sha256 of libRooUnfold.so failed"',
     '  h=$(sha_of "$LIB")', HR, None),
    # the sbatch files: the stale anchor, re-anchored, and the hardening's gates
    ("SH_PILOT_UNITS", "launch/pilot.sbatch", 'UNITS="p_off_c p_R_c p_off_b1 p_R_b1 p_off_b2 p_off_b3 p_off_b4 p_off_b5"',
     'UNITS="p_off_c p_R_c p_off_b1 p_R_b1 p_off_b2 p_off_b3 p_off_b4"', HS, None),
    ("SB_PILOT_NODES", "launch/pilot.sbatch", '[ "${SLURM_JOB_NUM_NODES:-}" = 2 ] ||', "true ||", HS, None),
    ("SB_PILOT_ROWS", "launch/pilot.sbatch", '[ "$SHA" = "$ROWS_SHA" ] ||', "true ||", HS, None),
    ("SB_PILOT_OUTCOMES", "launch/pilot.sbatch", '[ "$bad" = 0 ] && [ "$n" = 8 ] ||', "true ||", HS, None),
    ("SB_REPS_NODES", "launch/replicas.sbatch", '[ "${SLURM_JOB_NUM_NODES:-}" = 5 ] ||', "true ||", HS, None),
    ("SB_REPS_LIMIT", "launch/replicas.sbatch", '[ "$tm" = "$L" ]', '[ "$tm" -le 100000 ]', HS, None),
    ("SB_REPS_PARSE", "launch/replicas.sbatch", '  for v in "$d" "$h" "$m" "$s"; do case "$v" in \'\'|*[!0-9]*) return 1;; esac; done\n',
     "", HS, None),
    ("SB_REPS_ROWS", "launch/replicas.sbatch", '[ "$SHA" = "$ROWS_SHA" ] ||', "true ||", HS, None),
    ("SB_REPS_COUNT", "launch/replicas.sbatch", '[ "$n" = 199 ] && [ "$t" = 199 ]', "true", HS, None),
    # the Mac launcher (its local harness)
    ("LA_STAGE_NODE", "launch/ptmc_launch.sh", '[ "$NODE" = dtn01 ] ||', "true ||", HL, None),
    ("LA_DTN_ROUTE", "launch/ptmc_launch.sh", 'dtn01.nersc.gov "$R"', 'saul.nersc.gov "$R"', HL, None),
    ("LA_LOGIN_NODE", "launch/ptmc_launch.sh", 'case "$NODE" in login[0-9][0-9]) ;; *)', 'case "$NODE" in *) ;; x)', HL, None),
    ("LA_FETCH_HASH", "launch/ptmc_launch.sh",
     'h=$(shasum -a 256 "$F/$f" | cut -d\' \' -f1) || { echo "STOP: hashing $f failed"; exit 9; }',
     'h=$(shasum -a 256 "$F/$f" | cut -d\' \' -f1)', HL, None),
    ("LA_SCRIPT_SHA", "launch/ptmc_launch.sh", '[ "$h" = "$SHA" ] ||', "true ||", HL, None),
    # code-confirm-1 (codex-school2): one mutant per new gate
    ("SH_STAT_STATUS", "launch/ptmc_remote.sh",
     '  st=$(stat -c \'%n|atime=%x\' "$1") && [ -n "$st" ] || stop "stat $1 (before the copy)"',
     '  st=$(stat -c \'%n|atime=%x\' "$1")', HR, None),
    ("SH_PILOT_T60", "launch/ptmc_remote.sh", 'sbatch --parsable -N 2 -t "$PILOT_MIN"', "sbatch --parsable -N 2", HR, None),
    ("SH_DECISION_PRINT", "launch/ptmc_remote.sh",
     '    cat "$R/pilot-post/decision.json" || stop "printing the decision (the C-SUPPORT table) failed"',
     '    cat "$R/pilot-post/decision.json" 2>/dev/null', HR, None),
    ("SH_CHARGE_FIELDS", "launch/ptmc_remote.sh",
     "if ($5 !~ /^[0-9]+$/ || $6 !~ /^[0-9]+$/ || $5 == 0 || $6 == 0) bad = 1; ", "", HR, None),
    ("SH_TARS_SHA", "launch/ptmc_remote.sh", "sha256sum post.tar.gz d4.tar.gz > tars.sha256",
     "sha256sum post.tar.gz > tars.sha256", HR, None),
    ("SB_PILOT_LIMIT", "launch/pilot.sbatch", '[ "$tm" = 60 ] ||', "true ||", HS, None),
    ("SB_LANES_LITERAL", "launch/replicas.sbatch", "for l in $LANES; do lane $l & pid_of[$l]=$!; done",
     "for l in $(seq 0 19); do lane $l & pid_of[$l]=$!; done", HS, None),
    ("SB_LANES_20", "launch/replicas.sbatch", ' && [ "$nl" = 20 ]', "", HS, None),
    ("LA_FETCH_COMPARE", "launch/ptmc_launch.sh",
     '[ "$h" = "$want" ] || { echo "STOP: the fetched $f is $h, the remote one $want"; exit 9; }', ":", HL, None),
    ("PP_STEP_ID_REPEAT", "launch/ptmc_pilot_post.py",
     '        if jid in ids:\n            raise ValueError(f"a repeated step id {jid}")\n', "", LT, "PilotPost"),
    ("PP_STEP_ID_NUMERIC", "launch/ptmc_pilot_post.py",
     "if tail and tail not in HOUSEKEEPING and not (tail.isdigit() and tail == str(int(tail))):", "if False:",
     LT, "PilotPost"),
    ("PP_FILES_EXACT", "launch/ptmc_pilot_post.py", "out = {\"files_exactly_the_pilot's\": have == want}",
     "out = {\"files_exactly_the_pilot's\": True}", LT, "PilotPost"),
    ("PP_PINS_RECEIPT", "launch/ptmc_pilot_post.py",
     'ok = ok and rec.get("pass") is True and rec.get("units") == [u] and rec.get("outputs") == {u: digests}',
     "ok = ok", LT, "PilotPost"),
    ("PP_SLURM_JOB", "launch/ptmc_pilot_post.py", '        ok = ok and str(meta.get("slurm_job")) == jobid\n', "",
     LT, "PilotPost"),
    ("PP_CNORM_HEX", "launch/ptmc_pilot_post.py", ' and isinstance(one, str) and bool(re.fullmatch(r"[0-9a-f]{64}", one))',
     " and isinstance(one, str)", LT, "PilotPost"),
    ("PP_SUPPORT_VALUES", "launch/ptmc_pilot_post.py",
     "if not all(isinstance(c, int) and not isinstance(c, bool) and 0 <= c < 224 for c in cells):", "if False:",
     LT, "PilotPost"),
    ("SC_MOVE_INJECTION", "ptmc_score.py",
     '\n                and np.array_equal(np.asarray(z["inj_entries"], np.int64), mref["want_inj"]))', ")",
     [LT, S], None),
    ("RUN_CLAIM", "ptmc_run.py",
     '    try:  # the unit\'s claim: its marker, created exclusively, says RUNNING until the verdict replaces it (B2)\n'
     '        with open(marker, "x") as fh:\n'
     '            fh.write(json.dumps({"unit": name, "verdict": "RUNNING"}) + "\\n")\n'
     '    except FileExistsError:\n'
     '        print(f"refusing: {name} is claimed by another run", file=sys.stderr)\n'
     '        return RC_CONTROL\n', "", T, "Runner"),
    ("RUN_REUSE_PINS", "ptmc_run.py", "                  and all(mk.get(k) == v for k, v in own.items())\n", "",
     T, "Runner"),
    ("RUN_MODULE_PIN_LIB", "ptmc_run.py", '    module_ok(tree, "2d-unfolding/oofvc/oofvc_lib.py")\n', "", T, "Runner"),
    ("RUN_MODULE_PIN_RUNNER", "ptmc_run.py", '    module_ok(tree, "2d-unfolding/ref_c2c1/ref_c2c1.py")\n', "",
     T, "Runner"),
    ("RUN_CANONICAL_NAME", "ptmc_run.py", 'if name != (f"p_{conv}_c" if b is None else f"p_{conv}_b{b}"):', "if False:",
     T, "Runner"),
    ("RUN_COUPLE_SUMS", "ptmc_run.py", '\n                                                and controls["C-COUPLE"]["sums"]["pass"])',
     ")", T, "Runner"),
    ("RUN_SUPPRESSED_REPLICA", "ptmc_run.py", "resampled truth weights; agy 8)\n    if conv == \"R\" and b is not None:",
     "resampled truth weights; agy 8)\n    if False:", T, "Runner"),
    ("LIB_CSTAR_DSTAR", "ptmc_lib.py", "d_ok = bool(np.all(np.isfinite(d_star)) and np.all(d_star > 0))", "d_ok = True",
     T, "Completeness"),
    ("LIB_ROO_RAN", "ptmc_lib.py", 'if ctl["C-ROO"].get("ran") is not True:', "if False:", LT, "PilotPost"),
    ("LIB_ROW3_NAMING", "ptmc_lib.py", '; {PROTO_B}, on the "', '; the matched baseline, on the "', T, "Readings"),
    ("SC_DEN", "ptmc_score.py", 'need(not bad, f"C-DEN:', 'need(True, f"C-DEN:', S, "denominator"),
    ("SC_FIX_CLASS", "ptmc_score.py", ' or o[1] != FIX_CLASS.get(nm, "TParameter<double>"):', ":", S, "fix_requires"),
    ("SC_FIX_AXES", "ptmc_score.py", " and fix_axes_ok(nm, o[2])", "", S, "fix_requires"),
    ("SC_SYMLINK", "ptmc_score.py", "need(stat.S_ISREG(os.lstat(p).st_mode), ", "need(True, ", S, "symlink"),
    ("SC_ABSENT_PATH", "ptmc_score.py", "need(not unknown and len(set(absent)) == len(absent), ", "need(True, ",
     S, "absence_record"),
    ("SC_REF_ROOT", "ptmc_score.py", 'need(m.get("ref_root") == REF_ROOT, ', "need(True, ", S, "another_root"),
    ("SC_CENTRAL_ANYWHERE", "ptmc_score.py", 'list(base.rglob("c2_central.done"))',
     'list((base / "units-centrals").glob("c2_central.done"))', S, "central_marker"),
    ("SC_ROWS_STAGED", "ptmc_score.py", 'str(Path(stage["root"]) / ROWS_STAGED)', 'str(Path(stage["root"]) / rows.name)',
     S, "renamed"),
    ("SC_GRID_META", "ptmc_score.py", 'need(m.get("grid") == {', 'need(True or m.get("grid") == {', S, "effective_grid"),
    ("SC_PUB_CLASS", "ptmc_score.py", 'need(bool(h) and h.ClassName() == "TH2D", ', "need(bool(h), ", S, "publication"),
    ("SC_SKIPPED", "ptmc_score.py", 'controls["C-D4"]["skipped"] = skipped', 'controls["C-D4"]["skipped"] = []',
     S, "absent_replica"),
    ("SC_RATIO", "ptmc_score.py", "    return q if math.isfinite(q) else None", "    return q", S, "finite_ratio"),
    ("SC_PINS_RECORD", "ptmc_score.py", '"d4_manifest_sha256": sha256(a.d4 / "manifest.json"),', "", S, "differ_with"),
    ("D4_UNITS_ABSENT", "launch/ptmc_stage_d4.py", 'if d != ref / "units":', "if True:", LT, "StageD4"),
    # code-confirm-2 (codex-school2): one mutant per new gate
    ("PP_ALLOC_ID", "launch/ptmc_pilot_post.py", "if not tail and jid != jobid:", "if False:", LT, "PilotPost"),
    ("PP_STEP_CANONICAL", "launch/ptmc_pilot_post.py", "tail.isdigit() and tail == str(int(tail))", "tail.isdigit()",
     LT, "PilotPost"),
    ("PP_SEED_KEY_CANONICAL", "launch/ptmc_pilot_post.py", "k.isdigit() and k == str(int(k)) and", "k.isdigit() and",
     LT, "PilotPost"),
    ("PP_PINS_BEFORE_AFTER", "launch/ptmc_pilot_post.py",
     'and rec.get("before") == rec.get("after") and all(', "and all(", LT, "PilotPost"),
    ("PP_CNORM_TYPE", "launch/ptmc_pilot_post.py", 'isinstance(one, str) and bool(re.fullmatch(r"[0-9a-f]{64}", one))',
     'bool(re.fullmatch(r"[0-9a-f]{64}", str(one)))', LT, "PilotPost"),
    ("PP_PRINT_FIRST", "launch/ptmc_pilot_post.py",
     '    try:  # the decision, the C-SUPPORT table with it, is printed before PROCEED exists (B12)\n'
     '        print(json.dumps({"decision": d}, indent=1, default=str), flush=True)\n'
     '    except (OSError, ValueError) as e:\n'
     '        sys.stderr.write(f"STOP: printing the decision failed: {e}\\n")\n'
     '        return 6\n', "", LT, "PilotPost"),
    ("SC_INJ_DTYPE", "ptmc_score.py",
     '\n                and np.asarray(z["inj_entries"]).dtype.kind in "iu"  # no float entries truncated (B3)', "",
     LT, "float_injection"),
    ("LIB_NUMPY_REFUSED", "ptmc_lib.py",
     '        if meta.get("unfolder") == "numpy unfolder":\n            return {"ok": False, "why": "the numpy unfolder (tests only)"}\n',
     "", LT, "PilotPost"),
    ("RUN_REUSE_UNFOLDER", "ptmc_run.py", '"inputs_sha256": inputs_verified, "unfolder": lib_label,',
     '"inputs_sha256": inputs_verified,', T, "Runner"),
    ("D4_MODULE_PIN", "launch/ptmc_stage_d4.py", "    if sha256(a.tree / rel) != MODULE_PINS[rel]:", "    if False:",
     LT, "StageD4"),
    ("SC_PINS_INPUTS", "ptmc_score.py", '"make_tree_sha256": pins["own"]["make_tree.sh"],', "", S, "differ_with"),
    ("SH_RECHECK_RECORD", "launch/ptmc_remote.sh",
     'printf \'%s\\n\' "$chk" > "$R/replicas-check/recheck.json" || stop "recording the recheck"', ":", HR, None),
    ("SB_RECHECK_RECORD", "launch/replicas.sbatch",
     '[ "$rk" = "{\\"recheck\\": \\"SAME\\", \\"time_limit_minutes\\": $L}" ] ||', "true ||", HS, None),
    ("SH_DISTINCT_IDS", "launch/ptmc_remote.sh", '[ "$jp" != "$jr" ] || stop', "true || stop", HR, None),
    ("SH_ALLOC_ROLE", "launch/ptmc_remote.sh",
     '|| stop "the $f job $j has no single allocation named $jn on $nn nodes"', "|| true", HR, None),
    ("SH_ALLOC_STRING", "launch/ptmc_remote.sh", '($1 "") == (j "") {c++;', "$1 == j {c++;", HR, None),
    ("SH_ROW_STRING", "launch/ptmc_remote.sh", '((a[1] "") != (j ""))', "(a[1] != j)", HR, None),
    # code-confirm-3 (codex-school2): one mutant per fix, both halves of B1
    ("SB_RECHECK_CLAIM", "launch/replicas.sbatch", '  [ "$held" = "${SLURM_JOB_ID:-}" ] || refuse',
     "  true || refuse", HS, None),
    ("SH_POST_CLAIM", "launch/ptmc_remote.sh", '[ "$cl" = "$jr" ] || stop', "true || stop", HR, None),
    ("SH_POST_REPS_COUNT", "launch/ptmc_remote.sh", '[ "$nr" = 1 ] && printf', '[ "$nr" -ge 1 ] && printf', HR, None),
    ("SH_LIB_SHA_ARG", "launch/ptmc_remote.sh",
     '--rows "$R/stage/oofvc_rows.npz" --lib-sha "$LIB_SHA" --out "$R/pilot-post"',
     '--rows "$R/stage/oofvc_rows.npz" --lib-sha 0 --out "$R/pilot-post"', HR, None),
    ("RUN_CONFIG_BYTES", "ptmc_run.py", '"config_sha256": cfg_sha}', '"config_sha256": sha256(C.CONFIG)}', T, "Runner"),
    ("PP_PIN_KEYS", "launch/ptmc_pilot_post.py", 'set(rec["before"]) == RUNNER_PIN_KEYS', 'bool(rec["before"])',
     LT, "PilotPost"),
    ("PP_PIN_VALUES", "launch/ptmc_pilot_post.py", ' and all(rec["before"][k] == v for k, v in own.items())', "",
     LT, "PilotPost"),
    ("PP_LIB_SHA", "launch/ptmc_pilot_post.py", 'ok = ok and meta.get("unfolder") == lib_sha', "ok = ok", LT, "PilotPost"),
    ("SC_OWN_MAKE_TREE", "ptmc_score.py", 'OWN_FILES = ("ptmc_lib.py", "ptmc_score.py", "ptmc_run.py", "make_tree.sh")',
     'OWN_FILES = ("ptmc_lib.py", "ptmc_score.py", "ptmc_run.py")', S, "make_tree_is"),
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
    if test.startswith("LOCAL:"):
        p = subprocess.run(["bash", str(work / "launch" / test.split(":", 1)[1])], capture_output=True, text=True)
    elif test.startswith("HARNESS:"):
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
    ctl = one("CONTROL", None, "", "", [T, S, LT, HR, HS, HL], None)
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
