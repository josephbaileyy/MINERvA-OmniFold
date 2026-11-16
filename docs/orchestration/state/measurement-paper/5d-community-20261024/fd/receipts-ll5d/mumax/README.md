# D2's mu_max in LL5D's own space (package; DRAFT for the director and coverage-5b-audit)

The director's design rulings of 2026-11-16 close lrows-g README:121-127's "not covered". Per truth (G18, AR23):
- G = band:GEANT_Neutron + band:GEANT_Proton, as LL5D rebuilt them at T from that truth's own detector-universe
  unfolds;
- M = C_T (all), the primary, which is the matrix graded with the two bands, and C_T^- (leave-out-MEC), the secondary;
- mu_max is the largest generalized eigenvalue of (G, M), with chi2(M - G)/chi2(M) in [1, 1/(1 - mu_max)]. The
  record also gives the top three generalized eigenvalues, the direction across R00-R15 and the eigenmode shares.

`ll5d_mumax.py` reads only through LL5D's own functions (ll5d_b.setup and remade, unchanged since M 4231b14d), with
products read O_NOATIME. Its arithmetic is lrows-g's own geant_full.summarize (45fc4bcf, imported unchanged), on
fractional matrices (divided by X_T X_T^T).

**Controls:**
- **S1 reproduction:** local, committed in `s1_control.out.txt`. The same mumax_record on S1's committed data blocks
  reproduces geant_full.json's 0.081346592967004 (C_total) and 0.04097223733043594 (reported) bit for bit.
- **The products and made_from are the null's.** The script reads LL5D's committed null records; the connect checks
  their sha256 first. It requires mc.made_from to equal each record's made_from. It also requires the products'
  digest, built as ll5d_b.products_digest builds it but read O_NOATIME, to equal the record's products_sha256.
- **The removal control on the G used:** max |C_T(minus2) - (C_T(all) - G)| <= 1e-12 max |C_T(all)|, together with
  ll5d_b.removal_control itself.
- **atime-pre/post over the declared inputs:** every product at T in the null's roles, the staged S1 assembly, the
  definition, the cmodel json, the constraint and the two null records. None may move; the bulk HPSS copy of $U is
  pending.

| file | what |
|---|---|
| `ll5d_mumax.py` | the steps: s1-control, inputs, ll5d |
| `test_ll5d_mumax.py` (+`.out.txt`) | 8 cases: the digest equals products_digest's; partial refuses; clean; a wrong digest, a different made_from and a broken removal each STOP; the director's mutant (G perturbed by 1e-9) and G from GEANT_Neutron alone each STOP on the removal control |
| `s1_control.out.txt` | the S1 reproduction |
| `connect-g2r-d2.template.sh`, `fill_connect_d2.py` | the connect (login node; RE-2-shapes rev 3's fence verbatim) and its fill from git at the package commit |

**CANNOT AUTHORIZE:** any reading, or whether the paper prints the quantification. That decision is Joseph's.
