"""Compare an s5p_recompute output with production's ``stage7/joint/joint-evaluate.json`` (and ``robust-labels.json``).

Production's nesting was not read from its code: only the key names its output writes (``tests``, ``T_total_obs``,
``total``/``shape`` with ``p``/``k``/``B``, ``variants``, ``decisions``, ``holm_point``, ``decisions_robust_kappa``,
``robust_to_the_sub_fine_residual``, ``power``, ...). The matcher therefore locates quantities by key name.

**Every production leaf must be accounted for.** A leaf is either CONSUMED by a comparison row (agree or discrepancy),
or EXCLUDED by the explicit metadata scope ``EXCLUDED_SCOPE`` below (each entry with its reason), or it is UNRESOLVED.
An unresolved leaf is a mapping gap, never an agreement. Examples: a key the matcher does not know, a variant name
without a recompute counterpart, or an A7 label pending the kappa = 3 variant-set question.

Verdicts and exit codes:
- AGREE (exit 0): every row agrees, nothing expected is missing, and no leaf is unresolved.
- DISCREPANT (exit 1): at least one row disagrees.
- INCOMPLETE (exit 2): no row disagrees, but something expected is not located or a leaf is unresolved. Extend the
  mapping, or rule the pending question, and re-run.

Agreement rules: counts (k, B, n) exactly; p-values and interval ends to 1e-12 absolute; statistics to 1e-8
relative; labels, booleans and digests exactly.
"""
from __future__ import annotations

import json
from pathlib import Path

TESTS = ("total", "shape")
UNRESOLVED_VS = "UNRESOLVED: kappa = 3 variant set (A7-VS)"

# Optional metadata: excluded from the agreement verdict by key name (at any depth), each with its reason. Anything
# not listed here is required.
EXCLUDED_SCOPE = {
    "schema": "format identifier, not a computed quantity",
    "utc": "timestamp",
    "files_first_last": "input path echo",
    "path": "input path echo (the recompute enforces the design's declared digests at load)",
    "sha256": "input digest echo (the recompute refuses any input whose digest differs from the design's)",
    "code_sha256": "producer identity",
    "mode": "echo of the frozen design's process-shift mode (the design's sha256 is compared)",
    "kappa": "echo of the frozen design's kappa (the design's sha256 is compared)",
    "kappa_robust": "echo of the frozen design's kappa_robust (the design's sha256 is compared)",
    "reason": "free text",
    "lateral_symmetry": "V-construction diagnostic, frozen with V (V's sha256 is compared)",
    "shrinkage": "V-construction metadata, frozen with V (V's sha256 is compared)",
    "median_rel_sd": "V-construction metadata, frozen with V (V's sha256 is compared)",
}


def walk(node, path=()):
    """Every leaf with its path; a list of scalars is one leaf, a list of containers is walked."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, path + (str(k),))
    elif isinstance(node, list) and node and all(isinstance(x, (dict, list)) for x in node):
        for i, v in enumerate(node):
            yield from walk(v, path + (str(i),))
    else:
        yield path, node


def agree(kind, a, b):
    if a is None or b is None:
        return False
    if isinstance(a, list) or isinstance(b, list):
        if not (isinstance(a, list) and isinstance(b, list)) or len(a) != len(b):
            return False
        return all(agree(kind, x, y) for x, y in zip(a, b))
    if kind == "count":
        return (isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool)
                and not isinstance(b, bool) and float(a) == float(b))
    if kind == "p":
        return abs(float(a) - float(b)) <= 1e-12
    if kind == "stat":
        a, b = float(a), float(b)
        return a == b or abs(a - b) <= 1e-8 * max(abs(a), abs(b))
    return a == b


def kind_of(key: str) -> str:
    if key in ("k", "B", "n", "domain_cells", "count", "n_present", "n_declared", "min_B", "max_B", "step"):
        return "count"
    if key.startswith("T") or key in ("mean", "median", "sd", "magnitude", "a", "se", "a_over_se", "bias_norm_W"):
        return "stat"
    if key in ("p", "interval", "power", "p_min", "p_max", "p_median", "min", "max", "threshold"):
        return "p"
    return "exact"


class Ledger:
    """Comparison rows plus the set of production leaf paths they consumed."""

    def __init__(self, doc):
        self.doc = doc
        self.rows, self.consumed, self.missing, self.pending = [], set(), [], []

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
        theirs = self.get(path)
        self.rows.append({"item": label, "kind": kind, "mine": mine, "production": theirs,
                          "production_path": "/".join(path), "agree": agree(kind, mine, theirs)})
        self.consumed.add(tuple(path))

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


def excluded(path):
    for p in path:
        if p in EXCLUDED_SCOPE:
            return p
    return None


def locate_null(prod, key):
    """The shortest production path ending at ``key`` whose dict holds the null's statistics."""
    best = None

    def visit(node, path):
        nonlocal best
        if isinstance(node, dict):
            for k, v in node.items():
                p = path + (str(k),)
                if k == key and isinstance(v, dict) and ("T_total_obs" in v or "T_shape_obs" in v or any(
                        isinstance(v.get(t), dict) and "p" in v[t] for t in TESTS)):
                    if best is None or len(p) < len(best):
                        best = p
                visit(v, p)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                visit(v, path + (str(i),))

    visit(prod, ())
    return best


