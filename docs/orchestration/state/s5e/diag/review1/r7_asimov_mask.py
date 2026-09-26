"""Noise-free E_avail: driver-npz residual difference with/without sentinel rows vs per-functional edge-safe probe."""
import numpy as np
from common import *
a0 = L(f"{RUNS}/drv/driver_eavail.npz"); base = L(f"{RUNS}/asimov/asimov_b0_eavail.npz")
an = L(f"{RUNS}/rep/rep_asimov_eavail_nosentinel.npz"); aj = L(f"{RUNS}/rep/rep_asimov_eavail_jitteredge1.npz")
aj0 = L(f"{RUNS}/asimov/asimov_eavail_jitter1.npz")
b5 = U @ base["xsec_it5_flat"]
rd = R(a0["fn_unf"], a0["fn_true"]); rb = R(b5, base["fn_true"]); rn = R(U @ an["xsec_flat"], an["fn_true"])
print("nosentinel fn_true == b0 fn_true:", np.array_equal(an["fn_true"], base["fn_true"]), "max rel %.2e" % np.abs(R(an["fn_true"], base["fn_true"])).max())
probe = np.abs(R(U @ aj["xsec_flat"], b5))
d_with, d_wo = np.abs(rd - rb), np.abs(rd - rn)
mask_move = np.abs(rn - rb)
print("driver-npz (with sentinel): max %.3f pp (%s) med %.3f" % (100 * d_with.max(), NAMES[int(d_with.argmax())], 100 * np.median(d_with)))
print("driver-npz (without):       max %.3f pp (%s) med %.3f" % (100 * d_wo.max(), NAMES[int(d_wo.argmax())], 100 * np.median(d_wo)))
print("mask move on npz residual:  max %.3f pp (%s) med %.3f" % (100 * mask_move.max(), NAMES[int(mask_move.argmax())], 100 * np.median(mask_move)))
print("edge-safe probe:            max %.3f %% (%s) med %.3f" % (100 * probe.max(), NAMES[int(probe.argmax())], 100 * np.median(probe)))
j = NAMES.index("EW17")
print("EW17: diff with %.3f, without %.3f, mask move %.3f, probe %.3f (pp)" % (100 * d_with[j], 100 * d_wo[j], 100 * mask_move[j], 100 * probe[j]))
print("functionals where |driver-npz| > probe: with %d, without %d (of 153)" % ((d_with > probe).sum(), (d_wo > probe).sum()))
print("functionals where mask shrinks |diff| by more than probe:", int(((d_with - d_wo) > probe).sum()), " grows by more than probe:", int(((d_wo - d_with) > probe).sum()))
print("original (confounded) jitter asimov: max %.3f%% med %.3f%%" % (100 * np.abs(R(U @ aj0["xsec_flat"], b5)).max(), 100 * np.median(np.abs(R(U @ aj0["xsec_flat"], b5)))))
# nosentinel residual stats
print("nosentinel residual EW", ew(rn), " b0 k5", ew(rb))
