"""Compare an s5p_recompute output with production's ``stage7/joint/joint-evaluate.json`` and ``robust-labels.json``.

Production's nesting was not read from its code. The matcher uses the key names production writes (``tests``,
``T_total_obs``, ``total``/``shape`` with ``p``/``k``/``B``, ``variants``, ``robustness_variants``, ``decisions``,
``holm_point``, ``decisions_robust_kappa``, ``robust_to_the_sub_fine_residual``, ``power``, ...), plus the facts
stated by the production owner: variant names, the ``{"not_calibrated": ...}`` record of a null stopped at B = 0,
and the robust-labels schema "s5p-robust-labels/2".

**Two directions, both enforced (independent review 2026-09-29, REVIEW-20260929-s5p-recompute-comparer.md):**

1. **Required leaves.** Derived from the recompute record and the owner-stated schema, not from what production
   happens to contain. A missing one is NOT LOCATED, and the verdict cannot be AGREE. Required:
   - top-level ``design_sha256`` and ``v_sha256``;
   - per calibrated null: ``T_total_obs``, ``T_shape_obs`` and ``domain_cells``; per test the claim ``p``/``k``/``B``,
     the jitter summary (``min``, ``median``, ``max``, ``n``) and the implied size of each process-shift variant
     c > 0 (per null, or inside the variant entry as the frozen e2e test shows); every claim variant (``p``, ``k``
     per test) in ``variants``; every ruled κ = 3 M1 member in ``robustness_variants``. The top-level location of
     the two digests is inferred from the key names production writes; if they sit elsewhere, the verdict is
     INCOMPLETE until the mapping is extended;
   - per null at B = 0: a scalar ``not_calibrated`` marker (a marker of another shape is INCOMPLETE, a false one
     DISCREPANT), or claims with B = 0;
   - per test: ``decisions``, ``holm_point``, ``decisions_robust_kappa`` and ``robust_to_the_sub_fine_residual``;
   - per power set with products: ``n``, and each (test, level, rule);
   - in ``robust-labels.json``: ``labels``; ``decisions_kappa3_replace`` (``p``, ``k``, ``B``, ``threshold``,
     ``interval``, ``level``, ``decision``); ``family_members``;
     ``diagnostics.frozen_boolean_robust_to_the_sub_fine_residual``; ``diagnostics.keep_both.{family, labels}``;
     ``evaluate_sha256``, ``design_sha256`` and ``alpha_family``.
2. **Every production leaf accounted for.** A leaf is CONSUMED by a comparison row, or EXCLUDED by an anchored path
   pattern of ``EXCLUDED_SCOPE`` (a scalar leaf only; each pattern with its reason; the excluded paths are listed in
   the report), or it is UNRESOLVED, and the verdict cannot be AGREE.

Types are strict: a bool is not a number, a string is not a p-value, and a dict or list where a scalar is expected
is a discrepancy that consumes nothing beneath it.

Verdicts and exit codes:
- AGREE (exit 0): every row agrees, nothing required is missing, and no leaf is unresolved.
- DISCREPANT (exit 1): at least one row disagrees.
- INCOMPLETE (exit 2): nothing disagrees, but something required is not located or a leaf is unresolved.
- ERROR (exit 3): an input could not be read or processed (the report records the error), or the report itself
  could not be removed or written.

``--out`` is removed before comparing, so a failed run never leaves an earlier report in place.

Agreement rules: counts exactly (integral numbers); p-values and interval ends to 1e-12 absolute; statistics to
1e-8 relative; labels, booleans and digests exactly and of the same type.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

TESTS = ("total", "shape")
LEVELS = ("0.05", "0.005")
POWER_RULES = (("rank_unshifted", "unshifted"), ("rank_claim", "claim_rule"),
               ("determined_claim", "claim_rule_determined"))

_V_REASON = "V-construction metadata frozen with V; v_sha256 is required and compared"
# Anchored path patterns ("*" = one segment) of optional metadata, matched only by scalar leaves (or lists of scalars).
EXCLUDED_SCOPE = {
    "joint-evaluate.json": [
        (("schema",), "format identifier, not a computed quantity"),
        (("utc",), "timestamp"),
        (("code_sha256",), "producer identity"),
        (("files_first_last",), "input path echo"),
        (("lateral_symmetry", "*", "*"), _V_REASON),
        (("shrinkage",), _V_REASON),
        (("median_rel_sd",), _V_REASON),
    ],
    "robust-labels.json": [
        (("schema",), "format identifier"),
        (("code_sha256",), "producer identity"),
        (("ruling",), "citation of the ruling record (text)"),
        (("evaluate",), "input path echo; evaluate_sha256 is required and compared"),
    ],
}

_C_NAME = re.compile(r"^(?:c\s*=\s*)?([0-9]*\.?[0-9]+)$")
_M1_NAME = re.compile(r"^m1\s*=?\s*([+-])\s*([0-9]*\.?[0-9]+)$")


def variant_key(name):
    """A variant name as ('c', coefficient) or ('m1', signed kappa); None if it cannot be parsed (never guessed)."""
    if not isinstance(name, str):
        return None
    n = name.strip()
    m = _C_NAME.match(n)
    if m:
        return ("c", float(m.group(1)))
    m = _M1_NAME.match(n)
    if m:
        return ("m1", float(m.group(2)) * (1 if m.group(1) == "+" else -1))
    return None


def is_scalar(v):
    return v is None or isinstance(v, (bool, int, float, str))


def walk(node, path=()):
    """Every leaf with its path; a list of scalars is one leaf, a list containing containers is walked, and an
    EMPTY dict is itself a leaf (so an unknown empty container cannot pass unseen)."""
    if isinstance(node, dict) and not node:
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, path + (str(k),))
    elif isinstance(node, list) and node and not all(is_scalar(x) for x in node):
        for i, v in enumerate(node):
            yield from walk(v, path + (str(i),))
    else:
        yield path, node


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def agree(kind, a, b):
    if a is None or b is None:
        return False
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
        if not (isinstance(a, (list, tuple)) and isinstance(b, (list, tuple))) or len(a) != len(b):
            return False
        return all(agree(kind, x, y) for x, y in zip(a, b))
    if isinstance(a, dict) or isinstance(b, dict):
        return False
    if kind == "count":
        return _num(a) and _num(b) and float(a) == float(b) and float(b).is_integer()
    if kind == "p":
        return _num(a) and _num(b) and abs(float(a) - float(b)) <= 1e-12
    if kind == "stat":
        if not (_num(a) and _num(b)):
            return False
        a, b = float(a), float(b)
        return a == b or abs(a - b) <= 1e-8 * max(abs(a), abs(b))
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if _num(a) and _num(b):
        return float(a) == float(b)
    return type(a) is type(b) and a == b


def kind_of(key: str) -> str:
    if key in ("k", "B", "n", "domain_cells", "count", "n_present", "n_declared", "min_B", "max_B", "step",
               "n_pairs", "declared"):
        return "count"
    if key.startswith("T") or key in ("mean", "median", "sd", "magnitude", "a", "se", "a_over_se", "bias_norm_W"):
        return "stat"
    if key in ("p", "interval", "power", "p_min", "p_max", "p_median", "min", "max", "threshold", "level",
               "alpha_family"):
        return "p"
    return "exact"


class Ledger:
    """Comparison rows, the production leaf paths they consumed, and required items not located."""

    def __init__(self, doc, name):
        self.doc, self.name = doc, name
        self.rows, self.consumed, self.missing = [], set(), []

    def get(self, path):
        cur = self.doc
        for p in path:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            elif isinstance(cur, list) and p.isdigit() and int(p) < len(cur):
                cur = cur[int(p)]
            else:
                return None
        return cur

    def row(self, label, kind, mine, path):
        """Compare one production value with the recompute's. A container where a scalar (or a list, when the
        recompute's value is a list) is expected is a discrepancy, and nothing beneath it is consumed."""
        theirs = self.get(path)
        shape_ok = not isinstance(theirs, dict) and (isinstance(mine, (list, tuple)) or not isinstance(theirs, list))
        self.rows.append({"item": label, "kind": kind, "mine": mine, "production": theirs,
                          "production_path": f"{self.name}:" + "/".join(path),
                          "agree": shape_ok and agree(kind, mine, theirs)})
        if shape_ok:
            self.consumed.add(tuple(path))

    def require(self, label, path, kind, mine):
        if self.get(path) is None:
            self.missing.append(f"{self.name}:{label}")
        else:
            self.row(label, kind, mine, path)

    def first(self, *paths):
        for p in paths:
            if self.get(p) is not None:
                return p
        return None

    def same_names(self, label, mine: dict, path, skip=()):
        """Compare every scalar leaf of the production dict at ``path`` whose key the recompute record also has."""
        sub = self.get(path)
        if not isinstance(sub, dict) or not isinstance(mine, dict):
            return
        for k, v in sub.items():
            if k in skip or k not in mine or isinstance(v, dict):
                continue
            self.row(f"{label}:{k}", kind_of(k), mine[k], path + (k,))

    def is_consumed(self, path):
        return any(path[:len(c)] == c for c in self.consumed)


