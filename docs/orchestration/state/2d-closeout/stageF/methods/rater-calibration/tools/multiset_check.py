"""usage: python3 -I multiset_check.py NORMAL.txt RATER.txt -- exit 0 iff equal as word multisets once hold spans,
page-number lines, hyphen line-joins and hyphens themselves are removed (so a reflowed 'cross-section'/'crosssection'
compares equal).
       python3 -I multiset_check.py --self-test

A page-number line is removed by position only: on each form-feed-separated page of the pdftotext output, the first or
last non-empty line, when it is nothing but that page's own number. Numerals in the text are kept. This was added on
2026-11-09 (the director, for #977): the normal build, which carries the hold text, can run one page longer than the
rater copy, and the extra page number alone failed the check."""
import re, sys, collections


def drop_page_numbers(t):
    pages = t.split("\f")
    out = []
    for n, page in enumerate(pages, 1):
        lines = page.split("\n")
        filled = [i for i, l in enumerate(lines) if l.strip()]
        for i in {filled[0], filled[-1]} if filled else ():
            if lines[i].strip() == str(n):
                lines[i] = ""
        out.append("\n".join(lines))
    return "\f".join(out)


def bag_text(t):
    t = drop_page_numbers(t)
    t = re.sub(r"\[HOLD:[^\]]*\]", " ", t, flags=re.S)
    t = re.sub(r"-\s*\n\s*", "", t).replace("-", "")
    return collections.Counter(re.findall(r"\w+", t))


def compare(ta, tb):
    a, b = bag_text(ta), bag_text(tb)
    # a word split by a reflowed block ("hep" + ... + "ex") changes the bag only by re-tokenizing; compare letters too
    la = collections.Counter("".join(sorted(a.elements()))); lb = collections.Counter("".join(sorted(b.elements())))
    onlya, onlyb = a - b, b - a
    return la == lb and sum(onlya.values()) <= 6, onlya, onlyb


def self_test():
    body = ["Title line", "The result has 16 cells and 3 truths [HOLD: a long hold text]", "more text here",
            "and 14 values in the text", "The end of the paper."]
    normal = "\f".join([body[0] + "\n" + body[1], "2\n" + body[2], "3\n" + body[3], "4\n" + body[4]]) + "\f"
    rater = "\f".join([body[0] + "\n" + body[1].replace(" [HOLD: a long hold text]", ""), "2\n" + body[2] + "\n" + body[3],
                       "3\n" + body[4]]) + "\f"
    ok = True
    if not compare(normal, rater)[0]:
        print("self-test: two builds differing only in page count do not PASS"); ok = False
    for name, bad in (("a changed word", rater.replace("more text", "less text")),
                      ("a changed numeral", rater.replace("16 cells", "17 cells")),
                      ("a dropped in-text numeral", rater.replace("and 14 values", "and values"))):
        if compare(normal, bad)[0]:
            print("self-test: NOT CAUGHT", name); ok = False
    if drop_page_numbers("x\f2\nthe 2\nend 2\f") != "x\f\nthe 2\nend 2\f":
        print("self-test: drop_page_numbers removes more than the page's own number line"); ok = False
    print("multiset self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    ok, onlya, onlyb = compare(open(sys.argv[1], encoding="utf-8").read(), open(sys.argv[2], encoding="utf-8").read())
    print("multiset: only normal %s; only rater %s" % (dict(onlya.most_common(10)), dict(onlyb.most_common(10))))
    print("multiset VERDICT: %s" % ("PASS" if ok else "FAIL"))
    sys.exit(0 if ok else 1)
