# D2's mu_max in LL5D's own space (package and run: D2 PASS, 2026-11-16)

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
- **atime-pre/post over the watch list:** every product at T in the null's roles, the staged S1 assembly, the
  constraint and the two null records. None may move; the bulk HPSS copy of $U is pending. The connect's own deploy
  files (the definition and the cmodel json) are not on it. LL5D's setup, made_from and cmodel_parts read them
  plainly, and they are lane-made, the same class as LL5D's deploy manifest (coverage-5b-audit blocker 1; the
  director's fix).

| file | what |
|---|---|
| `ll5d_mumax.py` | the steps: s1-control, inputs, ll5d |
| `test_ll5d_mumax.py` (+`.out.txt`) | 8 cases: the digest equals products_digest's; partial refuses; clean; a wrong digest, a different made_from and a broken removal each STOP; the director's mutant (G perturbed by 1e-9) and G from GEANT_Neutron alone each STOP on the removal control |
| `s1_control.out.txt` | the S1 reproduction |
| `connect-g2r-d2.template.sh`, `fill_connect_d2.py` | the connect (login node; RE-2-shapes rev 3's fence verbatim) and its fill from git at the package commit |

**CANNOT AUTHORIZE:** any reading, or whether the paper prints the quantification. That decision is Joseph's.

## The run (`run/`): D2 PASS

**Go:** the director's fresh "go ea87c28b 83e987b7", given after coverage-5b-audit cleared rev 2. Rev 1's blocker:
the deploy's definition and cmodel json were on the atime list.
- The connect is `connect/connect-g2r-d2.sh` (`83e987b7…`), filled at PKG 00855c17. Its stand-in is
  `connect/test_connect_d2.sh`, 10/10. The launcher is `ea87c28b…`: 9d39a6bc plus the `d2)` arm
  (`connect/launch-g2r-vs-9d39a6bc.diff.txt`).
- **Launch** (`run/launcher/launch-stdout.txt`): DIGEST_MATCH; launched rc 0 at 09:43:54Z; DONE after 5 polls.
- **Connect** (`run/node/logs/connect.log.txt`), login02, 09:43:52–09:45:04Z:
  - fence clear; the deploy at PKG, porcelain 0 before and after; the 3 code shas OK;
  - python 3.11.14, numpy 1.26.4; the null records OK;
  - 458 declared inputs (`run/node/inputs.txt`). `atime: 458 declared inputs, moved 0`: atime-pre equals atime-post
    byte for byte;
  - mumax rc 0, 5.76 s; `D2 PASS`.
- **The record** is `run/node/mumax.json` (`422db056…`). `run/d2_report.out.txt` (from `d2_report.py`) prints it per
  truth beside geant_full.json's D2 values, as recorded:
  - the controls: the products equal the null's (227 per truth), made_from matches, and the removal deviation is
    7.49e-96 against limits of about 4.5e-92;
  - G has rank 2;
  - mu_max for C_T (all), the primary: g18 0.06543743477027143 (1/(1-mu) 1.0700193194172998) and ar23
    0.08611205096408803 (1.0942260493257738);
  - mu_max for C_T^-, the secondary: g18 0.06544993734286615 and ar23 0.09851537916779254;
  - beside D2's 0.081346592967004 (C_total at the data) and 0.04097223733043594 (reported).
- `run/node/`: the 10 records fetched O_NOATIME by `run/node/fetch_d2.py`. They equal `run/node/NODE-SHA256.txt`.

## Left for removal by Joseph

`/pscratch/sd/j/josephrb/cov2d-mumax-20261116/` (the deploy clone and the run's files), after this receipt merges.
