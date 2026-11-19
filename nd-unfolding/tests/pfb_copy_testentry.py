#!/usr/bin/env python3
"""The copy connect's test-only entry (K3): the production entry refuses any PFB_COPY_* switch, so tests build their
own Config here, rooted in a scratch directory: <root>/stage, <root>/rs1/runs/A0, <root>/pins.json, <root>/bin/sacct;
the deploy must sit under <root>. O_NOATIME is not required (the laptop has none). Never deployed or run on the cluster.

    python3 tests/pfb_copy_testentry.py <root> <deploy>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pfb_copy_remote as C  # noqa: E402


def config(root) -> "C.Config":
    root = Path(root)
    return C.Config(str(root / "stage"), str(root / "rs1" / "runs" / "A0"), json.loads((root / "pins.json").read_text()),
                    str(root / "bin" / "sacct"), str(root) + "/", False)


if __name__ == "__main__":
    sys.exit(C.copy(config(sys.argv[1]), sys.argv[2]))
