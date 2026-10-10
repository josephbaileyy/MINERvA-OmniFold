#!/usr/bin/env python3
"""Decide SB1 from its receipts, the scheduler's accounting and its outputs, by the frozen rules.

    sb1_verify.py verdict --outroot DIR --admission ADM --sacct SACCT.psv [--reference-product F]
                          [--cv-reference-product F] [--out VERDICT.json]
    sb1_verify.py ledger  --admission ADM --sacct SACCT.psv [--retry JOB]

``SACCT.psv`` is ``sacct -P --units=K -j <every SB1 job id> -o JobID,JobName,State,ElapsedRaw,
MaxRSS,MaxDiskRead,AllocTRES,ExitCode`` (``launch/sb1_hash.sbatch`` writes it). The verifier
shares no code with the wrapper beyond reading its receipts, so it re-derives every comparison
from recorded values. Criteria (REPORT §6, frozen before any run):

* P   provenance: every receipt strict, guarded, at the admitted commit with the admitted module
      digests; each input's stat equal to H0's at every job's start and end; H0 and H1 equal; and
      every guard inventory record shows the guard installed on the admitted checkout alone (no
      ``--allow``, no origin outside it) with the manifest's shim.
* S1  input preservation (mandatory): every loader's arrays and histogram byte-identical between
      arms in the lateral (UL vs SL), vertical (J1) and CV (C) patterns, with equal settings; the
      selective arm verified before its first read; the all arm entered with every branch active.
* NC  the two J1 activation controls were refused (exit 5) before any loader returned.
* S2  SL MaxDiskRead <= 10 GB and <= 0.1 x UL's.   S3  SL MaxRSS <= 30 GB and <= 0.5 x UL's.
* S4  SL elapsed <= 0.5 x UL elapsed (same argv, threads and node shape).
* S5  output equivalence UL vs SL: byte-identical histograms PASS; every hXSec2D bin within
      1e-8 relative PASS-AT-TOLERANCE; otherwise INCONCLUSIVE (the 128-thread rerun envelope is
      unmeasured). It never makes S1-S4 fail.
* S6  C's hooked phases cover >= 90 % of its wrapper wall (D2's phase profile).

Overall: PASS iff P, S1, NC, S2, S3 and S4 pass; FAIL if S1 or NC fails, or if P and S1 pass and
S2, S3 or S4 is measured and fails; otherwise INCONCLUSIVE. A comparison with a historical product
is reported as UNMATCHED and enters no criterion.
"""

import argparse
import json
import re
import sys
from pathlib import Path

GB = 1e9
UNIT = {"": 1, "K": 1024, "M": 1024 ** 2, "G": 1024 ** 3, "T": 1024 ** 4, "P": 1024 ** 5}
BILLING_PER_NODE = 256
TOL_REL = 1e-8


def sacct_bytes(text):
    """``'16296360K'`` -> bytes (sacct's suffixes are powers of 1024); empty -> None."""
    text = (text or "").strip()
    if not text:
        return None
    m = re.fullmatch(r"([0-9.]+)([KMGTP]?)", text)
    if not m:
        raise ValueError(f"unparsed sacct size {text!r}")
    return float(m.group(1)) * UNIT[m.group(2)]


def read_sacct(path):
    rows = [line.rstrip("\n").split("|") for line in Path(path).read_text().splitlines()
            if line.strip() and not line.startswith("#")]
    head, body = rows[0], rows[1:]
    return [dict(zip(head, r)) for r in body]


def job_metrics(rows, jobid):
    """Allocation row for State/Elapsed/billing; the batch step for MaxRSS/MaxDiskRead."""
    alloc = next((r for r in rows if r["JobID"] == jobid), None)
    batch = next((r for r in rows if r["JobID"] == f"{jobid}.batch"), None)
    if alloc is None:
        return None
    tres = dict(kv.split("=", 1) for kv in alloc.get("AllocTRES", "").split(",") if "=" in kv)
    billing = int(tres["billing"]) if "billing" in tres else None
    elapsed = int(alloc["ElapsedRaw"]) if alloc.get("ElapsedRaw") else None
    return {"state": alloc.get("State"), "elapsed_s": elapsed, "billing": billing,
            "node_h": (billing / BILLING_PER_NODE * elapsed / 3600.0
                       if billing is not None and elapsed is not None else None),
            "maxrss_bytes": sacct_bytes(batch.get("MaxRSS")) if batch else None,
            "maxdiskread_bytes": sacct_bytes(batch.get("MaxDiskRead")) if batch else None,
            "exit_code": alloc.get("ExitCode")}