def _match(pattern, path):
    return len(pattern) == len(path) and all(a == "*" or a == b for a, b in zip(pattern, path))


def excluded(doc_name, path, value):
    """The reason an unconsumed leaf is optional metadata, or None: an anchored pattern and a scalar value."""
    if not (is_scalar(value) or (isinstance(value, list) and all(is_scalar(x) for x in value))):
        return None
    for pattern, reason in EXCLUDED_SCOPE[doc_name]:
        if _match(pattern, path):
            return reason
    return None


def locate_null(prod, key):
    """``tests/<key>`` if production has it, else the shortest path ending at ``key`` whose dict holds statistics or
    a ``not_calibrated`` marker."""
    tests = prod.get("tests")
    if isinstance(tests, dict) and isinstance(tests.get(key), dict):
        return ("tests", key)
    best = None

    def visit(node, path):
        nonlocal best
        if isinstance(node, dict):
            for k, v in node.items():
                p = path + (str(k),)
                if k == key and isinstance(v, dict) and ("T_total_obs" in v or "T_shape_obs" in v or
                                                         "not_calibrated" in v or any(
                        isinstance(v.get(t), dict) and "p" in v[t] for t in TESTS)):
                    if best is None or len(p) < len(best):
                        best = p
                visit(v, p)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                visit(v, path + (str(i),))

    visit(prod, ())
    return best


