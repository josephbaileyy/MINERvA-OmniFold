# EVW2D BINDING 2: the HPSS copy and the deposit fetch, bound to SHA256SUMS e60867ef (director, 2026-11-26)

**Follows** EVW2D BINDING 1 (`EVW2D-BINDING-1.md`, #1370). Job 62022231 ran under binding 1 and ended COMPLETED 0:0 in 713 s, charged 0.1981 node-h. The receipts are merged in #1377 under `receipts/run-20261126/`.

**Authority:** as for binding 1. Joseph decided that every weight file goes on Zenodo in the same release (`DECISION-20261125c` §1). The deposit itself is Joseph's, after Ben approves. No lane uploads anything.

**Binds** the code merged in #1390 (head `92f7785e04d9b68f70becb3070ca31e724e77600`), on main at `d65e3f5178ac6b10bc6f019efdc1fa4c634d431a`:
- `launch/bound-deposit/PINS.txt` sha256 `7966ec112806152bf82385d7d510882acc3befbded43dca71ffdf3390e8e8c8a`, written by `fill_deposit_pins.sh` from commit 47f6a3ae;
- `launch/bound-deposit/evw2d_deposit.sh` sha256 `91fc4e1bb20d55f0f66e73263d4c30f1388d0bc8440e40a288a443ffe6db7e69`;
- `launch/bound-deposit/evw2d_hpss.sh` sha256 `5c674c6c00a24f460d8d7f600c3bb8c8805f6f46d4393bb6d7fd0125a1c5aa41`.

**SHA256SUMS sha256 = `e60867ef66eb47172a0e90140abc7a366d780dfc3aa3f9beb426a40a48d1416e`**

The director checked every pin in PINS.txt against the committed records by command:
- the products digest e60867ef and `evw2d.done` 830d7d76 are `out/SHA256SUMS` and `out/evw2d.done` in `receipts/run-20261126/post/SHA256SUMS`;
- evw2d.py 6106b23a and config bee02d38 are the ones in `EVW2D-BINDING-1.md` and `launch/bound/PINS.txt`;
- job 62022231 is the one in the run receipts.

The code passed 84 tests and killed 70 of 70 mutants, with the script shas checked unchanged after the run. It had six codex-school reads, r1 to r1f. The last, on the launcher, was ALL HOLD. Receipts: `launch/receipts/deposit/`.

## Rulings

1. **Three steps are bound**, run in order from `launch/bound-deposit/` at or after this binding's merge, each only after the previous one exits 0:
   - `evw2d_deposit.sh hpss <new empty session dir> <loginNN>`;
   - `evw2d_deposit.sh fetch <new empty dir>`, which verifies the HPSS receipt;
   - `evw2d_deposit.sh fetch-products <new empty dir under $HOME>`.
   Any changed byte goes back to the director.
2. **The HPSS path** is `/home/j/josephrb/mnv-evw2d-20261126/evw2d-20261126.tar` and its `.idx`, a new archive. The step refuses if any of the archive's names exists. It writes under a part name and verifies by htar CRC and -Hverify, hashcreate and hashverify, a full retrieval re-hashed against the pins, and htar -tf. Only then does it rename to the final names and read them back. Nothing is written to CFS.
3. **The deposit copy** goes into a new directory under `$HOME`, outside `/private/tmp` and `/tmp`, for example `~/evw2d-deposit-20261126/`. `evw2d.accepted()` must pass there on the Mac with the bound digests. The lane reports the path and the six shas, recomputed there. The copy is Joseph's upload copy; after it lands, no lane touches it. The Mac had 15 GiB free when this was written, for about 1.2 GB.
4. **Preconditions:** a valid NERSC certificate checked by command before each step (valid until 2026-11-27T14:22:19Z when this was written), with no use past expiry, and the director's GO naming this binding.
5. **One run of each step.** Any STOP or refusal is terminal, and nothing is rerun without the director. A failure after the archive exists leaves the part names on HPSS for the director. The scratch products stay where they are; removing them is Joseph's call.
