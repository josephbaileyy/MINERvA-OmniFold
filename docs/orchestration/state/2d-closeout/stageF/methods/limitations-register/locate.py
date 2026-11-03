"""locate.py -- find a quote from the built note in the note's TeX sources, and the records its source comments cite.

usage: python3 -I locate.py NOTEDIR QUOTES.tsv OUT.json [ROOT] [--self-test]

NOTEDIR is a docs/analysis-note directory. QUOTES.tsv has columns key<TAB>quote (header line first). For each quote
it finds the longest run of the quote's alphabetic tokens in the printed text of ROOT.tex's \\input closure (ROOT defaults to main_note; main_paper for the paper)
(comments and macro names stripped; the method of note-consolidate/recount.py), and reports file:line of the run's
first token, the share of the quote covered, and the governing records (DECISION-, OUTCOME-, RECORD-, CORRECTION-,
FINDING-, AUTHORIZATION-, DELIVERY-, *REPORT.md, OI-nnn, KNOWN_ISSUES rows) named in TeX comments within 12 lines
above and 3 below that line. A quote covered under 80% is reported as "partial" and must be checked by hand.
"""
import collections
import csv
import json
import os
import re
import sys

TOK = re.compile(r"[a-z]+")
INPUT = re.compile(r"\\input\{([^}]+)\}")
REC = re.compile(r"((?:DECISION|OUTCOME|RECORD|CORRECTION|FINDING|AUTHORIZATION|DELIVERY|AMENDMENT|RULING)-[0-9]{8}"
                 r"[A-Za-z0-9._-]*|[A-Za-z0-9_./-]*REPORT[A-Za-z0-9_.-]*\.md|OI-[0-9]+|VL[0-9]{2,3}|"
                 r"KNOWN_ISSUES(?:\.md)? (?:row )?[0-9]+)")
SKIP = {"preamble", "values", "values_inference", "values_fived16", "records_entry_numbers"}


def closure(notedir, name="main_note", seen=None):
    seen = [] if seen is None else seen
    path = os.path.join(notedir, name + ".tex")
    if name in SKIP or name in seen or not os.path.exists(path):
        return seen
    seen.append(name)
    for line in open(path, encoding="utf-8"):
        for m in INPUT.finditer(re.sub(r"(?<!\\)%.*", "", line)):
            closure(notedir, m.group(1).removesuffix(".tex"), seen)
    return seen


def stream_of(notedir, root="main_note"):
    stream, raw = [], {}
    for f in closure(notedir, root):
        lines = open(os.path.join(notedir, f + ".tex"), encoding="utf-8").read().split("\n")
        raw[f] = lines
        for i, line in enumerate(lines, 1):
            line = re.sub(r"(?<!\\)%.*", "", line)
            for t in TOK.findall(re.sub(r"\\[A-Za-z]+", " ", line).lower()):
                stream.append((t, f, i))
    return stream, raw


def locate(quote, stream, idx):
    toks = [s[0] for s in stream]
    qt = TOK.findall(quote.lower().replace("’", "'"))
    best, at = 0, None
    for j in range(len(qt) - 3):
        for k in idx.get(tuple(qt[j:j + 4]), []):
            n = 0
            while j + n < len(qt) and k + n < len(toks) and toks[k + n] == qt[j + n]:
                n += 1
            if n > best:
                best, at = n, k
    cov = best / len(qt) if qt else 0
    return (stream[at][1], stream[at][2], round(cov, 2)) if at is not None else (None, None, 0)


def records_near(raw, f, line):
    recs = []
    for i in range(max(0, line - 13), min(len(raw[f]), line + 3)):
        m = re.search(r"(?<!\\)%(.*)", raw[f][i])
        if m:
            recs += [r.rstrip(".,;:)") for r in REC.findall(m.group(1))]
    return list(dict.fromkeys(recs))


def main(notedir, tsv, out, root="main_note"):
    stream, raw = stream_of(notedir, root)
    idx = collections.defaultdict(list)
    toks = [s[0] for s in stream]
    for k in range(len(toks) - 3):
        idx[tuple(toks[k:k + 4])].append(k)
    res = {}
    with open(tsv, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE):
            f, line, cov = locate(r["quote"], stream, idx)
            res[r["key"]] = {"loc": f"{f}.tex:{line}" if f else None, "coverage": cov,
                             "match": "found" if cov >= 0.8 else "partial",
                             "records": records_near(raw, f, line) if f else []}
    json.dump(res, open(out, "w"), indent=1)
    print(f"{len(res)} quotes; found {sum(v['match'] == 'found' for v in res.values())}; "
          f"partial {sum(v['match'] == 'partial' for v in res.values())}")


def self_test():
    import tempfile
    d = tempfile.mkdtemp()
    open(os.path.join(d, "main_note.tex"), "w").write("\\input{preamble}\n\\input{sec_a}\n% \\input{sec_dead}\n")
    open(os.path.join(d, "sec_a.tex"), "w").write(
        "% DECISION-20261101-joseph-x.md governs this\nIntro text here.\n"
        "The coverage of the \\emph{reported} intervals has not been validated.\n")
    open(os.path.join(d, "sec_dead.tex"), "w").write("The coverage of the reported intervals has not been validated.\n")
    stream, raw = stream_of(d)
    idx = collections.defaultdict(list)
    toks = [s[0] for s in stream]
    for k in range(len(toks) - 3):
        idx[tuple(toks[k:k + 4])].append(k)
    f, line, cov = locate("The coverage of the reported intervals has not been validated.", stream, idx)
    ok = (f, line, cov) == ("sec_a", 3, 1.0) and records_near(raw, f, line) == ["DECISION-20261101-joseph-x.md"]
    ok &= locate("An entirely different sentence about flux weights.", stream, idx)[0] is None
    ok &= "sec_dead" not in closure(d)
    print("SELF-TEST ::", "PASS" if ok else "FAIL", "(true quote located to file:line with its comment record; "
          "absent quote unlocated; a commented-out \\input stays outside the closure)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    self_test() if "--self-test" in sys.argv else main(*sys.argv[1:5])
