#!/usr/bin/env python3
"""MP-2 S2 preflight addendum (report only): GiBUU-H per-event momentum/energy balance by production_ID, task1001 only."""
import numpy as np
P="/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3c/prod"
d=np.concatenate([np.loadtxt(f"{P}/task{i}/FinalEvents.dat",comments="#") for i in (1001,)])
key=d[:,0].astype(np.int64)*10**7+d[:,1].astype(np.int64)
u,inv=np.unique(key,return_inverse=True)
init=d[:,4]==0
px=np.bincount(inv,np.where(init,-1,1)*d[:,9]); py=np.bincount(inv,np.where(init,-1,1)*d[:,10])
pz=np.bincount(inv,np.where(init,-1,1)*d[:,11]); E=np.bincount(inv,np.where(init,-1,1)*d[:,8])
enu=np.bincount(inv,d[:,14])/np.bincount(inv)
pt=1000*np.hypot(px,py)
prod=np.zeros(u.size,int); prod[inv]=d[:,13].astype(int)
for p in np.unique(prod):
    m=prod==p; print("prod",p,"n",m.sum(),"pT imbalance MeV q50/q90",np.round(np.quantile(pt[m],[0.5,0.9]),3),"frac>1MeV",round(float(np.mean(pt[m]>1)),3),"pz-Enu q50",round(float(np.median(1000*(pz[m]-enu[m]))),2),"E-Enu q50",round(float(np.median(1000*(E[m]-enu[m]))),2))
# which ids in imbalanced events
bad=pt>1
ids=d[:,2].astype(int); print("ids in bad events", np.unique(ids[bad[inv]],return_counts=True)); print("ids in good", np.unique(ids[~bad[inv]],return_counts=True))