def compare(mine: dict, prod: dict, labels_doc: dict | None = None) -> dict:
    L = Ledger(prod)
    for pk, mv in (("design_sha256", (mine.get("inputs") or {}).get("design_sha256")),
                   ("v_sha256", ((mine.get("provenance") or {}).get("V") or {}).get("sha256"))):
        if pk in prod:
            L.row(pk, "exact", mv, (pk,))
    if "names" in prod:
        L.row("names", "exact", mine.get("names"), ("names",))
    for key, rec in mine["nulls"].items():
        base = locate_null(prod, key)
        if base is None:
            L.missing.append(key)
            continue
        for t, pk in (("total", "T_total_obs"), ("shape", "T_shape_obs")):
            if L.get(base + (pk,)) is not None:
                L.row(f"{key}:{t}:T_obs", "stat", rec["observed_T"][t], base + (pk,))
        if L.get(base + ("domain_cells",)) is not None:
            L.row(f"{key}:domain_cells", "count", rec["domain_cells"], base + ("domain_cells",))
        L.same_names(f"{key}:process_shift", rec.get("process_shift") or {}, base + ("process_shift",))
        for t in TESTS:
            mt = rec["tests"][t]
            L.same_names(f"{key}:{t}:claim", mt, base + (t,), skip=("variants", "unshifted"))
            if isinstance(L.get(base + (t, "unshifted")), dict):
                L.same_names(f"{key}:{t}:unshifted", mt.get("unshifted") or {}, base + (t, "unshifted"))
            for stat in ("median", "sd"):
                pk = f"null_T_{t}_{stat}"
                if L.get(base + (pk,)) is not None and "null_T_summary" in rec:
                    L.row(f"{key}:{pk}", "stat", rec["null_T_summary"][t][stat], base + (pk,))
            jit = mt.get("observed_jitter") or {}
            for stat, mk in (("min", "p_min"), ("median", "p_median"), ("max", "p_max"), ("n", "n")):
                p = L.first(base + ("observed_jitter_p", t, stat), base + (t, "observed_jitter_p", stat))
                if p is not None:
                    L.row(f"{key}:{t}:observed_jitter_p:{stat}", "count" if stat == "n" else "p", jit.get(mk), p)
            for pk, mine_map in (("implied_size_of_unshifted_test", mt.get("implied_size") or {}),
                                 ("median_shift_in_null_sd", mt.get("median_shift_in_null_sd") or {})):
                for lbl, mv in mine_map.items():
                    p = L.first(base + (pk, lbl, t), base + (pk, t, lbl), base + (t, pk, lbl))
                    if p is not None:
                        L.row(f"{key}:{t}:{pk}[{lbl}]", "p" if pk.startswith("implied") else "stat", mv, p)
            for vkey in ("variants", "robustness_variants"):
                pv = L.get(base + (vkey,))
                if pv is None:
                    continue
                mine_var = (mt.get("variants") or {}) if vkey == "variants" else \
                    ((mt.get("robust_kappa3_retain_kappa2") or {}).get("variants") or {})
                entries = pv.items() if isinstance(pv, dict) else enumerate(pv)
                for lbl, ent in entries:
                    if not isinstance(ent, dict) or not isinstance(ent.get(t), dict):
                        continue
                    name = str(ent.get("label", ent.get("variant", lbl)))
                    m = mine_var.get(name)
                    if m is None:
                        continue  # left UNRESOLVED: no recompute variant of that name
                    for f in ("k", "p"):
                        if f in ent[t]:
                            L.row(f"{key}:{t}:{vkey}[{name}]:{f}", kind_of(f), m.get(f),
                                  base + (vkey, str(lbl), t, f))
    mine_dec = {d["test"]: d for d in mine["family"]["decisions"]}
    mine_rob = {d["test"]: d for d in mine["family"]["holm_at_kappa_robust"]}
    for field, source, attr in (("decisions", mine_dec, "decision"), ("holm_point", mine_dec, "holm_point"),
                                ("decisions_robust_kappa", mine_rob, "decision")):
        if field not in prod:
            L.missing.append(field)
            continue
        for test, md in source.items():
            null, t = test.split(":")
            p = L.first((field, null, t), (field, test))
            if p is None:
                L.missing.append(f"{field}:{test}")
                continue
            if md.get(attr) == UNRESOLVED_VS:
                L.pending.append(f"{field}:{test}")
                continue
            node = L.get(p)
            if isinstance(node, dict):
                leafk = "decision" if "decision" in node else "label"
                L.row(f"{field}:{test}", "exact", md.get(attr), p + (leafk,))
                L.same_names(f"{field}:{test}", md, p, skip=(leafk, "test"))
            else:
                L.row(f"{field}:{test}", "exact", md.get(attr), p)
    if "robust_to_the_sub_fine_residual" not in prod:
        L.missing.append("robust_to_the_sub_fine_residual")
    else:
        for test, mv in mine["family"].get("robust_boolean_equivalent", {}).items():
            null, t = test.split(":")
            p = L.first(("robust_to_the_sub_fine_residual", null, t), ("robust_to_the_sub_fine_residual", test))
            if p is None:
                L.missing.append(f"robust_to_the_sub_fine_residual:{test}")
            elif mv == UNRESOLVED_VS:
                L.pending.append(f"robust_to_the_sub_fine_residual:{test}")
            else:
                L.row(f"robust_to_the_sub_fine_residual:{test}", "exact", mv, p)
    if isinstance(prod.get("not_calibrated"), list):
        L.row("not_calibrated", "exact", sorted(k for k, r in mine["nulls"].items() if r["B"] == 0),
              ("not_calibrated",))
    ppow = prod.get("power") if isinstance(prod.get("power"), dict) else {}
    for sk, mp in mine.get("power", {}).items():
        if sk not in ppow:
            L.missing.append(f"power:{sk}")
            continue
        base = ("power", sk)
        for pk, mv, kd in (("n", mp.get("n_present"), "count"), ("declared", mp.get("n_declared"), "count"),
                           ("null", mp.get("null"), "exact"), ("incomplete", not mp.get("complete", False), "exact")):
            if L.get(base + (pk,)) is not None:
                L.row(f"power:{sk}:{pk}", kd, mv, base + (pk,))
        for t in TESTS:
            for lvl in ("0.05", "0.005"):
                for mine_rule, prod_rule in (("rank_unshifted", "unshifted"), ("rank_claim", "claim_rule"),
                                             ("determined_claim", "claim_rule_determined")):
                    mr = mp.get(t, {}).get(lvl, {}).get(mine_rule) or {}
                    p = L.first(base + (t, prod_rule, lvl), base + (prod_rule, t, lvl),
                                base + ("levels", lvl, t, prod_rule), base + (t, lvl, prod_rule),
                                base + (prod_rule, lvl, t))
                    if p is None:
                        continue
                    if isinstance(L.get(p), dict):
                        L.same_names(f"power:{sk}:{t}:{lvl}:{mine_rule}", mr, p)
                    else:
                        L.row(f"power:{sk}:{t}:{lvl}:{mine_rule}", "p", mr.get("power"), p)
    unresolved, excl = [], {}
    label_rows = []
    if labels_doc is None:
        L.missing.append("robust-labels.json (not given)")
    else:
        LL = Ledger(labels_doc)
        if labels_doc.get("labels") is None:
            L.missing.append("robust-labels.json:labels")
        else:
            for test, mv in mine["family"].get("robust_labels", {}).items():
                null, t = test.split(":")
                p = LL.first(("labels", null, t), ("labels", test))
                if p is None:
                    L.missing.append(f"robust_labels:{test}")
                elif mv == UNRESOLVED_VS:
                    L.pending.append(f"robust_labels:{test}")
                else:
                    node = LL.get(p)
                    LL.row(f"robust_labels:{test}", "exact", mv, p + (("label",) if isinstance(node, dict) else ()))
            for p, v in walk(labels_doc["labels"], ("labels",)):
                if not LL.is_consumed(p) and not excluded(p):
                    unresolved.append({"path": "robust-labels.json/" + "/".join(p), "value": v})
        label_rows = LL.rows
    for p, v in walk(prod):
        if L.is_consumed(p):
            continue
        e = excluded(p)
        if e:
            excl[e] = excl.get(e, 0) + 1
            continue
        unresolved.append({"path": "/".join(p), "value": v})
    rows = L.rows + label_rows
    bad = [r for r in rows if not r["agree"]]
    if bad:
        verdict = "DISCREPANT"
    elif L.missing or unresolved or L.pending:
        verdict = "INCOMPLETE"
    else:
        verdict = "AGREE"
    return {"schema": "s5p-recompute-compare/2", "verdict": verdict, "items": len(rows),
            "agree": len(rows) - len(bad), "discrepancies": bad, "not_located": L.missing,
            "unresolved_production_leaves": unresolved, "pending_ruling": L.pending,
            "excluded_by_scope": {"counts": excl, "scope": EXCLUDED_SCOPE}, "rows": rows}


EXIT = {"AGREE": 0, "DISCREPANT": 1, "INCOMPLETE": 2}


def compare_files(mine_path: str, prod_path: str, out_path: str, labels_path: str | None = None) -> int:
    mine = json.loads(Path(mine_path).read_text())
    prod = json.loads(Path(prod_path).read_text())
    labels = json.loads(Path(labels_path).read_text()) if labels_path else None
    rep = compare(mine, prod, labels)
    rep["inputs"] = {"mine": mine_path, "production": prod_path, "robust_labels": labels_path}
    Path(out_path).write_text(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n")
    print(f"{rep['verdict']}: {rep['agree']}/{rep['items']} rows agree; {len(rep['discrepancies'])} discrepancies; "
          f"{len(rep['unresolved_production_leaves'])} unresolved leaves; {len(rep['pending_ruling'])} pending a "
          f"ruling; not located: {rep['not_located']}; wrote {out_path}")
    return EXIT[rep["verdict"]]
