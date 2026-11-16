"""g2r_readout.main() unchanged, with only the phase function replaced by one that returns a given record, so its own
printed line and return code can be fed to the readout connect's verdict block. Used by test_readout_place.sh only.
    python test_readout_verdict.py <checkout> <data|tune> <verdict> <atime 0|1> <out dir>"""
import sys
from pathlib import Path
root, phase, verdict, atime, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == "1", sys.argv[5]
sys.path.insert(0, str(Path(root) / "2d-unfolding/cov2d/g2r"))
import g2r_readout as gr  # noqa: E402
rec = {"verdict": verdict, "controls_failed": [], "stop": ["atime moved on 1 inputs"] if atime else [],
       "atime_moved": ["/x"] if atime else []}
gr.phase_data = lambda *a, **k: rec
gr.phase_tune = lambda *a, **k: rec
argv = ["data"] if phase == "data" else ["tune", "--truth", "G18"]
sys.exit(gr.main(argv + ["--products", "/dev/null", "--map-sha", "0" * 64, "--out", out]))
