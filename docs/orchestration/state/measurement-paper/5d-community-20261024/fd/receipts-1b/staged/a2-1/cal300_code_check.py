"""The backstop's 300-draw calibration (schema /1, job 60771025, at 02e71a0b) against the code at a later commit (the
director's ruling of 2026-11-05): is the code that produced its per-cell SDs unchanged?

Those SDs are rates(Rx)[t]["a"]["sd_per_cell"], where Rx comes from _one_set over the state that prepare(a) and
_worker_init build (calibrate_main at 02e71a0b). Starting from those four, at OLD, this walks every module-level
definition they reach: functions, classes and assignments, called or named, in their own module or in another through
`import X as Y` or `from X import f` (module-level or inside the function), over the repository's own modules. It then
compares each reached definition at OLD and NEW by fd_1b_c2.ast_digest (its AST, line numbers and docstrings set
aside). It also reports whether the source text is byte-identical.

Not seen by the walk: names reached only through getattr or strings; calibrate_main's own glue between the four (the
state keys, a.sets), which is printed for reading; and library code (numpy). Prints the record. Exit 0 only if every
reached definition is AST-identical, or differs only in a definition fd_1b_c2.CAL300_EXEMPT names and NEW holds.

With --write-pins PATH it also writes the pins file c2check reads (fd_1b_c2.cal300_code_check): every reached
definition's path and AST digest at OLD, and, for the names in fd_1b_c2.CAL300_EXEMPT, the digest at NEW with the
ruling that admits it. It first requires the 300-draw record's fd_1b_c2 digest to be OLD's file digest, so the pins
describe that record's code.

    python3 cal300_code_check.py OLD NEW [--write-pins nd-unfolding/fd_1b_cal300_pins.json]   (from the repo root)
"""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RECORD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/a2-1/calib-run/calibration.json"
RULING = "the director, 2026-11-05: n=st['n'] equals 02e71a0b's call at st['n'] = 300 (bitwise test in test_fd_1b_a21_e2e)"
ROOTS = [("fd_1b_c2", "prepare"), ("fd_1b_c2", "_worker_init"), ("fd_1b_c2", "_one_set"), ("fd_1b_c2", "rates")]
DIRS = ["nd-unfolding", "2d-unfolding/cov2d",
        "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/clip"]

sys.path.insert(0, str(Path.cwd() / "nd-unfolding"))
import fd_1b_c2  # noqa: E402  (ast_digest and top_level: one implementation with c2check's runtime check)

_src: dict = {}


def source(rev: str, mod: str):
    if (rev, mod) not in _src:
        _src[rev, mod] = None
        for d in DIRS:
            r = subprocess.run(["git", "show", f"{rev}:{d}/{mod}.py"], capture_output=True, text=True)
            if r.returncode == 0:
                _src[rev, mod] = (f"{d}/{mod}.py", r.stdout)
                break
    return _src[rev, mod]


def imports(nodes) -> dict:
    """alias -> ("mod", module) or ("from", module, name), over the repository's own modules only."""
    out = {}
    for n in nodes:
        for d in ast.walk(n):
            if isinstance(d, ast.Import):
                for a in d.names:
                    out[a.asname or a.name] = ("mod", a.name)
            elif isinstance(d, ast.ImportFrom) and d.module and d.level == 0:
                for a in d.names:
                    out[a.asname or a.name] = ("from", d.module, a.name)
    return out


def refs(rev: str, mod: str, node) -> set:
    tree = ast.parse(source(rev, mod)[1])
    tops = {fd_1b_c2_name(n) for n in tree.body} - {None}
    alias = dict(imports([n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]))
    alias.update(imports([node]))
    out = set()
    for d in ast.walk(node):
        if isinstance(d, ast.Name) and isinstance(d.ctx, ast.Load):
            if d.id in alias and alias[d.id][0] == "from" and source(rev, alias[d.id][1]):
                out.add((alias[d.id][1], alias[d.id][2]))
            elif d.id in tops and d.id not in alias:
                out.add((mod, d.id))
        elif isinstance(d, ast.Attribute) and isinstance(d.value, ast.Name) and d.value.id in alias:
            a = alias[d.value.id]
            if a[0] == "mod" and source(rev, a[1]):
                out.add((a[1], d.attr))
    return out


def fd_1b_c2_name(n):
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return n.name
    if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
        return n.targets[0].id
    if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
        return n.target.id
    return None


