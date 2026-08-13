#!/usr/bin/env python3
"""Truncation probe for ROOT inputs: compare the header's own fEND against st_size.

WHY THIS EXISTS AND WHY IT IS NOT A SECOND COPY OF SESSION C's PROBE. C's ROOT 6.28
probe (`opendata-input-integrity-20260813.json`, OI-55) answered the input-integrity
question on 3 files of Playlist1A MC using `TFile::GetEND()` and a full basket scan.
Its own not-claimed list named the limit: 1A MC only. This instrument closes that gap
by being cheap enough to run on everything -- it reads 32 bytes per file and never
imports ROOT.

THE TWO READERS ARE THE POINT (BEN-196: a check's denominator must come from a
different instrument than its numerator). C's numerator is ROOT's own GetEND(); this
one parses the header per the file-format spec. Agreement between them on the three
shared files is evidence; agreement of a tool with itself would not be.

HOW TRUNCATION SHOWS UP. `xrdcp` interrupted mid-transfer leaves a PREFIX of the
original. A prefix still carries the original's header, and that header records the
logical end-of-file. So fEND describes a file larger than what is on disk, and
fEND > st_size is a direct, unambiguous truncation signature that costs one read.
It cannot be faked by a valid-but-older production, which is self-consistent.

WHAT IT DOES NOT CLAIM. fEND == size proves the file is STRUCTURALLY COMPLETE -- it
is not a checksum and says nothing about whether the bytes are the ones the remote
holds today. A file that is complete and a file that is current are different claims;
this tool makes only the first. Nor does it read remote headers.

Header layout: "root" magic at 0; fVersion int32be at 4; when fVersion >= 1000000 the
file uses the large-file (>2 GiB) layout and fEND is int64be at 12, else int32be at 12.

Usage:
    fend_probe.py --self-test          # 7 checks; run this before trusting output
    fend_probe.py <dir> [<dir> ...]    # walk for *.root, one verdict line per file
"""
from __future__ import annotations

import os
import struct
import sys
import tempfile

OK = "OK"
TRUNCATED = "TRUNCATED"
SHORT_FEND = "SHORT-fEND"
NOT_ROOT = "NOT-A-ROOT-FILE"


def probe(path):
    """Return (path, st_size, fEND or None, verdict)."""
    st = os.stat(path)
    with open(path, "rb") as fh:
        hdr = fh.read(32)
    if len(hdr) < 24 or hdr[:4] != b"root":
        return (path, st.st_size, None, NOT_ROOT)
    version = struct.unpack(">i", hdr[4:8])[0]
    if version >= 1000000:  # large-file layout: 64-bit offsets
        fend = struct.unpack(">q", hdr[12:20])[0]
    else:
        fend = struct.unpack(">i", hdr[12:16])[0]
    if fend == st.st_size:
        verdict = OK
    elif fend > st.st_size:
        verdict = TRUNCATED
    else:
        verdict = SHORT_FEND  # trailing bytes past the logical EOF
    return (path, st.st_size, fend, verdict)


def _synth(tmpdir, name, *, magic=b"root", version, fend, total_size):
    """Write a file whose header claims `fend` and whose real length is `total_size`."""
    path = os.path.join(tmpdir, name)
    hdr = bytearray(32)
    hdr[0:4] = magic
    hdr[4:8] = struct.pack(">i", version)
    hdr[8:12] = struct.pack(">i", 100)
    if version >= 1000000:
        hdr[12:20] = struct.pack(">q", fend)
    else:
        hdr[12:16] = struct.pack(">i", fend)
    body = bytes(max(0, total_size - 32))
    with open(path, "wb") as fh:
        fh.write(bytes(hdr) + body)
    return path


def self_test():
    """Prove the probe reports OK for complete files AND fires on broken ones.

    A probe that only ever returns OK is indistinguishable from a probe that works, on
    a healthy tree. Checks 3/4 are the ones that make an all-OK sweep mean something:
    they show the OK verdict is contingent on the bytes rather than on the code path.
    """
    checks = []

    def check(label, got, want):
        checks.append((label, got == want, f"got {got!r} want {want!r}"))

    with tempfile.TemporaryDirectory() as td:
        # 1-2: complete files in both header layouts report OK.
        p = _synth(td, "small_ok.root", version=61200, fend=4096, total_size=4096)
        check("small-file layout, fEND==size -> OK", probe(p)[3], OK)
        p = _synth(td, "large_ok.root", version=1061200, fend=8192, total_size=8192)
        check("large-file layout, fEND==size -> OK", probe(p)[3], OK)

        # 3-4: THE NEGATIVE CONTROLS. A prefix keeps the original's fEND.
        p = _synth(td, "trunc.root", version=1061200, fend=17_318_473_069, total_size=4096)
        check("large-file layout, fEND>size -> TRUNCATED", probe(p)[3], TRUNCATED)
        p = _synth(td, "trunc_small.root", version=61200, fend=999_999, total_size=4096)
        check("small-file layout, fEND>size -> TRUNCATED", probe(p)[3], TRUNCATED)

        # 5: trailing bytes past the logical EOF are not truncation and must not be
        # reported as OK either -- they are their own anomaly.
        p = _synth(td, "over.root", version=1061200, fend=2048, total_size=8192)
        check("fEND<size -> SHORT-fEND", probe(p)[3], SHORT_FEND)

        # 6: a non-ROOT file must not be silently counted as a passing ROOT file.
        p = _synth(td, "notroot.root", magic=b"junk", version=1061200, fend=4096, total_size=4096)
        check("bad magic -> NOT-A-ROOT-FILE", probe(p)[3], NOT_ROOT)

        # 7: the verdict must depend on the FILE, not on the filename or a cached
        # answer -- extend a complete file and the same path must change verdict.
        p = _synth(td, "flip.root", version=1061200, fend=8192, total_size=8192)
        before = probe(p)[3]
        with open(p, "ab") as fh:
            fh.write(b"\0" * 16)
        after = probe(p)[3]
        check("same path flips OK->SHORT-fEND when bytes change", (before, after), (OK, SHORT_FEND))

    npass = sum(1 for _, ok, _ in checks if ok)
    for label, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + ("" if ok else f"  -- {detail}"))
    print(f"SELF-TEST: {npass}/{len(checks)} passed")
    return 0 if npass == len(checks) else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    roots = [a for a in argv if not a.startswith("-")]
    if not roots:
        print(__doc__)
        return 2
    files = []
    for r in roots:
        if os.path.isfile(r):
            files.append(r)
            continue
        for dirpath, _dirnames, filenames in os.walk(r):
            files.extend(os.path.join(dirpath, fn) for fn in filenames if fn.endswith(".root"))
    files.sort()

    counts = {}
    bad = []
    for f in files:
        try:
            path, size, fend, verdict = probe(f)
        except OSError as exc:
            path, size, fend, verdict = f, -1, None, f"OSERROR:{type(exc).__name__}"
        counts[verdict] = counts.get(verdict, 0) + 1
        if verdict != OK:
            bad.append((path, size, fend, verdict))
        print(f"{verdict}\t{size}\t{fend}\t{path}", flush=True)

    print("=" * 70, flush=True)
    print(f"FILES EXAMINED: {len(files)}", flush=True)
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}", flush=True)
    print(f"NON-OK: {len(bad)}", flush=True)
    for path, size, fend, verdict in bad:
        print(f"  {verdict}  size={size} fEND={fend}  {path}", flush=True)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
