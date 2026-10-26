#!/usr/bin/env python3
"""Build, and check, the results index from the committed receipts.

    results_index.py --write [--repo DIR]   # regenerate the index, the population table and the two .tex renderings
    results_index.py --check [--repo DIR]   # exit 1 if any committed generated file differs from a fresh generation
                                            # or a population receipt has no index row (pre-commit)
    results_index.py --check --base REF     # the same, but the rule-8 gate compares against the committed index of
                                            # `git merge-base REF HEAD`, not HEAD's (CI: a pull request's base)
    results_index.py --summary [--repo DIR] # print the population counts
    results_index.py --population           # print every in-root JSON with its class
    results_index.py --self-test            # discovery in both directions on a throwaway repository (pre-commit)

THE POPULATION, DECLARED BY RULE (not by a list of globs someone picked). A file is a RESULTS RECEIPT iff
  R1 it is in the git index (tracked or staged), and
  R2 its path is under one of ROOTS and ends in .json, and
  R3 it parses as JSON, and
  R4 somewhere in it a key that family() assigns to one of METRIC_FAMILIES (tokenized key; count and
     parameter exclusions first; see the block above METRIC_FAMILIES) holds a number, a non-empty list of numbers,
     or an object all of whose leaves are numbers or lists of numbers.
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
             begins with the word, or a STATUS.tsv row (citing a line carrying its quote) matches; else
             `design-projection` if its own status/schema declares design arithmetic (DESIGN_STATUS) or a
             STATUS.tsv row says so;
             else `unreviewed` -- which means no record in the registry withdraws or supersedes it, NOT that it
             is current.
  self_status  the receipt's own top-level `status` string (else "schema: <schema>"), and its top-level
             `verdict` string if it has one ("verdict: FUTILITY-FAIL"), first 100 characters.
  source, keypath  where to read the value.
Nothing is ever deleted: a superseded or withdrawn receipt keeps its rows and gains a status.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
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

# THE METRIC FAMILIES. A key is tokenized (lower-cased, split on every non-alphanumeric character) and judged by
# the rules below IN ORDER; the first that matches names its family. Two exclusions run first:
#   - a key whose FIRST token is a count word (COUNT_FIRST: n_closure, k_recovered, m_residual -- the last is a
#     seed count, state/s5p/recovery/s5p_recovery.py:500) is a count, not a metric;
#   - a key with any NON_METRIC token is a parameter, an operand or a pointer (closure_reweight_sigma is an
#     injection parameter, residual_correlation_EW a correlation, bias_correction a path).
# The value guard (metric_leaves) then requires a number or a non-empty list of numbers, directly or under
# statistic-word keys (CHILD_WORDS): a string, a boolean, a count or a named sub-quantity is never indexed.
# hits68/hits95 are COUNTS of covering intervals; they are indexed under their own families, named as counts.
COUNT_FIRST = {"n", "k", "m", "num", "count", "counts", "nhits"}
NON_METRIC = {"reweight", "hidden", "amplitude", "alpha", "center", "pt0", "ref", "denominator", "threshold",
              "tolerance", "allowance", "operand", "seed", "seeds", "receipt", "receipts", "digest", "digests",
              "path", "job", "sha256", "correlation", "cor", "corr", "slope", "shift", "evidence", "class",
              "recorded", "criterion", "reason", "budget", "cost", "costs", "rule", "glob",
              # OmniFold's step-2 "pull" and "push" are reweighting steps, not statistical pulls
              "push", "weights", "weight",
              # projections and counts declared by the key's own words
              "expected", "design", "failures", "failure", "missing", "predicted", "needed", "identical", "pass",
              # instrument coverage (which launchers a guard covers) is not statistical coverage
              "guard", "launcher", "mutation",
              # correlations and chi-square statistics are other quantities (p-values: P_VALUE_KEY below)
              "spearman", "pearson", "chi2"}
# Under a correlation key nothing is indexed. Under a chi2 key only pulls and residuals are (Q4/chi2/<variant>/pulls
# are pulls); chi2/bias_PB/pt_vs_VL175 is a chi-square, not a bias, and the chi2 value itself is never a metric.
OTHER_QUANTITY = {"spearman", "pearson", "correlation", "corr", "cor"}
CHI2_ALLOWED = {"pull", "pull_sd", "pull_mean", "max_abs_pull", "residual", "residual_se"}
# A key is a p-value only when the WHOLE key is one ("p", "p_value", "pvalue", "null_p..."): v3_p_mult_KE20 and
# D1_p0.350XD4c_p_up are labels that contain a p token, and results under them are indexed.
P_VALUE_KEY = re.compile(r"p|p_?values?|null_p(_.*)?")
# Token SEQUENCES that mark a non-metric: e_lo/e_hi are bin edges (E_lo_of_max_pull), null_p a null p-value.
NON_METRIC_PHRASES = ("e_lo", "e_hi")
# Keys excluded by name PREFIX, each with its reason: the weight sums of a closure sample (sum_w_reco_closure,
# sum_w_reco_closure_data_equiv, max_w_reco_closure) are not a closure metric.
EXCLUDED_KEYS = re.compile(r"(sum|max)_w_reco_closure(_.*)?")
# Under a family key whose value is an object, a numeric leaf is indexed only if every key on the way down is a
# statistic word of CHILD_WORDS (or a number, or a key that is itself in a family): {"max": .., "median": ..,
# "p90": .., "n": ..} under binning_bias_T2_K200 gives max, median and p90 and skips the count n; a named
# sub-quantity such as median_sd_pct under bias_variance_K5 is not a bias and is skipped.
CHILD_WORDS = {"mean", "median", "min", "max", "abs", "rel", "pct", "total", "value", "values", "per", "bin", "bins",
               "functional", "functionals", "all", "t", "frac", "p50", "p90", "p95", "p99", "p100", "i68", "i95",
               "lo", "hi", "low", "high"}
CHILD_WORDS_SPREAD = {"rms", "sd", "std"}  # also allowed under the residual and pull families
CHILD_WORDS |= {"pooled", "miss", "half", "width"}
# An object ALL of whose leaves are numbers is a table of the family's values (labelled by truth, variant or
# comparison: residual_median/{prior, recoil_only, fullevent}); every leaf is indexed except counts and parameters.
# Not when the family key itself names a second quantity (bias_variance_K5 holds sds and fractions too): then
# CHILD_WORDS decides.
MIXED_WORDS = {"variance", "sd", "std", "rms", "mse", "error", "errors", "share"}
METRIC_FAMILIES = (
    ("coverage68_hits", "hits68, hits_68 (a count of covering intervals)", r"hits_?68"),
    ("coverage95_hits", "hits95, hits_95 (a count of covering intervals)", r"hits_?95"),
    ("coverage68", "a cov68/coverage68 token or cov/coverage then 68, any prefix or suffix (pooled_cov68, "
                   "coverage68_min); frac_le1 (fraction inside 1 sigma)", r"(.*_)?cov(erage)?_?68(_.*)?|frac_le1"),
    ("coverage95", "the same with 95; frac_le196 (fraction inside 1.96 sigma)", r"(.*_)?cov(erage)?_?95(_.*)?|frac_le196"),
    ("coverage", "a coverage token", r"(.*_)?coverage(_.*)?"),
    ("pull_sd", "a pull token with sd/rms/std; pullrms, pullsd", r"(.*_)?pull_(.*_)?(sd|rms|std)(_.*)?|(.*_)?(sd|rms|std)_pull(_.*)?|pullrms|pullsd"),
    ("pull_mean", "a pull token with mean; pullmean", r"(.*_)?(mean_pull|pull_mean)(_.*)?|pullmean"),
    ("max_abs_pull", "a pull token with max", r"(.*_)?(max_abs_pull|pull_max_abs|max_pull)(_.*)?"),
    ("pull", "pulls (a list of pulls)", r"pulls"),
    ("bias", "a bias token (bias_norm_w, binning_bias_eavail, median_abs_bias_pct)", r"(.*_)?bias(_.*)?"),
    ("closure", "a closure token", r"(.*_)?closure(_.*)?"),
    ("residual_se", "se_rel(_pct); se_a/se_b/se_c, se_db/se_dc ONLY beside the matching r_/d_ key (ki98)",
     r"se_rel(_pct)?|se_[abc]|se_d[bc]"),
    ("residual", "a resid/residual/residuals token (not residency); mean_rel, median_abs_rel, max_abs_rel (_pct); r_a/r_b/r_c, d_b/d_c ONLY "
                 "when the same object holds the matching se_ key (ki98 mean residuals and their differences)",
     r"(.*_)?resid(ual|uals)?(_.*)?|(mean|median_abs|max_abs)_rel(_pct)?|r_[abc]|d_[bc]"),
)
_FAM = [(name, re.compile(rx)) for name, _, rx in METRIC_FAMILIES]
N_KEYS = ("n", "n_present", "n_declared", "n_experiments", "n_exp", "n_pseudo", "n_pe", "n_pseudo_experiments", "n_nominal_experiments",
          "n_members", "N")
SCALE_WORDS = (("development", ("dev", "development")), ("assessment", ("assess", "assessment")),
               ("production", ("prod", "production")), ("pilot", ("pilot",)), ("interim", ("interim",)))
# A file name carrying the word as a whole token, or a top-level `status` string that BEGINS with it ("SUPERSEDED
# by ...", "WITHDRAWN: ..."); "supersedes X" or "not superseded" do not match.
STATUS_WORDS = (("withdrawn", re.compile(r"(^|[-_.])withdrawn([-_.]|$)", re.I), re.compile(r"^\W*withdrawn\b", re.I)),
                ("superseded", re.compile(r"(^|[-_.])superseded([-_.]|$)", re.I), re.compile(r"^\W*superseded\b", re.I)))
# Design arithmetic is not a result: a receipt whose OWN `status` (or, lacking one, `schema`) says DRAFT, NOT
# REGISTERED, design or cost gets status design-projection for every row. A file name is not enough (r2_design.json
# holds measured values); a file without such a field is marked only by a STATUS.tsv row citing a line that says
# so. A KEY that names a design quantity is never indexed at all (NON_METRIC "design", "expected", "predicted").
DESIGN_STATUS = re.compile(r"\bDRAFT\b|NOT REGISTERED|design|\bcosts?\b", re.I)
# Short names the ambiguity table resolves with whatis.py's rule (reglib.resolve). The list only chooses what is
# printed; each verdict is computed from the registry, never typed.
PROBE_NAMES = ("R", "B0", "N", "F1", "F2", "configuration 1", "configuration 2", "configuration 3", "400/31",
               "400 trees, 31 leaves", "negweight-refined", "joint-test estimator", "exact-split", "lgbm")
INDEX_COLUMNS = ("estimator", "point", "scale", "n", "metric", "key", "value", "status", "superseding",
                 "self_status", "source", "keypath")


KI98_PAIRS = re.compile(r"(r|d|se|se_d)_([abc])")


def tokens(key: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", str(key).lower()) if t]


def non_metric(key: str) -> bool:
    """A count, a parameter, a pointer or another quantity: never a metric key (see the block above)."""
    if "/" in str(key):  # a path used as a key (guard/inventory-base-*): a pointer, not a quantity
        return True
    if P_VALUE_KEY.fullmatch("_".join(tokens(key))):
        return True
    toks = tokens(key)
    if not toks or toks[0] in COUNT_FIRST or "n" in toks or any(t in NON_METRIC for t in toks):
        return True
    k = "_".join(toks)
    return any(re.search(rf"(^|_){ph}(_|$)", k) for ph in NON_METRIC_PHRASES)


def family(key: str, siblings=()) -> str | None:
    if non_metric(key):
        return None
    toks = tokens(key)
    k = "_".join(toks)
    if EXCLUDED_KEYS.fullmatch(k):
        return None
    m = KI98_PAIRS.fullmatch(k)
    if m:  # r_a/d_b/se_c/se_db count only as a residual/standard-error pair in one object
        sib = {"_".join(tokens(x)) for x in siblings}
        letter = m.group(2)
        pair = ({f"se_{letter}"} if m.group(1) == "r" else {f"se_d{letter}"} if m.group(1) == "d" else
                {f"r_{letter}"} if m.group(1) == "se" else {f"d_{letter}"})
        if not pair & sib:
            return None
    for name, rx in _FAM:
        if rx.fullmatch(k):
            return name
    return None


def child_ok(key: str, fam: str) -> bool:
    toks = tokens(key)
    if non_metric(key):
        return False
    words = CHILD_WORDS | (CHILD_WORDS_SPREAD if fam in ("residual", "residual_se", "pull", "pull_sd") else set())
    return all(t.isdigit() or t in words for t in toks) or family(key) is not None


def isnum(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def metric_leaves(o, fam: str, path=(), key: str = ""):
    """(subpath, value) for the numeric leaves of a family key's value: the value itself if it is a number or a
    non-empty list of numbers; under an object, the leaves reached only through CHILD_WORDS keys (strings,
    booleans, counts and named sub-quantities are skipped)."""
    if isnum(o) or (isinstance(o, list) and o and all(isnum(v) for v in o)):
        return [(path, o)]
    out = []
    if isinstance(o, dict):
        table = all_numeric(o) and not (set(tokens(key)) & MIXED_WORDS)
        spread_ok = fam in ("residual", "residual_se", "pull", "pull_sd")
        for k, v in o.items():
            if table and not spread_ok and bare_spread(k):
                continue  # a bare spread (sd, std, rms) beside a bias or coverage value is another quantity
            if (table and not excluded_child(k)) or (not table and child_ok(k, fam)):
                out += metric_leaves(v, fam, path + (str(k),), key if table else k) if not table else \
                    [(path + (str(k),) + sub, val) for sub, val in numeric_table(v, (), spread_ok)]
    return out


def all_numeric(o) -> bool:
    if isnum(o) or (isinstance(o, list) and o and all(isnum(v) for v in o)):
        return True
    return isinstance(o, dict) and bool(o) and all(all_numeric(v) for v in o.values())


def excluded_child(key: str) -> bool:
    return non_metric(key)


def bare_spread(key: str) -> bool:
    t = set(tokens(key))
    return bool(t) and t <= CHILD_WORDS_SPREAD


def numeric_table(o, path=(), spread_ok=True):
    """Every numeric leaf of an all-numeric object, skipping counts and parameters -- and, unless the family is a
    spread family, a bare spread key (sd, std, rms): it is a different quantity from the bias beside it."""
    if isnum(o) or isinstance(o, list):
        return [(path, o)]
    return [x for k, v in o.items() if not excluded_child(k) and (spread_ok or not bare_spread(k))
            for x in numeric_table(v, path + (str(k),), spread_ok)]


def pointer(parts) -> str:
    """A JSON pointer (RFC 6901) without the leading slash: "~" -> "~0", "/" -> "~1", so a key holding "/" is
    unambiguous."""
    return "/".join(str(p).replace("~", "~0").replace("/", "~1") for p in parts)


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

    def walk(o, path, stack, allowed=None):
        if isinstance(o, dict):
            stack = stack + [o]
            for k, v in o.items():
                fam = family(k, o.keys())
                if fam and (allowed is None or fam in allowed):
                    leaves = metric_leaves(v, fam, (), str(k))
                    if leaves:
                        for sub, val in leaves:
                            out.append((path + (str(k),) + sub, str(k), fam, val, stack))
                        continue
                toks = set(tokens(k))
                if toks & OTHER_QUANTITY or P_VALUE_KEY.fullmatch("_".join(tokens(k))):
                    continue  # nothing under a correlation or p-value key is a metric
                walk(v, path + (str(k),), stack, CHI2_ALLOWED if "chi2" in toks else allowed)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, path + (str(i),), stack, allowed)

    walk(doc, (), [])
    return out


def load_rules(index: reglib.Index, path: str, kind: str, warns: list[str] | None = None,
               patterns: dict[str, list[str]] | None = None) -> tuple[list[dict], list[str]]:
    """Rows of ATTRIBUTION.tsv or STATUS.tsv with their citations checked. For ATTRIBUTION (`patterns` given:
    estimator -> its IDENTIFYING alias patterns), RECORDS-RULES rule 7: the cited line must also match one of the
    attributed estimator's identifying alias patterns, so a row cannot rest on a line that does not name it."""
    rows, errs = [], []
    for n, r in enumerate(reglib.read_tsv(index, path), start=2):
        err, warn = reglib.verify_citation(index, *reglib.fields(r))
        if err:
            errs.append(f"{kind} row {n}: {err}")
        if warn and warns is not None:
            warns.append(f"{kind} row {n}: {warn}")
        if patterns is not None and not err:
            text = reglib.cited_text(index, *reglib.fields(r)) or ""
            pats = patterns.get(r["estimator"], [])
            if not any(re.search(p, text) for p in pats):
                errs.append(f"{kind} row {n}: the cited line {r['source']}:{r['line']} matches none of the "
                            f"{len(pats)} identifying alias patterns of {r['estimator']} (rule 7): cite a line that "
                            "names the estimator, or drop the row and let the results stay UNATTRIBUTED")
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
    errs, warns = reglib.verify_registry(index)
    idpats: dict[str, list[str]] = {}
    for a in reglib.read_tsv(index, reglib.ALIASES):
        if a.get("identifying") == "yes":
            idpats.setdefault(a["estimator"], []).append(a["pattern"])
    attrib, e1 = load_rules(index, reglib.ATTRIBUTION, "ATTRIBUTION", warns, idpats)
    status_rules, e2 = load_rules(index, reglib.STATUS, "STATUS", warns)
    errs += e1 + e2
    est_ids = {e["id"] for e in reglib.read_tsv(index, reglib.ESTIMATORS)}
    for r in attrib:
        if r["estimator"] not in est_ids:
            errs.append(f"ATTRIBUTION: estimator {r['estimator']!r} is not an ESTIMATORS id")
    for r in status_rules:
        if r["status"] not in ("withdrawn", "superseded", "design-projection"):
            errs.append(f"STATUS: status {r['status']!r} is not withdrawn/superseded/design-projection")

    all_json = [p for p in index.paths() if p.endswith(".json")]
    in_roots = [p for p in all_json if p.startswith(ROOTS)]
    outside = [p for p in all_json if not p.startswith(ROOTS)]
    blobs = index.read_many(in_roots)
    pop_rows, rows = [], []
    raw: dict = {}
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
        self_status = ""
        if isinstance(doc, dict):
            if isinstance(doc.get("status"), str):
                self_status = doc["status"]
            elif isinstance(doc.get("schema"), str):
                self_status = "schema: " + doc["schema"]
        declared = self_status
        if isinstance(doc, dict) and isinstance(doc.get("verdict"), str):
            self_status = (self_status + "; " if self_status else "") + "verdict: " + doc["verdict"]
        base_status, base_by = "unreviewed", ""
        fname = path.rsplit("/", 1)[-1]
        for word, rx_name, rx_status in STATUS_WORDS:
            if rx_name.search(fname):
                base_status, base_by = word, "file name"
                break
            if self_status and rx_status.search(self_status):
                base_status, base_by = word, "receipt's own status field"
                break
        if base_status == "unreviewed" and DESIGN_STATUS.search(declared):
            base_status, base_by = "design-projection", "receipt's own status/schema"
        scale = scale_of(doc, path)
        for kp, key, fam, val, stack in found:
            keypath = pointer(kp)
            est = next((r["estimator"] for r in attrib if r["_p"].fullmatch(path) and r["_k"].match(keypath)),
                       "UNATTRIBUTED")
            st, by = base_status, base_by
            for r in status_rules:
                if r["_p"].fullmatch(path) and r["_k"].match(keypath):
                    st, by = r["status"], f"{r['superseding_record']} ({r['source']}:{r['line']})"
                    break
            rows.append((est, pointer(kp[:-1]) if len(kp) > 1 else "(top)", scale, find_n(stack), fam, key,
                         fmt(val), st, by, self_status[:100].replace("\t", " ").replace("\n", " "), path, keypath))
            raw[(path, keypath)] = val
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
    counts["_rows"] = rows
    counts["printed"] = printed_estimators(index)
    attributed = {r[0] for r in rows if r[0] != "UNATTRIBUTED"}
    counts["no_results"] = sorted(set(counts["printed"]) - attributed)
    files = {INDEX_TSV: idx_text, POP_TSV: pop_text,
             TEX_INDEX: render_index_tex(rows, counts, index, raw), TEX_REGISTRY: render_registry_tex(index)}
    counts["_warns"] = warns
    return files, errs, counts


