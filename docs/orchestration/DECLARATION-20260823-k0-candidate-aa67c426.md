# DECLARATION — the repaired k=0 candidate sha, and A-2(a)–(g) filed against it

**CITABLE FOR:** the constitution of the execution tree at `aa67c426`, measured 2026-08-23.

**NOT CITABLE FOR:** a Gate-1 pass. **Gate 1 does NOT pass at this sha and has not been graded here.**

**SUPERSEDES** [`DECLARATION-20260823-k0-candidate-sha.md`](DECLARATION-20260823-k0-candidate-sha.md),
which declared `a54038b2`. That declaration was **true when made and remains historically valid**;
it is superseded because the tree it declared cannot execute legs 5a/5b.

---

## 1. THE DECLARED SHA

```
sha     = aa67c426afaa9b6ca91c9996637a6bade950da9a
branch  = build-k0-execution-integrity
tree    = /pscratch/sd/j/josephrb/k0r2/clean
```

**Why this branch and not `main`.** `main` does not carry the Gate-1 apparatus — no
`lib_mnv_env_preflight.sh`, no `lib_mnv_env_pathcheck.sh`, no parity gate in any launcher. The
repair was authored on `main` and **cherry-picked here**, because deploying `main` would have
deployed a tree without the thing round 9 graded.

**This document does not name its own commit**, by the same convention as its predecessor and
`DECLARATION-20260822`: a declaration is paperwork *about* an execution tree and lives where the
paperwork lives. **The deployment is at the declared sha**, so A-2(a) holds exactly. Falsifier:

```bash
git -C /pscratch/sd/j/josephrb/k0r2/clean rev-parse HEAD     # must be aa67c426…
```

## 2. A-2(a)–(g), EACH MEASURED SEPARATELY

| # | requirement | result | evidence |
|---|---|---|---|
| **a** | `rev-parse HEAD` equals the declared sha | **MET** | `aa67c426afaa9b6ca91c9996637a6bade950da9a` |
| **b** | `git status --porcelain` emits zero lines | **MET** | `0` |
| **c** | a checkout by the guard's own definition | **MET** | `--require-checkout` **rc=0** |
| **d** | no nested checkout beneath it | **MET** | `--require-no-nested-checkout` **rc=0** |
| **e** | not nested inside another checkout | **MET** | `--require-not-nested` **rc=0** |
| **f** | full source manifest over tracked `*.py`/`*.sh` | **MET** | **782** files, listing sha256 `fa3489e22168954bebcc9a602338d924582fd231643bfa285b3a9225e7535420` |
| **g** | write protection applied | **MET** | `--require-readonly` **rc=0**, and independently `find … -type f -writable \| wc -l` → **0** |

**Every rc taken with `--write` or `--compare`.** Run bare, `mnv_source_manifest.py` returns **rc=2,
"COULD NOT LOOK"**, which is never "clean".

**A-2(f) as a gate:** `--compare` **rc=0**, `SOURCE MANIFEST IDENTICAL (782 files, fa3489e2…)`.

Manifest at `/pscratch/sd/j/josephrb/k0r2/declarations/aa67c426/source-manifest.json`, file sha256
`622ddc0ada33234d5b420130cd6e60e17ead8b2669b6e77436f0f57a89e2a405`, made read-only.

## 3. WHY 782, AND THE EXPIRY CLAUSE

`a54038b2` → 780; `aa67c426` → **782**. The two additions are
`nd-unfolding/tests/test_k0_5ab_separated_roots.py` and
`nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py`. **`compare_unified_throw.py` was modified,
not added, and a modification is count-neutral** — stated because the last declaration's provenance
gloss counted renames as adds and had to be corrected.

**Falsified by any add or removal of a tracked `*.py` or `*.sh`, and by nothing else.** Re-run before
the first `sbatch` and again after the last leg. **Do not inherit these numbers.**

## 4. WHAT THIS DOES NOT DO

- It does **not** pass Gate 1, and **round 9's PASS does not transfer to this sha** — see the packet.
- It authorizes **no** Slurm submission. None was made.
- The 415 products of the failed run at `a54038b2` are quarantined and are **not** reusable
  components of any accepted member — receipt `dfef7871`.
