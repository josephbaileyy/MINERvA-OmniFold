# FINDING 2026-08-14 — the only test path to the real object was a `skipTest`

**BEN-185.** Lane D (verifier), from the `OI-22` verification. Full adjudication:
`VERDICTS-20260811-session-D.md` §V51.

## The measurement

`OI-22` asked whether the alignment / schema-parity / no-truth-leakage tests a contract reports passing
actually run **against the object that will be published**. Measured at `866cec4`:

```
$ python3 -m pytest nd-unfolding/tests/test_fullevent_fps.py \
                    nd-unfolding/tests/test_fullevent_schema.py -q
61 passed in 4.09s
```

Every one of those 61 runs against `np.random.default_rng` sources written into `tempfile` dirs. The
publication input is
`/pscratch/…/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz` (9.897 GB), and it is **absent from
the checkout** — the directory holds only its 6,943-byte receipt.

**Two places in the test tree name a production NPZ and neither reads one:**

1. A **string in a config dict** (`test_fullevent_fps.py:429`), handed to a function that validates a
   dictionary. The neighbouring tests swap the filename for a wrong one and assert `ValueError`. That is
   filename-matching logic; no file is opened.
2. **A `skipTest`** (`test_pet_fullevent_nominal_launcher.py:409`):

```
SKIPPED [1] .../test_pet_fullevent_nominal_launcher.py:409: bound Gate-2 target NPZ not present
39 passed, 1 skipped in 0.72s
```

## The mechanism worth carrying forward

**A conditionally-skipped test is an absent test that reports inside a passing suite.** `39 passed,
1 skipped` and `40 passed` read almost identically at a glance, and neither says *the one test that
touches the real object did not run.* The skip reason is honest, printed, and requires `-rs` to see at
all — without that flag the run shows a bare `s` in a wall of dots.

The guard is the correct construct: the file genuinely is not there, and failing would be wrong. **The
defect is that nothing anywhere counts how many properties are proved on the real object versus a
fixture**, so the suite's green is read as covering both and covers one.

> **Check:** for any test whose subject is a *specific* production artifact, ask what it does when the
> artifact is missing — and then ask where that answer is reported. A skip is a coverage hole with a
> timestamp; it belongs in the coverage claim, not only in `-rs` output. If a contract says "these tests
> pass," the honest form names the object: *"pass on fixture, not run against the publication input."*

Related in shape but distinct: `BEN-149` is a **name** that claims a check nobody performs; this is a
**test** that would perform the check and silently does not. Both leave a reader with the impression of
coverage; the first has no execution, the second has execution against the wrong object — which is
`BEN-183`, the right command against the wrong object, arriving from the opposite direction.

## What was actually proved, and where the genuine gap is

Object aside, the fixture-level coverage is better than the suite's reputation and worse in exactly one
place:

- **schema parity** — proved. **no-truth-leakage** — proved, and it carries a working positive control
  (`test_leakage_detector_catches_truth_injection` makes the detector fire). **read-through** — proved.
- **Event-by-event alignment — not proved on any object**, and the best test bearing on it declares its
  own ceiling: after correctly explaining why it permutes rather than shifts a z-scored column, its
  docstring says *"the only thing it can detect is whether the per-row values reach the output at all."*
  **Sensitivity is not alignment** — a loader pairing `muon` row *i* with `cloud` row *j* also changes
  the output under permutation.

`FULL_EVENT_FEATURE_CONTRACT.md:215` says so too: *"row-count alignment is enforced; a full
event-by-event order proof … is a P5B hardening item."* **The contract, the tests, and this audit all
agree.** What was missing was not knowledge of the gap — it was that nothing made the gap visible from
the passing-suite side.

## Named interest

The two-tier remedy in §V51 splits cheap-numpy work from expensive-ROOT work, and a verifier who
proposes a decomposition has an incentive to make the cheap half look sufficient. **It is not** — the
cheap half closes leakage and schema parity on the real object and leaves alignment, the only property
unproved anywhere, entirely to the expensive half.
