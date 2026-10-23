#!/usr/bin/env python3
"""Build, and check, the results index from the committed receipts.

    results_index.py --write [--repo DIR]   # regenerate the index, the population table and the two .tex renderings
    results_index.py --check [--repo DIR]   # exit 1 if any committed generated file differs from a fresh generation
                                            # or a population receipt has no index row (pre-commit)
    results_index.py --summary [--repo DIR] # print the population counts
    results_index.py --population           # print every in-root JSON with its class
    results_index.py --self-test            # discovery in both directions on a throwaway repository (pre-commit)

THE POPULATION, DECLARED BY RULE (not by a list of globs someone picked). A file is a RESULTS RECEIPT iff
  R1 it is in the git index (tracked or staged), and
  R2 its path is under one of ROOTS and ends in .json, and
  R3 it parses as JSON, and
  R4 somewhere in it a key whose lower-cased name FULLY matches one regex of METRIC_FAMILIES holds a number,
     a non-empty list of numbers, or an object all of whose leaves are numbers or lists of numbers.
Every R2 file is classified `included` (R3 and R4 hold), `excluded-no-metric` (R3 holds, R4 does not: a
contract, a budget, a launch receipt, a design file) or `excluded-unparseable` (R3 fails). RESULTS-POPULATION.tsv
commits the included ones; --population prints all three classes, and every run prints their counts and the
count of tracked .json OUTSIDE the roots (never read), per top-level directory and for *receipt*.json names, so
the exclusion is visible without being a committed number that goes stale on every unrelated JSON file.

Each R4 hit is one index row. Columns, each derived mechanically:
  estimator  ATTRIBUTION.tsv's first row whose path_regex and keypath_regex match (each row cites a line that
             carries its quote); else UNATTRIBUTED. The index never guesses an estimator.
  point      the key path above the metric key (the test truth / point / functional the value belongs to).
  scale      the receipt's own top-level `stage` string if it has one, else the first SCALE_WORDS token of its
             path, else `unstated`.
  n          the nearest N_KEYS number in the metric's own object or an enclosing one, with the key named.
  metric     the METRIC_FAMILIES family; key, the metric's own key.
  value      the number (6 significant digits; the receipt holds the full value), or a list summary.
  status     `withdrawn`/`superseded` if the receipt's file name says so, or its top-level `status` string
             does, or a STATUS.tsv row (citing a line carrying its quote) matches; else `unreviewed` --
             which means no record in the registry withdraws or supersedes it, NOT that it is current.
  self_status  the receipt's own top-level `status` string, verbatim (first 100 characters).
  source, keypath  where to read the value.
Nothing is ever deleted: a superseded or withdrawn receipt keeps its rows and gains a status.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reglib  # noqa: E402

ROOTS = ("docs/orchestration/state/", "docs/orchestration/receipts/", "docs/orchestration/runs/")
INDEX_TSV = f"{reglib.REGISTRY_DIR}/RESULTS-INDEX.tsv"
POP_TSV = f"{reglib.REGISTRY_DIR}/RESULTS-POPULATION.tsv"
TEX_INDEX = "docs/analysis-note/records_results_index.tex"
TEX_REGISTRY = "docs/analysis-note/records_estimators.tex"
GENERATED = (INDEX_TSV, POP_TSV, TEX_INDEX, TEX_REGISTRY)

# The metric families. A key must match one of these regexes IN FULL (re.fullmatch, lower-cased key).
METRIC_FAMILIES = (
    ("coverage68", r"(pooled_|min_|max_|median_|mean_)?cov(erage)?_?68"),
    ("coverage95", r"(pooled_|min_|max_|median_|mean_)?cov(erage)?_?95"),
    ("coverage", r"(pooled_|true_|empirical_|observed_)?coverage(_[a-z0-9.]+)*"),
    ("pull_sd", r"(pooled_|se_)?pull_(sd|rms|std)(_median|_min|_max)?|pullrms"),
    ("pull_mean", r"mean_pull|pull_mean|pullmean"),
    ("max_abs_pull", r"max_abs_pull(_used)?|pull_max_abs"),
    ("bias", r"(median_abs_|mean_abs_|max_abs_|total_)?bias(_pct|_pc|_pb|_rel)?"),
    ("closure", r"closure_max_abs_c_minus_1|closure_ratio|closure_chi2"),
    ("residual", r"(median_|mean_|max_)?(abs_)?residual(_median|_pct|_max)?|m_residual|worst_residual|best_residual"),
)
_FAM = [(name, re.compile(rx)) for name, rx in METRIC_FAMILIES]
N_KEYS = ("n", "n_experiments", "n_exp", "n_pseudo", "n_pe", "n_pseudo_experiments", "n_nominal_experiments",
          "n_members", "N")
SCALE_WORDS = (("development", ("dev", "development")), ("assessment", ("assess", "assessment")),
               ("production", ("prod", "production")), ("pilot", ("pilot",)), ("interim", ("interim",)))
# A file name carrying the word as a whole token, or a top-level `status` string that BEGINS with it ("SUPERSEDED
# by ...", "WITHDRAWN: ..."); "supersedes X" or "not superseded" do not match.
STATUS_WORDS = (("withdrawn", re.compile(r"(^|[-_.])withdrawn([-_.]|$)", re.I), re.compile(r"^\W*withdrawn\b", re.I)),
                ("superseded", re.compile(r"(^|[-_.])superseded([-_.]|$)", re.I), re.compile(r"^\W*superseded\b", re.I)))
# Short names the ambiguity table resolves with whatis.py's rule (reglib.resolve). The list only chooses what is
# printed; each verdict is computed from the registry, never typed.
PROBE_NAMES = ("R", "B0", "N", "F1", "F2", "configuration 1", "configuration 2", "configuration 3", "400/31",
               "400 trees, 31 leaves", "negweight-refined", "joint-test estimator", "exact-split", "lgbm")
INDEX_COLUMNS = ("estimator", "point", "scale", "n", "metric", "key", "value", "status", "superseding",
                 "self_status", "source", "keypath")


def family(key: str) -> str | None:
    k = str(key).lower()
    for name, rx in _FAM:
        if rx.fullmatch(k):
            return name
    return None


def isnum(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def numeric_leaves(o, path=()):
    """(subpath, value) for every leaf of `o` if ALL its leaves are numbers or non-empty number lists, else None."""
    if isnum(o) or (isinstance(o, list) and o and all(isnum(v) for v in o)):
        return [(path, o)]
    if isinstance(o, dict) and o:
        out = []
        for k, v in o.items():
            sub = numeric_leaves(v, path + (str(k),))
            if sub is None:
                return None
            out += sub
        return out
    return None


def fmt(v) -> str:
    if isinstance(v, list):
        vals = [float(x) for x in v]
        return (f"list[{len(vals)}] min={min(vals):.6g} median={statistics.median(vals):.6g} "
                f"max={max(vals):.6g}")
    if isinstance(v, int):
        return str(v)
    return f"{v:.6g}"


def find_n(stack: list[dict]) -> str:
    for d in reversed(stack):
        for k in N_KEYS:
            if k in d and isnum(d[k]):
                return f"{d[k]} ({k})"
    return ""


def scale_of(doc, path: str) -> str:
    if isinstance(doc, dict) and isinstance(doc.get("stage"), str):
        return doc["stage"]
    tokens = re.split(r"[/_.\-]", path.lower())
    for word, keys in SCALE_WORDS:
        if any(t in keys for t in tokens):
            return word
    return "unstated"


def hits(doc):
    """(keypath tuple, metric key, family, value, enclosing-object stack) for every R4 hit."""
    out = []

    def walk(o, path, stack):
        if isinstance(o, dict):
            stack = stack + [o]
            for k, v in o.items():
                fam = family(k)
                if fam:
                    leaves = numeric_leaves(v)
                    if leaves is not None:
                        for sub, val in leaves:
                            out.append((path + (str(k),) + sub, str(k), fam, val, stack))
                        continue
                walk(v, path + (str(k),), stack)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, path + (str(i),), stack)

    walk(doc, (), [])
    return out


def load_rules(index: reglib.Index, path: str, kind: str) -> tuple[list[dict], list[str]]:
    rows, errs = [], []
    for n, r in enumerate(reglib.read_tsv(index, path), start=2):
        why = reglib.verify_citation(index, r["source"], r["line"], r["quote"])
        if why:
            errs.append(f"{kind} row {n}: {why}")
        try:
            r["_p"] = re.compile(r["path_regex"])
            r["_k"] = re.compile(r["keypath_regex"])
        except re.error as exc:
            errs.append(f"{kind} row {n}: regex does not compile: {exc}")
            continue
        rows.append(r)
    return rows, errs


def generate(repo: Path) -> tuple[dict[str, str], list[str], dict]:
    """The four generated files' bytes (as text), the registry/rule errors, and population counts."""
    index = reglib.Index(repo)
    errs = reglib.verify_registry(index)
    attrib, e1 = load_rules(index, reglib.ATTRIBUTION, "ATTRIBUTION")
    status_rules, e2 = load_rules(index, reglib.STATUS, "STATUS")
    errs += e1 + e2
    est_ids = {e["id"] for e in reglib.read_tsv(index, reglib.ESTIMATORS)}
    for r in attrib:
        if r["estimator"] not in est_ids:
            errs.append(f"ATTRIBUTION: estimator {r['estimator']!r} is not an ESTIMATORS id")
    for r in status_rules:
        if r["status"] not in ("withdrawn", "superseded"):
            errs.append(f"STATUS: status {r['status']!r} is not withdrawn/superseded")

    all_json = [p for p in index.paths() if p.endswith(".json")]
    in_roots = [p for p in all_json if p.startswith(ROOTS)]
    outside = [p for p in all_json if not p.startswith(ROOTS)]
    blobs = index.read_many(in_roots)
    pop_rows, rows = [], []
    for path in in_roots:
        try:
            doc = json.loads(blobs[path].decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            pop_rows.append((path, "excluded-unparseable", "0", type(exc).__name__))
            continue
        found = hits(doc)
        if not found:
            pop_rows.append((path, "excluded-no-metric", "0", ""))
            continue
        pop_rows.append((path, "included", str(len(found)), ""))
        self_status = doc.get("status") if isinstance(doc, dict) and isinstance(doc.get("status"), str) else ""
        base_status, base_by = "unreviewed", ""
        fname = path.rsplit("/", 1)[-1]
        for word, rx_name, rx_status in STATUS_WORDS:
            if rx_name.search(fname):
                base_status, base_by = word, "file name"
                break
            if self_status and rx_status.search(self_status):
                base_status, base_by = word, "receipt's own status field"
                break
        scale = scale_of(doc, path)
        for kp, key, fam, val, stack in found:
            keypath = "/".join(kp)
            est = next((r["estimator"] for r in attrib if r["_p"].fullmatch(path) and r["_k"].match(keypath)),
                       "UNATTRIBUTED")
            st, by = base_status, base_by
            for r in status_rules:
                if r["_p"].fullmatch(path) and r["_k"].match(keypath):
                    st, by = r["status"], f"{r['superseding_record']} ({r['source']}:{r['line']})"
                    break
            rows.append((est, "/".join(kp[:-1]) if len(kp) > 1 else "(top)", scale, find_n(stack), fam, key,
                         fmt(val), st, by, self_status[:100].replace("\t", " ").replace("\n", " "), path, keypath))
    rows.sort(key=lambda r: (r[0] == "UNATTRIBUTED", r[0], r[10], r[11]))
    counts = {
        "roots": len(in_roots), "outside": len(outside),
        "included": sum(1 for r in pop_rows if r[1] == "included"),
        "excluded-no-metric": sum(1 for r in pop_rows if r[1] == "excluded-no-metric"),
        "excluded-unparseable": sum(1 for r in pop_rows if r[1] == "excluded-unparseable"),
        "rows": len(rows), "attributed_rows": sum(1 for r in rows if r[0] != "UNATTRIBUTED"),
        "outside_by_top": Counter(p.split("/", 1)[0] if "/" in p else "." for p in outside),
        "outside_receipts_by_top": Counter(p.split("/", 1)[0] if "/" in p else "." for p in outside
                                           if "receipt" in p.rsplit("/", 1)[-1].lower()),
        "status": Counter(r[7] for r in rows),
    }

    def clean(s: str) -> str:
        return str(s).replace("\t", " ").replace("\n", " ")

    idx_text = "\t".join(INDEX_COLUMNS) + "\n" + "".join("\t".join(clean(c) for c in r) + "\n" for r in rows)
    # Only INCLUDED receipts are committed. Excluded files and the out-of-root counts are printed at run time
    # (--summary, --check, --population), never stored: a committed count of non-result JSON would go stale on
    # every new budget or contract file anywhere in the repository and fail commits that touch no result.
    head = ["# GENERATED by tools/registry/results_index.py --write; do not edit. Population rule: its docstring.",
            f"# roots: {', '.join(ROOTS)}. One row per INCLUDED receipt; `results_index.py --population` lists the"
            " excluded ones."]
    pop_text = ("\n".join(head) + "\npath\tclass\trows\tnote\n"
                + "".join("\t".join(r) + "\n" for r in pop_rows if r[1] == "included"))
    counts["_pop_rows"] = pop_rows
    files = {INDEX_TSV: idx_text, POP_TSV: pop_text,
             TEX_INDEX: render_index_tex(rows, counts, index), TEX_REGISTRY: render_registry_tex(index)}
    return files, errs, counts


def render_registry_tex(index: reglib.Index) -> str:
    T, B = reglib.tex_escape, reglib.tex_breakable
    ests = reglib.read_tsv(index, reglib.ESTIMATORS)
    als = reglib.read_tsv(index, reglib.ALIASES)
    out = ["% GENERATED by tools/registry/results_index.py --write from docs/orchestration/registry/ESTIMATORS.tsv",
           "% and ALIASES.tsv; do not edit. Every row cites a line that carries its quote (checked on every commit).",
           r"\begingroup\scriptsize\setlength{\LTleft}{0pt}\setlength{\LTright}{0pt}",
           r"\begin{longtable}{@{}p{0.17\textwidth}p{0.47\textwidth}p{0.30\textwidth}@{}}",
           r"\caption{Estimator registry: every configuration the records, note, primer and paper print, and every"
           r" one a scalar campaign contract defines.}\label{tab:rix-estimators}\\",
           r"\toprule Id & Definition & Defining record (file:line) \\ \midrule\endfirsthead",
           r"\toprule Id & Definition & Defining record (file:line) \\ \midrule\endhead"]
    for e in ests:
        out.append(f"\\texttt{{{B(e['id'])}}} & {T(e['summary'])}. Code: {B(e['code_path'])}. Used for: "
                   f"{T(e['used_for'])}. & \\texttt{{{B(e['defining_source'])}:{T(e['defining_line'])}}} \\\\")
    out += [r"\bottomrule", r"\end{longtable}",
            r"\begin{longtable}{@{}p{0.15\textwidth}p{0.10\textwidth}p{0.27\textwidth}p{0.42\textwidth}@{}}",
            r"\caption{Every alias of each registered estimator, with the line it is read from. A name listed under"
            r" two estimators is ambiguous on its own (Sec.~\ref{sec:rix-ambiguities}).}\label{tab:rix-aliases}\\",
            r"\toprule Estimator & Kind & Alias & Source (file:line) \\ \midrule\endfirsthead",
            r"\toprule Estimator & Kind & Alias & Source (file:line) \\ \midrule\endhead"]
    for a in als:
        out.append(f"\\texttt{{{B(a['estimator'])}}} & {T(a['kind'])} & {T(a['alias'])} & "
                   f"\\texttt{{{B(a['source'])}:{T(a['line'])}}} \\\\")
    out += [r"\bottomrule", r"\end{longtable}", r"\endgroup", ""]
    out += [r"\subsection{Names that do not identify one estimator}", r"\label{sec:rix-ambiguities}",
            "Each short name below is resolved by the rule of \\texttt{tools/registry/whatis.py}: an exact alias, an"
            " alias pattern that matches the name, or the name as a whole word of an alias. A name that resolves to"
            " more than one estimator must not be used alone; the second table lists names the sources use in a sense"
            " they do not map to any registered estimator.", "",
            r"\begingroup\scriptsize",
            r"\begin{longtable}{@{}p{0.22\textwidth}p{0.72\textwidth}@{}}",
            r"\toprule Name & Resolves to \\ \midrule\endhead"]
    unres = reglib.read_tsv(index, reglib.UNRESOLVED) if index.has(reglib.UNRESOLVED) else []
    for name in PROBE_NAMES:
        hits = reglib.resolve(name, ests, als)
        verdict = ("AMBIGUOUS: " if len(hits) > 1 else "") + (", ".join(f"\\texttt{{{B(h)}}}" for h in sorted(hits))
                                                             or "no registered estimator")
        more = [u for u in reglib.unresolved(name, unres)]
        if more:
            verdict += "; also used unmapped (" + ", ".join(f"\\texttt{{{B(u['source'])}:{T(u['line'])}}}" for u in more) + ")"
        out.append(f"{T(name)} & {verdict} \\\\")
    shared = {}
    for a in als:
        shared.setdefault(a["pattern"], set()).add(a["estimator"])
    for pat, owners in sorted(shared.items()):
        if len(owners) > 1:
            out.append(f"pattern \\texttt{{{B(pat)}}} & SHARED by " + ", ".join(f"\\texttt{{{B(o)}}}" for o in sorted(owners))
                       + " \\\\")
    out += [r"\bottomrule", r"\end{longtable}",
            r"\begin{longtable}{@{}p{0.16\textwidth}p{0.28\textwidth}p{0.50\textwidth}@{}}",
            r"\toprule Name & Where (file:line) & Why it is not mapped \\ \midrule\endhead"]
    for u in unres:
        out.append(f"{T(u['name'])} & \\texttt{{{B(u['source'])}:{T(u['line'])}}} & {T(u['why'])} \\\\")
    out += [r"\bottomrule", r"\end{longtable}", r"\endgroup", ""]
    return "\n".join(out)


def render_index_tex(rows, counts, index: reglib.Index) -> str:
    T, B = reglib.tex_escape, reglib.tex_breakable
    out = ["% GENERATED by tools/registry/results_index.py --write from the committed receipts; do not edit.",
           "% Its source of truth is docs/orchestration/registry/RESULTS-INDEX.tsv, generated in the same run.",
           f"{counts['included']} result receipts under "
           + ", ".join(f"\\texttt{{{B(r)}}}" for r in ROOTS)
           + f" give {counts['rows']} index rows, {counts['attributed_rows']} of them attributed to a registered"
           " estimator. Status counts: "
           + ", ".join(f"{T(k)} {v}" for k, v in sorted(counts["status"].items())) + ".",
           ""]
    groups: dict[str, list] = {}
    for r in rows:
        groups.setdefault(r[0], []).append(r)
    for est in sorted(groups, key=lambda e: (e == "UNATTRIBUTED", e)):
        rs = groups[est]
        out += [f"\\subsection*{{Results attributed to \\texttt{{{B(est)}}} ({len(rs)} rows)}}",
                r"\begingroup\tiny\setlength{\LTleft}{0pt}\setlength{\LTright}{0pt}\setlength{\tabcolsep}{2pt}",
                r"\begin{longtable}{@{}p{0.30\textwidth}p{0.09\textwidth}p{0.13\textwidth}p{0.17\textwidth}"
                r"p{0.17\textwidth}p{0.09\textwidth}@{}}",
                r"\toprule Point & Scale & $n$ & Metric: key & Value & Status \\ \midrule\endhead"]
        last = None
        for r in rs:
            if r[10] != last:
                out.append(f"\\multicolumn{{6}}{{@{{}}p{{0.98\\textwidth}}@{{}}}}{{\\textbf{{\\texttt{{{B(r[10])}}}}}}}"
                           r" \\*")
                last = r[10]
            status = T(r[7]) + (f" ({B(r[8])})" if r[8] else "")
            out.append(f"\\texttt{{{B(r[1])}}} & {T(r[2])} & {B(r[3])} & {T(r[4])}: \\texttt{{{B(r[5])}}}"
                       f" & {B(r[6])} & {status} \\\\")
        out += [r"\bottomrule", r"\end{longtable}", r"\endgroup", ""]
    return "\n".join(out)


def write(repo: Path) -> int:
    files, errs, counts = generate(repo)
    for e in errs:
        print("  REGISTRY ERROR " + e)
    for rel, text in files.items():
        (repo / rel).write_text(text)
    print(summary_line(counts) + f"; wrote {', '.join(files)}")
    print("  next: git add " + " ".join(files))
    return 1 if errs else 0


def summary_line(c: dict) -> str:
    out = ", ".join(f"{k} {v}" for k, v in sorted(c["outside_by_top"].items()))
    rec = ", ".join(f"{k} {v}" for k, v in sorted(c["outside_receipts_by_top"].items())) or "none"
    return (f"RESULTS-INDEX :: {c['roots']} tracked JSON in the roots: {c['included']} included "
            f"({c['rows']} rows, {c['attributed_rows']} attributed), {c['excluded-no-metric']} excluded-no-metric, "
            f"{c['excluded-unparseable']} excluded-unparseable; {c['outside']} tracked JSON outside the roots not read "
            f"({out}; named *receipt*.json: {rec})")


def check(repo: Path) -> int:
    files, errs, counts = generate(repo)
    index = reglib.Index(repo)
    fails = list(errs)
    committed_idx = index.text(INDEX_TSV) or ""
    indexed_sources = {r["source"] for r in reglib.read_tsv_text(committed_idx)} if committed_idx else set()
    for path, cls, nrows, _ in counts["_pop_rows"]:
        if cls == "included" and path not in indexed_sources:
            fails.append(f"UNINDEXED receipt {path}: it is in the population ({nrows} metric values) and has "
                         "no row in the committed RESULTS-INDEX.tsv")
    for rel, text in files.items():
        have = index.text(rel)
        if have is None:
            fails.append(f"STALE {rel}: not in the git index")
        elif have != text:
            fails.append(f"STALE {rel}: the staged file differs from a fresh generation")
    for f in fails:
        print("  FAIL " + f)
    if fails:
        print("  fix: python3 tools/registry/results_index.py --write && git add " + " ".join(GENERATED))
    print(summary_line(counts) + (f"; {len(fails)} failure(s)" if fails else "; index fresh and complete"))
    return 1 if fails else 0


def self_test() -> int:
    """The hook's discovery test, in both directions, on a throwaway repository with REAL staging: a copy of the
    registry, every file it cites and one real receipt; a committed fresh index; then (1) a planted result receipt
    must make --check fail as UNINDEXED, (2) a planted non-result JSON must leave it passing (and be counted as
    discovered-and-excluded), (3) a planted result JSON outside the roots must leave it passing."""
    import contextlib
    import io
    import subprocess
    import tempfile

    src = reglib.repo_root(Path(__file__).resolve().parent)
    sidx = reglib.Index(src)
    ok = True

    def quiet(fn, *a):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = fn(*a)
        return rc, buf.getvalue()

    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        env = reglib.git_env()

        def g(*a: str) -> None:
            subprocess.run(["git", "-C", str(t), *a], check=True, capture_output=True, env=env)

        g("init", "-q")
        need = {reglib.ESTIMATORS, reglib.ALIASES, reglib.ATTRIBUTION, reglib.STATUS, reglib.UNRESOLVED,
                "docs/orchestration/state/s5e/cand/assess_receipt.json"}
        need |= {r["defining_source"] for r in reglib.read_tsv(sidx, reglib.ESTIMATORS)}
        for tbl in (reglib.ALIASES, reglib.ATTRIBUTION, reglib.STATUS, reglib.UNRESOLVED):
            need |= {r["source"] for r in reglib.read_tsv(sidx, tbl)}
        for rel in need:
            (t / rel).parent.mkdir(parents=True, exist_ok=True)
            (t / rel).write_bytes(sidx.read(rel))
        g("add", "-A")
        rc, _ = quiet(write, t)
        g("add", "-A")
        rc, out = quiet(check, t)
        base = generate(t)[2]

        def case(name: str, got: int, want: int, out: str) -> None:
            nonlocal ok
            ok &= got == want
            last = out.strip().splitlines()[0] if out.strip() else ""
            print(f"  self-test {'ok' if got == want else 'WRONG':<5} {name}: --check exit {got} (want {want})"
                  f"{'; ' + last[:120] if got else ''}")

        case("fresh fixture", rc, 0, out)
        planted = "docs/orchestration/state/planted/assess_receipt.json"
        (t / planted).parent.mkdir(parents=True, exist_ok=True)
        (t / planted).write_text(json.dumps({"points": {"nominal": {"n": 40, "pooled_cov68": 0.61}}}))
        g("add", planted)
        rc, out = quiet(check, t)
        case("planted result receipt under state/", rc, 1, out)
        ok &= f"UNINDEXED receipt {planted}" in out
        g("rm", "-q", "--cached", planted)
        (t / planted).unlink()
        other = "docs/orchestration/state/planted/budget.json"
        (t / other).write_text(json.dumps({"schema": "budget/1", "node_hours": 3.5, "closure_reweight_sigma": 0.2}))
        g("add", other)
        rc, out = quiet(check, t)
        case("planted non-result JSON under state/", rc, 0, out)
        now = generate(t)[2]
        discovered = now["excluded-no-metric"] == base["excluded-no-metric"] + 1
        ok &= discovered
        print(f"  self-test {'ok' if discovered else 'WRONG':<5} the non-result JSON was discovered and excluded "
              f"(excluded-no-metric {base['excluded-no-metric']} -> {now['excluded-no-metric']})")
        outside = "nd-unfolding/planted/receipt.json"
        (t / outside).parent.mkdir(parents=True, exist_ok=True)
        (t / outside).write_text(json.dumps({"pooled_cov68": 0.5}))
        g("add", outside)
        rc, out = quiet(check, t)
        case("planted result JSON outside the roots", rc, 0, out)
    print("RESULTS-INDEX self-test :: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--summary", action="store_true")
    g.add_argument("--population", action="store_true", help="print every in-root JSON with its class")
    g.add_argument("--self-test", action="store_true")
    ap.add_argument("--repo", type=Path, default=None)
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    repo = reglib.repo_root(a.repo) if a.repo else reglib.repo_root(Path.cwd())
    if a.write:
        return write(repo)
    if a.check:
        return check(repo)
    files, errs, counts = generate(repo)
    for e in errs:
        print("  REGISTRY ERROR " + e)
    if a.population:
        for row in counts["_pop_rows"]:
            print("\t".join(row))
    print(summary_line(counts))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
