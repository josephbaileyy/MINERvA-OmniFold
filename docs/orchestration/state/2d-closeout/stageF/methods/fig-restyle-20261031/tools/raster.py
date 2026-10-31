#!/usr/bin/env python3
"""The identity control (DECLARATION.md §3 check 2): two PDFs must rasterize to the same pixels.

usage: python3 -I raster.py A.pdf B.pdf [--dpi 300] [--keep DIR]
       python3 -I raster.py --png A.png B.png
Each PDF's pages are rendered by pdftoppm (or by Ghostscript where pdftoppm is missing) at --dpi, as 8-bit RGB, and
compared page by page and pixel by pixel. A cluster-drawn PDF carries a creation date, so the files themselves are not
compared. Exit 0 if every page is equal, 1 otherwise, printing the number of pages and of differing pixels."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


def render(pdf, dpi, out):
    out.mkdir(parents=True, exist_ok=True)
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(pdf), str(out / "p")], check=True)
    else:
        subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", "-sDEVICE=png16m", f"-r{dpi}",
                        f"-sOutputFile={out / 'p-%03d.png'}", str(pdf)], check=True)
    return sorted(out.glob("p-*.png"))


def pixels(p):
    return np.asarray(Image.open(p).convert("RGB"))


def same(pa, pb):
    """(equal, message) for two lists of page images."""
    if len(pa) != len(pb):
        return False, f"{len(pa)} pages against {len(pb)}"
    bad = 0
    for x, y in zip(pa, pb):
        a, b = pixels(x), pixels(y)
        if a.shape != b.shape:
            return False, f"page size {a.shape[1]}x{a.shape[0]} against {b.shape[1]}x{b.shape[0]}"
        bad += int(np.any(a != b, axis=2).sum())
    return bad == 0, f"{len(pa)} page(s), {bad} differing pixel(s)"


def main():
    a = sys.argv[1:]
    if a[0] == "--png":
        ok, msg = same([Path(a[1])], [Path(a[2])])
    else:
        dpi = int(a[a.index("--dpi") + 1]) if "--dpi" in a else 300
        keep = Path(a[a.index("--keep") + 1]) if "--keep" in a else None
        with tempfile.TemporaryDirectory() as t:
            base = keep or Path(t)
            ok, msg = same(render(a[0], dpi, base / "a"), render(a[1], dpi, base / "b"))
    print("RASTER ::", "EQUAL" if ok else "DIFFER", "::", msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