def _variant_entries(pv):
    """(name, index-or-key, entry) of a production variant container (dict keyed by name, or list of labelled)."""
    if isinstance(pv, dict):
        for lbl, ent in pv.items():
            yield str(lbl), str(lbl), ent
    elif isinstance(pv, list):
        for i, ent in enumerate(pv):
            if isinstance(ent, dict):
                yield str(ent.get("label", ent.get("variant", i))), str(i), ent


def _compare_variant_family(L, key, rec, base, vkey, mine_members):
    """Required: every recompute member of this family, each test's k and p; production extras stay unresolved."""
    pv = L.get(base + (vkey,))
    if not mine_members and pv in ({}, []):
        L.consumed.add(base + (vkey,))  # expected empty (a null without M1 members) and empty
        return
    found = {}
    for name, idx, ent in _variant_entries(pv if pv is not None else {}):
        vk = variant_key(name)
        if vk is not None and vk not in found:
            found[vk] = (idx, ent)
        if isinstance(pv, list) and isinstance(ent, dict) and "label" in ent:
            L.consumed.add(base + (vkey, idx, "label"))
    for mname in mine_members:
        vk = variant_key(mname)
        if vk not in found:
            L.missing.append(f"{L.name}:{key}:{vkey}[{mname}]")
            continue
        idx, ent = found[vk]
        for t in TESTS:
            m = rec["tests"][t]
            src = m["variants"] if vkey == "variants" else (m.get("robust_kappa3_replace_kappa2") or {}).get("variants", {})
            mv = src.get(mname)
            for f in ("k", "p"):
                L.require(f"{key}:{t}:{vkey}[{mname}]:{f}", base + (vkey, idx, t, f), kind_of(f),
                          mv.get(f) if mv else None)


