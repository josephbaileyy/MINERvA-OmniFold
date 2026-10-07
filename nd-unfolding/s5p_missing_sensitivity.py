#!/usr/bin/env python3
"""s5p: a LABELLED worst/best-case sensitivity of the joint result to the seeds production lost (report only).

Production keeps the products that exist: the controller's B and the evaluator's ensemble are the finished products,
and a task killed at its time limit loses the seed it was running (INTERRUPTED) and the later seeds of its range
(NEVER STARTED). Their statistics are unobserved, so their effect cannot be measured; this step bounds it.

Classification, per submitted batch (a ``job`` record in the meter ledger) and per seed of its frozen task table:
``completed`` (a finished product), ``interrupted`` / ``never started`` (from the task-log classification of
``docs/orchestration/state/s5p/diag/s5p_lost_seed_runtime_diagnostic.py``), ``unestablished`` (anything else: no
finished log, an unverified or unaccounted seed). Batches never submitted are ``not submitted``, not missing. The
completed count of every calibration null must equal the evaluator's B and of every power set its n, otherwise the
step refuses (the classification would not describe the evaluated ensemble).

Bounds, per test, with M missing draws of a null (the claim p is the largest p over the variants, each variant's
count moves by the same amount, so the claim's does):
* ``worst_interrupted``: the interrupted draws AND any unestablished ones (unknowns count pessimistically) all
  exceed the observed statistic: k + I + U, B + I + U;
* ``worst_all_missing``: every missing draw (interrupted, never started, unestablished) exceeds it: k + M, B + M;
* ``best_all_missing``: none exceeds it: k, B + M.
p = (k + 1) / (B + 1). The full Holm procedure with determinacy (``s5p_inference.holm_determined``) is re-run on the
ten tests under each bound, so step-down effects on other tests are included. A decision "survives" a bound when
that bound's decision is the same. Holm with determinacy is NOT monotone in the counts, so these corners are
DESCRIPTIVE: they are not proven to be the extremes over all assignments of the missing draws.
CERTIFICATE (sufficient, proven for every assignment): R is the set rejected by a family's own run. With the
missing draws present (B' = B + M for each test), suppose that for every r in R the 95% Clopper-Pearson upper end
at the worst count (k + M, B + M) is below alpha / m, and that max over R of the worst p, (k + M + 1) / (B + M + 1),
is below min over the tests outside R of the best p, (k + 1) / (B + M + 1). Then for every assignment R occupies
the first |R| Holm positions, and each step rejects, since its interval lies below the smallest threshold alpha / m.
So every member of R is rejected under every assignment. The decisions outside R are not certified. The
certificate is computed for M = interrupted only and for M = all missing, for the primary family and for the
kappa = 3 replace family. A label "robust to the sub-fine residual" is certified only when its test is certified
in both. The kappa = 3 robustness labels (``s5p_robust_labels``, replace family) are
re-derived under each bound. Stopping: at every look (the controller's status files) the frozen rule
(``s5p_inference.sequential_decision``, its thresholds and min B) is re-applied with the draws missing by then, and
compared with the controller's decision. Power: bounds of each power fraction with the set's missing alternatives
(none detected / all detected). These power bounds CONDITION on the retained null calibration ensemble; the
effect of the null's own lost draws on power is not bounded (that would need per-alternative counts).

COMPLETENESS. The output is COMPLETE only if every null has a final status, every task log is finished, no seed is
unestablished, and every lane's completed seeds are exactly the seeds of the evaluator's own product selection
(``s5p_joint.product_files``: the design's globs, partials excluded). Otherwise the file is written with
``status: INCOMPLETE`` and its reasons, no certificate is marked certified, and the exit code is 4.
LOOKS are mapped to batches by the products, not by file order: look B follows batch count n iff the completed
products of batches < n sum to B. A wholly lost batch makes n ambiguous, and so does a status file overwritten at
an unchanged B; such looks are marked unresolved, and stopping is then not certifiable.

Reads the evaluator output, the design, the tables, the ledger, the status files and the task-log classification;
writes a SEPARATE file. MEASURES: how far the unobserved missing draws could move each decision. CANNOT AUTHORIZE:
a claim, a decision, a repair or any change of the frozen statistics or stopping rule; the primary result stands.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

import s5p_inference as si
import s5p_joint as sj
import s5p_robust_labels as rl

SIDES = rl.SIDES
SCENARIOS = ("worst_interrupted", "worst_all_missing", "best_all_missing")
TOKEN = re.compile(r"-(s5p_[a-z0-9_]+)$")


def label_of(table_stem: str) -> str:
    """The meter label of a frozen table: cal-GENIE_2_12_10_CV-b2 -> s5p_cal_genie_2_12_10_cv_b2; pow-P3_a1.0 -> s5p_pow_p3_a1p0."""
    return "s5p_" + table_stem.lower().replace("-", "_").replace(".", "p")


def read_tables(tables: Path) -> dict:
    """{label: {"lane", "kind", "batch", "rows": [(first, last, out, tag)]}} for every production table."""
    out = {}
    for t in sorted(tables.glob("*.tsv")):
        m = re.fullmatch(r"(cal)-(.+)-b(\d+)", t.stem) or re.fullmatch(r"(pow)-(.+)", t.stem)
        if not m:
            continue
        rows = []
        for line in t.read_text().splitlines():
            if line.startswith("#") or not line.strip():
                continue
            f = line.split("\t")
            a, b = re.search(r"--pseudo-seeds\t(\d+):(\d+)", line).groups()
            rows.append((int(a), int(b), f[f.index("--out") + 1], f[f.index("--tag") + 1]))
        out[label_of(t.stem)] = {"lane": m.group(2), "kind": m.group(1),
                                 "batch": int(m.group(3)) if m.group(1) == "cal" else 0, "rows": rows}
    return out


def submitted_labels(ledger: Path) -> set:
    labs = set()
    for line in ledger.read_text().splitlines():
        r = json.loads(line)
        if r.get("kind") == "job" and r.get("job_id") and (m := TOKEN.search(r.get("token", ""))):
            labs.add(m.group(1))
    return labs


def classify(tables: dict, submitted: set, seed_states: dict) -> dict:
    """{(kind, lane): {"by_batch": {b: {state: n}}, "seeds": {state: [seeds]}, "not_submitted_batches": [b]}}."""
    logged = {}
    for task in seed_states["tasks"]:
        for s, st in task["seeds"].items():
            logged[int(s)] = st["state"]
    out = defaultdict(lambda: {"by_batch": {}, "seeds": defaultdict(list), "not_submitted_batches": []})
    for lab, t in tables.items():
        rec = out[(t["kind"], t["lane"])]
        if lab not in submitted:
            rec["not_submitted_batches"].append(t["batch"])
            continue
        counts = defaultdict(int)
        for first, last, outdir, tag in t["rows"]:
            for s in range(first, last + 1):
                if Path(outdir, f"{tag}_s{s}.npz").exists():
                    st = "completed"
                elif logged.get(s) in ("interrupted", "never started"):
                    st = logged[s]
                else:
                    st = "unestablished"
                counts[st] += 1
                rec["seeds"][st].append(s)
        rec["by_batch"][t["batch"]] = dict(counts)
    return out


def missing(rec: dict, upto_batch: int | None = None) -> dict:
    """Missing draws of a lane, optionally only in batches < upto_batch."""
    n = defaultdict(int)
    for b, c in rec["by_batch"].items():
        if upto_batch is None or b < upto_batch:
            for st in ("interrupted", "never started", "unestablished"):
                n[st] += c.get(st, 0)
    return {"interrupted_or_unestablished": n["interrupted"] + n["unestablished"], "unestablished": n["unestablished"],
            "all": n["interrupted"] + n["never started"] + n["unestablished"]}


def shifted(c: dict, scenario: str, m: dict) -> dict:
    if c["B"] == 0:  # not calibrated: p = 1 in every family, nothing to move
        return dict(c)
    add_k, add_b = {"worst_interrupted": (m["interrupted_or_unestablished"], m["interrupted_or_unestablished"]),
                    "worst_all_missing": (m["all"], m["all"]),
                    "best_all_missing": (0, m["all"])}[scenario]
    k, b = int(c["k"]) + add_k, int(c["B"]) + add_b
    return {"p": (k + 1) / (b + 1), "k": k, "B": b}


def certificate(claims: dict, rejected: set, m_of: dict, which: str, alpha: float) -> dict:
    """The sufficient all-assignment certificate for the rejected set (see the module docstring)."""
    m = len(claims)
    th = alpha / m
    def mm(t):
        return m_of[t.split(":")[0]][which]
    worst = {t: shifted(c, "worst_all_missing", {"interrupted_or_unestablished": mm(t), "all": mm(t)}) for t, c in claims.items()}
    best = {t: shifted(c, "best_all_missing", {"interrupted_or_unestablished": mm(t), "all": mm(t)}) for t, c in claims.items()}
    if not rejected:
        return {"rejected_set": [], "certified": True, "note": "nothing rejected: nothing to certify"}
    upper = {t: si.cp_interval(int(worst[t]["k"]), int(worst[t]["B"]), 0.95)[1] for t in rejected}
    below = all(upper[t] < th for t in rejected)
    max_r = max(worst[t]["p"] for t in rejected)
    outside = [best[t]["p"] for t in claims if t not in rejected]
    sep = (not outside) or max_r < min(outside)
    return {"rejected_set": sorted(rejected), "missing_class": which, "alpha_over_m": th,
            "worst_cp_upper": upper, "all_below_alpha_over_m": below,
            "max_worst_p_in_R": max_r, "min_best_p_outside_R": min(outside) if outside else None,
            "separated": sep, "certified": bool(below and sep)}


def decisions(res: dict, design: dict, classes: dict, complete: bool = True) -> dict:
    alpha = float(design["alpha_family"])
    fam = rl.families(res)
    rl.derive(res, alpha)  # the leaves must reproduce the frozen evaluator's runs (refuses otherwise)
    m_of = {null: missing(classes[("cal", null)]) for null in res["tests"]}
    out = {"missing_draws": m_of, "primary": {t: res["decisions"][t]["decision"] for t in fam}, "scenarios": {}}
    for sc in SCENARIOS:
        prim = si.holm_determined({t: shifted(f["primary"], sc, m_of[t.split(":")[0]]) for t, f in fam.items()}, alpha)
        rep = si.holm_determined({t: shifted(f["replace"], sc, m_of[t.split(":")[0]]) for t, f in fam.items()}, alpha)
        out["scenarios"][sc] = {
            "claims": {t: {k: prim[t][k] for k in ("p", "k", "B", "decision")} for t in fam},
            "survives": {t: prim[t]["decision"] == res["decisions"][t]["decision"] for t in fam},
            "robust_labels": rl.labels(prim, rep), "extremal": "not proven (descriptive corner)"}
    rep0 = si.holm_determined({t: f["replace"] for t, f in fam.items()}, alpha)
    rej_p = {t for t, d in res["decisions"].items() if d["decision"] == "rejected"}
    rej_r = {t for t, d in rep0.items() if d["decision"] == "rejected"}
    out["certificates"] = {}
    for which in ("interrupted_or_unestablished", "all"):
        cp_ = certificate({t: f["primary"] for t, f in fam.items()}, rej_p, m_of, which, alpha)
        cr_ = certificate({t: f["replace"] for t, f in fam.items()}, rej_r, m_of, which, alpha)
        if not complete:
            for c in (cp_, cr_):
                c["certified"] = False
                c["note"] = "not certifiable: the output is INCOMPLETE (see status)"
        out["certificates"][which] = {
            "primary": cp_, "kappa3_replace": cr_,
            "certified_rejections": sorted(rej_p) if cp_["certified"] else [],
            "certified_robust_labels": sorted(rej_p & rej_r) if (cp_["certified"] and cr_["certified"]) else []}
    # per-test status: a corner is an explicit, realizable assignment (all missing draws exceed / none does), so a
    # corner that changes a decision is a counterexample; otherwise, without a certificate, survival is unestablished
    status = {}
    for t, d in res["decisions"].items():
        flips = [sc for sc in ("worst_interrupted", "worst_all_missing", "best_all_missing")
                 if not out["scenarios"][sc]["survives"][t]]
        cert_all = t in out["certificates"]["all"]["certified_rejections"]
        cert_int = t in out["certificates"]["interrupted_or_unestablished"]["certified_rejections"]
        if flips:
            status[t] = f"can change (counterexample: {', '.join(flips)})"
        elif d["decision"] == "rejected" and cert_all:
            status[t] = "certified under all missing-outcome assignments (all missing)"
        elif d["decision"] == "rejected" and cert_int:
            status[t] = ("certified for the interrupted and unestablished draws only; survival under all "
                         "missing-outcome assignments is unestablished")
        else:
            status[t] = "not certified: survival under all missing-outcome assignments is unestablished"
    out["per_test_status"] = status
    return out


def look_batches(rec: dict, b_look: int) -> list:
    """Every batch count n whose completed products (batches < n) sum to the look's B."""
    done = [rec["by_batch"].get(b, {}).get("completed", 0) for b in range(max(rec["by_batch"], default=-1) + 1)]
    return [n for n in range(len(done) + 1) if sum(done[:n]) == b_look]


