# FREEZE 2026-08-30 — the deployed tree stays detached at `7ac0edec` until the new rehearsal's F-1(b) is filed

**CITABLE FOR:** the text and scope of the dated freeze rule instantiated below, its expiry
condition, and the supersession of the `aa67c426` freeze.

**NOT CITABLE FOR:** a Gate-1 PASS, a Gate-2 clause, a readiness finding, a fitness finding for the
F-17(b) chain, authorization to submit anything, leg 6, any M(ii) leg, any member, `C_ML`, a
covariance construction or adoption, or any publication claim. **Gate 2 remains FAIL.** A freeze is a
prohibition; it authorizes nothing.

**Instantiated by:** the **DEPLOYMENT PRODUCER** lane for the forward-only k=0 rehearsal, running on
the **claude-school** account, under
[`PROPOSAL-20260830-forward-only-rehearsal.md`](PROPOSAL-20260830-forward-only-rehearsal.md) §2 as
approved — and ruled **delegated** — by
[`DECISION-20260830-joseph-accept-forward-only-rehearsal.md`](DECISION-20260830-joseph-accept-forward-only-rehearsal.md)
(commit `28d406ba`).

---

## 1. THE RULE

> **The deployed tree `/pscratch/sd/j/josephrb/k0r2/clean` stays detached at
> `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` from the filed near-end A-2(a)–(g) declaration until
> F-1(b)'s far-end A-2(a)–(g) measurement for the new rehearsal is producer-filed. No checkout,
> reset, fetch-and-merge, re-declaration, or branch repoint may occur in that directory during this
> interval. It expires when that rehearsal's F-1(b) producer filing is committed — not when its jobs
> merely look terminal.**

That is §2 of the proposal verbatim, with `32e403b8` replaced by `7ac0edec` **as the decision
requires**. The near-end declaration the interval starts from is
[`DECLARATION-20260830-k0-deployment-7ac0edec.md`](DECLARATION-20260830-k0-deployment-7ac0edec.md),
filed 2026-08-30.

**Terminality is measured with complete per-task scheduler accounting for all seven arms, including
dependency reason codes. An empty queue is not the expiry condition** — `combine` uses conjunctive
`afterok` on both uthrow arrays and can read as queued while terminal, or absent while never
submitted.

**THIS FREEZE HAS NOT EXPIRED AND CANNOT YET EXPIRE.** The rehearsal it names has not been
submitted; there are no jobs, so there is no far end, so there is no F-1(b) to file. Anyone reading a
zero-length job list as "terminal" would be committing the error the sentence above exists to
prevent.

## 2. THE SUPERSEDED PIN ROW — old value, new value, reason (OI-123)

A pin may only be **superseded** by a new dated row stating old value, new value and reason, never
silently repointed.

| field | value |
|---|---|
| date | **2026-08-30** |
| pin | the deployed execution tree `/pscratch/sd/j/josephrb/k0r2/clean` |
| **old value** | `aa67c426afaa9b6ca91c9996637a6bade950da9a` |
| **new value** | `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` |
| reason | At `aa67c426` the **deployed** `measure_m1_m6.py` predates the `measurement_wall_clock` and `branch_or_detached` keys that the repaired `compare_m1_m6.py` requires, and `measure_k0_farend_f1b_f17b.sh` takes `MEASURER` from its hardcoded `CODE_ROOT`. That is finding **N1**. Deploying the repaired pair at the same code root makes the **unchanged** wiring resolve the repaired measurer, so both tree documents come from the schema revision the comparator consumes. N1's mechanism is dissolved **without** an override, a `PYTHONPATH` substitution, an `MNV_MEASURER` override, a copied file, an in-place edit, or a schema exception. |
| authority | `DECISION-20260830-joseph-accept-forward-only-rehearsal.md` |
| old pin not destroyed | `aa67c426` remains recoverable from `k0-clean-aa67c426-20260826T075536Z.bundle`, whose six-item reverification recipe was re-run **in full and matched** immediately before the move — [`state/RECEIPT-20260830-aa67c426-preservation-remeasurement.json`](state/RECEIPT-20260830-aa67c426-preservation-remeasurement.json). `refs/tags/freeze/k0-aa67c426` was **not repointed**. |

