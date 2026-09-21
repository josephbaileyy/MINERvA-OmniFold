# LEDGER 2026-09-20 — branch names deleted from `origin`, and the commit each pointed at

**CITABLE FOR:** resolving a branch NAME cited in an older record to the commit it named.
**NOT CITABLE FOR:** the content or status of any of that work.

On 2026-09-20, 28 branches were deleted from `origin` so that `main` is the single discovery route.
**Every one was deleted only after its tip was verified to be an ancestor of `main`, so no commit was
lost** — deletion removed a name, not history. Each SHA below was re-verified as an ancestor of `main`
and each name re-verified absent from the server immediately before this ledger was written.

**This ledger exists because deleting a name breaks the citations that use it.** Several committed
records cite these branches by name — as status notes, ownership labels, and locations. Without this
mapping a reader could not resolve such a name to a commit. With it, every citation resolves.

To reach any of them: `git show <sha>`, or `git log <sha>`, from `main`. To restore one as a branch:
`git push origin <sha>:refs/heads/<name>`.

**One branch was NOT deleted although its tip is contained in `main`:**
`lane/pm-root-inspection-20260906` at `43468c04572d1f9b0b58ce94a2035d6f3b71c0aa`. Three committed
records — `CATALOG.md`, `FINDING-20260906-r5-meter-undercounted-requeue-attempts.md` and
`SPEC-20260906-complete-scalar5d-successor-Z.md` — cite it by name as the location of receipts at
`21b3d567`/`cd41ff41`. Both commits are reachable from `main`; the ref is retained by Joseph's decision
because it costs nothing and the citations read as routes.

Branches whose tips are NOT in `main` were not deleted and are indexed separately in
`INDEX-20260920-retained-branches-not-on-main.md`.

| deleted branch name | commit it pointed at |
|---|---|
| `evidence/merge-gate-final-68c0185f` | `68c0185f10e1a7f558b900239330f1c21077f081` |
| `lane/authorization-batch-route-20260908` | `2712692a30fe4f6393f9595d1f2920716ea09101` |
| `lane/family-a-execution-record` | `6875ede2ad38f4bc2a8498f676d1cfb6d0b9e073` |
| `lane/guard-firing-census-20260907` | `95de8898dc4addfe0c6187e238bd85b106b98853` |
| `lane/merge-gate-finding-t-20260908` | `fd793715b3fc38b4b16926ca9b0496107cdad1de` |
| `lane/packet-bindings-resolved` | `205a2139642719b2b83e7f606c69528674261188` |
| `lane/pm-contract-batch-route-20260908` | `9f12c728447e41a54314af2c5d6c740171274be8` |
| `lane/pm-inspection-executable-20260908` | `da8179f0c57a35d25fa6aed36da74b28afed5b65` |
| `lane/pm-inspection-round4-20260908` | `e3419a9225028d23c37904c29b9d9642672fd15a` |
| `lane/pm-launcher-batch-20260908` | `f2747e39444de94c8241bc5f27ef00cfb9a4c492` |
| `lane/pm-staging-runbook-20260908` | `1e878d194ec498f19dddf34e42c8b5e921c477be` |
| `lane/r5-followup-merged-head-20260907` | `899ab957d56fa6690a999b424c0c0461d53a8bf7` |
| `lane/r5-followup-ownership-20260907` | `e81e146d5ddd4cf42261582807c5b0319ebd9c6a` |
| `lane/ssh-pin-20260908` | `49bc0bb10db1288baa917da959dc336299708970` |
| `lane/throw-source-corrected` | `e4e1662ce0240df5d42042b2a0a5d1bf41e47d82` |
| `lane/transport-evidence-20260908` | `427a26620ac854769ab03c37d309238bf9f34c00` |
| `lane/transport-positive-control-20260908` | `4e36a67956f293940f506cb7aef23f44e987d4e8` |
| `lane/y-cause7-spec-and-scope` | `10c24678d6ebd002b0cc9d2fe35320e8c8136c14` |
| `lane/z-build-integration` | `979ffe8207bd2a771a71ad8cb6cd394ce50944e4` |
| `lane/z-implementation-20260907` | `d298b446f2d1390b4d10facacf552bba6fd46c80` |
| `lane/z-operand-schema-20260908` | `610d0882359bac142c9e0be86d8dbcc30e190a13` |
| `lane/z-precursor-repairs-bg-20260911` | `41a64f026e22963290a7d64c2182da16db16535f` |
| `lane/z-spec-rev22-stale-min-rule-20260910` | `10e016bc8bdf99a1ecaaa34bff1ea94bea915b91` |
| `lane/z-two-member-campaign-20260919` | `926a92a4096554257b09b7c13c10d0278241ee8b` |
| `pet-typed-keras-adapter` | `9064d59f6c936afa324d999496d6c1a612af4541` |
| `pet-typed-semantic-evidence-integration-r2-20260902` | `462d68bef6e021d03608393b776a0bc17f6d2e15` |
| `r5-accounting-requeue-repair-20260906` | `72bcd2f6c2f1bb4d01f3db66194bf390591a7676` |
| `wave1-integration-20260903` | `7708c24c69baf27e38eb8dbfc57745b331c7d9c4` |
