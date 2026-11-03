# BINDING 2: the run-period diagnosis (RPD), part 2, the code (director, 2026-11-03)

**Binds** [`FD-RPD-DECLARATION-PART2.md`](FD-RPD-DECLARATION-PART2.md), revision 3, sha256
`caba5ead65371370de3712865e5cf0a7cfd2279100eb8fd30e4b68266dc9e661`, as merged in PR #715 at
**M = `73f7828b300c60b2364f30e5637639f841ce39e8`** (PR head `7bd0440f`; code commit `c3e235b2`).

**Under** [`FD-RPD-BINDING-1.md`](FD-RPD-BINDING-1.md) (#703), which binds part 1's design, and
`DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md` item 3(b) (#690).

**What this binds.**
- The code, tests and commands of part 2.
- The **pin** for every command of part 2 §2 is M. The deploy verifies the 22 blobs of part 2 §7 at M.

## What the director checked

- **The digest.** The declaration's sha256 at M is the one above.
- **The pinned bytes.** All 22 rows of part 2 §7 equal `git rev-parse M:<path>`, with 0 mismatches.
- **The audit.** A fresh Sonnet audit of part 2 found 5 MAJOR, 8 MINOR and 5 NIT findings. Its prompt and answer are
  verbatim (`FD-RPD-PART2-AUDIT-SONNET-{PROMPT,ANSWER}.txt`), and part 2 §9 disposes of each finding.
- **The mutation receipt** (`fd/receipts-rpd/mutants_rpd.log`) reads "killed 114 of 114; survived 0; not applied 0;
  files restored True", rc 0, on `c3e235b2`.
- **The cluster test receipt** (`fd/receipts-rpd/root_tests_login.{sh,log}`) was run on login02:
  - root_6_28 activated by prefix, without `set -u`;
  - `test_fd_rpd` 110 OK with 0 skipped, so all 5 ROOT tests ran;
  - `test_fd_ct_periods` 85 OK; `test_fd_ct_readers` 77 OK;
  - porcelain and `squeue --me` empty before and after, and no pscratch or CFS read.

## Rulings

1. **Part 2 is bound as declared at M.**
2. **The deviations (part 2 §6):**
   - **1, ruled (a):** C1's `measured_weights` is printed per playlist, not graded. Config R does not read the key,
     and grading at 0.999 carried a measured 0–5% spurious-stop risk per playlist.
   - **2, accepted for printing:** stage D's descriptive α̂ is averaged over the first 25 outer datasets per truth. The
     readout's calibration gate uses all 2,000 (`R2_GATE_N`).
   - **3, resolved by ruling 2 (a):** F1 grades contents, both POTs and the edges to 10⁻¹², and prints the errors'
     max_rel.
   - **4, accepted:** the inputs driver's four records hold no unfold-derived number and skip the LeakGuard.
3. **Calibration (part 2 §4).**
   - Part 1's rule stands at 30 replicas, with the gate at 0.0646 and the readout at 2,000 datasets × 4 scales.
   - **Synthetic proxies:**
     - pooled α̂ is 0.0558 ± 0.0047 without T's MC-variance term, and 0.0475–0.0521 with it, κ bracketed;
     - the chance of an INCONCLUSIVE on calibration is about 0.044 per grid point, a correlated floor, and 0.000–0.007
       with the term.
   - An INCONCLUSIVE on calibration is a legitimate outcome, reported as one, with this risk stated in advance.
4. **The order, from binding 1, unchanged:**
   - stage S;
   - then stage 0 and stage D, on a login node at 0 node-h, whose records go to the director **before job A**, under
     binding 1 ruling 2;
   - job A;
   - the controls;
   - job B, only after the controls PASS;
   - the readout.

   The director is told before each connect and each submission, with the connect script's sha256.
5. **The connects** (binding 1 ruling 6):
   - each from a fresh clone at M;
   - `$R` = `/pscratch/sd/j/josephrb/fd-rpd-20261103` must not exist beforehand;
   - every audit or probe read through O_NOATIME, with the stat discipline;
   - writes only under `$R`, and nothing to CFS.
6. **The price** stays binding 1's: about 1.65 node-h expected, at most **3.0 node-h** (job A 1:00:00, job B 2:00:00),
   regular QOS, CPU only.
7. **The deadline:** the jobs run before 2026-12-15, the zero loops' exposure date. HPSS follows binding 1 ruling 4,
   after the deferral ends (2026-11-06 17:00).
8. **What may be claimed** stays binding 1 ruling 5:
   - no outcome supplies a cause;
   - no outcome by itself drops "poorly determined";
   - adopting C_PL,12 would be Joseph's decision.

Nothing is submitted, deposited or tagged.
