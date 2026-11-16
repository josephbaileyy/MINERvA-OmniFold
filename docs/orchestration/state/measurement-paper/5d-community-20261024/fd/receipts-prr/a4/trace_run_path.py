"""A4 receipt: the dynamic trace of prr_ibu's run path. A4's REQUIRED fixture and substitutions, with every temp path
protected; REF-G1's own guard test (ref_g1._audit's) is logged as well as applied. Lists every open and filesystem
event inside the guard by root and by the innermost repository frame (file:line), every import attempted inside the
guard, and every read the guard would refuse. Run from <clone>/nd-unfolding/prior_retention: python3 -B trace_run_path.py"""
import collections, contextlib, io, json, os, sys, tempfile
from pathlib import Path
HERE = Path.cwd().resolve(); ND = HERE.parent; REPO = ND.parent
sys.path.insert(0, str(HERE))
import test_prr as TP
import ibu1, ref_g1, s5p_universe
rows, imports, would_refuse = [], [], []
def site():
    f = sys._getframe(2)
    while f is not None:
        if f.f_code.co_filename.startswith(str(ND)) and "trace_run_path" not in f.f_code.co_filename:
            return f"{os.path.relpath(f.f_code.co_filename, REPO)}:{f.f_lineno}"
        f = f.f_back
    return "?"
EVENTS = ("os.listdir", "os.scandir", "os.mkdir", "os.rmdir", "os.remove", "os.rename", "os.replace", "shutil.rmtree",
          "shutil.copyfile", "os.symlink", "os.truncate", "glob.glob")
def hook(ev, args):
    if not ref_g1._READS["active"]:
        return
    if ev == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        p = os.path.abspath(os.fsdecode(args[0])); flags = args[2]
        kind = "write" if isinstance(flags, int) and (flags & os.O_ACCMODE) == os.O_WRONLY else "read"
        rows.append((p, kind, site()))
        if kind == "read" and any(ref_g1.under(p, r) for r in ref_g1._READS["protected"]) \
                and not any(ref_g1.under(p, r) for r in ref_g1._READS["allowed"]) and not (flags & ref_g1.noatime_flag()):
            would_refuse.append((p, site()))
    elif ev.startswith(("subprocess", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork")) or ev in EVENTS:
        rows.append((f"{ev} {os.fsdecode(args[0]) if args and isinstance(args[0], (str, bytes, os.PathLike)) else ''}", ev, site()))
sys.addaudithook(hook)
class Finder:
    def find_spec(self, name, path=None, target=None):
        if ref_g1._READS["active"]:
            imports.append(name)
        return None
sys.meta_path.insert(0, Finder())
with tempfile.TemporaryDirectory() as d:
    d = Path(d).resolve()
    with TP.route2_fixture(d) as fx:
        cfg = json.loads(ref_g1.CONFIG.read_text())
        cfg["ratios"]["sha256"][TP.R.CIBU["ratio"]] = next(f["sha256"] for f in fx.files if f["role"] == "closure_ratio_nuwro")
        cfg_copy = fx.stage / "ref_g1_config.json"; cfg_copy.write_text(json.dumps(cfg))
        real_load = ibu1.load_inputs
        def load_inputs(prod, icfg, npz, bkg):
            return real_load(prod, {**icfg, "inputs": {**icfg["inputs"], "of_inputs_5d_sha256": fx.npz_sha,
                                                       "bkg_dump_sha256": TP.P.sha256_path(bkg)}}, npz, bkg)
        saved = (ref_g1.PROTECTED, ref_g1.CONFIG, ibu1.load_inputs, s5p_universe.check_alignment)
        ref_g1.PROTECTED = tuple(saved[0]) + (d,); ref_g1.CONFIG, ibu1.load_inputs = cfg_copy, load_inputs
        s5p_universe.check_alignment = lambda *x, **k: {}
        try:
            rc, out, err = TP.route2_main(d, d / "route2")
        finally:
            ref_g1.PROTECTED, ref_g1.CONFIG, ibu1.load_inputs, s5p_universe.check_alignment = saved
    def root(p):
        if p.startswith(str(d) + "/"):
            rel = p[len(str(d)) + 1:]
            top = rel.split("/")[0]
            return {"stage": "the stage dest ($OUT/stage)", "queues": "the queues ($OUT/queues)",
                    "route2": "the output ($OUT/route2)"}.get(top, f"$OUT/{top}: OUTSIDE THE FOUR ROOTS")
        if p.startswith(str(REPO) + "/"):
            return "the repository (the deploy)"
        if p.startswith(sys.prefix) or p.startswith(sys.base_prefix):
            return "the python environment (not protected)"
        return "elsewhere"
    print(f"rc {rc}; stdout {out.strip().splitlines()[-1:]}; refusals in stderr: {err.count('refusing')}")
    print(f"guarded events: {len(rows)}; reads the guard would refuse: {len(would_refuse)}")
    for p, s in would_refuse:
        print(f"  WOULD REFUSE {p} at {s}")
    agg = collections.defaultdict(collections.Counter)
    for p, kind, s in rows:
        r = root(p) if p.startswith("/") else "event"
        agg[(r, kind, s)][p.replace(str(d), "$OUT").replace(str(REPO) + "/", "") if r != "the python environment (not protected)" else "(module files)"] += 1
    for (r, kind, s), c in sorted(agg.items()):
        names = sorted(c)
        print(f"  {r:40s} {kind:20s} {s:52s} {sum(c.values()):4d}  {names[0][:90]}{f' (+{len(names) - 1} more)' if len(names) > 1 else ''}")
    top = sorted({n.split('.')[0] for n in imports})
    print(f"imports attempted inside the guard: {len(top)} top-level names; ROOT among them: {'ROOT' in top}")
    print("  " + " ".join(top))
