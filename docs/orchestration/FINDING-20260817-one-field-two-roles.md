# FINDING 2026-08-17 — one field, two roles: the defect a new mode is always the first to find

**BEN-256.** Lane D (verifier), read-only, at the mediator's request. The seam analysis of instance 1
is joint with the Assistant session, which named the two roles; the second instance, the detection
rule, and the "the obvious fix cannot fail" result are mine. Hostile-pass receipt:
[`state/gate5-data-only-assert-hostile-pass-20260817.json`](state/gate5-data-only-assert-hostile-pass-20260817.json).

## The shape

> A configuration field acquires a **second** meaning because, at the time it was written, no mode
> existed that needed one meaning without the other. The two roles are then indistinguishable —
> **not hidden, indistinguishable** — and stay that way until a new mode needs exactly one of them.
> That mode has no way to say so, sets the field to the value that expresses the role it wants, and
> silently gets the other role too.

Two instances in this codebase. **Both were found only when a new mode needed one role without the
other**, which is the same as saying neither was findable before.

## Instance 1 — `bootstrap_seed`: "which replica this is" ∧ "draw the bootstrap factors"

`C_stat^data`, the data-only Gate-5 family. `57194055_0`/`_1` FAILED 2026-08-17 (00:02:24 / 00:02:16,
`ExitCode 1:0`) with

```
ValueError: [negweight] refined target has bootstrap_seed=None (NOMINAL) — cannot be reused for
            replica seed 50000 (fail closed; rebuild per replica)
```

Data-only means *data Poisson, MC unity*. The loader has **one** `bootstrap_seed` switch controlling
all three streams, so the only way to leave the MC legs unthinned is `bootstrap_seed=None` — which
also means *"this is the nominal build"* to everything downstream. The driver therefore passes the
replica identity alongside, in `precomputed_target_replica_seed`, and the guard reads the other one.

**The sharpest form, and it is not in the original diagnosis:** the *same* function is called twice
per job, on two dicts with **the same key names and swapped meanings**, and returns opposite verdicts
minutes apart.

| call site | dict | `bootstrap_seed` | `precomputed_target_replica_seed` | verdict |
|---|---|---|---|---|
| `train_fullevent_replica.py:99` | builder receipt's `runtime_target` | **50000** | `None` | **PASSES** |
| `train_fullevent_replica.py:288` | loader's `meta["target"]` | `None` | **50000** | **FAILS** |

Both rows measured — the first read out of `replica_00`'s receipt on scratch, the second from
`fullevent_fps_dataloader.py:1524` and the frozen driver's `:283-284`. In the builder the two roles
hold the same number, so the ambiguity is *invisible at the only site that ever exercised it*.

**A third call site proves that last clause.** `:198` is the *coherent* family's equivalent of
`:288`, and it has never failed — because there the driver passes `bootstrap_seed=<seed>` **and**
`precomputed_target_replica_seed=<the same seed>`. Both roles hold the same number, so either read is
correct. The guard ran the entire Gate-5 coherent campaign under the one condition that cannot
distinguish its two meanings.

**Digest parity, so these line numbers can be falsified.** `train_fullevent_replica.py` is
`7aee2f98…2128` and `fullevent_fps_dataloader.py` is `e1402370…0ce1` — **byte-identical between
`origin/main` and the frozen checkout `gate5-data-only-frozen-d0c42bd`**, verified both sides this
turn. Every line number here is valid in both trees.

### The role collapse also silently disabled a guard

`fullevent_fps_dataloader.py:1479` gates the entire seed-consistency block on
`if bootstrap_seed is not None`. Data-only sets it to `None`, so `:1488` — *"precomputed target was
built for replica X but this loader is drawing Y"* — **never runs in data-only at all.** One
assignment broke the assert and removed the mis-pairing check in the same stroke.

### And the obvious fix is a check that cannot fail

Reading `precomputed_target_replica_seed` instead (or coalescing the two) looks like a one-line
repair. It is not a check. **That field is not a property of the array on disk** — it is a value the
driver passes *in* (frozen `:284`, unconditionally `int(args.bootstrap_seed)`) and the loader echoes
back out (`:1523-1524`). Asserting on it is the driver asserting against its own argument: it returns
`True` for replica 7 handed replica 12's target, and for replica 7 handed the *nominal* array.

