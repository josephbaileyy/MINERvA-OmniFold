import ast, os, sys, glob
W = sys.argv[1]; OUT = sys.argv[2]
hits = set()
for f in glob.glob(os.path.join(OUT, "*.txt")):
    for ln in open(f):
        p, _, l = ln.rstrip().rpartition(":")
        hits.add((p, int(l)))

def executable(path):
    src = open(path).read()
    code = compile(src, path, "exec")
    lines = set()
    def walk(co):
        for _, _, l in co.co_lines():
            if l: lines.add(l)
        for c in co.co_consts:
            if hasattr(c, "co_lines"): walk(c)
    walk(code)
    return src.splitlines(), lines

def spans(lines):
    out, start, prev = [], None, None
    for l in sorted(lines):
        if start is None: start = prev = l
        elif l == prev + 1: prev = l
        else: out.append((start, prev)); start = prev = l
    if start is not None: out.append((start, prev))
    return out

for rel in ("2d-unfolding/cov2d/g2r/g2r.py", "2d-unfolding/cov2d/g2r/g2r_prepare.py", "2d-unfolding/cov2d/g2r/g2r_readout.py", "2d-unfolding/re2/re2_driver.py"):
    path = os.path.realpath(os.path.join(W, rel))
    text, ex = executable(path)
    if rel.endswith("re2_driver.py"):
        # the G2R lines only: lines marked # G2R and the body of g2r_miss_override
        tree = ast.parse("\n".join(text))
        fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "g2r_miss_override"][0]
        scope = {l for l in ex if "# G2R" in text[l - 1] or fn.lineno <= l <= fn.end_lineno}
    else:
        scope = ex
    miss = {l for l in scope if (path, l) not in hits}
    # drop module-level docstring/def lines that execute at import but were imported by tests (they are hits); keep as is
    print(f"== {rel}: {len(scope)} executable in scope, {len(miss)} never executed")
    for a, b in spans(miss):
        print(f"   {a}-{b}" if a != b else f"   {a}", "|", text[a - 1].strip()[:90])
