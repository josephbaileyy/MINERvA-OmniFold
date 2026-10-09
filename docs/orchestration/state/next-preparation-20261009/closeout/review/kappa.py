import json, sys, math
W=sys.argv[1]
a=json.load(open(W+'/docs/orchestration/state/ki85-diag-20261006/ki85_result.json'))
b=json.load(open(W+'/docs/orchestration/state/ki84-adopt-20261006/recompute_2d_budget.json'))
num=a['median_rel_spread_pct']['realboot']; den=b['VL170']['boot']['median_pct']
f=(num/den)**2
M=4.978198e21; D=1.057394e21; r=M/D
print('f_data',f,'MC/data',r)
for name,frac in [('N1 half',0.5),('N2 48%',0.48)]:
    g=1/frac  # MC-stream variance inflation
    share=f/(f+(1-f)*g)
    print(name,'bank MC/data',r*frac,'inflation',g,'data share',share,'kappa',math.sqrt(share))
# sensitivity: kappa if f_data were from a different ratio (e.g. per-bin variation) -> find f giving kappa 0.8 at half bank
# share=0.64 => f/(f+2(1-f))=0.64 => f=0.64*(2-f) => f(1+0.64)=1.28 => f=0.7805
for k in (0.8,):
    s=k*k; fstar=2*s/(1+s); print('f_data needed for kappa=0.8 at half bank', fstar)
# an alternative formulation: kappa defined as outer sd / sigma_hat; outer = sqrt(data-term at bank), data term at bank unchanged? data term itself also changes with bank? assume no.