**The current form cannot pass; the coalesced form cannot fail. Neither is evidence** (`BEN-250`).

What actually binds the array is already there and already passing: `read_replica_target_receipt`
verifies status, seed, index, owning path **and** `sha256_file(target) == feed.sha256`
(`:83` def, `:111` digest, `:155` stored as `_verified_target_sha256`). Re-verified on disk this turn — `616117e1…7499`, 18,723,004 bytes, matching both the receipt
and `57194054_0`'s `19:22:05Z` completion.

## Instance 2 — `--seed`: "estimator initialization" ∧ "throw realization"

`nd-unfolding/unified_throw_cov.py`, one flag (`:525`), two consumers:

```
:223   rng = np.random.default_rng(args.seed + gj)      # THROW realization: nuisance draws, flux universe
:244   x = _xsec_for_weights(..., args.iters, args.seed, flux=flux_j)   # ESTIMATOR seed
```

`:242` states the requirement the design has to meet — *"Systematic throws all use the SAME estimator
seed. ML variation belongs exclusively in `C_ML` and must not leak into `C_syst`."* The two roles are
separated **arithmetically**, by `+ gj`, not structurally. So the one operation that would measure
what is being held fixed — **re-run the identical throw ensemble under a different estimator seed** —
is unreachable: changing `--seed` changes every throw's Gaussian draw and flux universe too. `:417`
then *enforces* the coupling, refusing a mixed-seed combine.

Recorded consequence, independently and before this finding:
`DECISION-CALIBRATION-20260817.md:57` — *"Four legs share estimator seed 42, so their noise moves
coherently"*, with the cross-terms **unmeasured**. That is `M(ii)`, which cause 3 is still behind.

## The detection rule

The tempting rule — *"audit fields for multiple meanings"* — is unbounded and nobody will run it. Two
cheaper ones, in order of how well they actually fire.

**RULE 1 (executable, and it fires on both instances). Grep for the workaround, not the field.**
A mode that needs one role without the other cannot say so through the interface, so it *reaches
around* the interface — and in this codebase the author reliably documents the reach-around as
cleverness. `cstat_data_only.py:341-342` says it outright:

> *"'Data Poisson, background unity' is **not reachable through the loader's interface**, and the
> loader is hash-pinned 25 ways."*

That sentence **is** the finding, written down before the failure, by the person the failure was
waiting for. Instance 2's is `+ gj`. So: **a comment explaining why a value had to be produced by
monkeypatching a module global, offsetting a seed, or otherwise bypassing the declared parameter, is
a role collision until shown otherwise.** Grep the workaround idioms — a patched module global, a
seed with arithmetic on it — not the several hundred config fields.

**RULE 2 (static, narrower).** A field has two roles if **a value that is legitimate input at one
site is a sentinel at another.** `bootstrap_seed=None` is a legal nominal build *and* the value
`assert_refined_target_is_replica` reads as *"not a replica."* Detectable without any new mode
existing: find guards whose failure branch triggers on a value another caller legitimately passes.

**And the corollary that costs nothing:** when a new mode needs role A without role B, **the fix is
to give role A its own field**, not to teach the guard a second field to look at. A guard reading a
field the caller supplied is not reading evidence.

## Boundary

`fullevent_fps_dataloader.py` is **pinned at 25 digest sites**. This finding may recommend separating
the roles; **nobody edits that file on the strength of it.** The remedy shape for instance 1 touches
`train_fullevent_replica.py` only — assert on `consumed_precomputed_target` (loader `:1516`), an
abspath the *loader* wrote about what it actually opened, rather than on an echo of the driver's own
argument. Writing it is E's; approving it is not mine.

## Amendment 1 (2026-08-17) — my own recommended limb is WITHDRAWN. It is a tautology.

Lane B objected that the form recommended above reduces to comparing a value with itself, and the
mediator put the question precisely: **is there any reachable execution in which
`consumed_precomputed_target != abspath(args.target_npy)`?**

