"""Test compare_rerun.py on a real bulk product (ll5d_ar23_toy_all_4761060.npz, a6c926f9…, fetched O_NOATIME).

The 20 names come from the bulk partition's node 09 lane 4 row. Every case builds both sides in a fresh temporary
directory, from the one real product's bytes (each name gets a byte-identical copy on the orig side), and runs the
comparator as a subprocess. Each mutant changes one file, on the rerun side only, and has a byte-identical control
that passes.
    python3 -I test_compare_rerun.py <compare_rerun.py> <real product .npz> <bulk-lanes.tsv>
"""
import io
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import numpy as np

CMP, REAL, LANES = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
row = [ln.split("\t") for ln in LANES.read_text().splitlines() if ln.startswith("09\t4\t")]
assert len(row) == 1, row
NAMES = [f"ll5d_ar23_toy_{it}.npz" for it in row[0][4].split(",")]
assert len(NAMES) == 20
RAW = REAL.read_bytes()
TARGET = NAMES[6]
fails = []


def rezip(raw: bytes, edit=None, date=None, drop=None) -> bytes:
    zin = zipfile.ZipFile(io.BytesIO(raw))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zout:
        for i in zin.infolist():
            if i.filename == drop:
                continue
            data = zin.read(i.filename)
            if edit:
                data = edit(i.filename, data)
            ni = zipfile.ZipInfo(i.filename, date_time=date or i.date_time)
            ni.compress_type, ni.external_attr, ni.create_system = i.compress_type, i.external_attr, i.create_system
            zout.writestr(ni, data)
    return buf.getvalue()


def meta_edit(change: dict):
    def f(name, data):
        if name != "meta.npy":
            return data
        m = json.loads(str(np.lib.format.read_array(io.BytesIO(data))[()]))
        for path, v in change.items():
            d = m
            for p in path[:-1]:
                d = d[p]
            d[path[-1]] = v
        b = io.BytesIO()
        np.lib.format.write_array(b, np.asarray(json.dumps(m, default=str)), allow_pickle=False)
        return b.getvalue()
    return f


def flip_xsec(name, data):
    if name != "xsec_flat.npy":
        return data
    hdr = len(data) - 65856 * 8
    b = bytearray(data)
    b[hdr + 8 * 1000 + 3] ^= 0x01
    return bytes(b)


def case(label, want_rc, want_rx, rerun_bytes=None, names=None, extra=None, missing=None):
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        (t / "o").mkdir(); (t / "r").mkdir()
        for n in NAMES:
            (t / "o" / n).write_bytes(RAW)
            if n != missing:
                (t / "r" / n).write_bytes(rerun_bytes if (rerun_bytes is not None and n == TARGET) else RAW)
        if extra:
            (t / "r" / extra).write_bytes(RAW)
        (t / "names.txt").write_text("\n".join(names or NAMES) + "\n")
        p = subprocess.run([sys.executable, "-I", str(CMP), str(t / "o"), str(t / "r"), str(t / "names.txt")],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    import re
    hit = all(re.search(rx, p.stdout, re.M) for rx in want_rx)
    good = p.returncode == want_rc and hit
    print(f"{'PASS' if good else 'FAIL'} {label} rc={p.returncode} (want {want_rc})")
    for ln in p.stdout.splitlines():
        if ln.startswith(("MISMATCH", "REPORT", "COMPARE-RERUN")) or (ln.startswith("ALLOW") and TARGET in ln):
            print("    " + ln[:220])
    if not good:
        fails.append(label)
        print("\n".join("    | " + x for x in p.stdout.splitlines()[-30:]))


case("control-byte-identical", 0, [r"^COMPARE-RERUN EQUAL \(20 names\)$", rf"^EQUAL {TARGET} file sha256 "])
allow = {("slurm_job",): "99999999", ("seconds_unfold",): 1.5, ("peak_rss_kib",): 1, ("refinement", "seconds"): 2.25}
case("allow-listed-keys-only", 0, [r"^COMPARE-RERUN EQUAL", rf"^ALLOW {TARGET} meta.npy slurm_job: orig '61214614' rerun '99999999'$",
                                   rf"^EQUAL {TARGET} xsec_flat.npy: dtype float64 shape \(65856,\) bytes equal$"],
     rerun_bytes=rezip(RAW, edit=meta_edit(allow)))
case("zip-metadata-only", 0, [r"^COMPARE-RERUN EQUAL", rf"^REPORT {TARGET}: zip metadata differs"],
     rerun_bytes=rezip(RAW, date=(2030, 1, 1, 0, 0, 0)))
case("rezip-identity-control", 0, [r"^COMPARE-RERUN EQUAL"], rerun_bytes=rezip(RAW))
case("mutant-xsec-byte", 1, [r"^COMPARE-RERUN MISMATCH", rf"^MISMATCH {TARGET} xsec_flat.npy: dtype float64/float64 shape \(65856,\)/\(65856,\); 1 data bytes differ$"],
     rerun_bytes=rezip(RAW, edit=flip_xsec))
case("mutant-meta-item", 1, [r"^COMPARE-RERUN MISMATCH", rf"^MISMATCH {TARGET} meta.npy key item: orig 'all_4761060' rerun 'all_4761066'$"],
     rerun_bytes=rezip(RAW, edit=meta_edit({("item",): "all_4761066"})))
case("mutant-meta-code_sha256", 1, [r"^COMPARE-RERUN MISMATCH", rf"^MISMATCH {TARGET} meta.npy key code_sha256/ll5d_b\.py: "],
     rerun_bytes=rezip(RAW, edit=meta_edit({("code_sha256", "ll5d_b.py"): "0" * 64})))
case("mutant-meta-estimator_params-not-allowed", 1, [rf"^MISMATCH {TARGET} meta.npy key estimator_params: "],
     rerun_bytes=rezip(RAW, edit=meta_edit({("estimator_params",): []})))
case("mutant-member-dropped", 1, [rf"^MISMATCH {TARGET} member set: only orig \['clip_tdw_fine.npy'\]"],
     rerun_bytes=rezip(RAW, drop="clip_tdw_fine.npy"))
case("missing-on-rerun-side", 1, [rf"^MISMATCH {NAMES[3]}: missing on the rerun side$"], missing=NAMES[3])
case("extra-on-rerun-side", 1, [r"^MISMATCH rerun dir holds products outside the 20: \['ll5d_ar23_toy_all_4761999.npz'\]$"],
     extra="ll5d_ar23_toy_all_4761999.npz")
case("names-count-19", 1, [r"^MISMATCH names file: 19 names"], names=NAMES[:19])
print("COMPARE-RERUN TEST", "PASS" if not fails else f"FAILED {fails}")
sys.exit(1 if fails else 0)
