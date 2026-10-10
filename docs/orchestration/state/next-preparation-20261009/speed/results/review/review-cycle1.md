# Focused re-review (cycle 1): Session 4 (speed), commit `ce224e7f`

**Reviewer:** the same read-only reviewer as the initial review (Claude Opus 5.5). This is the one
allowed re-review.

**Target:** clean detached worktree
`/Users/josephbailey/local-research/MINERvA-OmniFold-next-speed-review-20261009` at
`ce224e7fb440d229b35ab4778a04d73648b8357f`.

**Repair commits:**
- `c209f3a7`: code and results
- `ce224e7f`: report and preserved review

**Diff from the initial freeze** (`git diff --stat 1e4e6f46..ce224e7f`):
- 20 files, all under `Q/speed/` (`git diff --name-only … | grep -v speed/` is empty).
- No production file changed.
- The subtree is now 556 KB.

**Worktree status:**
- start (23:42:08Z): empty, rc 0
- end (23:44:51Z): empty, rc 0

**Constraints honoured:** no sacct queries, no cluster access. Local work was one run of the test
suite plus three small probes, about 1 CPU-minute in total.

Below, `R:` = `Q/REPORT.md` at `ce224e7f`, and `Q` = `docs/orchestration/state/next-preparation-20261009/speed`.

Files written to `scratchpad/review/` in this cycle:
- `recompute_cycle1.py` and `recompute_cycle1.out`
- `boolview_mutant_fixed.py`, `bv_fixed_synth_rows200000_extra0.out`, `bv_fixed_synth_rows200000_extra192.out`
- `address_probe.py` and `address_probe.out`
- `tests_cycle1.out`

## Numbers the repair moved: independent recompute

`recompute_cycle1.py` is my own code; it imports nothing from the lane.

**P05 forecast by packing.** Inputs: purity sweep `55677843` RSS; node memory 511.50 GB; exact unfold
(69,523 + 1,801) s; CV exact rate 0.6657 node-h at 29 per node.

