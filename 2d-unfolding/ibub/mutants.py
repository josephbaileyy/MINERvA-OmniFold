#!/usr/bin/env python3
"""IBUB's hand mutants. Each one is a single-site change to ``ibub_unit.py`` or ``ibub_readout.py``, applied in place
and run against the tests that should kill it. The file is then restored and its sha256 re-checked; a restore that
does not reproduce the original bytes stops the run.

Before any mutant, every named test set must pass unmutated (the baseline), and every mutant's site must occur exactly
once. A mutant must still compile (``ast.parse`` for Python, ``bash -n`` for the job). It is KILLED only when a named
test fails or errors, and SURVIVES when they all pass. A suite that cannot load (an import failure, a missing test) is
a harness failure, which stops the run rather than counting as a kill. Every mutant must be killed.

    python -B mutants.py PYTHON [--only N]

PYTHON is an interpreter with PyROOT, numpy, scipy, LightGBM and scikit-learn. The results are printed as one TSV line
per mutant (index, verdict, file, tests, what it breaks), then a total line.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
U, R, L, O, J = "ibub_unit.py", "ibub_readout.py", "ibub_lanes.py", "ibub_overlap.py", "jobs/ibub_job.sbatch"
TU, TR, TJ, TO = "test_ibub_unit", "test_ibub_readout", "test_ibub_job", "test_ibub_overlap"
CT = "../../docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ibub/connect/ibub_run_connect.template.sh"

# (file, old, new, tests, what the mutant breaks)
MUTANTS = [
    (U, 'bad = sorted({a.split("=", 1)[0] for a in argv} & set(cfg["g2r_forbidden_options"]))', "bad = []",
     [f"{TU}.Pure", f"{TU}.Driver"], "C-G2R refuses nothing"),
    (U, '{a.split("=", 1)[0] for a in argv}', "set(argv)", [f"{TU}.Pure"], "C-G2R misses --miss-map=v"),
    (U, '        argv += ["--data-file", str(data_copy)]', "        pass", [f"{TU}.Driver"],
     "a data unit runs without its data file"),
    (U, "    if threads != cfg[\"e_r\"][\"thread_env\"]:", "    if False:", [f"{TU}.Driver"],
     "the thread gate is gone"),
    (U, "    if cpus != int(cfg[\"e_r\"][\"cpus\"]):", "    if False:", [f"{TU}.Driver"], "the CPU gate is gone"),
    (U, "    if got != want:\n        dest.unlink()\n        raise GateFailure(f\"C-DATA:",
     "    if False:\n        dest.unlink()\n        raise GateFailure(f\"C-DATA:", [f"{TU}.Driver"],
     "a data file off its pin is used"),
    (U, "        if data_copy is not None and Path(data_copy).exists():\n            Path(data_copy).unlink()",
     "        pass", [f"{TU}.Driver"], "the data copy is kept"),
    (U, 'data["pass"] = bool(data["argv_equal"] and prov.get("dataFileSha256") == data_sha)',
     'data["pass"] = bool(data["argv_equal"])', [f"{TU}.Driver"], "C-DATA ignores the recorded digest"),
    (U, 'xs = max([max_rel(np.asarray(a["xsec"])[i][rep], np.asarray(b["xsec"])[i][rep])',
     'xs = max([max_rel(np.asarray(a["xsec"])[i][~rep], np.asarray(b["xsec"])[i][~rep])', [f"{TU}.Pure"],
     "C-REP compares the unreported cells"),
    (U, 'out["pass"] = bool(max(out["xsec_max_rel"], out["T_max_rel"], out["y_max_rel"]) <= rtol)',
     'out["pass"] = bool(max(out["xsec_max_rel"], out["y_max_rel"]) <= rtol)', [f"{TU}.Pure"], "C-REP ignores T"),
    (U, "            os.chmod(dest, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)", "            pass", [f"{TU}.Pure"],
     "staged copies stay writable"),
    (U, "        ok = ok and not missing", "        pass", [f"{TU}.Pure"], "the preflight ignores a missing toy file"),
    (U, '    if hashlib.sha256(raw).hexdigest() != t["pseudo_b_sha256"]:', "    if False:", [f"{TU}.Pure"],
     "pseudo_b.json is read off its pin"),
    (R, "            cols.append(np.where(m, area, 0.0)[:, None])", "            cols.append(m.astype(float)[:, None])",
     [f"{TR}.Pure"], "bands are bare sums, not area-weighted"),
    (R, "    return NormalDist().inv_cdf(1 - alpha / 2 / tests)", "    return NormalDist().inv_cdf(1 - alpha / 2 / 205)",
     [f"{TR}.Pure"], "z* uses 205 tests, not the family"),
    (R, '    d = per_test(Y["IBU"] - Y["OF"], counts, zs, xt, sigma)',
     '    d = per_test(Y["IBU"] - Y["OF"][::-1], counts, zs, xt, sigma)', [f"{TR}.Pure"],
     "the difference is not paired toy by toy"),
    (R, '    flagged = [i for i in range(tests) if abs(d["z"][i]) > zs]',
     '    flagged = [i for i in range(tests) if abs(m["IBU"]["z"][i]) > zs]', [f"{TR}.Pure"],
     "the rule reads IBU's own bias, not the difference"),
    (R, '    for k in ("bias", "pull_mean", "pull_sd", "p_hat"):', '    for k in ("bias", "pull_mean"):', [f"{TR}.Pure"],
     "C-OF checks only the means (blind to a mispairing)"),
    (R, '        if prov.get("dataFileSha256") != shas[s]:', "        if False:", [f"{TR}.EndToEnd"],
     "the product's recorded data digest is not checked"),
    (R, "        k10.append(iu.max_rel(row10, h))", "        k10.append(0.0)", [f"{TR}.EndToEnd"], "C-K10 is gone"),
    (R, '                nonfinite["K5"] += int((~np.isfinite(row5)).sum())', "                pass", [f"{TR}.EndToEnd"],
     "C-CELLS skips K = 5"),
    (R, "            E_of = x_of - x_true", "            E_of = E_post", [f"{TR}.EndToEnd"],
     "OmniFold's errors are taken after the surrogates"),
    (R, '            if ibu["missing"]:                          # C-COMPLETE, per tune as declared; never the job\'s status\n                if not rec["controls_failed"]:',
     '            if False:\n                if not rec["controls_failed"]:', [f"{TR}.EndToEnd"],
     "a missing unit does not stop the reading"),
    (R, "            if nseeds != [n[\"seed\"] for n in natures]:", "            if False:", [f"{TR}.EndToEnd"],
     "the truth rows are not checked against the natures"),
    (R, "        guard_off_tree(path, what)\n        guard_in_root(path, root, what)", "        guard_in_root(path, root, what)",
     [f"{TR}.EndToEnd"], "--out under a guarded tree is allowed"),
    (R, '            if not rec["C-OF"]["pass"]:\n                rec["controls_failed"].append("C-OF")',
     '            if False:\n                rec["controls_failed"].append("C-OF")', [f"{TR}.EndToEnd"],
     "a failed C-OF does not invalidate the tune"),
    (U, "        if dest.exists():            # a partial or unverified copy never stays behind to block a rerun\n            dest.unlink()",
     "        if False:\n            dest.unlink()", [f"{TU}.Refusals"], "a partial data copy stays behind"),
    (U, '        if set(controls) != CONTROLS[unit["kind"]]:', "        if False:", [f"{TU}.Driver"],
     "a unit with an undeclared control set writes a marker"),
    (R, "            if str(meta.get(k)) != str(bound[k]):", "            if False:", [f"{TR}.EndToEnd"],
     "a unit from another job, runner or config is read"),
    (R, '        if set(ctl) != iu.CONTROLS["toy"]:', "        if False:", [f"{TR}.EndToEnd"],
     "a unit lacking a declared control is read"),
    (R, "                problems.append(f\"{name}: K scan {list(z['ks'])}\")", "                pass", [f"{TR}.EndToEnd"],
     "a unit of another K scan reads as only incomplete"),
    (R, '        if meta.get("data_sha256") != shas[s] or marker.get("data_sha256") != shas[s]:',
     '        if meta.get("data_sha256") != shas[s]:', [f"{TR}.EndToEnd"], "the marker's data digest is not checked"),
    (R, '        if (meta.get("kind"), meta.get("tune"), meta.get("seed")) != ("toy", truth, s):',
     '        if meta.get("seed") != s:', [f"{TR}.EndToEnd"], "a unit of another tune or kind is read"),
    (R, '        if not isinstance(marker, dict) or (marker.get("unit"), marker.get("seed")) != (name, s):',
     "        if not isinstance(marker, dict):", [f"{TR}.EndToEnd"], "a marker naming another unit is read"),
    (U, '        controls["C-ROO"] = {"max_rel": roo, "pass": bool(roo <= c2["c_roo_rtol"])}',
     '        controls["C-ROO"] = {"max_rel": roo, "pass": True}', [f"{TU}.Driver"], "C-ROO always passes"),
    (U, '        fast = isinstance(t["wall_s"], float) and t["wall_s"] <= limit and t["exit_status"] == 0',
     "        fast = True", [f"{TU}.Pure"], "the re-price trigger is gone"),
    (U, '        fast = isinstance(t["wall_s"], float) and t["wall_s"] <= limit and t["exit_status"] == 0',
     '        fast = isinstance(t["wall_s"], float) and t["wall_s"] <= limit', [f"{TU}.Pure"],
     "a failed reference step passes the barrier"),
    (U, '        ok = ok and rec["central_df_vs_central"]["pass"]', "        pass", [f"{TU}.Pure"],
     "the barrier ignores central_df against central"),
    (U, "    if (str(m.get(\"job\")), m.get(\"deploy_head\")) != (bound[\"job\"], bound[\"deploy_head\"]):\n        return False, f\"marker job/deploy",
     "    if False:\n        return False, f\"marker job/deploy", [f"{TU}.Refusals"], "a marker from another job is accepted"),
    (U, '    if p != n and not p.startswith(n + os.sep):', "    if False:", [f"{TU}.Hardening"],
     "a destination outside the namespace is accepted"),
    (U, "    if os.path.realpath(n) != os.path.abspath(n):", "    if False:", [f"{TU}.Hardening"],
     "a symlinked namespace is accepted"),
    (U, "    if r.returncode != 0 or head != want:", "    if r.returncode != 0:", [f"{TU}.Hardening"],
     "a unit runs at another deploy"),
    (U, "    rec[\"verdict\"] = \"PASS\" if (passed == len(expected) and not extra and barrier) else \"FAIL\"",
     "    rec[\"verdict\"] = \"PASS\" if (passed == len(expected) and barrier) else \"FAIL\"", [f"{TU}.Hardening"],
     "the completion check ignores undeclared markers"),
    (U, "    rec[\"verdict\"] = \"PASS\" if (passed == len(expected) and not extra and barrier) else \"FAIL\"",
     "    rec[\"verdict\"] = \"PASS\" if (passed == len(expected) and not extra) else \"FAIL\"", [f"{TU}.Hardening"],
     "the completion check ignores the barrier receipt"),
    (U, "    if a.shape != b.shape or not (np.all(np.isfinite(a)) and np.all(np.isfinite(b))):\n        return float(\"inf\")\n    nz",
     "    if a.shape != b.shape:\n        return float(\"inf\")\n    nz", [f"{TU}.Hardening"], "a NaN can pass max_rel"),
    (U, "        for u in units:                              # C-G2R, before the driver is imported (section 5)\n            resolve_argv(",
     "        for u in []:                              # C-G2R, before the driver is imported (section 5)\n            resolve_argv(",
     [f"{TU}.Refusals"], "C-G2R runs only after the driver import"),
    (R, '            if not rec["C-JOB"]["pass"]:', "            if False:", [f"{TR}.JobWide"],
     "a failing job-wide prerequisite is not recorded (the tune is graded)"),
    (R, '    problems += [f"{name}: a marker for an undeclared unit" for name in sorted(present - known)]',
     "    pass", [f"{TR}.EndToEnd"], "an undeclared marker is not noticed"),
    (R, '        for k in ("slurm_job", "runner_sha256", "config_sha256", "deploy_head"):',
     '        for k in ("slurm_job", "runner_sha256", "config_sha256"):', [f"{TR}.EndToEnd"],
     "a meta from another deploy is read"),
    (R, "        if final[\"verdict\"] == \"PASS\":", "        if True:", [f"{TR}.EndToEnd"],
     "a STOP record still carries the readings"),
    (R, "                run.watch(tpath)                                  # the truth file joins the atime ledger",
     "                pass", [f"{TR}.EndToEnd"], "the truth file is not in the atime ledger"),
    (L, "    rows += [(\"toys\", k % LANES, u) for k, u in enumerate(toys)]",
     "    rows += [(\"toys\", k % 3, u) for k, u in enumerate(toys)]", [f"{TJ}.Lanes"], "the toys are dealt to 3 lanes"),
    (L, "        if n != len(want) // LANES:", "        if False:", [f"{TJ}.Job"], "verify ignores the lane counts"),
    (O, '               or (o[0] == "read (cov2d-acked)" and t[0].startswith("cov2d"))]',
     '               or (o[0] == "read (cov2d-acked)")]', [f"{TO}"], "an acked read on another lane's path is allowed"),
    (O, "    out += IBUCHI + LR_P0", "    out += IBUCHI", [f"{TO}"], "LR's P0 paths are not protected"),
    (O, "    out += IBUCHI + LR_P0", "    out += LR_P0", [f"{TO}"], "the ibuchi root is not protected"),
    (J, 'if [ "$brc" -ne 0 ] || ! all_zero "$r0" "$r1"; then', "if false; then", [f"{TJ}.Job"],
     "the toys start without the barrier"),
    (J, 'case "$(key QOS)" in regular|regular_1) ;;', 'case "$(key QOS)" in *) ;;', [f"{TJ}.Job"],
     "another QOS is accepted"),
    (J, '[ "$(key NumNodes)" = 1 ] || refuse', '[ -n "$(key NumNodes)" ] || refuse', [f"{TJ}.Job"],
     "another node count is accepted"),
    (J, '[ "$(key OverSubscribe)" = NO ] || refuse', 'true || refuse', [f"{TJ}.Job"], "a shared node is accepted"),
    (J, '[ "$(key TimeLimit)" = "$LIMIT" ] || refuse', 'true || refuse', [f"{TJ}.Job"], "another time limit is accepted"),
    (J, '[ -z "$entries" ] || refuse', 'true || refuse', [f"{TJ}.Job"], "a used units directory is accepted"),
    (J, 'r=$(realpath "$d") && under "$r" "$RN" && [ ! -L "$d" ] || refuse', 'true || refuse', [f"{TJ}.Job"],
     "a symlinked logs directory is accepted"),
    (J, '[ "$crc" -eq 0 ] || ok=0', 'true || ok=0', [f"{TJ}.Job"], "a failed completion check ends PASS"),
    (J, 'info=$("$SCONTROL" show job "$SLURM_JOB_ID") || refuse', 'info=$("$SCONTROL" show job "$SLURM_JOB_ID") || true',
     [f"{TJ}.Job"], "a failed scontrol query is not refused"),
    (U, "    flags = os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | (os.O_EXCL if exclusive else os.O_TRUNC)",
     "    flags = os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_TRUNC", [f"{TU}.Refusals"],
     "a contained write replaces an existing file"),
    (U, "    path = Path(path)\n    inside(cfg, path.parent)", "    path = Path(path)", [f"{TU}.Refusals"],
     "a contained write may land outside the namespace"),
    (U, "    inside(cfg, dest.parent)                      # a symlinked stage/data", "    pass  # a symlinked stage/data",
     [f"{TU}.Refusals"], "a symlinked data directory takes the copy out of $N"),
    (U, "    if (meta.get(\"unit\"), str(meta.get(\"slurm_job\")), meta.get(\"deploy_head\")) != (name, bound[\"job\"], bound[\"deploy_head\"]):",
     "    if False:", [f"{TU}.Refusals"], "a skip ignores the npz's embedded provenance"),
    (U, "    if rc.sha256(npz) != m.get(\"sha256\") or rc.sha256(root) != m.get(\"root_sha256\"):\n        return False, \"a product is not at its marker's digest\"",
     "    if False:\n        return False, \"a product is not at its marker's digest\"", [f"{TU}.Refusals"],
     "a skip ignores the products' digests"),
    (U, "        ok, why = marker_ok(out, name, bound, unit[\"kind\"])", "        ok, why = True, \"ok\"", [f"{TU}.Driver"],
     "a present unit is skipped without its provenance"),
    (U, "        unit_ok = bool(good and fast and srun_rc == 0)", "        unit_ok = bool(good and fast)", [f"{TU}.Pure"],
     "the barrier ignores a failed srun step"),
    (U, "                and (r.get(\"npz_sha256\"), r.get(\"root_sha256\")) == (m.get(\"sha256\"), m.get(\"root_sha256\"))):\n            return False, f\"refcheck.json's",
     "                and True):\n            return False, f\"refcheck.json's", [f"{TU}.Hardening"],
     "the completion check ignores the barrier's reference digests"),
    (U, "        if not np.all(np.isfinite(x[covered])):\n            return False\n    return True",
     "        pass\n    return True", [f"{TU}.Driver"], "C-SIM's IBUB finite check passes a NaN"),
    (R, '    for path, what in ((out, "--out"), (tmp_root, "the temporary root")):\n        guard_off_tree(path, what)\n        guard_in_root(path, root, what)',
     '    for path, what in ((out, "--out"), (tmp_root, "the temporary root")):\n        guard_off_tree(path, what)',
     [f"{TR}.EndToEnd"], "the readout writes outside its declared root"),
    (R, '        if isinstance(comp, dict) and comp.get("barrier_sha256") not in (None, bsha):', "        if False:",
     [f"{TR}.JobWide"], "the readout does not bind a published IBUB-DONE to refcheck.json"),
    (R, '        if not isinstance(d, dict) or (str(d.get("job")), d.get("M"), d.get("stage")) != (job, bound["deploy_head"], "toys"):',
     "        if not isinstance(d, dict):", [f"{TR}.JobWide"],
     "a published IBUB-DONE naming another job, M or stage is accepted"),
    (R, '            missing.append(s)               # absent from the reading; INCOMPLETE unless something else fails',
     '            missing.append(s); problems.append(f"{name}: FAIL")', [f"{TR}.EndToEnd"],
     "a FAIL marker makes the tune INVALID"),
    (R, '            nonfinite["K10"] += int((~np.isfinite(h)).sum())', "            pass", [f"{TR}.EndToEnd"],
     "C-CELLS does not count a ROOT row on its own"),
    (R, '            except (OSError, ValueError, KeyError) as e:   # an input absent or unreadable: recorded, with its name\n                rec["refused"] = f"{type(e).__name__}: {e}"\n                return invalid(f"an input is absent or unreadable: {e}")',
     '            except ZeroDivisionError as e:\n                raise', [f"{TR}.EndToEnd"], "a missing input leaves no tune record"),
    (R, "        final = run.finish(stage, name)            # the atime, open-audit and module checks; STOP outranks a reading",
     "        final = run.finish(stage, name); publish_stage(); stage = out", [f"{TR}.EndToEnd"],
     "the result is published before its npz is written"),
    (J, '  publish_done toys 0 "$comp" || { say "end: IBUB-DONE was not published"; exit 1; }',
     '  publish_done toys 0 "$comp" || true', [f"{TJ}.Job"], "a failed IBUB-DONE publication ends PASS"),
    (J, 'gs=$(git -C "$C" status --porcelain --ignored) || refuse "git status failed (before)"',
     'gs=$(git -C "$C" status --porcelain --ignored) || true', [f"{TJ}.Job"], "a failed git status reads as clean"),
    (J, '  "$PY" -B 2d-unfolding/ibub/ibub_lanes.py "$1" "$2" > "$f" || return 1',
     '  "$PY" -B 2d-unfolding/ibub/ibub_lanes.py "$1" "$2" > "$f" || true', [f"{TJ}.Job"],
     "a failed lane producer's partial list runs"),
    (J, '[ -n "$f" ] && [ -f "$f" ] && [ ! -L "$f" ] && [ -O "$f" ] && r=$(realpath "$f") || r=""',
     '[ -n "$f" ] && [ -f "$f" ] && [ -O "$f" ] && r=$(realpath "$f") || r=""', [f"{TJ}.Job"],
     "a symlinked StdOut or StdErr is accepted"),
    (J, '  [ ! -e "$L/$tag.time" ] && [ ! -L "$L/$tag.time" ] || { say "refusing step $tag: $L/$tag.time exists"; return 2; }',
     "  true", [f"{TJ}.Job"], "a step writes over an existing time file"),
    (J, 'all_zero "${lrcs[@]}" || ok=0', 'true || ok=0', [f"{TJ}.Job"], "a failed toy lane ends PASS"),
    (J, '--step-rc "central=$r0" --step-rc "central_df=$r1"', '--step-rc "central=$r0" --step-rc "central_df=0"',
     [f"{TJ}.ReceiptChain"], "the barrier is not told a reference srun failed"),
    (U, "            done += n", "            done += len(view)", [f"{TU}.Refusals"], "a short write is taken as complete"),
    (R, '        if not isinstance(m, dict) or (m.get("unit"), m.get("verdict")) != (u, "PASS") \\\n                or (str(m.get("job")), m.get("deploy_head")) != (str(bound["slurm_job"]), bound["deploy_head"]):',
     '        if not isinstance(m, dict) or (m.get("unit"), m.get("verdict")) != (u, "PASS"):', [f"{TR}.JobWide"],
     "the readout accepts a reference marker from another job"),
    (J, "set -o noclobber   # from the first line", "true   # from the first line", [f"{TJ}.Job"],
     "a redirect follows a planted symlink (no noclobber)"),
    (J, 'fresh "$SREC" || refuse', 'true || refuse', [f"{TJ}.Job"],
     "a stale scontrol record is not refused before the query"),
    (J, '[ -d "$SD" ] && [ ! -L "$SD" ] || refuse', '[ -d "$SD" ] || refuse', [f"{TJ}.Job"],
     "a symlinked stdout directory is accepted"),
    (J, '[ -O "$SD" ] && [ -n "$(find "$SD" -maxdepth 0 -perm 700)" ] || refuse', '[ -O "$SD" ] || refuse',
     [f"{TJ}.Job"], "a non-private stdout directory is accepted"),
    (J, '[ -n "$r" ] && [ "$(dirname "$r")" = "$(realpath "$SD")" ] || refuse', '[ -n "$r" ] || refuse',
     [f"{TJ}.Job"], "stdout or stderr outside the private directory is accepted"),
    (J, 'SREC="$L/scontrol-batch-$SLURM_JOB_ID.txt"', 'SREC="$L/scontrol-connect-$SLURM_JOB_ID.txt"', [f"{TJ}.Job"],
     "the batch's scontrol record takes the connect's name (the shared name restored)"),
    (J, 'in_sd StdErr      #', 'true StdErr      #', [f"{TJ}.Job"], "StdErr is not checked"),
    (CT, 'SREC="$N/logs/scontrol-connect-$jid.txt"', 'SREC="$N/logs/scontrol-batch-$jid.txt"', [f"{TJ}.Job"],
     "the connect's scontrol record takes the batch's name (the shared name restored)"),
    (CT, '[ ! -e "$SREC" ] && [ ! -L "$SREC" ] || { echo "STOP: $SREC exists', 'true || { echo "STOP: $SREC exists',
     [f"{TJ}.Job"], "the connect writes its scontrol record without the fresh check"),
    (J, 'case "$(key QOS)" in regular|regular_1) ;;', 'case "$(key QOS)" in regular) ;;', [f"{TJ}.Job"],
     "the job's exact QOS=regular match is restored (Perlmutter's regular_1 refuses)"),
    (J, 'case "$(key QOS)" in regular|regular_1) ;;', 'case "$(key QOS)" in regular*) ;;', [f"{TJ}.Job"],
     "the job accepts any regular* QOS (regular_2)"),
    (CT, 'case "$qos" in regular|regular_1) ;;', 'case "$qos" in regular) ;;', [f"{TJ}.Job"],
     "the connect's exact QOS=regular match is restored (Perlmutter's regular_1 STOPs)"),
    (CT, 'case "$qos" in regular|regular_1) ;;', 'case "$qos" in regular*) ;;', [f"{TJ}.Job"],
     "the connect accepts any regular* QOS (regular_2)"),
    (R, '            if ibu["missing"]:                          # C-COMPLETE, per tune as declared; never the job\'s status',
     '            if ibu["missing"] or ((rec["job_terminal"] or {}).get("ibub_done") or {}).get("completion") != "PASS":', [f"{TR}.JobWide"],
     'the job-PASS gate is restored (a complete tune of a job not PASS is not graded)'),
    (R, '    if name != "ibub_run" or word not in TERMINAL:',
     '    if name != "ibub_run":', [f"{TR}.JobWide"],
     'the terminal-state check is dropped (a running job is read)'),
    (R, '    why = allocation_ok(scon)',
     '    why = None', [f"{TR}.JobWide"],
     'the allocation is taken from the stdout line alone'),
    (R, '            root = copy_inv(inv, run, units / f"{name}.root", marker["root_sha256"], f"{name}.root")',
     '            root = run.copy(units / f"{name}.root", marker["root_sha256"], f"{name}.root")', [f"{TR}.JobWide"],
     "a toy product's digest is left out of the inventory"),
    (R, '    if len(mine) != 1 or len(mine[0]) < 4:',
     '    if not mine or len(mine[0]) < 4:', [f"{TR}.JobWide"],
     'two sacct rows for the job are read as one'),
    (R, '        if got != want:\n            raise c.Refusal(f"the fetched record {rel}',
     '        if False:\n            raise c.Refusal(f"the fetched record {rel}', [f"{TR}.JobWide"],
     'a fetched record off its sum is read'),
    (R, '    if need - set(out):',
     '    if False:', [f"{TR}.JobWide"],
     'a fetch lacking a needed record is read'),
    (R, '    if not (isinstance(st, dict) and st.get("verdict") == "PASS"):',
     '    if False:', [f"{TR}.JobWide"],
     'stage.json is not checked'),
    (R, '    if sum(ln.startswith(ALLOCATION_LINE) for ln in lines) != 1:',
     '    if sum(ln.startswith(ALLOCATION_LINE) for ln in lines) < 1:', [f"{TR}.JobWide"],
     'a repeated allocation line is accepted'),
    (R, '    if braw != recs["units/refcheck.json"]:',
     '    if False:', [f"{TR}.JobWide"],
     "the fetched refcheck.json is not compared with the job's"),
    (R, '    if not (isinstance(cdc, dict) and cdc.get("pass") is True):',
     '    if False:', [f"{TR}.JobWide"],
     'C-REP across the two references is not checked'),
    (R, '                if src.is_symlink():\n                    raise c.Refusal(f"{src} is a symlink")',
     '                if False:\n                    raise c.Refusal(f"{src} is a symlink")', [f"{TR}.JobWide"],
     'a symlinked reference product is read'),
    (R, '            for ext, key in (("npz", "sha256"), ("root", "root_sha256")):\n                src = units / f"{u}.{ext}"',
     '            for ext, key in (("npz", "sha256"),):\n                src = units / f"{u}.{ext}"', [f"{TR}.JobWide"],
     "a reference's ROOT product is not hashed"),
    (R, '        if set(ctl) != iu.CONTROLS[u] or not all(isinstance(v, dict) and v.get("pass") is True for v in ctl.values()):',
     '        if False:', [f"{TR}.JobWide"],
     "a reference's C-REP / C-REP-D / C-SIM are not checked"),
    (R, '    if os.path.realpath(root) != os.path.normpath(root):',
     '    if False:', [f"{TR}.ReadoutInputs"],
     'a root under a symlinked ancestor is accepted'),
    (R, '    if st.st_uid != os.getuid() or st.st_mode & 0o022:',
     '    if st.st_uid != os.getuid():', [f"{TR}.ReadoutInputs"],
     'a group- or world-writable root is accepted'),
    (R, '    root = check_write_root(rcfg["write_root"])',
     '    root = rcfg["write_root"]', [f"{TR}.ReadoutInputs"],
     'the root is not checked before staging'),
    (R, '    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode) or os.path.realpath(parent) != os.path.normpath(parent):',
     '    if False:', [f"{TR}.ReadoutInputs"],
     "--out's parent may be a symlink"),
    (R, '    tmp_root = os.environ.get("TMPDIR") or root',
     '    tmp_root = os.environ.get("TMPDIR") or tempfile.gettempdir()', [f"{TR}.ReadoutInputs"],
     "temporary files default to the system's directory, not the root"),
    (R, '    saved, tempfile.tempdir = tempfile.tempdir, tmp_root',
     '    saved = tempfile.tempdir', [f"{TR}.ReadoutInputs"],
     "tempfile's default is left outside the root"),
    (R, '                if pre is not None:\n                    raise c.Refusal(f"a pinned input: {pre}")',
     '                if False:\n                    raise c.Refusal(f"a pinned input: {pre}")', [f"{TR}.ReadoutInputs"],
     'a pinned input that failed before the audit is not recorded'),
    (R, '    if anc.returncode != 0:',
     '    if False:', [f"{TR}.JobCode"],
     "--job-m need not be an ancestor of the readout's HEAD"),
    (R, '    if scontrol_key(text, "QOS") not in QOS:', '    if scontrol_key(text, "QOS") != "regular":',
     [f"{TR}.JobWide"], "the readout's exact QOS=regular match is restored (Perlmutter's regular_1 fails)"),
    (R, '    if scontrol_key(text, "QOS") not in QOS:', '    if not scontrol_key(text, "QOS").startswith("regular"):',
     [f"{TR}.JobWide"], "the readout accepts any regular* QOS (regular_2)"),
    # agy readout read 1 (gemini-4-hydrogen-xhigh), items 3-5: each fix, undone
    (R, '    present = {f[:-len(".done")] for f in os.listdir(units) if f.endswith(".done")}',
     '    present = {f[:-len(".done")] for f in os.listdir(units) if f.startswith(f"toy_{truth}_") and f.endswith(".done")}',
     [f"{TR}.EndToEnd"], "an undeclared marker outside the tune's prefix is not noticed"),
    (R, '        if any((units / f"{name}.{ext}").is_symlink() for ext in ("done", "root", "npz")):',
     '        if False:', [f"{TR}.EndToEnd"], "a symlinked toy marker or product is read"),
    (R, '        if (str(marker.get("job")), marker.get("deploy_head")) != (str(bound["slurm_job"]), bound["deploy_head"]):\n            missing.append(s)',
     '        if False:\n            missing.append(s)', [f"{TR}.EndToEnd"],
     "a marker from another job or deploy is checked only when it reads PASS"),
    (R, '        if not all(isinstance(v, dict) and v.get("pass") is True for v in ctl.values()):',
     '        if not all(v.get("pass") for v in ctl.values()):', [f"{TR}.EndToEnd"],
     "a toy control passing as a truthy non-True value is accepted"),
    (R, '        for k in ("runner_sha256", "config_sha256"):\n            if meta.get(k) != bound[k]:',
     '        for k in ():\n            if meta.get(k) != bound[k]:', [f"{TR}.JobWide"],
     "a reference's meta from another runner or config is accepted"),
    (R, '        inv[str(records / rel)] = hashlib.sha256(data).hexdigest()',
     '        pass', [f"{TR}.JobWide"], "the fetched records are not inventoried"),
    (R, '        if pre is None:     # read before the audit by toy_shas and reported_cells, each equal to its pin or refused',
     '        if False:', [f"{TR}.JobWide"], "pseudo_b.json and the cells' blocks record are not inventoried"),
    (R, '                inv[str(rd.COMPLETENESS[0])] = rd.COMPLETENESS[1]',
     '                pass', [f"{TR}.JobWide"], "the completeness table is not inventoried"),
    (R, '    bu = barrier.get("units") if isinstance(barrier.get("units"), dict) else {}',
     '    bu = barrier.get("units") or {}', [f"{TR}.JobWide"], "a barrier whose units is not an object crashes the readout"),
]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# Run in a fresh interpreter: rc 0 when every test passed, 1 when a named test failed or errored, 2 when the suite
# itself could not load (an import or syntax failure, or a named test that does not exist), ran no test, or failed in
# a class or module setup. That is a harness failure, which stops the run (the codex read, round 2, NB4).
RUNNER = """
import sys, unittest
sys.argv = sys.argv[:1]
loader = unittest.TestLoader()
suite = loader.loadTestsFromNames(NAMES)
def walk(t):
    if isinstance(t, unittest.TestSuite):
        for x in t:
            yield from walk(x)
    else:
        yield t
