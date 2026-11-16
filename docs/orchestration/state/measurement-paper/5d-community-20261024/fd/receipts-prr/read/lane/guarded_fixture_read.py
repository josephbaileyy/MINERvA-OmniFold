"""The PRR read connect's guarded call (prr_read_connect.sh), on test_prr's planted EndToEnd fixture, with
ref_g1.PROTECTED widened over the fixture's temp root and the clone's parent, so that any plain read outside the
two allowed roots (the clone and the fixture run) is refused. Usage: PYTHONHASHSEED=0 python3 -B this.py <clone> <out>"""
import sys, tempfile
from pathlib import Path
D, RO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
for p in ("nd-unfolding/prior_retention", "nd-unfolding", "nd-unfolding/ref_g1"):
    sys.path.insert(0, str(D / p))
import test_prr as TP
import prr_read, ref_g1
assert Path(prr_read.__file__).resolve().is_relative_to(D) and Path(ref_g1.__file__).resolve().is_relative_to(D)
t = TP.EndToEnd("test_planted_classes"); t.setUp()
try:
    plant = t.floor_plant()
    plant.update({("K50", "A7_gibuu"): 0.1, ("C1000", "A7_gibuu"): 0.40, ("O2", "q3"): 0.5, ("O3", "q3"): 0.1})
    t.build(plant, {(5, "A7_gibuu"): 0.15, (200, "A7_gibuu"): 0.05, (5, "q3"): 0.3, (200, "q3"): 0.31})
    run = Path(t.run).resolve()
    prot = ref_g1.PROTECTED + (Path(tempfile.gettempdir()).resolve(), D.parent)
    print("protected:", [str(p) for p in prot], "allowed:", [str(D), str(run)], flush=True)
    with ref_g1.read_guards(prot, (D, run), root=False):
        rc = prr_read.main(["--run", str(run), "--repo", str(D), "--out", str(RO)])
    print("prr_read rc", rc, flush=True)
    # the control: the same guard refuses a plain read outside the allowed roots
    probe = Path(tempfile.gettempdir()).resolve() / "guard-probe.txt"; probe.write_text("x")
    try:
        with ref_g1.read_guards(prot, (D, run), root=False):
            probe.read_text()
        print("CONTROL FAILED: the guard let a plain read through"); rc = 99
    except ref_g1.GateFailure as e:
        print("control: refused as expected:", str(e)[:90])
finally:
    t.tearDown()
sys.exit(rc)
