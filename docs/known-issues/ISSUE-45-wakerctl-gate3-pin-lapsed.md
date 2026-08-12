## The `wakerctl.py` pin in the Gate-3 queue-latency receipt LAPSED on 2026-07-20 — and three fixes were declined today on the belief it was live (found 2026-08-11)

`docs/orchestration/state/p3f-pet-gate3-queue-latency-reconciliation-56169838.json` records
`control_plane_repair.wakerctl_sha256 = d7c6a215f4a93b6b…`. The actual file is
`04d2e957013b23c2742d50acb9747f0a5a7e8f440c9d8ce8bde953e19eea8c76` — **identical in the local tree,
`origin/main`, and the cluster checkout**, so this is a lapsed *pin*, not a drifted *file*.

**It has been lapsed for three weeks.** `wakerctl.py` last changed at `7e69926` (2026-07-20) and the receipt
last changed at `8c8775f` (2026-07-20) — the same day. The file was edited after the pin was written and the
owning gate was never re-issued.

**Why this matters beyond the mismatch: it was load-bearing in the wrong direction.** On 2026-08-11 this lane
declined **three** separate fixes to `wakerctl.py`, each time reasoning *"editing it moves a sha a receipt
cites"*:

1. content-hashing the `BLOCKED-ON-USER.json` notification key instead of `stat`-ing its mtime (BEN-085);
2. failing closed in `read_scrontab` instead of returning `[]` on a non-zero `scrontab -l` (the entry above);
3. per-watch `try/except` around `evaluate()` in `scan()` — the single point of failure in the durable
   notification path (the entry above).

**All three declines rested on a premise nobody had checked.** The pin they were protecting has not matched
since 2026-07-20, so no receipt's integrity was being preserved by leaving the file alone. The declines were
not thereby *wrong* — a lapsed pin is a reason to fix the pin, not a licence to edit freely — but **the stated
reason was false, and it suppressed three real fixes to shared safety infrastructure for a day.** Third
instance in one day of an unverified premise converted into a decision.

**Disposition, and it is deliberately not taken here.** The two legitimate options are (a) re-run and re-issue
the owning gate so the pin matches, or (b) record the pin as deliberately retired with the reason. **Never
hand-edit the hash** — that is the prohibited act regardless of justification. Option (b) looks right on the
face of it, since the pinned "control plane repair" is three weeks stale and the file has moved on, but
retiring a pin is the gate owner's call and is not a unilateral edit. **Recorded now so the state is honest;
the disposition is open.**

### Addendum (GBDT/P4 lane, same day): the pin RESOLVES, which makes option (b) cheap

The above establishes the lapse from commit *dates* — file `7e69926`, receipt `8c8775f`, same day. Hashing
**every** revision of the file closes the remaining gap, which is whether the pinned sha corresponds to any
real content or to nothing at all:

| revision | sha256 | bytes |
|---|---|---|
| **receipt pin** | `d7c6a215…09bd99c` | 50283 |
| **`8c8775f`** "Reconcile P3F PET queue latency wake" — **the receipt's own commit** | `d7c6a215…09bd99c` | **50283** |
| `442aee3` "Send a 6-hour status digest email" | `bf459853…f7ed90b` | 53113 |
| `7e69926` "Cut over to interim Claude root" = HEAD | `04d2e957…9eea8c76` | 54600 |

**The pin reproduces `8c8775f` byte-for-byte, so the receipt was truthful when written and the exact code the
gate ran against is still in git.** The lapse is therefore *stale pin*, not *dangling pin*: the receipt remains
fully auditable by anyone who checks out `8c8775f`. Two consequences for the open disposition:

- **No re-run is implied.** Option (b) can be as cheap as recording that the pin names a historical revision
  and citing `8c8775f` beside it — the provenance the pin exists to provide is intact, just not at HEAD.
- **The prohibition on hand-editing the hash is now stronger, not weaker.** The pinned value is the one thing
  still carrying information: it identifies the code actually run. Overwriting it with HEAD's sha would
  destroy that and leave a receipt pointing at code its gate never saw.

*Instrument note (BEN-088(vi)):* Session A and this lane both first measured with `shasum` against git, which
is determinism rather than corroboration. Re-measured here with a varied instrument — `openssl dgst -sha256`
read straight off the filesystem, and the receipt value re-extracted with a JSON parser rather than `grep`.
Both agree with the values above.

**Cross-check discipline note:** two sessions independently ran `shasum` against git and agreed. Per
BEN-088(vi) that agreement is determinism, not corroboration — the third confirmation above is the *cluster*
checkout, which is a different tree rather than a second run of the same instrument.
