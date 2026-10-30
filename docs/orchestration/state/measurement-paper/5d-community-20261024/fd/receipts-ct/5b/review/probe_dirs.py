"""Probe: does job A's B layout exist when nn_dump_inputs.py, s5p_mc_truth_pred.py and check's write_json write?"""
import json, subprocess, sys, tempfile
from pathlib import Path
from unittest import mock
import numpy as np
WT = Path(sys.argv[1])
sys.path.insert(0, str(WT / "nd-unfolding")); sys.path.insert(0, str(WT / "nd-unfolding/tests"))
import fd_ct_period_inputs as pi
import test_fd_ct_periods as T

B = Path(tempfile.mkdtemp()) / "B"
# 1) nn_dump_inputs.py's write: np.savez_compressed(args.out) with no mkdir, B/dumps absent (submit refuses if it exists;
#    only merge has run, which creates B/merged)
(B / "merged").mkdir(parents=True)
try:
    np.savez_compressed(str(B / "dumps" / "nn_ALL.npz"), a=np.zeros(3))
    print("nn_dump write: OK")
except Exception as e:
    print("nn_dump write FAILS:", type(e).__name__, e)

# 2) suppose dumps/ existed (lateral mkdirs it): check with truth-out under B/truth and out under B/inputs, both absent
(B / "dumps").mkdir()
merged = B / "merged/runEventLoopOmniFold_5D_PB_zero.root"; merged.write_bytes(b"m")
merged.with_name(merged.name + ".json").write_text(json.dumps({"period": "PB", "out": str(merged), "out_sha256": pi.sha256(merged)}))
flux = B / "flux_PB.root"; flux.write_bytes(b"f")
nn = T.nn_npz(B / "dumps/nn_PB.npz"); lat = T.nn_npz(B / "dumps/lat_PB.npz")
bkg = T.bkg_npz(B / "dumps/lat_PB_bkg.npz", lat, merged)

def real_truth(cmd, *a, **k):   # s5p_mc_truth_pred.py's write: np.savez_compressed(a.out, ...), no mkdir
    out = cmd[cmd.index("--out") + 1]
    try:
        np.savez_compressed(out, xsec_flat=np.zeros(3))
        return subprocess.CompletedProcess(cmd, 0)
    except Exception as e:
        print("  truth write FAILS:", type(e).__name__, e)
        return subprocess.CompletedProcess(cmd, 1)

argv = ["check", "--period", "PB", "--merged", str(merged), "--nn-npz", str(nn), "--lat-npz", str(lat), "--lat-bkg",
        str(bkg), "--flux", str(flux), "--truth-out", str(B / "truth/truth_PB.npz"), "--out", str(B / "inputs/check_PB.json")]
with mock.patch.dict(pi.FLUX, {"PB": pi.sha256(flux)}), mock.patch.object(pi, "merged_data_pot", lambda p: 1.06e21), \
        mock.patch.object(pi, "flux_data_pot", lambda p: 1.06e21), mock.patch.object(pi.subprocess, "run", real_truth):
    print("check rc:", pi.main(argv))
(B / "truth").mkdir()
with mock.patch.dict(pi.FLUX, {"PB": pi.sha256(flux)}), mock.patch.object(pi, "merged_data_pot", lambda p: 1.06e21), \
        mock.patch.object(pi, "flux_data_pot", lambda p: 1.06e21), mock.patch.object(pi.subprocess, "run", real_truth):
    try:
        print("check rc with truth/ present:", pi.main(argv))
    except Exception as e:
        print("check with truth/ present RAISES:", type(e).__name__, e)
