"""move_check.py -- did each cut-list move's caveats merge or leave, as a fresh coder counts them?

usage: python3 -I move_check.py OLD_INV OLD_BLIND NEW_INV NEW_BLIND OUT.json [--moves M1,M2,...] [--self-test]

OLD_INV/OLD_BLIND: the inventory and blinded text the cut list was made on (58fa0b89); NEW_INV/NEW_BLIND: a fresh
coding of a later paper. moves.tsv and classes.tsv (beside this file) name each move's caveats.

For every NEW statement, the move it belongs to is the one whose proposal or old sentences share the longest run of
the statement's tokens; it is assigned only if that run is at least 6 tokens and half the statement (otherwise it
belongs to no move). Then, per move:
  - old caveats with a statement still printing verbatim in the new text;
  - the distinct new caveats (kind, issue) assigned to it. A merge succeeds if they number at most 1 (MV06, a merge
    INTO C24, may keep C24's one); an M move succeeds if they number 0. More than that is flagged: the coder still
    counts the move's content as separate caveats.
--moves restricts the verdicts to the moves the round says it made; the others are reported as not made.
"""
import collections
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOK = re.compile(r"[a-z0-9]+")


def norm(t):
    t = t.replace("­", "")
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)
    return re.sub(r"\s+", " ", t).strip()


def sentence(text_n, quote):
    q = norm(quote)
    i = text_n.find(q)
    if i < 0:
        return q
    a = max(text_n.rfind(". ", 0, i), text_n.rfind("? ", 0, i))
    a = 0 if a < 0 else a + 2
    b = text_n.find(". ", i + len(q) - 1)
    return text_n[a:len(text_n) if b < 0 else b + 1]


def toks(t):
    return TOK.findall(t.lower().replace("’", "'"))


def longest_run(q, ref):
    best = 0
    ref_idx = collections.defaultdict(list)
    for k in range(len(ref) - 2):
        ref_idx[tuple(ref[k:k + 3])].append(k)
    for j in range(len(q) - 2):
        for k in ref_idx.get(tuple(q[j:j + 3]), []):
            n = 0
            while j + n < len(q) and k + n < len(ref) and q[j + n] == ref[k + n]:
                n += 1
            best = max(best, n)
    return best


def read(p):
    with open(p, encoding="utf-8") as f:
        return [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f, delimiter="\t",
                                                                                     quoting=csv.QUOTE_NONE)]


def check(old_inv, old_blind, new_inv, new_blind, out, made=None, moves=HERE / "moves.tsv", classes=HERE / "classes.tsv"):
    old = collections.OrderedDict()
    for r in read(old_inv):
        old.setdefault((r["kind"], r["issue"].lower()), []).append(r)
    cid = {k: f"C{i:02d}" for i, k in enumerate(old, 1)}
    by_cid = {v: k for k, v in cid.items()}
    cls = {c["cid"]: c for c in read(classes)}
    mv = {m["move"]: m for m in read(moves)}
    on, nn = norm(Path(old_blind).read_text(errors="replace")), norm(Path(new_blind).read_text(errors="replace"))
    nh = re.sub(r"\s+", " ", Path(new_blind).read_text(errors="replace").replace("­", ""))
    refs = {}
    for m in mv.values():
        text = m["proposal"] + " " + " ".join(sentence(on, r["quote"]) for c in m["caveats"].split()
                                              for r in old[by_cid[c]] if r["loc"] != "abstract")
        refs[m["move"]] = toks(text)
    new = read(new_inv)
    assigned = collections.defaultdict(set)
    rows_of = collections.defaultdict(list)
    for r in new:
        q = toks(r["quote"])
        best, who = 0, None
        for name, ref in refs.items():
            n = longest_run(q, ref)
            if n > best:
                best, who = n, name
        if who and best >= 6 and best >= 0.5 * len(q):
            key = (r["kind"], r["issue"].lower())
            assigned[who].add(key)
            rows_of[(who, key)].append(r["quote"])
    res = []
    for name, m in mv.items():
        ids = m["caveats"].split()
        surviving = [c for c in ids if any(re.sub(r"\s+", " ", r["quote"]).strip() in nh or norm(r["quote"]) in nn
                                           for r in old[by_cid[c]] if r["loc"] != "abstract")]
        got = sorted(assigned.get(name, set()))
        allowed = 0 if m["type"] == "M" else 1
        is_made = made is None or name in made
        verdict = ("not made in this round" if not is_made else
                   "OK" if len(got) <= allowed else
                   f"FLAG: a coder counts {len(got)} caveats here (expected at most {allowed})")
        res.append({"move": name, "type": m["type"], "caveats": ids, "made": is_made,
                    "old_caveats_still_printing_verbatim": surviving,
                    "new_caveats_assigned": [{"kind": k, "issue": i, "statements": rows_of[(name, (k, i))]}
                                             for k, i in got],
                    "verdict": verdict})
    Path(out).write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    for r in res:
        print(f"{r['move']:6s} {r['type']:5s} {'made' if r['made'] else '-':4s} new caveats {len(r['new_caveats_assigned'])}"
              f" | old printing verbatim: {' '.join(r['old_caveats_still_printing_verbatim']) or '-'} | {r['verdict']}")
    return res


