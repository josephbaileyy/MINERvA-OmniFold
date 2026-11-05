# REF-G1 BINDING 2, step two: the 16-cell binned head-to-head's code (director, 2026-11-05)

**Binds** the code of PR #781 as merged at:

**M = `609d8f24ea2229fa4b3540627aa8c31acfcc0a54`** (PR head `eb265965`)

**Under** [`REF-G1-BINDING-1.md`](REF-G1-BINDING-1.md) (the design, `1ea76a3b…`, at `ddbc43e4`) and
`DECISION-20261104-joseph-g1-r1-calibrated-bars.md`.

| file | blob at M |
|---|---|
| `nd-unfolding/ref_g1/ref_g1.py` | `cfe089d466fa8cb1926d6665fbae65b5d269eaeb` |
| `nd-unfolding/ref_g1/ref_g1_read.py` | `e49ab974598ea3d15663f61da538fad3c9c8f12a` |
| `nd-unfolding/ref_g1/config.json` | `2a14b22f169b9a5e616a5498dcba79c682d6766b` |
| `nd-unfolding/ref_g1/test_ref_g1.py` | `c68198177807a39d41114c8286edd3d23bc6ab18` |
| `nd-unfolding/ref_g1/ref_g1_mutation.py` | `4ad3b92570b2196737df57944f94300a90d9ecc5` |

## What the director checked

- **The audit** (coverage-5b-audit, #781). The statistics are right: null_t follows the decision's item 2, the
  F-law self-check is sound, and the pairing, products digest and order guard are correct.
  - C1 (a failed control did not stop the run), C2 (foreign bars were accepted) and C3 (a G-draw-failed unit counted
    as done) were upheld by the director, fixed, and closed at `eb265965`.
  - The auditor ran 30 tests and killed each new mutant by its named test.
- **The receipt** (`fd/receipts-ref-g1/code/`): 30 tests; MUTATION CHECK PASS, with 26 mutations killed and 2
  expected survivors, jitter-skip and the jitter seed, each with its proof.
- **The rc-5 membership refusal** cannot be reached by real edge-safe jitter. It is tested through a counted
  substitution, and the docstrings say so.
- **The cited lines, at M:**
  - the declaration's within-cell spreading row at `REF-G1-DECLARATION.md:49`;
  - `did.share_matrix` at `next-preparation-20261009/d-id/did.py:252-258`;
  - `ibu1.py:179`, where u_fine comes from the unit's own half truth weights, and `ibu1.py:195`, which calls
    `share_matrix`.

## Director's correction to the declaration's wording

`REF-G1-DECLARATION.md:49` reads "`did.share_matrix` on the nominal truth". The code follows IBU-1: `ibu1.py:179`
builds `u_fine` from each unit's own MC truth weights, and `:195` spreads with it. The declaration's own rule makes the
truth grid the only change from IBU-1, and G-IBU1 requires IBU-1's data unit to reproduce bitwise. So **the spreading
uses each unit's own MC truth**: the replica's Poisson-weighted truth, the universe's weights, and the vertex's
reweighted prior. "Nominal truth" was a misstatement. The declaration's text stays as bound, and this correction
governs.

## Rulings

1. **Step two is bound:** the code at M, with the blobs above.
2. **The environment.**
   - The gibu1 unit runs under `/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3`, called by that exact path,
     with `sys.version` equal to IBU-1's recorded one (`ibu1/receipts/inventory/D_N.jsonl:1` at `ddbc43e4`).
   - The guard refuses anything else, and it fails closed. If a conda update changes it, the unit stops and comes to
     the director; the guard is not widened.
   - IBU-1's receipts record no numpy or scipy version, so gibu1 records its own and does not require one.
3. **The cluster lane is `limitation-resolver`.**
   - **First:** time one universe unit on its own, at the start of a connect whose sha256 comes to the director.
   - **Then:** a priced connect for the batch, also to the director first.
   - A projection above the **5.0 CPU node-h** cap stops and reports. It does not shrink the set.
   - Every `--time` is written `HH:MM:SS`, and scontrol's TimeLimit is checked after submission, with a cancel on a
     mismatch.
   - Every deploy is a fresh clean clone at M, run with `-B`. Report its porcelain, with `--ignored`, before and after.
4. **The order.** `bars.json` and its sha are committed before the central Δ is formed (ruling 5 of binding 1). The
   reader refuses otherwise.
5. **The calendar.** The run, including its read, finishes before **2026-12-18T15:04Z**, when D_N.npz is exposed.
   Otherwise D_N's HPSS copy is verified first.
6. **A STOP** of any control comes to the director unrepaired.

Nothing is submitted, deposited or tagged.
