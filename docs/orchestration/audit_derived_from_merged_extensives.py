#!/usr/bin/env python3
"""Find every quantity DERIVED from two or more `hadd`-summed extensive TParameters.

THE CLASS THIS SWEEPS, and why it needs its own tool.

`FINDING-20260809-tparameter-merge-semantics.md` established that `hadd` sums `TParameter` by
default, and that summing is CORRECT for an extensive quantity (POT, event counts, censuses) and
wrong only for an intensive one or a flag. Twelve of the fifteen fields that transit a merge are
extensive and merge correctly.

That result has a blind spot, and it is the reason this second sweep exists:

    TWO EXTENSIVE FIELDS CAN EACH MERGE CORRECTLY WHILE A QUANTITY DERIVED FROM THEM DOES NOT.

    sum(dataPOTUsed) / sum(mcPOTUsed) is NOT the playlist-mixture-correct Data/MC ratio. Both
    operands are impeccable. Per-field merge-sensitivity review asks "is this field
    merge-sensitive?", gets `no` for both, and passes the quotient without ever looking at it.

That is J36 (`KNOWN_ISSUES`): per-playlist Data/MC ratios span 0.1707-0.2371, **38.9% max/min-1**,
against a global 0.2124, giving a **9.4% POT-weighted mean absolute mixture error**. It has been
open since 2026-08-01 as a "scoping decision owed", and it sits **two functions away** from an
explicit, correct, well-commented defence of trap #8 for `pTmu_fiducial_nucleons`. The defence
did not generalise to it because a per-field question cannot reach a two-field answer.

**Nobody has swept this class.** J36 is its only known member, and one member is not a size.

WHAT COUNTS AS A HIT. A binary operation in which at least one operand carries taint from a read
of a merged extensive field. Reported by shape, because the shapes fail differently:

  RATIO_OF_TWO_MERGED   both sides tainted, operator `/`, and the two sides' field sets are
                        DISJOINT. **This is the J36 shape and the only one that is a defect by
                        construction:** `sum(A)/sum(B)` for different A and B is a POT-weighted
                        mean over the merged inventory, not the per-playlist ratio a reader
                        expects, and nothing cancels.
  RATIO_COMMON_SCALE    both sides tainted, operator `/`, but the SAME field appears on both
                        sides -- a POT-scaled histogram over another POT-scaled histogram. The
                        scale cancels. Real taint, different semantics, not this class. Reported
                        rather than suppressed so the distinction is visible and auditable.
  SCALED_BY_MERGED      one side tainted, `*` or `/`. A normalisation; correct iff the other
                        operand spans the same inventory as the merged total.
  DIFF_/OFFSET_BY_MERGED  `+`/`-` involving a tainted operand. Usually benign; listed for
                        completeness because a difference of two sums over DIFFERENT inventories
                        is not.

TAINT, and its honest bound. AST-based, intraprocedural, **flow-sensitive with kill-on-reassign**:
  * a read is any expression containing a string literal naming a merged extensive field
    (`f.Get("dataPOTUsed")`, `d["mcPOT"]`, ...);
  * assignment propagates taint to the target name; reassignment from an untainted expression
    KILLS it;
  * taint flows through `.GetVal()`, `float(...)`, subscripts, tuples and simple calls.

The first version was flow-INsensitive, on the reasoning that over-reporting is the safe error
when sizing a class. That was wrong in a way worth recording: in a 200-line `main()` a short name
(`mc`, `d`, `m`) is bound to a POT scalar early and REBOUND to a histogram array later, and sticky
taint then reported `dat / mc` -- an ordinary data/MC histogram ratio -- as a merged-POT quotient.
It produced 17 "ratios" of which 11 were that. Two-thirds noise does not size a class, it
transfers the triage (BEN-071 rule 2). Killing taint on reassignment and requiring disjoint field
sets took it to 8, all genuine.

It does NOT cross function boundaries, so a helper returning a ratio and a caller consuming it are
two sites and only the first is found; and it cannot see taint arriving through a dict passed as
an argument. Both make this an UNDER-count, which is the direction to be wrong in when the
question is "is this class bigger than one?".

POWER (`--power`): the sweep must find `get_pot_scales` in
`2d-unfolding/unfold_2d_omnifold_unbinned.py` as a RATIO_OF_TWO_MERGED. That is J36, it is live in
the tree, and if a future repair fixes it the power test fails loudly and forces this table to be
regenerated rather than passing forever against a synthetic control.

Usage:
    python3 docs/orchestration/audit_derived_from_merged_extensives.py [--root .] [--power] [--json]
"""
import argparse
import ast
import json
import os
import re
import subprocess
import sys

# The extensive fields that transit a hadd, from the per-field sweep. Flags and intensives are
# excluded deliberately: they are already defects on their own and are covered by the other tool.
# `POTUsed` is included because it is the same quantity under an older name.
MERGED_EXTENSIVE = {
    "dataPOTUsed", "mcPOTUsed", "POTUsed",
    "dataPOT", "mcPOT",                      # the python-side names written by the unfold drivers
    "activeUniverseTruthEntrants", "activeUniverseTruthExits",
    "activeUniverseRecoEntrants", "activeUniverseRecoExits",
    "nTruthOnlyMisses",
}