def load(path):
    p = Path(path)
    return json.loads(p.read_text()) if p.is_file() and p.stat().st_size else None


class Verdicts:
    def __init__(self):
        self.items = {}

    def set(self, key, verdict, **detail):
        self.items[key] = dict(verdict=verdict, **detail)

    def get(self, key):
        return self.items.get(key, {}).get("verdict", "INCONCLUSIVE")


def check_receipt(rec, adm, h0, want_status="complete"):
    """Provenance problems with one receipt (empty list: none)."""
    if rec is None:
        return ["missing"]
    bad = []
    if rec.get("status") != want_status:
        bad.append(f"status {rec.get('status')!r}, expected {want_status!r}")
    ident = rec.get("identity", {})
    if not ident.get("strict"):
        bad.append("not strict")
    guard = ident.get("guard", {})
    if not guard.get("installed") or guard.get("expect_root") != adm["checkout"]:
        bad.append(f"guard {guard}")
    git = ident.get("git", {})
    if git.get("commit") != adm["code"]["commit"] or git.get("mismatched"):
        bad.append(f"git {git}")
    executed = {r["relpath"]: r["sha256"] for r in ident.get("executed", [])}
    for rel, sha in adm["code"]["modules"].items():
        if executed.get(rel) != sha:
            bad.append(f"{rel} executed as {executed.get(rel)}")
    extra = sorted(set(executed) - set(adm["code"]["modules"]))
    if extra:
        bad.append(f"unadmitted modules executed {extra}")
    if want_status == "complete":
        for phase in ("inputs_start", "inputs_end"):
            for key, st in (rec.get(phase) or {}).items():
                ref = (h0 or {}).get("files", {}).get(st["path"])
                if ref is None or any(ref[k] != st[k] for k in ("size", "mtime_ns", "ino")):
                    bad.append(f"{phase} {key} differs from H0")
        if not rec.get("inputs_end"):
            bad.append("no end-of-run input check")
    return bad


#: Guarded runs per job: UL 1, SL 1, J1 4 + 4 + 2 controls, C 3.
INVENTORIES = {"UL": ("inventory.jsonl",), "SL": ("inventory.jsonl",),
               "J1": tuple(f"inventory_{a}_{t}.jsonl" for a in ("all", "selective")
                           for t in ("data", "mc_background", "mc_signal_reco", "mc_truth_denom"))
               + ("inventory_control_omit.jsonl", "inventory_control_extra.jsonl"),
               "C": ("inventory_unfold.jsonl", "inventory_loaders_all.jsonl",
                     "inventory_loaders_selective.jsonl")}


def check_inventories(outroot, adm, shim_sha256):
    """What the OI-136 guard itself recorded about every guarded run (empty list: no problem)."""
    bad = []
    for job, names in INVENTORIES.items():
        for name in names:
            path = Path(outroot) / job / name
            recs = [json.loads(line) for line in path.read_text().splitlines()] \
                if path.is_file() else []
            if not recs:
                bad.append(f"{job}/{name}: missing")
            for r in recs:
                if not (r.get("guard_installed") and r.get("expect_root") == adm["checkout"]
                        and r.get("allow_is_empty") and r.get("repo_origins_outside_expect_root") == 0
                        and r.get("script_checkout_root") == adm["checkout"]
                        and r.get("shim_sha256") == shim_sha256 and r.get("violation") is None):
                    bad.append(f"{job}/{name}: guard record {r.get('label')!r} does not show an "
                               "installed guard on the admitted checkout alone")
    return bad


def compare_loaders(a, b):
    """Differences between two receipts' loader records, keyed by tree."""
    if a is None or b is None:
        return ["missing receipt"]
    ra = {r["tree"]: r for r in a.get("loaders", [])}
    rb = {r["tree"]: r for r in b.get("loaders", [])}
    diffs = []
    for tree in sorted(set(ra) | set(rb)):
        x, y = ra.get(tree), rb.get(tree)
        if x is None or y is None:
            diffs.append(f"{tree}: present in one arm only")
            continue
        if x["digests"] != y["digests"]:
            diffs.append(f"{tree}: digests differ in "
                         f"{sorted(k for k in x['digests'] if x['digests'].get(k) != y['digests'].get(k))}")
        if x["settings"] != y["settings"]:
            diffs.append(f"{tree}: settings differ")
    return diffs


