# Packet B PB2 production-wiring repair — Agent A

Persistent role `agent-A-standard`, UUID `14951826-0680-4e57-ac92-8a9970bc07f7`, implemented the
sole verifier blocker in a clean detached worktree. No ROOT artifact, covariance, threshold,
physics configuration, scheduler job, adoption, or promotion changed.

The launcher now derives and writes the exact six-path committed-blob map plus receipt schema 2.
`p4_check_receipt.py` independently derives the same closure and cannot authorize `SKIP` until
`check_resume_surface()` passes. Only receipts with neither a schema nor a surface record are the
closed grandfathered class. Root review additionally made every declared pre-binding or unknown
schema reject, so an invented `receipt_schema: 1` cannot fall through to grandfathering.

Real CLI/launcher tests cover direct `omnifold.py` drift, transitive `omnifold_nn_core.py` drift,
omitted `xsec_nd.py`, a non-producing `p4_project_4d.py` change, bounded legacy behavior, malformed
current receipts, degenerate closures, and skip-path reachability.

Independent root rerun after the initial production-wiring repair:

```
269 passed, 25 subtests passed in 30.48s
```

The same verifier then found that `dict.get()` still conflated absent keys with explicit JSON null.
Agent A's same UUID corrected presence handling so grandfathering is reached iff both fields are
absent, and added real-CLI negatives for null schema, null surface, both null, and null schema with
an intact map. Independent root rerun after that correction gives:

```
274 passed, 29 subtests passed in 29.13s
```

`bash -n nd-unfolding/run_p4_*.sh`, `py_compile` for the changed Python gate/helper, and
`git diff --check` also pass. This patch is still subject to the same verifier UUID; PB2 is not
closed until that verdict lands.
