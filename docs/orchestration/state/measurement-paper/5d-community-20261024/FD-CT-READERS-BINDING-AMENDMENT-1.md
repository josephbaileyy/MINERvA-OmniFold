# Binding amendment 1: the cheap tier's 5A reader rerun (2026-10-29)

**By** the paper-tighten lane, as director.

**Under** [`FD-CT-READERS-BINDING.md`](FD-CT-READERS-BINDING.md) and the director's ruling of 2026-10-29 on the 5A
STOP, option (c).

**Binds** [`FD-CT-READERS-AMENDMENT-1.md`](FD-CT-READERS-AMENDMENT-1.md), merged in PR #491. Its file sha256 begins
`45d470d79afc9598`. Everything the first binding set stands, except as stated here.

**MEASURES:** nothing. It authorizes one deploy and its tests, and one rerun of 5A (`period`) only, on a login node at
0 node-h.

**CANNOT AUTHORIZE:** a rerun of 3a or 4C, whose bound runs stand; any change to the bound run's directory
`fd-ct-readers-20261028/`; and everything the first binding cannot authorize.

## 1. The bound code

**The deploy pin** is `bb8dc101898c79713a40aead51ed7980db4dc36e`, main after PR #491.
- `B=/pscratch/sd/j/josephrb/fd-ct-readers-am1-20261029` and `D=$B/deploy/bb8dc101`.

**At the PR head `cfd24474`, the director checked:**
- the new pins, `fd_ct_readers.py` `32e9b061` and `test_fd_ct_readers.py` `9c543aee`. The other four §6 pins are
  unchanged, and the same two digests and the amendment's `45d470d7` were measured again on `main` after the merge;
- the code diff: one new pure function `near_f` (|x/f − 1| < `f0.LEAK_REL`), and the central partial integrals
  dropped where `near_f` holds instead of where the outside share is exactly 0. Nothing else in the tool changed;
- the declared test set, locally with `-B` and a TMPDIR: **Ran 153 tests, OK**, rc 0, with 0 porcelain lines
  (including ignored files) after;
- the mutation receipt: 82 of 82 killed, including the four mutants of the change.

## 2. Rulings

1. **The boundary is LEAK_REL,** the guard's own tolerance, as amendment §7 item 1 proposes. An integral the guard
   would call f is f, and f is already in its table.
2. **Only 5A reruns,** into the new `$B`. 3a's and 4C's readouts from the bound run stand as reported in
   `FD-CT-READERS-REPORT.md`.

## 3. Conditions

1. **Deploy and tests,** as the declaration's §2.1 at the new pin. `$B` must not exist beforehand. The deploy log must
   show HEAD equal to the pin, 0 porcelain lines before and after, the amendment's §6 digests, `tests rc=0` and "Ran
   153 tests". Anything else is a STOP.
2. **The run:** the declaration's §2.2 `period` command, unchanged except for `$B` and `$D`, under its 75 s timeout.
   Any exit other than 0 is a STOP, reported unrepaired.
3. **The report is `FD-CT-READERS-5A-REPORT.md`, opened as a PR to the director,** with the first binding's §3
   condition 4 fields for 5A, ruling 6's departure stated, and no reading.
4. **Ledger** rows go in `fd/LEDGER.tsv`. **Retention:** `fd-ct-readers-am1-20261029` joins the pscratch list.

The steps may start once this record is on `main`.

## Not changed

- Every covariance, cell, readout and κ, and the reported matrix C_total + C_resp.
- `docs/analysis-note/**`.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
