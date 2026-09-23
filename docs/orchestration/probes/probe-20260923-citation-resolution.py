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
     def / async def / class, assignment targets (tuples too), annotated assignments, imports,
     `with ... as` and `for` targets, and names a function declares `global` AND assigns, including those under a
     module-level if/try/with/for/while (⚠ loop bodies, `as` targets and `global` were first missed;
     review #17b). A method, a nested def or a local does not count
     (the first version matched any indented `def` or `name =` line; review #16b). A basename shared
     by two files is reported AMBIGUOUS, not resolved. A miss whose symbol is `py`/`sh` is a file name
     that the pattern misreads as `module.symbol`, not a citation.
  D  every space-free backticked span on an added line that contains `/` (self-round 66), resolved as
     a path or directory at REV, directly or relative to the citing file's directory or to
     docs/orchestration/ (the tree's `probes/...` shorthand). A span holding `…`, `<`, `>`, `$`, `{`, `}`
     or `*` is a pattern or a placeholder, not a path: it is COUNTED as unexaminable and listed, not
     skipped. ⚠ A bare span (not `./` or `../`) is deduplicated tree-wide and resolved from its FIRST citing
     file's directory only, so the same span failing from another directory is not listed (review #20b: latent;
     no recorded range hides a miss this way). Most misses are not repository paths at all -- ratios, refs, cluster product
     directories -- and a human classifies them.

Exits 0 once it has looked: it is a lister, and a human classifies what it prints. Exits 2 when it
cannot look -- outside a git work tree, or when BASE or REV does not name a commit. The result DEPENDS ON
THE CLONE: a token that sits in a remote this clone has not fetched counts as unresolved. It runs from
the repository root whatever the caller's directory (self-round 64: `git diff`'s `'*.md'` pathspec and
`git ls-files` resolve relative to the caller, so parts A, B and C all read a different operand per
directory -- A read 26, 10 and 0 files from the root, docs/orchestration/ and nd-unfolding/ -- and
outside the repository it printed "0 resolve, 0 do not" at exit 0. ⚠ This first blamed `git diff` for
being root-relative and named part C alone; its OUTPUT is root-relative, its pathspec is not; review #17a).
"""
import ast
import os
import re
import symtable
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
                for it in n.items:
                    if it.optional_vars is not None:
                        targets(it.optional_vars)
                walk(n.body)
            elif isinstance(n, (ast.For, ast.AsyncFor, ast.While)):
                if not isinstance(n, ast.While):
                    targets(n.target)
                walk(n.body); walk(n.orelse)
    walk(tree.body)
    # a `global NAME` inside a function binds a module-level name -- but only if that function ASSIGNS it: a
    # `global` that is only read binds nothing (review #18b; first added unconditionally, review #17b)
    # a `global` binds a module-level name only where that scope ASSIGNS it -- read from Python's own `symtable`,
    # which knows every binding form. A hand-made scope walker, the second version, still erred at the edges:
    # comprehension targets, `def`/`class`/`except ... as` under a `global` (review #20b; first version #18b)
    def scopes(tab):
        yield tab
        for ch in tab.get_children():
            yield from scopes(ch)
    try:
        top = symtable.symtable(git("show", f"{REV}:{path}").stdout, path, "exec")
        for tab in scopes(top):
            if tab.get_type() != "module":
                names.update(s.get_name() for s in tab.get_symbols() if s.is_declared_global() and (s.is_assigned() or s.is_imported()))
    except (SyntaxError, ValueError):
        pass
    return names


seen, ok, miss, ambiguous, unparsable, gone = set(), 0, [], [], [], []
for f, L in added:
    for m in re.finditer(r"`([\w/.-]+\.py)::(\w+)`|`([A-Za-z_]\w*)\.([A-Za-z_]\w*)(?:\(\))?`", L):
        if m.group(1):
            # `./x.py` and `../x.py` are relative to the CITING file; they were once reported "not at REV" (#18b)
            q = m.group(1)
            rel = os.path.normpath(os.path.join(os.path.dirname(f), q)) if q.startswith(("./", "../")) else None
            cand = [p for p in py if p == rel] if rel else [p for p in py if p == q or p.endswith("/" + q)]
            sym, key = m.group(2), m.group(0)
        else:
            cand, sym, key = bymod.get(m.group(3), []), m.group(4), m.group(0)
            if not cand:
                continue                  # not a module of this repo
        # a relative span means something different from each citing directory: dedupe it per directory (#19b)
        dkey = (os.path.dirname(f), key) if key.startswith(("`./", "`../")) else key
        if dkey in seen:
            continue
        seen.add(dkey)
        if sym in ("py", "sh"):
            miss.append((f, key, True)); continue
        if not cand:                      # a `path.py::symbol` whose file is not at REV: renamed or deleted
            gone.append((f, key)); continue
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
      f"{len(ambiguous)} ambiguous (basename shared), {len(unparsable)} in a file that does not parse, "
      f"{len(gone)} citing a file not at REV")
for f, key, isname in miss:
    if not isname:
        print("   ", f, "|", key)
for f, key, cand in ambiguous:
    print("    AMBIGUOUS", f, "|", key, "|", ", ".join(cand))
for f, key, c in unparsable:
    print("    UNPARSABLE", f, "|", key, "|", c)
for f, key in gone:
    # ⚠ this indexed an empty candidate list and crashed at exit 1, losing part D (review #17b)
    print("    FILE NOT AT REV", f, "|", key)

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
        q = re.sub(r"(::\w+|:[\d,-]+)$", "", m.group(1)).rstrip("/")     # `x.py::sym` and `x.py:12` name the file
        dkey = (os.path.dirname(f), q) if q.startswith(("./", "../")) else q     # per directory if relative (#19b)
        if not q or dkey in seen:
            continue
        seen.add(dkey)
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
