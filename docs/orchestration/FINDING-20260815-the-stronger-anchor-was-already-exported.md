# Path + size + a claimed digest is not identity — and the stronger anchor was already exported

**Filed 2026-08-15 by the propagation-correction lane** (`BEN-326`, block `320-329`). Subject items
`OI-58`, `OI-57`. **Fix authorized by the mediator on Joseph's standing grant and applied to the unpinned
file only**; `train_fullevent_nominal.py` was **not** touched.

## 1. The defect, at both hops

`train_fullevent_replica.py`, one function, eleven lines apart:

```python
target_sha = sha256_file(target_npy)                     # :99  -- the TARGET is HASHED
if target_sha != feed.get("sha256"): raise SystemExit(...)
...
if os.path.abspath(source.get("path","")) != os.path.abspath(inputs_npz): raise SystemExit(...)
if int(source.get("size_bytes",-1)) != os.path.getsize(inputs_npz):       raise SystemExit(...)
if not source.get("sha256"):                                              raise SystemExit(...)
receipt["_verified_input_sha256"] = source["sha256"]     # :112 -- the SOURCE is COPIED
```

The 9.22 GiB source was verified by **path, size, and the presence of a digest in the receipt** — then the
receipt's own digest was copied into a field named `_verified_input_sha256`. **Nothing hashed the source on
the replica path.** A same-path, same-size content change was invisible.

`train_fullevent_nominal.py:642` then stamps that value into every replica artifact:

```python
# Already computed and CHECKED against the receipt by assert_target_provenance; reused
# rather than recomputed, so the artifact records the digest that was actually verified.
inputs_sha256=np.asarray(target_receipt["_verified_input_sha256"]),
```

**That comment is true on the nominal path and false on the replica path**, because the replica adapter
substitutes the provenance function. So 50 published artifacts carry a provenance field that is a
restatement of a claim, under a comment asserting it is a measurement.

## 2. What generalises: the strongest anchor was already computed, exported, and read by nobody

`submit_gate5_replica_n50.sh`:

```
:14  EXPECTED_INPUT_SHA=fa6b3463…                                  # HARDCODED, not floating
:25  [[ "$(sha_of "$INPUT")" == "$EXPECTED_INPUT_SHA" ]] || die "frozen G2 source hash mismatch"
:48  EXPORTS+=",GATE5_EXPECTED_INPUT_SHA=$EXPECTED_INPUT_SHA"
:54  sbatch --export="$EXPORTS" "$TARGET_SCRIPT"
:57  sbatch --export="$EXPORTS" "$TRAIN_SCRIPT"
```

**The input is hashed against a hardcoded digest, fail-closed, before either array is submitted — and the
verified constant is exported to every task.** `grep` over every `.py` in the tree returns **zero readers**
of `GATE5_EXPECTED_INPUT_SHA`, while `sbatch_gate5_replica_train_array.sh:17-22` consumes **four** sibling
`GATE5_EXPECTED_*` pins with `:?` fail-closed syntax and skips this one.

So the codebase held two candidate references for the same check and used the weaker:

| | proves | cost |
|---|---|---|
| the receipt's `sha256` (what was used, and what `OI-57` prescribed mirroring) | *file == receipt* — agreement with a claim | free |
| `GATE5_EXPECTED_INPUT_SHA` (exported, unread) | *file == frozen canonical* | **free** |

**This is the fourth instance today of a qualifying fact computed and then discarded before the consumer**
— `BEN-321` (an override counted as applied and clobbered), `BEN-322` (role-keyed pins in neither
accounting cell), `BEN-323` (`observer_errors` returned and never rendered), plus `tracking=intended` in
`OI-70` — **and the first where the discarded fact was STRONGER than the one used.** The others lost
information about *whether a check ran*; this one lost the *better check*.

## 3. Why the fix lands without a re-issue, which is the shape of it

Measured both ways, because `BEN-322` established role-keyed pins are invisible to
`verify_hash_bindings.py`:

| file | pin lists | verdict |
|---|---|---|
| `train_fullevent_nominal.py` | **4**, incl. live `gate6-leg0-tier-calibration-prepared-20260814.json` `gate_pin_check.pinned_paths[8]` | **do not touch** — editing is an `OI-123` `die … 3` at task start |
| `train_fullevent_replica.py` | **0** (its one hit is a *note* that driver pins are the launcher's job; `submit:50` recomputes the digest at submit, so it floats by design) | **editable** |

**Hop 2's stamp — and its false comment — become true because hop 1 now verifies.** The pinned file needs
no edit, so there is no repin and no Gate-5 re-issue. That is the whole reason this was worth separating
into two hops rather than costing as one blocked change.

## 4. What the guard now proves that it did not before

```python
source_sha = sha256_file(inputs_npz)
if source_sha != source["sha256"]:       raise SystemExit("… differs from its receipt")
frozen = os.environ.get("GATE5_EXPECTED_INPUT_SHA", "")
if not frozen:                           raise SystemExit("… is not exported …")
if source_sha != frozen:                 raise SystemExit("… differs from the frozen G2 digest")
receipt["_verified_input_sha256"] = source_sha
```

* **before:** the file is at the expected path, has the expected size, and the receipt contains some
  64-character string, which is then reported as verified.
* **after:** the file's **measured** digest equals both the receipt's claim **and** the constant the submit
  controller checked against a hardcoded literal. The stamped field is a measurement, and it is anchored to
  the frozen source rather than to the document quoting it.
* **fail-closed in three ways:** a missing export aborts (never a silent skip), a receipt disagreement
  aborts, a frozen-constant disagreement aborts.

**Power-tested in both directions — 5 green.** Absent env aborts; a source agreeing with the receipt but
*not* the frozen constant is refused (**the case an `OI-57`-only fix would have admitted**); **same path,
same size, one byte flipped is caught**, with the size preservation and the receipt's now-stale claim
asserted inside the test so it cannot silently stop testing that; and a mutant asserts the pre-fix copy
would have stamped a digest the file no longer has.

## 5. What this does NOT fix

* **The existing 50 artifacts still carry the copied field.** This changes future runs only, which is why
  the right remedy for the *quoting* half was the citation discharge at `c7eb704` and not this.
* **It reaches production only when `CODE_ROOT` syncs**, which `OI-74` blocks — the cluster tree is at
  `683bdcc` with 751 uncommitted paths.
* **It must not motivate a Gate-5 re-issue.** ~163 GPU-h with no partial re-issue available; this rides one
  if one ever happens, and is not a reason to have one.
* **`train_fullevent_nominal.py:642`'s comment was not edited**, deliberately — the file is pinned, and the
  comment becomes true rather than needing rewording.

## 6. A method error of mine, recorded because it is the same class

Checking whether I had broken an unrelated test, I ran it **alone** at `HEAD` (passed) and **inside a
`-k` subset** in my tree (failed), and briefly concluded I had broken it. **Those are two different
conditions and the comparison was invalid.** Running the same subset at `HEAD` reproduced the identical
failure — pre-existing test-order pollution in `test_pet_fullevent_nominal_launcher.py`, unrelated to this
change. **Comparing a test's status across two trees requires the same selection in both.** Fourth
instrument error of mine today, after the `| tail` exit code, the `split('|')` cell counter, and the
`head -15` truncated grep.
