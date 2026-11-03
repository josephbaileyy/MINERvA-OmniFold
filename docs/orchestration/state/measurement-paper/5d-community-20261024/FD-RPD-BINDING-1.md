# BINDING 1: the run-period diagnosis (RPD), part 1, the design (director, 2026-11-02)

**Binds** the design of [`FD-RPD-DECLARATION.md`](FD-RPD-DECLARATION.md), revision 4, sha256 `b3413ffc06a9df935df649d22b6cbad505640fdb7df9d6fbae5650f2c29f92f5`. It binds it as merged in PR #693 at **M = `648186f4c9abb4cdfd4f309a297ee18516ca3b90`** (PR head `85fb3236`).

**Under** `DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md` item 3(b) (#690).

**What this binds.** The design only: the rules, outcomes, wording, controls and price. Part 2, the code, needs its own
audit and a second binding before anything runs.

## What the director checked

- **The digest.** The declaration's sha256 at the head equals the lane's (`b3413ffc…`).
- **The audits.** Three fresh Sonnet audits are verbatim beside it (`FD-RPD-AUDIT-{1,2,3}-SONNET-{PROMPT,ANSWER}.txt`).
  Each finding is disposed of in §12–§14.
- **What audit 3 found:**
  - EC is reachable. Under exchangeable offsets its toy gave P(EC) = 0.74 at τ = 0.6%, and 0.97–0.98 from 1.1% up.
  - Under clustering of 0.3% or more, P(EC) ≤ 0.02.
  - EC and CLUSTERED are nearly disjoint.
  - 5B's real period offsets fall in the reachable regime.
- **The input ruling.** The 12 zero per-playlist loops, with the equality evidence named, replace the CFS bkgaware
  loops. The CFS copy stays as a fallback.

## Rulings

1. **The design is bound as declared:**
   - stage 0 on login, at 0 node-h, with its fixed branches;
   - stage D on login, at 0 node-h;
   - jobs A and B, with N0 and its partitions;
   - the readouts R1, R2 and R3;
   - the outcome table and the paper wording fixed for each outcome (§6.3).
2. **Stage D reports to the director before job A.**
   - Its rules may drop an R1 sentence: P(PERIOD-WIDE | PERIOD-WIDE truth) < 0.5 at stage 0's measured s₀.
   - Its rules may flag the 12-playlist wording as not expected: P(EC | T1) < 0.2.
   - Either result changes what can be claimed. It goes to Joseph if it removes a planned paper sentence.
3. **The price.** About 1.65 node-h expected, at most **3.0 node-h**: job A at 1:00:00 and job B at 2:00:00, regular
   QOS, CPU only. The reservation is the cap.
4. **HPSS.** The HPSS deferral record `RECORD-20261102-director-hpss-deferral.md` (#685) extends to RPD.
   - **What joins the post-2026-11-06 catch-up archive,** under the record's procedure:
     - RPD's pscratch-only inputs: the 12 zero loops (4.84 GB), 5B's PC dumps, lat_zero* (1.55 GB) and the flux files;
     - its products: the 492 unfolds and their MC truths, and N0's receipts.
   - **What stays on pscratch:** N0's pseudo-npz files, which can be rebuilt.
   - **The deadline.** The jobs run before 2026-12-15, the zero loops' exposure date.
5. **Departures from #690's wording, accepted and to be reported to Joseph with the result:**
   - (a) The input is the zero loops, not the CFS bkgaware copy.
   - (b) No outcome supplies a cause. At best a step is localized.
   - (c) No outcome by itself drops "poorly determined". That clause describes C_PL,5D's own three-group estimator.
     Adopting C_PL,12 after EXCHANGEABLE-COMPATIBLE would be Joseph's decision, and it would reopen
     `paper_body.tex:81`'s block description and `sec_fived16.tex:125`.
6. **The connects:**
   - every read through O_NOATIME, with the stat discipline;
   - writes only under a new pscratch directory, and nothing to CFS;
   - each run from a fresh clone at the bound commit.
7. **Part 2.** Its code needs blob digests, tests, a mutation receipt and its own audit, then binding 2. Nothing runs
   before that, except stage 0 and stage D at 0 node-h once binding 2 binds their code.

Nothing is submitted, deposited or tagged.
