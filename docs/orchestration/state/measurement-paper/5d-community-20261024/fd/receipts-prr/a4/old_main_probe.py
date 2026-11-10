"""A4 receipt probe: an earlier prr_ibu.py's main on A4's REQUIRED fixture, every path protected, the same
substitutions as test_the_run_path_end_to_end_with_every_path_protected. Usage (from <clone>/nd-unfolding/prior_retention):
python3 -B old_main_probe.py <file holding the earlier prr_ibu.py source> <label>. Prints the rc and the refusal."""
import contextlib, hashlib, io, json, os, sys, tempfile, types
from pathlib import Path
HERE = Path.cwd().resolve()
sys.path.insert(0, str(HERE))
import test_prr as TP
old_src = Path(sys.argv[1]).read_text()
mod = types.ModuleType("prr_ibu_old")
mod.__file__ = str(HERE / "prr_ibu.py")  # so REPO, the pins and the guard roots resolve as in the deploy
exec(compile(old_src, mod.__file__, "exec"), mod.__dict__)
print(f"{sys.argv[2]}: prr_ibu.py sha256 {hashlib.sha256(old_src.encode()).hexdigest()}")
import ibu1, ref_g1, s5p_universe
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
        so, se, cwd = io.StringIO(), io.StringIO(), os.getcwd()
        os.chdir(TP.REPO)
        try:
            with contextlib.redirect_stdout(so), contextlib.redirect_stderr(se):
                rc = mod.main(["run", "--queue-dir", str(d / "queues"), "--stage", str(d / "stage.json"), "--out", str(d / "route2")])
        finally:
            os.chdir(cwd)
            ref_g1.PROTECTED, ref_g1.CONFIG, ibu1.load_inputs, s5p_universe.check_alignment = saved
        msg = se.getvalue().strip().replace(str(d), "<tmp>")
        print(f"{sys.argv[2]}: rc {rc}")
        print(f"{sys.argv[2]}: stderr: {msg[-400:]}")
        print(f"{sys.argv[2]}: route2 products: {sorted(p.name for p in (d / 'route2').iterdir()) if (d / 'route2').exists() else None}")
