import sys, json
sys.argv=[sys.argv[0], sys.argv[1]]
import importlib.util
spec=importlib.util.spec_from_file_location("fx","fwer_extra.py"); fx=importlib.util.module_from_spec(spec); spec.loader.exec_module(fx)
import numpy as np
for m0 in (3,4,6,7,8,9):
    c=fx.ALPHA/m0
    ks=np.array([fx.kstar(c,B) for B in range(1,2000)]); K=int(ks.max())+2
    def f(p):
        d=np.zeros(K+1); d[0]=1.0; rej=0.0
        for B in range(1,2000):
            d=np.concatenate([[d[0]*(1-p)], d[1:]*(1-p)+d[:-1]*p]); t=ks[B-1]
            if t>=0: rej+=d[:t+1].sum(); d[:t+1]=0.0
        return rej
    v=fx.leg(f,c,24); print(json.dumps({"m0":m0,"FWER_bound_over_alpha":m0*v/fx.ALPHA}),flush=True)
