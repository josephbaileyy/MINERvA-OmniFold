# AMENDMENT A3 to FD-VF-ADDITION-DECLARATION.md: Phase 1's on-node test selection (2026-11-25)

**By** tier3-design. **Ruled by** the director on 2026-11-25 (option (a)), after codex-school's read of the Phase 1
connect script. It is for binding in FD-VF BINDING 1 with the code, A1, A2 and the two scripts.
**Amends** `FD-VF-ADDITION-DECLARATION.md` (sha256 `31662736e85f83e3772722fa9ec633ae4f8a9add2fd37c111b801f058dcfe39f`,
merged in #1334) §3, "Where and how", the bullet "the test modules pass with no skip". Nothing else changes.

## The change

On login02 in root_6_28, the connect runs this selection and requires **exactly 541 tests, no skip**:

- ten modules whole: `test_fd_vf_addition`, `test_fd_cpl_addition`, `test_fd_g_compare`, `test_fd_g_diag`,
  `test_fd_g_followup`, `test_fd_flux_boot`, `test_fd_f0_regrade`, `test_fd_g_figures`, `test_fd_deposit_candidate`,
  `test_fd_data_product`;
- `test_fd_gencmp_e.Sets`, `test_fd_gencmp_e.Stage`, `test_fd_gencmp_e.Materialize` and `test_fd_gencmp_e.Chain`.

The script's gate requires unittest's closing block to end with the rule, `Ran 541 tests in …s` and `OK` on its own
line, so a skip (`OK (skipped=N)`) or a narrowed selection stops the run (`fd/receipts-vf/p1/connect-vf-p1.sh`).

**Excluded:** only `test_fd_gencmp_e.StepCR`, all 9 of its tests.

## The reason

- **StepCR cannot run in root_6_28.** It builds ROOT fixtures with uproot, and root_6_28 has no uproot.
  - GENCMP E's rerun recorded exactly these 9 errors, each "No module named 'uproot'", and went on to its chain
    (`fd/gencmp-e/rerun1/logs/e_rerun.log`).
  - E-A2's first attempt stopped on the same 9 errors, with every other test passing
    (`FD-GENCMP-AMENDMENT-E-ADDENDUM-EA2-REPORT.md` §2).
  - E-A2's second attempt, under the director's ruling (a), left `test_fd_gencmp_e` out entirely. This amendment
    keeps the module's other 34 tests.
- **The V_F chain never reaches what StepCR tests.** StepCR exercises `fd_gencmp.py overlap --arm refined` (GENCMP's
  C-R step). From `fd_gencmp_e`, `fd_vf_addition.py` uses only three names, by
  `grep -noE '\bE\.[A-Za-z_]+' nd-unfolding/fd_vf_addition.py`:
  - `772:E.step_pins`
  - `972:E.Paths`
  - `992:E.load_chdefs`
- **StepCR passes where uproot exists.** The full `test_fd_gencmp_e`, StepCR included, passed locally in the
  317-test neighbour run at 1513e63d: `fd/receipts-vf/code/tests-1513e63d.txt` (sha256
  `2675ade6b6a9793d715babad4c2421247cda9445dbb90f4f713b707a42fda3a3`), "Ran 317 tests … OK", rc 0.
- codex-school's re-read of the connect script found no other uproot dependency or missing package in the selection.

**Declined:** running StepCR on the node in a second environment (omnifold_py310). GENCMP E's run1 ran its suite there
and got one error, a numpy-2 repr (`ValueError: could not convert string to float: 'np.float64(…)'`, "Ran 222 tests …
FAILED (errors=1)", `fd/gencmp-e/run1/logs/tests-omnifold_py310.log`). So that environment is not known to pass these
modules, and the director declined adding it on the node.
Search: git grep -l omnifold_py310 fd/ with test_fd_gencmp_e|vf_addition|cpl_addition|g_compare @ 8a7f9f7f6

**Disclosed, not changed:** the tests delete their own temporary fixtures, and the chain renames its own temporary
files into place. Both happen only to files the run created under `$BA`.

**CANNOT AUTHORIZE:** anything beyond the change above.
