"""xk_copy.py and xk_compare.py on synthetic inputs and the committed k.json.
xk_copy: the exact K set is copied to every destination and equals the committed list; a digest mismatch, a file the
list lacks, and an existing destination each refuse (rc 2); files outside the K set are not copied.
xk_compare: the committed k.json against itself PASSes with identical bytes; re-serialized it PASSes with differing bytes;
a changed reading, a changed route, a dropped input and an extra key each STOP.
    python3 test_xk_tools.py <committed k.json>"""
import copy, hashlib, json, os, subprocess, sys, tempfile
K = sys.argv[1]; H = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
fails = 0
def ok(name, cond):
    global fails
    fails += not cond; print(("PASS" if cond else "FAIL"), name)
def run(*args):
    r = subprocess.run([PY, *args], capture_output=True, text=True); return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1]
with tempfile.TemporaryDirectory() as T:
    src = os.path.join(T, "gencmp-x-20261102"); files = {
        "v0-a1/v0.json": b'{"pass": true}', "v0-a1/maps.npz": b"maps", "v1-a2/v1.json": b'{"bands_pass": {}}',
        "boot/native/lane_1_1.json": b"{}", "boot/native/native_b1_j101.npz": b"nat", "boot/xcov/lane_1_13.json": b"{}",
        "boot/xcov/xcov_b1_j101.npz": b"x1", "inputs/of_inputs_5d.npz": b"npz", "inputs/bkg_dump.npz": b"bkg", "k/k.json": b"{}"}
    for r, b in files.items():
        os.makedirs(os.path.dirname(os.path.join(src, r)), exist_ok=True); open(os.path.join(src, r), "wb").write(b)
    def hlist(path, drop=None, corrupt=None):
        with open(path, "w") as f:
            for r, b in files.items():
                if r == drop: continue
                d = hashlib.sha256(b if r != corrupt else b"other").hexdigest()
                f.write(f"{d}  {len(b):>10}  gencmp-x-20261102/{r}\n")
    L = os.path.join(T, "files.sha256"); hlist(L)
    d1, d2 = os.path.join(T, "d1"), os.path.join(T, "d2")
    rc, last = run(os.path.join(H, "xk_copy.py"), "--source", src, "--hpss-list", L, "--dest", d1, "--dest", d2)
    copied = sorted(os.path.relpath(os.path.join(r, f), d1) for r, _, fs in os.walk(d1) for f in fs)
    ok(f"copy: rc 0 and exactly the K set ({last})", rc == 0 and copied == sorted(["v0-a1/v0.json", "v1-a2/v1.json",
       "boot/native/lane_1_1.json", "boot/xcov/lane_1_13.json", "boot/xcov/xcov_b1_j101.npz", "inputs/of_inputs_5d.npz"])
       and all(open(os.path.join(d2, c), "rb").read() == files[c] for c in copied))
    rc, last = run(os.path.join(H, "xk_copy.py"), "--source", src, "--hpss-list", L, "--dest", d1)
    ok(f"copy: an existing destination refuses ({last})", rc == 2 and "exists" in last)
    L2 = os.path.join(T, "bad.sha256"); hlist(L2, corrupt="boot/xcov/xcov_b1_j101.npz")
    rc, last = run(os.path.join(H, "xk_copy.py"), "--source", src, "--hpss-list", L2, "--dest", os.path.join(T, "d3"))
    ok(f"copy: a digest mismatch refuses ({last})", rc == 2 and "!= committed" in last)
    L3 = os.path.join(T, "short.sha256"); hlist(L3, drop="v1-a2/v1.json")
    rc, last = run(os.path.join(H, "xk_copy.py"), "--source", src, "--hpss-list", L3, "--dest", os.path.join(T, "d4"))
    ok(f"copy: a K file absent from the list refuses ({last})", rc == 2 and "not in the committed list" in last)
    base = json.load(open(K)); P = os.path.join(T, "r.json")
    def cmp(obj=None, raw=None):
        open(P, "wb").write(raw if raw is not None else json.dumps(obj).encode()); return run(os.path.join(H, "xk_compare.py"), "--rerun", P, "--committed", K)
    rc, last = cmp(raw=open(K, "rb").read()); ok(f"compare: itself, identical bytes ({last})", rc == 0 and "identical" in last)
    rc, last = cmp(base); ok(f"compare: re-serialized, bytes differ, PASS ({last})", rc == 0 and "differ" in last)
    m = copy.deepcopy(base); m["d"][0] = m["d"][0] * (1 + 1e-15) if m["d"][0] * (1 + 1e-15) != m["d"][0] else m["d"][0] * (1 + 1e-12)
    rc, last = cmp(m); ok(f"compare: a reading changed STOPs ({last})", rc == 1)
    m = copy.deepcopy(base); m["route"] = "B"; rc, last = cmp(m); ok(f"compare: route changed STOPs ({last})", rc == 1)
    m = copy.deepcopy(base); m["inputs"].pop(next(iter(m["inputs"]))); rc, last = cmp(m); ok(f"compare: a dropped input STOPs ({last})", rc == 1)
    m = copy.deepcopy(base); m["products"] = "re2"; rc, last = cmp(m); ok(f"compare: an extra key STOPs ({last})", rc == 1)
print("XK TOOLS TEST PASS" if not fails else "XK TOOLS TEST FAILED"); sys.exit(1 if fails else 0)
