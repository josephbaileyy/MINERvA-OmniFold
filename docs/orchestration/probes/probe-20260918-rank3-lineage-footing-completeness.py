import numpy as np, uproot, json
D="/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
Z=D+"/uq_5d/z_pilot_20260916_a5"
CENTRAL=D+"/products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
PARENT=D+"/uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root"
THROW=D+"/uq_5d/z_precursor_20260914/unified_throw_cov_5d.root"
SUPPORT=D+"/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root"

def scal(f,k):
    try: return f[k].member("fVal")
    except Exception:
        try: return f[k].members.get("fVal")
        except Exception: return "<unreadable>"
def named(f,k):
    try:
        o=f[k]; return (o.member("fName"), o.member("fTitle"))
    except Exception as e: return ("<err>", str(e))

print("############ PART 1 — LINEAGE, read from the PARENT's own fields ############")
p=uproot.open(PARENT)
for k in ("centering_convention","uthrow_source","combined_source"):
    n,t = named(p,k); print("   %-24s name=%r\n   %-24s TITLE=%s" % (k,n,"",t))
print()
for k in ("sqrt_tr_old","sqrt_tr_new","upstream_fixed_seed_null_norm","upstream_joint_mean_shift_norm",
          "upstream_n_throws","n_throws_checked","fixed_seed_null_norm_checked","joint_mean_shift_norm_checked"):
    print("   %-32s = %r" % (k, scal(p,k)))
print()
print("   THROW root's own lineage keys:")
try:
    t=uproot.open(THROW); ks=t.keys()
    print("     n_keys:", len(ks))
    for k in ks:
        if not k.startswith("h"): 
            cn=t[k].classname
            if cn=="TNamed": n,ti=named(t,k); print("     %-34s TNamed  TITLE=%s"%(k,ti))
            else: print("     %-34s %-20s = %r"%(k,cn,scal(t,k)))
except Exception as e: print("     THROW open failed:", e)
print()

print("############ PART 2 — FOOTING, ELEMENTWISE (not by digest) ############")
z=np.load(Z+"/z-cv.npz", allow_pickle=True)
npz_cv   = z["hXSecND_flat"]; npz_mask = z["hSupportMask"].astype(bool)
npz_row  = z["hRowIndex5D"];  npz_g    = z["hInflation_g"]
c=uproot.open(CENTRAL)
prod_cv = c["hXSecND_flat"].values()          # bin contents, no under/overflow
print("   production hXSecND_flat nbins:", prod_cv.size, "   npz hXSecND_flat:", npz_cv.size)
if prod_cv.size == npz_cv.size:
    eq = (prod_cv == npz_cv)
    print("   ELEMENTWISE BITWISE IDENTICAL          :", bool(eq.all()), " (%d of %d agree)" % (int(eq.sum()), eq.size))
    d = np.abs(prod_cv - npz_cv)
    print("   max |abs diff|                         : %.3e" % d.max())
    nzm = npz_cv != 0
    print("   max |rel diff| where npz != 0          : %.3e" % (np.abs(d[nzm]/npz_cv[nzm]).max() if nzm.any() else 0.0))
else:
    print("   SIZE MISMATCH -- cannot compare elementwise")
print()
print("   support mask, recomputed from the PRODUCTION vector vs the persisted mask:")
prod_mask = prod_cv > 0
print("     n_support (production > 0)           :", int(prod_mask.sum()))
print("     n_support (persisted hSupportMask)   :", int(npz_mask.sum()))
print("     MASKS ELEMENTWISE IDENTICAL          :", bool(np.array_equal(prod_mask, npz_mask)))
print()
print("   row order, recomputed vs persisted hRowIndex5D:")
row_from_mask = np.flatnonzero(npz_mask)
print("     len(flatnonzero(persisted mask))     :", row_from_mask.size, " len(hRowIndex5D):", npz_row.size)
print("     ROW ORDER ELEMENTWISE IDENTICAL      :", bool(np.array_equal(row_from_mask, npz_row)))
print("     strictly increasing                  :", bool(np.all(np.diff(npz_row) > 0)))
row_from_prod = np.flatnonzero(prod_mask)
print("     vs rows from the PRODUCTION vector   :", bool(np.array_equal(row_from_prod, npz_row)))
print()
print("   inflation g, npz vs PARENT hInflation_g:")
pg = p["hInflation_g"].values()
print("     sizes %d / %d   ELEMENTWISE IDENTICAL: %s" % (pg.size, npz_g.size, bool(pg.size==npz_g.size and np.array_equal(pg, npz_g))))
if pg.size==npz_g.size and not np.array_equal(pg,npz_g):
    print("     max |abs diff| : %.3e" % np.abs(pg-npz_g).max())
