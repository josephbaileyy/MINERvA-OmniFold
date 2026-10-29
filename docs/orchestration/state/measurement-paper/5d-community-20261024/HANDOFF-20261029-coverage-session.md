# Handoff: the coverage session (cheap tier), 2026-10-29

**By** the measurement session `coverage` (ListAgents), which ran the cheap tier of
`DECISION-20261028-joseph-d2-approved-and-cheap-tier.md` item 2 under the director. It is written for a fresh session
that continues the cheap tier from a cold start.

**This is a working record.** It authorizes nothing. Joseph's decisions and the director's bindings govern, and where
this file and a record differ, the record wins. It names only `main`, pushed branches and committed records.

**State as of** `main` `1d25acd9`.

## 1. Role and rules

- **The director** is the session `director`: the paper-tighten lane, reached by `SendMessage`. It rules, binds and
  merges, and this session never merges its own PRs. Joseph's decision record names this session as the one that runs
  the cheap tier, under the director (`DECISION-20261028-joseph-protections-n4-release-retrospective.md` item 5).
- **The standing constraints** are the director's handoff §2 (`state/2d-closeout/stageF/director-handoff-20261027/HANDOFF.md`):
  - nothing published, and no contact with coauthors, Ben, the collaboration, MINERvA or NERSC;
  - jobs under 12 h, CPU only, QOS regular, nothing to CFS;
  - no work in the shared checkout; explicit `git add` paths;
  - commit with `-c core.hooksPath=.githooks -c user.name="measurement session (Claude)"
    -c user.email="measurement-session@minerva-omnifold.invalid"` and the `Co-Authored-By` trailer.
- **The workflow for each item:** a declaration PR, then the director's binding, then a deploy and the run exactly as
  bound, then a report PR. A STOP is reported unrepaired.

## 2. What is done

| item | records | PRs |
|---|---|---|
| step 1: the inputs' retention | `FD-CT-RETENTION.md` (with its dated W2b correction) | #460, #463 |
| 3b's npz inputs on HPSS | `FD-CT-PRESERVE-REPORT.md`; `/home/j/josephrb/mnv-5d-ct-3b-inputs-20261028` | #463 |
| the pscratch keep/archive/delete proposal | `FD-PSCRATCH-RETENTION-PROPOSAL.md` | #467 |
| 5B's input source | `FD-CT-5B-INPUTS.md` (MP-1's zero per-playlist loops; the bkgaware loops' risk accepted) | #481 |
| 3a, 4C, 5A | `FD-CT-READERS-DECLARATION.md`, `-BINDING.md`, `-AMENDMENT-1.md`, `-BINDING-AMENDMENT-1.md`; reports `FD-CT-READERS-REPORT.md` (3a, 4C) and `FD-CT-READERS-5A-REPORT.md` | #478, #482, #485, #491, #495, #497 |

**Open:** the 3b declaration, `FD-CT-3B-DECLARATION.md`, PR #504 (branch `fd/ct-3b-declaration`), awaiting the
director's binding.

## 3. What is next

1. **3b, after its binding:** deploy and test (§2.1 of the declaration), submit (§2.2), read out (§2.3), preserve the
   13 closures to HPSS (§2.4), then `FD-CT-3B-REPORT.md`.
2. **5B, the per-period 5D unfolds, not yet declared.** The input design is accepted (`FD-CT-5B-INPUTS.md` §5). The
   director added a condition: any fallback CV event loop is CPU only, declared and bound separately, and priced from
   MP-1's measured per-variant cost (`state/measurement-paper/phase1/mp1/S1-REPORT.md:94-102`). The design is the 2D
   period-unfold's on the 5D inputs (`LIMITATION-PLAN-ADDENDUM-20261028.md` §5.2), and it needs:
   - per-period merges;
   - a per-period flux;
   - `nn_dump_inputs.py` and `s5c_dump_bkg.py` per period;
   - a pooled ALL control against S1's f, at a tolerance declared first;
   - about 37 unfolds.
   No existing 5D tool takes a playlist subset.
3. **The pscratch decisions** are Joseph's, through the director (`FD-PSCRATCH-RETENTION-PROPOSAL.md` A0–A5). F0's
   per-experiment table is the first candidate. Re-measure the access dates before about 2026-12-17.

## 4. Lessons recorded in code or records

- **Leak guard and near-f integrals.** An integral equal to f to within LEAK_REL puts f/X ≈ 1 in the guard's table, and
  every "1" in a string is then refused. `fd_ct_readers.near_f` drops such integrals (amendment 1). Any new reader that
  passes data integrals to the guard should do the same.
- **Mixing with `main`.** Since #486 the overrides file is sorted by path, and `merge_main.sh` takes a sorted union
  (#489). For a hand merge, take `main`'s CATALOG and overrides and add this branch's rows, the overrides row at its
  sorted position. A keep-both resolution re-adds rows that `main` edited or deleted. `origin/main` is shared across
  worktrees, so a merge in one worktree can be overtaken by a fetch in another; merge the ref you just fetched, by sha.
- **Mutation receipts edit files in place.** Never stop one mid-mutant. If one is stopped, reverse the mutant by hand
  and check the file's sha256 before anything else (`FD-CT-READERS-DECLARATION.md` §11).
- **A planted-leak test must run in O(1) units,** or the guard's 10⁻³⁰ floor, not its table, refuses it.

## 5. Where things are on the cluster

`$P` = `/pscratch/sd/j/josephrb`:
- `fd-ct-readers-20261028/`: the bound 3a, 4C and 5A run, and the 5A diagnostic;
- `fd-ct-readers-am1-20261029/`: the 5A rerun;
- `fd-ct-preserve-20261028/`: the 3b inputs' tar, also on HPSS;
- `fd-ct-run-steps-20261029/`: step scripts and test clones.

All join the pscratch retention list.
