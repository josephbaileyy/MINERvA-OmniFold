# ROUND-5 REPAIR PACKET — `F-2(a)` and `F-17(a)`, ready for an independent grader

**CITABLE FOR:** what was repaired, the sha it is constituted at, and the exact read-only commands a
grader runs to check it.

**NOT CITABLE FOR:** a grade. **GATE 1 IS NOT CLOSED.** The round-4 verdict stands at **16 PASS /
2 FAIL** until a grader who is **neither this builder nor the round-4 verifier** re-grades. This lane
built every artifact below and is disqualified from grading any of it.

**Authorized by Joseph 2026-08-23**, bounded: in-scope code, tests, docs and receipts; commit and
push; refresh the frozen deployment; read-only cluster validation. **Not** authorized and **not
done**: any Slurm or science submission, the k=0 rehearsal, covariance construction or adoption,
deletion or release of any scientific artifact, or changing the Gate-1 verdict.

---

## 0. THE RE-DECLARED SHA — `PR-01` expired on this repair and is re-taken

```
MNV_CODE_ROOT  = /pscratch/sd/j/josephrb/k0r2/clean
sha            = f3c27870aa775b8a4ceb77a2e081169e80e76e5d
tracked source = 778 files          (775 -> 778: the three new env tools)
listing sha256 = 70fb59d4ce5b6ebbc005dcefa716c44d3c7cda8f6779118fdf094bebbdfba922
A-2(a)-(g)     = A2_CHECK_EXIT=0 on --require-clean --require-readonly --require-checkout
                 --require-no-nested-checkout --require-not-nested, re-verified as a
                 SEPARATE observation after --apply-readonly

MNV_ENV_ROOT      = /pscratch/sd/j/josephrb/k0env        (outside every checkout)
MNV_CONDA_PREFIX  = ~/.conda/envs/root_6_28
env manifest      = nd-unfolding/mnv_env_manifest.tsv, 14 members
                    tsv_sha256 499e923aaabfcf310e0abdc4a5bdd877cf58d3a9c52bd41d76fa0a05eb131392
```

**The previous declaration (`6113a34d`, 775 files, `cc004894…`) is SUPERSEDED**, exactly as its own
expiry clause said it would be: *"falsified by … any `.py`/`.sh` add or delete."*

---

## 1. BOTH FAILURES WERE REPRODUCED BEFORE ANYTHING WAS CHANGED

A completion requirement, and it is also the only way to know the repair addresses the real defect.

```
F-2(a)  bash 4.4.23 on saul, the launcher preamble replicated verbatim:
          .../k0r2/clean/setup_salloc_env.sh: line 18:
          .../k0r2/clean/unbinned_unfolding/build/setup.sh: No such file or directory
          REPRO_EXIT=1        # and REACHED_LINE_AFTER_SOURCE never printed

F-17(a) `M-5` reported `REPO=` at 0 of 8 and read as though the `.sh` half was repaired,
        while the launcher still carried an UNGUARDED
        `source "${CODE_ROOT}/setup_salloc_env.sh"` at :81.
```

---

## 2. WHAT CHANGED, against the six required elements