**The predecessor freeze had already expired before this one was written, and that is on the record
rather than inferred.** `DECISION-20260824-joseph-deployment-freeze-until-f1b.md` / review-contract
§7.0.19 held the tree at `aa67c426` *until F-1(b) is filed*;
[`FINDING-20260829-f17b-deferred-surfaces-and-stale-freeze-prose.md`](FINDING-20260829-f17b-deferred-surfaces-and-stale-freeze-prose.md)
records §7.0.19 as expired, and the producer F-1(b) filing landed at
[`RECEIPT-20260830-k0-f1b-producer-filing.md`](RECEIPT-20260830-k0-f1b-producer-filing.md). So this
deployment did not break a live hold; it replaced a spent one. **Do not read the old freeze's prose,
wherever it still appears, as governing this tree.**

## 3. WHAT ENFORCES IT, STATED HONESTLY

> **THIS IS A PROSE HOLD. IT IS PREVENTIVE BY CONVENTION AND DETECTIVE BY A-2(a) AND A-2(f), AND IT
> IS NOT A MECHANICAL GUARANTEE — do not read it as one.**

What is real, measured 2026-08-30:

- **The working copy is not writable.** `dr-xr-x---` on the root, 184 directories at `dr-xr-x---`,
  1638 regular files at `-r--r-----`, 165 at `-r-xr-x---`, **0 writable files and 0 writable
  directories** outside `.git`. Tool-attested, not hand-argued: `--apply-readonly --require-readonly`
  reported `0 of 1003 protected path(s) changed mode, plus 0 non-tracked writable file(s)`.
- **HEAD is detached and there is no branch to fast-forward.** `refs/heads` is **empty** and the tree
  carries **no remote**. Those two absences are what removed the mechanism of the 2026-08-23
  excursion, in which eighteen routine advances in under two days ended with the deployment on the
  wrong sha.
- **A-2(a) detects a moved HEAD** and **A-2(f) detects a moved source byte**, both against digests
  recorded in the declaration, and both with firing controls demonstrated in §7 of that document.

What is **not** real, and must not be claimed:

- **`.git` is writable — `drwxrwx---`, by ruling.** §11.1.1 of
  `DECISION-20260825-joseph-gate2-fail-and-four-rulings.md` orders that it **not** be `chmod`'ed and
  **reverted if it was applied**, for two reasons: it is an accident guard the tree owner undoes in
  one command, and it breaks `git worktree add`, this repo's mandated audit mechanism. Verified NOT
  applied here: `.git` measured `drwxrwx---` before and after, `.git` was pruned from **both**
  recursive mode changes, and the pruning was **proven** by an unchanged writable-file count inside
  it rather than asserted. So `update-ref`, `fetch`, `gc` and `checkout --detach` are all still
  mechanically possible in that directory. **The freeze raises their cost and makes them leave a
  trace; it does not prevent them.**
- **The owner may `chmod` the working tree back, and root ignores mode bits.** A-2(g) prevents
  accidents and makes deliberate mutation visible in A-2(f). It is not a security boundary.
- **The tree carries eleven refs, and a tag is checkoutable.** Ten are `refs/tags/evidence/*` at
  commits that are **not** the pin — other lanes' provenance anchors, not this lane's to remove — so
  `git checkout <evidence tag>` remains a live, never-exercised route out of the pin. The eleventh is
  the freeze ref and points **at** the pin, so it is not such a route.

## 4. THE NEW FREEZE REF, AND THE DECAY IT IS BUILT AGAINST

```
ref     = refs/tags/freeze/k0-7ac0edec
target  = 7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b
kind    = lightweight, LOCAL ONLY, deliberately not pushed
present in:
  /pscratch/sd/j/josephrb/k0r2/clean            (the deployed tree the freeze is about)
  /pscratch/sd/j/josephrb/MINERvA-OmniFold      (the canonical cluster checkout, and the bundle source)
bundle  = /pscratch/sd/j/josephrb/k0r2/freeze-receipts/k0-clean-7ac0edec-20260829T233037Z.bundle
          82761577 bytes, sha256 514bd46e70bb828d6116f98cbb2d660b74fd43be704dcdf067145dc578a0280d
```

`git bundle list-heads` was asserted to contain the **exact row**
`7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b refs/tags/freeze/k0-7ac0edec`, count **1**, with the script
refusing otherwise — an exact-row match and not a substring search, because a substring can match the
wrong row in either direction. Recovery from the bundle **alone** was **tested**: `clone --no-local`
→ `fsck` → detached checkout of the freeze ref, rc=0/0/0, HEAD the pin, tree `5c23cad6…`, porcelain
**0**, 1804 tracked files, and the recovered clone independently measured **820 files /
`8d036d94…`**.

