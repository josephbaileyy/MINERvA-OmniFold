"""Log every \\fvval key, values.tex macro and printed phrase that #981's build checks (D6 clean-env claim map).

usage: python3 log_checks.py <build_package.py> <out.tsv>
Imports the build, wraps Ctx.key/macro/printed to record (kind, file, name), and calls assemble(), which reads only.
Writes only <out.tsv> (outside the checkout).
"""
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("bp", sys.argv[1])
bp = importlib.util.module_from_spec(spec)
sys.dont_write_bytecode = True
spec.loader.exec_module(bp)
log = []
k0, m0, p0 = bp.Ctx.key, bp.Ctx.macro, bp.Ctx.printed


def key(self, fname, k, got):
    log.append(("key", fname, k, got))
    return k0(self, fname, k, got)


def macro(self, fname, m, got):
    log.append(("macro", fname, m, got))
    return m0(self, fname, m, got)


def printed(self, fname, phrase, doc="paper"):
    log.append(("printed:" + doc, fname, " ".join(phrase.split())[:160], ""))
    return p0(self, fname, phrase, doc)


bp.Ctx.key, bp.Ctx.macro, bp.Ctx.printed = key, macro, printed
pkg, pending, c = bp.assemble()
with open(sys.argv[2], "w") as f:
    for row in log:
        f.write("\t".join(str(x).replace("\t", " ").replace("\n", " ") for x in row) + "\n")
print(f"logged {len(log)} checks; files {len(pkg)}; pending {[p for p, _ in pending]}; n_checked {sum(c.n_checked.values())}")
