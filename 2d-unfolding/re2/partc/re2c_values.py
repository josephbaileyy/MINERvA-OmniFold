#!/usr/bin/env python3
"""RE-2 part C: the regenerated value of every printed number that derives from E_U or Q (RE2-DECLARATION-C.md §6).

    python3 -I re2c_values.py --repo REPO --spec re2c_values_spec.tsv --out-tsv T.tsv --out-json T.json \\
        [--refined-dir PARTC_OUT]

Each row of the spec names a printed site, the characters printed there, the committed purity source the value was
copied from, a path into it, a transform and a format. For every row, in this order:
  1. anchor: the printed characters must occur on the cited line (a values.tex macro must be defined exactly once,
     with exactly that value);
  2. positive control: format(transform(purity value)) must equal the printed characters;
  3. regenerated value: the same path, transform and format on the refined source, written beside the printed one.
A row whose anchor or control fails gets no regenerated value: its definition is not established, so a new number
from it would be unverified. It is listed with the reason. A row may declare `expect` = fails (a definition already
known not to reproduce, e.g. a number with no producer); any row whose outcome differs from its declaration, either
way, makes the run exit 3, so a broken row cannot pass unnoticed and a known gap cannot silently close. Rows with an empty `where` are new products (Q_R + C_model, E_R - E_U in Q_R's
sigma): no control applies and they are labelled new.

A `source` or `path` of the form "A || B" uses A for the purity control and B for the refined value, where the two
arms' records differ in layout (e.g. RE-1's committed numbers.json against this part's re2c_numbers.py output).

Without --refined-dir only steps 1 and 2 run (the purity dry run). Nothing here edits a .tex file: the table is the
input of the integration step, and printed wording is Joseph's (DECISION-20261024 item 3).
"""
import argparse
import csv
import gzip
import json
import math
import re
import sys
from pathlib import Path

N = "docs/analysis-note"
S = "docs/orchestration/state/2d-closeout"
R42 = "docs/orchestration/receipts/2d-lgbm42-20261011"
# purity sources (committed, relative to the repo) and the refined arm's outputs (relative to --refined-dir)
SOURCES = {
    "budget_Q": (f"{S}/stageF/rebuild/outputs/outA/budget_Q.json.gz", "outA/budget_Q.json"),
    "s5_json": (f"{S}/stageC/production/evidence/production/results/s5.json", "s5/s5.json"),
    "combination_json": (f"{S}/playlist-term/outputs/combination/combination.json", "combination/combination.json"),
    "playlist_term_json": (f"{S}/playlist-term/outputs/playlist_term.json", "playlist/playlist_term.json"),
    "analysis_json": (f"{S}/period-unfold-20261014/outputs/analysis.json", "periods/analysis.json"),
    "chi2_Q_std": (f"{S}/stageF/rebuild/outputs/chi2/chi2_Q_std.txt", "chi2/chi2_Q_std.txt"),
    "chi2_Q_lognormal": (f"{S}/stageF/rebuild/outputs/chi2/chi2_Q_lognormal.txt", "chi2/chi2_Q_lognormal.txt"),
    "chi2_Q_substat": (f"{S}/stageF/rebuild/outputs/chi2/chi2_Q_substat.txt", "chi2/chi2_Q_substat.txt"),
    "ours_only_Q": (f"{S}/stageF/rebuild/outputs/chi2/ours_only_Q.txt", "chi2/ours_only_Q.txt"),
    "ours_only_universe": (f"{S}/stageF/rebuild/outputs/chi2/ours_only_universe.txt", "chi2/ours_only_universe.txt"),
    "ours_only_universe_plus_stat": (f"{S}/stageF/rebuild/outputs/chi2/ours_only_universe_plus_stat.txt",
                                     "chi2/ours_only_universe_plus_stat.txt"),
    "chi2_paper": (f"{R42}/chi2_lgbm42_paperonly.txt", "receipts/chi2_paperonly.txt"),
    "agreement": (f"{R42}/RECEIPT-2d-agreement-windows-lgbm42-20261011.json", "receipts/RECEIPT-agreement-windows.json"),
    "tension_report": (f"{R42}/tension_report.txt", "receipts/figs/tension_report.txt"),
    "model_comp_report": (f"{R42}/model_comp_report.txt", "receipts/figs/model_comp_report.txt"),
    "tune_log": (f"{R42}/tune.log", "receipts/tune.log"),
    "lgbm_metrics": (f"{R42}/lgbm_central_metrics.out", None),
    "re1_numbers": (f"{S}/stageF/methods/re1/run2/f/numbers.json", None),   # purity only: the refined value is re2c_numbers.py's
    "re1_extras": (f"{S}/stageF/methods/re1/run2/readouts/report2_extras.json", None),   # purity only
    "cmodel": (None, "cmodel/cmodel_R.json"),
    "partc_numbers": (None, "partc_numbers.json"),
}
MACRO = re.compile(r"\\newcommand\{\\(\w+)\}\{([^}]*)\}")


