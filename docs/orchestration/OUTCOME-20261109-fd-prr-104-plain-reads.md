# OUTCOME 2026-11-09 — FD-PRR §10.4 deviation: 72 of 181 completed tasks read four rho npz plainly, unstaged

**Recorded by** the valid-region lane (session director-helper-2), at the director's ruling of 2026-11-09. The A4 trace
on the prr_ibu run path found this (`FD-PRR-ADDENDUM-A4`, in preparation). This is a process record. The director
reports it to Joseph as process hygiene, not a result question. It blocks nothing.

**CITABLE FOR:** the deviation from `FD-PRR-DECLARATION.md` §10.4 and its extent. That is 72 of the 181 tasks of
prr_dry, prr_iter, prr_cap and prr_misc, the files they read, and how the count was derived.

**NOT CITABLE FOR:**
- any claim that a product of those jobs is affected;
- any claim that those reads complied with §10.4.

## The rule

`FD-PRR-DECLARATION.md` §10.4 (`state/measurement-paper/5d-community-20261024/FD-PRR-DECLARATION.md:575` @
ef9411a3) says: "Every file outside the deploy that the jobs read is staged once". Each staged file is copied once
through O_NOATIME, with stat records before and after. Every task then reads only the staged copies. The declaration's
compliance row (`:673` @ ef9411a3) lists "every shared read staged once through O_NOATIME". This record does not
rewrite that row. It records where the row did not hold.

## What happened

- **The files.** Four fine-ratio hypothesis files are in the repository. They name their rho arrays by an absolute
  shared path, in `rho_npz.path`:

  | hypothesis (repository) | rho_npz.path | rho_npz.sha256 |
  |---|---|---|
  | `docs/orchestration/state/s5p/ratios/nullsF/null-genie_cv-F.json` | `/pscratch/sd/j/josephrb/s5p-20260926/ratios/nullsF/rho-genie_cv-F.npz` | `124e726163b38d24…` |
  | `…/null-genie_mec-F.json` | `…/rho-genie_mec-F.npz` | `2945a15a54dcf71f…` |
  | `…/null-gibuu_cv-F.json` | `…/rho-gibuu_cv-F.npz` | `d8f52112b010e5ad…` |
  | `…/null-nuwro_cv-F.json` | `…/rho-nuwro_cv-F.npz` | `c5e10bd0edf70b8a…` |

  The paths and shas are as committed @ 6727020a, the code all four jobs ran (each job's .out line 1, `pin=6727020a…`,
  in `fd/receipts-prr/{dry,iter,cap,misc}/cluster/logs/`).
- **The read.** The runner reads the hypothesis before its seed loop: `s5p_nullexp.py:298-299` @ 6727020a,
  `s5p_truths.hypothesis_weight`. For the fine kind, `s5p_truths.load_fine_rho` (`s5p_truths.py:238-242` @
  6727020a) hashes `rho_npz.path` and then loads it with `np.load`. Both are plain opens, in place.
- **Not staged.** None of the four is in `prr_probe.SOURCES` (`nd-unfolding/prior_retention/prr_probe.py:608-619` @
  6727020a), so none was staged. The four jobs ran with no read guard, so nothing refused the reads.
- **The truths.** The truths whose hypothesis is a fine ratio are A7_genie_cv, A7_genie_mec, A7_gibuu and A7_nuwro,
  at every level that runs them.

## The extent

| job | job id | tasks | tasks reading a rho npz | genie_cv | genie_mec | gibuu_cv | nuwro_cv |
|---|---|---|---|---|---|---|---|
| prr_dry | 61022062 | 15 | 1 | 0 | 0 | 1 | 0 |
| prr_iter | 61024185 | 44 | 16 | 4 | 4 | 4 | 4 |
| prr_cap | 61028298 | 29 | 8 | 2 | 2 | 2 | 2 |
| prr_misc | 61030122 | 93 | 47 | 7 | 7 | 26 | 7 |
| **all** | | **181** | **72** | 13 | 13 | 33 | 13 |

**How the counts were derived.** They come from the four queues as committed in
`state/measurement-paper/5d-community-20261024/fd/receipts-prr/dry/cluster/queues/`. Their sha256 begin 9fb47269,
e0f02c1c, 480b124d and 4ed15792, the digests each connect pinned. Each task line is counted by its `--hypothesis`
argument.
- **Fine-ratio tasks:** a task is counted when its argument is under `nullsF/`.
- **All tasks:** the totals count non-comment lines with more than four columns.
- **Every counted task ran.** Each job ended COMPLETED with DONE showing every task ended rc 0
  (`fd/receipts-prr/{dry,iter,cap,misc}/README.md`). The hypothesis is read before the seed loop, so every counted
  task made both reads, the hash and the load.

Search: `git show ef9411a3:<queue> | awk -F'\t' '!/^#/ && NF>4 {for(i=1;i<=NF;i++) if($i=="--hypothesis" && $(i+1) ~ /nullsF/) print}'` over dry, iter, cap and misc.tsv gives 1, 16, 8 and 47 lines; without the nullsF test, 15, 44, 29 and 93 @ ef9411a3

## What the reads were, and what they were not

- **Content-pinned.** `load_fine_rho` refuses unless the file's sha256 equals `rho_npz.sha256` in the committed json
  (`s5p_truths.py:240-241` @ 6727020a). Every one of the 72 tasks ended rc 0, so every rho array read was the committed
  one. The products are the products of the intended inputs.
- **Not staged, and not through O_NOATIME.** Every read was in place and plain. Each one can have moved the file's
  atime on pscratch, which is the purge clock §10.4 protects. No stat record was taken before or after. For these four
  files, §10.4's staging and atime rule did not hold.
- **The other inputs** of these jobs are not covered by this record. They were staged as declared: the six SOURCES
  files, their stat records and `stage.json`, in `fd/receipts-prr/dry/`. The A4 receipts carry a search of the
  runner path for any other absolute /pscratch or /global path. It is cited there, not here.

## What follows (the director's ruling)

- **Route 2 is brought inside §10.4 by addendum A4.** It stages exactly these four files once, through O_NOATIME,
  into `$OUT/stage/s5p-nullsF/`. Stat records are taken before and after, and each copy's sha256 is checked against
  its json. The staging is recorded in a stage-A4 record beside `stage.json`. prr_ibu's capture then reads the staged
  copies. The json files and `s5p_truths.py` are unchanged.
- **The director's ruling (2026-11-09):** the four completed jobs' products stand and are not rerun; each of these
  reads was sha-verified against the committed hypothesis, so the deviation concerns the staging and atime rule only.
- **The compliance row** at `FD-PRR-DECLARATION.md:673` is not rewritten. This record points at it.