def render_registry_tex(index: reglib.Index) -> str:
    T, B = reglib.tex_escape, reglib.tex_breakable
    ests = reglib.read_tsv(index, reglib.ESTIMATORS)
    als = reglib.read_tsv(index, reglib.ALIASES)
    out = ["% GENERATED by tools/registry/results_index.py --write from docs/orchestration/registry/ESTIMATORS.tsv",
           "% and ALIASES.tsv; do not edit. Every row cites a line that carries its quote. The check that verifies this,",
           "% tools/registry/check_registry.py, runs where docs/orchestration/RECORDS-RULES.md says (today: the branch's",
           "% own .githooks/pre-commit, run from its worktree; commit-time enforcement in worktrees is pending).",
           r"\begingroup\scriptsize\setlength{\LTleft}{0pt}\setlength{\LTright}{0pt}",
           r"\begin{longtable}{@{}p{0.17\textwidth}p{0.47\textwidth}p{0.30\textwidth}@{}}",
           r"\caption{Estimator registry: the configurations labelled (a)--(e) in the records, note, primer and paper,"
           r" the configurations the scalar campaign contracts s5c, s5n, s5e and s5p define, and two learner and"
           r" 2D variants the note prints. Labels are checked only for the patterns listed in"
           r" \texttt{check\_registry.py}; see ``What the checks do not do'' in"
           r" \texttt{docs/orchestration/RECORDS-RULES.md}.}\label{tab:rix-estimators}\\",
           r"\toprule Id & Definition & Defining record (file:line) \\ \midrule\endfirsthead",
           r"\toprule Id & Definition & Defining record (file:line) \\ \midrule\endhead"]
    for e in ests:
        out.append(f"\\texttt{{{B(e['id'])}}} & {T(e['summary'])}. Code: {B(e['code_path'])}. Used for: "
                   f"{T(e['used_for'])}. & \\texttt{{{B(e['defining_source'])}:{T(e['defining_line'])}}} \\\\")
    out += [r"\bottomrule", r"\end{longtable}",
            r"\begin{longtable}{@{}p{0.15\textwidth}p{0.10\textwidth}p{0.27\textwidth}p{0.05\textwidth}p{0.36\textwidth}@{}}",
            r"\caption{The registered aliases of each estimator, with the line each is read from. ``No'' in the"
            r" Ident.\ column marks an alias that several configurations share (a learner, a flag, a setting); it"
            r" does not identify the estimator on its own (Sec.~\ref{sec:rix-ambiguities}).}\label{tab:rix-aliases}\\",
            r"\toprule Estimator & Kind & Alias & Ident. & Source (file:line) \\ \midrule\endfirsthead",
            r"\toprule Estimator & Kind & Alias & Ident. & Source (file:line) \\ \midrule\endhead"]
    for a in als:
        out.append(f"\\texttt{{{B(a['estimator'])}}} & {T(a['kind'])} & {T(a['alias'])} & {T(a['identifying'])} & "
                   f"\\texttt{{{B(a['source'])}:{T(a['line'])}}} \\\\")
    out += [r"\bottomrule", r"\end{longtable}", r"\endgroup", ""]
    out += [r"\subsection{Names that do not identify one estimator}", r"\label{sec:rix-ambiguities}",
            "Each short name below is resolved by the rule of \\texttt{tools/registry/whatis.py}: an exact alias, an"
            " alias pattern that matches the name, or the name as a whole word of an alias; only aliases marked"
            " identifying count towards naming an estimator. A name that names more than one estimator, or only"
            " matches shared aliases, must not be used alone; the second table lists names the sources use in a sense"
            " they do not map to any registered estimator.", "",
            r"\begingroup\scriptsize",
            r"\begin{longtable}{@{}p{0.22\textwidth}p{0.72\textwidth}@{}}",
            r"\toprule Name & Resolves to \\ \midrule\endhead"]
    unres = reglib.read_tsv(index, reglib.UNRESOLVED) if index.has(reglib.UNRESOLVED) else []
    for name in PROBE_NAMES:
        hits = reglib.resolve(name, ests, als)
        named = reglib.identifying(hits)
        if named:
            verdict = ("AMBIGUOUS: " if len(named) > 1 else "") + ", ".join(f"\\texttt{{{B(h)}}}" for h in named)
        elif hits:
            verdict = "NON-IDENTIFYING (shared): " + ", ".join(f"\\texttt{{{B(h)}}}" for h in sorted(hits))
        else:
            verdict = "no registered estimator"
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


