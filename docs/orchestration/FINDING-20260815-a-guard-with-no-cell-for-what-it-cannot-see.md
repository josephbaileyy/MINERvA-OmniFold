# A guard whose accounting has no cell for what it cannot see

**Filed 2026-08-15 by the propagation-correction lane** (`BEN-322`, block `320-329`). Subject item
**`OI-127`**. Surfaced by the mediator while costing a Gate-5 re-issue and reported to it independently by
the `OI-124` peer session. **Every count below was re-derived in this session with the repo's own
function; the relayed figures were not inherited.** They matched, which is worth stating plainly because
agreement between independently derived numbers is the thing `BEN-300` says to check for and, here, is
what it looks like when it holds.

## 1. The mechanism

`verify_hash_bindings.py:137-152`. `collect()` harvests a `(path, sha256)` pair in exactly two shapes:

```python
p = obj.get("path") or obj.get("file") or obj.get("script")
s = obj.get("sha256") or obj.get("sha")
if isinstance(p, str) and isinstance(s, str) and len(s) == 64:
    out.append((p, s, src))
for k, v in obj.items():
    if k.endswith("_sha256") and ...:
        base = k[:-len("_sha256")]
        for cand in (base, base + "_path", base + "_file"):
            if isinstance(obj.get(cand), str):
                out.append((obj[cand], v, src))
                break
```

**A `<base>_sha256` with no sibling `<base>` / `<base>_path` / `<base>_file` produces nothing.** The loop
finds no candidate, no `out.append` runs, and there is no `else`. The Gate-5 receipts store their
implementation pins as **role-keyed hashes with no path key of any kind**, so they are not harvested.

## 2. What is invisible, measured

`state/gate5-target-array-active-56857232.json` — an **active** receipt. Its entire `implementation`
block, **6 of 6**:

```
/implementation/target_driver_sha256      siblings: NONE
/implementation/training_driver_sha256    siblings: NONE
/implementation/nominal_driver_sha256     siblings: NONE
/implementation/loader_sha256             siblings: NONE
/implementation/input_sha256              siblings: NONE
/implementation/gate3_manifest_sha256     siblings: NONE
```

Harvesting every JSON under `docs/orchestration` (261 files, 0 unparseable) with the repo's own
`collect()`: **413 pairs**, of which **0** name `fullevent_fps_dataloader.py`, **0** name
`build_fullevent_replica_target.py`, and **1** names `reconcile_gate5_family.py`.

Those files are pinned. Counting receipts that carry each file's **HEAD digest** — derived from the files
themselves, not from role names:

| file | receipts pinning it | of which `-active-` |
|---|---|---|
| `fullevent_fps_dataloader.py` | **12** | **5** |
| `build_fullevent_replica_target.py` | **4** | 1 |
| `reconcile_gate5_family.py` | **4** | 1 |

The five active dataloader pins include **`gate6-floor-replication-active-56863958.json`**, whose job
`56863958` (tasks 2–5) is the Leg F entry in the control plane's live-job list. *That is a
repo-recorded state, not a cluster measurement — no cluster work was performed for this finding.*

**Two details sharper than the totals:**

* **The single visible `reconcile_gate5_family.py` pin is in `gate5-training-terminal-preflight-56857233.json`
  — a terminal receipt — while the pin in `gate5-family-validator-active-56933831.json` is invisible.** For
  that file, coverage is *anti-correlated with liveness*: the guard sees the dead pin and not the live one.
* **The 6-of-6 receipt is not absent from the guard's output.** It contributes **2** pairs — for a waker
  event and for `sbatch_gate5_replica_target_array.sh`. So the receipt *appears* in the verified set while
  its whole implementation block is unseen. A reader spot-checking "is this receipt covered?" gets yes.

## 3. THE PART THAT MAKES THIS WORSE THAN A COVERAGE GAP

The tool discloses a residue. On the commits landed earlier tonight it printed:

```
resolved 180 bindings (600 unresolvable: data files, off-repo artifacts, binaries)
  165 of them from receipt bindings (floor 140)
```

**`600 unresolvable` is a different set, and it does not contain these.** From `:234-240`, `unresolved`
counts pairs that `collect()` **did** harvest and whose path then failed to localize inside the repo:

```python
for p, want, src in pairs:      # <- only what collect() harvested
    lp = localize(p, a.root)
    if lp is None:
        unresolved += 1
```

Role-keyed hashes never enter `pairs`. **So they are in neither the `resolved` count nor the
`unresolvable` count — the accounting has no cell for them at all.** This inverts the value of the
disclosure: a reader who asks the careful question, *"did it account for everything it saw?"*, gets a
ledger that balances. **The residue line makes the blind spot harder to find, not easier**, because it
looks like the place such things would be reported and it is not.

`RECEIPT_BINDING_FLOOR = 140` is met (`165`) throughout. A floor over a set that structurally excludes
the Gate-5 implementation pins cannot detect their absence, and raising it would not help.

### Size of the blind spot, with the honest denominator

Across the same 261 files: **1181** `*_sha256` keys, of which **123 are paired** (visible) and **1058
unpaired** (invisible).

**1058 is an upper bound and must not be quoted as the number of missed bindings.** Most unpaired keys
are not path bindings at all and correctly have no file to compare against — `receipt_sha256` (127),
`root_sha256` (120), `target_sha256` (112), `row_sha256` (108), `stdout_sha256` (15),
`stderr_sha256` (13): content hashes, Merkle roots, off-repo streams.

