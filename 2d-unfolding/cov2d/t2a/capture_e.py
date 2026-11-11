#!/usr/bin/env python3
"""T2A's capture (fd/tier2-20261110/T2A-COV2D-SPLIT-DECLARATION.md §2, bound by T2-BINDING-1.md at M_T2 3bb2a96c).

COV2D's phase S computes the error matrix E (300 toys x 205 cells) at ``cov2d_readout.py:564`` (``cs.errors``) and writes
only ``score_<T>.json``. This wrapper reruns phase S unchanged and keeps a copy of E:

* ``sys.path[0]`` is set to the deploy's ``2d-unfolding/cov2d`` (what ``python cov2d_readout.py`` itself sees), and
  ``cov2d_readout`` is imported from there; its own top-level imports and path setup run as they do for the script.
* ``cov2d_score.errors`` is replaced by a pass-through that calls the original with the same arguments, keeps a copy of
  the E it returns, and returns the original's return value unchanged. Nothing else is patched.
* ``cov2d_readout.main(["score", "--truth", T, "--null-digest", D, "--out", OUT])`` runs, exactly the phase S argv.
* The binding check (control A0), before E is written: the regenerated ``score_<T>.json`` must equal the committed one
  (given with its sha256) field for field at full depth, with only ``utc`` and ``host`` excepted. On any difference the
  wrapper writes ``STOP_<T>.json`` and exits 8, and no E is written. The committed record's sha256 is checked before
  phase S runs; a mismatch is also exit 8.
* A4 (part): E must be one call's return, 300 finite rows of 205 in TOY_SEEDS order (the readout's order). Phase S
  returning non-zero, errors() called other than once, or a wrong-shaped E is ``FAILED_<T>.json`` and exit 9.
* On success: ``E_<T>.npz`` (E float64, seeds, truth, M) written atomically, and ``capture_<T>.json`` with the digests:
  this file's sha256, cov2d_readout.py's, the committed and regenerated score records', and E_<T>.npz's.

Nothing here reads a toy, a block or a null itself; every input is read by phase S's own guarded code.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path

EXCEPTED = ("utc", "host")
N_TOYS, N_CELLS = 300, 205


def sha256_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def leaves_differing(a, b, path="") -> list[str]:
    """Key paths where two JSON values differ at full depth (NaN equals NaN; int and float are not mixed up)."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            p = f"{path}.{k}" if path else k
            if k not in a or k not in b:
                out.append(p)
            else:
                out += leaves_differing(a[k], b[k], p)
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}[len {len(a)} != {len(b)}]"]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += leaves_differing(x, y, f"{path}[{i}]")
        return out
    if type(a) is not type(b):
        return [path]
    if isinstance(a, float) and math.isnan(a) and math.isnan(b):
        return []
    return [] if a == b else [path]


def compare(regen: dict, ref: dict) -> dict:
    fields = sorted((set(regen) | set(ref)) - set(EXCEPTED))
    diff = [f for f in fields if leaves_differing(regen.get(f, KeyError), ref.get(f, KeyError))]
    leaves = []
    for f in diff:
        if f not in regen or f not in ref:
            leaves.append(f)
        else:
            leaves += leaves_differing(regen[f], ref[f], f)
    return {"compared": len(fields), "excepted": list(EXCEPTED), "differing_fields": diff,
            "differing_leaves": leaves[:50], "n_differing_leaves": len(leaves), "equal": not diff}


