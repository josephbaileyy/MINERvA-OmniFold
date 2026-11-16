"""cr_compare.py on the committed overlap_refined.json and edited copies: a rerun at another deploy with another argv
PASSes; a changed reading, a changed input digest, an atime_unchanged False, an extra key and a changed code_sha256
each STOP.   python3 test_cr_compare.py <committed overlap_refined.json>"""
import copy, json, os, subprocess, sys, tempfile
C = sys.argv[1]; H = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(C)); D0 = "/pscratch/sd/j/josephrb/gencmp-e-20261101/deploy"; D1 = "/pscratch/sd/j/josephrb/cov2d-cr-g2r-20261116/deploy"
def moved(d):
    d = copy.deepcopy(d)
    d["inputs"] = {(D1 + k[len(D0):] if k.startswith(D0 + "/") else k): v for k, v in d["inputs"].items()}
    d["argv"] = d["argv"][:-1] + ["/pscratch/sd/j/josephrb/cov2d-cr-g2r-20261116/control/overlap_refined.json"]
    return d
def first_number(d):
    for q, v in d["quadrants"].items() if isinstance(d["quadrants"], dict) else enumerate(d["quadrants"]):
        for k, x in (v.items() if isinstance(v, dict) else []):
            if isinstance(x, float): return q, k
cases = []
m = moved(base); cases.append(("moved deploy and argv", m, 0))
m = moved(base); q, k = first_number(m); m["quadrants"][q][k] *= 1 + 1e-12; cases.append((f"reading quadrants/{q}/{k} changed", m, 1))
m = moved(base); k0 = next(iter(m["inputs"])); m["inputs"][k0]["sha256"] = "0" * 64; cases.append(("an input digest changed", m, 1))
m = moved(base); m["inputs"][k0]["atime_unchanged"] = False; cases.append(("atime_unchanged False", m, 1))
m = moved(base); m["extra"] = 1; cases.append(("an extra key", m, 1))
m = moved(base); m["code_sha256"] = "1" * 64 if not isinstance(m["code_sha256"], dict) else {kk: "1" * 64 for kk in m["code_sha256"]}; cases.append(("code_sha256 changed", m, 1))
fail = 0
with tempfile.TemporaryDirectory() as T:
    for name, d, want in cases:
        p = os.path.join(T, "r.json"); json.dump(d, open(p, "w"))
        r = subprocess.run([sys.executable, os.path.join(H, "cr_compare.py"), "--rerun", p, "--committed", C, "--rerun-deploy", D1], capture_output=True, text=True)
        ok = r.returncode == want; fail += not ok
        print(("PASS" if ok else "FAIL"), name, "rc", r.returncode, "|", r.stdout.strip().splitlines()[-1])
print("CR-COMPARE TEST PASS" if not fail else "CR-COMPARE TEST FAILED"); sys.exit(1 if fail else 0)