| budget | RSS (GB) | jobs/node | P05 (node-h) | P03 N=50 + P05 + P09b | ×1.15 / 0.8 | share of remaining CPU | waves at 30 nodes |
|---|---:|---:|---:|---:|---:|---:|---:|
| median | 71.16 | 7 | 529.9 | 569.9 | 819.2 | 0.27 | 1 |
| p90 (index 9n//10) | 121.15 | 4 | 926.9 | 966.8 | 1,389.8 | 0.46 | 2 |
| worst | 186.56 | 2 | 1,853.1 | 1,893.1 | 2,721.3 | 0.89 | 4 |

All of this matches R:50, R:210, R:216 and `results/costs.json`. The other moved figures also match:

- Billing ×4.2–14.9 (R:183): 2.830 / 0.667 = 4.24 and 9.906 / 0.667 = 14.85.
- Saving per exact universe unfold 2.16–9.24 node-h (R:236), so 404–1,728 node-h over P05.

**Conservative C, prototypes 1 + 2, smaller loop fraction.** Here `a_lo` = 0.7563, from my own
reduction of `bench_loader_fill.jsonl`, with C's conservative operands and the conservative setup.

| total | mine | lane `costs.json` and R:222-224 |
|---|---:|---:|
| P1 | 659,899.9 | 659,899.9 |
| P2 | 2,724.8 | 2,724.8 |
| P3 | 64,018.1 | 64,018.1 |

These match.

**RSS ≤ 72.5 GB shares.**

- Purity: 162 of 187 (86.6 %). The report's 162 / 87 % is correct.
- Negweight: **164** of 187 (87.7 %). The report says "165 negweight, 88 %" (R:113-114). The
  percentage rounds correctly, but the count is off by one. There is no boundary ambiguity: the
  values nearest the threshold are 72.294 GB and then 76.322 GB.
- The count is in no committed results file, so it was transcribed by hand. This is new finding N1.

## F12: who was right

**The owner is right, and my initial F12 claim was wrong.** My cycle-0 probe (`boolview_mutant.py`)
passed the branch tuple as `tuple(names[:6])`. In `signal_branches`' list, index 4 is `sim_pass`, so
the probe fed `sim_pass` in as `w_truth` and `w_truth` in as `w_reco`. The lane's own helper uses
`(*names[:4], names[5], names[6])` (`Q/bench/test_prototypes.py:62-64`).

The comparison was against a reference from the same tree, so the tree was not the problem. The
"all 8 keys change" result came from the wrong weight branches, not from the removed view. My probe
also had no unmutated control, which would have exposed this at once.

**Corrected probe** (`boolview_mutant_fixed.py`): correct tuple plus an unmutated-prototype control,
run on both 200 k trees.

| tree | control: keys differing | without the view: keys differing |
|---|---|---|
| `synth_rows200000_extra0` (666 byte-2 rows) | `[]` | `[]` |
| `synth_rows200000_extra192` | `[]` | `[]` |

The lane's `DefensiveGuards.test_report_bool_view_difference` prints the same `[]` in my run
(`tests_cycle1.out`). This agrees with my own NumPy probe in cycle 0 (`boolview_probe.out`:
`raw != 0` normalizes byte 2 to 1).

The repaired text (R:141-146) is now accurate: the byte view is defensive and not shown necessary on
this platform. **F12 is RESOLVED in the report's favour, and I retract my "the trap is real"
statement.** The preserved `results/review/review.md` still carries that statement; §11 (R:383-387)
records the correction, which is enough.

## Disposition of F1–F16

**F1 — RESOLVED.** P05 is now a forecast of ≈ 530 / 927 / 1,853 node-h by packing policy, and the
basis is stated: no exact universe unfold has run, and the RSS is taken from LightGBM tasks (R:47-53,
R:209-212, R:216, R:269-270). Recomputed above.

**F2 — RESOLVED.** D1's PASS is bounded to full-node LightGBM universe-file unfolds at 128 threads
(R:21, R:319-325). Exact P05 and shared-64 billing are explicitly outside the PASS (R:326-328). The
shared-64 rate is labelled category 2 and a forecast (R:206-208, R:218, R:231-232).

**F3 — RESOLVED.** SB1 (b) now runs at 128 threads on a regular node, matching the references
(R:289-293). Attribution goes through (a)'s byte identity. An excess over tolerance in (b) is
"reported, not used to fail" prototype 1 (R:296-299), and the abort list no longer includes the (b)
tolerance (R:301-302).

**F4 — RESOLVED, with a remaining NOTE (N3).** Cost and hardware changes:
- (a) moved to a regular full node with a 1 h limit.
- Expected cost is ≈ 0.75 + 0.5 + 0.06 ≈ 1.3 node-h under a 2.0 cap (R:283-288, R:300-301).
- My check: (b) at 2 × ≈ 901 s is 0.50 node-h, and (c) is 0.06.
- Prototype 2's scope is restricted to the signal loader.

**F5 — RESOLVED.** The comparison is now "comparable", and seeds, driver revisions and background
mode are listed (R:42-44, R:102-109, R:400-402).

**F6 — RESOLVED.** Both f_io definitions are stated, and the smaller is used (R:105-107). On R:44,
"the difference is 69.5 %" follows a sentence quoting 2,561–2,597 against 778. That difference gives
70.7 %, and 69.5 % is the median-task version. This is a wording NOTE only.

**F7 — RESOLVED.** The allocation now reads 121,920 MiB (127.8 GB) at R:112 and R:207, and in
`costs.py:212`.

**F8 — RESOLVED.** The serial bound is described as approximate in both directions and not a strict
upper bound (R:75-78, R:100). The directions are now correct.

**F9 — RESOLVED.** The 213 excluded tasks and the `elapsed > 300 s` rule are stated in the R:86 table
row.

**F10 — PARTIAL.**
- Resolved in the body: R:333-335 limits FAIL to the load phase, and per-step overhead stays
  INCONCLUSIVE.
- Not resolved in the header: the `Disposition` field still says "**FAIL** for any
  wrapper/I/O/transpilation route" (R:21), which the narrowed body no longer supports.
- Correction: copy R:333-335's wording into R:21.

**F11a — OPEN.**
- §11 claims it is repaired "(header, §14, §10)" (R:381-382). In fact the `Resources` field (R:18)
  still lists caps and partial values with no measured elapsed time or CPU, and §14 (R:437-439) still
  reads "*(final figures filled in at delivery)*".
- `DISPATCH.md:82` requires measured elapsed, local CPU, scratch and tracked bytes.
- What was done: sha256 prefixes were added for the pinned inputs (R:17). I checked three against the
  base and they match: A `d9c8160e…`, `sacct_all.txt` `ae806c61…`, `omnifold.py` `e9623412…`.
- Still missing: `2d-unfolding/uq/universes_full_list.txt`, which `Q/profile_from_sacct.py:115` reads,
  is not among the pinned inputs.
- Correction: fill in the measured resources (or mark them as filled at delivery and drop the
  "repaired" claim), and pin the universe list.

**F11b — RESOLVED.** R:338-340 now says B's zero-loop floor is 2.1× the remaining CPU balance and
below the 20,000 annual allocation.

**F12 — RESOLVED, the report is right and the reviewer was wrong** (section above). The committed
bypass mutant is the faithful one (`Q/bench/test_prototypes.py:172-177`) and reports `[]`.

**F13 — RESOLVED** (disclosed at R:198-200).

**F14 — RESOLVED.** The conservative column now uses `a_lo` (`costs.py:322-323`), and the totals were
recomputed above. R:201 states the convention.

**F15 — PARTIAL, and the repair added a false inference (N2).** The test now asserts that the disabled
branch has status 0 and a null address (`Q/bench/test_prototypes.py:141-144`). The report then
concludes that an after-the-fact address check "is therefore vacuous" (R:136-137).

My positive-control probe (`address_probe.py`, 200 k tree) runs the pinned loader with `w_reco`
deactivated and then reads each branch:

| branch | active | address after the loader |
|---|---|---|
| `w_truth` | yes | non-null |
| `MC` | yes | non-null |
| `w_reco` | no | null |

So a post-hoc check of `GetAddress() != nullptr` over the needed branches **would** detect the
forgotten activation, and the committed assertion is in fact evidence of that. Choosing the call-time
guard is still reasonable; the claim that the alternative is vacuous is not.

Correction: replace R:135-138's "leaves no address behind to detect … therefore vacuous" with "leaves
the address null, which a post-hoc check could detect; the call-time guard refuses earlier".

**F16 — RESOLVED** (R:403-404).

## New errors introduced by the repair

**N1 — MINOR. R:113-114.** "165 negweight, 88 %" should read 164 (87.7 %). The percentage stands.

**N2 — MINOR. R:135-138.** The "vacuous" conclusion about a post-hoc address check is contradicted by
the committed assertion together with a positive control (see F15).

**N3 — NOTE. SB1 (a)/(b), R:283-288 and R:303-304.** SB1's success threshold for (b) is
`MaxDiskRead ≤ 10 GB`, and the truth-denominator tree alone is 57.7 GB. Meeting it needs the
prototype-1 branch lists for the truth, background and data loaders, which the report says "this lane
has not written". (a) tests them on Perlmutter only.

The spec should add a precondition: those lists pass the local synthetic byte-equality suite before
submission. Otherwise the first byte mismatch in (a) aborts a paid job for a defect a laptop test
would have caught.

**N4 — NOTE. R:217.** The N = 300 row ("2,059.5; admitted 2,961") is the worst-packing case only, and
it is not labelled as a forecast or as worst packing, unlike R:216.

## Are the narrowed D1 and the revised SB1 supported?

**D1: yes.** As narrowed (R:319-329), the PASS rests on:

- the Perlmutter-measured f_io = 0.695
- whole-file reads in 374/374 tasks
- the code mechanism (no `SetBranchStatus`)
- a byte-verified local prototype

The gain is stated as an Amdahl estimate from a measured f and a local s (2.8–3.2× wall, 2.8× full-node
billing), with SB1 (b) as the measurement. Even at s = 2 on Perlmutter, S = 1.53. This meets Goal 4's
PASS ("bounded opportunity supported by representative measurements"), and the forecasts are kept
outside it.

**SB1: supported as a specification**, subject to the N3 precondition. It is unauthorised (R:274,
R:306-308). It names:

- inputs
- byte identity for (a)
- a tolerance for (b) and (c), now attribution-safe
- hardware
- a cost of ≈ 1.3 node-h under a 2.0 cap
- an abort rule
- success thresholds

**D2, D3 and D4** are as settled in the initial review; D3's header wording is the open item under
F10.

## Findings table

| ID | Status / severity | Evidence | One line |
|---|---|---|---|
| F1 | RESOLVED | R:47-53, R:216 | P05 is now a forecast range of 530 / 927 / 1,853; recomputed |
| F2 | RESOLVED | R:21, R:319-328 | D1 PASS bounded; exact P05 and shared-64 are forecasts |
| F3 | RESOLVED | R:289-299 | SB1 (b) at 128 threads; attribution through (a) |
| F4 | RESOLVED | R:283-288, R:300-301 | regular node, 1 h, ≈ 1.3 node-h; prototype 2 scope fixed |
| F5 | RESOLVED | R:42-44, R:102-109, R:400-402 | "comparable" with the differences listed |
| F6 | RESOLVED (NOTE) | R:105-107; R:44 | both definitions given; R:44's antecedent is slightly ambiguous |
| F7 | RESOLVED | R:112, R:207, `costs.py:212` | 121,920 MiB (127.8 GB) |
| F8 | RESOLVED | R:75-78 | serial bound described as approximate in both directions |
| F9 | RESOLVED | R:86 | 213 excluded tasks disclosed |
| F10 | PARTIAL | R:333-335 vs R:21 | body narrowed; the header still says FAIL for "any wrapper" route |
| F11a | OPEN | R:18, R:437-439, R:381-382 | Resources/§14 still placeholders while §11 says "repaired"; universe list unpinned |
| F11b | RESOLVED | R:338-340 | B below the annual allocation, stated |
| F12 | RESOLVED (report right, reviewer wrong) | `test_prototypes.py:172-177`; `bv_fixed_*.out` | my probe misindexed the branch tuple; the bypass changes 0 keys |
| F13 | RESOLVED | R:198-200 | decoupling disclosed |
| F14 | RESOLVED | `costs.py:322-323`; R:222-224 | 659,900 / 2,725 / 64,018, recomputed |
| F15 | PARTIAL | `test_prototypes.py:141-144`; `address_probe.out` | the null-address assertion actually shows a post-hoc check works |
| F16 | RESOLVED | R:403-404 | concurrent reads disclosed |
| N1 | MINOR (new) | R:113-114 | 165 negweight should be 164 (87.7 %) |
| N2 | MINOR (new) | R:135-138 | "after-the-fact check vacuous" is contradicted by the evidence |
| N3 | NOTE (new) | R:283-288, R:303-304 | SB1 needs unwritten truth/bkg/data branch lists; require local equality tests first |
| N4 | NOTE (new) | R:217 | N = 300 row is worst-packing only and unlabelled |

## Overall verdict

The repair batch resolves all three MATERIAL findings (F1, F2, F3). Every number it moved recomputes
independently, apart from N1's off-by-one count. **No MATERIAL finding remains.** The narrowed D1
PASS and the revised SB1 are supported. D2 INCONCLUSIVE, D3 (body) and D4 FAIL stand.

Remaining, all MINOR or NOTE: F11a is open, F10 is partial in the header, F15 is partial and became
N2, plus N1 and the N3/N4 notes.

None of these changes a disposition, a consequential price or a scope claim. The lane's dispositions
are supported as now stated, provided:
- the header's D3 wording is aligned with §10
- the Resources field is actually filled at delivery rather than marked "repaired"

**F12:** I retract my initial claim. The owner's disposition is correct.

**Re-review resources:** about 12 minutes of wall time (23:42–23:54Z, approximately) and about
1 CPU-minute (≈ 0.02 core-h). No sacct, cluster, GPU or training.
