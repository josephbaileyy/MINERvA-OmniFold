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

Nothing is submitted, deposited or tagged.