def load(path):
    p = Path(path)
    if p.suffix == ".gz":
        return json.loads(gzip.open(p, "rt").read())
    if p.suffix == ".json":
        return json.loads(p.read_text())
    return p.read_text()


REDUCE = re.compile(r"^(min|max|maxabs)(\d*)\((.*)\)$", re.S)


def extract(doc, path):
    """A dotted path into JSON (integer parts index lists), or a one-group regex on text.

    `min(P)`, `max(P)`, `maxabs(P)` reduce over every match: P is a JSON path whose `*` part ranges over a list's
    items or a dict's values (`*-a,b` leaves out the keys a and b; None values are skipped), or a regex found on
    every text line. A count after the name (`max30(...)`) requires exactly that many matches, so a changed
    layout cannot be reduced silently over the wrong set."""
    m = REDUCE.match(path.strip())
    if m:
        fn, n, inner = m.group(1), m.group(2), m.group(3)
        vals = [float(v) for v in (re.findall(inner, doc, re.MULTILINE) if isinstance(doc, str)
                                   else _walk(doc, inner.split("."))) if v is not None]
        if not vals or (n and len(vals) != int(n)):
            raise KeyError(f"{path!r}: {len(vals)} matches" + (f", {n} required" if n else ""))
        return {"min": min, "max": max, "maxabs": lambda xs: max(abs(x) for x in xs)}[fn](vals)
    if isinstance(doc, str):
        m = re.search(path, doc, re.MULTILINE)
        if not m:
            raise KeyError(f"regex {path!r} does not match")
        return float(m.group(1))
    v = doc
    for part in path.split("."):
        if isinstance(v, list):
            v = v[int(part)]
        elif part in v:
            v = v[part]
        else:
            raise KeyError(f"no key {part!r} in path {path!r}")
    return float(v)


def _walk(v, parts):
    if not parts:
        return [v]
    head, rest = parts[0], parts[1:]
    if head.startswith("*"):
        skip = set(head[2:].split(",")) if head.startswith("*-") else set()
        items = v if isinstance(v, list) else [x for k, x in v.items() if k not in skip]
        return [y for x in items for y in _walk(x, rest)]
    if isinstance(v, list):
        return _walk(v[int(head)], rest)
    if head not in v:
        raise KeyError(f"no key {head!r}")
    return _walk(v[head], rest)


def render(v, transform, fmt):
    t = eval(transform, {"__builtins__": {}}, {"v": v, "abs": abs, "min": min, "max": max, "round": round,
                                                 "sqrt": math.sqrt})
    if fmt == "d":
        return str(int(round(t)))
    return format(t, fmt)


def arm_of(field, arm):
    """'A || B' -> A (purity) or B (refined); a plain field serves both arms."""
    parts = [x.strip() for x in field.split("||")]
    if len(parts) == 1:
        return parts[0]
    if len(parts) != 2:
        raise ValueError(f"{field!r}: at most one '||'")
    return parts[0] if arm == "purity" else parts[1]


