#!/usr/bin/env python3
"""Write the IBU-1 task table from ``config.json``: one line per experiments chunk (CHUNK seeds), bootstrap
unit or data unit. Deterministic; the committed ``tasks.tsv`` must equal this script's output (test)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHUNK = 25
SMOKE = ("P_d1", "D_P", "D_N")  # the first job: small units that also measure time and memory


def lines(cfg: dict) -> list[str]:
    out = []
    units = cfg["units"]
    for u in sorted(units, key=lambda u: (u["name"] not in SMOKE, u["kind"] != "bootstrap", units.index(u))):
        if u["kind"] != "experiments" or "pairs" in u:
            out.append(f"{u['name']}\t{u['name']}\t")
            continue
        first, last = u["seeds"]
        for s in range(first, last + 1, CHUNK):
            e = min(last, s + CHUNK - 1)
            out.append(f"{u['name']}_{s}\t{u['name']}\t{s}:{e}")
    return out


def render(cfg: dict) -> str:
    head = ("# IBU-1 tasks (make_tasks.py from config.json): <task><TAB><unit><TAB><seeds first:last or empty>. "
            f"Lines 0-{len(SMOKE) - 1} are the smoke job's.\n")
    return head + "\n".join(lines(cfg)) + "\n"


if __name__ == "__main__":
    sys.stdout.write(render(json.loads((HERE / "config.json").read_text())))
