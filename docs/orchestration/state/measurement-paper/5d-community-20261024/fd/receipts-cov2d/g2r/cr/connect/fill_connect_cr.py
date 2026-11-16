"""Fill connect-g2r-cr.sh's placeholders from git at PKG: PKG, fd_gencmp.py's and cr_compare.py's sha256.
    python3 fill_connect_cr.py <wt> <PKG> <template> <out>"""
import hashlib, re, subprocess, sys
wt, pkg, tpl, out = sys.argv[1:5]
C = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/cr"
blob = lambda p: subprocess.run(["git", "-C", wt, "show", f"{pkg}:{p}"], capture_output=True, check=True).stdout
assert re.fullmatch(r"[0-9a-f]{40}", pkg)
vals = {"__PKG__": pkg, "__SHA_GENCMP__": hashlib.sha256(blob("nd-unfolding/fd_gencmp.py")).hexdigest(),
        "__SHA_CMP__": hashlib.sha256(blob(f"{C}/cr_compare.py")).hexdigest()}
s = open(tpl).read()
for k, v in vals.items():
    assert s.count(k) == 1, k
    s = s.replace(k, v)
assert not re.search(r"__[A-Z0-9_]+__", s)
open(out, "w").write(s)
for k, v in vals.items():
    print(k, v)
