#!/usr/bin/env python3
"""Re-point `file.tex:N` line references inside TeX comments after the reflow.

    remap_comment_refs.py MAP.json BASE_SRC_DIR FILE ...

In the comment text of each reflowed FILE, a reference `X.tex:N`, `X.tex:N-M`, and the continuations `, :N` that
follow it are rewritten through the reflow map when X.tex is a reflowed file of this directory and N lies inside
its pre-reflow length. A comment that also carries a commit sha (7-40 hex digits) cites a dated version, and is left
as it is. Everything left alone is listed with its reason; every rewrite is printed.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[6] / "analysis-note"))
from reflow_tex import split_comment  # noqa: E402

REF = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*\.tex):(\d+)(?:-(\d+))?((?:,\s*:\d+(?:-\d+)?)*)")
CONT = re.compile(r"(,\s*:)(\d+)(?:-(\d+))?")
SHA = re.compile(r"\b[0-9a-f]{7,40}\b")


def main(argv: list[str]) -> int:
    maps = json.loads(Path(argv[0]).read_text())
    base = Path(argv[1])
    lengths = {k: len((base / k).read_text().split("\n")) for k in maps}
    for f in map(Path, argv[2:]):
        lines = f.read_text().split("\n")
        changed = False
        for i, line in enumerate(lines):
            code, com = split_comment(line)
            if not com or not REF.search(com):
                continue
            if SHA.search(com):
                print(f"KEEP {f.name}:{i + 1}: the comment cites a commit, so its line numbers are dated")
                continue

            def one(name: str, a: str, b: str | None) -> str:
                lo = int(a)
                hi = int(b) if b else None
                if lo > lengths[name] or (hi and hi > lengths[name]):
                    raise ValueError(f"{name}:{a}{'-' + b if b else ''} is past the pre-reflow end")
                nlo = maps[name][lo - 1]
                if hi is None:
                    return str(nlo)
                nhi = maps[name][hi - 1]
                return str(nlo) if nlo == nhi else f"{nlo}-{nhi}"

            def sub(m: re.Match) -> str:
                name = m.group(1)
                if name not in maps:
                    return m.group(0)
                try:
                    head = f"{name}:{one(name, m.group(2), m.group(3))}"
                    tail = CONT.sub(lambda c: c.group(1) + one(name, c.group(2), c.group(3)), m.group(4) or "")
                except ValueError as e:
                    print(f"KEEP {f.name}:{i + 1}: {e}")
                    return m.group(0)
                return head + tail

            new = REF.sub(sub, com)
            if new != com:
                print(f"REMAP {f.name}:{i + 1}: {[m.group(0) for m in REF.finditer(com)]} -> "
                      f"{[m.group(0) for m in REF.finditer(new)]}")
                lines[i] = code + new
                changed = True
        if changed:
            f.write_text("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