print("     g_min %.10f  g_median %.16f  g_max %.15f  n_gt_one %d" % (npz_g.min(), float(np.median(npz_g)), npz_g.max(), int((npz_g>1.0).sum())))
print()

print("############ PART 4 — ENDPOINT COMPLETENESS ############")
print("   central product globalCompleteness = %r" % scal(c,"globalCompleteness"))
print("   central dataPOT                    = %r" % scal(c,"dataPOT"))
print("   central ndim                       = %r" % scal(c,"ndim"))
hc = c["hCompletenessND_flat"].values()
print("   hCompletenessND_flat: nbins %d  min %.6f  max %.6f" % (hc.size, hc.min(), hc.max()))
print("     n == 0 exactly      : %d" % int((hc==0).sum()))
print("     n > 1               : %d" % int((hc>1).sum()))
print("     n == 1 exactly      : %d" % int((hc==1.0).sum()))
print("     max on support      : %.6f" % hc[npz_mask].max())
print("     n > 1 on support    : %d of %d" % (int((hc[npz_mask]>1).sum()), int(npz_mask.sum())))
print()
print("   metadata_json from z-cv.npz:")
try:
    md=json.loads(str(z["metadata_json"]))
    print(json.dumps(md, indent=2, sort_keys=True)[:2200])
except Exception as e:
    print("   ", type(e).__name__, e); print("   raw:", str(z["metadata_json"])[:1200])
import numpy as np, uproot
D="/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
c=uproot.open(D+"/products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
g=c["globalCompleteness"].member("fVal")
hc=c["hCompletenessND_flat"].values(); cv=c["hXSecND_flat"].values(); sup=cv>0
ov=hc[hc>1.0]
print("globalCompleteness = %.17g   exactly 1.0 -> %s" % (g, g==1.0))
print("per-bin n>1 = %d   max = %.17g   max excess = %.6e" % (ov.size, hc.max(), hc.max()-1.0))
print("n==1.0 exactly = %d   n==0.0 exactly = %d   support = %d" % (int((hc==1.0).sum()), int((hc==0.0).sum()), int(sup.sum())))
print("on support: n>1 %d (%.1f%%)  n==1 %d  n<1 %d" % (int((hc[sup]>1).sum()),100*float((hc[sup]>1).mean()),int((hc[sup]==1).sum()),int((hc[sup]<1).sum())))
print("excess (c-1 | c>1): min %.3e med %.3e max %.3e" % ((ov-1).min(),float(np.median(ov-1)),(ov-1).max()))
print("off-support hc nonzero:", int((hc[~sup]!=0).sum()))
print("central product scalar keys:", [k.split(';')[0] for k in c.keys() if c[k.split(';')[0]].classname.startswith('TParameter')])
import uproot, os
D="/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
comps=[("stat",D+"/uq_cov_stat_5d.root"),("ml",D+"/uq_cov_mlsplit_5d.root"),
       ("active",D+"/active_universe_5d/standard/candidate/std_final5_candidate.root")]
for lab,p in comps:
    print("--- %s  %s" % (lab, "MISSING" if not os.path.exists(p) else "%.1f MB"%(os.path.getsize(p)/1e6)))
    if not os.path.exists(p): continue
    try:
        f=uproot.open(p); ks=[k.split(';')[0] for k in f.keys()]
        print("    keys=%d" % len(ks))
        for k in ks[:18]:
            cn=f[k].classname
            if cn.startswith("TParameter"): print("      %-32s = %r" % (k, f[k].member('fVal')))
            elif cn=="TNamed": print("      %-32s TNamed = %s" % (k, f[k].member('fTitle')))
            else:
                try: n=f[k].member('fXaxis').member('fNbins')
                except Exception:
                    try: n=f[k].member('fNcells')-2
                    except Exception: n='?'
                print("      %-32s %-8s n=%s" % (k, cn, n))
        if len(ks)>18: print("      ... %d more" % (len(ks)-18))
    except Exception as e: print("    OPEN FAILED", type(e).__name__, e)
print()
print("--- the two combined candidates (existence/size only)")
for nm in ("uq_universe_5d_covariance_combined_bkgaware.root","uq_universe_5d_covariance_combined_bkgaware_uthrow.root"):
    p=D+"/uq_5d/universe_stage2_5d_bkgaware/"+nm
    print("   %-58s %s" % (nm, ("%.2f GB"%(os.path.getsize(p)/1e9)) if os.path.exists(p) else "ABSENT"))
