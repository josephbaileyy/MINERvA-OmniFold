#!/usr/bin/env python3
"""Check Markdown by RENDERING it, not by reading its source.

WHY THIS EXISTS. Self-rounds 29 and 30 found four defects of this lane's that thirteen
independent reviews had passed over, and every one was invisible in the source: pipes inside code
spans silently dropping half a table row, a row torn across two lines, a table cell one short that a
code-span pipe made LOOK complete, and a stranded bold marker that rendered as a literal pair of asterisks (⚠ described here at first as
"re-pairing every `**` after it", which rendering later showed it did not). Every
check before then counted characters or matched strings in the source. This one parses with a real
CommonMark + GFM-table parser (markdown-it-py) and inspects what a reader would actually see.

Two checks, scoped to inline blocks that contain a line changed since BASE (default 177af61b):
  leaks  -- `**` or a backtick that survives parsing as LITERAL TEXT, i.e. a formatting marker the
            parser could not pair. (Deliberately escaped markers -- `\\*\\*` -- also land here; the
            report says so, and a human must read each hit. This check lists, it does not judge.)
  links  -- every relative link AND image resolves to a file that exists and is tracked, or to a
            directory holding at least one tracked file (hrefs are percent-decoded first). A link to an
            untracked file works on the author's disk and breaks on every other clone.

Both checks run a built-in POSITIVE CONTROL first and refuse (exit 2) if it does not fire: a
filter must be shown to act in the direction it filters before its silence means anything.

Exit 0 clean, 1 hits, 2 cannot look.  Usage: [--since REV] [--links-only | --leaks-only]
"""
import os
import re
import subprocess
import sys
from urllib.parse import unquote

try:
    from markdown_it import MarkdownIt
except ImportError:
    print("[render] CANNOT LOOK :: markdown-it-py is not installed"); sys.exit(2)

MD = MarkdownIt("commonmark").enable(["table", "strikethrough"])   # no linkify: optional dep


def changed_md(base):
    # -z: `.split()` here silently dropped changed files whose names contain a space; the review-#11b
    # repair fixed only `ls-files` (review #12b)
    # `git diff BASE` with no `..HEAD` compares BASE with the WORKING TREE, staged files included: the
    # runner checks the tree that is about to become a commit, and `..HEAD` only ever saw the parent's
    # lines (review #13b appended an uncommitted dead link and a stranded marker; this reported CLEAN)
    out = subprocess.run(["git", "diff", "--name-only", "-z", base], capture_output=True, text=True)
    return [f for f in out.stdout.split("\0") if f.endswith(".md") and os.path.exists(f)]


HTML_REF = re.compile(r"""<(?:a|img)\b[^>]*?\b(?:href|src)\s*=\s*["']([^"']+)["']""", re.I)