def looks(design: dict, classes: dict, alpha: float) -> dict:
    m = 2 * len(design["nulls"])
    th = sorted(set(si.holm_thresholds(alpha, m)) | {0.01, 0.05})
    out = {}
    for null, spec in design["nulls"].items():
        sdir = Path(spec["calibration_n"]["sequential_status"]).parent
        files = sorted(sdir.glob(f"{null}-B*.json"), key=lambda p: int(re.search(r"-B(\d+)\.json$", p.name).group(1)))
        min_b = int(spec["calibration_n"].get("min", 0))
        rec = classes[("cal", null)]
        rows, resolved = [], True
        for f in files:
            st = json.loads(f.read_text())
            ns = look_batches(rec, int(st["B"]))
            row = {"status": f.name, "B": st["B"], "controller_stop": st.get("stop"), "reason": st.get("reason"),
                   "batches_before_look": ns[0] if len(ns) == 1 else None}
            if len(ns) != 1:
                row["batch_mapping"] = f"unresolved (candidate batch counts {ns}): a wholly lost batch or an overwritten same-B status"
                resolved = False
            elif "decisions" in st:
                mi = missing(rec, upto_batch=ns[0])
                for sc in SCENARIOS:
                    dec = {s: si.sequential_decision(*(lambda c: (c["k"], c["B"]))(shifted(st["decisions"][s], sc, mi)), th)
                           for s in SIDES}
                    b_sc = shifted(st["decisions"]["total"], sc, mi)["B"]
                    row[sc] = {"missing_by_look": mi, "rule_stops": all(d["stop"] for d in dec.values()) and b_sc >= min_b}
            rows.append(row)
        out[null] = {"min_B": min_b, "looks": rows, "all_looks_mapped": resolved,
                     "note": "re-applied rule under each corner; descriptive (not proven extremal)"}
    return out