**The defensible figure is the subset whose role name denotes repo code: 122 occurrences across 51
receipts** — `launcher_sha256` (21, in 18 receipts), `validator_sha256` (12), `script_sha256` (11),
`engine_net_sha256` (11), `engine_multifold_sha256` (11), `driver_sha256` (9), `loader_sha256` (5), and a
long tail. Those are credible bindings the guard cannot see. *Role-name inference is used here only to
BOUND the problem for costing; §5 explains why it must not be used to FIX it.*

## 4. What this is not — two live neighbours it must not be confused with

* **Lane A's `OI-64` is a different defect and it is RESOLVED.** That row is *"`verify_hash_bindings.py`
  guards every gate's code freeze and is on no path anything takes"* — a **wiring** defect, closed when the
  gate was installed as a 5th pre-commit check whole-tree and unscoped. **The guard now runs**; I saw
  `pre-commit: 7 checks passed` on my own commits tonight. This finding is about what it cannot see **when
  it does run**.
* **`OI-64(f)` already covers erosion** — coverage sliding `152 → 140` across a dozen legitimate
  retirements, with the constant's own comment saying *"do not read a green here as evidence that coverage
  held."* **This is a different axis: not coverage lost over time, but a class never admitted to the
  accounting in the first place.** Erosion needs a delta gate; this needs the collector to report what it
  declined to look at.

**And `OI-66` does not exist.** `verify_hash_bindings.py:121` says *"Tracked as OI-66"*, and lane C's
`OI-65` row cites `OI-66` too — but **`grep -c '^| OI-66 ' docs/OPEN_ITEMS.md` returns 0**. Lane A's
`OI-64` explains why: `(f)` and `(g)` were folded in as sub-parts *"rather than as `OI-66`/`OI-67` because
this row is itself half of an id collision"*. The decision was right; the **code comment pointing at the
id was never updated**, so a reader chasing the erosion item from the source finds nothing. `BEN-215`/
`BEN-216` class, found in passing, and cheap to fix by repointing the comment at `OI-64(f)`.

## 5. Is the fix cheap? Three tiers, and the expensive one is largely FORBIDDEN

**Tier 1 — make the gap visible. ~15 lines, recommended, and it is not a fix.** Count unpaired
`*_sha256` keys during the same walk and print them beside `resolved`/`unresolvable`, so the accounting
has a third cell. **This changes nothing about what is verified, so it reclassifies no past
`ALL BINDINGS INTACT`** — which is exactly the property the mediator asked to preserve by keeping the
collector change out of tonight. It converts an invisible gap into a reported number and gives any future
widening a before/after baseline.

**Tier 2 — require new receipts to carry a sibling path key.** A convention plus a lint scoped to
newly-added receipts. Cheap per receipt, and it fixes the future rather than the past.

**Tier 3 — retro-fit the 51 existing receipts. NOT MERELY EXPENSIVE: mostly forbidden.** Those receipts
are immutable records, many terminal; rewriting one to add a path key so a guard can see it is the same
act this repo declined this morning when it refused to rewrite already-emitted P5A products. **So
historical coverage cannot be recovered — only disclosed.** That is the load-bearing sentence for costing:
the answer to *"can we make the guard cover Gate-5's pins retroactively?"* is **no**, and the achievable
goal is that the output stop implying it already does.

**Explicitly rejected — inferring the path from the role name.** A map like `loader → …/fullevent_fps_dataloader.py`
inside the collector would make the guard assert a target **the receipt never named**, and would compare
rigorously against the wrong file exactly as `BEN-312`'s manifest did — its
`recomputed_from: "the weights artifact, not from any report or summary"` was *true*, and it rigorously
recomputed from the wrong file. A provenance assertion that names its **method** and not its **target** is
satisfied by the defect it should catch. **If a role key is ever resolved to a path, the mapping must be
declared receipt-side and reviewed, never inferred by the checker.**

**Not fixed tonight, per the dispatch, and I agree with the reasoning:** widening `collect()` changes what
every historical green meant, and that deserves its own change with its own before/after count rather than
a ride on a finding.

## 6. The family this belongs to

Third instance today, and the tenth this campaign, of **a tool reporting success over failure** — and the
second today where the *reporting mechanism itself* was the defect rather than the check:

* the `MANIFEST-overrides.tsv` entry that is applied, discarded, **and counted in `applied_overrides`** so
  the "unused overrides" warning cannot see it (`BEN-321`);
* this — pins outside both the `resolved` and `unresolvable` cells, with a residue line that reads as
  complete;
* `BEN-250`'s shape generally: **a diagnostic whose success message is uninformative about the thing it is
  believed to check.**

**The transferable rule: an accounting that partitions what it examined is only trustworthy if it also
counts what it declined to examine.** `resolved + unresolvable` is a partition of `pairs`, not of the
receipts' claims, and the gap between those two denominators is where this lived.

## 7. What this finding does not establish

* **Which of the 122 code-role occurrences are genuine bindings.** Role-name matching bounds the set; it
  does not adjudicate membership, and deciding that per key is part of `OI-127`, not of this finding.
* **Whether any binding is actually BROKEN.** This is a coverage finding, not a drift finding: I did not
  compare the invisible pins against their files, and **the guard's greens may all be true of what they
  checked.** A reader must not infer a broken freeze from it.
* **Anything about the cluster.** Leg F's liveness is quoted from the control plane's job list; no cluster
  command was run.
* **Whether `SHELL_PIN_FLOOR = 15`'s shell-side path has the same hole.** Only the receipt-side collector
  was examined; `collect_shell()` reads pins off comparison lines and was not audited.
