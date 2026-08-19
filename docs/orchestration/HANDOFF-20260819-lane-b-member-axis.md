# HANDOFF — the `M(ii)` member axis, for a lane B with none of my context

**Written 2026-08-19 immediately before merging `lane-b-member-axis-wip` to main, because a lane reset is
imminent and everything below otherwise lives only in cross-session messages.** Read this before touching
`lib_member_resume.sh` or `mii_*.py`.

Facts here are stated with their operands. Where something is **not** verified, it says so — that
distinction is the most valuable thing in this file.

---

## 1. WHAT THE MEMBER AXIS IS, IN ONE PARAGRAPH

`M(ii)` measures the estimator-seed contribution to the candidate's covariance by re-running the whole
`C_syst` chain 50 times at offsets `k_j = 1200j` from each leg's own baseline (`g1 = 42`, `g2 = 1000`).
Every output is namespaced into `mii/member_kNNNNNN/…` so cross-member contamination is **structurally
impossible** rather than merely checked. With `MNV_EST_SEED_OFFSET` **unset**, every path reduces to its
original literal and behaviour is byte-identical — that is the hard constraint, and it is tested.

## 2. FIVE DESIGN DECISIONS THAT LOOK ARBITRARY AND ARE NOT

**(a) `mii/member_k…` comes FIRST in the path, not after the namespace.** Lane C reversed my original
`uq_5d/…/member_k001200/` on two grounds. Spec §1's preflight must reject any member path *equal to, under,
or glob-overlapping* the six canonical archive namespaces — and under namespace-first **every** member path
is under one by construction, so the check could only exist as a guard special-casing the thing it guards.
And namespace-first placed 50 member trees as siblings *inside the directory the archive's own consumers
glob*, with only shell non-recursion keeping them out. `seed_offset_policy.assert_member_path_is_outside_the_archive`
is the check that became writable; a test feeds it the old shape and requires `SystemExit`.

**(b) `mr_run` / `mr_skip_if_complete` exist rather than `rg_run` / `rg_skip_if_complete`.**
`lib/resume_guard.sh`'s `rg_mark_complete` writes **no note**, so an identity-blind resume accepted *every
archive marker*: no note ⇒ fall through to size/mtime ⇒ **member 0 was handed the archive's product**.
Reproduced, then fixed. `mr_*` wrap the `rg_*` primitives and add a note comparison that **hard-fails**
(exit 3) on a note mismatch rather than falling through.

**(c) The offset regex is `^(0|-?[1-9][0-9]*)$`, not `^-?[0-9]+$`.** Zero-padded values are **octal in
bash**: `001200` gave a seed of `682`, a directory of `member_k000640`, and python provenance of `1200` —
three different numbers from one input — while `009600` errored *and still created* `member_k000000/`. The
regex rejects leading zeros so the three can never disagree.

**(d) `rtol` defaults to `0.0` in `mii_anchor_comparator.compare_files`.** This is the gate deciding whether
the archive was reproduced; a silent `1e-9` would make "reproduced" mean something nobody chose. **A default
is a choice, just one nobody has to defend.**

**(e) The launchers locate their library by a VALIDATED CASCADE, never by `BASH_SOURCE` alone.** `sbatch`
copies the script to `/var/spool/slurmd/job<N>/slurm_script` and runs **the copy**, so `BASH_SOURCE` *and*
`$0` are the spool path. This killed stage 0's first nine tasks in 12 s each. `SLURM_SUBMIT_DIR` is
**refused** even though it works: it is the *submit* directory, and canonical also holds a
`lib_member_resume.sh`, so a submission from elsewhere would silently source **the wrong tree's** library.
See `BEN-484`. Order: `MNV_LAUNCHER_DIR` → `dirname BASH_SOURCE` → `scontrol Command=` → **exit 2 naming
every candidate**. Each candidate is accepted only if the library is *readable there* — a resolver that
assumes cannot detect the environment where its assumption is false.

## 3. STATE: WHAT IS DONE, WHAT IS BLOCKED, WHAT IS NOT CLAIMED

| item | state |
|---|---|
| Gate 1 (two-role seed separation) | done |
| Member axis + 7 hooked leg launchers | done; undeclared is byte-identical |
| S1 substitution fence, 9 launchers | done; **247 of 263 launchers are in NEITHER set** — the real exposure, pinned by a test so it cannot grow silently |
| Stage 0 (does the offset change the numbers?) | **PASSED** — three `DISTINCT`, jobs 57252337/8/9 |
| Gate 2 (a comparator that is right) | **MET** — D ran `_th2_content` on a real 10694² `C_unified` at `ecee9ff1` unmodified: `de32843bca7128c951a37e18d4cdc437eef1023bee41cc35251846a91c643d6f` |
| B1 steps 1–3 (member-local combines + analyzer) | done |
| B1 steps 4–5 (adoption) | **PAUSED**, expiry = **remedy (A) VERIFIED BY C**, not merely landed |
| Remedy (A) identity stamps | **2 of 3.** analyzer + lateral landed; **`adopt_unified_5d.py` BLOCKED** |
| `mask_order_hash` | **NOT BUILT, NOT CLAIMED** |

**Stage 0's headline number, stated correctly:** the estimator seed moves C_stat's replicas on
**~10,508 of the ~10,694 reported-support bins**, i.e. essentially every bin that *can* move.
**Do not write "16% of bins"** — that divides by the 65,856 **grid**, ~84% of which is empty, and a bin
that is zero in both members cannot change. A **grid is not an artifact size**; every matrix and per-bin
array here is on the `cv > 0` support.