def end(out: Path, name: str, rec: dict, rc: int) -> int:
    (out / name).write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print(f"T2A-CAPTURE {rec.get('truth')} {rec['status']} rc={rc}: {rec.get('why', '')}")
    return rc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cov2d-dir", required=True, type=Path, help="the deploy's 2d-unfolding/cov2d")
    ap.add_argument("--truth", required=True)
    ap.add_argument("--null-digest", required=True)
    ap.add_argument("--out", required=True, type=Path, help="phase S's --out; must be empty or absent")
    ap.add_argument("--ref-score", required=True, type=Path, help="the committed score_<T>.json")
    ap.add_argument("--ref-score-sha256", required=True)
    a = ap.parse_args(argv)
    T, out = a.truth, a.out
    if out.exists() and any(out.iterdir()):
        print(f"T2A-CAPTURE {T} REFUSED rc=8: {out} is not empty")
        return 8
    out.mkdir(parents=True, exist_ok=True)
    rec = {"truth": T, "wrapper_sha256": sha256_file(__file__), "null_digest": a.null_digest,
           "ref_score": str(a.ref_score), "ref_score_sha256_declared": a.ref_score_sha256}
    got = sha256_file(a.ref_score)
    rec["ref_score_sha256"] = got
    if got != a.ref_score_sha256:
        return end(out, f"STOP_{T}.json", dict(rec, status="STOP", why="the committed score record's sha256 differs"), 8)
    ref = json.loads(Path(a.ref_score).read_text())

    cov2d_dir = a.cov2d_dir.resolve()
    if not (cov2d_dir / "cov2d_readout.py").is_file() or not (cov2d_dir / "cov2d_score.py").is_file():
        return end(out, f"FAILED_{T}.json", dict(rec, status="FAILED", why="no cov2d_readout.py/cov2d_score.py there"), 9)
    rec["readout_sha256"] = sha256_file(cov2d_dir / "cov2d_readout.py")
    rec["score_module_sha256"] = sha256_file(cov2d_dir / "cov2d_score.py")
    sys.path[0] = str(cov2d_dir)          # as `python cov2d_readout.py` sees it (sys.path[0] is the script's directory)
    import cov2d_readout as ro            # noqa: E402  (its own path setup and imports run here, unchanged)
    cs = sys.modules["cov2d_score"]
    if getattr(ro, "cs", None) is not cs or not callable(getattr(cs, "errors", None)):
        return end(out, f"FAILED_{T}.json", dict(rec, status="FAILED", why="cov2d_readout does not call cov2d_score.errors"), 9)

    captured = []
    original = cs.errors

    def errors(*args, **kwargs):
        result = original(*args, **kwargs)
        captured.append(result[0].copy())
        return result

    cs.errors = errors
    try:
        rc = ro.main(["score", "--truth", T, "--null-digest", a.null_digest, "--out", str(out)])
    except Exception as e:                # phase S's own refusals return 2; anything else it raises is a failure here
        import traceback
        rec["traceback"] = traceback.format_exc()[-4000:]
        return end(out, f"FAILED_{T}.json", dict(rec, status="FAILED", why=f"phase S raised {type(e).__name__}: {e}"), 9)
    finally:
        cs.errors = original
    rec["phase_s_rc"] = rc
    import numpy as np                    # already imported by cov2d_readout; used only after phase S has finished

    if rc != 0:
        return end(out, f"FAILED_{T}.json", dict(rec, status="FAILED", why=f"phase S returned {rc}"), 9)
    if len(captured) != 1:
        return end(out, f"FAILED_{T}.json", dict(rec, status="FAILED", why=f"errors() was called {len(captured)} times"), 9)
    regen_path = out / f"score_{T}.json"
    rec["regen_score_sha256"] = sha256_file(regen_path)
    cmp_ = compare(json.loads(regen_path.read_text()), ref)
    rec["A0"] = cmp_
    if not cmp_["equal"]:
        return end(out, f"STOP_{T}.json", dict(rec, status="STOP", why="A0: the regenerated score differs from the committed one"), 8)
    E = np.asarray(captured[0], dtype=np.float64)
    seeds = np.asarray(list(ro.c.TOY_SEEDS[T]), dtype=np.int64)
    if E.shape != (N_TOYS, N_CELLS) or seeds.shape != (N_TOYS,) or not np.all(np.isfinite(E)):
        return end(out, f"FAILED_{T}.json", dict(rec, status="FAILED", why=f"E is {E.shape}, or not finite"), 9)
    e_path = out / f"E_{T}.npz"
    tmp = out / f"E_{T}.partial.npz"
    np.savez(tmp, E=E, seeds=seeds, truth=np.array(T), M=np.array(ref.get("M", "")))
    os.replace(tmp, e_path)
    rec.update(status="OK", why="A0 EQUAL; E written", M=ref.get("M"), e_shape=list(E.shape),
               e_npz_sha256=sha256_file(e_path), seeds_first_last=[int(seeds[0]), int(seeds[-1])])
    return end(out, f"capture_{T}.json", rec, 0)


if __name__ == "__main__":
    sys.exit(main())
