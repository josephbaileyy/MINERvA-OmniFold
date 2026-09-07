# `pm_inspection` — the executable packaging of a predeclared read-only inspection

**STATUS: FOR REVIEW. NOT SUBMITTED, NOT APPROVED, NOT EXECUTED.** Nothing here has been run
against the real inputs. Admission is blocked on prerequisites recorded below.

These four files package the fixed reads already declared in
`docs/orchestration/PREDECLARATION-20260906-pm-root-inspection.md` §3–§4. They add no
scientific scope: every path opened and every object read was declared before this code
existed.

| file | role |
|---|---|
| `INPUT-BINDINGS-20260908.json` | the thirteen inputs, with digests and their provenance |
| `pm_root_inspect.py` | producer — opens each input `READ`, performs the declared reads |
| `pm_root_validate.py` | terminal validator — classifies capture, selects one branch |
| `test_pm_root_inspection.py` | 19 focused tests, no ROOT required |

The contract lives at `docs/orchestration/contracts/CONTRACT-20260908-pm-root-inspection.json`.

## What COMPLETE means, and the three things it does not mean

`COMPLETE` means **the declared measurements were captured**. It is not a scientific grade,
it does not discharge PM-1, PM-3, PM-4 or PM-5, and it does not make anything citable for a
gate movement. The validator has no acceptance threshold because none was authorized, and
inventing one here would be inventing a scientific criterion.

## The distinction the validator exists to keep

**An expected absence is a measurement. A missing required input is a fault.**
`hRowIndex5D` absent from G is the *answer* to a declared question — G's committed inventory
is 13 keys and contains neither `hRowIndex5D` nor `hXSecND_flat` — so absence is `COMPLETE`.
A required input that is missing, wrong-sized or digest-mismatched is `ERROR`. Collapsing
those two would turn a real measurement into a fault, or a fault into a measurement.

## The PM-4 provenance gap is preserved, not closed

Digests for the central CV and the ten endpoints were measured **2026-09-08 by ordinary
read-only access**. They bind the bytes those files hold **now**. They are **not** evidence
that these bytes were G's historical production input: G's own hash receipt does not bind the
central CV. Every digest this producer computes is labelled
`reconstructed_through_producer_input_route` and never `read_from_G`.

CS's digest is the **historical** `support_family_sha256` from
`nd-unfolding/active_universe_5d/standard/candidate/std_component_manifest.json`. **CS is not
re-hashed** — it is 41.4 GB; size is checked and bytes are not. That limitation is stated,
carried in the bindings, and asserted by a test.

## Runtime output never lands inside a checkout

`--out` must be **absolute** and outside every git working tree; the producer refuses
otherwise, and two tests hold it to that. `docs/orchestration/state/pm-root-inspection-20260908/`
is the **later, deliberate, committed evidence destination** — not the runtime directory.

## Environment yes, analysis code no

The deployed tree at `/pscratch/sd/j/josephrb/MINERvA-OmniFold` supplies the **installed and
built environment** only (`setup_salloc_env.sh`; its conda prefix and build setups are not in
any fresh clone). No analysis code is imported from it. That is measured rather than asserted:
`module_provenance()` records every loaded module's file and lists any resolving under that
root, so an accidental import shows up in the report instead of passing silently.

That tree is 235 commits behind `main` and carries dirty paths, so it **cannot be pinned by
commit**. Input identity is therefore by digest, never by commit reference.

## Known prerequisites, none of them resolved here

1. **TTY approval.** `campaignctl.py:3540-3541` refuses approval without an interactive
   terminal, and requires the staged proposal digest pasted back. No agent session can supply
   this. It is a human act, by design.
2. **The admission ref cannot be written from any available host** under campaignctl's
   sanitised environment. Perlmutter has no HTTPS credential; the Mac has two and can show
   neither to the tool, because both live in scopes campaignctl disables.
3. **Attendance.** Attended means the executing session stays present through completion and
   cleanup. An initial approval alone is not attendance.
4. **PyROOT on a compute node is unmeasured.** It works on a login node under this
   environment; the compute-node case is a declared unknown and must fail as `ERROR`, not hang.
