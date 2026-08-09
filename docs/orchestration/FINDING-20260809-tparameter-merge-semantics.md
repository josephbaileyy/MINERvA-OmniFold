# FINDING 2026-08-09 — `hadd` and `TParameter`: the general rule, and the complete triaged inventory

**Status:** inventory complete and mechanically regenerable. Two live defects, both already known
and both already handled at the read side; one OPEN scoping item (J36) which this reframing
explains. No new defect found — the value here is the *criterion*, which is sharper than the trap
it generalises, and the enumeration that bounds it.

**Generator:** `docs/orchestration/audit_tparameter_merge_semantics.py` (332 tracked source files,
C++ and Python, comments and docstrings stripped). Run with `--power` for the two live controls.

---

## 1. The rule, in the form that is actually useful

The version I first wrote down, and was asked to restate generally, was:

> Every `TParameter<double>` in a merged file is a sum across playlists.

That is **true and it is not the defect criterion.** ROOT's `TParameter<T>::Merge` defaults to
mode `'+'`, so `hadd` does add same-named TParameters across all 12 playlist inputs — but for most
of the fields that actually pass through a `hadd` in this repo, *adding is exactly right*. Stated
as "every TParameter is a sum", the rule flags 10 of the 15 hadd-transiting fields and is wrong
about 8 of them, which is the kind of rule that gets ignored after the third false alarm.

The criterion that separates the real cases:

> **A `hadd`-summed `TParameter` is correct for an EXTENSIVE quantity — one that legitimately adds
> across playlists (POT, event counts, migration censuses) — and wrong for an INTENSIVE one (a
> per-playlist constant, a ratio) or a FLAG (per-playlist 0/1, which becomes a count in [0, 12]).**
>
> **And a fourth case that neither form catches: two extensive fields can each merge correctly
> while a quantity DERIVED from them does not.** `sum(dataPOT)/sum(mcPOT)` is not the
> playlist-mixture-correct ratio, and both operands look impeccable.

That fourth case is J36, and it is the reason J36 sat undetected two functions away from an
explicit, correct, well-commented defence of trap #8: the trap-#8 defence asks "is this field
merge-sensitive?", both operands answer no, and the question that mattered was about their
quotient.

The other thing the inventory shows is that **both conventions are live in this codebase and the
difference is one character in a constructor in another language.** `runEventLoopOmniFold.cpp:1900`
writes `TParameter<int>("hasFullEventSchema", 1, 'f')` — the PET lane hit trap #8, read the
manual, and used the merge-mode argument. Nothing at any read site distinguishes that field from
`hasTruthOnlyMisses` two dozen lines later, which takes the default and sums. A reader cannot
recover the semantics from the artifact; only from this table or from the C++.

## 2. What passes through a `hadd`

Only `runEventLoop*.cpp` output is ever `hadd`-ed on this campaign (`sbatch_hadd_MEFHC*.sh`,
`run_p4_merge_audit_std.sh`, 12 playlists per merged endpoint). Of the 62 `TParameter` fields
written anywhere in the tree, **15 transit a merge**; the other 47 are written by analysis scripts
whose output is never merged, and their default `'+'` mode is inert.

| field | type | mode | post-`hadd` meaning | class | verdict |
|---|---|---|---|---|---|
| `dataPOTUsed` | double | `+` | total data POT over 12 playlists | extensive | **correct** |
| `mcPOTUsed` | double | `+` | total MC POT over 12 playlists | extensive | **correct** |
| `POTUsed` | double | `+` | total POT | extensive | **correct** |
| `activeUniverseTruthEntrants` | long | `+` | census summed over playlists | extensive | **correct** |
| `activeUniverseTruthExits` | long | `+` | census summed over playlists | extensive | **correct** |
| `activeUniverseRecoEntrants` | long | `+` | census summed over playlists | extensive | **correct** |
| `activeUniverseRecoExits` | long | `+` | census summed over playlists | extensive | **correct** |
| `nTruthOnlyMisses` | long | `+` | total truth-only misses | extensive | **correct** |
| `activeUniverseIndex` | int | `f` | first playlist's value | identity | **correct (explicit `'f'`)** |
| `activeUniverseIsLateral` | int | `f` | first playlist's value | identity | **correct (explicit `'f'`)** |
| `hasActiveUniverse` | int | `f` | first playlist's value | flag | **correct (explicit `'f'`)** |
| `hasFullEventSchema` | int | `f` | first playlist's value | flag | **correct (explicit `'f'`)** |
| `fullPhaseSpace` | int | `f` | first playlist's value | flag | **correct (explicit `'f'`)** |
| `hasTruthOnlyMisses` | int | `+` | **count of playlists with misses, in [0,12]** | flag | **DEFECT — mitigated at the reader** |
| `pTmu_fiducial_nucleons` | double | `+` | **12 x the nucleon count** | intensive | **DEFECT — retired at the writer** |