def added_lines(base, f):
    d = subprocess.run(["git", "diff", "-U0", base, "--", f], capture_output=True, text=True).stdout
    s = set()
    for m in re.finditer(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", d, re.M):
        a = int(m.group(1)); s.update(range(a, a + int(m.group(2) or 1)))
    return s


def inline_blocks(src, only=None):
    for t in MD.parse(src):
        if t.type == "inline" and t.map:
            if only is None or set(range(t.map[0] + 1, t.map[1] + 1)) & only:
                yield t


def leaks(src, only=None):
    return [(t.map[0] + 1, c.content.strip()[:100]) for t in inline_blocks(src, only)
            for c in (t.children or []) if c.type == "text" and ("**" in c.content or "`" in c.content)]


def links(path, src, tracked, only=None):
    bad = []
    for t in MD.parse(src):
        # an HTML BLOCK is a block token, never an inline one: `<img src="x.png">` alone on a line was
        # never checked (review #13b)
        if t.type == "html_block" and t.map and (only is None or set(range(t.map[0] + 1, t.map[1] + 1)) & only):
            for href in HTML_REF.findall(t.content):
                bad.extend(_check(path, href, tracked, t.map[0] + 1))
    for t in inline_blocks(src, only):
        for c in (t.children or []):
            # images too: the docstring promised "every relative link", and review #11b found images
            # and directory links were never checked
            if c.type in ("html_inline",):
                hrefs = HTML_REF.findall(c.content)     # <a href> and <img src> were never checked (review #12b)
            elif c.type in ("link_open", "image"):
                hrefs = [c.attrs.get("href", "") if c.type == "link_open" else c.attrs.get("src", "")]
            else:
                continue
            for href in hrefs:
                bad.extend(_check(path, href, tracked, t.map[0] + 1))
    return bad


def _check(path, href, tracked, line):
    bad = []
    if True:
        if True:
            # markdown-it PERCENT-ENCODES hrefs: a tracked file with a space in its name was reported
            # missing as "MINERvA%20with%20..." (review #11b)
            href = unquote(href)
            if re.match(r"^(https?:|mailto:|#)", href):
                return bad
            rel = re.split(r"[?#]", href)[0]          # `?plain=1` and `#anchor` are not part of the path
            if not rel:
                return bad
            # a leading `/` is REPOSITORY-root-relative on GitHub, not filesystem-root (review #12b)
            tgt = os.path.normpath(rel.lstrip("/") if rel.startswith("/") else os.path.join(os.path.dirname(path), rel))
            if not os.path.exists(tgt):
                bad.append((line, href, "missing"))
            elif os.path.isfile(tgt) and tgt not in tracked:
                bad.append((line, href, "untracked"))
            elif os.path.isdir(tgt) and not any(x.startswith(tgt.rstrip("/") + "/") for x in tracked):
                bad.append((line, href, "directory holds no tracked file"))
    return bad


def controls(tracked):
    ok = True
    if not leaks("a **stranded bold closer.** here**\n"):
        print("[render] CONTROL FAILED :: a stranded ** was not reported"); ok = False
    if leaks("clean **bold** and `code`\n"):
        print("[render] CONTROL FAILED :: clean markup was reported"); ok = False
    probe = "docs/orchestration/CATALOG.md"
    if not links(probe, "[x](MISSING-CONTROL-does-not-exist.md)\n", tracked):
        print("[render] CONTROL FAILED :: a missing link target was not reported"); ok = False
    if links(probe, "[x](CATALOG.md)\n", tracked):
        print("[render] CONTROL FAILED :: a real, tracked link target was reported"); ok = False
    # its OWN file with a space in the name, made for the purpose: this control once ran only if the repository
    # happened to hold such a file directly under docs/, and would have been skipped silently -- "controls
    # passed" -- without one (self-round 68). `_check` reads the disk too, so the file must really exist
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        spaced = os.path.join(td, "a b.md")
        open(spaced, "w").close()
        if links(os.path.join(td, "x.md"), "[x](<a b.md>)\n", set(tracked) | {spaced}):
            print("[render] CONTROL FAILED :: a tracked file with a space in its name was reported"); ok = False
        if not links(os.path.join(td, "x.md"), "[x](<a b.md>)\n", set(tracked)):
            print("[render] CONTROL FAILED :: an UNTRACKED file with a space in its name was not reported"); ok = False
    if links(probe, "[x](/KNOWN_ISSUES.md) and [y](CATALOG.md?plain=1)\n", tracked):
        print("[render] CONTROL FAILED :: a repo-root-relative or query-suffixed link to a real file was reported"); ok = False
    if not links(probe, '<img src="MISSING-CONTROL-block.png">\n', tracked):
        print("[render] CONTROL FAILED :: a missing target in an HTML BLOCK was not reported"); ok = False
    if not links(probe, '<a href="MISSING-CONTROL-html.md">x</a>\n', tracked):
        print("[render] CONTROL FAILED :: a missing HTML <a href> target was not reported"); ok = False
    if not links(probe, "![x](MISSING-CONTROL-image.png)\n", tracked):
        print("[render] CONTROL FAILED :: a missing IMAGE target was not reported"); ok = False
    return ok


def main():
    args = sys.argv[1:]
    base = "177af61b"
    if "--since" in args:
        k = args.index("--since"); base = args[k + 1]; del args[k:k + 2]
    # run from the repository root, whatever the caller's directory (the gfm probe failed open without this)
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    if not root:
        print("[render] CANNOT LOOK :: not inside a git work tree"); return 2
    os.chdir(root)
    # -z: `.split()` on newline output broke every path containing a space (review #11b)
    tracked = set(x for x in subprocess.run(["git", "ls-files", "-z"], capture_output=True,
                                             text=True).stdout.split("\0") if x)
    if not controls(tracked):
        print("[render] CANNOT LOOK :: a built-in control failed, so silence would mean nothing"); return 2
    files = changed_md(base)
    if not files:
        print("[render] CANNOT LOOK :: no changed .md files"); return 2
    hits = 0
    for f in files:
        src = open(f, encoding="utf-8").read(); only = added_lines(base, f)
        if "--links-only" not in args:
            for ln, txt in leaks(src, only):
                hits += 1; print(f"  leak   {f}:~{ln}  {txt!r}")
        if "--leaks-only" not in args:
            for ln, href, why in links(f, src, tracked, only):
                hits += 1; print(f"  link   {f}:~{ln}  ({href}) {why}")
    print(f"\n[render] {'HITS' if hits else 'CLEAN'} :: {hits} hit(s) across {len(files)} file(s) "
          f"changed in the WORKING TREE since {base}; controls passed")
    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
