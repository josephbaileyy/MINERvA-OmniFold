#!/usr/bin/env python3
"""Assemble an article release candidate as a byte-reproducible tarball.

The tarball is a pure function of its inputs: entries are sorted, every mtime is fixed, owners are 0/0 with empty
names, modes are 0644 (0755 for directories and code/*.py), and the gzip header carries no name or time. Rebuilding
from the same inputs gives the same sha256 (checked by building twice; see the RC README).

Inputs:
  --payload DIR   a tree holding data/frozen/, data/recovery-union/ and data/figs/ (the sufficient inputs and the
                  figure arrays, e.g. an extracted RC4 or the preserved copy on CFS); every file is checked against
                  --payload-sums before use
  --repo DIR      the repository checkout supplying code, README, requirements and expected outputs (default: this
                  checkout)
  --name NAME     the package directory and tarball stem, e.g. minerva-omnifold-article-release-rc5
  --out DIR       where to write NAME.tar.gz (refuses to overwrite)

  python3 publication/release/build_rc.py --payload <dir> --payload-sums <sums> --name <name> --out <dir>
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EPOCH = 1_759_708_800  # 2025-10-06T00:00:00Z, fixed for every entry

# (package path, source path relative to --repo). Code and expected outputs come from the repository.
FROM_REPO = {
    "README.md": "docs/publication/release/RC5-README.md",
    "requirements.txt": "publication/release/requirements.txt",
    "code/verify_rc.py": "publication/release/verify_rc.py",
    "code/replay_inference.py": "publication/release/replay_inference.py",
    "code/make_reading_b.py": "publication/release/make_reading_b.py",
    "code/w1_projected_tests.py": "publication/w1/w1_projected_tests.py",
    "code/m1_f2_norm_ratio.py": "docs/publication/corrections-20261008/m1_f2_norm_ratio.py",
    "code/figs/fig_numbers.py": "publication/release/figs/fig_numbers.py",
    "code/figs/make_figs.py": "publication/release/figs/make_figs.py",
    "code/figs/plot_joint_null_distributions.py": "publication/figures/plot_joint_null_distributions.py",
    "expected/joint-evaluate.json": "docs/orchestration/state/s5p/stage7/joint/joint-evaluate.json",
    "expected/W1-RESULT-20261006.json": "docs/publication/w1/W1-RESULT-20261006.json",
    "expected/resolved-evaluate.json": "docs/orchestration/state/s5p/recovery/phaseC/resolved-evaluate.json",
    "expected/values.tex": "docs/analysis-note/values.tex",
    "expected/values_inference.tex": "docs/analysis-note/values_inference.tex",
    "data/m1f2/MANIFEST.json": "publication/release/rc5-inputs/m1f2/MANIFEST.json",
    "data/anatuple-inventory.tsv": "docs/publication/corrections-20261008/anatuple-inventory-20261008.tsv",
}
M1F2 = [f"{kind}-{g}.npz" for kind in ("delta", "fine-minus-mid") for g in ("genie_cv", "genie_mec", "gibuu_cv", "nuwro_cv")]
FROM_PAYLOAD = [
    "data/frozen/inference_sufficient.npz", "data/frozen/inference_sufficient.npz.manifest.json",
    "data/recovery-union/inference_sufficient.npz", "data/recovery-union/inference_sufficient.npz.manifest.json",
    "data/figs/fig_arrays.npz", "data/figs/fig_arrays.npz.manifest.json",
]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def collect(payload: Path, sums: Path, repo: Path) -> dict[str, bytes]:
    want = {}
    for line in sums.read_text().splitlines():
        h, p = line.split(None, 1)
        want[p.strip().lstrip("*").removeprefix("./")] = h
    files: dict[str, bytes] = {}
    for rel in FROM_PAYLOAD:
        b = (payload / rel).read_bytes()
        if want.get(rel) != sha256(b):
            raise SystemExit(f"payload {rel}: sha256 {sha256(b)} is not the one in {sums}")
        files[rel] = b
    for rel, src in FROM_REPO.items():
        files[rel] = (repo / src).read_bytes()
    for name in M1F2:
        files[f"data/m1f2/{name}"] = (repo / "publication/release/rc5-inputs/m1f2" / name).read_bytes()
    lines = [f"{sha256(b)}  ./{rel}" for rel, b in sorted(files.items()) if rel != "SHA256SUMS"]
    files["SHA256SUMS"] = ("\n".join(lines) + "\n").encode()
    return files


def build(files: dict[str, bytes], name: str) -> bytes:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as tar:
        dirs = sorted({str(Path(name, rel).parent) for rel in files} | {name})
        alld = set()
        for d in dirs:
            parts = Path(d).parts
            for i in range(1, len(parts) + 1):
                alld.add(str(Path(*parts[:i])))
        for path in sorted(alld | {str(Path(name, rel)) for rel in files}):
            rel = str(Path(path).relative_to(name)) if path != name else ""
            ti = tarfile.TarInfo(path)
            ti.mtime, ti.uid, ti.gid, ti.uname, ti.gname = EPOCH, 0, 0, "", ""
            if rel in files:
                ti.type, ti.size = tarfile.REGTYPE, len(files[rel])
                ti.mode = 0o755 if rel.startswith("code/") and rel.endswith(".py") else 0o644
                tar.addfile(ti, io.BytesIO(files[rel]))
            else:
                ti.type, ti.mode = tarfile.DIRTYPE, 0o755
                tar.addfile(ti)
    gz = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=gz, mtime=0, compresslevel=9) as g:
        g.write(raw.getvalue())
    return gz.getvalue()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--payload", type=Path, required=True)
    ap.add_argument("--payload-sums", type=Path, required=True,
                    help="sha256 list covering the payload files (e.g. docs/publication/release/RC4-SHA256SUMS.txt)")
    ap.add_argument("--repo", type=Path, default=ROOT)
    ap.add_argument("--name", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    out = a.out / f"{a.name}.tar.gz"
    if out.exists():
        raise SystemExit(f"{out} exists; refusing to overwrite")
    files = collect(a.payload, a.payload_sums, a.repo)
    blob = build(files, a.name)
    a.out.mkdir(parents=True, exist_ok=True)
    out.write_bytes(blob)
    print(f"{sha256(blob)}  {out.name}  ({len(blob)} bytes, {len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
