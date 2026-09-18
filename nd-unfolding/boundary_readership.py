#!/usr/bin/env python3
"""Measure, for every declared acceptance boundary, whether PRODUCTION CODE READS IT.

WHY THIS EXISTS. Four protections on the scalar-5D path turned out to be asserted-but-inert, each
found only by measurement: a keyword search that authorised every candidate; an adoption gate a
routing document satisfied; `variant` living in a docstring nothing read; and `--run-class` never
passed, so a refusal conditioned on it could never fire. Then two MORE boundaries were declared --
under a delegation, in good faith -- that nothing reads. Joseph's instruction was to stop finding
instances and close the class: *"every declared boundary carries `read by production: yes/no`,
measured, not asserted."*

THE DEFINITION, stated so it can be disagreed with rather than inferred:

    read_by_production(key) is TRUE iff some non-test module contains a VALUE READ of that
    boundary -- `boundary("k").value` or `Z_BOUNDARIES["k"].value` -- and that module is
    REACHABLE: it has a `__main__` guard, or a shell launcher names it.

A `boundary_key="k"` string inside a declaration is NOT a read. It records an intent to read. The
distinction is the whole point: `z_validator.Z_LEG_SET` names three boundaries and
`z_validator.assess` would read them, but `assess` has no caller outside `tests/` and
`z_validator.py` has no `__main__`, so no value is ever read at runtime.

⚠ THIS IS A REACHABILITY APPROXIMATION AND IT ERRS TOWARD `no`. It does not trace call graphs. A
value read inside a helper in an unreachable module reads `no` even if some future caller makes it
live. That direction is the safe one: it cannot report a boundary as binding when it is not.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ND = Path(__file__).resolve().parent
DECLARING_MODULE = "z_contract.py"


def _production_modules():
    for p in sorted(ND.glob("*.py")):
        if p.name in (DECLARING_MODULE, Path(__file__).name):
            continue
        yield p


def _strip_comments(src: str) -> str:
    return "\n".join(re.sub(r"#.*$", "", ln) for ln in src.splitlines())


def _reachable(path: Path, shell_text: str) -> bool:
    if "__main__" in path.read_text(encoding="utf-8", errors="ignore"):
        return True
    return path.name in shell_text


def measure(keys) -> dict:
    shell_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                           for p in ND.glob("*.sh"))
    mods = [(p, _strip_comments(p.read_text(encoding="utf-8", errors="ignore")))
            for p in _production_modules()]
    out = {}
    for k in keys:
        read_sites, named_sites = [], []
        for p, code in mods:
            if re.search(rf'boundary\(\s*["\']{re.escape(k)}["\']\s*\)\s*\.value', code) or \
               re.search(rf'Z_BOUNDARIES\[\s*["\']{re.escape(k)}["\']\s*\]\s*\.value', code):
                read_sites.append(p)
            elif f'"{k}"' in code or f"'{k}'" in code:
                named_sites.append(p)
        live = [p for p in read_sites if _reachable(p, shell_text)]
        out[k] = {
            "read_by_production": bool(live),
            "value_read_in": sorted(p.name for p in read_sites),
            "named_only_in": sorted(p.name for p in named_sites),
            "reachable_readers": sorted(p.name for p in live),
        }
    return out


def main() -> int:
    sys.path.insert(0, str(ND))
    import z_contract as zc
    res = measure(sorted(zc.Z_BOUNDARIES))
    width = max(len(k) for k in res)
    print(f"{'boundary'.ljust(width)}  read_by_production  where")
    for k, v in res.items():
        where = (", ".join(v["reachable_readers"]) if v["read_by_production"]
                 else ("named only in " + ", ".join(v["named_only_in"]) if v["named_only_in"]
                       else "NOT REFERENCED outside its own declaration"))
        print(f"{k.ljust(width)}  {'yes' if v['read_by_production'] else 'no ':<18}  {where}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