def power_bounds(res: dict, classes: dict) -> dict:
    out = {}
    for key, entry in res.get("power", {}).items():
        if key == "levels" or not isinstance(entry, dict) or "not_evaluated" in entry:
            continue
        mi = missing(classes[("pow", key)])["all"]
        sides = {}
        for s in SIDES:
            lv = {}
            for level, v in entry.get(s, {}).items():
                one = {}
                for rule in ("unshifted", "claim_rule", "claim_rule_determined"):
                    n, pw = int(v[rule]["n"]), float(v[rule]["power"])
                    x = round(pw * n)
                    one[rule] = {"power": pw, "n": n, "missing": mi, "lower_none_detected": x / (n + mi),
                                 "upper_all_detected": (x + mi) / (n + mi),
                                 "conditions_on": "the retained null calibration ensemble (its own lost draws not bounded)"}
                lv[level] = one
            sides[s] = lv
        out[key] = sides
    return out


def seed_of(path: str) -> int:
    return int(re.search(r"_s(\d+)\.npz$", path).group(1))


def check_identity(res: dict, design: dict, classes: dict) -> list:
    """Completed seeds must be exactly the seeds of the evaluator's product selection and match its B / n. A mismatch
    refuses (the classification would not describe the evaluated ensemble)."""
    for null, e in res["tests"].items():
        done = set(classes[("cal", null)]["seeds"]["completed"])
        sel = {seed_of(p) for p in sj.product_files(design["nulls"][null]["calibration_glob"])}
        b = 0 if "not_calibrated" in e else int(e["total"]["B"])
        if done != sel or len(sel) != b:
            raise SystemExit(f"{null}: classified completed {len(done)}, evaluator selection {len(sel)}, B = {b}; "
                             f"seeds only classified {sorted(done - sel)[:5]}, only selected {sorted(sel - done)[:5]}")
    for key, entry in res.get("power", {}).items():
        if key == "levels" or not isinstance(entry, dict):
            continue
        done = set(classes[("pow", key)]["seeds"]["completed"])
        sel = {seed_of(p) for p in sj.product_files(design["power"][key]["glob"])}
        if done != sel or len(sel) != int(entry["n"]):
            raise SystemExit(f"power {key}: classified completed {len(done)}, selection {len(sel)}, n = {entry['n']}")
    return []


