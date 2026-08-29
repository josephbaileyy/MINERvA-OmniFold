# DECLARATION 2026-08-30 — the forward-only rehearsal's deployment sha, and A-2(a)–(g) filed against it

**CITABLE FOR:** the constitution of the execution tree `/pscratch/sd/j/josephrb/k0r2/clean` at
`7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b`, measured 2026-08-29T23:26Z–23:33Z
(2026-08-30 Europe/Paris), and for the A-2(f) listing digest and file count that the new rehearsal's
F-1(b) far-end measurement must reproduce.

**NOT CITABLE FOR:** a Gate-1 PASS, a Gate-2 clause, a readiness finding, a fitness finding for the
F-17(b) chain, authorization to submit anything, leg 6, any M(ii) leg, any member, `C_ML`, a
covariance construction or adoption, or any publication claim. **Gate 1 does NOT pass at this sha and
has not been graded here. Gate 2 remains FAIL.**

**Producer:** the **DEPLOYMENT PRODUCER** lane for the forward-only k=0 rehearsal, running on the
**claude-school** account. **This is a PRODUCER filing: this lane implemented the deployment and is
therefore INELIGIBLE to perform step 3's fresh independent full-chain grade.**

**Authority:** [`PROPOSAL-20260830-forward-only-rehearsal.md`](PROPOSAL-20260830-forward-only-rehearsal.md)
§1, approved as a unit and ruled **delegated** by
[`DECISION-20260830-joseph-accept-forward-only-rehearsal.md`](DECISION-20260830-joseph-accept-forward-only-rehearsal.md)
(commit `28d406ba`).

---

## 1. THE DECLARED SHA — and why it is `7ac0edec`, not the proposal's `32e403b8`

```
sha    = 7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b
tree   = /pscratch/sd/j/josephrb/k0r2/clean
state  = DETACHED (no branch exists in that tree at all)
```

The proposal names `32e403b84e9e8f9d9bc435028749f896653c7a43` throughout, because that was `main`'s
tip when it was drafted. **The decision supersedes it**, and every place the procedure said
`32e403b8` was executed at `7ac0edec` — including the new freeze rule's text.

**Measured, not assumed:** the only paths differing between the two shas are three `.md` files and
`docs/orchestration/MANIFEST.tsv` — **zero `.py`, zero `.sh`**. `mnv_source_manifest.py:70` sets
`SOURCE_SUFFIXES = (".py", ".sh")`, so the A-2(f) source listing digest is **identical at both
shas** and the choice changes no measurement. Independently: `nd-unfolding/mnv_source_manifest.py` is
the **same blob** `f643a1ec` at `aa67c426`, `32e403b8` **and** `7ac0edec`, so the instrument itself is
not a variable in this comparison.

**The four pinned artifacts of the proposal's §1 table, re-measured from the git objects at
`7ac0edec` rather than from a working copy:**

| artifact | sha256 | bytes |
|---|---|---:|
| `docs/orchestration/measure_m1_m6.py` | `ce52ff773c5261ed54cfc63150ef740785d5ed5aa81c9ae271d935f0efc3ed51` | 14108 |
| `docs/orchestration/compare_m1_m6.py` | `28490539b60c4a790f77b5dd1070dc7e9d192efabebee640662d9496cf465242` | 67440 |
| `docs/orchestration/measure_k0_farend_f1b_f17b.sh` | `ad1a8b6405e55094afbaa9cab00b0a2b7afb0fa52835653d147dad6e92b84775` | 16358 |
| `docs/orchestration/m1m6_expected_differences.json` | `13547f3f21333ea0545b232e7ca28847401cd4318fbf13e4e75c5276765efc2c` | 11302 |

All four equal the proposal's table exactly. **This declaration does not name its own commit**, by the
same convention as its predecessors: no commit can contain its own sha, and a declaration is
paperwork *about* an execution tree. **A-2(a)'s falsifier is one command:**

```bash
GIT_OPTIONAL_LOCKS=0 git -C /pscratch/sd/j/josephrb/k0r2/clean rev-parse HEAD   # must be 7ac0edec…
```

