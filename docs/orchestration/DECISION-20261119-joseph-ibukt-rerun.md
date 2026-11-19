# DECISION 2026-11-19 — Joseph: IBUKT may have the fixes, rehearsals and fresh runs it needs to reach its results

**Recorded by** director-helper-3, for the director, who relayed Joseph's words.

## What led to it

- **The binding and the advance go.** [`state/2d-closeout/IBUKT-BINDING-1.md`](state/2d-closeout/IBUKT-BINDING-1.md) binds the 2D OmniFold and binned-IBU known-truth recovery screen. [`DECISION-20261118b-joseph-ibukt-job-advance.md`](DECISION-20261118b-joseph-ibukt-job-advance.md) gave Joseph's go for the Slurm job in advance.
- **The STOP.** The director reports that IBUKT prepare job 61556304 STOPPED. The oi136 guard refused matplotlib's `fc-list` call after `identity.root` had been written, at about 0.18 node-h. This record cites the director's report; it holds no receipt of the job.
- **The gap.** DECISION-20261118b leaves out, under "Not decided here", a repair or re-run after a STOP.
- **The question.** The director asked Joseph to authorize two things:
  - a guarded rehearsal on a login node, at 0 node-h;
  - a fresh run under a new name, with a fresh envstage.

## Joseph's words, verbatim

2026-11-19, at about 04:20Z:

> yes I approve IBU whatever it needs in order to get results

(`a37db20d0fd0ac093d2db949587d71cb11e2e124b7ec68325cc6492d94df57dd`, the sha256 of the text plus a final newline.)

## What is decided

1. **What IBUKT may have.** Joseph authorizes what IBUKT needs to reach its results:
   - code fixes for STOPs;
   - rehearsals on a login node;
   - fresh runs under new run names, each with its own envstage.
2. **Each code change is reviewed and sha-pinned before it runs.** The director reviews the diff and one independent read, then gives a go for each stage on the pinned sha.
3. **The binding's conditions stand:**
   - fence acknowledgments from cov2d and tier3-design, each under 15 minutes old;
   - job state read with `sacct` only (never `squeue`);
   - `O_NOATIME` reads;
   - CPU only;
   - nothing written to CFS;
   - the cap of 5.90 CPU node-h across all IBUKT runs, including the about 0.18 node-h already spent.

   A projection above the cap still STOPs to the director, who brings it to Joseph with the number. The director reads "whatever it needs" as covering reruns and fixes, not as a silent raise of the cap.
4. **The outcome.** It goes to Joseph and Ben under the declaration's licenses, and no note wording changes (the binding's ruling 4).

## Not decided here

- Any change to the declaration's design, tests or licenses.
- Any note wording.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** Joseph's authorization of IBUKT's fixes, rehearsals and fresh runs, and the conditions above.
- **Not citable for:**
  - a director go on any stage's script sha;
  - any raise of the 5.90 node-h cap;
  - any IBUKT result;
  - any note or paper wording.

Nothing is submitted, deposited or tagged.
