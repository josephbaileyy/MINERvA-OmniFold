"""The estimator stamp a PET covariance component carries in its own artifacts (KNOWN_ISSUES row 32).

A covariance is unclassifiable the moment the estimator moves unless the artifact names the estimator
it was computed under; the estimator has moved twice (full-event schema 2026-08-01, `niter`
2026-08-06), and before this the fact lived only in the launcher. So every component written by
`combine_cstat_bkgsub.py` and every assembly written by `assemble_ctotal_bkgsub.py` carries

    estimator_stamp = {"niter": int, "schema_id": str, "producer_commit": str}

in its summary JSON AND inside its npz (key `estimator_stamp`, a JSON string), because the npz is
what the next consumer actually loads. `producer_commit` is the commit that PRODUCED THE ESTIMATOR
(trained the replicas / nominal), which the combiner cannot see, so the caller supplies it; the
combiner's own checkout is recorded separately as `combined_by`.

Agreement rule for assembly: `niter` and `schema_id` define the estimator configuration and must be
identical across components. `producer_commit` is provenance and is recorded per component; blocks
of one budget are legitimately built by different jobs at different commits, so a difference is
disclosed in the summary, not refused.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import numpy as np

NPZ_KEY = "estimator_stamp"
CONFIG_FIELDS = ("niter", "schema_id")
_COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")


def make_stamp(niter, schema_id, producer_commit) -> dict:
    """Validated stamp; raises ValueError with the offending field named."""
    try:
        niter_i = int(niter)
    except (TypeError, ValueError):
        raise ValueError(f"estimator niter must be an integer, got {niter!r}") from None
    if niter_i < 1 or str(niter).strip() != str(niter_i):
        raise ValueError(f"estimator niter must be a positive integer, got {niter!r}")
    schema = str(schema_id or "").strip()
    if not schema or any(c.isspace() for c in schema):
        raise ValueError(f"schema_id must be a non-empty token without whitespace, got {schema_id!r}")
    commit = str(producer_commit or "").strip().lower()
    if not _COMMIT_RE.match(commit):
        raise ValueError(f"producer_commit must be a 7-40 character hex sha, got {producer_commit!r}")
    return {"niter": niter_i, "schema_id": schema, "producer_commit": commit}


def add_arguments(ap, required: bool = True) -> None:
    """The three CLI flags, identical in every producer."""
    ap.add_argument("--estimator-niter", required=required, type=int,
                    help="OmniFold iterations of the estimator the inputs were produced with")
    ap.add_argument("--schema-id", required=required,
                    help="input schema / feature-set identifier of that estimator")
    ap.add_argument("--producer-commit", required=required,
                    help="commit sha that produced the estimator (trained the inputs)")


def from_args(args) -> dict | None:
    """Stamp from parsed flags; None if none were given; ValueError if only some were."""
    given = [args.estimator_niter, args.schema_id, args.producer_commit]
    if all(v is None for v in given):
        return None
    if any(v is None for v in given):
        raise ValueError("--estimator-niter, --schema-id and --producer-commit go together; "
                         "a partial stamp is not a stamp")
    return make_stamp(*given)


def npz_value(stamp: dict) -> np.ndarray:
    return np.asarray(json.dumps(stamp, sort_keys=True))


def read_npz(z) -> dict | None:
    """The stamp stored in an open npz, re-validated; None if the artifact carries none."""
    if NPZ_KEY not in z.files:
        return None
    raw = json.loads(str(z[NPZ_KEY][()]))
    return make_stamp(raw.get("niter"), raw.get("schema_id"), raw.get("producer_commit"))


def config(stamp: dict) -> tuple:
    return tuple(stamp[f] for f in CONFIG_FIELDS)


def checkout_state(start) -> str:
    """`head=<sha> tree=<state> scope=.` of the checkout running the producer, via the repo helper."""
    here = Path(start).resolve()
    for d in (here.parent, *here.parents):
        helper = d / "lib" / "tree_state.py"
        if helper.is_file():
            spec = importlib.util.spec_from_file_location("tree_state", helper)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.format_state(module.describe(here.parent))
    return "head=unknown tree=unknown scope=? (lib/tree_state.py not found)"