## 2. A-2(a)–(g), EACH MEASURED IN ITS OWN INVOCATION

**Interpreter NAMED, not assumed:** `/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3`,
**Python 3.11.14**. The login `/usr/bin/python3` is 3.6.15 and exits **1** with a `SyntaxError` on
`from __future__ import annotations` — neither the documented `rc=2` nor a clause result.

**Instrument NAMED, because a flag without its file is how four clauses once read as FAIL with none
tested:** the `--require-*` flags live in **`nd-unfolding/mnv_source_manifest.py`**, not in
`mnv_guarded_run.py`. The copy used was the one **inside the deployed tree**, blob `f643a1ec` ==
`git rev-parse HEAD:nd-unfolding/mnv_source_manifest.py`.

| # | requirement | result | evidence |
|---|---|---|---|
| **a** | `rev-parse HEAD` equals the declared sha | **MET** | `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b`; raw `.git/HEAD` is that bare sha and not a `ref:`; `symbolic-ref -q HEAD` **rc=1**; `branch --show-current` empty; **`refs/heads` is empty** and the tree carries **no remote** |
| **b** | `git status --porcelain` emits zero lines | **MET** | `0`, counted with `wc -l` on a **file**, never `$?` after a pipe; `--require-clean` **rc=0**. `status --porcelain --ignored` is **also 0**: the tree holds no untracked and no ignored file at all |
| **c** | a checkout by the guard's own definition | **MET** | `--require-checkout` **rc=0**; `is_checkout true`, markers `["VALIDATION_LEDGER.md", "nd-unfolding"]` |
| **d** | no nested checkout beneath it | **MET** | `--require-no-nested-checkout` **rc=0**; `nested_checkouts []` |
| **e** | not nested inside another checkout | **MET** | `--require-not-nested` **rc=0**; `enclosing_checkout null` |
| **f** | full source manifest over tracked `*.py`/`*.sh`, plus one digest over that list | **MET** | `--compare` **rc=0**, `SOURCE MANIFEST IDENTICAL (820 files, 8d036d9466eaff6ad1f6b62231b09a1dd9798c095d2d0f84ea96ba01a51fc8ea)` |
| **g** | write protection applied | **MET** | `--require-readonly` **rc=0**; `mode_writable []`, `uid_writable []`, `other_writable []`; and independently a filesystem walk found **0 writable files and 0 writable directories** outside `.git` |

**Every rc taken with `--write` or `--compare`.** Run bare the tool answers
`COULD NOT LOOK: give --write and/or --compare; measuring nothing and exiting 0 is exactly the shape
this file exists to prevent` at **rc=2** — re-confirmed as a live control here, not quoted from
history. **rc=2 means "could not look" in BOTH directions:** it is not a pass and it is not a fail.

**Consolidated arm:** all five `--require-*` plus `--compare` in **one** invocation, **rc=0**,
`SOURCE MANIFEST IDENTICAL (820 files, 8d036d94…)`. Each clause was **also** measured separately so
that one rc means one clause.

## 3. THE DECLARATION FILE, AND THE TWO DIGESTS THAT ARE NOT INTERCHANGEABLE

```
path             = /pscratch/sd/j/josephrb/k0r2/declarations/7ac0edec/source-manifest.json
mode             = -r--r-----   (440, matching the aa67c426 declaration's mode)
bytes            = 268643
file sha256      = ca6a8f2b0c8b73be9d69b6f8d2f97e5f63b1697571954d2db8f9227c8d11a032
schema           = mnv_source_manifest/1
built_at_utc     = 2026-08-29T23:28:39.524850+00:00
head             = 7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b
suffixes         = ['.py', '.sh']
file_count       = 820
listing_sha256   = 8d036d9466eaff6ad1f6b62231b09a1dd9798c095d2d0f84ea96ba01a51fc8ea
dirty_count      = 0
```

**`file sha256` hashes the JSON file's bytes; `listing_sha256` is the digest over the sorted
`<sha256>  <relpath>` listing.** They are different objects and must never be substituted for each
other — the 2026-08-30 F-1(b) filing had to say the same thing about the `aa67c426` pair.

