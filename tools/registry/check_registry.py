#!/usr/bin/env python3
"""Registry integrity and completeness.

    check_registry.py [--repo DIR]        # exit 1 on any failure (pre-commit)
    check_registry.py --self-test         # the label check fires on a planted unregistered label, stays silent on
                                          # registered ones, and the citation check fires on a moved quote

(1) INTEGRITY. Every ESTIMATORS definition, ALIASES row and UNRESOLVED-NAMES row cites file:line, and the cited
    line (staged bytes) must contain the row's quote verbatim; every alias names a registered id; every pattern
    compiles. A citation pins its line by number AND by the digest of the whole line (line_sha256): any move FAILS
    (naming the new number; `--repoint` rewrites it), and any edit of the cited line FAILS even if the quote is
    still on it (a retraction quoting the alias is an edit); re-read it and re-cite with `--cite FILE:LINE`.
    (ATTRIBUTION and STATUS rows are checked the same way by results_index.py.)
(2) COMPLETENESS, scoped to an explicit label pattern list (LABEL_PATTERNS). Over the printed text (comments
    removed) of the \\input closures of main_paper.tex, main_note.tex, main_primer.tex and main_records.tex, every
    estimator label matched by LABEL_PATTERNS must name (reglib.resolve, the rule whatis.py uses, counting only
    aliases marked identifying=yes) exactly one registered estimator. Unresolved or ambiguous: failure, with file:line. Labels outside the pattern list
    are NOT checked -- this is the scope, stated, not a claim that every name is covered.
(3) The records document main_records.tex \\inputs both generated renderings, records_estimators and
    records_results_index, and no posted driver (main_note, main_paper, main_primer, pet_note) reaches either
    through its \\input closure (RECORDS-RULES.md rule 6).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reglib  # noqa: E402

NOTE_DIR = "docs/analysis-note"
DRIVERS = ("main_paper.tex", "main_note.tex", "main_primer.tex", "main_records.tex")
COMMENT = re.compile(r"(?<!\\)%[^\n]*")
# (name, regex over printed text, how a match becomes the label(s) resolved)
LABEL_PATTERNS = (
    # "configuration (e)", "configuration~(a)", "configurations (d) and (e)", "configurations (c)--(e)", "(c), (d)"
    ("configuration-letter", re.compile(r"[Cc]onfigurations?[~\s]*((?:\([a-e]\)(?:\s*(?:,|and|--|-|or|to)\s*)?)+)")),
    # the Conf. column of the paper's findings table: \pcell{0.05\textwidth}{(c), (d)}
    ("findings-conf-cell", re.compile(r"\\pcell\{0\.05\\textwidth\}\{((?:\([a-e]\)(?:,\s*)?)+)\}")),
    # the first cell of an estimator-table row: \pcell{0.2x\...width}{(e) joint-test estimator}
    ("estimator-table-row", re.compile(r"\\pcell\{0\.2[04]\\(?:column|text)width\}\{(\([a-e]\))")),
    # contract names printed as "candidate R", "family N", "family F2", "baseline B0"
    ("contract-name", re.compile(r"\b(?:candidate|family|baseline)\s+(?:estimator\s+)?\\?(?:texttt\{)?([A-Z][A-Z0-9]?)(?![\w-])")),
)


def closure(index: reglib.Index, note_dir: str, driver: str) -> list[str]:
    out, seen = [], set()

    def walk(rel: str) -> None:
        if rel in seen or not index.has(rel):
            return
        seen.add(rel)
        out.append(rel)
        text = COMMENT.sub("", index.text(rel) or "")
        for name in re.findall(r"\\(?:input|include)\{([^}]+)\}", text):
            walk(f"{note_dir}/{name if name.endswith('.tex') else name + '.tex'}")

    walk(f"{note_dir}/{driver}")
    return out


def labels_in(text: str) -> list[tuple[int, str, str]]:
    """(line, pattern name, label to resolve) for every label in printed text (comments removed per line)."""
    found = []
    for ln, line in enumerate(text.split("\n"), start=1):
        printed = COMMENT.sub("", line)
        for name, rx in LABEL_PATTERNS:
            for m in rx.finditer(printed):
                if name == "contract-name":
                    found.append((ln, name, m.group(1)))
                    continue
                letters = re.findall(r"\(([a-e])\)", m.group(1))
                if name == "configuration-letter":
                    span = re.search(r"\(([a-e])\)\s*--\s*\(([a-e])\)", m.group(1))
                    if span:
                        letters += [chr(c) for c in range(ord(span.group(1)), ord(span.group(2)) + 1)]
                for x in sorted(set(letters)):
                    found.append((ln, name, f"configuration ({x})"))
    return found


def completeness(index: reglib.Index, note_dir: str = NOTE_DIR) -> tuple[list[str], int, int]:
    ests = reglib.read_tsv(index, reglib.ESTIMATORS)
    als = reglib.read_tsv(index, reglib.ALIASES)
    files = sorted({f for d in DRIVERS for f in closure(index, note_dir, d)})
    fails, n = [], 0
    for f in files:
        for ln, pat, label in labels_in(index.text(f) or ""):
            n += 1
            named = reglib.identifying(reglib.resolve(label, ests, als))
            if len(named) != 1:
                fails.append(f"{f}:{ln}: {pat} label {label!r} names {len(named)} registered estimators through "
                             f"identifying aliases ({', '.join(named) or 'none'}); register it in ALIASES.tsv "
                             "with its source line")
    return fails, n, len(files)


RECORDS_DRIVER = f"{NOTE_DIR}/main_records.tex"
RECORDS_INPUTS = ("records_estimators", "records_results_index")


POSTED_DRIVERS = ("main_note.tex", "main_paper.tex", "main_primer.tex", "pet_note.tex")


def records_include_index(index: reglib.Index, note_dir: str = NOTE_DIR) -> list[str]:
    """Rule 6, both directions: the records document \\inputs both generated renderings (outside comments), and
    no posted driver's \\input closure reaches either of them."""
    text = COMMENT.sub("", index.text(RECORDS_DRIVER) or "")
    got = set(re.findall(r"\\input\{([^}]+)\}", text))
    fails = [f"{RECORDS_DRIVER} does not \\input{{{name}}} (RECORDS-RULES.md rule 6)" for name in RECORDS_INPUTS
             if name not in got and name + ".tex" not in got]
    for d in POSTED_DRIVERS:
        named = set()
        for f in closure(index, note_dir, d):  # the \\input names each file of the closure asks for
            named |= {x[:-4] if x.endswith(".tex") else x
                      for x in re.findall(r"\\(?:input|include)\{([^}]+)\}", COMMENT.sub("", index.text(f) or ""))}
        for name in RECORDS_INPUTS:
            if name in named:
                fails.append(f"{note_dir}/{d} reaches {name}.tex through its \\input closure: the generated index "
                             "belongs to the internal records document only (RECORDS-RULES.md rule 6)")
    return fails


