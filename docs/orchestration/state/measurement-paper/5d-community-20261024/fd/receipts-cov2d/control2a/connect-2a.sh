#!/bin/bash
# COV2D connect 2a: control (2a), the writer bitwise at the input (COV2D-DECLARATION.md §2), run as three processes
# under the director's ruling of 2026-11-03, a change to how the control is run, not to what it compares. No cluster
# env has PyROOT and uproot together, and the bound cov2d_writer.writer_control needs both. The ruling's conditions:
#   1. patch reach: `reach` lists by AST every reference to write_data_file in cov2d_writer, cov2d and control 1's
#      check (and any subprocess, functools, multiprocessing or `from cov2d_writer import`), and refuses anything but
#      the definition and writer_control's one direct call; the grep is logged too. In the run, the stub must be called
#      exactly once;
#   2. the digest chain: read's npz and manifest sha256 -> write logs them first and refuses others -> write's output
#      sha256 -> check logs it first, and its stub refuses any other file;
#   3. npz exactness: write checks each loaded array's dtype, shape and byte digest against read's manifest;
#   4. threads: every step runs under nice 19, taskset -c 8-11, with OMP/OPENBLAS/MKL/NUMEXPR threads at 1;
#   5. a fresh clone at M in /dev/shm, porcelain and the five bound blobs before and after, products removed after,
#      removals logged.
# The written file is kept, because the pilot's (2b) and §9.12 runs take `--data-file` set to control (2a)'s file. It
# is copied to $KEEP on pscratch, with its sha256 checked after the copy. Nothing is written to CFS. $CV, on CFS, is
# read only by the bound read_cv_data and control 1's open_noatime (O_NOATIME), and its atime is checked.
# A login node, 0 node-h, no job. Verdict: CONTROL-2A PASS (rc 0 and the bound "WRITER-CONTROL PASS failures=0"),
# CONTROL-2A FAIL (the bound control's own FAIL, rc 3), else CONTROL-2A INVALID.
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-2a.sh >/dev/null 2>&1 </dev/null &
M=c96c97f392f7402791e921ccdac952e74d454cee
W=/dev/shm/josephrb-cov2d-2a; DD=$W/deploy; KEEP=/pscratch/sd/j/josephrb/cov2d-2a
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
CONDA=/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda
ROOTENV=$HOME/.conda/envs/root_6_28
RUN="nice -n 19 taskset -c 8-11"
verdict() { echo "CONTROL-2A $1"; echo "end=$(date -u +%FT%TZ)"; echo DONE; exit "$2"; }
stop() { echo "STOP $*"; cleanup; verdict INVALID 2; }
cleanup() {
  echo "removal: host=$(hostname) $(date -u +%FT%TZ)"
  for p in "$W/cv_data.npz" "$W/cv_data.json" "$W/writer_control.root"; do
    [ -e "$p" ] && { s=$(sha256sum "$p" | cut -c1-64); rm -f "$p"; echo "rm $p sha256=$s rc=$?"; }
  done
  echo "rm -rf $DD ($(du -sh "$DD" 2>/dev/null | cut -f1))"; rm -rf "$DD"; echo "rc=$?"; ls -d "$DD" 2>&1
}
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
[ -e "$KEEP" ] && { echo "STOP $KEEP exists"; exit 2; }
mkdir "$W" "$W/tmp" || exit 2
exec >> "$W/connect-2a.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cat > "$W/control2a_split.py" <<'PYEOF'
"""COV2D control (2a), run as three processes (the director's ruling of 2026-11-03): a change to how the control is
run, not to what it compares. No cluster env has PyROOT and uproot together, and the bound
``cov2d_writer.writer_control`` needs both, so:

  reach  (any env)        : every reference to ``write_data_file`` in cov2d_writer and what it imports, by AST; refuses
                            anything but the definition and writer_control's one direct call.
  read   (omnifold_py310) : the bound ``read_cv_data($CV)`` (O_NOATIME) to an npz, with a digest per array.
  write  (root_6_28)      : checks the npz and manifest digests, then each loaded array's dtype, shape and bytes, then
                            calls the bound ``write_data_file``.
  check  (omnifold_py310) : the bound ``cov2d_writer.main(["control", ...])``, with the module global
                            ``write_data_file`` replaced by a stub that writes nothing and refuses any file but the
                            write step's, by sha256. The stub must be called exactly once.

Every step prints the previous step's digest before it does anything. Exit codes: 0 pass, 3 the control's own FAIL
(``cov2d_writer.main``), 4 a refusal here, 5 the stub was not called exactly once, 6 the file changed under the check.
MEASURES: control (2a). CANNOT AUTHORIZE: a toy.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

SOURCES = ("2d-unfolding/cov2d/cov2d_writer.py", "2d-unfolding/cov2d/cov2d.py",
           "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/control1/"
           "control1_content_check.py")


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def digest(a: np.ndarray) -> dict:
    return {"dtype": a.dtype.str, "shape": list(a.shape),
            "sha256": hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()}


def writer(deploy: str):
    sys.path.insert(0, str(Path(deploy) / "2d-unfolding/cov2d"))
    import cov2d_writer
    return cov2d_writer


def refuse(msg: str) -> int:
    print(f"REFUSE {msg}")
    return 4


def step_reach(a) -> int:
    bad = []
    for rel in SOURCES:
        src = (Path(a.deploy) / rel).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) and any(n.name.split(".")[0] in ("subprocess", "functools", "multiprocessing")
                                                    for n in node.names):
                bad.append(f"{rel}:{node.lineno} imports {[n.name for n in node.names]}")
            if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] in (
                    "cov2d_writer", "subprocess", "functools", "multiprocessing"):
                bad.append(f"{rel}:{node.lineno} from {node.module} import {[n.name for n in node.names]}")
        refs = []  # every way to name it: a bare name, an attribute, or a string (getattr, globals()[...])
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "write_data_file":
                refs.append((node.lineno, type(node.ctx).__name__))
            elif isinstance(node, ast.Attribute) and node.attr == "write_data_file":
                refs.append((node.lineno, "Attribute"))
            elif isinstance(node, ast.Constant) and node.value == "write_data_file":
                refs.append((node.lineno, "string"))
        refs = sorted(refs)
        defs = sorted({n.lineno for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "write_data_file"})
        print(f"reach {rel}: def at {defs}, references {refs}")
        if rel.endswith("cov2d_writer.py"):
            wc = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "writer_control"]
            calls = [n for n in ast.walk(wc[0]) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                     and n.func.id == "write_data_file"] if wc else []
            if len(defs) != 1 or len(calls) != 1 or refs != [(calls[0].lineno, "Load")]:
                bad.append(f"{rel}: expected one def and one direct Load call in writer_control, got defs {defs}, "
                           f"calls {[c.lineno for c in calls]}, references {refs}")
            else:
                print(f"reach {rel}: the one use is writer_control's direct call at line {calls[0].lineno}, a module "
                      f"global looked up at call time")
        elif defs or refs:
            bad.append(f"{rel}: unexpected def {defs} or references {refs}")
    for b in bad:
        print(f"REACH-BAD {b}")
    print(f"REACH {'FAIL' if bad else 'PASS'}")
    return 4 if bad else 0


def step_read(a) -> int:
    w = writer(a.deploy)
    cv = a.cv or w.CV
    print(f"read: cv={cv}")
    before = os.stat(cv).st_atime_ns
    cols, pot = w.read_cv_data(cv)
    after = os.stat(cv).st_atime_ns
    print(f"read: atime_ns before={before} after={after}")
    if after != before:
        return refuse("CV atime moved during read_cv_data")
    arrays = {**{b: cols[b] for b in w.BRANCHES}, "dataPOTUsed": np.asarray(pot, dtype=np.float64)}
    manifest = {k: digest(v) for k, v in arrays.items()}
    for k in sorted(manifest):
        print(f"read: {k} {manifest[k]}")
    np.savez(a.npz, **arrays)
    Path(a.manifest).write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    print(f"read: rows={arrays['measured'].size} dataPOTUsed={pot!r}")
    print(f"READ npz_sha256={sha256_file(a.npz)} manifest_sha256={sha256_file(a.manifest)}")
    return 0


def step_write(a) -> int:
    print(f"write: expects npz_sha256={a.npz_sha} manifest_sha256={a.manifest_sha}")
    got_npz, got_man = sha256_file(a.npz), sha256_file(a.manifest)
    print(f"write: loaded npz_sha256={got_npz} manifest_sha256={got_man}")
    if (got_npz, got_man) != (a.npz_sha, a.manifest_sha):
        return refuse("the npz or the manifest is not the read step's")
    manifest = json.loads(Path(a.manifest).read_text())
    with np.load(a.npz, allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files}
    w = writer(a.deploy)
    want = set(w.BRANCHES) | {"dataPOTUsed"}
    if set(arrays) != want or set(manifest) != want:
        return refuse(f"keys: npz {sorted(arrays)}, manifest {sorted(manifest)}, expected {sorted(want)}")
    for k in sorted(want):
        d = digest(arrays[k])
        print(f"write: {k} loaded {d}")
        if d != manifest[k]:
            return refuse(f"{k}: loaded {d} differs from the read step's {manifest[k]}")
    print("write: every array equals the read step's in dtype, shape and bytes")
    w.write_data_file(a.out, {b: arrays[b] for b in w.BRANCHES}, float(arrays["dataPOTUsed"]))
    print(f"WRITE out_sha256={sha256_file(a.out)}")
    return 0


def step_check(a) -> int:
    print(f"check: expects out_sha256={a.out_sha}")
    w = writer(a.deploy)
    calls = []

    def stub(path, cols, data_pot):
        calls.append(str(path))
        got = sha256_file(path) if Path(path).is_file() else None
        print(f"check: stub called with {path}, sha256={got}, rows={np.asarray(cols['measured']).size}, "
              f"dataPOTUsed={data_pot!r}")
        if Path(path) != Path(a.out) or got != a.out_sha:
            raise w.c.Refusal(f"the stub refuses {path} (sha256 {got}): not the write step's {a.out} {a.out_sha}")

    w.write_data_file = stub
    argv = ["control", "--out", a.out] + (["--cv", a.cv] if a.cv else [])
    try:
        rc = w.main(argv)
    except w.c.Refusal as e:
        print(f"REFUSE {e}")
        rc = 4
    if len(calls) != 1:
        print(f"check: FAIL, the stub was called {len(calls)} times, expected 1")
        rc = rc or 5
    after = sha256_file(a.out)
    if after != a.out_sha:
        print(f"check: FAIL, the file changed under the check: {after}")
        rc = rc or 6
    print(f"CHECK rc={rc} stub_calls={len(calls)}")
    return rc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", required=True)
    sub = ap.add_subparsers(dest="step", required=True)
    sub.add_parser("reach")
    p = sub.add_parser("read")
    p.add_argument("--cv")
    p.add_argument("--npz", required=True)
    p.add_argument("--manifest", required=True)
    p = sub.add_parser("write")
    for k in ("--npz", "--npz-sha", "--manifest", "--manifest-sha", "--out"):
        p.add_argument(k, required=True)
    p = sub.add_parser("check")
    p.add_argument("--cv")
    p.add_argument("--out", required=True)
    p.add_argument("--out-sha", required=True)
    a = ap.parse_args(argv)
    return {"reach": step_reach, "read": step_read, "write": step_write, "check": step_check}[a.step](a)


if __name__ == "__main__":
    sys.exit(main())
PYEOF
H=$W/control2a_split.py
echo "harness sha256=$(sha256sum "$H" | cut -c1-64)"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
blobs() {
  (cd "$DD" && git ls-tree HEAD 2d-unfolding/re2/re2_driver.py 2d-unfolding/cov2d/cov2d.py 2d-unfolding/cov2d/cov2d_receipt.py \
    2d-unfolding/cov2d/cov2d_writer.py nd-unfolding/fd_1b_null.py) > "$W/bound.blobs.$1"
  cat "$W/bound.blobs.$1"
  for b in 97f26a1d03be8cf14cdb6e0ce05e794f66f9b571 7dafdd3ff827378554931bd1b3d1f19aeeabe11d \
           d5718bf44c2084c20c30a8b8614e9c40e6fbeee3 2402ed4b656cfc9e0bfcaf32e1870672cfb9074d \
           1810161d53c6b849d0dce7fb506d88d551d89900; do
    grep -q " $b	" "$W/bound.blobs.$1" || stop "bound blob $b missing at M ($1)"
  done
  echo "bound blobs ($1): 5 of 5"
}
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "porcelain_before_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
blobs before
echo "== reach (grep, logged)"
(cd "$DD" && grep -n "subprocess\|functools\|partial\|multiprocessing\|from cov2d_writer import\|write_data_file" \
  2d-unfolding/cov2d/cov2d_writer.py 2d-unfolding/cov2d/cov2d.py \
  docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/control1/control1_content_check.py)
echo "== reach (AST)"
$RUN "$PY310" -B "$H" --deploy "$DD" reach || stop "reach"
echo "== step 1: read (omnifold_py310)"
"$PY310" -c "import sys, numpy, uproot; print(sys.version.split()[0], 'numpy', numpy.__version__, 'uproot', uproot.__version__)" || stop "py310 import"
$RUN "$PY310" -B "$H" --deploy "$DD" read --npz "$W/cv_data.npz" --manifest "$W/cv_data.json" > "$W/step1.log" 2>&1; rc=$?
cat "$W/step1.log"; [ "$rc" = 0 ] || stop "read rc=$rc"
NPZ_SHA=$(sed -n 's/^READ npz_sha256=\([0-9a-f]\{64\}\) .*/\1/p' "$W/step1.log")
MAN_SHA=$(sed -n 's/.* manifest_sha256=\([0-9a-f]\{64\}\)$/\1/p' "$W/step1.log")
[ ${#NPZ_SHA} = 64 ] && [ ${#MAN_SHA} = 64 ] || stop "read did not report its digests"
echo "chain: npz_sha256=$NPZ_SHA manifest_sha256=$MAN_SHA"
echo "== step 2: write (root_6_28)"
(
  eval "$("$CONDA" shell.bash hook)" && conda activate "$ROOTENV" || exit 3
  python -c "import sys, numpy, ROOT; print(sys.version.split()[0], 'numpy', numpy.__version__, 'ROOT', ROOT.gROOT.GetVersion())" || exit 4
  $RUN python -B "$H" --deploy "$DD" write --npz "$W/cv_data.npz" --npz-sha "$NPZ_SHA" --manifest "$W/cv_data.json" \
    --manifest-sha "$MAN_SHA" --out "$W/writer_control.root"
) > "$W/step2.log" 2>&1; rc=$?
cat "$W/step2.log"; [ "$rc" = 0 ] || stop "write rc=$rc"
OUT_SHA=$(sed -n 's/^WRITE out_sha256=\([0-9a-f]\{64\}\)$/\1/p' "$W/step2.log")
[ ${#OUT_SHA} = 64 ] && [ "$(sha256sum "$W/writer_control.root" | cut -c1-64)" = "$OUT_SHA" ] || stop "write's digest"
echo "chain: out_sha256=$OUT_SHA"
echo "== step 3: check (omnifold_py310)"
$RUN "$PY310" -B "$H" --deploy "$DD" check --out "$W/writer_control.root" --out-sha "$OUT_SHA" > "$W/step3.log" 2>&1; rc=$?
cat "$W/step3.log"
n=$(git -C "$DD" status --porcelain | wc -l); echo "porcelain_after_lines=$n head=$(git -C "$DD" rev-parse HEAD)"
git -C "$DD" status --porcelain | head -20
[ "$n" = "0" ] || stop "porcelain after: $n lines"
blobs after
if [ "$rc" = 0 ] && grep -qx "WRITER-CONTROL PASS failures=0" "$W/step3.log" && grep -qx "CHECK rc=0 stub_calls=1" "$W/step3.log"; then
  V=PASS; X=0
elif [ "$rc" = 3 ] && grep -q "^WRITER-CONTROL FAIL" "$W/step3.log"; then
  V=FAIL; X=3
else
  V=INVALID; X=2
fi
if [ "$V" = PASS ]; then
  mkdir "$KEEP" && cp "$W/writer_control.root" "$KEEP/writer_control.root"; k=$(sha256sum "$KEEP/writer_control.root" | cut -c1-64)
  echo "kept: $KEEP/writer_control.root sha256=$k"
  [ "$k" = "$OUT_SHA" ] || { echo "the kept copy differs"; V=INVALID; X=2; }
fi
cleanup
verdict "$V" "$X"