**DISCLOSURE — the baseline JSON carries a MID-DEPLOYMENT `constitution` block, and it is not the
A-2 result.** The proposal's ordering writes the declaration at part 4, **before** part 5 re-applies
write protection, so this file records `mode_writable` with 1003 paths and `other_writable` with 983:
the tree *as it stood mid-deployment*. **The A-2(c)(d)(e)(g) results are the part-6 measurements in
§2 above**, taken after protection. The declaration's load-bearing content — the per-file digests,
the listing digest, the file count and the pin — is unaffected by mode bits. The same disclosure is
carried in the file's own `label` field, so it travels with the artifact rather than only with this
document.

## 4. WHY 820, AND THE EXPIRY CLAUSE

`aa67c426` → **782**; `7ac0edec` → **820**. The delta is arithmetic, not an estimate: `aa67c426` →
`7ac0edec` **adds 221 tracked paths and deletes none**, and **38** of the 221 are `.py` or `.sh`.
782 + 38 = 820.

**Falsified by any add or removal of a tracked `*.py` or `*.sh`, and by nothing else.** A
modification is count-neutral and moves only the digest. A **rename** moves the digest even when
every file's own digest is unchanged, deliberately, because a rename is how a hijack arrives without
a content diff.

**Re-run before the first `sbatch` and again after the last leg. DO NOT INHERIT THESE NUMBERS.**

## 5. THE DIGEST WAS PREDICTED BEFORE IT WAS MEASURED, AND THE PREDICTOR HAS A POSITIVE CONTROL

Stated because "the tree measured what the tree measured" is not independent of the tree.

Before anything on the cluster was touched, the A-2(f) listing digest for `7ac0edec` was computed
**off-cluster from git objects alone** — `git ls-tree -r` for the path set, `git cat-file blob` for
the bytes, sorted by relpath, `<sha256>  <relpath>\n` per line, sha256 of the concatenation:
**820 files, `8d036d9466eaff6ad1f6b62231b09a1dd9798c095d2d0f84ea96ba01a51fc8ea`**.

**Positive control for that script:** the identical code run at `aa67c426` reproduced **782** and
**`fa3489e22168954bebcc9a602338d924582fd231643bfa285b3a9225e7535420`** — the values
[`DECLARATION-20260823-k0-candidate-aa67c426.md`](DECLARATION-20260823-k0-candidate-aa67c426.md) §2
and [`RECEIPT-20260830-k0-f1b-producer-filing.md`](RECEIPT-20260830-k0-f1b-producer-filing.md) §2
both record. A predictor that could not reproduce a known answer would not be worth running.

The deployed tree then measured 820 / `8d036d94…`, and **so did the clone recovered from the new
bundle alone**. **Three independent agreements from three different object stores**, which is what
makes A-2(a) plus A-2(f) a statement about the bytes rather than a statement about one repository.

## 6. WHAT ELSE WAS VERIFIED AT PART 3, AND ITS HONEST LIMIT

`nd-unfolding/pet/verify_executing_copy_is_committed.py` — the copy inside the deployed tree, blob
`c9fb9dd0` == `git rev-parse HEAD:nd-unfolding/pet/verify_executing_copy_is_committed.py` — was run
with **one `--pair` per tracked `.py` and `.sh` at the pin: 820 pairs, the whole population and not a
named subset**. Result **rc=0, `820 of 820 CURRENT`**: 0 `STALE_BUT_COMMITTED`, 0 `UNCOMMITTED`,
0 `IN_ODB_UNREACHABLE`, 0 `MISSING`. Elapsed 7.07 s.

**Its limit, stated so the result is not over-read:** `--repo` was the deploy tree itself, so this
answers *"are these bytes HEAD's bytes for these paths"* and **not** *"is this tree authoritative"*.
Run 4 printed `5 of 5 CURRENT` honestly while the modules loaded came from elsewhere. The second
question is answered by A-2(a) plus §5's off-cluster cross-check, not by this tool — and neither is a
substitute for the OI-136 guard's *"which files did the interpreter actually load"*.

