"""Fail loudly unless every \\pubhold{...} in the given .tex files is a sentence of its own.

usage: python3 -I check_holds.py [--inventory HOLD-INVENTORY.md] file.tex [file.tex ...]
A hold is "standalone" when, after LaTeX comments are removed, the previous non-space
character is sentence-final (. ! ?) or a paragraph/file start, and the next non-space
character starts a new sentence (capital letter, a backslash command, or end of text).
Exit 0: all standalone (count printed). Exit 1: a hold shares its sentence with other text.

--inventory (2026-11-16, the director, relaying Joseph): the record inventory that section 7 printed as a hold is
carried by the draft-only cover sheet HOLD-INVENTORY.md. With the sheet given, exit 1 also unless the holds found are
exactly the sheet's "Holds the paper still prints" list (whitespace collapsed), so a hold the sheet does not carry, or
the inventory printed again, fails here too. make_rater_copy.sh passes the sheet when the tree has one.
"""
import re
import sys


def strip_comments(text):
    out = []
    for line in text.split("\n"):
        m = re.search(r"(?<!\\)%", line)
        out.append(line[: m.start()] if m else line)
    return "\n".join(out)


def listed_holds(sheet_path):
    """The backticked texts of the sheet's "Holds the paper still prints" list."""
    vis = re.sub(r"<!--.*?-->", "", open(sheet_path, encoding="utf-8").read(), flags=re.S)
    m = re.search(r"^## Holds the paper still prints\n(.*?)(?=^## )", vis, flags=re.S | re.M)
    return sorted(" ".join(h.split()) for h in re.findall(r"^- `([^`]+)`", m.group(1), flags=re.M)) if m else None


def main(paths):
    inventory = None
    if paths[:1] == ["--inventory"]:
        inventory, paths = paths[1], paths[2:]
    bad = 0
    total = 0
    args = []
    for path in paths:
        raw = open(path, encoding="utf-8").read()
        text = strip_comments(raw)
        for m in re.finditer(r"\\pubhold\{", text):
            if re.match(r"\\newcommand\{\\pubhold\}", text[max(0, m.start() - 12): m.end()]) or \
               text[max(0, m.start() - 12): m.start()].endswith("\\newcommand{"):
                continue
            depth, i = 1, m.end()
            while depth and i < len(text):
                depth += {"{": 1, "}": -1}.get(text[i], 0)
                i += 1
            total += 1
            line_no = text.count("\n", 0, m.start()) + 1
            before = text[: m.start()].rstrip()
            after = text[i:].lstrip()
            gap_before = text[len(before): m.start()]
            prev_ok = (not before) or before[-1] in ".!?" or "\n\n" in gap_before or before.endswith("\\par")
            next_ok = (not after) or after[0].isupper() or after[0] == "\\" or "\n\n" in text[i: len(text) - len(after)]
            arg = " ".join(text[m.end(): i - 1].split())
            args.append(arg)
            verdict = "standalone" if (prev_ok and next_ok) else "SHARES-SENTENCE"
            print(f"{path}:{line_no}: {verdict}: \\pubhold{{{arg}}}")
            if verdict != "standalone":
                print(f"   before: ...{before[-60:]!r}\n   after: {after[:60]!r}...")
                bad += 1
    print(f"holds found: {total}; sharing a sentence: {bad}")
    if inventory:
        want = listed_holds(inventory)
        if want != sorted(args):
            print(f"FAIL: the holds found are not the cover sheet's list ({inventory}):\n   found  {sorted(args)}\n   listed {want}")
            return 1
        print(f"the holds found are the cover sheet's list ({len(want)})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
