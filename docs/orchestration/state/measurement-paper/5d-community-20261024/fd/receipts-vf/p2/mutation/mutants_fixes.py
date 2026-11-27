import subprocess, shutil, sys, os, hashlib
from pathlib import Path
W = Path.home() / "s2r-wt"
F = W / "nd-unfolding/fd_vf_p2.py"
V = W / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-vf/readings/vf_readings.py"
MUT = [
 (F, 'and pv < P_FLOOR):', '):', "p-floor exemption without the floor"),
 (F, 'CHI2_EXACT = {"gch"}', 'CHI2_EXACT = set()', "gch back to 1e-9"),
 (F, '"not_replaced": {"/table_ii_committed_beside_B0"', '"not_replaced_": {"/table_ii_committed_beside_B0"', "prr not_replaced dropped"),
 (F, 'RTOL_XK = 1e-7', 'RTOL_XK = 1e-6', "xk tolerance loosened"),
 (F, 'RTOL_IBU = 1e-11 ', 'RTOL_IBU = 1e-10 ', "IBU tolerance loosened"),
 (F, 'if q.is_symlink() or not q.is_file():', 'if not q.exists():', "remap follows symlinks"),
 (F, '        log.append((s_, len(data), hashlib.sha256(data).hexdigest()))\n', '', "remap read unlogged"),
 (F, '        GC.read_noatime, XS.read_committed = orig_read, orig_rc\n', '        pass\n', "remap not restored"),
 (F, 'raw = subst[str(path)] if str(path) in subst else orig_rc(path)', 'raw = orig_rc(path)', "substitution ignored"),
 (F, '"fetched": {k: PS + v[0] for k, v in FETCHED.items()}', '"fetched": {k: v[0] for k, v in FETCHED.items()}', "fetched bare paths"),
 (V, 'return "a flag appears" if (not a and b) else None', 'return "a flag appears" if (a and not b) else None', "flag direction flipped"),
 (V, 'if not (re.fullmatch(r["readout"], readout) and r["path"].match(path)):', 'if False:', "ruling ignores path"),
 (V, 'if hit and (o is None or r["premise"](o, v, path)):', 'if hit:', "ruling ignores its premise"),
 (V, '                return {f"[{k}={i}]": v for i, v in zip(ids, x)}\n', '                return None\n', "lists keyed by index"),
 (V, '    return 1 if stop else 0', '    return 0', "stop exits 0"),
 (V, '("does not clear at these truths", "clears at these truths")}', '("does not clear at these truths", "clears at these truths"), ("agree", "agree below a correlation")}', "weakening allowed"),
 (V, 'return f"gains {sorted(gained)}" if gained else None', 'return None', "list gains ignored"),
 (V, 'empty = {"flag_bool": False,', 'empty = {"flag_bool": True,', "absent reads as flagged"),
 (V, 'return "descriptive" if DESCRIPTIVE.match(n) else "structural"', 'return "descriptive"', "unclassified passes"),
 (V, '"breaks_the_prior_closure", ', '', "breaks_the_prior_closure unclassed"),
 (V, '"cells_beyond_half_sigma", ', '', "cells_beyond_half_sigma unclassed"),
 (V, '    if len(hits) > 1 and value is not None:', '    if False:', "multi-class by order"),
 (V, '    if "/labels/" in path:\n        return "descriptive"\n', '', "labels not descriptive"),
 (V, 'SWEPT_SKIP = re.compile(r"(^|/)(vf_patch|argv|inputs_sha256|files_sha256)(/|$)")', 'SWEPT_SKIP = re.compile(r"(^|/)(vf_patch|argv|inputs_sha256|files_sha256|controls)(/|$)")', "controls skipped"),
 (V, 'and o["table"][at]["grade"]["flagged"] and v["table"][at]["grade"]["flagged"])', ')', "q3 premise without the level check"),
 (V, 'return a >= 1.0 and 0.999 < b < 1.0', 'return True', "QD premise always holds"),
]
env = dict(os.environ, VF_P2_FETCH="/Users/josephbailey/vf-p2-fetch-20261126")
res = []
for path, old, new, label in MUT:
    src = path.read_bytes(); txt = src.decode()
    assert txt.count(old) == 1, (label, txt.count(old))
    work = Path.home() / "vf-p2-fetch-20261126-xk"
    try:
        path.write_text(txt.replace(old, new))
        r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-x", "-q", "tests/test_fd_vf_p2.py"], cwd=W / "nd-unfolding",
                           env=env, capture_output=True, text=True, timeout=1800)
        killed = r.returncode != 0
    finally:
        path.write_bytes(src)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == hashlib.sha256(src).hexdigest()
    res.append((label, "KILLED" if killed else "SURVIVED", r.stdout.strip().splitlines()[-1][:120]))
    print(*res[-1], sep=" | ", flush=True)
print(f"{sum(x[1]=='KILLED' for x in res)}/{len(res)} killed")
