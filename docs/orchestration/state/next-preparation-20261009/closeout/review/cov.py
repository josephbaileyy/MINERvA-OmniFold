# Per-functional I68 coverage of T by U_e +- sigma_hat when the bank S is fixed:
# U_e - T = delta_j (fixed per functional, MC-stream realization of S) + eps_e (data stream)
# sigma_hat^2 = data + MC (exact both-stream calibration), share = data/(data+MC)
import math
from statistics import NormalDist
N=NormalDist()
share=0.3534430114159182; k=math.sqrt(share); m=math.sqrt(1-share)
z=1.0
def cov(d): return N.cdf((z-d)/k)-N.cdf((-z-d)/k)
print('cov at delta=0',cov(0))
# distribution over delta ~ N(0,m^2): fraction of functionals with coverage above / below nominal 0.6827
import random
# deterministic quadrature
xs=[i/1000 for i in range(-6000,6001)]
w=[N.pdf(x) for x in xs]; tot=sum(w)
over=sum(wi for x,wi in zip(xs,w) if cov(m*x)>0.682689492)/tot
mean=sum(wi*cov(m*x) for x,wi in zip(xs,w))/tot
print('fraction of functionals over-covering',over,'mean coverage',mean,'rms offset/sigma_hat',m)
