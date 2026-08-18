# A routing document's CURRENCY is not its CORRECTNESS — and a dispatch inherits its `asOf` without carrying it

**Row:** `BEN-429` (lane C, PET — the id that exhausts block `420-429`). **Date:** 2026-08-18.
**Nothing run; nothing spent. This finding exists because the check was made BEFORE the work, not after.**

---

## 1. What was dispatched, and what was already true

**Dispatched:** a 3–4 hour job on GBDT quarantine cause 1 — *"a static audit of X's path plus one measurement,
the per-band endpoint census"* — from `MAP-20260817-gbdt-note-section-blockers.md`, whose cause-1 row reads
`P` **PARTIAL** (*"no committed per-band endpoint census"*) and `M` **OPEN**.

**Already true, and committed:**

| artifact | state |
|---|---|
| `nd-unfolding/receipt_cause1_endpoint_census_5d.py` | exists |
| `docs/orchestration/PREDECLARE-20260817-cause1-endpoint-census-and-magnitude.md` | exists |
| `nd-unfolding/uq_5d/receipt_cause1_endpoint_census_5d.json` | **exists — the output** |

**The receipt's own verdict block:**

> **`P_leg`: `MET` — per-band census committed, both endpoints present for every pair band, Flux exactly 100
> contiguous.**
> **`M_leg`: `MEASURED` — the number `CRITERIA` says *"does not exist anywhere"* now exists.**

Measured: 44 bands, **42 ± pair bands**, `pair_bands_missing_an_endpoint: []`,
`flux_exactly_100_contiguous: true`. And a **positive control** with `all_targets_reproduced: true`,
reproducing production's committed `reported_bins` `(10694, 65856)` exactly, total syst sqrt-trace to
`3.9e-6` relative and total syst median rel% to `3.0e-5` relative.

## 2. The map is not WRONG. It is STALE by 2 hours 40 minutes.

```
map last touched : b7b7c0c1   2026-08-17T01:44:21-04:00
census receipt   : 75fc88df   2026-08-17T04:24:21-04:00
```

> **The row was ACCURATE WHEN WRITTEN.** So this is nobody's misreading: the map author's cause-1 row was
> true at its timestamp, and the dispatching lane's judgement — *cause 1 rewards PET-path familiarity* — was
> sound. **The defect is that a dispatch INHERITS a map's `asOf` and nothing carries it forward.**

**Distinct from the two neighbouring classes, and the distinction is what makes it actionable:**

| | the document was | the missing thing |
|---|---|---|
| `BEN-228` | **wrong now**, a stale index | re-derive rather than narrate |
| `BEN-239` | **right and unread** | read it against the question |
| **`BEN-429`** | **right AT ITS OWN TIMESTAMP** | **the timestamp itself** |

> **RULE — and it is the executable form, one field: a dispatch derived from a routing document must STATE
> that document's last-touched sha and time.** `git log -1 --format='%h %cI' -- <map>`. **It is the same
> discipline as binding a number to a sha, applied to a TASK ASSIGNMENT rather than to a measurement** — and
> a task assignment is exactly the artifact where nobody thinks to do it, because it reads as an instruction
> rather than as a claim.

## 3. What actually remains — one sentence of judgement, and the receipt's author named it

> **`"M MEASURED is not M ACCEPTABLE. Whether this magnitude leaves X's published numbers standing is a
> physics-presentation judgement and is NOT taken here."`**

**That is the open item.** It is a judgement, not an audit, and it is a different act from the one dispatched.

**Usable figures, so they travel correctly:** total ratios **`1.0594`** (`ep0`) / **`1.0313`** (`ep1`);
per-band trace-ratio medians **`2.10`** / **`1.78`**; `n_above_1` = 37/42 and 36/42.

> **NOT the distribution's `max = 2.53e+22`.** That is a **near-zero-denominator artefact** — the as-built
> diagonal for that band is ~0. **The receipt already declines to report a max and reports a distribution
> instead, honouring `BEN-064`** — so anyone quoting *"up to 2.5e22"* would be quoting a degenerate band past
> a guard that was put there for them.

## 4. Two second-order corrections to the dispatch

**(i) It is NOT cluster-free.** The script's own usage line: *"on Perlmutter, inside the ROOT env; `source
setup_salloc_env.sh`"*, and it opens ROOTs on scratch. **So the map's *"No cluster time"* is wrong, and I
could not have executed it from this host in any case** — verified: no `squeue`, no `sacct`, no `sbatch`, no
`/pscratch`. **The FIT judgement was right; AVAILABILITY is a separate axis and would have stopped the work
at its last step.**

**(ii) `M` does NOT transfer to a replacement product — and the CRITERION says so, not me.**
`CRITERIA-20260811` §2 cause 1 asks for *"sqrt-Tr and per-bin median of X built both ways on **X's OWN
bank**"*.

> **So the magnitude is BANK-SCOPED. The `C` leg (code path, 11 modules) transfers if the candidate shares
> the modules; `P` and `M` do not.** If X is replaced, both must be re-measured on the candidate's bank.
>
> **The mediator raised precisely this before authorising the spend — *"is the `M` leg worth measuring on X at
> all?"* — which was the right question arriving one step after the spend it would have prevented had already
> been made by someone else.** The question was correct and its timing was determined by the same stale map.

## 5. What this cost, and why that is the point

**Nothing.** The four hours were not spent, because the first action taken against the dispatch was to look
for the artifact rather than to start the audit. **Three times today an answering artifact turned out to
already exist; this is the first of the three found BEFORE the spend rather than after it.**
