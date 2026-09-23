#!/usr/bin/env python3
"""List quotations whose words were never written anywhere else. A LISTER, not a gate.

WHY THIS EXISTS. Self-round 42 swept every `*"..."*` quotation on a line changed since BASE and
found two of this lane's quotes were paraphrases wearing quotation marks -- the text they "quote"
was never written in that form -- plus a third, older one from another lane. Thirteen independent
reviews had passed over all three, because a quotation READS as evidence and nobody re-opened the
source.

A quote is listed when a fragment of it appears nowhere in the tracked tree (other than at its own
quoting site) and nowhere in commit messages. Each listed quote is then classified from history:
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
import re
import subprocess
import sys


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
    files = [f for f in git("diff", "--name-only", f"{base}..HEAD").split() if f.endswith(".md")]
    quotes = set()
    for f in files:
        for l in git("diff", "-U0", f"{base}..HEAD", "--", f).splitlines():
            if l.startswith("+") and not l.startswith("+++"):
                quotes.update((f, m.group(1)) for m in re.finditer(r'\*"([^"]{24,400}?)"\*', l))
    if not quotes:
        print("[quotes] CANNOT LOOK :: no quotations on changed lines"); return 2
    corpus = []
    for t in git("ls-files", "*.md", "*.py", "*.sh", "*.tex", "*.json").split():
        try:
            corpus.append(norm(open(t, errors="ignore").read()))
        except OSError:
            pass
    corpus = "\n".join(corpus)
    msgs = norm(git("log", "--format=%B"))
    listed = 0
    for f, q in sorted(quotes):
        parts = [p.strip() for p in re.split(r"\.\.\.|…", norm(q)) if len(p.strip()) >= 12]
        if not parts or all(corpus.count(p) >= 2 or p in msgs for p in parts):
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