## 4. THE BLOCKER, AND C DISSOLVED IT RATHER THAN CLEARING IT

**Remedy (A) on `adopt_unified_5d.py` cannot be committed.** Any edit breaks a receipt `sha256` binding
owned by `docs/orchestration/state/ben106-stamp-verify-active-56695424.json`, and the **pre-commit hook
refuses**. The guarding test states the remedy: *the owning gate must be re-run and its receipt re-issued —
do not just update the hash.*

Confirmed by measurement, both directions: restoring the file to `HEAD` returns `181 OK / ALL BINDINGS
INTACT`, so the binding was clean before the edit; and the conflict is with **any** edit, not this content.
**So C's "remedy (A) is mandatory before admission" and BEN-106's frozen binding are in direct conflict.**

**C RULED AT `783d648a` (§25) AND THE ANSWER IS NOT A RE-ISSUE.** Remedy (A) on the adopted roots is a
**NEW UNPINNED WRAPPER** invoking `adopt_unified_5d.py` **as a subprocess** and then reopening the output in
`UPDATE` to add the keys. `adopt_unified_5d.py` is not touched, the binding stays intact, no receipt moves.
The conflict was **C's §11j against C's own earlier `RULING-20260817-lanec-pinned-readers-get-wrappers-not-copies.md`**
— *"new unpinned files … must be WRAPPERS THAT IMPORT THE PINNED MODULES, never copies of them"* — and the
earlier ruling wins. **I had asked how to make the edit legal instead of whether it had to be an edit.**

So: the preserved patch is the **specification of what to stamp**, and
`docs/orchestration/pending/README-20260819-remedy-A-adopt.md` carries the superseding ruling at the top.
**DO NOT APPLY IT TO `adopt_unified_5d.py`.** The wrapper is **NOT YET BUILT** and is the next piece of work
on this axis. `ADOPTED_UTHROW`'s commented keys and `STAMP_COVERAGE[...]["stamps"]` flip in the same commit
as the wrapper. And **no receipt binds `analyze_universes_5d.py`** (C grepped `state/*.json`), so the third
writer's landed edit stands.

**Why the class table was left admitting the gap rather than describing the intent:** with those keys
classified, `identity_is_checkable("adopted_uthrow.root")` returns `True` while the writer stamps nothing —
a gate reporting identity as checkable on an artifact that carries none. **A table describing a writer that
does not exist yet is worse than one admitting the gap.**

## 5. TWO KNOWN-RED TESTS ON MAIN THAT THIS MERGE CAUSES

    tests/test_p4_resume_integration.py::…::test_launcher_emits_exactly_the_six_producing_paths
    tests/test_p4_token_gate_scope_and_rev.py::…::test_MUTATION_prefix_surface_OMITS_the_shell_invoked_scripts

One cause: the lateral's `import seed_offset_policy` widens the **P4 verifier's code surface**. The launcher
surface gains `nd-unfolding/seed_offset_policy.py`; repair-8's mutation surface goes **18 → 19**, same file.

**I believe the widening is CORRECT** — that file genuinely *is* a dependency of the unfold path now, so
covering it is an improvement — but these are **pinned measurements belonging to another lane**, to be
re-taken by their owner, exactly like the `p4_sweep` snapshot. **A function-local import does not dodge it:
measured, the walker scans all imports, not only module-level ones.** Inlining the offset parse to remove
the dependency is **refused** — a third copy of the offset rule is the drift hazard this campaign keeps
filing.

## 6. EXPOSURES A FRESH LANE SHOULD KNOW BEFORE TRUSTING THIS LIBRARY

- **The fence catches SUBSTITUTION, not CONCURRENCY** (lane D). `mr_fence_unhooked` triggers on
  `MNV_EST_SEED_OFFSET` being *declared*, so a concurrent **unfenced sibling** run is invisible to it **by
  construction**. D's sentence, which lands squarely on `lib_member_resume.sh`: *"a resume guard that trusts
  a complete product is one whose input a concurrent baseline run can forge."* Adversarial twin of `BEN-477`.
  **C is ruling on the marker; this was not a blocker on the merge but it is a real hole.**
- **`p4_sweep_snapshots` is red on main and I am a CONTRIBUTOR, not an observer**: 374 committed against
  **383** at my HEAD, two of them my own new libs (`lib_member_resume.sh`, `lib_substitution_fence.sh`).
  C checked itself after my flag and found it is a contributor too, by at least four files. Nobody had
  counted themselves in.
- **`read_keys_pyroot`'s failure branches are exercised by stubs only.** D ran the SUCCESS path on real
  data; the `ok=False` reasons are covered by local stubs. Neither covers the other's ground.
- **`DO NOT DELETE ${COMB}` during the B1 pause** — `BEN-485`. §11g gates deletion on `MVFINAL_j`, which
  needs steps (4)/(5), so *pause* + *11g releases the 41 GB* would delete the only input to the steps that
  have not run. At 50 members that is 2.087 TiB, the exact figure 11g exists to avoid.

## 7. HOW TO REPORT A SUITE RESULT HERE (`BEN-468`)

**Name the tests, not the count.** `3 ≤ 4` cannot witness a subset relation, so "3 failures, all
pre-existing" is *unestablished even when true* — and a true-but-unestablished claim is indistinguishable
from a verified one, which makes it worse than a false one. Baseline `8e48a811` fails **four** by name:
`gate2_target_runtime`, `p4_sweep_snapshots`, `pet_fullevent DriverConfigGate`, `resume_guard`
(the last fixed by `BEN-482`). Compare **sets**.
