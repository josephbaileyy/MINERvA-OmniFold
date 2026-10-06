# W2b pre-submission check of C1–C3 (publication lane, 2026-10-06)

**Target:** `study/w2-recoil-response-20261006` at `91401a0f`. No W2b job had been submitted when this check was
made.

**Required by:** `REVIEW-20261006-w2a-independent.md`.

| change | evidence checked by this lane | result |
|---|---|---|
| C1: per-playlist limits; Σ reservation + spend ≤ 8.0 | `publication/w2/w2b.py:27–52`: `CEILING = 8.0`; `EVLOOP_LIMIT_H` 1M 6 h, 1F/1D/1G 5 h, others 4 h; the reservation is limit × billing / 256; the in-flight jobs are counted. The lane's sum: event loops 6.2109 + spend 0.0985 = 6.3094; whole-plan worst case 7.4110. The refusal control returns rc 3. | **PASS** |
| C2: refuse dump modes when δ is set | `publication/w2/checks/C2-refusal-test.txt`: 3 clean cases rc 0; 12 cases with UNIVERSES, POINTCLOUD, empty-value or both × rr0/rr1/rrzero all rc 6 | **PASS** |
| C3: design copies differ only in `data_central` | This lane recomputed the diff independently, leaf by leaf, against the frozen `design.json` (`404446eb`): rr0, rr1 and rrzero each have 131 leaves, and the only differing leaf is `/data_central` | **PASS** |

**Noted deviation, accepted:** each step runs from the deploy that produced it in s5p (dump `c1cba7bf`, unfold
`4e4b4f56`, evaluation `e9372b75`), cloned fresh into the W2 namespace. A single deploy would not reproduce the
frozen unfold code, because `s5p_truths.py` changed between those deploys.

**Gate statement:**
- every precondition of Joseph's item 4 holds (the review clears the implementation; the cost fits; D2 is complete);
- C1–C3 pass.

W2b may be submitted. A failed control or stopping gate stops the study and authorizes nothing further.