POSTED = ("main_note.tex", "main_paper.tex", "main_primer.tex", "pet_note.tex")
NO_RESULTS_BEGIN = "% NO-RESULTS-INDEXED BEGIN"
NO_RESULTS_END = "% NO-RESULTS-INDEXED END"


def printed_estimators(index: reglib.Index) -> dict[str, list[str]]:
    """estimator id -> where a POSTED document prints a label naming it (check_registry's LABEL_PATTERNS)."""
    import check_registry as cr
    ests = reglib.read_tsv(index, reglib.ESTIMATORS)
    als = reglib.read_tsv(index, reglib.ALIASES)
    out: dict[str, list[str]] = {}
    files = sorted({f for d in POSTED for f in cr.closure(index, cr.NOTE_DIR, d)})
    for f in files:
        for ln, _, label in cr.labels_in(index.text(f) or ""):
            named = reglib.identifying(reglib.resolve(label, ests, als))
            if len(named) == 1:
                out.setdefault(named[0], []).append(f"{f.rsplit('/', 1)[-1]}:{ln}")
    return out


# Receipts whose nominal points are not called "nominal" in their key paths, each with the line that says so:
# s5e's development K1 (and its r2 recompute K1_*) is the nominal closure -- state/s5p/contract.json:27,
# "s5e dev_receipt.json (K1 nominal closure PASS on 20 development experiments)".
NOMINAL_POINTS = ((re.compile(r"docs/orchestration/state/s5e/cand/dev_receipt\.json"), re.compile(r"K1/")),
                  (re.compile(r"docs/orchestration/state/s5e/cand/review2/r2_recompute\.json"),
                   re.compile(r"development/K1_")))


