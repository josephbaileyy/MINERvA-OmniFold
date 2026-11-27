#!/usr/bin/env python3
"""Build RC10 from RC9's files with the repository's build_rc.py (imported unchanged, read from git).

usage: build_rc10.py REPO RC9_TARBALL SRC WORK OUT
SRC is the edited RC10 tree (zenodo-draft/work/rc10src/pkg). RC10 = RC9 with these changes, each checked here:
  - README.md: the RC10 change list, the 2D step's command and description, the new file's row;
  - expected/values.tex: the article's at origin/main (checked byte-identical to `git show origin/main:...`);
  - code/twod_numbers.py: --twod-pub; the four per-bin comparisons with the published result use the published-edge
    central values; code/verify_rc.py passes it;
  - data/twod/result_2d_published_edges.npz added (byte-identical to the deposit's
    result-products-2d-published-edges/result_2d_published_edges.npz, checked by the caller's manifest).
Every other file must be byte-identical to RC9's, expected/values_inference.tex included. RC9's sha256 is checked, the
build runs twice and the two tarballs must be identical, and RC10-SHA256SUMS.txt is written.
"""
import hashlib, importlib.util, io, subprocess, sys, tarfile
from pathlib import Path

REPO, RC9, SRC, WORK, OUT = (Path(a) for a in sys.argv[1:6])
DRAFT = "9e116f555d99e53a69f10fd0c093c361c916796d"  # build_rc.py as RC9 used it
RC9_SHA = "c06dab214baaa5300a05f3fe30b6f85b1a77231f82808e5eb1975d51107284b7"
CHANGED = {"README.md", "expected/values.tex", "code/twod_numbers.py", "code/verify_rc.py", "SHA256SUMS"}
ADDED = {"data/twod/result_2d_published_edges.npz"}
sha = lambda b: hashlib.sha256(b).hexdigest()
git = lambda ref, path: subprocess.run(["git", "-C", str(REPO), "show", f"{ref}:{path}"], check=True,
                                       capture_output=True).stdout

br_src = git(DRAFT, "publication/release/build_rc.py")
(WORK / "tool").mkdir(parents=True, exist_ok=True); (WORK / "tool" / "build_rc.py").write_bytes(br_src)
spec = importlib.util.spec_from_file_location("build_rc", WORK / "tool" / "build_rc.py")
br = importlib.util.module_from_spec(spec); spec.loader.exec_module(br)
print("build_rc.py sha256", sha(br_src))

b9 = RC9.read_bytes(); assert sha(b9) == RC9_SHA, "RC9 sha256"
rc9 = {}
with tarfile.open(fileobj=io.BytesIO(b9), mode="r:gz") as t:
    for m in t.getmembers():
        if m.isfile():
            rc9[m.name.split("/", 1)[1]] = t.extractfile(m).read()
src = {str(p.relative_to(SRC)): p.read_bytes() for p in SRC.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
assert set(src) == (set(rc9) | ADDED), sorted(set(src) ^ (set(rc9) | ADDED))
assert src["expected/values.tex"] == git("origin/main", "docs/analysis-note/values.tex"), "values.tex is not main's"
assert src["expected/values_inference.tex"] == rc9["expected/values_inference.tex"], "values_inference changed"
files = {}
for rel in sorted(src):
    if rel == "SHA256SUMS":
        continue
    if rel in rc9 and rel not in CHANGED:
        assert src[rel] == rc9[rel], f"{rel} changed but is not in the change list"
    if rel in CHANGED:
        assert src[rel] != rc9.get(rel), f"{rel} is listed as changed but is identical to RC9"
    files[rel] = src[rel]
for rel in ADDED:
    assert rel in files
files["SHA256SUMS"] = ("\n".join(f"{sha(b)}  ./{rel}" for rel, b in sorted(files.items())) + "\n").encode()
n_same = sum(1 for r in files if r in rc9 and r not in CHANGED)
print(f"{n_same} files byte-identical to RC9; changed: {sorted(CHANGED - {'SHA256SUMS'})}; added: {sorted(ADDED)}")

name = "minerva-omnifold-article-release-rc10"
a, b = br.build(files, name), br.build(dict(files), name)
assert a == b, "two builds differ"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / f"{name}.tar.gz").write_bytes(a)
outer = [f"# RC10 tarball (byte-reproducible; assembled with publication/release/build_rc.py, sha256 {sha(br_src)[:8]}...)",
         f"{sha(a)}  {name}.tar.gz", "# contents (the package's own SHA256SUMS)"] + files["SHA256SUMS"].decode().splitlines()
(OUT / "RC10-SHA256SUMS.txt").write_text("\n".join(outer) + "\n")
print(f"{name}.tar.gz", sha(a), len(a), "bytes")
