#!/usr/bin/env python3
"""OI-130 canonical inventory: extractor, coverage checker, and its own test suite.

    python3 oi130_inventory_checker.py --self-test
    python3 oi130_inventory_checker.py --extract  --tree <dir>            # in-corpus quoted values
    python3 oi130_inventory_checker.py --check    --tree <dir> --inventory <tsv>

WHAT THIS IS FOR. OI-130 asks for every value quoted in `docs/analysis-note/` mapped to its backing
artifact and preservation state, with counts. The predecessor `oi130_quoted_value_inventory.py` traced
ONLY the 71 `values.tex` macros and says so in its own epilogue; `AUDIT-20260819` states the same limit
("Only values.tex's 70 macros were traced ... the inline numbers are the larger population and none of
them was swept"). This instrument closes that gap: it extracts macro definitions AND inline numerals
across the per-deliverable `\\input` closure, and it FAILS when an extracted value has no inventory row.

WHY IT MUST BE ABLE TO FAIL. A coverage checker that cannot report a missing row is a checker that
reports its own fixture. `--self-test` therefore includes an explicit failing-direction case
(`test_unmapped_quoted_value_is_detected`) that plants a quoted value absent from the inventory and
asserts a non-zero exit. Each exclusion class additionally carries BOTH a positive fixture (the thing
it must exclude) and a negative fixture (a substantive value that looks similar and must NOT be
excluded), because a one-directional filter waves the other direction through at exit 0.

THE COUNT THIS DOES NOT PRODUCE. `preserved-off-scratch` is a fact about CFS/HPSS, not about this
repo. It is never inferred here. Absent an external probe the field is UNKNOWN and is excluded from
BOTH the tracked and the neither tallies, because a preservation claim this instrument cannot verify
must not be produced by it.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT = HERE / "oi130_corpus_contract.json"

BUILDS = {"note": "main_note.tex", "primer": "main_primer.tex", "paper": "main_paper.tex"}

DEF_RE = re.compile(r"^\s*\\(?:new|renew)command\s*\{\s*\\([A-Za-z]+)\s*\}\s*\{([^}]*)\}(.*)$")
NUM_RE = re.compile(r"(?<![\w.])[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?(?![\w])")
INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
DEAD_RE = re.compile(r"\\dead\s*\{")

# ---------------------------------------------------------------- exclusion classes
# Each entry: (class_id, predicate(line, match) -> bool). Order matters only for reporting;
# the first matching class is the one recorded, so every value gets exactly one exclusion class.
TEX_UNIT = r"(?:em|ex|pt|cm|mm|in|bp|dd|pc|sp)\b"
LEN_AFTER = re.compile(r"^\s*(?:" + TEX_UNIT + r"|\\(?:text|line|column)width|\\textheight)")
TOOLS = r"(?:python3?|ROOT|TensorFlow|TF|Keras|numpy|scipy|sklearn|LightGBM|biber|git|GEANT4?)"


def _in_cmd_arg(line, pos, cmds):
    """True if pos sits inside the braces of one of `cmds` on this line."""
    for c in cmds:
        for m in re.finditer(r"\\" + c + r"\s*\{", line):
            depth, i = 1, m.end()
            while i < len(line) and depth:
                if line[i] == "{":
                    depth += 1
                elif line[i] == "}":
                    depth -= 1
                i += 1
            if m.end() <= pos < i:
                return True
    return False


def _in_optional_arg(line, pos, cmd):
    for m in re.finditer(r"\\" + cmd + r"\s*\[", line):
        end = line.find("]", m.end())
        if end != -1 and m.end() <= pos < end:
            return True
    return False


#: ORDER IS SEMANTIC, not cosmetic. The first matching class is the one recorded, so a more
#: specific class must precede a more general one that would also match. `float_spec` precedes
#: `latex_length` because `\begin{minipage}{0.31\textwidth}` satisfies both and the float
#: specification is the more informative answer; the self-test pins this by asserting the
#: positive fixture lands in `float_spec` rather than merely in "some exclusion class".
EXCLUSIONS = [
    ("float_spec", lambda ln, m: bool(re.search(r"\\begin\{minipage\}(?:\[[^\]]*\])?\{[^}]*$", ln[:m.start()]))
        or bool(re.search(r"\\begin\{(?:tabular|tabularx)\}(?:\[[^\]]*\])?\{[^}]*$", ln[:m.start()]))),
    ("latex_length", lambda ln, m: bool(LEN_AFTER.match(ln[m.end():]))),
    ("graphics_option", lambda ln, m: _in_optional_arg(ln, m.start(), "includegraphics")
        or bool(re.search(r"--(?:bbox|margins)\s*'[^']*$", ln[:m.start()]))),
    ("citation_or_ref", lambda ln, m: _in_cmd_arg(ln, m.start(), ["cite", "ref", "label", "eqref", "autoref", "citep", "citet"])),
    ("arxiv_or_doi", lambda ln, m: bool(re.search(r"(?:arXiv:|doi:)\s*\S*$", ln[:m.start() + 1], re.I))),
    ("date", lambda ln, m: bool(re.match(r"^\d{4}(-\d{2}){1,2}$", m.group()))
        or bool(re.search(r"\b(?:in|ending|since|during|dated)\s+$", ln[:m.start()]) and re.match(r"^(?:19|20)\d{2}$", m.group()))),
    # window, not anchor: "python3 is 3.6" puts prose between the tool token and the version.
    # Bounded to 12 non-digit chars so an unrelated tool mention far up the line cannot capture
    # a substantive value -- that bound is what the negative fixture tests.
    ("software_version", lambda ln, m: bool(re.search(TOOLS + r"[^0-9]{0,12}$", ln[:m.start()], re.I))),
    ("sectioning_or_footnote", lambda ln, m: bool(re.search(r"\\S~?\s*$|\\(?:section|subsection|appendix)\*?\{[^}]*$|App(?:\.|endix)~?\s*$", ln[:m.start()]))),
    ("math_structure", lambda ln, m: bool(re.search(r"[_^]\s*\{?\s*$", ln[:m.start()]))),
]


def classify_exclusion(line, m):
    for cid, pred in EXCLUSIONS:
        try:
            if pred(line, m):
                return cid
        except Exception:
            continue
    return None


# ---------------------------------------------------------------- corpus closure
def closure(tree, rootname):
    """Transitive \\input closure from a build root. Returns ordered list of existing filenames."""
    note = pathlib.Path(tree)
    seen, stack = [], [rootname]
    while stack:
        n = stack.pop(0)
        if n in seen:
            continue
        p = note / n
        if not p.exists():
            continue
        seen.append(n)
        for m in INPUT_RE.finditer(p.read_text(errors="replace")):
            nm = m.group(1).strip()
            if not nm.endswith(".tex"):
                nm += ".tex"
            stack.append(nm)
    return seen


def macro_table(tree):
    """values.tex macro name -> {value, line, comment}. The canonical single-source values."""
    p = pathlib.Path(tree) / "values.tex"
    out = {}
    if not p.exists():
        return out
    for i, ln in enumerate(p.read_text(errors="replace").splitlines(), 1):
        m = DEF_RE.match(ln)
        if m and NUM_RE.search(m.group(2)):
            out[m.group(1)] = {"value": m.group(2).strip(), "line": i, "comment": m.group(3).strip()}
    return out


def extract(tree):
    """Return (values, excluded, closures). One row per macro NAME; one row per inline occurrence."""
    tree = pathlib.Path(tree)
    macros = macro_table(tree)
    closures = {b: closure(tree, r) for b, r in BUILDS.items()}
    reach = {}
    for b, files in closures.items():
        for f in files:
            reach.setdefault(f, set()).add(b)

    # macro consumption: which deliverables read a file that USES the macro
    consumed = {n: set() for n in macros}
    for f, builds in reach.items():
        if f == "values.tex":
            continue
        p = tree / f
        if not p.exists():
            continue
        body = p.read_text(errors="replace")
        for n in macros:
            if re.search(r"\\" + n + r"(?![A-Za-z])", body):
                consumed[n] |= builds

    values, excluded = [], []
    for n, d in sorted(macros.items()):
        values.append({
            "kind": "macro_def", "key": f"macro:{n}", "file": "values.tex", "line": d["line"],
            "raw": d["value"], "consumers": sorted(consumed[n]),
            "status": "inert" if not consumed[n] else "live",
            "has_provenance_comment": bool(d["comment"].lstrip("%").strip()),
        })

    macro_vals = {d["value"]: n for n, d in macros.items()}
    for f in sorted(reach):
        if f == "values.tex":
            continue
        p = tree / f
        if not p.exists():
            continue
        for i, ln in enumerate(p.read_text(errors="replace").splitlines(), 1):
            if ln.lstrip().startswith("%"):
                continue                                    # a comment is not a quoted value
            for m in NUM_RE.finditer(ln):
                cid = classify_exclusion(ln, m)
                rec = {"file": f, "line": i, "raw": m.group(), "consumers": sorted(reach[f])}
                if cid:
                    excluded.append({**rec, "exclusion_class": cid})
                    continue
                dup = macro_vals.get(m.group())
                values.append({**rec, "kind": "inline_numeral",
                               "key": f"inline:{f}:{i}:{m.group()}",
                               "status": "struck" if DEAD_RE.search(ln) else "live",
                               "duplicates_macro": dup})
    return values, excluded, closures


# ---------------------------------------------------------------- coverage check
def load_inventory(path):
    rows, keys = [], set()
    with open(path, encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        for ln in fh:
            if not ln.strip():
                continue
            cells = ln.rstrip("\n").split("\t")
            row = dict(zip(header, cells))
            rows.append(row)
            if row.get("key"):
                keys.add(row["key"])
    return rows, keys


#: The scientific content OI-130 requires per row, read from the contract so the two cannot drift.
#: `key` is additionally required as the machine join column back to extraction.
def required_columns():
    c = json.loads(CONTRACT.read_text())
    return ["key"] + list(c["evidence_binding"]["required_fields"])


def allowed_classifications():
    c = json.loads(CONTRACT.read_text())
    return set(c["evidence_binding"]["classification_values"]) | {"UNKNOWN-PRESERVATION"}


def validate_inventory(rows, header):
    """Schema and semantic violations. A coverage checker that only joins keys would pass an
    inventory with no `remediation_class` column at all -- which is most of what OI-130 asks for."""
    v = []
    missing = [c for c in required_columns() if c not in header]
    if missing:
        v.append(f"MISSING-COLUMNS: {missing}")
    allowed = allowed_classifications()
    for r in rows:
        k = r.get("key", "<no-key>")
        cl = (r.get("classification") or "").strip()
        if "classification" in header:
            if not cl:
                v.append(f"EMPTY-CLASSIFICATION: {k}")
            elif cl not in allowed:
                v.append(f"BAD-CLASSIFICATION: {k} = {cl!r} (allowed {sorted(allowed)})")
        # OI-130's completion criterion: every 'neither' item has a specific remediation class.
        if cl == "neither" and not (r.get("remediation_class") or "").strip():
            v.append(f"NEITHER-WITHOUT-REMEDIATION: {k}")
        # A preservation claim must not be asserted where the field was never probed.
        pres = (r.get("preserved_off_scratch") or "").strip().upper()
        if cl == "preserved-off-scratch" and pres not in ("YES", "TRUE", "1"):
            v.append(f"PRESERVED-CLAIM-UNSUPPORTED: {k} (preserved_off_scratch={pres!r})")
    return v


def tally(rows):
    """Counts by classification. UNKNOWN-PRESERVATION is its own bucket and is folded into
    NEITHER of the others, because an unverifiable preservation claim must not be produced here."""
    out = {}
    for r in rows:
        cl = (r.get("classification") or "<empty>").strip() or "<empty>"
        out[cl] = out.get(cl, 0) + 1
    return out


def check(tree, inventory):
    values, excluded, _ = extract(tree)
    rows, keys = load_inventory(inventory)
    with open(inventory, encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
    extracted = {v["key"] for v in values}
    unmapped = sorted(extracted - keys)
    orphan = sorted(keys - extracted)
    dupes = sorted({k for k in keys if [r.get("key") for r in rows].count(k) > 1})
    return {"extracted": len(extracted), "rows": len(rows), "unmapped": unmapped,
            "orphan": orphan, "duplicated": dupes, "excluded": len(excluded),
            "violations": validate_inventory(rows, header), "tally": tally(rows),
            "values": values}


# ---------------------------------------------------------------- fixtures / self-test
def _mktree(files):
    d = pathlib.Path(tempfile.mkdtemp(prefix="oi130fx-"))
    for name, body in files.items():
        (d / name).write_text(body)
    return d


MINIMAL = {
    "values.tex": "\\newcommand{\\sigTot}{3.073e-38}  % from unfold_out.root, receipt R-1\n"
                  "\\newcommand{\\chiP}{3.66}\n",
    "main_note.tex": "\\input{values}\n\\input{sec_a}\n",
    "main_primer.tex": "\\input{values}\n",
    "main_paper.tex": "\\input{values}\n\\input{sec_a}\n",
    "sec_a.tex": "The total is \\SI{\\sigTot}{cm^2/nucleon} and the ratio is $1.006$.\n",
}


def self_test():
    fails = []

    def ok(cond, name):
        if cond:
            print(f"  PASS  {name}")
        else:
            print(f"  FAIL  {name}")
            fails.append(name)

    print("-- contract --")
    c = json.loads(CONTRACT.read_text())
    ok(c["contract_id"] == "OI-130-corpus-v1", "contract loads and is versioned")
    declared = {e["id"] for e in c["exclusion_classes"]}
    implemented = {cid for cid, _ in EXCLUSIONS}
    ok(declared == implemented,
       f"every declared exclusion class is implemented (declared-only={declared - implemented}, "
       f"impl-only={implemented - declared})")

    print("-- exclusion classes, BOTH directions --")
    # positive: must be excluded. negative: must NOT be excluded.
    cases = [
        ("latex_length", r"\rule{0.82\textwidth}{1pt}", r"the ratio is $0.82$ of published"),
        ("graphics_option", r"\includegraphics[scale=0.5]{f}", r"we select $0.5$ GeV events"),
        ("float_spec", r"\begin{minipage}[c]{0.31\textwidth}", r"the fraction is $0.31$"),
        ("citation_or_ref", r"see \ref{fig:12} below", r"we report $12$ bins"),
        ("arxiv_or_doi", r"reproduction of arXiv:2106.16210", r"the value is $2106.16$"),
        ("date", r"operation, ending in 2019, MINERvA", r"the band is $2019$ universes"),
        ("software_version", r"python3 is 3.6 on that node", r"the pull RMS is 3.6 overall"),
        ("sectioning_or_footnote", r"described in App.~2 of the note", r"the section has $2$ bins"),
        ("math_structure", r"the term $x^{2}$ enters", r"the exponent is $-38$ here"),
    ]
    # A positive fixture containing NO extractable numeral cannot exercise its class: the old
    # \cite{MINERvA:2021owq} and \S\ref{sec:pet} fixtures both had zero NUM_RE matches, so they
    # tested nothing while reading like coverage. Assert non-vacuity FIRST so that failure mode
    # is loud rather than silent.
    for cid, pos, neg in cases:
        mp = NUM_RE.search(pos)
        ok(mp is not None, f"{cid}: positive fixture is non-vacuous (contains a numeral)")
        if mp is None:
            continue
        got_pos = classify_exclusion(pos, mp)
        ok(got_pos == cid, f"{cid}: positive fixture excluded as {cid} (got {got_pos!r})")
        mn = NUM_RE.search(neg)
        ok(mn is not None, f"{cid}: negative fixture is non-vacuous (contains a numeral)")
        if mn is None:
            continue
        got_neg = classify_exclusion(neg, mn)
        ok(got_neg is None, f"{cid}: negative fixture NOT excluded (got {got_neg!r})")

    print("-- closure and reach --")
    t = _mktree(MINIMAL)
    cl = {b: closure(t, r) for b, r in BUILDS.items()}
    ok(cl["primer"] == ["main_primer.tex", "values.tex"], "primer closure is 2 files")
    ok("sec_a.tex" in cl["note"] and "sec_a.tex" in cl["paper"], "sec_a reached by note and paper")
    ok("sec_a.tex" not in cl["primer"], "sec_a NOT reached by primer")

    vals, exc, _ = extract(t)
    mac = [v for v in vals if v["kind"] == "macro_def"]
    ok(len(mac) == 2, f"2 macro rows (got {len(mac)})")
    sig = next(v for v in mac if v["key"] == "macro:sigTot")
    ok(sig["consumers"] == ["note", "paper"], f"sigTot consumed by note+paper (got {sig['consumers']})")
    ok(sig["has_provenance_comment"], "sigTot provenance comment detected")
    chi = next(v for v in mac if v["key"] == "macro:chiP")
    ok(chi["consumers"] == [] and chi["status"] == "inert", "unused macro is inert with no consumers")
    ok(not chi["has_provenance_comment"], "missing provenance comment detected")

    print("-- shared-origin rule: macro USE is not a new row --")
    ok(not any(v["key"].startswith("inline:") and v["raw"] == "3.073e-38" for v in vals),
       "a macro's expansion is not re-counted as an inline value")
    inl = [v for v in vals if v["kind"] == "inline_numeral"]
    ok(len(inl) == 1 and inl[0]["raw"] == "1.006", f"the one inline numeral is found (got {[i['raw'] for i in inl]})")

    print("-- struck status --")
    t2 = _mktree({**MINIMAL, "sec_a.tex": "The old value \\dead{0.466} is retracted.\n"})
    v2, _, _ = extract(t2)
    s = [v for v in v2 if v["kind"] == "inline_numeral"]
    ok(len(s) == 1 and s[0]["status"] == "struck", f"a \\dead{{}} value is in-corpus and marked struck (got {s})")

    print("-- precision split (finer_precision_sibling must NOT read as a duplicate) --")
    t3 = _mktree({**MINIMAL, "sec_a.tex": "values $3.66$ and $3.661$ both appear.\n"})
    v3, _, _ = extract(t3)
    d = {v["raw"]: v.get("duplicates_macro") for v in v3 if v["kind"] == "inline_numeral"}
    ok(d.get("3.66") == "chiP", f"same-precision literal flagged as duplicating its macro (got {d.get('3.66')!r})")
    ok(d.get("3.661") is None, f"finer-precision sibling NOT flagged a duplicate (got {d.get('3.661')!r})")

    print("-- FAILING DIRECTION: an unmapped quoted value must be detected --")
    cols = required_columns()

    def write_inv(path, specs):
        """specs: list of dicts; every required column is emitted so a coverage failure is not
        confounded with a schema failure."""
        with open(path, "w") as fh:
            fh.write("\t".join(cols) + "\n")
            for s in specs:
                fh.write("\t".join(str(s.get(c, "n/a")) for c in cols) + "\n")

    inv = pathlib.Path(tempfile.mkdtemp(prefix="oi130inv-")) / "inv.tsv"
    # deliberately covers the macros but OMITS the inline 1.006
    write_inv(inv, [{"key": "macro:sigTot", "classification": "tracked"},
                    {"key": "macro:chiP", "classification": "no-artifact-named"}])
    r = check(t, inv)
    ok(r["unmapped"] == ["inline:sec_a.tex:1:1.006"],
       f"the omitted quoted value is reported unmapped (got {r['unmapped']})")
    ok(r["violations"] == [], f"and it is a COVERAGE failure, not a schema one (got {r['violations']})")
    ok(main(["--check", "--tree", str(t), "--inventory", str(inv)]) != 0,
       "checker EXITS NON-ZERO on an unmapped quoted value")

    print("-- and it passes once the row exists (negative control on the same fixture) --")
    write_inv(inv, [{"key": "macro:sigTot", "classification": "tracked"},
                    {"key": "macro:chiP", "classification": "no-artifact-named"},
                    {"key": "inline:sec_a.tex:1:1.006", "classification": "neither",
                     "remediation_class": "R3-name-a-producer"}])
    r2 = check(t, inv)
    ok(r2["unmapped"] == [], f"no unmapped rows once covered (got {r2['unmapped']})")
    ok(main(["--check", "--tree", str(t), "--inventory", str(inv)]) == 0,
       "checker EXITS ZERO when coverage is complete")

    print("-- orphan and duplicate detection --")
    write_inv(inv, [{"key": "macro:sigTot", "classification": "tracked"},
                    {"key": "macro:chiP", "classification": "no-artifact-named"},
                    {"key": "inline:sec_a.tex:1:1.006", "classification": "neither",
                     "remediation_class": "R3-name-a-producer"},
                    {"key": "macro:doesNotExist", "classification": "tracked"},
                    {"key": "macro:sigTot", "classification": "tracked"}])
    r3 = check(t, inv)
    ok(r3["orphan"] == ["macro:doesNotExist"], f"orphan row detected (got {r3['orphan']})")
    ok(r3["duplicated"] == ["macro:sigTot"], f"duplicate key detected (got {r3['duplicated']})")

    print("-- SCHEMA, failing direction: OI-130's own required fields --")
    ok(len(cols) == 23, f"22 contract fields + join key (got {len(cols)})")
    thin = pathlib.Path(tempfile.mkdtemp(prefix="oi130thin-")) / "thin.tsv"
    with open(thin, "w") as fh:                      # the OLD 2-column shape
        fh.write("key\tclassification\nmacro:sigTot\ttracked\n")
    vt = check(t, thin)["violations"]
    ok(any(x.startswith("MISSING-COLUMNS") for x in vt),
       f"an inventory missing OI-130's required fields is REJECTED (got {vt[:1]})")
    ok("remediation_class" in str(vt), "the rejection names remediation_class as missing")

    print("-- 'neither' without a remediation class must be rejected --")
    write_inv(inv, [{"key": "macro:sigTot", "classification": "tracked"},
                    {"key": "macro:chiP", "classification": "no-artifact-named"},
                    {"key": "inline:sec_a.tex:1:1.006", "classification": "neither",
                     "remediation_class": ""}])
    vn = check(t, inv)["violations"]
    ok(any(x.startswith("NEITHER-WITHOUT-REMEDIATION") for x in vn),
       f"a 'neither' row with no remediation class is rejected (got {vn})")
    ok(main(["--check", "--tree", str(t), "--inventory", str(inv)]) != 0,
       "and that alone EXITS NON-ZERO even though coverage is complete")

    print("-- an unsupported preservation claim must be rejected --")
    write_inv(inv, [{"key": "macro:sigTot", "classification": "preserved-off-scratch",
                     "preserved_off_scratch": "UNKNOWN"},
                    {"key": "macro:chiP", "classification": "no-artifact-named"},
                    {"key": "inline:sec_a.tex:1:1.006", "classification": "neither",
                     "remediation_class": "R3"}])
    vp = check(t, inv)["violations"]
    ok(any(x.startswith("PRESERVED-CLAIM-UNSUPPORTED") for x in vp),
       f"classification 'preserved-off-scratch' with an unprobed field is rejected (got {vp})")

    print("-- a bad classification token must be rejected (closed vocabulary) --")
    write_inv(inv, [{"key": "macro:sigTot", "classification": "probably-fine"},
                    {"key": "macro:chiP", "classification": "no-artifact-named"},
                    {"key": "inline:sec_a.tex:1:1.006", "classification": "neither",
                     "remediation_class": "R3"}])
    vb = check(t, inv)["violations"]
    ok(any(x.startswith("BAD-CLASSIFICATION") for x in vb),
       f"an out-of-vocabulary classification is rejected (got {vb})")

    print("-- and the fully-valid inventory still passes (negative control on schema) --")
    write_inv(inv, [{"key": "macro:sigTot", "classification": "tracked"},
                    {"key": "macro:chiP", "classification": "no-artifact-named"},
                    {"key": "inline:sec_a.tex:1:1.006", "classification": "neither",
                     "remediation_class": "R3-name-a-producer"}])
    rf = check(t, inv)
    ok(rf["violations"] == [] and rf["unmapped"] == [], f"clean inventory passes (got {rf['violations']})")
    ok(rf["tally"] == {"tracked": 1, "no-artifact-named": 1, "neither": 1},
       f"tally reports each classification separately (got {rf['tally']})")

    print()
    if fails:
        print(f"SELF-TEST :: FAIL ({len(fails)}): {fails}")
        return 1
    print("SELF-TEST :: PASS")
    return 0


# ---------------------------------------------------------------- cli
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--tree", help="a docs/analysis-note directory")
    ap.add_argument("--inventory", help="inventory TSV with a 'key' column")
    ap.add_argument("--tsv", action="store_true", help="emit extraction as TSV")
    a = ap.parse_args(argv)

    if a.self_test:
        return self_test()

    if not a.tree:
        print("FAIL: --tree is required", file=sys.stderr)
        return 2

    if a.extract:
        vals, exc, closures = extract(a.tree)
        if a.tsv:
            print("key\tkind\tfile\tline\traw\tstatus\tconsumers\tduplicates_macro")
            for v in vals:
                print("\t".join([v["key"], v["kind"], v["file"], str(v["line"]), v["raw"],
                                 v.get("status", ""), ",".join(v["consumers"]),
                                 str(v.get("duplicates_macro") or "")]))
            return 0
        for b, files in closures.items():
            print(f"closure {b:7} {len(files):3} files")
        print(f"in-corpus quoted values : {len(vals)}")
        print(f"  macro_def             : {sum(1 for v in vals if v['kind']=='macro_def')}")
        print(f"  inline_numeral        : {sum(1 for v in vals if v['kind']=='inline_numeral')}")
        print(f"excluded occurrences    : {len(exc)}")
        by = {}
        for e in exc:
            by[e["exclusion_class"]] = by.get(e["exclusion_class"], 0) + 1
        for k in sorted(by, key=lambda x: -by[x]):
            print(f"  {k:24} {by[k]:5}")
        return 0

    if a.check:
        if not a.inventory:
            print("FAIL: --check needs --inventory", file=sys.stderr)
            return 2
        r = check(a.tree, a.inventory)
        print(f"extracted in-corpus values : {r['extracted']}")
        print(f"inventory rows             : {r['rows']}")
        print(f"unmapped (no row)          : {len(r['unmapped'])}")
        for k in r["unmapped"][:40]:
            print(f"    UNMAPPED {k}")
        print(f"orphan (row, no value)     : {len(r['orphan'])}")
        for k in r["orphan"][:40]:
            print(f"    ORPHAN   {k}")
        print(f"duplicated keys            : {len(r['duplicated'])}")
        for k in r["duplicated"][:40]:
            print(f"    DUPLICATE {k}")
        print(f"schema/semantic violations : {len(r['violations'])}")
        for x in r["violations"][:40]:
            print(f"    VIOLATION {x}")
        print("classification tally:")
        for k in sorted(r["tally"]):
            print(f"    {k:24} {r['tally'][k]:5}")
        bad = (len(r["unmapped"]) + len(r["orphan"]) + len(r["duplicated"])
               + len(r["violations"]))
        print("RESULT :: " + ("PASS" if not bad else f"FAIL ({bad})"))
        return 0 if not bad else 1

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
