# B5D BINDING 2: amendments A1 and A2, and the local build of the 5D blocks (laptop, 0 node-h) (director, 2026-11-25)

**Authority:** Joseph, directly to the director on 2026-11-24: "yes build the 5D bias block". B5D-BINDING-1 bound the
read connect, and the read completed (tar sha256 `13e53ec2…`, 1,655/1,655 files). This binding binds amendments A1 and
A2 together, as the director ruled, and the build code that implements the declaration with them.

**Binds** the state merged to main in PR #1316 (merge `69e880bbc0249231c9c06e6768d1aaced8cee247`), at the reviewed head
`f0cdc7b54f71640665e4235f778234f023aa47be`, merged with `--match-head-commit`.

| file | sha256 |
|---|---|
| `docs/orchestration/state/ben-b-20261124/blocks5d-20261124/B5D-DECLARATION.md` (unchanged since BINDING-1) | `676c17fc5982a01c21f4c7feae2f6c8cd32b0b8ecdc69ec93882e5e30c0f0b1b` |
| `docs/orchestration/state/ben-b-20261124/blocks5d-20261124/B5D-AMENDMENT-A1.md` | `3d6a497d2d876c8b0141f8adba2a2a38fb474271a6f64421aef03d0408a55105` |
| `docs/orchestration/state/ben-b-20261124/blocks5d-20261124/B5D-AMENDMENT-A2.md` | `7f120dc64c7f64b2843f545eb2d55e0f0cc657fc30a04a4eb282cbc4db32d602` |
| `nd-unfolding/b5d/b5d_build.py` | `69f11025c4bc0ad0288bb74641c0e76d0286fea1ba9c86531fc25cc7bb27f30d` |
| `nd-unfolding/b5d/test_b5d.py` | `2df87a4d08487c4b65eb2cc9fe74b5c906321674cae53a6674a260f5294ae857` |

## What the director checked

- **The shas.** The director hashed each file from `git show` at the reviewed head before the merge and from main after
  it. Each equals the lane's reported value and the table. b5d_build.py pins the declaration and both amendments under
  C-PIN.
<!-- absence-ok: restates A2's band-state method rule (ACTIVE, RESOLVED-INACTIVE, UNRESOLVED, UNMEASURED), not a claim that a result does not exist -->
- **A2's stop rule is the director's rule.** Each band is ACTIVE if f̂_R − 1 > 3·SE(f̂_R); RESOLVED-INACTIVE if not
  active and SE ≤ 0.5; UNRESOLVED (φ = 1, flagged) if not active and SE > 0.5; UNMEASURED (φ = 1) if no primary ensemble
  keeps the band. The build stops short of V_F only if every band is UNRESOLVED or UNMEASURED. An UNRESOLVED band is
  never inflated.
- **The reads.** agy on gemini-4-hydrogen-xhigh gave GO with 0 blockers and 0 majors on the full delta and on each later
  delta. codex-school's rounds 3–5 and the final and micro deltas end with 0 blockers and 0 majors; every earlier
  finding is fixed and recorded under `reads/`.
<!-- absence-ok: line-trace scope of the lane's coverage run (two lines unexecuted on macOS), not a claim that a result does not exist -->
- **The checks, as the lane reported them from commands:** 68 tests pass; 73/73 mutants killed in one clean run; line
  trace 99% (the `__main__` guard and the Linux renameat2 branch are not run on macOS, where the build runs).
- **CI.** record-checks passed on the reviewed head.

## Rulings

1. **A1 and A2 are bound together** with the shas above. Any changed byte of these five files goes back to the director
   before the build runs.
2. **The price: 0 node-h.** The build runs locally on the fetched products (tar `13e53ec2…`), re-hashed against their
   pins before use. No NERSC contact.
3. **Before the build:** the lane re-hashes the five files above against this table, and the fetched products against
   their pins. Any mismatch is a STOP.
4. **One build.** The build runs once. Any refusal (exit 5) or STOP is terminal; nothing is re-run or tuned on its output
   without the director.
5. **The record goes to the director first,** with every band's state, f̂, SE, and the printed traces. Nothing is
   committed to the note.
6. **Adoption** of C_b, of the fluctuation block, or of any inflated V_F into the reported 16-cell covariance is Joseph's
   decision, made with the numbers and with A1 §7's double-counting caveat named.
7. **Held follow-ups (LOWs, no output change):** A1's PSD wording, the exotic C-LEAK type cases, three tighter tests, the
   second-OSError path, and build()'s docstring. They go in a follow-up PR; none blocks the build.
8. **A reader's figure is not a record.** A number agy printed during its read from committed simulation inputs (a C_b
   quadratic at F1 G18) is not a finding of this lane and is not cited anywhere.

**CITABLE FOR:** that A1, A2 and the build code were bound, and on what. **NOT CITABLE FOR:** any block, any factor, any
band state, any adoption, any note wording.
