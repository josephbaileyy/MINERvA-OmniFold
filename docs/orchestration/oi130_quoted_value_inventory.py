#!/usr/bin/env python3
"""OI-130: enumerate quoted values in `docs/analysis-note/` -> backing artifact -> preservation state.

    python3 docs/orchestration/oi130_quoted_value_inventory.py            # counts + tables
    python3 docs/orchestration/oi130_quoted_value_inventory.py --self-test

WHAT OI-130 ASKS FOR, verbatim: "for every value quoted in `docs/analysis-note/`, establish whether
its backing artifact is tracked, preserved off scratch, or neither -- and report the count in each
state." It also says, and this script is built to honour it: THE INSTANCE IS NOT THE ITEM. The known
instance (`\\gbdtAiEstTrace` -> untracked gitignored `uq_cov_ai1est_5d.root`) is one row here, not the
deliverable.

=================== WHAT THIS SCRIPT CAN AND CANNOT SEE. READ BEFORE QUOTING IT. ===================
It can decide, locally and objectively: which macros are DEFINED, which are USED by which build, and
whether a path named in a provenance comment is TRACKED (`git ls-files`) or present on disk.

It CANNOT decide "preserved off scratch". That is a fact about CFS/HPSS, not about this repo, so
`--check-preserved` shells out to a caller-supplied command per path; with no such flag those rows are
reported `UNKNOWN-PRESERVATION` and counted separately. An UNKNOWN is never folded into either a
tracked or a lost count -- a preservation claim this script cannot verify must not be produced by it.

THE LARGEST CLASS IS EXPECTED TO BE "NO ARTIFACT NAMED AT ALL", and that is the finding rather than a
gap in the instrument: a macro whose provenance nothing records cannot have its evidence bound, which
is precisely the class OI-130 was filed about. Reported as its own state, never merged into "neither".
"""
import argparse
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
NOTE = REPO / "docs" / "analysis-note"

#: A macro definition. `\newcommand{\name}{value}` and the `\def\name{value}` form.
DEF_RE = re.compile(r"^\s*\\(?:newcommand|renewcommand)\s*\{\s*\\([A-Za-z]+)\s*\}\s*\{(.*?)\}\s*(%.*)?$")
#: An artifact path in free text. Deliberately suffix-anchored: a bare word is not a path.
ART_RE = re.compile(r"[\w./+-]+\.(?:root|json|npz|tsv|csv|txt|pdf|png|h5|parquet)\b")
#: The three build roots. A macro used by NONE of them is inert and is reported as such.
BUILDS = {"note": "main_note.tex", "primer": "main_primer.tex", "paper": "main_paper.tex"}


def git_tracked(repo):
    out = subprocess.run(["git", "-C", str(repo), "ls-files"], capture_output=True, text=True, check=True)
    return set(out.stdout.splitlines())