def point_group(point: str, source: str = "") -> str:
    """"nominal" when the point's own path names nominal truth (points/nominal, grid/C3_nominal) or NOMINAL_POINTS
    declares it, else "other"."""
    if any(p.fullmatch(source) and k.match(point + "/") for p, k in NOMINAL_POINTS):
        return "nominal"
    return "nominal" if any("nominal" in t for t in tokens(point)) else "other"


def numbers(v) -> list[float]:
    return [float(x) for x in v] if isinstance(v, list) else [float(v)]


def render_index_tex(rows, counts, index: reglib.Index, raw: dict) -> str:
    """The records rendering: a summary per estimator x metric family; the full per-row table for ATTRIBUTED rows
    only; UNATTRIBUTED results as a list of receipts with row counts; and the NO-RESULTS-INDEXED table. The TSV
    remains the full record."""
    T, B = reglib.tex_escape, reglib.tex_breakable

    def short(xs, k=3):
        xs = sorted({x for x in xs if x})
        return ", ".join(xs[:k]) + (f" (+{len(xs) - k})" if len(xs) > k else "")

    out = ["% GENERATED by tools/registry/results_index.py --write from the committed receipts; do not edit.",
           "% Its source of truth is docs/orchestration/registry/RESULTS-INDEX.tsv, generated in the same run, which",
           "% holds every row; this rendering summarizes it.",
           f"{counts['included']} result receipts under "
           + ", ".join(f"\\texttt{{{B(r)}}}" for r in ROOTS)
           + f" give {counts['rows']} index rows, {counts['attributed_rows']} of them attributed to a registered"
           " estimator. Status counts: "
           + ", ".join(f"{T(k)} {v}" for k, v in sorted(counts["status"].items())) + ". The summary table gives,"
           " for each estimator and metric family, the number of rows and receipts, the scales and $n$ the receipts"
           " state, the receipts' own status and verdict fields, and the minimum, median and maximum of the values"
           " (list values contribute every element). Per-row tables follow for attributed rows only; unattributed"
           " rows are listed by receipt. Every row is in the TSV.", ""]
    groups: dict[str, list] = {}
    for r in rows:
        groups.setdefault(r[0], []).append(r)
    order = sorted(groups, key=lambda e: (e == "UNATTRIBUTED", e))
    out += [r"\subsubsection*{Summary by estimator, metric family, key, point group and status}",
            "A cell never pools unlike quantities: it holds one metric key, one point group (nominal truth when the"
            " point names it, other points otherwise), one scale (the receipt's stage) and one status.", "",
            r"\begingroup\tiny\setlength{\LTleft}{0pt}\setlength{\LTright}{0pt}\setlength{\tabcolsep}{2pt}",
            r"\begin{longtable}{@{}p{0.11\textwidth}p{0.08\textwidth}p{0.15\textwidth}p{0.07\textwidth}"
            r"p{0.08\textwidth}p{0.03\textwidth}p{0.03\textwidth}p{0.08\textwidth}p{0.13\textwidth}p{0.14\textwidth}@{}}",
            r"\toprule Estimator & Family & Key & Points, scale & Status & Rows & Rcpts & $n$ & Own status / verdict & "
            r"Min / median / max \\ \midrule\endhead"]
    for est in order:
        cells: dict = {}
        for r in groups[est]:
            cells.setdefault((r[4], r[5], point_group(r[1], r[10]), r[2], r[7]), []).append(r)
        for (fam, key, pg, sc, st) in sorted(cells):
            rs = cells[(fam, key, pg, sc, st)]
            vals = sorted(x for r in rs for x in numbers(raw[(r[10], r[11])]))
            med = vals[len(vals) // 2] if len(vals) % 2 else (vals[len(vals) // 2 - 1] + vals[len(vals) // 2]) / 2
            out.append(f"\\texttt{{{B(est)}}} & {T(fam)} & \\texttt{{{B(key)}}} & {T(pg)}, {T(sc)} & {T(st)} & {len(rs)} & "
                       f"{len({r[10] for r in rs})} & {B(short([r[3] for r in rs], 2))} & "
                       f"{B(short([(r[9] or 'none') for r in rs], 2))} & "
                       f"{B(f'{vals[0]:.4g} / {med:.4g} / {vals[-1]:.4g}')} \\\\")
    out += [r"\bottomrule", r"\end{longtable}", r"\endgroup", ""]
    for est in order:
        rs = groups[est]
        if est == "UNATTRIBUTED":
            by: dict[str, list] = {}
            for r in rs:
                by.setdefault(r[10], []).append(r)
            out += [f"\\subsubsection*{{Unattributed results: {len(rs)} rows in {len(by)} receipts}}",
                    "No ATTRIBUTION.tsv row with a cited line that names an estimator covers these rows; they are"
                    " listed by receipt, and RESULTS-INDEX.tsv holds every value.", "",
                    r"\begingroup\tiny\setlength{\LTleft}{0pt}\setlength{\LTright}{0pt}\setlength{\tabcolsep}{2pt}",
                    r"\begin{longtable}{@{}p{0.50\textwidth}p{0.05\textwidth}p{0.20\textwidth}p{0.20\textwidth}@{}}",
                    r"\toprule Receipt & Rows & Families & Own status / verdict \\ \midrule\endhead"]
            for src in sorted(by):
                rr = by[src]
                out.append(f"\\texttt{{{B(src)}}} & {len(rr)} & {T(short([r[4] for r in rr], 4))} & "
                           f"{B(rr[0][9] or 'none')} \\\\")
            out += [r"\bottomrule", r"\end{longtable}", r"\endgroup", ""]
            continue
        out += [f"\\subsubsection*{{Results attributed to \\texttt{{{B(est)}}} ({len(rs)} rows)}}",
                r"\begingroup\tiny\setlength{\LTleft}{0pt}\setlength{\LTright}{0pt}\setlength{\tabcolsep}{2pt}",
                r"\begin{longtable}{@{}p{0.26\textwidth}p{0.08\textwidth}p{0.10\textwidth}p{0.16\textwidth}"
                r"p{0.15\textwidth}p{0.18\textwidth}@{}}",
                r"\toprule Point & Scale & $n$ & Metric: key & Value & Status \\ \midrule\endhead"]
        last = None
        for r in rs:
            if r[10] != last:
                own = f" -- its own status: {T(r[9])}" if r[9] else " -- no status field of its own"
                out.append(f"\\multicolumn{{6}}{{@{{}}p{{0.98\\textwidth}}@{{}}}}{{\\textbf{{\\texttt{{{B(r[10])}}}}}"
                           f"{own}}} \\\\*")
                last = r[10]
            status = T(r[7]) + (f" ({B(r[8])})" if r[8] else "")
            out.append(f"\\texttt{{{B(r[1])}}} & {T(r[2])} & {B(r[3])} & {T(r[4])}: \\texttt{{{B(r[5])}}}"
                       f" & {B(r[6])} & {status} \\\\")
        out += [r"\bottomrule", r"\end{longtable}", r"\endgroup", ""]
    printed = counts["printed"]
    out += [NO_RESULTS_BEGIN, r"\subsubsection*{NO-RESULTS-INDEXED: printed estimators with no attributed row}",
            "Each estimator below is named by a label that the posted note, paper, primer or PET note prints, and no"
            " row of the index is attributed to it. This says only that the index holds no attributed row: its"
            " results may sit outside the indexed families or roots, or in receipts no cited line attributes"
            " (search with \\texttt{whatis.py}).", ""]
    if counts["no_results"]:
        out += [r"\begingroup\scriptsize", r"\begin{longtable}{@{}p{0.25\textwidth}p{0.70\textwidth}@{}}",
                r"\toprule Estimator & Printed at (file:line) \\ \midrule\endhead"]
        for e in counts["no_results"]:
            out.append(f"\\texttt{{{B(e)}}} & {B(short(printed[e], 4))} \\\\")
        out += [r"\bottomrule", r"\end{longtable}", r"\endgroup"]
    else:
        out.append("None: every printed estimator has at least one attributed row.")
    out += [NO_RESULTS_END, ""]
    return "\n".join(out)


def gate_rev(repo: Path, base: str | None) -> str:
    """The commit whose committed index the rule-8 gate compares against: HEAD (pre-commit: the staged index is
    the proposed change), or with `base` the merge-base of BASE and HEAD (CI: HEAD already contains the change, so
    comparing against HEAD would compare the change with itself; on a pull request's merge commit the merge-base
    is the base branch tip). Raises RuntimeError if BASE does not resolve."""
    if base is None:
        return "HEAD"
    tip = reglib.git(repo, "rev-parse", "--verify", f"{base}^{{commit}}").decode().strip()
    return reglib.git(repo, "merge-base", tip, "HEAD").decode().strip()


def attribution_drops(repo: Path, index: reglib.Index, rows, rev: str = "HEAD") -> list[str]:
    """Rule 8, the gate: an estimator with >= 1 attributed row in REV's committed index (default HEAD; see
    gate_rev) must keep >= 1 in the regenerated index, unless WAIVERS.tsv holds a row for it whose cited line
    (digest-checked) gives the reason. No REV, or no index at REV: nothing to compare (the first commit of the
    index)."""
    out = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{INDEX_TSV}"], capture_output=True,
                         env=reglib.git_env(repo), cwd=str(repo))
    if out.returncode != 0:
        return []
    before = {r["estimator"] for r in reglib.read_tsv_text(out.stdout.decode("utf-8", errors="replace"))} - {"UNATTRIBUTED"}
    now = {r[0] for r in rows} - {"UNATTRIBUTED"}
    waived, fails = set(), []
    if index.has(reglib.WAIVERS):
        for n, w in enumerate(reglib.read_tsv(index, reglib.WAIVERS), start=2):
            err, _ = reglib.verify_citation(index, *reglib.fields(w))
            if err:
                fails.append(f"WAIVERS row {n}: {err}")
            else:
                waived.add(w["estimator"])
    for e in sorted(before - now - waived):
        where = "HEAD" if rev == "HEAD" else rev[:12]
        fails.append(f"ATTRIBUTION LOST: {e} has attributed rows in {where}'s {INDEX_TSV} and none in the regenerated "
                     "index. Restore the attribution, or add a WAIVERS.tsv row citing the line that says why")
    return fails


