import os
import sys

fd = os.open(sys.argv[1], os.O_RDONLY | os.O_NOATIME)
out = sys.stdout.buffer
while True:
    b = os.read(fd, 1 << 20)
    if not b:
        break
    out.write(b)
out.flush()
os.close(fd)
