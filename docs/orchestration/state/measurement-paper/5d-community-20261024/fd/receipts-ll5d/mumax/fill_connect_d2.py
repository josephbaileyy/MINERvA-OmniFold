"""Fill connect-g2r-d2.sh's placeholders from git at PKG: PKG and the sha256 of ll5d_mumax.py, ll5d_b.py and
geant_full.py there.   python3 fill_connect_d2.py <wt> <PKG> <template> <out>"""
import hashlib, re, subprocess, sys
wt, pkg, tpl, out = sys.argv[1:5]
MX = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ll5d/mumax"
GF = "docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/lrows-g/geant_full.py"
h = lambda p: hashlib.sha256(subprocess.run(["git", "-C", wt, "show", f"{pkg}:{p}"], capture_output=True, check=True).stdout).hexdigest()
assert re.fullmatch(r"[0-9a-f]{40}", pkg)
vals = {"__PKG__": pkg, "__SHA_MUMAX__": h(f"{MX}/ll5d_mumax.py"), "__SHA_LL5DB__": h("nd-unfolding/ll5d_b.py"), "__SHA_GF__": h(GF)}
s = open(tpl).read()
for k, v in vals.items():
    assert s.count(k) == 1, k
    s = s.replace(k, v)
assert not re.search(r"__[A-Z0-9_]+__", s)
open(out, "w").write(s)
for k, v in vals.items():
    print(k, v)