def self_test():
    import contextlib, io, tempfile
    d = Path(tempfile.mkdtemp())
    (d / "old.txt").write_text("The run period block was added after the data were seen. The cause of the step is not known at all.")
    (d / "new.txt").write_text("The run period block was added after the data were seen and the cause of the step is not known at all. "
                               "The flux shape is assumed flat for every single cell here.")
    hdr = "n\tkind\tloc\tpolarity\tquant\tassigned\tissue\tquote\n"
    (d / "old.tsv").write_text(hdr + "1\tb\tsyst\tneg\tno\tno\tposthoc\tThe run period block was added after the data were seen.\n"
                               "2\tc\tsyst\tneg\tno\tno\tcause\tThe cause of the step is not known at all.\n")
    (d / "classes.tsv").write_text("cid\tkind\tissue\tcls\tq\tmove\tcampaign\tnote\tcomment\n"
                                   "C01\tb\tposthoc\tmerge\t\tMV1\t\t\t\nC02\tc\tcause\tmerge\t\tMV1\t\t\t\n")
    (d / "moves.tsv").write_text("move\ttype\tcaveats\tremoves\thome\tproposal\tretain\tflags\n"
                                 "MV1\tmerge\tC01 C02\t1\there\tThe run period block was added after the data were seen and "
                                 "the cause of the step is not known at all.\t\t\n")
    ok = True
    for new_rows, want in (("1\tb\tsyst\tneg\tno\tno\trun period\tThe run period block was added after the data were seen\n"
                            "2\tc\tsyst\tpos\tno\tno\tflux\tThe flux shape is assumed flat for every single cell here.\n", "OK"),
                           ("1\tb\tsyst\tneg\tno\tno\tposthoc\tThe run period block was added after the data were seen\n"
                            "2\tc\tsyst\tneg\tno\tno\tcause\tthe cause of the step is not known at all.\n", "FLAG")):
        (d / "new.tsv").write_text(hdr + new_rows)
        with contextlib.redirect_stdout(io.StringIO()):
            res = check(d / "old.tsv", d / "old.txt", d / "new.tsv", d / "new.txt", d / "o.json", None,
                        d / "moves.tsv", d / "classes.tsv")
        ok &= res[0]["verdict"].startswith(want)
    print("SELF-TEST ::", "PASS" if ok else "FAIL", "(a merge coded as one caveat is OK and an unrelated statement is "
          "not assigned to it; the same merge coded as two caveats is FLAGGED)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    made = None
    if "--moves" in sys.argv:
        made = set(sys.argv[sys.argv.index("--moves") + 1].split(","))
        a = [x for x in a if x != sys.argv[sys.argv.index("--moves") + 1]]
    check(*a[:5], made=made)
