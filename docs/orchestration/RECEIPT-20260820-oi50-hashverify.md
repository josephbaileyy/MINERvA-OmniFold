# Receipt — OI-50: `hsi hashverify` over `mnv-quoted-products-20260812` (2026-08-20)

**Result: PASS. 36 of 36 objects `(md5) OK`, `hashverify` rc 0, 322,306,102,132 B = 300.17 GiB — the
complete archive, nothing skipped. The bytes were read back from tape, not from disk cache.**

**This receipt does not close OI-50.** It supplies the measurement OI-50 asked for. Discharging the
open item is a claim for Joseph.

---

## 1. What ran

| field | value |
|---|---|
| Slurm job | **57287380** |
| QOS / partition | `-q xfer` → partition `cron`, node `login06` |
| account | `m3246` |
| command | `hsi -q "hashverify -R mnv-quoted-products-20260812"` |
| start / end | `2026-08-20T10:32:58Z` → `2026-08-20T10:40:02Z` (**7 m 04 s**) |
| `hashverify` exit status | **0** (recorded unpiped to `hashverify.rc`) |
| artifacts | `/pscratch/sd/j/josephrb/oi50-hashverify/` — `oi50_job.sh`, `hashverify.log`, `hashverify.rc`, `started.marker`, `verified.paths`, `hashed.paths`, `slurm-57287380.out` |

Inside the standing under-12 h approval; launched, not asked.

A start marker was stamped to `started.marker` **before** the verify ran, so a "nothing to do" outcome
could not have been mistaken for a pass:

```
2026-08-20T10:32:58Z
2026-08-20T10:32:58Z marker stamped BEFORE work
```

---

## 2. Coverage — stated as a set identity, not a count match

A count match would be a weak claim (36 of something is not 36 of the right thing). The verified set and
the hashed set were compared directly, after normalising `hashverify`'s absolute `/home/j/josephrb/…`
output against `hashlist`'s archive-relative paths:

```
VERIFIED_N=36   HASHED_N=36
diff verified.paths hashed.paths   → no output, rc 0
```

Independently, the archive's own inventory agrees on both count and bytes:

```
hsi -q "ls -lRD mnv-quoted-products-20260812" | (regular files only)
→ N=36  BYTES=322306102132  GiB=300.17
```

and 322,306,102,132 B = 300.17 GiB reconciles with `hpssquota`'s reading of the same allocation
(**300.17 / 512.00 GiB = 58.6%**), i.e. this archive is the entirety of the HPSS usage.

**Nothing was skipped.** No subsetting, no top-N, no sampling. Every object in
`mnv-quoted-products-20260812` was verified, including the 158.30 GiB
`nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full.root`, whose stored digest
`60c168b9eb3ebc36ead4a63ff97b0abd` was re-measured present in `hashlist -R` and then confirmed by the
verify rather than quoted from the prior report.

**Failures: zero.** `grep -v '(md5) OK' hashverify.log` produced no output and exited 1 — the log is 36
lines and all 36 are `OK`.

---

## 3. It read tape. This is the part OI-50 needed.

A digest match proves nothing about preservation if `hashverify` served the comparison from an HPSS disk
cache copy. Measured, on the largest member:

```
hsi -q "ls -V mnv-quoted-products-20260812/nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full.root"

Storage   VV   Stripe
 Level   Count  Width  Bytes at Level
----------------------------------------------------------------------------
 1 (tape)   1       1  169974191800
  VV[ 0]:   Object ID: 00000001-04-00000001-01f18340b0129564-0004
  Pos:   2466+0   PV List: AH099400
```

**One storage level, and it is tape**, holding all 169,974,191,800 bytes, on physical volume `AH099400`
at position `2466+0`. No disk-cache level is reported. And `hsi -q "dump"` on the same object:

```
TimeLastRead ....................... Thu Aug 20 03:37:52 2026     (local = 10:37:52Z)
```

which falls inside the 10:32:58Z–10:40:02Z job window. So the read happened, during this job, against a
tape-resident object.

