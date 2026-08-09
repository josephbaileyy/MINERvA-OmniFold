#!/usr/bin/env python3
"""Enumerate every TParameter written in this repo, its hadd merge mode, and who reads it.

THE RULE THIS MECHANISES, stated generally because the specific form kept being re-learned:

    EVERY `TParameter<T>` IN A MERGED FILE IS A SUM ACROSS THE MERGED INPUTS, unless it was
    written with an explicit non-'+' merge mode.

ROOT's `TParameter<T>::Merge` defaults to mode `'+'`. `hadd` therefore ADDS the values of
same-named TParameters across every input file. On this campaign a merged endpoint is 12
playlists, so a per-playlist quantity read out of a merged file is 12 x what the writer meant,
and a per-playlist 0/1 FLAG is a COUNT of how many playlists set it -- in [0, 12], not in {0, 1}.

WHY THIS IS A SWEEP AND NOT A NOTE. It has now cost real time three separate ways, and each
time the local fix was correct and the general rule was not extracted:

  KNOWN_ISSUES #8   `hadd` summed `pTmu_fiducial_nucleons` across playlists and silently
                    multiplied the fiducial nucleon count -- a normalisation error in a
                    published number.
  2026-08-09        `p4_evidence.py` required `hasTruthOnlyMisses in (0, 1)`. The merged value
                    is 12. The check was CORRECT about the writer's intent and WRONG about the
                    artifact, and it blocked all ten endpoints on perfectly good data.
  (mitigated)       `runEventLoopOmniFold.cpp:1900` writes `hasFullEventSchema` and
                    `fullPhaseSpace` as `TParameter<int>(..., 'f')` -- the PET lane hit #8, read
                    the manual, and used the merge-mode argument. That fix is invisible from the
                    reader's side, which is exactly why a reader needs this table.

The third entry is the point: the codebase contains BOTH conventions, the difference is a single
character in a constructor in another language, and nothing at the read site distinguishes them.

WHAT THE TOOL DECIDES AND WHAT IT DOES NOT.

  Decided mechanically: the set of TParameter names written, their C++/PyROOT type, and the
  declared merge mode (absent => '+' => SUMS). This is a parse, not a judgement.

  NOT decided mechanically: whether a given read is of a merged file. A name read in a script
  that only ever opens single-playlist output is fine at '+'; the same read against a `hadd`
  product is a defect. The tool reports every read site so the question can be ANSWERED per row,
  and refuses to guess -- per BEN-071, a hit list without per-row verdicts transfers the work
  rather than doing it. The triaged table lives in
  FINDING-20260809-tparameter-merge-semantics.md.

Comments and docstrings are stripped before matching: the loudest hits for "TParameter" in this
repo are the ledger prose and the regression tests that exist BECAUSE of trap #8 (the
mention-vs-use error that made the first cannot-fail sweep silent on two of its own instances).

POWER (`--power`): the sweep must report `hasTruthOnlyMisses` as SUMS and `hasFullEventSchema`
as 'f'/first. Both are live in the tree and they are the two opposite outcomes, so a change that
breaks the parse in either direction fails here rather than passing quietly.

Usage:
    python3 docs/orchestration/audit_tparameter_merge_semantics.py [--root .] [--power] [--json]
"""
import argparse
import json
import os
import re
import subprocess
import sys

# --------------------------------------------------------------------------------------------
# corpus
# --------------------------------------------------------------------------------------------
EXTS = (".py", ".cpp", ".cxx", ".cc", ".C", ".h", ".hpp")


def tracked_files(root):
    out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True).stdout
    return [f for f in out.splitlines() if f.endswith(EXTS)]


