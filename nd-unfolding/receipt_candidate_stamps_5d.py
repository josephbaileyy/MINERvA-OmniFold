#!/usr/bin/env python3
"""Read the BEN-106 provenance stamps off the ADOPTION-CANDIDATE arms and commit them.

Why this exists, and why it is not `receipt_construction_contract_5d.py`.
-------------------------------------------------------------------------
That receipt (2026-08-11) enumerates six adopted products and **neither candidate arm is among
them** -- it predates job 56720356. Its finding was the negative one: every construction stamp is
ABSENT from every adopted product, because `adopt_unified_5d.py` then wrote only two sqrt-traces.
The stamp propagation that closed that landed the same night, and the arms it produced have never
been read by a committed instrument.

`CRITERIA-20260811` section 3 grades the provenance leg of causes 2, 3 and 4 MET, citing values
"read back from the adopted product (job 56695424)". That job's artifact is
`STAMPTEST2_bkgaware_meancentered.root` -- 892170857 bytes, `test_product_only: true`,
`adopts_nothing: true` -- and it is mean-centered only. The arms actually named as the candidate
(892170881 and 892232198 bytes, job 56720356) got a receipt carrying **hashes only**, verdict
`HASHES_COMPLETE_READ_STDOUT_FOR_ARM_VALUES`, which defers the stamp values to a stdout on
purgeable scratch that no committed artifact contains. So the P leg of causes 3 and 4 is cited to
a file that adopts nothing, and the CV-centered arm has never been stamp-verified by anything.

This reads the stamps off the arms themselves and writes one committed JSON.

THE NEGATIVE CONTROLS ARE LOAD-BEARING, not decoration. A reader that reports "present" on
everything proves nothing about the subjects. The two July products behind `\\gbdtFiveAdoptTrace`
and `\\gbdtFiveCVTrace` are the form in which the defect is still live, so the instrument is
required to come back ABSENT on them in the SAME run in which it passes on the candidate. If it
does not, branch S5 fires and the subject result is void even if the subjects pass -- see
`docs/orchestration/PREDECLARE-20260817-candidate-stamp-receipt-causes-3-4.md` section 4.

Every key is reported `{"present": true, "value": ...}` or `{"present": false}`, never omitted: a
receipt listing only what it found cannot distinguish "the key is not there" from "nobody looked".

THIS ADOPTS NOTHING AND RECOMPUTES NOTHING. Every file is opened READ; the only write is the
output JSON. No covariance is rebuilt, no ROOT is modified, no value here becomes quotable, and
`values.tex` is not touched.

Usage (on Perlmutter, inside the ROOT env):
    source setup_salloc_env.sh
    python3 receipt_candidate_stamps_5d.py --out uq_5d/receipt_candidate_stamps_5d.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

# ---------------------------------------------------------------------------------------------
# Keys. The UNION is looked for on EVERY file, subjects and controls alike, so that "absent" is a
# measured property of the file rather than a property of which list it was checked against.
#
# `upstream_*` / `*_checked` are written by adopt_unified_5d.py:198-210 (BEN-106 propagation).
# The bare names are the THROW ROOT's own keys (unified_throw_cov.py:479-489); they are expected
# absent on every adopted product, and looking for them is how that stays measured rather than
# assumed.
# ---------------------------------------------------------------------------------------------
PARAM_KEYS = [
    "sqrt_tr_old",
    "sqrt_tr_new",
    "n_throws_checked",
    "upstream_n_throws",
    "joint_mean_shift_norm_checked",
    "upstream_joint_mean_shift_norm",
    "fixed_seed_null_norm_checked",
    "upstream_fixed_seed_null_norm",
    # bare throw-ROOT names, expected absent downstream:
    "fixed_seed_null_norm",
    "fixed_seed_null_checked",
    "joint_mean_shift_norm",
    "n_throws",
    "sqrt_tr_unified",
    "sqrt_tr_block",
]
NAMED_KEYS = ["centering_convention", "uthrow_source", "combined_source"]

# The six keys adopt_unified_5d.py:215-219 fails closed on, i.e. the ones a successful adopt run
# guarantees. Note what is NOT in this list: the three `upstream_*` VALUE parameters. That gap is
# the reason this read exists rather than trusting job exit 0.
ADOPT_SELF_CHECKED = [
    "fixed_seed_null_norm_checked",
    "joint_mean_shift_norm_checked",
    "n_throws_checked",
    "centering_convention",
    "uthrow_source",
    "combined_source",
]

# Tolerance for cause 4's criterion, WITH its derivation, because the criterion is
# "key present, and <= tol, with tol and its source both stated".
#   unified_throw_cov.py:445   tol = 1e-12 * max(||base||, 1.0)
# `base` is the reported 5D cross-section over 10694 bins at ~1e-38, so ||base|| ~ 1e-36 << 1, the
# max() binds, and the tolerance is an absolute floor of 1e-12.
NULL_TOL = 1e-12
NULL_TOL_SOURCE = "unified_throw_cov.py:445  tol = 1e-12 * max(||base||, 1.0); ||base|| ~ 1e-36 << 1 so max() binds => absolute 1e-12"

HASH_MAX_BYTES = 4 * 1024**3   # stated cut, not a silent omission

# ---------------------------------------------------------------------------------------------
# Predeclared expectations. Sourced in
# docs/orchestration/PREDECLARE-20260817-candidate-stamp-receipt-causes-3-4.md section 3.
# The verdict is computed from these BY CODE, so it cannot be chosen after seeing the numbers.
# ---------------------------------------------------------------------------------------------
EXPECT_UPSTREAM = {
    "upstream_n_throws": 160,
    "upstream_joint_mean_shift_norm": 1.878696733368378e-38,
    "upstream_fixed_seed_null_norm": 5.8223488501140625e-50,
}
EXPECT_SQRT_TR_OLD = 4.357790406860002e-38

SUBJECTS = {
    "A1_candidate_meancentered": {
        "path": "uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root",
        "role": "subject",
        "expect_centering": "mean-centered",
        "expect_sha256": "4f168e83eaeb4bc7191a4e13e219c7ff06556e5ad30b9df4fcc249e6720c7ec2",
        "expect_size": 892170881,
        "expect_sqrt_tr_new": 5.2696e-38,
        "note": "headline arm of the 2026-08-12 cause-2 discharge; P leg of causes 3 and 4 must be about THIS file",
    },
    "A2_candidate_cvcentered": {
        "path": "uq_5d/readopt_20260811_footing/stamped_bkgaware_cvcentered_20260812.root",
        "role": "subject",
        "expect_centering": "cv-centered",
        "expect_sha256": "dbcd5359c76e5c12b97ec8819980cb11c492f051f054a50d9b0bca2bd02fb9dd",
        "expect_size": 892232198,
        "expect_sqrt_tr_new": 5.6743e-38,
        "note": "conservative variant; NEVER stamp-verified by anything, not even a test product",
    },
    "STAMPTEST2_positive_control": {
        "path": "uq_5d/readopt_20260811_footing/STAMPTEST2_bkgaware_meancentered.root",
        "role": "control_positive",
        "expect_centering": "mean-centered",
        "expect_sha256": None,
        "expect_size": 892170857,
        "expect_sqrt_tr_new": 5.269625166386846e-38,
        "note": "the file CRITERIA section 3 actually cites; must reproduce ben106-stamp-verify-complete-56695424.json",
    },
    "X_july_meancentered_negative_control": {
        "path": "uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware_uthrow.root",
        "role": "control_negative",
        "expect_centering": None,
        "expect_sha256": "8feb8ba468411a66899e9edd0006b398a2e0c41c56c5b53e64cfebc6b1a0d72d",
        "expect_size": 892195314,
        "expect_sqrt_tr_new": 5.807716496958672e-38,
        "note": "feeds \\gbdtFiveAdoptTrace 5.81e-38; MUST come back with every stamp ABSENT",
    },
    "X_july_cvcentered_negative_control": {
        "path": "uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware_uthrow_cvcentered.root",
        "role": "control_negative",
        "expect_centering": None,
        "expect_sha256": "b4edc66588f1b9c78bc9a30793419746dc2b95ae220950f17e7329c128fe3a55",
        "expect_size": 892241032,
        "expect_sqrt_tr_new": 6.236702327843976e-38,
        "note": "feeds \\gbdtFiveCVTrace 6.24e-38; MUST come back with every stamp ABSENT",
    },
}


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(16 * 1024**2), b""):
            h.update(chunk)
    return h.hexdigest()


def read_one(path: str, want_hash: bool) -> dict:
    import ROOT

    ROOT.gErrorIgnoreLevel = ROOT.kError
    if not os.path.exists(path):
        return {"path": path, "exists": False, "read": False,
                "read_error": "file does not exist"}
    st = os.stat(path)
    block = {
        "path": path,
        "exists": True,
        "size_bytes": st.st_size,
        "mtime_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
    }
    if want_hash and st.st_size <= HASH_MAX_BYTES:
        block["sha256"] = sha256_file(path)
    else:
        block["sha256"] = None
        block["hash_skipped_reason"] = (
            f"size {st.st_size} > {HASH_MAX_BYTES} byte cut" if want_hash
            else "hashing not requested for this role"
        )
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        block["read"] = False
        block["read_error"] = "TFile.Open failed or zombie"
        return block
    block["read"] = True

    params = {}
    for name in PARAM_KEYS:
        obj = f.Get(name)
        if not obj:
            params[name] = {"present": False}
            continue
        try:
            params[name] = {"present": True, "value": obj.GetVal()}
        except AttributeError:
            params[name] = {"present": True, "value": None,
                            "note": f"present but not a TParameter: {type(obj).__name__}"}
    named = {}
    for name in NAMED_KEYS:
        obj = f.Get(name)
        if not obj:
            named[name] = {"present": False}
        else:
            try:
                named[name] = {"present": True, "value": obj.GetTitle()}
            except AttributeError:
                named[name] = {"present": True, "value": None,
                               "note": f"present but not a TNamed: {type(obj).__name__}"}
    block["parameters"] = params
    block["named"] = named
    block["all_keys"] = sorted({k.GetName() for k in f.GetListOfKeys()})
    f.Close()
    return block


def grade(label: str, meta: dict, block: dict) -> dict:
    """Compare a read against the predeclaration. Returns findings; does not decide the branch."""
    out = {"role": meta["role"], "mismatches": [], "confirmations": []}
    if not block.get("read"):
        out["mismatches"].append(f"UNREADABLE: {block.get('read_error')}")
        return out

    params, named = block["parameters"], block["named"]
    present = {k for k, v in params.items() if v["present"]} | {
        k for k, v in named.items() if v["present"]}

    if meta["role"] == "control_negative":
        # Every propagation stamp must be ABSENT. This is the direction the instrument must fail in.
        should_be_absent = [k for k in ADOPT_SELF_CHECKED] + list(EXPECT_UPSTREAM)
        leaked = sorted(k for k in should_be_absent if k in present)
        if leaked:
            out["mismatches"].append(
                f"NEGATIVE CONTROL LEAKED: expected every stamp absent, found {leaked}")
        else:
            out["confirmations"].append(
                f"all {len(should_be_absent)} propagation stamps ABSENT, as required")
    else:
        missing = sorted(k for k in ADOPT_SELF_CHECKED if k not in present)
        if missing:
            out["mismatches"].append(f"missing adopt-self-checked stamps: {missing}")
        else:
            out["confirmations"].append(
                f"all {len(ADOPT_SELF_CHECKED)} adopt-self-checked stamps present")

        for k in ("n_throws_checked", "joint_mean_shift_norm_checked",
                  "fixed_seed_null_norm_checked"):
            v = params.get(k, {})
            if v.get("present") and v.get("value") != 1:
                out["mismatches"].append(f"{k} = {v.get('value')}, expected 1")

        for k, exp in EXPECT_UPSTREAM.items():
            v = params.get(k, {})
            if not v.get("present"):
                out["mismatches"].append(f"{k} ABSENT -- this is the value leg, not the flag")
                continue
            got = v["value"]
            same = (got == exp) if isinstance(exp, int) else (
                abs(got - exp) <= 1e-15 * abs(exp))
            if same:
                out["confirmations"].append(f"{k} = {got!r} matches predeclared")
            else:
                out["mismatches"].append(f"{k} = {got!r}, predeclared {exp!r}")

        cent = named.get("centering_convention", {})
        if meta["expect_centering"] is not None:
            if cent.get("value") != meta["expect_centering"]:
                out["mismatches"].append(
                    f"centering_convention = {cent.get('value')!r}, expected "
                    f"{meta['expect_centering']!r}")
            else:
                out["confirmations"].append(
                    f"centering_convention = {cent.get('value')!r}")

        nul = params.get("upstream_fixed_seed_null_norm", {})
        if nul.get("present"):
            val = nul["value"]
            out["cause4_null_check"] = {
                "value": val, "tol": NULL_TOL, "tol_source": NULL_TOL_SOURCE,
                "ratio_to_tol": val / NULL_TOL, "within_tol": bool(val <= NULL_TOL),
            }
            if val > NULL_TOL:
                out["mismatches"].append(
                    f"upstream_fixed_seed_null_norm {val} EXCEEDS tol {NULL_TOL}")

    # sha256 / size binding applies to every role that predeclared one.
    if meta.get("expect_size") is not None and block.get("size_bytes") != meta["expect_size"]:
        out["mismatches"].append(
            f"size {block.get('size_bytes')} != predeclared {meta['expect_size']}")
    if meta.get("expect_sha256") and block.get("sha256"):
        if block["sha256"] != meta["expect_sha256"]:
            out["mismatches"].append(
                f"sha256 {block['sha256']} != predeclared {meta['expect_sha256']}")
        else:
            out["confirmations"].append("sha256 matches the committed receipt")

    exp_tr = meta.get("expect_sqrt_tr_new")
    got_tr = params.get("sqrt_tr_new", {}).get("value")
    if exp_tr is not None and got_tr is not None:
        rel = abs(got_tr - exp_tr) / abs(exp_tr)
        out["sqrt_tr_new_check"] = {"read": got_tr, "predeclared": exp_tr, "rel_diff": rel}
        # the two candidate predictions are quoted to 5 s.f. in STAMPED_HASH_RECEIPT.predicted
        if rel > 1e-4:
            out["mismatches"].append(
                f"sqrt_tr_new {got_tr} vs predeclared {exp_tr} (rel {rel:.2e})")
    if got_tr is not None:
        old = params.get("sqrt_tr_old", {}).get("value")
        if old is not None:
            out["ingredients"] = {
                "sqrt_tr_old": old, "sqrt_tr_new": got_tr, "ratio": got_tr / old,
                "sqrt_tr_old_matches_predeclared": abs(old - EXPECT_SQRT_TR_OLD) <= 1e-15 * EXPECT_SQRT_TR_OLD,
            }
    return out


def git_rev(repo: str) -> dict:
    def run(argv):
        try:
            return subprocess.run(argv, cwd=repo, capture_output=True, text=True,
                                  check=False).stdout.strip()
        except Exception:  # noqa: BLE001
            return None
    return {"head": run(["git", "rev-parse", "HEAD"]),
            "dirty": bool(run(["git", "status", "--porcelain"]))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="/pscratch/sd/j/josephrb/MINERvA-OmniFold")
    ap.add_argument("--out", default="uq_5d/receipt_candidate_stamps_5d.json")
    args = ap.parse_args()

    nd = os.path.join(args.repo, "nd-unfolding")
    os.chdir(nd)

    receipt = {
        "schema": "candidate-stamp-receipt/1",
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "purpose": ("Provenance (P) leg of quarantine causes 3 and 4, read off the ADOPTION-CANDIDATE "
                    "arms of job 56720356 rather than off the test product of job 56695424. Reads "
                    "existing stamps; adopts nothing, recomputes nothing, makes no value quotable."),
        "predeclaration": "docs/orchestration/PREDECLARE-20260817-candidate-stamp-receipt-causes-3-4.md",
        "criteria": "docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md",
        "adopts_nothing": True,
        "values_tex_untouched": True,
        "reader_sha256": sha256_file(os.path.abspath(__file__)),
        "git": git_rev(args.repo),
        "tolerance": {"null_tol": NULL_TOL, "derivation": NULL_TOL_SOURCE},
        "keys_looked_for": {
            "parameters": PARAM_KEYS,
            "named": NAMED_KEYS,
            "adopt_self_checked": ADOPT_SELF_CHECKED,
            "note": ("The UNION is looked for on every file, subjects and controls alike, so that "
                     "'absent' is a measured property of the file and not of which list it was "
                     "checked against. Absence is reported, never omitted. NOTE the three "
                     "upstream_* VALUE parameters are NOT in adopt_self_checked: "
                     "adopt_unified_5d.py:215-219 fails closed on the three *_checked flags and "
                     "three TNameds only, so job exit 0 does not by itself attest the values."),
        },
        "files": {},
        "grades": {},
    }

    for label, meta in SUBJECTS.items():
        want_hash = meta.get("expect_sha256") is not None or meta["role"] != "control_negative"
        print(f"[cand] reading {label}: {meta['path']}", flush=True)
        block = read_one(meta["path"], want_hash)
        block["role"] = meta["role"]
        block["note"] = meta["note"]
        receipt["files"][label] = block
        g = grade(label, meta, block)
        receipt["grades"][label] = g
        print(f"[cand]   read={block.get('read')} size={block.get('size_bytes')} "
              f"sha256={block.get('sha256')}", flush=True)
        for c in g["confirmations"]:
            print(f"[cand]   OK  {c}", flush=True)
        for m in g["mismatches"]:
            print(f"[cand]   !!  {m}", flush=True)

    subj = [l for l, m in SUBJECTS.items() if m["role"] == "subject"]
    negs = [l for l, m in SUBJECTS.items() if m["role"] == "control_negative"]
    pos = [l for l, m in SUBJECTS.items() if m["role"] == "control_positive"]

    unread = [l for l in SUBJECTS if not receipt["files"][l].get("read")]
    neg_bad = [l for l in negs if receipt["grades"][l]["mismatches"]]
    subj_bad = [l for l in subj if receipt["grades"][l]["mismatches"]]
    pos_bad = [l for l in pos if receipt["grades"][l]["mismatches"]]
    sha_bad = [l for l in SUBJECTS
               if any("sha256" in m for m in receipt["grades"][l]["mismatches"])]

    # Branch selection, in the order declared in the predeclaration. S5 dominates S1: an instrument
    # that cannot fail on the negative controls has not demonstrated anything on the subjects.
    if unread:
        branch, why = "S4", f"unreadable/absent: {unread}"
    elif neg_bad:
        branch, why = "S5", (f"negative control did not come back absent: {neg_bad}; "
                             "subject result is VOID even if the subjects passed")
    elif sha_bad:
        branch, why = "S3", f"sha256 binding broken: {sha_bad}"
    elif subj_bad:
        branch, why = "S2", f"subject stamps missing or values differ: {subj_bad}"
    else:
        branch, why = "S1", ("both candidate arms carry all six self-checked stamps AND all three "
                             "upstream_* values, matching the predeclaration; both negative "
                             "controls came back with every stamp absent")
    receipt["verdict"] = {
        "branch": branch,
        "why": why,
        "positive_control_reproduced": not pos_bad,
        "positive_control_mismatches": {l: receipt["grades"][l]["mismatches"] for l in pos_bad},
        "scope": ("P leg only, and for the CANDIDATE only. Under S1 this does NOT discharge cause 3 "
                  "or cause 4: cause 4's M leg is recorded UNRESOLVED in CRITERIA section 2 and no "
                  "stamp read changes that, and cause 3's M is graded differently in CRITERIA "
                  "section 2 (M(ii) UNRESOLVED) than in section 3 (MET). Both are judgements and "
                  "neither is taken here."),
    }
    print(f"\n[cand] BRANCH {branch}: {why}", flush=True)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tmp = args.out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, args.out)   # write-to-temp + rename (BEN-023)
    print(f"[cand] wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
