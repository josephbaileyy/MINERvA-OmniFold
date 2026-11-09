# BINDING 1: FD-PRR, the prior-retention study (director, 2026-11-08)

**Binds** [`FD-PRR-DECLARATION.md`](FD-PRR-DECLARATION.md) (rev 2) and its code, as merged in PR #937 at
**M = `a5235714a379457f09c539a2c94054354640648c`**. The audited head is `493ea6b4`; the declaration and every file under
`nd-unfolding/prior_retention/` are identical at the two commits.

| file | sha256 (prefix) |
|---|---|
| `FD-PRR-DECLARATION.md` | `5be1e19cb8db6706` |
| `nd-unfolding/prior_retention/prr_probe.py` | `f87ee90c58d2b890` |
| `nd-unfolding/prior_retention/prr_ibu.py` | `17acad82bad7c43f` |
| `nd-unfolding/prior_retention/prr_read.py` | `f35bc3282b50215d` |
| `nd-unfolding/prior_retention/sbatch_prr.sh` | `323f491afa2038a5` |
| `nd-unfolding/prior_retention/test_prr.py` | `33bfdf099077dbc4` |
| `nd-unfolding/prior_retention/prr_mutation.py` | `28f3f9e5edf1e63c` |

**Under:** `DECISION-20261106-joseph-plateau-next-work.md` item 2 (the prior-retention study, authorized and paused) and
`DECISION-20261108-joseph-5d-coverage-and-parallel-studies.md` item 3 (released).

## What the director checked

coverage-5b-audit's GO at `493ea6b4` (https://github.com/josephbaileyy/MINERvA-OmniFold/pull/937#issuecomment-6728818077):
- 103 tests pass and 62 of 62 mutants are killed by their named tests at the head, matching the committed receipt
  (made at code commit `0478e727` in a clean clone; the failed first run, 59 of 62, is kept as
  `mutation-run1-fail.txt`);
- the §8.1 digests match; the §10.3 packing, rebuilt independently, gives the 27.0 cap exactly;
- the director's rulings 1–2 are carried in the licences, `prr_read.LABELS` and `clears()`;
- C-CT reproduces F0b's committed σ to 0 and its closure_nuwro χ² to 1.9e-14;
- the §10.4 ENS1 queue check works, and both its mutants are killed.

## Rulings

1. **The design is bound as declared at M:** both routes (one factor at a time on FD-STAB's noise-free closures at the
   12 graded truths, and REF-G1's IBU on the same expectation experiments), the floor, the readings PR-1 to PR-3 and the
   descriptive R-ID and R-SUP.
2. **No level is adopted, whatever PR-3 shows** (FD-STAB §6's terminal rule). A level that clears the flagged truths is
   a finding about the mechanism; any change to the reported procedure needs a new decision by Joseph and its own
   held-out test.
3. **Grading at F0b's truths is description only.** NOT CITABLE FOR a held-out performance claim, or that any level
   "would pass". PR-3 reads "clears / does not clear at these truths".
4. **The price.** The cap is **27.0 CPU node-h**, the sum of the five jobs' limits (prr_dry 4:45:00, prr_iter 7:30:00,
   prr_cap 9:00:00, prr_misc 4:45:00, prr_ibu 0:30:00), with about 12.8 expected. A gate refuses a full job whose
   projection is above 0.9 × its `--time`, and no limit is raised without an addendum. `iris` is read before each
   connect.
5. **Sequencing.** prr_dry is submitted only after ENS1's stage 2 has ended and its post-run and analysis are done (the
   script's ens1_* queue check enforces the first part). Shared inputs with ENS1, the band diagnosis and LL5D (the
   inputs npz, the background dump and the bank's cv.npz, `receipts-ll5d` overlap check #949) are read only through
   noatime copies with per-file stat records before and after; no two lanes' connects copy at the same time. Directory
   atimes are not a control.
6. **The job-name family `prr_*`** is new. The director names it to every lane with a live fence before the first prr_
   go.
7. **Each connect** sends its sha256 and path to the director before launch, from a fresh clone at M with empty
   porcelain. ssh's rc is read unpiped, every `--time` is HH:MM:SS with scontrol's TimeLimit checked, and each receipt
   goes in as a PR.
8. **The report** gives PR-1 to PR-3 and the descriptive readouts with their licences, and the cost measured. It goes to
   the director, then to Joseph. No paper or note text.

The audit's two lows (the dry gate's 657 s unit against the 1,062 s `--time`; C-IBU(a) exercised only on the cluster)
are held for the follow-up list. Both fail safe.

Nothing is submitted, deposited or tagged.
