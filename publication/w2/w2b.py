#!/usr/bin/env python3
"""W2b orchestration (publication packet W2; Joseph 2026-10-06 item 4; W2a review C1-C3).

Subcommands (none of them submits a job; ``submit_w2b.sh`` does, after ``check-budget``):

  plan            print every W2b task with its time limit, billing and reservation, and the whole-plan worst case
  check-budget    C1: refuse (exit 3) unless  recorded spend (LEDGER-w2.tsv)
                                            + reservations of submitted jobs not yet in the ledger
                                            + reservations of the stage about to be submitted  <= 8.0 CPU node-h
  design-copies   C3: write one report-only design copy per variant that differs from the frozen design.json
                  ONLY in ``data_central``, plus a machine key-diff; refuse if any other leaf differs
  tables          write the s5c_array task tables for the lateral dumps and (with dump digests) the unfolds
  ledger-sync     append every TERMINAL submitted job (sacct ElapsedRaw x billing/256) to the ledger
  decide          C3: Holm-with-determinacy per sign, robustness (rejected under both signs), and the delta = 0
                  control; exit 0 PASS, 1 control FAIL (W2b stops), 2 could not decide

A reservation is limit_h * billing / 256 (the s5c_meter CPU convention). Spend is billed ElapsedRaw * billing/256.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

CEILING = 8.0
PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")  # run_p4_merge_audit_std.sh order
VARIANTS = ("rr0", "rr1", "rrzero")  # x0.96, x1.04, delta = 0 control
EVLOOP_LIMIT_H = {"1M": 6.0, "1F": 5.0, "1D": 5.0, "1G": 5.0}  # C1; every other playlist 4 h
EVLOOP_DEFAULT_H, EVLOOP_BILLING = 4.0, 10.0          # 2 CPU / 16 GB shared: billing 10 (measured, W2a)
DUMP_LIMIT_H, DUMP_BILLING = 1.0, 62.0               # 16 CPU / 110 GB shared: the meter declared 62 (sacct 60)
UNFOLD_LIMIT_H, UNFOLD_BILLING = 1.0, 32.0           # 32 CPU / 56 GB shared
FROZEN_DATA_SHA = "fb5cc6798b97b5902ad8f0fecbc49990271f7772f98d3063c1dc8596340e680c"  # runs/s2/num/data/data_b-_j-.npz
CV_NPZ = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"
DEPLOYS = {"dump": "c1cba7bfb214a82abde5580c72c9ef3c4704e73f",     # the s3-latdump deploy
           "unfold": "4e4b4f56bb0c4715dcf567829ac0449bfac745de",   # the s3-latunfold deploy
           "evaluate": "e9372b757250e9607f52e471d9b0c447b08e65d5"}  # the frozen evaluation deploy


def reservation(limit_h: float, billing: float) -> float:
    return limit_h * billing / 256.0


def stage_tasks(stage: str) -> list[dict]:
    if stage == "evloop":
        return [{"label": f"w2b_ev_{v}_{pl}", "limit_h": EVLOOP_LIMIT_H.get(pl, EVLOOP_DEFAULT_H),
                 "billing": EVLOOP_BILLING} for v in VARIANTS for pl in PLAYLISTS]
    if stage == "dump":
        return [{"label": f"w2b_dump_{v}", "limit_h": DUMP_LIMIT_H, "billing": DUMP_BILLING} for v in VARIANTS]
    if stage == "unfold":
        return [{"label": f"w2b_unfold_{v}", "limit_h": UNFOLD_LIMIT_H, "billing": UNFOLD_BILLING} for v in VARIANTS]
    raise SystemExit(f"unknown stage {stage}")


def read_ledger(path: Path) -> tuple[float, set[str]]:
    spend, ids = 0.0, set()
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("\t")
        if len(f) < 7:
            raise SystemExit(f"{path}: malformed ledger line: {line!r}")
        spend += float(f[6])
        ids.add(f[1])
    return spend, ids


def read_submitted(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        jobid, label, limit_h, billing = line.split("\t")[:4]
        out.append({"jobid": jobid, "label": label, "limit_h": float(limit_h), "billing": float(billing)})
    return out


def cmd_plan(_a) -> int:
    total = 0.0
    for stage in ("evloop", "dump", "unfold"):
        tasks = stage_tasks(stage)
        r = sum(reservation(t["limit_h"], t["billing"]) for t in tasks)
        total += r
        print(f"{stage}: {len(tasks)} tasks, reservation {r:.4f} node-h")
        for t in tasks:
            print(f"   {t['label']}\t{t['limit_h']:.1f} h\tbilling {t['billing']:.0f}\t{reservation(t['limit_h'], t['billing']):.4f}")
    print(f"W2b whole-plan worst case (every task at its limit): {total:.4f} node-h")
    return 0


def cmd_check_budget(a) -> int:
    spend, ledger_ids = read_ledger(a.ledger)
    inflight = [s for s in read_submitted(a.submitted) if s["jobid"] not in ledger_ids]
    r_inflight = sum(reservation(s["limit_h"], s["billing"]) for s in inflight)
    new = stage_tasks(a.stage)
    if a.labels is not None:
        want = [x for x in a.labels.split(",") if x]
        unknown = set(want) - {t["label"] for t in new}
        if unknown:
            raise SystemExit(f"labels not in stage {a.stage}: {sorted(unknown)}")
        new = [t for t in new if t["label"] in want]
    r_new = sum(reservation(t["limit_h"], t["billing"]) for t in new)
    total = spend + r_inflight + r_new
    verdict = "PASS" if total <= CEILING else "REFUSE"
    print(json.dumps({"stage": a.stage, "recorded_spend": round(spend, 4), "inflight_jobs": len(inflight),
                      "inflight_reservation": round(r_inflight, 4), "new_tasks": len(new),
                      "new_reservation": round(r_new, 4), "total": round(total, 4), "ceiling": CEILING,
                      "verdict": verdict}, indent=1))
    return 0 if verdict == "PASS" else 3


def flatten(x, prefix="") -> dict:
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            out.update(flatten(v, f"{prefix}/{k}"))
        return out if x else {prefix: {}}
    if isinstance(x, list):
        out = {}
        for i, v in enumerate(x):
            out.update(flatten(v, f"{prefix}[{i}]"))
        return out if x else {prefix: []}
    return {prefix: x}


def unfold_product(ns: str, variant: str) -> str:
    return f"{ns}/w2b/unf/w2b_{variant}_b-_j-.npz"   # s5p_numerics.product_name(tag, None, None)


def cmd_design_copies(a) -> int:
    frozen_bytes = a.frozen.read_bytes()
    frozen_sha = hashlib.sha256(frozen_bytes).hexdigest()
    frozen = json.loads(frozen_bytes)
    a.outdir.mkdir(parents=True, exist_ok=True)
    report = {"frozen_design": str(a.frozen), "frozen_sha256": frozen_sha, "copies": {}}
    ok = True
    for v in VARIANTS:
        copy = json.loads(frozen_bytes)
        copy["data_central"] = unfold_product(a.ns, v)
        fa, fb = flatten(frozen), flatten(copy)
        keys = sorted(set(fa) | set(fb))
        diff = [{"path": k, "frozen": fa.get(k, "<absent>"), "copy": fb.get(k, "<absent>")}
                for k in keys if fa.get(k, "<absent>") != fb.get(k, "<absent>")]
        out = a.outdir / f"design-w2b-{v}.json"
        out.write_text(json.dumps(copy, indent=1) + "\n")
        only = [d["path"] for d in diff] == ["/data_central"]
        ok &= only
        report["copies"][v] = {"file": out.name, "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
                               "leaves_compared": len(keys), "differing_leaves": diff,
                               "only_data_central_differs": only}
    report["verdict"] = "PASS" if ok else "FAIL"
    (a.outdir / "design-keydiff.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))
    return 0 if ok else 1


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def cmd_tables(a) -> int:
    ns = a.ns
    a.outdir.mkdir(parents=True, exist_ok=True)
    dump = ["# W2b lateral dumps (s5p_input_dumps.py lateral, as state/s5p/s3-latdump-tasks.tsv); deploy "
            + DEPLOYS["dump"]]
    for v in VARIANTS:
        dump.append("\t".join([f"w2b_dump_{v}", "s5p_input_dumps.py", "lateral", "--omnifile",
                               f"{ns}/w2b/merged/runEventLoopOmniFold_5D_MEFHC_w2b_{v}.root", "--cv-npz", CV_NPZ,
                               "--out", f"{ns}/w2b/lateral/lat_w2b_{v}.npz",
                               "--out-bkg", f"{ns}/w2b/lateral/lat_w2b_{v}_bkg.npz"]))
    (a.outdir / "w2b-dump-tasks.tsv").write_text("\n".join(dump) + "\n")
    print(f"wrote {a.outdir / 'w2b-dump-tasks.tsv'}")
    if not a.with_unfold:
        return 0
    unf = ["# W2b real-data unfolds (s5p_numerics.py, the state/s5p/s3-latunfold-tasks.tsv form); deploy "
           + DEPLOYS["unfold"]]
    for v in VARIANTS:
        npz, bkg = Path(f"{ns}/w2b/lateral/lat_w2b_{v}.npz"), Path(f"{ns}/w2b/lateral/lat_w2b_{v}_bkg.npz")
        unf.append("\t".join([f"w2b_unfold_{v}", "s5p_numerics.py", "--npz", str(npz), "--bkg", str(bkg),
                              "--expect-npz-sha256", sha256(npz), "--expect-bkg-sha256", sha256(bkg),
                              "--config", "R", "--iters", "5", "--construction", "data", "--pairs=-:-",
                              "--tag", f"w2b_{v}", "--threads", "32", "--out", f"{ns}/w2b/unf"]))
    (a.outdir / "w2b-unfold-tasks.tsv").write_text("\n".join(unf) + "\n")
    print(f"wrote {a.outdir / 'w2b-unfold-tasks.tsv'}")
    return 0


def cmd_ledger_sync(a) -> int:
    import subprocess
    _, have = read_ledger(a.ledger)
    todo = [s for s in read_submitted(a.submitted) if s["jobid"] not in have]
    if not todo:
        print("nothing to sync")
        return 0
    out = subprocess.run(["sacct", "-n", "-P", "-X", "-j", ",".join(s["jobid"] for s in todo),
                          "--format=JobID,State,ElapsedRaw,AllocTRES%80"], capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"sacct failed rc={out.returncode}: {out.stderr.strip()}")
    rows = {f[0]: f for f in (l.split("|") for l in out.stdout.splitlines() if l.strip())}
    added = 0
    with open(a.ledger, "a") as fh:
        for s in todo:
            f = rows.get(s["jobid"])
            if f is None or f[1].split()[0] in ("PENDING", "RUNNING", "REQUEUED", "CONFIGURING", "COMPLETING"):
                continue
            tres = dict(x.split("=", 1) for x in f[3].split(",") if "=" in x)
            billing = float(tres.get("billing", s["billing"]))
            fh.write(f"W2b\t{s['jobid']}\t{s['label']}\t{f[1]}\t{f[2]}\t{billing:g}\t"
                     f"{int(f[2]) / 3600 * billing / 256:.5f}\n")
            added += 1
    print(f"appended {added} of {len(todo)} pending ledger rows")
    return 0


def claims_of(evaluate: dict) -> dict:
    out = {}
    for g, t in evaluate["tests"].items():
        for s in ("total", "shape"):
            out[f"{g}:{s}"] = {"p": t[s]["p"], "k": t[s]["k"], "B": t[s]["B"]}
    return out


def cmd_decide(a) -> int:
    sys.path.insert(0, str(a.deploy / "nd-unfolding"))
    import s5p_inference as si  # the frozen module of the evaluation deploy
    alpha = json.loads(a.frozen_design.read_text())["alpha_family"]
    frozen = json.loads(a.frozen_evaluate.read_text())
    res = {"alpha_family": alpha, "signs": {}, "control": {}}
    dec = {}
    for v in VARIANTS:
        ev = json.loads((a.evaldir / f"{v}-evaluate.json").read_text())
        mine = si.holm_determined(claims_of(ev), alpha)
        agree = {k: mine[k]["decision"] == ev["decisions"][k]["decision"] for k in mine}
        if not all(agree.values()):
            print(json.dumps({"verdict": "COULD_NOT_DECIDE", "why": f"{v}: re-run Holm differs from the evaluator",
                              "tests": [k for k, ok in agree.items() if not ok]}))
            return 2
        dec[v] = mine
        res["signs"][v] = {k: {"p": mine[k]["p"], "k": mine[k]["k"], "B": mine[k]["B"],
                               "threshold": mine[k]["threshold"], "decision": mine[k]["decision"]} for k in mine}
    # delta = 0 control
    zero_prod = Path(a.zero_product)
    bitwise = sha256(zero_prod) == FROZEN_DATA_SHA
    ctrl = {"product": str(zero_prod), "sha256": sha256(zero_prod), "frozen_sha256": FROZEN_DATA_SHA,
            "bitwise_equal": bitwise}
    if bitwise:
        ctrl["verdict"] = "PASS"
    else:
        rows, ok = {}, True
        for k, e in dec["rrzero"].items():
            g, s = k.split(":")
            rng = frozen["tests"][g]["observed_jitter_p"][s]
            inside = rng["min"] <= e["p"] <= rng["max"]
            same_dec = e["decision"] == frozen["decisions"][k]["decision"]
            rows[k] = {"p": e["p"], "jitter_min": rng["min"], "jitter_max": rng["max"], "p_in_range": inside,
                       "decision": e["decision"], "frozen_decision": frozen["decisions"][k]["decision"],
                       "decision_equal": same_dec}
            ok &= inside and same_dec
        ctrl["fallback"] = rows
        ctrl["verdict"] = "PASS" if ok else "FAIL"
    res["control"] = ctrl
    if ctrl["verdict"] != "PASS":
        res["verdict"] = "CONTROL FAIL: W2b stops; no robustness statement"
        print(json.dumps(res, indent=1))
        if a.out:
            a.out.write_text(json.dumps(res, indent=1) + "\n")
        return 1
    res["robust_at_delta"] = {}
    for k in dec["rr0"]:
        both = dec["rr0"][k]["decision"] == "rejected" and dec["rr1"][k]["decision"] == "rejected"
        res["robust_at_delta"][k] = {"frozen": frozen["decisions"][k]["decision"],
                                     "minus_4pct": dec["rr0"][k]["decision"], "plus_4pct": dec["rr1"][k]["decision"],
                                     "robust": both}
    res["verdict"] = "DECIDED"
    text = json.dumps(res, indent=1)
    print(text)
    if a.out:
        a.out.write_text(text + "\n")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    c = sub.add_parser("check-budget")
    c.add_argument("--stage", choices=("evloop", "dump", "unfold"), required=True)
    c.add_argument("--ledger", type=Path, required=True)
    c.add_argument("--submitted", type=Path, required=True)
    c.add_argument("--labels", help="comma-separated subset of the stage's tasks actually being submitted")
    d = sub.add_parser("design-copies")
    d.add_argument("--frozen", type=Path, required=True)
    d.add_argument("--ns", required=True)
    d.add_argument("--outdir", type=Path, required=True)
    t = sub.add_parser("tables")
    t.add_argument("--ns", required=True)
    t.add_argument("--outdir", type=Path, required=True)
    t.add_argument("--with-unfold", action="store_true")
    ls = sub.add_parser("ledger-sync")
    ls.add_argument("--ledger", type=Path, required=True)
    ls.add_argument("--submitted", type=Path, required=True)
    e = sub.add_parser("decide")
    e.add_argument("--deploy", type=Path, required=True)
    e.add_argument("--frozen-design", type=Path, required=True)
    e.add_argument("--frozen-evaluate", type=Path, required=True)
    e.add_argument("--evaldir", type=Path, required=True)
    e.add_argument("--zero-product", required=True)
    e.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    return {"plan": cmd_plan, "check-budget": cmd_check_budget, "design-copies": cmd_design_copies,
            "tables": cmd_tables, "ledger-sync": cmd_ledger_sync, "decide": cmd_decide}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
