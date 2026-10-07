"""Diff two port-check receipts field by field, so "unchanged" is reproducible.

The optimisation pass claims not to have changed his network. `test_port.py`
proves that bitwise on a unit fixture; this proves it on the full P-1..P-6 run
against the upstream torch model, which is the measurement that matters. The
claim it supports is not "both passed" -- two runs can both pass and disagree --
but "every numeric field is identical".

Prints the count of identical and changed fields and exits non-zero if any
numeric field moved, so it can be used as a gate and not only as a report.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


def numeric_fields(node: Any, prefix: str = "") -> dict[str, float]:
    """Every numeric leaf, by dotted path. Booleans are not numbers here."""
    found: dict[str, float] = {}
    if isinstance(node, dict):
        for key, value in node.items():
            found.update(numeric_fields(value, f"{prefix}{key}."))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found.update(numeric_fields(value, f"{prefix}{index}."))
    elif isinstance(node, (int, float)) and not isinstance(node, bool):
        found[prefix.rstrip(".")] = node
    return found


def boolean_fields(node: Any, prefix: str = "") -> dict[str, bool]:
    """Every boolean leaf, by dotted path.

    Kept separate from the numeric walk rather than folded into it: `True` would
    otherwise compare equal to `1`, and a verdict flipping from `held: True` to
    `held: 1` is not the same event as a deviation moving. Both are reported, so
    the comparator is a complete gate and not only a numeric one.
    """
    found: dict[str, bool] = {}
    if isinstance(node, dict):
        for key, value in node.items():
            found.update(boolean_fields(value, f"{prefix}{key}."))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found.update(boolean_fields(value, f"{prefix}{index}."))
    elif isinstance(node, bool):
        found[prefix.rstrip(".")] = node
    return found


def _moved(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return {
        key: {"before": left.get(key), "after": right.get(key)}
        for key in sorted(set(left) | set(right))
        if left.get(key) != right.get(key)
    }


def compare(before: dict[str, Any], after: dict[str, Any],
            section: str = "checks") -> dict[str, Any]:
    left = numeric_fields(before.get(section, {}))
    right = numeric_fields(after.get(section, {}))
    left_flags = boolean_fields(before.get(section, {}))
    right_flags = boolean_fields(after.get(section, {}))
    changed = _moved(left, right)
    changed_flags = _moved(left_flags, right_flags)
    return {
        "section": section,
        "fields_before": len(left),
        "fields_after": len(right),
        "identical": len(set(left) & set(right)) - len(changed),
        "changed": changed,
        "boolean_fields": len(left_flags),
        "changed_booleans": changed_flags,
        "unchanged": not changed and not changed_flags,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--section", default="checks")
    args = parser.parse_args()
    result = compare(json.loads(args.before.read_text()),
                     json.loads(args.after.read_text()), args.section)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["unchanged"] else 1)


if __name__ == "__main__":
    main()