def _claim_members(rec):
    return list(rec["tests"]["total"].get("variants", {}))


def _robust_m1_members(rec):
    r = rec["tests"]["total"].get("robust_kappa3_replace_kappa2")
    return [n for n in (r or {}).get("variants", {}) if n.startswith("m1=")]


def compare_evaluate(mine, prod) -> Ledger:
    L = Ledger(prod, "joint-evaluate.json")
    L.require("design_sha256", ("design_sha256",), "exact", (mine.get("inputs") or {}).get("design_sha256"))
    L.require("v_sha256", ("v_sha256",), "exact", ((mine.get("provenance") or {}).get("V") or {}).get("sha256"))
    if "names" in prod:
        L.row("names", "exact", mine.get("names"), ("names",))
    prov = mine.get("provenance") or {}
    for key, rec in mine["nulls"].items():
        base = locate_null(prod, key)
        if base is None:
            L.missing.append(f"{L.name}:{key}")
            continue
        node = L.get(base)
        if rec["B"] == 0:
            if "not_calibrated" in node:
                mark = node["not_calibrated"]
                if is_scalar(mark):  # true or a non-empty reason agrees; false, 0, "" or null is a disagreement
                    ok = mark is True or (isinstance(mark, str) and mark != "")
                    L.rows.append({"item": f"{key}:not_calibrated", "kind": "exact", "mine": True, "production": mark,
                                   "production_path": f"{L.name}:" + "/".join(base + ("not_calibrated",)),
                                   "agree": ok})
                    L.consumed.add(base + ("not_calibrated",))
                else:  # a marker of an unstated shape is a mapping gap, not a disagreement; its leaves stay unresolved
                    L.missing.append(f"{L.name}:{key}:not_calibrated (a scalar marker; found {type(mark).__name__})")
            else:
                for t in TESTS:
                    for f in ("p", "k", "B"):
                        L.require(f"{key}:{t}:claim_{f}", base + (t, f), kind_of(f), rec["tests"][t].get(f))
                for pk, mv, kd in (("T_total_obs", rec["observed_T"]["total"], "stat"),
                                   ("T_shape_obs", rec["observed_T"]["shape"], "stat"),
                                   ("domain_cells", rec["domain_cells"], "count")):
                    if L.get(base + (pk,)) is not None:
                        L.row(f"{key}:{pk}", kd, mv, base + (pk,))
            continue
        if "not_calibrated" in node:  # the recompute calibrated this null
            L.rows.append({"item": f"{key}:not_calibrated", "kind": "exact", "mine": False,
                           "production": node["not_calibrated"],
                           "production_path": f"{L.name}:" + "/".join(base + ("not_calibrated",)), "agree": False})
        L.require(f"{key}:T_total_obs", base + ("T_total_obs",), "stat", rec["observed_T"]["total"])
        L.require(f"{key}:T_shape_obs", base + ("T_shape_obs",), "stat", rec["observed_T"]["shape"])
        L.require(f"{key}:domain_cells", base + ("domain_cells",), "count", rec["domain_cells"])
        ps = dict(rec.get("process_shift") or {})
        ps.update(prov.get(f"process_shift:{key}") or {})
        L.same_names(f"{key}:process_shift", ps, base + ("process_shift",))
        L.same_names(f"{key}:m1_shift", prov.get(f"m1_shift:{key}") or {}, base + ("m1_shift",))
        for t in TESTS:
            mt = rec["tests"][t]
            for f in ("p", "k", "B"):
                L.require(f"{key}:{t}:claim_{f}", base + (t, f), kind_of(f), mt.get(f))
            L.same_names(f"{key}:{t}:claim", mt, base + (t,), skip=("variants", "unshifted", "p", "k", "B", "argmax"))
            if isinstance(L.get(base + (t, "unshifted")), dict):
                L.same_names(f"{key}:{t}:unshifted", mt.get("unshifted") or {}, base + (t, "unshifted"))
            for stat in ("median", "sd"):
                pk = f"null_T_{t}_{stat}"
                if L.get(base + (pk,)) is not None:
                    L.row(f"{key}:{pk}", "stat", rec["null_T_summary"][t][stat], base + (pk,))
            jit = mt.get("observed_jitter") or {}
            for stat, mk in (("min", "p_min"), ("median", "p_median"), ("max", "p_max"), ("n", "n")):
                p = L.first(base + ("observed_jitter_p", t, stat), base + (t, "observed_jitter_p", stat))
                if p is None:
                    L.missing.append(f"{L.name}:{key}:{t}:observed_jitter_p:{stat}")
                else:
                    L.row(f"{key}:{t}:observed_jitter_p:{stat}", "count" if stat == "n" else "p", jit.get(mk), p)
            for lbl, mv in (mt.get("implied_size") or {}).items():
                # the frozen evaluator reports the implied size "per variant c > 0" (s5p_joint docstring): required for
                # the process-shift variants, compared where present for any other
                p = _implied_size_path(L, base, lbl, t)
                if p is not None:
                    L.row(f"{key}:{t}:implied_size_of_unshifted_test[{lbl}]", "p", mv, p)
                elif lbl.startswith("c="):
                    L.missing.append(f"{L.name}:{key}:{t}:implied_size_of_unshifted_test[{lbl}]")
            for lbl, mv in (mt.get("median_shift_in_null_sd") or {}).items():
                p = L.first(*[base + ("median_shift_in_null_sd", x, t) for x in _names_like(L.get(base + ("median_shift_in_null_sd",)), lbl)],
                            *[base + ("median_shift_in_null_sd", t, x) for x in _names_like(L.get(base + ("median_shift_in_null_sd", t)), lbl)])
                if p is not None:
                    L.row(f"{key}:{t}:median_shift_in_null_sd[{lbl}]", "stat", mv, p)
            # the frozen keep-both robust claim, when production writes it per test (e.g. tests/<null>/total_robust)
            rob = mt.get("robust_kappa3_retain_kappa2") or {"p": mt.get("p"), "k": mt.get("k"), "B": mt.get("B")}
            if isinstance(L.get(base + (f"{t}_robust",)), dict):
                L.same_names(f"{key}:{t}_robust(keep-both)", rob, base + (f"{t}_robust",), skip=("variants", "argmax"))
                _compare_argmax(L, f"{key}:{t}_robust(keep-both)", rob, base + (f"{t}_robust",))
            _compare_argmax(L, f"{key}:{t}:claim", mt, base + (t,))
        _compare_variant_family(L, key, rec, base, "variants", _claim_members(rec))
        _compare_variant_family(L, key, rec, base, "robustness_variants", _robust_m1_members(rec))
    fam = mine["family"]
    sources = (("decisions", {d["test"]: d for d in fam["decisions"]}, "decision"),
               ("holm_point", {d["test"]: d for d in fam["decisions"]}, "holm_point"),
               ("decisions_robust_kappa", {d["test"]: d for d in fam["keep_both_kappa3_diagnostic"]["holm"]},
                "decision"))
    for field, source, attr in sources:
        for test, md in source.items():
            null, t = test.split(":")
            p = L.first((field, null, t), (field, test))
            if p is None:
                L.missing.append(f"{L.name}:{field}:{test}")
                continue
            node = L.get(p)
            if isinstance(node, dict):
                leafk = "decision" if "decision" in node else "label"
                L.require(f"{field}:{test}", p + (leafk,), "exact", md.get(attr))
                L.same_names(f"{field}:{test}", md, p, skip=(leafk, "test"))
            else:
                L.row(f"{field}:{test}", "exact", md.get(attr), p)
    for test, mv in fam.get("frozen_boolean_equivalent_diagnostic", {}).items():
        null, t = test.split(":")
        p = L.first(("robust_to_the_sub_fine_residual", null, t), ("robust_to_the_sub_fine_residual", test))
        if p is None:
            L.missing.append(f"{L.name}:robust_to_the_sub_fine_residual:{test}")
        else:
            L.row(f"robust_to_the_sub_fine_residual:{test}", "exact", mv, p)
    if "not_calibrated" in prod:
        L.row("not_calibrated", "exact", sorted(k for k, r in mine["nulls"].items() if r["B"] == 0),
              ("not_calibrated",))
    ppow = prod.get("power") if isinstance(prod.get("power"), dict) else {}
    if not mine.get("power") and ppow == {} and "power" in prod:
        L.consumed.add(("power",))  # no power set on either side
    for sk, mp in mine.get("power", {}).items():
        if sk not in ppow:
            L.missing.append(f"{L.name}:power:{sk}")
            continue
        base = ("power", sk)
        L.require(f"power:{sk}:n", base + ("n",), "count", mp.get("n_present"))
        for pk, mv, kd in (("declared", mp.get("n_declared"), "count"), ("null", mp.get("null"), "exact"),
                           ("incomplete", not mp.get("complete", False), "exact")):
            if L.get(base + (pk,)) is not None:
                L.row(f"power:{sk}:{pk}", kd, mv, base + (pk,))
        if not mp.get("n_present"):
            continue
        for t in TESTS:
            for lvl in LEVELS:
                for mine_rule, prod_rule in POWER_RULES:
                    mr = mp.get(t, {}).get(lvl, {}).get(mine_rule) or {}
                    p = L.first(base + (t, prod_rule, lvl), base + (prod_rule, t, lvl),
                                base + ("levels", lvl, t, prod_rule), base + (t, lvl, prod_rule),
                                base + (prod_rule, lvl, t))
                    label = f"power:{sk}:{t}:{lvl}:{mine_rule}"
                    if p is None:
                        L.missing.append(f"{L.name}:{label}")
                    elif isinstance(L.get(p), dict):
                        L.same_names(label, mr, p)
                        if not any(r["item"].startswith(label + ":") for r in L.rows):
                            L.missing.append(f"{L.name}:{label} (no comparable field)")
                    else:
                        L.row(label, "p", mr.get("power"), p)
    return L


