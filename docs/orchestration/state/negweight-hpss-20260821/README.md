# Raw evidence — negweight HPSS durability, 2026-08-21

Cluster-side artifacts, copied verbatim from
`/pscratch/sd/j/josephrb/negweight-durability-20260821/`. The derived record is
`../negweight-hpss-durability-20260821.json`; the human receipt is
`../../RECEIPT-20260821-negweight-hpss-durability.md`.

| file | what it is |
|---|---|
| `inventory.tsv` | the ruled 247: relpath, size, sha256, md5, mtime. Measured on the source tree. |
| `sidecar_inventory.tsv` | the 29 beside-scope files, same columns. NOT part of the ruled 247. |
| `markers/*.hpss.json` | per-object local vs **server-side** md5 and the size read back from HPSS. A marker exists only where those matched. |
| `archive_listing.txt` | `hsi ls -lRD` — the archive's own inventory, independent of this job's counters. |
| `hashverify.log.txt`, `hashverify.rc` | `hsi hashverify -R`, rc captured **unpiped**. |
| `hashlist.log.txt`, `verified.paths`, `hashed.paths`, `coverage.diff`, `coverage.rc`, `coverage.verdict` | coverage as a path-set diff, with a non-empty floor on both sides. |
| `residency_after_migrate.txt` | `ls -V` + `dump` per object after `hsi migrate -R`: bytes at the tape level, PV, position, `TimeLastRead`. |
| `residency_negative_control.txt` | the instrument shown able to FAIL: a freshly-put object reporting zero bytes at the tape level, beside an archive object reporting its full count. |
| `migrate.rc` | `hsi migrate -R` exit status. |
| `quota_before.txt`, `quota_after.txt` | `hpssquota -u josephrb`, not `hsi`. |
| `provenance_summary.txt`, `sacct_producers.txt` | `sacct` over 2026-07-07..07-12. These are what show the frozen state record's job list to be a launch plan rather than a record. |
| `preserve_nojob.log.txt` | the preservation run's own log, both invocations appended. |

## One artifact is deliberately misnamed, and this is the note that says so

`residency_before_migrate.CLOBBERED-SEE-README.txt` **does not contain a pre-migration
reading.** The preservation script is idempotent and was run twice — the first run put and
migrated, the second run (with a repaired coverage parse) re-executed the residency block and
**overwrote the first run's pre-migration file with a post-migration reading under a "before"
name.** It is kept, renamed, rather than deleted, because a deleted artifact leaves no trace of
the hazard.

The pre-migration state is instead evidenced by `residency_negative_control.txt`, which measures
it live on a throwaway object. That is the stronger form anyway: it is a reproducible
measurement rather than a reading whose label has to be trusted. The script now writes
run-stamped residency filenames so this cannot recur.

## Three files carry a `.log.txt` suffix, and that is not cosmetic

`.gitignore:15` is a blanket `*.log`. A plain `git add` of this directory **silently skips**
`hashverify.log`, `hashlist.log` and `preserve_nojob.log` — which would have committed a receipt
citing `hashverify.log` as its tape-read evidence while git carried no such file. `git add` reports
nothing when it skips an ignored path, and `verify_receipt_artifacts.py` does not cover this case:
its rule is scoped to binary extensions (`.root`, `.npz`, `.h5`, …) under
`docs/orchestration/state/`, so a `.log` walks straight past it.

They are **renamed, not force-added**, because `git add -f` fights the ignore rule and leaves the
next lane to rediscover the trap. The bytes are unchanged; the cluster-side names are preserved
inside the new ones. sha256 as renamed:

```
fa19e9eba43b6a63e28a732e3c6d2fcbe8cee9d67d0717f5143335322fe3903e  preserve_nojob.log.txt
20c24a32cfa46c36b5220757b2f670c0e1654bbfa4496942cec5baf2461b3c86  hashlist.log.txt
8bfaee3386cee896e1cc6821308336d2638d8c089b9787765a0611da486ca139  hashverify.log.txt
```

The manifest builder resolves either name (`_evidence()`), so it reads the cluster directory and
the committed directory alike.