Plus one derived-quantity defect that no single row can express:

| derived | from | verdict |
|---|---|---|
| global `data_pot/mc_pot` scale | `dataPOTUsed`, `mcPOTUsed` (both individually correct) | **J36, OPEN** — ratios span 0.1707–0.2371 across playlists, 38.9 % max/min−1; the merged quotient discards the mixture |

## 3. The two defects, and why neither is open

**`pTmu_fiducial_nucleons`** — the original trap #8. Fixed on both sides: the event loop no longer
writes it (`runEventLoopOmniFold.cpp:1908`, "Do not write pTmu_fiducial_nucleons here"), and the
reader refuses the merged value outright (`unfold_2d_omnifold_unbinned.py:1323-1329`, "Ignoring
merge-sensitive pTmu_fiducial_nucleons metadata"), substituting the fixed tracker constant
3.2353e30. Note the *shape* of that fix: writer retired, reader defended, and a `[WARN]` printed
if the field is encountered. That is the right treatment and it is worth copying.

**`hasTruthOnlyMisses`** — found 2026-08-09 when `p4_evidence.py` required it to be in `(0, 1)`
and every one of the ten endpoints reported `12`. The check was *correct about the writer's intent
and wrong about the artifact*, and it fail-closed on ten perfectly good endpoints. Mitigated at
the reader: `p4_evidence.py` now records it as
`native_miss_playlists_with_misses`, requires `0 < value <= 12`, and requires it to agree in
direction with `nTruthOnlyMisses`. **The writer is still wrong** — a per-playlist 0/1 flag under
`'+'` — and the correct repair is one character in the C++ (`'f'`) or, better, a rename to
`nPlaylistsWithTruthOnlyMisses` so the merged value's meaning is in its name. That is a change to
the event loop, which re-running is a multi-hour production step in another lane, so it is logged
as an OPEN item rather than done here.

## 4. Rules

1. **When adding a `TParameter` to anything the event loop writes, classify it before you write
   it.** Extensive → default `'+'`. Intensive, identity, or flag → pass `'f'` explicitly. The
   argument exists; five fields in this repo already use it.
2. **Name the field for its merged meaning, not its per-playlist meaning.** `hasTruthOnlyMisses`
   reads as a boolean at every call site and is not one. `nPlaylistsWithTruthOnlyMisses` could not
   have produced the 2026-08-09 fail-closed.
3. **A reader that validates a `TParameter` from a merged file must state which convention it
   assumes** — a bare `in (0, 1)` is a claim about the writer's merge mode, made silently.
4. **Ask the derived-quantity question separately.** Field-by-field merge-sensitivity review
   passes J36 cleanly. Whenever two merged fields are combined, re-ask the question of the
   combination.
5. **The general form, for the next reader:** ROOT gives every mergeable object a merge policy,
   and the default is usually the one that is right for counts. Any time a per-file *property* is
   stored in an object with a *count's* merge policy, merging silently converts a property into a
   tally. `TParameter` is where this bites here; it is not the only place it could.

## 5. Bound on this result

The sweep resolves field names statically. One write site builds its name at runtime
(`assemble_gbdt5d_adopted.py:120`, `f"sqrt_tr_{k}"`) and is reported separately; it is in an
analysis script whose output is never `hadd`-ed. Read sites are matched by literal name and are
therefore over-inclusive, which is the correct direction of error for an inventory. The
"transits a `hadd`" determination rests on the claim that only `runEventLoop*.cpp` output is ever
merged — established by reading every `hadd` invocation in the tracked shell corpus, and true
today; a new merge of analysis-script output would silently enlarge the live set, which is the
one thing here that a future change could invalidate without any test going red.
