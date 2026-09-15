"""Re-derive the pinned upstream cap/aggregation semantics from upstream's own bytes.

The overflow specification's claims about Gregor's cap behaviour must be
measurable, not paraphrased, so this script executes the upstream function
itself rather than a local restatement of it. Upstream code is deliberately not
vendored into this repository: the operator supplies the file and its SHA-256 is
checked against the digest already bound in ``external-source-check.json`` before
a single line of it is executed.

Fetch the input with, at the pin recorded in that file::

    curl -o preprocessing.py \\
      https://raw.githubusercontent.com/gregorkrz/minerva-ml/<pin>/src/dataset/preprocessing.py

This is a semantics probe over synthetic arrays. It reads no detector source,
trains nothing, and establishes no representation winner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import types
from typing import Any

import numpy as np

UPSTREAM_FILE = "src/dataset/preprocessing.py"
FUNCTION = "aggregate_low_energy_blobs_from_four_momentum"
AUXILIARY_WIDTH = 5


def _bound_digest(check: Path) -> str:
    """Return the digest this repository already bound for the upstream file."""
    record = json.loads(check.read_text())
    return str(record["files"][UPSTREAM_FILE]["sha256"])


def load_upstream_function(source: Path, expected_sha256: str) -> Any:
    """Verify the supplied bytes, then execute only the aggregation function.

    Parameters
    ----------
    source : Path
        Operator-supplied copy of the upstream preprocessing module.
    expected_sha256 : str
        Digest bound in this repository for that path at the recorded pin.

    Returns
    -------
    Any
        The upstream aggregation callable.

    Raises
    ------
    ValueError
        If the bytes do not match the bound digest, or the function is absent.
    """
    payload = source.read_bytes()
    measured = hashlib.sha256(payload).hexdigest()
    if measured != expected_sha256:
        raise ValueError(
            f"Upstream digest mismatch: measured {measured}, bound {expected_sha256}"
        )
    text = payload.decode()
    match = re.search(rf"def {FUNCTION}\(.*?\n(?=def )", text, re.S)
    if match is None:
        raise ValueError(f"Upstream function {FUNCTION} not found")
    module = types.ModuleType("upstream_overflow")
    module.np = np  # type: ignore[attr-defined]
    exec(match.group(0), module.__dict__)  # noqa: S102 - digest-verified upstream
    return getattr(module, FUNCTION)


def _case(aggregate: Any, n_objects: int, n_keep: int) -> dict[str, Any]:
    """Run one synthetic multiplicity through the upstream aggregation."""
    four_momentum = np.zeros((n_objects, 4), dtype=np.float32)
    # A strictly descending energy column makes the ordering unambiguous.
    four_momentum[:, 3] = np.arange(n_objects, 0, -1)
    pid = np.full(n_objects, 2, dtype=np.int32)
    auxiliary = np.arange(n_objects * AUXILIARY_WIDTH, dtype=np.float32).reshape(
        n_objects, AUXILIARY_WIDTH
    )
    out_momentum, out_pid, out_auxiliary = aggregate(
        four_momentum, pid, auxiliary, n_keep=n_keep, aggregate_pid=6
    )
    binds = n_objects > n_keep
    expected_tail_mean = (
        auxiliary[n_keep - 1 :].mean(axis=0) if binds else np.zeros(AUXILIARY_WIDTH)
    )
    return {
        "n_objects": n_objects,
        "n_keep": n_keep,
        "cap_binds": binds,
        "output_tokens": int(len(out_momentum)),
        "docstring_predicted_tokens": min(n_keep + 1, n_objects),
        "energy_in": float(four_momentum[:, 3].sum()),
        "energy_out": float(out_momentum[:, 3].sum()),
        "aggregate_pid_present": bool(6 in set(out_pid.tolist())),
        "auxiliary_aggregate_is_tail_mean": bool(
            binds and np.allclose(out_auxiliary[-1], expected_tail_mean)
        ),
    }


def measure(aggregate: Any) -> dict[str, Any]:
    """Measure the four properties the overflow specification depends on."""
    cases = [
        _case(aggregate, n_objects, n_keep)
        for n_objects, n_keep in (
            (5, 20),
            (19, 20),
            (20, 20),
            (21, 20),
            (30, 20),
            (90, 20),
            (21, 5),
        )
    ]
    binding = [case for case in cases if case["cap_binds"]]
    inert = [case for case in cases if not case["cap_binds"]]
    properties = {
        # 1. When the cap binds the code returns exactly n_keep, not n_keep + 1.
        "binding_output_equals_n_keep": all(
            case["output_tokens"] == case["n_keep"] for case in binding
        ),
        "docstring_is_off_by_one_when_binding": all(
            case["docstring_predicted_tokens"] == case["output_tokens"] + 1
            for case in binding
        ),
        # 2. Aggregation conserves total energy; truncation would not.
        "total_energy_conserved": all(
            np.isclose(case["energy_in"], case["energy_out"]) for case in cases
        ),
        # 3. The merged auxiliary block is a mean over the tail, not a sum.
        "auxiliary_aggregate_is_tail_mean": all(
            case["auxiliary_aggregate_is_tail_mean"] for case in binding
        ),
        # 4. Multiplicity leaves no explicit trace: distinct inputs, one width.
        "multiplicity_collapses_to_one_width": len(
            {case["output_tokens"] for case in binding if case["n_keep"] == 20}
        )
        == 1,
        # Inert control: below the cap the transform must change nothing.
        "inert_below_cap": all(
            case["output_tokens"] == case["n_objects"]
            and not case["aggregate_pid_present"]
            for case in inert
        ),
    }
    return {
        "scope": "synthetic semantics probe of pinned upstream code; not a learning result",
        "upstream_file": UPSTREAM_FILE,
        "function": FUNCTION,
        "cases": cases,
        "properties": properties,
        "verdict": (
            "UPSTREAM-SEMANTICS-AS-SPECIFIED"
            if all(properties.values())
            else "UPSTREAM-SEMANTICS-DIVERGED"
        ),
    }


def main() -> None:
    """Verify the upstream digest, measure its semantics, and write a receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--upstream",
        type=Path,
        required=True,
        help="Operator-supplied copy of the pinned upstream preprocessing module",
    )
    parser.add_argument(
        "--external-source-check",
        type=Path,
        default=Path(__file__).with_name("external-source-check.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record = json.loads(args.external_source_check.read_text())
    aggregate = load_upstream_function(
        args.upstream, _bound_digest(args.external_source_check)
    )
    result = measure(aggregate)
    result["pin"] = record["pin"]
    result["upstream_sha256"] = record["files"][UPSTREAM_FILE]["sha256"]
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(result["verdict"])
    if result["verdict"] != "UPSTREAM-SEMANTICS-AS-SPECIFIED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
