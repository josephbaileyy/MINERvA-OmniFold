import importlib.util, sys, sysconfig, os
D = os.path.realpath(sys.argv[1])
before = set(sys.modules)
p = os.path.join(D, "nd-unfolding", "s1_assemble.py")
spec = importlib.util.spec_from_file_location("s1_assemble", p)
m = importlib.util.module_from_spec(spec); sys.modules["s1_assemble"] = m; spec.loader.exec_module(m)
std = {os.path.realpath(sysconfig.get_paths()[k]) for k in ("stdlib", "platstdlib")}
site = {os.path.realpath(sysconfig.get_paths()[k]) for k in ("purelib", "platlib")}
print("cwd", os.getcwd()); print("python", sys.version.split()[0], sys.executable); print("flags isolated", sys.flags.isolated, "safe_path", sys.flags.safe_path, "dont_write_bytecode", sys.dont_write_bytecode)
print("sys.path", sys.path)
bad = 0; local = []; third = set()
for name in sorted(set(sys.modules) - before):
    f = getattr(sys.modules[name], "__file__", None)
    if not f: continue
    rf = os.path.realpath(f)
    if any(rf.startswith(s + os.sep) for s in site):
        third.add(name.split(".")[0]); continue
    if any(rf.startswith(s + os.sep) for s in std): continue
    ok = rf.startswith(D + os.sep)
    local.append((name, rf, ok)); bad += (not ok)
for n, f, ok in local: print("LOCAL", "UNDER_DEPLOY" if ok else "OUTSIDE_DEPLOY", n, f)
print("THIRD_PARTY_SITE_PACKAGES", sorted(third), "from", sorted(site))
print("RESULT", "PASS" if bad == 0 and any(n == "s5p_stage1_inspect" for n, _, _ in local) else "STOP", "local_modules", len(local), "outside", bad)