def arm_checks(rec, arm):
    out = []
    for r in (rec or {}).get("loaders", []):
        if arm == "all" and r.get("n_active_on_entry") != r.get("n_branches_in_tree"):
            out.append(f"{r['tree']}: all arm entered with inactive branches")
        if arm == "selective" and not r.get("verified_before_first_read"):
            out.append(f"{r['tree']}: selective arm not verified before its first read")
    return out


def hist_values(path):
    import ROOT
    import numpy as np
    f = ROOT.TFile.Open(str(path))
    if not f or f.IsZombie():
        raise OSError(f"cannot open {path}")
    out = {}
    for key in f.GetListOfKeys():
        h = key.ReadObj()
        if h.InheritsFrom("TH1"):
            n = h.GetNcells()
            out[key.GetName()] = (np.array([h.GetBinContent(i) for i in range(n)]),
                                  np.array([h.GetBinError(i) for i in range(n)]))
    f.Close()
    return out


def max_rel(a, b):
    import numpy as np
    den = np.maximum(np.abs(a), np.abs(b))
    nz = den > 0
    return float(np.max(np.abs(a - b)[nz] / den[nz])) if nz.any() else 0.0


def output_comparison(pa, pb, label):
    try:
        ha, hb = hist_values(pa), hist_values(pb)
    except Exception as exc:                          # noqa: BLE001 - recorded
        return {"label": label, "error": f"{type(exc).__name__}: {exc}"}
    names = sorted(set(ha) & set(hb))
    identical = all(ha[n][0].tobytes() == hb[n][0].tobytes() and
                    ha[n][1].tobytes() == hb[n][1].tobytes() for n in names) and \
        set(ha) == set(hb)
    rel = {n: max_rel(ha[n][0], hb[n][0]) for n in names}
    return {"label": label, "histograms": len(names), "byte_identical": identical,
            "max_rel_hXSec2D": rel.get("hXSec2D"), "max_rel_any": max(rel.values()) if rel else None,
            "only_in_one": sorted(set(ha) ^ set(hb))}


LEAF_PHASES = ("load:", "digest:", "omnifold", "build_measured_training_2d", "compute_",
               "extract_cross_section_2d", "project_xsec_1d")


def phase_coverage(rec):
    if not rec or not rec.get("wall_s"):
        return None
    leaf = [e for e in rec["phases"] if e["name"].startswith(LEAF_PHASES) and "end_s" in e]
    by = {}
    for e in leaf:
        key = e["name"].split(":")[0] if e["name"].startswith(("load:", "digest:")) else e["name"]
        by[key] = by.get(key, 0.0) + e["end_s"] - e["start_s"]
    covered = sum(by.values())
    return {"wall_s": rec["wall_s"], "covered_s": covered, "fraction": covered / rec["wall_s"],
            "by_phase_s": by}


