#!/usr/bin/env python3
"""Tabulate every validator's tolerances and flag functions that MIX absolute and relative units.

THE HEURISTIC THIS MECHANISES. Read a validator's checks against each other before reading any of them
against the physics. Three times in two days a guard was written in different units from its neighbours,
and twice the correct scale was two lines away:

  BEN-044  `combine_cstat_bkgsub_100rep.compute_cstat` -- symmetry `> 1e-30` ABSOLUTE beside a PSD check
           written relative, on a matrix whose entries are ~1e-79.
  BEN-070  `p4_lib` covariance validator -- symmetry `/max(1e-300, max|C|)` and PSD `-ratio*abs(ev[-1])`
           both RELATIVE, then the diagonal `>= -1e-30` ABSOLUTE.
  (live)   `p4_validate_active_lateral_fps.mat_gates` -- lines 66 and 68 relative, line 70 absolute, in
           one function, with the eigenvalues already in scope.

The inconsistency is far easier to see than either check's correctness, which is what makes it a
mechanisable review rule rather than a judgement call.

CLASSIFICATION, done on the AST rather than by regex, because `-1e-9 * max(eig, 1.0)` and
`abs(a-b)/total < 1e-9` are the same characters in different shapes and regexes get this wrong. For each
comparison against a numeric tolerance:

  RELATIVE  the tolerance is multiplied/divided by a scale (`1e-12 * abs(ev[-1])`), OR the compared
            quantity is itself a quotient (`max|C-C^T| / denom < tol`), OR the compared name/call
            announces a ratio (`rel_asymmetry`, `_relmax(...)`, `..._over_gap`).
  ABSOLUTE  a bare literal compared against a raw quantity.
  FLOOR     the literal is an argument of `max()`/`min()` beside another expression -- a div-by-zero
            guard like `max(1e-300, max|C|)`, not a tolerance. Counted as neither.

TOLERANCE CUT: |literal| <= 1e-2. This keeps real tolerances (1e-30, 1e-12, 5e-4) and excludes physics
BARS (recovery >= 0.80, floor/gap <= 0.10, residual/gap <= 0.20), which are absolute *by specification*
and would otherwise flag every criterion function spuriously. The cut is stated because it is the one
judgement in the tool.

POWER: `--power` requires the sweep to flag the known instances. One of them
(`p4_validate_active_lateral_fps.mat_gates`) is LIVE in the tree, so this tool has a real positive control
rather than only synthetic ones -- and if a future repair fixes it, the power test will say so instead of
silently passing.
"""
import argparse
import ast
import os
import sys

TOL_CUT = 1e-2
REL_NAME_HINTS = ("rel", "ratio", "frac", "_over_", "relmax", "relerr", "pct", "percent")