def anchor(repo, where, printed, macros):
    """True if the printed characters are at `where` (file:line, or values.tex:\\macro)."""
    if not where:
        return True, "new product: no printed site"
    f, _, loc = where.rpartition(":")
    if loc.startswith("\\"):
        vals = macros.get(loc[1:], [])
        if len(vals) != 1:
            return False, f"macro {loc} defined {len(vals)} times"
        return vals[0] == printed, f"macro {loc} = {vals[0]!r}"
    lines = (Path(repo) / f.replace("N/", N + "/", 1)).read_text().splitlines()
    ln = int(loc)
    if not 1 <= ln <= len(lines):
        return False, f"line {ln} outside {f}"
    return printed in lines[ln - 1], lines[ln - 1].strip()[:160]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--refined-dir")
    ap.add_argument("--out-tsv", required=True)
    ap.add_argument("--out-json", required=True)
    a = ap.parse_args(argv)
    repo = Path(a.repo)
    macros = {}
    for name, val in MACRO.findall((repo / N / "values.tex").read_text()):
        macros.setdefault(name, []).append(val)
    rows = list(csv.DictReader(open(a.spec), delimiter="\t"))
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit(f"duplicate ids: {sorted({i for i in ids if ids.count(i) > 1})}")
    cache = {}

    def doc(key, arm):
        k = (key, arm)
        if k not in cache:
            purity, refined = SOURCES[key]
            rel = purity if arm == "purity" else refined
            if rel is None:
                raise KeyError(f"source {key} has no {arm} file")
            cache[k] = load((repo / rel) if arm == "purity" else (Path(a.refined_dir) / rel))
        return cache[k]

    out, bad = [], 0
    for r in rows:
        rec = {k: r[k] for k in ("id", "where", "printed", "source", "group", "note")}
        rec["anchor_ok"], rec["anchor"] = anchor(repo, r["where"], r["printed"], macros)
        new_product = not r["where"]
        try:
            if new_product:
                rec["purity_value"], rec["control_ok"] = None, None
            else:
                v = extract(doc(arm_of(r["source"], "purity"), "purity"), arm_of(r["path"], "purity"))
                rec["purity_value"] = v
                rec["purity_rendered"] = render(v, r["transform"], r["fmt"])
                rec["control_ok"] = rec["purity_rendered"] == r["printed"]
        except (KeyError, ValueError, OSError, IndexError) as e:
            rec["purity_value"], rec["control_ok"], rec["control_error"] = None, False, str(e)
        ok = rec["anchor_ok"] and (new_product or rec["control_ok"])
        rec["expect"] = r.get("expect") or "pass"
        if ok != (rec["expect"] == "pass"):
            bad += 1
            rec["unexpected"] = True
        rec["status"] = "new product" if new_product else ("control PASS" if ok else "CONTROL FAILS: not regenerated")
        if a.refined_dir and ok:
            try:
                v = extract(doc(arm_of(r["source"], "refined"), "refined"), arm_of(r["path"], "refined"))
                rec["refined_value"] = v
                rec["refined_rendered"] = render(v, r["transform"], r["fmt"])
                rec["changes_at_printed_precision"] = None if new_product else rec["refined_rendered"] != r["printed"]
            except (KeyError, ValueError, OSError, IndexError) as e:
                rec["refined_error"] = str(e)
                bad += 1
        out.append(rec)
    cols = ["id", "where", "printed", "refined_rendered", "changes_at_printed_precision", "status", "expect", "group",
            "source", "purity_value", "refined_value", "note"]
    with open(a.out_tsv, "w") as f:
        f.write("\t".join(cols) + "\n")
        for rec in out:
            f.write("\t".join("" if rec.get(c) is None else str(rec.get(c)) for c in cols) + "\n")
    summary = {"rows": len(out), "unexpected": bad,
               "control_pass": sum(r["status"] == "control PASS" for r in out),
               "new_products": sum(r["status"] == "new product" for r in out),
               "changes": sum(bool(r.get("changes_at_printed_precision")) for r in out) if a.refined_dir else None,
               "refined": bool(a.refined_dir)}
    summary["declared_fails"] = sum(r["expect"] == "fails" for r in out)
    json.dump({"summary": summary, "rows": out}, open(a.out_json, "w"), indent=1)
    print(json.dumps(summary))
    for rec in out:
        if rec.get("unexpected") or rec.get("refined_error"):
            print("UNEXPECTED", rec["id"], rec["where"], rec["status"], rec.get("control_error") or
                  rec.get("purity_rendered"), rec.get("anchor") if not rec["anchor_ok"] else "",
                  rec.get("refined_error", ""))
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