def verdict(a):
    adm = json.loads(Path(a.admission).read_text())
    rows = read_sacct(a.sacct)
    sub = load(Path(a.outroot) / "submission.json") or {}
    ids = sub.get("jobs", {})
    out = Path(a.outroot)
    h0, h1 = load(out / "H0" / "hashes.json"), load(out / "H1" / "hashes.json")
    rec = {"UL": load(out / "UL" / "receipt.json"), "SL": load(out / "SL" / "receipt.json"),
           "C": load(out / "C" / "receipt.json"),
           "C_all": load(out / "C" / "loaders_all.json"),
           "C_sel": load(out / "C" / "loaders_selective.json")}
    for t in ("data", "mc_background", "mc_signal_reco", "mc_truth_denom"):
        rec[f"J1_all_{t}"] = load(out / "J1" / f"all_{t}.json")
        rec[f"J1_sel_{t}"] = load(out / "J1" / f"selective_{t}.json")
    controls = {k: load(out / "J1" / f"control_{k}.json") for k in ("omit", "extra")}
    v = Verdicts()

    # P: provenance and input identity
    prov = {}
    if h0 is None or h1 is None:
        prov["hashes"] = ["H0 or H1 record missing"]
    else:
        for path, st in adm["inputs_observed"].items():
            r0, r1 = h0["files"].get(path), h1["files"].get(path)
            if r0 is None or r1 is None:
                prov.setdefault("hashes", []).append(f"{path} not hashed in H0 and H1")
                continue
            if any(r0[k] != st[k] for k in ("size", "mtime_ns", "ino")):
                prov.setdefault("hashes", []).append(f"{path}: H0 stat differs from the admission")
            if r0 != {**r1, "seconds": r0["seconds"]}:
                prov.setdefault("hashes", []).append(f"{path}: H1 differs from H0")
    for key, r in rec.items():
        problems = check_receipt(r, adm, h0)
        if problems:
            prov[key] = problems
    for k, r in controls.items():
        problems = check_receipt(r, adm, h0, want_status="selection-refused")
        if problems:
            prov[f"control_{k}"] = problems
    manifest = json.loads((Path(__file__).resolve().parent / "manifest" /
                           "expected-code.json").read_text())
    inv = check_inventories(out, adm, manifest["guard"]["nd-unfolding/mnv_guard_shim/sitecustomize.py"])
    if inv:
        prov["guard_inventories"] = inv
    v.set("P", "PASS" if not prov else ("INCONCLUSIVE" if any("missing" in str(p) for p in prov.values())
                                        else "FAIL"), problems=prov)

    # S1: input preservation in three patterns
    s1 = {"lateral": compare_loaders(rec["UL"], rec["SL"]),
          "vertical": sum((compare_loaders(rec[f"J1_all_{t}"], rec[f"J1_sel_{t}"])
                           for t in ("data", "mc_background", "mc_signal_reco", "mc_truth_denom")), []),
          "cv": compare_loaders(rec["C_all"], rec["C_sel"]),
          "cv_unfold_vs_loaders": compare_loaders(rec["C"], rec["C_all"])}
    s1["arms"] = (arm_checks(rec["UL"], "all") + arm_checks(rec["SL"], "selective") +
                  arm_checks(rec["C_all"], "all") + arm_checks(rec["C_sel"], "selective") +
                  sum((arm_checks(rec[f"J1_all_{t}"], "all") + arm_checks(rec[f"J1_sel_{t}"], "selective")
                       for t in ("data", "mc_background", "mc_signal_reco", "mc_truth_denom")), []))
    missing = [k for k, d in s1.items() if any("missing" in x for x in d)]
    differs = [k for k, d in s1.items() if d and k not in missing]
    v.set("S1", "FAIL" if differs else ("INCONCLUSIVE" if missing else "PASS"), detail=s1)

    # NC: activation controls refused before any loader returned
    nc = {k: (c is not None and c.get("exit_code") == 5 and c.get("status") == "selection-refused"
              and c.get("loaders") == []) for k, c in controls.items()}
    v.set("NC", "PASS" if all(nc.values()) else
          ("INCONCLUSIVE" if any(c is None for c in controls.values()) else "FAIL"), detail=nc)

    # S2-S4 from the scheduler
    m = {j: job_metrics(rows, ids[j]) if j in ids else None for j in ("H0", "UL", "SL", "J1", "C", "H1")}
    ul, sl = m.get("UL"), m.get("SL")
    complete = bool(ul and sl and ul["state"] == "COMPLETED" and sl["state"] == "COMPLETED")

    def crit(key, ok, **detail):
        v.set(key, ("PASS" if ok else "FAIL") if complete else "INCONCLUSIVE", **detail)
    if complete and None not in (ul["maxdiskread_bytes"], sl["maxdiskread_bytes"],
                                 ul["maxrss_bytes"], sl["maxrss_bytes"]):
        crit("S2", sl["maxdiskread_bytes"] <= 10 * GB and
             sl["maxdiskread_bytes"] <= 0.1 * ul["maxdiskread_bytes"],
             sl_gb=sl["maxdiskread_bytes"] / GB, ul_gb=ul["maxdiskread_bytes"] / GB)
        crit("S3", sl["maxrss_bytes"] <= 30 * GB and sl["maxrss_bytes"] <= 0.5 * ul["maxrss_bytes"],
             sl_gb=sl["maxrss_bytes"] / GB, ul_gb=ul["maxrss_bytes"] / GB)
        crit("S4", sl["elapsed_s"] <= 0.5 * ul["elapsed_s"], sl_s=sl["elapsed_s"],
             ul_s=ul["elapsed_s"], ratio=sl["elapsed_s"] / ul["elapsed_s"])
    else:
        for key in ("S2", "S3", "S4"):
            v.set(key, "INCONCLUSIVE", reason="UL or SL incomplete or unaccounted")

    # S5: output equivalence (matched), and the unmatched historical comparison
    s5 = None
    if rec["UL"] and rec["SL"] and rec["UL"].get("output") and rec["SL"].get("output"):
        s5 = output_comparison(rec["UL"]["output"]["path"], rec["SL"]["output"]["path"],
                               "UL vs SL (matched: same commit, argv, threads, node shape)")
    if s5 is None or "error" in s5:
        v.set("S5", "INCONCLUSIVE", detail=s5)
    elif s5["byte_identical"]:
        v.set("S5", "PASS", detail=s5)
    elif s5["max_rel_hXSec2D"] is not None and s5["max_rel_hXSec2D"] <= TOL_REL:
        v.set("S5", "PASS-AT-TOLERANCE", detail=s5,
              note="within 1e-8; the 128-thread rerun envelope itself is unmeasured")
    else:
        v.set("S5", "INCONCLUSIVE", detail=s5,
              note="exceeds 1e-8 with byte-identical inputs: unexplained until the 128-thread "
                   "rerun envelope is measured; not evidence against prototype 1")
    unmatched = []
    if a.reference_product:
        for arm in ("UL", "SL"):
            if rec[arm] and rec[arm].get("output"):
                unmatched.append(output_comparison(rec[arm]["output"]["path"], a.reference_product,
                                                   f"{arm} vs historical reference (UNMATCHED: "
                                                   "July driver revision)"))
    if a.cv_reference_product and rec["C"] and rec["C"].get("output"):
        unmatched.append(output_comparison(rec["C"]["output"]["path"], a.cv_reference_product,
                                           "C vs 59410433_1 (UNMATCHED: other driver revision)"))

    cov = phase_coverage(rec["C"])
    v.set("S6", "INCONCLUSIVE" if cov is None else ("PASS" if cov["fraction"] >= 0.9 else "FAIL"),
          detail=cov)

    core = [v.get(k) for k in ("P", "S1", "NC", "S2", "S3", "S4")]
    if v.get("S1") == "FAIL" or v.get("NC") == "FAIL":
        overall = "FAIL"
    elif all(x == "PASS" for x in core):
        overall = "PASS"
    elif v.get("P") == "PASS" and v.get("S1") == "PASS" and "FAIL" in core[3:]:
        overall = "FAIL"
    else:
        overall = "INCONCLUSIVE"
    charged = sum(x["node_h"] for x in m.values() if x and x["node_h"] is not None)
    result = {"schema": "sb1-verdict/1", "overall": overall, "criteria": v.items,
              "unmatched_historical": unmatched, "scheduler": m,
              "charged_node_h": charged, "ceiling_node_h": adm["ceiling_node_h"],
              "within_ceiling": charged <= adm["ceiling_node_h"],
              "cannot_authorize": adm.get("cannot_authorize")}
    text = json.dumps(result, indent=1, sort_keys=True, default=str)
    if a.out:
        Path(a.out).write_text(text + "\n")
    print(text)
    return 0