def strip_comments(text, is_py):
    """Remove comments and (for python) string literals, so prose about TParameter does not
    register as a use. Deliberately crude and deliberately over-eager: a false NEGATIVE here
    would hide a write site, so string literals are blanked rather than dropped, preserving
    offsets and line numbers."""
    if is_py:
        # blank out triple-quoted blocks, keep newlines so line numbers survive
        def _blank(m):
            return re.sub(r"[^\n]", " ", m.group(0))
        text = re.sub(r'"""(?:.|\n)*?"""', _blank, text)
        text = re.sub(r"'''(?:.|\n)*?'''", _blank, text)
        text = re.sub(r"(?m)#.*$", lambda m: " " * len(m.group(0)), text)
    else:
        text = re.sub(r"/\*(?:.|\n)*?\*/",
                      lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
        text = re.sub(r"(?m)//.*$", lambda m: " " * len(m.group(0)), text)
    return text


# --------------------------------------------------------------------------------------------
# writes
# --------------------------------------------------------------------------------------------
# C++:      new TParameter<int>("name", v, 'f')      /  TParameter<double>("name", v).Write()
# PyROOT:   ROOT.TParameter("double")("name", v)     /  ROOT.TParameter("int")("name", v, 'f')
CPP_WRITE = re.compile(
    r"TParameter\s*<\s*(?P<type>[A-Za-z_][\w: ]*?)\s*>\s*\(\s*"
    r"(?P<name>\"[^\"]+\"|[A-Za-z_]\w*)\s*,(?P<rest>[^;]*)")
PY_WRITE = re.compile(
    r"TParameter\s*\(\s*[\"'](?P<type>\w+)[\"']\s*\)\s*\(\s*"
    r"(?P<name>[^,]+?)\s*,(?P<rest>[^\n]*)")
MERGE_MODE = re.compile(r"[,(]\s*'(?P<mode>[+flmM])'")


def _literal(tok):
    tok = tok.strip()
    if tok.startswith(('"', "'")) and tok.endswith(('"', "'")):
        return tok[1:-1], True
    return tok, False           # f-string / variable / concatenation


def find_writes(root, files):
    writes = {}                                     # name -> dict
    dynamic = []                                    # non-literal names, reported separately
    for rel in files:
        path = os.path.join(root, rel)
        try:
            raw = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if "TParameter" not in raw:
            continue
        is_py = rel.endswith(".py")
        text = strip_comments(raw, is_py)
        for rx in (CPP_WRITE, PY_WRITE):
            for m in rx.finditer(text):
                name, literal = _literal(m.group("name"))
                line = text[:m.start()].count("\n") + 1
                mode = MERGE_MODE.search(m.group("rest"))
                rec = {"type": m.group("type").strip(),
                       "mode": mode.group("mode") if mode else "+",
                       "mode_explicit": bool(mode),
                       "site": f"{rel}:{line}"}
                if not literal:
                    dynamic.append(dict(rec, name=name))
                    continue
                writes.setdefault(name, []).append(rec)
    return writes, dynamic


# --------------------------------------------------------------------------------------------
# reads
# --------------------------------------------------------------------------------------------
def find_reads(root, files, names):
    """A read is the field's literal name appearing in executable code in a file that does not
    write it. Name-based and therefore over-inclusive; that is the correct direction of error
    for an inventory whose job is to make sure nothing is missed."""
    reads = {n: [] for n in names}
    for rel in files:
        path = os.path.join(root, rel)
        try:
            raw = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if not any(n in raw for n in names):
            continue
        text = strip_comments(raw, rel.endswith(".py"))
        for i, line in enumerate(text.splitlines(), 1):
            for n in names:
                if f'"{n}"' in line or f"'{n}'" in line:
                    if "TParameter" in line:
                        continue                     # that is the write site
                    reads[n].append(f"{rel}:{i}")
    return reads


MEANING = {
    # '+' is the DEFAULT and is correct for extensive quantities; the tool cannot tell extensive
    # from intensive, so it states the mechanism and leaves the verdict to the triaged table.
    "+": ("SUM over merged inputs (12 playlists here). Correct for an EXTENSIVE quantity (POT, "
          "counts, censuses); WRONG for a per-playlist constant, a ratio, or a 0/1 flag (which "
          "becomes a count in [0,12])"),
    "f": "FIRST input's value -- hadd-safe, means what the writer meant",
    "l": "LAST input's value -- hadd-safe but order-dependent",
    "m": "MIN over merged inputs",
    "M": "MAX over merged inputs",
}


def summary(root="."):
    files = tracked_files(root)
    writes, dynamic = find_writes(root, files)
    reads = find_reads(root, files, set(writes))
    rows = []
    for name in sorted(writes):
        recs = writes[name]
        modes = sorted({r["mode"] for r in recs})
        rows.append({"name": name,
                     "types": sorted({r["type"] for r in recs}),
                     "mode": modes[0] if len(modes) == 1 else "MIXED:" + ",".join(modes),
                     "mode_explicit": any(r["mode_explicit"] for r in recs),
                     "post_hadd_meaning": MEANING.get(modes[0], "AMBIGUOUS -- written both ways")
                                          if len(modes) == 1 else "AMBIGUOUS -- written both ways",
                     "written_at": [r["site"] for r in recs],
                     "read_at": reads.get(name, [])})
    return {"tool": "audit_tparameter_merge_semantics",
            "n_files_scanned": len(files),
            "n_fields": len(rows),
            "n_summing": sum(1 for r in rows if r["mode"] == "+"),
            "n_hadd_safe": sum(1 for r in rows if r["mode"] != "+"),
            "dynamic_names": dynamic,
            "fields": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--power", action="store_true", help="assert the two live controls")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    s = summary(root)

    if a.json:
        print(json.dumps(s, indent=2, sort_keys=True))
    else:
        print("=" * 100)
        print(f"TParameter merge semantics -- {s['n_fields']} fields over "
              f"{s['n_files_scanned']} tracked source files")
        print(f"  {s['n_summing']} SUM across merged inputs (default '+'), "
              f"{s['n_hadd_safe']} declare a hadd-safe mode")
        print("=" * 100)
        for r in s["fields"]:
            flag = "  " if r["mode"] != "+" else "!!"
            print(f"\n{flag} {r['name']}   <{'/'.join(r['types'])}>   mode={r['mode']}"
                  f"{'' if r['mode_explicit'] else ' (implicit)'}")
            print(f"     post-hadd : {r['post_hadd_meaning']}")
            print(f"     written   : {', '.join(r['written_at'])}")
            print(f"     read      : {', '.join(r['read_at']) if r['read_at'] else '(no read site found)'}")
        if s["dynamic_names"]:
            print("\n" + "-" * 100)
            print("NAMES BUILT AT RUNTIME (f-string / variable) -- not resolvable statically, "
                  "check by hand:")
            for d in s["dynamic_names"]:
                print(f"  {d['site']}: {d['name']}  <{d['type']}> mode={d['mode']}")

    if a.power:
        by = {r["name"]: r for r in s["fields"]}
        bad = []
        if by.get("hasTruthOnlyMisses", {}).get("mode") != "+":
            bad.append("hasTruthOnlyMisses should parse as '+' (it is why this sweep exists)")
        if by.get("hasFullEventSchema", {}).get("mode") != "f":
            bad.append("hasFullEventSchema should parse as 'f' (the mitigated control)")
        if bad:
            print("\nPOWER TEST FAILED:")
            for b in bad:
                print("  " + b)
            sys.exit(1)
        print("\nPOWER TEST PASSED: both live controls classified correctly "
              "(hasTruthOnlyMisses '+', hasFullEventSchema 'f')")
    return 0


if __name__ == "__main__":
    sys.exit(main())