**Measured answer: NO. B is right and I withdraw the limb.** The chain, every link verified in the
digest-pinned tree above:

| step | site | what happens to the string |
|---|---|---|
| 1 | `train_fullevent_replica.py:402` | `"--target-npy", args.target_npy` — copied **verbatim** into nominal's argv |
| 2 | `train_fullevent_nominal.py:377-379` | the **sole** `build_fullevent_loaders(` call site in the module; passes `precomputed_target=args.target_npy` |
| 3 | `fullevent_fps_dataloader.py:1516` | `os.path.abspath(precomputed_target)` |
| 4 | `train_fullevent_replica.py:106` | `os.path.abspath(target_npy)` — **the same string**, from the same variable |

Both operands are `abspath()` of one unmodified value. The only mechanism that could separate them is
a **cwd change between steps 4 and 3 with a relative path** — and there is **no `chdir` in any of the
three modules** (grepped), while the launcher supplies an absolute path
(`sbatch_gate5_data_only_train_array.sh:34,51`), which makes `abspath` the identity function anyway.

**And note the shape of that lone hypothetical, because it is the decisive part rather than a
caveat:** even if a `chdir` did make them differ, the check would be *detecting a chdir* — not
detecting a wrong target. **A check whose only route to failing is not the failure it claims to
detect is not a measurement of that failure.** So the limb fails on its own terms, not merely on
C's independence-of-routes rule (`9b1e2d45`, `BEN-423`), which it also fails.

I passed exactly this verdict on the coalesce fix two sections up and then proposed a second form of
it. **The operand I chose was independent-*looking* — a loader-written abspath rather than a driver
argument — and I did not trace it back to its source.** Provenance of a *value* is not provenance of
its *route*, which is the whole content of C's rule.

**The one thing worth keeping, because the next person will reach for this field for the same good
reason:** `consumed_precomputed_target` records **what the loader actually opened**, which is a
genuinely different kind of fact from what the driver intended. It is unusable here only because
**nothing independent exists to compare it against** — not because the field is uninformative. Pair
it with a family-position operand (`campaign/replicas/replica_NN/target`) and it becomes a
measurement; pair it with the driver's own argument and it is an echo.

**Nothing is lost by dropping it.** The mis-pairing it was meant to catch is *already* caught, in
process and before any GPU work: `read_replica_target_receipt` checks the receipt's own
`replica_index` (`:92`) and `bootstrap_seed` (`:94`) against the driver's. Replica 7 handed replica
12's target-and-receipt dies there. `:288` has no identity work left to do.

### The `:198` observation generalizes, and there is a third read nobody has hit yet

C establishes that the same overloaded field is read for identity at
`validate_gate5_training_artifacts.py:283` — `checks.eq("target_meta_seed",
target_meta.get("bootstrap_seed"), seed)` — so this is **not one guard, it is a family of reads**,
and the coherent campaign satisfied all of them under the one condition that cannot distinguish the
field's two meanings.

**Measured, and it is latent rather than fired:** that validator has **zero** `data_only` /
`cstat_product` awareness (grepped: no hits). For a data-only artifact `target_meta["bootstrap_seed"]`
is `None`, so `:283` compares `None` against `50000` and **fails on all 50**. It is not wired into
`submit_gate5_data_only_n50.sh` — that campaign is two stages, target and train, with no validation
stage — so it does not block E's repair. **It blocks the step immediately after it**, via
`sbatch_gate5_training_family_validate.sh:25`, which is the natural next thing anyone reaches for.
A second candidate in the same file that I did **not** evaluate: `:189-191`, the `EXPECTED_CODE`
digest comparison (`BEN-386`, `OI-60`).

## Family

- `BEN-250` — a check whose strongest statement could not fail. **Instance 1's obvious fix lands
  here**, which is why it is named rather than applied.
- `BEN-252` — a recorded quantity that could not express the question. Adjacent but distinct: there
  the field could not *represent* the answer; here it represents two answers with one symbol.
- `BEN-255` — a check evaluated on the wrong population.
- **`BEN-256`** — a field carrying two roles, separable only by a mode that does not exist yet.
  **The third instance should be cheap; Rule 1 is what makes it so.**
