# BINDING 1: RSN, the referee sensitivity analyses (G6, SM, WR, WU, TR) (director, 2026-11-12)

**Binds** [`RSN-DECLARATION.md`](RSN-DECLARATION.md) rev 3, sha256 `c2a55cbc26c7d97e…`, and its §7 code, as merged
in PR #1077 at **M_RSN = `af7112989417f180e846573c31d101e44e6b02f9`**. The audited head is `5fe578e4` (code and
declaration `0336ba64`). The director re-hashed every §7 file on main after the merge, and each equals its §7 digest:
`rsn_prep.py` `7b0fc567…`, `rsn_unfold.py` `5796bb60…`, `rsn_cmodel.py` `ab632921…`, `rsn_regrade.py` `661608d8…`,
`rsn_read.py` `4dd37197…`, `sbatch_rsn.sh` `f889a0cf…`, `rsn_tasks.tsv` `354bd16d…`, `test_rsn.py` `887dbccd…`,
`rsn_mutation.py` `8075fe8c…`.

**Under:**
- the recheck referee round's 3.1, 3.2 and 1.2, and the fresh round's F1.1 and F1.2(ii)
  (`state/2d-closeout/stageF/methods/methods-short-20261109/RESPONSE.md`);
- Joseph's instruction of 2026-11-11 to run new analyses that are not too costly and report the cost of the rest.

## What the director checked

- **coverage-5b-audit's GO** at `5fe578e4`, after two majors at rev 2 (`fd536748`):
  - R1 is closed. Under G6, P1 can change through any grade that depends on a GiBUU row, W3 and A7_nuwro included.
    The outcome rows say so. C-INV checks the GENIE+MEC and NuWro rows bitwise, and all three invariant fields.
  - R2 is closed. WR's verdict is scoped to pvl's noise-free signal-only closures. A "material" WR licenses only a
    stated sensitivity there. Attribution to the approximation stays with T3's MW reading.
  - The audit's reruns at `5fe578e4` gave 52 tests OK and 109 of 109 mutants killed, line-identical to
    `rev3/mutation.txt`.
- **The NC-R gate** (§6 step 3) reproduces F1's 22 records, control 7's verdict, χ² and p, and the group and
  by-family counts, at 0 node-h on a login node. Every job refuses without its PASS.
- **The HPSS archive** of §6 step 2 is done: pv-ladder's `prep/` and `products/` and `cpl_block.npz`, 67 files,
  every member re-read from HPSS equal to its pin (PR #1085, `hpss/run-20261112/`).

## Rulings

1. **The design and code are bound as declared at M_RSN.**
2. **The price:** projected 0.78 node-h, with a hard maximum of 1.01 at the three time limits and a **cap of 1.25
   CPU node-h**. A stopped job is reported to the director and is not resubmitted without the director's go.
3. **Order:** as §6.
   - **Connect 1** (clone at the pin, the prep, the NC-R gate): its shas come to the director first.
   - **The `rsn_` family:** the director announces it to every fenced lane before `fence.txt` is written and J1 is
     submitted. A queued or running fenced prefix STOPs the launcher.
   - **J2 (or J2n) and J3:** only after J1's NC PASS and the committed gate files.
4. **The audit's low r1:** `sbatch_rsn.sh` checks `nc_r.json`'s schema and PASS but not its code sha. It is not
   fixed in code. At connect 1, the cluster lane prints `nc_r.json`'s recorded code sha256 beside the deployed
   `rsn_regrade.py`'s, and the two must be equal before `fence.txt` is written. **r2** (TR's scope has no mutant)
   goes on the follow-up list.
5. **Reserved for Joseph:** any change of paper wording these readings could support, after a PRD-referee read.
6. **Not declared here:** F1.2(i), the event-loop re-dump with truth quantities outside the five. It is approved in
   principle as its own lane after this binding: a pilot on 1A first, and a cap of 2.5 node-h, pilot included.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the bound design, code digests, price and order.
- **Not citable for:** any reading. Nothing has run.

Nothing is submitted, deposited or tagged.
