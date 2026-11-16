import glob, os, types
B = "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023"
def tree(run):
    ds = glob.glob(f"{B}/{run}/periods_ns/tmp/tmp*"); assert len(ds) == 1, ds
    n = os.path.basename(ds[0]); out = {}
    for f in sorted(os.listdir(ds[0])):
        rel = f"periods_ns/tmp/{n}/{f}"; m = SCRATCH.match(rel)
        out[(m.group(1) + "<mkdtemp>" + m.group(3)) if m else rel] = hashlib.sha256(open(f"{ds[0]}/{f}", "rb").read()).hexdigest()
    return out, n
(s, s_tmp), (r, r_tmp) = tree("partc-r2"), tree("partc")
a = types.SimpleNamespace(partc_r2=f"{B}/partc-r2", c0=f"{B}/partc")
pp = [(b"/2d-closeout-re2-20261023/partc/", b"/2d-closeout-re2-20261023/partc-r2/"), (b"/deploy-e079ff05/", b"/deploy-903fb78b/")]
print("names", s_tmp, r_tmp, "same file set:", set(s) == set(r))
for rel in sorted(s):
    print(rel, "bitwise" if s[rel] == r.get(rel) else scratch(rel, a, pp, s, r, s_tmp, r_tmp))
