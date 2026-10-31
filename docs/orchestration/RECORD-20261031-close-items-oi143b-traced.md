# RECORD — OI-143(b) traced: the fixture question was answered on 2026-08-21, and the residual is cluster-only (2026-10-31)

**By** the close-items session, on the director's order of 2026-10-31. Read-only and local: `git log`, `git grep` and
one local run of `verify_hash_bindings.py`, at `efd014670`. **No connection to the cluster was made.**

**CITABLE FOR:** which of OI-143's decisions landed and where, what calls the gate at `efd014670`, and what the gate
prints on a clean local tree.

**NOT CITABLE FOR:**
- what the gate prints on the canonical checkout today;
- how many untracked receipts that checkout still holds, or whether any of them is the only copy of a binding.

Both need the cluster, which this record did not touch.
<!-- absence-ok: scoping statements about what this record's own measurements cover -->

**PROPOSES:** closing the fixture question as answered, and deferring the cluster residual to a named trigger (§3).
The register is not changed here; the ruling is the director's.

## 1. What the row waits on

OI-143 is `WAITING-USER`, owner *"Joseph — narrowing a provenance gate's scope is his call"*, dated 2026-08-21. Its
state cell: *"(a) LANDED 2026-08-21 (`ea1a3fd6`); (b) NARROWED AND STILL OPEN."* The next-action cell asks for two
decisions:
1. *"Decide whether the gate should exclude `tests/fixtures/**`."* It adds: *"Do NOT update the B1_E digest."*
2. *"Separately decide the second mismatch: `train_fullevent_nominal.py` is bound by an UNTRACKED scratch receipt
   from job `56534116` … dropping that source is a real loss of coverage."*

The state cell's last sentence names what (b) still needs: *"migrating the useful cluster-side untracked-receipt
bindings into a reviewed TRACKED manifest before retiring that source."*

## 2. What landed, and what calls the gate

**Decision 1 was answered by (a), and not by a path rule.**
- `ea1a3fd6a` (2026-08-21) holds out of the production verdict any JSON that declares a top-level `_fixture` key.
  `fixture_integrity` pins that set and each file's sha256. Its message also records (b) as *"ALREADY DONE"* for the
  inventory: `tracked_paths` and `receipt_inventory` already count only tracked bound paths.
- `9bf92bdee` (2026-08-21) made `REFERENCE_real_manifest.json` self-declare. That was the one fixture the cluster
  mismatch on `std_final5_candidate.root` resolved through. The commit records why this costs no coverage: five
  non-fixture files bind the artifact at its on-disk digest `950f8cb1…`.
- So no `tests/fixtures/**` exclusion was needed, and the B1_E digest was not touched.
  `verify_hash_bindings.py:201-235` carries the reasoning.

**The gate on a clean tree, run locally** (in a worktree whose `.json`, `.sh` and `.py` files equal `efd014670`):
- `ALL BINDINGS INTACT`, rc 0;
- inventory 157 tracked, sha256 `9abec558…`, equal to the pinned `RECEIPT_BINDING_COUNT` and `RECEIPT_BINDING_SHA256`
  (`:480-481`);
- 24 bindings in 12 self-declared fixtures held out, set digest `36355204…`;
- 5 known pre-existing drifts (`KNOWN_PREEXISTING`, `:90`). `train_fullevent_nominal.py` is not among them.

**What runs the gate.** Search: `git grep -n 'verify_hash_bindings'` @ `efd014670` over `*.sh`, `*.yml` and
`.githooks`, comment lines excluded. Four callers:
- the pre-commit hook (`.githooks/pre-commit:265`);
- CI (`record-checks.yml:84`);
- two state check suites under `state/next-preparation-20261009/`.

All four run in whatever tree they are invoked in. None is a launcher. The five PET launchers that name the gate
(`sbatch_gate5_data_only_target_array.sh`, `sbatch_powered_closure.sh`, `merge_g2_gate1_mefhc.sh` and two others)
name it only in comments, about the pin idiom it can discover.
<!-- absence-ok: the search and sha are named in this paragraph -->

**What this means for (b).** The per-tree divergence comes from untracked scratch receipts that exist only in the
cluster's canonical checkout. The gate reads them there because it globs `docs/**/*.json` and `nd-unfolding/**/*.json`
(`:892-893`). A clean checkout, CI included, does not have them. So the divergence shows only when someone runs the
gate inside that checkout, by hand or by committing there. Nothing in the repository runs it there.

**Decision 2, `train_fullevent_nominal.py`.** Its tracked binding was re-pointed on 2026-09-23, `91144bee` →
`ba939bd2` (`:321-325`, the Gate-4 launch-code re-issue under KNOWN_ISSUES 28/38/33). No tracked path carries job
`56534116`'s id. The id appears in the text of ten tracked files, which this record did not open as receipts.
Search: `git ls-tree -r --name-only | grep 56534116` @ `efd014670`, empty.
Whether the untracked receipt still sits in the canonical checkout was not measured. It is a PET file, and PET has
been diagnostic since 2026-08-20.
<!-- absence-ok: the search and sha are named in this paragraph; the last sentences scope what was not measured -->

## 3. The proposal

**Close decision 1 as answered.** The semantic holdout of `ea1a3fd6a` and `9bf92bdee` is the narrowing. It is not a
path exclusion, and it has a pinned integrity check. A lane landed it on 2026-08-21; the row kept its owner as Joseph.
The gate is green with it on a clean tree today (§2). If the director wants his explicit
ratification, it is one line: *"Keep the `_fixture` holdout in verify_hash_bindings.py (12 fixtures, integrity
pinned)?"*

**Defer the residual, (b)'s migration and decision 2,** with this trigger: *"the hash-binding gate is to be run in
the canonical checkout, or that checkout's untracked receipts are to be removed or purged."* Until then, nothing runs
the gate there. Curating the cluster's untracked bindings into a tracked manifest is work for an owner with the
cluster in scope. It needs its own declaration.

**A limit, stated rather than measured.** The canonical checkout is on `/pscratch`, which is purgeable. If any of its
untracked receipts is the only record of a binding, a purge would lose it. That is the durability question under the
deferral trigger, and only a cluster read can answer it.

**Dependency check.** Search: `git grep -n 'OI-143'` @ `efd014670`, excluding `OPEN_ITEMS.md` and the generated
views:
- `verify_hash_bindings.py:201, 250, 259, 792, 899, 1125`: history of (a) and the per-tree note;
- `DESIGN-20260902-declarative-routing-register.md:436`: a format note.

None routes open work to the row.
<!-- absence-ok: the search and sha are named in this paragraph -->