| # | requirement | what was built |
|---|---|---|
| 1 | **`MNV_ENV_ROOT`, mandatory, no fallback** | `ENV_ROOT="${MNV_ENV_ROOT:?…}"` in all eight. Separation verified on the **canonical target**, so a **directory** symlink is allowed and a view onto a checkout is not. `MNV_CONDA_PREFIX` is mandatory too — `ROOT628_PREFIX` was `${VAR:-default}`, so verifying the activator's bytes did not determine which conda executed. |
| 2 | **Digest manifest over the FULL closure, before any source** | `mnv_env_preflight.sh`, **pure bash** (it runs before the activator, and the pre-conda interpreter is 3.6.15). 14 members: activator + 2 hop-1 + 3 hop-2 + 8 conda `activate.d/*.sh`. **Hop 3 is empty, measured.** Fails closed on missing, mismatched, **extra**, unreadable, and on an env root inside any checkout. `mnv_env_manifest.json` carries the TSV's own sha256, so an edited TSV is detectable by a reader that cannot parse JSON. |
| 3 | **No canonical path on the three channels** | `unbinned_unfolding/build/setup.sh` **regenerated self-locating**. Four further latent defaults fail-closed: `setup_MAT.sh`, `setup_MAT-MINERvA.sh`, `setup_UnfoldUtils.sh`, `MINERvA101/opt/bin/setup.sh` each did `PREFIX=${MINERVA_PREFIX:-"<canonical>"}`. **All six closure members now contain zero canonical references.** `mnv_env_pathcheck.sh` inspects `PATH`/`PYTHONPATH`/`LD_LIBRARY_PATH` **after** activation — allowlist, not denylist. |
| 4 | **`_mr_lib` bound before use in all eight** | Containment check moved **above** the source; **0 of 8** remain bind-after-use. The extraction window of `LibraryResolverSurvivesSbatch` moved to an explicit `END RESOLVER` marker — **the test was updated rather than the defect retained to keep an old fixture green**, per the authorization. |
| 5 | **Route the Gate-5 template** | Its header now names `MNV_ENV_ROOT` as the same contract, clause by clause, so two environment-root conventions cannot drift. **Its diagnosis already contained the three-reference count, absence-by-construction, the symlink distinction, the `set -u` kill and "a separate `GATE5_ENV_ROOT`"** — and was referenced by nothing on the k=0 path, so round 4 paid to re-derive it. |
| 6 | **Real-activator tests** | The fixture now builds a **real multi-hop closure** in its own root. 15 arms, positive controls first. |

**Invariant preserved: `set -u` is NOT added anywhere**, and every new file restates why —
`activate-binutils_linux-64.sh` references `ADDR2LINE` unbound and killed job `57235710` in ten
seconds.

---

## 3. THE POSITIVE CONTROL A GRADER SHOULD RUN FIRST

**The shipped bytes of the deployed launcher**, not a replica and not the fixture:

```
$ ssh saul.nersc.gov
$ export MNV_CODE_ROOT=/pscratch/sd/j/josephrb/k0r2/clean
$ export MNV_DATA_ROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold
$ export MNV_ENV_ROOT=/pscratch/sd/j/josephrb/k0env
$ export MNV_CONDA_PREFIX=$HOME/.conda/envs/root_6_28
$ export MNV_ENV_SYSTEM_PREFIXES="/usr /bin /sbin /lib /lib64 /etc /opt /global/common/software $HOME/.local/bin $HOME/.nvm"
$ L=$MNV_CODE_ROOT/nd-unfolding/sbatch_bootstrap_5d_gpu.sh
$ END=$(grep -n 'mnv_env_pathcheck "\$ENV_ROOT"' "$L" | head -1 | cut -d: -f1)   # 94
$ sed -n "1,${END}p" "$L" > /tmp/preamble.sh && bash /tmp/preamble.sh ; echo "EXIT=$?"

[env-preflight] OK: 14 closure member(s) verified against mnv_env_manifest.tsv; env root /pscratch/sd/j/josephrb/k0env
[env-pathcheck] OK: 45 search-path entr(ies) checked; none inside a checkout, none outside the declared environment
EXIT=0
```

**`[env-pathcheck] OK` prints only after the `source` RETURNS.** That is the statement round 4 could
not make: execution reaches the line after the activator.

---

## 4. `F-17(a)` RE-MEASURED — `M-5` restated so it answers about the `.sh` ROUTE

`M-5`'s round-4 failure was that it measured the greppable half and reported it as the whole.
Re-measured at `f3c27870`, on the four things the `.sh` route actually consists of:

| what | round 4 | now |
|---|---|---|
| `REPO=` assignments | 0 of 8 | **0 of 8** |
| **UNGUARDED activator sources** | **8 of 8** | **0 of 8** |
| activator sourced from `ENV_ROOT` | 0 of 8 | **8 of 8** |
| **`_mr_lib` bind-after-use** | **8 of 8** | **0 of 8** |