def _num(node):
    """Return the float value if `node` is a numeric literal or a negated one, else None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
            and not isinstance(node.value, bool):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = _num(node.operand)
        return None if v is None else -v
    return None


def _names_in(node):
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.append(n.id)
        elif isinstance(n, ast.Attribute):
            out.append(n.attr)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
    return [s.lower() for s in out]


def _announces_ratio(node):
    return any(h in s for s in _names_in(node) for h in REL_NAME_HINTS)


def _has_division(node):
    return any(isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div) for n in ast.walk(node))


def _is_floor_literal(parents, node):
    """True if this literal sits inside max()/min() alongside another argument."""
    p = parents.get(id(node))
    while p is not None:
        if isinstance(p, ast.Call) and isinstance(p.func, ast.Name) \
                and p.func.id in ("max", "min") and len(p.args) >= 2:
            return True
        if isinstance(p, ast.Compare):
            return False
        p = parents.get(id(p))
    return False


def _scaled(parents, node):
    """True if the literal is multiplied or divided by something (i.e. a relative tolerance)."""
    p = parents.get(id(node))
    while p is not None and not isinstance(p, ast.Compare):
        if isinstance(p, ast.BinOp) and isinstance(p.op, (ast.Mult, ast.Div)):
            other = p.right if p.left is node or _contains(p.left, node) else p.left
            if _num(other) is None:          # scaled by an expression, not by another literal
                return True
        node = p
        p = parents.get(id(p))
    return False


def _contains(hay, needle):
    return any(n is needle for n in ast.walk(hay))


def classify_function(fn, src_lines, parents):
    """Return list of dicts, one per tolerance comparison inside `fn`."""
    rows = []
    for cmp_node in [n for n in ast.walk(fn) if isinstance(n, ast.Compare)]:
        operands = [cmp_node.left] + list(cmp_node.comparators)
        lits = [(o, _num(o)) for o in operands]
        lits = [(o, v) for o, v in lits if v is not None and v != 0.0 and abs(v) <= TOL_CUT]
        # a literal may also be nested, e.g. `ev[0] >= -1e-12 * abs(ev[-1])`
        if not lits:
            for o in operands:
                for n in ast.walk(o):
                    v = _num(n)
                    if v is not None and v != 0.0 and abs(v) <= TOL_CUT:
                        lits.append((n, v))
                        break
        if not lits:
            continue
        lit_node, tol = lits[0]
        if _is_floor_literal(parents, lit_node):
            kind = "FLOOR"
        elif _scaled(parents, lit_node):
            kind = "RELATIVE"
        else:
            other = [o for o in operands if not _contains(o, lit_node)]
            if any(_has_division(o) or _announces_ratio(o) for o in other):
                kind = "RELATIVE"
            else:
                kind = "ABSOLUTE"
        ln = cmp_node.lineno
        rows.append({"line": ln, "tol": tol, "kind": kind,
                     "src": src_lines[ln - 1].strip()[:130] if ln - 1 < len(src_lines) else ""})
    return rows


def sweep_file(path, rel):
    try:
        src = open(path, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except (OSError, SyntaxError):
        return []
    lines = src.split("\n")
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node
    out = []
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        rows = classify_function(fn, lines, parents)
        kinds = {r["kind"] for r in rows}
        if "ABSOLUTE" in kinds and "RELATIVE" in kinds:
            out.append({"file": rel, "func": fn.name, "lineno": fn.lineno, "rows": rows})
    return out


def sweep(root):
    skip = {".git", "__pycache__", "worktrees", "node_modules", ".pytest_cache"}
    hits, n_files = [], 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for fn in filenames:
            if not fn.endswith(".py") or fn == os.path.basename(__file__):
                continue
            p = os.path.join(dirpath, fn)
            if os.path.islink(p):
                continue
            rel = os.path.relpath(p, root)
            if rel.split(os.sep)[0] == "orchestration":
                continue
            n_files += 1
            hits.extend(sweep_file(p, rel))
    return hits, n_files


KNOWN_LIVE = ("p4_validate_active_lateral_fps.py", "mat_gates")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    _here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(_here)))
    ap.add_argument("--min-files", type=int, default=200)
    ap.add_argument("--markdown", action="store_true", help="emit the table as markdown")
    a = ap.parse_args()

    hits, n_files = sweep(a.root)
    if n_files < a.min_files:
        raise SystemExit(f"[units] visited only {n_files} .py files under {a.root} (floor "
                         f"{a.min_files}); a sweep that matches nothing reports success, so this fails "
                         f"closed rather than printing a clean table.")

    # POWER: the live instance must be found, or the classifier has regressed.
    found_live = any(h["file"].endswith(KNOWN_LIVE[0]) and h["func"] == KNOWN_LIVE[1] for h in hits)
    print(f"POWER (live positive control {KNOWN_LIVE[0]}:{KNOWN_LIVE[1]}): "
          f"{'FOUND' if found_live else '*** NOT FOUND ***'}")
    if not found_live:
        print("  -> either that instance was repaired (good: update KNOWN_LIVE and re-verify) or the "
              "classifier has regressed (bad). Refusing to present the table until resolved.")
        raise SystemExit(3)
    print()

    hits.sort(key=lambda h: (h["file"], h["lineno"]))
    if a.markdown:
        print(f"| file | function | absolute checks | relative checks | floors |")
        print(f"|---|---|---|---|---|")
        for h in hits:
            ab = [r for r in h["rows"] if r["kind"] == "ABSOLUTE"]
            re_ = [r for r in h["rows"] if r["kind"] == "RELATIVE"]
            fl = [r for r in h["rows"] if r["kind"] == "FLOOR"]
            f_ab = "; ".join(f"L{r['line']} `{r['tol']:g}`" for r in ab)
            f_re = "; ".join(f"L{r['line']} `{r['tol']:g}`" for r in re_)
            print(f"| `{h['file']}` | `{h['func']}` | {f_ab} | {f_re} | {len(fl)} |")
    else:
        print(f"=== {len(hits)} function(s) MIX absolute and relative tolerances "
              f"({n_files} .py files) ===")
        for h in hits:
            print(f"\n{h['file']}:{h['lineno']}  {h['func']}()")
            for r in sorted(h["rows"], key=lambda r: r["line"]):
                print(f"  L{r['line']:<5} {r['kind']:<9} tol={r['tol']:<10g} {r['src']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
