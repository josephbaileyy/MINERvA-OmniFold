#!/usr/bin/env python3
"""Writes q0_connect.sh from q0_connect.template.sh, embedding cov2d_fence.sh rev 3 (sha256 7e81a721...) and
q0_extract.py (its sha256 pinned in the script) as base64, so the node runs exactly those bytes. Prints the sha256."""
import base64
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
FENCE = ROOT / "docs/orchestration/state/2d-closeout/cov2d-fence-20261122/cov2d_fence.sh"
FENCE_SHA = "7e81a721476da987a0e1262ab2054132bd8440cd49b0dc7a5c4f01d50a310738"
X = HERE.parent / "q0_extract.py"
fence, x = FENCE.read_bytes(), X.read_bytes()
assert hashlib.sha256(fence).hexdigest() == FENCE_SHA
text = (HERE / "q0_connect.template.sh").read_text()
text = (text.replace("@@FENCE_B64@@", base64.encodebytes(fence).decode().rstrip("\n"))
        .replace("@@X_B64@@", base64.encodebytes(x).decode().rstrip("\n"))
        .replace("@@XSHA@@", hashlib.sha256(x).hexdigest()))
assert "@@" not in text
out = HERE / "q0_connect.sh"
out.write_text(text)
print(hashlib.sha256(out.read_bytes()).hexdigest(), out.name)