`M-2` unchanged: **125** importable names, **zero** stdlib collisions. `M-4` unchanged:
`b2d7d4ca`, **721** dirty (**a drifting quantity — re-measure, do not inherit**).

---

## 5. `F-8(a)` / `P-5` IS RE-OPENED AT THE NEW SHA — and `P-5` gains a FIFTH blind spot

**Re-opened, not inherited.** `F-8(a)` is bound to the pinned sha and the sha moved. Per the
round-4 exchange, the next grader must **re-measure it, never carry it forward**.

`P-5` gains the channel the round-4 verdict exposed:

> **Blind spot 5 — `PATH` / `PYTHONPATH` / `LD_LIBRARY_PATH`.** The OI-136 guard wraps Python
> **import resolution**. It sees a `sys.path` consequence and is **blind to `PATH` and
> `LD_LIBRARY_PATH` entirely**, so a verified file can still place a checkout on the search path by
> **content**. This is no longer only a disclosure: `mnv_env_pathcheck.sh` measures all three after
> activation, and the arm fires **per channel**.

`P-6`'s entrypoint set is unchanged in shape and must be re-run at the new sha.

---

## 6. EVIDENCE A GRADER CAN RE-RUN

```
suite      TMPDIR=<writable> python3 -m pytest nd-unfolding/tests/{test_k0_launcher_two_roots,
           test_k0_preflight_exclusion_census,test_uq_remediation,test_source_manifest_constitution,
           test_p4_ratchet_fail_closed,test_mnv_guarded_run}.py -q
           -> 390 passed, 2 skipped
bindings   python3 docs/orchestration/verify_hash_bindings.py      -> rc 0, ALL BINDINGS INTACT
census     python3 nd-unfolding/mnv_preflight_census.py            -> 14 guarded + 16 preflight
                                                                      + 0 unclassified  (UNCHANGED)
manifest   python3 docs/orchestration/generate_manifest.py --check -> rc 0
env        python3 nd-unfolding/mnv_env_manifest.py --env-root ... --conda-prefix ... --check
```

**The census is the load-bearing null here:** the guarding boundary is **unchanged** at 14/16/0, so
this repair did not widen or narrow ruling 21's boundary while touching all eight launchers.

---

## 7. THREE OF THE BUILDER'S OWN BUGS, each found by a control rather than by review

Recorded because each is one of this campaign's named shapes, and because a packet that lists only
successes is not evidence.

1. **The EXTRA check was directory-scoped** and refused a correct environment over four unrelated
   scripts in a shared `MINERvA101/opt/bin`. Now scoped to `activate.d`, where conda **globs** and
   every member really does execute — and there is an arm asserting the unrelated script is *not* an
   extra.
2. **The path helper compared a RESOLVED entry against an UNRESOLVED prefix**, so a correct
   predeclaration could never match where `/global/homes` symlinks to `/global/u2`. Both sides are
   canonicalized now. *A containment check must resolve both sides or it is not the check it claims.*
3. **The manifest JSON emitted RELATIVE paths beside `sha256` keys**, which
   `verify_hash_bindings.py` collected as **repo** bindings and resolved against the repo — reporting
   `MISMATCH setup_salloc_env.sh` that was really a mis-resolution. Absolute paths fixed it, and the
   binding inventory did **not** need moving, because off-repo artifacts are correctly unresolvable.

---

## 8. WHAT THIS PACKET DOES NOT ESTABLISH

- **It does not grade Gate 1**, and it does not touch `F-1(a)`, `F-3`…`F-16` beyond re-declaring the
  sha they are measured against. **All of them are re-opened by the sha move.**
- **It does not prove a leg runs.** The positive control reaches the line after the activator; it does
  not run science, and **no Slurm job was submitted**.
- **The env root is a real directory today, not a shared immutable tree.** A shared tree is permitted
  by the design and is **not** what is deployed; if one is adopted, note that a shared tree makes the
  digest manifest **more** load-bearing, since it is mutable by an owner outside the deployment.
- **`MNV_ENV_SYSTEM_PREFIXES` is a submitter-declared allowlist.** The two `$HOME` entries above are
  predeclared **explicitly** and deliberately are not defaults.
