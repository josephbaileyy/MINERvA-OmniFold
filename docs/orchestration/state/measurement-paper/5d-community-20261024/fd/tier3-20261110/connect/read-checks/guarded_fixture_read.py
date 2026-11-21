"""The T3 read connect's guarded call (t3p_read_connect.sh), on test_t3p's planted EndToEnd fixture, with
ref_g1.PROTECTED widened over the fixture's temp root and the clone's parent, so that any plain read outside the two
allowed roots (the clone and the fixture run) is refused. The fixture's own patch (M16 = identity) is kept, as in
test_t3p. The call body is the connect's: sys.path, the guard, t3p_read.main with stdout to /dev/null, then the
verdict from readout.json. A control shows the same guard refuses a plain read outside the allowed roots.
Usage: PYTHONHASHSEED=0 python3 -B this.py <clone> <out>"""
import contextlib, json, os, sys, tempfile
from pathlib import Path
D, RO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
for p in ("nd-unfolding/tier3", "nd-unfolding/prior_retention", "nd-unfolding", "nd-unfolding/ref_g1"):
    sys.path.insert(0, str(D / p))
import test_t3p as TT
import t3p_read, ref_g1
assert Path(t3p_read.__file__).resolve().is_relative_to(D) and Path(ref_g1.__file__).resolve().is_relative_to(D)
t = TT.EndToEnd("test_planted_classes"); t.setUp()
rc = 99
try:
    t.build(t.plant)
    run = Path(t.run).resolve()
    prot = ref_g1.PROTECTED + (Path(tempfile.gettempdir()).resolve(), D.parent)
    print("protected:", [str(p) for p in prot], "allowed:", [str(D), str(run)], flush=True)
    with ref_g1.read_guards(prot, (D, run), root=False):
        with open(os.devnull, "w") as null, contextlib.redirect_stdout(null):
            rc = t3p_read.main(["--run", str(run), "--repo", str(D), "--out", str(RO)])
    print(json.dumps({"verdict": json.loads((RO / "readout.json").read_text())["verdict"]}), flush=True)
    print("t3p_read rc", rc, flush=True)
    print("out dir:", sorted(p.name for p in RO.iterdir()), flush=True)
    probe = Path(tempfile.gettempdir()).resolve() / "t3-guard-probe.txt"; probe.write_text("x")
    try:
        with ref_g1.read_guards(prot, (D, run), root=False):
            probe.read_text()
        print("CONTROL FAILED: the guard let a plain read through"); rc = 99
    except ref_g1.GateFailure as e:
        print("control: refused as expected:", str(e)[:90])
    finally:
        probe.unlink()
finally:
    t.tearDown()
sys.exit(rc)