def run(repo: Path) -> int:
    index = reglib.Index(repo)
    fails, warns = reglib.verify_registry(index)
    fails += records_include_index(index)
    cfails, n, nfiles = completeness(index)
    fails += cfails
    for w in warns:
        print("  WARN " + w)
    for f in fails:
        print("  FAIL " + f)
    ests = reglib.read_tsv(index, reglib.ESTIMATORS)
    als = reglib.read_tsv(index, reglib.ALIASES)
    print(f"REGISTRY :: {len(ests)} estimators, {len(als)} aliases, every citation checked; {n} printed labels in "
          f"{nfiles} files of the four builds, each naming exactly one estimator through identifying aliases; "
          f"records document holds the index and no posted build does"
          + (f" -- {len(fails)} failure(s)" if fails else ""))
    return 1 if fails else 0


def self_test() -> int:
    """A throwaway repository holding a copy of the registry and a two-file note: real staging, real reads."""
    src = reglib.repo_root(Path(__file__).resolve().parent)
    src_index = reglib.Index(src)
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        subprocess.run(["git", "init", "-q", str(t)], check=True, env=reglib.git_env())
        need = {reglib.ESTIMATORS, reglib.ALIASES, reglib.UNRESOLVED}
        for row in reglib.read_tsv(src_index, reglib.ESTIMATORS):
            need.add(row["defining_source"])
        for row in reglib.read_tsv(src_index, reglib.ALIASES) + reglib.read_tsv(src_index, reglib.UNRESOLVED):
            need.add(row["source"])
        for rel in need:
            (t / rel).parent.mkdir(parents=True, exist_ok=True)
            (t / rel).write_bytes(src_index.read(rel))
        note = t / NOTE_DIR
        note.mkdir(parents=True, exist_ok=True)
        good = ("\\input{body}\n", "Configuration~(e), the joint-test estimator, and configurations (c)--(d); "
                "candidate R.\n% configuration (z) in a comment is not printed\n")

        def stage(driver_text: str, body_text: str) -> reglib.Index:
            for d in DRIVERS:
                (note / d).write_text(driver_text if d == "main_paper.tex" else "")
            (note / "body.tex").write_text(body_text)
            subprocess.run(["git", "-C", str(t), "add", "-A"], check=True, env=reglib.git_env())
            return reglib.Index(t)

        def case(name: str, body: str, want_fail: bool, idx_mut=None) -> None:
            nonlocal ok
            idx = stage(good[0], body)
            errs, warns = reglib.verify_registry(idx)
            fails = errs + completeness(idx)[0]
            fired = bool(fails)
            verdict = "ok" if fired == want_fail else "WRONG"
            ok &= fired == want_fail
            print(f"  self-test {verdict:<5} {name}: {'FIRES' if fired else 'silent'} (want "
                  f"{'FIRES' if want_fail else 'silent'}){': ' + fails[0][:110] if fails else ''}")
            return warns

        case("registered labels (e), (c)--(d), candidate R", good[1], False)
        case("unregistered configuration (f) is outside the a-e pattern: not checked", "configuration (f)\n", False)
        case("planted unregistered contract name 'candidate Q'", good[1] + "Then candidate Q was run.\n", True)
        case("estimator-table row (e) of a registered configuration",
             "\\pcell{0.24\\columnwidth}{(e) joint-test estimator}\n", False)
        # A registry conflict: "configuration (e)" also registered (with a valid citation) under d-N-B0.
        al = t / reglib.ALIASES
        clean_aliases = al.read_text()
        l290 = (t / "docs/analysis-note/paper_body.tex").read_text().split("\n")[289]
        al.write_text(clean_aliases + "d-N-B0\tpaper-label\tconfiguration (e)\tzzz-no-match\tyes\tdefault\t"
                      f"docs/analysis-note/paper_body.tex\t290\tconfiguration~(e)\t{reglib.line_digest(l290)}\n")
        case("planted conflict: 'configuration (e)' registered under two estimators", good[1], True)
        al.write_text(clean_aliases)
        (note / "main_records.tex").write_text("\\input{records_estimators}\n\\input{records_results_index}\n")
        subprocess.run(["git", "-C", str(t), "add", "-A"], check=True, env=reglib.git_env())
        r6 = records_include_index(reglib.Index(t))
        ok &= not r6
        print(f"  self-test {'ok' if not r6 else 'WRONG':<5} records document inputs both renderings: "
              f"{'FIRES' if r6 else 'silent'} (want silent)")
        (note / "main_records.tex").write_text("\\input{records_estimators}\n% \\input{records_results_index}\n")
        subprocess.run(["git", "-C", str(t), "add", "-A"], check=True, env=reglib.git_env())
        r6 = records_include_index(reglib.Index(t))
        ok &= bool(r6)
        print(f"  self-test {'ok' if r6 else 'WRONG':<5} records document with the index input commented out: "
              f"{'FIRES' if r6 else 'silent'} (want FIRES)")
        (note / "main_records.tex").write_text("\\input{records_estimators}\n\\input{records_results_index}\n")
        (note / "main_note.tex").write_text("\\input{body}\n\\input{records_results_index}\n")
        subprocess.run(["git", "-C", str(t), "add", "-A"], check=True, env=reglib.git_env())
        r6 = records_include_index(reglib.Index(t))
        ok &= bool(r6)
        print(f"  self-test {'ok' if r6 else 'WRONG':<5} a posted driver (main_note) inputs the generated index: "
              f"{'FIRES' if r6 else 'silent'} (want FIRES){': ' + r6[0][:100] if r6 else ''}")
        (note / "main_note.tex").write_text("\\input{body}\n")
        subprocess.run(["git", "-C", str(t), "add", "-A"], check=True, env=reglib.git_env())
        # Citation power. The cited line is pinned by number AND digest: a move, an edit and a retraction that
        # still quotes the alias all FAIL; --repoint repairs a pure move and nothing else.
        cited = reglib.read_tsv(src_index, reglib.ALIASES)[0]
        p = t / cited["source"]
        original = p.read_text()
        lines = original.split("\n")
        n = int(cited["line"])
        p.write_text("inserted line\n" + original)
        case(f"cited line of alias {cited['alias']!r} moved down by one", good[1], True)
        subprocess.run(["git", "-C", str(t), "add", "-A"], check=True, env=reglib.git_env())
        rep = reglib.repoint(reglib.Index(t), t)
        case("... after --repoint rewrote the line numbers", good[1], False)
        (t / reglib.ALIASES).write_text(clean_aliases)
        retracted = lines[:]
        retracted[n - 1] = ("We no longer use the wording \"" + cited["quote"] + "\"; it is withdrawn.")
        p.write_text("\n".join(retracted))
        case(f"cited line replaced by a retraction that still quotes {cited['quote']!r}", good[1], True)
        subprocess.run(["git", "-C", str(t), "add", "-A"], check=True, env=reglib.git_env())
        rep = reglib.repoint(reglib.Index(t), t)
        refused = any(r.startswith("CANNOT REPOINT") for r in rep) and not any(r.startswith("REPOINTED ALIASES row 2:")
                                                                              for r in rep)
        ok &= refused
        print(f"  self-test {'ok' if refused else 'WRONG':<5} --repoint refuses to accept the retraction "
              f"({'refused' if refused else 'ACCEPTED'})")
        (t / reglib.ALIASES).write_text(clean_aliases)
        p.write_text(original.replace(cited["quote"], "QUOTE REMOVED"))
        case(f"quote of alias {cited['alias']!r} removed from its file", good[1], True)
        p.write_text("\n".join(lines[:n - 1] + ["x"] + lines[n:] + [lines[n - 1], lines[n - 1]]))
        case(f"cited line moved to two other lines (ambiguous)", good[1], True)
        p.write_text(original)
    print("REGISTRY self-test :: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", type=Path, default=None)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--repoint", action="store_true",
                    help="re-point citations whose whole line (same digest) moved to exactly one other line (edits "
                         "the working-tree TSVs; never accepts an edited line)")
    ap.add_argument("--cite", metavar="FILE:LINE", help="print the line and its line_sha256, for writing a row")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.cite:
        repo = reglib.repo_root(a.repo or Path.cwd())
        src, _, ln = a.cite.rpartition(":")
        text = (reglib.Index(repo).text(src) or "").split("\n")
        line = text[int(ln) - 1]
        print(f"{src}\t{ln}\t{reglib.line_digest(line)}\t{line}")
        return 0
    if a.repoint:
        repo = reglib.repo_root(a.repo or Path.cwd())
        rep = reglib.repoint(reglib.Index(repo), repo)
        print("\n".join(rep) or "nothing to re-point")
        print("then: git add docs/orchestration/registry/*.tsv && python3 tools/registry/results_index.py --write")
        return 1 if any(r.startswith("CANNOT") for r in rep) else 0
    return run(reglib.repo_root(a.repo or Path.cwd()))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