**One number I will not over-claim.** 322.3 GB in 424 s is ~760 MB/s aggregate, which is faster than a
single tape drive. `-A` (auto-scheduling of retrievals) is the default and is documented to schedule
retrievals so as to minimise tape mounts, so parallel streams across drives is the plausible
explanation — but I did not measure the drive count and this receipt does not assert it. The elapsed
time and the residency evidence are measured; the mechanism behind the rate is not.

Nothing was staged to, purged from, or migrated within the hierarchy by this job: neither `-C` (purge
after retrieval) nor `-S` (bypass staging) was passed, so the default read path was used and no
storage-hierarchy state was deliberately altered.

---

## 4. Two corrections

### 4a. `hashverify` is not free — the prior audit's mechanism is wrong

`AUDIT-FINDINGS-20260820.md` §1b recommends this verify on the grounds that *"digests are already
stored, so it reads metadata and moves zero bytes."* **That is not what it does.** `hashverify`
*recomputes* the digest from the data, so it reads every byte — 300.17 GiB off tape here. The
recommendation was correct and cheap in wall-clock (7 minutes), but the stated reason was not, and
anyone sizing a larger archive from that sentence would under-budget it badly.

### 4b. The `-A` trap is a flag-meaning error, not a missing capability

Reproduced exactly as reported:

```
hsi -q "hashverify -A mnv-quoted-products-20260812"
→ *** Warning: `mnv-quoted-products-20260812' is a directory - ignored
→ rc 0
```

But the diagnosis "hashverify cannot recurse, so you need an explicit file list" is wrong.
`hashverify`'s **own usage string** lists `-R : recursively traverse directories`, and it works — that
is what this job used. `-A` means **enable auto-scheduling of retrievals**, not *all*. The fix is one
flag.

The reason this is easy to get wrong: hsi's *general* `help` output has a section listing the
recursion-capable commands —

> `cget, chgrp, chmod, chown, cput, delete, get, ls, mdelete, mget, migrate, mput, purge, put, rm, stage, touch`

— and **`hashverify` is absent from it.** That list is incomplete. I believed it first, wrote down that
recursion was unavailable, and had to retract after reading the per-command usage. **The per-command
usage is authoritative; the general help's capability list is not.**

### 4c. And one bug of my own, so the Slurm record is not misread

`sacct -j 57287380` reports **`State=FAILED`**. The verify did not fail. My job script's last command
was `grep -v '(md5) OK' "$OUT/hashverify.log"`, which exits **1** precisely when every file passed, and
that became the script's exit status. The verify's own status was captured separately and unpiped
(`hashverify.rc` → `0`) for exactly this reason, but the job-level state is misleading and anyone
reading `sacct` alone would draw the wrong conclusion. **Read `hashverify.rc`, not the job state.**
A green-looking exit and a red-looking exit can both be artifacts of the last command in a wrapper.

---

## 5. What this supports and what it does not

**Supports:** the tape copy of `mnv-quoted-products-20260812` is intact and verified as of
2026-08-20 — all 36 objects, 300.17 GiB, read from tape and digest-matched. Every "the archive holds X"
sentence downstream of this now rests on a measurement. That includes the archived FPS uncertainty
products (`uq_fps/unified_throw_cov_fps.root`, its `corrected/` twin, and
`uq_universe_fps_covariance_combined_activelat.root`) and the merged plain 5D omnifile.

**Does not support:**

- **Any claim about files not in this archive.** In particular neither FPS event-loop target in
  `AUDIT-FINDINGS-20260820-fps.md` is on tape at all, so this verify says nothing about them.
- **A recovery path for the 12 plain per-playlist 5D files.** They are not in this archive. Blocker (i)
  of that audit's §3 — no second copy anywhere — is untouched.
- **Closing OI-50.** The measurement is done; the discharge is Joseph's call.
- **A permanent guarantee.** This is a point-in-time verify. It does not make the tape copy a tested
  *recovery* path — no object was restored and re-read end-to-end into a usable file; the digest was
  recomputed in place on HPSS.
