"""Compare an s5p_recompute output with production's ``stage7/joint/joint-evaluate.json``.

Production's nesting was not read from its code (only the key names its output uses: ``tests``, ``T_total_obs``,
``T_shape_obs``, ``total``/``shape`` with ``p``/``k``/``B``, ``decisions``, ``holm_point``, ``power``, ...), so
the matcher locates, for each null, the production sub-tree keyed by the null's name, and for each quantity the
nearest leaf with the expected key name. Every production numeric leaf under a null that no rule maps is listed
as UNMAPPED, so a mapping gap is visible rather than read as agreement.

Agreement rules: counts (k, B) exactly; p-values to 1e-12 absolute; statistics to 1e-8 relative; decision strings
exactly. Exit 0 when every mapped item agrees and something was mapped for every null, 1 on any discrepancy, 2 if
a null or the decisions could not be located.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

TESTS = ("total", "shape")


def walk(node, path=()):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, path + (str(k),))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, path + (str(i),))
    else:
        yield path, node


def find_subtrees(node, key, path=()):
    """Every dict value stored under ``key`` (any depth)."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key and isinstance(v, dict):
                yield path + (k,), v
            yield from find_subtrees(v, key, path + (str(k),))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from find_subtrees(v, key, path + (str(i),))


def agree(kind, a, b):
    if a is None or b is None:
        return False
    if kind == "count":
        return int(a) == int(b)
    if kind == "p":
        return abs(float(a) - float(b)) <= 1e-12
    if kind == "stat":
        a, b = float(a), float(b)
        return a == b or abs(a - b) <= 1e-8 * max(abs(a), abs(b))
    return a == b


def item(rows, label, kind, mine, theirs, where):
    rows.append({"item": label, "kind": kind, "mine": mine, "production": theirs, "production_path": where,
                 "agree": agree(kind, mine, theirs)})


def leaf(tree, *names):
    """The value at the first matching nested path of ``names`` (a name may be a tuple of alternatives)."""
    cur = tree
    for n in names:
        alts = n if isinstance(n, tuple) else (n,)
        for a in alts:
            if isinstance(cur, dict) and a in cur:
                cur = cur[a]
                break
        else:
            return None
    return cur


