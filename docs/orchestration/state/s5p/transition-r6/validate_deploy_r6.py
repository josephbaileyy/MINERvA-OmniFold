#!/usr/bin/env python3
"""s5p transition r6: validate a candidate deploy against ``transition-r6/plan.json`` (read-only).

Exit 0 only if every assertion holds:
- HEAD is exactly --expect-sha, and the tracked tree is clean;
- ``nd-unfolding/`` differs from 55a41765 only by non-production report-step files, plus (by path, printed) the
  separate ``gbdt_model_dependence/`` analysis subdirectory and top-level ``*.md`` logs that no other nd-unfolding file
  references; the frozen modules are byte-identical to 4f5a613f;
- ``budget.json`` is byte-identical to the ledger-bound revision 7, so no rebind is needed;
- for each planned lane, the target and the rollback queue each hold a header, then the wait line of the planned
  label, then the source queue's lines from that wait line, identical except for the ``--throttle`` value. Every
  throttle must equal the planned value (target) or the rollback value.

MEASURES: the deploy's fitness as a runner source. CANNOT AUTHORIZE: starting a runner.
"""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path
ALLOWED_ND = {"nd-unfolding/s5p_robust_labels.py", "nd-unfolding/tests/test_s5p_robust_labels.py",
              "nd-unfolding/s5p_missing_sensitivity.py", "nd-unfolding/tests/test_s5p_missing_sensitivity.py"}
FROZEN = ["nd-unfolding/s5p_joint.py", "nd-unfolding/s5p_inference.py", "nd-unfolding/s5p_seqstop.py"]
Q = "docs/orchestration/state/s5p/prod"
EXEMPT_DIR = "nd-unfolding/gbdt_model_dependence/"
THR = re.compile(r"--throttle \d+ ")
def git(d, *a):
    p = subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True); return p.returncode, p.stdout
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--deploy", type=Path, required=True); ap.add_argument("--expect-sha", required=True)
    a = ap.parse_args(); d, bad = a.deploy, []
    def check(ok, what):
        print(("PASS " if ok else "FAIL ") + what)
        if not ok: bad.append(what)
    plan_p = d / "docs/orchestration/state/s5p/transition-r6/plan.json"
    if not plan_p.exists():
        print("FAIL no transition-r6/plan.json in this deploy"); print("INVALID (1 failed)"); return 1
    plan = json.loads(plan_p.read_text())
    rc, head = git(d, "rev-parse", "HEAD"); check(rc == 0 and head.strip() == a.expect_sha, f"HEAD {head.strip()[:12]} == {a.expect_sha[:12]}")
    rc, st = git(d, "status", "--porcelain", "--untracked-files=no"); check(rc == 0 and st.strip() == "", "tracked tree clean")
    rc, nd = git(d, "diff", "--name-only", "55a41765", "HEAD", "--", "nd-unfolding")
    # Not production inputs (added by PR #9, 2026-10-04): the separate GBDT-analysis subdirectory and top-level .md logs.
    # Exempted by path, printed, and guarded by a no-reference check so a production module cannot reach them.
    exempt = {f for f in nd.split() if f.startswith(EXEMPT_DIR) or (f.count("/") == 1 and f.endswith(".md"))}
    extra = set(nd.split()) - ALLOWED_ND - exempt
    print(f"     exempted (non-production, by path): {len(exempt)} files under {EXEMPT_DIR} or top-level nd-unfolding/*.md")
    check(rc == 0 and not extra, f"nd-unfolding vs 55a41765 only report-step files plus the exemption (extra: {sorted(extra)})")
    rc, refs = git(d, "grep", "-l", "gbdt_model_dependence", "HEAD", "--", "nd-unfolding/*.py", "nd-unfolding/*.sh",
               f":(exclude){EXEMPT_DIR}")
    check(refs.strip() == "", f"no nd-unfolding .py/.sh outside {EXEMPT_DIR} references it ({refs.split()})")
    rc, _ = git(d, "diff", "--quiet", "4f5a613f", "HEAD", "--", *FROZEN); check(rc == 0, "frozen modules byte-identical to 4f5a613f")
    bsha = hashlib.sha256((d / "docs/orchestration/state/s5p/budget.json").read_bytes()).hexdigest()
    check(bsha == plan["budget_sha256_expected"], f"budget.json byte-identical to the ledger-bound revision 7 ({bsha[:12]})")
    for name, lane in plan["lanes"].items():
        src = (d / Q / plan["source_dir"] / name).read_text().splitlines()
        lab = lane["label"]
        w = [i for i, ln in enumerate(src) if ln.startswith("until out=$(squeue") and f"-n s5p-{lab} " in ln]
        for kind, sub, thr in (("target", plan["target_dir"], lane["throttle"]), ("rollback", plan["rollback_dir"], lane["rollback_throttle"])):
            p = d / Q / sub / name
            if not p.exists(): check(False, f"{kind} {sub}/{name} exists"); continue
            new = p.read_text().splitlines()
            ok_head = len(new) > 1 and new[0].startswith("# ") and new[1].startswith(f"until out=$(squeue -h --me -n s5p-{lab} ")
            norm = lambda ls: [THR.sub("--throttle X ", x) for x in ls]
            ok_body = len(w) == 1 and norm(new[1:]) == norm(src[w[0]:])
            vals = {int(x) for x in re.findall(r"--throttle (\d+) ", "\n".join(new))}
            check(ok_head and ok_body and vals == {thr}, f"{kind} {sub}/{name}: wait line {lab}, body identical except throttle, throttle {sorted(vals)} == [{thr}]")
    print("VALID" if not bad else f"INVALID ({len(bad)} failed)"); return 0 if not bad else 1
if __name__ == "__main__": sys.exit(main())
