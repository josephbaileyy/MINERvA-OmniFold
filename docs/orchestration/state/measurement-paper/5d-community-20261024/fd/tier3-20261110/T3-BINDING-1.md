# BINDING 1: Tier 3, the noise-free pipeline tests of where configuration (e)'s retained prior stops falling (director, 2026-11-11)

**Binds** [`T3-PIPELINE-TESTS-DECLARATION.md`](T3-PIPELINE-TESTS-DECLARATION.md) (rev 4, sha256 `f96ed6f29a155e97`)
and its code under `nd-unfolding/tier3/`, as merged in PR #1038 at
**M_T3 = `14fb9e5235307c96080d28da2c84ce0880931b9a`**. Every file is byte-identical at the audited head `d1ce9e87` and
at M_T3.

| file | sha256 (prefix) |
|---|---|
| `t3p_arms.py` | `4a685bde238dcc6d` |
| `t3p_probe.py` | `e27bf07a3e2c6032` |
| `t3p_read.py` | `f4c221dda95fbbdf` |
| `sbatch_t3p.sh` | `a21ad29f35a71e46` |
| `test_t3p.py` | `69621cb52deb2f96` |
| `t3p_mutation.py` | `3b532709e8d1b6d6` |

**Under:**
- `DECISION-20261110-joseph-confirm-round-scope.md` item 2 and its correction: the question is why (e)'s ρ at the two
  flagged truths stays well above 0 and changes little as iterations and capacity grow;
- the director's rulings on §12 (OP kept; MW at w_push·w_truth only; MU kept; the five-split floor).

## What the director checked

- **coverage-5b-audit's four rounds.** After rev 4: "ready to bind", with no blocking or major findings. Along the
  way:
  - T1: no "clears" wording; each "no effect" is printed with δ_A, δ_A/ρ_B0(50) and the headroom; "bounded by step 2"
    is decided from the headroom;
  - T2: the class precedence is stated, and "crosses and returns" is its own class;
  - t1: C-PAIR and C-X are genuinely bitwise (dtype, shape, bytes), with tests on +0.0 against −0.0;
  - R1: tests kill the three reading-rule mutants.
- **Reruns:** 68 tests OK at two seeds; 73 of 73 mutants killed, line-identical to the receipt.
- **The licence is descriptive.** It names the power limit: an arm must remove more than about half the limit at A7
  (0.53) and about a third at q3 (0.31) to register. A reading names no remedy, and adopting a changed estimator needs
  Joseph's decision and its own held-out test.

## Rulings

1. **Nothing runs before the LL5D readout.** After it, each connect (dry, then q3, then floor) comes to the director
   with its sha256s and a go. The job family `t3p_` is announced to every fenced lane before the first submit.
2. **The price:** a cap of 10.0 CPU node-h (dry 2:15, q3 2:00, floor 5:45), about 6 expected. iris is read before each
   connect.
3. **C-PAIR is binding.** B0's trace must equal FD-PRR's B0, K10, K20 and K50 products bitwise, or the study STOPs as
   not made.
4. **The audit's low v1** (the headroom = δ_A equality boundary is untested; the code follows §5.2's strict "<") is
   closed by a test-only addendum, one test and one mutant, which the audit glances at. The bound code is unchanged by
   it.
   <!-- absence-ok: the audit's own finding about one boundary case, which the addendum closes; not a claim that a result does not exist -->
5. **Each result is read once** from its committed record.

Nothing is submitted, deposited or tagged.

## Binding 1, addendum V1: the equality-boundary test (director, 2026-11-11)

**Binds** [`T3-ADDENDUM-V1.md`](T3-ADDENDUM-V1.md) (`3998708a91dde4b0`) and its test-only change, as merged in PR #1067
at **M_V1 = `8bb4e3b0e1028d960e39de0c202569a08a1218a0`**. Under `nd-unfolding/tier3/` and `fd/tier3-20261110/`, M_V1
is byte-identical to the audited head `444993d1`; the rest of the merge brought in only E96D's #1066 and #1068 from
main. It closes ruling 4's low v1.

| file | sha256 (prefix) | was |
|---|---|---|
| `test_t3p.py` | `4879178f4f9783f0` | `69621cb52deb2f96` |
| `t3p_mutation.py` | `ae9667bc71819f09` | `3b532709e8d1b6d6` |

- **The bound code is unchanged:** `t3p_probe.py`, `t3p_read.py` and `sbatch_t3p.sh` are byte-identical to M_T3, at
  the prefixes in the table above.
- **The test** pins both sides of §5.2's strict "<": not bounded at headroom = bar = 0.05 exactly, and bounded one ulp
  below. Its mutant (`<` → `<=`) is killed.
- **coverage-5b-audit's OK:** 69 tests OK at seeds 0 and 1; 74 of 74 mutants killed, line-identical to the receipt
  (`addendum-v1/`); all 13 of the audit's own mutants are killed.
- **Every connect** checks the two new test digests in place of the old ones. Rulings 1, 2, 3 and 5 stand.

Nothing is submitted, deposited or tagged.
