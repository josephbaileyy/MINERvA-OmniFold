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

---

## SECOND PASS, 2026-09-20 (later the same day, after the clause-(c) merge at `ff0b6df0`)

**Same rule, same verification:** every tip below was checked with
`git merge-base --is-ancestor <sha> main` **before** any ref was deleted, so **no commit was lost**
— each deletion removed a name, not history. `git fetch origin <sha>` still reaches any of them.

### On `origin` — 2 name(s)

The clause-(c) lane's 69 commits are now **on `main`** (see
[`INDEX-20260920-retained-branches-not-on-main.md`](INDEX-20260920-retained-branches-not-on-main.md)),
so its branch name no longer holds anything `main` does not.

| deleted name | commit it pointed at |
|---|---|
| `lane/pm-root-inspection-20260906` | `43468c04572d1f9b0b58ce94a2035d6f3b71c0aa` |
| `lane/z-criteria-independent-assessment-20260910` | `935b75585a7b9cc39cd52d4aa001df4edbea875f` |

### Local refs in the primary checkout — 64 name(s)

These were **local only**; none existed on `origin` at deletion time, so nothing shared changed.
They are recorded to the same standard anyway, because a citation does not know whether the name it
uses was local.

| deleted name | commit it pointed at |
|---|---|
| `codex/gate1-round2-f17a-20260830` | `077d81750baefdfdc6c32fd26e263a5fbb88737c` |
| `codex/gate1-round2-f17a-20260830-personal` | `22fc4e84d27c6728c941178556b93e443f85df23` |
| `fix/merge-gate-committed-semantics-20260908` | `e19822f253fdd440a3bebd89031c90fa0196b0a3` |
| `integrate/collector-revision-pins` | `23334c3fbf7fe98ec5897235a1f2d645c6fb3aca` |
| `integrate/family-a-record` | `a65e23a67b9d8c70c563fffb434894369428b08c` |
| `integrate/guard-idempotence-20260909` | `9dd282c4758916066a9cb15a01147631871eb9a1` |
| `integrate/m-amendment` | `ceb474cc979c57bd0c0f4d6879f96d929e740157` |
| `integrate/m-equivalence` | `48bace8ec17eb2842c036ff4111f8c5cf52d1112` |
| `integrate/manifest-repair` | `6f24fb0097a7603b7d6acb695de06dbb3f3ea157` |
| `integrate/packet-plan` | `2254d7fa19c7ad931bccdd481981d74a3d39c338` |
| `integrate/pm-20260909c` | `210cc742d6c1b1defe7a89cd818b39cc0f6a76d7` |
| `integrate/pm-capture-20260909c` | `0d49b97b77f39fa3430fe6ff6d34ed5ae89b4260` |
| `integrate/pm-proposal-20260909b` | `c52fe7dc2c6ac5e17c4d07475fb67a18c0257517` |
| `integrate/rootpath-20260909` | `803b6e061c265e00e36e005c79485f1844845cfb` |
| `integrate/sep09-talk` | `5580d1d5b68b87d8e7e24a8ac041a39e0d7ed226` |
| `integrate/spec22-and-registration` | `923e13236fa6212f9df59d69b9655a03854eea7f` |
| `integrate/throw-corrected` | `bea0dabd6dc88ffdf5ba339a0e8f4232973765a1` |
| `integrate/z-build` | `93021448691429d07c22ffe80685309251497ca2` |
| `integrate/z-corrections` | `c18f9daaf974cdef80a8333126ecf268fca0db92` |
| `integrate/z-plan` | `d147880fc7e4a4078e5b2d5e51aa4334d0e1736f` |
| `lane/authorization-batch-route-20260908` | `2712692a30fe4f6393f9595d1f2920716ea09101` |
| `lane/binding-collector-revision-pins` | `ab341cc47702f4dcc62c21b44be42443ee99dbc8` |
| `lane/family-a-execution-record` | `6875ede2ad38f4bc2a8498f676d1cfb6d0b9e073` |
| `lane/finding-registration` | `cd973e42d49aab2aa9bf71c69451dc0f3ae73b7d` |
| `lane/guard-firing-census-20260907` | `95de8898dc4addfe0c6187e238bd85b106b98853` |
| `lane/guard-install-idempotence-20260909` | `5b84f5e278b57892f1204abf8d7d4795f4d87891` |
| `lane/m-builder-equivalence-20260910` | `37e5e53d164e5805c123de65a487ec4fe8d783d4` |
| `lane/m-finding-amendment` | `2ebe191d3e766f47cabcb7a066b598705ad1c755` |
| `lane/manifest-committed-only` | `f5d868121f8b552ae3c07ac4358586740dd11392` |
| `lane/merge-gate-clean-merge-20260908` | `71a2b8f39fb4e9d66aaf42ffc8e7ccf9e7b7534a` |
| `lane/merge-gate-finding-t-20260908` | `fd793715b3fc38b4b16926ca9b0496107cdad1de` |
| `lane/packet-bindings-resolved` | `205a2139642719b2b83e7f606c69528674261188` |
| `lane/pm-capture-20260909c` | `420c6f48158ca5f95b7d3179a4cfaab582d767f1` |
| `lane/pm-contract-batch-route-20260908` | `9f12c728447e41a54314af2c5d6c740171274be8` |
| `lane/pm-inspection-20260909c` | `a2525342d5489b0558328a7fbbd7785646c6e477` |
| `lane/pm-inspection-executable-20260908` | `da8179f0c57a35d25fa6aed36da74b28afed5b65` |
| `lane/pm-inspection-proposal-20260910` | `4a175df0115f7928508bd177d0a8112f3e64ea97` |
| `lane/pm-inspection-round4-20260908` | `e3419a9225028d23c37904c29b9d9642672fd15a` |
| `lane/pm-launcher-batch-20260908` | `f2747e39444de94c8241bc5f27ef00cfb9a4c492` |
| `lane/pm-root-inspection-20260906` | `43468c04572d1f9b0b58ce94a2035d6f3b71c0aa` |
| `lane/pm-staging-runbook-20260908` | `1e878d194ec498f19dddf34e42c8b5e921c477be` |
| `lane/r5-followup-merged-head-20260907` | `899ab957d56fa6690a999b424c0c0461d53a8bf7` |
| `lane/r5-followup-ownership-20260907` | `e81e146d5ddd4cf42261582807c5b0319ebd9c6a` |
| `lane/sep09-ai-research-talk` | `803b6e061c265e00e36e005c79485f1844845cfb` |
| `lane/sep09-talk` | `f71ad1169ce83f7fc0f7a0a1bbc4e312f111a909` |
| `lane/ssh-pin-20260908` | `49bc0bb10db1288baa917da959dc336299708970` |
| `lane/throw-source-corrected` | `e4e1662ce0240df5d42042b2a0a5d1bf41e47d82` |
| `lane/transport-evidence-20260908` | `427a26620ac854769ab03c37d309238bf9f34c00` |
| `lane/transport-positive-control-20260908` | `4e36a67956f293940f506cb7aef23f44e987d4e8` |
| `lane/y-cause7-spec-and-scope` | `10c24678d6ebd002b0cc9d2fe35320e8c8136c14` |
| `lane/z-build-integration` | `979ffe8207bd2a771a71ad8cb6cd394ce50944e4` |
| `lane/z-construction-plan` | `99d3b9bb1de3b14af0f513270bbe44a641e37776` |
| `lane/z-corrections` | `f13018656a426758fc733aeb7a2b712004d6baf3` |
| `lane/z-criteria-independent-assessment-20260910` | `935b75585a7b9cc39cd52d4aa001df4edbea875f` |
| `lane/z-implementation-20260907` | `d298b446f2d1390b4d10facacf552bba6fd46c80` |
| `lane/z-operand-schema-20260908` | `610d0882359bac142c9e0be86d8dbcc30e190a13` |
| `lane/z-spec-rev22-stale-min-rule-20260910` | `10e016bc8bdf99a1ecaaa34bff1ea94bea915b91` |
| `r5-accounting-requeue-repair-20260906` | `72bcd2f6c2f1bb4d01f3db66194bf390591a7676` |
| `w1r12-credential` | `a302ed2615d3f2323cba7dfe59191de225ad1461` |
| `wave1-integration-20260903` | `7708c24c69baf27e38eb8dbfc57745b331c7d9c4` |
| `worktree-agent-a02661486e0bccbfc` | `9dba11949df648aa31bc179ac9f2c0cfaa293742` |
| `worktree-agent-a0b75a3977fe1b61f` | `9dba11949df648aa31bc179ac9f2c0cfaa293742` |
| `worktree-agent-a3caedc3fd18bfb46` | `77a4af38c259f51ed2ad044d8c3fc8e1f40e2c3c` |
| `worktree-agent-a9ae492934a2e1843` | `9dba11949df648aa31bc179ac9f2c0cfaa293742` |

### ⚠ FOUR MERGED BRANCHES WERE **NOT** DELETED, and the reason is not caution

| retained name | why |
|---|---|
| `decision-packet-20260902-cause7-cause3-stop` | checked out in a live worktree |
| `lane/z-precursor-repairs-bg-20260911` | checked out in a live worktree |
| `presentation/sep09-ai-research` | checked out in a live worktree |
| `worktree-permanence-scope-ruling` | checked out in a live worktree |

Each is fully merged into `main` and would otherwise qualify. **Deleting a branch that another
worktree has checked out leaves that worktree on a ref that no longer exists, and its stale index
then reads as a staged revert of everything `main` has gained since.** Git refuses the deletion for
exactly this reason; the refusal is not routed around. Delete them from the worktree that owns each
one, or after removing that worktree.

**And the retained-branch set is unchanged otherwise:** the fifteen rows of
`INDEX-20260920-retained-branches-not-on-main.md` hold commits `main` does not, so none of them was
a candidate here. Only the clause-(c) row left that index, and it left by being merged.
