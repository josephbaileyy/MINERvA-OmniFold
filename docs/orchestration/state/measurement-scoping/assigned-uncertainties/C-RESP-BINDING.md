# Binding: the C_resp build on R00–R15 (2026-10-26)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261026-joseph-abstract-and-cresp-build.md` item 2.

**Binds** [`C-RESP-SPEC.md`](C-RESP-SPEC.md), merged in PR #365. Its file sha256 begins `d0d4b9f3ad9e70e1`.

**MEASURES:** nothing. It authorizes the one login-node run of the spec's §6.2, at 0 node-h.

**CANNOT AUTHORIZE:**
- adopting C_resp into the reported total, which is Joseph's decision from its readout;
- Stage G's run;
- any claim, Slurm job, GPU use or write to CFS.

## 1. The bound code

**The code pin** is `973142a7fc150f2ceb9fd3530297ec1ddcbd0dc3`, as in the spec's §6.1. It is an ancestor of main.

**Digests.** At that pin, and unchanged on main at `ddf16f10`, the director checked:

| file | sha256 begins |
|---|---|
| `build_cresp.py` | `fe1aec8b` |
| `test_build_cresp.py` | `ea0dd6db` |
| `s1_assemble.py` | `b157250a` |
| `s5p_stage1_inspect.py` | `26569afc` |

**Tests.** The director ran `test_build_cresp` locally at the spec's PR head: 22 tests, OK.

## 2. Conditions

1. **The run.** It is the §6.2 argv, exactly.
   - `$R=/pscratch/sd/j/josephrb/cresp-20261026` must not exist beforehand.
   - Porcelain is 0 before and after.
   - Both test modules must pass in the clone.
2. **Once.** Any test failure, refusal or non-zero exit is a STOP, reported unrepaired. Nothing is retried.
3. **The readout,** in the report's PR:
   - `cresp.json`, committed at `cresp/cresp.json`;
   - a short `CRESP-REPORT.md` giving per-species and total relative σ per cell (median, min and max), rank and
     trace shares, and C_total_resp's per-cell σ beside C_total's;
   - the npz's sha256. The npz stays on pscratch.

   **No data-against-generator quantity is computed.** The labels say "sensitivity variant, not adopted".
4. **After the report,** the director brings the readout to Joseph for the adoption decision. Stage G's binding then
   names `cresp.npz`'s digest.

## Not changed

- S1's covariance, R00–R15, κ = 1, F0 and the route decision.
