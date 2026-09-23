#!/usr/bin/env python3
"""Rounds 61-62 of the review-residue loop, made re-runnable (review #15a finding 4).

    probe-20260923-citation-resolution.py [BASE [REV]]      (defaults 177af61b 75bdde7e)

Reads every file at REV via `git show` and lists files with `git ls-tree REV`, never the working tree or
the index, so the result depends only on the two revisions and on which objects this clone holds (⚠ part C
first took its module list from `git ls-files`, the checkout's index; review #16b). The operands are the `.md` files changed between
BASE and REV.

  A  sha-like tokens (7-40 lower-hex, at least one letter and one digit) in the WHOLE of each file,
     counted by occurrence; the distinct ones that do not resolve as a COMMIT (`git cat-file -e
     <t>^{commit}`) are listed. Most are content digests, not commits.
  B  the same tokens restricted to lines ADDED between BASE and REV that resolve to NO object at all
     and whose surrounding 70/40 characters read like a commit citation.
  C  `module.symbol` / `path.py::symbol` code spans on added lines, where `module` is the basename of
     a .py file at REV, resolved against that file's MODULE-LEVEL names as Python's `ast` reads them:
     def / async def / class, assignment targets (tuples too), annotated assignments and imports,
     including those under a module-level if/try/with. A method, a nested def or a local does not count
     (the first version matched any indented `def` or `name =` line; review #16b). A basename shared
     by two files is reported AMBIGUOUS, not resolved. A miss whose symbol is `py`/`sh` is a file name
     that the pattern misreads as `module.symbol`, not a citation.
  D  every space-free backticked span on an added line that contains `/` (self-round 66), resolved as
     a path or directory at REV, directly or relative to the citing file's directory or to
     docs/orchestration/ (the tree's `probes/...` shorthand). A span holding `…`, `<`, `>`, `$`, `{`, `}`
     or `*` is a pattern or a placeholder, not a path: it is COUNTED as unexaminable and listed, not
     skipped. Most misses are not repository paths at all -- ratios, refs, cluster product
     directories -- and a human classifies them.

Exits 0 once it has looked: it is a lister, and a human classifies what it prints. Exits 2 when it
cannot look -- outside a git work tree, or when BASE or REV does not name a commit. The result DEPENDS ON
THE CLONE: a token that sits in a remote this clone has not fetched counts as unresolved. It runs from
the repository root whatever the caller's directory (self-round 64: `git ls-files` prints paths relative
to the caller, `git diff` and `git show REV:path` relative to the root, so part C read 6/18 from the root,
0/2 from docs/orchestration/, and "0 resolve, 0 do not" at exit 0 from outside the repository).
"""
import ast
import os
import re
import subprocess
import sys

BASE, REV = (sys.argv[1:] + ["177af61b", "75bdde7e"][len(sys.argv[1:]):])[:2]
SHA = re.compile(r"(?<![0-9a-fA-F/._-])([0-9a-f]{7,40})(?![0-9a-fA-F])")
CTX = re.compile(r"commit|\bsha\b|HEAD|\bat [0-9a-f]{7}|pushed|landed|\^|\.\.", re.I)


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True)


def shaish(s):
    return bool(re.search(r"[a-f]", s) and re.search(r"\d", s))


def resolves(obj):
    return git("cat-file", "-e", obj).returncode == 0


root = git("rev-parse", "--show-toplevel").stdout.strip()
if not root:
    print("[citations] CANNOT LOOK :: not inside a git work tree")
    sys.exit(2)
os.chdir(root)
for r_ in (BASE, REV):
    if not resolves(r_ + "^{commit}"):
        print(f"[citations] CANNOT LOOK :: {r_!r} does not name a commit in this clone")
        sys.exit(2)

files = [f for f in git("diff", "--name-only", "-z", BASE, REV, "--", "*.md").stdout.split("\0") if f]
occ, unres = 0, set()
for f in files:
    r = git("show", f"{REV}:{f}")
    if r.returncode:
        continue                          # deleted at REV
    for m in SHA.finditer(r.stdout):
        if shaish(m.group(1)):
            occ += 1
            if not resolves(m.group(1) + "^{commit}"):
                unres.add(m.group(1))
print(f"A  {BASE}..{REV}: {len(files)} .md file(s), {occ} sha-like occurrence(s), "
      f"{len(unres)} distinct not resolving as a commit in this clone")

added, cur = [], None
for L in git("diff", "-U0", BASE, REV, "--", "*.md").stdout.splitlines():
    if L.startswith("+++ "):
        cur = L[6:]
    elif L.startswith("+"):
        added.append((cur, L))
