# Fixed bank S: U_e - T = delta_j (bank MC realization, fixed over e) + eps_e (data stream).
# Exactly calibrated both-stream sigma_hat^2 = D + M; data-only sigma_hat^2 = D. share = D/(D+M).
import math
from statistics import NormalDist
N=NormalDist(); share=0.3534430114159182; Nexp=719; tcrit=4.0625
xs=[i/500 for i in range(-4000,4001)]; w=[N.pdf(x) for x in xs]; tot=sum(w)
def report(name, rms_delta, sd_eps):
    def cov(d): return N.cdf((1-d)/sd_eps)-N.cdf((-1-d)/sd_eps)
    mean=sum(wi*cov(rms_delta*x) for x,wi in zip(xs,w))/tot
    over=sum(wi for x,wi in zip(xs,w) if cov(rms_delta*x)>0.682689492)/tot
    # bias test: t = (delta/sigma_hat)/(sd_eps/sqrt(N)); fails if |t|>tcrit
    thr=tcrit*sd_eps/math.sqrt(Nexp)/rms_delta
    pfail=2*(1-N.cdf(thr))
    print(f'{name}: rms offset/sigma_hat={rms_delta:.3f} outer sd/sigma_hat={sd_eps:.3f} I68 cov at delta=0 {cov(0):.3f}; mean I68 coverage over functionals {mean:.4f}; frac over-covering {over:.3f}; expected bias-test fails {206*pfail:.0f}/206')
report('both-stream inner', math.sqrt(1-share), math.sqrt(share))
report('data-only inner  ', math.sqrt((1-share)/share), 1.0)
