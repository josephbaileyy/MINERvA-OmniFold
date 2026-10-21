"""Word-level diff of a normal build's text against the hold-free rater copy.

usage: python3 -I holddiff.py normal.txt rater.txt
Prints every differing word run (raw tokens). Verdict: after deleting the [HOLD: ...] spans
from the normal text and normalizing line-break hyphenation and page-number lines, the two word sequences must be
identical and the rater copy must contain no "HOLD". Exit 1 otherwise.
"""
import difflib
import re
import sys

HOLD = re.compile(r"\[HOLD:.*?\]", re.S)


def key_tokens(text):
    text = re.sub(r"\f[ \t]*\d{1,3}[ \t]*\n", "\f\n", text)  # page numbers move when a hold's removal reflows a page
    text = re.sub(r"-\n[\s\f]*(?=\S)", "", text)   # rejoin words split across lines, blank lines or page breaks
    return [t.replace("-", "").replace("\u00ad", "") for t in text.split()]


def main(normal_path, rater_path):
    normal = open(normal_path, encoding="utf-8").read()
    rater = open(rater_path, encoding="utf-8").read()
    a, b = normal.split(), rater.split()
    print(f"raw words: normal={len(a)} rater={len(b)}")
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            print(f"  {tag}: normal[{i1}:{i2}] [-{' '.join(a[i1:i2])}-]  rater[{j1}:{j2}] {{+{' '.join(b[j1:j2])}+}}")
    holds = HOLD.findall(normal)
    for h in holds:
        print("  hold span in normal build:", " ".join(h.split()))
    ka, kb = key_tokens(HOLD.sub(" ", normal)), key_tokens(rater)
    sm2 = difflib.SequenceMatcher(None, ka, kb, autojunk=False)
    residual = [op for op in sm2.get_opcodes() if op[0] != "equal"]
    for tag, i1, i2, j1, j2 in residual:
        print(f"  NON-HOLD DIFF {tag}: [-{' '.join(ka[i1:i2])}-] {{+{' '.join(kb[j1:j2])}+}}")
    ok = not residual and "HOLD" not in rater and len(holds) >= 0
    print(f"holds in normal={len(holds)}; 'HOLD' in rater={'HOLD' in rater}; non-hold diffs after hyphen normalization={len(residual)}")
    print("VERDICT:", "PASS (only hold text differs)" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