def _implied_size_path(L, base, lbl, t):
    """The production path of one implied size: per null (``implied_size_of_unshifted_test/<variant>/<t>``, or
    ``.../<t>/<variant>``), or inside the variant entry (``variants/<variant>/implied_size_of_unshifted_test/<t>``,
    the layout the frozen e2e test asserts), where the value may be a scalar or ``{"power": ...}``."""
    pk = "implied_size_of_unshifted_test"
    cands = [base + (pk, x, t) for x in _names_like(L.get(base + (pk,)), lbl)] + \
            [base + (pk, t, x) for x in _names_like(L.get(base + (pk, t)), lbl)] + \
            [base + ("variants", x, pk, t) for x in _names_like(L.get(base + ("variants",)), lbl)]
    p = L.first(*cands)
    if p is not None and isinstance(L.get(p), dict) and "power" in L.get(p):
        p = p + ("power",)
    return p


def _compare_argmax(L, label, mine_rec, path):
    """``argmax`` (the variants attaining the claim) compared as a set of parsed variant names."""
    node = L.get(path + ("argmax",))
    if node is None or "argmax" not in mine_rec:
        return
    ok_type = isinstance(node, list) and all(isinstance(x, str) for x in node)
    keys = [variant_key(x) for x in node] if ok_type else None
    if ok_type and any(k is None for k in keys):
        return  # an unparsable name: left UNRESOLVED
    L.rows.append({"item": f"{label}:argmax", "kind": "names", "mine": mine_rec["argmax"], "production": node,
                   "production_path": f"{L.name}:" + "/".join(path + ("argmax",)),
                   "agree": ok_type and sorted(keys) == sorted(variant_key(x) for x in mine_rec["argmax"])})
    if ok_type:
        L.consumed.add(path + ("argmax",))


