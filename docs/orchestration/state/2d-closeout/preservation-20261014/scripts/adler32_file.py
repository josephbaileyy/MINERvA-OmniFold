"""Compute a file's adler32 by reading every byte, without writing anything.

``xrdadler32 <path>`` is NOT used on inputs: it stores its result in the file's
``user.XrdCks.adler32`` extended attribute (changing the file's ctime) and answers
later queries from that cache without reading the data. This reader opens the
file read-only and reports the bytes it actually read, so a caller can check
that the whole file was read (bytes_read == st_size).

Usage: python3 -I adler32_file.py PATH
Prints: ``<8-hex adler32>\t<bytes_read>\t<st_size>\t<seconds>\t<PATH>``; exit 0
only if the read reached end of file and bytes_read == st_size.
"""
import os
import sys
import time
import zlib

CHUNK = 16 * 1024 * 1024


def main(path: str) -> int:
    t0 = time.monotonic()
    # O_NOATIME (we own the files) keeps the read from resetting the purge clock; fall back if refused.
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOATIME)
    except PermissionError:
        fd = os.open(path, os.O_RDONLY)
    try:
        size = os.fstat(fd).st_size
        value, nread = 1, 0
        while True:
            block = os.read(fd, CHUNK)
            if not block:
                break
            value = zlib.adler32(block, value)
            nread += len(block)
    finally:
        os.close(fd)
    dt = time.monotonic() - t0
    print(f"{value & 0xFFFFFFFF:08x}\t{nread}\t{size}\t{dt:.1f}\t{path}")
    return 0 if nread == size else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
