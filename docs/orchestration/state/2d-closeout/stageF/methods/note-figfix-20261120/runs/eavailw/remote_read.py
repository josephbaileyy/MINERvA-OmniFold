import base64, hashlib, json, os, socket, time
D = "/global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006/stage7/genfig/3d-unfolding/genie"
for n in ("genie_cv", "genie_mec", "nuwro_cv", "gibuu_cv"):
    p = f"{D}/{n}_xsec_eavailW.root"
    s0 = os.stat(p)
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    try:
        chunks = []
        while True:
            b = os.read(fd, 1 << 20)
            if not b:
                break
            chunks.append(b)
    finally:
        os.close(fd)
    data = b"".join(chunks)
    s1 = os.stat(p)
    print(json.dumps({"name": n, "path": p, "host": socket.gethostname(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                      "size": len(data), "st_size": s0.st_size, "sha256": hashlib.sha256(data).hexdigest(),
                      "atime_before_ns": s0.st_atime_ns, "atime_after_ns": s1.st_atime_ns, "mtime_ns": s0.st_mtime_ns,
                      "b64": base64.b64encode(data).decode()}))