def no_results_listed(index: reglib.Index, counts: dict) -> list[str]:
    """Never silently zero: every estimator a posted document prints by label has an attributed row in the
    COMMITTED index, or is listed between the NO-RESULTS-INDEXED markers of the COMMITTED rendering."""
    committed = reglib.read_tsv_text(index.text(INDEX_TSV) or "") if index.has(INDEX_TSV) else []
    attributed = {r["estimator"] for r in committed}
    tex = index.text(TEX_INDEX) or ""
    block = tex.split(NO_RESULTS_BEGIN, 1)[1].split(NO_RESULTS_END, 1)[0] if NO_RESULTS_BEGIN in tex else ""
    fails = []
    for e in sorted(counts["printed"]):
        if e not in attributed and reglib.tex_breakable(e) not in block:
            fails.append(f"SILENT ZERO: {e} is printed by a posted document ({', '.join(counts['printed'][e][:3])}) "
                         f"and has no attributed row in the committed index, and the committed {TEX_INDEX} does "
                         "not list it under NO-RESULTS-INDEXED")
    return fails


def print_warnings(counts: dict) -> None:
    for w in counts.get("_warns", []):
        print("  NOTE " + w)


def write(repo: Path) -> int:
    files, errs, counts = generate(repo)
    print_warnings(counts)
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


