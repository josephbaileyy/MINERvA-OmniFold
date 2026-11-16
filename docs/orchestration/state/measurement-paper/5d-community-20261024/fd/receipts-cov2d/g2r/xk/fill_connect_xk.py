"""Fill connect-g2r-xk.sh's placeholders from git at PKG: PKG and the sha256 of fd_xcov.py, fd_xcov_steps.py,
xk_copy.py and xk_compare.py there.   python3 fill_connect_xk.py <wt> <PKG> <template> <out>"""
import hashlib, re, subprocess, sys
wt, pkg, tpl, out = sys.argv[1:5]
XK = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/xk"
h = lambda p: hashlib.sha256(subprocess.run(["git", "-C", wt, "show", f"{pkg}:{p}"], capture_output=True, check=True).stdout).hexdigest()
assert re.fullmatch(r"[0-9a-f]{40}", pkg)
vals = {"__PKG__": pkg, "__SHA_XCOV__": h("nd-unfolding/fd_xcov.py"), "__SHA_STEPS__": h("nd-unfolding/fd_xcov_steps.py"),
        "__SHA_COPY__": h(f"{XK}/xk_copy.py"), "__SHA_CMP__": h(f"{XK}/xk_compare.py")}
s = open(tpl).read()
for k, v in vals.items():
    assert s.count(k) == 1, k
    s = s.replace(k, v)
assert not re.search(r"__[A-Z0-9_]+__", s)
open(out, "w").write(s)
for k, v in vals.items():
    print(k, v)