def ledger(a):
    adm = json.loads(Path(a.admission).read_text())
    rows = read_sacct(a.sacct)
    sub = load(Path(adm["outroot"]) / "submission.json") or {}
    spent, pending = 0.0, 0.0
    lines = []
    for job in adm["jobs"]:
        jid = sub.get("jobs", {}).get(job["id"])
        met = job_metrics(rows, jid) if jid else None
        if met and met["state"] not in ("PENDING", "RUNNING") and met["node_h"] is not None:
            spent += met["node_h"]
            lines.append(f"{job['id']} {met['state']} {met['node_h']:.4f} node-h charged")
        else:
            pending += job["ceiling_node_h"]
            lines.append(f"{job['id']} not finished: ceiling {job['ceiling_node_h']:.4f}")
    retry = 0.0
    if a.retry:
        retry = next(j["ceiling_node_h"] for j in adm["jobs"] if j["id"] == a.retry)
    total = spent + pending + retry
    print("\n".join(lines))
    print(f"charged {spent:.4f} + unfinished ceilings {pending:.4f} + retry {retry:.4f} = "
          f"{total:.4f} of {adm['ceiling_node_h']} node-h")
    return 0 if total <= adm["ceiling_node_h"] else 6


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("verdict")
    p.add_argument("--outroot", required=True)
    p.add_argument("--admission", required=True)
    p.add_argument("--sacct", required=True)
    p.add_argument("--reference-product")
    p.add_argument("--cv-reference-product")
    p.add_argument("--out")
    q = sp.add_parser("ledger")
    q.add_argument("--admission", required=True)
    q.add_argument("--sacct", required=True)
    q.add_argument("--retry")
    a = ap.parse_args(argv)
    return verdict(a) if a.cmd == "verdict" else ledger(a)


if __name__ == "__main__":
    sys.exit(main())