def tracked_py(root):
    out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True).stdout
    return [f for f in out.splitlines() if f.endswith(".py")]


def _strings(node):
    """Every string literal anywhere inside an expression."""
    return {n.value for n in ast.walk(node)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def _names(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


class Scan(ast.NodeVisitor):
    """One pass per function; taint is a set of local names."""

    def __init__(self, rel, src):
        self.rel, self.src = rel, src
        self.hits = []

    def _fields_read(self, node):
        return _strings(node) & MERGED_EXTENSIVE

    def visit_FunctionDef(self, fn):
        # FLOW-SENSITIVE, with kill-on-reassign. The first version of this tool was
        # flow-insensitive over two passes, on the theory that over-reporting is the safe error
        # for a class being sized. It is not: in a 200-line `main()` a short name like `mc` or `d`
        # is bound to a POT value early and REBOUND to a histogram array later, and sticky taint
        # then flagged `dat / mc` -- a data/MC histogram ratio -- as a merged-POT quotient. Eleven
        # of seventeen "ratios" were that. A hit list that is two-thirds noise transfers the
        # triage instead of doing it (BEN-071), so taint is now killed when a name is reassigned
        # from an untainted expression, and sites are visited in source order.
        tainted = {}
        events = []
        for node in ast.walk(fn):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.BinOp)):
                events.append(node)
        events.sort(key=lambda n: (n.lineno, n.col_offset))

        for node in events:
            if isinstance(node, ast.BinOp):
                op = type(node.op).__name__
                if op not in ("Div", "Mult", "Sub", "Add"):
                    continue

                def side(e):
                    return self._fields_read(e) | {f for n in _names(e) if n in tainted
                                                   for f in tainted[n]}
                L, R = side(node.left), side(node.right)
                if not (L or R):
                    continue
                # THE DISCRIMINATOR for the J36 shape, and the one judgement in this tool.
                # J36 is `sum(A) / sum(B)` where A and B are DIFFERENT merged fields: each side
                # carries exactly one field and the two differ, so nothing cancels and the
                # quotient is a POT-weighted mean masquerading as a per-playlist ratio. When both
                # sides carry the SAME field, that field is a common scale applied to both
                # operands (a POT-scaled histogram divided by another POT-scaled histogram) and
                # it cancels -- real taint, different semantics, not this class.
                disjoint = bool(L and R and not (L & R))
                if L and R:
                    if op == "Div":
                        shape = "RATIO_OF_TWO_MERGED" if disjoint else "RATIO_COMMON_SCALE"
                    else:
                        shape = "DIFF_OF_TWO_MERGED"
                else:
                    shape = "SCALED_BY_MERGED" if op in ("Div", "Mult") else "OFFSET_BY_MERGED"
                self.hits.append({
                    "file": self.rel, "line": node.lineno, "function": fn.name,
                    "op": op, "shape": shape,
                    "fields": sorted(L | R),
                    "lhs_fields": sorted(L), "rhs_fields": sorted(R),
                    "both_sides": bool(L and R),
                    "source": self.src.splitlines()[node.lineno - 1].strip()[:130],
                })
                continue

            val = node.value
            if val is None:
                continue
            got = self._fields_read(val) | {f for n in _names(val) if n in tainted
                                            for f in tainted[n]}
            if isinstance(node, ast.AugAssign):
                targets = [node.target]
            elif isinstance(node, ast.AnnAssign):
                targets = [node.target]
            else:
                targets = node.targets
            for t in targets:
                for nm in ast.walk(t):
                    if isinstance(nm, ast.Name):
                        if got:
                            tainted.setdefault(nm.id, set()).update(got)
                        elif not isinstance(node, ast.AugAssign):
                            tainted.pop(nm.id, None)          # KILL: rebound to something else
        self.generic_visit(fn)

    visit_AsyncFunctionDef = visit_FunctionDef


CPP_EXTS = (".cpp", ".cxx", ".cc", ".C", ".h", ".hpp")