tests = list(walk(suite))
if loader.errors or not tests or any(type(t).__name__ == "_FailedTest" for t in tests):
    sys.exit(2)
r = unittest.TextTestRunner(verbosity=0).run(suite)
# a class or module setup error (an _ErrorHolder), or no test executed, is a harness failure, never a kill
if r.testsRun == 0 or any(type(t).__name__ == "_ErrorHolder" for t, _ in r.errors + r.failures):
    sys.exit(2)
sys.exit(0 if r.wasSuccessful() else 1)
"""


def run_tests(py: str, tests: list) -> int:
    code = RUNNER.replace("NAMES", repr(list(tests)))
    r = subprocess.run([py, "-B", "-c", code], cwd=HERE, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="2"))
    return r.returncode


def compiles(py: str, path: Path) -> bool:
    if path.suffix == ".py":
        return subprocess.run([py, "-B", "-c", f"import ast; ast.parse(open({str(path)!r}).read())"],
                              capture_output=True).returncode == 0
    return subprocess.run(["bash", "-n", str(path)], capture_output=True).returncode == 0


def main(argv: list) -> int:
    py = argv[0]
    only = int(argv[argv.index("--only") + 1]) if "--only" in argv else None
    chosen = [(i, m) for i, m in enumerate(MUTANTS, 1) if only is None or i == only]
    for i, (f, old, new, tests, what) in chosen:     # every site exists exactly once before anything runs
        n = (HERE / f).read_text().count(old)
        if n != 1:
            print(f"{i}\tNOT-APPLIED\t{f}\t{what} (the site occurs {n} times)")
            return 2
    sets = sorted({tuple(m[3]) for _, m in chosen})
    for t in sets:                                   # the baseline: unmutated, every named test set must pass
        b = run_tests(py, list(t))
        print(f"BASELINE\t{'PASS' if b == 0 else 'FAIL rc ' + str(b)}\t{','.join(t)}", flush=True)
        if b != 0:
            return 2
    killed = total = 0
    for i, (f, old, new, tests, what) in chosen:
        path = HERE / f
        orig = path.read_bytes()
        try:
            path.write_text(orig.decode().replace(old, new))
            if not compiles(py, path):
                print(f"{i}\tHARNESS\t{f}\t{','.join(tests)}\t{what} (the mutant does not compile)")
                return 2
            rc = run_tests(py, tests)
        finally:
            path.write_bytes(orig)
        if sha(path.read_bytes()) != sha(orig):
            print(f"{i}\tRESTORE-FAILED\t{f}")
            return 3
        if rc == 2:
            print(f"{i}\tHARNESS\t{f}\t{','.join(tests)}\t{what} (the suite did not load)")
            return 2
        total += 1
        verdict = "KILLED" if rc == 1 else "SURVIVED"
        killed += verdict == "KILLED"
        print(f"{i}\t{verdict}\t{f}\t{','.join(tests)}\t{what}", flush=True)
    print(f"TOTAL\t{killed}/{total} killed")
    return 0 if killed == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
