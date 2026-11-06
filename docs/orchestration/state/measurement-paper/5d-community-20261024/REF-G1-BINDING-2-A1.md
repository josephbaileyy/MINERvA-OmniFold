# REF-G1 BINDING 2, addendum A1: G-IBU1 at IBU-1's threads, read discipline, and the re-made read (director, 2026-11-06)

**Binds** [`REF-G1-ADDENDUM-A1.md`](REF-G1-ADDENDUM-A1.md), sha256
`38d4b42a86994a163e5d25c1500adbc92c4d52c420e66e7252f0b21d714404ca`, and its code, as merged in #806 at
**M' = `0bb9a1bfcb462ebd171d337ae1c8b2e2d0905e93`** (PR head `7b0e92f4`).

**Under** [`REF-G1-BINDING-2.md`](REF-G1-BINDING-2.md), after the read's G-IBU1 STOP (`fd/receipts-ref-g1/read/`, #792).
The diagnosis (#795) found F_fold and F_sub at most 2 ulps off D_N in about 3 % of elements, with ks exact. IBU-1 ran at
1/1/1 threads on 2 CPUs; gibu1 ran at 32.

| file | blob at M' |
|---|---|
| `nd-unfolding/ref_g1/ref_g1.py` | `d015a352e0e1789f88f4bd45c088850453850c7f` |
| `nd-unfolding/ref_g1/ref_g1_read.py` | `e045d96215ab266a8b16347ed9b03561a23658d5` |
| `nd-unfolding/ref_g1/config.json` | `245697523a76b7f2a6839f0f70569df73898886e` |
| `nd-unfolding/ref_g1/test_ref_g1.py` | `820d4afdede7bf49bd4e19df3d36af1554452f36` |
| `nd-unfolding/ref_g1/ref_g1_mutation.py` | `2d29a9151d27a85f2ba3d65a48a8a744cf95302a` |

## What the director checked

- **The digest** of A1 at M'.
- **The audit** (coverage-5b-audit, #806): B1, the pin in config.json between the bars and the read, is fixed by option
  (a). The pin is passed as read arguments, with a bars→merge→read test. L1–L3 are closed: the closure is code-derived;
  gibu1 and the reader run ROOT-free, enforced; threadpool and `root_loaded` are recorded.
- **The receipt:** 40 tests; MUTATION CHECK PASS on 42 mutations; the run-path trace shows 0 of 74 hits, with a firing
  control.

## Rulings

1. **A1 is bound at M'.** REF-G1's code is frozen unless a control STOPs.
2. **G-IBU1 keeps its bitwise rule.** gibu1 re-runs alone at OMP/OPENBLAS/MKL = 1 on 2 CPUs, the environment
   `ibu1/sbatch_ibu1.sh:25, :37` and sacct 60130813.0 record. A non-bitwise result is a STOP to the director, and any
   tolerance would be a separate decision labelled post hoc. The other 232 units stand (SHA256SUMS `6a4c1929`).
3. **Every declared input is read once,** through an O_NOATIME, digest-checked copy, under the audit hook and the TFile
   guard. The reused modules are unchanged.
4. **A fixed conditional sequence.** It is the one A1 §5 sets out. Each step proceeds when the previous one's PASS
   record is on main, and anything else stops and comes to the director. limitation-resolver reports each connect's
   sha256 and result, and does not wait for a go.
   1. **Connect 1:**
      - a fresh clone at M', run with `-B`, porcelain `--ignored` before and after;
      - the stat of `ref_g1_read.py reads`' set, which fixes the deadline as the earliest exposure;
      - the gibu1 re-run;
      - the bars from the new reader, into a new read directory.
   2. **The merge** of bars.json and connect 1's receipt, with gibu1's product path and sha256.
   3. **Connect 2:** the read, with `--gibu1-product` and `--gibu1-sha256` from that receipt.
5. **The price.** It stays within the 5.0 CPU node-h cap, with 0.15 spent. Write every `--time` as HH:MM:SS, with the
   TimeLimit check. The COV2D fence holds.
6. **Unchanged:** binding 1 ruling 6 (paper wording through the PRD read and Joseph), and §5's licences.

Nothing is submitted, deposited or tagged.
