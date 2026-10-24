# R10 binding, amendment 1: the reco-tree join resolves duplicated identities by vertex (2026-10-24)

**By** the paper-tighten lane, as director. **Amends** [`BINDING.md`](BINDING.md) (PR #303). This ruling is made before
any R10 output: no R10 readout exists.

## What happened

- **X failed closed.** Job 60196485 exited 7 on playlist 1E after 1,320 s, charging 0.3667 CPU node-h, and wrote
  nothing.
- **Where it passed:** playlists 1A–1D passed every admission and join control.
- **What tripped the control:** in 1E, 111 identities are duplicated within one reco tree
  (`MasterAnaDev_mc_AnaTuple_run00111353`), and exactly one row to be joined carries one of them. The duplicate control
  refused it.
- **The lane's read-only diagnosis:** the two entries are different events; their vertices are 1,665 mm apart. Exactly
  one matches the row's G2 reco vertex, at 0.0 mm. This is the reco-side counterpart of MP-2 S1's Truth-side
  duplicates in 1E.

## The fix: accepted

The fix is PR #309, commit `289a1ff755fe8c21aeef4f19aebe559cf7849bc1`. The director checked the diff: only
`r10_extract.py`'s `join_rows` and its tests change.
- A unique identity joins as before.
- A duplicated identity joins to the single entry whose vertex equals G2's within the declared 1e-6 mm.
- If no entry, or more than one, matches, the row is UNRESOLVED and the join fails.
- The vertex control on every joined row is unchanged.
- There are two new tests: the duplicate resolves by vertex, not by tree order; and zero or two matches fail.

## Amended terms

- **X** is re-deployed at `289a1ff7`, once, at the bound limit of 1:19:00.
- **Y** runs at that commit too. `r10.py` checks that the receipt's `r10_extract.py` sha256 equals its own.
- `r10.py`, `config.json` and `binding-delta.txt` are unchanged.
- **Controls-only** (K0–K2) is re-run at the new commit for the record before X.
- **Charge:** 0.408 so far. The worst case with the re-run is at most 1.73 CPU node-h, inside the cap of 4.
- **The report** states:
  - the duplicate count;
  - how many rows were resolved by vertex;
  - that no row was left unresolved (otherwise R10 is INCOMPLETE).
- Everything else in BINDING.md stands.