## 7. THE CONTROLS THAT FIRE — because a clause only ever observed passing is decoration

| clause | fires on bad | silent on good |
|---|---|---|
| **f** | `--compare` against the **superseded** `declarations/aa67c426/source-manifest.json` → **rc=3 MEASURED DIFFERENCE**, `SOURCE MANIFEST MOVED`, recorded `fa3489e2…` at HEAD `aa67c426…` vs live `8d036d94…` at HEAD `7ac0edec…`, 25 `ADDED` lines printed. rc=3 is deliberately not rc=2 | `--compare` against the new declaration → **rc=0 IDENTICAL** |
| **g** | `chmod u+w nd-unfolding/mnv_source_manifest.py` (440 → 640) → `--require-readonly` **rc=2**, `1 tracked source path(s) still carry a write bit`. **One bit on one file is enough** | `chmod a-w` restores 440 → **rc=0**, and the tree returns to the state §2 records |
| **g** (whole-tree arm) | run at part 3 while the tree was deliberately writable, **rc=2** with **both** arms firing: 983 non-tracked paths and 1003 tracked-source paths carrying a write bit | — |
| **b, c, d, e** | in a disposable `mktemp -d` fixture: (b) **rc=2** on a dirty tree; (c) **rc=2** on a marker-less git tree; (d) **rc=2** on a tree with a checkout nested beneath it, naming `['inner']`; (e) **rc=2** on a tree nested inside a checkout, naming the enclosing path. Fixture removed | the rc=0 rows in §2 |

**THE LIMIT OF THE FIXTURE ARMS, because it is the easy thing to over-read.** They prove the
**instrument's** arms fire. They say **nothing** about the deploy tree. The claim about the deploy
tree rests entirely on the rc=0 measurements taken **on it**. A control proving the instrument works
leaves the claim untested.

## 8. WHAT THIS DECLARATION DOES NOT DO

- It does **not** pass Gate 1, and no prior round's PASS transfers to this sha.
- It does **not** move Gate 2, which remains **FAIL**, and it discharges no clause.
- It does **not** convert `F17B-REPAIRED-CHAIN: NOT FIT` into FIT. The deployment removes finding
  **N1's mechanism** — the hardcoded `CODE_ROOT` now resolves the repaired measurer, so both tree
  documents are produced by the schema revision the comparator consumes. **Whether the chain is now
  FIT is step 3's question, and this lane is ineligible to answer it.**
- It authorizes **no** Slurm submission. **None was made.** `squeue --me` showed one row throughout,
  the long-held cron waker `57712764` (PD, BeginTime), which is not this lane's.
- It does not touch a `.py` or `.sh` byte anywhere. **No in-place edit, copied file, `PYTHONPATH`
  substitution, `MNV_MEASURER` override, or schema exception was used** — the proposal forbids all
  five and none was needed.
- It does **not** file the new rehearsal's **F-1(b)**. The new freeze expires on that filing; it
  belongs to the rehearsal, not to this deployment.
- It does not `chmod` `.git`. Per §11.1.1 that ruling was honoured and **verified NOT applied**:
  `.git` measured `drwxrwx---` before and after, with `.git` pruned from **both** recursive mode
  changes and the pruning **proven** by an unchanged writable-file count inside it, not asserted.

## 9. ROUTES

- Bundle, tested recovery, the new freeze ref, the six-part command record and the `.git` delta:
  [`state/RECEIPT-20260830-k0-deployment-and-freeze-bundle-7ac0edec.json`](state/RECEIPT-20260830-k0-deployment-and-freeze-bundle-7ac0edec.json)
- The preservation precondition that had to pass first:
  [`state/RECEIPT-20260830-aa67c426-preservation-remeasurement.json`](state/RECEIPT-20260830-aa67c426-preservation-remeasurement.json)
- The rule that now holds this tree in place:
  [`FREEZE-20260830-k0-deployment-7ac0edec.md`](FREEZE-20260830-k0-deployment-7ac0edec.md)