def _names_like(container, mine_label):
    """Production keys of ``container`` naming the same variant as the recompute's label."""
    if not isinstance(container, dict):
        return []
    vk = variant_key(mine_label.replace("c=", "")) or variant_key(mine_label)
    return [k for k in container if variant_key(k) == vk] if vk else []


def family_names(mine: dict, which: str) -> dict:
    """Per test, the variant names of the recompute's κ = 3 family ('replace' ruled, 'retain' keep-both)."""
    out = {}
    for key, rec in mine["nulls"].items():
        for t in TESTS:
            tr = rec["tests"][t]
            fam = tr.get(f"robust_kappa3_{which}_kappa2")
            out[f"{key}:{t}"] = sorted((fam or tr).get("variants", {}))
    return out


def compare_labels_doc(mine, doc, prod_sha256) -> Ledger:
    LL = Ledger(doc, "robust-labels.json")
    fam = mine["family"]
    if prod_sha256 is None:  # the evaluate file's digest was not computed: nothing to check against, not a discrepancy
        LL.missing.append(f"{LL.name}:evaluate_sha256 (the evaluate file's digest was not computed)")
        if "evaluate_sha256" in doc:
            LL.consumed.add(("evaluate_sha256",))
    else:
        LL.require("evaluate_sha256", ("evaluate_sha256",), "exact", prod_sha256)
    LL.require("design_sha256", ("design_sha256",), "exact", (mine.get("inputs") or {}).get("design_sha256"))
    LL.require("alpha_family", ("alpha_family",), "p", mine.get("alpha_family"))

    def per_test(field_path, src, what):
        if LL.get(field_path) is None:
            LL.missing.append(f"{LL.name}:{'/'.join(field_path)}")
            return
        for test, mv in src.items():
            null, t = test.split(":")
            p = LL.first(field_path + (test,), field_path + (null, t))
            label = f"{'/'.join(field_path)}:{test}"
            if p is None:
                LL.missing.append(f"{LL.name}:{label}")
                continue
            node = LL.get(p)
            if what == "names":
                ok_type = isinstance(node, list) and all(isinstance(x, str) for x in node)
                keys = [variant_key(x) for x in node] if ok_type else None
                if ok_type and any(k is None for k in keys):
                    continue  # an unparsable name: left UNRESOLVED
                LL.rows.append({"item": label, "kind": "names", "mine": mv, "production": node,
                                "production_path": f"{LL.name}:" + "/".join(p),
                                "agree": ok_type and sorted(keys) == sorted(variant_key(x) for x in mv)})
                if ok_type:
                    LL.consumed.add(tuple(p))
            elif what == "holm":
                if not isinstance(node, dict):
                    LL.row(label, "exact", mv.get("decision"), p)
                    continue
                for f in ("p", "k", "B", "threshold", "interval", "level", "decision"):
                    LL.require(f"{label}:{f}", p + (f,), kind_of(f), mv.get(f))
            else:
                LL.row(label, "exact", mv, p)

    per_test(("labels",), fam.get("robust_labels", {}), "value")
    per_test(("decisions_kappa3_replace",), {d["test"]: d for d in fam["holm_at_kappa_robust"]}, "holm")
    per_test(("family_members",), family_names(mine, "replace"), "names")
    per_test(("diagnostics", "frozen_boolean_robust_to_the_sub_fine_residual"),
             fam.get("frozen_boolean_equivalent_diagnostic", {}), "value")
    per_test(("diagnostics", "keep_both", "labels"), fam["keep_both_kappa3_diagnostic"]["labels"], "value")
    per_test(("diagnostics", "keep_both", "family"), family_names(mine, "retain"), "names")
    return LL


