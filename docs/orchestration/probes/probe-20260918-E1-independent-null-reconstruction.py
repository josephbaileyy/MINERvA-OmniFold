import numpy as np, json, hashlib, sys, os
sys.path.insert(0, "/tmp/e1pin")
D = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5"
F = D + "/z-null.npz"

print("E1 -- INDEPENDENT RECONSTRUCTION of r_null (SPEC reject condition 11b)")
print("performed by z-independent-assessor; NOT the pilot's owner, NOT the proposal's author")
h = hashlib.sha256(open(F,"rb").read()).hexdigest()
print("file   :", F)
print("sha256 :", h)
print("expected cb82fc3285c981b91625530d48c14ff5554db5154db298a3144a57520633d77e")
print("MATCH  :", h == "cb82fc3285c981b91625530d48c14ff5554db5154db298a3144a57520633d77e")
print()

z = np.load(F, allow_pickle=True)
x1, x2, m_persisted = z["x_cv"], z["x_cv2"], z["support_mask"]
print("keys present:", sorted(z.files))
print("NOTE: the npz carries NO recorded null norm, so nothing here reads the producer's number.")
print()

# --- 1. RECOMPUTE the predicate and CHECK it, never apply it blind
m_mine = x1 > 0.0
print("--- 1. the support predicate, recomputed and CHECKED (not applied)")
print("   n_total                    :", x1.size)
print("   n_support (my x_cv > 0)     :", int(m_mine.sum()))
print("   n_support (persisted mask)  :", int(m_persisted.sum()))
print("   masks ELEMENTWISE IDENTICAL :", bool(np.array_equal(m_mine, m_persisted)))
print("   n_genuine_zero (x_cv == 0)  :", int((x1 == 0.0).sum()))
print("   n_negative     (x_cv <  0)  :", int((x1 < 0.0).sum()))
print("   all finite                  :", bool(np.all(np.isfinite(x1)) and np.all(np.isfinite(x2))))
print()

# --- 2. my own arithmetic, two independent summation orders
a, b = x1[m_mine], x2[m_mine]
d = b - a
num_np = float(np.linalg.norm(d)); den_np = float(np.linalg.norm(a))
num_srt = float(np.sqrt(np.sum(np.sort(d*d))))      # ascending-magnitude summation
den_srt = float(np.sqrt(np.sum(np.sort(a*a))))
num_ks  = float(np.sqrt(sum(sorted((d*d).tolist()))))  # pure-python Kahan-free ordered sum
print("--- 2. r_null, my own arithmetic, three summation orders")
print("   numpy order   r_null = %.17e" % (num_np/den_np))
print("   sorted order  r_null = %.17e" % (num_srt/den_srt))
print("   python order  r_null = %.17e" % (num_ks/den_srt))
print("   num_norm = %.17e   cv_norm = %.17e" % (num_np, den_np))
print()

# --- 3. CALL the committed instrument rather than trusting my retype
from z_statistics import null_ratio, reconstruct_null_ratio, support_mask
r_inst = null_ratio(x1, x2)
r_rec  = reconstruct_null_ratio(x1, x2, m_persisted)
print("--- 3. the committed instrument (blob-pinned), called rather than reimplemented")
print("   null_ratio            :", {k: (('%.17e'%v) if isinstance(v,float) else v) for k,v in r_inst.items()})
print("   reconstruct_null_ratio:", {k: (('%.17e'%v) if isinstance(v,float) else v) for k,v in r_rec.items()})
print()

# --- 4. the comparison target comes from the COMMITTED run log, not from the receipt
BUILD = 4.4520002137582904e-14
mine  = num_np/den_np
print("--- 4. against the build's r_null as recorded in the COMMITTED run log")
print("   build   : %.17e" % BUILD)
print("   mine    : %.17e" % mine)
print("   bitwise equal :", mine == BUILD)
print("   relative diff : %.3e   (=%.2f ULP)" % (abs(mine/BUILD-1), abs(mine/BUILD-1)/np.finfo(float).eps))
print()

# --- 5. the other relayed figures, independently
diff = (a != b)
print("--- 5. relayed figures, re-derived")
print("   bins differing BITWISE on support   :", int(diff.sum()), "of", int(m_mine.sum()))
print("   bins AGREEING bitwise on support    :", int((~diff).sum()))
off = ~m_mine
print("   bins differing bitwise OFF support  :", int((x1[off] != x2[off]).sum()))
rho = np.abs(d/a)
i = int(np.argmax(rho))
grid = np.flatnonzero(m_mine)[i]
print("   max |d/x| on support                : %.17e" % rho[i])
print("   at support-index %d  = grid-index %d" % (i, grid))
print("   min |d/x| on support                : %.17e" % rho.min())
print("   bracket  min <= r_null <= max       :", bool(rho.min() <= mine <= rho[i]))
print("   per-bin max vs eps=1e-9  margin     : %.1fx" % (1e-9/rho[i]))
print("   r_null      vs eps=1e-9  margin     : %.4gx" % (1e-9/mine))
