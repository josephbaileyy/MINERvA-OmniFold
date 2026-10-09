#!/usr/bin/env python3
"""N2 harness: plan, split checks, admission, one guarded member at a time, and aggregation.

    harness.py plan        --out PLAN
    harness.py check-split --folds DIR --manifest SPLIT
    harness.py admit       --admission ADM
    harness.py run-member  --admission ADM --plan PLAN --member ID
    harness.py aggregate   --admission ADM --plan PLAN --out RESULT

It submits nothing and starts no event loop. ``run-member`` runs exactly one member's producer,
through ``nd-unfolding/mnv_guarded_run.py`` on the admitted checkout with
``--require-provenance``, and records a failure rather than retrying. Every command that runs or
summarizes members needs an admission record:

    {"design": "N2", "design_sha256": ..., "synthetic": false,
     "authorization": {"path": <repo-relative record>, "sha256": ...},
     "plan_sha256": ..., "producer": <repo-relative path>,
     "code": {"commit": ..., "modules": {<relpath>: <sha256>}},
     "inputs": {"split_manifest": {"path", "sha256"}, "fold_tables": {"path"},
                "rebuilt_omnifile": {"path", "sha256"}},
     "outroot": <absolute directory>}

A synthetic admission (``"synthetic": true``) may run only ``n2/synthetic_producer.py`` and needs no
authorization or rebuilt file; a real one may not run the synthetic producer. No real admission
exists: N2 is not admitted (``design.py``).
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE.parent))

from n2 import design, execution as gx, identity, members as mb  # noqa: E402

SYNTHETIC_PRODUCER = "2d-unfolding/uq/coverage_fixed_truth/n2/synthetic_producer.py"
GUARD = "nd-unfolding/mnv_guarded_run.py"


class AdmissionError(RuntimeError):
    """The admission record is missing, incomplete or does not match this checkout."""


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_fold_tables(directory):
    out = {}
    for fold in identity.FOLDS:
        out[fold] = {}
        for tree in identity.TREES:
            path = Path(directory) / fold / f"{tree}.npz"
            if not path.exists():
                raise identity.IdentityError(f"no {path}")
            with np.load(path, allow_pickle=False) as z:
                out[fold][tree] = {k: z[k] for k in z.files}
    return out


def check_admission(path, root=REPO):
    if path is None or not Path(path).is_file():
        raise AdmissionError(f"no admission record at {path}; N2 is not admitted")
    adm = json.loads(Path(path).read_text())
    need = ["design", "design_sha256", "synthetic", "plan_sha256", "producer", "code", "inputs",
            "outroot"]
    if adm.get("synthetic") is False:
        need.append("authorization")
    missing = [k for k in need if k not in adm]
    if missing:
        raise AdmissionError(f"admission record lacks {missing}")
    if adm["design"] != design.DESIGN or adm["design_sha256"] != design.design_digest():
        raise AdmissionError("the admitted design is not this design.py")
    if not isinstance(adm["synthetic"], bool):
        raise AdmissionError("'synthetic' must be true or false")
    if adm["synthetic"] != (adm["producer"] == SYNTHETIC_PRODUCER):
        raise AdmissionError("the synthetic producer runs only under a synthetic admission, and "
                             "a synthetic admission runs only the synthetic producer")
    if adm["producer"] not in adm["code"].get("modules", {}):
        raise AdmissionError("the admission states no digest for its producer")
    head = gx.git_identity(root, [])
    if head["status"] != "ok" or adm["code"].get("commit") != head["commit"]:
        raise AdmissionError(f"admitted commit {adm['code'].get('commit')} is not this "
                             f"checkout's HEAD {head['commit']}")
    if not adm["synthetic"]:
        auth = Path(root) / adm["authorization"]["path"]
        if not auth.is_file() or sha_file(auth) != adm["authorization"].get("sha256"):
            raise AdmissionError("the authorization record is absent or its digest differs")
        omni = adm["inputs"].get("rebuilt_omnifile", {})
        if not omni.get("path") or not omni.get("sha256"):
            raise AdmissionError("a real admission names the identity-carrying rebuild and its "
                                 "digest")
    split = adm["inputs"].get("split_manifest", {})
    if not split.get("path") or sha_file(split["path"]) != split.get("sha256"):
        raise AdmissionError("the split manifest is absent or its digest differs")
    if not Path(adm["outroot"]).is_absolute():
        raise AdmissionError("outroot must be absolute")
    return adm


def load_plan(path, adm):
    plan = json.loads(Path(path).read_text())
    design.validate_plan(plan["members"])
    digest = mb.plan_digest(plan["members"])
    if plan.get("plan_sha256") != digest or adm["plan_sha256"] != digest:
        raise AdmissionError("the plan is not the admitted plan")
    return plan["members"], digest


def check_split(adm):
    tables = load_fold_tables(adm["inputs"]["fold_tables"]["path"])
    recorded = json.loads(Path(adm["inputs"]["split_manifest"]["path"]).read_text())
    return identity.run_all(tables, recorded)


def cmd_plan(a):
    plan = design.members()
    design.validate_plan(plan)
    mb.write_new(a.out, json.dumps({"design": design.design_record(), "members": plan,
                                    "plan_sha256": mb.plan_digest(plan)}, indent=1, sort_keys=True))
    print(f"[plan] {len(plan)} members, sha256 {mb.plan_digest(plan)}")


def cmd_check_split(a):
    tables = load_fold_tables(a.folds)
    identity.run_all(tables, json.loads(Path(a.manifest).read_text()))
    print("[split] identities, manifest, rule, C1, C2, C3 and C5 hold")


def cmd_admit(a):
    adm = check_admission(a.admission)
    check_split(adm)
    print(f"[admit] admission holds: synthetic={adm['synthetic']} commit={adm['code']['commit']}")


def cmd_run_member(a):
    adm = check_admission(a.admission)
    plan, digest = load_plan(a.plan, adm)
    member = next((m for m in plan if m["id"] == a.member), None)
    if member is None:
        raise AdmissionError(f"{a.member} is not a declared member")
    check_split(adm)
    out = mb.result_path(adm["outroot"], member["id"])
    for p in (out, mb.failure_path(adm["outroot"], member["id"])):
        if p.exists():
            raise mb.MemberError(f"{p} exists; a member runs once and is never overwritten")
    exp = Path(adm["outroot"]) / "expect" / f"{member['id']}.json"
    mb.write_new(exp, json.dumps(adm["code"]))
    inventory = Path(adm["outroot"]) / "inventory" / f"{member['id']}.jsonl"
    inventory.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(REPO / GUARD), "--expect-root", str(REPO), "--inventory",
           str(inventory), "--label", f"N2 {member['id']}", "--", str(REPO / adm["producer"]),
           "--admission", str(Path(a.admission).resolve()), "--member", json.dumps(member),
           "--plan-sha256", digest, "--expect", str(exp), "--require-provenance", "--out", str(out)]
    cp = subprocess.run(cmd, capture_output=True, text=True)
    if cp.returncode != 0 or not out.exists():
        mb.record_failure(adm["outroot"], member["id"], digest, cp.returncode,
                          (cp.stderr or cp.stdout)[-2000:])
        print(f"[run-member] {member['id']} FAILED (exit {cp.returncode}); recorded")
        return 1
    print(f"[run-member] {member['id']} ok")
    return 0


def member_checker(adm, folds):
    def check(member, rec):
        design.check_record(member, rec)
        prov = rec.get("provenance", {})
        if not (prov.get("strict") and prov.get("guard", {}).get("expect_root") == str(REPO)
                and prov.get("git", {}).get("commit") == adm["code"]["commit"]
                and prov.get("git", {}).get("mismatched") == []):
            raise mb.MemberError(f"{member['id']}: provenance is not strict on the admitted commit")
        threads = prov.get("environment", {}).get("threads", {}).get("OMP_NUM_THREADS")
        if not adm["synthetic"] and threads != str(member["estimator"]["threads"]):
            raise mb.MemberError(f"{member['id']}: ran with OMP_NUM_THREADS={threads!r}, the "
                                 f"design fixes {member['estimator']['threads']}")
        try:
            identity.check_c6_sidecar(folds, rec.get("sidecar", {}), design.INTENDED_FOLDS)
        except identity.IdentityError as exc:
            raise mb.MemberError(f"{member['id']}: {exc}") from None
    return check


def cmd_aggregate(a):
    adm = check_admission(a.admission)
    plan, digest = load_plan(a.plan, adm)
    folds = check_split(adm)
    entries = mb.ledger(plan, adm["outroot"], digest, member_checker(adm, folds))
    result = {"design": design.design_record(), "plan_sha256": digest,
              "admission_sha256": sha_file(a.admission), "synthetic": adm["synthetic"],
              "ledger": mb.summary(entries),
              "scope": "N2 data-stream diagnostic only: no interval, MC stream, coverage or total "
                       "uncertainty is validated"}
    try:
        result.update(design.evaluate(mb.require_complete(entries)))
    except mb.MemberError as exc:
        result.update({"verdict": "INCONCLUSIVE", "reason": str(exc)})
    mb.write_new(a.out, json.dumps(result, indent=1, sort_keys=True))
    print(f"[aggregate] {result['verdict']}; {result['ledger']['counts']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--out", required=True)
    p = sub.add_parser("check-split")
    p.add_argument("--folds", required=True)
    p.add_argument("--manifest", required=True)
    p = sub.add_parser("admit")
    p.add_argument("--admission", required=True)
    p = sub.add_parser("run-member")
    p.add_argument("--admission", required=True)
    p.add_argument("--plan", required=True)
    p.add_argument("--member", required=True)
    p = sub.add_parser("aggregate")
    p.add_argument("--admission", required=True)
    p.add_argument("--plan", required=True)
    p.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        return {"plan": cmd_plan, "check-split": cmd_check_split, "admit": cmd_admit,
                "run-member": cmd_run_member, "aggregate": cmd_aggregate}[a.cmd](a) or 0
    except (AdmissionError, design.DesignError, identity.IdentityError, mb.MemberError,
            gx.ProvenanceRefusal) as exc:
        print(f"[REFUSED] {exc}", file=sys.stderr)
        return gx.REFUSAL_EXIT


if __name__ == "__main__":
    sys.exit(main())