def account(ledger: Ledger, doc_name: str):
    """Every leaf of a production document: consumed, excluded by an anchored pattern, or unresolved."""
    unresolved, excl = [], []
    for p, v in walk(ledger.doc):
        if ledger.is_consumed(p):
            continue
        reason = excluded(doc_name, p, v)
        if reason:
            excl.append({"path": f"{doc_name}:" + "/".join(p), "reason": reason})
        else:
            unresolved.append({"path": f"{doc_name}:" + "/".join(p), "value": v})
    return unresolved, excl


def compare(mine: dict, prod: dict, labels_doc: dict | None = None, prod_sha256: str | None = None,
            labels_missing_reason: str | None = None) -> dict:
    L = compare_evaluate(mine, prod)
    unresolved, excl = account(L, "joint-evaluate.json")
    rows, missing = list(L.rows), list(L.missing)
    if labels_doc is None:
        missing.append(f"robust-labels.json ({labels_missing_reason or 'not given'})")
    else:
        LL = compare_labels_doc(mine, labels_doc, prod_sha256)
        u2, e2 = account(LL, "robust-labels.json")
        rows += LL.rows
        missing += LL.missing
        unresolved += u2
        excl += e2
    bad = [r for r in rows if not r["agree"]]
    verdict = "DISCREPANT" if bad else ("INCOMPLETE" if missing or unresolved else "AGREE")
    return {"schema": "s5p-recompute-compare/3", "verdict": verdict, "items": len(rows),
            "agree": len(rows) - len(bad), "discrepancies": bad, "not_located": missing,
            "unresolved_production_leaves": unresolved,
            "excluded_by_scope": {"paths": excl, "scope": {d: [["/".join(p), r] for p, r in v]
                                                           for d, v in EXCLUDED_SCOPE.items()}},
            "rows": rows}


