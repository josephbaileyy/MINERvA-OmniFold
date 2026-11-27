# DECISION 2026-11-24 — Joseph: COVFIX rev 12's correlation truth, ceiling and family draw; the CPU-only rule relaxed for every job; and seven decisions on the codex-school advisory

**Recorded by** the director. Every answer below reached the director through the rewrite helper, Joseph's wording
channel, by message on 2026-11-24. Quoted words are Joseph's, as the rewrite helper relayed them. Where the director
holds no relayed quote for an item, the record says so.

## 1. COVFIX rev 12 (the draft on `cov2d/covfix-rev12-20261124`, at `133445583dec4d812e3cd6f686e88e1dae2c8510`)

1. **The blind correlation truth and three smaller items.** Relayed at 06:49Z: "lets do the blind correlation truth
   and the three smaller items." Rev 12 adds the third sealed truth, u = 2. It is a correlation deformation that keeps
   the graded 2D truth at nominal.
2. **The ceiling.** Relayed at 06:54Z: "we can raise the ceiling too." The rewrite helper gave it as "about 600
   (599), subject to your read of the iris balance". The director set the CPU ceiling at 600.00 node-h. The rebuilt
   laterals branch prices at 599.56, and the committed iris receipt (#1276) showed 630.4 left at 06:55Z.
3. **The custody family draw.** Relayed at 06:57Z: "sure lets go ahead", with one change, the redraw on reco-level
   non-triviality dropped. Rev 12's draft later carries a 1σ reco-level floor, (b), after the codex-school
   reco-floor advisory (`report.md` sha256 `f4e6597c…`). The director holds no relayed quote of Joseph accepting the
   floor, so this goes to Joseph for confirmation with rev 12's final text.
4. **P-2 on the full V**, with the trace readings beside it as descriptive readings. This was the codex-school view
   relayed at 06:57Z. The director holds no relayed quote of Joseph accepting it, so it is confirmed with rev 12's
   final text as well.

Rev 12 binds nothing until Joseph approves its final text.

## 2. The CPU-only rule

1. Relayed at 07:34Z: "no we should relax that cpu only rule."
2. Relayed at 07:36Z: "I am fine relaxing the cpu only rule for everything. and yes measure the correlation of q0
   with eavail".

What is decided:
- Perlmutter GPU (`m3246_g`) is allowed for every job.
- Each job that moves needs a declared reproduction test before its graded outputs are read: non-bitwise, tolerance
  1e-8, with matched threads.
- Keeping a job on CPU is now a choice on the merits:
  - **COVFIX's 2D toys** stay on CPU. The estimator E_R was run on CPU, and the bars assume it.
  - **IBUB** stays on its bound CPU node.
- **The ledger.** DECISION-20261023 (GPU 5,100) approved up to 5,100 GPU node-h for the 5D design's stages, ledgered
  per job. GPU jobs outside those stages are ledgered on their own lines in the same ledger, and do not draw on the
  5,100: COVFIX's (b) readout (25.8 GPU node-h for three truths) and RPD-RECO's event-loop rerun (about 1.4 GPU
  node-h). Each is far below half the `m3246_g` balance (about 27,488 GPU node-h), so it is within the director's
  operational authority. Joseph is told of each. iris is read before each GPU binding.

## 3. Seven decisions on the codex-school (gpt-6.2) advisory

The advisory is `~/codex-reports/note-measurement/seven-decisions-20261124/FINAL.md`, sha256 `358d0f105ead7359…`. It
was read-only at `25367f3cd` and is not a record. Relayed at 15:34Z, in Joseph's words:

> okay I agree with it all and yes set the branch protection and check pass probability.

"It all" means the advisory's seven items plus the rewrite helper's one addition (item 6).

1. **RPD-RECO: route (A),** the event-loop E_ν route, at a lower priority than COVFIX review. The C-E3 gate stays at
   3%. The retention receipt (`fd/anatuple-mc-stat-20261124/README.md:16-31`) shows 489/489 MC AnaTuples present,
   with the earliest purge exposure on 2027-01-18.
2. **COVFIX slot 1: (A),** the sha-pinned private copy of SciSoft's G21_11a. The condition: a clean replay must
   verify the extracted files, the resolved GENIE configuration, and the spline the generator actually opens, not
   only the tarball hash. If that can't be verified, the slot is dropped and the claim narrowed. Slot 2 stays
   G18_02a_00_000.
3. **A codex-school review of rev 12:** yes, once, on the final amendment text, then a focused recheck of any blockers
   it finds.
4. **covfix-ledger protection:** done by the rewrite helper as repository ruleset 27996874, "covfix-ledger
   append-only". The director read it back by API: active, no bypass actors, ref `refs/heads/covfix-ledger`, rules
   `non_fast_forward` and `deletion`. Creation and ordinary pushes are not blocked. The branch is not on origin yet:
   `git ls-remote origin refs/heads/covfix-ledger` printed no ref on 2026-11-24. Its first push is the synthetic-seal
   rehearsal's ledger line, under the director's approval.
   <!-- absence-ok: the state of one git ref, read by the ls-remote stated in the sentence; not a claim that a result does not exist -->

5. **Step 2:** yes, as time-boxed pricing. It needs one data-usable candidate, its cost, and a pass/fail test at both
   the GiBUU hybrid and the q3 tilt. If none passes by 2026-11-25T12:00Z, the director's time box, the current
   estimator is frozen.
6. **The (b) readout in rev 12:** conditional yes. Before the first seal spend, rev 12 must freeze:
   - the estimator, the cells, the intervals and the failure rule;
   - which response and run-period variations the toys exercise;
   - a joint-coverage grade of the frozen set. This is the rewrite helper's addition, which Joseph accepted.

   If the 5D design can't be frozen and rehearsed in time, COVFIX proceeds with 2D only.
7. **Keep R00–R15.** Codex's proposed values for the draft rule's blanks go to Ben as a draft, through Joseph. They
   are not applied until Joseph and Ben ratify them.

**Pass probability (Joseph's "check pass probability").** The advisory proposed a per-cell held-out minimum: a
one-sided 95% exact binomial lower bound of 63.27%, or ≥ 204/300. The rewrite helper found it unworkable, and the
director reproduced the figures with scipy, under independence:
- at nominal 68.27% coverage, one cell passes with probability 0.567;
- 48 tests all pass with probability 1.5e-12, and 8 tests with 0.011;
- for 48 tests to pass jointly with probability 0.95 at nominal, a cell needs ≥ 180/300. That threshold passes with
  probability 0.891 at a true coverage of 63.27%, and 0.261 at 58%;
- the one-sided CP lower bound at 204/300 is 0.6328.

So the 204 rule is not used. Each threshold, per-cell and joint, is fixed by a declared pass probability at nominal,
simulated with COVFIX's zero-bias reference machinery on correlated toys drawn from the carried 16-cell covariance.
The amendment states each threshold with its simulated pass probability at nominal and its power at declared
under-coverage points. No threshold is tuned on sealed output.

## Who does what

- **cov2d:** rev 12 text (slot 1 with its drop branch, slot 2, folding in (b)), the pass-probability simulation, then
  the codex-school read.
- **tier3-design:** step 2 within the time box, then the (b) design and the carried covariance file.
- **tune-generator:** slot 1's private product and replay. Its blinding is unchanged.
- **limitation-resolver:** RPD-RECO route (A), behind COVFIX in the read queue.
- **journal-editor:** the wrapper's tests against the ruleset, with no test push to the real ref.

**CITABLE FOR:** what Joseph decided on 2026-11-24, and in what words. **NOT CITABLE FOR:** any result, any covariance
adoption, any note wording.
