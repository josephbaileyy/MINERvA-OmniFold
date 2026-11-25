# (b) part 3: amendment A2 to the B5D declaration: when the build stops short of V_F (tier3-design, 2026-11-24)

**Amends:**
- `blocks5d-20261124/B5D-DECLARATION.md` rev 1, sha256
  `676c17fc5982a01c21f4c7feae2f6c8cd32b0b8ecdc69ec93882e5e30c0f0b1b`, §4: "If the bootstrap cannot resolve f̂";
- A1's item 6, last rule ("If no band is measured, the build stops short of V_F").

Both files are unchanged. Where this text differs from them, this text governs.

**Authority:**
- **The question.** codex-school's delta reads of PR #1316 (rounds 2 and 3, under `reads/`). An absolute precision rule
  should not veto a clearly resolved excess.
- **The rule.** The director's direction, by message on 2026-11-24: "A2: codex is right that an absolute precision rule
  shouldn't veto a clearly resolved excess", with the rule below.
- **The binding.** The director binds A1 and A2 together, after agy's delta read and the dispositions.

## The rule

The 3·SE activation trigger is unchanged. Each band R gets exactly one state:

<!-- absence-ok: UNMEASURED is a method state for a band no ensemble keeps, not a claim that a result does not exist -->
| state | condition | φ_R |
|---|---|---|
| **ACTIVE** | f̂_R − 1 > 3·SE(f̂_R) | f̂_R |
| **RESOLVED-INACTIVE** | not active, and SE(f̂_R) ≤ 0.5 | 1 |
| **UNRESOLVED** | not active, and SE(f̂_R) > 0.5 | 1, flagged in the record |
| **UNMEASURED** | no primary ensemble keeps band R (A1 item 6) | 1 |

<!-- absence-ok: the stop rule names method states, not the absence of a result -->
- **The build stops short of V_F only if every band is UNRESOLVED or UNMEASURED.** That case goes to the director with
  the price of new toys, as declared. The fallback is not authorized.
- **Otherwise V_F = L C_e Lᵀ is built.** L inflates only the ACTIVE bands, as declared.
- **Every band's state is in the record,** whatever the outcome. So are its f̂ and SE, and the raw toy and reference
  traces on its kept modes, relative to T's cell integrals (the director, 2026-11-24).

**What changes:**
- **A resolved large excess builds V_F.** An example is f̂ = 30 ± 4, where 29 > 12. Under the declared rule, an SE above
  0.5 in every band suppressed V_F, however clear the excess.
- **Noise never inflates anything.** An UNRESOLVED band has φ = 1.

## Why this rule, and not round 3's

codex-school's round 3 proposed: stop if no band is measured, or if every measured band has
SE > max[0.5, 0.20 (f̂_R − 1)₊], keeping the 3·SE trigger. A2 keeps the director's rule for three reasons:
- **One threshold.** In the director's rule, an ACTIVE band is resolved by the same 3·SE test that activates it. Round
  3's relative tolerance is a 5·SE test, since SE ≤ 0.2 (f̂ − 1) means f̂ − 1 ≥ 5·SE. It would sit beside the 3·SE
  trigger.
- **A real case it would stop.** Take f̂ = 4 ± 0.9. The band is active (3 > 2.7), but SE exceeds max(0.5, 0.6), so if
  every measured band were like it, round 3's rule would stop. That is a 3.3·SE excess.
- **The imprecision of φ is printed, not hidden.** A φ = f̂ known only to about 30% is the cost of the 3·SE trigger. Every
  ACTIVE band's f̂ and SE are printed for Joseph's adoption decision.
