#!/usr/bin/env python3
"""List quotations whose words were never written anywhere else. A LISTER, not a gate.

WHY THIS EXISTS. Self-round 42 swept every `*"..."*` quotation on a line changed since BASE and
found two of this lane's quotes were paraphrases wearing quotation marks -- the text they "quote"
was never written in that form -- plus a third, older one from another lane. Thirteen independent
reviews had passed over all three, because a quotation READS as evidence and nobody re-opened the
source.

A quote is listed when a fragment of it appears nowhere UNQUOTED -- neither in the tracked tree nor in
commit messages, with every other quotation removed first (`*"..."*`, curly quotes, plain double
quotes, and blockquote lines), so that a misquote copied to a second site
cannot serve as its own source (it could, until review #11b). Each listed quote is then classified from history:
  born-as-assertion -- the first commit to add its longest fragment added it OUTSIDE quote marks,
                       so a real original existed and a retraction later quoted it. Usually fine.
  BORN-AS-QUOTE     -- the fragment first appeared already inside `*"` or a curly quote, so no
                       original in that wording exists in this repository. Either the source is
                       outside the repo (a job log, a reviewer's report), or it is a MISQUOTE.

⚠ EVERY HIT NEEDS A HUMAN. Known false-positive classes, all seen in round 42: bold or backticks
placed differently in the quote than in the original; straight versus curly quotes; a quote
elided with an ellipsis whose fragments cross a Markdown line break; and sources that live
outside the repository. That is why this exits 0 after listing: its job is to make the short list,
not to decide it.

Usage: [--since REV]   Exit 0 listed, 2 cannot look.
"""
import os
import re
import subprocess
import sys


QUOTE = re.compile(r'\*"([^"]{24,400}?)"\*', re.S)


def dequote(t):
    """Remove every quotation, so only UNQUOTED text can serve as a quote's source.

    ⚠ The first version counted any second occurrence as a source. Review #11b showed the flaw: a
    misquote this lister found was then quoted again in KNOWN_ISSUES row 72, and from that moment the
    copy "sourced" the original and the misquote vanished from the listing. A quotation cannot be
    the evidence for another quotation of the same words."""
    t = QUOTE.sub(" ", t)
    # ⚠ and EVERY OTHER quotation form: review #12b showed a misquote copied into curly quotes, into a
    # `>` blockquote, or into plain double quotes still counted as its own source. Removing them errs
    # toward LISTING, which is the right direction for a lister whose hits a human adjudicates.
    t = re.sub(r"(?m)^\s{0,3}>.*$", " ", t)
    t = re.sub(r"\u201c[^\u201d]{0,600}\u201d", " ", t)
    t = re.sub(r'"[^"\n]{0,600}"', " ", t)
    return t


def norm(t):
    t = re.sub(r"\\([*|`_])", r"\1", t)
    t = re.sub(r"\*\*|`|\*", "", t).replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", t).strip().lower()


def main():
    base = "177af61b"
    a = sys.argv[1:]
    if "--since" in a:
        base = a[a.index("--since") + 1]
    git = lambda *x: subprocess.run(["git", *x], capture_output=True, text=True).stdout
    # -z: `.split()` dropped changed files whose names contain a space (review #12b)
    files = [f for f in git("diff", "--name-only", "-z", base).split("\0") if f.endswith(".md")]
    # run from the repository root whatever the caller's directory (the table probe failed open without it)
    root = git("rev-parse", "--show-toplevel").strip()
    if not root:
        print("[quotes] CANNOT LOOK :: not inside a git work tree"); return 2
    os.chdir(root)
    quotes = set()
    for f in files:
        if not os.path.exists(f):
            continue
        # collect from the WHOLE FILE, keeping quotes that START on a changed line: the first version
        # read single diff lines and never saw a quote wrapped across a line break (review #11b)
        changed = set()
        for m in re.finditer(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", git("diff", "-U0", base, "--", f), re.M):
            a = int(m.group(1)); changed.update(range(a, a + int(m.group(2) or 1)))
        text = open(f, encoding="utf-8", errors="ignore").read()
        for m in QUOTE.finditer(text):
            if text.count("\n", 0, m.start()) + 1 in changed:
                quotes.add((f, re.sub(r"\s+", " ", m.group(1))))
    if not quotes:
        print("[quotes] CANNOT LOOK :: no quotations on changed lines"); return 2
    corpus = []
    for t in git("ls-files", "-z", "*.md", "*.py", "*.sh", "*.tex", "*.json").split("\0"):
        if not t:
            continue
        try:
            corpus.append(norm(dequote(open(t, errors="ignore").read())))
        except OSError:
            pass
    corpus = "\n".join(corpus)
    msgs = norm(dequote(git("log", "--format=%B")))
    listed = 0
    for f, q in sorted(quotes):
        parts = [p.strip() for p in re.split(r"\.\.\.|…", norm(q)) if len(p.strip()) >= 12]
        if not parts or all(p in corpus or p in msgs for p in parts):
            continue
        frags = sorted((x.strip() for x in re.split(r"\*\*|`|\.\.\.|…|\*|\|", q)
                        if len(x.strip()) >= 14), key=len, reverse=True)
        kind = "?"
        if frags:
            commits = git("log", "--all", "--reverse", "-S", frags[0], "--format=%h").split()
            if commits:
                added = [l for l in git("show", commits[0], "--format=", "-U0").splitlines()
                         if l.startswith("+") and frags[0] in l]
                if added:
                    pre = added[0][:added[0].find(frags[0])]
                    # a quote opens with *" or a curly quote; an apostrophe (17's) does not
                    kind = ("BORN-AS-QUOTE" if re.search(r'(\*"|“)[^"”]*$', pre)
                            else "born-as-assertion") + f" @{commits[0]}"
        listed += 1
        print(f"  {kind:32s} {f}\n      *\"{q[:140]}\"*")
    print(f"\n[quotes] LISTED :: {listed} of {len(quotes)} quotation(s) need a human to open the source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
