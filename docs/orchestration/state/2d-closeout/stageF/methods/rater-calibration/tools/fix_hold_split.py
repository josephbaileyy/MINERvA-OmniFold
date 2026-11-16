"""usage: python3 -I fix_hold_split.py NORMAL.txt RATER.txt   (rewrites NORMAL.txt in place)
       python3 -I fix_hold_split.py --self-test

A [HOLD: ...] span that crosses a page break can have other text emitted inside it: pdftotext writes the next page's
first block, here the end of a limitations item, between the page number and the hold's continuation (2026-11-16,
Fig. 1 B' reflowed section 7). Removing the span by its brackets would then delete that paper text from the rater copy.

For each hold span holding a form feed, take the text after the page break (minus a page-number line). The longest
token prefix of it that occurs verbatim in the hold-free RATER build's text is the interleaved block. It is moved to
just after the span's closing bracket, so the word multiset is unchanged. Fail when the block is shorter than five
tokens or does not end a sentence: then no rule here describes the layout. A span without a form feed is untouched."""
import re
import sys

HOLD = re.compile(r"\[HOLD:.*?\]", re.S)


def fix(normal, rater):
    rk = " ".join(rater.split())
    out, pos, moved = [], 0, []
    for m in HOLD.finditer(normal):
        s = m.group(0)
        if "\f" not in s:
            continue
        a, b = s.split("\f", 1)
        lines = b.split("\n")
        i = 0
        while i < len(lines) and not lines[i].strip():
            i += 1
        pn = ""
        if i < len(lines) and re.fullmatch(r"\s*\d{1,3}\s*", lines[i]):
            pn, i = lines[i].strip(), i + 1
        toks = "\n".join(lines[i:]).split()
        k = 0
        for j in range(1, len(toks)):
            if " ".join(toks[:j]) in rk:
                k = j
            else:
                break
        if k < 5 or not toks[k - 1].endswith("."):
            sys.exit(f"FAIL: a hold span crosses a page break, but its interleaved block ({k} tokens: "
                     f"{' '.join(toks[:k])[:80]!r}) is not a whole sentence run found in the rater build")
        new = a.rstrip() + " " + " ".join(toks[k:]) + "\f" + (pn + "\n" if pn else "\n") + " ".join(toks[:k]) + "\n"
        out += [normal[pos:m.start()], new]
        pos = m.end()
        moved.append(" ".join(toks[:k]))
    out.append(normal[pos:])
    return "".join(out), moved


def self_test():
    n = "Body one. [HOLD: alpha beta gamma\f\n18\nNext page text runs on. It ends here. delta epsilon.] Tail."
    r = "Body one.\f\n18\nNext page text runs on. It ends here. Tail."
    t, mv = fix(n, r)
    assert mv == ["Next page text runs on. It ends here."], mv
    assert HOLD.findall(t) == ["[HOLD: alpha beta gamma delta epsilon.]"], HOLD.findall(t)
    assert sorted(t.split()) == sorted(n.split()), "the word multiset changed"
    assert fix("A [HOLD: x y] B", "A B")[1] == [], "a span without a page break is untouched"
    print("FIX-HOLD-SPLIT SELF-TEST :: PASS")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test(); sys.exit(0)
    p, q = sys.argv[1:3]
    t, mv = fix(open(p, encoding="utf-8").read(), open(q, encoding="utf-8").read())
    open(p, "w", encoding="utf-8").write(t)
    print(f"fix_hold_split: {len(mv)} interleaved block(s) moved out of hold spans" + "".join(f"\n  moved: {x}" for x in mv))