def check(repo: Path, base: str | None = None) -> int:
    try:
        rev = gate_rev(repo, base)
    except RuntimeError as exc:
        print(f"RESULTS-INDEX :: CANNOT CHECK: --base {base} does not resolve: {exc}".rstrip())
        return 2
    files, errs, counts = generate(repo)
    print_warnings(counts)
    index = reglib.Index(repo)
    fails = list(errs)
    committed_idx = index.text(INDEX_TSV) or ""
    indexed_sources = {r["source"] for r in reglib.read_tsv_text(committed_idx)} if committed_idx else set()
    for path, cls, nrows, _ in counts["_pop_rows"]:
        if cls == "included" and path not in indexed_sources:
            fails.append(f"UNINDEXED receipt {path}: it is in the population ({nrows} metric values) and has "
                         "no row in the committed RESULTS-INDEX.tsv")
    fails += no_results_listed(index, counts)
    fails += attribution_drops(repo, index, counts["_rows"], rev)
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
    gate = "" if base is None else f"; rule-8 gate against merge-base {rev[:12]} of --base {base}"
    print(summary_line(counts) + (f"; {len(fails)} failure(s)" if fails else "; index fresh and complete") + gate)
    return 1 if fails else 0


def self_test() -> int:
    """The hook's discovery test, in both directions, on a throwaway repository with REAL staging: a copy of the
    registry, every file it cites and one real receipt; a committed fresh index; then (1) a planted result receipt
    must make --check fail as UNINDEXED, (2) a planted non-result JSON must leave it passing (and be counted as
    discovered-and-excluded), (3) a planted result JSON outside the roots must leave it passing, (4) an
    ATTRIBUTION row whose cited line does not name its estimator must fail (rule 7), and the same line attributed
    to the estimator it does name must pass."""
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
        env = reglib.clean_env()  # a throwaway repository: never the hook's GIT_INDEX_FILE

        def g(*a: str) -> None:
            subprocess.run(["git", "-C", str(t), "-c", "user.name=self-test", "-c", "user.email=self-test@invalid",
                            *a], check=True, capture_output=True, env=env, cwd=str(t))

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
        # Rule 7, both directions: an ATTRIBUTION row whose cited line does not name its estimator fails; one whose
        # cited line does (the same line, attributed to the estimator it names) passes.
        attr = t / reglib.ATTRIBUTION
        clean = attr.read_text()
        # The cited configuration-(a) line is found by the digest its ALIASES row records, not by a line number,
        # so the paper may be edited above it (register round r15 review, item 5).
        # The paper-TABLE line: a table row names configuration (a) alone. Since the TeX reflow (one source line per
        # paragraph, DECISION-20261026-joseph-fps-scope-r04-sensitivity-and-tex-reflow.md section 3) the paper-label
        # line is a whole paragraph that also names configuration (e), so it could not show rule 7 failing.
        a_row = reglib.alias_citation((t / reglib.ALIASES).read_text(), "a-central-lgbm", "paper-table")
        n_a, l_a = reglib.find_cited_line((t / a_row["source"]).read_text(), a_row["quote"], a_row["line_sha256"])
        d285 = reglib.line_digest(l_a)
        # The lookup must follow the line when it moves, and must refuse a file in which the line was edited.
        shifted = "% planted line\n" + (t / a_row["source"]).read_text()
        moved_ok = reglib.find_cited_line(shifted, a_row["quote"], a_row["line_sha256"])[0] == n_a + 1
        try:
            reglib.find_cited_line(shifted.replace(l_a, l_a + " edited"), a_row["quote"], a_row["line_sha256"])
            edit_refused = False
        except ValueError:
            edit_refused = True
        case("cited line found by digest after a line is added above it", 0 if moved_ok else 1, 0, "")
        case("an edited cited line is refused by the digest lookup", 1 if edit_refused else 0, 1, "")
        attr.write_text(clean + "docs/orchestration/state/planted/budget\\.json\t\te-R-joint-test\t"
                        f"docs/analysis-note/paper_body.tex\t{n_a}\t{a_row['quote']}\t{d285}\n")
        g("add", reglib.ATTRIBUTION)
        rc, out = quiet(check, t)
        case("ATTRIBUTION row citing a line that names (a), attributed to R", rc, 1, out)
        ok &= "rule 7" in out
        attr.write_text(clean + "docs/orchestration/state/planted/budget\\.json\t\ta-central-lgbm\t"
                        f"docs/analysis-note/paper_body.tex\t{n_a}\t{a_row['quote']}\t{d285}\n")
        g("add", reglib.ATTRIBUTION)
        rc, out = quiet(write, t)
        g("add", "-A")
        rc, out = quiet(check, t)
        case("the same line attributed to (a), the estimator it names", rc, 0, out)
        # Rule 8, the gate: commit a fresh index, then DROP R's real attribution rules and regenerate.
        attr.write_text(clean)
        g("add", "-A")
        quiet(write, t)
        g("add", "-A")
        g("commit", "-q", "-m", "fixture base")
        lines = clean.split("\n")
        attr.write_text("\n".join(l for l in lines if l.split("\t")[2:3] != ["e-R-joint-test"]))
        g("add", reglib.ATTRIBUTION)
        quiet(write, t)
        g("add", "-A")
        rc, out = quiet(check, t)
        case("R's attribution rules dropped and the index regenerated", rc, 1, out)
        ok &= "ATTRIBUTION LOST: e-R-joint-test" in out
        # --base (CI): the same drop once COMMITTED. Against HEAD the gate compares the change with itself and is
        # silent -- the reason CI passes --base; against the fixture base it fires; against a base that already
        # lacked R it is silent.
        fixture_base = subprocess.run(["git", "-C", str(t), "rev-parse", "HEAD"], check=True, capture_output=True,
                                      env=env, cwd=str(t), text=True).stdout.strip()
        g("commit", "-q", "-m", "drop R's attribution")
        rc, out = quiet(check, t)
        case("R's drop COMMITTED, gate against HEAD (vacuous: why CI needs --base)", rc, 0, out)
        rc, out = quiet(check, t, fixture_base)
        case("R's drop COMMITTED, --base the fixture base", rc, 1, out)
        ok &= "ATTRIBUTION LOST: e-R-joint-test" in out and fixture_base[:12] in out
        rc, out = quiet(check, t, "HEAD")
        case("R's drop COMMITTED, --base a commit that already lacks R", rc, 0, out)
        rc, out = quiet(check, t, "no-such-ref")
        case("--base that does not resolve (cannot check)", rc, 2, out)
        g("reset", "-q", "--soft", fixture_base)
        wv = t / reglib.WAIVERS
        wv.write_text("estimator\treason\tsource\tline\tquote\tline_sha256\ne-R-joint-test\tself-test waiver\t"
                      f"docs/analysis-note/paper_body.tex\t{n_a}\t{a_row['quote']}\t{d285}\n")
        g("add", reglib.WAIVERS)
        quiet(write, t)
        g("add", "-A")
        rc, out = quiet(check, t)
        case("... with a cited WAIVERS.tsv row for it", rc, 0, out)
        wv.write_text("estimator\treason\tsource\tline\tquote\tline_sha256\n")
        attr.write_text(clean)
        g("add", "-A")
        quiet(write, t)
        g("add", "-A")
        # Never silently zero: with a posted driver that prints labels (a)-(e), removing the NO-RESULTS-INDEXED
        # listing from the committed rendering must fail.
        (t / "docs/analysis-note/main_paper.tex").write_text("\\input{paper_body}\n")
        g("add", "-A")
        quiet(write, t)
        g("add", "-A")
        rc, out = quiet(check, t)
        case("posted driver added; regenerated index lists its zero-row estimators", rc, 0, out)
        tex = t / TEX_INDEX
        body = tex.read_text()
        head_, rest = body.split(NO_RESULTS_BEGIN, 1)
        tex.write_text(head_ + NO_RESULTS_BEGIN + "\n" + NO_RESULTS_END + rest.split(NO_RESULTS_END, 1)[1])
        g("add", TEX_INDEX)
        rc, out = quiet(check, t)
        case("NO-RESULTS-INDEXED listing emptied in the committed rendering", rc, 1, out)
        ok &= "SILENT ZERO" in out
    # One fixture per exclusion class (family() on the key as the walker sees it), and a positive control each.
    sd_doc = {"library_bias_eavail": {"cases": {"D1_p0.350": {"bias": 0.1, "sd": 0.02}}}}
    got_sd = sorted("/".join(h[0]) for h in hits(sd_doc))
    good = got_sd == ["library_bias_eavail/cases/D1_p0.350/bias"]
    ok &= good
    print(f"  self-test {'ok' if good else 'WRONG':<5} a bare sd beside a bias in a numeric table is not a bias: {got_sd}")
    for key, want in (("E_lo_of_max_pull", None), ("residency_ratio", None), ("guard/inventory-base-x.py", None),
                      ("spearman(r,shift)", None), ("chi2_bias_PB_raw_frozen_pz", None),
                      ("control_bias_PB_chi2_pz", None), ("null_P(max pull SD over 20 >= observed)", None),
                      ("sum_w_reco_closure_data_equiv", None), ("M_residual", None), ("argmax_mean_pull", "pull_mean"),
                      ("p", None), ("p_value", None), ("v3_p_mult_KE20", None),
                      ("pearson_bias", None), ("max_pull_sd", "pull_sd"), ("residual_median", "residual"),
                      ("bias_norm_W", "bias"), ("coverage68_min", "coverage68"), ("hits95", "coverage95_hits")):
        got = family(key)
        good = got == want
        ok &= good
        print(f"  self-test {'ok' if good else 'WRONG':<5} family({key!r}) = {got} (want {want})")
    doc = {"chi2": {"bias_PB": {"pt_vs_VL175": 1.9}}, "pooled_cov68": 0.68}
    under = [h[0] for h in hits(doc)]
    good = under == [("pooled_cov68",)]
    ok &= good
    print(f"  self-test {'ok' if good else 'WRONG':<5} a bias under a chi2 key is not indexed: {under}")
    doc = {"V3_statistics": {"v3_p_mult_KE20": {"max_abs_pull_used": 2.0}},
           "cases": {"D1_p0.350XD4c_p_up": {"library_bias_eavail": 0.1}}, "p": 0.01, "p_value": {"bias": 1.0},
           "Q4": {"chi2": {"variant_i": {"pulls": [1.0, -1.0], "chi2": 3.0}}}}
    got = sorted("/".join(h[0]) for h in hits(doc))
    want = ["Q4/chi2/variant_i/pulls", "V3_statistics/v3_p_mult_KE20/max_abs_pull_used",
            "cases/D1_p0.350XD4c_p_up/library_bias_eavail"]
    good = got == want
    ok &= good
    print(f"  self-test {'ok' if good else 'WRONG':<5} labels with a p token are descended, a whole p/p_value key "
          f"is not, and pulls under chi2 are indexed while the chi2 value is not: {got}")
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
    ap.add_argument("--base", default=None, metavar="REF",
                    help="with --check: the rule-8 gate compares against `git merge-base REF HEAD` (CI)")
    a = ap.parse_args(argv)
    if a.base is not None and not a.check:
        ap.error("--base is valid only with --check")
    if a.self_test:
        return self_test()
    repo = reglib.repo_root(a.repo) if a.repo else reglib.repo_root(Path.cwd())
    if a.write:
        return write(repo)
    if a.check:
        return check(repo, a.base)
    files, errs, counts = generate(repo)
    print_warnings(counts)
    for e in errs:
        print("  REGISTRY ERROR " + e)
    if a.population:
        for row in counts["_pop_rows"]:
            print("\t".join(row))
    print(summary_line(counts))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