def completeness(design: dict, classes: dict, seed_states: dict) -> list:
    reasons = []
    for null, spec in design["nulls"].items():
        if not Path(spec["calibration_n"]["sequential_status"]).exists():
            reasons.append(f"{null}: no final status (production not terminal)")
    if int(seed_states.get("tasks_unfinished_skipped", 0)) != 0:
        reasons.append(f"{seed_states['tasks_unfinished_skipped']} task logs unfinished (tasks still running)")
    for (kind, lane), r in sorted(classes.items()):
        u = len(r["seeds"].get("unestablished", []))
        if u:
            reasons.append(f"{kind}:{lane}: {u} unestablished seeds")
    return reasons


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--evaluate", type=Path, required=True)
    ap.add_argument("--design", type=Path, required=True)
    ap.add_argument("--tables", type=Path, required=True)
    ap.add_argument("--ledger", type=Path, required=True)
    ap.add_argument("--seed-states", type=Path, required=True, help="s5p_lost_seed_runtime_diagnostic.py output")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    raw, draw = a.evaluate.read_bytes(), a.design.read_bytes()
    res, design = json.loads(raw), json.loads(draw)
    if res.get("design_sha256") != hashlib.sha256(draw).hexdigest():
        raise SystemExit("the evaluator output was not produced with this design")
    seed_states = json.loads(a.seed_states.read_text())
    classes = classify(read_tables(a.tables), submitted_labels(a.ledger), seed_states)
    check_identity(res, design, classes)
    reasons = completeness(design, classes, seed_states)
    alpha = float(design["alpha_family"])
    out = {"schema": "s5p-missing-sensitivity/1",
           "label": "LABELLED SENSITIVITY (report only): bounds on the unobserved missing draws; the primary decisions stand",
           "status": "COMPLETE" if not reasons else "INCOMPLETE", "incomplete_reasons": reasons,
           "evaluate_sha256": hashlib.sha256(raw).hexdigest(), "design_sha256": res["design_sha256"],
           "seed_states_sha256": hashlib.sha256(a.seed_states.read_bytes()).hexdigest(),
           "ledger_sha256": hashlib.sha256(a.ledger.read_bytes()).hexdigest(),
           "code_sha256": hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest(),
           "classification": {f"{k}:{lane}": {"by_batch": r["by_batch"], "not_submitted_batches": sorted(r["not_submitted_batches"]),
                                              "counts": {s: len(v) for s, v in r["seeds"].items()},
                                              "missing_seeds": {s: sorted(v) for s, v in r["seeds"].items() if s != "completed"}}
                              for (k, lane), r in sorted(classes.items())},
           "decisions": decisions(res, design, classes, complete=not reasons),
           "stopping": looks(design, classes, alpha),
           "power": power_bounds(res, classes)}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    surv = {sc: out["decisions"]["scenarios"][sc]["survives"] for sc in SCENARIOS}
    cert = {w: {"primary_certified": c["primary"]["certified"], "certified_rejections": c["certified_rejections"]}
            for w, c in out["decisions"]["certificates"].items()}
    print(json.dumps({"status": out["status"], "incomplete_reasons": reasons, "primary": out["decisions"]["primary"],
                      "survives_descriptive": surv, "certificates": cert}, indent=1))
    return 0 if not reasons else 4


if __name__ == "__main__":
    raise SystemExit(main())
