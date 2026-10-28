# Binding, amendment 1: 3D, after the B2 STOP at the deploy's tests (2026-10-28)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md` (PR #423), item 3, and
[`FD-FLUX-BOOT-BINDING.md`](FD-FLUX-BOOT-BINDING.md) (PR #430), which this amends.

**Binds** [`FD-FLUX-BOOT-DECLARATION-AMENDMENT-1.md`](FD-FLUX-BOOT-DECLARATION-AMENDMENT-1.md), merged in PR #436
(after `merge_main.sh` as `aae1266a`). Its file sha256 begins `44e6a88988b3430d`.

**MEASURES:** nothing. It authorizes the declaration's deploy, its tests and its one run, as amended, at 0 node-h on a
login node.

**CANNOT AUTHORIZE:** anything `FD-FLUX-BOOT-BINDING.md` cannot authorize, and any widening of B2's 10⁻¹⁰ after the
real inputs are seen.

## 1. The bound code

**The deploy pin** is `91312bc8f22b90e90724741e6edffdb1b15f0c72`, main after PR #436.
- `B=/pscratch/sd/j/josephrb/fd-flux-boot-20261028` and `D=$B/deploy/91312bc8`. `$B` must not exist beforehand.
- `/pscratch/sd/j/josephrb/fd-flux-boot-20261027` stays untouched as the STOP's evidence.

**At the merged head `aae1266a`, the director checked:**
- `fd_flux_boot.py` `f82bd4f4` and `test_fd_flux_boot.py` `00b3ba42`, as amendment §5 declares, with the other six
  §8 files unchanged from `main`;
- the declared test modules, locally with `-B` and a TMPDIR: **Ran 207 tests, OK**.

## 2. Rulings

1. **All eight constraints of the STOP ruling are met,** as amendment §8 states.
2. **The tool's bytes changed, and that is accepted.** The STOP's cause was in the tool, not the fixture. The
   pre-amendment shape-only χ² was computed relative to f, a different float problem from Stage G's absolute-units
   one, and could not reproduce Stage G to better than about 10⁻¹⁰ (amendment §1). Every χ² now goes through Stage G's
   own `compare()`. B2's clause and tolerance are unchanged.
3. **B6 is accepted** as declared, with amendment §2.2's own statement of what it adds and what it does not.
4. **The fixture's regime** (amendment §3) is accepted. It errs toward more degenerate than the real block. The real
   block's correlation range is 0.913–0.998, not the 0.97–0.998 the STOP ruling quoted.
5. **B2 on real inputs is measured for the first time in the run.** A refusal is a STOP, unrepaired.
6. **`FD-FLUX-BOOT-BINDING.md` §2, rulings 1–7, stand.** That includes ruling 2: a paper sentence may describe only the
   percentile band, with its offset.

## 3. Conditions

`FD-FLUX-BOOT-BINDING.md` §3 applies, with:
- `<pin>` = `91312bc8…` and the new `$B`;
- "Ran 207 tests" in place of "Ran 203";
- the amended §8 digests in the deploy log;
- the readout's `controls_passed` ending with `B6`.

The report adds B2's and B6's worst values on the real inputs, and the STOP's receipts from `fd/flux-boot-report`
(`79c013ac`) with its ledger row. **Retention:** both `$B` roots stay on the pscratch list.

The steps may start once this record is on `main`.

## Not changed

- Every covariance, cell, readout and κ. G-SENS2's α results stand.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
