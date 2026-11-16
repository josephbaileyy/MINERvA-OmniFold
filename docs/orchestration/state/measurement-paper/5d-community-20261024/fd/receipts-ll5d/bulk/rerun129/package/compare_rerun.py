"""Compare the rc-129 rerun's 20 products with the bulk's 20 (the director's rule (d), 2026-11-14).

    python3 -I compare_rerun.py <orig dir> <rerun dir> <names file: one product file name per line>

Read-only: every file is opened read-only, with O_NOATIME where the platform has it; nothing is written anywhere.
The rule:
- Files pair by name. A missing or extra file on either side, or a count other than the names file's (which must be
  20), is a MISMATCH.
- Each pair's zip member sets must be equal; otherwise a MISMATCH.
- Each numeric (.npy, non-meta) member: equal name, dtype, shape and bytes, else a MISMATCH.
- `meta.npy`: parsed as JSON (np.savez_compressed stores `json.dumps(meta)` as a 0-d str array; s5n_pseudo.py
  write_product at 4231b14d), equal on every key except ALLOW, whose values are printed for both sides.
- A non-.npy member: equal bytes, else a MISMATCH.
- Equal file sha256 is sufficient. A difference only in zip metadata (dates, attributes, compression) is REPORTED and
  is not a mismatch.
ALLOW is fixed before the rerun and is never widened after the results are seen. Each key is per-run, from code at
4231b14d:
- slurm_job: ll5d_b.py:320, os.environ.get("SLURM_JOB_ID").
- seconds_unfold: ll5d_b.py:313 and :320, wall time of the item.
- peak_rss_kib: ll5d_b.py:321, getrusage ru_maxrss.
- refinement/seconds: s5n_pseudo.py:268, :282 and :304, the refinement's wall time. The toy role's ev comes from
  fd_1b_mc.py:411-413 → s5n_pseudo.unfold_negweight (:311-331).
estimator_params is NOT allow-listed: it is the classifier's get_params() record (s5c_unfold.py:119-146 via
s5n_pseudo.py:330), all fixed hyperparameters, with num_threads = --threads = 32 on both sides. The rest of
`refinement` (counts, sums, g range, classifier_params) is computed from the data and is NOT allow-listed either.
Every verdict line names the file and the member. Exit 0 only for EQUAL.
"""
import hashlib
import io
import json
import os
import sys
import zipfile

import numpy as np

ALLOW = (("slurm_job",), ("seconds_unfold",), ("peak_rss_kib",), ("refinement", "seconds"))   # key paths (tuples)
WANT_N = 20


def read(path: str) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOATIME", 0)
    fd = os.open(path, flags)
    try:
        chunks = []
        while True:
            c = os.read(fd, 1 << 22)
            if not c:
                break
            chunks.append(c)
        return b"".join(chunks)
    finally:
        os.close(fd)


def flat(d, p=()):
    """Nested dicts to {key path tuple: leaf}; tuples, because keys such as "ll5d_b.py" contain dots."""
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flat(v, p + (k,)))
    else:
        out[p] = d
    return out


def ks(path) -> str:
    return "/".join(path)


def members(raw: bytes):
    z = zipfile.ZipFile(io.BytesIO(raw))
    info = {i.filename: (i.date_time, i.compress_type, i.external_attr, i.create_system, i.flag_bits) for i in z.infolist()}
    return {n: z.read(n) for n in z.namelist()}, info


def npy(b: bytes) -> np.ndarray:
    return np.lib.format.read_array(io.BytesIO(b), allow_pickle=False)


