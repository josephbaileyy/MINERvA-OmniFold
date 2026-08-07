# Repo-wide sweep for gates that cannot fail: one new instance, and an honest false-positive rate

**Date:** 2026-08-07 · **Tool:** `docs/orchestration/audit_gates_that_cannot_fail.py` (self-power-tested)
· **Ledger:** BEN-070 · **Commissioned by** Joseph, 2026-08-07: *"five-plus instances across two lanes in
one day … makes it systemic rather than local"*, and a repo-wide sweep is *"likely higher-yield right now
than either lane's current queue."*

## 1. The new instance: `p4_lib.py:219` — a non-negativity check 55 orders too loose

    require(np.all(np.isfinite(d)) and np.all(d >= -1e-30), "non-finite/negative diagonal")

Measured on the real product `products/pet/bkgsub/pet_cstat_bkgsub_5d.npz`:

    diagonal   median 3.867e-86     min 5.510e-102     max 8.128e-79
    the -1e-30 floor is 2.586e+55x LARGER than the diagonal median
    a negative variance of -1e-40 -- itself 2.6e+45x the median magnitude -- PASSES

**So this check cannot detect any physically possible negative variance.** It is a gate that cannot fail.

What makes it a clean example rather than an oversight: the *same function* validates symmetry and PSD
**relatively** and correctly —

    denom = max(1e-300, np.max(np.abs(C)))          # scale-aware, with a div-by-zero floor
    asym  = np.max(np.abs(C - C.T)) / denom
    require(ev[0] >= -psd_atol_ratio * abs(ev[-1])) # relative to the largest eigenvalue

— so the author plainly knew the idiom, applied it twice, and then used an absolute floor for the third
check. That is the signature of this whole defect family: not ignorance, but one guard written in different
units from its neighbours.

Present in **two** places, one of them shared: `nd-unfolding/p4_lib.py:219` (the library) and
`nd-unfolding/p4_validate_active_lateral_fps.py:70` (a caller that re-implements the same expression).

**Not fixed by me.** `p4_lib.py` is the P4/GBDT lane's shared library and that session is actively working
in it; a concurrent edit there is the lane violation CLAUDE.md warns about. Handed over rather than
touched. The fix is one character class: `-1e-30` → `-psd_atol_ratio * abs(ev[-1])`, or a relative floor on
`max(abs(d))`.

## 2. Also confirmed still live: BEN-046's non-emptiness gate

    nd-unfolding/run_p4_standard.sh:41    if [[ -z "${P4_VERIFIER_PASS}" ]]; then

The GBDT lane filed this as BEN-046 and renumbered it off my 044, but the **code is still in the tree on
`main`** — their fix is on `worktree-gbdt-closeout` (`329d230` touches only the ledger prose). Worth
saying because the ledger row reads as resolved and the gate is not.

## 3. The honest scorecard, including what the sweep did NOT find

624 files, 3 DEFECT and 22 REVIEW after tightening. Triaged by hand:

| hit | verdict |
|---|---|
| `p4_lib.py:219` + `p4_validate_active_lateral_fps.py:70` | **REAL, new** (§1) |
| `run_p4_standard.sh:41` | **REAL, known** as BEN-046, still live on main (§2) |
| `test_cstat_100rep_gates.py:81,93` | false positive — my own power test *deliberately* reconstructs the old bad tolerance |
| `unfold_nd_omnifold_unbinned.py:754` | false positive — `max(n_td,1)` is a div-by-zero guard inside a display f-string, not a tolerance |
| the remaining ~20 REVIEW | false positives — `1e-12 * lmax`, `_relmax(...) < 1e-12`, `abs(...)/total < 1e-12` are all already relative |

**One new instance in 624 files is the result, and it deserves stating both ways.** Either the repo is not
riddled with this defect class and the five-in-one-day cluster was concentrated in newly-written code — which
is plausible, since BEN-043/044/046 all landed in code written in the last two days — or my detectors are
too narrow to find the older ones. Both readings are consistent with the evidence and I am not choosing
between them on one sweep. What would discriminate: detectors for the classes I could **not** mechanise
(below).

## 4. The auditor caught three of its own bugs, which is the point of building it as a tool

1. **Two detectors were silent on their own known instances.** `\btol\b` cannot match inside `psd_tol` and
   `\bPASS\b` cannot match inside `P4_VERIFIER_PASS`, because `_` is a word character. The power test
   refused to report the sweep until both fired.
2. **The first sweep reported "0 hits" because `--root` resolved to `docs/`** — two `dirname`s from
   `docs/orchestration/`, not three. A clean bill of health from a check that examined nothing, i.e. the
   exact defect the tool hunts. There is now a `--min-files` floor (default 200) that fails closed, the
   same idiom as `SHELL_PIN_FLOOR` and `_LAUNCH_CODE_FLOOR`.
3. **Mention-vs-use swamped the first real sweep.** The loudest hits were the ledger prose and the
   regression tests that exist *because* of these defects. `strip_noncode()` blanks comments and
   docstrings while preserving line numbers — the same fix `_executable_lines()` needed in
   `test_pet_fullevent_nominal_launcher.py` earlier the same day.

## 5. What I could not mechanise, and why that bounds the sweep

Three of the historical instances resist static detection, so the sweep's silence is not evidence about
them:

- **BEN-032 / BEN-025 (wrong population).** Whether a check runs over rows that *can* exhibit the defect is
  a runtime property of the data, not a syntactic one.
- **BEN-040 (never returned PASS on real input).** Detecting this needs execution history — "has this
  fail-closed path ever returned true?" — which is a coverage question, not a grep. This is the highest-value
  gap: a coverage harness that records which guards have ever passed *and* ever failed on real inputs would
  find the whole family at once.
- **BEN-042 (normalised vs absolute comparison across documents).** The two quantities live in different
  files with different weightings; nothing local reveals the mismatch.

Consistent with what this campaign has already learned about coverage sweeps outperforming code review:
the mechanical sweep found one instance, and the *uninstrumented* question — which guards have never been
observed to fire in either direction — is where the rest of the family probably lives.

## 6. Convention, so the collisions stop

Two BEN id collisions in one day (041, 044) because both lanes fetch, both see the same highest id, and both
increment. Per Joseph, 2026-08-07: **this lane takes ids from 070+, the GBDT lane from 060+.** This finding
is BEN-070.