def closure(rev: str) -> list:
    seen, todo = set(), list(ROOTS)
    while todo:
        m, name = todo.pop()
        if (m, name) in seen:
            continue
        s = source(rev, m)
        node = fd_1b_c2.top_level(s[1], name) if s else None
        if node is None:
            continue                                              # a submodule, a builtin or a library name
        seen.add((m, name))
        todo += sorted(refs(rev, m, node) - seen)
    return sorted(seen)


def main(argv) -> int:
    old, new = argv[0], argv[1]
    rows, ok, exempt_ok = [], True, True
    for m, name in closure(old):
        so, sn = source(old, m), source(new, m)
        do = fd_1b_c2.ast_digest(so[1], name)
        dn = fd_1b_c2.ast_digest(sn[1], name) if sn else None
        to, tn = fd_1b_c2.top_level(so[1], name), (fd_1b_c2.top_level(sn[1], name) if sn else None)
        same_text = tn is not None and ast.get_source_segment(so[1], to) == ast.get_source_segment(sn[1], tn)
        if do != dn and f"{m}.{name}" in fd_1b_c2.CAL300_EXEMPT:
            exempt_ok &= dn is not None
        else:
            ok &= do == dn
        rows.append({"module": m, "name": name, "path": so[0], "ast_sha256_old": do, "ast_sha256_new": dn,
                     "ast_identical": do == dn, "source_identical": same_text})
    for r in rows:
        print(f"{'SAME' if r['ast_identical'] else 'CHANGED':8s} {'text-same' if r['source_identical'] else 'text-diff':9s} "
              f"{r['module']}.{r['name']}")
    glue = {rev: ast.get_source_segment(source(rev, "fd_1b_c2")[1], fd_1b_c2.top_level(source(rev, "fd_1b_c2")[1], "calibrate_main"))
            for rev in (old, new)}
    print("calibrate_main's glue at OLD (for reading):")
    for line in glue[old].splitlines():
        if any(k in line for k in ("prepare(", "_worker_init(", "_one_set", "state = ", "Rx[", "rates(", "a.sets")):
            print("   ", line.strip())
    print(json.dumps({"old": old, "new": new, "roots": [".".join(r) for r in ROOTS], "reached": len(rows),
                      "changed": [f"{r['module']}.{r['name']}" for r in rows if not r["ast_identical"]],
                      "text_differs_ast_same": [f"{r['module']}.{r['name']}" for r in rows
                                                if r["ast_identical"] and not r["source_identical"]]}, indent=1))
    if "--write-pins" in argv:
        out = Path(argv[argv.index("--write-pins") + 1])
        rec_sha = json.loads(Path(RECORD).read_text())["code_sha256"]["fd_1b_c2.py"]
        old_sha = hashlib.sha256(subprocess.run(["git", "show", f"{old}:nd-unfolding/fd_1b_c2.py"], capture_output=True,
                                                check=True).stdout).hexdigest()
        assert rec_sha == old_sha, f"the 300-draw record's fd_1b_c2 ({rec_sha[:8]}) is not {old}'s ({old_sha[:8]})"
        doc = {"schema": "fd-1b-cal300-pins/1", "rev": old, "record": RECORD, "record_fd_1b_c2_sha256": rec_sha,
               "roots": [".".join(r) for r in ROOTS],
               "pins": {f"{r['module']}.{r['name']}": r["ast_sha256_old"] for r in rows},
               "paths": {f"{r['module']}.{r['name']}": r["path"] for r in rows},
               "exempt": {f"{r['module']}.{r['name']}": {"ast_sha256": r["ast_sha256_new"], "rev": new, "ruling": RULING}
                          for r in rows if f"{r['module']}.{r['name']}" in fd_1b_c2.CAL300_EXEMPT}}
        out.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
        print(f"wrote {out} sha256 {hashlib.sha256(out.read_bytes()).hexdigest()}")
    verdict = "IDENTICAL" if ok and rows and all(r["ast_identical"] for r in rows) else \
        "IDENTICAL BUT THE EXEMPT" if ok and exempt_ok else "CHANGED"
    print(f"CAL300-CODE-CHECK :: {verdict} :: {len(rows)} definitions reached from {len(ROOTS)} roots :: "
          f"exempt {list(fd_1b_c2.CAL300_EXEMPT)} :: old={old} new={new}")
    return 0 if ok and exempt_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