**`--all` would still not do.** That clone has no branch and no remote-tracking ref, and
`merge-base --is-ancestor 7ac0edec <evidence tag>` is **FALSE for all ten**, so `git bundle create
--all` would verify, hash, and contain nothing to recover. `git bundle verify` does not catch this: it
checks well-formedness and prerequisites, not that the bundle holds what you meant.

**WHY THE REF IS IN TWO REPOSITORIES.** The `aa67c426` freeze ref lived in exactly one working
checkout — `/global/u2/j/josephrb/mnv-work/MINERvA-OmniFold`, per the 2026-08-26 receipt's
`generated_from`. **That path no longer exists**, and when this deployment began the tag
`refs/tags/freeze/k0-aa67c426` was present in **no live cluster repository** (checked in the
canonical checkout and in `k0r2/bare.git`; the frozen deploy's own ten-ref set never held it).
Recoverability survived only because recipe items 5 and 6 read the ref out of the **bundle**. It has
since been re-created at the same commit in the canonical checkout — a restoration of the same
name-to-bytes mapping, **not** a repoint. **A single-copy, unpushed, working-checkout-resident ref is
preservation only for as long as that checkout exists, and nothing made its disappearance
detectable.** Two copies plus an asserted presence in the bundle is the fix.

## 5. WHAT THIS FREEZE DOES **NOT** LICENSE, AND WHAT IT DOES NOT BLOCK

**Does not license.** Being deployed and frozen at a repaired pin is not fitness, readiness, or
permission. Step 4 of the approved sequence is conditional in its own words — *"if and only if all
three pass, submit the seven bounded arms"* — the three being a fresh independent full-chain **FIT**,
the §10.1 readiness confirmation, and **Gate-1 PASS**. **None has happened.** The latest independent
grade remains `F17B-REPAIRED-CHAIN: NOT FIT` on finding `N1`, and *being writable does not convert
that grade into FIT*. **Step 3 is where a fresh reviewer — neither the implementer, nor
`agy-capacity-probe`, nor the grader of the 2026-08-28 round — decides whether the chain is now FIT.
The lane that produced this deployment is by construction ineligible.**

**Does not block.** Read-only inspection, `git worktree add` for audit work (which is exactly why
§11.1.1 forbids locking `.git`), and the A-2 re-measurements this rule itself demands are all
expected activity in that directory. What is prohibited is **moving it**: `checkout`, `reset`,
`fetch`-and-merge, re-declaration, branch repoint.

**One consequence worth stating for whoever writes the new run driver.**
`measure_k0_farend_f1b_f17b.sh:71` prints `ON BRANCH -- would violate the 7.0.19 freeze`.
`FINDING-20260829` correctly recorded that §7.0.19 had expired and that the check was still worth
keeping while its stated reason was stale. **Under this rule the reason is live again** — an on-branch
deployed tree violates *this* freeze — but **the message's sha and clause number are now wrong.**
**It was deliberately not edited**: that file is a tracked `.sh`, so any edit moves the A-2(f) listing
digest and falsifies the declaration this deployment exists to file. Fix it, if at all, with the new
run driver, under its own grade — never inside a frozen interval.

## 6. ROUTES

- The declaration this interval starts from:
  [`DECLARATION-20260830-k0-deployment-7ac0edec.md`](DECLARATION-20260830-k0-deployment-7ac0edec.md)
- Bundle, tested recovery, the six-part command record, the `.git` delta, and the reverification
  recipe:
  [`state/RECEIPT-20260830-k0-deployment-and-freeze-bundle-7ac0edec.json`](state/RECEIPT-20260830-k0-deployment-and-freeze-bundle-7ac0edec.json)
- The preservation precondition that had to pass before anything was made writable:
  [`state/RECEIPT-20260830-aa67c426-preservation-remeasurement.json`](state/RECEIPT-20260830-aa67c426-preservation-remeasurement.json)
- The superseded freeze and its expiry:
  [`DECISION-20260824-joseph-deployment-freeze-until-f1b.md`](DECISION-20260824-joseph-deployment-freeze-until-f1b.md),
  [`FINDING-20260829-f17b-deferred-surfaces-and-stale-freeze-prose.md`](FINDING-20260829-f17b-deferred-surfaces-and-stale-freeze-prose.md),
  [`RECEIPT-20260830-k0-f1b-producer-filing.md`](RECEIPT-20260830-k0-f1b-producer-filing.md)
