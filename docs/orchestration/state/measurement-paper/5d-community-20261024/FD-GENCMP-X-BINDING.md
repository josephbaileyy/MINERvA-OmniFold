# BINDING: GENCMP X, the 16-cell–2D cross-covariance and the quadrant test (director, 2026-11-02)

**Binds** [`FD-GENCMP-X-DECLARATION.md`](FD-GENCMP-X-DECLARATION.md) and `fd/xcov/INPUTS.sha256`, as merged in PR
#666 at **M = `260e299b37e2a82deaeef165b79d0757115e8887`** (PR head `26dd124f88d115875de376f473eb5fb9e628d22b`). It cites
`fd/gencmp-e/INPUTS.sha256` at `6cd095d6`, as the X declaration requires.

**Under:**
- `DECISION-20261101-joseph-gencmp-paper-adoption.md`, item 5, and its correction (#652);
- the director's four rulings on the scoping (#653 §9), applied in the declaration.

## The code bound (git blob digests at M)

| blob | path |
|---|---|
| `244ff110727fe769eb872723b42970a76625df8f` | `nd-unfolding/fd_xcov.py` |
| `60184cc1072286b176119eea7db350e8016f7374` | `nd-unfolding/fd_xcov_steps.py` |
| `1b0d33c596dd8239069ae8399aaa6a1a88d0c7fe` | `nd-unfolding/tests/test_fd_xcov.py` |
| `afec433069781af3eab9af86464e878140097cef` | `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/xcov/INPUTS.sha256` |
| `e57a3150e0420b61732b0648094f500cc41dec02` | `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/xcov/receipts/x_v1.sh` |
| `824ec76611f4705160d296ccfb2f24f55c091edf` | `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/xcov/receipts/x_boot.sh` |

## What the director checked

- **The digests.** The six above match the lane's list. The head's fix touched only `MANIFEST-overrides.tsv` and
  `MANIFEST.tsv`.
- **The tests.** At `1605dc45` (code identical to M), `python3 -B -m pytest` ran `test_fd_xcov.py`,
  `test_fd_gencmp.py` and `test_fd_gencmp_e.py` with their own TMPDIR: 141 passed, 1 skipped.
- **The review.** A fresh Sonnet subagent's audit is verbatim in `FD-GENCMP-X-REVIEW-{PROMPT,ANSWER}.txt`. Its blocker
  B1 (K1's np.allclose atol on entries near 1e-80) is fixed and tested.
- **The rule (§4) applies the rulings:**
  - C₂D = Q_R + C_model,2D, vertex-paired;
  - route B;
  - "agree" iff p ≥ 0.05 and every |z| ≤ 2.50;
  - the C_PL pair constructed, with z at 0 printed.
- **The outcomes (§5).** The paper text for each is fixed in advance, and "differ" has no text until the director and
  Joseph rule.

## Rulings

1. **V0, V1 (probe, then full), BOOT and K are bound as declared (§2, §6).** The caps are V1 0.25 + 1.75 and BOOT 3.0,
   so **5.0 node-h**. The reservation is the cap.
   - V0 and K run on a login node at 0 node-h.
   - V0, V1 and K run in omnifold_py310, and BOOT in root_6_28, as §6 states.
2. **Order.** B0 runs alone first and gates the mapped lanes. K runs once, after BOOT has ended or was never due. A
   stop is final under this binding.
3. **Stated limits, accepted as written in §8.**
   - V1 checks signal-row weights only. The denominator and background weights are a limit, and the paper says
     "signal weights".
   - The C_PL pair is constructed.
   - Unpaired blocks enter V_d in full.
4. **The result goes to Joseph with C-R's numbers** (#662 §3.2, QA's changed reading included). `paper_body.tex:119`
   is not touched before he rules.
5. **Connects:**
   - regular CPU only, every job under 12 h;
   - a fresh clone detached at M, with empty porcelain before and after;
   - writes only under `$R`, and nothing to CFS;
   - O_NOATIME for every pscratch or CFS original, with a moved atime reported and not restored;
   - the HPSS copy after `hpssquota`, with an explicit list, `hashverify` and retrieval.
6. **The report** gives every step's controls and readouts, the §5 outcome, its cost from `sacct`, and every
   deviation unprompted.

## Addendum X-A1 (director, 2026-11-02)

**The defect.** V0's draw check failed on 0 of 100 replicas. The cause was in the check itself.
- It required a background draw-sum line in RE-2's replica logs.
- RE-2's negweight-refined mode prints that line only in the purity branch (`re2_driver.py:2123`), so the line cannot
  exist in this mode.
- The background stream is recorded instead in each replica's `p1Streams` provenance record
  (`re2_driver.py:2221-2230`).
- Every other V0 leg passed:
  - the counts exactly;
  - the MC rows, apart from the 2,801 sentinels;
  - the data and background joins, complete with 0 ambiguous rows;
  - the data and MC draw sums.
- Nothing K-dependent had been computed.

**The director's ruling (by message).** The defect is in the control, not in the pairing, so this is a repair and not a
route choice. It is bound before it runs.

**Binds** addendum X-A1 as merged in PR #671 at **M′ = `f14119b11ccd151f910163455e575196be38b96a`** (PR head `62b1a523ee197d200a17a89b9e0266dc6eeb7b1d`):
- **What changes.** The draw check's background leg reads `bootstrap_seed`, `seed_offsets.bkg`, `n.bkg` and `sum.bkg`
  from each replica's pinned `xsec.root` `p1Streams` record, read through `Inputs.bytes`: O_NOATIME, and checked
  against `fd/xcov/INPUTS.sha256`, which is unchanged.
- **What stays.** The data and MC legs are unchanged.
- **Plumbing.** V0 writes to `$R/v0-a1/`, and BOOT runs from `$R/deploy-a1` at M′.
- **The blobs at M′:**
  - `nd-unfolding/fd_xcov.py` `e708f3cffcfd62fe3eb5f38b2681ec467bee516f`;
  - `nd-unfolding/fd_xcov_steps.py` `aedfa0b831279193e37d761607c7acaeaefb50cc`;
  - `nd-unfolding/tests/test_fd_xcov.py` `033831e881457506b62452920d69376bf8103088`;
  - `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/xcov/receipts/x_boot.sh` `084fe2331f48af2843198df5047cd1c233608df7`;
  plus the fixtures and `x_a1_mutants.tsv` as merged. `x_v1.sh` is unchanged.

**What the director checked.**
- The diff: only the background leg and the run-directory plumbing change.
- The tests, run locally at the head: `test_fd_xcov.py`, `test_fd_gencmp.py` and `test_fd_gencmp_e.py` gave 147 passed,
  1 skipped.
  - The new `BkgLeg` tests pass on replica 1's real record.
  - They fail on a wrong seed offset, n ± 1, sum ± 1, a wrong bootstrap seed, a missing key, the wrong replica, a short
    stream, a wrong seed, and an absent record.
  - The three guard mutants are caught (`x_a1_mutants.tsv`).

**Rulings.**
1. **V0-A1 runs** on a login node, in omnifold_py310, from a fresh clone `$R/deploy-a1` at M′, into `$R/v0-a1/`.
   - The first `$R/v0/v0.json` stays untouched as the record.
   - **Route B continues only if V0-A1 passes in full.** Otherwise route A stands.
2. **V1 full (job 60679146)** was submitted from `$R/deploy` at M under the original binding, after its probe passed.
   That is accepted: V1 does not read V0, and its code is unchanged.
3. **BOOT and K** run only after V0-A1's result. BOOT runs from `$R/deploy-a1`.
4. **The report** gives both V0 runs. Its deviations are:
   - the four-log diagnostic;
   - the fixture read;
   - the /dev/shm writes.

## Addendum X-A2 (director, 2026-11-02)

**The stop.** The full V1 (job 60679146) failed after 4:14 with "EtaNCEL:0 wt: 22 files carry its digest". The cause
was `weight_files`, which required exactly one pinned file per digest. Identical digests are byte-identical files, so
the rule should have been "at least one".
- The match histogram over 350 lookups is {1: 322, 2: 4, 8: 8, 22: 16}.
- The multi-match classes span:
  - the NC knobs: EtaNCEL, MaNCEL, NormNCRES, NormDISCC;
  - GEANT_Neutron, GEANT_Pion and GEANT_Proton;
  - MinosEfficiency;
  - Rvn1pi.

**The director's rulings (by message).**
- **The lookup rule.** Take the sorted-first file and record n_matches. Stop on zero matches.
- **Before resubmission, a full lookup sweep.** Every lookup is checked once on its own, with no weight array read.
- **K's own-side controls, dry-run first** on the real products, with no cross quantity computed.
- **The 2D NormDISCC block failed K1 on cancellation noise.** Its block is 1.1e-25 of max|C2q|. So **explicit null
  bands** take the place of a scale floor:
  - a band is null on a side when its blocks are below 1e-12 (PD_REL) of that side's max|C_side|;
  - a band null on both sides is asserted null;
  - a band null on one side only fails;
  - every other band keeps `same_block` at 1e-10, plus the zero rule.

**Binds** addendum X-A2 as merged in PR #681 at **M‴ = `b2e2d23263d379e8d5affc1f27aaea18175bb66c`** (PR head `b3b8479d651c287105a0c106b3526d1247fc9f46`).
The blobs at M‴:
  - `nd-unfolding/fd_xcov.py` `2bef2618a5fa43a8414b3ebe1ce646d24a21ca99`;
  - `nd-unfolding/fd_xcov_steps.py` `ed21d590b1627f181ce73607a05acacdb8382cbc`;
  - `nd-unfolding/tests/test_fd_xcov.py` `050691ee13ada48ad3d0161e2c6c9091523f32a6`;
  - `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/xcov/receipts/x_v1.sh` `8f6995d610a165aecd575767f5847a40cf07482b`;
  - `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/xcov/receipts/x_boot.sh` `084fe2331f48af2843198df5047cd1c233608df7`;

`x_v1.sh`'s only change moves its `cd` to `$R/deploy-a2`.

**What the director checked.**
- **The diff:** the lookup rule, the dry modes (`v1 --dry`, `k --own-only`), the null rule and the run-directory
  plumbing.
- **The tests.** `test_fd_xcov.py`, `test_fd_gencmp.py` and `test_fd_gencmp_e.py` gave 154 passed and 1 skipped
  locally at the head.
- **The receipts.**
  - The V1 dry sweep: 175 universes, 350 lookups, 0 zero-match, 0 failing.
  - The K own-side dry run at `d670e9a5`: 102/102 PASS. NormDISCC is the only null band, on both sides.
  - The null-rule mutants: 7 of 7 caught.
- **The lane's extension of the null rule to the 5 lateral bands is accepted.** No verdict changes.

**Rulings.**
1. **The order:** a fresh clone at M‴ into `$R/deploy-a2`, then the full V1 into `v1-a2`, then K.
2. **The cost.** X stands at 3.064 of 5.0 node-h. The V1 rerun is ≤ 1.75, so the worst case is ≤ 4.81.
3. **K's stop is final, as bound.** The report gives every V1 run, every dry run and the null-band list.

Nothing is submitted, deposited or tagged.