hits = []
for f, L in added:
    for m in SHA.finditer(L):
        s = m.group(1)
        if shaish(s) and not resolves(s):
            ctx = L[max(0, m.start() - 70):m.end() + 40]
            if CTX.search(ctx):
                hits.append((f, s, ctx))
print(f"B  {len(hits)} token(s) on added lines resolving to NO object, in commit-like context")
for h in hits:
    print("   ", h[0], "|", h[1], "|", h[2])

at_rev = set(git("ls-tree", "-r", "--name-only", "-z", REV).stdout.split("\0")) - {""}
py = sorted(x for x in at_rev if x.endswith(".py"))
bymod = {}
for p in py:
    bymod.setdefault(os.path.basename(p)[:-3], []).append(p)


def module_names(path):
    """Module-level names of `path` at REV, or None if it does not parse."""
    try:
        tree = ast.parse(git("show", f"{REV}:{path}").stdout)
    except (SyntaxError, ValueError):
        return None
    names = set()

    def targets(node):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, (ast.Tuple, ast.List)):
            for e in node.elts:
                targets(e)
        elif isinstance(node, ast.Starred):
            targets(node.value)

    def walk(body):
        for n in body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(n.name)
            elif isinstance(n, ast.Assign):
                for tg in n.targets:
                    targets(tg)
            elif isinstance(n, (ast.AnnAssign, ast.AugAssign)):
                targets(n.target)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                for a in n.names:
                    names.add(a.asname or a.name.split(".")[0])
            elif isinstance(n, ast.If):
                walk(n.body); walk(n.orelse)
            elif isinstance(n, ast.Try):
                walk(n.body); walk(n.orelse); walk(n.finalbody)
                for h in n.handlers:
                    walk(h.body)
            elif isinstance(n, (ast.With, ast.AsyncWith)):
                walk(n.body)
    walk(tree.body)
    return names


seen, ok, miss, ambiguous, unparsable = set(), 0, [], [], []
for f, L in added:
    for m in re.finditer(r"`([\w/.-]+\.py)::(\w+)`|`([A-Za-z_]\w*)\.([A-Za-z_]\w*)(?:\(\))?`", L):
        if m.group(1):
            cand, sym, key = [p for p in py if p == m.group(1) or p.endswith("/" + m.group(1))], m.group(2), m.group(0)
        else:
            cand, sym, key = bymod.get(m.group(3), []), m.group(4), m.group(0)
            if not cand:
                continue                  # not a module of this repo
        if key in seen:
            continue
        seen.add(key)
        if sym in ("py", "sh"):
            miss.append((f, key, True)); continue
        if len(cand) > 1:
            ambiguous.append((f, key, cand)); continue
        names = module_names(cand[0])
        if names is None:
            unparsable.append((f, key, cand[0])); continue
        if sym in names:
            ok += 1
        else:
            miss.append((f, key, False))
print(f"C  {ok} resolve, {len(miss)} do not; {sum(x[2] for x in miss)} of the misses are file names; "
      f"{len(ambiguous)} ambiguous (basename shared), {len(unparsable)} in a file that does not parse")
for f, key, isname in miss:
    if not isname:
        print("   ", f, "|", key)
for f, key, cand in ambiguous:
    print("    AMBIGUOUS", f, "|", key, "|", ", ".join(cand))
for f, key, c in unparsable:
    print("    UNPARSABLE", f, "|", key, "|", c)

dirs = {os.path.dirname(x) for x in at_rev}
while True:
    up = {os.path.dirname(d) for d in dirs} - dirs
    if not up:
        break
    dirs |= up
known = at_rev | dirs
seen, ok, dmiss, odd = set(), 0, [], []
for f, L in added:
    for m in re.finditer(r"(?<!`)`([^`\s]*/[^`\s]*)`(?!`)", L):
        q = re.sub(r":[\d,-]+$", "", m.group(1)).rstrip("/")
        if not q or q in seen:
            continue
        seen.add(q)
        if re.search(r"[\u2026<>${}*]", q):
            odd.append((f, q)); continue
        if any(os.path.normpath(os.path.join(b, q)) in known for b in ("", os.path.dirname(f), "docs/orchestration")):
            ok += 1
        else:
            dmiss.append((f, q))
print(f"D  {ok} backticked slash-span(s) resolve at {REV}, {len(dmiss)} do not, "
      f"{len(odd)} are patterns or placeholders and not examined")
for f, q in dmiss:
    print("   ", f, "|", q)
for f, q in odd:
    print("    UNEXAMINED", f, "|", q)
sys.exit(0)
