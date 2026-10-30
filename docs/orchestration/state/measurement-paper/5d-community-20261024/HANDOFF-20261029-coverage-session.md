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

**3b:** declared in `FD-CT-3B-DECLARATION.md` (#504) and bound in `FD-CT-3B-BINDING.md` (#507) at `e904d635`. Its
run is in progress in this session; its report will be `FD-CT-3B-REPORT.md`.

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

   **Read-only notes for the fresh 5B session** (the director ruled that 5B goes to a fresh session, 2026-10-29; none
   of this has been built or run):
   - **The 2D analogue:**
     - `state/2d-closeout/period-unfold-20261014/scripts/build_inputs.sh` `hadd`s the per-playlist files into PA (1A–1F),
       PB (1G, 1L, 1M), PC (1N–1P) and ALL, so that each period carries its own POT;
     - `build_flux.py` writes each period's data-POT-weighted flux from `2d-unfolding/baseline_flux/runEventLoopMC_<pl>.root`;
     - its control `pu_CTRL_s42` reproduced production to about 1e-11 (`period-unfold-20261014/REPORT.md` §1), and
       the test charged 1.9414 node-h;
     - the noise reference was seed 43 and 10 bootstrap replicas per period (`state/2d-closeout/playlist-term/DESIGN.md:29`,
       `pu_X_s43` and `pu_X_b01–b10`).
   - **The 5D mapping:**
     - merge MP-1's `evloop/zero/runEventLoopOmniFold_5D_<PL>_zero.root` per period with
       `2d-unfolding/uq/hadd_universes_full.py`, as MP-1 merged them (`measurement-paper/phase1/mp1/mp1_s1_pipeline.sh:38-48`);
     - `nn_dump_inputs.py --axes eavail,q3,W`, which takes any `--omnifile` and `--mcfile`, the flux histogram
       `pTmu_reweightedflux_integrated` (`nd-unfolding/nn_dump_inputs.py:34-35`, `:73`), so a period flux file of
       `build_flux.py`'s form fits;
     - `s5c_dump_bkg.py --omnifile <period merge> --npz <period npz>`;
     - the (e) data unfold as S1's central value was made: `s5p_numerics.py` in data mode, giving `data_b-_j-.npz`.
   - **A sharp control:** the ALL chain from the zero loops is MP-1's own zero chain.
     - MP-1's zero data unfold `mp1s1_zero_b-_j-.npz` (`f1d5178a…`, `build_cresp.PRODUCTS["zero"][0]`) is its natural
       reference.
     - The lateral dumper and `nn_dump_inputs.py` may differ in detail: the −9999 rows, and the background array's
       dtype (`fd/receipts-ct/3b/review/REVIEW.txt`; `FD-CT-5B-INPUTS.md` §1). So whether the reproduction is bitwise
       has to be measured before a tolerance is declared.
     - Against S1's f, the chain difference is W2b's already-recorded one (`publication/w2/W2B-REPORT-20261006.md` §4).
   - **Any reader** that passes data integrals to the leak guard should drop those within LEAK_REL of f
     (`fd_ct_readers.near_f`, amendment 1).
   - **The cost** in the addendum is 37 unfolds × 0.0226 node-h plus 4 dumps, about 1.0–1.9 node-h, cap about 3.0
     (`LIMITATION-PLAN-ADDENDUM-20261028.md` §5.2). That is an estimate: the 5D per-period merges and dumps are unpriced.
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
