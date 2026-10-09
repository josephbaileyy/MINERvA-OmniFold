# Independent re-derivation (different method from cycle 0): closed form + explicit Monte Carlo.
import json, math, random, sys
from statistics import NormalDist, fmean, stdev
W=sys.argv[1]; N=NormalDist()
a=json.load(open(W+'/docs/orchestration/state/ki85-diag-20261006/ki85_result.json'))
b=json.load(open(W+'/docs/orchestration/state/ki84-adopt-20261006/recompute_2d_budget.json'))
f=(a['median_rel_spread_pct']['realboot']/b['VL170']['boot']['median_pct'])**2
share=f/(f+(1-f)*2.0); k=math.sqrt(share); m=math.sqrt(1-share)
print('share',share,'offset rms (both)',m,'offset rms (data-only)',m/k)
# closed-form pooled coverage: offset+noise ~ N(0, m^2+k^2=1)
print('pooled I68 both', 2*N.cdf(1/math.sqrt(m*m+k*k))-1, 'data-only', 2*N.cdf(1/math.sqrt((m/k)**2+1))-1)
# over-cover fraction, exact: find d* with cov(d*)=nominal, fraction = P(|delta|<d*)
nom=0.682689492
cov=lambda d: N.cdf((1-d)/k)-N.cdf((-1-d)/k)
lo,hi=0.0,3.0
for _ in range(80):
    mid=(lo+hi)/2
    (lo,hi)=(mid,hi) if cov(mid)>nom else (lo,mid)
print('d*',lo,'over-cover fraction', 2*N.cdf(lo/m)-1)
# explicit MC of the bias test and coverage with 719 experiments x 206 functionals
rng=random.Random(20261009); Ne=719; fails=[]; overs=[]
for rep in range(5):
    nf=0; no=0
    for j in range(206):
        d=rng.gauss(0,m); pulls=[d+rng.gauss(0,k) for _ in range(Ne)]
        mj=fmean(pulls); sj=stdev(pulls); t=mj/(sj/math.sqrt(Ne))
        nf+= abs(t)>4.0625
        no+= sum(abs(p)<1 for p in pulls)/Ne > nom
    fails.append(nf); overs.append(no)
print('MC bias fails per 206',fails,'MC over-cover count per 206',overs)