def compare_pair(name: str, a_raw: bytes, b_raw: bytes, out: list) -> bool:
    ha, hb = hashlib.sha256(a_raw).hexdigest(), hashlib.sha256(b_raw).hexdigest()
    if ha == hb:
        out.append(f"EQUAL {name} file sha256 {ha} (both sides)")
        return True
    out.append(f"INFO {name} file sha256 orig {ha} rerun {hb}: comparing by member")
    ma, ia = members(a_raw)
    mb, ib = members(b_raw)
    ok = True
    if set(ma) != set(mb):
        out.append(f"MISMATCH {name} member set: only orig {sorted(set(ma) - set(mb))} only rerun {sorted(set(mb) - set(ma))}")
        return False
    for m in sorted(ma):
        if m == "meta.npy":
            try:
                ja = flat(json.loads(str(npy(ma[m])[()])))
                jb = flat(json.loads(str(npy(mb[m])[()])))
            except Exception as exc:
                out.append(f"MISMATCH {name} {m}: not parseable as JSON ({exc})")
                ok = False
                continue
            keys = sorted(set(ja) | set(jb))
            bad = [k for k in keys if k not in ALLOW and (k not in ja or k not in jb or ja[k] != jb[k])]
            for k in bad:
                out.append(f"MISMATCH {name} {m} key {ks(k)}: orig {ja.get(k, '<absent>')!r} rerun {jb.get(k, '<absent>')!r}")
            missing_allow = [k for k in ALLOW if k not in ja or k not in jb]
            for k in missing_allow:
                out.append(f"MISMATCH {name} {m} allow-listed key {ks(k)} absent on a side")
            for k in ALLOW:
                out.append(f"ALLOW {name} {m} {ks(k)}: orig {ja.get(k)!r} rerun {jb.get(k)!r}")
            if bad or missing_allow:
                ok = False
            else:
                out.append(f"EQUAL {name} {m}: {len(keys) - len(ALLOW)} keys equal outside the allow-list")
        elif m.endswith(".npy"):
            xa, xb = npy(ma[m]), npy(mb[m])
            same = xa.dtype == xb.dtype and xa.shape == xb.shape and xa.tobytes() == xb.tobytes()
            if same:
                out.append(f"EQUAL {name} {m}: dtype {xa.dtype} shape {xa.shape} bytes equal")
            else:
                diff = ""
                if xa.dtype == xb.dtype and xa.shape == xb.shape:
                    ba, bb = np.frombuffer(xa.tobytes(), np.uint8), np.frombuffer(xb.tobytes(), np.uint8)
                    diff = f"; {int(np.count_nonzero(ba != bb))} data bytes differ"
                out.append(f"MISMATCH {name} {m}: dtype {xa.dtype}/{xb.dtype} shape {xa.shape}/{xb.shape}{diff}")
                ok = False
        else:
            if ma[m] == mb[m]:
                out.append(f"EQUAL {name} {m}: bytes equal")
            else:
                out.append(f"MISMATCH {name} {m}: bytes differ")
                ok = False
    if ok and ia != ib:
        out.append(f"REPORT {name}: zip metadata differs (not a mismatch): orig {ia} rerun {ib}")
    return ok


def main(argv) -> int:
    orig, rerun, names_file = argv[1], argv[2], argv[3]
    names = [ln.strip() for ln in open(names_file) if ln.strip()]
    out = [f"compare_rerun allow-list {[ks(k) for k in ALLOW]}; names {len(names)} (want {WANT_N})"]
    ok = len(names) == WANT_N and len(set(names)) == len(names)
    if not ok:
        out.append(f"MISMATCH names file: {len(names)} names, {len(set(names))} distinct, want {WANT_N}")
    want = set(names)
    have_o = {f for f in os.listdir(orig) if f.endswith(".npz")} & want if os.path.isdir(orig) else set()
    rerun_all = {f for f in os.listdir(rerun) if f.endswith(".npz")} if os.path.isdir(rerun) else set()
    extra = sorted(rerun_all - want)
    if extra:
        out.append(f"MISMATCH rerun dir holds products outside the 20: {extra}")
        ok = False
    for n in names:
        po, pr = os.path.join(orig, n), os.path.join(rerun, n)
        if n not in have_o or not os.path.isfile(po):
            out.append(f"MISMATCH {n}: missing on the orig side")
            ok = False
            continue
        if not os.path.isfile(pr):
            out.append(f"MISMATCH {n}: missing on the rerun side")
            ok = False
            continue
        ok = compare_pair(n, read(po), read(pr), out) and ok
    out.append(f"COMPARE-RERUN {'EQUAL' if ok else 'MISMATCH'} ({len(names)} names)")
    print("\n".join(out))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
