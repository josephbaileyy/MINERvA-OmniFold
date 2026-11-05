# DECISION 2026-11-05 (later) — Joseph: COV2D's AR23 guard firing is counted as STOP #2 and ruled externally caused, so (c) continues; #765 takes the second reviewer's two phrase changes

**Recorded by** the paper-tighten lane, as director.

## 1. The AR23 guard firing

**What happened.** The G18 pseudo-data job passed this morning. COV2D's AR23 pseudo-data job (60860645, 16:13:57–17:26:00Z,
1.20 node-h) then ended FAILED 5:0 because step A's guard returned STOP.
- **The guard** (`cov2d_pseudo.py:198-335` at M `cb31611c`) stats four inputs' atime at step start (:199) and step end
  (:332), and stops if any differs. It keeps only the list of moved files, not the values.
- **One file moved:** the shared flux constraint, `…/MINERvA101/…/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`.
- **AR23's own read of it** went through O_NOATIME (:203).
- Every other output was clean (`pseudo_a.json` `9e581949…`). The data are unaffected.

**Under `COV2D-BINDING-2.md` ruling 6** (binding 1's rule), "a second STOP ends (c) unless Joseph rules otherwise". STOP #1
was CONTROL-2A, the writer defect fixed in A1.

**The evidence on the cause.** All of it is stat-only, from other lanes' records.
- REF-G1's reader read the file with a plain `read_text()` (`ref_g1_read.py:477-478`; `s1_assemble.py:133-144`) at about
  15:01:52Z (bars) and at 15:18:14Z (read). This is a known REF-G1 read-discipline defect, now under its addendum A1.
- coverage-5b's login-node snapshots show atime 15:01:52Z both at 15:33:38Z and at 16:08:53Z
  (`a2-1/c2probe-run/atime-pre.tsv`, `atime-post.tsv`).
- limitation-resolver's stat at 19:34:06Z shows **15:18:14Z** (1793891894), the time of REF-G1's second read.
- Every lane's records show no access to the file in 16:14–17:26Z, and a read in that window would stamp a later atime.
- **The best-supported explanation, inferred and not measured:** REF-G1's 15:18:14 read became visible to `stat` only after
  16:08, through lazy atime propagation, so the guard saw an earlier external read appear mid-job. Lustre's atime
  settings were not measured, and the guard did not record its values.
  <!-- absence-ok: scopes the inference (what the record lacks: Lustre settings, guard values), not a claim that a result is absent -->

**The independent read** (Sonnet), verbatim with SHA256SUMS, is in
`state/measurement-paper/5d-community-20261024/fd/consult-cov2d-ar23-stop-20261105/`. It recommends counting the firing
and ruling it external, under the conditions below.

### Joseph's answer, verbatim

> Count it, rule external, continue (Recommended)

sha256 of the text plus a final newline begins `5782caed9bcad113`.

The option as put to him: recorded as STOP #2, ruled externally caused by him, for this event only. A third firing, or
any firing on a private file, ends the campaign. AR23 reruns (about 3 node-h) in a new directory under an addendum:
- the shared file is staged as a verified private copy first;
- the guard records its values and is tested to fire and to stay silent;
- REF-G1 is fenced off until fixed;
- Lustre's atime settings are recorded if readable.

### What is decided

1. **The STOP count is two.** STOP #2 is this firing, ruled externally caused by Joseph, 2026-11-05. The ruling covers this
   event only. **A third STOP of any kind, or any guard firing on a private (staged) file, ends (c)** with no further
   reclassification.
2. **(c) continues** under a COV2D addendum A2, written by the cov2d lane, audited and bound by the director, before any
   rerun:
   - **AR23's pseudo-data job reruns** into a new output directory, at about 3 node-h within the 165.8 cap.
   - **The shared constraint is staged first:** an O_NOATIME copy into the run's own directory, its content hash checked
     against the pin. The shared file's atime is stat-recorded before and after staging, and the job reads only the
     copy. Do the same for any other shared input the guard watches.
   - **The guard records its before and after values** (epoch ns) in `pseudo_a.json`, and step B's guard does the same.
     It is tested in both directions: it fires on a plain read of the private copy, and stays silent on a clean run.
   - **The order is fenced:** no REF-G1 run before its addendum A1 is bound. No lane runs code that plain-reads a
     COV2D-guarded input while a COV2D job is running.
   - **Lustre's atime settings** are recorded if they can be read without privilege (for example `lctl get_param` or
     mount options). If they can't be read, the record says so.
3. **The record states:** the classification is inferred; the evidence above; what would falsify it (a non-REF-G1 access
   in the window, or atime settings that rule out lazy propagation); and that under the literal rule the paper would have
   kept "the coverage has not been validated" for the 2D result.
   <!-- absence-ok: quotes the paper's existing limitation sentence as the counterfactual, not an absence claim -->

## 2. #765: the second reviewer read's phrase changes

**The second PRD-referee read** (Sonnet) of the item-4 precision sentences in reading copy 3 is in
`state/2d-closeout/stageF/methods/referee-presentation-20261104/consult-wording-2-20261105/`, verbatim with SHA256SUMS. It
suggests clarity fixes to the two precision sentences, and two phrase changes to the sentence Joseph had approved
(`DECISION-20261105-joseph-765-abstract-and-2d-disclosure.md` item 3).

### Joseph's answer, verbatim

> Accept both changes (Recommended)

sha256 of the text plus a final newline begins `9a44e650c8ada679`.

### What is decided

1. "It was formally adopted after its distance from the published result was known" becomes **"It was adopted in the
   analysis only after that comparison was known"**.
2. "should be read as a consistency check, not a blind validation" becomes **"should be read as a descriptive comparison,
   not a blind validation"**.
3. **The reviewer's clarity fixes** to the LightGBM and closure sentences go in under the earlier approval. Each fact is
   re-checked against its producer before it prints:
   - the 2.70 for the histogram estimator;
   - that 3.66 is exact-split's value;
   - that 5.9 and 0.44 are maxima of the 20-seed mean residual;
   - that the 14 bins come from the closure, not from the data result. The reviewer's "in the data result" would be
     wrong there and is not used.
4. **Then the director checks the built PDF against this record and merges #765 on CI.** Overleaf is re-synced afterwards.

Nothing is submitted, deposited or tagged.
