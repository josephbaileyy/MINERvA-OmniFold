"""Fill connect-sd.template.sh's placeholders from git at PKG: PKG and the sha256 there of the package's producer, boxes.py,
the restyle's capture.py, artists.py and overlap.py, restyle_2026_10.py, technote_style.py and reported_cells.py.
   python3 -I fill_connect_sd.py <worktree> <PKG> <template> <out>"""
import hashlib
import re
import subprocess
import sys

wt, pkg, tpl, out = sys.argv[1:5]
PS = "docs/orchestration/state/2d-closeout/stageF/methods/pull-sd-relabel-20261117"
RT = "docs/orchestration/state/2d-closeout/stageF/methods/fig-restyle-20261031/tools"
assert re.fullmatch(r"[0-9a-f]{40}", pkg), pkg


def h(p):
    return hashlib.sha256(subprocess.run(["git", "-C", wt, "show", f"{pkg}:{p}"], capture_output=True,
                                         check=True).stdout).hexdigest()


vals = {"__PKG__": pkg, "__SHA_CPF__": h("2d-unfolding/compare_to_paper_fullcov.py"), "__SHA_BOXES__": h(f"{PS}/boxes.py"),
        "__SHA_CAPTURE__": h(f"{RT}/capture.py"), "__SHA_ARTISTS__": h(f"{RT}/artists.py"),
        "__SHA_OVERLAP__": h(f"{RT}/overlap.py"), "__SHA_RESTYLE__": h("2d-unfolding/restyle_2026_10.py"),
        "__SHA_TECHNOTE__": h("technote_style.py"), "__SHA_RC__": h("2d-unfolding/uq/reported_cells.py")}
s = open(tpl).read()
for k, v in vals.items():
    assert s.count(k) == 1, k
    s = s.replace(k, v)
assert not re.search(r"__[A-Z0-9_]+__", s)
open(out, "w").write(s)
for k, v in vals.items():
    print(k, v)