EXIT = {"AGREE": 0, "DISCREPANT": 1, "INCOMPLETE": 2, "ERROR": 3}


def compare_files(mine_path: str, prod_path: str, out_path: str, labels_path: str | None = None) -> int:
    out = Path(out_path)
    try:
        if out.exists():
            out.unlink()  # a failed run must never leave an earlier report in place
    except OSError as exc:
        print(f"ERROR: cannot remove the earlier report {out_path}: {exc}")
        return EXIT["ERROR"]
    try:
        mine = json.loads(Path(mine_path).read_text())
        prod_bytes = Path(prod_path).read_bytes()
        prod = json.loads(prod_bytes)
        labels, why = None, None
        if labels_path:
            if Path(labels_path).exists():
                labels = json.loads(Path(labels_path).read_text())
            else:
                why = f"file does not exist: {labels_path}"
        rep = compare(mine, prod, labels, hashlib.sha256(prod_bytes).hexdigest(), why)
    except Exception as exc:  # noqa: BLE001 - any failure is an ERROR verdict, never a comparison result
        rep = {"schema": "s5p-recompute-compare/3", "verdict": "ERROR", "error": f"{type(exc).__name__}: {exc}"}
    rep["inputs"] = {"mine": mine_path, "production": prod_path, "robust_labels": labels_path}
    try:
        out.write_text(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n")
    except OSError as exc:
        print(f"ERROR: cannot write the report {out_path}: {exc} (verdict would have been {rep['verdict']})")
        return EXIT["ERROR"]
    if rep["verdict"] == "ERROR":
        print(f"ERROR: {rep['error']}; wrote {out_path}")
    else:
        print(f"{rep['verdict']}: {rep['agree']}/{rep['items']} rows agree; {len(rep['discrepancies'])} "
              f"discrepancies; {len(rep['unresolved_production_leaves'])} unresolved leaves; "
              f"{len(rep['not_located'])} required items not located; wrote {out_path}")
    return EXIT[rep["verdict"]]