def compare(mine: dict, prod: dict) -> dict:
    rows, unmapped, missing = [], {}, []
    for key, rec in mine["nulls"].items():
        subs = [(p, s) for p, s in find_subtrees(prod, key)
                if "T_total_obs" in s or "T_shape_obs" in s or any(isinstance(s.get(t), dict) and "p" in s[t]
                                                                   for t in TESTS)]
        if not subs:
            missing.append(key)
            continue
        path, sub = max(subs, key=lambda s: len(json.dumps(s[1])))
        where = "/".join(path)
        used = set()
        for t, pk in (("total", "T_total_obs"), ("shape", "T_shape_obs")):
            if pk in sub:
                item(rows, f"{key}:{t}:T_obs", "stat", rec["observed_T"][t], sub[pk], f"{where}/{pk}")
                used.add((pk,))
        if "domain_cells" in sub:
            item(rows, f"{key}:domain_cells", "count", rec["domain_cells"], sub["domain_cells"], where)
            used.add(("domain_cells",))
        for t in TESTS:
            mt = rec["tests"][t]
            pt = sub.get(t)
            if isinstance(pt, dict):
                for f, kind in (("p", "p"), ("k", "count"), ("B", "count")):
                    if f in pt:
                        item(rows, f"{key}:{t}:claim_{f}", kind, mt.get(f), pt[f], f"{where}/{t}/{f}")
                        used.add((t, f))
            for vkey, mine_var in (("variants", mt.get("variants", {})),
                                   ("robustness_variants", (mt.get("robust_kappa3") or {}).get("variants", {}))):
                pv = sub.get(vkey)
                if pv is None:
                    continue
                entries = pv.items() if isinstance(pv, dict) else enumerate(pv)
                for lbl, ent in entries:
                    if not isinstance(ent, dict):
                        continue
                    v = ent.get(t) if isinstance(ent.get(t), dict) else None
                    if v is None:
                        continue
                    name = str(ent.get("label", ent.get("variant", lbl)))
                    m = mine_var.get(name)
                    for f, kind in (("k", "count"), ("p", "p")):
                        if f in v:
                            item(rows, f"{key}:{t}:{vkey}[{name}]:{f}", kind, m.get(f) if m else None, v[f],
                                 f"{where}/{vkey}/{lbl}/{t}/{f}")
        for p, val in walk(sub):
            if isinstance(val, (int, float)) and not isinstance(val, bool) and (p[:1] not in used and p[:2] not in used):
                if p[0] not in ("variants", "robustness_variants"):
                    unmapped.setdefault(key, []).append({"path": where + "/" + "/".join(p), "value": val})
    # family decisions
    dec_rows = []
    mine_dec = {d["test"]: d for d in mine["family"]["decisions"]}
    for field, mine_field in (("decisions", "decision"), ("holm_point", "holm_point")):
        pd = prod.get(field)
        if pd is None:
            missing.append(field)
            continue
        for test, md in mine_dec.items():
            null, t = test.split(":")
            theirs = leaf(pd, null, t)
            if theirs is None and isinstance(pd, dict):
                theirs = pd.get(test)
            if isinstance(theirs, dict):
                theirs = theirs.get("decision", theirs.get("label"))
            item(dec_rows, f"{field}:{test}", "exact", md.get(mine_field), theirs, field)
    pr = prod.get("decisions_robust_kappa")
    if pr is not None:
        mine_rob = {d["test"]: d for d in mine["family"]["holm_at_kappa_robust"]}
        for test, md in mine_rob.items():
            null, t = test.split(":")
            theirs = leaf(pr, null, t)
            if isinstance(theirs, dict):
                theirs = theirs.get("decision", theirs.get("label"))
            item(dec_rows, f"decisions_robust_kappa:{test}", "exact", md["decision"], theirs, "decisions_robust_kappa")
    # power
    pow_rows = []
    ppow = prod.get("power", {})
    for sk, mp in mine.get("power", {}).items():
        theirs = ppow.get(sk) if isinstance(ppow, dict) else None
        if theirs is None:
            missing.append(f"power:{sk}")
            continue
        item(pow_rows, f"power:{sk}:n", "count", mp.get("n_present"), theirs.get("n"), f"power/{sk}/n")
        for t in TESTS:
            for lvl in ("0.05", "0.005"):
                for mine_rule, prod_rule in (("rank_unshifted", "unshifted"), ("rank_claim", "claim_rule"),
                                             ("determined_claim", "claim_rule_determined")):
                    mv = (mp.get(t, {}).get(lvl, {}).get(mine_rule) or {}).get("power")
                    pv = None
                    for cand in (leaf(theirs, t, prod_rule, lvl), leaf(theirs, prod_rule, t, lvl),
                                 leaf(theirs, "levels", lvl, t, prod_rule), leaf(theirs, t, lvl, prod_rule)):
                        if cand is not None:
                            pv = cand
                            break
                    if isinstance(pv, dict):
                        pv = pv.get("power", pv.get("p"))
                    item(pow_rows, f"power:{sk}:{t}:{lvl}:{mine_rule}", "p", mv, pv, f"power/{sk}")
    allrows = rows + dec_rows + pow_rows
    bad = [r for r in allrows if not r["agree"]]
    return {"schema": "s5p-recompute-compare/1", "items": len(allrows), "agree": len(allrows) - len(bad),
            "discrepancies": bad, "not_located": missing, "unmapped_production_leaves": unmapped,
            "rows": allrows}


def compare_files(mine_path: str, prod_path: str, out_path: str) -> int:
    mine = json.loads(Path(mine_path).read_text())
    prod = json.loads(Path(prod_path).read_text())
    rep = compare(mine, prod)
    rep["inputs"] = {"mine": mine_path, "production": prod_path}
    Path(out_path).write_text(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n")
    print(f"{rep['agree']}/{rep['items']} items agree; {len(rep['discrepancies'])} discrepancies; "
          f"not located: {rep['not_located']}; wrote {out_path}")
    if rep["not_located"]:
        return 2
    return 0 if not rep["discrepancies"] else 1


def _finite(x):
    return isinstance(x, (int, float)) and math.isfinite(x)