def scan_cpp(root):
    """C++ pass (2026-08-09, added because an unswept language is where a count hides).

    Deliberately NOT an AST pass. Only ONE tracked C++ file reads a merged extensive at all
    (`ExtractCrossSection.cpp` -- everything else WRITES them), so the population is small enough
    to enumerate by identifier and verify by eye, and a clang-level tool would be more machinery
    than the corpus justifies. Two stages: find every C++ read of a merged-extensive TParameter,
    then find every `/` on a line mentioning two identifiers bound from those reads.

    Bound, stated plainly: this finds ratios formed on ONE line from locally-named values. A ratio
    split across lines, or hidden behind a helper, is not found. Like the Python pass it is a
    floor."""
    out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True).stdout
    files = [f for f in out.splitlines() if f.endswith(CPP_EXTS)]
    reads, ratios = [], []
    for rel in files:
        try:
            raw = open(os.path.join(root, rel), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if not any(f in raw for f in MERGED_EXTENSIVE):
            continue
        local = set()
        lines = raw.splitlines()
        for i, line in enumerate(lines, 1):
            code = line.split("//")[0]
            if not code.strip():
                continue
            hit = [f for f in MERGED_EXTENSIVE if f'"{f}"' in code]
            # A READ is a GetIngredient/Get of the name, not a construction. The construction is
            # frequently SPLIT across lines --
            #     auto pNMisses = new TParameter<long>(
            #         "nTruthOnlyMisses", nTruthOnlyMisses);
            # -- so testing the current line alone reported five writes as reads. Look back over
            # the preceding continuation lines until a statement boundary.
            if hit:
                j, is_write = i - 2, False
                while j >= 0:
                    prev = lines[j].split("//")[0]
                    # ONLY `new TParameter` marks a construction. An earlier version also keyed
                    # on `TParameter<`, which matches `GetIngredient<TParameter<double>>` -- i.e.
                    # the READ idiom -- and silently reclassified a real read as a write, taking
                    # the count from 2 to 1 and the ratios from 2 to 0. Over-correcting a false
                    # positive into a false negative is the worse of the two errors here.
                    if "new TParameter" in prev:
                        is_write = True
                    if prev.rstrip().endswith(";") or not prev.strip():
                        break
                    j -= 1
                if is_write or "new TParameter" in code:
                    hit = []
            if hit:
                reads.append({"file": rel, "line": i, "fields": sorted(hit),
                              "source": code.strip()[:130]})
                for nm in re.findall(r"\b([A-Za-z_]\w*)\s*=", code):
                    local.add(nm)
            if "/" in code and local:
                present = [n for n in local if re.search(rf"\b{re.escape(n)}\b", code)]
                if len(present) >= 2 and re.search(r"\b\w+\s*/\s*\w+", code):
                    ratios.append({"file": rel, "line": i, "locals": sorted(present),
                                   "source": code.strip()[:130]})
    return {"reads": reads, "ratios": ratios}


def summary(root="."):
    hits = []
    for rel in tracked_py(root):
        path = os.path.join(root, rel)
        try:
            src = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if not any(f in src for f in MERGED_EXTENSIVE):
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        sc = Scan(rel, src)
        sc.visit(tree)
        hits.extend(sc.hits)
    order = {"RATIO_OF_TWO_MERGED": 0, "SCALED_BY_MERGED": 1, "RATIO_COMMON_SCALE": 2,
             "DIFF_OF_TWO_MERGED": 3, "OFFSET_BY_MERGED": 4}
    hits.sort(key=lambda h: (order.get(h["shape"], 9), h["file"], h["line"]))
    by_shape = {}
    for h in hits:
        by_shape[h["shape"]] = by_shape.get(h["shape"], 0) + 1
    cpp = scan_cpp(root)
    return {"tool": "audit_derived_from_merged_extensives",
            "n_sites": len(hits), "by_shape": by_shape,
            "cpp": cpp, "n_cpp_reads": len(cpp["reads"]), "n_cpp_ratios": len(cpp["ratios"]),
            "n_files": len({h["file"] for h in hits}),
            "sites": hits}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--power", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    s = summary(os.path.abspath(a.root))

    if a.json:
        print(json.dumps(s, indent=2, sort_keys=True))
    else:
        print("=" * 100)
        print(f"Quantities DERIVED from hadd-summed extensive TParameters -- "
              f"{s['n_sites']} sites in {s['n_files']} files")
        for k, v in sorted(s["by_shape"].items()):
            print(f"    {k:22s} {v}")
        print("=" * 100)
        cur = None
        for h in s["sites"]:
            if h["shape"] != cur:
                cur = h["shape"]
                print(f"\n---- {cur} " + "-" * (94 - len(cur)))
            print(f"\n  {h['file']}:{h['line']}  in {h['function']}()   [{h['op']}]")
            print(f"     fields : {', '.join(h['fields'])}")
            print(f"     source : {h['source']}")

        print("\n" + "=" * 100)
        print(f"C++ PASS -- {s['n_cpp_reads']} read site(s), {s['n_cpp_ratios']} ratio site(s)")
        print("=" * 100)
        for r in s["cpp"]["reads"]:
            print(f"  READ  {r['file']}:{r['line']}  {', '.join(r['fields'])}")
            print(f"        {r['source']}")
        for r in s["cpp"]["ratios"]:
            print(f"  RATIO {r['file']}:{r['line']}  locals: {', '.join(r['locals'])}")
            print(f"        {r['source']}")

    if a.power:
        j36 = [h for h in s["sites"]
               if h["file"].endswith("unfold_2d_omnifold_unbinned.py")
               and h["function"] == "get_pot_scales"
               and h["shape"] == "RATIO_OF_TWO_MERGED"]
        if not j36:
            print("\nPOWER TEST FAILED: J36's get_pot_scales was not found as "
                  "RATIO_OF_TWO_MERGED. Either the sweep is broken or J36 was repaired -- "
                  "if repaired, re-derive this table rather than deleting the control.")
            sys.exit(1)
        print(f"\nPOWER TEST PASSED: J36 found live at "
              f"{j36[0]['file']}:{j36[0]['line']} (get_pot_scales)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