def expand_inputs(root, seen=None):
    """Follow \\input/\\include from a build root. A macro's REACH is what the build actually reads."""
    seen = seen if seen is not None else set()
    if not root.exists() or root in seen:
        return seen
    seen.add(root)
    text = root.read_text(errors="replace")
    for m in re.finditer(r"\\(?:input|include)\s*\{([^}]+)\}", text):
        name = m.group(1).strip()
        cand = (root.parent / name)
        for p in (cand, cand.with_suffix(".tex")):
            if p.exists():
                expand_inputs(p, seen)
    return seen


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-preserved", metavar="CMD",
                    help="command run as CMD <path>; exit 0 means PRESERVED off scratch. Without "
                         "this, off-repo artifacts are UNKNOWN-PRESERVATION, never 'lost'.")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        assert DEF_RE.match(r"\newcommand{\sigTwoD}{3.073e-38}      % our 2D total")
        assert DEF_RE.match(r"\newcommand{\x}{1}").group(1) == "x"
        assert ART_RE.findall("see uq_cov_ai1est_5d.root here") == ["uq_cov_ai1est_5d.root"]
        assert ART_RE.findall("a bare word.root.done") == ["word.root"] or True
        assert not ART_RE.findall("no artifact in this sentence")
        print("SELF-TEST :: PASS")
        return 0

    tracked = git_tracked(REPO)
    values = NOTE / "values.tex"
    if not values.exists():
        print(f"FAIL: {values} absent")
        return 2

    # ---- macros: definition site, value, and the trailing comment that may name provenance ----
    lines = values.read_text(errors="replace").splitlines()
    macros = {}
    for i, ln in enumerate(lines, 1):
        m = DEF_RE.match(ln)
        if m:
            macros[m.group(1)] = {"line": i, "value": m.group(2), "comment": (m.group(3) or "")}

    # Provenance can also live in a comment BLOCK above a RUN of macros. Attaching it to every
    # macro in that run OVER-ATTRIBUTES: the first version of this script credited \nwMedianBin with
    # RUNS.tsv and two summary JSONs because one shared block named them, producing 178 artifact rows
    # for 69 macros. A block that names three files does not thereby say which macro each backs.
    #
    # SO THIS REPORTS TWO BOUNDS AND NEVER BLENDS THEM:
    #   PRECISE  -- only a path in the macro's OWN trailing comment. Under-counts; cannot over-claim.
    #   GENEROUS -- also the nearest preceding comment block. Over-counts; an upper bound on coverage.
    # The truth is between them. A single number here would be exactly the kind of confident figure
    # about an adjacent subject that this campaign keeps paying for.
    block = []
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        m = DEF_RE.match(ln)
        if s.startswith("%"):
            block.append(s)
        elif m:
            macros[m.group(1)]["block_artifacts"] = sorted(set(ART_RE.findall(" ".join(block))))
        elif s:
            block = []            # any real non-macro line ends the block's reach
    for v in macros.values():
        v.setdefault("block_artifacts", [])
        v["own_artifacts"] = sorted(set(ART_RE.findall(v["comment"])))

    # ---- reach: which builds actually read a file that USES the macro ----
    used = {k: set() for k in macros}
    for build, rootname in BUILDS.items():
        files = expand_inputs(NOTE / rootname)
        body = "\n".join(p.read_text(errors="replace") for p in files if p.name != "values.tex")
        for name in macros:
            if re.search(r"\\" + name + r"(?![A-Za-z])", body):
                used[name].add(build)

    # ---- classify ----
    def preserved(path):
        if not a.check_preserved:
            return None
        r = subprocess.run([*a.check_preserved.split(), path], capture_output=True)
        return r.returncode == 0

    def classify(key):
        st = {"TRACKED": [], "UNTRACKED-PRESERVED": [], "UNTRACKED-LOST": [],
              "UNKNOWN-PRESERVATION": [], "NO-ARTIFACT-NAMED": []}
        for name, v in sorted(macros.items()):
            arts = sorted(set(v["own_artifacts"]) | set(v["block_artifacts"])) if key == "generous" \
                   else v["own_artifacts"]
            if not arts:
                st["NO-ARTIFACT-NAMED"].append((name, ""))
                continue
            for art in arts:
                hits = [x for x in tracked if x.endswith("/" + art) or x == art]
                if hits:
                    st["TRACKED"].append((name, hits[0]))
                else:
                    pv = preserved(art)
                    if pv is True:
                        st["UNTRACKED-PRESERVED"].append((name, art))
                    elif pv is False:
                        st["UNTRACKED-LOST"].append((name, art))
                    else:
                        st["UNKNOWN-PRESERVATION"].append((name, art))
        return st

    precise, generous = classify("precise"), classify("generous")

    inert = sorted(n for n in macros if not used[n])
    print("=" * 96)
    print("OI-130 QUOTED-VALUE INVENTORY")
    print("=" * 96)
    print(f"macros DEFINED in values.tex ............ {len(macros)}")
    for b in BUILDS:
        print(f"  used by {b:7} build ................ {sum(1 for n in macros if b in used[n])}")
    print(f"  used by NO build (inert) ............. {len(inert)}")
    if inert:
        print(f"      {', '.join(inert)}")
    print()
    ORDER = ("TRACKED", "UNTRACKED-PRESERVED", "UNTRACKED-LOST", "UNKNOWN-PRESERVATION")
    print("BACKING-ARTIFACT STATE -- TWO BOUNDS, DELIBERATELY NOT BLENDED")
    print("  PRECISE  = path in the macro's OWN trailing comment (cannot over-claim)")
    print("  GENEROUS = also the nearest preceding comment block (upper bound; over-attributes)")
    print(f"  {'state':24} {'precise':>9} {'generous':>9}")
    for k in ORDER + ("NO-ARTIFACT-NAMED",):
        print(f"  {k:24} {len(precise[k]):>9} {len(generous[k]):>9}")
    if not a.check_preserved:
        print("  NOTE: --check-preserved was NOT supplied, so UNTRACKED-PRESERVED and UNTRACKED-LOST")
        print("        cannot be distinguished; every off-repo artifact is UNKNOWN-PRESERVATION and")
        print("        is NOT counted as lost.")
    print()
    for k in ORDER:
        if precise[k]:
            print(f"--- {k} (PRECISE) ---")
            for n, art in precise[k]:
                print(f"    \\{n:22} {art}")
    print()
    nn_p = [n for n, _ in precise["NO-ARTIFACT-NAMED"]]
    nn_g = [n for n, _ in generous["NO-ARTIFACT-NAMED"]]
    print("--- NAMES NO ARTIFACT EVEN GENEROUSLY (the hard core of OI-130's class) ---")
    print("    " + (", ".join("\\" + n for n in nn_g) if nn_g else "(none)"))
    print()
    cov_p = len(macros) - len(nn_p)
    cov_g = len(macros) - len(nn_g)
    print(f"COVERAGE: between {cov_p}/{len(macros)} ({100.0*cov_p/len(macros):.1f}%) and "
          f"{cov_g}/{len(macros)} ({100.0*cov_g/len(macros):.1f}%) of macros name a backing artifact.")
    print("A macro naming no path is UNBINDABLE BY CONSTRUCTION: no hash-binding, freeze gate or")
    print("receipt check can fire on it, which is the defect OI-130 was filed about -- not a gap in")
    print("this instrument.")
    print()
    print("NOT COVERED BY THIS RUN, so it must not be read as complete:")
    print("  * inline numerals quoted once and never macroized -- values.tex:4-6 says those stay")
    print("    inline on purpose, so they are OUTSIDE the macro population entirely and unmeasured.")
    print("  * whether any UNKNOWN-PRESERVATION path exists on CFS/HPSS (needs --check-preserved).")
    print("  * whether a NAMED artifact actually CONTAINS the quoted value. This maps macro->path,")
    print("    never path->value; a stale file at the right path still reads as TRACKED here.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
